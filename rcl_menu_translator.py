#!/usr/bin/env python3
"""RetroCameraLand — Navigasyon Menüsü Çeviri (6 dil)"""

import json, time, urllib.request
from deep_translator import GoogleTranslator

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"

LANGUAGES = [
    ("de",    "de",  "Almanca"),
    ("fr",    "fr",  "Fransızca"),
    ("it",    "it",  "İtalyanca"),
    ("pt-PT", "pt",  "Portekizce"),
    ("ar",    "ar",  "Arapça"),
    ("ja",    "ja",  "Japonca"),
]

# Marka/teknik isimler — çevrilmeyecek
SKIP_TRANSLATE = {"Blog", "KVKK and Privacy", "Your Privacy Choices", "Profil",
                  "Affilate", "Affiliate"}


def gql(query, variables=None):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/graphql.json"
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_menu_links():
    result = gql('{ translatableResources(resourceType: LINK, first: 50) { edges { node { resourceId translatableContent { key value digest } } } } }')
    return result["data"]["translatableResources"]["edges"]


def translate_menu(shopify_locale, translator_code, lang_name):
    print(f"\n── {lang_name} ({shopify_locale}) ──────────────")
    tr = GoogleTranslator(source="tr", target=translator_code)
    links = fetch_menu_links()
    updated = 0

    for edge in links:
        node   = edge["node"]
        rid    = node["resourceId"]
        fields = node["translatableContent"]

        for field in fields:
            if field["key"] != "title":
                continue
            original = field["value"] or ""
            digest   = field["digest"]

            if not original or original in SKIP_TRANSLATE:
                continue

            translated = tr.translate(original)
            time.sleep(0.4)

            if not translated or translated == original:
                continue

            result = gql(
                """mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
                    translationsRegister(resourceId: $resourceId, translations: $translations) {
                        userErrors { message }
                        translations { key value }
                    }
                }""",
                {"resourceId": rid, "translations": [{
                    "locale": shopify_locale,
                    "key": "title",
                    "value": translated,
                    "translatableContentDigest": digest
                }]}
            )
            errors = result.get("data", {}).get("translationsRegister", {}).get("userErrors", [])
            if not errors:
                print(f"  ✓ {original:20} → {translated}")
                updated += 1
            time.sleep(0.5)

    print(f"  {updated} öğe çevrildi")


def main():
    print("=" * 50)
    print("  RetroCameraLand — Menü Çevirisi (6 dil)")
    print("=" * 50)
    for shopify_locale, translator_code, lang_name in LANGUAGES:
        translate_menu(shopify_locale, translator_code, lang_name)
    print("\n  Tamamlandı ✓")


if __name__ == "__main__":
    main()
