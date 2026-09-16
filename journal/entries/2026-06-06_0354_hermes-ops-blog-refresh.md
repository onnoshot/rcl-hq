# 2026-06-06 03:54 — Hermes Ops Asistanı + 235 Blog Görsel/SEO Refresh

## Ne yapıldı
1. **`rcl-blog-refresh.py`** — 235 blogun kapak görseli (Instagram media + YouTube thumbnail havuzu, 49 görsel,
   Claude ile eşleştirme) ve SEO başlık+meta (Claude Haiku 4.5) güncelleniyor. Arka planda çalışıyor.
   - Title değişimi handle/URL'i bozmaz; görseller Shopify CDN'ine kalıcı alınır (canlı test: cdn.shopify.com ✓).
   - Yedek + `--restore` (geri alınabilir). 2 blogda canlı test ✓, sonra tümü `--apply` arka planda.
2. **`rcl_ops.py`** — Hermes komut/sorgu asistanı (Claude): trafik (GA4), satış (Shopify), rakip analizi
   (DDG+Claude), kalite/ton/google (QA monitör + organik pay proxy), "blog düzelt N" (refresh). Hepsi test ✓.
3. **`claude-telegram-bot.py`** — Groq → **Claude Sonnet 4.6** sohbet beyni + `ops_route` komut yönlendirme.
   Yeniden başlatıldı (PID aktif, import hatası yok). Kullanıcı artık Telegram'dan komutla sorgulayıp düzeltebiliyor.
4. **IG fetch** scriptine media_url/thumbnail_url/caption alanları eklendi (görsel havuzu tazeliği).

## Gerçek veri doğrulamaları (canlı)
- Trafik: 7g 2.128 oturum (önceki 7g'ye göre -%11), organik arama %21, mobil %73
- Satış: son 30g 11 sipariş / 129.800 ₺ / dönüşüm %0.12
- Rakip analizi: Dolap/Sahibinden/niş mağazalar + RCL avantajı + eksikler + aksiyon

## Açık nokta
- Gerçek Google anahtar-kelime sıralaması için Search Console bağlanmalı (şimdilik organik trafik payı proxy).

## Sonraki
- 235 refresh bitince script kendi Telegram özetini atacak.
- İstenirse: GSC bağlantısı, blog gövdesine JSON-LD schema + ürün deep-link (QA bulguları; MEMORY/HEARTBEAT'e
  kullanıcı zaten not düştü), rakip analizine canlı fiyat scraping.
