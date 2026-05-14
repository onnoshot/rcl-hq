# Skill: Product Description Writing

## Purpose
Retrocameraland.com ürün sayfaları için SEO skoru ≥90 olan, hedef kitleye özgü, dönüşüme yönelik ürün açıklamaları yazmak.

## Serves Goals
- Ürün açıklaması kalitesi (≥200 kelime)
- SEO performansı (organik trafik artışı)
- Dönüşüm (sepete ekleme oranı %5 artış)

## Inputs
- `data/imports/` — işlenecek ürün listesi (CSV veya MD: ürün adı, marka, model, mevcut açıklama, URL)
- `knowledge/AUDIENCE.md` — hedef kitle segmentleri ve dil tarzı
- `knowledge/STRATEGY.md` — öne çıkarılacak öncelikli ürün kategorileri
- `MEMORY.md` — önceden onaylanan açıklamalarda işe yarayan kalıplar

## Process

### Adım 1 — Ürünü Tanı
1. Ürün adı, marka, model ve kategoriyi not et
2. Mevcut açıklamayı oku (varsa) — ne eksik, ne yanlış?
3. Ürün kategorisini belirle: film kamera / dijital kamera / lens / aksesuar / film / lab hizmeti

### Adım 2 — Hedef Kitleyi Eşleştir
1. `knowledge/AUDIENCE.md` oku
2. Bu ürünün hangi segment için en uygun olduğunu belirle
3. O segmentin dilini, pain point'lerini ve satın alma motivasyonlarını not et

### Adım 3 — Yapıyı Oluştur
Açıklama şu bölümleri içermelidir:
1. **Açılış cümlesi** (1 cümle): Ürünün en güçlü özelliği + kitleye duygusal bağ
2. **Teknik özellikler** (3-5 madde): Doğrulanmış teknik bilgiler — tahmin yok
3. **Kullanım senaryosu** (1-2 paragraf): Bu ürünle ne yapabilirsin? Hangi çekimlerde parlar?
4. **Neden Retrocameraland?** (1 paragraf): Güven, seçim kalitesi, destek — marka değeri
5. **CTA** (1 cümle): Spesifik ve eylem yönelimli

### Adım 4 — Taslak Yaz
- Minimum 200, maksimum 500 kelime
- `knowledge/AUDIENCE.md` içindeki marka tonunu koru: samimi, uzman, nostaljiye duyarlı
- Aşırı satışçı dilden kaçın ("en iyi", "eşsiz", "benzersiz" gibi boş üstünlükler)
- Teknik doğrulanamayan iddialar → "doğrulanması gereken" etiketiyle işaretle

### Adım 5 — SEO Analizi Çalıştır
1. `skills/SEO_ANALYSIS.md` talimatlarını uygula
2. SEO skoru ≥90 olana kadar optimize et
3. SEO kriter raporunu çıktıya ekle

### Adım 6 — Çıktı Dosyasını Oluştur
Dosya adı: `YYYY-MM-DD_retrocameraland_product-desc_[ürün-slug].md`

Dosya yapısı:
```
# [Ürün Adı] — Ürün Açıklaması

[SEO: XX/100] | Hedef Anahtar Kelime: [kelime]

---

## Açıklama Metni
[yazılan açıklama]

---

## Meta Açıklama (150-160 karakter)
[meta açıklama metni]

---

## Dahili Link Önerileri
- [ilgili ürün veya blog yazısı]

---

## SEO Kriter Raporu
[kriter bazlı puan kırılımı]

---

## İnsan Onayı Notları
- [ ] Teknik bilgiler doğrulandı
- [ ] Ton ve dil uygun
- [ ] Yayına hazır
```

## Quality Bar
- SEO skoru ≥90 olmadan çıktı kabul edilmez
- Her açıklama minimum 200 kelime
- Hiçbir teknik iddia doğrulanmadan "kesin" olarak sunulamaz
- Marka tonu: samimi + uzman + nostaljiye duyarlı

## Tools
- `skills/SEO_ANALYSIS.md` — zorunlu son adım
- `data/imports/` — ürün verisi kaynağı

## Integration
- Bu skill'in çıktısı BLOG_WRITING skill'ine girdi sağlayabilir (ürün odaklı blog yazıları için)
- SEO_ANALYSIS skill'ini her zaman son adımda çalıştırır
- Onay kararları `journal/` aracılığıyla takip edilir
