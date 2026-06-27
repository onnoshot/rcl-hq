// FAZ 2: GET /apps/community/sitemap  -> topluluk URL'leri icin XML sitemap (Shopify bunlari uretmez)
// Search Console'a https://retrocameraland.com/apps/community/sitemap olarak ekle.
// Sadece DEGER tasiyan sayfalar: >=2 fotosu olan profiller + onayli fotograflar + aktif yarismalar.
import { verifyProxy, adminClient } from './_lib.js';

const SITE = 'https://retrocameraland.com';
function esc(s){return String(s).replace(/[&<>]/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])})}

export default async function handler(req, res) {
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET)) return res.status(401).send('imza');
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Cache-Control', 's-maxage=3600');
  const db = adminClient();

  const urls = [];
  const { data: contests } = await db.from('contests').select('slug,created_at');
  (contests || []).forEach(function(c){ urls.push([SITE+'/apps/community/yarisma/'+c.slug, c.created_at]); });

  // >=2 onayli fotosu olan profiller
  const { data: photos } = await db.from('photos')
    .select('id,created_at,customer_id,profiles(handle,updated_at)').eq('status','approved')
    .order('created_at',{ascending:false}).limit(5000);
  const perUser = {};
  (photos || []).forEach(function(p){
    urls.push([SITE+'/apps/community/foto/'+p.id, p.created_at]);
    const h = p.profiles && p.profiles.handle; if (!h) return;
    perUser[h] = perUser[h] || { n:0, mod: p.profiles.updated_at };
    perUser[h].n++;
  });
  Object.keys(perUser).forEach(function(h){ if (perUser[h].n >= 2) urls.push([SITE+'/apps/community/profil/'+h, perUser[h].mod]); });

  const body = urls.map(function(u){
    return '<url><loc>'+esc(u[0])+'</loc>'+(u[1]?'<lastmod>'+new Date(u[1]).toISOString().slice(0,10)+'</lastmod>':'')+'</url>';
  }).join('');
  res.status(200).send('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+body+'</urlset>');
}
