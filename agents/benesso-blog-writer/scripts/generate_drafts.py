#!/usr/bin/env python3
"""
3 blog yazısı üret (OpenAI GPT-4o) ve outputs/ klasörüne kaydet.
Shopify token hazır olduğunda publish_drafts.py ile yayınla.
"""

import os, json, re, sys
from datetime import date
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent
STRATEGY  = AGENT_DIR / "knowledge" / "STRATEGY.md"
OUTPUTS   = AGENT_DIR / "outputs"
ROOT_ENV  = AGENT_DIR.parent.parent / ".env"

def load_env():
    if ROOT_ENV.exists():
        for line in ROOT_ENV.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def generate_post(client, tr_kw, en_kw, product_handle, content_type, strategy):
    product_url = f"https://benessocoffee.com/products/{product_handle}" if product_handle and product_handle != "-" else ""

    prompt = f"""Sen Benesso Coffee için blog yazarısın. Specialty (3. nesil) kahve uzmanısın.

MARKA STRATEJİSİ (özet):
{strategy[:1500]}

GÖREV: Keyword için TR + EN blog yaz.

TR Keyword: {tr_kw}
EN Keyword: {en_kw}
Ürün linki: {product_url or "yok"}
İçerik tipi: {content_type}

KURALLAR:
- TR yazı 700+ kelime. EN yazı 700+ kelime (doğrudan çeviri değil, EN okuyucuya özgü yaz)
- Keyword H1 başlıkta VE ilk paragrafta geçmeli
- Ürün linki varsa yazıda doğal bir yerde <a href="{product_url}">ürün adı</a> şeklinde link ver
- body_html: temiz HTML (h1, h2, p, a, ul, li tagları)
- Benesso marka sesi: samimi, bilgili, kahve tutkusu yansıtmalı, "sen" dili (TR), "you" (EN)
- Clickbait ve uydurma istatistik yasak

SADECE JSON döndür, başka hiçbir şey yazma:
{{
  "tr_title": "...",
  "tr_meta": "150-160 karakter meta description (keyword içermeli)",
  "tr_body": "<h1>...</h1><p>...</p>...",
  "en_title": "...",
  "en_meta": "150-160 char meta description (keyword inside)",
  "en_body": "<h1>...</h1><p>...</p>..."
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8000,
        temperature=0.7,
    )
    raw = response.choices[0].message.content.strip()
    # JSON bloğunu çıkar (```json ... ``` veya düz JSON)
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    m = re.search(r'\{[\s\S]+\}', raw)
    if not m:
        raise ValueError(f"JSON yok: {raw[:300]}")
    return json.loads(m.group(0))

def get_product_image(handle):
    if not handle or handle == "-":
        return None
    import requests
    try:
        r = requests.get(f"https://benessocoffee.com/products/{handle}.json", timeout=10)
        if r.status_code == 200:
            imgs = r.json().get("product", {}).get("images", [])
            if imgs:
                return imgs[0].get("src")
    except Exception:
        pass
    return None

def save_draft(slug, kw_info, content, image_url):
    OUTPUTS.mkdir(exist_ok=True)
    today = date.today().isoformat()
    fname = OUTPUTS / f"{today}_DRAFT_{slug}.json"
    fname.write_text(json.dumps({
        "date": today,
        "tr_keyword": kw_info[0],
        "en_keyword": kw_info[1],
        "product_handle": kw_info[2],
        "content_type": kw_info[3],
        "image_url": image_url,
        "tr_title": content["tr_title"],
        "tr_meta": content["tr_meta"],
        "tr_body": content["tr_body"],
        "en_title": content["en_title"],
        "en_meta": content["en_meta"],
        "en_body": content["en_body"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Kaydedildi: {fname.name}")
    return fname

POSTS = [
    ("ethiopia kahvesi nedir", "what is ethiopian coffee",
     "etiyopya-guji-washed-yoresel-filtre-kahve", "product"),
    ("kenya kahvesi nedir", "what is kenyan coffee",
     "kenya-kathakwa-washed-yoresel-filtre-kahve", "product"),
    ("kosta rika kahvesi özellikleri", "costa rica coffee characteristics",
     "kosta-rika-la-isla-honey-filtre-kahve", "product"),
]

def main():
    load_env()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        print("HATA: OPENAI_API_KEY bulunamadı", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("openai paketi yükleniyor...")
        os.system("pip3 install openai -q")
        from openai import OpenAI

    client = OpenAI(api_key=openai_key)
    strategy = STRATEGY.read_text(encoding="utf-8") if STRATEGY.exists() else ""

    drafts = []
    for i, kw_info in enumerate(POSTS, 1):
        tr_kw, en_kw, handle, ctype = kw_info
        print(f"\n[{i}/3] Yazılıyor: {tr_kw}")
        try:
            content = generate_post(client, tr_kw, en_kw, handle, ctype, strategy)
            image_url = get_product_image(handle)
            slug = re.sub(r'[^a-z0-9]+', '-', tr_kw.lower())[:30]
            fname = save_draft(slug, kw_info, content, image_url)
            drafts.append(str(fname))
            print(f"  TR: {content['tr_title']}")
            print(f"  EN: {content['en_title']}")
            print(f"  Görsel: {image_url or 'yok (Unsplash yedek kullanılacak)'}")
        except Exception as e:
            print(f"  HATA [{tr_kw}]: {e}", file=sys.stderr)

    print(f"\n{'='*50}")
    print(f"✓ {len(drafts)}/3 taslak hazır → outputs/ klasörü")
    print("Sonraki adım: Shopify Custom App token alınınca")
    print("  → python3 publish_drafts.py SHOPIFY_TOKEN_BURAYA")

if __name__ == "__main__":
    main()
