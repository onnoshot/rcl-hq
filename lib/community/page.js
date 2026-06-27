// FAZ 2: App Proxy server-render GEO sayfalari (Content-Type: application/liquid -> tema icinde render)
//   /apps/hesabim/community/profil/<handle>   -> ProfilePage + Person semasi
//   /apps/hesabim/community/foto/<id>         -> ImageObject + creator semasi
//   /apps/hesabim/community/yarisma/<slug>    -> Event semasi + en cok begenilenler
// App-proxy sayfalari Shopify sitemap'inde DEGIL: kendi canonical'ini ve sitemap'ini biz veriyoruz.
// vercel.json: /api/community/(profil|foto|yarisma)/(.*) -> /api/community/page?type=$1&seg=$2
import { verifyProxy, adminClient } from './core.js';

const SITE = 'https://retrocameraland.com';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])})}
function ld(o){return JSON.stringify(o)}

function shell(title, desc, canonical, jsonld, body){
  return '<meta name="description" content="'+esc(desc)+'">'+
    '<link rel="canonical" href="'+esc(canonical)+'">'+
    '<meta property="og:title" content="'+esc(title)+'"><meta property="og:type" content="website">'+
    '<meta property="og:url" content="'+esc(canonical)+'">'+
    '<script type="application/ld+json">'+jsonld+'</script>'+
    '<div class="rcl-comm-page" style="max-width:1080px;margin:0 auto;padding:40px 20px;font-family:-apple-system,\'SF Pro Display\',sans-serif">'+body+'</div>';
}

export async function run(req, res) {
  const q = req.query || {};
  if (!verifyProxy(q, process.env.SHOPIFY_APP_PROXY_SECRET)) return res.status(401).send('imza');
  res.setHeader('Content-Type', 'application/liquid');

  // type+seg (vercel.json rewrite) ya da path'ten parse
  let type = q.type, seg = q.seg;
  if (!type) { const m = (req.url || '').match(/\/(profil|foto|yarisma)\/([^/?]+)/); if (m) { type = m[1]; seg = decodeURIComponent(m[2]); } }
  const db = adminClient();

  // -------- profil --------
  if (type === 'profil') {
    const { data: pr } = await db.from('profiles').select('*').eq('handle', seg).maybeSingle();
    if (!pr) return res.status(404).send('<p>Profil bulunamadi</p>');
    const { data: photos } = await db.from('photos')
      .select('id,image_url,camera_model,location,like_count').eq('customer_id', pr.customer_id)
      .eq('status', 'approved').order('like_count', { ascending: false }).limit(48);
    const url = SITE + '/apps/hesabim/community/profil/' + pr.handle;
    const thin = (photos || []).length < 2;
    const jsonld = ld({ '@context':'https://schema.org','@type':'ProfilePage',
      dateCreated: pr.member_since, dateModified: pr.updated_at,
      mainEntity:{ '@type':'Person', name: pr.display_name, alternateName: pr.handle,
        identifier:'user-'+pr.customer_id, description: pr.bio || undefined, image: pr.avatar_url || undefined,
        interactionStatistic:{ '@type':'InteractionCounter', interactionType:'https://schema.org/LikeAction', userInteractionCount: pr.total_likes },
        agentInteractionStatistic:{ '@type':'InteractionCounter', interactionType:'https://schema.org/WriteAction', userInteractionCount:(photos||[]).length } } });
    const grid = (photos || []).map(function(p){return '<a href="'+SITE+'/apps/hesabim/community/foto/'+p.id+'"><img loading="lazy" src="'+esc(p.image_url)+'" alt="'+esc(p.camera_model+', '+p.location)+'" width="240" style="width:100%;border-radius:12px"></a>'}).join('');
    const body = '<h1>'+esc(pr.display_name)+' (@'+esc(pr.handle)+')</h1>'+
      (pr.bio?'<p>'+esc(pr.bio)+'</p>':'')+
      '<p>'+esc(pr.city||'')+' &#183; '+esc((photos||[]).length)+' fotograf &#183; '+esc(pr.total_likes)+' begeni</p>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:20px">'+grid+'</div>';
    if (thin) res.setHeader('X-Robots-Tag', 'noindex, follow'); // ince profil -> indeksleme
    return res.status(200).send(shell(pr.display_name+' - RetroCameraLand Toplulugu',
      (pr.bio||(pr.display_name+' RetroCameraLand topluluk profili')), url, jsonld, body));
  }

  // -------- foto --------
  if (type === 'foto') {
    const { data: p } = await db.from('photos')
      .select('*,profiles(handle,display_name)').eq('id', seg).eq('status','approved').maybeSingle();
    if (!p) return res.status(404).send('<p>Fotograf bulunamadi</p>');
    const url = SITE + '/apps/hesabim/community/foto/' + p.id;
    const author = p.profiles || {};
    const jsonld = ld({ '@context':'https://schema.org','@type':'ImageObject',
      contentUrl: p.image_url, caption: p.caption || (p.camera_model+' ile '+p.location),
      dateCreated: p.created_at, inLanguage:'tr',
      creator:{ '@type':'Person', name: author.display_name, url: SITE+'/apps/hesabim/community/profil/'+author.handle },
      contentLocation:{ '@type':'Place', name: p.location },
      interactionStatistic:{ '@type':'InteractionCounter', interactionType:'https://schema.org/LikeAction', userInteractionCount: p.like_count } });
    const body = '<h1>'+esc(p.camera_model)+' &#183; '+esc(p.location)+'</h1>'+
      '<img src="'+esc(p.image_url)+'" alt="'+esc(p.camera_model+' fotograf, '+p.location+(p.caption?', '+p.caption:''))+'" style="max-width:100%;border-radius:16px">'+
      (p.caption?'<p>'+esc(p.caption)+'</p>':'')+
      '<p>Ceken: <a href="'+SITE+'/apps/hesabim/community/profil/'+esc(author.handle)+'">@'+esc(author.handle)+'</a> &#183; '+esc(p.like_count)+' begeni</p>';
    return res.status(200).send(shell(p.camera_model+' - '+p.location+' | RetroCameraLand',
      (p.caption||(p.camera_model+' ile '+p.location+'de cekilmis fotograf')), url, jsonld, body));
  }

  // -------- yarisma --------
  if (type === 'yarisma') {
    const { data: c } = await db.from('contests').select('*').eq('slug', seg).maybeSingle();
    if (!c) return res.status(404).send('<p>Yarisma bulunamadi</p>');
    const { data: top } = await db.from('photos')
      .select('id,image_url,camera_model,location,like_count,profiles(handle)').eq('contest_id', c.id)
      .eq('status','approved').order('like_count',{ascending:false}).limit(12);
    const url = SITE + '/apps/hesabim/community/yarisma/' + c.slug;
    const jsonld = ld({ '@context':'https://schema.org','@type':'Event', name: c.title,
      description:'RetroCameraLand toplulugu aylik fotograf yarismasi. Tema: '+(c.theme||'')+'. Kazanan topluluk oylamasiyla; haftalik 1000 TL, aylik 5000 TL hediye ceki.',
      startDate: c.starts_at, endDate: c.ends_at, eventStatus:'https://schema.org/EventScheduled',
      eventAttendanceMode:'https://schema.org/OnlineEventAttendanceMode',
      location:{'@type':'VirtualLocation',url}, inLanguage:'tr',
      organizer:{'@type':'Organization',name:'RetroCameraLand',url:SITE} });
    const grid = (top||[]).map(function(p){return '<a href="'+SITE+'/apps/hesabim/community/foto/'+p.id+'"><img loading="lazy" src="'+esc(p.image_url)+'" alt="'+esc(p.camera_model)+'" style="width:100%;border-radius:12px"></a>'}).join('');
    const body = '<h1>'+esc(c.title)+'</h1><p>Tema: <b>'+esc(c.theme||'')+'</b></p>'+
      '<p>Bu yarismada en cok begenilen kareler. Katilmak icin <a href="'+SITE+'/pages/topluluk">topluluk sayfasina</a> git.</p>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:20px">'+grid+'</div>';
    return res.status(200).send(shell(c.title+' | RetroCameraLand Toplulugu',
      'Tema: '+(c.theme||'')+'. Topluluk oylamali aylik fotograf yarismasi.', url, jsonld, body));
  }

  return res.status(404).send('<p>Sayfa bulunamadi</p>');
}
