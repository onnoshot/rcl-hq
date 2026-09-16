# Video Clipper — Scripts

Yerel Python venv (`agents/video-clipper/.venv`, Python 3.12) içinde çalışır.

## Kurulum (bir kez)
```bash
cd agents/video-clipper
/opt/homebrew/bin/python3.12 -m venv .venv
./.venv/bin/pip install -r scripts/requirements.txt
```
Yüz tespit modeli `models/face_detection_yunet.onnx` zaten repoya dahil.

## Uçtan uca kullanım
```bash
cd agents/video-clipper
./.venv/bin/python scripts/make_short.py /path/to/video.mp4 --clips 5
```
Çıktılar `outputs/YYYY-MM-DD_video-clipper_<isim>_clipNN.mp4` olarak yazılır, yanında bir `_manifest.json` (her klibin zaman aralığı + skoru) oluşur.

## Sadece aday kesitleri görmek için
```bash
./.venv/bin/python scripts/detect_highlights.py /path/to/video.mp4 --top-k 5
```

## Belirli bir zaman aralığını elle dikeye çevirmek için
```bash
./.venv/bin/python scripts/reframe_speaker.py /path/to/video.mp4 out.mp4 --start 90 --end 130
```

## Parametreler (reframe_speaker.py tepesinde)
- `TARGET_FACE_FRACTION` — yüz ne kadar büyük görünsün (yüksek = daha yakın zoom)
- `MIN_CROP_FRACTION` — en fazla ne kadar zoom yapılabilir (aşırı yakınlaşmayı sınırlar)
- `EMA_ALPHA` — kadraj yumuşatma (düşük = daha yumuşak ama gecikmeli takip)
- `HOLD_FRAMES_BEFORE_DRIFT` — yüz kaybolunca ne kadar süre son konumda beklensin
