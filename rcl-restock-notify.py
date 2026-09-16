#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Restock Notify — kendi "Stoğa gelince haber ver" motorumuz (Klaviyo'suz, ücretsiz)
======================================================================================
Akış:
  1. Bekleme listesi = Shopify müşterileri, `bekleme:<variant_id>` etiketiyle
     (etiketi Vercel `notify-me` fonksiyonu, ürün sayfasındaki formdan ekler)
  2. Bu script (cron, günlük) stokta olan (qty>0) varyantları bulur
  3. O varyantı bekleyen etiketli müşterilere Brevo ile mail atar
  4. Mail gidince etiketi siler  → idempotent (kimse iki kez mail almaz)
  5. Özeti Hermes/Telegram'a loglar

State dosyası GEREKMEZ: tetik = "etiket var + stokta var", idempotensi = etiketi silmek.

CLI:
  python3 rcl-restock-notify.py            # canlı: mail atar, etiketi siler
  python3 rcl-restock-notify.py --dry      # deneme: kimseye mail atmaz, sadece raporlar
  python3 rcl-restock-notify.py --test E-POSTA --variant VID   # tek test maili
"""
import sys, os, json, time, urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from retrocameraland_api import shopify, log

WAITLIST_PREFIX = "bekleme:"          # müşteri etiketi öneki
STORE_URL       = "https://retrocameraland.com"

def _env(key, default=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, default)

BREVO_KEY    = _env("BREVO_API_KEY")
SENDER_NAME  = _env("BREVO_SENDER_NAME", "Retrocameraland")
SENDER_EMAIL = _env("BREVO_SENDER_EMAIL", "bilgi@retrocameraland.com")   # doğrulanmış domain
REPLYTO      = _env("BREVO_REPLYTO", "retrocameraland@gmail.com")        # yanıtlar buraya düşsün
TG_TOKEN     = _env("TELEGRAM_BOT_TOKEN")
TG_CHAT      = _env("TELEGRAM_CHAT_ID")

# ── Brevo gönderim ───────────────────────────────────────────────────────────
def brevo_send(to_email, subject, html):
    body = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "replyTo": {"email": REPLYTO, "name": SENDER_NAME},
        "subject": subject,
        "htmlContent": html,
    }
    req = urllib.request.Request("https://api.brevo.com/v3/smtp/email",
                                 data=json.dumps(body).encode(), method="POST")
    req.add_header("api-key", BREVO_KEY)
    req.add_header("content-type", "application/json")
    req.add_header("accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# ── E-posta şablonu (Türkçe) ─────────────────────────────────────────────────
def render_email(product):
    title = product["title"]; price = product["price"]; url = product["url"]; img = product.get("image", "")
    img_html = f'<img src="{img}" alt="{title}" style="width:100%;max-width:420px;border-radius:12px;display:block;margin:0 auto 24px;">' if img else ""
    return f"""<!DOCTYPE html><html><body style="margin:0;background:#f4f1ec;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1a1a1a;">
<div style="max-width:520px;margin:0 auto;padding:40px 24px;">
  <p style="font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#c8a882;margin:0 0 8px;">Retrocameraland</p>
  <h1 style="font-size:26px;line-height:1.2;margin:0 0 20px;">Bekleyiş sona erdi 📸</h1>
  <p style="font-size:16px;line-height:1.6;margin:0 0 24px;">Merhaba! Haber verilmesini istediğin <b>{title}</b> yeniden stokta.
  Bu retro dijital kameralardan genelde <b>tek adet</b> buluyoruz ve çok hızlı tükeniyor — kaçırmadan göz at.</p>
  {img_html}
  <div style="text-align:center;margin:8px 0 32px;">
    <a href="{url}" style="background:#1a1a1a;color:#fff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:700;font-size:17px;display:inline-block;">Hemen İncele — {price} →</a>
  </div>
  <p style="font-size:13px;color:#888;line-height:1.6;margin:24px 0 0;text-align:center;">
    Bu e-postayı <b>{title}</b> için "stoğa gelince haber ver" dediğin için aldın.<br>
    Retrocameraland · <a href="{STORE_URL}" style="color:#888;">retrocameraland.com</a></p>
</div></body></html>"""

# ── Bekleyen müşterileri bul (etikete göre) ──────────────────────────────────
def customers_waiting_for(variant_id):
    tag = WAITLIST_PREFIX + str(variant_id)
    q = urllib.parse.quote(f"tag:{tag}")
    r = shopify("GET", f"customers/search.json?query={q}&limit=250&fields=id,email,tags")
    return r.get("customers", [])

def remove_tag(customer, variant_id):
    tag = WAITLIST_PREFIX + str(variant_id)
    tags = [t.strip() for t in (customer.get("tags") or "").split(",") if t.strip()]
    tags = [t for t in tags if t != tag]
    shopify("PUT", f"customers/{customer['id']}.json",
            {"customer": {"id": customer["id"], "tags": ", ".join(tags)}})

# ── Stoktaki ürün/varyant haritası ───────────────────────────────────────────
def instock_variants():
    out = []
    r = shopify("GET", "products.json?limit=250&fields=id,title,handle,image,images,variants,status")
    for p in r.get("products", []):
        if p.get("status") != "active":
            continue
        img = (p.get("image") or {}).get("src") or (p.get("images") or [{}])[0].get("src", "")
        for v in p.get("variants", []):
            if (v.get("inventory_quantity") or 0) > 0:
                out.append({
                    "variant_id": v["id"],
                    "title": p["title"],
                    "price": f"{float(v.get('price', 0)):,.0f} ₺".replace(",", "."),
                    "url": f"{STORE_URL}/products/{p['handle']}?variant={v['id']}",
                    "image": img,
                })
    return out

# ── Hermes/Telegram log ──────────────────────────────────────────────────────
def tg(msg):
    if not (TG_TOKEN and TG_CHAT):
        return
    try:
        data = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data, timeout=15)
    except Exception:
        pass

# ── Ana akış ─────────────────────────────────────────────────────────────────
def run(dry=False):
    if not BREVO_KEY:
        log("⚠ BREVO_API_KEY yok (.env). Çıkılıyor."); return
    variants = instock_variants()
    log(f"Stokta {len(variants)} varyant. Bekleyen kontrol ediliyor...")
    sent = 0; notified_products = []
    for v in variants:
        waiters = customers_waiting_for(v["variant_id"])
        if not waiters:
            continue
        log(f"  '{v['title']}' stokta → {len(waiters)} bekleyen")
        for c in waiters:
            email = c.get("email")
            if not email:
                continue
            if dry:
                log(f"    [DRY] mail atılacaktı → {email}")
                sent += 1; continue
            try:
                brevo_send(email, f"Beklediğin kamera yeniden stokta 📸 — {v['title']}", render_email(v))
                remove_tag(c, v["variant_id"])
                log(f"    ✅ {email} bilgilendirildi, etiket silindi")
                sent += 1; time.sleep(0.3)
            except urllib.error.HTTPError as e:
                log(f"    ⚠ {email} gönderilemedi: {e.code} {e.read().decode()[:120]}")
            except Exception as e:
                log(f"    ⚠ {email}: {str(e)[:120]}")
        notified_products.append(f"{v['title']} ({len(waiters)})")
    summary = (f"🔔 <b>Restock Bildirimi</b>\nGönderilen mail: <b>{sent}</b>\n"
               + ("\n".join("• " + p for p in notified_products) if notified_products else "Bekleyen yok."))
    log(summary.replace("<b>", "").replace("</b>", ""))
    if sent and not dry:
        tg(summary)

if __name__ == "__main__":
    if "--test" in sys.argv:
        i = sys.argv.index("--test"); email = sys.argv[i + 1]
        vid = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else None
        v = next((x for x in instock_variants() if str(x["variant_id"]) == str(vid)), None) \
            or (instock_variants() or [None])[0]
        if not v:
            print("Stokta test edilecek ürün yok."); sys.exit(1)
        print(f"Test maili → {email} ({v['title']})")
        print(brevo_send(email, f"[TEST] Beklediğin kamera stokta 📸 — {v['title']}", render_email(v)))
    else:
        run(dry="--dry" in sys.argv)
