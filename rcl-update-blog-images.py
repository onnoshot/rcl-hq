#!/usr/bin/env python3
"""
rcl-update-blog-images.py — Retrocameraland blog görsellerini Pinterest
görselleriyle toplu güncelle. Fallback: Shopify ürün görselleri.

Çalışma mantığı:
  1. Shopify'dan tüm blog makalelerini çek (başlık)
  2. Pinterest cache'inden tüm pinleri yükle (pinterest_image_fetcher.py)
  3. Her makale için başlığa göre en uygun Pinterest görselini bul
  4. Shopify PUT ile makalenin image alanını güncelle
  5. Sonuçları ekrana yaz

Kullanım:
  python3 rcl-update-blog-images.py
  python3 rcl-update-blog-images.py --dry-run    # güncelleme yapmadan eşleşmeleri göster
  python3 rcl-update-blog-images.py --limit 10   # sadece ilk 10 makaleyi güncelle (test)
  python3 rcl-update-blog-images.py --refresh    # Pinterest cache'ini yenile

Ön koşul:
  python3 pinterest_auth.py   # ilk kez Pinterest bağlantısı kur
"""

import sys, os, json, re, time, random, argparse
import urllib.request, urllib.error

sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import BLOG_ID

SHOPIFY_TOKEN = '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'
SHOPIFY_STORE = 'retrocameraland.myshopify.com'

BRANDS = {"sony","canon","fujifilm","nikon","panasonic","olympus","casio",
          "kodak","samsung","pentax","minolta","sanyo","ricoh","leica",
          "polaroid","agfa","konica","vivitar","benq","hp"}
STOP_WORDS = {"kamera","dijital","retro","fiyat","nedir","rehber","satın","al",
              "ile","için","inceleme","türkiye","nasıl","hangi","karşılaştırma",
              "seçimi","önerisi","hakkında","2026","2025","en","iyi","ve","bir",
              "bu","da","de","mi","mı","ya","yı","yi","yu","yü"}
ACCESSORY_KW = {"çanta","bag","pil","batarya","şarj","aksesuar","kılıf",
                "kayış","strap","aktarıcı","adaptör","filtre","tripod","kapak",
                "okuyucu","reader","xd","sd kart","bez","hafıza"}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shopify_get(path):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        link = r.headers.get("Link", "")
        return json.loads(r.read()), link


def shopify_put(path, body):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code}: {e.read().decode()[:300]}")


# ── Tüm makaleleri çek ────────────────────────────────────────────────────────
def fetch_all_articles():
    log("Blog makaleleri çekiliyor...")
    articles = []
    path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,image,handle"
    while path:
        data, link = shopify_get(path)
        batch = data.get("articles", [])
        articles.extend(batch)
        # cursor-based next page
        path = None
        if 'rel="next"' in link:
            m = re.search(r'<([^>]+)>; rel="next"', link)
            if m:
                path = m.group(1).split("/admin/api/2024-01/")[-1]
    log(f"  {len(articles)} makale yüklendi")
    return articles


# ── Tüm ürünleri çek ──────────────────────────────────────────────────────────
def fetch_all_products():
    log("Ürün kataloğu yükleniyor...")
    data, _ = shopify_get("products.json?limit=250&fields=title,images,vendor")
    products = [p for p in data.get("products", []) if p.get("images")]
    camera_products = [p for p in products
                       if not any(kw in p["title"].lower() for kw in ACCESSORY_KW)]
    log(f"  {len(products)} ürün ({len(camera_products)} kamera)")
    return products, camera_products


# ── Makale başlığından arama terimleri üret ───────────────────────────────────
def extract_search_terms(title):
    title_low = title.lower()
    # Model numaraları: sd400, t9, dsc-t9, t200, es65, a480 vb.
    model_terms = re.findall(r'[a-z]{1,5}-?[0-9]{1,4}[a-z]?|[0-9]{1,4}[a-z]{1,3}', title_low)
    # Marka adları
    brand_terms = [w for w in title_low.split() if w in BRANDS]
    # Diğer anlamlı kelimeler
    other_terms = [w for w in re.findall(r'[a-z]{4,}', title_low)
                   if w not in BRANDS and w not in STOP_WORDS]
    # Öncelik: model > marka > diğer
    seen, ordered = set(), []
    for term in model_terms + brand_terms + other_terms:
        if term not in seen:
            seen.add(term)
            ordered.append(term)
    return ordered


# ── En uygun ürün görselini bul ───────────────────────────────────────────────
def find_best_image(title, products, camera_products):
    terms = extract_search_terms(title)
    for term in terms:
        # Sadece kamera ürünlerinde ara — aksesuar ürünlerine düşme
        matches = [p for p in camera_products if term in p["title"].lower()]
        if matches:
            # Birden fazla eşleşmede en çok terimi barındıranı seç
            best = max(matches, key=lambda p: sum(
                1 for t in terms if t in p["title"].lower()
            ))
            return best["images"][0]["src"], best["title"], term

    # Fallback: rastgele kamera ürünü (her seferinde farklı bir kamera görünsün)
    pool = camera_products if camera_products else products
    pick = random.choice(pool)
    return pick["images"][0]["src"], pick["title"], "fallback"


# ── Ana akış ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Güncelleme yapma, sadece eşleşmeleri göster")
    parser.add_argument("--limit",   type=int, default=0, help="Kaç makale güncellenecek (0=hepsi)")
    parser.add_argument("--refresh", action="store_true", help="Pinterest cache'ini zorla yenile")
    args = parser.parse_args()

    articles = fetch_all_articles()
    products, camera_products = fetch_all_products()

    # Pinterest cache yükle
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from pinterest_image_fetcher import find_pinterest_image, get_all_pins
        pins = get_all_pins(force_refresh=args.refresh)
        use_pinterest = len(pins) > 0
        log(f"Pinterest: {len(pins)} pin yüklendi")
    except Exception as e:
        log(f"⚠ Pinterest yüklenemedi ({e}) — sadece Shopify görselleri kullanılacak")
        use_pinterest = False

    def get_best_image(title):
        """Pinterest (birincil) → Shopify (fallback)"""
        if use_pinterest:
            url, desc, score = find_pinterest_image(title, title)
            if url:
                src = "pinterest" if score > 0 else "pinterest-random"
                return url, desc or "pin", src
        url, product, term = find_best_image(title, products, camera_products)
        return url, product, f"shopify:{term}"

    if args.limit:
        articles = articles[:args.limit]

    log(f"\n{'─'*60}")
    log(f"{'DRY-RUN — ' if args.dry_run else ''}Toplam güncellenecek: {len(articles)} makale")
    log(f"{'─'*60}\n")

    ok = skip = fail = 0
    t0 = time.time()

    for i, article in enumerate(articles, 1):
        aid   = article["id"]
        title = article["title"]
        img_url, matched, source = get_best_image(title)

        match_icon = "✓" if "random" not in source and "fallback" not in source else "→"
        log(f"[{i:3}/{len(articles)}] {match_icon} \"{title[:48]}\"")
        log(f"          [{source}] \"{matched[:50]}\"")
        log(f"            {img_url[:80]}...")

        if args.dry_run:
            skip += 1
            continue

        try:
            shopify_put(
                f"blogs/{BLOG_ID}/articles/{aid}.json",
                {"article": {
                    "id":    aid,
                    "image": {"src": img_url, "alt": title[:200]}
                }}
            )
            ok += 1
        except Exception as e:
            log(f"  ✗ HATA: {e}")
            fail += 1

        # Rate limit: ~2 istek/sn (Shopify 40 istek/sn izin veriyor)
        time.sleep(0.6)

        # Her 50 makalede ilerleme raporu
        if i % 50 == 0:
            elapsed = int(time.time() - t0)
            remaining = len(articles) - i
            eta = int(remaining * (elapsed / i))
            log(f"\n  ── İlerleme: {i}/{len(articles)} | ✓{ok} ✗{fail} | geçen:{elapsed}s tahmini:{eta}s ──\n")

    elapsed = int(time.time() - t0)
    log(f"\n{'═'*60}")
    log(f"TAMAMLANDI — {len(articles)} makale | ✓{ok} güncellendi | ✗{fail} hata | {elapsed}s")
    log(f"{'═'*60}")


if __name__ == "__main__":
    main()
