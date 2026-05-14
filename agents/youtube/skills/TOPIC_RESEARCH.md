# Beceri: Konu Araştırması

## Amaç
Retrocameraland izleyicisinin aradığı, rekabette boşluk olan ve abone kazandıran video konularını araştırıp öncelik sıralamasıyla listelemek.

## Hedeflere Hizmet Eder
- İçerik hattı (6+ hazır fikir)
- İzlenme büyümesi

## Girdiler
- `knowledge/AUDIENCE.md` — izleyici profili, ilgi alanları, sıkıntı noktaları
- `knowledge/STRATEGY.md` — mevcut öncelikler
- `journal/` — son journal girişleri, trend sinyalleri
- `MEMORY.md` — daha önce işe yarayan konular
- `data/imports/products.md` — mevcut ürün kategorileri (ilgili konular için)

## Süreç
1. `knowledge/AUDIENCE.md` ve `MEMORY.md` dosyalarını oku — kanalın kime hitap ettiğini ve neyin işe yaradığını anla
2. Aşağıdaki arama açılarından her biri için en az 3 konu adayı üret:
   - **Arama tabanlı:** "analog kamera nasıl kullanılır", "film fotoğrafçılığı başlangıç" gibi sık aranan sorgular
   - **Trend tabanlı:** Analog fotoğrafçılık, film simülasyonu, vintage lens gibi yükselen trendler
   - **Ürün tabanlı:** `data/imports/products.md` listesindeki ürünlere bağlı konular
   - **Rakip boşluğu:** Türkçe içerikte az ele alınan ama talep gören konular
3. Her aday konu için şunları belirle:
   - Tahmini arama hacmi (düşük/orta/yüksek)
   - Rekabet düzeyi (düşük/orta/yüksek)
   - İzleyici uyumu skoru (1–5)
   - Ürün bağlantısı var mı?
4. En iyi 10 konuyu öncelik sıralamasıyla seç
5. Her konu için önerilen başlık formatı yaz (merak, fayda veya kişisel deneyim çerçevesinden)
6. Çıktıyı `outputs/` klasörüne yaz

## Çıktılar
- `outputs/YYYY-MM-DD_youtube_topic-research.md`
  - Öncelikli 10 konu listesi
  - Her konu için: açıklama, anahtar kelime, izleyici uyumu, ürün bağlantısı, tahmini başlık

## Kalite Çıtası
- En az 3 konu doğrudan `data/imports/products.md` listesiyle bağlantılı olmalı
- Her konu için en az bir başlık alternatifi yazılmış olmalı
- "İzleyici bu videoyu neden izler?" sorusu her konu için yanıtlanmış olmalı

## Araçlar
- Web araması (YouTube arama önerileri, Google Trends, rakip kanal analizi)
- `data/imports/products.md` — ürün referansı

## Entegrasyon
- Bu becerinin çıktısı doğrudan **PRODUCT_IDEAS** ve **COPYWRITING** becerilerine beslenir
- Yüksek öncelikli konular bir sonraki döngüde outline/script'e dönüştürülür
