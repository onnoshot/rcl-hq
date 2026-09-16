# Vercel serverless patterns (the auth/prize bridge)

The theme NEVER talks to Supabase directly. It calls the App Proxy (`/apps/community/*`), Shopify forwards
to Vercel with an HMAC `signature` + `logged_in_customer_id`, Vercel verifies and talks to Supabase with
the **service-role key** (server-only). This keeps the Supabase service key and Admin API token off the
client.

## App-Proxy HMAC verify (reuse RCL's exact helper — api/hesabim.js)

```js
import crypto from 'node:crypto';
function verifyProxy(query, secret) {
  if (!secret) return false;
  const { signature, ...rest } = query;
  if (!signature) return false;
  const msg = Object.keys(rest).sort().map((k) => {
    const v = Array.isArray(rest[k]) ? rest[k].join(',') : rest[k];
    return k + '=' + v;               // sorted, key=value, NO delimiter
  }).join('');
  const digest = crypto.createHmac('sha256', secret).update(msg).digest('hex');
  try { return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(String(signature))); }
  catch (e) { return false; }
}
```
Env: `SHOPIFY_APP_PROXY_SECRET` (the app's API secret), `SHOPIFY_STORE`, `SHOPIFY_ACCESS_TOKEN`.

## The New-Customer-Accounts gotcha → mint your own JWT

`logged_in_customer_id` can be empty under New Customer Accounts. Pattern: `/apps/community/session`
verifies HMAC; if `logged_in_customer_id` present → upsert profile (pull `created_at`/`orders_count` from
Admin API for badges) → mint a short-lived HS256 JWT with `sub = customer_id`. The theme caches that JWT
(sessionStorage) and sends it on upload/vote/profile calls. The Vercel handlers verify the JWT, then set
the Supabase request claim so RLS sees `auth_member_id() = sub`.

```js
// mint
import jwt from 'jsonwebtoken';
const token = jwt.sign({ sub: customerId }, process.env.COMMUNITY_JWT_SECRET, { expiresIn: '2h' });
// verify + scoped Supabase client (RLS-aware)
import { createClient } from '@supabase/supabase-js';
function memberClient(sub) {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
    global: { headers: { /* claim set via PostgREST: */ } },
    auth: { persistSession: false },
  });
  // simplest: use service key + pass sub explicitly to SECURITY DEFINER RPCs that re-check sub,
  // OR set request.jwt.claims via a signed Supabase JWT whose 'sub' = customerId.
}
```
Practical simplest-robust route: issue a **Supabase-signed JWT** (sign with the Supabase JWT secret,
`sub = customerId`, `role = 'authenticated'`) so PostgREST sets `request.jwt.claims` and your RLS
`auth_member_id()` works with the anon/authenticated client — no service key on hot paths.

## Endpoints (Phase 1)

| Route | Method | Does |
|---|---|---|
| `/apps/community/session` | GET | HMAC verify → upsert profile (badges from Admin API) → return community JWT + profile |
| `/apps/community/upload` | POST | verify JWT → moderate (Rekognition) → Storage put (EXIF already stripped client-side) → insert photo `pending` → Telegram alert |
| `/apps/community/vote` | POST | verify JWT → insert vote (DB enforces unique + self-vote block) → return new count |
| `/apps/community/unvote` | POST | verify JWT → delete own vote |
| `/apps/community/feed` | GET | approved photos for a contest, paginated (keyset on `like_count,created_at`) |
| `/apps/community/leaderboard` | GET | `leaderboard_week` / `leaderboard_month` view, cached ~30–60s |
| `/apps/community/profile` | GET/POST | read/update own profile |

## Prize automation (Phase 2) — giftCardCreate, server-only

```js
// Admin GraphQL — needs write_gift_cards + read_customers
const q = `mutation($input: GiftCardCreateInput!){
  giftCardCreate(input:$input){ giftCard{ id maskedCode } userErrors{ field message } } }`;
const input = { initialValue: "1000.00", customerId: "gid://shopify/Customer/123",
  note: "Haftalık yarışma ödülü", recipientAttributes: { id: "gid://shopify/Customer/123",
  message: "Tebrikler! Bu haftanın kazananı sensin." } };
```
Trigger from a weekly/monthly cron → query top photo from `leaderboard_week/month` → Telegram "confirm
winner?" → on tap, call `giftCardCreate` → record `gift_card_id` + award Week/Month-Winner badge + Brevo
congrats. Keep human-in-the-loop; never auto-pay.

## Moderation pipeline

Client strips EXIF (canvas re-encode / piexifjs) and uploads → Vercel runs AWS Rekognition
`DetectModerationLabels` (~$0.001/img, 1000/mo free) → clean auto-`approved`, flagged → `pending` +
Telegram for human decision. Insert with `status` accordingly.

## Reuse map (RCL)

- HMAC verify + `customerEmail()` Admin lookup + `readJson()` → `api/hesabim.js`
- Telegram `notifyTelegram()` / Brevo `sendOfferEmail()` → `api/sell-camera.js`
- Blob/dashboard ingestion + design system → `retrocameraland-hq-dashboard.html`
- ASCII-safe build (`E()` entities + `ld()` `\uXXXX`) → `build_finder.py` / `build_about.py`
