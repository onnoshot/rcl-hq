// GET /apps/community/leaderboard?range=week|month
// Bu hafta / bu ay en cok begenilen ilk 10 + (giris varsa) uyenin kendi sirasi.
import { verifyProxy, readToken, adminClient, cors } from './core.js';

export async function run(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  res.setHeader('Cache-Control', 's-maxage=45, stale-while-revalidate=120');

  const range = (req.query?.range === 'month') ? 'month' : 'week';
  const view = range === 'month' ? 'leaderboard_month' : 'leaderboard_week';
  const db = adminClient();

  const { data: rows } = await db.from(view)
    .select('id,image_url,camera_model,location,like_count,handle,display_name,avatar_url,customer_id')
    .limit(50);
  const ranked = (rows || []).map((r, i) => ({ rank: i + 1, ...r }));

  const claims = readToken(req);
  let me = null;
  if (claims?.sub) {
    const idx = ranked.findIndex((r) => r.customer_id === claims.sub);
    if (idx >= 0) me = ranked[idx];
  }
  return res.status(200).json({ ok: true, range, top: ranked.slice(0, 10), me, prize: range === 'month' ? '5000 TL' : '1000 TL' });
}
