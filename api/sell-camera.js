// RetroCameraLand - Kamera On Satin Alim basvuru API (Node.js serverless)
// POST (public): Shopify "Kamerani Sat" formundan basvuru alir, fotograflari
//   Vercel Blob'a yukler, kaydi Blob'a JSON olarak yazar, Telegram'a bildirir.
// GET (token):   tum basvurulari listeler (HQ dashboard "Kamera Alim" sekmesi).
// PATCH (token): bir basvurunun durumunu/notunu/teklifini gunceller.
//
// Gerekli env: BLOB_READ_WRITE_TOKEN (Vercel Blob otomatik saglar)
// Opsiyonel:   RCL_ALIM_KEY (dashboard erisim anahtari), TG_BOT_TOKEN, TG_CHAT_ID
import { put, list } from '@vercel/blob';
import crypto from 'node:crypto';

const PREFIX = 'submissions/';
const STATUSES = ['yeni', 'inceleniyor', 'teklif', 'kapandi'];

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-rcl-key');
}
function send(res, status, body) {
  cors(res);
  res.status(status).setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}

function makeId() {
  return crypto.randomBytes(8).toString('hex');
}

function dataUrlToBuffer(dataUrl) {
  const comma = dataUrl.indexOf(',');
  const meta = dataUrl.slice(0, comma);
  const b64 = dataUrl.slice(comma + 1);
  const mime = (meta.match(/data:([^;]+)/) || [])[1] || 'image/jpeg';
  return { buffer: Buffer.from(b64, 'base64'), mime };
}

async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

function authed(req) {
  const need = process.env.RCL_ALIM_KEY || '';
  if (!need) return true; // anahtar tanimli degilse acik (ilk kurulum)
  return req.headers['x-rcl-key'] === need;
}

async function notifyTelegram(rec) {
  const token = process.env.TG_BOT_TOKEN, chatId = process.env.TG_CHAT_ID;
  if (!token || !chatId) return;
  const e = (s) => String(s || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const text =
    '<b>Yeni Kamera Alim Basvurusu</b>\n' +
    'Ref: <code>' + e(rec.ref) + '</code>\n' +
    'Kamera: <b>' + e(rec.model) + '</b>\n' +
    'Beklenti: ' + e(rec.price) + ' TL\n' +
    'Calisiyor: ' + e(rec.working) + ' / ' + e(rec.condition) + '\n' +
    'Ad: ' + e(rec.name) + '  Tel: ' + e(rec.phone) + '\n' +
    'E-posta: ' + e(rec.email) + '  Il: ' + e(rec.city) + '\n' +
    'Foto: ' + (rec.photos ? rec.photos.length : 0) + ' adet';
  try {
    await fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
  } catch (e) { /* bildirim hatasi basvuruyu bozmaz */ }
}

async function sendOfferEmail(rec) {
  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey || !rec.email || !rec.offer) return { skipped: true };
  const amount = String(rec.offer.amount || '').trim();
  const msg = String(rec.offer.message || '').trim();
  const portal = process.env.RCL_PORTAL_URL || 'https://www.retrocameraland.com/pages/basvurularim';
  const e = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const html =
    '<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:0 auto;color:#111">' +
    '<div style="background:#0a0a0b;color:#fff;padding:26px;border-radius:16px 16px 0 0">' +
    '<div style="font-size:12px;letter-spacing:.18em;color:#FF8A3D;font-weight:700">RETROCAMERALAND</div>' +
    '<div style="font-size:22px;font-weight:800;margin-top:6px">Kameran icin teklifimiz hazir</div></div>' +
    '<div style="border:1px solid #eee;border-top:none;border-radius:0 0 16px 16px;padding:26px">' +
    '<p>Merhaba ' + e(rec.name) + ',</p>' +
    '<p><b>' + e(rec.model) + '</b> (Ref: ' + e(rec.ref) + ') basvurun icin teklifimiz:</p>' +
    '<div style="font-size:30px;font-weight:800;color:#FF4D2E;margin:14px 0">' + e(amount) + ' TL</div>' +
    (msg ? '<p style="background:#f6f6f6;border-radius:10px;padding:14px;white-space:pre-wrap">' + e(msg) + '</p>' : '') +
    '<a href="' + e(portal) + '" style="display:inline-block;background:#FF4D2E;color:#fff;text-decoration:none;font-weight:700;padding:13px 24px;border-radius:11px;margin-top:10px">Teklifi Goruntule ve Yanitla</a>' +
    '<p style="color:#888;font-size:13px;margin-top:22px">Sorularin icin bu e-postayi yanitlayabilir veya bizimle iletisime gecebilirsin.</p>' +
    '</div></div>';
  try {
    const r = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: { 'api-key': apiKey, 'Content-Type': 'application/json', accept: 'application/json' },
      body: JSON.stringify({
        sender: { name: 'RetroCameraLand', email: process.env.BREVO_SENDER || 'bilgi@retrocameraland.com' },
        to: [{ email: rec.email, name: rec.name }],
        subject: 'RetroCameraLand - ' + (rec.model || 'Kamera') + ' icin teklifimiz (' + amount + ' TL)',
        htmlContent: html,
      }),
    });
    return { ok: r.ok };
  } catch (e) { return { ok: false, error: String(e) }; }
}

async function loadRecord(id) {
  const res = await list({ prefix: PREFIX + id + '.json', limit: 1 });
  const hit = res.blobs.find((x) => x.pathname === PREFIX + id + '.json');
  if (!hit) return null;
  const r = await fetch(hit.url, { cache: 'no-store' });
  return r.ok ? await r.json() : null;
}
async function saveRecord(rec) {
  await put(PREFIX + rec.id + '.json', JSON.stringify(rec), {
    access: 'public', contentType: 'application/json', addRandomSuffix: false, allowOverwrite: true,
  });
}

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') { cors(res); return res.status(204).end(); }

  // ---- POST: yeni basvuru (public) ----
  if (req.method === 'POST') {
    let b;
    try { b = await readJson(req); } catch (e) { return send(res, 400, { error: 'Gecersiz istek' }); }

    for (const k of ['name', 'phone', 'email', 'model', 'price']) {
      if (!b[k] || !String(b[k]).trim()) return send(res, 400, { error: 'Eksik alan: ' + k });
    }
    const photos = Array.isArray(b.photos) ? b.photos.filter((p) => typeof p === 'string' && p.startsWith('data:')) : [];
    if (photos.length < 1) return send(res, 400, { error: 'En az 1 fotograf gerekli' });
    if (photos.length > 10) return send(res, 400, { error: 'Cok fazla fotograf' });

    const id = makeId();
    const ref = 'RCL-' + id.slice(0, 6).toUpperCase();

    const urls = [];
    try {
      for (let i = 0; i < photos.length; i++) {
        const { buffer, mime } = dataUrlToBuffer(photos[i]);
        const ext = mime.includes('png') ? 'png' : (mime.includes('webp') ? 'webp' : 'jpg');
        const blob = await put(PREFIX + id + '/foto-' + (i + 1) + '.' + ext, buffer, {
          access: 'public', contentType: mime, addRandomSuffix: true,
        });
        urls.push(blob.url);
      }
    } catch (e) {
      return send(res, 500, { error: 'Fotograf yuklenemedi: ' + (e.message || e) });
    }

    const rec = {
      id, ref, createdAt: new Date().toISOString(),
      name: String(b.name).trim(), phone: String(b.phone).trim(), email: String(b.email).trim(),
      city: String(b.city || '').trim(), model: String(b.model).trim(), price: String(b.price).trim(),
      box: String(b.box || '').trim(), working: String(b.working || '').trim(),
      condition: String(b.condition || '').trim(), missing: String(b.missing || '').trim(),
      photos: urls, source: String(b.source || '').trim(), page: String(b.page || '').trim(),
      memberEmail: b.memberEmail ? String(b.memberEmail).trim().toLowerCase() : '',
      status: 'yeni', note: '', offer: null,
    };

    try { await saveRecord(rec); }
    catch (e) { return send(res, 500, { error: 'Kayit yazilamadi: ' + (e.message || e) }); }

    notifyTelegram(rec);
    return send(res, 200, { ok: true, ref, id });
  }

  // ---- bundan sonrasi korumali ----
  if (!authed(req)) return send(res, 401, { error: 'Yetkisiz' });

  // ---- GET: listele ----
  if (req.method === 'GET') {
    try {
      const out = [];
      let cursor;
      do {
        const r = await list({ prefix: PREFIX, cursor, limit: 1000 });
        for (const it of r.blobs) {
          if (!it.pathname.endsWith('.json')) continue;
          try { const j = await fetch(it.url, { cache: 'no-store' }); if (j.ok) out.push(await j.json()); }
          catch (e) { /* bozuk kayit atla */ }
        }
        cursor = r.cursor;
      } while (cursor);
      out.sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''));
      return send(res, 200, { ok: true, items: out });
    } catch (e) {
      return send(res, 500, { error: 'Liste alinamadi: ' + (e.message || e) });
    }
  }

  // ---- PATCH: durum / not / teklif guncelle ----
  if (req.method === 'PATCH') {
    let b;
    try { b = await readJson(req); } catch (e) { return send(res, 400, { error: 'Gecersiz istek' }); }
    if (!b.id) return send(res, 400, { error: 'id gerekli' });
    if (b.status && !STATUSES.includes(b.status)) return send(res, 400, { error: 'Gecersiz durum' });
    try {
      const cur = await loadRecord(b.id);
      if (!cur) return send(res, 404, { error: 'Kayit bulunamadi' });
      if (typeof b.status === 'string') cur.status = b.status;
      if (typeof b.note === 'string') cur.note = b.note;
      let offerJustSent = false;
      if (b.offer && typeof b.offer === 'object') {
        cur.offer = {
          amount: String(b.offer.amount || '').trim(),
          message: String(b.offer.message || '').trim(),
          sentAt: new Date().toISOString(),
          accepted: null,
        };
        cur.status = 'teklif';
        offerJustSent = true;
      }
      // musteri teklifi kabul/red ederse (portal'dan)
      if (typeof b.acceptOffer === 'boolean' && cur.offer) {
        cur.offer.accepted = b.acceptOffer;
        cur.offer.answeredAt = new Date().toISOString();
      }
      cur.updatedAt = new Date().toISOString();
      await saveRecord(cur);
      let email = null;
      if (offerJustSent) email = await sendOfferEmail(cur);
      return send(res, 200, { ok: true, item: cur, email });
    } catch (e) {
      return send(res, 500, { error: 'Guncellenemedi: ' + (e.message || e) });
    }
  }

  return send(res, 405, { error: 'Method Not Allowed' });
}
