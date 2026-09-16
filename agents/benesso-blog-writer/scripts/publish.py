#!/usr/bin/env python3
"""
Benesso Blog Writer — Ana otomasyon scripti
Günde 3 kez çalışır: 07:00, 12:00, 18:00
Her çalıştırmada: 1 keyword seçer → TR + EN blog yazar → Shopify'a yayınlar
"""

import os
import json
import re
import sys
import requests
from datetime import datetime, date
from pathlib import Path
import anthropic

# ─── Paths ─────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent.parent
STRATEGY   = AGENT_DIR / "knowledge" / "STRATEGY.md"
KEYWORDS   = AGENT_DIR / "data" / "imports" / "keywords.md"
PUB_LOG    = AGENT_DIR / "data" / "imports" / "published_log.md"
OUTPUTS    = AGENT_DIR / "outputs"
JOURNAL    = AGENT_DIR.parent.parent / "journal"

# ─── Config ────────────────────────────────────────────────────────────────
SHOPIFY_STORE      = os.getenv("SHOPIFY_STORE", "benessocoffee.myshopify.com")
SHOPIFY_TOKEN      = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_BLOG_HANDLE = "news"
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

DAILY_TARGET = 3


# ─── Shopify helpers ────────────────────────────────────────────────────────

def shopify_headers():
    return {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }


def get_blog_id() -> int:
    """Blog handle 'news' için numeric ID'yi çek."""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs.json"
    r = requests.get(url, headers=shopify_headers(), timeout=15)
    r.raise_for_status()
    for blog in r.json().get("blogs", []):
        if blog.get("handle") == SHOPIFY_BLOG_HANDLE:
            return blog["id"]
    raise RuntimeError(f"Blog handle '{SHOPIFY_BLOG_HANDLE}' bulunamadı")


def get_product_image(handle: str) -> str | None:
    """Ürün handle'ından ilk görselin URL'ini al."""
    if not handle or handle == "-":
        return None
    url = f"https://benessocoffee.com/products/{handle}.json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            images = r.json().get("product", {}).get("images", [])
            if images:
                return images[0].get("src")
    except Exception:
        pass
    return None


def get_unsplash_image(query: str) -> str | None:
    """Unsplash'ten yedek görsel al."""
    if not UNSPLASH_ACCESS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=10,
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None


def publish_article(blog_id: int, title: str, body_html: str,
                    meta_desc: str, image_url: str | None,
                    tags: list[str], lang: str) -> int:
    """Shopify'a bir blog yazısı yayınla, article ID'yi döndür."""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs/{blog_id}/articles.json"
    payload: dict = {
        "article": {
            "title": title,
            "body_html": body_html,
            "author": "Benesso Coffee",
            "published": True,
            "tags": ", ".join(tags),
            "metafields": [
                {
                    "key": "description_tag",
                    "value": meta_desc,
                    "type": "single_line_text_field",
                    "namespace": "global",
                }
            ],
        }
    }
    if image_url:
        payload["article"]["image"] = {"src": image_url, "alt": title}

    r = requests.post(url, headers=shopify_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["article"]["id"]


# ─── Keyword helpers ────────────────────────────────────────────────────────

def load_published_keywords() -> set[str]:
    """published_log.md'den kullanılmış TR keyword'leri döndür."""
    used = set()
    if not PUB_LOG.exists():
        return used
    for line in PUB_LOG.read_text(encoding="utf-8").splitlines():
        parts = line.split("|")
        if len(parts) >= 4 and parts[0].strip().startswith("20"):
            used.add(parts[3].strip().lower())
    return used


def count_today_posts() -> int:
    """Bugün yayınlanan yazı sayısını döndür."""
    today = date.today().isoformat()
    count = 0
    if PUB_LOG.exists():
        for line in PUB_LOG.read_text(encoding="utf-8").splitlines():
            if line.startswith(today):
                count += 1
    return count


def select_keyword(used: set[str]) -> tuple[str, str, str, str] | None:
    """
    keywords.md'den kullanılmamış bir keyword seç.
    Dönüş: (tr_keyword, en_keyword, product_handle, content_type)
    Öncelik: product > origin > method > brew-guide > education
    """
    if not KEYWORDS.exists():
        return None

    priority_order = ["product", "origin", "method", "brew-guide", "education"]
    candidates: dict[str, list] = {p: [] for p in priority_order}

    for line in KEYWORDS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        tr_kw, en_kw, handle, ctype = parts[0], parts[1], parts[2], parts[3]
        if tr_kw.lower() not in used:
            if ctype in candidates:
                candidates[ctype].append((tr_kw, en_kw, handle, ctype))

    for ptype in priority_order:
        if candidates[ptype]:
            return candidates[ptype][0]

    return None


def append_to_log(tr_title: str, en_title: str, tr_kw: str,
                   tr_id: int, en_id: int) -> None:
    """published_log.md'ye yeni satır ekle."""
    today = date.today().isoformat()
    line = f"{today} | {tr_title} | {en_title} | {tr_kw} | {tr_id} | {en_id}\n"
    with open(PUB_LOG, "a", encoding="utf-8") as f:
        f.write(line)


# ─── Claude content generation ─────────────────────────────────────────────

def load_strategy() -> str:
    if STRATEGY.exists():
        return STRATEGY.read_text(encoding="utf-8")[:2000]
    return ""


def generate_content(tr_keyword: str, en_keyword: str,
                     product_handle: str, content_type: str) -> dict:
    """
    Claude'a TR + EN blog içeriği ürettir.
    Dönüş: {tr_title, tr_meta, tr_body, en_title, en_meta, en_body}
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    strategy = load_strategy()

    # Ürün URL'ini prompt'a ekle
    product_url = ""
    if product_handle and product_handle != "-":
        product_url = f"https://benessocoffee.com/products/{product_handle}"

    prompt = f"""Sen Benesso Coffee için blog yazarısın. Specialty (3. nesil) kahve uzmanısın.

MARKA STRATEJİSİ:
{strategy}

GÖREV:
Aşağıdaki keyword için hem Türkçe hem İngilizce olmak üzere iki ayrı blog yazısı üret.

TR Keyword: {tr_keyword}
EN Keyword: {en_keyword}
İlişkili ürün linki: {product_url if product_url else "yok"}
İçerik tipi: {content_type}

KURALLAR:
- TR yazı en az 600 kelime
- EN yazı en az 600 kelime (doğrudan çeviri değil, EN okuyucuya özgü)
- Keyword H1 başlıkta ve ilk paragrafta geçmeli
- Ürün linki varsa, yazının içinde doğal bir yerde ürüne link ver
- body_html: HTML formatında (h1, h2, p, a tagları kullan)
- Clickbait yasak, uydurma istatistik yasak
- Marka sesi: samimi, bilgili, kahve tutkusu yansıtmalı

ÇIKTI FORMATI (sadece JSON, başka hiçbir şey yazma):
{{
  "tr_title": "...",
  "tr_meta": "150-160 karakter meta description (keyword içermeli)",
  "tr_body": "<h1>...</h1><p>...</p>...",
  "en_title": "...",
  "en_meta": "150-160 char meta description (keyword inside)",
  "en_body": "<h1>...</h1><p>...</p>..."
}}"""

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # JSON bloğunu çıkar
    match = re.search(r'\{[\s\S]+\}', raw)
    if not match:
        raise ValueError(f"Claude JSON döndürmedi: {raw[:200]}")
    return json.loads(match.group(0))


# ─── Save output ────────────────────────────────────────────────────────────

def save_output(tr_kw: str, content: dict, tr_id: int, en_id: int) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    today = date.today().isoformat()
    slug = re.sub(r'[^a-z0-9]+', '-', tr_kw.lower())[:40]
    path = OUTPUTS / f"{today}_benesso-blog_{slug}.md"
    path.write_text(
        f"# {content['tr_title']}\n\n"
        f"**TR Shopify ID:** {tr_id}  \n"
        f"**EN Shopify ID:** {en_id}  \n"
        f"**Keyword:** {tr_kw}  \n"
        f"**Date:** {today}\n\n"
        f"---\n\n## TR\n\n{content['tr_body']}\n\n"
        f"---\n\n## EN\n\n{content['en_body']}\n",
        encoding="utf-8",
    )


def log_to_journal(msg: str) -> None:
    JOURNAL.mkdir(exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H%M")
    path = JOURNAL / f"{now}_benesso-blog.md"
    path.write_text(f"# Benesso Blog — {now}\n\n{msg}\n", encoding="utf-8")


# ─── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    if not SHOPIFY_TOKEN:
        print("HATA: SHOPIFY_ACCESS_TOKEN env değişkeni eksik.", file=sys.stderr)
        sys.exit(1)
    if not ANTHROPIC_API_KEY:
        print("HATA: ANTHROPIC_API_KEY env değişkeni eksik.", file=sys.stderr)
        sys.exit(1)

    # Bugün kaç yazı var?
    today_count = count_today_posts()
    if today_count >= DAILY_TARGET:
        print(f"Bugün {today_count} yazı zaten yayınlandı. Hedef tamamlandı.")
        return

    # Kullanılmış keyword'leri yükle
    used = load_published_keywords()

    # Keyword seç
    selected = select_keyword(used)
    if not selected:
        msg = "UYARI: keywords.md boşaldı! İnsan müdahalesi gerekiyor."
        print(msg, file=sys.stderr)
        log_to_journal(msg)
        sys.exit(1)

    tr_kw, en_kw, product_handle, content_type = selected
    print(f"Seçilen keyword: {tr_kw} | {en_kw} | {content_type}")

    # Blog ID al
    blog_id = get_blog_id()
    print(f"Blog ID: {blog_id}")

    # Görsel bul
    image_url = get_product_image(product_handle)
    if not image_url:
        search_term = f"coffee {product_handle.replace('-', ' ')}"
        image_url = get_unsplash_image(search_term)
        if not image_url:
            image_url = get_unsplash_image("specialty coffee")

    print(f"Görsel: {image_url or 'bulunamadı'}")

    # İçerik üret
    print("Claude ile içerik üretiliyor...")
    content = generate_content(tr_kw, en_kw, product_handle, content_type)

    # Türkçe yayınla
    print("TR yayınlanıyor...")
    tr_tags = ["specialty coffee", "kahve", tr_kw.split()[0]]
    tr_id = publish_article(
        blog_id=blog_id,
        title=content["tr_title"],
        body_html=content["tr_body"],
        meta_desc=content["tr_meta"],
        image_url=image_url,
        tags=tr_tags,
        lang="tr",
    )
    print(f"TR yayınlandı → ID: {tr_id}")

    # İngilizce yayınla
    print("EN yayınlanıyor...")
    en_tags = ["specialty coffee", "coffee", en_kw.split()[0]]
    en_id = publish_article(
        blog_id=blog_id,
        title=content["en_title"],
        body_html=content["en_body"],
        meta_desc=content["en_meta"],
        image_url=image_url,
        tags=en_tags,
        lang="en",
    )
    print(f"EN yayınlandı → ID: {en_id}")

    # Log güncelle
    append_to_log(content["tr_title"], content["en_title"], tr_kw, tr_id, en_id)
    save_output(tr_kw, content, tr_id, en_id)

    msg = (
        f"✓ Yayınlandı: {content['tr_title']}\n"
        f"  Keyword: {tr_kw}\n"
        f"  TR ID: {tr_id} | EN ID: {en_id}\n"
        f"  Görsel: {image_url or 'yok'}\n"
        f"  Bugün toplam: {today_count + 1}/{DAILY_TARGET}"
    )
    log_to_journal(msg)
    print(msg)


if __name__ == "__main__":
    main()
