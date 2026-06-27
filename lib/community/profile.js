// Kullanici profili: kendi kameralari + yukledigi fotograflar; profile kamera ekleme
import { verifyProxy, readToken, adminClient, readJson, cors } from './core.js';

// GET profile?handle=<handle>  -> profil + user_cameras + yukledigi fotograflar
export async function get(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const db = adminClient();
  const claims = readToken(req);
  const handle = req.query.handle;
  if (!handle) return res.status(400).json({ ok: false });
  const { data: pr } = await db.from('profiles').select('*').eq('handle', handle).maybeSingle();
  if (!pr) return res.status(404).json({ ok: false });
  const own = !!(claims?.sub && claims.sub === pr.customer_id);

  const { data: cams } = await db.from('user_cameras')
    .select('id,brand,model').eq('customer_id', pr.customer_id).order('created_at', { ascending: false });
  const { data: photos } = await db.from('camera_photos')
    .select('id,image_url,location,taken_date,like_count,cameras(brand,model)')
    .eq('customer_id', pr.customer_id).eq('status', 'approved').order('created_at', { ascending: false }).limit(60);

  // kendi profili: begendigi (oyladigi) kameralar + bekleme listesi
  let votedCameras = [], waitlistCameras = [];
  if (own) {
    const { data: vr } = await db.from('camera_votes')
      .select('cameras(id,brand,model,image_url,year)').eq('voter_id', pr.customer_id).order('created_at', { ascending: false }).limit(60);
    votedCameras = (vr || []).map((x) => x.cameras).filter(Boolean);
    const { data: wr } = await db.from('camera_waitlist')
      .select('cameras(id,brand,model,image_url,year)').eq('customer_id', pr.customer_id).order('created_at', { ascending: false }).limit(60);
    waitlistCameras = (wr || []).map((x) => x.cameras).filter(Boolean);
  }

  return res.status(200).json({
    ok: true, own,
    profile: { handle: pr.handle, display_name: pr.display_name, avatar_url: pr.avatar_url, bio: pr.bio,
      city: pr.city, member_since: pr.member_since },
    cameras: cams || [],
    votedCameras, waitlistCameras,
    photos: (photos || []).map((p) => ({ id: p.id, image_url: p.image_url, location: p.location,
      taken_date: p.taken_date, like_count: p.like_count,
      camera: p.cameras ? p.cameras.brand + ' ' + p.cameras.model : null })),
  });
}

// POST my-camera { brand, model, action? }  -> profile'a kamera ekle/cikar
export async function addCamera(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const db = adminClient();

  if (b.action === 'remove' && b.id) {
    await db.from('user_cameras').delete().eq('id', b.id).eq('customer_id', claims.sub);
  } else {
    if (!b.brand || !b.model) return res.status(400).json({ ok: false, error: 'marka ve model zorunlu' });
    await db.from('user_cameras').upsert(
      { customer_id: claims.sub, brand: String(b.brand).slice(0, 40), model: String(b.model).slice(0, 80) },
      { onConflict: 'customer_id,brand,model', ignoreDuplicates: true });
  }
  const { data: cams } = await db.from('user_cameras')
    .select('id,brand,model').eq('customer_id', claims.sub).order('created_at', { ascending: false });
  return res.status(200).json({ ok: true, cameras: cams || [] });
}
