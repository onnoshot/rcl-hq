// RetroCameraLand - musteri mesajlasma API (serverless)
// Ziyaretci (public, token ile):  POST ?action=send   GET ?action=poll   GET ?action=health
// Panel (x-rcl-key):              GET ?action=list    GET ?action=thread POST ?action=reply  POST ?action=status
// Telegram botu (x-rcl-tg):       POST ?action=tgreply  (bildirime verilen yanit, kisa kod ile)
//
// Gerekli env: SUPABASE_URL, SUPABASE_SERVICE_KEY. Opsiyonel: RCL_ALIM_KEY, TG_BOT_TOKEN, TG_CHAT_ID.
// Tablolar: rcl-community/supabase/schema_chat.sql
import crypto from 'node:crypto';
import { createClient } from '@supabase/supabase-js';

const MAX_BODY = 2000;
const RENOTIFY_MIN = 30; // son mesajdan bu kadar dakika sonra gelen ziyaretci mesaji yeniden bildirilir

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-rcl-key, x-rcl-tg');
}
function send(res, status, body) {
  cors(res);
  res.status(status).setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}
async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}
function s(v, max) { return String(v == null ? '' : v).trim().slice(0, max || 120); }
function db() {
  return createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
function isAdmin(req) {
  const need = process.env.RCL_ALIM_KEY || '';
  return !!need && req.headers['x-rcl-key'] === need;
}
// Yerel Telegram botu ayni bot tokenini bilir; ek sir gerekmeden imza olarak kullanilir.
function tgSecret() {
  const t = process.env.TG_BOT_TOKEN || '';
  return t ? crypto.createHash('sha256').update(t + ':rcl-chat-reply').digest('hex') : '';
}
function isTelegramBot(req) {
  const need = tgSecret();
  const got = String(req.headers['x-rcl-tg'] || '');
  if (!need || got.length !== need.length) return false;
  try { return crypto.timingSafeEqual(Buffer.from(got), Buffer.from(need)); } catch (e) { return false; }
}
const esc = (x) => String(x || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
async function tgSend(text) {
  const token = process.env.TG_BOT_TOKEN, chatId = process.env.TG_CHAT_ID;
  if (!token || !chatId) return;
  try {
    await fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
  } catch (e) { /* bildirim hatasi akisi bozmaz */ }
}
const MSG_COLS = 'id, sender, body, via, created_at';

async function addAdminMessage(sb, conv, body, via) {
  const { data: msg, error } = await sb.from('chat_messages')
    .insert({ conversation_id: conv.id, sender: 'admin', body, via }).select(MSG_COLS).single();
  if (error) throw error;
  await sb.from('chat_conversations').update({
    last_message_at: msg.created_at, last_preview: body.slice(0, 140), last_sender: 'admin',
    unread_admin: 0, unread_visitor: (conv.unread_visitor || 0) + 1, status: 'open',
  }).eq('id', conv.id);
  return msg;
}

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') { cors(res); return res.status(204).end(); }
  const action = s(req.query && req.query.action, 20);
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) return send(res, 503, { ok: false, error: 'yapilandirma' });
  const sb = db();

  try {
    // ---- health: tablolar hazir mi? (site penceresi buna gore acilir) ----
    if (action === 'health') {
      const { error } = await sb.from('chat_conversations').select('id').limit(1);
      return send(res, error ? 503 : 200, { ok: !error });
    }

    // ================= ZIYARETCI =================
    if (action === 'send' && req.method === 'POST') {
      const b = await readJson(req);
      if (b.website) return send(res, 200, { ok: true }); // honeypot: botlari sessizce yut
      const body = s(b.body, MAX_BODY);
      if (!body) return send(res, 400, { ok: false, error: 'Mesaj bos' });
      let conv = null;
      const token = s(b.token, 80);
      if (token) {
        const r = await sb.from('chat_conversations').select('*').eq('token', token).maybeSingle();
        conv = r.data || null;
      }
      let isNew = false;
      if (!conv) {
        const name = s(b.name, 60);
        if (!name) return send(res, 400, { ok: false, error: 'Ad gerekli' });
        const ins = await sb.from('chat_conversations').insert({
          token: crypto.randomBytes(24).toString('hex'),
          code: 'M-' + crypto.randomBytes(3).toString('hex').toUpperCase(),
          name, contact: s(b.contact, 120), page: s(b.page, 200), device: s(b.device, 12),
        }).select('*').single();
        if (ins.error) throw ins.error;
        conv = ins.data; isNew = true;
      } else {
        // basit sel koruması: 10 dakikada en fazla 30 ziyaretci mesaji
        const since = new Date(Date.now() - 10 * 60000).toISOString();
        const c = await sb.from('chat_messages').select('id')
          .eq('conversation_id', conv.id).eq('sender', 'visitor').gte('created_at', since).limit(31);
        if (((c.data || []).length) >= 30) return send(res, 429, { ok: false, error: 'Cok fazla mesaj, biraz bekleyin' });
      }
      const gapMin = (Date.now() - new Date(conv.last_message_at).getTime()) / 60000;
      const { data: msg, error } = await sb.from('chat_messages')
        .insert({ conversation_id: conv.id, sender: 'visitor', body, via: 'web' }).select(MSG_COLS).single();
      if (error) throw error;
      const upd = {
        last_message_at: msg.created_at, last_preview: body.slice(0, 140), last_sender: 'visitor',
        unread_admin: (conv.unread_admin || 0) + 1, status: 'open',
      };
      if (!conv.contact && b.contact) upd.contact = s(b.contact, 120);
      await sb.from('chat_conversations').update(upd).eq('id', conv.id);
      if (isNew || gapMin >= RENOTIFY_MIN) {
        await tgSend(
          '<b>' + (isNew ? 'Yeni musteri mesaji' : 'Musteri tekrar yazdi') + '</b>  #' + esc(conv.code) + '\n' +
          'Kisi: <b>' + esc(conv.name) + '</b>' + (conv.contact || upd.contact ? '  (' + esc(upd.contact || conv.contact) + ')' : '') + '\n' +
          'Sayfa: ' + esc(conv.page) + '\n\n' + esc(body.slice(0, 600)) + '\n\n' +
          '<i>Yanitlamak icin bu mesaji yanitla (reply) ya da panelde Mesajlar sekmesini ac.</i>'
        );
      }
      return send(res, 200, { ok: true, token: conv.token, code: conv.code, message: msg });
    }

    if (action === 'poll' && req.method === 'GET') {
      const token = s(req.query.token, 80);
      if (!token) return send(res, 400, { ok: false, error: 'token' });
      const { data: conv } = await sb.from('chat_conversations').select('id, unread_visitor, status').eq('token', token).maybeSingle();
      if (!conv) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      const after = Number(req.query.after) || 0;
      const { data: msgs, error } = await sb.from('chat_messages').select(MSG_COLS)
        .eq('conversation_id', conv.id).gt('id', after).order('id', { ascending: true }).limit(200);
      if (error) throw error;
      if (conv.unread_visitor && req.query.seen === '1') await sb.from('chat_conversations').update({ unread_visitor: 0 }).eq('id', conv.id);
      return send(res, 200, { ok: true, messages: msgs || [], unread: conv.unread_visitor || 0 });
    }

    // ================= TELEGRAM BOTU =================
    if (action === 'tgreply' && req.method === 'POST') {
      if (!isTelegramBot(req)) return send(res, 401, { ok: false, error: 'Yetkisiz' });
      const b = await readJson(req);
      const code = s(b.code, 12).toUpperCase(), body = s(b.body, MAX_BODY);
      if (!code || !body) return send(res, 400, { ok: false, error: 'Eksik alan' });
      const { data: conv } = await sb.from('chat_conversations').select('*').eq('code', code).maybeSingle();
      if (!conv) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      const msg = await addAdminMessage(sb, conv, body, 'telegram');
      return send(res, 200, { ok: true, name: conv.name, message: msg });
    }

    // ================= PANEL =================
    if (!isAdmin(req)) return send(res, 401, { ok: false, error: 'Yetkisiz' });

    if (action === 'list' && req.method === 'GET') {
      const { data, error } = await sb.from('chat_conversations')
        .select('id, code, name, contact, page, device, status, unread_admin, last_preview, last_sender, created_at, last_message_at')
        .order('last_message_at', { ascending: false }).limit(200);
      if (error) throw error;
      return send(res, 200, { ok: true, items: data || [] });
    }
    if (action === 'thread' && req.method === 'GET') {
      const id = s(req.query.id, 40);
      const after = Number(req.query.after) || 0;
      const { data: msgs, error } = await sb.from('chat_messages').select(MSG_COLS)
        .eq('conversation_id', id).gt('id', after).order('id', { ascending: true }).limit(500);
      if (error) throw error;
      await sb.from('chat_conversations').update({ unread_admin: 0 }).eq('id', id);
      return send(res, 200, { ok: true, messages: msgs || [] });
    }
    if (action === 'reply' && req.method === 'POST') {
      const b = await readJson(req);
      const body = s(b.body, MAX_BODY);
      if (!body) return send(res, 400, { ok: false, error: 'Mesaj bos' });
      const { data: conv } = await sb.from('chat_conversations').select('*').eq('id', s(b.id, 40)).maybeSingle();
      if (!conv) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      const msg = await addAdminMessage(sb, conv, body, 'panel');
      return send(res, 200, { ok: true, message: msg });
    }
    if (action === 'status' && req.method === 'POST') {
      const b = await readJson(req);
      const st = b.status === 'closed' ? 'closed' : 'open';
      const { error } = await sb.from('chat_conversations').update({ status: st }).eq('id', s(b.id, 40));
      if (error) throw error;
      return send(res, 200, { ok: true });
    }
    return send(res, 404, { ok: false, error: 'Bilinmeyen islem' });
  } catch (e) {
    return send(res, 500, { ok: false, error: String((e && e.message) || e).slice(0, 200) });
  }
}
