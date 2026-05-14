# Beceri: Ürün Fikir Üretimi

## Amaç
Retrocameraland.com'daki ürünleri YouTube içeriğiyle organik şekilde birleştirerek hem izleyiciye değer katan hem de ürün görünürlüğü sağlayan video fikirleri üretmek.

## Hedeflere Hizmet Eder
- Ürün entegrasyonu (fikirlerin %60'ı ürün bağlantılı)
- İçerik hattı (6+ hazır fikir)

## Girdiler
- `data/imports/products.md` — güncel ürün listesi, kategoriler, açıklamalar
- `knowledge/AUDIENCE.md` — izleyici profili, hangi ürünlerle ilgilendikleri
- `MEMORY.md` — ürün-video kombinasyonlarından öğrenilen örüntüler
- `outputs/` klasöründeki son araştırma raporu — hangi konular öne çıktı

## Süreç
1. `data/imports/products.md` dosyasını oku — ürün kategorilerini ve mevcut stoku gör
2. Her ürün kategorisi için 2–3 video fikri üret, aşağıdaki formatlardan birini kullan:
   - **İnceleme formatı:** "[Ürün adı] — Dürüst inceleme (X ay kullandım)"
   - **Karşılaştırma formatı:** "[Ürün A] vs [Ürün B] — Hangisini almalısın?"
   - **Nasıl kullanılır formatı:** "[Ürün adı] ile [sonuç] nasıl elde edilir"
   - **Alım rehberi formatı:** "[Kategori] için en iyi seçimler 2025"
   - **Hikaye formatı:** "[Ürün] ile çektiğim en iyi fotoğraf — film rulosu deneyimi"
3. Her fikir için şunları belirle:
   - Hangi ürün(ler) öne çıkıyor
   - Retrocameraland.com'dan direkt link eklenecek mi?
   - İzleyici için değer önerisi nedir (sadece reklam değil, bilgi veya eğlence)
   - Ürün yerleştirmesi videonun neresinde ve nasıl yapılacak
4. Fikirleri "izleyici değeri" ve "ürün görünürlüğü" dengesine göre puanla (1–5)
5. En iyi 6 fikri öncelik sırasıyla listele
6. Çıktıyı `outputs/` klasörüne yaz

## Çıktılar
- `outputs/YYYY-MM-DD_youtube_video-ideas.md`
  - Öncelikli 6+ video fikri
  - Her fikir için: format, ürün bağlantısı, değer önerisi, yerleştirme stratejisi, puan

## Kalite Çıtası
- Hiçbir fikir "açık reklam" gibi hissettirmemeli — izleyici için somut bir değer sunmalı
- Her fikir için ürünün videonun hangi dakikasında ve nasıl geçeceği belirtilmeli
- En az 2 fikir "nasıl kullanılır" veya "eğitici" formatta olmalı

## Araçlar
- `data/imports/products.md` — ürün referansı

## Entegrasyon
- Bu becerinin çıktısı **COPYWRITING** becerisine beslenir (outline için)
- **TOPIC_RESEARCH** becerisiyle paralel çalışabilir — araştırma hangi konuların arandığını gösterirse, ürün fikirleri o konulara göre hizalanır
- **CHANNEL_ANALYTICS** ürün içerikli videolar diğerlerine kıyasla nasıl performans gösteriyor bilgisini verir; bu bilgiyi MEMORY.md üzerinden bu beceriye besle
