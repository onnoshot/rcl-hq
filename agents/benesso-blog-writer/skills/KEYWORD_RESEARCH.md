# Skill: Keyword Research

## Purpose
Benesso için kullanılmamış, SEO değeri yüksek kahve anahtar kelimelerini seçmek.

## Serves Goals
- Organik trafik artışı
- SEO kapsama (200+ keyword)

## Inputs
- `data/imports/keywords.md` — mevcut keyword havuzu
- `data/imports/published_log.md` — daha önce kullanılan keyword'ler
- `knowledge/STRATEGY.md` — marka öncelikleri

## Process
1. `published_log.md` oku → kullanılmış keyword listesini çıkar
2. `keywords.md` oku → tüm havuzu al
3. Kullanılmamış keyword'leri filtrele
4. Öncelik sırası: uzun kuyruk (long-tail) > genel terimler; ticari niyet > bilgi arama
5. Bugün için 1 keyword seç — WRITE_POST skill'e geçir
6. Eğer keywords.md boşsa → journal'a eskalasyon logu yaz, dur

## Outputs
- Seçilen keyword + kısa gerekçe (neden bu?) → WRITE_POST skill'e input olarak geçer
- Journal'a: "Seçilen keyword: [X], gerekçe: [Y]"

## Quality Bar
- Seçilen keyword daha önce kullanılmamış olmalı
- Long-tail tercih edilmeli (3+ kelime)
- Türkçe ve İngilizce karşılığı her ikisi de belirlenmeli

## Tools
- Sadece mevcut dosyalar okunur — dış API kullanılmaz
- Gelecekte: scripts/keyword_fetch.py (Google Search Console entegrasyonu)

## Integration
- Bu skill çıktısı WRITE_POST skill'e doğrudan input olur
- Seçilen keyword published_log.md'ye eklenmez — yayın sonrası SHOPIFY_PUBLISH ekler
