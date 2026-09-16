---
name: shopify-community-platform
description: Build a gamified, members-only community + monthly photo/UGC contest + member profiles + badges + (optional) forum on top of a Shopify store, with a Supabase backend and Vercel serverless auth bridge. Use when the user wants a Shopify "topluluk / community / yarışma / contest / oylama / forum / rozet / leaderboard" experience that stores user-generated content (photos, votes, profiles), gates participation to logged-in customers, awards prizes (gift cards via Admin API), and must be top-tier on mobile, GEO/SEO, and Apple SF-Pro minimal design. Covers the architecture (section liquid + App Proxy + Supabase), gamification mechanics, anti-vote-fraud, prize automation, and UGC schema/GEO.
---

# Shopify Gamified Community Platform Builder

A repeatable playbook for building a **members-only community + recurring UGC contest** on a Shopify
store. The storefront is a Liquid section; the brain is **Supabase** (Postgres + Storage + Realtime +
RLS); the auth/prize bridge is **Vercel serverless** (the user's existing stack). Apple SF-Pro minimal,
mobile-first, GEO/SEO-maxed.

## The one thing you must say out loud first

A Shopify **section/theme is storefront-only** (Liquid/HTML/CSS/JS). It can *render* the logged-in
`customer` object and make `fetch()` calls, but it **cannot store data, authenticate securely, or accept
uploads by itself.** Photo uploads, votes, profiles, forum posts and badges all need an external backend.
So this is never "just a section you paste" — it's `section liquid (UI) → App Proxy (auth) → Vercel
(bridge) → Supabase (data)`. Tell the user this before anything else, or expectations break.

## Architecture (the whole system on one screen)

```
Shopify Theme  (Liquid section, SF Pro, mobile-first)
  ├─ {% if customer %} gate  →  render customer.id / customer.created_at / customer.orders_count
  │     ⇒ tenure + purchase-count BADGES need ZERO backend (read straight from Liquid)
  ├─ exifr (client-side) reads EXIF Make/Model + GPS  ⇒ auto-fills the two REQUIRED fields
  │     (camera model, location), then STRIP EXIF before upload (GPS privacy)
  └─ fetch  →  App Proxy  /apps/community/*   (Shopify appends shop, timestamp, signature, logged_in_customer_id)
                    │  HMAC-SHA256 verified
              Vercel serverless functions   (existing stack)
  ├─ verify App-Proxy HMAC + re-verify customer identity (Admin API)  →  mint own short-lived JWT
  ├─ Shopify Admin API  giftCardCreate (write_gift_cards)  →  weekly/monthly winner prize
  ├─ image moderation (AWS Rekognition DetectModerationLabels ~$0.001/img, 1000/mo free) + Telegram human-in-loop
  └─ Brevo email + Telegram alerts   (already in stack)
                    │
              Supabase   (primary backend)
  ├─ Postgres: profiles, contests, photos, votes, badges, (forum)   + RLS = fairness rules in the DB
  ├─ Storage (or Cloudflare R2 at scale) for images
  └─ Realtime: live vote counts + leaderboards (no WS server to run)
```

Forum: do NOT hand-roll a robust forum unless the user explicitly wants pixel-perfect brand match.
Default to **Discourse on a subdomain** (`forum.brand.com`) + Shopify SSO (Discoursify app) — moderation,
spam, pagination and `DiscussionForumPosting` schema all come free, and AI engines cite forum content
disproportionately (Reddit appears in ~49% of Google AI Overviews). If brand fidelity wins, build a
custom forum on the same Supabase backend and own the schema yourself.

## 2026 gotchas that change the plan (verify, don't assume)

- **Legacy customer accounts were deprecated Feb 2026.** New Customer Accounts (OAuth2 + PKCE, email OTP)
  are default. There's a documented bug: `logged_in_customer_id` arrives **empty/inconsistent** on
  app-proxy requests under New Accounts. ⇒ Treat `logged_in_customer_id` as a best-effort hint; the
  backend must re-verify identity (Admin/Storefront API by id) and mint its own session JWT. App proxies
  also **strip cookies**, so auth is per-request.
- **`customer.*` in Liquid is trustworthy for DISPLAY only.** JS in the theme can spoof an id when POSTing.
  Never trust a client-supplied customer id on a write — verify server-side.
- **Shopify forces URL prefixes** (`/products/`, `/pages/`, ...). For dynamic pages use **App Proxy** —
  Shopify allows exactly four proxy prefixes: `a`, `apps`, `community`, `tools`. Nested routes work
  (`/community/profil/jane`, `/community/yarisma/2026-haziran`). App-proxy pages are NOT in Shopify's
  auto-sitemap and Shopify won't manage their canonicals — you emit canonical tags + host your own sitemap.
- **Prizes:** prefer `giftCardCreate` (stored value, redeemable across orders, can email recipient via
  `recipientAttributes`) over `discountCodeBasicCreate`. Call it **server-side only** with an Admin API
  token (`write_gift_cards` + `read_customers`). Keep issuance **manual-trigger after human verification**
  of the winner (one Telegram tap/week) so you never auto-pay a fraudulent win.

## Phase 0 — Research (always, before building)

Spawn parallel agents: (1) map the store's existing reusable patterns (auth, Vercel APIs, build scripts,
dashboard design system), (2) GEO/SEO for UGC at scale, (3) gamification/UX + technical architecture.
Then confirm the four forks with the user: **backend** (Supabase vs extend Blob), **forum** (Discourse vs
custom vs later), **membership gate** (customers-only ≥1 order vs all registered), **sequencing** (phased
vs all-at-once). These materially change the build and aren't derivable from the repo.

## Phase 1 — Core (ship this first)

Community homepage + contest + photo upload + voting + profiles + badges. Order of work:

1. **Supabase schema** — see `reference/supabase-schema.sql`. Tables: `profiles`, `contests`, `photos`,
   `votes`, `badges`, `user_badges`. Fairness lives in constraints + RLS: `UNIQUE(photo_id, voter_id)`
   (one vote/member/photo), a policy blocking `voter_id == submitter_id` (no self-vote), insert-as-self
   RLS. Leaderboard = a view ranking photos by like-count inside the current week/month window.
2. **Vercel API** — `api/community/session` (App-Proxy HMAC verify → mint JWT), `upload` (verify JWT →
   moderate → Storage → insert `pending`), `vote` (JWT → insert with DB constraints), `profile`,
   `leaderboard`, `award` (cron-triggered winner → `giftCardCreate`). Reuse the store's existing HMAC +
   Telegram + Brevo helpers.
3. **Section liquid** — generated by an **ASCII-safe `build_community.py`** (see the store's
   `build_finder.py`/`build_about.py`). Visible Turkish → `&#NNNN;` HTML entities; JS/JSON/JSON-LD →
   `\uXXXX`. Output must be 100% ASCII (assert at end) so Shopify's editor doesn't double-encode.
   Sections: preloader → glass nav → contest hero (theme + countdown to weekly close = loss-aversion) →
   live "X üye oy veriyor" social proof → CTA "Fotoğrafını yükle" → masonry/justified feed (lazy,
   infinite scroll, double-tap-like) → leaderboard (Bu Hafta / Bu Ay tabs + sticky "sen #14" row) →
   profile drawer (upload grid + badge shelf + tenure/order stats + auto "submission style" summary).
4. **Gamification** — see `reference/gamification.md`. Dual cadence: daily browse/vote streak →
   **weekly** most-liked = 1000 TL gift card (fresh zero every Monday so latecomers stay in) →
   **monthly** most-liked = 5000 TL → seasonal theme reduces blank-canvas friction. Badges on two free
   axes (tenure from `created_at`, purchases from `orders_count`) + achievement axis (contest behavior).
5. **GEO/SEO** — see `reference/geo-schema.md`. Inject `Event` (contest), `ProfilePage`→`Person`,
   `ImageObject`+`creator`, `BreadcrumbList`, site-wide `Organization` with real `sameAs`. **Escape every
   UGC string** (`| escape` / `| json`) or special chars break the JSON-LD (the #1 invalid-schema cause).
   Answer-first first 200 words, question-shaped Turkish H2/H3, 50–150-word self-contained passages,
   FAQ + FAQPage. `noindex,follow` thin/empty profiles & photos & threads; self-canonical valuable pages;
   `rel="ugc nofollow"` on user outbound links; type-split sitemaps with honest `lastmod`; allow
   `OAI-SearchBot`, `PerplexityBot`, `ClaudeBot`/`Claude-SearchBot` and don't block `Googlebot`/`Google-Extended`.

## Phase 2 — Forum + automation (after core proves out)

Discourse subdomain + Shopify SSO; weekly/monthly winner cron → Telegram confirm → `giftCardCreate` →
Brevo congrats → award Week/Month-Winner badge; advanced GEO (llms.txt is native on Shopify since May
2026 — ship it but expect ~0 citation lift; its value is tooling, not ranking).

## Anti-vote-fraud (make-or-break for a cash-prize contest)

Identity gate is your strongest shield. Stack: (1) only logged-in members vote; (2) `UNIQUE(photo_id,
voter_id)` one vote each; (3) block self-vote at API + DB; (4) vote-velocity anomaly flag (spike with no
correlated profile views → human review); (5) reciprocal vote-ring graph check; (6) eligibility freeze
(only members who joined before the contest started can vote in it); (7) **human verification before any
gift card is issued.** If membership = "all registered" (not customers-only), lean harder on 4–7.

## Performance (image-heavy feed — INP is the top risk)

- Like/vote buttons: **optimistic UI** (update count instantly, reconcile in background, revert on fail;
  never disable the button), then `await globalThis.scheduler?.yield?.()` before the background write.
- Hero/first photo: `fetchpriority="high"`, never `loading="lazy"`; AVIF→WebP via `<picture>` + `srcset`.
- Every `<img>` explicit `width`/`height` or `aspect-ratio`; lock grid-cell ratios (CLS).
- Below fold: native `loading="lazy"` + `content-visibility:auto` + `contain-intrinsic-size`; infinite
  scroll via debounced IntersectionObserver sentinel (`rootMargin:200px`), not scroll events.
- Targets (mobile, p75): LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1.

## EXIF auto-fill (biggest UX win)

The two *required* fields users dread (camera model, location) are usually already in the photo. Use
`exifr` in the browser: `Make`+`Model` → camera field; `exifr.gps()` → reverse-geocode (OpenCage/Nominatim)
→ location field. User just confirms/corrects. **Then strip EXIF before upload/display** (canvas
re-encode or piexifjs) so you never publish someone's home GPS. Camera-make data also powers brand-loyalist
badges and image-SEO alt text (`alt="Canon AE-1 35mm fotoğraf, İstanbul'da çekildi"`).

## Notes / reuse

- Reuse the store's existing App-Proxy HMAC verify, Telegram notify, Brevo email, and ASCII build helpers
  rather than re-writing them. For RCL: `api/sell-camera.js`, `api/hesabim.js`, `build_finder.py`,
  `retrocameraland-hq-dashboard.html` design system (SF Pro, obsidian, 24px radius, inline SVG icons).
- Add new HQ-dashboard tabs (submissions, leaderboard, community activity) by forking that design system.
- Photo storage: start on Supabase Storage; migrate hot blobs to Cloudflare R2 only if egress bills justify.
- Reference files in this skill: `reference/supabase-schema.sql`, `reference/gamification.md`,
  `reference/geo-schema.md`, `reference/vercel-api-patterns.md`.
