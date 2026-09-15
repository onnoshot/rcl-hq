#!/usr/bin/env python3
"""
rcl-higgsfield-blog-images.py
Higgsfield Nano Banana 2 ile blog kapak görselleri üret → Shopify'a yükle.

Öncelik sırası:
  1. GA4 top ürünlerle eşleşen bloglar (sony t9, canon sd400, fujifilm t200...)
  2. Spesifik model adı içeren bloglar
  3. Genel Y2K/retro bloglar

Kullanım:
  python3 rcl-higgsfield-blog-images.py --count 30
  python3 rcl-higgsfield-blog-images.py --count 30 --dry-run
"""

import sys, os, re, json, time, argparse
import urllib.request, urllib.error

sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, BLOG_ID

ENV_FILE = '/Users/onnoshot/Downloads/Agentlar/.env'

def load_env(key):
    try:
        for line in open(ENV_FILE).readlines():
            if line.startswith(f'{key}='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, '')

HIGGSFIELD_TOKEN = load_env('HIGGSFIELD_API_KEY') or load_env('HIGGSFIELD_TOKEN')

# ── Higgsfield API ────────────────────────────────────────────────────────────
HF_BASE = "https://api.higgsfield.ai"

def hf_post(path, body):
    url  = f"{HF_BASE}{path}"
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {HIGGSFIELD_TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def hf_get(path):
    url = f"{HF_BASE}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {HIGGSFIELD_TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def hf_generate(prompt, aspect_ratio="3:2"):
    body = {
        "model":        "nano_banana_2",
        "prompt":       prompt,
        "aspect_ratio": aspect_ratio,
        "resolution":   "1k",
    }
    resp = hf_post("/v1/image/generate", body)
    return resp

def hf_wait(job_id, timeout=120):
    """Tamamlanana kadar polling yap, görsel URL'ini döndür."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = hf_get(f"/v1/jobs/{job_id}")
        status = resp.get("status") or resp.get("generation", {}).get("status", "")
        if status == "completed":
            raw = (resp.get("results") or
                   resp.get("generation", {}).get("results") or {})
            return raw.get("rawUrl") or raw.get("minUrl")
        if status in ("failed", "error"):
            raise RuntimeError(f"Higgsfield job failed: {resp}")
        time.sleep(5)
    raise TimeoutError(f"Job {job_id} timed out")


# ── Prompt üretici ────────────────────────────────────────────────────────────
PROMPT_MAP = [
    # (anahtar kelime listesi, prompt)
    (["dsc-t9", "dsc t9"],
     "Sony Cyber-shot DSC-T9 slim silver digital camera, Y2K aesthetic, warm golden tones, soft bokeh, 2000s nostalgia, retro lifestyle photography"),
    (["dsc-s85"],
     "Sony Cyber-shot DSC-S85 silver digital camera, Y2K retro aesthetic, warm vintage tones, bokeh, 2000s nostalgia"),
    (["dsc-tx9", "dsc tx9"],
     "Sony Cyber-shot DSC-TX9 touchscreen slim camera, Y2K aesthetic, glossy modern retro, warm tones"),
    (["dsc-w", "cybershot"],
     "Sony Cyber-shot compact digital camera, Y2K aesthetic, silver metallic, warm nostalgic tones, retro 2000s"),
    (["finepix t200", "t200"],
     "Fujifilm FinePix T200 blue compact digital camera, Y2K pastel aesthetic, retro 2000s vibe, warm grain, nostalgic lifestyle"),
    (["finepix", "fujifilm"],
     "Fujifilm FinePix retro digital camera, Y2K aesthetic, warm pastel tones, film grain, nostalgic 2000s photography"),
    (["sd400"],
     "Canon PowerShot SD400 silver slim digital camera, Y2K aesthetic, retro 2000s nostalgia, warm tones, minimal background"),
    (["powershot"],
     "Canon PowerShot compact digital camera, Y2K retro aesthetic, silver, warm golden bokeh, 2000s nostalgia"),
    (["ixus"],
     "Canon IXUS ultra slim silver digital camera, Y2K aesthetic, elegant retro, warm tones, 2000s nostalgia"),
    (["optio s7", "optio"],
     "Pentax Optio S7 ultra slim metallic compact camera, Y2K aesthetic, 2000s retro digital, warm lifestyle"),
    (["coolpix"],
     "Nikon Coolpix compact digital camera, Y2K aesthetic, retro 2000s nostalgia, warm vintage tones"),
    (["lumix", "panasonic"],
     "Panasonic Lumix compact digital camera, Y2K aesthetic, silver metallic, retro lifestyle, warm nostalgic tones"),
    (["exilim", "casio"],
     "Casio Exilim ultra slim digital camera, Y2K aesthetic, retro 2000s, warm tones, nostalgic photography"),
    (["samsung", "es65"],
     "Samsung ES65 compact silver digital camera, Y2K aesthetic, retro 2000s nostalgia, warm bokeh, lifestyle"),
    (["sanyo", "xacti"],
     "Sanyo Xacti vertical grip digital camera, Y2K aesthetic, 2000s retro video, warm nostalgic tones"),
    (["olympus"],
     "Olympus compact digital camera, Y2K aesthetic, retro 2000s lifestyle, warm tones, nostalgia"),
    (["ccd kamera", "ccd"],
     "CCD digital camera sensor close-up, Y2K aesthetic, warm nostalgic grain, retro 2000s film look, golden tones"),
    (["y2k"],
     "Y2K aesthetic digital cameras collection, warm grain, nostalgic 2000s photography, pastel tones, retro vibes, lifestyle flat lay"),
    (["instagram", "tiktok", "sosyal medya", "içerik"],
     "Y2K retro digital camera lifestyle content creation, warm aesthetic, Instagram worthy, 2000s nostalgia, soft light"),
    (["vintage", "koleksiyon"],
     "Vintage digital cameras collection flat lay, Y2K aesthetic, warm tones, retro 2000s nostalgia, nostalgic photography"),
    (["3000 tl", "ucuz", "bütçe"],
     "Affordable retro digital camera collection, Y2K aesthetic, warm tones, 2000s nostalgia, compact cameras"),
    (["karşılaştırma", "vs", "hangisi"],
     "Two retro digital cameras comparison, Y2K aesthetic, warm bokeh, nostalgic 2000s lifestyle photography"),
    (["rehber", "nasıl", "ipucu"],
     "Retro Y2K digital camera photography guide, warm aesthetic, 2000s nostalgia, film grain, lifestyle photography tips"),
    (["retro"],
     "Retro digital camera Y2K aesthetic, warm golden tones, soft bokeh, 2000s nostalgia, vintage lifestyle photography"),
]

DEFAULT_PROMPT = "Retro Y2K digital camera aesthetic, warm vintage tones, soft bokeh, nostalgic 2000s photography, film grain, lifestyle"

def make_prompt(title):
    title_low = title.lower()
    for keywords, prompt in PROMPT_MAP:
        if any(kw in title_low for kw in keywords):
            return prompt
    return DEFAULT_PROMPT


# ── Shopify ───────────────────────────────────────────────────────────────────
def shopify_put(path, body):
    url  = f"https://retrocameraland.myshopify.com/admin/api/2024-01/{path}"
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("X-Shopify-Access-Token", "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")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code}: {e.read().decode()[:200]}")


def fetch_all_articles():
    import re as _re
    articles = []
    path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,handle,published_at"
    while path:
        url = f"https://retrocameraland.myshopify.com/admin/api/2024-01/{path}"
        req = urllib.request.Request(url)
        req.add_header("X-Shopify-Access-Token", "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")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as r:
            link = r.headers.get("Link", "")
            data = json.loads(r.read())
        articles.extend(data.get("articles", []))
        path = None
        if 'rel="next"' in link:
            m = _re.search(r'<([^>]+)>; rel="next"', link)
            if m:
                path = m.group(1).split("/admin/api/2024-01/")[-1]
    return articles


# ── Öncelik puanlama ──────────────────────────────────────────────────────────
# GA4 top ürünlere göre öncelik (daha yüksek = daha önemli)
PRIORITY_KEYWORDS = {
    "dsc-t9": 10, "dsc t9": 10, "t9": 8,
    "sd400": 9,
    "dsc-s85": 8,
    "dsc-tx9": 7,
    "t200": 9, "finepix t200": 10,
    "ixus": 7,
    "optio s7": 8, "s7": 6,
    "coolpix": 6,
    "y2k kamera": 5, "y2k": 4,
    "retro kamera": 3,
    "3000 tl": 5,
    "ccd": 4,
}

def priority_score(title):
    title_low = title.lower()
    score = 0
    for kw, pts in PRIORITY_KEYWORDS.items():
        if kw in title_low:
            score = max(score, pts)
    return score


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ── Ana akış ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count",   type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("Makaleler yükleniyor...")
    articles = fetch_all_articles()
    log(f"  {len(articles)} makale bulundu")

    # Öncelik sırala — en önemli önce, aynı öncelikliler en yeni önce
    articles.sort(key=lambda a: (
        -priority_score(a["title"]),
        -(int(a.get("published_at","").replace("-","").replace("T","").replace(":","").replace("Z","")[:14] or 0))
    ))

    top = articles[:args.count]

    log(f"\nİlk {args.count} makale (öncelik sırası):")
    for i, a in enumerate(top, 1):
        p     = priority_score(a["title"])
        prompt = make_prompt(a["title"])
        log(f"  {i:2}. [puan:{p}] {a['title'][:55]}")
        log(f"       prompt: {prompt[:70]}...")

    if args.dry_run:
        log("\nDRY-RUN — gerçek işlem yapılmadı.")
        return

    log(f"\n{'═'*60}")
    log(f"Başlıyor: {args.count} görsel × 1.5 kredi = ~{args.count*1.5} kredi")
    log(f"{'═'*60}\n")

    ok = fail = 0
    t0 = time.time()

    for i, article in enumerate(top, 1):
        aid    = article["id"]
        title  = article["title"]
        prompt = make_prompt(title)

        log(f"[{i:2}/{args.count}] {title[:52]}")
        log(f"  prompt: {prompt[:72]}...")

        try:
            # Görsel üret
            resp   = hf_generate(prompt)
            # job id farklı yerlerde olabilir
            job_id = (resp.get("id") or
                      (resp.get("results") or [{}])[0].get("id") or
                      resp.get("generation", {}).get("id"))
            if not job_id:
                raise RuntimeError(f"Job ID alınamadı: {resp}")

            log(f"  ⏳ Job: {job_id} — bekleniyor...")
            img_url = hf_wait(job_id, timeout=120)
            if not img_url:
                raise RuntimeError("Görsel URL alınamadı")

            log(f"  ✓ Görsel: {img_url[-60:]}")

            # Shopify'a yükle
            shopify_put(
                f"blogs/{BLOG_ID}/articles/{aid}.json",
                {"article": {"id": aid, "image": {"src": img_url, "alt": title[:200]}}}
            )
            log(f"  ✅ Shopify güncellendi")
            ok += 1

        except Exception as e:
            log(f"  ✗ HATA: {str(e)[:120]}")
            fail += 1

        # Higgsfield rate limit için kısa bekleme
        if i < args.count:
            time.sleep(2)

        # Her 10'da ilerleme raporu
        if i % 10 == 0:
            elapsed = int(time.time() - t0)
            log(f"\n── İlerleme: {i}/{args.count} | ✓{ok} ✗{fail} | {elapsed}s geçti ──\n")

    elapsed = int(time.time() - t0)
    log(f"\n{'═'*60}")
    log(f"TAMAMLANDI | ✓{ok} görsel | ✗{fail} hata | {elapsed}s | ~{ok*1.5:.0f} kredi")
    log(f"{'═'*60}")


if __name__ == "__main__":
    main()
