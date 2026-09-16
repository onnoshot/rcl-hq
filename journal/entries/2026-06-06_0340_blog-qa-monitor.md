# 2026-06-06 03:40 — RCL Blog QA Monitör ("Hermes takip etsin")

## Ne yapıldı
`rcl-blog-qa-monitor.py` oluşturuldu: retrocameraland.com bloglarını Shopify API'den çeker,
5 boyutta puanlar ve Telegram'a (Hermes kanalı) rapor atar. LaunchAgent `com.rcl.blog-qa-monitor`
ile **günlük 09:30** çalışacak şekilde yüklendi.

## Boyutlar
1. **SEO** — `rcl-seo-blog-agent.score_seo` yeniden kullanılır; gerçek meta_desc metafield'den çekilir
2. **AI-arama (AEO)** — JSON-LD schema, FAQ yapısı, soru-başlık, taranabilir liste/tablo
3. **Yönlendirme** — ürün deep-link / koleksiyon / sosyal medya / YouTube embed
4. **İnsan vs AI-slop** — Groq llama-3.3-70b jüri (`agent.groq` SDK; raw HTTP 403 verir), klişe sayımı
5. **Mobil/Animasyon** — taşan tablo riski (overflow-x yok), animasyon/transition yok

## İlk denetim bulguları (son 6 blog)
- SEO ~69/100 (on-page temel iyi) 🟡
- AEO 60/100 — **0/6 schema** 🔴 (AI/zengin sonuçlara uygun değil)
- Yönlendirme 60/100 — sosyal+YT var ama **0/6 ürün deep-link** 🟡
- Mobil/Animasyon 30/100 — **0/6 animasyon**, geniş tablolar mobilde taşıyor 🔴
- İnsan tonu 43/100 — **5/6 AI-slop** işaretli (şablon + klişe, deneyim yok) 🔴

## Sonraki (üretim tarafı düzeltmeleri — kullanıcı onayı bekliyor)
1. JSON-LD Article + FAQPage schema enjeksiyonu (`publish_blog`)
2. Blog gövdesine gerçek ürün deep-link'leri (TOP_PRODUCTS)
3. Geniş tabloları `overflow-x:auto` ile sarmala + hafif animasyon/CSS
4. Şablonu kır: birinci-tekil deneyim tonu, klişe azalt (`generate_blog_html` promptları)

## Doğrulama
- `py_compile` ✓ · canlı çalıştırma ✓ (Telegram'a 2 rapor gönderildi, msg 49 onay)
