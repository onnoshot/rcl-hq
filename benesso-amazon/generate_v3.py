"""
Benesso Coffee — Amazon A+ Content Image Generator v3
Model: fal-ai/nano-banana-2/edit
References: /Users/onnoshot/Desktop/design/ (real product box photos)
"""

import os
import sys
import time
import requests
import fal_client

FAL_KEY = "cfe9e128-eae8-48b6-9f14-26d0e01e0ecb:3378e59f3f07cbb8600e196b0c3b07d7"
os.environ["FAL_KEY"] = FAL_KEY

OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "outputs_v3")
DESIGN_DIR = "/Users/onnoshot/Desktop/design"

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
# PRODUCTS — referanslar design klasöründen gerçek kutu fotoları
# Foto6.jpg / Foto7.jpg: 3 kutu stack (Kathakwa üstte, La Isla + Guji altta)
# Foto9.jpg: 3 kutu yan yana marble masada (La Isla sol, Guji orta, Kathakwa sağ)
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "id": "product-1-ethiopia",
        "name": "Ethiopia Guji Washed",
        "ref_images": [
            os.path.join(DESIGN_DIR, "Foto9.jpg"),   # Guji box clearly visible center
            os.path.join(DESIGN_DIR, "Foto6.jpg"),   # stack shot with all 3 boxes
        ],
        "box_desc": "orange-terracotta Benesso box labeled GUJI WASHED ETHIOPIA",
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
            os.path.join(DESIGN_DIR, "Foto6.jpg"),   # Kathakwa clearly on top of stack
            os.path.join(DESIGN_DIR, "Foto9.jpg"),   # all 3 boxes row
        ],
        "box_desc": "dark maroon/wine-red Benesso box labeled KATHAKWA WASHED KENYA",
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
            os.path.join(DESIGN_DIR, "Foto9.jpg"),   # La Isla box on left, marble table
            os.path.join(DESIGN_DIR, "Foto7.jpg"),   # stack shot showing La Isla bottom-left
        ],
        "box_desc": "warm amber-orange Benesso box labeled LA ISLA HONEY COSTA RICA",
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


def get_fal_url(local_path):
    url = fal_client.upload_file(local_path)
    return url


def get_shots(p):
    name = p["name"]
    tasting = p["tasting"]
    accent = p["color_accent"]
    landscape = p["landscape"]
    box = p["box_desc"]

    return [
        # ── MAIN IMAGES ────────────────────────────────────────────────────
        {
            "key": "main/01_white_bg",
            "spec": "main",
            "ref_idx": 0,
            "strength": 0.30,
            "prompt": (
                f"The {box} placed on pure white seamless background, "
                "soft even studio lighting from top-left, box perfectly centered and upright, "
                "slight soft shadow below box, clean commercial product photography, "
                f"preserve all box label details and exact colors, {STYLE}"
            ),
        },
        {
            "key": "main/02_dark_lifestyle",
            "spec": "main",
            "ref_idx": 0,
            "strength": 0.50,
            "prompt": (
                f"The {box} placed on a dark slate surface, "
                f"dramatic single-source side lighting highlighting the box texture, "
                f"a small white ceramic espresso cup beside the box with steam rising, "
                f"{accent} color tones in background bokeh, "
                f"preserve box label design and colors exactly, moody premium product photo, {STYLE}"
            ),
        },
        {
            "key": "main/03_wood_table",
            "spec": "main",
            "ref_idx": 0,
            "strength": 0.50,
            "prompt": (
                f"The {box} upright on a dark walnut wooden table, "
                f"window light from left casting soft shadows, "
                f"scattered fresh whole coffee beans around the base of the box, "
                f"{accent} warm tones, minimal props, preserve all box label details and colors, "
                f"premium lifestyle product photography, {STYLE}"
            ),
        },

        # ── HERO BANNERS ───────────────────────────────────────────────────
        {
            "key": "hero/04_hero_banner",
            "spec": "hero",
            "ref_idx": 1,
            "strength": 0.65,
            "prompt": (
                f"Wide cinematic hero image: {landscape}, "
                f"the {box} prominently placed in foreground left, "
                f"sunrise golden light across the farm, atmospheric mist, "
                f"{accent} dominant palette, vast sky on the right two-thirds, "
                f"preserve box label design and colors exactly, premium coffee brand hero photography, {STYLE}"
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
                f"the {box} resting on stone in foreground corner, "
                f"dramatic sky with {accent} tones, "
                f"preserve box colors and label, National Geographic quality, {STYLE}"
            ),
        },

        # ── FEATURE IMAGES ─────────────────────────────────────────────────
        {
            "key": "features/06_tasting_notes",
            "spec": "feature",
            "ref_idx": 0,
            "strength": 0.75,
            "prompt": (
                f"Elegant dark flat lay: fresh {tasting} fruits arranged artfully "
                f"on dark slate next to the {box}, "
                f"{accent} color palette, overhead square composition, "
                f"soft dramatic studio lighting, specialty coffee flavor visualization, "
                f"preserve box label details, premium food photography, {STYLE}"
            ),
        },
        {
            "key": "features/07_process",
            "spec": "feature",
            "ref_idx": 1,
            "strength": 0.70,
            "prompt": (
                f"Close-up square: freshly processed coffee beans drying on raised beds, "
                f"{landscape} soft blur in background, "
                f"the {box} placed on the drying table corner, "
                f"morning golden light, {accent} tones, "
                f"preserve box label exactly, artisan coffee processing photography, {STYLE}"
            ),
        },
        {
            "key": "features/08_brew_guide",
            "spec": "feature",
            "ref_idx": 0,
            "strength": 0.70,
            "prompt": (
                f"Square: V60 pour-over setup on dark wooden surface, "
                f"gooseneck kettle pouring, steam wisps, amber coffee flowing, "
                f"the {box} in soft background, "
                f"{accent} tones, dark moody lighting, "
                f"preserve box label details, barista artisan photography, {STYLE}"
            ),
        },

        # ── MODULE PORTRAITS ───────────────────────────────────────────────
        {
            "key": "modules/09_origin_portrait",
            "spec": "module",
            "ref_idx": 1,
            "strength": 0.65,
            "prompt": (
                f"Tall portrait: {landscape} at golden hour, "
                f"coffee cherry branch with ripe cherries sharp in foreground, "
                f"the {box} leaning against natural stone, "
                f"{accent} color grade, cinematic portrait crop, "
                f"preserve box label, premium origin story photography, {STYLE}"
            ),
        },
        {
            "key": "modules/10_cup_portrait",
            "spec": "module",
            "ref_idx": 0,
            "strength": 0.60,
            "prompt": (
                f"Tall portrait: white ceramic cup of specialty coffee on dark slate, "
                f"steam rising, the {box} blurred elegantly behind, "
                f"{accent} warm tones, soft window light from left, "
                f"preserve box label visible, fine dining coffee photography, {STYLE}"
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
                f"center beans sharp, the {box} corner visible right edge, "
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
                f"vast coffee farm to horizon, the {box} "
                f"silhouetted in extreme left corner, "
                f"cinematic anamorphic crop, {STYLE}"
            ),
        },
    ]


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


def main():
    print("=" * 65)
    print("BENESSO COFFEE — Amazon Asset Generator v3 (Design Refs)")
    print("Model: fal-ai/nano-banana-2/edit")
    print(f"Refs:  {DESIGN_DIR}")
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

        # Upload reference images directly to fal
        print("\n[1/2] Uploading design references to fal.ai...")
        fal_urls = []
        for local_path in product["ref_images"]:
            if not os.path.exists(local_path):
                print(f"  [ERR]  Not found: {local_path}")
                continue
            try:
                url = get_fal_url(local_path)
                fal_urls.append(url)
                print(f"  [UP]   {os.path.basename(local_path)} → {url[:60]}...")
            except Exception as e:
                print(f"  [ERR]  Upload failed: {e}")

        if not fal_urls:
            print("  [ERR] No fal URLs — skipping product")
            continue

        print(f"\n[2/2] Generating {len(get_shots(product))} images...")
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
