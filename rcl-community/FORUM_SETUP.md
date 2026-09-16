# Faz 2 — Forum (Discourse) kurulumu + Shopify SSO

Forum, siteyle aynı görünmesin diye değil; **moderasyon/spam/şema hazır gelsin ve AI aramaları forum
içeriğini orantısız alıntılasın** diye Discourse'ta, ayrı subdomainde kuruluyor. Üyeler Shopify hesabıyla
giriş yapar (tek hesap), `forum.retrocameraland.com` adresinde tartışır.

## 1) Discourse'u kur
En kolay: **Discourse resmi hosting** (managed) veya bir VPS'te `discourse_docker` (DigitalOcean/Hetzner,
~2GB RAM). Subdomain: `forum.retrocameraland.com` → sunucu IP (A kaydı). SMTP gerekir (mevcut Brevo
SMTP'ni kullanabilirsin: `smtp-relay.brevo.com`).

## 2) DiscourseConnect (SSO) aç
Discourse Admin → **Settings → Login**:
- `enable discourse connect` = açık
- `discourse connect url` = `https://retrocameraland.com/apps/hesabim/community/discourse-sso`
- `discourse connect secret` = uzun rastgele bir dize → bunu Vercel'e `DISCOURSE_SSO_SECRET` olarak ekle
- `discourse connect overrides email` = açık (Shopify e-postası kaynak doğruluk)
- `logout redirect` = `https://retrocameraland.com/account/logout`

Vercel env (api/community):
```
DISCOURSE_URL=https://forum.retrocameraland.com
DISCOURSE_SSO_SECRET=<discourse ile aynı sır>
```
`discourse-sso.js` zaten yazıldı: Shopify HMAC doğrular → giriş yoksa `/account/login`'e atar → Discourse
nonce'unu imzalı geri döndürür. `orders_count>=1` olan müşterileri Discourse'ta `musteriler` grubuna ekler
(o gruba özel rozet/kategori verebilirsin).

## 3) Tema/giriş bağlantısı
- Forumdaki "Login" butonu otomatik SSO url'ine gider (Discourse halleder).
- Sitenden foruma giriş: topluluk section'ına / menüye `forum.retrocameraland.com` linki ekle. Üye Shopify'da
  giriş yapmışsa foruma tek tıkla geçer.

## 4) Discourse görünümünü RCL'e yaklaştır (opsiyonel)
Admin → **Customize → Themes**: koyu tema, vurgu `#FF4D2E`, font `-apple-system, "SF Pro Display"`. SF Pro
birebir olmasa da marka rengi + koyu zemin + logo ile yakın durur.

## 5) GEO/SEO
- Discourse `DiscussionForumPosting` şemasını **otomatik** üretir — ekstra iş yok.
- `robots.txt`: forum subdomain'inde AI botlarına izin ver (`OAI-SearchBot`, `PerplexityBot`,
  `ClaudeBot`/`Claude-SearchBot`). Discourse'un kendi robots ayarından.
- İçerik herkese **açık ve indekslenebilir** kalsın (login-duvarı arkasındaki içerik AI'da ~0 alıntı alır).
  Sadece yazma üyelere özel; okuma herkese açık.
- Kategoriler soru-başlıklı olsun ("Canon AE-1 light seal nasıl değiştirilir?") → uzun-kuyruk + AEO.

## 6) Kategori önerisi (kamera topluluğu)
Tamir & Bakım · Film & Tarama · Kamera Tavsiyesi · Alım-Satım · Galeri & Geri Bildirim · Yarışma Sohbeti.

## Test
1. Çıkış yap, `forum.retrocameraland.com` → Login → Shopify girişine düşmeli → giriş sonrası foruma üye
   olarak dönmeli.
2. Discourse Admin → Users → kullanıcının `external_id` = Shopify customer.id olmalı.
