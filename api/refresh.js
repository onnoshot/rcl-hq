// RCL — "Her şeyi güncelle" sinyali (panel butonu -> Mac dinleyici köprüsü)
// POST /api/refresh  {key}        -> requested_at = now  (yetki: RCL_ALIM_KEY)
// GET  /api/refresh               -> { requested_at, processed_at, build_no }  (Mac dinleyici bunu yoklar)
// Kalıcı durum tek satırlık Supabase tablosunda (ops_refresh, id=1).
import { createClient } from '@supabase/supabase-js';

function db() {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
    auth: { persistSession: false },
  });
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const sb = db();

  if (req.method === 'GET') {
    const { data, error } = await sb.from('ops_refresh')
      .select('requested_at,processed_at,build_no').eq('id', 1).maybeSingle();
    return res.status(200).json({
      ok: true,
      table_ready: !error,                 // teşhis: ops_refresh tablosu kurulu mu
      row_exists: !!data,                  // teşhis: id=1 satırı var mı
      error: error ? error.message : null,
      requested_at: (data && data.requested_at) || null,
      processed_at: (data && data.processed_at) || null,
      build_no: (data && data.build_no) || null,
    });
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
    const key = (body && body.key) || (req.query && req.query.key) || '';
    if (!process.env.RCL_ALIM_KEY || key !== process.env.RCL_ALIM_KEY) {
      return res.status(401).json({ ok: false, error: 'yetki' });
    }
    const now = new Date().toISOString();
    const { error } = await sb.from('ops_refresh').upsert({ id: 1, requested_at: now }, { onConflict: 'id' });
    if (error) return res.status(500).json({ ok: false, error: error.message });
    return res.status(200).json({ ok: true, requested_at: now });
  }

  return res.status(405).json({ ok: false, error: 'method' });
}
