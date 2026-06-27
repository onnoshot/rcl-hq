// Time Capsule yonetim paneli ucu - HEPSI RCL_ALIM_KEY ile korunur (App Proxy DEGIL).
// Genel bakis, kullanicilar, bekleme listesi, anilar + ani sil/duzenle (admin).
import crypto from 'node:crypto';
import { adminClient } from './core.js';

function safeEq(a, b) {
  const x = Buffer.from(String(a || '')), y = Buffer.from(String(b || ''));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}
function auth(req, res) {
  cors(res);
  const key = (req.query && req.query.key) || (req.headers['x-admin-key']);
  if (!process.env.RCL_ALIM_KEY || !safeEq(key, process.env.RCL_ALIM_KEY)) {
    res.status(401).json({ ok: false, error: 'yetki' });
    return false;
  }
  return true;
}
function cors(res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'content-type,x-admin-key');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
}

// GET admin?key=  -> genel bakis (KPI + en cok oylanan + marka + geri bildirim ozeti)
export async function overview(req, res) {
  if (!auth(req, res)) return;
  const db = adminClient();
  const cnt = async (t) => { const { count } = await db.from(t).select('*', { count: 'exact', head: true }); return count || 0; };
  const [users, cams, votes, photos, likes, comments, waitlist, feedback] = await Promise.all([
    cnt('profiles'), cnt('cameras'), cnt('camera_votes'), cnt('camera_photos'),
    cnt('photo_likes'), cnt('photo_comments'), cnt('camera_waitlist'), cnt('feedback'),
  ]);
  const { count: pending } = await db.from('camera_photos').select('*', { count: 'exact', head: true }).eq('status', 'pending');
  const { count: priv } = await db.from('camera_photos').select('*', { count: 'exact', head: true }).eq('visibility', 'private');
  const { data: topCams } = await db.from('cameras')
    .select('handle,brand,model,score,base_score,votes_count,photo_count,image_url')
    .order('score', { ascending: false }).limit(25);
  const { data: brandRows } = await db.from('cameras').select('brand,votes_count,photo_count');
  const bAgg = {};
  (brandRows || []).forEach((r) => { (bAgg[r.brand] = bAgg[r.brand] || { brand: r.brand, votes: 0, photos: 0, cameras: 0 }); bAgg[r.brand].votes += r.votes_count; bAgg[r.brand].photos += r.photo_count; bAgg[r.brand].cameras++; });
  const brands = Object.values(bAgg).sort((a, b) => b.votes - a.votes);
  const { data: fb } = await db.from('feedback').select('rating,category,message,created_at,profiles(handle,display_name)').order('created_at', { ascending: false }).limit(60);
  const byRating = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }; let rs = 0, rn = 0;
  (fb || []).forEach((r) => { if (r.rating) { byRating[r.rating]++; rs += r.rating; rn++; } });
  return res.status(200).json({
    ok: true,
    totals: { users, cameras: cams, votes, photos, likes, comments, waitlist, feedback, pending: pending || 0, private: priv || 0 },
    topCameras: (topCams || []).map((c) => ({ ...c, seed: c.base_score, real: c.votes_count })),
    brands,
    feedback: { avg: rn ? +(rs / rn).toFixed(2) : null, byRating, recent: (fb || []).map((r) => ({ rating: r.rating, category: r.category, message: r.message, created_at: r.created_at, author: r.profiles?.display_name || r.profiles?.handle || 'Uye' })) },
  });
}

// GET admin-users?key=  -> kullanicilar + ani/oy/yorum sayilari
export async function users(req, res) {
  if (!auth(req, res)) return;
  const db = adminClient();
  const { data: profs } = await db.from('profiles').select('customer_id,handle,display_name,city,member_since,avatar_url').order('member_since', { ascending: false }).limit(1000);
  const [{ data: ph }, { data: vt }, { data: cm }, { data: wl }] = await Promise.all([
    db.from('camera_photos').select('customer_id'),
    db.from('camera_votes').select('voter_id'),
    db.from('photo_comments').select('customer_id'),
    db.from('camera_waitlist').select('customer_id'),
  ]);
  const tally = (rows, k) => { const m = {}; (rows || []).forEach((r) => { m[r[k]] = (m[r[k]] || 0) + 1; }); return m; };
  const pm = tally(ph, 'customer_id'), vm = tally(vt, 'voter_id'), cmm = tally(cm, 'customer_id'), wm = tally(wl, 'customer_id');
  const list = (profs || []).map((p) => ({
    handle: p.handle, display_name: p.display_name, city: p.city, avatar_url: p.avatar_url,
    member_since: p.member_since, seed: String(p.customer_id || '').startsWith('seed-'),
    photos: pm[p.customer_id] || 0, votes: vm[p.customer_id] || 0, comments: cmm[p.customer_id] || 0, waitlist: wm[p.customer_id] || 0,
  }));
  return res.status(200).json({ ok: true, users: list });
}

// GET admin-waitlist?key=  -> kamera basina bekleyenler
export async function waitlist(req, res) {
  if (!auth(req, res)) return;
  const db = adminClient();
  const { data: wl } = await db.from('camera_waitlist')
    .select('camera_id,created_at,cameras(brand,model,image_url),profiles(handle,display_name,avatar_url)')
    .order('created_at', { ascending: false }).limit(2000);
  const map = {};
  (wl || []).forEach((r) => {
    const c = r.cameras; if (!c) return;
    const key = c.brand + ' ' + c.model;
    map[key] = map[key] || { camera: key, image_url: c.image_url, people: [] };
    map[key].people.push({ handle: r.profiles?.handle, display_name: r.profiles?.display_name, avatar_url: r.profiles?.avatar_url, at: r.created_at });
  });
  const groups = Object.values(map).sort((a, b) => b.people.length - a.people.length);
  return res.status(200).json({ ok: true, total: (wl || []).length, groups });
}

// GET admin-photos?key=&cursor=&status=  -> anilar (moderasyon)
export async function photos(req, res) {
  if (!auth(req, res)) return;
  const db = adminClient();
  const from = parseInt(req.query.cursor || '0', 10) || 0;
  const PAGE = 60;
  let q = db.from('camera_photos')
    .select('id,image_url,note,location,taken_date,status,visibility,like_count,comment_count,created_at,customer_id,cameras(brand,model),profiles(handle,display_name)')
    .order('created_at', { ascending: false }).range(from, from + PAGE - 1);
  if (req.query.status && ['pending', 'approved', 'rejected'].includes(req.query.status)) q = q.eq('status', req.query.status);
  const { data: rows } = await q;
  const items = (rows || []).map((r) => ({
    id: r.id, image_url: r.image_url, note: r.note, location: r.location, taken_date: r.taken_date,
    status: r.status, visibility: r.visibility, like_count: r.like_count, comment_count: r.comment_count, created_at: r.created_at,
    camera: r.cameras ? r.cameras.brand + ' ' + r.cameras.model : null,
    author: r.profiles?.display_name || r.profiles?.handle || 'Uye', handle: r.profiles?.handle,
    seed: String(r.customer_id || '').startsWith('seed-'),
  }));
  return res.status(200).json({ ok: true, items, next: items.length === PAGE ? from + PAGE : null });
}

// POST admin-photo  { key, action:'delete'|'edit', id, note?, location?, status?, visibility? }
export async function photoAction(req, res) {
  if (req.method === 'OPTIONS') { cors(res); return res.status(200).end(); }
  if (!auth(req, res)) return;
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  let b; try { b = typeof req.body === 'object' && req.body ? req.body : JSON.parse(await readRaw(req)); } catch (e) { return res.status(400).json({ ok: false }); }
  if (!b.id) return res.status(400).json({ ok: false });
  const db = adminClient();
  if (b.action === 'delete') {
    const { data: ph } = await db.from('camera_photos').select('image_url').eq('id', b.id).maybeSingle();
    const { error } = await db.from('camera_photos').delete().eq('id', b.id);
    if (error) return res.status(500).json({ ok: false, error: 'silme' });
    try { const m = String(ph?.image_url || '').match(/community-photos\/(.+)$/); if (m) await db.storage.from('community-photos').remove([m[1]]); } catch (e) {}
    return res.status(200).json({ ok: true, deleted: true });
  }
  const patch = {};
  if (typeof b.note === 'string') patch.note = b.note.slice(0, 400);
  if (typeof b.location === 'string') patch.location = b.location.slice(0, 120);
  if (['pending', 'approved', 'rejected'].includes(b.status)) patch.status = b.status;
  if (['public', 'private'].includes(b.visibility)) patch.visibility = b.visibility;
  if (!Object.keys(patch).length) return res.status(400).json({ ok: false });
  const { data: up, error } = await db.from('camera_photos').update(patch).eq('id', b.id).select('id,note,location,status,visibility').single();
  if (error) return res.status(500).json({ ok: false, error: 'guncelleme' });
  return res.status(200).json({ ok: true, photo: up });
}

async function readRaw(req) {
  const chunks = []; for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8') || '{}';
}
