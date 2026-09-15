#!/usr/bin/env python3
"""RetroCameraLand — Ürün SEO Title & Meta Description + Koleksiyon İçerik Güncelleyici
Sadece boş olanları doldurur, mevcut dolulara dokunmaz.
"""

import json
import re
import urllib.request
import urllib.error
import time

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
DELAY = 0.55


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
        print(f"  ✗ HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def shopify_post(path, data):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def get_metafields(resource, resource_id):
    data = shopify_get(f"{resource}/{resource_id}/metafields.json")
    return data.get("metafields", [])


def upsert_metafield(resource, resource_id, namespace, key, value):
    metafields = get_metafields(resource, resource_id)
    existing = next(
        (m for m in metafields if m["namespace"] == namespace and m["key"] == key), None
    )
    if existing:
        shopify_put(f"metafields/{existing['id']}.json", {
            "metafield": {"id": existing["id"], "value": value, "type": "single_line_text_field"}
        })
    else:
        shopify_post(f"{resource}/{resource_id}/metafields.json", {
            "metafield": {
                "namespace": namespace, "key": key,
                "value": value, "type": "single_line_text_field"
            }
        })
    time.sleep(DELAY)


def strip_html(html):
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def make_meta_desc(title, body_html, max_len=155):
    """Ürün içeriğinden anlamlı meta description üret."""
    text = strip_html(body_html)
    if len(text) >= 40:
        if len(text) <= max_len:
            return text
        cut = text[:max_len]
        last_space = cut.rfind(" ")
        if last_space > 80:
            cut = cut[:last_space]
        return cut + "…"
    # İçerik çok kısaysa title'dan üret
    return f"{title} — test edilmiş retro dijital kamera. RetroCameraLand'de incele, hızlı kargo ile teslim al."[:max_len]


def make_seo_title(title, max_len=60):
    """Ürün SEO title üret."""
    suffix = " | Retro Dijital Kamera | RetroCameraLand"
    if len(title) + len(suffix) <= max_len:
        return title + suffix
    # Kısa suffix
    short_suffix = " | RetroCameraLand"
    if len(title) + len(short_suffix) <= max_len:
        return title + short_suffix
    return (title[:max_len - len(short_suffix)] + short_suffix)


# ─── KOLEKSİYON İÇERİKLERİ ──────────────────────────────────────────────────

COLLECTION_CONTENT = {
    "Best of Retro Cameras": {
        "body_html": """<div class="rcl-collection">
  <h1>En İyi Retro Dijital Kameralar</h1>
  <p>RetroCameraLand'in el seçimi koleksiyonu: test edilmiş, temiz ve koleksiyonluk Y2K dijital kameralar. Kodak, Canon, Nikon, Olympus, Sony, Fujifilm ve Pentax'ın en beğenilen modelleri burada.</p>
  <p>Her kamera satışa sunulmadan önce titizlikle incelenir ve çalışır durumu doğrulanır.</p>
</div>""",
        "seo_title": "En İyi Retro Dijital Kameralar | RetroCameraLand",
        "meta_description": "RetroCameraLand'in el seçimi retro dijital kameralar. Test edilmiş Kodak, Canon, Olympus, Fujifilm modelleri. Koleksiyonluk Y2K kameralar uygun fiyatlarla."
    },
    "Öne Çıkan Ürünler": {
        "body_html": """<div class="rcl-collection">
  <h1>Öne Çıkan Ürünler</h1>
  <p>RetroCameraLand'de en çok ilgi gören, hızlı satılan ve müşterilerimizin en beğendiği kamera ve aksesuarlar. Stoklar sınırlıdır — beğendiğini kaçırma.</p>
</div>""",
        "seo_title": "Öne Çıkan Ürünler | RetroCameraLand",
        "meta_description": "RetroCameraLand'de öne çıkan ve en çok beğenilen retro dijital kameralar ve aksesuarlar. Stoklar sınırlı, hızlı kargo ile teslim."
    },
    "Retro Dijital Kameralar": {
        "body_html": """<div class="rcl-collection">
  <h1>Retro Dijital Kameralar</h1>
  <p>2000'li yılların ikonik dijital kompakt kameraları — test edilmiş, temiz ve kullanıma hazır. Kodak, Canon, Nikon, Olympus, Sony, Fujifilm, Pentax ve daha fazlası.</p>
  <p>Y2K estetiğini arıyorsan doğru yerdesin. Her model orijinal görünümünü koruyarak yeniden hayat buluyor.</p>
</div>""",
        "seo_title": "Retro Dijital Kameralar | Y2K Kamera | RetroCameraLand",
        "meta_description": "Test edilmiş retro dijital kameralar: Kodak, Canon, Nikon, Olympus, Sony, Fujifilm, Pentax. Y2K estetiği, koleksiyonluk modeller. RetroCameraLand'de incele."
    },
}


def update_collections():
    print("\n── KOLEKSİYONLAR ──────────────────────────────")
    colls = shopify_get("custom_collections.json?limit=250&fields=id,title,body_html,handle")
    for c in colls.get("custom_collections", []):
        name = c["title"]
        if name not in COLLECTION_CONTENT:
            continue
        body = (c.get("body_html") or "").strip()
        if body:
            print(f"  ATLANDI (dolu): {name}")
            continue

        content = COLLECTION_CONTENT[name]
        print(f"  ▶ {name}")
        shopify_put(f"custom_collections/{c['id']}.json", {
            "custom_collection": {"id": c["id"], "body_html": content["body_html"]}
        })
        time.sleep(DELAY)
        print(f"    ✓ İçerik eklendi")

        upsert_metafield("custom_collections", c["id"], "global", "title_tag", content["seo_title"])
        print(f"    ✓ SEO title: {content['seo_title']}")

        upsert_metafield("custom_collections", c["id"], "global", "description_tag", content["meta_description"])
        print(f"    ✓ Meta desc: {content['meta_description'][:60]}…")


def update_products():
    print("\n── ÜRÜNLER ─────────────────────────────────────")
    products = shopify_get("products.json?limit=250&fields=id,title,body_html").get("products", [])
    print(f"  {len(products)} ürün bulundu\n")

    seo_title_updated = 0
    meta_desc_updated = 0
    skipped = 0

    for i, p in enumerate(products, 1):
        pid = p["id"]
        title = p["title"]
        body = p.get("body_html", "") or ""

        metafields = get_metafields("products", pid)
        time.sleep(DELAY)

        has_seo_title = any(m["namespace"] == "global" and m["key"] == "title_tag" for m in metafields)
        has_meta_desc = any(m["namespace"] == "global" and m["key"] == "description_tag" for m in metafields)

        if has_seo_title and has_meta_desc:
            skipped += 1
            print(f"  [{i:>3}/{len(products)}] ATLANDI (dolu): {title[:50]}")
            continue

        print(f"  [{i:>3}/{len(products)}] {title[:55]}")

        if not has_seo_title:
            seo_title = make_seo_title(title)
            upsert_metafield("products", pid, "global", "title_tag", seo_title)
            print(f"    ✓ SEO title: {seo_title[:65]}")
            seo_title_updated += 1

        if not has_meta_desc:
            meta_desc = make_meta_desc(title, body)
            upsert_metafield("products", pid, "global", "description_tag", meta_desc)
            print(f"    ✓ Meta desc: {meta_desc[:65]}…")
            meta_desc_updated += 1

    print(f"\n  SEO title güncellenen : {seo_title_updated}")
    print(f"  Meta desc güncellenen : {meta_desc_updated}")
    print(f"  Atlanan (zaten dolu)  : {skipped}")


def main():
    print("=== RetroCameraLand SEO — Ürün & Koleksiyon Güncelleyici ===")
    update_collections()
    update_products()
    print("\n=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
