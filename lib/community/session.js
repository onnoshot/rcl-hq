// GET session -> App Proxy HMAC dogrula, logged_in_customer_id al, profil upsert,
// topluluk JWT uret, profil + kullanicinin kameralarini dondur.
import { verifyProxy, mintToken, adminClient, fetchShopifyCustomer, slugifyHandle, cors } from './core.js';

export async function run(req, res) {
  cors(res);
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const cid = req.query.logged_in_customer_id;
  if (!cid) return res.status(200).json({ ok: true, loggedIn: false });

  const db = adminClient();
  const cust = await fetchShopifyCustomer(cid);
  const name = cust ? ((cust.first_name || '') + ' ' + (cust.last_name || '')).trim() || 'Uye' : 'Uye';
  // mevcut profili koru: uye kendi kullanici adini/ismini/avatarini ozellestirdiyse ezme
  const { data: existing } = await db.from('profiles')
    .select('handle,display_name,avatar_url').eq('customer_id', cid).maybeSingle();
  const handle = existing?.handle || slugifyHandle(name, cid);
  const displayName = existing?.display_name || name;
  const { error: upErr } = await db.from('profiles').upsert({
    customer_id: cid, handle, display_name: displayName,
    city: cust?.default_address?.city || null,
    member_since: cust?.created_at || new Date().toISOString(),
    orders_count: cust?.orders_count || 0, updated_at: new Date().toISOString(),
  }, { onConflict: 'customer_id' });
  if (upErr) return res.status(500).json({ ok: false, error: 'profil' });

  const { data: myCameras } = await db.from('user_cameras')
    .select('id,brand,model').eq('customer_id', cid).order('created_at', { ascending: false });

  return res.status(200).json({
    ok: true, loggedIn: true, token: mintToken(cid),
    profile: { customer_id: cid, handle, display_name: displayName, avatar_url: existing?.avatar_url || null },
    myCameras: myCameras || [],
  });
}
