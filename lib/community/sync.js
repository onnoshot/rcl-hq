// Shopify magazasindaki urunleri Time Capsule 'cameras' kataloguna OTOMATIK senkron eder.
// Yeni urun ekledigimde buraya da gelsin: gunluk Vercel cron (Authorization: Bearer CRON_SECRET)
// veya elle: GET /api/community/sync?key=<RCL_ALIM_KEY>
// ONEMLI: mevcut kameralarda base_score / year / highlight / photo_count KORUNUR (payloadda yok).
import crypto from 'node:crypto';
import { adminClient } from './core.js';

function safeEq(a, b) {
  const x = Buffer.from(String(a || '')), y = Buffer.from(String(b || ''));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

// Bilinen markalar (basligin icinden cikar). 'Fuji' -> 'Fujifilm'.
const BRANDS = ['Sony', 'Canon', 'Nikon', 'Fujifilm', 'Fuji', 'Casio', 'Olympus', 'Panasonic', 'Lumix',
  'Kodak', 'Pentax', 'Samsung', 'Sanyo', 'Rollei', 'Ricoh', 'Leica', 'Minolta', 'Konica', 'Sigma',
  'GoPro', 'Polaroid', 'Agfa', 'Praktica', 'Yashica', 'BenQ', 'Toshiba', 'Vivitar', 'Contax', 'JVC'];
function deriveBrand(title, vendor) {
  const t = String(title || '');
  for (const b of BRANDS) {
    if (new RegExp('\\b' + b + '\\b', 'i').test(t)) return b === 'Fuji' ? 'Fujifilm' : (b === 'Lumix' ? 'Panasonic' : b);
  }
  if (vendor && !/retro\s*camera\s*land/i.test(vendor)) return vendor;
  return (t.split(/\s+/)[0] || 'Diger');
}

// body_html -> duz metin (gercek urun aciklamasi); kargo/iade baslamis kaliplari at
function htmlToText(html) {
  if (!html) return null;
  let t = String(html)
    .replace(/<\s*(br|\/p|\/div|\/li|\/h[1-6])\s*>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/&#39;|&rsquo;|&lsquo;/gi, "'")
    .replace(/&quot;/gi, '"').replace(/&lt;/gi, '<').replace(/&gt;/gi, '>')
    .replace(/[ \t]+/g, ' ').replace(/\n{2,}/g, '\n').replace(/^\s+|\s+$/gm, '').trim();
  // kargo/iade/garanti boilerplate satirlarini ele
  t = t.split('\n').filter((ln) => ln && !/kargo|iade|garanti|whatsapp|sat[ıi]n al|sipari[şs]|stokta|ücretsiz/i.test(ln)).join(' ');
  t = t.replace(/\s{2,}/g, ' ').trim();
  return t ? t.slice(0, 700) : null;
}

export async function run(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  const q = req.query || {};
  const auth = req.headers.authorization || '';
  const cronOk = process.env.CRON_SECRET && auth === 'Bearer ' + process.env.CRON_SECRET;
  const keyOk = process.env.RCL_ALIM_KEY && safeEq(q.key, process.env.RCL_ALIM_KEY);
  if (!cronOk && !keyOk) return res.status(401).json({ ok: false, error: 'yetki' });

  const store = process.env.SHOPIFY_PUBLIC_DOMAIN || 'retrocameraland.com';
  let page = 1, all = [];
  for (; page <= 20; page++) {
    let r;
    try { r = await fetch('https://' + store + '/products.json?limit=250&page=' + page); }
    catch (e) { break; }
    if (!r.ok) break;
    const j = await r.json();
    const prods = (j && j.products) || [];
    all = all.concat(prods);
    if (prods.length < 250) break;
  }
  if (!all.length) return res.status(502).json({ ok: false, error: 'urun cekilemedi' });

  const rows = all.map((p) => {
    const v = (p.variants && p.variants[0]) || {};
    const img = (p.images && p.images[0] && p.images[0].src) || (p.image && p.image.src) || null;
    return {
      handle: p.handle,
      brand: deriveBrand(p.title, p.vendor),
      model: p.title,
      title: p.title,
      image_url: img,
      price: v.price != null && v.price !== '' ? Number(v.price) : null,
      product_url: 'https://' + store + '/products/' + p.handle,
      description: htmlToText(p.body_html),
      source: 'catalog',
    };
  }).filter((r) => r.handle && r.model);

  const db = adminClient();
  // 200'luk parcalarla upsert (handle cakismasinda guncelle; eksik kolonlar korunur)
  let upserted = 0;
  for (let i = 0; i < rows.length; i += 200) {
    const chunk = rows.slice(i, i + 200);
    const { error } = await db.from('cameras').upsert(chunk, { onConflict: 'handle', ignoreDuplicates: false });
    if (error) return res.status(500).json({ ok: false, error: error.message, upserted });
    upserted += chunk.length;
  }
  return res.status(200).json({ ok: true, fetched: all.length, upserted });
}
