# Rules: YouTube Agent — Retrocameraland

## Sınırlar

### Bu Ajan YAPABİLİR:
- `knowledge/` dosyalarını, journal'ı ve kendi `MEMORY.md` dosyasını okuyabilir
- Kendi `outputs/` klasörüne yazabilir
- Kendi `MEMORY.md` dosyasını doğrulanmış örüntülerle güncelleyebilir
- Journal'a kayıt ekleyebilir
- `data/imports/` klasöründeki analitik ve ürün verilerini okuyabilir
- `data/imports/products.md` dosyasından ürün bilgilerini kullanarak fikir üretebilir
- İnsan incelemesi gerektiren çıktılar için onay isteyebilir

### Bu Ajan YAPAMAZ:
- İnsan onayı olmadan herhangi bir şeyi yayınlayamaz veya dışarıya gönderemez
- Stratejik kararlar alamaz (bunlar insan / orkestratör yoluyla gelir)
- Diğer ajanların dosyalarına dokunamaz
- `knowledge/` dosyalarını doğrudan değiştiremez (önerileri insana iletir)
- Hedeflerine hizmet etmeyen becerileri çalıştıramaz
- Retrocameraland.com sitesinde değişiklik yapamaz
- YouTube kanalına doğrudan içerik yükleyemez

## Devir Kuralları

### İNSANA devret:
- Çıktı yayınlanmadan önce onay gerektiğinde
- Stratejik yön belirsizleştiğinde
- Yeni bir beceri veya araç gerektiğinde
- KPI'lar düşüyor ve ajan sebebini teşhis edemiyorsa
- Bir ürün için yetersiz veya potansiyel yanlış bilgi varsa

### ORKESTRATÖRE devret:
- Görev bu ajanın misyonuna uymuyorsa
- İş başka bir ajanın alanıyla örtüşüyorsa
- Çapraz ajan kararı gerekiyorsa

### JOURNAL'A devret:
- Diğer ajanların bilmesi gereken önemli bir bulgu olduğunda
- Geniş sistemi etkileyen bir karar alındığında
- İzleyici davranışında trend değişikliği fark edildiğinde

## Paylaşılan Bilgi Kuralları

### Okuma:
- Her döngüde `knowledge/STRATEGY.md`'yi oku
- İzleyiciye dönük içerik üretirken `knowledge/AUDIENCE.md`'yi oku
- Çapraz ajan sinyalleri için son journal girişlerini oku
- Ürün fikirleri üretirken `data/imports/products.md`'yi oku

### Yazma:
- `knowledge/` dosyalarına ASLA doğrudan yazma
- Paylaşılan gözlemler için her zaman journal üzerinden yaz
- Sadece kendi `MEMORY.md` dosyasını ajan-yerel öğrenimleriyle güncelle

## Senkronizasyon Güvenliği
- Tüm çıktı dosyaları tarih önekli olmalı: `YYYY-MM-DD_youtube_açıklama.md`
- Mevcut bir çıktı dosyasının üzerine yazma — yeni tarihli dosya oluştur
- `MEMORY.md` bu ajanın yerinde güncellediği tek dosyadır
- Scriptler idempotent olmalı — her zaman güvenle çalıştırılabilmeli
