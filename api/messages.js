// RetroCameraLand - musteri mesajlasma API (serverless)
// Ziyaretci (public, token ile):  POST ?action=send   GET ?action=poll   GET ?action=health
// Panel (x-rcl-key):              GET ?action=list    GET ?action=thread POST ?action=reply  POST ?action=status
// Telegram botu (x-rcl-tg):       POST ?action=tgreply  (bildirime verilen yanit, kisa kod ile)
//
// Gerekli env: CHAT_SUPABASE_URL + CHAT_SUPABASE_SERVICE_KEY (yoksa SUPABASE_URL + SUPABASE_SERVICE_KEY). Opsiyonel: RCL_ALIM_KEY, TG_BOT_TOKEN, TG_CHAT_ID.
// Tablolar: rcl-community/supabase/schema_chat.sql
import crypto from 'node:crypto';
import { createClient } from '@supabase/supabase-js';
import * as club from '../lib/club.js';
import * as chatbot from '../lib/chatbot.js';

const MAX_BODY = 2000;
const AGENTS = ['Umut', 'Ayb\u00fcke', 'Deniz']; // paneldeki destek ekibi
const JOIN_AGAIN_MIN = 60; // ayni temsilci icin "sohbete katildi" bildirimi en fazla saatte bir
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const RENOTIFY_MIN = 30;
const HUMAN_HOLD_MIN = 30; // ekipten biri yazdiysa asistan bu sure boyunca araya girmez // son mesajdan bu kadar dakika sonra gelen ziyaretci mesaji yeniden bildirilir

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-rcl-key, x-rcl-tg');
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
// Asistan acik/kapali: club_settings tablosunda 'chatbot' anahtari (panelden tek tikla degisir).
async function botEnabled(sb) {
  const { data } = await sb.from('club_settings').select('value').eq('key', 'chatbot').maybeSingle();
  return !!(data && data.value && data.value.enabled);
}
function agentOf(v) { const a = s(v, 20); return AGENTS.indexOf(a) >= 0 ? a : ''; }
// Panelde ayni e-postadan gelen konusmalar tek pencerede toplanir; anahtar = e-posta (yoksa konusma id'si).
function groupKey(c) { return c.contact ? c.contact.toLowerCase() : c.id; }
async function groupConvs(sb, key) {
  const k = s(key, 120);
  const q = sb.from('chat_conversations').select('*').order('last_message_at', { ascending: false });
  const r = k.indexOf('@') > 0 ? await q.eq('contact', k.toLowerCase()) : await q.eq('id', k);
  return r.data || [];
}
function s(v, max) { return String(v == null ? '' : v).trim().slice(0, max || 120); }
// Mesajlasma kendi Supabase projesini kullanabilir (CHAT_*); tanimli degilse topluluk projesine duser.
const SB_URL = process.env.CHAT_SUPABASE_URL || process.env.SUPABASE_URL;
const SB_KEY = process.env.CHAT_SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_KEY;
function db() {
  return createClient(SB_URL, SB_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
function isAdmin(req) {
  const need = process.env.RCL_ALIM_KEY || '';
  return !!need && req.headers['x-rcl-key'] === need;
}
// Yerel Telegram botu ayni bot tokenini bilir; ek sir gerekmeden imza olarak kullanilir.
function tgSecret() {
  const t = String(process.env.TG_BOT_TOKEN || '').trim(); // env degerinde satir sonu kalmis olabiliyor
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

// Musteriye "<Temsilci> sohbete katildi" bildirimi. Ayni temsilci icin en fazla saatte bir; eklendiyse satiri doner.
async function ensureJoin(sb, conv, agent) {
  if (!agent) return null;
  const via = 'system:join:' + agent;
  const prev = await sb.from('chat_messages').select('created_at').eq('conversation_id', conv.id).eq('via', via)
    .order('id', { ascending: false }).limit(1);
  const last = prev.data && prev.data[0];
  if (last && (Date.now() - new Date(last.created_at).getTime()) / 60000 < JOIN_AGAIN_MIN) return null;
  const ins = await sb.from('chat_messages').insert({ conversation_id: conv.id, sender: 'admin', via,
    body: agent + ' sohbete kat\u0131ld\u0131. Ger\u00e7ek bir ki\u015fiyle yaz\u0131\u015f\u0131yorsunuz.' }).select(MSG_COLS).single();
  if (ins.error) return null;
  conv.unread_visitor = (conv.unread_visitor || 0) + 1;
  await sb.from('chat_conversations').update({ unread_visitor: conv.unread_visitor }).eq('id', conv.id);
  return ins.data;
}
async function addAdminMessage(sb, conv, body, via, agent) {
  if (agent) via = via + ':' + agent;
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
  const action = s(req.query && req.query.action, 30);
  if (!SB_URL || !SB_KEY) return send(res, 503, { ok: false, error: 'yapilandirma' });
  const sb = db();

  try {
    // ---- Retro Club: ayni fonksiyon altinda (Vercel fonksiyon siniri) ----
    if (action.startsWith('club.')) return await club.handle(action, req, res, { sb, send, readJson, isAdmin, tgSend });

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
        const email = s(b.email || b.contact, 120).toLowerCase();
        if (!EMAIL_RE.test(email)) return send(res, 400, { ok: false, error: 'Ge\u00e7erli bir e-posta adresi gerekli' });
        const ins = await sb.from('chat_conversations').insert({
          token: crypto.randomBytes(24).toString('hex'),
          code: 'M-' + crypto.randomBytes(3).toString('hex').toUpperCase(),
          name, contact: email, page: s(b.page, 200), device: s(b.device, 12),
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
      await sb.from('chat_conversations').update(upd).eq('id', conv.id);
      if (isNew || gapMin >= RENOTIFY_MIN) {
        await tgSend(
          '<b>' + (isNew ? 'Yeni musteri mesaji' : 'Musteri tekrar yazdi') + '</b>  #' + esc(conv.code) + '\n' +
          'Kisi: <b>' + esc(conv.name) + '</b>' + (conv.contact ? '  (' + esc(conv.contact) + ')' : '') + '\n' +
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

    // ---- asistan yaniti: ziyaretci mesajindan sonra pencere bu ucu cagirir ----
    if (action === 'bot' && req.method === 'POST') {
      const b = await readJson(req);
      const { data: conv } = await sb.from('chat_conversations').select('*').eq('token', s(b.token, 80)).maybeSingle();
      if (!conv) return send(res, 404, { ok: false });
      if (!(await botEnabled(sb))) return send(res, 200, { ok: true, skipped: 'off' });
      const { data: rows } = await sb.from('chat_messages').select(MSG_COLS).eq('conversation_id', conv.id).order('id', { ascending: false }).limit(30);
      const msgs = (rows || []).reverse().filter((m) => !String(m.via).startsWith('system'));
      const last = msgs[msgs.length - 1];
      if (!last || last.sender !== 'visitor') return send(res, 200, { ok: true, skipped: 'answered' });
      const human = msgs.filter((m) => m.sender === 'admin' && m.via !== 'bot').pop();
      if (human && (Date.now() - new Date(human.created_at).getTime()) / 60000 < HUMAN_HOLD_MIN) return send(res, 200, { ok: true, skipped: 'human' });
      let text = '';
      try { text = await chatbot.reply(msgs, conv.name); }
      catch (e) { return send(res, 200, { ok: true, skipped: 'error', detail: String((e && e.message) || e).slice(0, 160) }); }
      if (!text) return send(res, 200, { ok: true, skipped: 'empty' });
      // uretim sirasinda ekipten biri yazdiysa asistanin yanitini atla
      const chk = await sb.from('chat_messages').select('id, sender').eq('conversation_id', conv.id).order('id', { ascending: false }).limit(1);
      if (chk.data && chk.data[0] && chk.data[0].id !== last.id) return send(res, 200, { ok: true, skipped: 'raced' });
      const ins = await sb.from('chat_messages').insert({ conversation_id: conv.id, sender: 'admin', body: text, via: 'bot' }).select(MSG_COLS).single();
      if (ins.error) throw ins.error;
      await sb.from('chat_conversations').update({ last_message_at: ins.data.created_at, last_preview: text.slice(0, 140), last_sender: 'admin',
        unread_visitor: (conv.unread_visitor || 0) + 1 }).eq('id', conv.id); // unread_admin korunur: panel konusmayi hala "yeni" gorur
      return send(res, 200, { ok: true, message: ins.data, src: chatbot.source });
    }

    // ================= TELEGRAM WEBHOOK (bildirime verilen yanit dogrudan Telegram'dan gelir) =================
    if (action === 'tghook' && req.method === 'POST') {
      if (!tgSecret() || req.headers['x-telegram-bot-api-secret-token'] !== tgSecret()) return send(res, 401, { ok: false });
      const u = await readJson(req);
      const m = u && u.message;
      if (!m || !m.text || String(m.chat && m.chat.id) !== String(process.env.TG_CHAT_ID || '')) return send(res, 200, { ok: true });
      const CODE = /#?(M-[0-9A-Fa-f]{6})/;
      let code = null, body = m.text.trim();
      const rep = (m.reply_to_message && m.reply_to_message.text) || '';
      const a = CODE.exec(rep);
      if (a) code = a[1];
      else { const b2 = /^\s*#?(M-[0-9A-Fa-f]{6})[\s:,-]+([\s\S]+)/.exec(body); if (b2) { code = b2[1]; body = b2[2].trim(); } }
      if (!code) return send(res, 200, { ok: true });
      const { data: conv } = await sb.from('chat_conversations').select('*').eq('code', code.toUpperCase()).maybeSingle();
      if (!conv) { await tgSend('Konusma bulunamadi: ' + esc(code)); return send(res, 200, { ok: true }); }
      await addAdminMessage(sb, conv, s(body, MAX_BODY), 'telegram');
      await tgSend('✓ ' + esc(conv.name) + ' kisisine iletildi (' + esc(conv.code) + ').');
      return send(res, 200, { ok: true });
    }
    // Webhook kurulumu / durumu. Yetki: mesajlasma veritabani anahtarindan turetilen imza.
    if (action === 'tgsetup') {
      const need = crypto.createHash('sha256').update(String(SB_KEY) + ':tgsetup').digest('hex');
      if (s(req.query.k, 80) !== need) return send(res, 401, { ok: false, error: 'Yetkisiz' });
      const token = process.env.TG_BOT_TOKEN;
      if (!token) return send(res, 503, { ok: false, error: 'TG_BOT_TOKEN yok' });
      const tg = async (method, payload) => (await fetch('https://api.telegram.org/bot' + token + '/' + method, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload || {}),
      })).json();
      const me = await tg('getMe');
      let info = await tg('getWebhookInfo');
      let set = null;
      if (req.query.mode === 'set') {
        set = await tg('setWebhook', { url: 'https://rclhq.vercel.app/api/messages?action=tghook', secret_token: tgSecret(), allowed_updates: ['message'] });
        info = await tg('getWebhookInfo');
      }
      return send(res, 200, { ok: true, bot: me.result && me.result.username, webhook: (info.result && info.result.url) || '',
        pending: info.result && info.result.pending_update_count, lastError: (info.result && info.result.last_error_message) || '', set: set && set.ok });
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
        .order('last_message_at', { ascending: false }).limit(400);
      if (error) throw error;
      const groups = {}, order = [];
      for (const c of data || []) {
        const k = groupKey(c);
        let g = groups[k];
        if (!g) { // ilk gorulen = en yeni konusma: baslik bilgileri ondan gelir
          g = groups[k] = { key: k, name: c.name, contact: c.contact, code: c.code, page: c.page, device: c.device,
            status: 'closed', unread_admin: 0, last_preview: c.last_preview, last_sender: c.last_sender,
            last_message_at: c.last_message_at, created_at: c.created_at, count: 0 };
          order.push(g);
        }
        g.count++; g.unread_admin += c.unread_admin || 0;
        if (c.status === 'open') g.status = 'open';
        if (c.created_at < g.created_at) g.created_at = c.created_at;
      }
      return send(res, 200, { ok: true, items: order, agents: AGENTS, bot: await botEnabled(sb) });
    }
    if (action === 'botset' && req.method === 'POST') {
      const b = await readJson(req);
      const u = await sb.from('club_settings').upsert({ key: 'chatbot', value: { enabled: !!b.enabled }, updated_at: new Date().toISOString() });
      if (u.error) throw u.error;
      return send(res, 200, { ok: true, bot: !!b.enabled });
    }
    if (action === 'thread' && req.method === 'GET') {
      const convs = await groupConvs(sb, req.query.key);
      if (!convs.length) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      const ids = convs.map((c) => c.id);
      const after = Number(req.query.after) || 0;
      const { data: msgs, error } = await sb.from('chat_messages').select(MSG_COLS)
        .in('conversation_id', ids).gt('id', after).order('id', { ascending: true }).limit(800);
      if (error) throw error;
      const unread = convs.reduce((n, c) => n + (c.unread_admin || 0), 0);
      const agent = agentOf(req.query.agent);
      let joined = null;
      // Temsilci okunmamis mesaji actiginda musteriye "X sohbete katildi" bildirimi (ayni temsilci icin saatte en fazla bir)
      if (agent && unread > 0) joined = await ensureJoin(sb, convs[0], agent);
      if (unread > 0) await sb.from('chat_conversations').update({ unread_admin: 0 }).in('id', ids);
      const out = (msgs || []).slice();
      if (joined && !out.some((m) => m.id === joined.id)) out.push(joined);
      return send(res, 200, { ok: true, messages: out });
    }
    if (action === 'reply' && req.method === 'POST') {
      const b = await readJson(req);
      const body = s(b.body, MAX_BODY);
      if (!body) return send(res, 400, { ok: false, error: 'Mesaj bos' });
      const agent = agentOf(b.agent);
      if (!agent) return send(res, 400, { ok: false, error: 'Temsilci secilmedi' });
      const convs = await groupConvs(sb, b.key);
      if (!convs.length) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      // Temsilcinin ilk yanitindan ONCE katilma bildirimi gitsin (konusma temsilci secilmeden acilmis olabilir).
      const joined = await ensureJoin(sb, convs[0], agent);
      const msg = await addAdminMessage(sb, convs[0], body, 'panel', agent); // en son yazilan konusmaya gider
      return send(res, 200, { ok: true, message: msg, joined });
    }
    if (action === 'status' && req.method === 'POST') {
      const b = await readJson(req);
      const st = b.status === 'closed' ? 'closed' : 'open';
      const convs = await groupConvs(sb, b.key);
      if (!convs.length) return send(res, 404, { ok: false, error: 'Konusma bulunamadi' });
      const { error } = await sb.from('chat_conversations').update({ status: st }).in('id', convs.map((c) => c.id));
      if (error) throw error;
      return send(res, 200, { ok: true });
    }
    return send(res, 404, { ok: false, error: 'Bilinmeyen islem' });
  } catch (e) {
    return send(res, 500, { ok: false, error: String((e && e.message) || e).slice(0, 200) });
  }
}
