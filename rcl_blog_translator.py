#!/usr/bin/env python3
"""RetroCameraLand — Blog (ARTICLE) Çok Dilli Çeviri Script
Blogları 7 dile çevirir: İngilizce → Almanca → Fransızca → İtalyanca →
Portekizce → Arapça → Japonca.

ÖNEMLİ: Zaten çevrilmiş (ve güncel) alanları ATLAR — resume edilebilir.
Kesilirse tekrar çalıştır, kaldığı yerden devam eder.

Kaynak dil: tr. ürün/sayfa/koleksiyon çevirileri ayrı script'te
(rcl_multilang_translator.py). Bu script SADECE blogları işler.
"""

import json
import re
import socket
import time
import urllib.request
from deep_translator import GoogleTranslator

# Ağ takılmalarını sonsuz donmaya çevirmesin: her soket çağrısına global timeout.
# Takılma -> exception -> translate_text/gql try-except yakalar, sonsuz beklemez.
socket.setdefaulttimeout(30)

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
TRANSLATE_DELAY = 0.5
SHOPIFY_DELAY  = 0.6

# Shopify locale → (deep-translator kodu, dil adı)
LANGUAGES = [
    ("en",    "en",    "İngilizce"),
    ("de",    "de",    "Almanca"),
    ("fr",    "fr",    "Fransızca"),
    ("it",    "it",    "İtalyanca"),
    ("pt-PT", "pt",    "Portekizce (PT)"),
    ("ar",    "ar",    "Arapça"),
    ("ja",    "ja",    "Japonca"),
]

# Blog yazısı için çevrilecek alanlar (handle çevrilmez — URL kırılmasın)
FIELDS_TO_TRANSLATE = {
    "title", "body_html", "summary_html", "meta_title", "meta_description",
}


# ─── SHOPIFY API ─────────────────────────────────────────────────────────────

def gql(query, variables=None):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/graphql.json"
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


# ─── ÇEVİRİ ─────────────────────────────────────────────────────────────────

def make_translator(target_code):
    return GoogleTranslator(source="tr", target=target_code)


def translate_text(translator, text):
    if not text or not text.strip():
        return text
    try:
        chunk = text[:4800]
        result = translator.translate(chunk)
        time.sleep(TRANSLATE_DELAY)
        return result or text
    except Exception as e:
        print(f"    ⚠ Çeviri hatası: {e}")
        time.sleep(2)
        return text


def translate_html(translator, html):
    if not html or not html.strip():
        return html

    # Style bloklarını koru
    style_blocks = []
    def save_style(m):
        style_blocks.append(m.group(0))
        return f"__STYLE_{len(style_blocks)-1}__"
    cleaned = re.sub(r"<style[^>]*>.*?</style>", save_style, html,
                     flags=re.DOTALL | re.IGNORECASE)

    # Script bloklarını koru (JSON-LD schema dahil)
    script_blocks = []
    def save_script(m):
        script_blocks.append(m.group(0))
        return f"__SCRIPT_{len(script_blocks)-1}__"
    cleaned = re.sub(r"<script[^>]*>.*?</script>", save_script, cleaned,
                     flags=re.DOTALL | re.IGNORECASE)

    # Uzun içerik → parçala
    if len(cleaned) > 4800:
        chunks = []
        current = ""
        tokens = re.split(r"(</(?:p|div|li|h1|h2|h3|h4|h5|h6|section)>)", cleaned)
        for token in tokens:
            current += token
            if len(current) > 4000 and re.search(
                r"</(?:p|div|li|h[1-6]|section)>$", current
            ):
                chunks.append(current)
                current = ""
        if current:
            chunks.append(current)
        translated = "".join(translate_text(translator, c) for c in chunks)
    else:
        translated = translate_text(translator, cleaned)

    # Blokları geri koy
    for i, block in enumerate(style_blocks):
        translated = translated.replace(f"__STYLE_{i}__", block)
    for i, block in enumerate(script_blocks):
        translated = translated.replace(f"__SCRIPT_{i}__", block)

    return translated


# ─── LOCALE & YÜKLEME ────────────────────────────────────────────────────────

def enable_locale(shopify_locale, lang_name):
    gql(f'mutation {{ shopLocaleEnable(locale: "{shopify_locale}") '
        f'{{ shopLocale {{ locale published }} userErrors {{ message }} }} }}')
    result2 = gql(f'mutation {{ shopLocaleUpdate(locale: "{shopify_locale}", '
                  f'shopLocale: {{ published: true }}) '
                  f'{{ shopLocale {{ locale published }} userErrors {{ message }} }} }}')
    published = result2.get("data", {}).get("shopLocaleUpdate", {}).get(
        "shopLocale", {}).get("published", False)
    print(f"  ✓ {lang_name} ({shopify_locale}) locale aktif: {published}")
    time.sleep(SHOPIFY_DELAY)


def register_translations(resource_id, translations_input, shopify_locale):
    if not translations_input:
        return True
    for t in translations_input:
        t["locale"] = shopify_locale
    result = gql(
        """mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
            translationsRegister(resourceId: $resourceId, translations: $translations) {
                userErrors { field message }
                translations { key }
            }
        }""",
        {"resourceId": resource_id, "translations": translations_input}
    )
    errors = result.get("data", {}).get("translationsRegister", {}).get("userErrors", [])
    if errors:
        print(f"    ✗ {errors}")
        return False
    time.sleep(SHOPIFY_DELAY)
    return True


def fetch_all_resources(resource_type, shopify_locale):
    """Kaynak içeriği + mevcut çevirileri (skip için) birlikte çeker."""
    all_nodes = []
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        result = gql(f"""{{
            translatableResources(resourceType: {resource_type}, first: 50{after}) {{
                pageInfo {{ hasNextPage endCursor }}
                edges {{
                    node {{
                        resourceId
                        translatableContent {{ key value digest }}
                        translations(locale: "{shopify_locale}") {{ key value outdated }}
                    }}
                }}
            }}
        }}""")
        data = result["data"]["translatableResources"]
        all_nodes.extend(data["edges"])
        if data["pageInfo"]["hasNextPage"]:
            cursor = data["pageInfo"]["endCursor"]
            time.sleep(SHOPIFY_DELAY)
        else:
            break
    return all_nodes


def process_resource(resource_id, content_list, existing, translator, shopify_locale):
    # Zaten çevrilmiş (ve güncel olmayan = outdated DEĞİL) alanları atla
    done_keys = {
        t["key"] for t in (existing or [])
        if t.get("value") and not t.get("outdated")
    }

    translations = []
    skipped = 0
    for field in content_list:
        key   = field["key"]
        value = field.get("value") or ""
        digest = field["digest"]

        if key not in FIELDS_TO_TRANSLATE or not value.strip():
            continue
        if key in done_keys:
            skipped += 1
            continue

        translated = (translate_html(translator, value)
                      if key in ("body_html", "summary_html")
                      else translate_text(translator, value))

        if translated and translated != value:
            translations.append({
                "locale": shopify_locale,
                "key": key,
                "value": translated,
                "translatableContentDigest": digest,
            })

    if translations:
        register_translations(resource_id, translations, shopify_locale)
        return ("translated", skipped)
    return ("skip" if skipped else "empty", skipped)


def translate_language(shopify_locale, translator_code, lang_name):
    print(f"\n{'='*55}")
    print(f"  {lang_name.upper()} ({shopify_locale})")
    print(f"{'='*55}")

    translator = make_translator(translator_code)
    enable_locale(shopify_locale, lang_name)

    for resource_type, label in [("BLOG", "Blog başlıkları"),
                                 ("ARTICLE", "Blog yazıları")]:
        nodes = fetch_all_resources(resource_type, shopify_locale)
        print(f"\n  ── {label} ({len(nodes)}) ──")
        n_translated = n_skipped = 0
        for i, edge in enumerate(nodes, 1):
            node    = edge["node"]
            rid     = node["resourceId"]
            content = node["translatableContent"]
            existing = node.get("translations", [])
            title   = next((c["value"] for c in content if c["key"] == "title"), rid)
            status, _ = process_resource(rid, content, existing, translator, shopify_locale)
            if status == "translated":
                n_translated += 1
                print(f"  [{i:>3}/{len(nodes)}] ✓ {title[:50]}")
            else:
                n_skipped += 1
        print(f"  → {n_translated} çevrildi, {n_skipped} atlandı (zaten çevrili)")

    print(f"\n  ✓ {lang_name} tamamlandı")


# ─── ANA PROGRAM ─────────────────────────────────────────────────────────────

def main():
    start = time.time()
    print("=" * 55)
    print("  RetroCameraLand — Blog Çok Dilli Çeviri")
    print(f"  {len(LANGUAGES)} dil: EN → DE → FR → IT → PT → AR → JA")
    print("  (zaten çevrilmiş alanlar atlanır — resume edilebilir)")
    print("=" * 55)

    for shopify_locale, translator_code, lang_name in LANGUAGES:
        translate_language(shopify_locale, translator_code, lang_name)
        print(f"\n  Sonraki dile geçiliyor... (15 sn bekleniyor)")
        time.sleep(15)

    elapsed = round((time.time() - start) / 60, 1)
    print("\n" + "=" * 55)
    print(f"  TÜM BLOG ÇEVİRİLERİ TAMAMLANDI ✓  ({elapsed} dakika)")
    print("  Kontrol: Shopify > Online Store > Blog posts (dil seçici)")
    print("=" * 55)


if __name__ == "__main__":
    main()
