// Kullanici profili: kendi kameralari + yukledigi fotograflar; profile kamera ekleme; profil duzenleme
import { verifyProxy, readToken, adminClient, readJson, cors, moderateImage } from './core.js';

const BUCKET = 'community-photos';

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

// POST profile-update { display_name?, handle?, avatar?(base64) }  -> uye kendi profilini duzenler
export async function update(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const db = adminClient();
  const patch = { updated_at: new Date().toISOString() };

  if (typeof b.display_name === 'string') {
    const dn = b.display_name.trim().slice(0, 40);
    if (dn) patch.display_name = dn;
  }

  if (typeof b.handle === 'string' && b.handle.trim()) {
    const h = b.handle.trim().toLowerCase().replace(/[^a-z0-9._]/g, '').replace(/^[._]+|[._]+$/g, '').slice(0, 30);
    if (h.length < 3) return res.status(400).json({ ok: false, error: 'Kullanici adi en az 3 karakter olmali' });
    const { data: taken } = await db.from('profiles').select('customer_id').eq('handle', h).maybeSingle();
    if (taken && taken.customer_id !== claims.sub) return res.status(409).json({ ok: false, error: 'Bu kullanici adi alinmis' });
    patch.handle = h;
  }

  if (typeof b.avatar === 'string' && /^data:image\//.test(b.avatar)) {
    const base64 = b.avatar.replace(/^data:image\/\w+;base64,/, '');
    const bytes = Buffer.from(base64, 'base64');
    if (bytes.length > 5 * 1024 * 1024) return res.status(413).json({ ok: false, error: 'Fotograf cok buyuk' });
    const mod = await moderateImage(base64);
    if (!mod.clean) return res.status(400).json({ ok: false, error: 'Gorsel uygun degil' });
    const path = 'avatars/' + claims.sub + '-' + Date.now() + '.jpg';
    const up = await db.storage.from(BUCKET).upload(path, bytes, { contentType: 'image/jpeg', upsert: true });
    if (up.error) return res.status(500).json({ ok: false, error: 'yukleme' });
    const { data: pub } = db.storage.from(BUCKET).getPublicUrl(path);
    patch.avatar_url = pub.publicUrl;
  }

  const { data: pr, error } = await db.from('profiles').update(patch).eq('customer_id', claims.sub)
    .select('handle,display_name,avatar_url,city').single();
  if (error) return res.status(500).json({ ok: false, error: 'guncelleme' });
  return res.status(200).json({ ok: true, profile: pr });
}
