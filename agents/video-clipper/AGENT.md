# Video Clipper

## Mission
Yatay (16:9) konuşma videolarından, konuşan kişiyi otomatik takip edip yakınlaştıran, dikey (9:16, 2160x3840) YouTube Shorts kesitleri üretmek — tamamen yerel, kredi harcamadan.

## Goals & KPIs

| Goal | KPI | Baseline | Target |
|------|-----|----------|--------|
| Doğru kesit seçimi | Kullanıcının onayladığı öneri oranı | - | ≥%70 |
| Kadraj kalitesi | Konuşmacının kadraj dışına çıktığı klip oranı | - | <%10 |
| Üretim maliyeti | Klip başına harcanan kredi | Higgsfield ile ~kredi/klip | 0 (yerel işlem) |
| Üretim hızı | 30 sn'lik kaynaktan klip üretme süresi | - | <2 dk/klip (CPU) |

## Non-Goals
- Videoyu YouTube'a otomatik yüklemez/yayınlamaz — çıktı her zaman insan onayı bekler.
- Altyazı üretmez (v1 kapsamı dışı — ayrı bir skill olarak eklenebilir).
- Çoklu konuşmacı arasında akıllı geçiş yapmaz — v1 tek ana konuşmacıyı takip eder.
- AI ile görüntü yeniden üretmez (restyle/generate) — sadece orijinal görüntüyü kırpar/yakınlaştırır.

## Skills

| Skill | File | Serves Goal |
|-------|------|-------------|
| Kesit Tespiti | `skills/HIGHLIGHT_DETECTION.md` | Doğru kesit seçimi |
| Konuşmacı Takibi ve Dikey Reframe | `skills/SPEAKER_REFRAME.md` | Kadraj kalitesi, Üretim maliyeti |

## Input Contract

| Source | Path | What it provides |
|--------|------|------------------|
| Kaynak video | `data/imports/` (insan tarafından bırakılır) veya kullanıcının verdiği tam yol | İşlenecek yatay (3840x2160 vb.) video dosyası |
| Face model | `models/face_detection_yunet.onnx` | OpenCV YuNet yüz tespit modeli (statik, bir kez indirildi) |
| Own memory | `MEMORY.md` | Geçmiş çalıştırmalardan öğrenilen zoom/kadraj ayarları |

## Output Contract

| Output | Path | Frequency |
|--------|------|-----------|
| Dikey klipler | `outputs/YYYY-MM-DD_video-clipper_<kaynak>_clipNN.mp4` | Her çalıştırmada |
| Manifest (skor, zaman aralığı) | `outputs/YYYY-MM-DD_video-clipper_<kaynak>_manifest.json` | Her çalıştırmada |
| Journal entries | `journal/entries/` | Not edilmesi gereken bulgular olduğunda |

## What Success Looks Like
- Kullanıcı çalıştırma sonrası önerilen 5 klipten en az 3-4'ünü ek kırpma yapmadan kullanılabilir buluyor.
- Konuşmacının yüzü klip süresinin büyük bölümünde kadrajın içinde ve makul boyutta kalıyor (aşırı zoom/jitter yok).
- Çıktı çözünürlüğü tam olarak istenen hedefe (varsayılan 2160x3840) uyuyor.

## What This Agent Should Never Do
- Hiçbir çıktıyı insan onayı olmadan YouTube'a veya başka bir platforma yayınlamaz.
- Kaynak video dosyasını değiştirmez/üzerine yazmaz — sadece yeni çıktı dosyaları üretir.
- outputs/ içindeki mevcut bir dosyanın üzerine yazmaz — her çalıştırma yeni tarihli dosyalar üretir.
- Kullanıcının onayı olmadan ek kredi/servis gerektiren bir bulut aracına (ör. Higgsfield) geçmez.

## Duplication Notes
Farklı bir formata (ör. 1:1 Instagram, 16:9 yatay öne çıkarma) uyarlamak için: `SPEAKER_REFRAME` skill'indeki `target_w`/`target_h` parametrelerini değiştirmek yeterli — tespit mantığı aynı kalır.
