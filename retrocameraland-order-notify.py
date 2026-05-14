#!/usr/bin/env python3
"""
Retrocameraland — Yeni Sipariş Telegram Bildirimi
Her 5 dakikada bir çalışır. Daha önce bildirilmemiş siparişler varsa Telegram'a gönderir.
"""

import json, os, urllib.request, urllib.error
from datetime import datetime, timezone

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
TG_TOKEN      = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID    = "7904534693"
STATE_FILE    = os.path.expanduser("~/.config/rcl-shopify/last_order_id.json")

MONTHS_TR = ["","Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]

CHANNEL_ICONS = {
    "instagram": "📸 Instagram",
    "google":    "🔍 Google",
    "youtube":   "▶️ YouTube",
    "tiktok":    "♪ TikTok",
    "pinterest": "⊕ Pinterest",
    "facebook":  "🔵 Facebook",
}


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"last_id": 0}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def shopify_get(path):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def tg_send(text):
    import urllib.parse
    url  = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    body = json.dumps({"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    req  = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def classify_channel(referring_site):
    if not referring_site:
        return "🔗 Direkt"
    ref = referring_site.lower()
    for kw, label in CHANNEL_ICONS.items():
        if kw in ref:
            return label
    if "retrocameraland" in ref:
        return "🔗 Direkt"
    return "🌐 Diğer"


def fmt_date(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    return f"{dt.day} {MONTHS_TR[dt.month]} {dt.hour:02d}:{dt.minute:02d}"


def build_message(order):
    order_num = order.get("order_number", order["id"])
    amount    = float(order.get("total_price", 0))
    created   = fmt_date(order["created_at"])
    channel   = classify_channel(order.get("referring_site", ""))

    items = order.get("line_items", [])
    item_lines = []
    for it in items[:5]:
        qty  = it.get("quantity", 1)
        name = it.get("name", "?")
        if len(name) > 40:
            name = name[:38] + "…"
        item_lines.append(f"  • {name} ×{qty}")
    if len(items) > 5:
        item_lines.append(f"  • … +{len(items)-5} ürün daha")

    lines = [
        "🛍️ <b>Yeni Sipariş!</b>",
        "",
        f"📦 <b>Sipariş #{order_num}</b>",
        f"💰 <b>₺{amount:,.0f}</b>",
        f"📅 {created}",
        f"📣 {channel}",
    ]

    if item_lines:
        lines += ["", "<b>Ürünler:</b>"] + item_lines

    # Kargo adresi şehir/ülke
    addr = order.get("shipping_address") or order.get("billing_address")
    if addr:
        city    = addr.get("city", "")
        country = addr.get("country", "")
        loc = ", ".join(x for x in [city, country] if x)
        if loc:
            lines.append(f"📍 {loc}")

    return "\n".join(lines)


def main():
    state   = load_state()
    last_id = state.get("last_id", 0)

    data   = shopify_get(
        "orders.json?status=any&financial_status=paid&limit=10"
        "&fields=id,order_number,created_at,total_price,line_items,"
        "referring_site,shipping_address,billing_address"
        "&order=id+desc"
    )
    orders = data.get("orders", [])

    new_orders = [o for o in orders if int(o["id"]) > last_id]
    new_orders.sort(key=lambda o: int(o["id"]))  # eskiden yeniye

    for order in new_orders:
        msg = build_message(order)
        tg_send(msg)
        print(f"[OK] Sipariş #{order.get('order_number')} bildirildi")

    if new_orders:
        state["last_id"] = int(new_orders[-1]["id"])
        save_state(state)
    else:
        print("[OK] Yeni sipariş yok")


if __name__ == "__main__":
    main()
