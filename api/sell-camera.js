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

async function tgSend(text) {
  const token = process.env.TG_BOT_TOKEN, chatId = process.env.TG_CHAT_ID;
  if (!token || !chatId) return;
  try {
    await fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
  } catch (e) { /* bildirim hatasi akisi bozmaz */ }
}

async function notifyTelegram(rec) {
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
  await tgSend(text);
}

async function sendOfferEmail(rec) {
  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey || !rec.email || !rec.offer) return { skipped: true };
  const amount = String(rec.offer.amount || '').trim();
  const msg = String(rec.offer.message || '').trim();
  const base = process.env.RCL_PORTAL_URL || 'https://www.retrocameraland.com/pages/teklif';
  const portal = base + (base.includes('?') ? '&' : '?') + 'id=' + rec.id + '&t=' + (rec.token || '');
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

// Her basvuruda Shopify musterisini olustur/etiketle (musteri datasi toplama).
// write_customers scope'u yoksa sessizce atlar; basvuruyu asla bozmaz.
async function upsertShopifyCustomer(rec) {
  const store = process.env.SHOPIFY_STORE, token = process.env.SHOPIFY_ACCESS_TOKEN;
  if (!store || !token) return { skipped: true };
  const base = 'https://' + store + '/admin/api/2024-01';
  const H = { 'X-Shopify-Access-Token': token, 'Content-Type': 'application/json' };
  const note = 'Kamera Alim: ' + rec.model + ' | Beklenti: ' + rec.price + ' TL | Tel: ' + rec.phone + ' | Ref: ' + rec.ref;
  const parts = (rec.name || '').trim().split(/\s+/);
  const first = parts.shift() || rec.name || 'Musteri';
  const last = parts.join(' ');
  try {
    const sr = await fetch(base + '/customers/search.json?query=' + encodeURIComponent('email:' + rec.email), { headers: H });
    const sj = sr.ok ? await sr.json() : { customers: [] };
    const found = (sj.customers || [])[0];
    if (found) {
      const tags = (found.tags ? found.tags + ', ' : '') + 'kamera-satici';
      await fetch(base + '/customers/' + found.id + '.json', {
        method: 'PUT', headers: H,
        body: JSON.stringify({ customer: { id: found.id, tags, note } }),
      });
      return { ok: true, id: found.id, existed: true };
    }
    const cr = await fetch(base + '/customers.json', {
      method: 'POST', headers: H,
      body: JSON.stringify({ customer: { first_name: first, last_name: last, email: rec.email, tags: 'kamera-satici', note } }),
    });
    const cj = cr.ok ? await cr.json() : null;
    return { ok: cr.ok, id: cj && cj.customer ? cj.customer.id : null };
  } catch (e) { return { ok: false, error: String(e) }; }
}

// Blob CDN, ayni URL'i onbellekte tutar; mutable kayitlari okurken
// cache-bust query'si ekleyerek her zaman taze veri aliriz.
function bust(url) { return url + (url.includes('?') ? '&' : '?') + '_cb=' + Date.now(); }

async function loadRecord(id) {
  const res = await list({ prefix: PREFIX + id + '.json', limit: 1 });
  const hit = res.blobs.find((x) => x.pathname === PREFIX + id + '.json');
  if (!hit) return null;
  const r = await fetch(bust(hit.url), { cache: 'no-store' });
  return r.ok ? await r.json() : null;
}
async function saveRecord(rec) {
  await put(PREFIX + rec.id + '.json', JSON.stringify(rec), {
    access: 'public', contentType: 'application/json', addRandomSuffix: false,
    allowOverwrite: true, cacheControlMaxAge: 0,
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
    // Fotograflar, kayit id'sinden BAGIMSIZ rastgele bir klasorde saklanir;
    // boylece bir foto URL'i sizsa bile PII kaydinin yolu (submissions/<id>.json)
    // tahmin edilemez.
    const photoDir = makeId();
    try {
      for (let i = 0; i < photos.length; i++) {
        const { buffer, mime } = dataUrlToBuffer(photos[i]);
        const ext = mime.includes('png') ? 'png' : (mime.includes('webp') ? 'webp' : 'jpg');
        const blob = await put('photos/' + photoDir + '/foto-' + (i + 1) + '.' + ext, buffer, {
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
      token: makeId() + makeId(),
      status: 'yeni', note: '', offer: null,
    };

    // Shopify musterisi olustur/etiketle (best-effort) — kaydetmeden once
    try { const c = await upsertShopifyCustomer(rec); if (c && c.id) rec.shopifyCustomerId = c.id; }
    catch (e) { /* musteri olusmazsa basvuru yine kaydedilir */ }

    try { await saveRecord(rec); }
    catch (e) { return send(res, 500, { error: 'Kayit yazilamadi: ' + (e.message || e) }); }

    await notifyTelegram(rec);
    return send(res, 200, { ok: true, ref, id });
  }

  // ===== MUSTERI (PUBLIC, token ile) =====
  // Tek basvuru goruntule:  GET ?id=...&t=token
  if (req.method === 'GET' && req.query && req.query.id && req.query.t) {
    try {
      const cur = await loadRecord(String(req.query.id));
      if (!cur || !cur.token || cur.token !== String(req.query.t)) return send(res, 404, { error: 'Basvuru bulunamadi' });
      const pub = {
        id: cur.id, ref: cur.ref, createdAt: cur.createdAt, name: cur.name, model: cur.model, price: cur.price,
        working: cur.working, condition: cur.condition, box: cur.box, status: cur.status, photos: cur.photos, offer: cur.offer,
      };
      return send(res, 200, { ok: true, item: pub });
    } catch (e) { return send(res, 500, { error: String(e) }); }
  }
  // Teklife yanit ver:  PATCH {id, token, acceptOffer:true|false}
  if (req.method === 'PATCH' && req.body && req.body.token) {
    let b;
    try { b = await readJson(req); } catch (e) { return send(res, 400, { error: 'Gecersiz istek' }); }
    try {
      const cur = await loadRecord(String(b.id || ''));
      if (!cur || !cur.token || cur.token !== String(b.token)) return send(res, 404, { error: 'Basvuru bulunamadi' });
      if (typeof b.acceptOffer !== 'boolean' || !cur.offer) return send(res, 400, { error: 'Yanitlanacak teklif yok' });
      cur.offer.accepted = b.acceptOffer;
      cur.offer.answeredAt = new Date().toISOString();
      cur.status = b.acceptOffer ? 'kapandi' : cur.status;
      cur.updatedAt = new Date().toISOString();
      await saveRecord(cur);
      await tgSend('<b>' + (b.acceptOffer ? 'TEKLIF KABUL EDILDI ' : 'TEKLIF REDDEDILDI ') + '</b>\n' +
        'Ref: <code>' + cur.ref + '</code>  ' + (cur.model || '') + '\n' +
        'Tutar: ' + (cur.offer.amount || '') + ' TL\n' +
        'Musteri: ' + (cur.name || '') + '  ' + (cur.phone || ''));
      return send(res, 200, { ok: true, item: { id: cur.id, ref: cur.ref, model: cur.model, status: cur.status, offer: cur.offer } });
    } catch (e) { return send(res, 500, { error: 'Yanit kaydedilemedi: ' + (e.message || e) }); }
  }

  // ===== ADMIN (korumali) =====
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
          try { const j = await fetch(bust(it.url), { cache: 'no-store' }); if (j.ok) out.push(await j.json()); }
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
        if (!cur.token) cur.token = makeId() + makeId(); // eski kayitlara token ekle
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
