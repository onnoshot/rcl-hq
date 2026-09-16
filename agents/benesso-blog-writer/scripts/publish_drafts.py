#!/usr/bin/env python3
"""
Hazır taslakları (outputs/*_DRAFT_*.json) Shopify'a yayınla.
Kullanım: python3 publish_drafts.py <SHOPIFY_ACCESS_TOKEN>
"""

import os, json, sys, re, requests
from datetime import datetime, date
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent
OUTPUTS   = AGENT_DIR / "outputs"
PUB_LOG   = AGENT_DIR / "data" / "imports" / "published_log.md"
JOURNAL   = AGENT_DIR.parent.parent / "journal"

SHOPIFY_STORE = "benessocoffee.myshopify.com"
BLOG_HANDLE   = "news"


def shopify_headers(token):
    return {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}


def get_blog_id(token):
    r = requests.get(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs.json",
        headers=shopify_headers(token), timeout=15
    )
    r.raise_for_status()
    for blog in r.json().get("blogs", []):
        if blog.get("handle") == BLOG_HANDLE:
            return blog["id"]
    raise RuntimeError(f"Blog '{BLOG_HANDLE}' bulunamadı. Mevcut bloglar: "
                       + str([b["handle"] for b in r.json().get("blogs", [])]))


def get_image(handle):
    if not handle or handle == "-":
        return None
    try:
        r = requests.get(f"https://benessocoffee.com/products/{handle}.json", timeout=10)
        imgs = r.json().get("product", {}).get("images", [])
        if imgs:
            return imgs[0]["src"]
    except Exception:
        pass
    # Unsplash yedek — token gerektirmiyor (public CDN)
    fallback = {
        "etiyopya": "https://images.unsplash.com/photo-1497515114629-f71d768fd07c?w=1200",
        "kenya":    "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1200",
        "kosta":    "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=1200",
    }
    for key, url in fallback.items():
        if key in (handle or ""):
            return url
    return "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1200"


def publish_article(blog_id, token, title, body_html, meta_desc, image_url, tags):
    payload = {
        "article": {
            "title": title,
            "body_html": body_html,
            "author": "Benesso Coffee",
            "published": True,
            "tags": ", ".join(tags),
            "metafields": [{
                "key": "description_tag",
                "value": meta_desc[:160],
                "type": "single_line_text_field",
                "namespace": "global",
            }],
        }
    }
    if image_url:
        payload["article"]["image"] = {"src": image_url, "alt": title}

    r = requests.post(
        f"https://{SHOPIFY_STORE}/admin/api/2024-01/blogs/{blog_id}/articles.json",
        headers=shopify_headers(token), json=payload, timeout=30
    )
    r.raise_for_status()
    return r.json()["article"]["id"]


def append_log(tr_title, en_title, tr_kw, tr_id, en_id):
    today = date.today().isoformat()
    line = f"{today} | {tr_title} | {en_title} | {tr_kw} | {tr_id} | {en_id}\n"
    with open(PUB_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def log_journal(msg):
    JOURNAL.mkdir(exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H%M")
    (JOURNAL / f"{now}_benesso-blog.md").write_text(
        f"# Benesso Blog — {now}\n\n{msg}\n", encoding="utf-8"
    )


def main():
    if len(sys.argv) < 2:
        print("Kullanım: python3 publish_drafts.py <SHOPIFY_ACCESS_TOKEN>")
        sys.exit(1)

    token = sys.argv[1].strip()

    # Token doğrula
    print("Shopify bağlantısı test ediliyor...")
    try:
        blog_id = get_blog_id(token)
        print(f"✓ Bağlantı başarılı! Blog ID: {blog_id}")
    except requests.HTTPError as e:
        print(f"HATA: Shopify API reddetti → {e.response.text}")
        print("\nDoğru token almak için: Shopify Admin > Settings > Apps > Develop apps")
        sys.exit(1)

    # Taslakları bul
    drafts = sorted(OUTPUTS.glob("*_DRAFT_*.json"))
    if not drafts:
        print("Yayınlanacak taslak bulunamadı (outputs/*_DRAFT_*.json)")
        sys.exit(0)

    print(f"\n{len(drafts)} taslak bulundu. Yayınlanıyor...\n")

    published = []
    for draft_path in drafts:
        data = json.loads(draft_path.read_text(encoding="utf-8"))
        tr_kw = data["tr_keyword"]
        handle = data.get("product_handle", "-")
        image_url = data.get("image_url") or get_image(handle)

        print(f"[{draft_path.name}]")
        print(f"  TR: {data['tr_title']}")

        try:
            tr_id = publish_article(
                blog_id, token,
                data["tr_title"], data["tr_body"], data["tr_meta"],
                image_url, ["specialty coffee", "kahve", tr_kw.split()[0]]
            )
            print(f"  ✓ TR yayınlandı → ID: {tr_id}")

            en_id = publish_article(
                blog_id, token,
                data["en_title"], data["en_body"], data["en_meta"],
                image_url, ["specialty coffee", "coffee", data["en_keyword"].split()[0]]
            )
            print(f"  ✓ EN yayınlandı → ID: {en_id}")

            append_log(data["tr_title"], data["en_title"], tr_kw, tr_id, en_id)
            published.append(draft_path)

            # Taslağı arşivle (DRAFT_ prefix'ini kaldır)
            archived = draft_path.parent / draft_path.name.replace("_DRAFT_", "_published_")
            draft_path.rename(archived)
            print(f"  → Arşivlendi: {archived.name}\n")

        except Exception as e:
            print(f"  HATA: {e}\n")

    msg = f"{len(published)}/{len(drafts)} taslak başarıyla yayınlandı."
    log_journal(msg)
    print(f"\n{'='*50}")
    print(f"✓ {msg}")
    print(f"Blog: https://benessocoffee.com/blogs/news")


if __name__ == "__main__":
    main()
