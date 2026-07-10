// RetroCameraLand Topluluk - paylasilan yardimcilar
// Tema HICBIR ZAMAN Supabase ile dogrudan konusmaz: tema -> App Proxy (/apps/community/*)
// -> Shopify HMAC imzalar -> bu Vercel uclari -> Supabase.
import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';
import { createClient } from '@supabase/supabase-js';

// ---- App Proxy HMAC dogrulama (RCL api/hesabim.js ile birebir) ----
export function verifyProxy(query, secret) {
  if (!secret) return false;
  // signature + dispatcher'in ekledigi parametreler (action/type/seg) HMAC disinda kalmali;
  // Shopify bunlari imzalamadi (vercel.json rewrite sonradan ekliyor).
  const { signature, action, type, seg, ...rest } = query;
  if (!signature) return false;
  const msg = Object.keys(rest).sort().map((k) => {
    const v = Array.isArray(rest[k]) ? rest[k].join(',') : rest[k];
    return k + '=' + v;
  }).join('');
  const digest = crypto.createHmac('sha256', secret).update(msg).digest('hex');
  try { return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(String(signature))); }
  catch (e) { return false; }
}

// ---- Topluluk JWT: tema -> upload/vote cagrilarinda Authorization: Bearer ----
// KENDI sirrimizla (COMMUNITY_JWT_SECRET) imzalanir; sadece Vercel dogrular. Supabase'e
// gonderilmez. Yeni Hesaplar'da logged_in_customer_id kirilgan oldugu icin session'da bir
// kez uretilip sonraki cagrilarda kullanilir. Kimligi Vercel dogrular, DB erisimi secret key.
export function mintToken(customerId) {
  return jwt.sign({ sub: String(customerId) }, process.env.COMMUNITY_JWT_SECRET, { expiresIn: '7d' });
}
export function readToken(req) {
  const h = req.headers.authorization || '';
  const t = h.startsWith('Bearer ') ? h.slice(7) : '';
  if (!t) return null;
  try { return jwt.verify(t, process.env.COMMUNITY_JWT_SECRET); } catch (e) { return null; }
}

// ---- Supabase istemcisi ----
// Tema Supabase ile ASLA dogrudan konusmaz (sadece App Proxy -> Vercel). Vercel guvenilir
// sunucu oldugu icin tum DB erisimi SECRET anahtarla yapilir; adillik API + DB kisitlarinda
// (UNIQUE oy, self-vote trigger). Yeni 'sb_secret_...' anahtari da service-role gorevi gorur.
export function adminClient() {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
// Geriye donuk uyumluluk: eski memberClient cagrilari ayni secret istemciyi alir.
export function memberClient() { return adminClient(); }

// ---- Shopify Admin: musteri tenure + siparis sayisi (rozetler icin) ----
export async function fetchShopifyCustomer(customerId) {
  const store = process.env.SHOPIFY_STORE, token = process.env.SHOPIFY_ACCESS_TOKEN;
  if (!store || !token) return null;
  try {
    const r = await fetch('https://' + store + '/admin/api/2024-01/customers/' + customerId + '.json',
      { headers: { 'X-Shopify-Access-Token': token } });
    if (!r.ok) return null;
    const j = await r.json();
    return j.customer || null;
  } catch (e) { return null; }
}

// ---- Telegram bildirim (RCL api/sell-camera.js ile ayni desen) ----
export async function notifyTelegram(text) {
  const bot = process.env.TG_BOT_TOKEN, chat = process.env.TG_CHAT_ID;
  if (!bot || !chat) return;
  try {
    await fetch('https://api.telegram.org/bot' + bot + '/sendMessage', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chat, text, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
  } catch (e) { /* sessiz */ }
}

// ---- Brevo e-posta (RCL sell-camera.js ile ayni desen) ----
export async function sendBrevoEmail(to, subject, html) {
  const key = process.env.BREVO_API_KEY;
  if (!key || !to) return false;
  try {
    const r = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST', headers: { 'api-key': key, 'Content-Type': 'application/json', accept: 'application/json' },
      body: JSON.stringify({
        sender: { email: process.env.BREVO_SENDER_EMAIL || 'bilgi@retrocameraland.com', name: process.env.BREVO_SENDER_NAME || 'RetroCameraLand' },
        to: [{ email: to }], subject, htmlContent: html,
      }),
    });
    return r.ok;
  } catch (e) { return false; }
}

// ---- AWS Rekognition foto moderasyon (opsiyonel; key yoksa otomatik onay) ----
// Basit: dataURL/base64 -> DetectModerationLabels. Key yoksa true (temiz) doner.
export async function moderateImage(bytesBase64) {
  if (!process.env.AWS_ACCESS_KEY_ID) return { clean: true, labels: [] };
  try {
    const { RekognitionClient, DetectModerationLabelsCommand } = await import('@aws-sdk/client-rekognition');
    const c = new RekognitionClient({ region: process.env.AWS_REGION || 'eu-central-1' });
    const out = await c.send(new DetectModerationLabelsCommand({
      Image: { Bytes: Buffer.from(bytesBase64, 'base64') }, MinConfidence: 60,
    }));
    const labels = (out.ModerationLabels || []).map((l) => l.Name);
    return { clean: labels.length === 0, labels };
  } catch (e) { return { clean: true, labels: [], error: String(e) }; }
}

// ---- handle uretimi (benzersiz) ----
export function slugifyHandle(name, customerId) {
  const base = String(name || 'uye').toLowerCase()
    .replace(/[^a-z0-9]+/g, '').slice(0, 16) || 'uye';
  return base + String(customerId).slice(-4);
}

export async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const chunks = []; for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

export function cors(res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
}
