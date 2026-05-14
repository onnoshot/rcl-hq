# Beceri: Metin Yazarlığı

## Amaç
Onaylı video konuları için tıklatıcı başlık, çekici açıklama, bölümlü outline ve güçlü CTA yazarak videonun performansını maksimize etmek.

## Hedeflere Hizmet Eder
- İzlenme büyümesi (başlık + thumbnail metni CTR'yi etkiler)
- İzleyici etkileşimi (ortalama izlenme süresi)
- Ürün entegrasyonu (doğal ürün yerleştirmesi)

## Girdiler
- Onaylı video konusu (`outputs/` klasöründen seçilmiş veya insan tarafından verilmiş)
- `knowledge/AUDIENCE.md` — izleyicinin dili ve sıkıntı noktaları
- `knowledge/BRAND.md` — ses tonu, marka kimliği
- `MEMORY.md` — daha önce yüksek performans gösteren başlık formatları
- `data/imports/products.md` — ürün linkleri ve açıklamaları (CTA ve açıklama için)

## Süreç
1. Konu için 5 farklı başlık alternatifi yaz (her biri farklı bir çerçeveden):
   - Merak çerçevesi: "Hiç bilmediğin X şey..."
   - Fayda çerçevesi: "X kamera ile nasıl Y yapılır"
   - Kişisel deneyim: "X kamerayı 30 gün kullandım, işte sonuç"
   - Karşılaştırma: "X vs Y: Hangisi daha iyi?"
   - Hata/uyarı: "X yaparken yaptığım en büyük hata"
2. Her başlık için thumbnail metni öner (max 4 kelime, büyük harf)
3. Video outline yaz (yapı):
   - **Açılış kancası** (ilk 30 saniye — izleyiciyi tutan soru veya iddia)
   - **Giriş** (kanal/kişi tanıtımı, videonun vaadi)
   - **Ana bölümler** (3–5 bölüm, her biri başlıklı)
   - **Ürün anı** (doğal yerleşim — hangi bölümde, nasıl geçiş yapılır)
   - **CTA** (abone ol + link açıklamada + bir sonraki video)
4. YouTube açıklaması yaz:
   - İlk 2 satır: kanca (arama sonuçlarında görünen kısım)
   - Ürün linkleri (retrocameraland.com)
   - Bölüm zaman damgaları (placeholder olarak)
   - Hashtag önerileri (5–8 adet)
5. Çıktıyı `outputs/` klasörüne yaz

## Çıktılar
- `outputs/YYYY-MM-DD_youtube_script-[konu-slug].md`
  - 5 başlık alternatifi + tercih edilen başlık
  - Thumbnail metin önerileri
  - Bölümlü video outline
  - YouTube açıklaması
  - Hashtag listesi

## Kalite Çıtası
- Her başlık 60 karakteri geçmemeli (YouTube'da kırpılmaz)
- Açılış kancası ilk 2 cümlede izleyiciye "bu video benim için" dedirtmeli
- En az bir ürün doğal olarak outline'a yerleştirilmiş olmalı
- CTA videonun sonuna yerleştirilmiş ve açık olmalı

## Araçlar
- `data/imports/products.md` — ürün URL'leri ve açıklamaları

## Entegrasyon
- **TOPIC_RESEARCH** çıktısını girdi olarak alır
- **CHANNEL_ANALYTICS** becerisi yüksek CTR'li başlık formatlarını belirledikçe bu beceri güncellenir
