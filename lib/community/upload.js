// POST /apps/community/upload  { contest_id, image (base64 jpeg, EXIF zaten temizli), camera_model, location, caption }
// JWT dogrula -> moderasyon -> Supabase Storage'a koy -> photos insert (pending|approved) -> Telegram.
import { verifyProxy, readToken, adminClient, moderateImage, notifyTelegram, readJson, cors } from './core.js';

const BUCKET = 'community-photos';

export async function run(req, res) {
  cors(res);
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!verifyProxy(req.query || {}, process.env.SHOPIFY_APP_PROXY_SECRET))
    return res.status(401).json({ ok: false, error: 'imza' });
  const claims = readToken(req);
  if (!claims?.sub) return res.status(401).json({ ok: false, error: 'oturum' });

  let b; try { b = await readJson(req); } catch (e) { return res.status(400).json({ ok: false }); }
  const { contest_id, image, camera_model, location, caption } = b;
  if (!contest_id || !image || !camera_model || !location)
    return res.status(400).json({ ok: false, error: 'eksik alan (kamera modeli ve konum zorunlu)' });

  const base64 = String(image).replace(/^data:image\/\w+;base64,/, '');
  const bytes = Buffer.from(base64, 'base64');
  if (bytes.length > 8 * 1024 * 1024) return res.status(413).json({ ok: false, error: 'foto cok buyuk' });

  const mod = await moderateImage(base64);
  const status = mod.clean ? 'approved' : 'pending';

  const db = adminClient();
  const path = contest_id + '/' + claims.sub + '-' + Date.now() + '.jpg';
  const up = await db.storage.from(BUCKET).upload(path, bytes, { contentType: 'image/jpeg', upsert: false });
  if (up.error) return res.status(500).json({ ok: false, error: 'yukleme' });
  const { data: pub } = db.storage.from(BUCKET).getPublicUrl(path);

  const { data: photo, error } = await db.from('photos').insert({
    contest_id, customer_id: claims.sub, image_url: pub.publicUrl,
    camera_model: String(camera_model).slice(0, 80), location: String(location).slice(0, 120),
    caption: caption ? String(caption).slice(0, 280) : null, status,
  }).select().single();
  if (error) return res.status(500).json({ ok: false, error: 'kayit' });

  await notifyTelegram(
    '<b>RCL Topluluk - yeni foto</b>\nKamera: ' + camera_model + '\nKonum: ' + location +
    '\nDurum: ' + status + (mod.labels?.length ? '\nFlag: ' + mod.labels.join(', ') : ''));

  return res.status(200).json({ ok: true, photo, moderated: status });
}
