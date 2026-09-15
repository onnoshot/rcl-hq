#!/usr/bin/env python3
"""RetroCameraLand — Shopify Görsel Alt Text Güncelleyici
900 boş alt text'i ürün adına göre SEO uyumlu şekilde doldurur.
"""

import json
import urllib.request
import urllib.error
import time

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"

# Shopify REST bucket: 40 istek / 2 istek/sn → 0.55s güvenli aralık
REQUEST_DELAY = 0.55


def shopify_get(path):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def shopify_put(path, data):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"    ✗ HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def make_alt(title, position, total):
    """
    SEO uyumlu alt text üret.
    - 1. görsel: ürün adı + retro dijital kamera + site
    - Sonrakiler: ürün adı + açıklayıcı etiket + site
    """
    labels = [
        "ön görünüm", "arka görünüm", "yan görünüm",
        "detay", "üst görünüm", "ekran detayı",
        "lens detayı", "kutu içeriği", "aksesuar",
    ]
    brand = "RetroCameraLand"

    if position == 1:
        return f"{title} | Retro Dijital Kamera | {brand}"
    else:
        idx = (position - 2) % len(labels)
        label = labels[idx] if total > 2 else "detay görünüm"
        return f"{title} {label} | {brand}"


def fetch_all_products():
    products = []
    page_info = None
    while True:
        if page_info:
            path = f"products.json?limit=250&fields=id,title,images&page_info={page_info}"
        else:
            path = "products.json?limit=250&fields=id,title,images"
        data = shopify_get(path)
        batch = data.get("products", [])
        products.extend(batch)
        if len(batch) < 250:
            break
        # Shopify cursor pagination — basit limit yeterli bu boyut için
        break
    return products


def main():
    print("=== RetroCameraLand Alt Text Güncelleyici ===\n")

    print("Ürünler çekiliyor...")
    products = fetch_all_products()
    print(f"  {len(products)} ürün bulundu\n")

    total_updated = 0
    total_skipped = 0
    total_errors = 0

    for p_idx, product in enumerate(products, 1):
        title = product["title"]
        images = product.get("images", [])
        empty_images = [img for img in images if not img.get("alt")]

        if not empty_images:
            total_skipped += len(images)
            continue

        print(f"[{p_idx}/{len(products)}] {title} — {len(empty_images)} görsel güncelleniyor")

        for img in empty_images:
            position = img.get("position", 1)
            alt = make_alt(title, position, len(images))
            result = shopify_put(
                f"products/{product['id']}/images/{img['id']}.json",
                {"image": {"id": img["id"], "alt": alt}}
            )
            if result:
                total_updated += 1
                print(f"    ✓ [{position}] {alt[:70]}")
            else:
                total_errors += 1
            time.sleep(REQUEST_DELAY)

    print(f"\n=== Tamamlandı ===")
    print(f"  Güncellenen : {total_updated}")
    print(f"  Atlanan     : {total_skipped} (zaten doluydu)")
    print(f"  Hata        : {total_errors}")


if __name__ == "__main__":
    main()
