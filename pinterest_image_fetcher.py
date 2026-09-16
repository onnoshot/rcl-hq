#!/usr/bin/env python3
"""
pinterest_image_fetcher.py — Pinterest'ten tüm pin görsellerini çek ve cache'le.

Kullanım (modül olarak):
  from pinterest_image_fetcher import find_pinterest_image
  img_url = find_pinterest_image("sony dsc-t9 retro kamera")

Bağımsız çalıştırma (cache yenile):
  python3 pinterest_image_fetcher.py
"""

import os, sys, json, re, time, random
import urllib.request, urllib.error

ENV_FILE   = os.path.join(os.path.dirname(__file__), '.env')
CACHE_FILE = os.path.join(os.path.dirname(__file__), '.pinterest_cache.json')
USED_FILE  = os.path.join(os.path.dirname(__file__), '.pinterest_used.json')
CACHE_TTL  = 24 * 3600  # 24 saat

_MEMORY_CACHE = None  # process içi cache
_USED_CACHE   = None  # process içi kullanilmis URL seti


# ── Kullanilan gorsel takibi (her blogda FARKLI gorsel garantisi) ─────────────
def _load_used():
    """Daha once bloglarda kullanilmis Pinterest URL'lerini yukle."""
    global _USED_CACHE
    if _USED_CACHE is not None:
        return _USED_CACHE
    used = set()
    try:
        if os.path.exists(USED_FILE):
            data = json.load(open(USED_FILE, encoding='utf-8'))
            used = set(data.get("used", []))
    except Exception:
        pass
    _USED_CACHE = used
    return used


def mark_used(url):
    """Bir gorseli 'kullanildi' olarak isaretle — bir daha secilmez."""
    if not url:
        return
    used = _load_used()
    if url in used:
        return
    used.add(url)
    try:
        json.dump({"used": sorted(used)}, open(USED_FILE, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=0)
    except Exception as e:
        log(f"  ⚠ Kullanilan gorsel kaydedilemedi: {e}")

def _load_env(key):
    try:
        for line in open(ENV_FILE).readlines():
            if line.startswith(f'{key}='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, '')


def log(msg):
    print(f"[Pinterest] {msg}", flush=True)


# ── API yardımcıları ──────────────────────────────────────────────────────────
def _api(path, token):
    url = f"https://api.pinterest.com/v5/{path.lstrip('/')}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Pinterest API {path} → {e.code}: {e.read().decode()[:200]}")


def _get_all_boards(token):
    data = _api("boards?page_size=100", token)
    return data.get("items", [])


def _get_board_pins(board_id, token, max_pins=200):
    """Bir board'un tüm pinlerini sayfalı çek, sadece resim olan pinleri döndür."""
    pins = []
    cursor = None
    while len(pins) < max_pins:
        path = f"boards/{board_id}/pins?page_size=100&pin_type=PUBLIC"
        if cursor:
            path += f"&bookmark={cursor}"
        try:
            data = _api(path, token)
        except Exception as e:
            log(f"  Board {board_id} hata: {e}")
            break
        batch = data.get("items", [])
        for pin in batch:
            # Sadece resim pini — video ve carousel hariç
            media_type = pin.get("media", {}).get("media_type", "")
            if media_type not in ("", "image"):
                continue
            # Görsel URL — en büyük boyutu al
            images = pin.get("media", {}).get("images") or {}
            url = None
            for size in ("originals", "1200x", "736x", "600x", "400x300"):
                if size in images:
                    url = images[size].get("url")
                    break
            if not url:
                continue
            pins.append({
                "id":          pin.get("id"),
                "title":       (pin.get("title") or "").lower(),
                "description": (pin.get("description") or "").lower(),
                "alt_text":    (pin.get("alt_text") or "").lower(),
                "url":         url,
                "board_id":    board_id,
            })
        cursor = data.get("bookmark")
        if not cursor or len(batch) < 100:
            break
        time.sleep(0.3)
    return pins


# ── Cache ─────────────────────────────────────────────────────────────────────
def _load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            data = json.load(open(CACHE_FILE, encoding='utf-8'))
            age  = time.time() - data.get("timestamp", 0)
            if age < CACHE_TTL:
                return data.get("pins", [])
    except Exception:
        pass
    return None


def _save_cache(pins):
    data = {"timestamp": time.time(), "pins": pins}
    json.dump(data, open(CACHE_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    log(f"Cache kaydedildi: {len(pins)} pin → {CACHE_FILE}")


def _build_cache(token):
    log("Tüm boardlar taranıyor...")
    boards = _get_all_boards(token)
    log(f"  {len(boards)} board bulundu: {[b['name'] for b in boards]}")

    all_pins = []
    for b in boards:
        bid   = b["id"]
        bname = b["name"]
        pins  = _get_board_pins(bid, token)
        log(f"  [{bname}] → {len(pins)} resim pini")
        all_pins.extend(pins)
        time.sleep(0.5)

    log(f"Toplam: {len(all_pins)} pin")
    _save_cache(all_pins)
    return all_pins


def get_all_pins(force_refresh=False):
    global _MEMORY_CACHE
    if _MEMORY_CACHE and not force_refresh:
        return _MEMORY_CACHE
    cached = None if force_refresh else _load_cache()
    if cached is not None:
        _MEMORY_CACHE = cached
        return cached
    token = _load_env("PINTEREST_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("PINTEREST_ACCESS_TOKEN bulunamadı. Önce: python3 pinterest_auth.py")
    pins = _build_cache(token)
    _MEMORY_CACHE = pins
    return pins


# ── Arama & eşleştirme ────────────────────────────────────────────────────────
BRANDS = {"sony","canon","fujifilm","nikon","panasonic","olympus","casio",
          "kodak","samsung","pentax","minolta","sanyo","ricoh","leica",
          "polaroid","agfa","konica"}

STOP_WORDS = {"kamera","dijital","retro","fiyat","nedir","rehber","satın","al",
              "ile","için","inceleme","türkiye","nasıl","hangi","ve","bir",
              "bu","da","de","mi","mı","ya","yı","yi","yu","yü","en","iyi",
              "ile","the","and","for","with","how","best","review","vs","top"}

def _score_pin(pin, search_terms):
    """Pin ile search_terms arasındaki uyum skorunu hesapla."""
    haystack = f"{pin['title']} {pin['description']} {pin['alt_text']}"
    score = 0
    for term in search_terms:
        if term in haystack:
            # Model numarası eşleşmesi daha değerli
            is_model = bool(re.match(r'[a-z]{1,5}[-]?[0-9]{1,4}', term))
            score += 3 if is_model else 1
    return score


def find_pinterest_image(keyword, topic_title="", fallback_random=True):
    """Blog konusuyla en alakalı Pinterest görsel URL'ini döndür.

    Returns: (url, matched_pin_description, score) or (None, None, 0)
    """
    try:
        pins = get_all_pins()
    except RuntimeError as e:
        log(f"Cache yüklenemedi: {e}")
        return None, None, 0

    if not pins:
        return None, None, 0

    combined = (topic_title + " " + keyword).lower()

    # Arama terimlerini çıkar
    model_terms = re.findall(r'[a-z]{1,5}-?[0-9]{1,4}[a-z]?', keyword.lower())
    brand_terms = [w for w in combined.split() if w in BRANDS]
    other_terms = [w for w in re.findall(r'[a-z]{4,}', combined)
                   if w not in BRANDS and w not in STOP_WORDS]

    search_terms = list(dict.fromkeys(model_terms + brand_terms + other_terms[:4]))

    # Tüm pinleri skorla
    scored = [(p, _score_pin(p, search_terms)) for p in pins]
    scored = [(p, s) for p, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    if scored:
        best_pin, best_score = scored[0]
        desc = (best_pin['title'] or best_pin['description'])[:60]
        return best_pin['url'], desc, best_score

    if fallback_random:
        pin = random.choice(pins)
        desc = (pin['title'] or pin['description'])[:60]
        return pin['url'], desc, 0

    return None, None, 0


def find_unused_pinterest_image(keyword, topic_title="", mark=True):
    """Blog konusuyla en alakali, DAHA ONCE KULLANILMAMIS Pinterest gorselini dondur.

    Bir kez secilen URL .pinterest_used.json'a yazilir; sonraki cagrilar onu atlar —
    boylece her blogda farkli bir gorsel kullanilir.

    Returns: (url, matched_pin_description, score) or (None, None, 0)
    """
    try:
        pins = get_all_pins()
    except RuntimeError as e:
        log(f"Cache yüklenemedi: {e}")
        return None, None, 0

    if not pins:
        return None, None, 0

    used = _load_used()
    fresh = [p for p in pins if p['url'] not in used]
    if not fresh:
        log("  ⚠ Tum pinler kullanilmis — havuz sifirlanmadan tekrar kullanilacak.")
        fresh = pins

    combined = (topic_title + " " + keyword).lower()
    model_terms = re.findall(r'[a-z]{1,5}-?[0-9]{1,4}[a-z]?', keyword.lower())
    brand_terms = [w for w in combined.split() if w in BRANDS]
    other_terms = [w for w in re.findall(r'[a-z]{4,}', combined)
                   if w not in BRANDS and w not in STOP_WORDS]
    search_terms = list(dict.fromkeys(model_terms + brand_terms + other_terms[:4]))

    scored = [(p, _score_pin(p, search_terms)) for p in fresh]
    scored = [(p, s) for p, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    if scored:
        best_pin, best_score = scored[0]
    else:
        # alakali pin yok → kullanilmamis havuzdan rastgele (deterministik degil)
        best_pin, best_score = random.choice(fresh), 0

    if mark:
        mark_used(best_pin['url'])
    desc = (best_pin['title'] or best_pin['description'])[:60]
    return best_pin['url'], desc, best_score


# ── Bağımsız çalıştırma ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", action="store_true", help="Cache'i zorla yenile")
    p.add_argument("--test",    type=str, default="", help="Test keyword")
    args = p.parse_args()

    pins = get_all_pins(force_refresh=args.refresh)
    print(f"\nToplam pin: {len(pins)}")

    if args.test:
        url, desc, score = find_pinterest_image(args.test)
        print(f"Test '{args.test}': score={score} | {desc}")
        print(f"URL: {url}")
    else:
        # Örnek aramalar
        samples = [
            ("sony cyber-shot dsc-t9", "Sony DSC-T9 İnceleme"),
            ("fujifilm finepix t200", "Fujifilm FinePix T200"),
            ("y2k kamera estetik", "Y2K Kamera Trendi"),
            ("retro kamera seçimi", "Retro Kamera Rehberi"),
            ("canon ixus", "Canon IXUS İnceleme"),
        ]
        print("\nÖrnek eşleşmeler:")
        for kw, title in samples:
            url, desc, score = find_pinterest_image(kw, title)
            ok = "✓" if score > 0 else "→"
            print(f"  {ok} [{kw}] score={score} | {desc or 'fallback'}")
