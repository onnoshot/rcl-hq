#!/usr/bin/env python3
"""
Retrocameraland — Shopify Dashboard Güncelleyici
Saatlik çalışır: sipariş, müşteri ve stok verilerini çekip HQ dashboard'u günceller.

Kullanım:
    python3 retrocameraland-shopify-fetch.py
"""

import fcntl
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# ─── AYARLAR ───────────────────────────────────────────────────────────────
from rcl_config import SHOPIFY_TOKEN, write_block, publish   # token / yol / push tek yer: rcl_config.py
SHOPIFY_STORE  = "retrocameraland.myshopify.com"

SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))

MONTH_TR = {
    "01":"Oca","02":"Şub","03":"Mar","04":"Nis","05":"May","06":"Haz",
    "07":"Tem","08":"Ağu","09":"Eyl","10":"Eki","11":"Kas","12":"Ara",
}

ACC_KEYWORDS = ["kart okuyucu", "aktarıcı", "şarj", "tripod", "usb", "type-c", "ulanzi"]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def wait_for_network(host="retrocameraland.myshopify.com", retries=12, delay=10):
    import socket
    for i in range(retries):
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(host, 443)
            return True
        except OSError:
            if i == 0:
                log("Ağ bekleniyor...")
            time.sleep(delay)
    log("HATA: Ağa bağlanılamadı, çıkılıyor.")
    sys.exit(1)


def shopify_get(path):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Shopify GET {path} → {e.code}: {e.read().decode()[:200]}")


def fetch_orders():
    """Magazanin EN BASTAN beri tum odenmis siparisleri (sayfalamali, 250'lik sayfalar).
    NOT: token'da read_all_orders yoksa Shopify yalniz son 60 gunu dondurur."""
    import re
    url = (f"https://{SHOPIFY_STORE}/admin/api/2024-01/orders.json?status=any&financial_status=paid&limit=250"
           "&fields=id,created_at,total_price,line_items,referring_site")
    orders = []
    while url:
        req = urllib.request.Request(url)
        req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                orders += json.loads(r.read()).get("orders", [])
                m = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("Link", "") or "")
                url = m.group(1) if m else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Shopify GET orders → {e.code}: {e.read().decode()[:200]}")
    if orders:
        oldest = min(o["created_at"] for o in orders)[:10]
        log(f"  En eski siparis: {oldest}")
        if datetime.fromisoformat(oldest) > datetime.now() - timedelta(days=62):
            log("  UYARI: siparisler yalniz son ~60 gunu kapsiyor — token'da read_all_orders yetkisi yok olabilir")
    return orders


def fetch_customers_count():
    return shopify_get("customers/count.json").get("count", 0)


def fetch_inventory_costs(inventory_item_ids):
    """Shopify inventory_items API'den ürün maliyetlerini çek."""
    costs = {}
    if not inventory_item_ids:
        return costs
    # Batch: max 250 per request. ÖNEMLİ: &limit=250 şart — yoksa Shopify varsayılan 50 döner
    # ve batch'in geri kalanı sessizce düşer (maliyetler eksik gelir).
    for i in range(0, len(inventory_item_ids), 250):
        batch = inventory_item_ids[i:i+250]
        ids_str = ",".join(str(x) for x in batch)
        try:
            data = shopify_get(f"inventory_items.json?ids={ids_str}&limit=250")
            for item in data.get("inventory_items", []):
                raw_cost = item.get("cost")
                if raw_cost:
                    costs[item["id"]] = float(raw_cost)
        except Exception as e:
            log(f"  Maliyet çekme hatası: {e}")
    return costs


def previous_costs():
    """Dashboard'daki mevcut SHOPIFY blogundan urun adi -> maliyet (kamera + aksesuar)."""
    try:
        from rcl_config import DASHBOARD_HTML, MARKERS
        start, end = MARKERS["SHOPIFY"]
        with open(DASHBOARD_HTML, encoding="utf-8") as f:
            html = f.read()
        block = html[html.index(start) + len(start):html.index(end)]
        data = json.loads(block[block.index("{"):block.rindex("}") + 1])
        return {x["name"]: x["cost"] for x in data.get("cameras", []) + data.get("accessories", []) if x.get("cost")}
    except Exception as e:
        log(f"  Onceki maliyetler okunamadi: {e}")
        return {}


def fetch_inventory():
    # Sadece AKTIF urunler — taslak/arsiv urunler stok degerini sisirmesin.
    data = shopify_get("products.json?limit=250&status=active&fields=id,title,handle,product_type,variants")
    cameras, accessories, out_of_stock = [], [], 0
    inv_item_ids = []

    # Önce tüm ürünleri topla ve inventory_item_id'leri biriktir
    raw_items = []
    for p in data.get("products", []):
        for v in p["variants"]:
            qty   = v.get("inventory_quantity", 0)
            price = float(v.get("price", 0))
            name  = p["title"]
            inv_id = v.get("inventory_item_id")
            if qty <= 0:
                out_of_stock += 1
                continue
            if inv_id:
                inv_item_ids.append(inv_id)
            ptype = (p.get("product_type") or "").lower()
            is_acc = ptype == "aksesuar" or (ptype != "digital camera" and any(kw in name.lower() for kw in ACC_KEYWORDS))
            compare = float(v.get("compare_at_price") or 0)
            item = {"name": name, "price": price, "qty": qty, "inv_item_id": inv_id,
                    "handle": p.get("handle", "")}
            if compare > price:
                item["compare_at"] = compare
            raw_items.append((is_acc, item))

    # Maliyetleri çek
    log("  Ürün maliyetleri Shopify'dan çekiliyor...")
    costs = fetch_inventory_costs(inv_item_ids)

    # Maliyet cekilemezse (or. token'da read_inventory yok → 403) son bilinen maliyetleri koru
    prev_costs = previous_costs() if not costs else {}
    if prev_costs:
        log(f"  UYARI: Shopify maliyeti alinamadi — {len(prev_costs)} urunde son bilinen maliyet kullaniliyor")

    for is_acc, item in raw_items:
        inv_id = item.pop("inv_item_id", None)
        cost = costs.get(inv_id)
        if cost is None:
            cost = prev_costs.get(item["name"])
        if cost is not None:
            item["cost"] = int(round(cost))
        (accessories if is_acc else cameras).append(item)

    cameras.sort(key=lambda x: -x["price"])
    accessories.sort(key=lambda x: -(x["price"] * x["qty"]))
    cost_count = sum(1 for c in cameras + accessories if c.get("cost"))
    log(f"  {len(cameras)} kamera, {len(accessories)} aksesuar — {cost_count} kalemde maliyet bulundu")
    return cameras, accessories, out_of_stock


def fetch_variant_costs():
    """TUM urunlerin (satilip arsivlenenler dahil) variant_id -> birim maliyet haritasi."""
    data = shopify_get("products.json?limit=250&fields=id,variants")
    var_to_inv = {v["id"]: v.get("inventory_item_id") for p in data.get("products", []) for v in p["variants"]}
    inv_costs = fetch_inventory_costs([i for i in var_to_inv.values() if i])
    return {vid: inv_costs[iid] for vid, iid in var_to_inv.items() if iid in inv_costs}


def annotate_order_cogs(orders, variant_costs):
    """Her siparise gercek satilan urun maliyeti (_cogs) ve maliyeti bilinmeyen satir cirosu (_unmatched) ekler."""
    matched = total = 0
    for o in orders:
        cogs = unmatched = 0.0
        for li in o.get("line_items", []):
            qty = int(li.get("quantity") or 0)
            line_rev = float(li.get("price") or 0) * qty
            cost = variant_costs.get(li.get("variant_id"))
            total += 1
            if cost is not None:
                cogs += cost * qty
                matched += 1
            else:
                unmatched += line_rev
        o["_cogs"], o["_unmatched"] = cogs, unmatched
    log(f"  Satilan urun maliyeti: {matched}/{total} satirda maliyet bulundu")


def classify_channel(referring_site):
    if not referring_site:
        return "Direkt"
    ref = referring_site.lower()
    if "instagram" in ref:  return "Instagram"
    if "google"    in ref:  return "Google"
    if "youtube"   in ref:  return "YouTube"
    if "tiktok"    in ref or "tt.com" in ref: return "TikTok"
    if "pinterest" in ref:  return "Pinterest"
    if "facebook"  in ref or "fb.com" in ref: return "Facebook"
    if "chatgpt"   in ref or "openai" in ref or "bing" in ref: return "AI / Arama"
    if "retrocameraland" in ref: return "Direkt"
    return "Diğer"


CHANNEL_META = {
    "Direkt":     {"icon": "🔗", "color": "#F5A623"},
    "Google":     {"icon": "🔍", "color": "#4285F4"},
    "Instagram":  {"icon": "📸", "color": "#BF5AF2"},
    "YouTube":    {"icon": "▶",  "color": "#FF453A"},
    "TikTok":     {"icon": "♪",  "color": "#ffffff"},
    "Pinterest":  {"icon": "⊕",  "color": "#E60023"},
    "Facebook":   {"icon": "f",  "color": "#1877F2"},
    "AI / Arama": {"icon": "🤖", "color": "#5AC8FA"},
    "Diğer":      {"icon": "•",  "color": "#8E8E93"},
}


def calc_channels(orders):
    ch_cnt = defaultdict(int)
    ch_rev = defaultdict(float)
    for o in orders:
        ch = classify_channel(o.get("referring_site", ""))
        ch_cnt[ch] += 1
        ch_rev[ch] += float(o.get("total_price", 0))

    total_ord = sum(ch_cnt.values())
    total_rev = sum(ch_rev.values())
    result = []
    for ch, cnt in sorted(ch_cnt.items(), key=lambda x: -x[1]):
        meta = CHANNEL_META.get(ch, {"icon": "•", "color": "#888"})
        result.append({
            "name":       ch,
            "icon":       meta["icon"],
            "color":      meta["color"],
            "orders":     cnt,
            "rev":        round(ch_rev[ch]),
            "order_pct":  round(cnt / total_ord * 100, 1) if total_ord else 0,
            "rev_pct":    round(ch_rev[ch] / total_rev * 100, 1) if total_rev else 0,
        })
    return result


def calc_period(orders, days):
    now     = datetime.now(timezone.utc)
    cutoff  = now - timedelta(days=days)
    subset  = [o for o in orders if datetime.fromisoformat(
        o["created_at"].replace("Z", "+00:00")) >= cutoff]
    rev = sum(float(o["total_price"]) for o in subset)
    cnt = len(subset)
    return {"revenue": round(rev), "orders": cnt, "aov": round(rev / cnt) if cnt else 0,
            "cogs": round(sum(o.get("_cogs", 0) for o in subset)),
            "cogs_unmatched_rev": round(sum(o.get("_unmatched", 0) for o in subset))}


def calc_monthly(orders):
    now = datetime.now(timezone.utc)
    monthly_rev = defaultdict(float)
    monthly_cnt = defaultdict(int)
    monthly_cogs = defaultdict(float)
    monthly_unm = defaultdict(float)
    for o in orders:
        dt  = datetime.fromisoformat(o["created_at"].replace("Z", "+00:00"))
        key = dt.strftime("%Y-%m")
        monthly_rev[key] += float(o["total_price"])
        monthly_cnt[key] += 1
        monthly_cogs[key] += o.get("_cogs", 0)
        monthly_unm[key] += o.get("_unmatched", 0)

    first = min(monthly_rev) if monthly_rev else now.strftime("%Y-%m")
    span = (now.year - int(first[:4])) * 12 + now.month - int(first[5:7])
    months = []
    for i in range(max(11, span), -1, -1):
        year  = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year  -= 1
        key = f"{year:04d}-{month:02d}"
        months.append(key)

    labels  = [f"{MONTH_TR[k[5:7]]} {k[2:4]}" for k in months]
    revenue = [round(monthly_rev.get(k, 0)) for k in months]
    cnt     = [monthly_cnt.get(k, 0) for k in months]
    cogs    = [round(monthly_cogs.get(k, 0)) for k in months]
    unm     = [round(monthly_unm.get(k, 0)) for k in months]
    return labels, revenue, cnt, cogs, unm


def calc_recent_orders(orders, n=10):
    sorted_o = sorted(orders, key=lambda o: o["created_at"], reverse=True)
    result = []
    for o in sorted_o[:n]:
        dt  = datetime.fromisoformat(o["created_at"].replace("Z", "+00:00"))
        mon = MONTH_TR[dt.strftime("%m")]
        result.append({"date": f"{dt.day} {mon} {dt.year}", "amount": round(float(o["total_price"]))})
    return result


def _stock_item(item):
    r = {"name": item["name"], "price": int(round(item["price"])), "qty": int(item["qty"])}
    if item.get("compare_at"):
        r["compare_at"] = int(round(item["compare_at"]))
    if item.get("cost"):
        r["cost"] = int(item["cost"])
    if item.get("handle"):
        r["handle"] = item["handle"]
    return r


def cam_only(item):
    return _stock_item(item)


def acc_only(item):
    return _stock_item(item)


def build_data_block(orders, customers, cameras, accessories, out_of_stock):
    now_iso  = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    labels, monthly_rev, monthly_orders, monthly_cogs, monthly_unm = calc_monthly(orders)
    data = {
        "updated_at":      now_iso,
        "period_30d":      calc_period(orders, 30),
        "period_90d":      calc_period(orders, 90),
        "period_year":     calc_period(orders, 365),
        "period_all":      calc_period(orders, 100000),
        "customers_total": customers,
        "monthly_labels":  labels,
        "monthly_revenue": monthly_rev,
        "monthly_orders":  monthly_orders,
        "monthly_cogs":    monthly_cogs,
        "monthly_cogs_unmatched_rev": monthly_unm,
        "channels":        calc_channels(orders),
        "recent_orders":   calc_recent_orders(orders),
        "cameras":         [cam_only(c) for c in cameras],
        "accessories":     [acc_only(a) for a in accessories],
        "out_of_stock":    out_of_stock,
    }
    js = json.dumps(data, ensure_ascii=False, indent=2)
    return f"const SHOPIFY = {js};"


def update_dashboard(payload):
    # ANA KAYNAGA yaz; data.js publish() icinde ANA KAYNAKTAN turetilir
    write_block("SHOPIFY", payload)
    log("ANA KAYNAK guncellendi (SHOPIFY)")
    return True



def main():
    log("=== Retrocameraland Shopify Fetch ===")
    wait_for_network()

    log("Siparişler çekiliyor...")
    orders = fetch_orders()
    log(f"  {len(orders)} ödeme yapılmış sipariş")

    log("Müşteri sayısı çekiliyor...")
    customers = fetch_customers_count()
    log(f"  {customers} kayıtlı müşteri")

    log("Stok çekiliyor...")
    cameras, accessories, out_of_stock = fetch_inventory()
    cam_val = sum(c["price"] * c["qty"] for c in cameras)
    acc_val = sum(a["price"] * a["qty"] for a in accessories)
    log(f"  {len(cameras)} kamera + {sum(a['qty'] for a in accessories)} aksesuar — ₺{cam_val+acc_val:,.0f}")
    log(f"  {out_of_stock} tükenen varyant")

    log("Satılan ürün maliyetleri (COGS) hesaplanıyor...")
    annotate_order_cogs(orders, fetch_variant_costs())

    log("Kanal dağılımı hesaplanıyor...")
    channels = calc_channels(orders)
    for ch in channels:
        log(f"  {ch['name']}: {ch['orders']} sipariş (%{ch['order_pct']})")

    log("Dashboard güncelleniyor...")
    data_block = build_data_block(orders, customers, cameras, accessories, out_of_stock)
    update_dashboard(data_block)
    publish("shopify", log)
    log("=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
