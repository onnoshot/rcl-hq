#!/usr/bin/env python3
"""
rcl-seo-blog-agent.py — Retrocameraland Günlük SEO Blog Ajanı v3
Görev: Web + X/Twitter trendlerini araştır, retrocameraland odaklı
       min 90 SEO puanlı Türkçe blog yaz, YouTube video göm, yayınla.
Yazım: Claude Code CLI (birincil, abonelik) → Gemini → Groq → Claude API (son çare)
Zamanlama: 00:00, 12:00, 15:00, 19:00, 23:00
"""

import sys, os, json, time, re, subprocess, shutil
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log, BLOG_ID, SOCIAL_BLOCK, CTA_BLOCK

class DuplicateTopicError(RuntimeError):
    """Shopify handle çakışması: bu konu zaten canlıda yayınlanmış demektir.
    run() bunu yakalayınca yeniden DENEMEZ (deneme aynı handle'a çarpar) — sadece atlar."""
    pass

# ── Config ─────────────────────────────────────────────────────────────────────
TG_TOKEN      = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID    = "7904534693"
BATCH_COUNT   = 2
MIN_SEO_SCORE = 90

# API keys
def _load_env_key(var_name):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        for line in open(env_path).readlines():
            if line.startswith(f'{var_name}='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(var_name, '')

ANTHROPIC_KEY = _load_env_key('ANTHROPIC_API_KEY')
GEMINI_KEY    = _load_env_key('GEMINI_API_KEY')
GROQ_KEY      = _load_env_key('GROQ_API_KEY')
MAX_RETRIES   = 3

STATE_FILE         = '/Users/onnoshot/Downloads/Agentlar/published-topics.json'
KEYWORD_STATE_FILE = '/Users/onnoshot/Downloads/Agentlar/published-keywords.json'
IMAGE_STATE_FILE   = '/Users/onnoshot/Downloads/Agentlar/published-images.json'
ENTITY_STATE_FILE  = '/Users/onnoshot/Downloads/Agentlar/published-entities.json'
KEYWORD_COOLDOWN_DAYS = 45
ENTITY_COOLDOWN_DAYS  = 60  # aynı marka+model (ör. "fujifilm t200 vs sony dsc-t9") farklı
                            # "açı"yla (5 altın kural, ucuz seçim, yıl güncellemesi) yeniden
                            # yazılmasın diye — keyword string'i farklı olsa bile yakalar
LOG_DIR    = '/Users/onnoshot/Downloads/Agentlar/outputs'

CHANNEL_ID = "UCq0jJ7knS1MDtNgx8DtJCvw"
CHANNEL_URL = f"https://www.youtube.com/@RetroCameraLand?utm_source=blog&utm_medium=embed&utm_campaign=blog"

# retrocameraland YouTube videoları — konu etiketiyle
YT_VIDEOS = [
    # ── Kanaldan çekilen en güncel videolar (2026-07-17 itibarıyla) — pick_yt_video()
    # bunları keyword/tag örtüşmesine göre eşleştirir; retrocameraland-youtube-fetch.py
    # her saat bunları retrocameraland-hq-dashboard.html'deki YOUTUBE bloğuna güncelliyor.
    {"id": "pZJB6mBWYRg", "title": "Samsung WB350F İncelemesi: 21x Zoom Yapan Retro Dijital Kamera!",
     "tags": ["samsung", "wb350f", "zoom"]},
    {"id": "LLXSMuhZAko", "title": "Panasonic Lumix TZ91: Cebe Sığan 30x Zoom Leica Lensli Dijital Kamera",
     "tags": ["panasonic", "lumix", "tz91", "zoom", "leica"]},
    {"id": "lh4DVJUz1QY", "title": "Küçük anların büyük hisleri — Lumix TZ91",
     "tags": ["panasonic", "lumix", "tz91"]},
    {"id": "fiWC7WOtCtk", "title": "Kullanımı Kolay Kompakt Dijital Kamera! Lumix DMC LS70",
     "tags": ["panasonic", "lumix", "ls70", "kompakt"]},
    {"id": "LjyZRaLNGcc", "title": "Casio Exilim Dijital Fotoğraf Makinesi (2005) Y2K Fotoğraf Çek!",
     "tags": ["casio", "exilim", "y2k"]},
    {"id": "ZRzvt8SJEG8", "title": "Sanyo Xacti Dijital Kamera ile Y2K VLOG (2005)",
     "tags": ["sanyo", "xacti", "y2k", "vlog"]},
    {"id": "8XWAJXORa9c", "title": "Fujifilm Finepix V60 Retro Dijital Kamera ile tatlı fotoğraflar",
     "tags": ["fujifilm", "finepix", "v60"]},
    {"id": "4mC6-c_-JYc", "title": "Kompakt Canon Dijital Kamera ile Manzara Fotoğrafçılığı",
     "tags": ["canon", "manzara", "kompakt"]},
    {"id": "TxLwf8D_C7Q", "title": "Canon PowerShot SD400 incelemesi", "tags": ["canon", "powershot", "sd400", "y2k"]},
    {"id": "SdvyqeBglac", "title": "Canon IXUS 160 incelemesi",         "tags": ["canon", "ixus", "160"]},
    {"id": "k6ccwjtkhgw", "title": "Panasonic Lumix DC-TZ99 incelemesi","tags": ["panasonic", "lumix", "tz99"]},
    {"id": "N6iINZdtf_o", "title": "Retrocameraland tanıtım",           "tags": ["retro", "kamera", "koleksiyon"]},
]

# En iyi performans gösteren ürünler (GA4 verisi)
TOP_PRODUCTS = [
    {"model": "Sony Cyber-shot DSC-T9",  "keyword": "sony dsc t9",     "url": "/products/sony-cyber-shot-dsc-t9"},
    {"model": "Canon PowerShot SD400",   "keyword": "canon sd400",     "url": "/products/canon-powershot-sd400"},
    {"model": "Sony Cyber-shot DSC-S85", "keyword": "sony dsc s85",    "url": "/products/sony-cybershot-dsc-s85"},
    {"model": "Sony Cyber-shot DSC-TX9", "keyword": "sony dsc tx9",    "url": "/products/sony-cyber-shot-dsc-tx9"},
    {"model": "Fujifilm FinePix T200",   "keyword": "fujifilm t200",   "url": "/products/fujifilm-finepix-t200"},
]

# Sosyal medya linkleri (UTM'li)
SOCIAL_LINKS = {
    "instagram": "https://www.instagram.com/retrocameraland/?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=Instagram",
    "youtube":   "https://www.youtube.com/@RetroCameraLand?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=Youtube",
    "tiktok":    "https://www.tiktok.com/@retrocameraland?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=Tiktok",
    "pinterest": "https://pinterest.com/retrocameraland/?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=Pinterest",
    "linkedin":  "https://www.linkedin.com/company/retro-camera-land/?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=linkedin",
    "site":      "https://retrocameraland.com?utm_source=ajan&utm_medium=ai&utm_campaign=Links&utm_content=site",
}

# ── İçerik Kalite Kuralları (kullanıcı onaylı, 2026-07-25) ──────────────────────
# Konu seçimi (pick_topics/pick_themed_topic) ve içerik üretimi (generate_blog_html)
# prompt'larının ikisine de enjekte edilir. Tek yerden değiştirilsin diye burada tutulur.
TARGET_AUDIENCE = (
    "18-35 yaş, Y2K estetiği seven sosyal medya içerik üreticileri (Instagram/TikTok), "
    "retro fotoğraf meraklıları, kamera koleksiyoncuları, nostalji arayan Gen Z/genç "
    "millennial. Türkiye ağırlıklı ama İngilizce sürümler global (ABD/Filipinler/G.Kore/"
    "Avrupa) okuyucuya da hitap eder — ton samimi ama bilgili, asla kurumsal/mesafeli değil."
)

NATURAL_VOICE_RULES = (
    "DOĞAL TÜRKÇE — AI TONU YASAK: "
    "Şu kalıpları ASLA kullanma: 'zaman tüneline yolculuk', 'bu makale ... bahseder/anlatır', "
    "'aslında', 'gerçekten de', 'söylemek gerekirse', 'harikalar dünyasına hoş geldiniz', "
    "'dün ve bugünü bağlamak', 'bilinir ki', 'söylenebilir', "
    "'günümüzün hızla değişen dünyasında', 'kuşkusuz', 'hiç şüphesiz', "
    "'sonuç olarak belirtmek gerekirse', 'yolculuğa çıkalım', 'oyun değiştirici', "
    "'kusursuz bir şekilde', 'sözün özü', 'içine dalalım'. "
    "Cümle uzunluğunu ÇEŞİTLENDİR — art arda paragraflarda aynı uzunlukta/aynı kalıpta "
    "cümle kurma (robotik simetri AI kokusu verir); bazen kısa çarpıcı cümle, bazen uzun. "
    "Net bir GÖRÜŞ/TAVSİYE belirt ('bence', 'tavsiyem şu', 'gördüğümüz kadarıyla') — "
    "AI metni hep tarafsız/mesafeli kalır, bu belli eder; bir tarafını tut. "
    "Bölümler birbirinin aynı iskeletini tekrarlamasın, madde listeleri her seferinde "
    "aynı sayıda/aynı formatta olmasın."
)

MODEL_SCOPE_RULES = (
    "MODEL SEÇİMİ: Sadece şu an stokta olan modellerle sınırlı kalma — popüler/aranan "
    "modeller hakkında (stokta olmasa da) yazmak SEO/AI-arama için değerli. Böyle bir "
    "yazıda: (a) modelin RCL'de şu an stokta olup olmadığını dürüstçe belirt, (b) stokta "
    "değilse en yakın/benzer segmentte stoktaki bir RCL modelini alternatif olarak öner "
    "ve ona link ver, (c) yine de retrocameraland.com'a en az 2 gerçek link ver."
)

# ── Utility ────────────────────────────────────────────────────────────────────
def make_slug(title):
    r = {"ş":"s","ç":"c","ö":"o","ü":"u","ğ":"g","ı":"i",
         "Ş":"s","Ç":"c","Ö":"o","Ü":"u","Ğ":"g","İ":"i"," ":"-"}
    s = "".join(r.get(c, c) for c in title).lower()
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:80]

def load_published():
    try:
        if os.path.exists(STATE_FILE):
            return json.load(open(STATE_FILE, encoding='utf-8'))
    except Exception:
        pass
    return []

def save_published(new_titles):
    existing = load_published()
    combined = list(dict.fromkeys(existing + new_titles))
    json.dump(combined, open(STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def _normalize_kw(kw):
    kw = (kw or '').lower().strip()
    kw = re.sub(r'[^a-zçğıöşü0-9 ]', '', kw)
    return re.sub(r'\s+', ' ', kw).strip()

def load_keyword_history():
    """{normalized_keyword: 'YYYY-MM-DD son yayın tarihi'} — konu KONUSU tekrarını önler
    (sadece başlık string'i değil, aynı ana keyword'ün kısa sürede tekrar seçilmesini engeller)."""
    try:
        if os.path.exists(KEYWORD_STATE_FILE):
            return json.load(open(KEYWORD_STATE_FILE, encoding='utf-8'))
    except Exception:
        pass
    return {}

def save_keyword_history(keywords):
    hist  = load_keyword_history()
    today = datetime.now().strftime('%Y-%m-%d')
    for kw in keywords:
        nk = _normalize_kw(kw)
        if nk:
            hist[nk] = today
    json.dump(hist, open(KEYWORD_STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def keyword_on_cooldown(kw, hist, days=None):
    nk = _normalize_kw(kw)
    if nk not in hist:
        return False
    try:
        last = datetime.strptime(hist[nk], '%Y-%m-%d')
    except Exception:
        return False
    return (datetime.now() - last).days < (days if days is not None else KEYWORD_COOLDOWN_DAYS)

# ── Marka+model varlık (entity) bazlı tekrar kontrolü ───────────────────────
# keyword_on_cooldown() literal keyword string'ini karşılaştırır; LLM aynı ürüne
# ("fujifilm t200 vs sony dsc-t9") her seferinde yeni bir açı/keyword string'i
# uydurunca (5 altın kural, ucuz seçim, yıl güncellemesi...) o kontrol atlanır.
# Bunun yerine başlık+keyword'den marka/model varlığını çıkarıp ayrı bir tarihçeyle
# karşılaştırır — ifade değişse de aynı ürün(ler) çok kısa sürede tekrar seçilemez.
_ENTITY_BRAND_WORDS = {
    "fujifilm","fuji","sony","canon","nikon","casio","kodak","olympus","panasonic",
    "samsung","sanyo","pentax","konica","minolta","traveler","kyocera","polaroid",
    "vivitar","ricoh","leica","hp","benq","ge","instax",
}
_ENTITY_GENERIC_WORDS = {
    "kamera","kameralar","kamerasi","kamerayi","kamerayla","retro","dijital","y2k",
    "rehberi","rehber","ccd","inceleme","incelemesi","secimi","secim","fotograf",
    "fotografciligi","fotografcilik","ile","icin","kompakt","altin","kural","cin",
    "estetigi","estetik","neden","satin","alma","turkiye","vintage","hangi","zoom",
    "ucuz","trendi","modelleri","modeli","model","iyi","en","bir","ve","de","da",
    "mi","mu","nedir","vs","2025","2026","tl","dolar","fiyat","fiyati","fiyatlari",
    "karsilastirma","karsilastirmasi","seri","serisi","nereden","alinir","herkes",
    "onerisi","onerileri","secenekleri","icinde","gercek","yaz",
}
# rakamsız ama ürün ailesini belirleyen özel isimler (sabit liste — serbest
# ">=5 karakter" kuralı "estetiginin"/"simgesi" gibi yanlış pozitifler üretiyordu)
_ENTITY_MODEL_FAMILY_WORDS = {
    "ixus","finepix","coolpix","cybershot","cyber","powershot","exilim","lumix",
    "xacti","optio","instax","dimage","easyshare","stylus","tough","pixpro",
    "cyber-shot","rebel","eos","alpha","xperia","galaxy",
}

def _entity_slugify(t):
    r = {"ş":"s","ç":"c","ö":"o","ü":"u","ğ":"g","ı":"i",
         "Ş":"s","Ç":"c","Ö":"o","Ü":"u","Ğ":"g","İ":"i"}
    t = "".join(r.get(c, c) for c in (t or "")).lower()
    return re.sub(r"[^a-z0-9\s\-]", " ", t)

def extract_entities(*texts):
    """Metin(ler)den marka+model varlıklarını çıkarır (ör. {'fujifilm','sony','t200'}).
    Genel/dolgu kelimeleri yok sayar; sadece marka isimleri ve rakam içeren model
    kodlarını (t200, dsc-t9, sd400, es65...) varlık sayar."""
    ents = set()
    for text in texts:
        for w in re.split(r"[\s\-]+", _entity_slugify(text)):
            if not w or w in _ENTITY_GENERIC_WORDS:
                continue
            if w in _ENTITY_BRAND_WORDS or (re.search(r"\d", w) and len(w) >= 2):
                ents.add(w)
            elif w in _ENTITY_MODEL_FAMILY_WORDS:
                # rakamsız model-ailesi adları (finepix, coolpix, cybershot,
                # powershot, exilim, ixus...) da varlık sayılsın — ama serbest
                # >=5 karakter kuralı YANLIŞ pozitif üretiyordu (ör. "estetiginin",
                # "simgesi"), o yüzden sabit bir liste kullanılıyor.
                ents.add(w)
    return ents

def load_entity_history():
    try:
        if os.path.exists(ENTITY_STATE_FILE):
            return json.load(open(ENTITY_STATE_FILE, encoding='utf-8'))
    except Exception:
        pass
    return []

def save_entity_history(entity_sets):
    """entity_sets: [{'fujifilm','t200',...}, ...] — her biri bir yayının varlık kümesi."""
    entity_sets = [e for e in entity_sets if e]
    if not entity_sets:
        return
    hist = load_entity_history()
    today = datetime.now().strftime('%Y-%m-%d')
    for e in entity_sets:
        hist.append({"entities": sorted(e), "date": today})
    hist = hist[-500:]
    json.dump(hist, open(ENTITY_STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

_TR_MONTH_NAMES = ("ocak","subat","şubat","mart","nisan","mayis","mayıs","haziran",
                   "temmuz","agustos","ağustos","eylul","eylül","ekim","kasim","kasım",
                   "aralik","aralık")

def _strip_title_suffix(title):
    """Başlık sonundaki tarih/yıl/ay eki farkını yok sayarak karşılaştırma anahtarı
    üretir (ör. '... — 2026', '... (Temmuz)', '...-07101245' hepsi aynı taban başlığa
    indirgenir). FALLBACK_POOL'un 'havuz tükendi' varyasyon üretimi (pick_topics içinde,
    yıl/ay eki ekleyerek 'yeni' konu üretme) tam olarak bu kalıbı üretiyor — keyword alanı
    farklıysa bile bu kontrol yakalar."""
    t = (title or "").strip().lower()
    month_pat = "|".join(_TR_MONTH_NAMES)
    t = re.sub(rf"\s*[—\-]\s*(2025|2026|{month_pat}\w*|\d{{6,8}})\s*\.*$", "", t)
    t = re.sub(r"\s*\((2025|2026)\)\s*\.*$", "", t)
    t = re.sub(r"\s+(2025|2026)$", "", t)
    return t.strip().rstrip(".…")

def entity_on_cooldown(topic_entities, hist, days=None):
    """topic_entities, cooldown penceresi içinde yayınlanmış bir kayıtla en az 2 varlığı
    (tek marka+model varsa 1) paylaşıyorsa True — aynı ürün(ler) hakkında yeni bir 'açı'
    ile tekrar yazılmasını engeller."""
    if not topic_entities:
        return False
    now = datetime.now()
    window = days if days is not None else ENTITY_COOLDOWN_DAYS
    required = 2 if len(topic_entities) >= 2 else 1
    for rec in hist:
        try:
            last = datetime.strptime(rec.get("date", ""), '%Y-%m-%d')
        except Exception:
            continue
        if (now - last).days >= window:
            continue
        shared = topic_entities & set(rec.get("entities", []))
        if len(shared) >= required:
            return True
    return False

def load_image_history():
    """Daha önce kullanılmış görsel URL'leri — aynı görselin farklı bloglarda tekrarını önler."""
    try:
        if os.path.exists(IMAGE_STATE_FILE):
            return json.load(open(IMAGE_STATE_FILE, encoding='utf-8'))
    except Exception:
        pass
    return []

def save_image_used(url):
    if not url:
        return
    hist = load_image_history()
    hist.append(url)
    hist = hist[-300:]
    try:
        json.dump(hist, open(IMAGE_STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"  ⚠ Görsel geçmişi kaydedilemedi: {e}")

def tg_send(text):
    import urllib.request
    url  = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def pick_yt_video(topic_title, topic_keyword):
    """Blog konusuyla en alakalı YouTube videosunu seç."""
    title_lower = (topic_title + " " + topic_keyword).lower()
    best = None
    best_score = 0
    for v in YT_VIDEOS:
        score = sum(1 for tag in v["tags"] if tag in title_lower)
        if score > best_score:
            best_score = score
            best = v
    return best or YT_VIDEOS[-1]  # fallback to last

def yt_embed_block(video_id, video_title):
    """YouTube embed iframe HTML bloğu."""
    return f"""<div style="margin:32px 0;text-align:center;">
<iframe width="100%" height="400" style="max-width:700px;border-radius:12px;border:0;"
  src="https://www.youtube.com/embed/{video_id}"
  title="{video_title} — RetroCameraLand"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowfullscreen loading="lazy"></iframe>
<p style="margin:8px 0 0;font-size:0.85rem;color:#888;">
📺 <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener"
   style="color:#c8a882;">YouTube'da izle</a> &nbsp;|&nbsp;
<a href="{CHANNEL_URL}" target="_blank" rel="noopener" style="color:#c8a882;">
Kanalımıza abone ol →</a></p></div>"""

def social_inline_block():
    """Blog içi sosyal medya + site yönlendirme bloğu."""
    return f"""<div style="background:linear-gradient(135deg,#1a1208 0%,#1a1a1a 100%);border:1px solid rgba(200,168,130,0.2);border-radius:14px;padding:22px 26px;margin:36px 0;color:#fff;">
<p style="margin:0 0 6px;font-weight:700;font-size:1.05rem;color:#c8a882;">📸 Retrocameraland'i Takip Et</p>
<p style="margin:0 0 14px;font-size:0.78rem;color:rgba(255,255,255,0.45);">Retro kamera içerikleri, incelemeler ve Y2K estetik fotoğraflar için tüm kanallarımız:</p>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px;">
<a href="{SOCIAL_LINKS['instagram']}" target="_blank" rel="noopener" style="background:rgba(200,168,130,0.12);border:1px solid rgba(200,168,130,0.25);color:#c8a882;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:0.82rem;font-weight:600;">📷 Instagram</a>
<a href="{SOCIAL_LINKS['tiktok']}" target="_blank" rel="noopener" style="background:rgba(200,168,130,0.12);border:1px solid rgba(200,168,130,0.25);color:#c8a882;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:0.82rem;font-weight:600;">🎵 TikTok</a>
<a href="{SOCIAL_LINKS['youtube']}" target="_blank" rel="noopener" style="background:rgba(200,168,130,0.12);border:1px solid rgba(200,168,130,0.25);color:#c8a882;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:0.82rem;font-weight:600;">▶️ YouTube</a>
<a href="{SOCIAL_LINKS['pinterest']}" target="_blank" rel="noopener" style="background:rgba(200,168,130,0.12);border:1px solid rgba(200,168,130,0.25);color:#c8a882;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:0.82rem;font-weight:600;">📌 Pinterest</a>
<a href="{SOCIAL_LINKS['linkedin']}" target="_blank" rel="noopener" style="background:rgba(200,168,130,0.12);border:1px solid rgba(200,168,130,0.25);color:#c8a882;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:0.82rem;font-weight:600;">💼 LinkedIn</a>
</div>
<a href="{SOCIAL_LINKS['site']}" target="_blank" rel="noopener" style="display:inline-block;background:#c8a882;color:#1a1208;padding:10px 20px;border-radius:9px;text-decoration:none;font-size:0.88rem;font-weight:700;">🛒 Retrocameraland.com'a Git →</a>
</div>"""


# ── Web Research ───────────────────────────────────────────────────────────────
def ddg_search(query, max_results=5):
    import urllib.request, urllib.parse
    url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        snippets = re.findall(r"class='result-snippet'>(.*?)</td>", html, re.DOTALL)
        titles   = re.findall(r"class='result-link'[^>]*>(.*?)</a>", html, re.DOTALL)
        results  = []
        for t, s in zip(titles[:max_results], snippets[:max_results]):
            clean_t = re.sub(r'<[^>]+>', '', t).strip()
            clean_s = re.sub(r'<[^>]+>', '', s).strip()
            if clean_t:
                results.append({'title': clean_t, 'snippet': clean_s})
        return results
    except Exception as e:
        log(f"DDG hata: {e}")
        return []

def get_tr_twitter_trends():
    import urllib.request
    try:
        req = urllib.request.Request("https://trends24.in/turkey/")
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        trends = re.findall(r'<a[^>]+class="[^"]*trend[^"]*"[^>]*>([^<]{2,40})</a>', html)
        if not trends:
            trends = re.findall(r'>#([^\s<"]{2,30})</a>', html)
        seen = []
        for t in trends:
            t = t.strip().lstrip('#')
            if t and t not in seen:
                seen.append(t)
        return seen[:20]
    except Exception as e:
        log(f"Twitter trend hata: {e}")
        return []

def research_trends():
    """retrocameraland odaklı trend verisi topla."""
    log("🔍 Trendler araştırılıyor...")
    now = datetime.now()
    months = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
              "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    month_tr = months[now.month - 1]
    date_str  = f"{now.day} {month_tr} {now.year}"

    # retrocameraland'e özgü aramalar — keyword fırsatları dahil
    queries = [
        f"dijital kamera 2026 Türkiye {month_tr} trend",
        "retro kamera türkiye ucuz dijital kamera 2026",
        "y2k kamera fujifilm finepix estetik instagram tiktok",
        "canon ixus fiyat nikon coolpix vintage retro",
        "ccd kamera nedir 3000 tl dijital kamera önerisi",
        "hangi dijital kamera almalıyım y2k fotoğrafçılık",
    ]

    web_results = []
    for q in queries[:3]:
        results = ddg_search(q, max_results=4)
        web_results.extend(results)
        time.sleep(1.5)

    # X araması — retro kamera odaklı
    x_results = ddg_search("site:x.com retro kamera y2k fotoğraf estetik", max_results=4)
    time.sleep(1)

    twitter_trends = get_tr_twitter_trends()
    log(f"  → {len(web_results)} web | {len(twitter_trends)} TR trend | {len(x_results)} X")

    return {
        'web':      web_results,
        'twitter':  twitter_trends,
        'x':        x_results,
        'date':     date_str,
        'month':    month_tr,
        'year':     now.year,
    }


# ── Dünya Çapında Popüler Model Araştırması (Claude API) ────────────────────────
GLOBAL_MODELS_CACHE_FILE = '/Users/onnoshot/Downloads/Agentlar/global-camera-models-research.json'
GLOBAL_MODELS_TTL_DAYS   = 14  # statik bir araştırma, günlük tazelenmesine gerek yok

def research_global_camera_models():
    """Claude API ile RCL'nin stoğuyla/markalarıyla SINIRLI KALMADAN dünya çapında
    popüler/ikonik/kült dijital kamera modellerini araştırır (MODEL_SCOPE_RULES ile
    uyumlu — stokta olmayan modeller hakkında da blog yazılabilir, amaç 'tüm dijital
    kamera modelleriyle ilgili kapsamlı blog kütüphanesi'). 14 günlük dosya cache —
    her cron koşusunda yeniden sorgulanmaz."""
    try:
        if os.path.exists(GLOBAL_MODELS_CACHE_FILE):
            cached = json.load(open(GLOBAL_MODELS_CACHE_FILE, encoding='utf-8'))
            age_days = (time.time() - cached.get('fetched_at', 0)) / 86400
            if age_days < GLOBAL_MODELS_TTL_DAYS and cached.get('models'):
                return cached['models']
    except Exception:
        pass

    if not ANTHROPIC_KEY:
        return []

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=90.0, max_retries=2)
        system = (
            "Sen retro/vintage dijital kamera konusunda uzman bir araştırmacısın. "
            "1995-2012 arası CCD sensörlü dijital kompakt kameralar ve günümüzde Y2K/"
            "nostalji trendiyle yeniden popüler olan modeller konusunda derin bilgin var."
        )
        user = (
            "Dünya çapında (sadece Türkiye değil) popüler, ikonik, kült veya şu anda "
            "Y2K/nostalji trendiyle yeniden aranan 40 dijital kamera modeli listele. "
            "Tek bir markayla/mağazayla sınırlı kalma — Canon, Sony, Nikon, Casio, Kodak, "
            "Olympus, Panasonic, Fujifilm, Samsung, Pentax, Konica Minolta, Ricoh, Sanyo, "
            "HP, Vivitar, Polaroid, Sigma, Leica dahil geniş bir yelpaze kapsa. Her model için: "
            "model adı, marka, hangi yıl/dönem, neden popüler/ikonik (1 cümle), günümüzde "
            "hangi kitlede popüler (koleksiyoncu / Y2K içerik üreticisi / vintage fotoğrafçı vb). "
            'SADECE JSON dizi döndür, başka metin yazma: '
            '[{"model":"...", "brand":"...", "era":"...", "why":"...", "audience":"..."}]'
        )
        resp = client.messages.create(
            model=CLAUDE_MODEL, max_tokens=8000, system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = _claude_text(resp)
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        models = json.loads(m.group(0)) if m else []
        json.dump({'fetched_at': time.time(), 'models': models},
                   open(GLOBAL_MODELS_CACHE_FILE, 'w', encoding='utf-8'),
                   ensure_ascii=False, indent=2)
        log(f"  ✓ Claude: {len(models)} dünya çapında popüler model araştırıldı (14 gün cache)")
        return models
    except Exception as e:
        log(f"  ⚠ Global model araştırması başarısız: {str(e)[:100]}")
        return []


# ── AI-Slop / Şablon Tespiti ────────────────────────────────────────────────────
AI_SLOP_PATTERNS = [
    r'zaman tüneline yolculuk', r'bu makale.*?bahseder', r'şimdi derinliklere inmek için',
    r'her zaman önemli', r'\baslında\b', r'gerçekten de', r'söylemek gerekirse',
    r'size.*?sunmak için buradayız', r'harikalar dünyasına hoş geldiniz',
    r'dün ve bugünü bağlamak', r'\bbilinir ki\b', r'\bsöylenebilir\b',
    # 2026-07-25 eklendi: kullanıcı geri bildirimiyle genişletildi (feedback_content_automation_dedup)
    r'günümüzün hızla değişen dünyasında', r'\bkuşkusuz\b', r'\bhiç şüphesiz\b',
    r'sonuç olarak belirtmek gerekirse', r'yolculuğa çıkalım', r'oyun değiştirici',
    r'kusursuz bir şekilde', r'\bsözün özü\b', r'içine dalalım', r'derinlemesine inceleyelim',
    r'göz atalım', r'\bönemle belirtmek gerekir\b', r'\bhiç kuşkusuz\b',
    r'dünyasına adım at', r'unutulmaz bir deneyim',
]

def count_ai_slop(body_html):
    clean = re.sub(r'<[^>]+>', ' ', body_html)
    return sum(1 for p in AI_SLOP_PATTERNS if re.search(p, clean, re.IGNORECASE))


# ── SEO Scoring ────────────────────────────────────────────────────────────────
def score_seo(title, meta_desc, body_html, keyword):
    score, details = 0, []
    kw = keyword.lower()
    kw_words = kw.split()

    def kw_in(text):
        t = text.lower()
        return kw in t or all(w in t for w in kw_words)

    # Title (20)
    if kw_in(title):
        score += 12; details.append("✓ Keyword başlıkta (+12)")
    else:
        details.append("✗ Keyword başlıkta YOK (0)")
    tl = len(title)
    if 45 <= tl <= 70:
        score += 8;  details.append(f"✓ Başlık {tl} kar (+8)")
    elif tl > 0:
        score += 3;  details.append(f"△ Başlık {tl} kar (+3)")

    # Meta (15)
    if kw_in(meta_desc):
        score += 8;  details.append("✓ Keyword meta'da (+8)")
    else:
        details.append("✗ Keyword meta'da YOK (0)")
    ml = len(meta_desc)
    if 140 <= ml <= 170:
        score += 7;  details.append(f"✓ Meta {ml} kar (+7)")
    elif ml >= 100:
        score += 3;  details.append(f"△ Meta {ml} kar (+3)")

    # Word count (20)
    clean = re.sub(r'<[^>]+>', ' ', body_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    wc    = len(words)
    if wc >= 1500:
        score += 20; details.append(f"✓ {wc} kelime (+20)")
    elif wc >= 1000:
        score += 13; details.append(f"△ {wc} kelime (+13)")
    elif wc >= 700:
        score += 7;  details.append(f"△ {wc} kelime (+7)")
    else:
        details.append(f"✗ {wc} kelime çok az (0)")

    # Headings (15)
    h2 = len(re.findall(r'<h2[^>]*>', body_html, re.I))
    h3 = len(re.findall(r'<h3[^>]*>', body_html, re.I))
    score += (10 if h2 >= 5 else 6 if h2 >= 3 else 0)
    details.append(f"{'✓' if h2>=5 else '△'} {h2} H2 (+{10 if h2>=5 else 6 if h2>=3 else 0})")
    score += (5 if h3 >= 2 else 2 if h3 == 1 else 0)
    details.append(f"{'✓' if h3>=2 else '△'} {h3} H3 (+{5 if h3>=2 else 2 if h3==1 else 0})")

    # FAQ (10)
    if re.search(r'(sık sorulan|SSS|FAQ|soru[^a-z])', body_html, re.I):
        score += 10; details.append("✓ FAQ (+10)")
    else:
        details.append("✗ FAQ YOK (0)")

    # Ürün Deep-Link (10) — AEO/yönlendirme kriteri: min 3 spesifik ürün sayfası (koleksiyon değil)
    pl = len(re.findall(r'href="https://retrocameraland\.com/products/', body_html))
    if pl >= 3:
        score += 10; details.append(f"✓ {pl} ürün deep-link (+10)")
    elif pl >= 1:
        score += 5;  details.append(f"△ {pl} ürün deep-link (+5)")
    else:
        details.append("✗ Ürün deep-link YOK (0)")

    # Keyword density (10) — Türkçe bileşik kelimeler için geniş aralık
    kw_count = clean.lower().count(kw)
    # Keyword 2+ kelimeyse ilk kelimenin yoğunluğuna bakarak da değerlendir
    kw_parts  = kw.split()
    if len(kw_parts) > 1 and kw_count < 5:
        kw_count = max(kw_count, clean.lower().count(kw_parts[0] + " " + kw_parts[1]) // 2)
    density  = (kw_count / max(wc, 1)) * 100
    if 0.5 <= density <= 4.0:
        score += 10; details.append(f"✓ Yoğunluk {density:.1f}% (+10)")
    elif 0.2 <= density <= 5.5:
        score += 5;  details.append(f"△ Yoğunluk {density:.1f}% (+5)")
    else:
        details.append(f"✗ Yoğunluk {density:.1f}% (0)")

    # First paragraph (5)
    fp = re.search(r'<p[^>]*>(.*?)</p>', body_html, re.DOTALL | re.I)
    if fp and kw_in(re.sub(r'<[^>]+>', '', fp.group(1))):
        score += 5;  details.append("✓ Keyword ilk paragrafta (+5)")
    else:
        details.append("△ Keyword ilk paragrafta değil (0)")

    # İnsan Tonu / AI-Slop (10) — şablon klişeleri tespit edilirse düşük puan → yeniden dene
    slop = count_ai_slop(body_html)
    if slop == 0:
        score += 10; details.append("✓ AI-slop klişesi yok (+10)")
    elif slop <= 2:
        score += 5;  details.append(f"△ {slop} klişe tespit edildi (+5)")
    else:
        details.append(f"✗ {slop} klişe tespit edildi — şablon ton (0)")

    return score, details


# ── Claude Code CLI (birincil yazar — abonelik, API kredisi harcamaz) ──────────
CLAUDE_CLI = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
_CLAUDE_CODE_DEAD_THIS_RUN = False  # CLI bulunamaz/patlarsa bu süreç boyunca bir daha denenmez

def claude_code_write(system_prompt, user_prompt, max_tokens=4000):
    """Blog yazımı — Claude Code CLI headless (-p) modu. Kullanıcının Claude Code
    aboneliğini kullanır, ANTHROPIC_API_KEY'in pay-per-token bakiyesini tüketmez.
    launchd cron'dan bağımsız bir süreç olarak çalışır; CLAUDECODE ortam değişkenini
    temizlemezsek CLI "iç içe oturum" sanıp reddediyor, bu yüzden siliniyor."""
    global _CLAUDE_CODE_DEAD_THIS_RUN
    if _CLAUDE_CODE_DEAD_THIS_RUN:
        raise RuntimeError("Claude Code CLI bu koşuda daha önce başarısız oldu")
    env = os.environ.copy()
    for k in ("CLAUDECODE", "CLAUDE_CODE_EXECPATH", "CLAUDE_CODE_SSE_PORT", "CLAUDE_CODE_ENTRYPOINT"):
        env.pop(k, None)
    try:
        result = subprocess.run(
            [CLAUDE_CLI, "-p", user_prompt,
             "--system-prompt", system_prompt,
             "--model", "sonnet",
             "--output-format", "text",
             "--tools", "",
             "--strict-mcp-config",
             "--no-session-persistence"],
            capture_output=True, text=True, timeout=240, env=env, cwd=SCRIPT_DIR,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Claude Code CLI zaman aşımı")
    except FileNotFoundError:
        _CLAUDE_CODE_DEAD_THIS_RUN = True
        raise RuntimeError("Claude Code CLI bulunamadı")
    if result.returncode != 0:
        _CLAUDE_CODE_DEAD_THIS_RUN = True
        raise RuntimeError(f"Claude Code CLI hata: {result.stderr.strip()[:200]}")
    text = result.stdout.strip()
    if not text:
        raise RuntimeError("Claude Code CLI boş yanıt döndürdü")
    return text


# ── Claude API (son çare — ücretli, sadece hepsi başarısız olursa) ─────────────
CLAUDE_MODEL = "claude-sonnet-5"

def _claude_text(resp):
    """resp.content[0] her zaman metin bloğu OLMAYABİLİR (bazı istemlerde önce bir
    ThinkingBlock gelebiliyor) — ilk gerçek metin bloğunu bul, körlemesine [0].text alma."""
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise RuntimeError("Claude yanıtında metin bloğu bulunamadı (sadece thinking/tool_use olabilir)")

def claude_write(system_prompt, user_prompt, max_tokens=4000):
    """Blog yazımı — Claude Sonnet (birincil)."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=120.0, max_retries=2)
    for attempt in range(3):
        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return _claude_text(resp)
        except Exception as e:
            msg = str(e)
            if 'credit balance' in msg.lower() or 'too low' in msg.lower():
                raise RuntimeError(f"Claude bakiye yetersiz — Groq'a geçiliyor")
            elif 'overloaded' in msg.lower() or '529' in msg:
                wait = 30 if attempt == 0 else 60
                log(f"  Claude yoğun — {wait}s bekleniyor...")
                time.sleep(wait)
            elif '401' in msg or 'authentication' in msg.lower():
                raise RuntimeError(f"Claude API anahtarı geçersiz: {msg[:80]}")
            else:
                log(f"  Claude hata ({attempt+1}): {msg[:120]}")
                time.sleep(10)
    raise RuntimeError("Claude 3 denemede başarısız")


# ── Gemini API (birincil yazar) ────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.5-flash"

_GEMINI_QUOTA_DEAD = False  # bu süreç boyunca kalıcı — günlük kota bir kez tükendi mi bir daha denenmez

def gemini_write(system_prompt, user_prompt, max_tokens=8000):
    """Blog yazımı — Gemini 2.5 Flash (birincil)."""
    global _GEMINI_QUOTA_DEAD
    if _GEMINI_QUOTA_DEAD:
        raise RuntimeError("Gemini günlük kota tükenmiş (bu koşuda tekrar denenmiyor)")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_KEY, http_options=types.HttpOptions(timeout=120000))
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config=types.GenerateContentConfig(max_output_tokens=max_tokens),
            )
            return resp.text
        except Exception as e:
            msg = str(e)
            # "free_tier_requests" + düşük "limit" = GÜNLÜK kota duvarı, dakikalık rate
            # limit değil (2026-07-28'de tespit edildi: limit 20/gün, her çağrı anında
            # 429 veriyordu). Buna karşı 3x tekrar denemek saf zaman kaybı — Groq zaten
            # TÜM yükü tek başına taşımak zorunda kalıyor, gereksiz Gemini denemeleri onu
            # daha da geciktiriyor. Böyle bir hata görünce süreç boyunca Gemini'yi kapat.
            if 'free_tier_requests' in msg or ('RESOURCE_EXHAUSTED' in msg and 'quota' in msg.lower()):
                _GEMINI_QUOTA_DEAD = True
                log(f"  ⚠ Gemini günlük kota tükenmiş — bu koşu boyunca atlanacak: {msg[:100]}")
                raise RuntimeError("Gemini günlük kota tükenmiş")
            if '429' in msg or 'RESOURCE_EXHAUSTED' in msg:
                # ESKİDEN 60s/120s/120s (blog başına ~15dk boşa gidiyordu — 2026-07-25/26
                # loglarında HER çağrı rate-limit yiyordu, tek blog 51dk sürdü). Kota
                # gerçekten tükendiyse uzun beklemek yardımcı olmaz — hızlı Groq'a düş.
                wait = 8 if attempt == 0 else 15
                log(f"  Gemini rate limit — {wait}s bekleniyor...")
                time.sleep(wait)
            elif '401' in msg or 'API_KEY' in msg or 'PERMISSION_DENIED' in msg:
                raise RuntimeError(f"Gemini API anahtarı geçersiz: {msg[:80]}")
            else:
                log(f"  Gemini hata ({attempt+1}): {msg[:120]}")
                time.sleep(10)
    raise RuntimeError("Gemini 3 denemede başarısız")


# ── Groq API (fallback + konu seçimi) ─────────────────────────────────────────
GROQ_SMART  = "openai/gpt-oss-120b"
GROQ_WRITER = "openai/gpt-oss-20b"

def _groq_call(model, system_prompt, user_prompt, max_tokens=4000, temperature=0.75):
    from groq import Groq
    client = Groq(api_key=GROQ_KEY, timeout=120.0, max_retries=2)
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as e:
            msg = str(e)
            if '429' in msg or 'rate_limit' in msg.lower():
                # ESKİDEN 180s/300s — Groq bu bölümde SON çare (Gemini zaten başarısız oldu),
                # uzun beklemek sadece toplam süreyi şişiriyor; kota gerçekten tükendiyse
                # kısa beklemek de değişmez, hızlı başarısız olup dış döngüye (yeni deneme/
                # başka konu) bırakmak daha iyi.
                wait = 15 if attempt == 0 else 25
                log(f"  Groq rate limit — {wait}s bekleniyor...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Groq 3 denemede başarısız")

def groq(system_prompt, user_prompt, max_tokens=2000, temperature=0.75):
    """Konu seçimi — Groq 70B."""
    return _groq_call(GROQ_SMART, system_prompt, user_prompt, max_tokens, temperature)

def groq_write(system_prompt, user_prompt, max_tokens=4000, temperature=0.78):
    """Blog yazımı — Groq 8B (fallback)."""
    return _groq_call(GROQ_WRITER, system_prompt, user_prompt, max_tokens, temperature)

def _clean(raw):
    raw = re.sub(r'^```html?\s*', '', raw.strip(), flags=re.I)
    raw = re.sub(r'\s*```$', '', raw.strip())
    return raw

def _extract_json_array(raw):
    """LLM'in döndürdüğü metinden JSON dizisini çıkarır. Eski kod `re.search(r'\\[.*\\]')`
    kullanıyordu — LLM JSON'dan sonra açıklama/yorum eklerse (ör. 'Not: ...') ve o metinde
    başka bir ']' geçerse greedy regex fazla metni yakalayıp 'Extra data' hatası veriyordu
    (2026-07-26 00:00 koşusunda konu seçimi tamamen başarısız oldu). Parantez derinliği
    sayarak İLK dengeli [...] bloğunu bulur — daha güvenilir."""
    start = raw.find('[')
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == '[':
            depth += 1
        elif raw[i] == ']':
            depth -= 1
            if depth == 0:
                candidate = raw[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    break
    # yedek: eski greedy davranış (bulamazsak hiç değilse eskisi kadar dener)
    m = re.search(r'\[.*\]', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None

_GROQ_DEAD_THIS_RUN = False  # bir bölümde 3 deneme de başarısız olursa, bu SÜREÇ boyunca
                             # bir daha denenmez — Groq süreç-başı sıfırlanır (Gemini'nin
                             # aksine kalıcı günlük kota değil, geçici yoğunluk)

def _write(system_prompt, user_prompt, max_tokens=4000):
    """Claude Code CLI birincil (abonelik, ücretsiz+kaliteli) → Gemini (ücretsiz ama
    günde 20 istekle sınırlı) → Groq (ücretsiz ama paylaşımlı/sıkışabiliyor) → Claude API
    (ücretli, güvenilir — SON çare, sadece üçü de başarısız olursa).
    2026-08-23: Claude Code CLI eklendi (kullanıcı isteği — abonelik zaten var, API
    bakiyesi/Gemini kotası bitince bile yazabiliyor)."""
    global _GROQ_DEAD_THIS_RUN
    if not _CLAUDE_CODE_DEAD_THIS_RUN:
        try:
            return _clean(claude_code_write(system_prompt, user_prompt, max_tokens))
        except Exception as e:
            log(f"  ⚠ Claude Code CLI başarısız, Gemini'ye geçiliyor: {str(e)[:80]}")

    if GEMINI_KEY:
        try:
            return _clean(gemini_write(system_prompt, user_prompt, max_tokens))
        except Exception as e:
            log(f"  ⚠ Gemini başarısız, Groq fallback: {str(e)[:80]}")

    if not _GROQ_DEAD_THIS_RUN:
        try:
            return _clean(groq_write(system_prompt, user_prompt, max_tokens))
        except Exception as e:
            groq_err = e
            # Bu koşuda Groq bir kez 3-deneme başarısız olduysa muhtemelen o an tamamen
            # tıkanmış (2026-07-29'da 5/5 bölüm art arda başarısız oldu) — sonraki
            # bölümlerde tekrar 65sn boşa harcamak yerine direkt Claude'a geç.
            _GROQ_DEAD_THIS_RUN = True
            log(f"  ⚠ Groq bu koşuda tıkandı, bir daha denenmeyecek: {str(groq_err)[:80]}")
    else:
        groq_err = RuntimeError("Groq bu koşuda zaten tıkanmıştı")

    if not ANTHROPIC_KEY:
        raise groq_err
    log(f"  → Claude'a düşülüyor (son çare)")
    return _clean(claude_write(system_prompt, user_prompt, max_tokens))


# ── Topic Selection ────────────────────────────────────────────────────────────
FALLBACK_POOL = [
    {"title": "Sony Cyber-shot DSC-T9 İnceleme: Y2K Portresinin Şampiyonu",
     "keyword": "sony cyber-shot dsc-t9",
     "secondary_keywords": ["sony dsc t9", "retro kamera", "y2k portre"],
     "tags": "sony, dsc-t9, retro kamera, y2k, retrocameraland",
     "meta_desc": "Sony Cyber-shot DSC-T9 incelemesi — Y2K estetik portrelerde öne çıkan retro dijital kamera. Türkiye'de fiyatı ve özellikleri.",
     "image_prompt": "Sony Cyber-shot DSC-T9 silver retro digital camera Y2K aesthetic portrait pastel background",
     "angle": "DSC-T9 neden Türkiye'de Y2K içerik üreticilerinin favorisi?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["sony", "retro"]},
    {"title": "Canon PowerShot SD400: 2025'te Neden Herkes Bu Kamerayı Arıyor?",
     "keyword": "canon powershot sd400",
     "secondary_keywords": ["canon sd400 fiyat", "retro canon kamera", "y2k kamera"],
     "tags": "canon, sd400, powershot, y2k, retrocameraland",
     "meta_desc": "Canon PowerShot SD400 neden 2025'te bu kadar popüler? Y2K estetiği, fiyatı ve teknik özellikleri — tam inceleme.",
     "image_prompt": "Canon PowerShot SD400 silver compact digital camera Y2K aesthetic vintage flat lay",
     "angle": "2025'in en çok aranan retro kamerası neden bu model?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["canon", "powershot", "sd400"]},
    {"title": "Fujifilm FinePix T200 ile Y2K Fotoğrafçılığı: Tam Rehber",
     "keyword": "fujifilm finepix t200",
     "secondary_keywords": ["fujifilm t200 retro", "y2k kamera fujifilm"],
     "tags": "fujifilm, finepix, t200, y2k, retrocameraland",
     "meta_desc": "Fujifilm FinePix T200 ile Y2K tarzı fotoğrafçılık rehberi — ayarlar, ışık, CCD sensör avantajları ve Türkiye fiyatı.",
     "image_prompt": "Fujifilm FinePix T200 retro digital camera Y2K aesthetic warm tones film grain",
     "angle": "CCD sensörü neden Y2K estetiğini mükemmel yapar?",
     "search_intent": "rehber",
     "yt_tags": ["retro", "fotoğraf"]},
    {"title": "Retro Kamerayla Instagram İçerik Üretimi: 10 İpucu",
     "keyword": "retro kamera instagram içerik",
     "secondary_keywords": ["y2k estetik instagram", "retro fotoğraf içerik"],
     "tags": "instagram, içerik üretimi, retro kamera, y2k, retrocameraland",
     "meta_desc": "Retro dijital kamerayla Instagram'da öne çıkan içerik nasıl üretilir? 10 pratik ipucu ve kamera önerileri.",
     "image_prompt": "retro digital camera Instagram content creation Y2K aesthetic flat lay phone social media",
     "angle": "Retro kamera içerikleri neden algoritma tarafından daha çok gösteriliyor?",
     "search_intent": "rehber",
     "yt_tags": ["retro", "estetik"]},
    {"title": "Türkiye'de Retro Dijital Kamera Satın Alma Rehberi 2025",
     "keyword": "retro dijital kamera satın al türkiye",
     "secondary_keywords": ["vintage kamera fiyat", "retro kamera nerede bulunur"],
     "tags": "satın alma rehberi, türkiye, retro kamera, 2025, retrocameraland",
     "meta_desc": "2025'te Türkiye'de retro dijital kamera nereden satın alınır? Fiyat karşılaştırması, model önerileri ve dikkat edilecekler.",
     "image_prompt": "retro digital cameras collection Turkey market price comparison Y2K vintage flat lay",
     "angle": "Hangi modeller Türk TL'siyle hâlâ erişilebilir?",
     "search_intent": "satın alma",
     "yt_tags": ["retro", "kamera", "koleksiyon"]},

    # ── Yüksek Hacim Keywordleri ──────────────────────────────────────────────
    {"title": "2026'da En İyi Dijital Kamera: Retro ve Modern Seçenekler",
     "keyword": "dijital kamera 2026",
     "secondary_keywords": ["en iyi dijital kamera 2026", "dijital kamera önerisi 2026", "retro kamera 2026"],
     "tags": "dijital kamera, 2026, retro kamera, retrocameraland",
     "meta_desc": "Dijital kamera 2026 rehberi: retro CCD kameralardan modern kompaktlara en iyi seçenekler. Türkiye fiyatları ve satın alma ipuçları.",
     "image_prompt": "best digital cameras 2026 retro Y2K CCD modern compact comparison flat lay",
     "angle": "2026'da retro kamera mı yoksa modern kompakt mı? Hangi özelliklere bakmalısın?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["retro", "kamera", "dijital"]},

    {"title": "Retro Kamera Türkiye: Nerede Bulunur, Fiyatlar Ne Kadar?",
     "keyword": "retro kamera türkiye",
     "secondary_keywords": ["türkiye retro kamera fiyat", "retro kamera nereden alınır", "vintage kamera türkiye"],
     "tags": "retro kamera, türkiye, fiyat, satın alma, retrocameraland",
     "meta_desc": "Retro kamera türkiye rehberi: fiyatlar, nereden alınır ve dikkat edilecekler. CCD kompakt kameraları Türkiye'de bulmak artık kolay.",
     "image_prompt": "retro camera Turkey market vintage digital CCD compact collection Turkish lira price",
     "angle": "Türkiye'de retro kamera piyasası: fiyatlar artıyor mu, hangi modeller değer kazanıyor?",
     "search_intent": "satın alma",
     "yt_tags": ["retro", "kamera", "koleksiyon"]},

    {"title": "Ucuz Dijital Kamera: 3000 TL Altında En İyi 7 Seçenek",
     "keyword": "ucuz dijital kamera",
     "secondary_keywords": ["3000 tl dijital kamera", "uygun fiyatlı kamera", "ucuz retro kamera"],
     "tags": "ucuz dijital kamera, 3000 tl, uygun fiyat, retrocameraland",
     "meta_desc": "Ucuz dijital kamera arayanlar için 2026'nın en iyi seçenekleri. 3000 TL altında Y2K estetiği sunan retro CCD kameralar ve modern kompaktlar.",
     "image_prompt": "budget digital cameras under 3000 TL retro CCD compact affordable Y2K aesthetic",
     "angle": "3000 TL ile kaliteli CCD kamera alınır mı? Piyasanın gerçek tablosu.",
     "search_intent": "satın alma",
     "yt_tags": ["retro", "ucuz", "kamera"]},

    {"title": "Fujifilm FinePix Serisi: Y2K Estetiğinin Simgesi",
     "keyword": "fujifilm finepix",
     "secondary_keywords": ["fujifilm finepix y2k", "fujifilm finepix türkiye", "fujifilm retro kamera"],
     "tags": "fujifilm, finepix, y2k, retro kamera, retrocameraland",
     "meta_desc": "Fujifilm FinePix serisi neden Y2K estetiğinin favorisi? Z serisi, T serisi ve klasik modeller — özellikleri, fiyatları ve satın alma rehberi.",
     "image_prompt": "Fujifilm FinePix series Y2K aesthetic retro cameras collection pastel vintage",
     "angle": "FinePix hangi modeli gerçekten Y2K fotoğraf estetiği için en iyi?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["fujifilm", "retro", "y2k"]},

    {"title": "Y2K Kamera Nedir? 2000'lerin Dijital Fotoğraf Trendi",
     "keyword": "y2k kamera",
     "secondary_keywords": ["y2k kamera özellikleri", "y2k fotoğraf estetiği", "2000ler dijital kamera"],
     "tags": "y2k kamera, estetik, retro fotoğraf, 2000ler, retrocameraland",
     "meta_desc": "Y2K kamera nedir, neden bu kadar popüler? CCD sensörlü retro dijital kameraların 2025'te geri dönüşü ve en çok tercih edilen modeller.",
     "image_prompt": "Y2K camera aesthetic retro digital CCD 2000s nostalgic warm tones grainy texture",
     "angle": "Y2K kamera trendi geçici mi yoksa kalıcı bir estetik hareketi mi?",
     "search_intent": "bilgi",
     "yt_tags": ["y2k", "retro", "estetik"]},

    # ── Orta Rekabet Keywordleri ──────────────────────────────────────────────
    {"title": "3000 TL Dijital Kamera Önerisi: 2026'da En İyi Seçimler",
     "keyword": "3000 tl dijital kamera",
     "secondary_keywords": ["3000 tl kamera önerisi", "uygun dijital kamera", "3000 tl retro kamera"],
     "tags": "3000 tl, dijital kamera, öneri, bütçe dostu, retrocameraland",
     "meta_desc": "3000 TL dijital kamera arayanlar için 2026'nın en iyi seçenekleri karşılaştırması. CCD retro kameralar mı, modern kompaktlar mı?",
     "image_prompt": "3000 TL budget digital cameras comparison retro CCD compact 2026 Turkey",
     "angle": "3000 TL ile gerçek Y2K estetiği veren kamera bulunabilir mi?",
     "search_intent": "satın alma",
     "yt_tags": ["retro", "kamera", "ucuz"]},

    {"title": "Canon IXUS Fiyat ve İnceleme: Hangi Model 2026'da Değer?",
     "keyword": "canon ixus fiyat",
     "secondary_keywords": ["canon ixus türkiye fiyat", "canon ixus modelleri", "canon retro kamera"],
     "tags": "canon ixus, fiyat, inceleme, retro kamera, retrocameraland",
     "meta_desc": "Canon IXUS fiyat rehberi 2026: tüm modellerin Türkiye fiyatları, teknik özellikleri ve Y2K estetiği için en iyi seçenekler.",
     "image_prompt": "Canon IXUS series compact cameras price comparison 2026 retro Y2K silver vintage",
     "angle": "Canon IXUS modelleri fiyat/performans açısından hâlâ rakipsiz mi?",
     "search_intent": "satın alma + bilgi",
     "yt_tags": ["canon", "ixus", "retro"]},

    {"title": "CCD Kamera Nedir? Retro Fotoğrafçılığın Sırrı",
     "keyword": "ccd kamera nedir",
     "secondary_keywords": ["ccd sensör nedir", "ccd vs cmos kamera", "ccd kamera y2k"],
     "tags": "ccd kamera, sensör, retro fotoğrafçılık, y2k, retrocameraland",
     "meta_desc": "CCD kamera nedir, CMOS'tan farkı ne? Y2K estetiğini yaratan CCD sensör teknolojisi ve en iyi CCD kamera modelleri 2026 rehberi.",
     "image_prompt": "CCD sensor retro digital camera technology Y2K aesthetic warm tones vintage film grain",
     "angle": "CCD sensör neden CMOS'tan daha 'nostaljik' görünür? Bilimsel açıklama.",
     "search_intent": "bilgi",
     "yt_tags": ["ccd", "retro", "kamera"]},

    # ── AI Search Hedefi Keywordleri ──────────────────────────────────────────
    {"title": "Hangi Dijital Kamera Almalıyım? 2026 Kapsamlı Rehber",
     "keyword": "hangi dijital kamera almalıyım",
     "secondary_keywords": ["dijital kamera seçimi", "kamera tavsiyesi 2026", "retro mi modern mi kamera"],
     "tags": "kamera seçimi, dijital kamera, rehber, 2026, retrocameraland",
     "meta_desc": "Hangi dijital kamera almalıyım? 2026'da bütçe, kullanım amacı ve estetik tercihe göre en doğru kamera seçimi rehberi — retro ve modern seçenekler.",
     "image_prompt": "digital camera buying guide 2026 comparison retro CCD modern compact decision chart",
     "angle": "Kamera seçiminde asıl soru: ne çekmek istiyorsun? Kullanım senaryosuna göre rehber.",
     "search_intent": "rehber",
     "yt_tags": ["kamera", "rehber", "retro"]},

    {"title": "Fujifilm mi Canon mu? 2026 Retro Kamera Karşılaştırması",
     "keyword": "fujifilm mi canon mu",
     "secondary_keywords": ["fujifilm canon karşılaştırma", "fujifilm finepix vs canon ixus", "retro kamera karşılaştırma"],
     "tags": "fujifilm, canon, karşılaştırma, retro kamera, retrocameraland",
     "meta_desc": "Fujifilm mi Canon mu? 2026'da Y2K estetiği, fiyat ve kullanım kolaylığı açısından detaylı karşılaştırma. Hangi marka retro fotoğrafçılık için daha iyi?",
     "image_prompt": "Fujifilm vs Canon retro digital cameras side by side comparison Y2K aesthetic 2026",
     "angle": "Retro kamera seçiminde marka sadakati mi, sensör kalitesi mi daha önemli?",
     "search_intent": "karşılaştırma",
     "yt_tags": ["fujifilm", "canon", "karşılaştırma"]},

    # ── GSC Quick Wins (Rank 5-15, yüksek impression) ──────────────────────────
    {"title": "Retro Kamera 2026: En İyi Modeller ve Türkiye Fiyatları",
     "keyword": "retro kamera",
     "secondary_keywords": ["retro dijital kamera", "vintage kamera", "y2k kamera fiyat"],
     "tags": "retro kamera, y2k, ccd, retrocameraland, 2026",
     "meta_desc": "2026 yılının en iyi retro kameraları: CCD sensörlü modeller, Türkiye fiyatları ve satın alma rehberi. RetroCameraLand uzman değerlendirmesi.",
     "image_prompt": "collection of retro Y2K digital cameras CCD aesthetic vintage 2000s flat lay warm tones Turkish market",
     "angle": "Retro kamera trendi 2026'da neden zirveye çıktı? Hangi modeller öne çıkıyor?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["retro", "kamera", "y2k"]},

    {"title": "Retro Camera Guide 2026: Best Y2K Digital Cameras for Turkish Buyers",
     "keyword": "retro camera",
     "secondary_keywords": ["retro camera Turkey", "vintage digital camera 2026", "y2k camera buy"],
     "tags": "retro camera, y2k, ccd, vintage, retrocameraland",
     "meta_desc": "Best retro cameras for 2026: CCD digital cameras with Y2K aesthetic, prices in Turkey and buying guide from RetroCameraLand.",
     "image_prompt": "Y2K retro digital cameras collection vintage CCD aesthetic pastel background studio shot 2026",
     "angle": "Why global retro camera trend is exploding and how to find the best deals in Turkey.",
     "search_intent": "informational + purchase",
     "yt_tags": ["retro", "camera", "y2k"]},

    {"title": "Y2K Digital Camera Trendi 2026: Neden Herkes CCD Kamera Satın Alıyor?",
     "keyword": "y2k digital camera",
     "secondary_keywords": ["y2k kamera estetiği", "ccd kamera y2k", "2000s camera aesthetic"],
     "tags": "y2k, digital camera, ccd, estetik, retrocameraland",
     "meta_desc": "Y2K digital camera trendi 2026'da zirveye çıktı. CCD sensörlü kameraların estetiği, popüler modeller ve Türkiye'de nereden alınır.",
     "image_prompt": "Y2K aesthetic digital camera 2000s CCD sensor warm grain nostalgic film look vintage compact",
     "angle": "TikTok ve Instagram'da patlayan Y2K kamera trendi: hangi modeller bu estetiği en iyi veriyor?",
     "search_intent": "bilgi + ilham",
     "yt_tags": ["y2k", "digital", "kamera"]},

    {"title": "Vintage Kamera Rehberi 2026: En Değerli 2000'ler CCD Modelleri",
     "keyword": "vintage kamera",
     "secondary_keywords": ["vintage dijital kamera", "eski kamera fiyat", "koleksiyon kamera"],
     "tags": "vintage kamera, ccd, koleksiyon, retrocameraland, 2026",
     "meta_desc": "2026'da vintage kamera seçimi: En değerli 2000'ler CCD modelleri, koleksiyon değeri yüksek kameralar ve Türkiye fiyatları.",
     "image_prompt": "vintage digital cameras 2000s CCD models collection value retro aesthetic warm tones flat lay",
     "angle": "Hangi vintage kameralar 2026'da koleksiyon değeri kazanıyor? Değer trendleri.",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["vintage", "kamera", "koleksiyon"]},

    {"title": "Samsung ES65 İnceleme: Y2K Estetiğinin İkonu — Fiyat ve Özellikler",
     "keyword": "samsung es65",
     "secondary_keywords": ["samsung es65 fiyat", "samsung es65 türkiye", "samsung retro kamera"],
     "tags": "samsung, es65, retro kamera, y2k, retrocameraland",
     "meta_desc": "Samsung ES65 detaylı inceleme: Y2K döneminin ikonik kompakt kamerası. Türkiye fiyatı, teknik özellikler ve neden bu kadar popüler?",
     "image_prompt": "Samsung ES65 compact digital camera silver Y2K aesthetic retro 2000s vintage flat lay pastel",
     "angle": "Samsung ES65 neden Google Trend'de yükselişte? Gerçek kullanıcı deneyimi.",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["samsung", "es65", "retro"]},

    # ── GSC Almost There (Rank 11-20, page-1 potansiyeli) ─────────────────────
    {"title": "Retro Fotoğraf Makinesi Seçimi 2026: Uzman Satın Alma Rehberi",
     "keyword": "retro fotoğraf makinesi",
     "secondary_keywords": ["retro fotoğraf makinesi fiyat", "dijital fotoğraf makinesi retro", "eski model fotoğraf makinesi"],
     "tags": "retro fotoğraf makinesi, dijital, satın alma, retrocameraland",
     "meta_desc": "Retro fotoğraf makinesi nasıl seçilir? 2026 en iyi modeller, fiyat aralıkları ve RetroCameraLand uzman önerileri.",
     "image_prompt": "retro digital cameras buying guide 2026 comparison multiple models flat lay vintage Turkish",
     "angle": "Retro fotoğraf makinesi alırken nelere dikkat edilmeli? 7 kritik soru.",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["retro", "fotoğraf", "makinesi"]},

    {"title": "Pentax Optio S7 İnceleme: Y2K Döneminin Unutulmaz Kompakt Mucizesi",
     "keyword": "pentax optio s7",
     "secondary_keywords": ["pentax optio s7 fiyat", "pentax retro kamera", "pentax optio inceleme"],
     "tags": "pentax, optio s7, retro kamera, y2k, retrocameraland",
     "meta_desc": "Pentax Optio S7 kapsamlı inceleme: 2000'lerin en şık kompakt kamerası. Teknik özellikler, Türkiye fiyatı ve Y2K estetiğindeki yeri.",
     "image_prompt": "Pentax Optio S7 slim compact digital camera silver metallic Y2K 2000s aesthetic retro vintage",
     "angle": "Pentax Optio S7: O kadar küçük, o kadar şık — 2026'da neden geri döndü?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["pentax", "optio", "retro"]},

    {"title": "Canon PowerShot A480 İnceleme: Retro Kameranın Zamansız Şampiyonu",
     "keyword": "canon powershot a480",
     "secondary_keywords": ["canon a480 fiyat", "canon powershot retro", "canon a serisi vintage"],
     "tags": "canon, powershot, a480, retro, y2k, retrocameraland",
     "meta_desc": "Canon PowerShot A480 inceleme: Klasik tasarımı ve güvenilir performansıyla hâlâ popüler retro kamera. Türkiye fiyatı ve özellikleri.",
     "image_prompt": "Canon PowerShot A480 compact digital camera retro red silver 2000s Y2K aesthetic vintage flat lay",
     "angle": "Canon A480 neden 15 yıl sonra hâlâ ilk 10'da? Kalıcı popülerliğin sırrı.",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["canon", "powershot", "a480"]},

    {"title": "Nostaljik Kamera Akımı 2026: Y2K Estetiği Neden Bu Kadar Popüler?",
     "keyword": "nostaljik kamera",
     "secondary_keywords": ["nostalji kamera trendi", "2000s kamera estetiği", "eski fotoğraf makinesi trendleri"],
     "tags": "nostaljik kamera, y2k, trend, estetik, retrocameraland",
     "meta_desc": "Nostaljik kamera akımı 2026'da zirveye çıktı. Y2K estetiği, CCD kamera kültürü ve sosyal medyadaki etkisi. Neden bu kadar popüler?",
     "image_prompt": "nostalgic 2000s Y2K cameras aesthetic warm grain CCD social media content creation TikTok trend",
     "angle": "Neden Z kuşağı analog döneme değil, 2000'lerin dijitaline geri dönüyor?",
     "search_intent": "bilgi + ilham",
     "yt_tags": ["nostaljik", "kamera", "y2k"]},

    {"title": "Sanyo Xacti İnceleme: Y2K Döneminin Efsanevi Video Kamerası",
     "keyword": "sanyo xacti",
     "secondary_keywords": ["sanyo xacti fiyat", "sanyo retro kamera", "xacti video kamera"],
     "tags": "sanyo, xacti, video kamera, retro, y2k, retrocameraland",
     "meta_desc": "Sanyo Xacti kapsamlı inceleme: 2000'lerin ikonik dikey video kamerası. Teknik özellikler, Türkiye fiyatı ve koleksiyon değeri.",
     "image_prompt": "Sanyo Xacti vertical grip digital video camera Y2K 2000s retro aesthetic silver blue compact",
     "angle": "Sanyo Xacti'nin dikey formu TikTok nesline neden bu kadar tanıdık geliyor?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["sanyo", "xacti", "video"]},

    # ── GSC Hidden Gems (Rank 20+, büyüme potansiyeli) ────────────────────────
    {"title": "Vintage Fotoğraf Makinesi Koleksiyonu: 2026'nın En Değerli Retro Modeller",
     "keyword": "vintage fotoğraf makinesi",
     "secondary_keywords": ["vintage fotoğraf makinesi koleksiyon", "eski model dijital kamera", "vintage kamera değer"],
     "tags": "vintage fotoğraf makinesi, koleksiyon, değer, retrocameraland",
     "meta_desc": "Vintage fotoğraf makinesi koleksiyonu için en değerli 2000'ler modelleri. Değer artışı beklenen kameralar ve 2026 fiyat rehberi.",
     "image_prompt": "vintage digital camera collection 2000s models value appreciation retro aesthetic flat lay warm",
     "angle": "Hangi vintage fotoğraf makineleri 2026'da yatırım değeri taşıyor?",
     "search_intent": "bilgi + satın alma",
     "yt_tags": ["vintage", "fotoğraf", "koleksiyon"]},
]

def pick_topics(trends, published, count):
    all_titles  = set(t.lower() for t in published)     # tüm zamanların tam başlık geçmişi (kısa pencere DEĞİL)
    title_prefixes_seen = set(_strip_title_suffix(t) for t in published)
    recent_ctx  = list(published)[-20:]                  # LLM'e sadece son 20'yi bağlam olarak ver
    kw_hist     = load_keyword_history()
    ent_hist    = load_entity_history()

    def is_fresh(t):
        """Aynı başlık, aynı ana keyword (cooldown içinde), aynı marka+model varlığı
        (cooldown içinde, farklı 'açı'yla olsa bile) VEYA sadece tarih/yıl eki farklı
        aynı başlık (havuz-tükendi varyasyon üretiminin ürettiği kalıp) tekrar seçilemez."""
        if t.get('title', '').lower() in all_titles:
            return False
        if keyword_on_cooldown(t.get('keyword', ''), kw_hist):
            return False
        if entity_on_cooldown(extract_entities(t.get('title', ''), t.get('keyword', '')), ent_hist):
            return False
        if _strip_title_suffix(t.get('title', '')) in title_prefixes_seen:
            return False
        return True

    def dedupe_by_keyword(items, n):
        """Aynı batch içinde de aynı ana keyword iki kez seçilmesin (ör. yıl eki farklı
        iki 'sony dsc-t9' varyantı aynı gün yayınlanmasın)."""
        picked, used_kw = [], set()
        for t in items:
            nk = _normalize_kw(t.get('keyword', ''))
            if nk in used_kw:
                continue
            picked.append(t)
            used_kw.add(nk)
            if len(picked) >= n:
                break
        return picked

    web_ctx = "\n".join(f"- {r['title']}: {r['snippet'][:100]}" for r in trends['web'][:6])
    tw_ctx  = ", ".join(trends['twitter'][:15]) or "yok"
    price_data = get_real_price_snapshot()
    stock_titles = [p["title"] for p in price_data["in_stock"]]
    prod_ctx = "\n".join(f"- {p['model']} ({p['keyword']})" for p in TOP_PRODUCTS)
    broad_ctx = ", ".join(stock_titles[:30]) if stock_titles else prod_ctx

    global_models = research_global_camera_models()
    global_ctx = "\n".join(
        f"- {m.get('model','?')} ({m.get('brand','?')}, {m.get('era','?')}): {m.get('why','')}"
        for m in global_models[:40]
    ) if global_models else ""

    system = (
        "Sen retrocameraland.com için uzman bir Türk SEO stratejistisin. "
        "retrocameraland.com Türkiye'nin en büyük retro dijital kamera mağazası. "
        f"Hedef kitle: {TARGET_AUDIENCE} Sadece retrocameraland ile DOĞRUDAN İLGİLİ konular seç."
    )
    user = f"""Bugünkü ({trends['date']}) verilere dayanarak {count} SEO blog konusu öner.

## Güncel Web Trendleri (retro kamera odaklı)
{web_ctx}

## Türkiye Twitter/X Trendleri
{tw_ctx}

## retrocameraland.com — En Çok Trafik Alan Ürünler (referans, TEK kaynak DEĞİL)
{prod_ctx}

## retrocameraland.com — Şu an stoktaki TÜM modeller (konu çeşitliliği için — her seferinde
## aynı 2-3 modele saplanma, aşağıdaki geniş listeden de seç)
{broad_ctx}

## Dünya Çapında Popüler/İkonik Modeller (Claude araştırması — RCL stoğuyla SINIRLI DEĞİL,
## amaç "tüm dijital kamera modelleriyle ilgili kapsamlı blog kütüphanesi". Bu modeller
## hakkında da yazabilirsin — MODEL_SCOPE_RULES'a göre stok durumunu dürüstçe belirt ve
## en yakın stoktaki RCL alternatifine link ver)
{global_ctx or "— (bu koşuda araştırma verisi yok, yukarıdaki listelerden seç)"}

## Öncelikli Keyword Fırsatları (bunları hedefle, ama TEK kaynak olarak kullanma —
## her koşuda bu SABİT listeye saplanmak aynı 2-3 konunun sürekli tekrar seçilmesine
## yol açtı; farklı model/açı kombinasyonları da dene)
YÜKSEK HACİM (18K-7K/ay): dijital kamera 2026, retro kamera türkiye, ucuz dijital kamera, fujifilm finepix, y2k kamera
ORTA REKABET (4.8K-1.9K/ay): 3000 tl dijital kamera, canon ixus fiyat, nikon coolpix vintage, ccd kamera nedir, kamera batarya uyumlu
AI SEARCH HEDEFİ: en iyi retro kamera 2026, hangi dijital kamera almalıyım, fujifilm mi canon mu, 3000 tl kamera önerisi, y2k fotoğrafçılık nasıl yapılır

## Daha Önce Yayınlananlar (BUNLARI SEÇME — hiçbirinin konusu/keyword'ü/marka+model çifti tekrar edilmeyecek)
{json.dumps(recent_ctx, ensure_ascii=False)}

{MODEL_SCOPE_RULES}

Konu seçim kriterleri:
- Yukarıdaki Keyword Fırsatları listesinden en az 1 konu seç AMA hepsi aynı 1-2 ürün
  çiftine (ör. sürekli aynı marka karşılaştırması) odaklanmasın — model/açı çeşitlendir
- retrocameraland.com ürünleriyle DOĞRUDAN ilgili (kamera modeli, Y2K estetik, retro fotoğraf)
- Popüler ama şu an stokta olmayan modeller hakkında da yazılabilir (yukarıdaki kural)
- Türkiye'de Google ve AI arama motorlarında yüksek görünürlük için optimize et
- Blog içinde Instagram, TikTok, YouTube, Pinterest, LinkedIn yönlendirmeleri ve retrocameraland.com site linki olacak
- Her konunun farklı bir açısı olsun (model inceleme, rehber, karşılaştırma, ipuçları)

Her konu için TAM JSON:
[
  {{
    "title": "Türkçe SEO başlık — MUTLAKA 52-68 karakter, kısa kabul edilmez",
    "keyword": "Ana anahtar kelime (Türkçe, Türkiye'de aranan)",
    "secondary_keywords": ["kw1", "kw2", "kw3"],
    "tags": "tag1, tag2, retrocameraland",
    "meta_desc": "Meta açıklama MUTLAKA 148-165 karakter — keyword ilk 30 karakterde olmalı",
    "image_prompt": "English image prompt: retro Y2K camera specific scene",
    "angle": "Benzersiz açı (1 cümle Türkçe)",
    "search_intent": "bilgi|karşılaştırma|satın alma|rehber",
    "yt_tags": ["ilgili", "etiketler"]
  }}
]

SADECE JSON döndür."""

    try:
        raw = groq_write(system, user, max_tokens=2000, temperature=0.8)
        topics = _extract_json_array(raw)
        if topics:
            # Groq bazen istenen şemaya tam uymuyor (ör. birden fazla ayrı [...] bloğu +
            # aralarında düz metin döndürüyor — 2026-07-26'da tespit edildi). dict OLMAYAN
            # öğeleri sessizce ele, tek bozuk madde tüm batch'i çökertmesin.
            topics = [t for t in topics if isinstance(t, dict)]
        if topics:
            # Fix title/meta/keyword alignment ÖNCE, tazelik kontrolü SONRA yapılmalı —
            # aksi halde _fix_topic_lengths'in değiştirdiği başlık tekrar kontrolünden kaçabilir
            for t in topics:
                _fix_topic_lengths(t)
            fresh = dedupe_by_keyword([t for t in topics if is_fresh(t)], count)
            if fresh:
                log(f"✓ Groq: {len(fresh)} konu")
                return fresh
    except Exception as e:
        log(f"⚠ Konu seçimi hatası: {e}")

    import random
    pool = [t for t in FALLBACK_POOL if is_fresh(t)]
    if len(pool) < count:
        # Sabit havuz (24 konu) tükendi — yıl/ay ekiyle varyasyonlanmış tazeler üret,
        # aynı başlığı aylarca kelimesi kelimesine tekrar yayınlamak yerine
        extra_needed = count - len(pool)
        variants, seen_titles = [], {t['title'].lower() for t in pool}
        month_tr = trends.get('month', '')
        for base in FALLBACK_POOL:
            for sfx in (f" — {datetime.now().year}", f" ({month_tr})" if month_tr else ""):
                if not sfx:
                    continue
                v = dict(base)
                v['title'] = (base['title'].rstrip('.') + sfx)[:70]
                if is_fresh(v) and v['title'].lower() not in seen_titles:
                    variants.append(v)
                    seen_titles.add(v['title'].lower())
                if len(variants) >= extra_needed:
                    break
            if len(variants) >= extra_needed:
                break
        pool = pool + variants

    if not pool:
        # ACİL SON ÇARE — 2 kademe. FALLBACK_POOL sadece ~26 konudan oluşuyor; tam 45-60
        # günlük cooldown'lar bu havuzu tamamen tıkayıp SIFIR YAYIN'a yol açabiliyor
        # (2026-07-26 00:00 koşusunda tam olarak bu oldu — 26/26 konu bloklandı, hiçbir
        # şey yayınlanmadı). AMA cooldown'u TÜMDEN yok saymak da yanlış — ilk denemede
        # öyle yapılınca, birkaç saat önce birleştirilmiş bir konunun neredeyse-aynısı
        # tekrar üretildi (2026-07-26, canlı testte tespit edildi). Bu yüzden önce KISA
        # bir pencereyle (6 gün) dene — hem sıfır-yayını önler hem yakın zamanda
        # birleştirilmiş/yayınlanmış konuları tekrar üretmez.
        month_tr = trends.get('month', '')
        def _variants(base):
            return [base] + [
                {**base, 'title': (base['title'].rstrip('.') + sfx)[:70]}
                for sfx in (f" — {datetime.now().year}", f" ({month_tr})" if month_tr else "")
                if sfx
            ]

        for short_days, ignore_cooldown in ((6, False), (0, True)):
            emergency, seen = [], set()
            for base in FALLBACK_POOL:
                for v in _variants(base):
                    tl = v['title'].lower()
                    if tl in all_titles or tl in seen:
                        continue
                    if _strip_title_suffix(v['title']) in title_prefixes_seen:
                        continue
                    if not ignore_cooldown:
                        ents = extract_entities(v.get('title', ''), v.get('keyword', ''))
                        if entity_on_cooldown(ents, ent_hist, days=short_days):
                            continue
                        if keyword_on_cooldown(v.get('keyword', ''), kw_hist, days=short_days):
                            continue
                    emergency.append(v)
                    seen.add(tl)
                    break
            if emergency:
                tier = f"{short_days} günlük kısa cooldown ile" if not ignore_cooldown else "cooldown tamamen göz ardı edilerek (son çare)"
                log(f"⚠ Havuz normal cooldown'la tamamen bloklandı — acil son çare: {len(emergency)} "
                    f"konu {tier} kullanılabilir hale getirildi")
                pool = emergency
                break

        if not pool:
            log("⚠ Konu havuzu tamamen tükendi (tam-aynı-başlıklar bile tükendi) — bu döngüde yeni konu üretilemedi")
            return []
    random.shuffle(pool)
    selected = dedupe_by_keyword(pool, count)
    for t in selected:
        _fix_topic_lengths(t)
    return selected

def _fix_topic_lengths(t):
    """Title 50-70 kar, keyword başlıkta, meta_desc 148-165 kar garantile."""
    kw    = t.get('keyword', '')
    title = t.get('title', '')

    # Keyword başlıkta yoksa ekle (token-bazlı kontrol)
    kw_words_fix = kw.lower().split()
    kw_in_title = kw.lower() in title.lower() or all(w in title.lower() for w in kw_words_fix)
    if kw and not kw_in_title:
        kw_cap = kw.title()
        title = f"{kw_cap}: {title}" if len(title) <= 50 else f"{title.rstrip('.')} — {kw_cap}"
        t['title'] = title

    # Başlık çok kısa (<50) — uzun suffix ile büyüt
    if len(title) < 50:
        suffix = f" — {datetime.now().year} Türkiye Rehberi ve Satın Alma İpuçları"
        t['title'] = (title + suffix)[:70]
        title = t['title']

    # Başlık çok uzun (>70) — kırp
    if len(title) > 70:
        t['title'] = title[:68].rstrip(' —:,') + "…"

    # Meta desc — her zaman 148-165 karakter aralığında garantile
    meta = t.get('meta_desc', '')
    if len(meta) < 148:
        pool = [
            f" {kw} için Türkiye'nin en kapsamlı rehberi retrocameraland.com'da.",
            f" Fiyat, model karşılaştırması ve profesyonel ipuçları burada.",
            f" retrocameraland.com'da test edilmiş {kw} içerikleri.",
        ]
        for ext in pool:
            meta += ext
            if len(meta) >= 148:
                break
    t['meta_desc'] = meta[:165]


# ── Temalı Kampanya: Öğrenci & Sevgili (ay sonuna kadar) ───────────────────────
# İstek: bu ay (Haziran 2026) sonuna kadar yayınlanan HER İKİ blogtan BİRİ
# "öğrenciler için kamera önerileri" veya "sevgiliye/çiftlere retro kamera hediyesi"
# temasında olsun. İki tema her temalı slotta sırayla döner (öğrenci → sevgili → …).
# Bu tarihten sonra ajan otomatik olarak normal akışına döner — kod değişikliği gerekmez.
THEME_DEADLINE = datetime(2026, 7, 1)
THEME_STATE_FILE = '/Users/onnoshot/Downloads/Agentlar/themed-blog-state.json'

THEME_CONFIG = {
    "student": {
        "label": "Öğrenciler için kamera önerileri",
        "keywords": [
            "öğrenci için dijital kamera", "öğrenci bütçesine uygun retro kamera",
            "uygun fiyatlı dijital kamera öğrenci", "kampüs için kompakt kamera",
            "harçlıkla alınabilecek retro kamera", "yurt için dijital kamera",
            "ucuz Y2K kamera öğrenci", "öğrenci kamera önerisi 2026",
        ],
        "angles": [
            "Sınırlı harçlıkla en iyi retro dijital kamera nasıl seçilir",
            "Kampüs ve sosyal medya içeriği için ideal, cepte taşınan kompakt retro kameralar",
            "Öğrenci bütçesine uygun, test edilmiş ve garantili retro modeller — telefon yerine gerçek karakter",
            "Mezuniyet, dönem başı ve kampüs anıları için bütçe dostu Y2K kameralar",
        ],
        "img": [
            "affordable retro digital camera for students campus Y2K aesthetic flat lay budget",
            "student backpack with compact retro CCD camera campus life Y2K social content warm tones",
            "budget Y2K digital cameras collection for students under budget pastel flat lay 2026",
        ],
        "titles": [
            "Öğrenciler İçin En İyi Retro Dijital Kamera Önerileri 2026",
            "Öğrenci Bütçesine Uygun Y2K Retro Kamera Seçim Rehberi",
            "Kampüs Fotoğrafçılığı: Öğrenciler İçin Uygun Fiyatlı Kameralar",
            "Harçlıkla Alınır Retro Kamera: Öğrenci Satın Alma Rehberi 2026",
        ],
        "tags": "öğrenci kamera, uygun fiyatlı, retro kamera, y2k, retrocameraland",
        "yt_tags": ["retro", "kamera", "öğrenci", "uygun fiyat"],
        "philosophy": (
            "Hedef kitle üniversite/lise öğrencileri: bütçe sınırlı, sosyal medya için estetik içerik "
            "üretmek istiyorlar, dayanıklı ve kolay taşınır kamera arıyorlar. retrocameraland felsefesi: "
            "her kamera test edilip garantilenir, özel kutuda çekime hazır gelir, İstanbul içi aynı gün teslim. "
            "Telefonun veremediği Y2K/CCD karakteri vurgulanır. Somut bütçe aralıkları ve model isimleri ver."
        ),
    },
    "lover": {
        "label": "Sevgiliye/çiftlere retro kamera hediyesi",
        "keywords": [
            "sevgiliye hediye kamera", "çift için retro kamera",
            "yıldönümü hediyesi kamera", "sevgiliyle fotoğraf çekmek için kamera",
            "romantik hediye fikri retro kamera", "ikimize özel kamera anıları",
            "sevgiliye anlamlı hediye kamera", "çiftler için Y2K kamera",
        ],
        "angles": [
            "Sevgilinize unutulmaz bir anı hediye etmenin en şık ve nostaljik yolu",
            "Çift olarak retro kamerayla anıları ölümsüzleştirmek — telefon değil, gerçek bir hatıra makinesi",
            "Yıldönümü ve özel günler için beraber kullanacağınız retro kamera seçimi",
            "İkinize özel romantik içerik üretmek için Y2K estetiğinde retro kameralar",
        ],
        "img": [
            "romantic gift retro digital camera for couple Y2K aesthetic gift box warm tones flat lay",
            "couple taking photos together with retro CCD camera nostalgic warm romantic Y2K",
            "anniversary gift retro digital camera in gift box ribbon pastel romantic flat lay 2026",
        ],
        "titles": [
            "Sevgiliye Hediye Retro Dijital Kamera: Anlamlı Hediye Rehberi",
            "Çift İçin Retro Kamera: İkinizin Anılarını Ölümsüzleştirin 2026",
            "Yıldönümü Hediyesi Fikri: Sevgiliye Retro Dijital Kamera 2026",
            "Sevgiliyle Kullanmak İçin En İyi Retro Kamera Önerileri 2026",
        ],
        "tags": "sevgiliye hediye, çift kamera, yıldönümü, retro kamera, retrocameraland",
        "yt_tags": ["retro", "kamera", "hediye", "çift", "y2k"],
        "philosophy": (
            "Hedef kitle sevgilisine/eşine anlamlı bir hediye arayan kişiler ve birlikte anı biriktirmek "
            "isteyen çiftler. retrocameraland felsefesi: her kamera test edilip garantilenir, özel hediye "
            "kutusunda çekime hazır gelir, romantik bir hatıra makinesidir. Telefonun veremediği filmsi/CCD "
            "karakteri ve 'birlikte kullanma' deneyimi vurgulanır. Hediye olarak alma çağrısı (satın alma) net olsun."
        ),
    },
}
THEME_ORDER = ["student", "lover"]


def _load_theme_count():
    try:
        if os.path.exists(THEME_STATE_FILE):
            return int(json.load(open(THEME_STATE_FILE, encoding='utf-8')).get('count', 0))
    except Exception:
        pass
    return 0


def _save_theme_count(n):
    try:
        json.dump({'count': n}, open(THEME_STATE_FILE, 'w', encoding='utf-8'))
    except Exception as e:
        log(f"⚠ tema state kaydı: {e}")


def _themed_fallback(theme_key, idx, used):
    """LLM başarısız olursa garantili temalı konu üret (bank'tan). Üretilen başlık
    _fix sonrası bile yayınlananlarla çakışmaz — gerekirse yıl/ay eki ile benzersizleşir."""
    cfg = THEME_CONFIG[theme_key]
    n = len(cfg["titles"])
    kw  = cfg["keywords"][idx % len(cfg["keywords"])]
    suffixes = ["", f" ({datetime.now().year})", f" — {('Ocak Şubat Mart Nisan Mayıs Haziran Temmuz Ağustos Eylül Ekim Kasım Aralık'.split())[datetime.now().month-1]}"]
    for off in range(n):
        for sfx in suffixes:
            base_title = cfg["titles"][(idx + off) % n]
            t = {
                "title": (base_title + sfx)[:70],
                "keyword": kw,
                "secondary_keywords": [cfg["keywords"][(idx + 1) % len(cfg["keywords"])],
                                       cfg["keywords"][(idx + 2) % len(cfg["keywords"])], "retro kamera"],
                "tags": cfg["tags"],
                "meta_desc": f"{kw} arayanlar için retrocameraland.com rehberi: test edilmiş, garantili retro dijital kameralar, fiyat aralıkları ve profesyonel öneriler.",
                "image_prompt": cfg["img"][idx % len(cfg["img"])],
                "angle": cfg["angles"][idx % len(cfg["angles"])],
                "search_intent": "rehber + satın alma",
                "yt_tags": cfg["yt_tags"],
                "theme": theme_key,
            }
            _fix_topic_lengths(t)
            if t["title"].lower() not in used:
                return t
    return t  # hepsi kullanılmışsa son üretilen (çok nadir)


def pick_themed_topic(trends, used, theme_key, idx):
    """Belirli temada (öğrenci/sevgili) tek bir SEO konu üret — LLM, başarısızsa bank fallback."""
    cfg = THEME_CONFIG[theme_key]
    seed_kw    = cfg["keywords"][idx % len(cfg["keywords"])]
    seed_angle = cfg["angles"][idx % len(cfg["angles"])]
    seed_img   = cfg["img"][idx % len(cfg["img"])]
    web_ctx = "; ".join(r['title'] for r in trends.get('web', [])[:3]) or "retro kamera trendleri"

    system = (
        "Sen retrocameraland.com için uzman bir Türk SEO stratejistisin. "
        "retrocameraland.com Türkiye'nin en büyük retro dijital (CCD/Y2K) kamera mağazası. "
        f"BU KONU ŞU TEMADA OLMALI: {cfg['label']}. {cfg['philosophy']}"
    )
    user = f"""Aşağıdaki tema için retrocameraland.com'a 1 adet SEO blog konusu öner.

Tema: {cfg['label']}
Önerilen ana keyword (kullan veya çok benzerini kullan): "{seed_kw}"
Önerilen açı: {seed_angle}
Güncel trend bağlamı: {web_ctx}

Kurallar:
- Konu DOĞRUDAN retrocameraland retro dijital kameralarına yönlendirsin ve satın almaya teşvik etsin
- Türkiye'de Google + AI aramada görünür, gerçek bir soruyu yanıtlayan açı
- Blog içinde Instagram/TikTok/YouTube yönlendirmeleri ve site linki olacağını varsay
- Daha önce yayınlananlardan FARKLI olsun: {json.dumps(list(used)[-12:], ensure_ascii=False)}

SADECE şu JSON'u döndür (tek obje, dizi değil):
{{
  "title": "Türkçe SEO başlık — MUTLAKA 52-68 karakter",
  "keyword": "ana anahtar kelime (Türkçe)",
  "secondary_keywords": ["kw1", "kw2", "kw3"],
  "tags": "tag1, tag2, retrocameraland",
  "meta_desc": "148-165 karakter, keyword ilk 30 karakterde",
  "image_prompt": "{seed_img}",
  "angle": "benzersiz açı (1 cümle Türkçe)",
  "search_intent": "rehber|satın alma|karşılaştırma",
  "yt_tags": {json.dumps(cfg['yt_tags'], ensure_ascii=False)}
}}"""

    ent_hist = load_entity_history()
    used_prefixes = set(_strip_title_suffix(u) for u in used)

    try:
        raw = groq_write(system, user, max_tokens=900, temperature=0.85)
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            t = json.loads(m.group(0))
            if t.get('title', '').lower() not in used:
                t.setdefault('image_prompt', seed_img)
                t['theme'] = theme_key
                _fix_topic_lengths(t)
                ents = extract_entities(t.get('title', ''), t.get('keyword', ''))
                fresh = (t['title'].lower() not in used
                         and not entity_on_cooldown(ents, ent_hist)
                         and _strip_title_suffix(t.get('title', '')) not in used_prefixes)
                if fresh:
                    log(f"  ✓ Temalı konu ({cfg['label']}): {t['title'][:50]}")
                    return t
    except Exception as e:
        log(f"  ⚠ Temalı konu LLM hatası ({theme_key}): {e}")

    t = _themed_fallback(theme_key, idx, used)
    log(f"  ✓ Temalı konu [fallback] ({cfg['label']}): {t['title'][:50]}")
    return t


def inject_themed_topics(topics, published, count, trends):
    """Ay sonuna kadar: her iki slottan birini (index 0,2,…) temalı konuyla değiştir.
    Temalar öğrenci/sevgili sırayla döner; sayaç themed-blog-state.json'da tutulur."""
    if datetime.now() >= THEME_DEADLINE:
        return topics
    used = set(t.lower() for t in published)
    out = list(topics)
    base = _load_theme_count()
    made = 0
    for i in range(0, count, 2):
        theme_key = THEME_ORDER[(base + made) % len(THEME_ORDER)]
        themed = pick_themed_topic(trends, used, theme_key, base + made)
        if not themed:
            continue
        if i < len(out):
            out[i] = themed
        else:
            out.append(themed)
        used.add(themed['title'].lower())
        made += 1
    if made:
        _save_theme_count(base + made)
        log(f"✓ Temalı kampanya: {made} temalı konu enjekte edildi (toplam sayaç: {base + made})")
    return out


# ── Blog Generation ────────────────────────────────────────────────────────────
def generate_blog_html(topic, trends, attempt=0):
    """5 Groq çağrısıyla garantili 1600+ kelime, iç link enjeksiyonlu SEO blog."""
    kw    = topic['keyword']
    kws   = ', '.join(topic.get('secondary_keywords', []))
    date  = trends['date']
    month = trends.get('month', '')
    angle = topic.get('angle', '')

    web_snip = "; ".join(r['title'] for r in trends['web'][:3]) or f"retro kamera {datetime.now().year}"
    tw_snip  = ", ".join(trends['twitter'][:8]) or "y2k estetik, retro fotoğraf"

    price_data = get_real_price_snapshot()

    sys_base = (
        f"Sen retrocameraland.com için profesyonel bir Türkçe SEO içerik yazarısın. "
        f"SADECE HTML döndür. <h1> kullanma. Markdown blok kullanma. "
        f"Ana keyword: '{kw}'. İkincil keywordler: {kws}. Tarih: {date}. "
        f"Her bölüm için EN AZ 350 kelime yaz — kısa tutma, detaylı ol. "
        f"Keyword yoğunluğu 1-2% olsun — aşırı tekrar YOK. "
        f"KESİN KURAL — UYDURMA YASAK: Doğrulayamayacağın kesin sayısal iddialar (kesin pil ömrü "
        f"saati, kesin çözünürlük gibi) UYDURMA. Var olmayan marka veya model İCAT ETME. "
        f"{price_data['prompt_block']} "
        f"HEDEF KİTLE: {TARGET_AUDIENCE} "
        f"{NATURAL_VOICE_RULES} "
        f"{MODEL_SCOPE_RULES} "
        f"AI-ARAMA SAYFA YAPISI (GEO — Princeton/Georgia Tech/IIT Delhi araştırması): Her H2 "
        f"altındaki İLK cümle 'X, ...dır/...bir Y'dir' gibi TANIM-ÖNCE olsun (ChatGPT/Perplexity "
        f"bu cümleleri doğrudan alıntılıyor, +2.1x alıntılanma). Mümkün olduğunda somut bir "
        f"istatistik/rakam + kaynak belirt (ör. 'X modeli Y yılında çıktı' — +%40 alıntılanma). "
        f"En az bir H2'yi soru formunda yaz (kullanıcıların gerçekte aradığı gibi)."
    )

    # ── Bölüm 1: Giriş + Temel Bilgi ─────────────────────────────────────────
    p1 = _write(sys_base, f"""Konu: {topic['title']}
Ana keyword: '{kw}' — bu kelime ilk cümlede MUTLAKA geçmeli.
Açı: {angle}
Trend bağlamı: {web_snip[:120]} | Twitter/X: {tw_snip[:80]}

ŞU BÖLÜMLERI YAZ — her biri EN AZ 350 kelime:

<p>[İLK KELİME OLARAK '{kw}' ile başla veya ilk cümlede '{kw}' geçsin.
Türkiye'deki Y2K ve retro kamera trendine güncel tarih ({date}) ile referans.
{month} ayında bu konu neden önemli. Kim aramalı, ne beklemeli.]</p>

<div class="rcl-quick-answer" style="background:#f7f4ef;border-left:3px solid #1a1a1a;padding:14px 18px;margin:18px 0">
<strong>Hızlı Cevap:</strong> [AI arama motorlarının (ChatGPT, Perplexity, Google AI Overview)
doğrudan alıntılayabileceği, KENDİ BAŞINA ANLAMLI 55-75 kelimelik tek paragraf. '{kw}' sorusunu
tanım-önce cümleyle (ör. "{kw}, ... olan bir ...dır") yanıtla, somut 1 rakam/istatistik veya
karşılaştırma noktası ekle. Bu kutu makalenin geri kalanını okumadan da tek başına cevap versin.]</div>

<p>[İkinci güçlü paragraf — Türkiye'deki retro fotoğraf kültürü, gençlerin ilgisi, sosyal medya etkisi]</p>

<h2>{kw}: Kapsamlı Teknik İnceleme</h2>
<p>[Detaylı teknik açıklama — sensör, lens, ekran, batarya, boyutlar, renk seçenekleri]</p>
<ul>
<li><strong>Sensör:</strong> [tam açıklama]</li>
<li><strong>Lens:</strong> [açıklama]</li>
<li><strong>Ekran:</strong> [açıklama]</li>
<li><strong>Batarya:</strong> [açıklama]</li>
<li><strong>Özel Özellikler:</strong> [açıklama]</li>
<li><strong>Boyutlar ve Ağırlık:</strong> [açıklama]</li>
</ul>

<h2>Y2K Estetiği ve {kw}: Neden Bu Kadar Popüler?</h2>
<p>[Y2K estetik trendini detaylı anlat — neden CCD sensörlü kameralar Y2K görünümü verir,
Instagram/TikTok'ta nasıl kullanılıyor, hangi filtreler/efektler benzer sonuç verir]</p>
<p>[Türkiye'deki içerik üreticilerinin tercihi, sosyal medya algoritması etkisi]</p>

SADECE HTML. Her bölüm çok detaylı olsun.""")

    # ── Bölüm 2: Kullanım + Türkiye Pazarı ───────────────────────────────────
    p2 = _write(sys_base, f"""Konu: {topic['title']} — kullanım rehberi ve piyasa analizi

ŞU BÖLÜMLERI YAZ — her biri EN AZ 350 kelime:

<h2>{kw} ile Nasıl Fotoğraf Çekilir? Adım Adım Rehber</h2>
<p>[Kapsamlı kullanım rehberi — başlangıçtan ileri seviyeye]</p>
<ol>
<li><strong>Doğru Mod Seçimi:</strong> [2-3 cümle detaylı açıklama]</li>
<li><strong>Işık Koşulları:</strong> [açıklama — gündüz, gece, iç mekan]</li>
<li><strong>Flaş Kullanımı:</strong> [ne zaman açık/kapalı, Y2K etkisi için]</li>
<li><strong>Kompozisyon İpuçları:</strong> [portre, sokak, still life için özel ipuçları]</li>
<li><strong>Düzenleme ve Paylaşım:</strong> [hangi uygulamalar, minimal düzenleme felsefesi]</li>
</ol>

<h2>Türkiye'de {kw}: Fiyat ve Satın Alma Rehberi</h2>
<p>[Türkiye pazarı — detaylı fiyat analizi, nerede bulunur (retrocameraland.com dahil),
sahte/bozuk ürün nasıl anlaşılır, garantili alım için ipuçları. Fiyat rakamı verirken
sistem talimatındaki GERÇEK GÜNCEL STOK FİYATLARI listesini kullan — o listede olan bir
modelden bahsediyorsan GERÇEK fiyatını yaz, listede yoksa göreli ifade kullan, uydurma.]</p>
<table style="width:100%;border-collapse:collapse;margin:16px 0">
<thead><tr style="background:#f0ece8">
<th style="padding:10px;border:1px solid #ddd;text-align:left">Kriter</th>
<th style="padding:10px;border:1px solid #ddd;text-align:left">Detay</th>
</tr></thead>
<tbody>
<tr><td style="padding:9px;border:1px solid #ddd">Fiyat Aralığı</td><td style="padding:9px;border:1px solid #ddd">[GERÇEK STOK FİYATLARI listesinden — bu modelin veya en yakın benzerin gerçek fiyatı, yoksa göreli aralık]</td></tr>
<tr><td style="padding:9px;border:1px solid #ddd">Nereden Alınır</td><td style="padding:9px;border:1px solid #ddd">retrocameraland.com, ikinci el platformlar</td></tr>
<tr><td style="padding:9px;border:1px solid #ddd">Dikkat Edilecekler</td><td style="padding:9px;border:1px solid #ddd">[kontrol listesi]</td></tr>
<tr><td style="padding:9px;border:1px solid #ddd">Aksesuarlar</td><td style="padding:9px;border:1px solid #ddd">[batarya, kılıf, SD kart]</td></tr>
</tbody></table>
<p>[3-4 cümle piyasa yorumu]</p>

SADECE HTML. Her bölüm çok detaylı olsun.""")

    # ── Bölüm 3: Karşılaştırma + İpuçları ────────────────────────────────────
    # Karşılaştırma çeşitliliği için sadece sabit 5 TOP_PRODUCTS değil, o an stoktaki
    # tüm modellerden geniş bir örneklem ver — aynı 2-3 modelin sürekli tekrar
    # karşılaştırılmasını önler (RCL'nin Fujifilm T200 vs Sony DSC-T9 sorunu buradan
    # da besleniyordu: LLM hep aynı dar listeden seçiyordu).
    stock_models = [p["title"] for p in price_data["in_stock"]]
    real_models = ", ".join(stock_models[:20]) if stock_models else ", ".join(p['model'] for p in TOP_PRODUCTS)
    p3 = _write(sys_base, f"""Konu: {topic['title']} — karşılaştırma ve ipuçları

ŞU BÖLÜMLERI YAZ — her biri EN AZ 350 kelime:

<h2>Rakip Modellerle Karşılaştırma: {kw} vs Alternatifler</h2>
<p>[Kapsamlı karşılaştırma — SADECE gerçekten var olan modellerden bahset. Karşılaştırma için
şu GERÇEK retrocameraland modellerinden FARKLI ikisini seç (her blogda aynı 1-2 modeli tekrar
tekrar seçme, çeşitlendir): {real_models}. Bunların dışında bilmediğin/emin olmadığın bir
model İCAT ETME — bilmiyorsan genel kategori adıyla ("benzer bir CCD kompakt model" gibi)
an, uydurma özel isim verme.]</p>
<table style="width:100%;border-collapse:collapse;margin:16px 0">
<thead><tr style="background:#f0ece8">
<th style="padding:10px;border:1px solid #ddd">Model</th>
<th style="padding:10px;border:1px solid #ddd">Artıları</th>
<th style="padding:10px;border:1px solid #ddd">Eksileri</th>
<th style="padding:10px;border:1px solid #ddd">Fiyat Segmenti</th>
</tr></thead>
<tbody>
<tr><td style="padding:8px;border:1px solid #ddd">{kw}</td><td style="padding:8px;border:1px solid #ddd">[artılar]</td><td style="padding:8px;border:1px solid #ddd">[eksiler]</td><td style="padding:8px;border:1px solid #ddd">[GERÇEK STOK FİYATLARI listesinde varsa gerçek TL rakamı, yoksa uygun/orta/üst segment]</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd">[gerçek model adı]</td><td>[artılar]</td><td>[eksiler]</td><td>[gerçek fiyat veya segment]</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd">[gerçek model adı]</td><td>[artılar]</td><td>[eksiler]</td><td>[gerçek fiyat veya segment]</td></tr>
</tbody></table>
<p>[karşılaştırma sonucu ve önerim — gerçek fiyat verebiliyorsan ver, veremiyorsan göreli kıyasla]</p>

<h2>Uzman İpuçları: {kw} ile Mükemmel Sonuçlar</h2>
<p>[Giriş]</p>
<ul>
<li><strong>İpucu 1 — Doğru Ayarlar:</strong> [detaylı açıklama 2-3 cümle]</li>
<li><strong>İpucu 2 — Işık Kullanımı:</strong> [detaylı açıklama]</li>
<li><strong>İpucu 3 — Kompozisyon:</strong> [detaylı açıklama]</li>
<li><strong>İpucu 4 — Bakım:</strong> [detaylı açıklama]</li>
<li><strong>İpucu 5 — Sosyal Medya Paylaşımı:</strong> [detaylı açıklama]</li>
<li><strong>İpucu 6 — Aksesuarlar:</strong> [detaylı açıklama]</li>
<li><strong>İpucu 7 — Depolama ve Aktarım:</strong> [detaylı açıklama]</li>
</ul>

SADECE HTML. Her bölüm çok detaylı olsun.""")

    # ── Bölüm 4: Hedef Kitle + SSS ───────────────────────────────────────────
    p4 = _write(sys_base, f"""Konu: {topic['title']} — hedef kitle analizi ve SSS

ŞU BÖLÜMLERI YAZ — her biri EN AZ 300 kelime:

<h2>Kimler İçin İdeal? Kullanım Senaryoları</h2>
<p>[Geniş hedef kitle analizi]</p>
<ul>
<li><strong>Sosyal Medya İçerik Üreticileri:</strong> [Instagram, TikTok, YouTube için neden ideal - 3 cümle]</li>
<li><strong>Fotoğraf Tutkunları:</strong> [hobist fotoğrafçılar için avantajlar - 3 cümle]</li>
<li><strong>Nostalji Arayanlar:</strong> [Y2K dönemi atmosferini yeniden yaşamak isteyenler - 3 cümle]</li>
<li><strong>Koleksiyoncular:</strong> [değer artışı, koleksiyon potansiyeli - 3 cümle]</li>
<li><strong>Hediye Arayanlar:</strong> [doğum günü, yılbaşı, mezuniyet hediyesi - 3 cümle]</li>
</ul>
<p>[Bu grupların ortak noktası ve retrocameraland.com'daki model arayışı]</p>

<h2>Sık Sorulan Sorular</h2>

<h3>{kw} fiyatı ne kadar?</h3>
<p>[GERÇEK STOK FİYATLARI listesinde bu model varsa gerçek TL rakamını yaz; yoksa Türkiye'deki
güncel piyasa fiyat aralığını göreli anlat, hangi faktörler fiyatı etkiler — 4 cümle]</p>

<h3>{kw} nereden satın alınır?</h3>
<p>[retrocameraland.com'dan güvenli alım önerisi, nelere dikkat edilmeli — 4 cümle]</p>

<h3>{kw} bataryası ne kadar dayanır?</h3>
<p>[Batarya ömrü, şarj bilgileri, yedek batarya önerileri — 3 cümle]</p>

<h3>{kw} ile hangi fotoğraf türleri çekilir?</h3>
<p>[Portre, sokak, gece, makro çekim kapasitesi — 4 cümle]</p>

<h3>{kw} Y2K fotoğrafları için gerçekten iyi mi?</h3>
<p>[CCD sensör açıklaması, Y2K estetiği neden bu kamerada mükemmel çıkar — 4 cümle]</p>

SADECE HTML. Her cevap kapsamlı olsun.""")

    # ── Bölüm 5: Sonuç + Uzman Görüşü ───────────────────────────────────────
    p5 = _write(sys_base, f"""Konu: {topic['title']} — sonuç ve uzman değerlendirmesi

ŞU BÖLÜMLERI YAZ:

<h2>{kw} ile Retrocameraland'de Alışveriş</h2>
<p>retrocameraland.com, Türkiye'nin en kapsamlı retro dijital kamera koleksiyonunu sunan öncü platformdur.
<a href="https://retrocameraland.com/collections/all">Tüm koleksiyona göz atmak için tıklayın</a> —
Sony, Canon, Fujifilm, Olympus ve daha pek çok markadan onlarca model sizleri bekliyor.</p>
<p>[{kw} modeline özel satın alma tavsiyeleri, hangi aksesuarları birlikte almalı,
garanti ve iade politikaları, müşteri deneyimi — 150+ kelime]</p>
<p>Yeni ürünler ve özel kampanyalar için
<a href="https://retrocameraland.com/blogs/retro-dijital-kamera">retrocameraland.com blogunu</a> takip edin.</p>

<h2>Sonuç: {kw} — Son Değerlendirme</h2>
<p>[Kapsamlı kapanış — 300+ kelime. Tüm konuyu özetle: {kw}'in artıları/eksileri,
kimin alması gerektiği, Y2K estetiğine katkısı, Türkiye'deki retro kamera topluluğunun önemi,
gelecekte değer artışı beklentisi, retrocameraland.com'a son çağrı.]</p>
<p>Bizi takip et:
<a href="{SOCIAL_LINKS['instagram']}" target="_blank" rel="noopener">📷 Instagram</a> &nbsp;|&nbsp;
<a href="{SOCIAL_LINKS['youtube']}" target="_blank" rel="noopener">▶️ YouTube</a> &nbsp;|&nbsp;
<a href="{SOCIAL_LINKS['tiktok']}" target="_blank" rel="noopener">🎵 TikTok</a> &nbsp;|&nbsp;
<a href="{SOCIAL_LINKS['pinterest']}" target="_blank" rel="noopener">📌 Pinterest</a> &nbsp;|&nbsp;
<a href="{SOCIAL_LINKS['linkedin']}" target="_blank" rel="noopener">💼 LinkedIn</a></p>

SADECE HTML. Sonuç bölümü en az 300 kelime olsun.""")

    combined = p1 + "\n" + p2 + "\n" + p3 + "\n" + p4 + "\n" + p5

    # ── Garantili iç link enjeksiyonu ─────────────────────────────────────────
    # p5 zaten 2 link içeriyor ama Groq bazen değiştirebilir — kontrol et
    existing_links = len(re.findall(r'href=["\']https://retrocameraland\.com', combined))
    if existing_links < 2:
        combined += (
            f'\n<p style="margin-top:24px">Retrocameraland koleksiyonunu keşfetmek için: '
            f'<a href="https://retrocameraland.com/collections/all">retrocameraland.com/collections/all</a> '
            f'— <a href="https://retrocameraland.com/blogs/retro-dijital-kamera">Blog yazılarımız için tıklayın</a>.</p>'
        )

    return combined


# ── Publish ─────────────────────────────────────────────────────────────────────
_PRICE_CACHE = None

def get_real_price_snapshot():
    """Shopify'dan GERÇEK, GÜNCEL kamera fiyatlarını çeker (uydurma fiyat yerine).
    Döner: dict {
        'in_stock': [{'title','price','handle'}, ...] (stokta, fiyata göre sıralı),
        'cheapest': en ucuz stoktaki kamera veya None,
        'priciest': en pahalı stoktaki kamera veya None,
        'prompt_block': LLM prompt'una gömülecek hazır metin,
    }
    Süreç içi cache'lenir (bir batch koşusu boyunca tek Shopify çağrısı)."""
    global _PRICE_CACHE
    if _PRICE_CACHE is not None:
        return _PRICE_CACHE
    try:
        resp = shopify("GET", "products.json?limit=250&fields=title,handle,variants,product_type")
        cams = [p for p in resp.get("products", []) if p.get("product_type") == "Digital Camera"]

        def qty(p):
            return sum((v.get("inventory_quantity") or 0) for v in p.get("variants", []))

        in_stock = []
        for p in cams:
            if qty(p) > 0:
                try:
                    price = float(p["variants"][0]["price"])
                except (KeyError, ValueError, TypeError):
                    continue
                in_stock.append({"title": p["title"], "price": price, "handle": p["handle"]})
        in_stock.sort(key=lambda x: x["price"])

        cheapest = in_stock[0] if in_stock else None
        priciest = in_stock[-1] if in_stock else None

        if in_stock:
            lines = [f"- {p['title']}: {p['price']:,.0f} TL".replace(",", ".") for p in in_stock[:25]]
            block = (
                "GERÇEK GÜNCEL STOK FİYATLARI (bugün retrocameraland.com'dan çekildi — "
                "TL rakamı yazarken SADECE bu listeden gerçek fiyat kullan, uydurma YASAK):\n"
                + "\n".join(lines)
                + f"\nEn ucuz stoktaki kamera: {cheapest['title']} — {cheapest['price']:,.0f} TL".replace(",", ".")
                + f"\nEn pahalı stoktaki kamera: {priciest['title']} — {priciest['price']:,.0f} TL".replace(",", ".")
                + "\nBu listede olmayan bir model/marka için KESİN TL rakamı YAZMA — "
                  "'piyasada genelde X-Y TL bandında' gibi göreli ifade kullan. "
                  "Bir bütçe rakamı (ör. '3000 TL') anarken bu bütçenin gerçek stoktaki "
                  "en ucuz fiyatın ALTINDA olup olmadığını kontrol et — altındaysa bunu "
                  "RCL'de o bütçeye tam karşılık gelen bir ürün varmış gibi YAZMA, dürüst ol "
                  "('güncel giriş fiyatımız X TL'den başlıyor' gibi gerçek rakamla düzelt)."
            )
        else:
            block = "Şu anda gerçek stok fiyat verisi çekilemedi — KESİN TL rakamı YAZMA, sadece göreli ifade kullan."

        _PRICE_CACHE = {"in_stock": in_stock, "cheapest": cheapest, "priciest": priciest, "prompt_block": block}
        log(f"  ✓ Gerçek fiyat verisi: {len(in_stock)} stoktaki kamera "
            f"({cheapest['price']:,.0f}-{priciest['price']:,.0f} TL)".replace(",", ".") if in_stock else "  ⚠ Stokta kamera yok")
    except Exception as e:
        log(f"  ⚠ Fiyat verisi çekilemedi: {e}")
        _PRICE_CACHE = {"in_stock": [], "cheapest": None, "priciest": None,
                         "prompt_block": "Fiyat verisi çekilemedi — KESİN TL rakamı YAZMA."}
    return _PRICE_CACHE


_PRODUCT_CACHE = None

def _get_all_products():
    """Shopify kataloğundaki tüm ürünleri tek seferinde çek, cache'le."""
    global _PRODUCT_CACHE
    if _PRODUCT_CACHE is not None:
        return _PRODUCT_CACHE
    try:
        resp = shopify("GET", "products.json?limit=250&fields=title,handle,images,vendor")
        _PRODUCT_CACHE = [p for p in resp.get("products", []) if p.get("images")]
        log(f"  ✓ Ürün kataloğu yüklendi: {len(_PRODUCT_CACHE)} görsellli ürün")
    except Exception as e:
        log(f"  ⚠ Katalog yüklenemedi: {e}")
        _PRODUCT_CACHE = []
    return _PRODUCT_CACHE


def fetch_site_image(keyword, topic_title=""):
    """Shopify ürün kataloğundan konu ile ilgili görsel çek.
    Öncelik: model no → marka + model → marka → kamera ürünleri → rastgele."""
    import random
    combined = (topic_title + " " + keyword).lower()
    products = _get_all_products()
    if not products:
        return None

    BRANDS = {"sony","canon","fujifilm","nikon","panasonic","olympus","casio",
              "kodak","samsung","pentax","minolta","sanyo","ricoh","leica"}
    # Aksesuar/non-kamera ürünleri filtrele (fallback için kameraları tercih et)
    ACCESSORY_KW = {"çanta","bag","pil","batarya","şarj","aksesuar","kılıf","kayış","strap","lens cap"}

    def is_camera(p):
        title_low = p["title"].lower()
        return not any(a in title_low for a in ACCESSORY_KW)

    camera_products = [p for p in products if is_camera(p)]

    # Model numarası adayları — harf+rakam karışımı (dsc-t9, sd400, t200, es65 vb.)
    model_terms = re.findall(r'[a-z]{1,5}-?[0-9]{1,4}[a-z]?|[0-9]{1,4}[a-z]{1,3}', keyword.lower())
    # Keyword'deki anlamlı kelimeler (markalar hariç, 3+ karakter)
    other_terms = [w for w in re.findall(r'[a-z]{3,}', keyword.lower()) if w not in BRANDS and w not in {"kamera","dijital","retro","fiyat","nedir","rehber","satın","al","ile","için"}]
    # Marka adları
    brand_terms = [w for w in combined.split() if w in BRANDS]

    # Arama sırası: model no → diğer keyword kelimeleri → marka
    search_order = model_terms + other_terms + brand_terms

    for term in search_order:
        # Önce kamera ürünlerinde ara
        matches = [p for p in camera_products if term in p["title"].lower()]
        if not matches:
            matches = [p for p in products if term in p["title"].lower()]
        if matches:
            pick = matches[0]
            log(f"  ✓ Ürün görseli: '{pick['title'][:45]}' (arama: '{term}')")
            return pick["images"][0]["src"]

    # Fallback: kamera ürünlerinden rastgele
    pool = camera_products if camera_products else products
    pick = random.choice(pool)
    log(f"  → Katalog fallback görseli: '{pick['title'][:45]}'")
    return pick["images"][0]["src"]


# ── Pinterest panosu (everyday-aesthetic) — birincil görsel kaynağı ────────────
_BOARD_RSS = "https://tr.pinterest.com/retrocameraland/everyday-aesthetic.rss"
_board_cache = []
_board_recent = []

def pinterest_board_image(title):
    """everyday-aesthetic panosundan blog için bir görsel URL'i döndür.
    Kalıcı published-images.json geçmişine karşı kontrol edilir — aynı görsel farklı
    çalıştırmalarda (her cron ayrı process olduğu için in-memory _board_recent yetmez)
    tekrar seçilmez; pano tamamen tükenirse döngüsel olarak yeniden kullanılır."""
    global _board_cache
    import urllib.request, hashlib
    try:
        if not _board_cache:
            req = urllib.request.Request(_BOARD_RSS, headers={"User-Agent": "Mozilla/5.0"})
            xml = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
            for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
                im = re.search(r"https://i\.pinimg\.com/[^\"'<> ]+\.(?:jpg|png)", it)
                if im:
                    _board_cache.append(re.sub(r"/\d+x\d*/", "/originals/", im.group(0)))
        if not _board_cache:
            return None
        used = set(load_image_history())
        idx  = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(_board_cache)
        for _ in range(len(_board_cache)):
            candidate = _board_cache[idx]
            if candidate not in used and idx not in _board_recent:
                break
            idx = (idx + 1) % len(_board_cache)
        else:
            log("  ⚠ Pinterest panosundaki tüm görseller kullanılmış — döngüsel tekrar")
        _board_recent.append(idx); _board_recent[:] = _board_recent[-5:]
        return _board_cache[idx]
    except Exception as e:
        log(f"  ⚠ Pinterest board RSS: {str(e)[:60]}")
        return None

_SLUG_TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")
def _seo_slug(text, maxlen=60):
    s = (text or "").translate(_SLUG_TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:maxlen].rstrip("-") or "retro-kamera")

def _img_b64(url):
    import urllib.request, base64
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return base64.b64encode(urllib.request.urlopen(req, timeout=30).read()).decode()


# ── Ürün Deep-Link Garantisi (AEO/yönlendirme kriteri) ─────────────────────────
def inject_product_deep_links(body_html, topic):
    """Her blog en az 3 spesifik ürün sayfasına linklemeli (genel koleksiyon değil).
    LLM gerçek envanteri bilmediği için bunu her zaman koddan garanti ederiz."""
    existing = len(re.findall(r'href="https://retrocameraland\.com/products/', body_html))
    if existing >= 3:
        return body_html

    combined = (topic.get('title', '') + ' ' + topic.get('keyword', '')).lower()
    words    = [w for w in re.findall(r'[a-z0-9]+', combined) if len(w) > 2]
    products = _get_all_products()
    if not products:
        return body_html

    def relevance(p):
        t = p['title'].lower()
        return sum(1 for w in words if w in t)

    ranked = sorted(products, key=relevance, reverse=True)
    picks, seen_handles = [], set()
    for p in ranked:
        handle = p.get('handle') or make_slug(p['title'])
        if handle in seen_handles:
            continue
        seen_handles.add(handle)
        picks.append((p['title'], handle))
        if len(picks) >= (3 - existing):
            break

    if not picks:
        return body_html

    items = "".join(
        f'<li><a href="https://retrocameraland.com/products/{handle}">{title}</a></li>'
        for title, handle in picks
    )
    block = (
        '<div style="margin:28px 0;"><p style="font-weight:700;margin:0 0 8px;">'
        f'İlginizi çekebilir:</p><ul>{items}</ul></div>'
    )
    h2s = list(re.finditer(r'<h2[^>]*>', body_html, re.I))
    if h2s:
        insert_at = h2s[-1].start()
        return body_html[:insert_at] + block + "\n" + body_html[insert_at:]
    return body_html + block


# ── JSON-LD Şemaları (SEO/SGE-AEO) ──────────────────────────────────────────────
def build_jsonld_schemas(topic, article_url, img_url, body_html):
    """Article + FAQPage + BreadcrumbList — AI Overview/SGE ve zengin sonuçlar için zorunlu.
    FAQ soruları blogun kendi SSS bölümündeki <h3>soru</h3><p>cevap</p> çiftlerinden çıkarılır."""
    faqs = []
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', body_html, re.S | re.I):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if q and a:
            faqs.append((q, a))

    today = datetime.now().strftime('%Y-%m-%d')
    schemas = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": topic['title'][:110],
        "description": topic.get('meta_desc', ''),
        "image": img_url or "https://retrocameraland.com/logo.png",
        "datePublished": today,
        "dateModified": today,
        "author": {"@type": "Organization", "name": "Retrocameraland"},
        "publisher": {
            "@type": "Organization", "name": "Retrocameraland",
            "logo": {"@type": "ImageObject", "url": "https://retrocameraland.com/logo.png"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": article_url},
    }]

    if faqs:
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs[:8]
            ],
        })

    schemas.append({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Anasayfa", "item": "https://retrocameraland.com"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://retrocameraland.com/blogs/retro-dijital-kamera"},
            {"@type": "ListItem", "position": 3, "name": topic['title'], "item": article_url},
        ],
    })

    # "</script" literal olarak içerikte geçerse (LLM üretimi FAQ metni vb.) script'i
    # erken kapatmasın diye kaçır
    return "\n".join(
        '<script type="application/ld+json">'
        + json.dumps(s, ensure_ascii=False).replace('</', '<\\/')
        + '</script>'
        for s in schemas
    )


def publish_blog(topic, body_html, yt_video):
    handle = make_slug(topic['title'])

    # YouTube embed bloğunu içeriğe ekle (SSS bölümünden önce)
    yt_block = yt_embed_block(yt_video['id'], yt_video['title'])
    if '<h2>' in body_html:
        # 3. H2'den önce ekle
        h2s = list(re.finditer(r'<h2[^>]*>', body_html, re.I))
        if len(h2s) >= 3:
            insert_at = h2s[2].start()
            body_html = body_html[:insert_at] + yt_block + "\n" + body_html[insert_at:]

    # Sosyal medya inline bloğu — kapanıştan önce
    sm_block = social_inline_block()
    body_html += "\n" + sm_block

    # Görsel — çok-panolu Pinterest havuzu (328 pin, TÜM panolar, kalıcı kullanılmamış-
    # görsel takibi) BİRİNCİL kaynak → tek-pano RSS (25-50 pin) yedek → Shopify kataloğu
    # son çare. Tek-panoya bağımlılık az sayıda görselin defalarca tekrarlanmasına
    # yol açıyordu — 328 pinlik paylaşımlı havuz (pinterest_image_fetcher.py, RCL'nin
    # diğer blog script'lerinde de kullanılan kaynak) çok daha geniş çeşitlilik sağlar.
    img_url, img_from_board = None, False
    try:
        from pinterest_image_fetcher import find_unused_pinterest_image
        pin_url, pin_desc, pin_score = find_unused_pinterest_image(topic['keyword'], topic['title'])
        if pin_url:
            img_url = pin_url
            log(f"  ✓ Pinterest görseli (çok-pano havuzu, score={pin_score}): {pin_desc or ''}")
    except Exception as e:
        log(f"  ⚠ Çok-pano Pinterest hatası: {str(e)[:80]}")
    if not img_url:
        img_url = pinterest_board_image(topic['title'])
        img_from_board = bool(img_url)
        if img_url:
            log(f"  ✓ Pinterest panosu görseli (yedek, tek pano): {img_url[:60]}")
    if not img_url:
        log("  → Shopify katalogdan görsel aranıyor (son çare)...")
        img_url = fetch_site_image(topic['keyword'], topic['title'])
        # Katalog görselleri konuyla alakasız olabiliyor (kart okuyucu vb.) — yalnızca
        # kamera/retro görselleri kabul et; değilse görselsiz bırak
        if img_url and any(b in img_url.lower() for b in ("kart_okuyucu", "kart-okuyucu", "hediyekart", "card_reader", "kablo", "adaptor")):
            log(f"  ✗ Alakasız katalog görseli reddedildi: {img_url.split('/')[-1][:40]}")
            img_url = None
        elif img_url:
            log(f"  ✓ Site görseli: {img_url[:70]}...")
        if not img_url:
            log("  ✗ Uygun görsel bulunamadı — görselsiz yayın")

    article_url  = f"https://retrocameraland.com/blogs/retro-dijital-kamera/{handle}"
    schema_block = build_jsonld_schemas(topic, article_url, img_url, body_html)
    full_html = body_html + "\n" + schema_block + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK

    article_data = {
        "title":     topic['title'],
        "body_html": full_html,
        "handle":    handle,
        "tags":      topic.get('tags', 'retrocameraland'),
        "published": True,
        "metafields": [
            {"namespace": "seo", "key": "description", "value": topic.get('meta_desc', ''), "type": "single_line_text_field"},
            {"namespace": "seo", "key": "title",       "value": topic['title'],              "type": "single_line_text_field"},
        ],
    }
    if img_url:
        seo_file = _seo_slug(topic['title']) + ".jpg"
        if img_from_board:
            # Pinterest panosu görselini SEO dosya adıyla yükle
            try:
                article_data["image"] = {"attachment": _img_b64(img_url),
                                         "filename": seo_file, "alt": topic['title']}
            except Exception as e:
                log(f"  ⚠ board görsel indirilemedi, src: {str(e)[:50]}")
                article_data["image"] = {"src": img_url, "alt": topic['title']}
        elif img_url.startswith("http"):
            article_data["image"] = {"src": img_url, "alt": topic['title']}
        else:
            article_data["image"] = {"attachment": img_url, "filename": seo_file, "alt": topic['title']}

    try:
        resp = shopify("POST", f"blogs/{BLOG_ID}/articles.json", {"article": article_data})
        art  = resp["article"]
        if img_url:
            save_image_used(img_url)
        return art["id"], art["handle"]
    except RuntimeError as e:
        if 'has already been taken' in str(e):
            # ESKİDEN: yeni bir "-MMDDHHMM" ekli handle üretip AYNI konuyu tekrar
            # yayınlıyordu — RCL'de tek bir konunun 33 kez tekrar yayınlanmasının doğrudan
            # sebebi buydu. Handle çakışması "bu konu zaten canlıda var" demektir —
            # ikinci bir kopya ASLA oluşturulmasın; DuplicateTopicError fırlat, run()
            # bunu yakalayıp konuyu atlasın (yeniden denemesin — deneme aynı handle'a
            # çarpar, sonuç değişmez).
            raise DuplicateTopicError(
                f"Handle '{handle}' zaten var — bu konu muhtemelen daha önce yayınlandı, ikinci kopya oluşturulmadı."
            ) from e
        raise


# ── Telegram Notification ──────────────────────────────────────────────────────
def send_notification(results, failed, elapsed_s, batch_time, trends):
    now  = datetime.now().strftime('%d.%m.%Y')
    rows = []
    for r in results:
        em = "🟢" if r['seo_score'] >= 90 else "🟡" if r['seo_score'] >= 75 else "🔴"
        rows.append(
            f"{em} <b>{r['title']}</b>\n"
            f"   SEO: {r['seo_score']}/100 | KW: {r['keyword']}\n"
            f"   🔗 {r['url']}"
        )
    tw_part = ""
    if trends['twitter']:
        tw_part = f"\n\n📊 <b>TR Trendleri:</b> {', '.join(trends['twitter'][:6])}"
    msg = (
        f"📝 <b>RCL Blog Ajanı — {now} {batch_time}</b>\n"
        f"✅ {len(results)} yayın | ❌ {failed} hata | ⏱ {elapsed_s}s\n\n"
        + "\n\n".join(rows) + tw_part
    )
    try:
        tg_send(msg)
        log("✓ Telegram bildirimi gönderildi")
    except Exception as e:
        log(f"⚠ Telegram hatası: {e}")


# ── Report ─────────────────────────────────────────────────────────────────────
def save_report(results, failed, elapsed_s, batch_time, errors=None):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    path = f"{LOG_DIR}/{date_str}_seo-blog-{batch_time.replace(':','')}.md"
    lines = [
        f"# RCL SEO Blog — {date_str} {batch_time}",
        f"Yayın: {len(results)} | Hata: {failed} | Süre: {elapsed_s}s", "",
    ]
    for r in results:
        lines += [f"## {r['title']}", f"- SEO: {r['seo_score']}/100",
                  f"- URL: {r['url']}", f"- YT: {r.get('yt_video','—')}", ""]
    if errors:
        lines += ["## ❌ Hatalar"]
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    log(f"✓ Rapor: {path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def run(batch_count=BATCH_COUNT):
    t0 = time.time()
    batch_time = datetime.now().strftime('%H:%M')
    log(f"\n{'═'*56}\nRCL SEO Blog Ajanı v2 ─ {batch_time} ─ {batch_count} blog\n{'═'*56}")

    published_titles, published_keywords, published_entities, results, failed, errors = [], [], [], [], 0, []
    duplicate_skips = 0

    # 1. Trend araştırması
    try:
        trends = research_trends()
    except Exception as e:
        log(f"⚠ Trend hatası: {e}")
        now = datetime.now()
        months = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                  "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        trends = {'web':[], 'twitter':[], 'x':[],
                  'date': f"{now.day} {months[now.month-1]} {now.year}",
                  'month': months[now.month-1], 'year': now.year}

    # 2. Konu seçimi
    existing = load_published()
    try:
        topics = pick_topics(trends, existing, batch_count)
    except Exception as e:
        log(f"⚠ Konu hatası: {e}")
        import random
        topics = random.sample(FALLBACK_POOL, min(batch_count, len(FALLBACK_POOL)))

    # Temalı kampanya (ay sonuna kadar): her 2 blogtan 1'i öğrenci/sevgili temasında
    try:
        topics = inject_themed_topics(topics, existing, batch_count, trends)
    except Exception as e:
        log(f"⚠ Temalı enjeksiyon hatası: {e}")

    # 3. Her blog: üret → puan → yayınla
    for i, topic in enumerate(topics[:batch_count], 1):
        log(f"\n── Blog {i}/{batch_count}: {topic['title'][:55]}")
        yt_video = pick_yt_video(topic['title'], topic['keyword'])
        log(f"  YT Video: {yt_video['title']} ({yt_video['id']})")
        success = False
        was_duplicate = False

        for attempt in range(MAX_RETRIES):
            try:
                log(f"  [{attempt+1}/{MAX_RETRIES}] İçerik üretiliyor (4 bölüm)...")
                body_html = generate_blog_html(topic, trends, attempt)
                body_html = inject_product_deep_links(body_html, topic)

                seo_score, score_details = score_seo(
                    topic['title'], topic.get('meta_desc',''), body_html, topic['keyword']
                )
                log(f"  SEO Skoru: {seo_score}/100")
                for d in score_details:
                    log(f"    {d}")

                if seo_score < MIN_SEO_SCORE and attempt < MAX_RETRIES - 1:
                    log("  ⚠ Skor düşük — tekrar:")
                    time.sleep(2)
                    continue

                log("  Shopify'a yükleniyor...")
                art_id, art_handle = publish_blog(topic, body_html, yt_video)
                url = f"https://retrocameraland.com/blogs/retro-dijital-kamera/{art_handle}"
                log(f"  ✅ ID:{art_id} SEO:{seo_score}/100")

                results.append({
                    'title': topic['title'], 'id': art_id, 'handle': art_handle,
                    'seo_score': seo_score, 'keyword': topic['keyword'],
                    'url': url, 'yt_video': yt_video['id'],
                })
                published_titles.append(topic['title'])
                published_keywords.append(topic['keyword'])
                published_entities.append(extract_entities(topic['title'], topic.get('keyword', '')))
                # Toplu (batch sonu) kayda GÜVENME: süreç bu noktadan sonra çökerse/asılı
                # kalırsa STATE_FILE'lara hiç yazılmaz ve aynı FALLBACK_POOL konusu bir
                # sonraki koşuda "taze" görünüp tekrar yayınlanır — bunun canlıda olduğu
                # doğrulandı (aynı başlık 5 kez). Her başarılı yayından hemen sonra da kaydet.
                save_published([topic['title']])
                save_keyword_history([topic['keyword']])
                save_entity_history([published_entities[-1]])
                success = True
                break

            except DuplicateTopicError as e:
                # Yeniden denemek anlamsız — aynı başlık aynı handle'ı üretir, tekrar çakışır.
                err_msg = str(e)[:200]
                log(f"  ⚠ Atlandı (zaten yayınlanmış): {err_msg}")
                # KENDİNİ ONAR: bu başlık published-topics.json'da kayıtlı DEĞİLDİ (eski
                # non-incremental-save döneminden kalma bir boşluk) — Shopify'ın kendisi
                # "zaten var" dediğine göre artık kayda geç. Yoksa aynı konu (ve varyant
                # ekleri) sonraki koşularda tekrar tekrar denenip her seferinde birkaç
                # dakika boşa gider (2026-07-28/29'da gözlemlendi — aynı 2 konu defalarca
                # "içerik üret → çakışma → atla" döngüsüne girdi).
                try:
                    save_published([topic['title']])
                    save_keyword_history([topic.get('keyword', '')])
                    save_entity_history([extract_entities(topic['title'], topic.get('keyword', ''))])
                except Exception:
                    pass
                was_duplicate = True
                duplicate_skips += 1
                break

            except Exception as e:
                err_msg = str(e)[:200]
                log(f"  ✗ Deneme {attempt+1}: {err_msg}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5)

        if not success and not was_duplicate:
            failed += 1
            errors.append(f"{topic['title'][:40]}: {err_msg if 'err_msg' in dir() else 'bilinmiyor'}")

        if i < batch_count:
            time.sleep(3)

    # 4. Kayıt ve bildirim
    if published_titles:
        save_published(published_titles)
    if published_keywords:
        save_keyword_history(published_keywords)
    if published_entities:
        save_entity_history(published_entities)

    elapsed = int(time.time() - t0)
    send_notification(results, failed, elapsed, batch_time, trends)
    save_report(results, failed, elapsed, batch_time, errors)

    log(f"\n{'═'*56}\n✅ {len(results)} yayın | ⚠ {duplicate_skips} zaten-var atlandı | ❌ {failed} hata | ⏱ {elapsed}s\n{'═'*56}\n")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, default=BATCH_COUNT)
    args = p.parse_args()
    run(args.count)
