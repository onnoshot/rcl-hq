// GET  /apps/community/profile?handle=<handle>   -> profil + fotograflar + rozetler + "tarz ozeti"
// POST /apps/community/profile  { bio, city, avatar_url }  -> kendi profilini guncelle (JWT)
import { verifyProxy, readToken, adminClient, memberClient, readJson, cors } from './_lib.js';

export default async function handler(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });

  const db = adminClient();

  if (req.method === 'POST') {
    const claims = readToken(req);
    if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });
    let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
    const token = (req.headers.authorization || '').slice(7);
    const m = memberClient(token);
    await m.from('profiles').update({
      bio: b.bio ? String(b.bio).slice(0, 280) : null,
      city: b.city ? String(b.city).slice(0, 60) : null,
      avatar_url: b.avatar_url || null, updated_at: new Date().toISOString(),
    }).eq('customer_id', claims.sub);
    return res.status(200).json({ ok: true });
  }

  const handle = req.query?.handle;
  if (!handle) return res.status(400).json({ ok: false });
  const { data: pr } = await db.from('profiles').select('*').eq('handle', handle).maybeSingle();
  if (!pr) return res.status(404).json({ ok: false });

  const { data: photos } = await db.from('photos')
    .select('id,image_url,camera_model,location,like_count,created_at')
    .eq('customer_id', pr.customer_id).eq('status', 'approved')
    .order('created_at', { ascending: false }).limit(60);
  const { data: badges } = await db.from('user_badges')
    .select('badge_key,badges(label,axis,icon)').eq('customer_id', pr.customer_id);

  // "tarz ozeti": en cok kullanilan kamera markasi + en cok cekilen konum
  const makeCount = {}, locCount = {};
  (photos || []).forEach((p) => {
    const make = (p.camera_model || '').split(' ')[0]; if (make) makeCount[make] = (makeCount[make] || 0) + 1;
    if (p.location) locCount[p.location] = (locCount[p.location] || 0) + 1;
  });
  const top = (o) => Object.entries(o).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

  return res.status(200).json({
    ok: true,
    profile: { handle: pr.handle, display_name: pr.display_name, avatar_url: pr.avatar_url, bio: pr.bio,
      city: pr.city, member_since: pr.member_since, orders_count: pr.orders_count, total_likes: pr.total_likes },
    style: { top_camera: top(makeCount), top_location: top(locCount), photo_count: (photos || []).length },
    photos: photos || [], badges: badges || [],
  });
}
