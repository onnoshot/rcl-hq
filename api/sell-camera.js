// RetroCameraLand - Kamera On Satin Alim basvuru API
// POST (public): Shopify "Kamerani Sat" formundan basvuru alir, fotograflari
//   Vercel Blob'a yukler, kaydi Blob'a JSON olarak yazar, Telegram'a bildirir.
// GET (token):   tum basvurulari listeler (HQ dashboard "Kamera Alim" sekmesi).
// PATCH (token): bir basvurunun durumunu/notunu gunceller.
//
// Gerekli env: BLOB_READ_WRITE_TOKEN (Vercel Blob otomatik saglar)
// Opsiyonel:   RCL_ALIM_KEY (dashboard erisim anahtari), TG_BOT_TOKEN, TG_CHAT_ID
import { put, list } from '@vercel/blob';

export const config = { runtime: 'edge' };

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, x-rcl-key',
};
const PREFIX = 'submissions/';
const STATUSES = ['yeni', 'inceleniyor', 'teklif', 'kapandi'];

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status: status || 200,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

function makeId() {
  const a = new Uint8Array(8);
  crypto.getRandomValues(a);
  return Array.from(a, (b) => b.toString(16).padStart(2, '0')).join('');
}

function dataUrlToBytes(dataUrl) {
  const comma = dataUrl.indexOf(',');
  const meta = dataUrl.slice(0, comma);
  const b64 = dataUrl.slice(comma + 1);
  const mime = (meta.match(/data:([^;]+)/) || [])[1] || 'image/jpeg';
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return { bytes, mime };
}

function authed(req) {
  const need = (typeof process !== 'undefined' && process.env.RCL_ALIM_KEY) || '';
  if (!need) return true; // anahtar tanimli degilse acik (ilk kurulum)
  return req.headers.get('x-rcl-key') === need;
}

async function notifyTelegram(rec) {
  const token = typeof process !== 'undefined' ? process.env.TG_BOT_TOKEN : null;
  const chatId = typeof process !== 'undefined' ? process.env.TG_CHAT_ID : null;
  if (!token || !chatId) return;
  const esc = (s) => String(s || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const text =
    '<b>Yeni Kamera Alim Basvurusu</b>\n' +
    'Ref: <code>' + esc(rec.ref) + '</code>\n' +
    'Kamera: <b>' + esc(rec.model) + '</b>\n' +
    'Beklenti: ' + esc(rec.price) + ' TL\n' +
    'Durum: ' + esc(rec.working) + ' / ' + esc(rec.condition) + '\n' +
    'Kutu: ' + esc(rec.box) + '\n' +
    'Ad: ' + esc(rec.name) + '\n' +
    'Tel: ' + esc(rec.phone) + '\n' +
    'E-posta: ' + esc(rec.email) + '\n' +
    'Il: ' + esc(rec.city) + '\n' +
    'Foto: ' + (rec.photos ? rec.photos.length : 0) + ' adet';
  try {
    await fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
  } catch (e) { /* bildirim hatasi basvuruyu bozmaz */ }
}

export default async function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

  // ---- POST: yeni basvuru (public) ----
  if (req.method === 'POST') {
    let b;
    try { b = await req.json(); } catch (e) { return json({ error: 'Gecersiz istek' }, 400); }

    const required = ['name', 'phone', 'email', 'model', 'price'];
    for (const k of required) {
      if (!b[k] || !String(b[k]).trim()) return json({ error: 'Eksik alan: ' + k }, 400);
    }
    const photos = Array.isArray(b.photos) ? b.photos.filter((p) => typeof p === 'string' && p.startsWith('data:')) : [];
    if (photos.length < 1) return json({ error: 'En az 1 fotograf gerekli' }, 400);
    if (photos.length > 10) return json({ error: 'Cok fazla fotograf' }, 400);

    const id = makeId();
    const ref = 'RCL-' + id.slice(0, 6).toUpperCase();
    const createdAt = new Date().toISOString();

    // fotograflari yukle
    const urls = [];
    try {
      for (let i = 0; i < photos.length; i++) {
        const { bytes, mime } = dataUrlToBytes(photos[i]);
        const ext = mime.indexOf('png') >= 0 ? 'png' : (mime.indexOf('webp') >= 0 ? 'webp' : 'jpg');
        const blob = await put(PREFIX + id + '/foto-' + (i + 1) + '.' + ext, bytes, {
          access: 'public', contentType: mime, addRandomSuffix: true,
        });
        urls.push(blob.url);
      }
    } catch (e) {
      return json({ error: 'Fotograf yuklenemedi: ' + (e.message || e) }, 500);
    }

    const rec = {
      id, ref, createdAt,
      name: String(b.name).trim(),
      phone: String(b.phone).trim(),
      email: String(b.email).trim(),
      city: String(b.city || '').trim(),
      model: String(b.model).trim(),
      price: String(b.price).trim(),
      box: String(b.box || '').trim(),
      working: String(b.working || '').trim(),
      condition: String(b.condition || '').trim(),
      missing: String(b.missing || '').trim(),
      photos: urls,
      source: String(b.source || '').trim(),
      page: String(b.page || '').trim(),
      status: 'yeni',
      note: '',
    };

    try {
      await put(PREFIX + id + '.json', JSON.stringify(rec), {
        access: 'public', contentType: 'application/json', addRandomSuffix: false, allowOverwrite: true,
      });
    } catch (e) {
      return json({ error: 'Kayit yazilamadi: ' + (e.message || e) }, 500);
    }

    notifyTelegram(rec);
    return json({ ok: true, ref, id });
  }

  // ---- bundan sonrasi korumali ----
  if (!authed(req)) return json({ error: 'Yetkisiz' }, 401);

  // ---- GET: listele ----
  if (req.method === 'GET') {
    try {
      const out = [];
      let cursor;
      do {
        const res = await list({ prefix: PREFIX, cursor, limit: 1000 });
        for (const it of res.blobs) {
          if (!it.pathname.endsWith('.json')) continue;
          try {
            const r = await fetch(it.url, { cache: 'no-store' });
            if (r.ok) out.push(await r.json());
          } catch (e) { /* tek kayit bozuksa atla */ }
        }
        cursor = res.cursor;
      } while (cursor);
      out.sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''));
      return json({ ok: true, items: out });
    } catch (e) {
      return json({ error: 'Liste alinamadi: ' + (e.message || e) }, 500);
    }
  }

  // ---- PATCH: durum/not guncelle ----
  if (req.method === 'PATCH') {
    let b;
    try { b = await req.json(); } catch (e) { return json({ error: 'Gecersiz istek' }, 400); }
    if (!b.id) return json({ error: 'id gerekli' }, 400);
    if (b.status && STATUSES.indexOf(b.status) < 0) return json({ error: 'Gecersiz durum' }, 400);
    try {
      const res = await list({ prefix: PREFIX + b.id + '.json', limit: 1 });
      const hit = res.blobs.find((x) => x.pathname === PREFIX + b.id + '.json');
      if (!hit) return json({ error: 'Kayit bulunamadi' }, 404);
      const cur = await (await fetch(hit.url, { cache: 'no-store' })).json();
      if (typeof b.status === 'string') cur.status = b.status;
      if (typeof b.note === 'string') cur.note = b.note;
      cur.updatedAt = new Date().toISOString();
      await put(PREFIX + b.id + '.json', JSON.stringify(cur), {
        access: 'public', contentType: 'application/json', addRandomSuffix: false, allowOverwrite: true,
      });
      return json({ ok: true, item: cur });
    } catch (e) {
      return json({ error: 'Guncellenemedi: ' + (e.message || e) }, 500);
    }
  }

  return json({ error: 'Method Not Allowed' }, 405);
}
