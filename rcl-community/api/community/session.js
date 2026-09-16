// GET /apps/community/session
// App Proxy HMAC dogrula -> profili upsert (Shopify'dan tenure+siparis cek, rozet ver)
// -> topluluk JWT + profil + aktif yarisma dondur. Yeni Hesaplar'da logged_in_customer_id
// bos gelebilir: o durumda loggedIn:false donulur, tema giris CTA gosterir.
import { verifyProxy, mintToken, adminClient, fetchShopifyCustomer, slugifyHandle, cors } from './_lib.js';

function tenureBadges(memberSince) {
  const days = (Date.now() - new Date(memberSince).getTime()) / 86400000;
  const tiers = [[1095,'tenure_curator'],[730,'tenure_darkroom'],[365,'tenure_archivist'],
    [180,'tenure_dev'],[90,'tenure_test'],[0,'tenure_fresh']];
  return tiers.filter(([d]) => days >= d).map(([,k]) => k);
}
function purchaseBadges(orders) {
  const tiers = [[20,'orders_legend'],[10,'orders_vault'],[5,'orders_hoarder'],
    [3,'orders_enthusiast'],[1,'orders_collector']];
  return tiers.filter(([n]) => orders >= n).map(([,k]) => k);
}

export default async function handler(req, res) {
  cors(res);
  const q = req.query || {};
  if (!verifyProxy(q, process.env.SHOPIFY_APP_PROXY_SECRET)) {
    return res.status(401).json({ ok: false, error: 'imza' });
  }
  const cid = q.logged_in_customer_id;
  if (!cid) return res.status(200).json({ ok: true, loggedIn: false });

  const db = adminClient();
  const cust = await fetchShopifyCustomer(cid);
  const memberSince = cust?.created_at || new Date().toISOString();
  const orders = cust?.orders_count || 0;
  const name = cust ? ((cust.first_name || '') + ' ' + (cust.last_name || '')).trim() || 'Uye' : 'Uye';

  // profil upsert (handle ilk seferde sabitlenir)
  const { data: existing } = await db.from('profiles').select('handle').eq('customer_id', cid).maybeSingle();
  const handle = existing?.handle || slugifyHandle(name, cid);
  await db.from('profiles').upsert({
    customer_id: cid, handle, display_name: name, city: cust?.default_address?.city || null,
    member_since: memberSince, orders_count: orders, updated_at: new Date().toISOString(),
  }, { onConflict: 'customer_id' });

  // tenure + purchase rozetlerini ver (idempotent)
  const want = [...tenureBadges(memberSince), ...purchaseBadges(orders)];
  if (want.length) {
    await db.from('user_badges').upsert(
      want.map((k) => ({ customer_id: cid, badge_key: k })),
      { onConflict: 'customer_id,badge_key', ignoreDuplicates: true });
  }

  const { data: badges } = await db.from('user_badges')
    .select('badge_key, badges(label,axis,icon)').eq('customer_id', cid);
  const { data: contest } = await db.from('contests')
    .select('*').eq('status', 'active').order('starts_at', { ascending: false }).limit(1).maybeSingle();

  return res.status(200).json({
    ok: true, loggedIn: true, token: mintToken(cid),
    profile: { customer_id: cid, handle, display_name: name, member_since: memberSince, orders_count: orders },
    badges: badges || [], contest: contest || null,
  });
}
