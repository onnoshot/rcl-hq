// GET /apps/community/feed?contest=<slug>&sort=new|top&cursor=<n>
// Onayli fotograflar, sayfali. Giris yapan uyenin verdigi oylar 'liked' ile isaretlenir.
import { verifyProxy, readToken, adminClient, cors } from './core.js';

const PAGE = 24;

export async function run(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });

  const q = req.query || {};
  const claims = readToken(req); // opsiyonel: giris yoksa da feed gorunur
  const db = adminClient();

  const slug = q.contest || '2026-haziran';
  const { data: contest } = await db.from('contests').select('id').eq('slug', slug).maybeSingle();
  if (!contest) return res.status(200).json({ ok: true, items: [], next: null });

  const from = parseInt(q.cursor || '0', 10) || 0;
  const order = q.sort === 'new' ? { col: 'created_at', asc: false } : { col: 'like_count', asc: false };

  const { data: rows } = await db.from('photos')
    .select('id,image_url,camera_model,location,caption,like_count,created_at,customer_id,profiles(handle,display_name,avatar_url)')
    .eq('contest_id', contest.id).eq('status', 'approved')
    .order(order.col, { ascending: order.asc }).order('created_at', { ascending: false })
    .range(from, from + PAGE - 1);

  let liked = new Set();
  if (claims?.sub && rows?.length) {
    const ids = rows.map((r) => r.id);
    const { data: mine } = await db.from('votes').select('photo_id').eq('voter_id', claims.sub).in('photo_id', ids);
    liked = new Set((mine || []).map((v) => v.photo_id));
  }

  const items = (rows || []).map((r) => ({
    id: r.id, image_url: r.image_url, camera_model: r.camera_model, location: r.location,
    caption: r.caption, like_count: r.like_count, created_at: r.created_at,
    handle: r.profiles?.handle, author: r.profiles?.display_name, avatar: r.profiles?.avatar_url,
    liked: liked.has(r.id), mine: claims?.sub === r.customer_id,
  }));
  const next = items.length === PAGE ? from + PAGE : null;
  return res.status(200).json({ ok: true, items, next });
}
