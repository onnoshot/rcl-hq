# Skill: Sosyal Medya Görselleri (SOCIAL_MEDIA_DESIGN)

## Purpose
Müşterinin marka kimliğini sosyal medya platformlarına taşımak: profil görselleri, kapak fotoğrafları, post şablonları, story şablonları ve platform özelinde görsel sistemler üretmek.

## Serves Goals
- İçerik çeşitliliği (≥5 farklı kategori/ay)
- Müşteri memnuniyeti (≤2 revizyon turu)

## Inputs
- `outputs/` — Marka kimliği kılavuzu (BRAND_IDENTITY çıktısı)
- `data/imports/` — Müşteri brief'i: hangi platformlar, içerik türleri, yayın sıklığı
- `data/imports/` — Varsa mevcut içerik örnekleri veya rakip referansları
- `knowledge/AUDIENCE.md` — Hedef kitle ve platform davranışları
- `MEMORY.md` — Hangi format ve stillerin daha iyi performans gösterdiği

## Process

1. **Platform haritası oluşturma:** Müşterinin aktif olduğu platformları ve her platformun tasarım gereksinimlerini listele:

   | Platform | Profil | Kapak | Post | Story/Reel |
   |----------|--------|-------|------|------------|
   | Instagram | 320×320px | — | 1080×1080 / 1080×1350 | 1080×1920 |
   | LinkedIn | 400×400px | 1584×396px | 1200×627 | — |
   | Facebook | 180×180px | 820×312px | 1200×630 | 1080×1920 |
   | Twitter/X | 400×400px | 1500×500px | 1200×675 | — |
   | YouTube | 800×800px | 2560×1440px | Thumbnail: 1280×720 | — |
   | TikTok | 200×200px | — | — | 1080×1920 |

2. **Profil görseli spesifikasyonu:** Her platform için:
   - Logo veya karakter fotoğrafı kullanım kuralı
   - Arka plan rengi ve şekli
   - Safe zone (profil fotoğrafı genellikle daire kesilir — köşelerdeki önemli elementlerden kaçın)

3. **Kapak fotoğrafı tasarımı:** Varsa kapak alanları için:
   - Kompozisyon düzeni: logo konumu, başlık, slogan, iletişim
   - Renk ve görsel dil uyumu
   - Mobil ve masaüstü görünüm farkı (LinkedIn kapağı mobilden farklı kırpılır)

4. **Post şablonu sistemi:** Her içerik türü için şablon tasarımı:
   - **Bilgi paylaşımı (eğitici):** Başlık + ikon + metin bloğu + logo watermark
   - **Ürün/hizmet tanıtımı:** Ürün görseli + başlık + CTA butonu + marka rengi arka plan
   - **Alıntı/quote:** Tipografi odaklı, marka renkleri
   - **Kampanya/duyuru:** Bold tipografi + güçlü renk kullanımı + tarih/detay
   - **Before/After veya karşılaştırma:** Split layout
   - **Carousel başlığı:** Sol tarihte kaydır imleci ipucu + başlık

5. **Story/Reel şablonu sistemi:**
   - Safe zone (üst 250px ve alt 250px — platform UI'ı ve parmak alanı)
   - Arka plan: düz renk / gradient / bulanık fotoğraf
   - CTA alanı (link sticker veya swipe-up yönlendirmesi)
   - Anket, soru, countdown için placeholder alan

6. **Görsel dil kuralları:** Sosyal medyaya özel:
   - Fotoğraf filtre/ton tutarlılığı: renk sıcaklığı, doygunluk seviyesi
   - Metin üzerine renk okunabilirlik kuralları (karanlık overlay uygulamaları)
   - Emoji ve ikonografi kullanım politikası
   - Watermark/logo küçük boyutta bile okunabilir mi? (minimum 32px)

7. **İçerik takvimi şablonu:** Aylık post türü dağılım önerisi:
   - Eğitici: %30
   - Ürün/hizmet: %25
   - Sosyal kanıt / müşteri yorumu: %20
   - Hikaye / perde arkası: %15
   - Etkileşim (anket, soru, yarışma): %10

## Outputs
- `outputs/YYYY-MM-DD_uniqbee-design_social-media-[müşteri]-[platform].md` — Platform bazlı görsel sistem spesifikasyonları

**Belge yapısı:**
```
1. Platform Haritası ve Boyut Referansı
2. Profil Görseli Spesifikasyonları (platform bazlı)
3. Kapak Fotoğrafı Spesifikasyonları
4. Post Şablon Sistemi (her içerik türü için)
5. Story/Reel Şablon Sistemi
6. Görsel Dil Kuralları (filtre, tipografi, emoji politikası)
7. İçerik Türü Dağılım Önerisi
```

## Quality Bar
- Her şablon belirtilen safe zone kurallarına uygun olmalı.
- Tüm boyutlar platform güncel spesifikasyonlarına göre verilmiş olmalı.
- Post şablonları en az 5 farklı içerik türünü kapsıyor olmalı.
- Renk ve tipografi BRAND_IDENTITY kılavuzuyla %100 uyumlu olmalı.
- Story safe zone her şablonda açıkça belirtilmiş olmalı.

## Tools
- Platform boyutları için güncel spesifikasyonlar referans alınır (2024 standartları).
- Carousel postlarda görsel akış tutarlılığı için sol kenar hizalaması belirtilir.

## Integration
- BRAND_IDENTITY çıktısına bağlıdır.
- CORPORATE_DESIGN ile renk ve tipografi tutarlılığını paylaşır.
- DESIGN_AUDIT skill'i bu çıktıları marka kılavuzuna ve platform kurallarına göre denetler.
