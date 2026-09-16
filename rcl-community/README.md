# RetroCameraLand Topluluk — oyunlaştırılmış yarışma + profil + rozet sistemi

Üyelere özel, oyunlaştırılmış topluluk: aylık fotoğraf yarışması, oylama, profiller, rozetler.
Mimari: **Shopify section (UI) → App Proxy (kimlik) → Vercel (köprü) → Supabase (veri)**.
Apple SF Pro, mobil-öncelikli, GEO/SEO uyumlu. Forum + kazanan otomasyonu = Faz 2.

> **Önemli:** Bu "sadece yapıştırılan bir section" değil. Section görsel katman; fotoğraf yükleme,
> oylama, profil ve rozetler için Supabase backend + Vercel köprüsü gerekir. Adımlar aşağıda.

## Dosyalar

```
rcl-community/
├─ build_community.py          # ASCII-safe section üretici  -> sections/rcl-topluluk.liquid
├─ sections/rcl-topluluk.liquid# Shopify'a yapıştıracağın section (otomatik üretildi)
├─ supabase/schema.sql         # Supabase SQL Editor'e yapıştır (tablolar + RLS + rozet/yarışma seed)
└─ api/community/              # Vercel serverless uçları (App Proxy arkasında)
   ├─ _lib.js                  # HMAC doğrulama, JWT, Supabase istemcileri, Telegram, moderasyon
   ├─ session.js              # /apps/community/session  -> JWT + profil + rozet ver
   ├─ upload.js               # /apps/community/upload   -> moderasyon + Storage + insert
   ├─ vote.js                 # /apps/community/vote     -> oy (tekil + self-vote engeli DB'de)
   ├─ feed.js                 # /apps/community/feed     -> onaylı fotoğraflar, sayfalı
   ├─ leaderboard.js          # /apps/community/leaderboard -> bu hafta / bu ay
   ├─ profile.js              # /apps/community/profile  -> profil + tarz özeti + rozetler
   └─ award.js                # FAZ 2: kazanana giftCardCreate (Telegram onayıyla)
```

## Kurulum (Faz 1)

### 1) Supabase
1. supabase.com'da yeni proje. **SQL Editor** → `supabase/schema.sql` içeriğini yapıştır → RUN.
2. **Storage** → `community-photos` adında **public** bucket oluştur.
3. **Settings → API**'den 2 şey al: `Project URL` → `SUPABASE_URL`, `secret key` (sb_secret_…) → `SUPABASE_SERVICE_KEY`. (anon key / JWT secret gerekmez — tema Supabase'e dokunmaz.) Ayrıca `COMMUNITY_JWT_SECRET` için uzun rastgele bir dize üret.

### 2) Shopify — YENİ uygulama YOK (mevcut RCL uygulamasını yeniden kullan)
Bir Shopify uygulaması yalnızca **tek bir App Proxy** yoluna sahip olabilir; mevcut uygulaman zaten
`/apps/hesabim → api/hesabim.js` proxy'sini kullanıyor. Community'yi onun **altına** bindiriyoruz:
- Community section App Proxy yolu = `/apps/hesabim/community`
- Vercel `vercel.json` rewrite'ı `/api/hesabim/community/*` → `/api/community/*` bağlar (repoda hazır).
- Shopify tarafında **hiçbir değişiklik gerekmez**, mevcut `SHOPIFY_APP_PROXY_SECRET` aynen kullanılır.
- `SHOPIFY_ACCESS_TOKEN` (sell-camera/hesabim'in kullandığı) aynen kullanılır. **`write_gift_cards`
  gerekmez** — ödüller artık senin elinle hazırladığın sabit kodlarla paylaşılıyor (aşağıda).

### 3) Vercel
`api/community/` klasörünü + `vercel.json`'ı mevcut rclhq projene koy. Env (`.env.example`):
```
SUPABASE_URL + SUPABASE_SERVICE_KEY (sb_secret_...) + COMMUNITY_JWT_SECRET   (anon/JWT secret GEREKMEZ)
SHOPIFY_STORE/ACCESS_TOKEN/APP_PROXY_SECRET     (zaten var)
TG_BOT_TOKEN/TG_CHAT_ID, BREVO_API_KEY/SENDER   (zaten var)
PRIZE_CODE_WEEK=OZELWIN1000  PRIZE_CODE_MONTH=WIN5000   (ödül kodları - sen hazırlarsın)
RCL_ALIM_KEY (moderasyon paneli)  RCL_COMMUNITY_BASE=https://rclhq.vercel.app
AWS_ACCESS_KEY_ID/SECRET/REGION  (opsiyonel moderasyon - yoksa otomatik onay)
```
`npm i` (api/package.json: `@supabase/supabase-js`, `jsonwebtoken`, `@aws-sdk/client-rekognition`).

### 4) Shopify section
1. `sections/rcl-topluluk.liquid` içeriğini kopyala.
2. Admin → **Online Store → Themes → Edit code → Sections → Add new** → `rcl-topluluk` → yapıştır → Save.
   (Türkçe karakterler `&#NNNN;` olarak ASCII; editör bozmaz.)
3. **Online Store → Pages → Add page** → "Topluluk", URL `/pages/topluluk`. Theme template'e section ekle.
4. Section ayarları: App Proxy yolu **`/apps/hesabim/community`**, yarışma slug `2026-haziran`, vurgu `#FF4D2E`.

### 5) robots.txt (GEO — AI aramaları)
`robots.txt.liquid`'de `robots.default_groups` döngüsüne ekle: `OAI-SearchBot`, `PerplexityBot`,
`ClaudeBot`/`Claude-SearchBot` allow; `Googlebot`/`Google-Extended` engelleme. `/community/` ve foto
CDN crawlanabilir kalsın.

## Nasıl çalışıyor (akış)

1. Üye sayfaya girer → `{% if customer %}` UI'yi açar → section `/apps/community/session` çağırır →
   Shopify HMAC imzalar + `logged_in_customer_id` ekler → Vercel doğrular, Shopify'dan kıdem+sipariş çeker,
   **tenure + purchase rozetlerini otomatik verir**, kısa ömürlü JWT döner.
2. Foto yükle: tarayıcıda **exifr** EXIF'ten kamera modeli + GPS→konum otomatik doldurur (zorunlu 2 alan),
   EXIF temizlenir (canvas), base64 → `/upload` → moderasyon → Supabase Storage → `pending|approved`.
3. Oy: **optimistik UI** (sayaç anında artar) + `scheduler.yield()` → `/vote`. DB tekil-oy + self-vote
   engelini zorlar. Çift-dokunuş = beğen.
4. Lider tablosu: `leaderboard_week` / `leaderboard_month` view'ları; sticky "senin sıran" satırı.

## Oyunlaştırma & adillik
- **Çift cadence:** haftalık birinci 1000 TL, aylık birinci 5000 TL. Her pazartesi sıfırlanır → geç
  katılanlar oyunda kalır.
- **Rozetler:** kıdem (`created_at`) + alışveriş (`orders_count`) Shopify'dan **bedava**; başarı rozetleri
  (Haftanın/Ayın Kazananı, Sharpshooter, Globetrotter, marka sadığı) yarışma davranışından.
- **Anti-hile:** giriş zorunlu, `UNIQUE(photo_id,voter_id)`, self-vote engeli (API+DB), hız anomalisi
  (gece sorgusu), kazanan **insan onayı** olmadan çek basılmaz. Üyelik "tüm kayıtlılar" seçildiği için
  hız anomalisi + onay adımına yaslan.

## Faz 2 — KOD HAZIR (kurulum aşağıda)

Faz 2 bileşenleri yazıldı ve doğrulandı; canlıya almak için kurulum gerekiyor:

1. **GEO server-render sayfaları** (`api/community/page.js` + `vercel.json`): App Proxy
   `/apps/community/profil/<handle>`, `/foto/<id>`, `/yarisma/<slug>` → `application/liquid` (tema içinde
   render) + `ProfilePage`/`ImageObject`/`Event` JSON-LD + kendi canonical'ı. İnce profiller `noindex,follow`.
   `api/community/sitemap.js` → topluluk sitemap'i (Search Console'a `/apps/community/sitemap` ekle).
   - Section'daki `@handle` ve foto linklerini bu URL'lere bağlamak için (opsiyonel) section'ı
     güncelleyebiliriz; şu an profil section içi drawer'da açılıyor, SEO sayfaları ayrıca indekslenir.

2. **Moderasyon paneli** (`rcl-community-admin.html` + `api/community/moderate.js`): tarayıcıda aç,
   `RCL_ALIM_KEY` gir → bekleyen fotoğrafları Onayla/Reddet, sayaçlar. (AWS moderasyon kapalıysa fotolar
   `pending` gelir ve burada onaylanır; açıksa temizler otomatik `approved`.)

3. **Kazanan otomasyonu** (`api/community/award.js` + `scripts/award-cron.sh` + 2 LaunchAgent plist):
   Pazartesi 10:00 haftalık, ayın 1'i aylık → kazananı bulur, **senin Shopify'da hazırladığın sabit
   indirim kodunu** kazanana e-postayla (Brevo) yollar + sana Telegram bildirir + kazanan rozeti verir.
   Çek BASILMAZ. Kodlar env'den: `PRIZE_CODE_WEEK=OZELWIN1000`, `PRIZE_CODE_MONTH=WIN5000`. İdempotent
   (aynı dönem 2 kez göndermez). Test: `…/api/community/award?range=week&dry` (sadece aday + kod gösterir).
   Kur: plist yollarını kontrol et → `cp scripts/*.plist ~/Library/LaunchAgents/` →
   `launchctl load ~/Library/LaunchAgents/com.retrocameraland.community.award-*.plist`.

4. **Forum:** `FORUM_SETUP.md` — Discourse subdomain + DiscourseConnect SSO (`api/community/discourse-sso.js`
   hazır: Shopify hesabıyla tek girişle foruma geçiş). Moderasyon/spam/`DiscussionForumPosting` şeması
   otomatik; AI aramaları forum içeriğini orantısız alıntılar.

5. **İleri GEO (sonra):** robots.txt AI-bot allow (aşağıda), llms.txt (Shopify native), FAQ blokları,
   soru-başlıklı içerik, tazelik sinyalleri.

### Faz 2 ek env (api/community)
```
DISCOURSE_URL=https://forum.retrocameraland.com   DISCOURSE_SSO_SECRET=...
RCL_ALIM_KEY=...            # moderasyon paneli (HQ ile ayni token)
PRIZE_CODE_WEEK=OZELWIN1000   PRIZE_CODE_MONTH=WIN5000   # senin hazirladigin sabit kodlar
RCL_COMMUNITY_BASE=https://rclhq.vercel.app
```

## Notlar
- Section'ı her değiştirdiğinde `python3 build_community.py` çalıştır (ASCII assert + JS `node --check`).
- Skill: `.claude/skills/shopify-community-platform/` — bu metodolojinin tamamı (mimari, GEO, oyunlaştırma,
  Vercel desenleri, Supabase şema) tekrar kullanılabilir halde.
