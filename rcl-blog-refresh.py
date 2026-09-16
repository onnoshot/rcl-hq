#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Blog Refresh — görsel + SEO başlık/meta güncelleyici (Claude destekli)
==========================================================================
retrocameraland.com bloglarının (1) kapak görselini RetroCameraLand Instagram
medyası + YouTube thumbnail havuzundan en uygun olanla, (2) SEO başlık ve meta
açıklamasını Claude ile yeniden üreterek günceller. Her değişiklik öncesi mevcut
değerleri yedekler (geri alınabilir).

Kullanım:
  python3 rcl-blog-refresh.py                 # DRY-RUN (yazma yok), planı yazdırır
  python3 rcl-blog-refresh.py --apply         # canlıya uygular
  python3 rcl-blog-refresh.py --apply --limit 3
  python3 rcl-blog-refresh.py --apply --offset 50 --limit 50
  python3 rcl-blog-refresh.py --restore       # yedekten geri yükler (son değerler)

Model: Claude Haiku 4.5 (bu hacimde uygun/hızlı). Anahtar .env → ANTHROPIC_API_KEY
"""
import sys, os, re, json, time, urllib.request, urllib.parse, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrocameraland_api import shopify, log, BLOG_ID

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_FILE = os.path.join(ROOT, "rcl-blog-refresh-backup.jsonl")
TG_TOKEN   = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID = "7904534693"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

def _env(key):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, "")

ANTHROPIC_KEY = _env("ANTHROPIC_API_KEY")

def tg_send(text):
    try:
        data = urllib.parse.urlencode({"chat_id": TG_CHAT_ID, "text": text,
                                       "parse_mode": "HTML", "disable_web_page_preview": "true"}).encode()
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data), timeout=20)
    except Exception as e:
        log(f"⚠ TG: {e}")

# ── Claude ─────────────────────────────────────────────────────────────────────
def claude(system, user, max_tokens=600):
    import anthropic
    c = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    r = c.messages.create(model=CLAUDE_MODEL, max_tokens=max_tokens,
                          system=system, messages=[{"role": "user", "content": user}])
    return r.content[0].text

# ── Görsel havuzu: Instagram + YouTube ─────────────────────────────────────────
YT_VIDEOS = [
    {"id": "TxLwf8D_C7Q", "text": "Canon PowerShot SD400 inceleme y2k"},
    {"id": "SdvyqeBglac", "text": "Canon IXUS 160 inceleme"},
    {"id": "k6ccwjtkhgw", "text": "Panasonic Lumix DC-TZ99 inceleme"},
    {"id": "To_AIAUFESk", "text": "Sanyo Xacti HD1 video kamera"},
    {"id": "N6iINZdtf_o", "text": "Retrocameraland tanıtım retro kamera koleksiyon"},
    {"id": "D4MhR4I21T0", "text": "retro kamera y2k estetik genel"},
    {"id": "-mrJ8maR2eo", "text": "retro kamera inceleme dijital"},
    {"id": "Cit6csTi8gE", "text": "retrocameraland kamera fotoğraf"},
    {"id": "fNZrON7-dco", "text": "retro kamera çekim fotoğraf"},
]

# RetroCameraLand Pinterest panosu — görsel kaynağı
PINTEREST_BOARD_RSS = "https://tr.pinterest.com/retrocameraland/everyday-aesthetic.rss"

def fetch_pinterest_board(rss=PINTEREST_BOARD_RSS):
    """everyday-aesthetic panosundan pinleri (yüksek çözünürlük + caption) çek."""
    out = []
    try:
        req = urllib.request.Request(rss, headers={"User-Agent": "Mozilla/5.0"})
        xml = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
            tm = re.search(r"<title>(.*?)</title>", it, re.S)
            title = re.sub(r"<[^>]+>", "", tm.group(1)).strip() if tm else ""
            im = re.search(r"https://i\.pinimg\.com/[^\"'<> ]+\.(?:jpg|png)", it)
            if not im:
                continue
            src = re.sub(r"/\d+x\d*/", "/originals/", im.group(0))  # tam boyut
            out.append({"src": src, "text": title[:200], "source": "pinterest", "like": 0})
    except Exception as e:
        log(f"⚠ Pinterest RSS hatası: {e}")
    return out

def build_image_pool():
    pool = fetch_pinterest_board()
    log(f"✓ Pinterest panosu (everyday-aesthetic): {len(pool)} görsel")
    # YouTube thumbnail — model bazlı bloglar için takviye
    for v in YT_VIDEOS:
        pool.append({"src": f"https://img.youtube.com/vi/{v['id']}/maxresdefault.jpg",
                     "text": v["text"], "source": "youtube", "like": 0})
    log(f"✓ Toplam görsel havuzu: {len(pool)} (Pinterest + YouTube)")
    return pool

# ── SEO dosya adı ──────────────────────────────────────────────────────────────
_TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")
def slugify(text, maxlen=60):
    s = (text or "").translate(_TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:maxlen].rstrip("-") or "retro-kamera")

def download_b64(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    import base64
    return base64.b64encode(urllib.request.urlopen(req, timeout=30).read()).decode()

# ── Görsel eşleştirme (Claude seçer; fallback token-overlap) ────────────────────
def match_image_fallback(pool, title, keyword):
    q = (title + " " + keyword).lower()
    qtok = set(re.findall(r"\w+", q))
    best, bs = None, -1
    for i, im in enumerate(pool):
        itok = set(re.findall(r"\w+", im["text"].lower()))
        s = len(qtok & itok) * 10 + (im["like"] / 50.0)
        if s > bs:
            best, bs = i, s
    # eşleşme yoksa başlık hash'iyle çeşitlilik
    if bs <= 0:
        best = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(pool)
    return best

# ── Tek blog için Claude: SEO başlık + meta + görsel index ─────────────────────
def plan_blog(pool, title, body_text, keyword):
    pool_list = "\n".join(f"{i}: [{p['source']}] {p['text'][:70]}" for i, p in enumerate(pool))
    system = (
        "Sen retrocameraland.com (Türkiye'nin en büyük retro/Y2K dijital kamera mağazası) için "
        "uzman bir Türk SEO editörüsün. Mevcut bir blog yazısının SEO başlığını ve meta açıklamasını "
        "iyileştir ve verilen görsel havuzundan yazıya en uygun kapak görselini seç. "
        "Klişe/şablon dilden kaçın; net, arama-niyetine uygun, tıklanmaya değer yaz."
    )
    user = f"""Blog mevcut başlık: {title}
Ana keyword (tahmini): {keyword}
Yazının ilk bölümü: {body_text[:600]}

Görsel havuzu (index: [kaynak] açıklama):
{pool_list}

Görevler:
1. SEO başlık: 52-68 karakter, keyword içersin, Türkçe, tıklanır, abartısız.
2. Meta açıklama: 148-165 karakter, keyword ilk 60 karakterde, eyleme çağıran ama spam olmayan.
3. image_index: havuzdan yazıya EN UYGUN görselin index'i (kamera modeli/temaya göre; uygun yoksa marka-genel bir RCL görseli).

SADECE şu JSON: {{"seo_title":"...","meta_desc":"...","image_index":0}}"""
    try:
        raw = claude(system, user, max_tokens=400)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            d = json.loads(m.group(0))
            idx = int(d.get("image_index", -1))
            if not (0 <= idx < len(pool)):
                idx = match_image_fallback(pool, title, keyword)
            st = _fix_title(d.get("seo_title", "").strip(), keyword)
            md = _fix_meta(d.get("meta_desc", "").strip(), keyword)
            return st, md, idx
    except Exception as e:
        log(f"  ⚠ Claude plan hatası: {e}")
    idx = match_image_fallback(pool, title, keyword)
    return "", "", idx


def _fix_title(t, kw):
    if not t:
        return t
    if len(t) > 68:
        t = t[:66].rstrip(" —:|,") + "…"
    if len(t) < 50:
        t = (t + f" — Retro Dijital Kamera Rehberi")[:68]
    return t


def _fix_meta(m, kw):
    """Meta'yı 148-165 karaktere getir."""
    if not m:
        return m
    pads = [
        " retrocameraland.com'da test edilmiş ve garantili modeller.",
        " Fiyat, öneri ve detaylar retrocameraland.com'da.",
        " Hemen keşfedin.",
    ]
    for p in pads:
        if len(m) >= 148:
            break
        if not m.endswith("."):
            m += "."
        m += p
    return m[:165].rstrip()

# ── Yedek / geri yükleme ───────────────────────────────────────────────────────
def backup(record):
    with open(BACKUP_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def get_seo_metafields(art_id):
    out = {}
    try:
        r = shopify("GET", f"articles/{art_id}/metafields.json")
        for mf in r.get("metafields", []):
            if mf.get("namespace") == "seo":
                out[mf["key"]] = {"id": mf["id"], "value": mf.get("value", "")}
    except Exception:
        pass
    return out

def apply_blog(art, seo_title, meta_desc, image_src, image_slug=None):
    aid = art["id"]
    article = {"id": aid}
    if seo_title:
        article["title"] = seo_title
    if image_src:
        alt = seo_title or art.get("title", "")
        slug = image_slug or slugify(alt)
        # SEO dosya adı için attachment (base64) ile yükle; olmazsa src'ye düş
        try:
            article["image"] = {"attachment": download_b64(image_src),
                                 "filename": f"{slug}.jpg", "alt": alt}
        except Exception as e:
            log(f"   ⚠ görsel indirilemedi, src ile: {str(e)[:60]}")
            article["image"] = {"src": image_src, "alt": alt}
    # metafields: seo.title + seo.description
    mfs = []
    if seo_title:
        mfs.append({"namespace": "seo", "key": "title", "value": seo_title, "type": "single_line_text_field"})
    if meta_desc:
        mfs.append({"namespace": "seo", "key": "description", "value": meta_desc, "type": "single_line_text_field"})
    if mfs:
        article["metafields"] = mfs
    shopify("PUT", f"blogs/{BLOG_ID}/articles/{aid}.json", {"article": article})

# ── Ana akış ───────────────────────────────────────────────────────────────────
def iter_articles(limit, offset):
    """235 blog sayfalı çekilir (Shopify limit 250)."""
    arts = []
    r = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,handle,image,body_html,tags")
    arts = r.get("articles", [])
    arts.sort(key=lambda a: a.get("id", 0), reverse=True)
    return arts[offset:offset + limit] if limit else arts[offset:]

def run(apply=False, limit=0, offset=0):
    mode = "CANLI UYGULAMA" if apply else "DRY-RUN (yazma yok)"
    log(f"\n{'═'*56}\nRCL Blog Refresh — {mode}\n{'═'*56}")
    pool = build_image_pool()
    if not pool:
        log("✗ Görsel havuzu boş — durduruldu"); return
    arts = iter_articles(limit, offset)
    log(f"İşlenecek blog: {len(arts)} (offset={offset})")

    done = img_done = seo_done = fail = 0
    recent = []  # son seçilen görsel index'leri — ardışık tekrarı önle
    for i, art in enumerate(arts, 1):
        title = art.get("title", "")
        body = re.sub(r"<[^>]+>", " ", art.get("body_html", "") or "")
        body = re.sub(r"\s+", " ", body).strip()
        tags = art.get("tags", "")
        tag_list = [t.strip() for t in tags.split(",") if t.strip().lower() not in ("retrocameraland", "y2k", "retro kamera")]
        keyword = (tag_list[0] if tag_list else title).strip()

        seo_title, meta_desc, idx = plan_blog(pool, title, body, keyword)
        # Ardışık çeşitlilik: son 4 blogda kullanılan görseli tekrar seçme
        if idx in recent and len(pool) > 5:
            order = sorted(range(len(pool)),
                           key=lambda j: -(len(set(re.findall(r"\w+", (title+" "+keyword).lower())) &
                                            set(re.findall(r"\w+", pool[j]["text"].lower()))) * 10 + pool[j]["like"]/50.0))
            for j in order:
                if j not in recent:
                    idx = j; break
        recent.append(idx); recent = recent[-4:]
        image_src = pool[idx]["src"]
        cur_img = (art.get("image") or {}).get("src", "")

        log(f"\n[{i}/{len(arts)}] {title[:46]}")
        log(f"   → SEO başlık: {seo_title[:60] or '(üretilemedi, atlanıyor)'}")
        log(f"   → meta ({len(meta_desc)} kar): {meta_desc[:70]}")
        log(f"   → görsel: [{pool[idx]['source']}] {image_src[:60]}")

        if apply:
            try:
                img_slug = slugify(seo_title or keyword or title)
                backup({"id": art["id"], "old_title": title, "old_image": cur_img,
                        "old_seo": get_seo_metafields(art["id"]),
                        "new_title": seo_title, "new_meta": meta_desc,
                        "new_image": image_src, "new_image_file": img_slug + ".jpg"})
                apply_blog(art, seo_title, meta_desc, image_src, img_slug)
                if seo_title or meta_desc: seo_done += 1
                if image_src and image_src != cur_img: img_done += 1
                done += 1
                time.sleep(0.6)  # Shopify rate limit
            except Exception as e:
                fail += 1
                log(f"   ✗ Hata: {str(e)[:140]}")

    summary = (f"<b>🖼️ Blog Refresh — {mode}</b>\n"
               f"İşlenen: {len(arts)} blog\n"
               f"✅ Güncellenen: {done} | 🖼️ görsel: {img_done} | 📝 SEO: {seo_done} | ❌ hata: {fail}\n"
               f"Görsel havuzu: {len(pool)} (Pinterest everyday-aesthetic + YouTube)")
    log(f"\n{summary}")
    if apply:
        tg_send(summary)

def fix_bad_images(substrs, apply=False):
    """Görsel dosya adında verilen ifadelerden (ör. kart_okuyucu) birini taşıyan blogların
    görselini Pinterest panosundan yenisiyle değiştir. Başlık/meta'ya DOKUNMAZ (sadece görsel)."""
    subs = [s.strip().lower() for s in substrs if s.strip()]
    pool = build_image_pool()
    if not pool:
        log("✗ Görsel havuzu boş"); return
    arts = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,image")["articles"]
    targets = [a for a in arts if any(s in ((a.get("image") or {}).get("src", "").lower()) for s in subs)]
    log(f"Hedef (kötü görselli) blog: {len(targets)}  [aranan: {', '.join(subs)}]")

    recent, done, fail = [], 0, 0
    for i, art in enumerate(targets, 1):
        title = art.get("title", "")
        idx = match_image_fallback(pool, title, title)
        if idx in recent and len(pool) > 5:
            for j in range(len(pool)):
                if j not in recent:
                    idx = j; break
        recent.append(idx); recent = recent[-5:]
        image_src = pool[idx]["src"]
        slug = slugify(title)
        cur = (art.get("image") or {}).get("src", "")
        log(f"[{i}/{len(targets)}] {title[:46]}  → [{pool[idx]['source']}] {slug}.jpg")
        if apply:
            try:
                backup({"id": art["id"], "old_title": title, "old_image": cur,
                        "old_seo": {}, "new_title": "", "new_meta": "",
                        "new_image": image_src, "new_image_file": slug + ".jpg"})
                apply_blog(art, "", "", image_src, slug)  # sadece görsel
                done += 1; time.sleep(0.6)
            except Exception as e:
                fail += 1; log(f"   ✗ {str(e)[:120]}")
    msg = (f"<b>🖼️ Kötü görsel düzeltme</b>\nHedef: {len(targets)} | "
           f"✅ değişen: {done} | ❌ hata: {fail}\nKaynak: Pinterest everyday-aesthetic")
    log("\n" + msg)
    if apply:
        tg_send(msg)


def restore():
    """Yedekten en son kaydedilen eski değerleri geri yükler."""
    if not os.path.exists(BACKUP_FILE):
        log("Yedek yok."); return
    latest = {}
    for line in open(BACKUP_FILE, encoding="utf-8"):
        r = json.loads(line)
        latest.setdefault(r["id"], r)  # İLK kayıt kazanır = gerçek orijinal değer
    log(f"Geri yüklenecek: {len(latest)} blog")
    for aid, r in latest.items():
        try:
            article = {"id": aid, "title": r["old_title"]}
            if r.get("old_image"):
                article["image"] = {"src": r["old_image"]}
            mfs = []
            for k, v in (r.get("old_seo") or {}).items():
                mfs.append({"namespace": "seo", "key": k, "value": v["value"], "type": "single_line_text_field"})
            if mfs: article["metafields"] = mfs
            shopify("PUT", f"blogs/{BLOG_ID}/articles/{aid}.json", {"article": article})
            time.sleep(0.5)
        except Exception as e:
            log(f"  ✗ {aid}: {str(e)[:100]}")
    log("✓ Geri yükleme bitti")

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--restore" in a:
        restore(); sys.exit(0)
    if "--fix-image" in a:
        subs = a[a.index("--fix-image") + 1].split(",")
        fix_bad_images(subs, apply="--apply" in a); sys.exit(0)
    apply = "--apply" in a
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else 0
    offset = int(a[a.index("--offset") + 1]) if "--offset" in a else 0
    run(apply=apply, limit=limit, offset=offset)
