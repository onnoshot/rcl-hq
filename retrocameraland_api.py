#!/usr/bin/env python3
"""
retrocameraland API helper — import this in daily cron scripts.
Usage:
  from retrocameraland_api import generate_image, publish_article
"""

import urllib.request, urllib.error, json, time, sys

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"
BLOG_ID       = "91197866123"
FAL_KEY       = "65067257-e286-49f2-aa12-4318001c2999:8c8bf90fa5a185945f52f4cb1f978580"

SOCIAL_BLOCK = """<div style="background:#f8f4f0;border-left:4px solid #c8a882;padding:20px 24px;margin:40px 0;border-radius:0 8px 8px 0;">
<p style="margin:0 0 12px 0;font-weight:700;font-size:16px;">📸 Retrocameraland'i Takip Edin</p>
<p style="margin:0;line-height:2;">
📷 <a href="https://www.instagram.com/retrocameraland/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Instagram">Instagram</a> &nbsp;|&nbsp;
▶️ <a href="https://www.youtube.com/@RetroCameraLand?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Youtube">YouTube</a> &nbsp;|&nbsp;
🎵 <a href="https://www.tiktok.com/@retrocameraland?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Tiktok">TikTok</a> &nbsp;|&nbsp;
📌 <a href="https://pinterest.com/retrocameraland/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Pinterest">Pinterest</a> &nbsp;|&nbsp;
💼 <a href="https://www.linkedin.com/company/retro-camera-land/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=linkedin">LinkedIn</a>
</p>
</div>"""

CTA_BLOCK = """<div style="text-align:center;margin:48px 0;"><a href="https://retrocameraland.com/collections/all" style="background:#1a1a1a;color:#fff;padding:16px 36px;border-radius:6px;text-decoration:none;font-weight:700;font-size:17px;">🛒 Tüm Koleksiyonu Gör →</a></div>"""


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fal_generate_image(prompt):
    url  = "https://fal.run/fal-ai/nano-banana-2"
    data = json.dumps({"prompt": prompt, "image_size": "landscape_4_3",
                        "num_inference_steps": 28, "guidance_scale": 7.5,
                        "num_images": 1}).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Key {FAL_KEY}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
    images = result.get("images") or result.get("image") or []
    if isinstance(images, dict): images = [images]
    img = images[0] if images else {}
    return img.get("url") or img.get("image_url") or (img if isinstance(img, str) else None)


def shopify(method, path, body=None):
    url  = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Shopify {method} {path} → {e.code}: {e.read().decode()[:300]}")


def publish_article(title, handle, tags, body_html, meta_desc, image_prompt, image_filename):
    """Generate image + publish article. Returns (article_id, handle)."""
    log(f"  Görsel: {image_prompt[:55]}...")
    img_url = fal_generate_image(image_prompt)
    if not img_url:
        raise ValueError("Fal görsel URL boş döndü")
    log(f"  → {img_url[:70]}")

    full_html = body_html + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    resp = shopify("POST", f"blogs/{BLOG_ID}/articles.json", {
        "article": {
            "title": title,
            "body_html": full_html,
            "handle": handle,
            "tags": tags,
            "published": True,
            "image": {"src": img_url, "alt": title},
            "metafields": [
                {"namespace": "seo", "key": "description", "value": meta_desc, "type": "single_line_text_field"},
                {"namespace": "seo", "key": "title",       "value": title,    "type": "single_line_text_field"}
            ]
        }
    })
    art = resp["article"]
    log(f"  ✅ ID:{art['id']} → {art['handle']}")
    return art["id"], art["handle"]
