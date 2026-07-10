// RetroCameraLand - AI Kamera Eslestirici (kamera bulucu) log API (serverless)
// POST (public): Shopify "Kamera Bulucu" testinden bir tamamlama kaydi alir,
//   Vercel Blob'a JSON yazar, Telegram'a kisa bildirim atar.
// GET (token):   tum test kayitlarini listeler (HQ dashboard "Kamera Bulucu" sekmesi).
//
// Gerekli env: BLOB_READ_WRITE_TOKEN (Vercel Blob otomatik saglar)
// Opsiyonel:   RCL_ALIM_KEY (dashboard erisim anahtari - alim ile ayni),
//              TG_BOT_TOKEN, TG_CHAT_ID (Telegram bildirim)
import { put, list } from '@vercel/blob';
import crypto from 'node:crypto';

const PREFIX = 'finder/';

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-rcl-key');
}
function send(res, status, body) {
  cors(res);
  res.status(status).setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));
}
function makeId() { return crypto.randomBytes(8).toString('hex'); }

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
function bust(url) { return url + (url.includes('?') ? '&' : '?') + '_cb=' + Date.now(); }

// Kullanici girdisini guvenle stringe cevir, kisalt.
function s(v, max) { return String(v == null ? '' : v).trim().slice(0, max || 120); }
// Etiket dizisi (cevap secimleri) temizle.
function arr(v, max) {
  if (!Array.isArray(v)) return [];
  return v.filter((x) => typeof x === 'string').map((x) => s(x, 80)).slice(0, max || 8);
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

async function saveRecord(rec) {
  await put(PREFIX + rec.id + '.json', JSON.stringify(rec), {
    access: 'public', contentType: 'application/json', addRandomSuffix: false,
    allowOverwrite: true, cacheControlMaxAge: 0,
  });
}

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') { cors(res); return res.status(204).end(); }

  // ---- POST: yeni test tamamlama (public) VEYA mevcut kaydi guncelleme (begen/begenme, e-posta) ----
  if (req.method === 'POST') {
    let b;
    try { b = await readJson(req); } catch (e) { return send(res, 400, { error: 'Gecersiz istek' }); }

    // ---- UPDATE: sonuc ekranindaki begen/begenmedim veya e-posta opt-in, ayni teste islenir ----
    if (b.id && !b.name) {
      const fid = s(b.id, 40);
      if (!fid) return send(res, 400, { error: 'Eksik alan: id' });
      try {
        const path = PREFIX + fid + '.json';
        const r = await list({ prefix: path, limit: 1 });
        const blob = r.blobs.find((x) => x.pathname === path);
        if (!blob) return send(res, 404, { error: 'Kayit bulunamadi' });
        const existing = await (await fetch(bust(blob.url), { cache: 'no-store' })).json();
        if (b.feedback === 'like' || b.feedback === 'dislike') existing.feedback = b.feedback;
        if (b.email) existing.email = s(b.email, 120);
        existing.updatedAt = new Date().toISOString();
        await saveRecord(existing);
        return send(res, 200, { ok: true });
      } catch (e) { return send(res, 500, { error: 'Guncellenemedi: ' + (e.message || e) }); }
    }

    if (!b.name || !String(b.name).trim()) return send(res, 400, { error: 'Eksik alan: name' });

    const id = makeId();
    const ref = 'RCLF-' + id.slice(0, 6).toUpperCase();
    const recs = Array.isArray(b.recommended) ? b.recommended.slice(0, 3).map((r) => ({
      title: s(r && r.title, 120), brand: s(r && r.brand, 60),
      pct: Number(r && r.pct) || 0, handle: s(r && r.handle, 160),
    })) : [];

    const rec = {
      id, ref, createdAt: new Date().toISOString(),
      sid: s(b.sid, 40),                 // tarayici oturum id'si (tekil kisi sayimi icin)
      name: s(b.name, 80),
      age: s(b.age, 30),
      gender: s(b.gender, 30),
      city: s(b.city, 60),
      // cevap secimleri (her soru icin secilen etiketler - coklu secim)
      // sema: use, budget, aes, level (4 soru); env/occasion/size/pers eski surumlerden geriye-donuk
      answers: {
        use: arr(b.use, 5),
        budget: arr(b.budget, 4),
        aes: arr(b.aes, 3),
        level: arr(b.level, 3),
        // geriye donuk uyumluluk (eski testler)
        env: arr(b.env, 4),
        occasion: arr(b.occasion, 3),
        size: arr(b.size, 3),
        pers: arr(b.pers, 5),
      },
      // onerilen ilk kameranin markasi/fiyati - reklam/segment analizi icin
      top_brand: s(b.top_brand, 60),
      top_price: Number(b.top_price) || 0,
      recommended: recs,
      // sonuc ekranindaki begen/begenmedim + "haber ver" e-posta opt-in (sonradan logUpdate ile islenir)
      feedback: '',
      email: '',
      source: s(b.source, 60), page: s(b.page, 160),
      ua: s(req.headers['user-agent'], 200),
    };

    try { await saveRecord(rec); }
    catch (e) { return send(res, 500, { error: 'Kayit yazilamadi: ' + (e.message || e) }); }

    const e = (x) => String(x || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const topCam = recs[0] ? (recs[0].title + ' (%' + recs[0].pct + ')') : '-';
    const j = (a) => e((a || []).join(', ')) || '-';
    await tgSend(
      '<b>Kamera Bulucu - yeni test</b>\n' +
      'Ref: <code>' + e(ref) + '</code>\n' +
      'Kisi: <b>' + e(rec.name) + '</b>  ' + e(rec.age) + ' / ' + e(rec.gender) + '\n' +
      'Sehir: ' + e(rec.city) + '\n' +
      'Kullanim: ' + j(rec.answers.use) + '\n' +
      'Butce: ' + j(rec.answers.budget) + '  |  Seviye: ' + j(rec.answers.level) + '\n' +
      'Vesile: ' + j(rec.answers.occasion) + '\n' +
      'En uyumlu: ' + e(topCam)
    );
    return send(res, 200, { ok: true, ref, id });
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

  return send(res, 405, { error: 'Method Not Allowed' });
}
