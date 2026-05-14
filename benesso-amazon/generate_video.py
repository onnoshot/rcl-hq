"""
Benesso Coffee — Amazon Video Generator
Model: fal-ai/kling-video/v1.6/pro/image-to-video
Refs:  /Users/onnoshot/Desktop/design/
Specs: 1920x1080, 16:9, H.264 uyumlu
"""

import os
import sys
import requests
import fal_client

FAL_KEY = "cfe9e128-eae8-48b6-9f14-26d0e01e0ecb:3378e59f3f07cbb8600e196b0c3b07d7"
os.environ["FAL_KEY"] = FAL_KEY

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs_video")
DESIGN_DIR = "/Users/onnoshot/Desktop/design"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# VIDEO SHOTS — her biri bir design görseli baz alır
# ---------------------------------------------------------------------------
SHOTS = [
    {
        "id": "01_all_boxes_reveal",
        "image": "Foto9.jpg",   # 3 kutu yan yana, marble masa
        "prompt": (
            "Slow cinematic camera pull back revealing three premium specialty coffee boxes "
            "on a marble table, warm soft studio lighting, subtle depth of field, "
            "boxes remain perfectly still and sharp, elegant luxury product reveal, "
            "no text appearing, no extra objects, dark moody background"
        ),
        "duration": "10",
        "aspect_ratio": "16:9",
    },
    {
        "id": "02_stack_zoom",
        "image": "Foto6.jpg",   # 3 kutu üst üste
        "prompt": (
            "Slow gentle zoom in toward the stacked Benesso coffee boxes, "
            "warm cinematic lighting with subtle bokeh in background, "
            "boxes stay perfectly sharp and still, premium product atmosphere, "
            "dark moody roastery background, no text, luxury coffee brand feel"
        ),
        "duration": "10",
        "aspect_ratio": "16:9",
    },
    {
        "id": "03_passport_cinematic",
        "image": "Foto7.jpg",   # EVERY CUP HAS A PASSPORT görseli
        "prompt": (
            "Cinematic slow orbit around the three stacked coffee boxes, "
            "warm moody roastery lighting, subtle camera drift from left to right, "
            "boxes remain sharp, premium specialty coffee brand atmosphere, "
            "dark background with soft bokeh, no additional text or overlays"
        ),
        "duration": "10",
        "aspect_ratio": "16:9",
    },
]


def generate_shot(shot):
    image_path = os.path.join(DESIGN_DIR, shot["image"])
    out_path = os.path.join(OUTPUT_DIR, f"{shot['id']}.mp4")

    if os.path.exists(out_path):
        print(f"  [SKIP] {shot['id']}")
        return out_path

    if not os.path.exists(image_path):
        print(f"  [ERR]  Image not found: {image_path}")
        return None

    print(f"\n  [UP]   Uploading {shot['image']}...")
    image_url = fal_client.upload_file(image_path)
    print(f"         → {image_url[:60]}...")

    print(f"  [GEN]  {shot['id']} ({shot['duration']}s, {shot['aspect_ratio']})...")

    try:
        result = fal_client.run(
            "fal-ai/kling-video/v1.6/pro/image-to-video",
            arguments={
                "prompt": shot["prompt"],
                "image_url": image_url,
                "duration": shot["duration"],
                "aspect_ratio": shot["aspect_ratio"],
            },
        )

        video = result.get("video", {})
        video_url = video.get("url") if isinstance(video, dict) else None

        if not video_url:
            print(f"  [ERR]  No video URL in response: {result}")
            return None

        print(f"  [DL]   Downloading video...")
        video_data = requests.get(video_url, timeout=120).content
        with open(out_path, "wb") as f:
            f.write(video_data)

        size_mb = len(video_data) / (1024 * 1024)
        print(f"  [OK]   Saved {size_mb:.1f}MB → {out_path}")
        return out_path

    except Exception as e:
        print(f"  [ERR]  {shot['id']}: {e}")
        return None


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 65)
    print("BENESSO COFFEE — Amazon Video Generator")
    print("Model: fal-ai/kling-video/v1.6/pro/image-to-video")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 65)

    total = 0
    success = 0

    for shot in SHOTS:
        if target and target not in shot["id"]:
            continue
        total += 1
        r = generate_shot(shot)
        if r:
            success += 1

    print(f"\n{'='*65}")
    print(f"DONE: {success}/{total} videos generated")
    print(f"Output: {OUTPUT_DIR}/")
    print("=" * 65)


if __name__ == "__main__":
    main()
