# Skill: Shopify Publish

## Purpose
WRITE_POST skill'den gelen TR ve EN içerikleri görselle birlikte Shopify'a yayınlamak.

## Serves Goals
- Yayın tutarlılığı
- İçerik üretimi (Shopify'da live)

## Inputs
- WRITE_POST skill çıktısı: TR başlık, EN başlık, TR body HTML, EN body HTML, TR meta, EN meta
- Konu ile ilişkili ürün handle'ı (görsel için)
- `scripts/publish.py` — otomasyon betiği
- `.env` — SHOPIFY_ACCESS_TOKEN, ANTHROPIC_API_KEY

## Process
1. İlgili ürünün görselini bul:
   - Konu ile eşleşen ürün `products.json`'dan çekilir (handle veya isim eşleşmesi)
   - Ürün görseli yoksa Unsplash'ten kahve anahtar kelimesiyle görsel al
2. TR blog post oluştur:
   - `POST /admin/api/2024-01/blogs/{blog_id}/articles.json`
   - title, body_html, author, tags, image (src), published_at
3. EN blog post oluştur (aynı blog'a, farklı başlık ve içerik)
4. Her iki post'un Shopify article ID'sini kaydet
5. `data/imports/published_log.md` güncelle

## Outputs
- Shopify'da yayınlanan 2 article (TR + EN)
- published_log.md'de yeni satır: `YYYY-MM-DD | [TR başlık] | [EN başlık] | [keyword] | [TR ID] | [EN ID]`
- `outputs/YYYY-MM-DD_benesso-blog_[slug].md` — arşiv kopyası

## Quality Bar
- Her iki dil için de Shopify'dan 201 Created yanıtı alınmalı
- Görsel her yazıda zorunlu — görselsiz yayın yapılmaz
- published_log.md güncellenmeden döngü bitmez

## Tools
- `scripts/publish.py` — tüm mantığı yönetir
- Shopify Admin API (Articles endpoint)
- Unsplash API (yedek görsel kaynağı)

## Integration
- WRITE_POST'tan içeriği alır, döngüyü tamamlar
- Hata durumunda: log at, bir sonraki döngüde tekrar dene (max 3 deneme)
