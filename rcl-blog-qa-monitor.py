#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Blog QA Monitor — "Hermes blogları takip etsin"
====================================================
retrocameraland.com bloglarını periyodik denetler ve Telegram'a (Hermes kanalı) rapor atar.

Denetim boyutları (her blog 0-100 puanlanır):
  1. SEO           — rcl-seo-blog-agent.score_seo (başlık/meta/kelime/H2/FAQ/iç link/yoğunluk)
  2. AI-arama (AEO)— JSON-LD schema (Article/FAQPage), SSS yapısı, soru-başlıklar, net cevaplar
  3. Yönlendirme   — ürün deep-link sayısı, koleksiyon linki, sosyal medya, YouTube embed
  4. İnsan vs Slop — Groq LLM jüri: deneyim/birinci-tekil mi, klişe/şablon AI tonu mu
  5. Mobil/Animasyon— taşan tablo riski, responsive sarmalayıcı, animasyon/transition

Kullanım:  python3 rcl-blog-qa-monitor.py [adet]   (varsayılan 8 son blog)
"""
import sys, os, re, json, importlib.util, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrocameraland_api import shopify, log, BLOG_ID

# ── score_seo'yu mevcut ajandan içe al (kod tekrarı yok) ───────────────────────
def _load_agent():
    spec = importlib.util.spec_from_file_location(
        "rcl_agent", os.path.join(os.path.dirname(os.path.abspath(__file__)), "rcl-seo-blog-agent.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# ── Telegram (Hermes kanalı = aynı sohbet) ─────────────────────────────────────
TG_TOKEN   = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID = "7904534693"
GROQ_KEY   = "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"

def tg_send(text):
    try:
        data = urllib.parse.urlencode({
            "chat_id": TG_CHAT_ID, "text": text,
            "parse_mode": "HTML", "disable_web_page_preview": "true",
        }).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()).get("ok", False)
    except Exception as e:
        log(f"⚠ TG hata: {e}")
        return False

def groq_judge(agent, title, text):
    """İçeriğin insan-deneyimi mi yoksa AI-slop mu olduğuna LLM ile karar ver.
    Ajanın çalışan Groq SDK fonksiyonunu (agent.groq) yeniden kullanır."""
    system = (
        "Sen kıdemli bir içerik editörüsün. Türkçe bir blog yazısını değerlendir. "
        "SADECE JSON döndür: {\"human_score\":0-100, \"slop\":true/false, \"verdict\":\"1 cümle Türkçe\", \"fix\":\"1 öneri Türkçe\"}. "
        "human_score yüksek = gerçek deneyim/birinci-tekil anlatı/özgün ses. "
        "Düşük = şablon, klişe, genel AI tonu, deneyim yok."
    )
    user = f"Başlık: {title}\n\nİçerik (kısaltılmış):\n{text[:3500]}\n\nSADECE JSON."
    try:
        raw = agent.groq(system, user, max_tokens=250, temperature=0.3)
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception as e:
        log(f"  ⚠ Groq jüri hatası: {e}")
    return {"human_score": None, "slop": None, "verdict": "değerlendirilemedi", "fix": ""}

def get_meta_desc(art_id):
    """Blogun gerçek SEO meta açıklamasını metafield'den çek (doğru SEO skoru için)."""
    try:
        r = shopify("GET", f"articles/{art_id}/metafields.json")
        for mf in r.get("metafields", []):
            if mf.get("namespace") == "seo" and mf.get("key") == "description":
                return mf.get("value", "") or ""
    except Exception:
        pass
    return ""

# ── Tek blog denetimi ──────────────────────────────────────────────────────────
CLICHE = ["zaman tüneli", "yolculuğa çıkalım", "hazırsanız", "gelin birlikte",
          "kemerlerinizi bağlayın", "büyülü dünya", "hayal gücünüzün sınırları",
          "unutmayın ki", "sonuç olarak", "kısacası", "özetle", "adeta bir"]

def audit_blog(agent, art, meta=""):
    title = art.get("title", "")
    html  = art.get("body_html", "") or ""
    tags  = art.get("tags", "")
    text  = re.sub(r"<[^>]+>", " ", html)
    text  = re.sub(r"\s+", " ", text).strip()

    # Hedef keyword tahmini: ilk anlamlı tag (jenerik 'retrocameraland' hariç)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()
                and t.strip().lower() not in ("retrocameraland", "y2k", "retro kamera")]
    kw = (tag_list[0] if tag_list else (tags.split(",")[0] if tags else title)).strip().lower()
    seo_score, _ = agent.score_seo(title, meta or title, html, kw)

    # AI-arama (AEO)
    has_schema = "application/ld+json" in html
    has_faq    = ("sık sorulan" in html.lower()) or ("<h3" in html.lower() and "?" in html)
    q_headings = len(re.findall(r"<h[23][^>]*>[^<]*\?", html, re.I))
    aeo = 0
    aeo += 40 if has_schema else 0
    aeo += 25 if has_faq else 0
    aeo += min(20, q_headings * 5)
    aeo += 15 if re.search(r"<(ul|ol|table)", html, re.I) else 0  # taranabilir liste/tablo
    aeo = min(100, aeo)

    # Yönlendirme
    product_links = len(re.findall(r'href="[^"]*?/products/', html, re.I))
    coll_links    = len(re.findall(r'href="[^"]*?/collections/', html, re.I))
    socials = sum(1 for s in ["instagram.com", "tiktok.com", "youtube.com", "pinterest", "linkedin.com"]
                  if s in html.lower())
    yt_embed = ("youtube.com/embed" in html.lower()) or ("youtube-nocookie" in html.lower())
    redirect = 0
    redirect += min(40, product_links * 20)       # ürün deep-link en değerli
    redirect += 15 if coll_links else 0
    redirect += min(30, socials * 6)
    redirect += 15 if yt_embed else 0
    redirect = min(100, redirect)

    # Mobil / Animasyon
    tables = len(re.findall(r"<table", html, re.I))
    has_overflow_wrap = bool(re.search(r"overflow-x\s*:\s*auto", html, re.I))
    wide_table_risk = tables > 0 and not has_overflow_wrap
    has_anim = bool(re.search(r"@keyframes|animation\s*:|transition\s*:|data-aos", html, re.I))
    mobile = 100
    if wide_table_risk: mobile -= 40   # geniş tablo mobilde taşar
    if not has_anim:    mobile -= 30   # animasyon yok
    mobile = max(0, mobile)

    # Klişe yoğunluğu (slop sinyali)
    cliche_hits = sum(text.lower().count(c) for c in CLICHE)

    return {
        "title": title, "wc": len(text.split()),
        "seo": seo_score, "aeo": aeo, "redirect": redirect, "mobile": mobile,
        "has_schema": has_schema, "has_faq": has_faq, "q_headings": q_headings,
        "product_links": product_links, "coll_links": coll_links,
        "socials": socials, "yt_embed": yt_embed,
        "tables": tables, "wide_table_risk": wide_table_risk, "has_anim": has_anim,
        "cliche": cliche_hits, "text": text,
    }

def run(limit=8, judge=True):
    agent = _load_agent()
    log(f"RCL Blog QA Monitor — son {limit} blog deneteniyor...")
    r = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit={limit}&fields=id,title,handle,created_at,body_html,tags")
    arts = r.get("articles", [])
    if not arts:
        tg_send("⚠️ RCL Blog QA: hiç blog bulunamadı."); return

    rows = []
    for a in arts:
        meta = get_meta_desc(a["id"])
        d = audit_blog(agent, a, meta)
        if judge:
            j = groq_judge(agent, d["title"], d["text"])
            d.update({"human": j.get("human_score"), "slop": j.get("slop"),
                      "verdict": j.get("verdict", ""), "fix": j.get("fix", "")})
        rows.append(d)
        hs = d.get("human")
        log(f"  {d['title'][:40]:42} SEO{d['seo']:>3} AEO{d['aeo']:>3} Yön{d['redirect']:>3} "
            f"Mob{d['mobile']:>3} İnsan{hs if hs is not None else '—'}")

    # Ortalamalar
    def avg(k):
        vals = [x[k] for x in rows if isinstance(x.get(k), (int, float))]
        return round(sum(vals)/len(vals)) if vals else 0
    a_seo, a_aeo, a_red, a_mob, a_hum = avg("seo"), avg("aeo"), avg("redirect"), avg("mobile"), avg("human")
    n_schema = sum(1 for x in rows if x["has_schema"])
    n_prod   = sum(1 for x in rows if x["product_links"] > 0)
    n_slop   = sum(1 for x in rows if x.get("slop") is True)
    n_anim   = sum(1 for x in rows if x["has_anim"])

    def bar(v):
        return "🟢" if v >= 85 else "🟡" if v >= 60 else "🔴"

    lines = [f"<b>📊 RCL Blog QA Raporu</b> — son {len(rows)} blog\n"]
    lines.append(f"{bar(a_seo)} SEO: <b>{a_seo}</b>/100")
    lines.append(f"{bar(a_aeo)} AI-arama (schema/FAQ): <b>{a_aeo}</b>/100  "
                 f"({n_schema}/{len(rows)} schema'lı)")
    lines.append(f"{bar(a_red)} Yönlendirme: <b>{a_red}</b>/100  ({n_prod}/{len(rows)} ürün deep-link)")
    lines.append(f"{bar(a_mob)} Mobil/Animasyon: <b>{a_mob}</b>/100  ({n_anim}/{len(rows)} animasyonlu)")
    if a_hum:
        lines.append(f"{bar(a_hum)} İnsan tonu: <b>{a_hum}</b>/100  ({n_slop}/{len(rows)} AI-slop işareti)")
    lines.append("\n<b>Öne çıkan sorunlar:</b>")
    if n_schema < len(rows):
        lines.append("• JSON-LD schema yok → AI/zengin sonuçlarda görünmez")
    if n_prod < len(rows):
        lines.append("• Çoğu blog ürün sayfasına değil koleksiyona link veriyor")
    if n_anim < len(rows):
        lines.append("• Animasyon yok, geniş tablolar mobilde taşabilir")
    if n_slop:
        lines.append(f"• {n_slop} blogda şablon/AI-slop tonu")

    # En zayıf 2 blog
    worst = sorted(rows, key=lambda x: x["seo"] + x["aeo"] + x["redirect"] + x["mobile"])[:2]
    lines.append("\n<b>En zayıf 2 blog:</b>")
    for w in worst:
        v = w.get("verdict", "")
        lines.append(f"• {w['title'][:46]} — {v[:70]}")

    report = "\n".join(lines)
    ok = tg_send(report)
    log(f"\n{'='*50}\nRapor Telegram'a gönderildi: {ok}\n{'='*50}")
    print(report.replace("<b>", "").replace("</b>", ""))
    return rows

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    run(n)
