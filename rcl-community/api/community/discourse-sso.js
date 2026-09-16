// FAZ 2: GET /apps/community/discourse-sso?sso=...&sig=...
// DiscourseConnect (Discourse SSO) koprusu. Discourse, kullanici giris yapmak isteyince
// buraya sso(base64 payload+nonce)+sig(HMAC) ile yonlendirir. Shopify App Proxy bu istege
// logged_in_customer_id ekler. Akis:
//   1) App Proxy HMAC dogrula
//   2) giris yoksa -> /account/login?return_url=<bu istek>  (Shopify girisine yonlendir)
//   3) Discourse sig dogrula -> nonce coz -> external_id=customer.id + email + username ile
//      imzali payload uret -> {DISCOURSE_URL}/session/sso_login'e geri yonlendir
//
// Env: SHOPIFY_APP_PROXY_SECRET, DISCOURSE_URL, DISCOURSE_SSO_SECRET, SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN
import crypto from 'node:crypto';
import { verifyProxy, fetchShopifyCustomer, slugifyHandle } from './_lib.js';

function hmac(secret, msg) { return crypto.createHmac('sha256', secret).update(msg).digest('hex'); }

export default async function handler(req, res) {
  const q = req.query || {};
  if (!verifyProxy(q, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).send('imza');

  const secret = process.env.DISCOURSE_SSO_SECRET;
  const base = (process.env.DISCOURSE_URL || '').replace(/\/$/, '');
  const { sso, sig } = q;
  if (!sso || !sig || !secret || !base) return res.status(400).send('eksik parametre');

  // Discourse imzasini dogrula
  if (hmac(secret, sso) !== String(sig)) return res.status(403).send('discourse imza hatasi');

  const cid = q.logged_in_customer_id;
  if (!cid) {
    // Shopify girisine yonlendir, donus bu uca
    const ret = encodeURIComponent('/apps/community/discourse-sso?sso=' + encodeURIComponent(sso) + '&sig=' + encodeURIComponent(sig));
    res.writeHead(302, { Location: '/account/login?return_url=' + ret });
    return res.end();
  }

  // nonce + return_sso_url payload'dan coz
  const payload = Buffer.from(sso, 'base64').toString('utf8');
  const params = new URLSearchParams(payload);
  const nonce = params.get('nonce');
  if (!nonce) return res.status(400).send('nonce yok');

  const cust = await fetchShopifyCustomer(cid);
  const email = cust?.email || (cid + '@uye.retrocameraland.com');
  const name = cust ? ((cust.first_name || '') + ' ' + (cust.last_name || '')).trim() || 'Uye' : 'Uye';
  const username = slugifyHandle(name, cid);

  const out = new URLSearchParams();
  out.set('nonce', nonce);
  out.set('external_id', String(cid));
  out.set('email', email);
  out.set('username', username);
  out.set('name', name);
  out.set('require_activation', 'false');
  if (cust?.orders_count >= 1) out.set('add_groups', 'musteriler');

  const b64 = Buffer.from(out.toString(), 'utf8').toString('base64');
  const sig2 = hmac(secret, b64);
  const url = base + '/session/sso_login?sso=' + encodeURIComponent(b64) + '&sig=' + sig2;
  res.writeHead(302, { Location: url });
  return res.end();
}
