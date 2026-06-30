// RCL — Panel e-posta gönderim kuyruğu (panel -> Mac köprüsü)
// GET  /api/email-send                         -> { ok, queue:[...] }  (Brevo ile canli mutabakat)
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

// Brevo kampanya adı: RCL-YYYYMMDDHHMM-<theme>-<segment>[-<chunk>]  (yerel İstanbul saati)
const SEGMENTS = ['all', 'customers', 'non_customers', 'recent'];
function parseCampaignName(name) {
  const m = /^RCL-(\d{12})-(.+?)-(all|customers|non_customers|recent)(?:-(\d+))?$/.exec(name || '');
  if (!m) return null;
  const [, ts, theme, segment, chunk] = m;
  // ts = İstanbul (+03:00) yerel zaman damgası -> UTC ms
  const iso = `${ts.slice(0,4)}-${ts.slice(4,6)}-${ts.slice(6,8)}T${ts.slice(8,10)}:${ts.slice(10,12)}:00+03:00`;
  return { ts, theme, segment, chunk: chunk ? +chunk : 0, t: Date.parse(iso) };
}

async function fetchBrevoCampaigns() {
  const key = process.env.BREVO_API_KEY;
  if (!key) return null;
  try {
    const r = await fetch('https://api.brevo.com/v3/emailCampaigns?limit=100&sort=desc', {
      headers: { 'api-key': key, accept: 'application/json' },
    });
    if (!r.ok) return null;
    const j = await r.json();
    return (j.campaigns || []).map(c => ({
      id: c.id, name: c.name, status: c.status,
      scheduledAt: c.scheduledAt || null, sentDate: c.sentDate || null,
      parsed: parseCampaignName(c.name),
    })).filter(c => c.parsed);
  } catch (e) { return null; }
}

// Bir kuyruk satırını Brevo kampanyalarıyla eşle ve gerçek durumu çıkar
// Bir kuyruk satırını Brevo kampanya "parti"siyle eşle -> batch dizisi (cancel/reschedule de kullanır)
function matchBatch(item, camps) {
  const rowT = Date.parse(item.created_at);
  const same = camps.filter(c => c.parsed.theme === item.theme && c.parsed.segment === (item.segment || 'all'));
  if (!same.length) return [];
  let bestTs = null, bestDelta = Infinity;
  for (const c of same) {
    const d = Math.abs(c.parsed.t - rowT);
    if (d < bestDelta) { bestDelta = d; bestTs = c.parsed.ts; }
  }
  if (bestDelta > 24 * 3600 * 1000) return [];  // 24 saatten uzak eşleşme şüpheli
  return same.filter(c => c.parsed.ts === bestTs);
}

function reconcile(item, camps) {
  const batch = matchBatch(item, camps);
  if (!batch.length) return null;
  const total = batch.length;
  const sent = batch.filter(c => c.status === 'sent').length;
  const errored = batch.filter(c => c.status === 'suspended' || c.status === 'archive').length;
  const pendingChunks = batch.filter(c => c.status === 'queued' || c.status === 'inProcess' || c.status === 'draft');
  // Sıradaki gönderim zamanı (gönderilmemiş en yakın)
  let nextAt = null;
  for (const c of pendingChunks) {
    if (c.scheduledAt && (!nextAt || Date.parse(c.scheduledAt) < Date.parse(nextAt))) nextAt = c.scheduledAt;
  }
  let lastSent = null;
  for (const c of batch) {
    if (c.sentDate && (!lastSent || Date.parse(c.sentDate) > Date.parse(lastSent))) lastSent = c.sentDate;
  }
  let status;
  if (errored && sent === 0) status = 'error';
  else if (sent >= total) status = 'sent';
  else if (sent > 0) status = 'sending';
  else status = 'scheduled';
  return { status, brevo: { total, sent, scheduled: pendingChunks.length, next_at: nextAt, last_sent: lastSent } };
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const sb = db();

  if (req.method === 'GET') {
    const { data, error } = await sb.from('email_queue')
      .select('*').order('created_at', { ascending: false }).limit(40);
    let queue = data || [];
    if (queue.length) {
      const camps = await fetchBrevoCampaigns();
      if (camps) {
        queue = queue.map(it => {
          // Mac zaten kesin sonuç yazdıysa (done/error) ona dokunma; aksi halde Brevo'dan canli durum
          const rec = reconcile(it, camps);
          if (rec) return { ...it, status: rec.status, brevo: rec.brevo };
          return it;
        });
      }
    }
    return res.status(200).json({
      ok: true, table_ready: !error, error: error ? error.message : null, queue,
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
    // ── PLANLI KAMPANYAYI İPTAL ET / YENİDEN ZAMANLA (yalnız gönderilmemiş parçalar) ──
    if (action === 'cancel' || action === 'reschedule') {
      const { data: item } = await sb.from('email_queue').select('*').eq('id', body.id).maybeSingle();
      if (!item) return res.status(404).json({ ok: false, error: 'kuyruk ögesi bulunamadı' });
      const bkey = process.env.BREVO_API_KEY;
      if (!bkey) return res.status(500).json({ ok: false, error: 'BREVO_API_KEY yok' });
      const camps = await fetchBrevoCampaigns();
      if (!camps) return res.status(502).json({ ok: false, error: 'Brevo erişilemedi' });
      const batch = matchBatch(item, camps);
      // yalnız henüz gönderilmemiş (zamanlı/sırada/taslak) parçalar düzenlenebilir
      const editable = batch.filter(c => c.status === 'queued' || c.status === 'inProcess' || c.status === 'draft')
        .sort((a, b) => (a.parsed.chunk || 0) - (b.parsed.chunk || 0));
      if (!editable.length) return res.status(409).json({ ok: false, error: 'Düzenlenebilir parça yok (gönderilmiş veya eşleşmedi).' });
      const bh = { 'api-key': bkey, 'content-type': 'application/json', accept: 'application/json' };
      const affected = [];
      if (action === 'cancel') {
        for (const c of editable) {
          const r = await fetch(`https://api.brevo.com/v3/emailCampaigns/${c.id}/status`,
            { method: 'PUT', headers: bh, body: JSON.stringify({ status: 'suspended' }) });
          affected.push({ id: c.id, ok: r.ok });
        }
        await sb.from('email_queue').update({ status: 'canceled' }).eq('id', body.id);
        return res.status(200).json({ ok: true, action: 'cancel', count: affected.length, affected });
      }
      // reschedule: chunk sırasına göre ardışık gün (orijinal _shift_day mantığı)
      if (!body.at) return res.status(400).json({ ok: false, error: 'tarih (at) gerekli' });
      const baseT = Date.parse(body.at);
      if (isNaN(baseT)) return res.status(400).json({ ok: false, error: 'geçersiz tarih' });
      for (let i = 0; i < editable.length; i++) {
        const when = new Date(baseT + i * 86400000).toISOString();
        const r = await fetch(`https://api.brevo.com/v3/emailCampaigns/${editable[i].id}`,
          { method: 'PUT', headers: bh, body: JSON.stringify({ scheduledAt: when }) });
        affected.push({ id: editable[i].id, at: when, ok: r.ok });
      }
      await sb.from('email_queue').update({ scheduled_at: body.at }).eq('id', body.id);
      return res.status(200).json({ ok: true, action: 'reschedule', count: affected.length, affected });
    }
    return res.status(400).json({ ok: false, error: 'bilinmeyen action' });
  }

  return res.status(405).json({ ok: false, error: 'method' });
}
