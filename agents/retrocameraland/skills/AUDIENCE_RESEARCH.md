# Skill: Audience Research

## Purpose
Retrocameraland.com hedef kitlesinin ilgilendiği konuları, sorduğu soruları ve kullandığı dili araştırarak içerik stratejisine yön vermek.

## Serves Goals
- Tüm içerik hedefleri (doğru kitle için doğru içerik)
- Kitle bağlılığı (okuma süresi >3 dakika)
- Blog içerik hattı (doğru konu seçimi)

## Inputs
- `knowledge/AUDIENCE.md` — mevcut kitle tanımı (başlangıç noktası)
- `data/imports/` — varsa anket sonuçları, sipariş verileri, e-posta soruları, yorum export'u
- `journal/` — insan tarafından not edilen kitle sinyalleri
- `MEMORY.md` — önceki araştırmalardan kalıplar

## Process

### Adım 1 — Mevcut Kitle Tanımını Gözden Geçir
1. `knowledge/AUDIENCE.md` oku
2. Son araştırmanın tarihi neydi? (Journal'dan bak)
3. Tanım hâlâ güncel mi? Değiştiyse ne değişti?

### Adım 2 — Konu Havuzu Oluştur
Aşağıdaki kaynaklardan konu/soru toparla:
- `data/imports/` içindeki müşteri mesajları, yorumlar, sipariş notları
- İnsan tarafından `journal/` girişlerinde belirtilen kitle sinyalleri
- Analog/film fotoğrafçılığı topluluklarında sık sorulan sorular (insan tarafından import edilmişse)

Her konu/soru için şu bilgileri kaydet:
- Soru veya konu
- Hangi kitle segmentine ait?
- Tahmini arama hacmi seviyesi: Yüksek / Orta / Düşük (varsa veriye dayalı, yoksa segmente göre tahmin)
- İçerik formatı önerisi: Rehber / Karşılaştırma / Liste / Hikaye / Teknik

### Adım 3 — Segmentlere Göre Önceliklendir
Her segment için en yüksek değerli 3 konuyu seç:

| Segment | Top 3 Konu | Format | Öncelik |
|---------|------------|--------|---------|
| Yeni başlayanlar | | | |
| Meraklılar | | | |
| Koleksiyoncular | | | |
| Dijitalden geçenler | | | |
| Yaratıcılar | | | |

### Adım 4 — Dil ve Ton Analizi
- Bu kitlenin kullandığı spesifik terimler neler? (ör. "grain", "shoot film", "analog vibes")
- Hangi referanslar rezonans yaratıyor? (ör. belirli kamera modelleri, dönemler, filmler)
- Kaçınılması gereken jargon veya ton nedir?

### Adım 5 — Rapor Oluştur
Dosya adı: `YYYY-MM-DD_retrocameraland_audience-research.md`

Rapor şunları içermeli:
1. Araştırma özeti (3-5 madde: ne değişti, ne doğrulandı)
2. Öncelikli konu listesi (segmentlere göre gruplanmış)
3. Dil ve ton notları
4. Bir sonraki 30 gün için önerilen blog takvimi (8-10 konu)
5. `knowledge/AUDIENCE.md` için güncelleme önerileri (insan onayına)

## Outputs
- `outputs/YYYY-MM-DD_retrocameraland_audience-research.md` — araştırma raporu
- Journal girişi: araştırmanın ne zaman yapıldığı ve önemli bulgular

## Quality Bar
- Rapor en az 5 öncelikli konu içermeli
- Her konu bir kitle segmentiyle eşleştirilmiş olmalı
- Rapor "tahmin" değil, mevcut veriye dayalı olmalı — veri yoksa açıkça belirtilmeli
- Konu önerileri BLOG_WRITING skill'inin doğrudan kullanabileceği formatta olmalı

## Tools
- `data/imports/` — ham veri kaynağı
- `knowledge/AUDIENCE.md` — başlangıç referansı

## Integration
- BLOG_WRITING skill'ine girdi sağlar (hangi konular yazılacak?)
- Çıktısındaki kitle dil notları PRODUCT_DESCRIPTION skill'inde de kullanılır
- Aylık çalıştırılır; haftalık BLOG_WRITING döngüleri bu skill'in son çıktısını kullanır
