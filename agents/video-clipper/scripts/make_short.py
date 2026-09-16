#!/usr/bin/env python3
"""End-to-end: detect highlight windows in a local video, reframe each to a vertical
speaker-tracking clip, and save into agents/video-clipper/outputs/."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detect_highlights import analyze_video, speech_coverage, face_presence, \
    build_candidates, select_non_overlapping
from reframe_speaker import reframe

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def slugify(name):
    return "".join(c if c.isalnum() else "-" for c in name).strip("-").lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Local source video path")
    parser.add_argument("--clips", type=int, default=5, help="How many clips to produce")
    parser.add_argument("--min-dur", type=float, default=20.0)
    parser.add_argument("--max-dur", type=float, default=55.0)
    parser.add_argument("--width", type=int, default=2160)
    parser.add_argument("--height", type=int, default=3840)
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Video bulunamadi: {input_path}", file=sys.stderr)
        sys.exit(1)

    print("1/3 Sahne ve konusma analizi...", file=sys.stderr)
    boundaries, silence_intervals, face_timeline = analyze_video(input_path)
    candidates = build_candidates(boundaries, args.min_dur, args.max_dur)

    print(f"2/3 {len(candidates)} aday pencere puanlaniyor...", file=sys.stderr)
    scored = []
    for start, end in candidates:
        cov = speech_coverage(start, end, silence_intervals)
        if cov < 0.4:
            continue
        face = face_presence(start, end, face_timeline)
        if face < 0.95:
            continue
        score = 0.6 * cov + 0.4 * face
        scored.append({"start": start, "end": end, "score": score,
                        "speech_coverage": round(cov, 2), "face_presence": round(face, 2)})

    selected = select_non_overlapping(scored, args.clips)
    if not selected:
        print("Uygun kesit bulunamadi (konusma/yuz kriterlerini karsilayan pencere yok).", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = slugify(input_path.stem)
    today = date.today().isoformat()

    manifest = []
    print(f"3/3 {len(selected)} klip dikey formata donusturuluyor...", file=sys.stderr)
    for i, cand in enumerate(selected, 1):
        out_name = f"{today}_video-clipper_{stem}_clip{i:02d}.mp4"
        out_path = OUTPUT_DIR / out_name
        print(f"  Klip {i}/{len(selected)}: {cand['start']:.1f}s-{cand['end']:.1f}s "
              f"(skor {cand['score']:.2f}) -> {out_name}", file=sys.stderr)
        reframe(input_path, out_path, cand["start"], cand["end"], args.width, args.height,
                shot_boundaries=boundaries)
        manifest.append({**cand, "output": str(out_path)})

    manifest_path = OUTPUT_DIR / f"{today}_video-clipper_{stem}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\nBitti. {len(selected)} klip: {OUTPUT_DIR}", file=sys.stderr)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
