// Time Capsule - Gorev / Rozet sistemi (oyunlastirma).
// Kullanicinin gercek eylemleri sayilir, esige ulasinca rozet + odul kuponu acilir.
// Kupon kodlari Shopify'da SEN olusturursun; env ile gercek koda baglanir (yoksa varsayilan placeholder).
import { verifyProxy, readToken, adminClient, cors } from './core.js';

function QUESTS() {
  const e = process.env;
  return [
    { key: 'vote10',   icon: 'heart',   title: 'Oy Verici',      desc: '10 kameraya beğeni ver',                target: 10, metric: 'votes',
      reward: { label: 'Ücretsiz Kargo',  code: e.COUPON_VOTE10  || 'KARGOBEDAVA' } },
    { key: 'photo3',   icon: 'camera',  title: 'Anı Avcısı',     desc: '3 anı yükle',                           target: 3,  metric: 'photos',
      reward: { label: '%10 indirim',      code: e.COUPON_PHOTO3  || 'ANI10' } },
    { key: 'mycam3',   icon: 'grid',    title: 'Koleksiyoncu',   desc: 'Profiline 3 kamera ekle',               target: 3,  metric: 'mycams',  reward: null },
    { key: 'like10',   icon: 'spark',   title: 'Sosyal Kelebek', desc: '10 anıyı beğen',                        target: 10, metric: 'likes',   reward: null },
    { key: 'comment5', icon: 'chat',    title: 'Yorumcu',        desc: '5 yorum yaz',                           target: 5,  metric: 'comments', reward: null },
    { key: 'wait3',    icon: 'clock',   title: 'Sabırlı',        desc: '3 kamerayı bekleme listesine ekle',     target: 3,  metric: 'waitlist', reward: null },
    { key: 'photo10',  icon: 'archive', title: 'Arşivci',        desc: '10 anı yükle',                          target: 10, metric: 'photos',
      reward: { label: '%15 indirim',      code: e.COUPON_PHOTO10 || 'ARSIVCI15' } },
    { key: 'vote30',   icon: 'crown',   title: 'Süper Oy',       desc: '30 kameraya beğeni ver',                target: 30, metric: 'votes',
      reward: { label: '%20 indirim',      code: e.COUPON_VOTE30  || 'SUPEROY20' } },
  ];
}

export async function get(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(200).json({ ok: true, loggedIn: false, quests: [], earned: 0 });
  const db = adminClient();
  const sub = claims.sub;
  const cnt = async (t, col) => { const { count } = await db.from(t).select(col, { count: 'exact', head: true }).eq(col, sub); return count || 0; };
  const [votes, photos, comments, likes, mycams, waitlist] = await Promise.all([
    cnt('camera_votes', 'voter_id'),
    cnt('camera_photos', 'customer_id'),
    cnt('photo_comments', 'customer_id'),
    cnt('photo_likes', 'customer_id'),
    cnt('user_cameras', 'customer_id'),
    cnt('camera_waitlist', 'customer_id'),
  ]);
  const M = { votes, photos, comments, likes, mycams, waitlist };
  let earned = 0;
  const quests = QUESTS().map((q) => {
    const progress = M[q.metric] || 0;
    const done = progress >= q.target;
    if (done) earned++;
    return {
      key: q.key, icon: q.icon, title: q.title, desc: q.desc, target: q.target,
      progress: Math.min(progress, q.target), done,
      reward: q.reward ? { label: q.reward.label, code: done ? q.reward.code : null } : null,
    };
  });
  return res.status(200).json({ ok: true, loggedIn: true, quests, earned, totals: M });
}
