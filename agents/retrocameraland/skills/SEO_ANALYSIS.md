# Skill: SEO Analysis & Scoring

## Purpose
Her içerik parçasının SEO puanını hesaplamak, eksiklikleri raporlamak ve %90 eşiğine ulaşana kadar optimize etmek.

## Serves Goals
- SEO performansı (organik trafik %20 artış)
- Ürün açıklaması kalitesi
- Blog içerik hattı
- Dönüşüm

## Inputs
- Analiz edilecek içerik (ürün açıklaması veya blog yazısı taslağı)
- `knowledge/AUDIENCE.md` — hedef anahtar kelimeler ve kitle dili
- `data/imports/` — varsa anahtar kelime listesi veya rakip analiz dosyası
- `MEMORY.md` — önceki döngülerde işe yarayan SEO kalıpları

## Process

### Adım 1 — Hedef Anahtar Kelimeyi Belirle
1. İçeriğin ana konusunu tanımla (1 anahtar kelime + 2-3 LSI kelimesi)
2. `knowledge/AUDIENCE.md` ve `data/imports/` içindeki anahtar kelime listesiyle karşılaştır
3. Hedef anahtar kelimeyi içeriğin başına kaydet

### Adım 2 — SEO Puanı Hesapla (100 puan üzerinden)

| Kriter | Max Puan | Kontrol |
|--------|----------|---------|
| Başlık (H1) hedef anahtar kelimeyi içeriyor mu? | 15 | İçeriyorsa 15, içermiyorsa 0 |
| Meta açıklama mevcut ve 150-160 karakter mi? | 10 | Tam aralıktaysa 10, varsa ama aralık dışındaysa 5, yoksa 0 |
| Meta açıklama hedef anahtar kelimeyi içeriyor mu? | 10 | İçeriyorsa 10, içermiyorsa 0 |
| Anahtar kelime yoğunluğu %1-2 arasında mı? | 10 | Aralıktaysa 10, %0.5-3 arasındaysa 5, dışındaysa 0 |
| İlk 100 kelimede hedef anahtar kelime geçiyor mu? | 10 | Geçiyorsa 10, geçmiyorsa 0 |
| Alt başlıklar (H2/H3) anahtar kelime içeriyor mu? | 10 | ≥1 alt başlıkta geçiyorsa 10, hiçbirinde yoksa 0 |
| İçerik uzunluğu yeterlimi? (ürün: 200-500k, blog: 800-2000k) | 10 | Aralıktaysa 10, kısaysa 5, çok uzunsa 7 |
| Dahili link önerisi mevcut mu? | 10 | ≥1 dahili link önerisi varsa 10, yoksa 0 |
| Alt metin (img alt tag) önerisi var mı? | 5 | Varsa 5, yoksa 0 |
| Okunabilirlik skoru (cümle başına ort. kelime ≤20) | 10 | ≤20 ise 10, 21-25 ise 5, >25 ise 0 |

**Toplam: 100 puan — Geçer not: ≥90**

### Adım 3 — Eksiklikleri Raporla
- 90 altındaki her kriterden puan kesilenler için kısa açıklama yaz
- Öncelik sırası: en yüksek puan kayıplı kriter önce

### Adım 4 — Optimize Et
- Her eksikliği gider (başlığı düzenle, meta açıklama ekle, anahtar kelimeyi ilk paragrafa yerleştir vb.)
- Düzeltme sonrası puanı yeniden hesapla
- Puan ≥90 olana kadar tekrarla (maksimum 3 tur)

### Adım 5 — Final Raporu
- İçeriği SEO skoru etiketiyle birlikte çıktıya ekle
- Format: `[SEO: 94/100]` içerik başlığının altına
- Kriter bazlı puanları da raporda göster

## Outputs
- Optimize edilmiş içerik + SEO skoru etiketi
- SEO kriter raporu (puan kırılımı)
- Dahili link önerileri listesi
- Çıktı dosyasına eklenir: `outputs/YYYY-MM-DD_retrocameraland_[içerik-adı].md`

## Quality Bar
- Hiçbir içerik %90 SEO skoru altında çıktıya eklenmez
- Raporun her kriteri geçer/kalır olarak işaretlenmiş olmalı
- Optimize edilmiş içerik orijinal anlamı korumalı — sadece SEO için içeriği bozmak kabul edilemez

## Tools
- Puan hesaplama tamamen bu skill'in içindeki kriterlere dayanır (harici araç gerektirmez)
- Anahtar kelime araştırması için `data/imports/keywords.md` veya `data/imports/keywords.csv` okunur (varsa)

## Integration
- PRODUCT_DESCRIPTION ve BLOG_WRITING skill'lerinin zorunlu son adımı — her iki skill de çıktı üretmeden önce bu skill'i çalıştırır
- Haftalık gözden geçirmede ortalama SEO skoru hesaplanır ve MEMORY.md'ye kaydedilir
