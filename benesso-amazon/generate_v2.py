"""
Benesso Coffee — Amazon A+ Content Image Generator v2
Model: fal-ai/nano-banana-2/edit (image-to-image with real product reference)
"""

import os
import sys
import time
import requests
import fal_client

FAL_KEY = "cfe9e128-eae8-48b6-9f14-26d0e01e0ecb:3378e59f3f07cbb8600e196b0c3b07d7"
os.environ["FAL_KEY"] = FAL_KEY

OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "outputs")
REF_DIR = os.path.join(os.path.dirname(__file__), "references")
os.makedirs(REF_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# BRAND STYLE CORE
# ---------------------------------------------------------------------------
STYLE = (
    "premium specialty coffee brand photography, dark moody cinematic lighting, "
    "deep espresso brown and warm cream color palette, gold accents, "
    "ultra sharp focus, 8K commercial product photography, "
    "elegant minimalist composition, no text, no watermark, no logo"
)

# ---------------------------------------------------------------------------
# PRODUCTS + THEIR REFERENCE IMAGE URLS
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "id": "product-1-ethiopia",
        "name": "Ethiopia Guji Washed",
        "ref_images": [
            "https://www.benessocoffee.com/cdn/shop/files/IMG_8043.jpg?v=1775585637",
            "https://www.benessocoffee.com/cdn/shop/files/guji_w3_b21c2479-efc3-4e5c-b3ba-baa05cc5b288.jpg?v=1775589887",
            "https://www.benessocoffee.com/cdn/shop/files/guji_w2_c57c8bf4-b404-4447-9966-122d54a6d674.jpg?v=1776108941",
            "https://www.benessocoffee.com/cdn/shop/files/guji_w1_6fe4ae79-cb54-41aa-9cd5-83c991fd5aac.jpg?v=1775589887",
        ],
        "origin": "Guji region, Ethiopia, 1950–2050m altitude",
        "process": "fully washed process",
        "tasting": "apricot, walnut, sugarcane sweetness",
        "body": "silky elegant body, soft vibrant acidity, crystal clean cup",
        "color_accent": "warm golden amber and deep terracotta",
        "landscape": "Ethiopian highland coffee forest, misty green terraced farms at high altitude",
    },
    {
        "id": "product-2-kenya",
        "name": "Kenya Kathakwa Washed",
        "ref_images": [
            "https://www.benessocoffee.com/cdn/shop/files/IMG_8042.jpg?v=1775585499",
            "https://www.benessocoffee.com/cdn/shop/files/katwa3.jpg?v=1775592261",
        ],
        "origin": "Kirinyaga-Karumandi, Mount Kenya slopes, 1610m",
        "process": "fully washed, SL28 SL34 Batian varieties",
        "tasting": "rosehip, red currant, quince",
        "body": "bright sparkling acidity, wine-like complexity, crisp finish",
        "color_accent": "deep ruby red and forest green",
        "landscape": "Kenyan highland coffee farm on Mount Kenya slopes, lush red-berry coffee cherries",
    },
    {
        "id": "product-3-costa-rica",
        "name": "Costa Rica La Isla Honey",
        "ref_images": [
            "https://www.benessocoffee.com/cdn/shop/files/IMG_8044.jpg?v=1775585361",
            "https://www.benessocoffee.com/cdn/shop/files/laislaa_honey.jpg?v=1775592760",
        ],
        "origin": "Naranjo, Western Valley, Costa Rica, 1560m",
        "process": "honey process, Obata variety",
        "tasting": "black currant, cocoa, brown sugar",
        "body": "medium body, soft bright acidity, caramel and floral notes",
        "color_accent": "warm honey amber and chocolate brown",
        "landscape": "lush Costa Rican coffee farm, tropical valley with honey-drying raised beds",
    },
]

# ---------------------------------------------------------------------------
# IMAGE SIZE SPECS
# ---------------------------------------------------------------------------
SPECS = {
    "main":    {"width": 1000, "height": 1000},
    "hero":    {"width": 1920, "height": 1080},
    "feature": {"width": 800,  "height": 800},
    "module":  {"width": 600,  "height": 800},
    "divider": {"width": 1920, "height": 600},
}

# ---------------------------------------------------------------------------
# DOWNLOAD REFERENCE IMAGE → upload to fal → get CDN URL
# ---------------------------------------------------------------------------
def get_fal_url(local_path):
    """Upload a local image to fal storage and return its CDN URL."""
    url = fal_client.upload_file(local_path)
    return url


def download_reference(url, dest_path):
    if os.path.exists(dest_path):
        return dest_path
    print(f"  [DL]   {url}")
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(r.content)
        print(f"  [OK]   → {dest_path}")
        return dest_path
    except Exception as e:
        print(f"  [ERR]  Download failed: {e}")
        return None


# ---------------------------------------------------------------------------
# PROMPT SETS — each takes the real product image as reference
# ---------------------------------------------------------------------------
def get_shots(p):
    name = p["name"]
    tasting = p["tasting"]
    accent = p["color_accent"]
    landscape = p["landscape"]

    # Which ref image index to use per shot
    return [
        # ── MAIN IMAGES ────────────────────────────────────────────────────
        {
            "key": "main/01_white_bg",
            "spec": "main",
            "ref_idx": 0,   # primary product shot
            "strength": 0.35,
            "prompt": (
                "Exact same coffee bag product, placed on pure white seamless background, "
                "soft even studio lighting from top-left, bag perfectly centered and upright, "
                "slight soft shadow below bag, clean commercial product photography, "
                "preserve all bag label details and colors exactly, "
                f"{STYLE}"
            ),
        },
        {
            "key": "main/02_dark_lifestyle",
            "spec": "main",
            "ref_idx": 0,
            "strength": 0.55,
            "prompt": (
                f"The exact same Benesso coffee bag placed on a dark slate surface, "
                f"dramatic single-source side lighting highlighting the bag texture, "
                f"a small white ceramic espresso cup beside the bag with steam rising, "
                f"{accent} color tones in background bokeh, "
                f"preserve bag label design exactly, moody premium product photo, {STYLE}"
            ),
        },
        {
            "key": "main/03_wood_table",
            "spec": "main",
            "ref_idx": 0,
            "strength": 0.55,
            "prompt": (
                f"The same Benesso coffee bag upright on a dark walnut wooden table, "
                f"window light from left casting soft shadows, "
                f"scattered fresh whole coffee beans around the base of the bag, "
                f"{accent} warm tones, minimal props, preserve all bag label details, "
                f"premium lifestyle product photography, {STYLE}"
            ),
        },

        # ── HERO BANNERS ───────────────────────────────────────────────────
        {
            "key": "hero/04_hero_banner",
            "spec": "hero",
            "ref_idx": 1,   # use lifestyle/secondary shot
            "strength": 0.65,
            "prompt": (
                f"Wide cinematic hero image: {landscape}, "
                f"the same Benesso coffee bag prominently placed in foreground left, "
                f"sunrise golden light across the farm, atmospheric mist, "
                f"{accent} dominant palette, vast sky on the right two-thirds, "
                f"preserve bag label design exactly, premium coffee brand hero photography, {STYLE}"
            ),
        },
        {
            "key": "hero/05_origin_story",
            "spec": "hero",
            "ref_idx": 1,
            "strength": 0.70,
            "prompt": (
                f"Wide panoramic: {landscape} at golden hour, "
                f"coffee cherry clusters sharp in foreground, farm terraces in background, "
                f"the same Benesso coffee bag resting on stone in foreground corner, "
                f"dramatic sky with {accent} tones, "
                f"preserve bag colors and label, National Geographic quality, {STYLE}"
            ),
        },

        # ── 3-COLUMN FEATURE IMAGES ────────────────────────────────────────
        {
            "key": "features/06_tasting_notes",
            "spec": "feature",
            "ref_idx": 0,
            "strength": 0.80,
            "prompt": (
                f"Elegant dark flat lay: fresh {tasting} fruits arranged artfully "
                f"on dark slate next to the same Benesso coffee bag, "
                f"{accent} color palette, overhead square composition, "
                f"soft dramatic studio lighting, specialty coffee flavor visualization, "
                f"preserve bag label details, premium food photography, {STYLE}"
            ),
        },
        {
            "key": "features/07_process",
            "spec": "feature",
            "ref_idx": 1,
            "strength": 0.75,
            "prompt": (
                f"Close-up square composition: freshly processed coffee beans drying "
                f"on raised beds, {landscape} soft blur in background, "
                f"the same Benesso coffee bag placed on the drying table corner, "
                f"morning golden light, {accent} tones, "
                f"preserve bag label exactly, artisan coffee processing photography, {STYLE}"
            ),
        },
        {
            "key": "features/08_brew_guide",
            "spec": "feature",
            "ref_idx": 0,
            "strength": 0.75,
            "prompt": (
                f"Square composition: V60 pour-over setup on dark wooden surface, "
                f"gooseneck kettle pouring, steam wisps, amber coffee flowing, "
                f"the same Benesso coffee bag in soft background, "
                f"{accent} tones, dark moody lighting, "
                f"preserve bag label details, barista artisan photography, {STYLE}"
            ),
        },

        # ── MODULE PORTRAITS ───────────────────────────────────────────────
        {
            "key": "modules/09_origin_portrait",
            "spec": "module",
            "ref_idx": 1,
            "strength": 0.70,
            "prompt": (
                f"Tall portrait: {landscape} at golden hour, "
                f"coffee cherry branch with ripe cherries sharp in foreground, "
                f"the same Benesso coffee bag leaning against natural stone, "
                f"{accent} color grade, cinematic portrait crop, "
                f"preserve bag label, premium origin story photography, {STYLE}"
            ),
        },
        {
            "key": "modules/10_cup_portrait",
            "spec": "module",
            "ref_idx": 0,
            "strength": 0.65,
            "prompt": (
                f"Tall portrait: white ceramic cup of specialty coffee on dark slate, "
                f"steam rising, the same Benesso coffee bag blurred elegantly behind, "
                f"{accent} warm tones, soft window light from left, "
                f"preserve bag label visible, fine dining coffee photography, {STYLE}"
            ),
        },

        # ── DIVIDER BANNERS ────────────────────────────────────────────────
        {
            "key": "divider/11_beans_divider",
            "spec": "divider",
            "ref_idx": 0,
            "strength": 0.80,
            "prompt": (
                f"Ultra wide panoramic: extreme close-up of roasted coffee beans "
                f"filling entire frame, {accent} warm tones, "
                f"dramatic raking side light, shallow depth of field, "
                f"center beans sharp, the same Benesso coffee bag corner visible right edge, "
                f"dark moody premium texture photography, {STYLE}"
            ),
        },
        {
            "key": "divider/12_landscape_divider",
            "spec": "divider",
            "ref_idx": 1,
            "strength": 0.75,
            "prompt": (
                f"Ultra wide panoramic: {landscape} at blue hour, "
                f"dramatic sky with {accent} horizon glow, "
                f"vast coffee farm to horizon, the same Benesso coffee bag "
                f"silhouetted in extreme left corner, "
                f"preserve bag silhouette shape, cinematic anamorphic crop, {STYLE}"
            ),
        },
    ]


# ---------------------------------------------------------------------------
# GENERATE ONE IMAGE VIA EDIT ENDPOINT
# ---------------------------------------------------------------------------
def generate_image(shot, product_id, fal_ref_urls):
    spec = SPECS[shot["spec"]]
    key = shot["key"]
    out_path = os.path.join(OUTPUT_BASE, product_id, f"{key}.jpg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if os.path.exists(out_path):
        print(f"  [SKIP] {key}")
        return out_path

    ref_idx = min(shot["ref_idx"], len(fal_ref_urls) - 1)
    image_url = fal_ref_urls[ref_idx]

    print(f"\n  [GEN]  {product_id} / {key}")
    print(f"         size={spec['width']}x{spec['height']}  strength={shot['strength']}")
    print(f"         ref=image[{ref_idx}]")

    try:
        result = fal_client.run(
            "fal-ai/nano-banana-2/edit",
            arguments={
                "prompt": shot["prompt"],
                "image_urls": [image_url],
                "strength": shot["strength"],
                "image_size": {
                    "width": spec["width"],
                    "height": spec["height"],
                },
                "num_inference_steps": 30,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True,
            },
        )

        images = result.get("images", [])
        if not images:
            print(f"  [ERR]  No images returned")
            return None

        img_data = requests.get(images[0]["url"], timeout=60).content
        with open(out_path, "wb") as f:
            f.write(img_data)

        size_kb = len(img_data) // 1024
        print(f"  [OK]   Saved {size_kb}KB → {out_path}")
        return out_path

    except Exception as e:
        print(f"  [ERR]  {key}: {e}")
        return None


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 65)
    print("BENESSO COFFEE — Amazon Asset Generator v2 (Image-to-Image)")
    print("Model: fal-ai/nano-banana-2/edit")
    print("=" * 65)

    target = sys.argv[1] if len(sys.argv) > 1 else None

    total = 0
    success = 0

    for product in PRODUCTS:
        if target and target not in product["id"]:
            continue

        print(f"\n{'─'*65}")
        print(f"PRODUCT: {product['name']}")
        print(f"{'─'*65}")

        # ── Step 1: Download reference images locally ──────────────────────
        print("\n[1/3] Downloading reference images...")
        local_refs = []
        for i, url in enumerate(product["ref_images"]):
            ext = "jpg" if ".jpg" in url else "png"
            dest = os.path.join(REF_DIR, f"{product['id']}_ref_{i}.{ext}")
            path = download_reference(url, dest)
            if path:
                local_refs.append(path)

        if not local_refs:
            print("  [ERR] No reference images — skipping product")
            continue

        # ── Step 2: Upload references to fal CDN ──────────────────────────
        print("\n[2/3] Uploading references to fal.ai...")
        fal_urls = []
        for lp in local_refs:
            try:
                url = get_fal_url(lp)
                fal_urls.append(url)
                print(f"  [UP]   {os.path.basename(lp)} → {url[:60]}...")
            except Exception as e:
                print(f"  [ERR]  Upload failed: {e}")

        if not fal_urls:
            print("  [ERR] No fal URLs — skipping product")
            continue

        # ── Step 3: Generate all shots ─────────────────────────────────────
        print(f"\n[3/3] Generating {len(get_shots(product))} images...")
        for shot in get_shots(product):
            total += 1
            r = generate_image(shot, product["id"], fal_urls)
            if r:
                success += 1
            time.sleep(1.5)

    print(f"\n{'='*65}")
    print(f"DONE: {success}/{total} images generated successfully")
    print(f"Output: {OUTPUT_BASE}/")
    print("=" * 65)


if __name__ == "__main__":
    main()
