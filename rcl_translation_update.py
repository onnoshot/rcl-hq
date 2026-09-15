#!/usr/bin/env python3
"""RetroCameraLand — Artımlı Çeviri Güncelleyici
Sadece çevirisi OLMAYAN yeni içerikleri çevirir. Mevcutlara dokunmaz.
Kullanım: python3 rcl_translation_update.py
"""

import json
import re
import time
import urllib.request
from deep_translator import GoogleTranslator

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
TRANSLATE_DELAY = 0.5
SHOPIFY_DELAY  = 0.6

LANGUAGES = [
    ("de",    "de",  "Almanca"),
    ("fr",    "fr",  "Fransızca"),
    ("it",    "it",  "İtalyanca"),
    ("pt-PT", "pt",  "Portekizce (PT)"),
    ("ar",    "ar",  "Arapça"),
    ("ja",    "ja",  "Japonca"),
]

FIELDS_TO_TRANSLATE = {"title", "body_html", "meta_title", "meta_description"}


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


def translate_text(translator, text):
    if not text or not text.strip():
        return text
    try:
        result = translator.translate(text[:4800])
        time.sleep(TRANSLATE_DELAY)
        return result or text
    except Exception as e:
        print(f"    ⚠ {e}")
        time.sleep(2)
        return text


def translate_html(translator, html):
    if not html or not html.strip():
        return html
    style_blocks = []
    def save_style(m):
        style_blocks.append(m.group(0))
        return f"__STYLE_{len(style_blocks)-1}__"
    cleaned = re.sub(r"<style[^>]*>.*?</style>", save_style, html,
                     flags=re.DOTALL | re.IGNORECASE)
    script_blocks = []
    def save_script(m):
        script_blocks.append(m.group(0))
        return f"__SCRIPT_{len(script_blocks)-1}__"
    cleaned = re.sub(r"<script[^>]*>.*?</script>", save_script, cleaned,
                     flags=re.DOTALL | re.IGNORECASE)
    if len(cleaned) > 4800:
        chunks, current = [], ""
        tokens = re.split(r"(</(?:p|div|li|h1|h2|h3|h4|h5|h6|section)>)", cleaned)
        for token in tokens:
            current += token
            if len(current) > 4000 and re.search(r"</(?:p|div|li|h[1-6]|section)>$", current):
                chunks.append(current)
                current = ""
        if current:
            chunks.append(current)
        translated = "".join(translate_text(translator, c) for c in chunks)
    else:
        translated = translate_text(translator, cleaned)
    for i, b in enumerate(style_blocks):
        translated = translated.replace(f"__STYLE_{i}__", b)
    for i, b in enumerate(script_blocks):
        translated = translated.replace(f"__SCRIPT_{i}__", b)
    return translated


def fetch_resources_with_translations(resource_type, locale):
    """Kaynakları mevcut çevirileriyle birlikte çek."""
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
                        translations(locale: "{locale}") {{ key value }}
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


def process_resource(resource_id, content_list, existing_translations, translator, locale):
    # Mevcut çeviri anahtarlarını bul
    existing_keys = {t["key"] for t in existing_translations if t.get("value")}

    translations = []
    for field in content_list:
        key    = field["key"]
        value  = field.get("value") or ""
        digest = field["digest"]

        # Zaten çevrilmişse atla
        if key in existing_keys:
            continue
        if key not in FIELDS_TO_TRANSLATE or not value.strip():
            continue

        translated = (translate_html(translator, value)
                      if key == "body_html"
                      else translate_text(translator, value))

        if translated and translated != value:
            translations.append({
                "locale": locale,
                "key": key,
                "value": translated,
                "translatableContentDigest": digest,
            })

    if not translations:
        return False

    result = gql(
        """mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
            translationsRegister(resourceId: $resourceId, translations: $translations) {
                userErrors { message }
                translations { key }
            }
        }""",
        {"resourceId": resource_id, "translations": translations}
    )
    errors = result.get("data", {}).get("translationsRegister", {}).get("userErrors", [])
    if errors:
        print(f"    ✗ {errors}")
    time.sleep(SHOPIFY_DELAY)
    return True


def update_language(shopify_locale, translator_code, lang_name):
    print(f"\n── {lang_name} ({shopify_locale}) ─────────────────────")
    translator = GoogleTranslator(source="tr", target=translator_code)
    total_new = 0

    for resource_type, label in [("PAGE", "Sayfalar"), ("COLLECTION", "Koleksiyonlar"), ("PRODUCT", "Ürünler")]:
        nodes = fetch_resources_with_translations(resource_type, shopify_locale)
        new_count = 0
        for edge in nodes:
            node     = edge["node"]
            rid      = node["resourceId"]
            content  = node["translatableContent"]
            existing = node.get("translations", [])

            # Tüm alanlar zaten çevrilmişse atla
            existing_keys = {t["key"] for t in existing if t.get("value")}
            needed = {f["key"] for f in content
                      if f["key"] in FIELDS_TO_TRANSLATE and (f.get("value") or "").strip()}
            if needed.issubset(existing_keys):
                continue

            title = next((c["value"] for c in content if c["key"] == "title"), rid)
            print(f"  YENİ [{label}] {title[:55]}")
            updated = process_resource(rid, content, existing, translator, shopify_locale)
            if updated:
                new_count += 1

        print(f"  {label}: {new_count} yeni kayıt çevrildi")
        total_new += new_count

    print(f"  Toplam yeni: {total_new} kayıt")
    return total_new


def main():
    print("=" * 55)
    print("  RetroCameraLand — Artımlı Çeviri Güncelleyici")
    print("  (Sadece yeni/eksik içerikler çevrilir)")
    print("=" * 55)

    grand_total = 0
    for shopify_locale, translator_code, lang_name in LANGUAGES:
        new = update_language(shopify_locale, translator_code, lang_name)
        grand_total += new

    print(f"\n{'='*55}")
    if grand_total == 0:
        print("  Tüm diller güncel — yeni içerik bulunamadı.")
    else:
        print(f"  Tamamlandı ✓  Toplam {grand_total} yeni kayıt çevrildi.")
    print("=" * 55)


if __name__ == "__main__":
    main()
