#!/usr/bin/env python3
"""Crop a horizontal video to a vertical frame, holding a stable crop per shot
(sub-scene) so the frame never jitters — it only repositions at cut points,
snapping to whichever person/shot is on screen."""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
FACE_MODEL = SCRIPT_DIR.parent / "models" / "face_detection_yunet.onnx"

DETECT_WIDTH = 480          # downscale width used only for face detection speed
TARGET_FACE_FRACTION = 0.30 # face bbox height as a fraction of the crop height (bigger = tighter zoom)
MIN_CROP_FRACTION = 0.32    # never crop tighter than this fraction of source height (avoid extreme zoom)
FACE_VERTICAL_BIAS = 0.38   # face center sits at this fraction down from top of crop (headroom for shoulders)
SHOT_SAMPLE_INTERVAL = 0.4  # seconds between face samples used to find a shot's stable crop
MIN_SHOT_DURATION = 1.0     # shots shorter than this are merged into a neighbor (avoids spurious micro-cuts)


def pick_best_face(faces, prev_cx, prev_cy, scale):
    if faces is None or len(faces) == 0:
        return None
    best = None
    best_score = -1
    for f in faces:
        x, y, w, h, *_ = f
        x, y, w, h = x / scale, y / scale, w / scale, h / scale
        area = w * h
        cx, cy = x + w / 2, y + h / 2
        dist = np.hypot(cx - prev_cx, cy - prev_cy)
        score = area - dist * 50
        if score > best_score:
            best_score = score
            best = (x, y, w, h)
    return best


def detect_face(cap, detector, t, source_w, source_h, prev_cx, prev_cy):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    if not ok:
        return None
    scale = DETECT_WIDTH / source_w
    detect_h = int(source_h * scale)
    small = cv2.resize(frame, (DETECT_WIDTH, detect_h))
    detector.setInputSize((DETECT_WIDTH, detect_h))
    _, faces = detector.detect(small)
    return pick_best_face(faces, prev_cx, prev_cy, scale)


def build_shots(start, end, shot_boundaries):
    if not shot_boundaries:
        return [(start, end)]
    cuts = sorted(b for b in shot_boundaries if start < b < end)
    points = [start] + cuts + [end]
    shots = list(zip(points[:-1], points[1:]))

    merged = []
    for s_start, s_end in shots:
        if merged and s_end - s_start < MIN_SHOT_DURATION:
            prev_start, _ = merged[-1]
            merged[-1] = (prev_start, s_end)
        else:
            merged.append((s_start, s_end))
    if len(merged) > 1 and merged[0][1] - merged[0][0] < MIN_SHOT_DURATION:
        second_start, second_end = merged[1]
        merged[0] = (merged[0][0], second_end)
        del merged[1]
    return merged


def compute_shot_crop(cap, detector, shot_start, shot_end, source_w, source_h, target_aspect):
    samples = []
    prev_cx, prev_cy = source_w / 2, source_h / 2
    t = shot_start
    while t < shot_end:
        face = detect_face(cap, detector, t, source_w, source_h, prev_cx, prev_cy)
        if face is not None:
            fx, fy, fw, fh = face
            prev_cx, prev_cy = fx + fw / 2, fy + fh / 2
            samples.append((prev_cx, prev_cy, fh))
        t += SHOT_SAMPLE_INTERVAL

    if not samples:
        crop_h = source_h
        crop_w = min(crop_h * target_aspect, source_w)
        crop_h = crop_w / target_aspect
        cx, cy = source_w / 2, source_h / 2
    else:
        med_cx = float(np.median([s[0] for s in samples]))
        med_cy = float(np.median([s[1] for s in samples]))
        med_fh = float(np.median([s[2] for s in samples]))
        crop_h = np.clip(med_fh / TARGET_FACE_FRACTION, source_h * MIN_CROP_FRACTION, source_h)
        crop_w = crop_h * target_aspect
        if crop_w > source_w:
            crop_w = source_w
            crop_h = crop_w / target_aspect
        cx = med_cx
        cy = med_cy - (FACE_VERTICAL_BIAS - 0.5) * crop_h

    cx = np.clip(cx, crop_w / 2, source_w - crop_w / 2)
    cy = np.clip(cy, crop_h / 2, source_h - crop_h / 2)
    return int(cx - crop_w / 2), int(cy - crop_h / 2), int(crop_w), int(crop_h)


def reframe(input_path, output_path, start=None, end=None,
            target_w=2160, target_h=3840, shot_boundaries=None, crf=18, preset="medium"):
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Video acilamadi: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    source_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start = start or 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_source = total_frames / fps
    end = min(end if end is not None else duration_source, duration_source)

    detector = cv2.FaceDetectorYN_create(str(FACE_MODEL), "", (320, 320))
    target_aspect = target_w / target_h

    shots = build_shots(start, end, shot_boundaries)
    print(f"  {len(shots)} alt-sahne icin sabit kadraj hesaplaniyor...", file=sys.stderr)
    shot_crops = [
        (s_start, s_end, compute_shot_crop(cap, detector, s_start, s_end, source_w, source_h, target_aspect))
        for s_start, s_end in shots
    ]

    n_frames = int((end - start) * fps)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{target_w}x{target_h}", "-r", str(fps), "-i", "-",
        "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(input_path),
        "-map", "0:v:0", "-map", "1:a:0?",
        "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    processed = 0
    shot_idx = 0
    try:
        while processed < n_frames:
            ok, frame = cap.read()
            if not ok:
                break
            t = start + processed / fps
            while shot_idx < len(shot_crops) - 1 and t >= shot_crops[shot_idx][1]:
                shot_idx += 1
            x0, y0, cw, ch = shot_crops[shot_idx][2]
            crop = frame[y0:y0 + ch, x0:x0 + cw]
            resized = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            proc.stdin.write(resized.tobytes())

            processed += 1
            if processed % (int(fps) * 5) == 0:
                print(f"  {processed / n_frames * 100:.0f}%", file=sys.stderr)
    finally:
        cap.release()
        proc.stdin.close()
        proc.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Source video path")
    parser.add_argument("output", help="Output vertical video path")
    parser.add_argument("--start", type=float, default=None)
    parser.add_argument("--end", type=float, default=None)
    parser.add_argument("--width", type=int, default=2160)
    parser.add_argument("--height", type=int, default=3840)
    args = parser.parse_args()

    if not FACE_MODEL.exists():
        print(f"Yuz modeli bulunamadi: {FACE_MODEL}", file=sys.stderr)
        sys.exit(1)

    print(f"Isleniyor: {args.input} [{args.start}-{args.end}]", file=sys.stderr)
    reframe(args.input, args.output, args.start, args.end, args.width, args.height)
    print(f"Tamamlandi: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
