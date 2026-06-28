# RCL HQ Dashboard — Sistem Haritası

Canlı panel: **https://rclhq.vercel.app**
Son düzen: 2026-06-28 (karışık kablolar temizlendi, tek doğru-kaynak + tek yayınlama yolu)

---

## 1. Tek doğru-kaynak (TEK dosya düzenlersin)

```
retrocameraland-hq-dashboard.html   ←  ANA KAYNAK. Tüm UI + tüm veri blokları burada.
```

- Dashboard'un **görünümünü/tasarımını** değiştirmek istersen SADECE bu dosyayı düzenle.
- Veriler bu dosyanın içinde **marker bloklarında** durur (aşağıda). Onları elle düzenleme — scriptler yazar.
- Bu dosya her yayınlamada olduğu gibi `rcl-dashboard/index.html`'e kopyalanır → Vercel canlıya alır.

## 2. Merkezi ayar (yol / token / marker → TEK yer)

```
rcl_config.py
```

| Ne değişti | Nereyi düzenle |
|---|---|
| Repo taşındı / yol değişti | `rcl_config.py` → `REPO_DIR` |
| Shopify token yenilendi | `rcl_config.py` → `SHOPIFY_TOKEN` |
| Marker adı değişti | `rcl_config.py` → `MARKERS` |

Başka HİÇBİR dosyada yol/token yok. Eskiden 5 dosyaya dağılmıştı — artık tek yer.

`rcl_config.py` ayrıca **`publish()`** fonksiyonunu sağlar: tüm scriptler bununla yayınlar.
`publish()` daima önce remote ucuna senkron olur (`git fetch` + `reset --hard`) → **repo ASLA çatallanmaz**.
`flock` ile eşzamanlı çalışmalar sıraya girer → push yarışı olmaz.

## 3. Veri kaynakları (her feed = AYRI script, ayrı düzenlenir)

| Feed | Script | Auth | Marker bloğu | Zaman |
|---|---|---|---|---|
| Shopify (satış/stok/müşteri) | `retrocameraland-shopify-fetch.py` | `rcl_config.SHOPIFY_TOKEN` | SHOPIFY | saatlik |
| YouTube | `retrocameraland-youtube-fetch.py` | `yt_token.json` + `yt_client_secret.json` | YOUTUBE | saatlik |
| Instagram | `retrocameraland-instagram-fetch.py` | `ig_token.json` | INSTAGRAM | saatlik |
| GA4 trafik + Blog SEO | `retrocameraland-ga4-hq-fetch.py` | `~/.config/ga4/token.json` (+Shopify blog listesi) | GA4_TRAFFIC, BLOG_SEO | her gün 09:00 |
| E-posta (Brevo) | `rcl-email-stats.py` | `.env` → `BREVO_API_KEY` | EMAIL | 10:00 + 16:00 |

Her script SADECE kendi marker bloğunu yazar → birbirine karışmaz. Bir feed'i değiştirmek istersen sadece o scripti düzenle.

**Her scriptin akışı aynı:** `veri çek → write_block("FEED", payload) [ANA KAYNAĞA] → publish("feed")`.

## 4. data.js (otomatik türetilir — ELLE DÜZENLEME)

`rcl-dashboard/data.js`, `publish()` içinde ANA KAYNAKTAN üretilir (YOUTUBE + SHOPIFY + INSTAGRAM blokları).
Sadece eski `youtube.html` + `instagram.html` mini sayfaları okur. Elle dokunma.

## 5. Zamanlayıcılar (LaunchAgent)

```
com.rcl.shopify-fetch      StartInterval 3600  (saatlik)   → logs/shopify-fetch.log
com.rcl.youtube-fetch      StartInterval 3600  (saatlik)   → logs/youtube-fetch.log
com.rcl.instagram-fetch    StartInterval 3600  (saatlik)   → logs/instagram-fetch.log
com.retrocameraland.analytics   09:00 (GA4 + analytics)
com.rcl.email-stats        10:00 + 16:00
```

> Eski **çift** agent seti (`retrocameraland-*.hourly`) emekliye ayrıldı:
> `~/Library/LaunchAgents/_retired-duplicates/`. Her script artık saatte 1 kez çalışır.

## 6. Manuel tazeleme

```bash
cd /Users/onnoshot/Downloads/Agentlar
python3 retrocameraland-shopify-fetch.py     # veya yt / instagram / ga4 / email-stats
```
Her biri kendi bloğunu günceller + canlıya push eder. Sıra önemsiz, çatallanmaz.

## 7. Altın kurallar

1. **Tasarım/UI** → sadece `retrocameraland-hq-dashboard.html` düzenle.
2. **Yol/token** → sadece `rcl_config.py` düzenle.
3. **Bir feed'in verisi/mantığı** → sadece o feed'in scriptini düzenle.
4. `rcl-dashboard/index.html` ve `data.js`'i ELLE düzenleme — otomatik üretilir, üzerine yazılır.
5. Yeni veri bloğu eklemek → `rcl_config.MARKERS`'a ekle + ANA KAYNAĞA `<!-- marker -->` koy + scriptte `write_block()` çağır.
