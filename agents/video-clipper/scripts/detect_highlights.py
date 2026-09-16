#!/usr/bin/env python3
"""Find candidate highlight windows in a video: scene-cut aligned, speech-heavy, face-visible."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

SCRIPT_DIR = Path(__file__).resolve().parent
FACE_MODEL = SCRIPT_DIR.parent / "models" / "face_detection_yunet.onnx"
CACHE_DIR = SCRIPT_DIR.parent / ".cache"


def analyze_video(video_path):
    """Scene boundaries, silence intervals, and face timeline for a video —
    the expensive full-video passes. Cached by path+size+mtime since these
    never change unless the source file does, so re-tuning candidate filters
    (min/max duration, face threshold, etc.) doesn't require redoing this."""
    video_path = Path(video_path)
    stat = video_path.stat()
    key = hashlib.sha1(f"{video_path.resolve()}:{stat.st_size}:{stat.st_mtime}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"{key}.json"

    if cache_file.exists():
        print(f"Onbellekten yukleniyor: {cache_file.name}", file=sys.stderr)
        data = json.loads(cache_file.read_text())
        return data["boundaries"], [tuple(x) for x in data["silence_intervals"]], \
            [tuple(x) for x in data["face_timeline"]]

    print("Sahne kesimleri bulunuyor...", file=sys.stderr)
    boundaries = get_scene_boundaries(str(video_path))
    print(f"{len(boundaries) - 1} sahne bulundu.", file=sys.stderr)

    print("Sessizlik/konusma araligi analiz ediliyor...", file=sys.stderr)
    silence_intervals = get_silence_intervals(video_path)

    print("Yuz zaman cizelgesi cikariliyor (tek gecis)...", file=sys.stderr)
    face_timeline = compute_face_timeline(video_path)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({
        "boundaries": boundaries,
        "silence_intervals": silence_intervals,
        "face_timeline": face_timeline,
    }))
    return boundaries, silence_intervals, face_timeline


def get_scene_boundaries(video_path, threshold=27.0):
    video = open_video(video_path)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    manager.detect_scenes(video)
    scenes = manager.get_scene_list()
    if not scenes:
        return [0.0, video.duration.seconds]
    boundaries = [scenes[0][0].get_seconds()]
    for start, end in scenes:
        boundaries.append(end.get_seconds())
    return boundaries


def get_silence_intervals(video_path, noise_db="-30dB", min_silence=0.5):
    cmd = [
        "ffmpeg", "-i", str(video_path), "-vn", "-af",
        f"silencedetect=noise={noise_db}:d={min_silence}", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", result.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", result.stderr)]
    return list(zip(starts, ends))


def speech_coverage(start, end, silence_intervals):
    duration = end - start
    if duration <= 0:
        return 0.0
    silent = 0.0
    for s_start, s_end in silence_intervals:
        overlap = min(end, s_end) - max(start, s_start)
        if overlap > 0:
            silent += overlap
    return max(0.0, 1.0 - silent / duration)


def compute_face_timeline(video_path, interval=2.0):
    """Single pass over the video: sample one frame every `interval` seconds and
    record whether a face is visible. Reused across all candidates instead of
    reopening the video/model per candidate (which is what made this slow)."""
    detector = cv2.FaceDetectorYN_create(str(FACE_MODEL), "", (320, 320))
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    detect_w = 480
    detect_h = int(h * detect_w / w)
    detector.setInputSize((detect_w, detect_h))

    step_frames = max(1, int(fps * interval))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    timeline = []
    for frame_idx in range(0, total_frames, step_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (detect_w, detect_h))
        _, faces = detector.detect(small)
        timeline.append((frame_idx / fps, faces is not None and len(faces) > 0))
    cap.release()
    return timeline


def face_presence(start, end, timeline):
    points = [has_face for t, has_face in timeline if start <= t <= end]
    if not points:
        return 0.0
    return sum(points) / len(points)


def build_candidates(boundaries, min_dur, max_dur):
    candidates = []
    n = len(boundaries)
    for i in range(n - 1):
        for j in range(i + 1, n):
            dur = boundaries[j] - boundaries[i]
            if dur < min_dur:
                continue
            if dur > max_dur:
                break
            candidates.append((boundaries[i], boundaries[j]))
    return candidates


def select_non_overlapping(scored, top_k):
    scored = sorted(scored, key=lambda c: c["score"], reverse=True)
    selected = []
    for cand in scored:
        overlaps = any(
            cand["start"] < s["end"] and s["start"] < cand["end"] for s in selected
        )
        if not overlaps:
            selected.append(cand)
        if len(selected) >= top_k:
            break
    return sorted(selected, key=lambda c: c["start"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="Path to source video")
    parser.add_argument("--min-dur", type=float, default=20.0)
    parser.add_argument("--max-dur", type=float, default=55.0)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--out", default=None, help="Write candidates JSON here")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)
    if not FACE_MODEL.exists():
        print(f"Face model not found: {FACE_MODEL}", file=sys.stderr)
        sys.exit(1)

    boundaries, silence_intervals, face_timeline = analyze_video(video_path)

    candidates = build_candidates(boundaries, args.min_dur, args.max_dur)
    print(f"{len(candidates)} aday pencere degerlendiriliyor...", file=sys.stderr)

    scored = []
    for start, end in candidates:
        cov = speech_coverage(start, end, silence_intervals)
        if cov < 0.4:
            continue
        face = face_presence(start, end, face_timeline)
        if face < 0.95:
            continue
        score = 0.6 * cov + 0.4 * face
        scored.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 2),
            "speech_coverage": round(cov, 2),
            "face_presence": round(face, 2),
            "score": round(score, 3),
        })

    selected = select_non_overlapping(scored, args.top_k)

    print(json.dumps(selected, ensure_ascii=False, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(selected, ensure_ascii=False, indent=2))
        print(f"Kaydedildi: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
