// Time Capsule - Gorev / Rozet sistemi (oyunlastirma).
// Kullanicinin gercek eylemleri sayilir, esige ulasinca rozet + odul kuponu acilir.
// Kupon kodlari Shopify'da SEN olusturursun; env ile gercek koda baglanir (yoksa varsayilan placeholder).
import { verifyProxy, readToken, adminClient, cors } from './core.js';

// Kategoriler: kesif (begeni/oy), ani (foto), sosyal (begeni/yorum), koleksiyon (kamera/bekleme)
// Olumlu, tesvik edici adlar; odul sayisi arttirildi. Kodlari Shopify'da SEN olusturursun (env).
function QUESTS() {
  const e = process.env;
  return [
    // --- Kesif ---
    { key: 'vote5',    cat: 'kesif', icon: 'spark',  title: 'Acemi Kaşif',     desc: '5 kameraya beğeni ver',                target: 5,  metric: 'votes',    reward: null },
    { key: 'vote10',   cat: 'kesif', icon: 'heart',  title: 'Oy Verici',       desc: '10 kameraya beğeni ver',               target: 10, metric: 'votes',
      reward: { label: 'Ücretsiz Kargo', code: e.COUPON_VOTE10  || 'KARGOBEDAVA' } },
    { key: 'vote30',   cat: 'kesif', icon: 'crown',  title: 'Süper Oy',        desc: '30 kameraya beğeni ver',               target: 30, metric: 'votes',
      reward: { label: '%20 indirim',     code: e.COUPON_VOTE30  || 'SUPEROY20' } },
    { key: 'vote60',   cat: 'kesif', icon: 'trophy', title: 'Efsane Seçici',   desc: '60 kameraya beğeni ver',               target: 60, metric: 'votes',
      reward: { label: '%25 indirim',     code: e.COUPON_VOTE60  || 'SECICI25' } },
    // --- Ani ---
    { key: 'photo1',   cat: 'ani', icon: 'camera',   title: 'İlk Anı',         desc: 'İlk anını kapsüle ekle',               target: 1,  metric: 'photos',
      reward: { label: '%5 indirim',      code: e.COUPON_PHOTO1  || 'ILKANI5' } },
    { key: 'photo3',   cat: 'ani', icon: 'cam2',     title: 'Anı Avcısı',      desc: '3 anı yükle',                          target: 3,  metric: 'photos',
      reward: { label: '%10 indirim',     code: e.COUPON_PHOTO3  || 'ANI10' } },
    { key: 'photo10',  cat: 'ani', icon: 'archive',  title: 'Arşivci',         desc: '10 anı yükle',                         target: 10, metric: 'photos',
      reward: { label: '%15 indirim',     code: e.COUPON_PHOTO10 || 'ARSIVCI15' } },
    { key: 'photo25',  cat: 'ani', icon: 'trophy',   title: 'Kapsül Ustası',   desc: '25 anı yükle',                         target: 25, metric: 'photos',
      reward: { label: '%30 indirim',     code: e.COUPON_PHOTO25 || 'USTA30' } },
    // --- Sosyal ---
    { key: 'like10',   cat: 'sosyal', icon: 'spark', title: 'Sosyal Kelebek',  desc: '10 anıyı beğen',                       target: 10, metric: 'likes',    reward: null },
    { key: 'like50',   cat: 'sosyal', icon: 'heart', title: 'Gönülden Destek', desc: '50 anıyı beğen',                       target: 50, metric: 'likes',
      reward: { label: '%10 indirim',     code: e.COUPON_LIKE50  || 'DESTEK10' } },
    { key: 'comment5', cat: 'sosyal', icon: 'chat',  title: 'Yorumcu',         desc: '5 yorum yaz',                          target: 5,  metric: 'comments', reward: null },
    { key: 'comment20',cat: 'sosyal', icon: 'chat',  title: 'Sohbet Ustası',   desc: '20 yorum yaz',                         target: 20, metric: 'comments',
      reward: { label: '%10 indirim',     code: e.COUPON_CMT20   || 'SOHBET10' } },
    // --- Koleksiyon ---
    { key: 'mycam3',   cat: 'koleksiyon', icon: 'grid',     title: 'Koleksiyoncu',     desc: 'Koleksiyonuna 3 kamera ekle',  target: 3,  metric: 'mycams',   reward: null },
    { key: 'mycam10',  cat: 'koleksiyon', icon: 'archive',  title: 'Büyük Koleksiyon', desc: 'Koleksiyonuna 10 kamera ekle', target: 10, metric: 'mycams',
      reward: { label: '%15 indirim',     code: e.COUPON_MYCAM10 || 'KOLEKSIYON15' } },
    { key: 'wait3',    cat: 'koleksiyon', icon: 'clock',    title: 'Sabırlı',          desc: '3 kamerayı bekleme listene ekle', target: 3, metric: 'waitlist', reward: null },
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
    (async () => { const { count } = await db.from('camera_photos').select('customer_id', { count: 'exact', head: true }).eq('customer_id', sub).eq('status', 'approved'); return count || 0; })(),
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
      key: q.key, cat: q.cat, icon: q.icon, title: q.title, desc: q.desc, target: q.target, metric: q.metric,
      progress: Math.min(progress, q.target), done,
      reward: q.reward ? { label: q.reward.label, code: done ? q.reward.code : null } : null,
    };
  });
  return res.status(200).json({ ok: true, loggedIn: true, quests, earned, totals: M });
}
