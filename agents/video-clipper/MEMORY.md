# Memory: Video Clipper

Agent-local learnings. Updated after runs where a pattern is confirmed across multiple videos/clips.

<!-- IMPORTANT: Only write here when a pattern is confirmed across multiple data points. -->
<!-- Do not log one-off observations. Those go in the journal. -->

## Doğrulanmış Kalibrasyon Değerleri
<!-- TARGET_FACE_FRACTION, EMA_ALPHA, FACE_VERTICAL_BIAS gibi parametrelerde işe yarayan ayarlar -->
- Kesit seçiminde `face_presence` eşiği %95 (kullanıcı talebi, 2026-07-16). Önce %100 denendi — 27 dk'lık gerçek videoda 616 adaydan sadece 1'i geçti, kullanıcı %95'e gevşetmeyi onayladı (pratikte fark edilmeyen anlık boşluklara izin verir, kalifiye aday sayısını ciddi artırır).
- Alt-sahne birleştirme eşiği: 1.0 saniyeden kısa "sahne"ler (genelde ffmpeg -ss/-to'nun tam kare sınırında kesmemesinden kaynaklanan sahte mikro-kesitler) komşusuna birleştirilmeli, yoksa klip sonunda ani kadraj sıçraması oluyor.

## İşe Yaramayan Yaklaşımlar
<!-- Denenip başarısız olan kadraj/zoom stratejileri -->
- **Kare-kare EMA ile sürekli yüz takibi** (v1): Yüz her hareket ettiğinde kadraj da onunla birlikte kaydığı için titreşim/sallanma hissi yarattı. Kullanıcı geri bildirimi (2026-07-16): "yüz takibi genel olarak doğru fakat titreşim oluyor... genel bir merkez bulup orada ortalamalıyız". Yerine geçen yaklaşım: her alt-sahne (kamera kesimi) için o sahnenin tüm örneklerinin medyanından **tek, sabit** bir kadraj hesaplanıyor; kadraj yalnızca sahne değiştiğinde (= genelde konuşan kişi değiştiğinde) değişiyor, sahne içinde hiç kaymıyor. **Doğrulandı (2026-07-16):** kullanıcı 31 sn'lik gerçek test kesitini izleyip "sabit olmuş kadraj güzel" onayı verdi. Detay: [[../skills/SPEAKER_REFRAME.md]]

## Sahne Tipi Notları
<!-- Hangi video türlerinde (röportaj, tek kamera, hareketli konuşmacı vb.) hangi ayarlar gerekiyor -->
- Çok kameralı/kurgulu röportaj-show formatı (ör. Birebir Show): sık geniş plan/reaksiyon/başka açı kesimi olduğu için genel yüz görünürlüğü düşük olabilir (test videosunda %54). Bu tür içerikte 20-55 sn'lik pencerelerde %95 yüz şartı çok az aday çıkarır — kullanıcı bunu kabul etti, az ama kusursuz klip tercih edildi (2026-07-16). Daha fazla klip isteniyorsa min-dur kısaltılabilir veya eşik gevşetilebilir (henüz denenmedi).

## Kesit Seçim Kalitesi
<!-- HIGHLIGHT_DETECTION'ın önerdiği kesitlerin kullanıcı tarafından ne oranda onaylandığı -->
-

## Süreç İyileştirmeleri
<!-- Script/pipeline'da tekrar eden sorunlar ve çözümleri -->
- `ffmpeg silencedetect`'e `-vn` eklenmeli — yoksa sadece ses lazımken tüm 4K görüntüyü de gereksiz yere çözümleyip işi 5-10x yavaşlatıyor.
- Sahne/konuşma/yüz analizi (`analyze_video`) artık `.cache/`'e (video path+boyut+mtime anahtarlı) kaydediliyor — aynı video üzerinde eşik/parametre denemesi yapmak saniyeler sürüyor, video değişmediği sürece ~15 dk'lık analiz tekrar edilmiyor.
- `face_presence` gibi puanlama fonksiyonlarını her aday için video/modeli yeniden açacak şekilde yazma — tek geçişte tüm video için zaman çizelgesi çıkarıp adaylar sadece o veriden anlık okumalı (v1'de 616 aday × video açma hatası verimliliği çok düşürmüştü).

## Last Updated
2026-07-16 — v2 (sabit kadraj + %95 yüz eşiği + cache) gerçek videoda doğrulandı, kullanıcı onayladı.
