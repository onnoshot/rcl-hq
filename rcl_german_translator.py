#!/usr/bin/env python3
"""RetroCameraLand — Türkçe → Almanca Çeviri & Shopify Translations API Yükleyici
Kapsar: 101 ürün + 11 sayfa + 7 koleksiyon
"""

import json
import re
import time
import urllib.request
import urllib.error
from deep_translator import GoogleTranslator

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
TARGET_LOCALE = "de"
TRANSLATE_DELAY = 0.4   # Google Translate rate limit
SHOPIFY_DELAY  = 0.55   # Shopify API rate limit

translator = GoogleTranslator(source="tr", target="de")


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


# ─── ÇEVIRI YARDIMCILARI ─────────────────────────────────────────────────────

def translate_text(text):
    """Düz metni Türkçe'den Almanca'ya çevir."""
    if not text or not text.strip():
        return text
    try:
        # Max 4800 karakter (Google limiti 5000)
        if len(text) > 4800:
            text = text[:4800]
        result = translator.translate(text)
        time.sleep(TRANSLATE_DELAY)
        return result or text
    except Exception as e:
        print(f"    ⚠ Çeviri hatası: {e}")
        time.sleep(1)
        return text


def translate_html(html):
    """HTML içeriğini çevir — style/script bloklarını koru."""
    if not html or not html.strip():
        return html

    # Style bloklarını çıkar, sonra geri koy
    style_blocks = []
    def save_style(m):
        style_blocks.append(m.group(0))
        return f"__STYLE_{len(style_blocks)-1}__"
    cleaned = re.sub(r"<style[^>]*>.*?</style>", save_style, html, flags=re.DOTALL|re.IGNORECASE)

    # Script bloklarını çıkar
    script_blocks = []
    def save_script(m):
        script_blocks.append(m.group(0))
        return f"__SCRIPT_{len(script_blocks)-1}__"
    cleaned = re.sub(r"<script[^>]*>.*?</script>", save_script, cleaned, flags=re.DOTALL|re.IGNORECASE)

    # Çok uzun HTML'i parçalara böl
    if len(cleaned) > 4800:
        # Kapanış taglarında böl (fixed-width pattern ile)
        chunks = []
        current = ""
        # Basit token bazlı bölme
        tokens = re.split(r"(</(?:p|div|li|h1|h2|h3|h4|h5|h6|section)>)", cleaned)
        for token in tokens:
            current += token
            if len(current) > 4000 and re.search(r"</(?:p|div|li|h[1-6]|section)>$", current):
                chunks.append(current)
                current = ""
        if current:
            chunks.append(current)
        translated = "".join(translate_text(c) for c in chunks)
    else:
        translated = translate_text(cleaned)

    # Style/Script bloklarını geri koy
    for i, block in enumerate(style_blocks):
        translated = translated.replace(f"__STYLE_{i}__", block)
    for i, block in enumerate(script_blocks):
        translated = translated.replace(f"__SCRIPT_{i}__", block)

    return translated


# ─── LOCALE AKTİFLEŞTİRME ───────────────────────────────────────────────────

def enable_german():
    print("Almanca locale aktifleştiriliyor...")
    # Önce enable et
    result = gql("""
        mutation {
            shopLocaleEnable(locale: "de") {
                shopLocale { locale name published }
                userErrors { field message }
            }
        }
    """)
    errors = result.get("data", {}).get("shopLocaleEnable", {}).get("userErrors", [])
    if errors:
        print(f"  Enable hatası: {errors}")

    # Published yap
    result = gql("""
        mutation {
            shopLocaleUpdate(locale: "de", shopLocale: { published: true }) {
                shopLocale { locale name published }
                userErrors { field message }
            }
        }
    """)
    locale = result.get("data", {}).get("shopLocaleUpdate", {}).get("shopLocale", {})
    print(f"  ✓ {locale.get('name')} ({locale.get('locale')}) — published:{locale.get('published')}")
    time.sleep(SHOPIFY_DELAY)


# ─── ÇEVİRİ & YÜKLEME ───────────────────────────────────────────────────────

FIELDS_TO_TRANSLATE = {"title", "body_html", "meta_title", "meta_description"}


def register_translations(resource_id, translations_input):
    """Shopify'a çevirileri yükle."""
    result = gql(
        """
        mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
            translationsRegister(resourceId: $resourceId, translations: $translations) {
                userErrors { field message }
                translations { key value }
            }
        }
        """,
        {"resourceId": resource_id, "translations": translations_input}
    )
    errors = result.get("data", {}).get("translationsRegister", {}).get("userErrors", [])
    if errors:
        print(f"    ✗ Upload hatası: {errors}")
        return False
    time.sleep(SHOPIFY_DELAY)
    return True


def process_resource(resource_id, content_list, label):
    """Bir kaynağın tüm alanlarını çevir ve yükle."""
    translations = []
    for field in content_list:
        key = field["key"]
        value = field.get("value") or ""
        digest = field["digest"]

        if key not in FIELDS_TO_TRANSLATE or not value.strip():
            continue

        if key == "body_html":
            translated = translate_html(value)
        else:
            translated = translate_text(value)

        if translated and translated != value:
            translations.append({
                "locale": TARGET_LOCALE,
                "key": key,
                "value": translated,
                "translatableContentDigest": digest
            })
            print(f"    ✓ {key}: {translated[:60]}")

    if translations:
        register_translations(resource_id, translations)


def translate_resource_type(resource_type, label):
    print(f"\n── {label} ─────────────────────────────────")
    # Tüm kaynakları çek (pagination)
    all_nodes = []
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        result = gql(f"""
            {{
                translatableResources(resourceType: {resource_type}, first: 50{after}) {{
                    pageInfo {{ hasNextPage endCursor }}
                    edges {{
                        node {{
                            resourceId
                            translatableContent {{ key value digest locale }}
                        }}
                    }}
                }}
            }}
        """)
        data = result["data"]["translatableResources"]
        all_nodes.extend(data["edges"])
        if data["pageInfo"]["hasNextPage"]:
            cursor = data["pageInfo"]["endCursor"]
            time.sleep(SHOPIFY_DELAY)
        else:
            break

    print(f"  {len(all_nodes)} kayıt bulundu")

    for i, edge in enumerate(all_nodes, 1):
        node = edge["node"]
        rid = node["resourceId"]
        content = node["translatableContent"]

        # Görünen ad için title bul
        title_field = next((c["value"] for c in content if c["key"] == "title"), rid)
        print(f"\n  [{i:>3}/{len(all_nodes)}] {title_field[:55]}")

        process_resource(rid, content, label)

    print(f"\n  ✓ {label} tamamlandı")


# ─── ANA PROGRAM ─────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  RetroCameraLand — Türkçe → Almanca Çeviri")
    print("=" * 55)

    # 1. Almanca aktifleştir
    enable_german()

    # 2. Sayfalar
    translate_resource_type("PAGE", "SAYFALAR (11)")

    # 3. Koleksiyonlar
    translate_resource_type("COLLECTION", "KOLEKSİYONLAR (7)")

    # 4. Ürünler (en uzun süren)
    translate_resource_type("PRODUCT", "ÜRÜNLER (101)")

    print("\n" + "=" * 55)
    print("  Tüm çeviriler tamamlandı ✓")
    print("  Shopify admin > Online Store > Themes > Languages")
    print("  adresinden Almanca sayfayı görüntüleyebilirsin.")
    print("=" * 55)


if __name__ == "__main__":
    main()
