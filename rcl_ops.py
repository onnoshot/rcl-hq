#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Ops — Hermes komut/sorgu asistanı (Claude destekli)
=======================================================
Telegram'dan (Hermes) gelen komutları aksiyona çevirir ve cevap üretir.

Komutlar (Türkçe doğal dil — anahtar kelimeyle eşleşir):
  trafik / analytics / girişler   → GA4 trafik + trend + organik pay
  satış / sipariş / ciro          → Shopify son 30 gün sipariş & ciro
  rakip / competitor              → rakip marka analizi (canlı arama + Claude)
  ton / kalite / seo / google     → blog kalite + AI-arama + Google durumu (proxy)
  blog düzelt / görsel / refresh   → blog görsel+SEO yenileme (küçük parti)
  rapor / durum / özet            → hepsinin kısa birleşik özeti

CLI:  python3 rcl_ops.py [analytics|sales|competitors|quality|digest]
Bot entegrasyonu:  from rcl_ops import route;  handled, reply = route(text)
"""
import sys, os, re, json, subprocess, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from retrocameraland_api import shopify, log

GA_FILE = os.path.join(ROOT, "agents/retrocameraland-analytics/data/ga_data.json")

def _env(key):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, "")

ANTHROPIC_KEY = _env("ANTHROPIC_API_KEY")
CLAUDE_MODEL  = "claude-sonnet-4-6"   # analiz/yorum için; kısa görevler haiku'ya çekilebilir

def claude(system, user, max_tokens=900, model=None):
    import anthropic
    c = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    r = c.messages.create(model=model or CLAUDE_MODEL, max_tokens=max_tokens,
                          system=system, messages=[{"role": "user", "content": user}])
    return r.content[0].text

def ddg_search(query, n=6):
    """Hafif DuckDuckGo lite araması (rakip/canlı veri için)."""
    try:
        url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        hits = re.findall(r'<a[^>]+class="result-link"[^>]*>(.*?)</a>', html, re.S)
        titles = [re.sub(r"<[^>]+>", "", h).strip() for h in hits]
        return [t for t in titles if t][:n]
    except Exception as e:
        log(f"⚠ DDG: {e}")
        return []

# ── 1. Trafik (GA4) ────────────────────────────────────────────────────────────
def analytics_report():
    try:
        d = json.load(open(GA_FILE))
    except Exception as e:
        return f"⚠️ GA4 verisi okunamadı: {e}"
    p7, p30 = d.get("period_7d", {}), d.get("period_30d", {})
    # 7g trend: günlük listeden son 7 vs önceki 7
    daily = d.get("daily", [])
    trend = ""
    if len(daily) >= 14:
        last7 = sum(x["sessions"] for x in daily[-7:])
        prev7 = sum(x["sessions"] for x in daily[-14:-7])
        if prev7:
            chg = (last7 - prev7) / prev7 * 100
            trend = f"{'📈 +' if chg>=0 else '📉 '}{chg:.0f}% (önceki 7 güne göre)"
    sources = d.get("sources", [])
    organic = next((s["pct"] for s in sources if "organic search" in s["name"].lower()), None)
    top_src = ", ".join(f"{s['name']} %{s['pct']:.0f}" for s in sources[:4])
    devices = d.get("devices", {})
    mob = devices.get("mobile", {}).get("pct", 0)

    lines = ["<b>📊 Trafik (GA4)</b>"]
    lines.append(f"Son 7g: <b>{p7.get('sessions',0):,}</b> oturum, {p7.get('activeUsers',0):,} kullanıcı  {trend}")
    lines.append(f"Son 30g: <b>{p30.get('sessions',0):,}</b> oturum, {p30.get('screenPageViews',0):,} sayfa görüntüleme")
    lines.append(f"Bounce: %{p30.get('bounceRate',0)*100:.0f} | Ort. süre: {p30.get('averageSessionDuration',0):.0f}sn | Mobil: %{mob:.0f}")
    if organic is not None:
        lines.append(f"🔎 Organik arama payı: <b>%{organic:.0f}</b>")
    lines.append(f"Kaynaklar: {top_src}")
    # Claude yorumu
    try:
        c = claude("Sen bir e-ticaret büyüme analistisin. Kısa, somut, Türkçe yorum yap (max 3 cümle). Markdown kullanma.",
                   f"RetroCameraLand GA4 özeti:\n{json.dumps({'7d':p7,'30d':p30,'sources':sources[:5],'organic_pct':organic}, ensure_ascii=False)}\n"
                   f"Trend: {trend}. Site retro dijital kamera satıyor. Trafik artıyor mu, organik durum nasıl, ne yapmalı?",
                   max_tokens=200)
        lines.append(f"\n<b>💡 Yorum:</b> {c.strip()}")
    except Exception:
        pass
    return "\n".join(lines)

# ── 2. Satış (Shopify) ─────────────────────────────────────────────────────────
def sales_report():
    try:
        from datetime import datetime, timedelta
        since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
        r = shopify("GET", f"orders.json?status=any&created_at_min={since}&limit=250&fields=id,total_price,created_at,financial_status")
        orders = r.get("orders", [])
        paid = [o for o in orders if o.get("financial_status") in ("paid", "partially_paid")]
        revenue = sum(float(o.get("total_price", 0)) for o in orders)
        lines = ["<b>🛒 Satış (Shopify, son 30g)</b>"]
        lines.append(f"Sipariş: <b>{len(orders)}</b> (ödenen: {len(paid)})")
        lines.append(f"Ciro: <b>{revenue:,.0f} ₺</b>")
        if orders:
            aov = revenue / len(orders)
            lines.append(f"Ortalama sepet: {aov:,.0f} ₺")
        # GA4 oturum başına dönüşüm (kabaca)
        try:
            d = json.load(open(GA_FILE)); s30 = d.get("period_30d", {}).get("sessions", 0)
            if s30:
                lines.append(f"Dönüşüm (sipariş/oturum): <b>%{len(orders)/s30*100:.2f}</b>")
        except Exception:
            pass
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Satış verisi alınamadı: {str(e)[:140]}"

# ── 3. Rakip analizi ───────────────────────────────────────────────────────────
def competitor_report():
    queries = ["retro dijital kamera satın al türkiye", "y2k kamera mağaza türkiye",
               "ikinci el dijital kamera ccd türkiye", "vintage fotoğraf makinesi satış"]
    hits = []
    for q in queries:
        hits += ddg_search(q, 5)
    ctx = "\n".join(f"- {h}" for h in hits[:20]) or "(canlı sonuç alınamadı)"
    system = ("Sen retrocameraland.com için bir pazar/rekabet analistisin. Türkiye retro/Y2K dijital "
              "kamera pazarını biliyorsun. Telegram HTML (<b></b>) ile kısa, somut analiz yaz; markdown kullanma.")
    user = (f"Canlı arama başlıkları:\n{ctx}\n\n"
            "Şunları ver: 1) Öne çıkan 3-5 rakip/platform (Dolap, Letgo, sahibinden, niş mağazalar dahil), "
            "2) RetroCameraLand'in farkı/avantajı, 3) Rakiplerin yaptığı ama bizim eksik olduğumuz 2-3 şey, "
            "4) 2 somut aksiyon önerisi. Kısa tut.")
    try:
        return "<b>🏁 Rakip Analizi</b>\n" + claude(system, user, max_tokens=700).strip()
    except Exception as e:
        return f"⚠️ Rakip analizi hatası: {str(e)[:140]}"

# ── 4. Ton / Kalite / SEO / Google ─────────────────────────────────────────────
def quality_report():
    """Blog QA monitörünü çağırır (ton, AI-arama, yönlendirme, mobil) ve Google durumunu ekler."""
    out = "<b>🔍 Blog Kalite & SEO</b>\n"
    try:
        p = subprocess.run([sys.executable, os.path.join(ROOT, "rcl-blog-qa-monitor.py"), "6"],
                           capture_output=True, text=True, timeout=300)
        # monitör zaten Telegram'a atıyor; CLI çıktısının özetini al
        tail = "\n".join(l for l in p.stdout.splitlines() if any(k in l for k in
                ("SEO:", "AI-arama", "Yönlendirme", "Mobil", "İnsan tonu", "•")))
        out += tail or "(QA monitör çalıştı, Telegram'a rapor gönderildi)"
    except Exception as e:
        out += f"QA monitör hatası: {str(e)[:120]}"
    # Google durumu — GSC yok, organik trafik proxy
    try:
        d = json.load(open(GA_FILE))
        org = next((s["pct"] for s in d.get("sources", []) if "organic search" in s["name"].lower()), None)
        if org is not None:
            out += f"\n\n<b>🔎 Google:</b> Organik arama trafiğin payı %{org:.0f}. " \
                   f"(Gerçek anahtar-kelime sıralaması için Search Console bağlantısı gerekir.)"
    except Exception:
        pass
    return out

# ── 5. Blog düzelt / görsel yenile ─────────────────────────────────────────────
def blog_fix(n=5):
    try:
        p = subprocess.run([sys.executable, os.path.join(ROOT, "rcl-blog-refresh.py"),
                            "--apply", "--limit", str(n)],
                           capture_output=True, text=True, timeout=600)
        tail = "\n".join(p.stdout.splitlines()[-4:])
        return f"<b>🖼️ Blog Yenileme ({n} blog)</b>\n<code>{tail[-500:]}</code>"
    except Exception as e:
        return f"⚠️ Blog yenileme hatası: {str(e)[:140]}"

# ── Komut yönlendirme ──────────────────────────────────────────────────────────
def route(text):
    """(handled: bool, reply: str|None) döner. Eşleşme yoksa (False, None)."""
    t = (text or "").lower()
    def has(*ks): return any(k in t for k in ks)

    if has("rapor", "durum", "özet", "genel bak"):
        parts = [analytics_report(), sales_report(), quality_report()]
        return True, "\n\n".join(parts)
    if has("trafik", "analytics", "giriş", "ziyaret", "ga4", "oturum"):
        return True, analytics_report()
    if has("satış", "satis", "sipariş", "siparis", "ciro", "gelir", "dönüş", "donus"):
        return True, sales_report()
    if has("rakip", "rekabet", "competitor", "pazar"):
        return True, competitor_report()
    if has("ton", "kalite", "seo", "google", "sıralama", "ai arama", "ai-arama", "slop"):
        return True, quality_report()
    if has("blog düzelt", "blog duzelt", "görsel güncelle", "gorsel guncelle", "refresh", "yenile", "kapak"):
        m = re.search(r"\d+", t)
        return True, blog_fix(int(m.group()) if m else 5)
    return False, None

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "digest"
    fn = {"analytics": analytics_report, "sales": sales_report,
          "competitors": competitor_report, "quality": quality_report,
          "digest": lambda: "\n\n".join([analytics_report(), sales_report()])}.get(cmd)
    print((fn() if fn else "bilinmeyen komut").replace("<b>", "").replace("</b>", ""))
