"""
Benesso Coffee — Amazon A+ Content Image Generator
Model: fal-ai/nano-banana-2
"""

import os
import sys
import time
import requests
import fal_client

FAL_KEY = "cfe9e128-eae8-48b6-9f14-26d0e01e0ecb:3378e59f3f07cbb8600e196b0c3b07d7"
os.environ["FAL_KEY"] = FAL_KEY

OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "outputs")

# ---------------------------------------------------------------------------
# BRAND STYLE CORE — applied to every prompt
# ---------------------------------------------------------------------------
STYLE = (
    "premium specialty coffee brand photography, dark moody cinematic lighting, "
    "deep espresso brown and warm cream color palette, gold accents, "
    "ultra sharp focus, 8K commercial product photography, "
    "elegant minimalist composition, no text, no watermark, no logo"
)

# ---------------------------------------------------------------------------
# IMAGE SPECS  (width x height)
# ---------------------------------------------------------------------------
SPECS = {
    "main":    {"width": 1000, "height": 1000},   # 1:1 white bg product
    "hero":    {"width": 1940, "height": 1200},   # A+ hero banner
    "feature": {"width": 800,  "height": 800},    # 3-column feature
    "module":  {"width": 600,  "height": 800},    # image+text portrait
    "divider": {"width": 1940, "height": 600},    # full-width divider
}

# ---------------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "id": "product-1-ethiopia",
        "name": "Ethiopia Guji Washed",
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
        "origin": "Kirinyaga-Karumandi, Mount Kenya slopes, 1610m",
        "process": "fully washed process, SL28 SL34 Batian varieties",
        "tasting": "rosehip, red currant, quince",
        "body": "bright sparkling acidity, wine-like complexity, crisp finish",
        "color_accent": "deep ruby red and forest green",
        "landscape": "Kenyan highland coffee farm on Mount Kenya slopes, lush red-berry coffee cherries",
    },
    {
        "id": "product-3-costa-rica",
        "name": "Costa Rica La Isla Honey",
        "origin": "Naranjo, Western Valley, Costa Rica, 1560m",
        "process": "honey process, Obata variety, Jimenez & Padilla family farm",
        "tasting": "black currant, cocoa, brown sugar",
        "body": "medium body, soft bright acidity, caramel and floral notes",
        "color_accent": "warm honey amber and chocolate brown",
        "landscape": "lush Costa Rican coffee farm, tropical valley with honey-drying raised beds",
    },
]

# ---------------------------------------------------------------------------
# PROMPT TEMPLATES
# ---------------------------------------------------------------------------
def prompts_for(p):
    name = p["name"]
    origin = p["origin"]
    process = p["process"]
    tasting = p["tasting"]
    body = p["body"]
    accent = p["color_accent"]
    landscape = p["landscape"]

    return [
        # 1. MAIN — clean white background product shot
        {
            "key": "main/01_product_white_bg",
            "spec": "main",
            "prompt": (
                f"A single premium specialty coffee bag for '{name}' standing upright, "
                f"centered on pure white background, soft diffused studio lighting, "
                f"matte kraft paper bag with elegant minimal label design, "
                f"slight shadow at base, commercial product photography style, "
                f"{STYLE}"
            ),
            "negative": "text, logo, brand name, watermark, background patterns, props",
        },

        # 2. MAIN — lifestyle product shot (dark bg)
        {
            "key": "main/02_product_dark_lifestyle",
            "spec": "main",
            "prompt": (
                f"Premium specialty coffee bag '{name}' on a dark slate surface, "
                f"dramatic side lighting, steam rising from a small white ceramic espresso cup beside the bag, "
                f"{accent} color tones, depth of field blur in background, "
                f"ultra premium commercial photography, {STYLE}"
            ),
            "negative": "text, watermark, logo, cluttered background",
        },

        # 3. HERO — full-width lifestyle banner
        {
            "key": "hero/03_hero_banner",
            "spec": "hero",
            "prompt": (
                f"Wide cinematic hero banner: {landscape}, "
                f"a single perfect specialty coffee bag in foreground left third, "
                f"sunrise golden light raking across the scene, "
                f"atmospheric mist, {accent} tones dominating, "
                f"vast negative space on right two-thirds for text overlay, "
                f"ultra wide cinematic crop, premium lifestyle coffee brand photography, "
                f"{STYLE}"
            ),
            "negative": "text, watermark, logo, people faces, animals",
        },

        # 4. HERO — origin story banner
        {
            "key": "hero/04_origin_banner",
            "spec": "hero",
            "prompt": (
                f"Wide cinematic banner of {landscape}, "
                f"dramatic golden hour light, mist over the hills, "
                f"coffee cherry clusters in sharp focus foreground, "
                f"vast sky with warm {accent} tones, "
                f"National Geographic quality landscape photography, "
                f"left side available for text overlay, {STYLE}"
            ),
            "negative": "text, watermark, logo, people faces",
        },

        # 5. FEATURE — Tasting notes visual
        {
            "key": "features/05_tasting_notes",
            "spec": "feature",
            "prompt": (
                f"Elegant flat lay arrangement of fresh {tasting} fruits and ingredients "
                f"on a dark slate surface, {accent} color palette, "
                f"artful overhead composition, soft dramatic lighting, "
                f"specialty coffee flavor profile visualization, "
                f"premium food photography, {STYLE}"
            ),
            "negative": "text, watermark, coffee bag, coffee cup",
        },

        # 6. FEATURE — Process / origin close-up
        {
            "key": "features/06_processing_method",
            "spec": "feature",
            "prompt": (
                f"Close-up macro shot of freshly washed green coffee beans drying "
                f"on raised African beds, {landscape} in soft background blur, "
                f"morning dew on the beans, golden light, {accent} tones, "
                f"specialty coffee processing artisan photography, {STYLE}"
            ),
            "negative": "text, watermark, logo",
        },

        # 7. FEATURE — Brew guide visual
        {
            "key": "features/07_brew_guide",
            "spec": "feature",
            "prompt": (
                f"Premium V60 pour-over brewing setup on a dark wooden table, "
                f"slow pour of hot water from a gooseneck kettle, "
                f"steam wisps curling upward, amber coffee flowing through filter, "
                f"{accent} color tones, dark moody side lighting, "
                f"barista coffee brewing artisan photography, {STYLE}"
            ),
            "negative": "text, watermark, logo, people",
        },

        # 8. MODULE — Image+Text portrait (origin story)
        {
            "key": "modules/08_origin_portrait",
            "spec": "module",
            "prompt": (
                f"Tall portrait composition: {landscape} at golden hour, "
                f"coffee cherry branch with ripe red cherries in sharp foreground, "
                f"farm terraces receding into misty background, {accent} color grade, "
                f"cinematic portrait crop, premium origin coffee photography, {STYLE}"
            ),
            "negative": "text, watermark, logo, people faces",
        },

        # 9. MODULE — Image+Text portrait (product in use)
        {
            "key": "modules/09_cup_portrait",
            "spec": "module",
            "prompt": (
                f"Tall portrait: beautiful white ceramic cup filled with perfectly brewed specialty coffee "
                f"on a dark slate slab, coffee bag blurred elegantly in background, "
                f"steam rising, {accent} warm tones, window light from left, "
                f"fine dining coffee service photography, {STYLE}"
            ),
            "negative": "text, watermark, logo, people",
        },

        # 10. DIVIDER — Full-width atmospheric band
        {
            "key": "divider/10_divider_banner",
            "spec": "divider",
            "prompt": (
                f"Ultra wide panoramic divider: extreme close-up of roasted coffee beans "
                f"filling the entire frame, {accent} warm tones, "
                f"dramatic raking side light casting long bean shadows, "
                f"shallow depth of field, center beans in sharp focus, "
                f"dark moody premium texture photography, {STYLE}"
            ),
            "negative": "text, watermark, logo, people",
        },

        # 11. DIVIDER — Landscape panoramic
        {
            "key": "divider/11_landscape_divider",
            "spec": "divider",
            "prompt": (
                f"Ultra wide panoramic landscape: {landscape} at blue hour, "
                f"dramatic sky with {accent} horizon glow, "
                f"vast coffee farm stretching to the horizon, cinematic anamorphic feel, "
                f"premium brand photography banner, {STYLE}"
            ),
            "negative": "text, watermark, logo, people faces",
        },
    ]


# ---------------------------------------------------------------------------
# GENERATION
# ---------------------------------------------------------------------------
def generate_image(prompt_obj, product_id):
    spec_key = prompt_obj["spec"]
    spec = SPECS[spec_key]
    key = prompt_obj["key"]
    out_path = os.path.join(OUTPUT_BASE, product_id, f"{key}.jpg")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if os.path.exists(out_path):
        print(f"  [SKIP] Already exists: {key}")
        return out_path

    print(f"  [GEN]  {product_id} / {key}")
    print(f"         {spec['width']}x{spec['height']}")

    try:
        result = fal_client.run(
            "fal-ai/nano-banana-2",
            arguments={
                "prompt": prompt_obj["prompt"],
                "negative_prompt": prompt_obj.get("negative", ""),
                "image_size": {
                    "width": spec["width"],
                    "height": spec["height"],
                },
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True,
            },
        )

        images = result.get("images", [])
        if not images:
            print(f"  [ERR]  No images returned for {key}")
            return None

        img_url = images[0]["url"]
        img_data = requests.get(img_url, timeout=60).content
        with open(out_path, "wb") as f:
            f.write(img_data)

        print(f"  [OK]   Saved → {out_path}")
        return out_path

    except Exception as e:
        print(f"  [ERR]  {key}: {e}")
        return None


def main():
    print("=" * 60)
    print("BENESSO COFFEE — Amazon Asset Generator")
    print("Model: fal-ai/nano-banana-2")
    print("=" * 60)

    target = sys.argv[1] if len(sys.argv) > 1 else None  # optional: filter by product id

    total = 0
    success = 0

    for product in PRODUCTS:
        if target and target not in product["id"]:
            continue

        print(f"\n{'─'*60}")
        print(f"PRODUCT: {product['name']}")
        print(f"{'─'*60}")

        for prompt_obj in prompts_for(product):
            total += 1
            result = generate_image(prompt_obj, product["id"])
            if result:
                success += 1
            time.sleep(1)  # rate limit courtesy

    print(f"\n{'='*60}")
    print(f"DONE: {success}/{total} images generated")
    print(f"Output folder: {OUTPUT_BASE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
