# Beceri: Kanal Analizi

## Amaç
YouTube Studio verilerini analiz ederek kanal büyümesini takip etmek, neyin işe yarayıp yaramadığını tespit etmek ve bir sonraki döngü için aksiyon önermek.

## Hedeflere Hizmet Eder
- Tüm hedefler (büyüme, etkileşim, ürün entegrasyonu)

## Girdiler
- `data/imports/` — YouTube Studio CSV export dosyaları (haftalık/aylık)
- `MEMORY.md` — önceki dönemlerden kanıtlanmış örüntüler
- `knowledge/STRATEGY.md` — mevcut hedefler ve öncelikler

## Süreç
1. `data/imports/` klasöründeki en son CSV dosyasını oku
2. Temel metrikleri çek ve hedeflerle karşılaştır:

   | Metrik | Hedef | Mevcut | Önceki Dönem | Değişim |
   |--------|-------|--------|--------------|---------|
   | Toplam izlenme | +20%/ay | | | |
   | Net abone kazanımı | Pozitif | | | |
   | Ortalama izlenme süresi (%) | >%50 | | | |
   | Tıklama oranı (CTR) | >%4 | | | |
   | İmpresyon sayısı | — | | | |

3. **Büyüme Analizi:**
   - Abone büyüme hızı: kaç aboneye ulaşıldı, 10.000 hedefine ne kadar kaldı?
   - Hangi videolar en fazla abone kazandırdı?
   - Hangi trafik kaynağı en çok görüntülenme getiriyor? (arama, önerilen, dış)

4. **Video Performans Analizi:**
   - Son 30 günün en iyi 3 videosu (görüntülenme ve izlenme süresi açısından)
   - Son 30 günün en düşük 3 videosu
   - Ürün bağlantılı videolar vs bağlantısız — karşılaştır

5. **Başlık & Thumbnail CTR Analizi:**
   - CTR >%5 olan videolar — hangi başlık formatını kullandı?
   - CTR <%2 olan videolar — başlık/thumbnail sorunu mu?

6. **Örüntü Çıkarımı:**
   - 3+ videoda tekrarlayan başarı faktörü varsa `MEMORY.md`'ye yaz
   - 3+ videoda tekrarlayan başarısızlık varsa `MEMORY.md`'ye yaz

7. Analiz raporunu `outputs/` klasörüne yaz
8. Journal'a özet giriş ekle

## Çıktılar
- `outputs/YYYY-MM-DD_youtube_channel-analysis.md`
  - Metrik tablosu (hedef vs mevcut)
  - 10.000 abone hedefine kalan mesafe ve tahmini süre
  - En iyi / en düşük performanslı videolar
  - CTR analizi
  - 3 aksiyon önerisi (bu haftanın en değerli adımları)
  - `MEMORY.md` güncellemesi gereken örüntüler

## Kalite Çıtası
- Her raporda 10.000 abone hedefine olan mesafe açıkça belirtilmeli
- En az 3 somut aksiyon önerisi olmalı ("daha iyi içerik yap" değil, "X formatlı videolarda CTR 2x yüksek, bir sonraki 2 fikri bu formata çevir" gibi)
- Ürün bağlantılı video performansı ayrı bir satırda raporlanmalı

## Araçlar
- YouTube Studio CSV export (`data/imports/` klasörüne insan tarafından yüklenir)

## Entegrasyon
- Bu becerinin bulguları **TOPIC_RESEARCH** ve **PRODUCT_IDEAS** becerilerini yönlendirir
- Doğrulanmış örüntüler `MEMORY.md` üzerinden tüm becerilere aktarılır
- Büyük performans değişimleri (iyi veya kötü) journal'a kaydedilir
