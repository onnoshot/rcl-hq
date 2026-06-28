// RCL — Hermes etkileşim durumu köprüsü (panel <-> Mac'teki Hermes CEO)
// GET  /api/hermes            -> { ok, state:{actions, messages, addressed} }
// POST /api/hermes {key,state} -> durumu MERGE eder (key: RCL_ALIM_KEY)
//   - actions: sağlanırsa üzerine yazılır (panel aksiyon durumlarının sahibi)
//   - messages: (ts+from) ile birleştirilir (panel kullanıcı mesajı yazar, Hermes yanıt yazar)
//   - addressed: birleştirilir (Hermes hangi kullanıcı mesajını yanıtladı)
// Kalıcı durum tek satırlık Supabase tablosunda: hermes_state (id=1, jsonb state).
import { createClient } from '@supabase/supabase-js';

function db() {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
    auth: { persistSession: false },
  });
}
const EMPTY = { actions: {}, messages: [], addressed: [] };

function mergeMessages(a, b) {
  const seen = new Set(), out = [];
  for (const m of [...(a || []), ...(b || [])]) {
    if (!m) continue;
    const k = (m.ts || '') + '|' + (m.from || '');
    if (seen.has(k)) continue;
    seen.add(k); out.push(m);
  }
  out.sort((x, y) => String(x.ts || '').localeCompare(String(y.ts || '')));
  return out;
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const sb = db();

  if (req.method === 'GET') {
    const { data, error } = await sb.from('hermes_state').select('state').eq('id', 1).maybeSingle();
    return res.status(200).json({
      ok: true, table_ready: !error, error: error ? error.message : null,
      state: (data && data.state) || EMPTY,
    });
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
    const key = (body && body.key) || (req.query && req.query.key) || '';
    if (!process.env.RCL_ALIM_KEY || key !== process.env.RCL_ALIM_KEY) {
      return res.status(401).json({ ok: false, error: 'yetki' });
    }
    const patch = (body && body.state) || {};
    const cur = await sb.from('hermes_state').select('state').eq('id', 1).maybeSingle();
    const base = (cur.data && cur.data.state) || EMPTY;
    const merged = {
      actions: patch.actions !== undefined ? patch.actions : (base.actions || {}),
      messages: mergeMessages(base.messages, patch.messages),
      addressed: Array.from(new Set([...(base.addressed || []), ...(patch.addressed || [])])),
    };
    const { error } = await sb.from('hermes_state').upsert({ id: 1, state: merged }, { onConflict: 'id' });
    if (error) return res.status(500).json({ ok: false, error: error.message });
    return res.status(200).json({ ok: true, state: merged });
  }

  return res.status(405).json({ ok: false, error: 'method' });
}
