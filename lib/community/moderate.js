// FAZ 2: Topluluk moderasyon ucu (token korumali - App Proxy DEGIL, admin paneli icin).
//   GET  /api/community/moderate?key=<RCL_ALIM_KEY>&filter=pending|all   -> liste
//   POST /api/community/moderate { key, id, action:'approve'|'reject' }  -> durum degistir
// Ayni token RCL_ALIM_KEY (HQ dashboard ile ayni desen).
import { adminClient, notifyTelegram, readJson, cors } from './core.js';

function authed(req, body) {
  const key = (req.query && req.query.key) || (body && body.key);
  return key && key === process.env.RCL_ALIM_KEY;
}

export async function run(req, res) {
  cors(res);
  const db = adminClient();

  if (req.method === 'POST') {
    let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok:false }); }
    if (!authed(req, b)) return res.status(401).json({ ok:false });
    if (!b.id || !['approve','reject'].includes(b.action)) return res.status(400).json({ ok:false });
    const status = b.action === 'approve' ? 'approved' : 'rejected';
    const { data, error } = await db.from('photos').update({ status }).eq('id', b.id).select('camera_model,location').single();
    if (error) return res.status(500).json({ ok:false });
    await notifyTelegram('<b>Moderasyon</b>\n' + (data?.camera_model||'') + ' -> ' + status);
    return res.status(200).json({ ok:true, status });
  }

  if (!authed(req)) return res.status(401).json({ ok:false });
  const filter = req.query?.filter || 'pending';
  let qy = db.from('photos')
    .select('id,image_url,camera_model,location,caption,status,created_at,like_count,profiles(handle,display_name)')
    .order('created_at', { ascending: false }).limit(200);
  if (filter !== 'all') qy = qy.eq('status', filter);
  const { data } = await qy;
  const counts = {};
  for (const s of ['pending','approved','rejected']) {
    const { count } = await db.from('photos').select('id', { count:'exact', head:true }).eq('status', s);
    counts[s] = count || 0;
  }
  return res.status(200).json({ ok:true, items: data || [], counts });
}
