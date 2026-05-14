#!/usr/bin/env python3
"""
Retrocameraland — Shopify Dashboard Güncelleyici
Saatlik çalışır: sipariş, müşteri ve stok verilerini çekip HQ dashboard'u günceller.

Kullanım:
    python3 retrocameraland-shopify-fetch.py
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# ─── AYARLAR ───────────────────────────────────────────────────────────────
SHOPIFY_TOKEN  = "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"
SHOPIFY_STORE  = "retrocameraland.myshopify.com"

SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_HTML = os.path.join(SCRIPT_DIR, "retrocameraland-hq-dashboard.html")
DATA_JS        = "/Users/onnoshot/Downloads/rcl-dashboard/data.js"
START_MARKER   = "/* ─── SHOPIFY DATA START ─── */"
END_MARKER     = "/* ─── SHOPIFY DATA END ─── */"

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
    data = shopify_get(
        "orders.json?status=any&financial_status=paid&limit=250"
        "&fields=id,created_at,total_price,line_items,referring_site"
    )
    return data.get("orders", [])


def fetch_customers_count():
    return shopify_get("customers/count.json").get("count", 0)


def fetch_inventory():
    data = shopify_get("products.json?limit=250&fields=id,title,variants")
    cameras, accessories, out_of_stock = [], [], 0
    for p in data.get("products", []):
        for v in p["variants"]:
            qty   = v.get("inventory_quantity", 0)
            price = float(v.get("price", 0))
            name  = p["title"]
            if qty <= 0:
                out_of_stock += 1
                continue
            is_acc = any(kw in name.lower() for kw in ACC_KEYWORDS)
            item = {"name": name, "price": price, "qty": qty}
            (accessories if is_acc else cameras).append(item)
    cameras.sort(key=lambda x: -x["price"])
    accessories.sort(key=lambda x: -(x["price"] * x["qty"]))
    return cameras, accessories, out_of_stock


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
    return {"revenue": round(rev), "orders": cnt, "aov": round(rev / cnt) if cnt else 0}


def calc_monthly(orders):
    now = datetime.now(timezone.utc)
    monthly_rev = defaultdict(float)
    monthly_cnt = defaultdict(int)
    for o in orders:
        dt  = datetime.fromisoformat(o["created_at"].replace("Z", "+00:00"))
        key = dt.strftime("%Y-%m")
        monthly_rev[key] += float(o["total_price"])
        monthly_cnt[key] += 1

    months = []
    for i in range(11, -1, -1):
        d   = now.replace(day=1) - timedelta(days=30 * i)
        key = d.strftime("%Y-%m")
        months.append(key)

    labels  = [f"{MONTH_TR[k[5:7]]} {k[2:4]}" for k in months]
    revenue = [round(monthly_rev.get(k, 0)) for k in months]
    cnt     = [monthly_cnt.get(k, 0) for k in months]
    return labels, revenue, cnt


def calc_recent_orders(orders, n=10):
    sorted_o = sorted(orders, key=lambda o: o["created_at"], reverse=True)
    result = []
    for o in sorted_o[:n]:
        dt  = datetime.fromisoformat(o["created_at"].replace("Z", "+00:00"))
        mon = MONTH_TR[dt.strftime("%m")]
        result.append({"date": f"{dt.day} {mon} {dt.year}", "amount": round(float(o["total_price"]))})
    return result


def cam_only(item):
    return {"name": item["name"], "price": int(item["price"])}


def acc_only(item):
    return {"name": item["name"], "price": int(item["price"]), "qty": item["qty"]}


def build_data_block(orders, customers, cameras, accessories, out_of_stock):
    now_iso  = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    labels, monthly_rev, monthly_orders = calc_monthly(orders)
    data = {
        "updated_at":      now_iso,
        "period_30d":      calc_period(orders, 30),
        "period_90d":      calc_period(orders, 90),
        "period_year":     calc_period(orders, 365),
        "customers_total": customers,
        "monthly_labels":  labels,
        "monthly_revenue": monthly_rev,
        "monthly_orders":  monthly_orders,
        "channels":        calc_channels(orders),
        "recent_orders":   calc_recent_orders(orders),
        "cameras":         [cam_only(c) for c in cameras],
        "accessories":     [acc_only(a) for a in accessories],
        "out_of_stock":    out_of_stock,
    }
    js = json.dumps(data, ensure_ascii=False, indent=2)
    return f"{START_MARKER}\nconst SHOPIFY = {js};\n{END_MARKER}"


def update_file(path, data_block):
    if not os.path.exists(path):
        log(f"HATA: Dosya bulunamadı: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    si = content.find(START_MARKER)
    ei = content.find(END_MARKER)
    if si == -1 or ei == -1:
        log(f"HATA: Marker bulunamadı: {path}")
        return False
    new_content = content[:si] + data_block + content[ei + len(END_MARKER):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    log(f"Güncellendi: {path}")
    return True


def update_dashboard(data_block):
    update_file(DASHBOARD_HTML, data_block)
    update_file(DATA_JS, data_block)
    return True


def git_push():
    import subprocess, shutil
    dash_dir = "/Users/onnoshot/Downloads/rcl-dashboard"
    git = ["git", "-c", "credential.helper=osxkeychain"]
    try:
        shutil.copy(DASHBOARD_HTML, f"{dash_dir}/index.html")
        subprocess.run(git + ["add", "data.js", "index.html"], cwd=dash_dir, check=True, capture_output=True)
        r = subprocess.run(git + ["commit", "-m", f"data: shopify {datetime.now().strftime('%Y-%m-%dT%H:%M')}"],
                           cwd=dash_dir, capture_output=True)
        if r.returncode != 0:
            log("Git commit: değişiklik yok, push atlandı")
            return
        result = subprocess.run(git + ["push"], cwd=dash_dir, check=True, capture_output=True)
        log("Git push tamamlandı")
    except subprocess.CalledProcessError as e:
        log(f"Git push hatası: {e.stderr.decode().strip()}")


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
    cam_val = sum(c["price"] for c in cameras)
    acc_val = sum(a["price"] * a["qty"] for a in accessories)
    log(f"  {len(cameras)} kamera + {sum(a['qty'] for a in accessories)} aksesuar — ₺{cam_val+acc_val:,.0f}")
    log(f"  {out_of_stock} tükenen varyant")

    log("Kanal dağılımı hesaplanıyor...")
    channels = calc_channels(orders)
    for ch in channels:
        log(f"  {ch['name']}: {ch['orders']} sipariş (%{ch['order_pct']})")

    log("Dashboard güncelleniyor...")
    data_block = build_data_block(orders, customers, cameras, accessories, out_of_stock)
    ok = update_dashboard(data_block)

    git_push()
    log("=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
