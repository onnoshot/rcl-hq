#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RetroCameraLand — Instagram -> Pinterest aktarici
=================================================
Instagram'da paylasilan TUM gonderileri (en eskiden baslayarak) Pinterest'e pin yapar.

Her pin:
  - INGILIZCE, SEO uyumlu baslik (<=100 karakter)
  - Gorsel/video ile ilgili SEO aciklama + konu etiketleri (hashtag)
  - retrocameraland.com hem LINK olarak hem aciklama icinde
  - Icerik temasina gore otomatik board secimi
  - Video gonderiler de pinlenir (Pinterest video upload akisi)
  - Idempotent: .ig_pinned.json ile daha once pinlenen gonderi tekrar pinlenmez

GEREKSINIM: Pinterest uygulamasi STANDARD access olmali. Trial access production'da
pin olusturamaz (403 code 29). Onay sonrasi calistir.

Kullanim:
  python3 rcl-ig-to-pinterest.py --dry            # ag yok: sadece uretilen metadata onizleme
  python3 rcl-ig-to-pinterest.py --limit 1        # CANLI: en eski 1 gonderiyi pinle (test)
  python3 rcl-ig-to-pinterest.py                  # CANLI: kalan tum gonderileri pinle
  python3 rcl-ig-to-pinterest.py --sandbox --limit 1   # sandbox'a karsi test
"""
import os, sys, json, time, argparse, re, io
import urllib.request
try:
    import requests
except Exception:
    requests = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pinterest_auth import get_env

HERE       = os.path.dirname(os.path.abspath(__file__))
POSTS_FILE = os.path.join(HERE, ".ig_all_posts.json")
PINNED_FILE= os.path.join(HERE, ".ig_pinned.json")
IG_TOKEN   = os.path.join(HERE, "ig_token.json")
SITE       = "https://retrocameraland.com"
LINK       = SITE + "/?utm_source=pinterest&utm_medium=social&utm_campaign=ig_repost"
PROD_BASE  = "https://api.pinterest.com/v5"
SBX_BASE   = "https://api-sandbox.pinterest.com/v5"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

# ── IG gonderilerini (gerekirse) yeniden cek ──────────────────────────────────
def fetch_all_ig():
    cfg = json.load(open(IG_TOKEN)); tok = cfg["page_access_token"]; ig = cfg["ig_business_id"]
    def get(url):
        if "access_token" not in url:
            url += ("&" if "?" in url else "?") + "access_token=" + tok
        req = urllib.request.Request(url); req.add_header("Accept", "application/json")
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    url = (f"https://graph.facebook.com/v25.0/{ig}/media?fields=id,timestamp,media_type,"
           "media_product_type,permalink,media_url,thumbnail_url,caption,"
           "children{media_type,media_url,thumbnail_url}&limit=100")
    allp = []
    while url:
        d = get(url); allp += d.get("data", [])
        url = d.get("paging", {}).get("next")
    json.dump(allp, open(POSTS_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    return allp

def load_posts():
    if not os.path.exists(POSTS_FILE):
        return fetch_all_ig()
    return json.load(open(POSTS_FILE, encoding="utf-8"))

def load_pinned():
    if os.path.exists(PINNED_FILE):
        try: return json.load(open(PINNED_FILE, encoding="utf-8"))
        except Exception: pass
    return {"pinned": {}}

def save_pinned(d):
    json.dump(d, open(PINNED_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ── INGILIZCE SEO metadata uretimi ────────────────────────────────────────────
# Bilinen marka + model tespiti (caption TR/EN karisik olabilir)
BRANDS = ["sony","canon","fujifilm","fuji","nikon","panasonic","lumix","olympus",
          "casio","kodak","samsung","pentax","minolta","konica","sanyo","ricoh",
          "leica","polaroid","agfa","hp","rollei","jvc","traveler","premier","minton"]
MODEL_RE = re.compile(r"\b([a-z]{1,4}[- ]?\d{2,4}[a-z]{0,3})\b", re.I)

# Tema -> (board adi, baslik kaliplari, hashtag seti)
THEMES = {
  "night":   {"kw":["gece","night","parti","party","flash","flaş","neon","club","konser"],
              "board":"Y2K Diaries",
              "titles":["Y2K Flash Night Aesthetic with a Retro Digicam",
                        "Night Out Photos That Hit Different — CCD Flash Look",
                        "Capture the Party in True Y2K Flash Style"],
              "tags":"#y2k #flashphotography #nightout #digicam #retrocamera #ccdcamera #partyaesthetic"},
  "travel":  {"kw":["seyahat","travel","gezi","tatil","trip","yol","deniz","beach"],
              "board":"Everyday Aesthetic",
              "titles":["The Perfect Travel Companion: A Pocket Retro Digicam",
                        "Travel Memories in Warm Retro Film Tones",
                        "Pack Light, Shoot Retro — Travel Digicam Vibes"],
              "tags":"#travelcamera #digicam #retrocamera #travelaesthetic #y2k #filmlook #wanderlust"},
  "portrait":{"kw":["portre","portrait","yüz","selfie","ten","skin","sevgili","couple","insan"],
              "board":"Everyday Aesthetic",
              "titles":["Warm, Soft Portraits in True CCD Color",
                        "Portrait Magic with a Retro Digital Camera",
                        "Skin Tones That Feel Like Film — Retro Digicam"],
              "tags":"#portrait #digicam #retrocamera #ccdcamera #filmlook #aesthetic #photography"},
  "vlog":    {"kw":["vlog","içerik","content","tiktok","reels","video","blog"],
              "board":"Fashion in Motion",
              "titles":["Make Content That Stops the Scroll — Retro Digicam",
                        "The Digicam Look Every Creator Wants",
                        "Y2K Content Vibes with a Real CCD Camera"],
              "tags":"#contentcreator #digicam #y2k #retrocamera #tiktokaesthetic #reels #aesthetic"},
  "gift":    {"kw":["hediye","gift","doğum","birthday","yılbaşı","sürpriz","surprise"],
              "board":"Everyday Aesthetic",
              "titles":["The Retro Camera Gift Everyone Secretly Wants",
                        "A Y2K Digicam — The Most Memorable Gift Idea",
                        "Gift a Real Retro Digital Camera"],
              "tags":"#giftidea #digicam #retrocamera #y2k #aesthetic #photographygift #ccdcamera"},
  "tips":    {"kw":["ipucu","tip","nasıl","how","ayar","setting","rehber","guide","öğren"],
              "board":"Digicam Tips",
              "titles":["Retro Digicam Tips for the Perfect Y2K Shot",
                        "Get the Most Out of Your CCD Camera",
                        "How to Nail the Retro Digital Camera Look"],
              "tags":"#digicamtips #retrocamera #y2k #ccdcamera #photographytips #digicam #aesthetic"},
  "default": {"kw":[],
              "board":"Retro Digicam Club",
              "titles":["Real CCD Magic — Retro Digital Camera Aesthetic",
                        "The Y2K Digicam Look You Have Been Missing",
                        "Nostalgic Retro Digital Camera Vibes"],
              "tags":"#retrocamera #digicam #y2k #ccdcamera #aesthetic #vintagecamera #filmlook"},
}
VIDEO_BOARD = "Raw Video Moments"

def detect_model(cap):
    low = cap.lower()
    brand = next((b for b in BRANDS if b in low), "")
    if not brand:
        return ""
    # markadan sonraki model tokenini yakalamaya calis
    m = re.search(re.escape(brand) + r"[^\n]{0,18}?([a-z]{0,3}[- ]?\d{2,4}[a-z]{0,3})", low)
    model = (m.group(1).strip() if m else "").upper()
    name = brand.capitalize()
    if brand == "fuji": name = "Fujifilm"
    if brand == "lumix": name = "Panasonic Lumix"
    return (name + " " + model).strip()

def detect_theme(cap):
    low = cap.lower()
    best = "default"
    for key, t in THEMES.items():
        if key == "default": continue
        if any(k in low for k in t["kw"]):
            best = key; break
    return best

def make_meta(post, idx):
    cap = (post.get("caption") or "").strip()
    is_video = post.get("media_type") == "VIDEO" or post.get("media_product_type") == "REELS"
    theme = detect_theme(cap)
    T = THEMES[theme]
    model = detect_model(cap)
    # ── baslik (<=100) ──
    if model and len(model) > 3:
        title = f"{model} — {T['titles'][idx % len(T['titles'])]}"
    else:
        title = T["titles"][idx % len(T["titles"])]
    title = title[:97].rstrip() + "" if len(title) <= 100 else title[:97].rstrip() + "..."
    # ── aciklama (SEO + site + hashtag) ──
    lead_pool = [
      "Discover the nostalgic charm of 2000s CCD digital cameras.",
      "Bring back that authentic Y2K digital camera look.",
      "Real retro digicams, tested and ready to shoot.",
      "Trade phone perfection for true retro character.",
    ]
    lead = lead_pool[idx % len(lead_pool)]
    subject = (model + " " if model else "") + ("retro digital camera video" if is_video else "retro digital camera")
    desc = (f"{lead} This {subject} captures warm film-like tones, flash-lit Y2K energy and "
            f"that unmistakable nostalgic mood you cannot fake. Explore tested, ready-to-ship "
            f"retro digicams at retrocameraland.com. {T['tags']}")
    desc = desc[:495]
    return {
        "title": title,
        "description": desc,
        "link": LINK,
        "board": VIDEO_BOARD if is_video else T["board"],
        "theme": theme,
        "model": model,
        "is_video": is_video,
    }

# ── Pinterest API ─────────────────────────────────────────────────────────────
class Pin:
    def __init__(self, base):
        self.base = base
        self.tok = get_env("PINTEREST_ACCESS_TOKEN")
        self.H = {"Authorization": "Bearer " + self.tok}
        self.boards = {}

    def load_boards(self):
        r = requests.get(self.base + "/boards?page_size=100", headers=self.H, timeout=30)
        r.raise_for_status()
        self.boards = {b["name"]: b["id"] for b in r.json().get("items", [])}
        return self.boards

    def board_id(self, name):
        return self.boards.get(name) or next(iter(self.boards.values()))

    def image_pin(self, board_id, title, desc, link, image_url):
        payload = {"board_id": board_id, "title": title, "description": desc, "link": link,
                   "media_source": {"source_type": "image_url", "url": image_url}}
        r = requests.post(self.base + "/pins", headers=self.H, json=payload, timeout=60)
        return r

    def video_pin(self, board_id, title, desc, link, video_url, cover_url):
        # 1) medya kaydi
        reg = requests.post(self.base + "/media", headers=self.H,
                            json={"media_type": "video"}, timeout=30)
        reg.raise_for_status()
        rj = reg.json()
        media_id = rj["media_id"]; up_url = rj["upload_url"]; up_par = rj["upload_parameters"]
        # 2) videoyu indir + S3'e multipart yukle
        vid = requests.get(video_url, timeout=120).content
        files = {"file": ("video.mp4", io.BytesIO(vid), "video/mp4")}
        up = requests.post(up_url, data=up_par, files=files, timeout=300)
        if up.status_code not in (200, 201, 204):
            raise RuntimeError(f"S3 upload {up.status_code}: {up.text[:160]}")
        # 3) islem bitene kadar bekle
        for _ in range(40):
            st = requests.get(self.base + f"/media/{media_id}", headers=self.H, timeout=30).json()
            s = st.get("status")
            if s == "succeeded": break
            if s == "failed": raise RuntimeError("media islemesi failed")
            time.sleep(3)
        # 4) pin olustur
        payload = {"board_id": board_id, "title": title, "description": desc, "link": link,
                   "media_source": {"source_type": "video_id", "cover_image_url": cover_url,
                                    "media_id": media_id}}
        r = requests.post(self.base + "/pins", headers=self.H, json=payload, timeout=60)
        return r

# ── ana akis ──────────────────────────────────────────────────────────────────
def representative_image(post):
    if post.get("media_type") == "CAROUSEL_ALBUM":
        for c in (post.get("children", {}) or {}).get("data", []):
            u = c.get("media_url") if c.get("media_type") == "IMAGE" else c.get("thumbnail_url")
            if u: return u
    return post.get("media_url") or post.get("thumbnail_url") or ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true", help="IG gonderilerini yeniden cek")
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()

    posts = fetch_all_ig() if args.refresh else load_posts()
    posts.sort(key=lambda p: p["timestamp"])     # EN ESKIDEN basla
    pinned = load_pinned()
    todo = [p for p in posts if p["id"] not in pinned["pinned"]]
    if args.limit: todo = todo[:args.limit]
    log(f"{'DRY' if args.dry else ('SANDBOX' if args.sandbox else 'CANLI')} | toplam {len(posts)} gonderi, "
        f"{len(posts)-len(todo) if not args.limit else len(pinned['pinned'])} pinlenmis, {len(todo)} islenecek")

    api = None
    if not args.dry:
        if requests is None: log("requests yok!"); sys.exit(1)
        api = Pin(SBX_BASE if args.sandbox else PROD_BASE)
        api.load_boards()
        log(f"  board sayisi: {len(api.boards)}")

    ok = fail = 0
    for i, p in enumerate(todo):
        meta = make_meta(p, i)
        img  = representative_image(p)
        tag = "VIDEO" if meta["is_video"] else "IMG  "
        if args.dry:
            log(f"[{i+1}/{len(todo)}] {tag} board={meta['board']!r}")
            print(f"    TITLE: {meta['title']}")
            print(f"    DESC : {meta['description'][:120]}...")
            print(f"    LINK : {meta['link']}")
            continue
        try:
            bid = api.board_id(meta["board"])
            if meta["is_video"] and p.get("media_url"):
                r = api.video_pin(bid, meta["title"], meta["description"], meta["link"],
                                  p["media_url"], p.get("thumbnail_url") or img)
            else:
                r = api.image_pin(bid, meta["title"], meta["description"], meta["link"], img)
            if r.status_code in (200, 201):
                pid = r.json().get("id")
                pinned["pinned"][p["id"]] = {"pin_id": pid, "board": meta["board"],
                                             "ts": p["timestamp"][:10], "type": tag.strip()}
                save_pinned(pinned)
                ok += 1
                log(f"[{i+1}/{len(todo)}] OK {tag} pin:{pid} | {meta['title'][:48]}")
            else:
                fail += 1
                log(f"[{i+1}/{len(todo)}] FAIL {r.status_code}: {r.text[:160]}")
                if r.status_code == 403 and "Trial access" in r.text:
                    log("  !! Uygulama hala TRIAL access — STANDARD onayi gerekiyor. Duruluyor.")
                    break
        except Exception as e:
            fail += 1
            log(f"[{i+1}/{len(todo)}] HATA: {str(e)[:160]}")
        time.sleep(args.sleep)

    log(f"\nBitti — OK:{ok} FAIL:{fail} | toplam pinlenmis: {len(pinned['pinned'])}/{len(posts)}")

if __name__ == "__main__":
    main()
