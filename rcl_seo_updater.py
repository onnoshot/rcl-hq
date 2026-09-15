#!/usr/bin/env python3
"""
RCL SEO Blog Güncelleyici v1
Mevcut blogları analiz edip düşük SEO puanlıları otomatik iyileştirir.

- Tüm Shopify blogu çeker, her makaleyi SEO puanlar
- Eşik altı (varsayılan < 90) makaleleri önceliğe göre sıralar
- Groq ile: meta açıklama, FAQ, iç link, ilk paragraf düzeltir
- Shopify'a yazar + Telegram bildirimi gönderir

Kullanım:
  python3 rcl_seo_updater.py                  # 10 makale işle, eşik=90
  python3 rcl_seo_updater.py --limit 20       # 20 makale
  python3 rcl_seo_updater.py --min-score 75   # sadece <75 olanlar
  python3 rcl_seo_updater.py --dry-run        # değişiklik yazmadan test
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# ── Ayarlar ──────────────────────────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
SHOPIFY_TOKEN  = "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"
SHOPIFY_STORE  = "retrocameraland.myshopify.com"
BLOG_ID        = "91197866123"
GROQ_KEY       = "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"
GROQ_WRITER    = "openai/gpt-oss-20b"
TG_TOKEN       = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID     = "7904534693"

INTERNAL_LINKS = [
    "https://retrocameraland.com/collections/all",
    "https://retrocameraland.com/collections/dijital-kameralar",
    "https://retrocameraland.com/collections/retro-kameralar",
    "https://retrocameraland.com/pages/hakkimizda",
]

# ── Loglama ──────────────────────────────────────────────────────────────────
_log_lines = []
def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    _log_lines.append(line)

# ── Shopify ──────────────────────────────────────────────────────────────────
def shopify(method, path, body=None, retries=3):
    url  = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    data = json.dumps(body).encode() if body else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
            req.add_header("Content-Type",  "application/json")
            req.add_header("Accept",        "application/json")
            with urllib.request.urlopen(req, timeout=30) as r:
                raw      = r.read()
                link_hdr = r.headers.get("Link", "")
            return json.loads(raw), link_hdr
        except urllib.error.HTTPError as e:
            body_err = e.read().decode()[:300]
            if e.code == 429:
                wait = 10 * (attempt + 1)
                log(f"  Shopify 429 — {wait}s bekleniyor...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Shopify {method} {path} → {e.code}: {body_err}")
    raise RuntimeError("Shopify 3 denemede başarısız")


def fetch_all_articles():
    """Tüm blog makalelerini sayfalı şekilde çeker."""
    articles = []
    path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,body_html,tags,handle,published_at"
    while path:
        data, link = shopify("GET", path)
        arts = data.get("articles", [])
        articles.extend(arts)
        log(f"  Çekildi: {len(articles)} makale")
        # Cursor-based pagination
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r'<[^>]+\?([^>]+)>', part)
                if m:
                    next_url = f"blogs/{BLOG_ID}/articles.json?" + m.group(1)
        path = next_url
        if path:
            time.sleep(0.6)
    return articles


def get_article_metafields(article_id):
    """Makalenin SEO metafield'larını döndürür."""
    data, _ = shopify("GET", f"articles/{article_id}/metafields.json")
    return data.get("metafields", [])


def upsert_metafield(article_id, metafields, namespace, key, value, field_type):
    """Mevcut metafield'ı günceller veya yeni oluşturur."""
    existing = next((m for m in metafields
                     if m.get("namespace") == namespace and m.get("key") == key), None)
    if existing:
        shopify("PUT", f"articles/{article_id}/metafields/{existing['id']}.json", {
            "metafield": {"id": existing["id"], "value": value, "type": field_type}
        })
    else:
        shopify("POST", f"articles/{article_id}/metafields.json", {
            "metafield": {"namespace": namespace, "key": key,
                          "value": value, "type": field_type}
        })
    time.sleep(0.6)


def update_article_body(article_id, new_body):
    shopify("PUT", f"blogs/{BLOG_ID}/articles/{article_id}.json", {
        "article": {"id": article_id, "body_html": new_body}
    })
    time.sleep(0.6)


# ── SEO Scoring (rcl-seo-blog-agent ile aynı mantık) ─────────────────────────
def score_seo(title, meta_desc, body_html, keyword):
    score, issues = 0, []
    kw       = keyword.lower()
    kw_words = kw.split()

    def kw_in(text):
        t = text.lower()
        return kw in t or all(w in t for w in kw_words)

    # Title (20)
    if kw_in(title):
        score += 12
    else:
        issues.append("NO_KW_TITLE")
    tl = len(title)
    if 45 <= tl <= 70:
        score += 8
    elif tl > 0:
        score += 3
        if tl < 45:
            issues.append("TITLE_SHORT")
        else:
            issues.append("TITLE_LONG")

    # Meta (15)
    if kw_in(meta_desc):
        score += 8
    else:
        issues.append("NO_KW_META")
    ml = len(meta_desc)
    if 140 <= ml <= 170:
        score += 7
    elif ml >= 100:
        score += 3
        issues.append("META_SHORT") if ml < 140 else issues.append("META_LONG")
    else:
        issues.append("META_MISSING") if ml < 10 else issues.append("META_SHORT")

    # Word count (20)
    clean = re.sub(r'<[^>]+>', ' ', body_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    wc    = len(clean.split())
    if wc >= 1500:
        score += 20
    elif wc >= 1000:
        score += 13
        issues.append("WORDCOUNT_LOW")
    elif wc >= 700:
        score += 7
        issues.append("WORDCOUNT_LOW")
    else:
        issues.append("WORDCOUNT_VERY_LOW")

    # Headings (15)
    h2 = len(re.findall(r'<h2[^>]*>', body_html, re.I))
    h3 = len(re.findall(r'<h3[^>]*>', body_html, re.I))
    score += (10 if h2 >= 5 else 6 if h2 >= 3 else 0)
    if h2 < 3: issues.append("H2_FEW")
    score += (5 if h3 >= 2 else 2 if h3 == 1 else 0)
    if h3 < 2: issues.append("H3_FEW")

    # FAQ (10)
    if re.search(r'(sık sorulan|SSS|FAQ|soru[^a-z])', body_html, re.I):
        score += 10
    else:
        issues.append("NO_FAQ")

    # Internal links (5)
    il = len(re.findall(r'href="https://retrocameraland\.com', body_html))
    if il >= 2:
        score += 5
    elif il == 1:
        score += 2
        issues.append("FEW_ILINKS")
    else:
        issues.append("NO_ILINKS")

    # Keyword density (10)
    kw_count = clean.lower().count(kw)
    kw_parts = kw.split()
    if len(kw_parts) > 1 and kw_count < 5:
        kw_count = max(kw_count, clean.lower().count(kw_parts[0] + " " + kw_parts[1]) // 2)
    density = (kw_count / max(wc, 1)) * 100
    if 0.5 <= density <= 4.0:
        score += 10
    elif 0.2 <= density <= 5.5:
        score += 5
    else:
        issues.append("DENSITY_BAD")

    # First paragraph (5)
    fp = re.search(r'<p[^>]*>(.*?)</p>', body_html, re.DOTALL | re.I)
    if fp and kw_in(re.sub(r'<[^>]+>', '', fp.group(1))):
        score += 5
    else:
        issues.append("NO_KW_FIRST_PARA")

    return score, issues


# ── Keyword Extraction ────────────────────────────────────────────────────────
BRAND_WORDS = ["sony", "canon", "fujifilm", "nikon", "olympus", "casio", "kodak",
               "panasonic", "samsung", "minolta", "pentax", "ricoh", "sanyo", "konica",
               "agfa", "leica", "vivitar", "yashica", "polaroid"]

def extract_keyword(title, tags_str):
    """Başlık ve tag'lardan ana anahtar kelimeyi çıkarır."""
    tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
    title_l = title.lower()

    # Tag'larda kamera model ismi ara
    for tag in tags:
        if any(b in tag for b in BRAND_WORDS) and len(tag) > 4:
            return tag

    # Başlıktan marka + model çıkar
    for brand in BRAND_WORDS:
        if brand in title_l:
            # Başlıktaki marka ve sonrasındaki 2-3 kelimeyi al
            idx = title_l.index(brand)
            words = title_l[idx:].split()[:3]
            candidate = " ".join(words).rstrip(",:—-")
            # Gereksiz kelimeleri kırp
            candidate = re.sub(r'\s+(inceleme|rehber|nedir|nasıl|fiyat|karşılaştırma).*$', '', candidate)
            if len(candidate) > 4:
                return candidate

    # Başlığın ilk anlamlı kısmını kullan (kolon veya tire öncesi)
    for sep in [":", " —", " -", "|"]:
        if sep in title:
            kw = title.split(sep)[0].strip().lower()
            if len(kw) > 6:
                return kw

    # Son çare: başlıktan stopword çıkar
    stopwords = {"en", "iyi", "ile", "için", "ve", "veya", "bir", "bu", "da", "de",
                 "nasıl", "neden", "nedir", "rehberi", "rehber", "inceleme", "kılavuz",
                 "türkiye", "satın", "alma", "yıl", "2025", "2026", "2024"}
    words = [w for w in title.lower().split() if w not in stopwords and len(w) > 2]
    return " ".join(words[:3]) if words else title.lower()[:30]


# ── Groq Çağrıları ────────────────────────────────────────────────────────────
def groq_call(prompt, system, max_tokens=600):
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=GROQ_WRITER,
                messages=[{"role": "system", "content": system},
                          {"role": "user",   "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.70,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                wait = 180 if attempt == 0 else 300
                log(f"  Groq rate limit — {wait}s bekleniyor...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Groq başarısız")


def fix_meta_desc(title, keyword, body_snippet, current_meta):
    """140-165 karakter, keyword'ü içeren, Türkçe meta açıklama üretir."""
    sys = (
        "Sen Retrocameraland.com için SEO meta açıklama yazan uzmansın. "
        "KURAL: TAM OLARAK 148-163 karakter, Türkçe, keyword ilk 30 karakterde, "
        "doğal ve tıklanabilir. Sadece tek satır metin döndür, başka hiçbir şey yazma."
    )
    prompt = (
        f"Başlık: {title}\n"
        f"Anahtar Kelime: {keyword}\n"
        f"Mevcut meta ({len(current_meta)} kar): {current_meta[:100]}\n"
        f"İçerik özeti: {body_snippet[:200]}\n\n"
        f"Bu makale için 148-163 karakter arası Türkçe SEO meta açıklama yaz. "
        f"'{keyword}' kelimesi ilk 30 karakterde geçmeli. "
        f"retrocameraland.com sitesine uygun, satın alma isteği uyandıran bir cümle ekle."
    )
    raw = groq_call(prompt, sys, max_tokens=200)
    # Temizle
    raw = re.sub(r'^["\'`]|["\'`]$', '', raw.strip())
    raw = raw.split("\n")[0].strip()
    # Uzunluk garantisi
    if len(raw) < 140:
        ext = f" retrocameraland.com'da incele, Türkiye'ye hızlı kargo seçeneğiyle."
        raw = (raw + ext)[:165]
    return raw[:165]


def fix_first_para(title, keyword, body_html):
    """İçeriğin ilk paragrafına keyword eklenmiş versiyon üretir."""
    sys = (
        "Retrocameraland.com için Türkçe blog yazarısın. "
        "Sadece istenen paragrafı yaz, başka hiçbir şey ekleme."
    )
    prompt = (
        f"Başlık: {title}\nAnahtar Kelime: {keyword}\n\n"
        f"'{keyword}' ile başlayan, 3-4 cümlelik giriş paragrafı yaz. "
        f"Türkçe, samimi, SEO'ya uygun. Sadece metin, HTML tag'ı yok."
    )
    raw = groq_call(prompt, sys, max_tokens=200)
    raw = raw.strip().split("\n")[0]
    return f"<p>{raw}</p>"


def generate_faq(title, keyword, body_snippet):
    """5 soruluk HTML FAQ bölümü üretir."""
    sys = (
        "Retrocameraland.com için Türkçe SEO FAQ bölümü yazarısın. "
        "HTML formatında, schema markup uyumlu, sadece istenen bölümü döndür."
    )
    prompt = (
        f"Başlık: {title}\nAnahtar Kelime: {keyword}\n"
        f"İçerik: {body_snippet[:300]}\n\n"
        f"Bu blog için 5 soru-cevap içeren Türkçe SSS bölümü yaz. "
        f"Format:\n"
        f"<h2>Sık Sorulan Sorular</h2>\n"
        f"<h3>Soru 1?</h3><p>Cevap</p>\n"
        f"<h3>Soru 2?</h3><p>Cevap</p>\n"
        f"... (5 soru)\n"
        f"Her cevap 2-3 cümle. '{keyword}' en az 2 soruda geçmeli."
    )
    raw = groq_call(prompt, sys, max_tokens=1200)
    raw = re.sub(r'^```html?\s*', '', raw.strip(), flags=re.I)
    raw = re.sub(r'\s*```$', '', raw.strip())
    return raw


def add_internal_links(body_html, keyword):
    """Body HTML'e 2 iç link ekler (zaten yoksa)."""
    existing = len(re.findall(r'href="https://retrocameraland\.com', body_html))
    if existing >= 2:
        return body_html

    # Eklenmek üzere uygun link bloku
    links_block = (
        f'\n<p>Retrocameraland koleksiyonumuzu incelemek için '
        f'<a href="https://retrocameraland.com/collections/all">tüm kameralarımıza</a> '
        f'veya <a href="https://retrocameraland.com/collections/dijital-kameralar">'
        f'dijital kamera koleksiyonumuza</a> göz atabilirsiniz.</p>\n'
    )

    # Sonuncu </p> veya </h2> öncesine ekle
    match = list(re.finditer(r'</p>|</h2>', body_html, re.I))
    if match and len(match) >= 3:
        ins = match[-3].end()  # Sondan 3. tag'in ardına
        return body_html[:ins] + links_block + body_html[ins:]
    else:
        return body_html + links_block


# ── Telegram ─────────────────────────────────────────────────────────────────
def telegram(msg):
    try:
        data = json.dumps({"chat_id": TG_CHAT_ID, "text": msg,
                           "parse_mode": "HTML"}).encode()
        req  = urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        log(f"  Telegram hatası: {e}")


# ── Ana Akış ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit",     type=int, default=10,
                        help="İşlenecek maksimum makale sayısı")
    parser.add_argument("--min-score", type=int, default=90,
                        help="Bu puanın altındakileri iyileştir")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Shopify'a yazma, sadece analiz et")
    args = parser.parse_args()

    start_time = time.time()
    date_str   = datetime.now().strftime("%Y-%m-%d")

    log("=" * 60)
    log(f"RCL SEO Güncelleyici — eşik: {args.min_score} — limit: {args.limit}"
        + (" [DRY-RUN]" if args.dry_run else ""))
    log("=" * 60)

    # 1. Tüm makaleleri çek
    log("📥 Makaleler çekiliyor...")
    articles = fetch_all_articles()
    log(f"  Toplam: {len(articles)} makale")

    # 2. Her makaleyi SEO puanla
    log("🔍 SEO analizi yapılıyor...")
    scored = []
    for i, a in enumerate(articles):
        keyword = extract_keyword(a["title"], a.get("tags", ""))
        body    = a.get("body_html") or ""
        # Meta: şimdilik boş — ileride metafield ile çekeceğiz
        s, issues = score_seo(a["title"], "", body, keyword)
        scored.append({"article": a, "score": s, "issues": issues,
                       "keyword": keyword})
        if (i + 1) % 50 == 0:
            log(f"  {i+1}/{len(articles)} analiz edildi")

    # 3. Düşük puanlıları filtrele, en kötüden başla
    to_fix = [x for x in scored if x["score"] < args.min_score]
    to_fix.sort(key=lambda x: x["score"])
    log(f"  {len(to_fix)} makale {args.min_score} altında → {args.limit} tanesi işlenecek")

    results = []
    updated  = 0
    errors   = 0

    for item in to_fix[:args.limit]:
        a       = item["article"]
        issues  = item["issues"]
        keyword = item["keyword"]
        old_score = item["score"]
        title   = a["title"]

        log(f"\n── {title[:55]} [{old_score}]")
        log(f"   Keyword: {keyword}")
        log(f"   Sorunlar: {', '.join(issues)}")

        try:
            # Mevcut metafield'ları çek
            metafields = []
            if not args.dry_run:
                metafields = get_article_metafields(a["id"])
                time.sleep(0.5)

            current_meta = next(
                (m["value"] for m in metafields
                 if m.get("namespace") == "seo" and m.get("key") == "description"),
                ""
            )

            body_html = a.get("body_html") or ""
            clean_text = re.sub(r'<[^>]+>', ' ', body_html)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            body_snippet = clean_text[:500]

            changes = []
            new_body = body_html

            # — Meta açıklaması —
            needs_meta = (
                "NO_KW_META"   in issues or
                "META_MISSING" in issues or
                "META_SHORT"   in issues
            )
            if needs_meta:
                log("   → Meta açıklama yazılıyor...")
                new_meta = fix_meta_desc(title, keyword, body_snippet, current_meta)
                log(f"   ✓ Meta ({len(new_meta)} kar): {new_meta[:80]}...")
                if not args.dry_run:
                    upsert_metafield(a["id"], metafields,
                                     "seo", "description",
                                     new_meta, "single_line_text_field")
                changes.append(f"meta({len(new_meta)}kar)")
                current_meta = new_meta

            # — İlk paragraf —
            if "NO_KW_FIRST_PARA" in issues:
                log("   → İlk paragraf düzeltiliyor...")
                new_para = fix_first_para(title, keyword, new_body)
                # Mevcut ilk <p> varsa değiştir, yoksa başa ekle
                fp_match = re.search(r'<p[^>]*>.*?</p>', new_body, re.DOTALL | re.I)
                if fp_match:
                    new_body = new_body[:fp_match.start()] + new_para + new_body[fp_match.end():]
                else:
                    new_body = new_para + new_body
                changes.append("ilk-para")
                log("   ✓ İlk paragraf güncellendi")

            # — İç linkler —
            if "NO_ILINKS" in issues or "FEW_ILINKS" in issues:
                log("   → İç linkler ekleniyor...")
                new_body = add_internal_links(new_body, keyword)
                changes.append("iç-link")
                log("   ✓ İç linkler eklendi")

            # — FAQ —
            if "NO_FAQ" in issues:
                log("   → FAQ bölümü yazılıyor...")
                faq_html = generate_faq(title, keyword, body_snippet)
                # CTA blokundan önce ekle (varsa), yoksa body sonuna
                cta_pattern = r'<div[^>]*text-align:center[^>]*>.*?</div>'
                cta_m = re.search(cta_pattern, new_body, re.DOTALL)
                if cta_m:
                    new_body = (new_body[:cta_m.start()] +
                                "\n" + faq_html + "\n" +
                                new_body[cta_m.start():])
                else:
                    new_body = new_body + "\n" + faq_html
                changes.append("FAQ")
                log("   ✓ FAQ eklendi")

            # — Body güncelle —
            if any(c in changes for c in ["ilk-para", "iç-link", "FAQ"]):
                if not args.dry_run:
                    update_article_body(a["id"], new_body)
                log(f"   ✓ Body güncellendi ({', '.join(changes)})")

            # — Yeni skoru hesapla —
            new_score, _ = score_seo(title, current_meta, new_body, keyword)
            gain = new_score - old_score
            log(f"   📈 Skor: {old_score} → {new_score} (+{gain})")

            results.append({
                "title": title, "keyword": keyword,
                "old_score": old_score, "new_score": new_score,
                "changes": changes, "id": a["id"]
            })
            updated += 1

        except Exception as e:
            log(f"   ❌ HATA: {e}")
            errors += 1

        time.sleep(1.0)  # Shopify rate limit için

    # ── Rapor ─────────────────────────────────────────────────────────────────
    elapsed = int(time.time() - start_time)
    total_analyzed = len(scored)
    above_90 = sum(1 for x in scored if x["score"] >= 90)
    avg_score = sum(x["score"] for x in scored) // max(len(scored), 1)

    report_lines = [
        f"# RCL SEO Güncelleme Raporu — {date_str}",
        f"",
        f"## Genel Durum",
        f"- Toplam makale: **{total_analyzed}**",
        f"- 90+ skor: **{above_90}** (%{above_90*100//max(total_analyzed,1)})",
        f"- Ortalama skor: **{avg_score}**",
        f"- İşlenen: **{updated}** güncellendi, **{errors}** hata",
        f"- Süre: {elapsed}s",
        f"",
        f"## SEO Dağılımı",
    ]

    brackets = [
        ("≥90 Mükemmel",  [x for x in scored if x["score"] >= 90]),
        ("75-89 İyi",      [x for x in scored if 75 <= x["score"] < 90]),
        ("60-74 Orta",     [x for x in scored if 60 <= x["score"] < 75]),
        ("<60 Kritik",     [x for x in scored if x["score"] < 60]),
    ]
    for label, group in brackets:
        report_lines.append(f"- {label}: **{len(group)}** makale")

    if results:
        report_lines += ["", "## Güncellenen Makaleler"]
        for r in sorted(results, key=lambda x: x["new_score"] - x["old_score"], reverse=True):
            gain_str = f"+{r['new_score']-r['old_score']}" if r["new_score"] >= r["old_score"] else str(r["new_score"]-r["old_score"])
            report_lines.append(
                f"- **{r['title'][:60]}**  \n"
                f"  Skor: {r['old_score']} → **{r['new_score']}** ({gain_str}) | "
                f"Değişiklikler: {', '.join(r['changes']) or '—'}"
            )

    if to_fix[args.limit:]:
        report_lines += ["", f"## Bekleyenler ({len(to_fix)-args.limit} makale)"]
        for item in to_fix[args.limit:args.limit+20]:
            report_lines.append(
                f"- [{item['score']}] {item['article']['title'][:60]}  "
                f"({', '.join(item['issues'][:3])})"
            )

    report_path = os.path.join(SCRIPT_DIR, "outputs",
                               f"{date_str}_seo-update.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    log(f"\n✓ Rapor: {report_path}")

    # ── Telegram ──────────────────────────────────────────────────────────────
    gain_avg = ""
    if results:
        avg_gain = sum(r["new_score"] - r["old_score"] for r in results) // len(results)
        gain_avg = f" (ort. +{avg_gain})"

    tg_msg = (
        f"<b>📊 SEO Güncelleme Tamamlandı</b>\n"
        f"Analiz: {total_analyzed} makale | Ort. skor: {avg_score}\n"
        f"90+: {above_90} makale (%{above_90*100//max(total_analyzed,1)})\n"
        f"Güncellendi: {updated} makale{gain_avg}\n"
        f"Süre: {elapsed}s"
    )
    telegram(tg_msg)
    log("✓ Telegram bildirimi gönderildi")

    log("\n" + "=" * 60)
    log(f"✅ Tamamlandı | {updated} güncellendi | {errors} hata | {elapsed}s")
    log("=" * 60)


if __name__ == "__main__":
    main()
