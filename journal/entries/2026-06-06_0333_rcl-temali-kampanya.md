# 2026-06-06 03:33 — RCL Blog: Öğrenci & Sevgili Temalı Kampanya

## Ne yapıldı
`rcl-seo-blog-agent.py` ajanına **ay sonuna kadar (Haziran 2026)** geçerli temalı
kampanya enjeksiyonu eklendi. Yayınlanan **her iki blogtan biri** sırayla şu iki temada:

1. **Öğrenciler için kamera önerileri** — bütçe dostu, kampüs/sosyal medya içeriği,
   test edilmiş & garantili retro modeller (telefon yerine gerçek Y2K/CCD karakteri).
2. **Sevgiliye / çiftlere retro kamera hediyesi** — anlamlı hediye, yıldönümü/özel gün,
   beraber kullanma deneyimi, özel hediye kutusu, romantik anı makinesi.

Her temalı blog RCL felsefesiyle (test + garanti + aynı gün teslim + özel kutu) birleşiyor,
**satışa teşvik** ediyor, blog içi **YouTube embed + Instagram/TikTok/Pinterest/LinkedIn**
yönlendirmeleri ve site CTA'sı otomatik enjekte ediliyor (mevcut SOCIAL_BLOCK/CTA_BLOCK).

## Nasıl çalışıyor (teknik)
- `THEME_DEADLINE = 2026-07-01` — bu tarihten sonra ajan **otomatik** normal akışına döner.
- `inject_themed_topics()` her çalışmada (BATCH_COUNT=2) slot 0'ı temalı konuyla değiştirir,
  slot 1 normal kalır → "her iki gönderiden biri" karşılanır.
- Temalar `themed-blog-state.json` sayacıyla **sıralı döner** (öğrenci → sevgili → …).
- `pick_themed_topic()` Groq LLM ile tema+trend araştırmalı benzersiz konu üretir;
  LLM başarısızsa `_themed_fallback()` garantili temalı konu verir (test: 10 çalışmada 0 tekrar).
- Konu seçimi yayınlanan başlıklara karşı dedup edilir; SEO başlık 52-68 kar, meta 148-165 kar.

## Doğrulama
- `python3 -m py_compile` ✓
- Rotasyon + her-iki-slottan-biri + dedup testi ✓ (10 çalışma simülasyonu)
- Canlı Groq testi ✓ (her iki tema geçerli SEO konusu üretti)

## Sonraki
- Cron (00:00/12:00/15:00/19:00/23:00) bir sonraki çalışmasında otomatik devreye girer.
- Temmuz'da kampanya kendiliğinden kapanır; istenirse `THEME_DEADLINE` uzatılır.
