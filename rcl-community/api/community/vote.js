// POST /apps/community/vote   { photo_id, action: 'like'|'unlike' }
// JWT dogrula -> uye istemcisiyle insert/delete. DB tetikleyicileri tekil-oy + self-vote
// engelini ve sayac guncellemesini zorlar. Optimistik UI temada; burada gercek sayac doner.
import { verifyProxy, readToken, memberClient, readJson, cors } from './_lib.js';

export default async function handler(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });

  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const { photo_id, action } = b;
  if (!photo_id) return res.status(400).json({ ok: false });

  const token = (req.headers.authorization || '').slice(7);
  const db = memberClient(token);

  if (action === 'unlike') {
    await db.from('votes').delete().eq('photo_id', photo_id).eq('voter_id', claims.sub);
  } else {
    const { error } = await db.from('votes').insert({ photo_id, voter_id: claims.sub });
    if (error) {
      // self_vote_not_allowed veya unique ihlali -> sessizce mevcut sayaci dondur
      if (!/duplicate|unique|self_vote/i.test(error.message || ''))
        return res.status(400).json({ ok: false, error: error.message });
    }
  }
  const { data: photo } = db
    ? await memberClient(token).from('photos').select('like_count').eq('id', photo_id).maybeSingle()
    : { data: null };
  return res.status(200).json({ ok: true, like_count: photo?.like_count ?? null });
}
