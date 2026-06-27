// Time Capsule geri bildirim toplama + dashboard istatistikleri
import { verifyProxy, readToken, adminClient, readJson, cors } from './core.js';

// POST feedback { rating(1-5), category, message }  (App Proxy + oturum)
export async function submit(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const rating = Math.max(1, Math.min(5, parseInt(b.rating, 10) || 0)) || null;
  if (!rating && !b.message) return res.status(400).json({ ok: false });
  const db = adminClient();
  await db.from('feedback').insert({
    customer_id: claims?.sub || null, rating,
    category: b.category ? String(b.category).slice(0, 40) : 'genel',
    message: b.message ? String(b.message).slice(0, 800) : null,
  });
  return res.status(200).json({ ok: true });
}

// GET stats?key=<RCL_ALIM_KEY>  -> dashboard icin tum istatistikler (App Proxy DEGIL, token)
export async function stats(req, res) {
  cors(res);
  if (!req.query.key || req.query.key !== process.env.RCL_ALIM_KEY)
    return res.status(401).json({ ok: false });
  const db = adminClient();
  const count = async (t, f) => {
    let q = db.from(t).select('id', { count: 'exact', head: true });
    if (f) q = f(q);
    const { count: c } = await q; return c || 0;
  };
  const [users, cams, votes, photos, likes, comments, fb] = await Promise.all([
    count('profiles'), count('cameras'), count('camera_votes'),
    count('camera_photos'), count('photo_likes'), count('photo_comments'), count('feedback'),
  ]);

  // feedback dagilimi
  const { data: fbRows } = await db.from('feedback')
    .select('rating,category,message,created_at,profiles(handle,display_name)')
    .order('created_at', { ascending: false }).limit(200);
  const byRating = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }, byCat = {};
  let ratingSum = 0, ratingN = 0;
  (fbRows || []).forEach((r) => {
    if (r.rating) { byRating[r.rating] = (byRating[r.rating] || 0) + 1; ratingSum += r.rating; ratingN++; }
    if (r.category) byCat[r.category] = (byCat[r.category] || 0) + 1;
  });

  // en cok oylanan kameralar
  const { data: topCams } = await db.from('cameras')
    .select('brand,model,score,votes_count,photo_count,image_url').order('score', { ascending: false }).limit(10);
  // en cok begenilen fotograflar
  const { data: topPhotos } = await db.from('camera_photos')
    .select('image_url,location,like_count,comment_count,cameras(brand,model)')
    .eq('status', 'approved').order('like_count', { ascending: false }).limit(8);
  // marka dagilimi (oy toplami)
  const { data: brandRows } = await db.from('cameras').select('brand,votes_count,photo_count');
  const brandAgg = {};
  (brandRows || []).forEach((r) => {
    brandAgg[r.brand] = brandAgg[r.brand] || { brand: r.brand, votes: 0, photos: 0, cameras: 0 };
    brandAgg[r.brand].votes += r.votes_count; brandAgg[r.brand].photos += r.photo_count; brandAgg[r.brand].cameras++;
  });
  const brands = Object.values(brandAgg).sort((a, b) => b.votes - a.votes);

  return res.status(200).json({
    ok: true,
    totals: { users, cameras: cams, votes, photos, likes, comments, feedback: fb },
    feedback: {
      avgRating: ratingN ? +(ratingSum / ratingN).toFixed(2) : null,
      byRating, byCategory: byCat,
      recent: (fbRows || []).slice(0, 40).map((r) => ({
        rating: r.rating, category: r.category, message: r.message, created_at: r.created_at,
        author: r.profiles?.display_name || r.profiles?.handle || 'Uye' })),
    },
    topCameras: topCams || [], topPhotos: topPhotos || [], brands,
  });
}
