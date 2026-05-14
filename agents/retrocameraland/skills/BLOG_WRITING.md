# Skill: Blog Writing

## Purpose
Retrocameraland.com hedef kitlesinin ilgilendiği konularda, SEO skoru ≥90 olan, organik trafik ve kitle bağlılığı sağlayan blog yazıları üretmek.

## Serves Goals
- Blog içerik hattı (4 yazı/ay)
- Kitle bağlılığı (ortalama okuma süresi >3 dakika)
- SEO performansı (organik trafik %20 artış)

## Inputs
- `knowledge/AUDIENCE.md` — kitle segmentleri, pain points, sık sorulan sorular
- `knowledge/STRATEGY.md` — öne çıkarılacak ürün kategorileri ve dönemsel öncelikler
- `journal/` — son döngülerde ortaya çıkan konu fikirleri veya kitle sinyalleri
- `MEMORY.md` — daha önce işe yarayan konu formatları
- `data/imports/` — varsa konu listesi, anahtar kelime araştırması, rakip blog analizi

## Konu Kategorileri (Hedef Kitleye Göre)

Retrocameraland.com hedef kitlesi şu segmentlerden oluşur (bkz. `knowledge/AUDIENCE.md`):
1. **Film fotoğrafçılığına yeni başlayanlar** — "Nasıl başlarım?" sorusu
2. **Analog fotoğrafçılık meraklıları** — derinlemesine teknik ve nostaljik içerik
3. **Koleksiyoncular** — nadir model, üretim tarihi, değer bilgisi
4. **Dijital fotoğrafçılar film deneyen** — dijital ile karşılaştırmalı perspektif
5. **Yaratıcı içerik üreticileri** — estetik, stil, social media için analog

Blog konuları bu segmentlerin sorularına yanıt vermelidir.

## Process

### Adım 1 — Konu Seç
1. `MEMORY.md`, `journal/`, `data/imports/` ve `knowledge/` oku
2. Hedef kitlede en büyük soruyu (pain point veya merak) yanıtlayan konuyu seç
3. Konu formatlarından birini belirle:
   - **Rehber/Nasıl Yapılır:** "Filmi ilk kez nasıl yüklerim?"
   - **Karşılaştırma:** "Nikon FM2 vs Canon AE-1: Hangisi sana göre?"
   - **Ürün Odaklı:** "Lomography Color 400 ile çekim deneyimi"
   - **Nostaljik/Hikaye:** "Analog fotoğrafçılığa dönüşün 5 nedeni"
   - **Teknik Derinlik:** "Film ISO'su nedir, nasıl seçilir?"
   - **Liste:** "Başlangıç için en iyi 5 film kamera (2025)"

### Adım 2 — Anahtar Kelime ve SEO Stratejisi
1. Konu için birincil anahtar kelimeyi belirle (uzun kuyruklu önerilir)
2. 2-3 LSI (semantik ilişkili) anahtar kelimeyi listele
3. Rakip içeriklerin başlık formatını not et (varsa `data/imports/` içinde)
4. Başlık seçenekleri: 3 farklı H1 alternatifi yaz, en güçlü olanı seç

### Adım 3 — İçerik Taslağı (Outline)
```
H1: [Başlık — hedef anahtar kelime içermeli]
Giriş (100-150 kelime): Problem/merak + bu yazının ne vaat ettiği
H2: [Alt başlık 1]
H2: [Alt başlık 2]
...
Sonuç (100 kelime): Özet + CTA (Retrocameraland ürünlerine yönlendirme)
```

### Adım 4 — Yazıyı Üret
- Minimum 800, maksimum 2000 kelime
- Marka tonu: samimi, uzman, nostaljiye duyarlı — didaktik değil, sohbet tarzı
- Her H2 bölümü bağımsız okunabilir olmalı (tarama okuyucusu için)
- En az 1 ürün veya kategori sayfasına dahili link
- Teknik iddialar doğrulanmış veya "doğrulanması gereken" olarak etiketlenmiş

### Adım 5 — SEO Analizi Çalıştır
1. `skills/SEO_ANALYSIS.md` talimatlarını uygula
2. SEO skoru ≥90 olana kadar optimize et

### Adım 6 — Çıktı Dosyasını Oluştur
Dosya adı: `YYYY-MM-DD_retrocameraland_blog_[konu-slug].md`

Dosya yapısı:
```
# [Blog Başlığı]

[SEO: XX/100] | Hedef Anahtar Kelime: [kelime] | Segment: [kitle segmenti]
Tahmini okuma süresi: X dakika

---

## Blog Yazısı
[yazı içeriği]

---

## Meta Açıklama (150-160 karakter)
[meta açıklama]

---

## Dahili Link Önerileri
- [ürün sayfaları veya diğer blog yazıları]

---

## SEO Kriter Raporu
[kriter bazlı puan kırılımı]

---

## İnsan Onayı Notları
- [ ] Teknik bilgiler doğrulandı
- [ ] Kitle uygunluğu kontrol edildi
- [ ] Dahili linkler çalışıyor
- [ ] Yayına hazır
```

## Quality Bar
- SEO skoru ≥90 olmadan çıktı kabul edilmez
- Minimum 800 kelime
- Her yazı en az 1 H2 alt başlık içermeli
- Her yazı en az 1 dahili link önerisi içermeli
- Hiçbir teknik iddia doğrulanmadan kesin olarak sunulamaz
- Yazı gerçekten bir soruyu yanıtlamalı — sadece anahtar kelime doldurma değil

## Tools
- `skills/SEO_ANALYSIS.md` — zorunlu son adım

## Integration
- AUDIENCE_RESEARCH skill'inin çıktısını girdi olarak kullanır (hangi konular seçileceği)
- SEO_ANALYSIS skill'ini her zaman son adımda çalıştırır
- Ürün odaklı yazılar PRODUCT_DESCRIPTION çıktılarıyla bağlantılı olabilir
