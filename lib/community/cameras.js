// Kamera siralama / oylama / marka kategorileri
import { verifyProxy, readToken, adminClient, readJson, cors } from './core.js';

const PAGE = 30;

// GET cameras?brand=<marka>&cursor=<n>  -> puana gore sirali kameralar (+ kullanicinin oyu)
export async function list(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();
  const claims = readToken(req);
  const from = parseInt(req.query.cursor || '0', 10) || 0;
  const brand = req.query.brand && req.query.brand !== 'all' ? req.query.brand : null;
  const sort = req.query.sort || 'pop';   // pop | year_new | year_old | brand

  let q = db.from('cameras')
    .select('id,handle,brand,model,title,image_url,price,product_url,score,votes_count,photo_count,year,highlight')
    .range(from, from + PAGE - 1);
  if (sort === 'year_new') q = q.order('year', { ascending: false, nullsFirst: false }).order('score', { ascending: false });
  else if (sort === 'year_old') q = q.order('year', { ascending: true, nullsFirst: false }).order('score', { ascending: false });
  else if (sort === 'brand') q = q.order('brand', { ascending: true }).order('score', { ascending: false });
  else q = q.order('score', { ascending: false });
  if (brand) q = q.eq('brand', brand);
  const { data: rows } = await q;

  let voted = new Set();
  if (claims?.sub && rows?.length) {
    const ids = rows.map((r) => r.id);
    const { data: mine } = await db.from('camera_votes').select('camera_id').eq('voter_id', claims.sub).in('camera_id', ids);
    voted = new Set((mine || []).map((v) => v.camera_id));
  }
  const items = (rows || []).map((r, i) => ({ ...r, rank: from + i + 1, voted: voted.has(r.id) }));
  return res.status(200).json({ ok: true, items, next: items.length === PAGE ? from + PAGE : null });
}

// GET brands -> her markanin kamera sayisi + en yuksek puanli ornegi
export async function brands(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();
  const { data: rows } = await db.from('cameras')
    .select('brand,score,image_url,model').order('score', { ascending: false });
  const map = {};
  (rows || []).forEach((r) => {
    if (!map[r.brand]) map[r.brand] = { brand: r.brand, count: 0, top_image: r.image_url, top_model: r.model, top_score: r.score };
    map[r.brand].count++;
  });
  const out = Object.values(map).sort((a, b) => b.count - a.count);
  return res.status(200).json({ ok: true, brands: out });
}

// GET camera?id=<uuid>  -> kamera detayi + kartindaki fotograflar
export async function detail(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();
  const claims = readToken(req);
  const id = req.query.id;
  if (!id) return res.status(400).json({ ok: false });
  const { data: cam } = await db.from('cameras').select('*').eq('id', id).maybeSingle();
  if (!cam) return res.status(404).json({ ok: false });
  const { data: photos } = await db.from('camera_photos')
    .select('id,image_url,taken_date,location,note,like_count,comment_count,created_at,customer_id,profiles(handle,display_name,avatar_url)')
    .eq('camera_id', id).eq('status', 'approved').order('created_at', { ascending: false }).limit(60);
  const { count: waitCount } = await db.from('camera_waitlist').select('camera_id', { count: 'exact', head: true }).eq('camera_id', id);

  let voted = false, liked = new Set(), onWait = false;
  if (claims?.sub) {
    const { data: v } = await db.from('camera_votes').select('camera_id').eq('camera_id', id).eq('voter_id', claims.sub).maybeSingle();
    voted = !!v;
    const { data: w } = await db.from('camera_waitlist').select('camera_id').eq('camera_id', id).eq('customer_id', claims.sub).maybeSingle();
    onWait = !!w;
    if (photos?.length) {
      const { data: ls } = await db.from('photo_likes').select('photo_id').eq('customer_id', claims.sub).in('photo_id', photos.map((p) => p.id));
      liked = new Set((ls || []).map((l) => l.photo_id));
    }
  }
  const ph = (photos || []).map((p) => ({
    id: p.id, image_url: p.image_url, taken_date: p.taken_date, location: p.location, note: p.note,
    like_count: p.like_count, comment_count: p.comment_count, created_at: p.created_at,
    handle: p.profiles?.handle, author: p.profiles?.display_name, avatar: p.profiles?.avatar_url,
    liked: liked.has(p.id),
  }));
  return res.status(200).json({ ok: true, camera: { ...cam, voted, waitCount: waitCount || 0, onWait }, photos: ph });
}

// POST camera-waitlist { camera_id, action:'join'|'leave' }  -> bekleme listesi
export async function waitlist(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  if (!b.camera_id) return res.status(400).json({ ok: false });
  const db = adminClient();
  if (b.action === 'leave') {
    await db.from('camera_waitlist').delete().eq('camera_id', b.camera_id).eq('customer_id', claims.sub);
  } else {
    await db.from('camera_waitlist').upsert({ camera_id: b.camera_id, customer_id: claims.sub }, { onConflict: 'camera_id,customer_id', ignoreDuplicates: true });
  }
  const { count } = await db.from('camera_waitlist').select('camera_id', { count: 'exact', head: true }).eq('camera_id', b.camera_id);
  return res.status(200).json({ ok: true, count: count || 0, joined: b.action !== 'leave' });
}

// POST camera-vote { camera_id, action:'up'|'down' }
export async function vote(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  if (!b.camera_id) return res.status(400).json({ ok: false });
  const db = adminClient();
  if (b.action === 'down') {
    await db.from('camera_votes').delete().eq('camera_id', b.camera_id).eq('voter_id', claims.sub);
  } else {
    await db.from('camera_votes').upsert({ camera_id: b.camera_id, voter_id: claims.sub }, { onConflict: 'camera_id,voter_id', ignoreDuplicates: true });
  }
  const { data: cam } = await db.from('cameras').select('score,votes_count').eq('id', b.camera_id).maybeSingle();
  return res.status(200).json({ ok: true, score: cam?.score, votes_count: cam?.votes_count, voted: b.action !== 'down' });
}
