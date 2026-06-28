// RCL — Panel e-posta gönderim kuyruğu (panel -> Mac köprüsü)
// GET  /api/email-send                         -> { ok, queue:[...] }
// POST /api/email-send {key, action, ...}      -> enqueue | complete   (yetki: RCL_ALIM_KEY)
//   action=enqueue {theme, segment, at}  -> kuyruğa ekle (Mac işler)
//   action=complete {id, status, result} -> Mac sonucu yazar
// Kalıcı durum Supabase tablosunda: email_queue.
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
    const { data, error } = await sb.from('email_queue')
      .select('*').order('created_at', { ascending: false }).limit(40);
    return res.status(200).json({
      ok: true, table_ready: !error, error: error ? error.message : null, queue: data || [],
    });
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
    const key = (body && body.key) || (req.query && req.query.key) || '';
    if (!process.env.RCL_ALIM_KEY || key !== process.env.RCL_ALIM_KEY) {
      return res.status(401).json({ ok: false, error: 'yetki' });
    }
    const action = body.action;
    if (action === 'enqueue') {
      const row = {
        theme: body.theme, segment: body.segment || 'all',
        scheduled_at: body.at || null, status: 'pending',
        created_at: new Date().toISOString(),
      };
      const { data, error } = await sb.from('email_queue').insert(row).select().maybeSingle();
      if (error) return res.status(500).json({ ok: false, error: error.message });
      return res.status(200).json({ ok: true, item: data });
    }
    if (action === 'complete') {
      const { error } = await sb.from('email_queue')
        .update({ status: body.status || 'done', result: body.result || null }).eq('id', body.id);
      if (error) return res.status(500).json({ ok: false, error: error.message });
      return res.status(200).json({ ok: true });
    }
    return res.status(400).json({ ok: false, error: 'bilinmeyen action' });
  }

  return res.status(405).json({ ok: false, error: 'method' });
}
