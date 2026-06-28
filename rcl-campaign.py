#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Campaign — haftalık temalı e-posta kampanyası motoru (Brevo, ücretsiz)
==========================================================================
Akış:  tema seç → stoktaki ürünleri çek → Claude ile Türkçe metin yaz →
        (opsiyonel) Shopify indirim kodu üret → HTML render → ÖNİZLEME kaydet.
Gönderim ayrı ve manuel: --send (300/gün Brevo limiti otomatik bölünür).

Asla otomatik göndermez. Önce önizle, onayla, sonra --send.

Kullanım:
  python3 rcl-campaign.py preview haftanin-seckisi            # önizleme üret (mail ATMAZ)
  python3 rcl-campaign.py preview hediye-rehberi --discount 10
  python3 rcl-campaign.py send  <campaign_id>                 # ONAYDAN SONRA gönder
  python3 rcl-campaign.py send  <campaign_id> --test E-POSTA  # önce kendine test
  python3 rcl-campaign.py stats <campaign_id>                 # Brevo açılma/tıklama
  python3 rcl-campaign.py list                                # kampanya kayıtları
"""
import sys, os, re, json, time, html, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from retrocameraland_api import shopify, log

STORE = "https://retrocameraland.com"
CAMPAIGN_DB = os.path.join(ROOT, "rcl-campaigns.json")
PREVIEW_DIR = os.path.join(ROOT, "outputs")
UTM = "utm_source=email&utm_medium=brevo&utm_campaign="

def _env(key, default=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, default)

BREVO_KEY    = _env("BREVO_API_KEY")
ANTHROPIC    = _env("ANTHROPIC_API_KEY")
SENDER_NAME  = _env("BREVO_SENDER_NAME", "Retrocameraland")
SENDER_EMAIL = _env("BREVO_SENDER_EMAIL", "bilgi@retrocameraland.com")
REPLYTO      = _env("BREVO_REPLYTO", "retrocameraland@gmail.com")
ACCENT = "#ff3b3b"        # retrocameraland.com marka vermilyonu
ACCENT2 = "#e21f1f"       # koyu kırmızı (gradyan için)
PAGE_BG = "#f2f1ee"
LOGO_URL = "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/RetroCameraLand_photo1.png?v=1750024064"

# ── Temalar ──────────────────────────────────────────────────────────────────
THEMES = {
    "haftanin-seckisi": {
        "name": "Haftanın Seçkisi",
        "n": 4,
        "brief": ("Bu hafta öne çıkan stoktaki retro dijital kameralardan bir seçki. ASIL VURGU: "
                  "bu kameraların KOLEKSİYONLUK DEĞERİ ve HEDİYELİK önemi. Üretimi durmuş, bulunması "
                  "zorlaşan, değeri artan parçalar oldukları için özel. Her biri tek adet. "
                  "Premium ama sıcak ton, koleksiyoner heyecanı."),
    },
    "hediye-rehberi": {
        "name": "Hediye Rehberi",
        "n": 4,
        "brief": ("Retro kamera hediyesi teması. ASIL VURGU: KOLEKSİYONLUK ve HEDİYELİK DEĞER. "
                  "Üretimi durmuş, her yıl değerlenen, anlamlı bir koleksiyon parçası ve sevdiğine "
                  "verebileceğin en özel hediyelerden biri olduğu için değerli. Duygusal ama "
                  "değer-odaklı, premium ton."),
    },
    "kamera-bulucu": {
        "name": "Kamera Bulucu",
        "n": 3,
        "brief": ("'Hangi Kamera Bana Uygun?' interaktif test/eşleştirme aracının tanıtımı. "
                  "ASIL VURGU: kararsızlara yardım — birkaç soruyla, 30 saniyede, kişinin tarzına/"
                  "bütçesine/kullanımına en uygun retro dijital kamerayı yapay zekayla eşleştirme. "
                  "Davetkar, eğlenceli ama premium ton; ürün satışı değil, aracı denemeye davet."),
    },
}

# Kamera Bulucu (interaktif test) sayfası
FINDER_URL = f"{STORE}/pages/hangi-kamera-bana-uygun"

# ── Claude ───────────────────────────────────────────────────────────────────
GEMINI = _env("GEMINI_API_KEY")

def claude(system, user, max_tokens=1200):
    import anthropic
    c = anthropic.Anthropic(api_key=ANTHROPIC)
    r = c.messages.create(model="claude-sonnet-4-6", max_tokens=max_tokens,
                          system=system, messages=[{"role": "user", "content": user}])
    return r.content[0].text

def gemini(system, user):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI}"
    body = {"system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user}]}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    req.add_header("content-type", "application/json")
    r = json.loads(urllib.request.urlopen(req, timeout=40).read())
    return r["candidates"][0]["content"]["parts"][0]["text"]

# Hazır yedek metin (LLM yoksa) — tema bazlı, üzerine ürün isimleri eklenir
STATIC_COPY = {
    "haftanin-seckisi": {"subject": "Koleksiyonluk retro kameralar, tek adet",
        "preview": "Üretimi durmuş, değeri artan parçalar. Koleksiyona ve hediyeye değer.",
        "heading": "Koleksiyonluk değeri olan kameralar",
        "intro": "Sattığımız her retro kamera, üretimi çoktan durmuş ve bulunması her geçen gün zorlaşan bir parça. Bu yüzden sadece fotoğraf çekmek için değil, koleksiyon değeri ve hediye anlamı için de özel. Aşağıdaki seçkinin her biri tek adet; gerçek değerini bilen biri için, ister kendine ister sevdiğin birine."},
    "kamera-bulucu": {"subject": "Hangi retro kamera sana uygun? 30 saniyede bul",
        "preview": "Birkaç soru, sana özel kamera önerisi. Kararsızsan tam sana göre.",
        "heading": "Hangi retro kamera tam sana göre?",
        "intro": "Onlarca kamera arasından sana en uygun olanı seçmek bazen zor olabilir. Yeni hazırladığımız kısa testle; tarzına, bütçene ve nasıl kullanacağına göre sana en uygun retro dijital kamerayı saniyeler içinde eşleştiriyoruz. Kararsızsan başlamak için en güzel yer burası."},
    "hediye-rehberi": {"subject": "Sıradan değil, koleksiyonluk bir hediye",
        "preview": "Değeri olan, hatırlanan, koleksiyonluk bir hediye.",
        "heading": "Sıradan değil, koleksiyonluk bir hediye",
        "intro": "Üretimi durmuş, her yıl biraz daha değerlenen bir retro kamera, sevdiğin birine verebileceğin en anlamlı hediyelerden biri. Hem elle tutulur bir koleksiyon parçası hem de anıları gerçek bir nesneyle saklama davetiyesi. İşte hediye için en sevdiğimiz, her biri tek adet kameralar."},
}

def get_copy(theme_key, products, disc):
    th = THEMES[theme_key]
    sys_p = ("Sen Retrocameraland'in e-posta editörüsün. Türkçe, sıcak, AI-klişesinden uzak yaz. "
             "ÖNEMLİ: Asla '—' (uzun tire / em dash) kullanma; cümleleri uzun tire olmadan, "
             "virgül veya nokta ile kur. Markdown YOK. Sadece JSON döndür: "
             "{\"subject\":..,\"preview\":..,\"heading\":..,\"intro\":..} "
             "subject<=55 karakter, preview<=90, heading kısa vurucu, intro 2-3 cümle.")
    usr = (f"Tema: {th['name']}. Brief: {th['brief']}\n"
           f"Öne çıkan ürünler: {', '.join(p['title']+' ('+p['price']+')' for p in products)}\n"
           f"{('İlk alışverişe özel bir indirim kodu da var, introda nazikçe ima et.' if disc else '')}")
    for engine_fn, name in [(claude, "Claude"), (gemini, "Gemini")]:
        try:
            raw = engine_fn(sys_p, usr)
            m = re.search(r"\{.*\}", raw, re.S)
            if m:
                log(f"  metin: {name} ✓"); return json.loads(m.group())
        except Exception as e:
            log(f"  {name} atlandı: {str(e)[:80]}")
    log("  metin: hazır şablon (LLM yok)")
    return dict(STATIC_COPY[theme_key])

# ── Stoktaki ürünler ─────────────────────────────────────────────────────────
def instock_products(n):
    r = shopify("GET", "products.json?limit=250&fields=id,title,handle,image,images,variants,status")
    out = []
    for p in r.get("products", []):
        if p.get("status") != "active":
            continue
        img = (p.get("image") or {}).get("src") or (p.get("images") or [{}])[0].get("src", "")
        for v in p.get("variants", []):
            if (v.get("inventory_quantity") or 0) > 0:
                out.append({"title": p["title"], "handle": p["handle"],
                            "price": f"{float(v.get('price', 0)):,.0f}".replace(",", ".") + " ₺",
                            "image": img,
                            "url": f"{STORE}/products/{p['handle']}"})
                break
    # çeşitlilik için fiyatı yüksekten düşüğe sırala, ilk n
    out.sort(key=lambda x: -float(x["price"].replace(".", "").replace(" ₺", "")))
    return out[:max(n, 1)]

# ── İndirim önayarları ───────────────────────────────────────────────────────
DISCOUNTS = {
    "new250": {"code": "NEW250", "type": "fixed_amount", "amount": 250, "days": 30,
               "once_per_customer": True, "headline": "İlk alışverişe özel",
               "sub": "250 TL indirim"},
}

def discount_spec(key):
    """key: önayar adı ('new250') veya yüzde sayısı ('10')."""
    if not key:
        return None
    if key in DISCOUNTS:
        return dict(DISCOUNTS[key])
    if key.isdigit():
        return {"code": f"RETRO{key}", "type": "percentage", "amount": int(key), "days": 7,
                "once_per_customer": False, "headline": "Sana özel indirim", "sub": f"%{key} indirim"}
    return None

# ── Shopify indirim kodu ─────────────────────────────────────────────────────
def create_discount(spec):
    ends = (datetime.now(timezone.utc) + timedelta(days=spec.get("days", 7))).strftime("%Y-%m-%dT23:59:59Z")
    starts = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    val = f"-{spec['amount']}.0" if spec["type"] == "fixed_amount" else f"-{spec['amount']}"
    pr = shopify("POST", "price_rules.json", {"price_rule": {
        "title": spec["code"], "target_type": "line_item", "target_selection": "all",
        "allocation_method": "across", "value_type": spec["type"], "value": val,
        "customer_selection": "all", "once_per_customer": spec.get("once_per_customer", False),
        "starts_at": starts, "ends_at": ends, "usage_limit": None}})
    rid = pr["price_rule"]["id"]
    shopify("POST", f"price_rules/{rid}/discount_codes.json", {"discount_code": {"code": spec["code"]}})
    return spec["code"], ends

SOCIAL = [
    ("Instagram", "https://www.instagram.com/retrocameraland/?utm_source=email&utm_medium=brevo&utm_campaign=social&utm_content=Instagram"),
    ("YouTube",   "https://www.youtube.com/@RetroCameraLand?utm_source=email&utm_medium=brevo&utm_campaign=social&utm_content=Youtube"),
    ("TikTok",    "https://www.tiktok.com/@retrocameraland?utm_source=email&utm_medium=brevo&utm_campaign=social&utm_content=Tiktok"),
    ("Pinterest", "https://pinterest.com/retrocameraland/?utm_source=email&utm_medium=brevo&utm_campaign=social&utm_content=Pinterest"),
    ("LinkedIn",  "https://www.linkedin.com/company/retro-camera-land/?utm_source=email&utm_medium=brevo&utm_campaign=social&utm_content=linkedin"),
]
IG_DATA_JS = "/Users/onnoshot/Downloads/rcl-dashboard/data.js"

def instagram_posts(n=4):
    """data.js içindeki son IG gönderilerini oku (görsel + link + beğeni)."""
    try:
        txt = open(IG_DATA_JS, encoding="utf-8").read()
        m = re.search(r"const INSTAGRAM\s*=\s*(\{.*?\});", txt, re.S)
        data = json.loads(m.group(1))
        posts = data.get("posts") or data.get("media") or []
        out = []
        for p in posts:
            img = p.get("image") or p.get("media_url"); link = p.get("url") or p.get("permalink")
            if img and link:
                out.append({"img": img, "link": link, "likes": p.get("likes") or p.get("like_count") or 0})
        out.sort(key=lambda x: -x["likes"])
        return out[:n], data.get("followers", 0)
    except Exception as e:
        log(f"  IG verisi okunamadı: {str(e)[:80]}"); return [], 0

def rehost_to_shopify(url, key):
    """IG CDN görselini indirip Shopify tema asset'ine yükle → kalıcı CDN URL döndür."""
    import base64
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    img = urllib.request.urlopen(req, timeout=30).read()
    b64 = base64.b64encode(img).decode()
    r = shopify("PUT", "themes/147158499467/assets.json",
                {"asset": {"key": f"assets/{key}.jpg", "attachment": b64}})
    return r.get("asset", {}).get("public_url", "")

def instagram_section(campaign_id):
    posts, followers = instagram_posts(4)
    if not posts:
        return ""
    cells = ""
    for i, p in enumerate(posts):
        try:
            cdn = rehost_to_shopify(p["img"], f"rcl-ig-{i+1}")
        except Exception as e:
            log(f"  IG görsel {i+1} yeniden barındırılamadı: {str(e)[:70]}"); cdn = p["img"]
        cells += f"""<td width="25%" style="padding:3px;"><a href="{p['link']}?{UTM}{campaign_id}">
          <img src="{cdn}" width="124" alt="Instagram gönderisi" style="width:100%;border-radius:8px;display:block;"></a></td>"""
    foll = f"{followers:,}".replace(",", ".")
    return f"""<div style="margin:34px 0 8px;text-align:center;">
      <p style="margin:0 0 3px;font-size:15px;font-weight:700;color:#1a1a1a;">Bizi Instagram'da takip et</p>
      <p style="margin:0 0 12px;font-size:13px;color:#999;">@retrocameraland · {foll} takipçi</p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{cells}</tr></table></div>"""

def social_footer():
    pills = ""
    for name, url in SOCIAL:
        pills += f"""<a href="{url}" style="display:inline-block;margin:4px;padding:9px 15px;border:1px solid #ddd;border-radius:20px;text-decoration:none;font-size:12.5px;font-weight:600;color:#555;">{name}</a>"""
    return f'<div style="text-align:center;margin:26px 0 6px;">{pills}</div>'

# ── E-posta HTML şablonu (mail-uyumlu, inline stil) ──────────────────────────
def render_email(copy, products, discount=None, campaign_id=""):
    def card(p):
        link = f'{p["url"]}?{UTM}{campaign_id}'
        img = f'<img src="{p["image"]}" alt="{html.escape(p["title"])}" width="150" style="width:150px;max-width:150px;border-radius:12px;display:block;">' if p["image"] else ""
        # Vizör köşeli (retro kamera) çerçeveli görsel
        framed = f"""<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="position:relative;padding:6px;border:1.5px solid #e7e1d6;border-radius:14px;background:#faf8f4;">{img}
          <div style="position:absolute;top:2px;left:2px;width:13px;height:13px;border-top:2px solid {ACCENT};border-left:2px solid {ACCENT};border-radius:3px 0 0 0;"></div>
          <div style="position:absolute;top:2px;right:2px;width:13px;height:13px;border-top:2px solid {ACCENT};border-right:2px solid {ACCENT};border-radius:0 3px 0 0;"></div>
          <div style="position:absolute;bottom:2px;left:2px;width:13px;height:13px;border-bottom:2px solid {ACCENT};border-left:2px solid {ACCENT};border-radius:0 0 0 3px;"></div>
          <div style="position:absolute;bottom:2px;right:2px;width:13px;height:13px;border-bottom:2px solid {ACCENT};border-right:2px solid {ACCENT};border-radius:0 0 3px 0;"></div></td></tr></table>"""
        return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="rcl-card" style="margin:0 0 16px;"><tr>
          <td style="background:#ffffff;border:1px solid #eadfce;border-radius:18px;padding:16px;box-shadow:0 6px 22px rgba(40,30,15,.07);">
            <table role="presentation" width="100%"><tr>
              <td width="162" valign="top">{framed}</td>
              <td valign="top" style="padding-left:16px;">
                <span style="display:inline-block;background:{ACCENT};color:#ffffff;font-size:10.5px;font-weight:800;letter-spacing:.8px;text-transform:uppercase;padding:4px 10px;border-radius:6px;margin-bottom:9px;">● Tek Adet</span>
                <p style="margin:0 0 4px;font-size:17px;font-weight:800;color:#15120e;line-height:1.25;letter-spacing:-.01em;">{html.escape(p['title'])}</p>
                <p style="margin:0 0 13px;font-size:19px;color:{ACCENT};font-weight:800;">{p['price']}</p>
                <a href="{link}" class="rcl-btn-sm" style="background:#15120e;color:#ffffff;text-decoration:none;font-size:13px;font-weight:700;padding:12px 22px;border-radius:9px;display:inline-block;">İncele &rsaquo;</a>
              </td></tr></table></td></tr></table>"""
    cards = "".join(card(p) for p in products)
    disc_html = ""
    if discount:
        disc_html = f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0;"><tr>
          <td class="rcl-coupon" style="text-align:center;background:linear-gradient(135deg,{ACCENT},{ACCENT2});border-radius:14px;padding:20px;">
          <p style="margin:0 0 5px;color:#fff;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;opacity:.92;">{discount['headline']}</p>
          <p style="margin:0 0 5px;color:#fff;font-size:30px;font-weight:800;letter-spacing:3px;">{discount['code']}</p>
          <p style="margin:0;color:#fff;font-size:12px;opacity:.85;">{discount['sub']} · Ödeme sepetinde kodu ekle · {discount['days']} gün geçerli</p></td></tr></table>"""
    film = ('<table role="presentation" width="100%"><tr><td style="text-align:center;padding:4px 0 22px;">'
            f'<span style="display:inline-block;width:46px;height:3px;border-radius:3px;background:{ACCENT};"></span></td></tr></table>')
    ig = instagram_section(campaign_id)
    social = social_footer()
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  @keyframes rclFade{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
  @keyframes rclPulse{{0%,100%{{box-shadow:0 6px 20px rgba(255,59,59,.28)}}50%{{box-shadow:0 10px 32px rgba(255,59,59,.50)}}}}
  @keyframes rclShimmer{{0%{{background-position:-200% 0}}100%{{background-position:200% 0}}}}
  .rcl-wrap{{animation:rclFade .7s ease both}}
  .rcl-cta{{animation:rclPulse 2.4s ease-in-out infinite}}
  .rcl-card{{transition:transform .2s ease}} .rcl-card:hover{{transform:translateY(-2px)}}
  .rcl-btn-sm{{transition:opacity .2s}} .rcl-btn-sm:hover{{opacity:.82}}
  .rcl-brand{{background:linear-gradient(90deg,{ACCENT},#e9c07e,{ACCENT});background-size:200% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:rclShimmer 4s linear infinite}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style></head>
<body style="margin:0;background:{PAGE_BG};font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
<div class="rcl-wrap" style="max-width:580px;margin:0 auto;padding:30px 22px;">
  <p style="text-align:center;margin:0 0 20px;"><a href="{STORE}?{UTM}{campaign_id}"><img src="{LOGO_URL}" alt="Retrocameraland" height="48" style="height:48px;width:auto;display:inline-block;border:0;"></a></p>
  {film}
  <h1 style="font-size:27px;line-height:1.22;margin:0 0 14px;color:#1a1a1a;letter-spacing:-.02em;">{html.escape(copy['heading'])}</h1>
  <p style="font-size:16px;line-height:1.7;color:#54504a;margin:0 0 8px;">{html.escape(copy['intro'])}</p>
  {disc_html}
  {cards}
  <table role="presentation" width="100%"><tr><td style="text-align:center;padding:20px 0 6px;">
    <a href="{STORE}/collections/dijital-fotograf-makinesi?{UTM}{campaign_id}" class="rcl-cta" style="background:#1a1a1a;color:#fff;padding:16px 38px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">Tüm Koleksiyonu Gör &rsaquo;</a>
  </td></tr></table>
  {ig}
  <div style="height:1px;background:#e5e0d8;margin:28px 0 0;"></div>
  {social}
  <p style="font-size:12.5px;color:#a8a39a;line-height:1.7;margin:14px 0 0;text-align:center;">
    Retrocameraland · <a href="{STORE}" style="color:#a8a39a;">retrocameraland.com</a><br>
    Bu e-postayı abonemiz olduğun için aldın · <a href="mailto:{REPLYTO}?subject=Abonelikten%20çıkmak%20istiyorum" style="color:#bbb;">Abonelikten çık</a></p>
</div></body></html>"""

# ── Kamera Bulucu e-postası (interaktif test daveti) ─────────────────────────
def render_finder_email(copy, products, campaign_id=""):
    finder = f"{FINDER_URL}?{UTM}{campaign_id}"
    def card(p):
        link = f'{p["url"]}?{UTM}{campaign_id}'
        img = f'<img src="{p["image"]}" alt="{html.escape(p["title"])}" width="100%" style="width:100%;border-radius:10px 10px 0 0;display:block;border:1px solid #ece7df;border-bottom:none;">' if p["image"] else ""
        return f"""<td width="33%" valign="top" style="padding:4px;">
          <table role="presentation" width="100%" class="rcl-card" style="background:#fff;border:1px solid #ece7df;border-radius:11px;overflow:hidden;box-shadow:0 4px 16px rgba(40,30,15,.05);"><tr><td>{img}</td></tr>
          <tr><td style="padding:9px 10px 11px;">
            <p style="margin:0 0 3px;font-size:12.5px;font-weight:700;color:#1a1a1a;line-height:1.25;">{html.escape(p['title'])}</p>
            <p style="margin:0;font-size:13px;color:{ACCENT};font-weight:800;">{p['price']}</p>
          </td></tr></table></td>"""
    teaser = "".join(card(p) for p in products[:3])
    step = lambda n, t, d: f"""<td width="33%" valign="top" style="padding:8px;text-align:center;">
        <div style="width:38px;height:38px;line-height:38px;margin:0 auto 8px;border-radius:50%;background:#1a1a1a;color:#fff;font-weight:800;font-size:16px;">{n}</div>
        <p style="margin:0 0 3px;font-size:14px;font-weight:700;color:#1a1a1a;">{t}</p>
        <p style="margin:0;font-size:12.5px;color:#7a756d;line-height:1.45;">{d}</p></td>"""
    film = ('<table role="presentation" width="100%"><tr><td style="text-align:center;padding:4px 0 22px;">'
            f'<span style="display:inline-block;width:46px;height:3px;border-radius:3px;background:{ACCENT};"></span></td></tr></table>')
    ig = instagram_section(campaign_id)
    social = social_footer()
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  @keyframes rclFade{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
  @keyframes rclPulse{{0%,100%{{box-shadow:0 6px 22px rgba(255,59,59,.30)}}50%{{box-shadow:0 12px 36px rgba(255,59,59,.52)}}}}
  .rcl-wrap{{animation:rclFade .7s ease both}}
  .rcl-cta{{animation:rclPulse 2.4s ease-in-out infinite}}
  .rcl-card{{transition:transform .2s ease}} .rcl-card:hover{{transform:translateY(-2px)}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style></head>
<body style="margin:0;background:{PAGE_BG};font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
<div class="rcl-wrap" style="max-width:580px;margin:0 auto;padding:30px 22px;">
  <p style="text-align:center;margin:0 0 20px;"><a href="{STORE}?{UTM}{campaign_id}"><img src="{LOGO_URL}" alt="Retrocameraland" height="48" style="height:48px;width:auto;display:inline-block;border:0;"></a></p>
  {film}
  <p style="text-align:center;margin:0 0 10px;"><span style="display:inline-block;background:#ffe9e9;color:{ACCENT};font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;padding:5px 12px;border-radius:20px;">Yeni · Kamera Bulucu</span></p>
  <h1 style="font-size:27px;line-height:1.22;margin:0 0 14px;color:#1a1a1a;letter-spacing:-.02em;text-align:center;">{html.escape(copy['heading'])}</h1>
  <p style="font-size:16px;line-height:1.7;color:#54504a;margin:0 0 22px;text-align:center;">{html.escape(copy['intro'])}</p>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;"><tr>
    <td style="background:linear-gradient(150deg,#1a1a1a,#2b2b30);border-radius:18px;padding:30px 24px;text-align:center;">
      <p style="margin:0 0 6px;color:#bdbac4;font-size:12.5px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;">30 saniye · birkaç soru</p>
      <p style="margin:0 0 18px;color:#fff;font-size:20px;font-weight:800;line-height:1.3;">Yapay zeka, sana en uygun<br>retro kamerayı eşleştirsin</p>
      <a href="{finder}" class="rcl-cta" style="background:{ACCENT};color:#fff;padding:16px 40px;border-radius:11px;text-decoration:none;font-weight:800;font-size:17px;display:inline-block;">Kameranı Bul &rsaquo;</a>
    </td></tr></table>

  <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#1a1a1a;text-align:center;letter-spacing:.3px;">NASIL ÇALIŞIR</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 26px;"><tr>
    {step('1','Birkaç soru','Tarzın, bütçen ve nasıl kullanacağın')}
    {step('2','AI eşleştirir','Canlı stoktan sana göre seçer')}
    {step('3','Önerini gör','Sana en uygun kameralar, % uyumuyla')}
  </tr></table>

  <p style="margin:0 0 10px;font-size:14px;font-weight:700;color:#1a1a1a;">Şu an stokta, eşleşebileceğin kameralar</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px;"><tr>{teaser}</tr></table>
  <table role="presentation" width="100%"><tr><td style="text-align:center;padding:10px 0 6px;">
    <a href="{finder}" style="background:#1a1a1a;color:#fff;padding:14px 34px;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;display:inline-block;">Teste Başla &rsaquo;</a>
  </td></tr></table>
  {ig}
  <div style="height:1px;background:#e5e0d8;margin:28px 0 0;"></div>
  {social}
  <p style="font-size:12.5px;color:#a8a39a;line-height:1.7;margin:14px 0 0;text-align:center;">
    Retrocameraland · <a href="{STORE}" style="color:#a8a39a;">retrocameraland.com</a><br>
    Bu e-postayı abonemiz olduğun için aldın · <a href="mailto:{REPLYTO}?subject=Abonelikten%20çıkmak%20istiyorum" style="color:#bbb;">Abonelikten çık</a></p>
</div></body></html>"""

# ── Kampanya kaydı ───────────────────────────────────────────────────────────
def load_db():
    try: return json.load(open(CAMPAIGN_DB))
    except Exception: return []
def save_db(db): json.dump(db, open(CAMPAIGN_DB, "w"), ensure_ascii=False, indent=2)

# ── Önizleme üret ────────────────────────────────────────────────────────────
def preview(theme_key, discount_key=None):
    th = THEMES[theme_key]
    cid = f"{datetime.now().strftime('%Y%m%d')}-{theme_key}"
    products = instock_products(th["n"])
    disc = discount_spec(discount_key)
    copy = get_copy(theme_key, products, disc)
    if theme_key == "kamera-bulucu":
        html_out = render_finder_email(copy, products, cid)
    else:
        html_out = render_email(copy, products, disc, cid)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, f"{cid}_preview.html")
    open(path, "w").write(html_out)
    db = [c for c in load_db() if c["id"] != cid]
    db.append({"id": cid, "theme": theme_key, "name": th["name"], "subject": copy["subject"],
               "preview_text": copy.get("preview", ""), "created": datetime.now().isoformat(),
               "products": [p["title"] for p in products],
               "discount": disc["code"] if disc else None,
               "discount_spec": disc,
               "sent": 0, "status": "draft"})
    save_db(db)
    print(f"\n✅ Önizleme: {path}")
    print(f"   Konu: {copy['subject']}")
    print(f"   Ürün: {', '.join(p['title'] for p in products)}")
    if disc: print(f"   İndirim kodu: {disc['code']} ({disc['sub']}, {disc['days']} gün)")
    print(f"   Campaign ID: {cid}")
    print(f"\n   Aç:  open {path}")
    print(f"   Test:  python3 rcl-campaign.py send {cid} --test SENIN@MAIL.com")
    print(f"   Gönder (onaydan sonra):  python3 rcl-campaign.py send {cid}")
    return cid

# ── Brevo gönderim ───────────────────────────────────────────────────────────
def brevo_send(to_email, subject, html_body, tag, params=None):
    body = {"sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
            "to": [{"email": to_email}], "replyTo": {"email": REPLYTO, "name": SENDER_NAME},
            "subject": subject, "htmlContent": html_body, "tags": [tag],
            "headers": {"List-Unsubscribe": f"<mailto:{REPLYTO}?subject=unsubscribe>",
                        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}}
    req = urllib.request.Request("https://api.brevo.com/v3/smtp/email",
                                 data=json.dumps(body).encode(), method="POST")
    req.add_header("api-key", BREVO_KEY); req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def subscribers():
    """Abone e-postaları. Önce yerel liste (CSV'den üretilmiş), yoksa Shopify (PII açıksa)."""
    local = os.path.join(ROOT, "rcl-email-list.json")
    if os.path.exists(local):
        try:
            return json.load(open(local))
        except Exception:
            pass
    out, since = [], 0
    while True:
        r = shopify("GET", f"customers.json?limit=250&since_id={since}&fields=id,email,email_marketing_consent")
        cs = r.get("customers", [])
        if not cs:
            break
        for c in cs:
            st = (c.get("email_marketing_consent") or {}).get("state")
            if c.get("email") and st == "subscribed":
                out.append(c["email"])
        since = cs[-1]["id"]
        if len(cs) < 250:
            break
    return out

def send(cid, test=None):
    db = load_db(); camp = next((c for c in db if c["id"] == cid), None)
    if not camp: print("Kampanya bulunamadı:", cid); return
    path = os.path.join(PREVIEW_DIR, f"{cid}_preview.html")
    html_body = open(path).read()
    if test:
        print("Test maili →", test); print(brevo_send(test, "[TEST] " + camp["subject"], html_body, "test-" + cid)); return
    # indirim kodu varsa gönderimde gerçekten oluştur (henüz yoksa)
    if camp.get("discount_spec") and not camp.get("discount_created"):
        try:
            create_discount(camp["discount_spec"]); camp["discount_created"] = True
            print(f"İndirim kodu oluşturuldu: {camp['discount_spec']['code']} ({camp['discount_spec']['sub']})")
        except Exception as e:
            log(f"⚠ indirim kodu oluşturulamadı: {str(e)[:120]}")
    subs = subscribers()
    sent_list = camp.setdefault("sent_emails", [])
    already = set(sent_list)
    todo = [e for e in subs if e not in already]
    DAILY = 300
    batch = todo[:DAILY]
    print(f"Toplam abone: {len(subs)} · Bugüne dek gönderilen: {len(already)} · Bu turda: {len(batch)} (limit {DAILY}/gün)")
    sent = 0
    for e in batch:
        try:
            brevo_send(e, camp["subject"], html_body, cid); sent += 1; sent_list.append(e); time.sleep(0.25)
        except urllib.error.HTTPError as ex:
            log(f"⚠ {e}: {ex.code} {ex.read().decode()[:100]}")
    camp["sent"] = len(sent_list)
    remaining = len(todo) - len(batch)
    camp["status"] = "sent" if remaining <= 0 else "partial"
    camp["last_sent"] = datetime.now().isoformat()
    save_db(db)
    print(f"✅ {sent} gönderildi (toplam {len(sent_list)}). " +
          (f"Kalan {remaining} için yarın tekrar 'send' çalıştır." if remaining else "Tüm abonelere ulaşıldı."))

# ── Brevo istatistik (dashboard için) ────────────────────────────────────────
def stats(cid):
    def bv(p):
        req = urllib.request.Request("https://api.brevo.com/v3/" + p)
        req.add_header("api-key", BREVO_KEY); req.add_header("accept", "application/json")
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    agg = bv(f"smtp/statistics/aggregatedReport?tag={urllib.parse.quote(cid)}&days=90")
    print(json.dumps(agg, ensure_ascii=False, indent=2))
    return agg

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "preview":
        d = None
        if "--discount" in sys.argv: d = sys.argv[sys.argv.index("--discount") + 1]
        preview(sys.argv[2], d)
    elif cmd == "send":
        t = sys.argv[sys.argv.index("--test") + 1] if "--test" in sys.argv else None
        send(sys.argv[2], t)
    elif cmd == "stats":
        stats(sys.argv[2])
    elif cmd == "list":
        for c in load_db():
            print(f"  {c['id']} · {c['name']} · {c['status']} · gönderilen:{c.get('sent',0)} · {c['subject']}")
    else:
        print(__doc__)
