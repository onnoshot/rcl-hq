// RetroCameraLand - "Basvurularim" Shopify App Proxy ucu (guvenli).
// Shopify, /apps/hesabim isteklerini buraya imzali (signature) + logged_in_customer_id
// ile yonlendirir. Imzayi SHOPIFY_APP_PROXY_SECRET ile dogrularik; musteri SADECE
// kendi basvurularini gorur (IDOR yok).
//
// GET  /apps/hesabim            -> giris yapan musterinin tum basvuru+teklifleri
// POST /apps/hesabim {id,acceptOffer} -> teklifi kabul/red (sahiplik dogrulanir)
//
// Env: SHOPIFY_APP_PROXY_SECRET (app'in API secret key'i), SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN
import { list } from '@vercel/blob';
import crypto from 'node:crypto';

const PREFIX = 'submissions/';
const SELF = 'https://rclhq.vercel.app/api/sell-camera';

function bust(u) { return u + (u.includes('?') ? '&' : '?') + '_cb=' + Date.now(); }

function verifyProxy(query, secret) {
  if (!secret) return false;
  const { signature, ...rest } = query;
  if (!signature) return false;
  const msg = Object.keys(rest).sort().map((k) => {
    const v = Array.isArray(rest[k]) ? rest[k].join(',') : rest[k];
    return k + '=' + v;
  }).join('');
  const digest = crypto.createHmac('sha256', secret).update(msg).digest('hex');
  try { return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(String(signature))); }
  catch (e) { return false; }
}

async function customerEmail(customerId) {
  const store = process.env.SHOPIFY_STORE, token = process.env.SHOPIFY_ACCESS_TOKEN;
  if (!store || !token) return null;
  try {
    const r = await fetch('https://' + store + '/admin/api/2024-01/customers/' + customerId + '.json', {
      headers: { 'X-Shopify-Access-Token': token },
    });
    if (!r.ok) return null;
    const j = await r.json();
    return j.customer ? String(j.customer.email || '').toLowerCase() : null;
  } catch (e) { return null; }
}

async function allRecords() {
  const out = [];
  let cursor;
  do {
    const r = await list({ prefix: PREFIX, cursor, limit: 1000 });
    for (const it of r.blobs) {
      if (!it.pathname.endsWith('.json')) continue;
      try { const j = await fetch(bust(it.url), { cache: 'no-store' }); if (j.ok) out.push(await j.json()); }
      catch (e) { /* atla */ }
    }
    cursor = r.cursor;
  } while (cursor);
  return out;
}

function owns(rec, email, cid) {
  return String(rec.email || '').toLowerCase() === email ||
    String(rec.memberEmail || '').toLowerCase() === email ||
    (cid && String(rec.shopifyCustomerId || '') === String(cid));
}

async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

export default async function handler(req, res) {
  const q = req.query || {};
  if (!verifyProxy(q, process.env.SHOPIFY_APP_PROXY_SECRET)) {
    res.status(401).json({ error: 'Imza dogrulanamadi' }); return;
  }
  res.setHeader('Content-Type', 'application/json');

  const cid = q.logged_in_customer_id;
  if (!cid) { res.status(200).json({ ok: true, loggedIn: false, items: [] }); return; }
  const email = await customerEmail(cid);
  if (!email) { res.status(200).json({ ok: true, loggedIn: true, items: [] }); return; }

  // ---- POST: teklife yanit ----
  if (req.method === 'POST') {
    let b; try { b = await readJson(req); } catch (e) { res.status(400).json({ error: 'Gecersiz istek' }); return; }
    const recs = await allRecords();
    const rec = recs.find((r) => r.id === b.id);
    if (!rec || !owns(rec, email, cid)) { res.status(404).json({ error: 'Basvuru bulunamadi' }); return; }
    if (typeof b.acceptOffer !== 'boolean' || !rec.offer) { res.status(400).json({ error: 'Yanitlanacak teklif yok' }); return; }
    // ana uca, kaydin kendi token'iyla ilet (kabul + tum bildirimler orada calisir)
    try {
      const r = await fetch(SELF, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: rec.id, token: rec.token, acceptOffer: b.acceptOffer }),
      });
      const j = await r.json().catch(() => ({}));
      res.status(r.ok ? 200 : 500).json(j); return;
    } catch (e) { res.status(500).json({ error: 'Yanit kaydedilemedi' }); return; }
  }

  // ---- GET: musterinin kendi basvurulari ----
  const recs = await allRecords();
  const mine = recs.filter((r) => owns(r, email, cid));
  mine.sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''));
  const items = mine.map((r) => ({
    id: r.id, ref: r.ref, createdAt: r.createdAt, model: r.model, price: r.price,
    working: r.working, condition: r.condition, box: r.box, status: r.status, photos: r.photos, offer: r.offer,
  }));
  res.status(200).json({ ok: true, loggedIn: true, email, count: items.length, items });
}
