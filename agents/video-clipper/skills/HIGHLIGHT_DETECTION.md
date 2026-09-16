# Skill: Highlight Detection

## Purpose
Uzun bir videoda hangi bölümlerin kesit olmaya değer olduğunu (sahne kesimleri + konuşma yoğunluğu + konuşmacının kamerada görünürlüğü) otomatik bulup puanlamak.

## Serves Goals
- Doğru kesit seçimi

## Inputs
- Kaynak video dosyası (yerel yol)
- `--min-dur` / `--max-dur` — istenen klip süre aralığı (varsayılan 20-55 sn)
- `--top-k` — kaç aday döndürüleceği

## Process
1. `PySceneDetect` (ContentDetector) ile videodaki sahne kesim noktalarını bul.
2. `ffmpeg silencedetect` ile sessiz olmayan (konuşma olan) zaman aralıklarını çıkar.
3. Sahne sınırlarını birleştirerek `min-dur`–`max-dur` aralığına düşen tüm aday pencereleri oluştur.
4. Her aday için:
   - `speech_coverage`: pencerenin ne kadarının konuşma/sessizlik-dışı olduğu
   - `face_presence`: pencere içinden örneklenen karelerde (YuNet ile) yüz tespit edilme oranı
   - `score = 0.6*speech_coverage + 0.4*face_presence`
5. `speech_coverage < 0.4` olan adayları ele — konuşma olmayan sahne kesit olmaya değmez.
6. `face_presence < 0.95` olan adayları da ele — konuşmacı klip boyunca neredeyse her an kadrajda olmalı (kullanıcı talebi, 2026-07-16; başta %100 denendi ama 27 dk'lık gerçek videoda 616 adaydan sadece 1'i geçti, %95'e gevşetildi).
7. Skora göre sırala, üst üste binmeyen en iyi `top-k` adayı seç.

## Outputs
- JSON aday listesi: `{start, end, duration, speech_coverage, face_presence, score}`
- `--out` verilirse dosyaya da yazılır

## Quality Bar
- Seçilen pencereler her zaman gerçek sahne kesim noktalarında başlar/biter (cümle ortasından kesmez).
- `face_presence` düşük olan pencereler (konuşmacı kadrajda yok) düşük skorla elenir, üst sıralara çıkmaz.

## Tools
- `scripts/detect_highlights.py` — CLI, `python make_short.py` içinden de fonksiyon olarak çağrılır
- Bağımlılık: `ffmpeg`, `scenedetect`, `opencv-python`, `models/face_detection_yunet.onnx`

## Integration
Çıktısındaki her aday, `SPEAKER_REFRAME` skill'ine `start`/`end` olarak verilir; `scripts/make_short.py` bu iki skill'i zincirler.
