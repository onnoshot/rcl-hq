// Kamera kartlarina foto yukleme + global feed + begeni + yorum
import { verifyProxy, readToken, adminClient, moderateImage, notifyTelegram, readJson, cors } from './core.js';

const BUCKET = 'community-photos';
const PAGE = 20;

// POST camera-photo { camera_id, image(base64), taken_date, location, note, caption? }
export async function upload(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const { camera_id, image, taken_date, location, note } = b;
  if (!camera_id || !image) return res.status(400).json({ ok: false, error: 'kamera ve fotograf zorunlu' });

  const base64 = String(image).replace(/^data:image\/\w+;base64,/, '');
  const bytes = Buffer.from(base64, 'base64');
  if (bytes.length > 8 * 1024 * 1024) return res.status(413).json({ ok: false, error: 'foto cok buyuk' });

  const mod = await moderateImage(base64);
  const status = mod.clean ? 'approved' : 'pending';
  const db = adminClient();
  const path = 'cam/' + camera_id + '/' + claims.sub + '-' + Date.now() + '.jpg';
  const up = await db.storage.from(BUCKET).upload(path, bytes, { contentType: 'image/jpeg', upsert: false });
  if (up.error) return res.status(500).json({ ok: false, error: 'yukleme' });
  const { data: pub } = db.storage.from(BUCKET).getPublicUrl(path);

  const { data: photo, error } = await db.from('camera_photos').insert({
    camera_id, customer_id: claims.sub, image_url: pub.publicUrl,
    taken_date: taken_date || null, location: location ? String(location).slice(0, 120) : null,
    note: note ? String(note).slice(0, 400) : null, status,
  }).select().single();
  if (error) return res.status(500).json({ ok: false, error: 'kayit' });
  await notifyTelegram('<b>RCL Topluluk - yeni foto</b>\nKamera karti: ' + camera_id + '\nDurum: ' + status);
  return res.status(200).json({ ok: true, photo, moderated: status });
}

// GET feed?cursor=<n>  -> tum onayli fotograflar (kamera + yazar + begeni/yorum)
export async function feed(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();
  const claims = readToken(req);
  const from = parseInt(req.query.cursor || '0', 10) || 0;
  const { data: rows } = await db.from('camera_photos')
    .select('id,image_url,taken_date,location,note,like_count,comment_count,created_at,customer_id,cameras(id,brand,model,image_url),profiles(handle,display_name,avatar_url)')
    .eq('status', 'approved').order('created_at', { ascending: false }).range(from, from + PAGE - 1);

  let liked = new Set();
  if (claims?.sub && rows?.length) {
    const { data: ls } = await db.from('photo_likes').select('photo_id').eq('customer_id', claims.sub).in('photo_id', rows.map((r) => r.id));
    liked = new Set((ls || []).map((l) => l.photo_id));
  }
  const items = (rows || []).map((r) => ({
    id: r.id, image_url: r.image_url, taken_date: r.taken_date, location: r.location, note: r.note,
    like_count: r.like_count, comment_count: r.comment_count, created_at: r.created_at,
    camera: r.cameras ? { id: r.cameras.id, brand: r.cameras.brand, model: r.cameras.model } : null,
    handle: r.profiles?.handle, author: r.profiles?.display_name, avatar: r.profiles?.avatar_url,
    liked: liked.has(r.id),
  }));
  return res.status(200).json({ ok: true, items, next: items.length === PAGE ? from + PAGE : null });
}

// POST photo-like { photo_id, action:'like'|'unlike' }
export async function like(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  if (!b.photo_id) return res.status(400).json({ ok: false });
  const db = adminClient();
  let lerr;
  if (b.action === 'unlike') {
    ({ error: lerr } = await db.from('photo_likes').delete().eq('photo_id', b.photo_id).eq('customer_id', claims.sub));
  } else {
    ({ error: lerr } = await db.from('photo_likes').upsert({ photo_id: b.photo_id, customer_id: claims.sub }, { onConflict: 'photo_id,customer_id', ignoreDuplicates: true }));
  }
  if (lerr) return res.status(400).json({ ok: false, error: 'begeni' });
  const { data: p } = await db.from('camera_photos').select('like_count').eq('id', b.photo_id).maybeSingle();
  return res.status(200).json({ ok: true, like_count: p?.like_count });
}

// GET comments?photo_id=<id>  /  POST comments { photo_id, body }
export async function comments(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();

  if (req.method === 'POST') {
    const claims = readToken(req);
    if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
    let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
    if (!b.photo_id || !b.body || !String(b.body).trim()) return res.status(400).json({ ok: false });
    const { data: c, error } = await db.from('photo_comments')
      .insert({ photo_id: b.photo_id, customer_id: claims.sub, body: String(b.body).slice(0, 500).trim() })
      .select('id,body,created_at,profiles(handle,display_name,avatar_url)').single();
    if (error) return res.status(500).json({ ok: false });
    return res.status(200).json({ ok: true, comment: {
      id: c.id, body: c.body, created_at: c.created_at,
      handle: c.profiles?.handle, author: c.profiles?.display_name, avatar: c.profiles?.avatar_url } });
  }

  const pid = req.query.photo_id;
  if (!pid) return res.status(400).json({ ok: false });
  const { data: rows } = await db.from('photo_comments')
    .select('id,body,created_at,profiles(handle,display_name,avatar_url)')
    .eq('photo_id', pid).order('created_at', { ascending: true }).limit(200);
  return res.status(200).json({ ok: true, comments: (rows || []).map((c) => ({
    id: c.id, body: c.body, created_at: c.created_at,
    handle: c.profiles?.handle, author: c.profiles?.display_name, avatar: c.profiles?.avatar_url })) });
}
