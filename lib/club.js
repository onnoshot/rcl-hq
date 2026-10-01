// RetroCameraLand - Retro Club sunucu mantigi. api/messages.js icinden cagrilir (Vercel 12-fonksiyon siniri).
// Uye:   kart numarasi = uyeligin anahtari. Ilk giriste uyelik olusur, sonraki girislerde ayni uyelik acilir.
// Panel: x-rcl-key (RCL_ALIM_KEY). Tablolar: rcl-community/supabase/schema_club.sql
import crypto from 'node:crypto';

const PUB = 'club-public', PRIV = 'club-private';
const KINDS = ['bulusma', 'kurs', 'workshop', 'gezi'];
const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 0/O, 1/I yok: karttan okunurken karismasin
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const USER_RE = /^[a-z0-9._]{3,20}$/;
const MEMBER_PUBLIC = 'id, username, name, city, instagram, bio, avatar_url, member_no, joined_at';
const DEFAULT_SETTINGS = {
  welcome_title: 'Hoş geldin',
  welcome_text: 'Retro Club üyelerine özel alan.',
  announcement: '',
  show_events: true, show_photos: true, show_soon: true, show_members: true,
};

const s = (v, max) => String(v == null ? '' : v).trim().slice(0, max || 120);
const esc = (x) => String(x || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export function makeCode() {
  const b = crypto.randomBytes(8);
  let o = '';
  for (let i = 0; i < 8; i++) o += ALPHA[b[i] % ALPHA.length];
  return 'RC-' + o.slice(0, 4) + '-' + o.slice(4);
}
function normCode(v) {
  const raw = String(v || '').toUpperCase().replace(/[^A-Z0-9]/g, '').replace(/^RC/, '');
  return raw.length === 8 ? 'RC-' + raw.slice(0, 4) + '-' + raw.slice(4) : '';
}
function cleanInsta(v) { return s(v, 40).replace(/^https?:\/\/(www\.)?instagram\.com\//i, '').replace(/^@/, '').replace(/[^a-zA-Z0-9._]/g, '').slice(0, 30); }

async function settings(sb) {
  const { data } = await sb.from('club_settings').select('value').eq('key', 'main').maybeSingle();
  return Object.assign({}, DEFAULT_SETTINGS, (data && data.value) || {});
}
async function memberFromReq(sb, req) {
  const h = String(req.headers.authorization || '');
  const token = h.startsWith('Bearer ') ? h.slice(7).trim() : '';
  if (!token || token.length < 20) return null;
  const { data: ses } = await sb.from('club_sessions').select('member_id').eq('token', token).maybeSingle();
  if (!ses) return null;
  const { data: m } = await sb.from('club_members').select('*').eq('id', ses.member_id).maybeSingle();
  return m && m.status === 'active' ? m : null;
}
// data URL (istemcide kucultulmus JPEG) -> Supabase Storage
async function saveImage(sb, bucket, folder, dataUrl) {
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ''));
  if (!m) throw new Error('Geçersiz görsel');
  const buf = Buffer.from(m[2], 'base64');
  if (buf.length < 2000 || buf.length > 4 * 1024 * 1024) throw new Error('Görsel boyutu uygun değil');
  const ext = m[1] === 'image/png' ? 'png' : (m[1] === 'image/webp' ? 'webp' : 'jpg');
  const path = folder + '/' + crypto.randomBytes(12).toString('hex') + '.' + ext;
  const up = await sb.storage.from(bucket).upload(path, buf, { contentType: m[1], cacheControl: '31536000', upsert: false });
  if (up.error) throw up.error;
  return bucket === PUB ? sb.storage.from(PUB).getPublicUrl(path).data.publicUrl : path;
}
async function sendMail(to, subject, html) {
  const key = process.env.BREVO_API_KEY;
  if (!key || !EMAIL_RE.test(to || '')) return false;
  try {
    const r = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST', headers: { 'api-key': key, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: { email: process.env.BREVO_SENDER_EMAIL || 'bilgi@retrocameraland.com', name: 'Retro Club' },
        to: [{ email: to }], subject, htmlContent: html,
      }),
    });
    return r.ok;
  } catch (e) { return false; }
}
const mailWrap = (inner) => '<div style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;background:#0b0b0c;color:#f5f5f7;border-radius:18px">' +
  '<p style="margin:0 0 18px;font-size:12px;letter-spacing:.2em;color:#cc0000">RETRO CLUB</p>' + inner +
  '<p style="margin:28px 0 0;font-size:12px;color:#86868b">RetroCameraLand</p></div>';

async function eventsWithPeople(sb, me, includeAll) {
  let q = sb.from('club_events').select('*').order('starts_at', { ascending: true }).limit(60);
  if (!includeAll) q = q.eq('status', 'published').gte('starts_at', new Date(Date.now() - 6 * 3600 * 1000).toISOString());
  const { data: evs } = await q;
  const list = evs || [];
  if (!list.length) return [];
  const { data: rs } = await sb.from('club_event_rsvps').select('event_id, member_id, created_at').in('event_id', list.map((e) => e.id));
  const ids = [...new Set((rs || []).map((r) => r.member_id))];
  const people = {};
  if (ids.length) {
    const { data: ms } = await sb.from('club_members').select(MEMBER_PUBLIC).in('id', ids);
    for (const m of ms || []) people[m.id] = m;
  }
  return list.map((e) => {
    const att = (rs || []).filter((r) => r.event_id === e.id).sort((a, b) => a.created_at.localeCompare(b.created_at))
      .map((r) => people[r.member_id]).filter(Boolean);
    return Object.assign({}, e, { attendees: att, going: !!(me && att.some((a) => a.id === me.id)), full: e.capacity > 0 && att.length >= e.capacity });
  });
}
async function soonCameras() {
  const store = process.env.SHOPIFY_STORE, token = process.env.SHOPIFY_ACCESS_TOKEN;
  if (!store || !token) return [];
  try {
    const r = await fetch('https://' + store + '/admin/api/2024-10/graphql.json', {
      method: 'POST', headers: { 'X-Shopify-Access-Token': token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '{products(first:20,query:"status:draft AND tag:club-onizleme",sortKey:UPDATED_AT,reverse:true){nodes{title vendor featuredImage{url} priceRangeV2{minVariantPrice{amount}}}}}' }),
    });
    const j = await r.json();
    return ((j.data && j.data.products && j.data.products.nodes) || []).map((p) => ({
      title: p.title, brand: p.vendor || '', image: (p.featuredImage && p.featuredImage.url) || '',
      price: Number(p.priceRangeV2 && p.priceRangeV2.minVariantPrice && p.priceRangeV2.minVariantPrice.amount) || 0,
    }));
  } catch (e) { return []; }
}
function meView(m) {
  return { id: m.id, username: m.username || '', name: m.name, email: m.email, city: m.city, instagram: m.instagram, bio: m.bio,
    avatar_url: m.avatar_url, member_no: m.member_no, joined_at: m.joined_at, card_code: m.card_code, needs_setup: !m.username };
}

export async function handle(action, req, res, ctx) {
  const { sb, send, readJson, isAdmin, tgSend } = ctx;
  const a = action.replace(/^club\./, '');

  // ================= HERKESE ACIK =================
  if (a === 'health') {
    const { error } = await sb.from('club_cards').select('code').limit(1);
    return send(res, error ? 503 : 200, { ok: !error });
  }
  if (a === 'enter' && req.method === 'POST') {
    const b = await readJson(req);
    const code = normCode(b.code);
    if (!code) return send(res, 400, { ok: false, error: 'Kart numarasını kartta yazdığı gibi gir.' });
    const { data: card } = await sb.from('club_cards').select('*').eq('code', code).maybeSingle();
    if (!card || card.status === 'void') return send(res, 404, { ok: false, error: 'Bu numara tanımlı değil. Karttaki numarayı kontrol et.' });
    let { data: member } = await sb.from('club_members').select('*').eq('card_code', code).maybeSingle();
    let isNew = false;
    if (!member) {
      const ins = await sb.from('club_members').insert({ card_code: code, via: card.batch === 'basvuru' ? 'application' : 'card' }).select('*').single();
      if (ins.error) { // ayni anda iki istek: digerinin olusturdugunu al
        const again = await sb.from('club_members').select('*').eq('card_code', code).maybeSingle();
        if (!again.data) throw ins.error;
        member = again.data;
      } else { member = ins.data; isNew = true; }
      await sb.from('club_cards').update({ status: 'used', used_at: new Date().toISOString() }).eq('code', code);
      if (card.batch === 'basvuru') { // basvurudan gelen uye: bilgileri hazir gelsin
        const { data: app } = await sb.from('club_applications').select('name, email, city, instagram').eq('card_code', code).maybeSingle();
        if (app) { await sb.from('club_members').update(app).eq('id', member.id); Object.assign(member, app); }
      }
    }
    if (member.status !== 'active') return send(res, 403, { ok: false, error: 'Üyeliğin askıda. Bizimle iletişime geç.' });
    const token = crypto.randomBytes(32).toString('hex');
    await sb.from('club_sessions').insert({ token, member_id: member.id });
    await sb.from('club_members').update({ last_seen_at: new Date().toISOString() }).eq('id', member.id);
    if (isNew) await tgSend('<b>Retro Club - yeni üye</b>\nKart: <code>' + esc(code) + '</code>\nÜye no: ' + member.member_no);
    return send(res, 200, { ok: true, token, isNew, me: meView(member) });
  }
  if (a === 'apply' && req.method === 'POST') {
    const b = await readJson(req);
    if (b.website) return send(res, 200, { ok: true });
    const name = s(b.name, 60), email = s(b.email, 120).toLowerCase(), camera = s(b.camera_model, 80);
    if (!name || !EMAIL_RE.test(email) || !camera) return send(res, 400, { ok: false, error: 'Ad, e-posta ve kamera modeli gerekli.' });
    if (!b.consent) return send(res, 400, { ok: false, error: 'Devam etmek için onay kutusunu işaretle.' });
    const dup = await sb.from('club_applications').select('id').eq('email', email).eq('status', 'pending').limit(1);
    if (dup.data && dup.data.length) return send(res, 409, { ok: false, error: 'Bu e-postayla bekleyen bir başvurun var.' });
    const selfie = await saveImage(sb, PRIV, 'selfie', b.selfie);
    const ins = await sb.from('club_applications').insert({
      name, email, city: s(b.city, 60), camera_model: camera, instagram: cleanInsta(b.instagram), note: s(b.note, 400),
      selfie_path: selfie, consent_at: new Date().toISOString(),
    }).select('id').single();
    if (ins.error) throw ins.error;
    await tgSend('<b>Retro Club - yeni başvuru</b>\n' + esc(name) + ' (' + esc(email) + ')\nKamera: ' + esc(camera) + '\nŞehir: ' + esc(s(b.city, 60)) +
      '\n\n<i>Panelde Retro Club sekmesinden onayla ya da reddet.</i>');
    return send(res, 200, { ok: true });
  }

  // ================= PANEL =================
  if (a.startsWith('admin')) {
    if (!isAdmin(req)) return send(res, 401, { ok: false, error: 'Yetkisiz' });
    if (a === 'admin' && req.method === 'GET') {
      const [apps, members, cards, photos, evs, st] = await Promise.all([
        sb.from('club_applications').select('*').order('created_at', { ascending: false }).limit(200),
        sb.from('club_members').select('*').order('joined_at', { ascending: false }).limit(1000),
        sb.from('club_cards').select('*').order('created_at', { ascending: false }).limit(2000),
        sb.from('club_photos').select('*').order('created_at', { ascending: false }).limit(200),
        eventsWithPeople(sb, null, true), settings(sb),
      ]);
      if (apps.error) throw apps.error;
      const appList = apps.data || [];
      await Promise.all(appList.filter((x) => x.selfie_path).slice(0, 60).map(async (x) => {
        const sg = await sb.storage.from(PRIV).createSignedUrl(x.selfie_path, 3600);
        x.selfie_url = (sg.data && sg.data.signedUrl) || '';
      }));
      const byId = {}; for (const m of members.data || []) byId[m.id] = m;
      return send(res, 200, { ok: true, applications: appList, members: members.data || [], cards: cards.data || [],
        photos: (photos.data || []).map((p) => Object.assign({}, p, { member: byId[p.member_id] ? (byId[p.member_id].username || byId[p.member_id].name) : '' })),
        events: evs, settings: st, kinds: KINDS });
    }
    if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'Method' });
    const b = await readJson(req);
    if (a === 'admin.application') {
      const { data: app } = await sb.from('club_applications').select('*').eq('id', s(b.id, 40)).maybeSingle();
      if (!app) return send(res, 404, { ok: false, error: 'Başvuru bulunamadı' });
      if (app.status !== 'pending') return send(res, 409, { ok: false, error: 'Bu başvuru zaten sonuçlandı' });
      const now = new Date().toISOString();
      if (b.decision === 'approve') {
        const code = makeCode();
        const c = await sb.from('club_cards').insert({ code, batch: 'basvuru', note: app.email });
        if (c.error) throw c.error;
        await sb.from('club_applications').update({ status: 'approved', card_code: code, reviewed_at: now, review_note: s(b.note, 300) }).eq('id', app.id);
        const mailed = await sendMail(app.email, 'Retro Club başvurun onaylandı', mailWrap(
          '<h1 style="margin:0 0 12px;font-size:26px;letter-spacing:-.02em">Kulübe hoş geldin, ' + esc(app.name) + '.</h1>' +
          '<p style="margin:0 0 20px;font-size:15px;line-height:1.55;color:#c7c7cc">Başvurun onaylandı. Aşağıdaki numara senin kulüp kartın; bu numarayla her zaman giriş yapabilirsin.</p>' +
          '<p style="margin:0 0 22px;padding:18px;border-radius:14px;background:#1c1c1f;font-family:Menlo,monospace;font-size:24px;letter-spacing:.12em;text-align:center;color:#fff">' + code + '</p>' +
          '<a href="https://retrocameraland.com/pages/retro-club" style="display:inline-block;padding:14px 26px;border-radius:100px;background:#cc0000;color:#fff;text-decoration:none;font-weight:600">Kulübe gir</a>'));
        return send(res, 200, { ok: true, code, mailed });
      }
      if (b.decision === 'reject') {
        if (app.selfie_path) await sb.storage.from(PRIV).remove([app.selfie_path]);
        await sb.from('club_applications').update({ status: 'rejected', reviewed_at: now, review_note: s(b.note, 300), selfie_path: '' }).eq('id', app.id);
        const mailed = await sendMail(app.email, 'Retro Club başvurun hakkında', mailWrap(
          '<h1 style="margin:0 0 12px;font-size:24px;letter-spacing:-.02em">Merhaba ' + esc(app.name) + ',</h1>' +
          '<p style="margin:0;font-size:15px;line-height:1.55;color:#c7c7cc">Başvurunu inceledik ancak şu an onaylayamadık. Retro dijital kameranla çektiğin net bir selfie ile yeniden başvurabilirsin.</p>'));
        return send(res, 200, { ok: true, mailed });
      }
      return send(res, 400, { ok: false, error: 'Karar eksik' });
    }
    if (a === 'admin.event') {
      if (b.delete) {
        const d = await sb.from('club_events').delete().eq('id', s(b.id, 40));
        if (d.error) throw d.error;
        return send(res, 200, { ok: true });
      }
      const title = s(b.title, 120), starts = new Date(b.starts_at);
      if (!title || isNaN(starts.getTime())) return send(res, 400, { ok: false, error: 'Başlık ve tarih gerekli' });
      const row = {
        kind: KINDS.indexOf(b.kind) >= 0 ? b.kind : 'bulusma', title, description: s(b.description, 2000),
        starts_at: starts.toISOString(), ends_at: b.ends_at && !isNaN(new Date(b.ends_at).getTime()) ? new Date(b.ends_at).toISOString() : null,
        place: s(b.place, 160), city: s(b.city, 60), capacity: Math.max(0, Math.min(5000, Number(b.capacity) || 0)),
        status: ['draft', 'published', 'cancelled'].indexOf(b.status) >= 0 ? b.status : 'published',
      };
      if (b.cover && String(b.cover).startsWith('data:')) row.cover_url = await saveImage(sb, PUB, 'event', b.cover);
      else if (b.cover_url != null) row.cover_url = s(b.cover_url, 400);
      const q = b.id ? sb.from('club_events').update(row).eq('id', s(b.id, 40)) : sb.from('club_events').insert(row);
      const r = await q.select('*').single();
      if (r.error) throw r.error;
      return send(res, 200, { ok: true, event: r.data });
    }
    if (a === 'admin.cards') {
      const n = Math.max(1, Math.min(500, Number(b.count) || 0));
      const rows = [], seen = {};
      while (rows.length < n) { const c = makeCode(); if (!seen[c]) { seen[c] = 1; rows.push({ code: c, batch: s(b.batch, 40) || new Date().toISOString().slice(0, 10), note: s(b.note, 80) }); } }
      const ins = await sb.from('club_cards').insert(rows);
      if (ins.error) throw ins.error;
      return send(res, 200, { ok: true, codes: rows.map((r) => r.code) });
    }
    if (a === 'admin.card') {
      const st = b.status === 'void' ? 'void' : 'unused';
      const u = await sb.from('club_cards').update({ status: st }).eq('code', normCode(b.code)).neq('status', 'used');
      if (u.error) throw u.error;
      return send(res, 200, { ok: true });
    }
    if (a === 'admin.member') {
      const u = await sb.from('club_members').update({ status: b.status === 'suspended' ? 'suspended' : 'active' }).eq('id', s(b.id, 40));
      if (u.error) throw u.error;
      if (b.status === 'suspended') await sb.from('club_sessions').delete().eq('member_id', s(b.id, 40));
      return send(res, 200, { ok: true });
    }
    if (a === 'admin.photo') {
      const u = b.delete ? await sb.from('club_photos').delete().eq('id', s(b.id, 40))
        : await sb.from('club_photos').update({ status: b.status === 'hidden' ? 'hidden' : 'visible' }).eq('id', s(b.id, 40));
      if (u.error) throw u.error;
      return send(res, 200, { ok: true });
    }
    if (a === 'admin.settings') {
      const v = {
        welcome_title: s(b.welcome_title, 80), welcome_text: s(b.welcome_text, 300), announcement: s(b.announcement, 300),
        show_events: !!b.show_events, show_photos: !!b.show_photos, show_soon: !!b.show_soon, show_members: !!b.show_members,
      };
      const u = await sb.from('club_settings').upsert({ key: 'main', value: v, updated_at: new Date().toISOString() });
      if (u.error) throw u.error;
      return send(res, 200, { ok: true, settings: v });
    }
    return send(res, 404, { ok: false, error: 'Bilinmeyen islem' });
  }

  // ================= UYE =================
  const me = await memberFromReq(sb, req);
  if (!me) return send(res, 401, { ok: false, error: 'Oturum yok' });

  if (a === 'home' && req.method === 'GET') {
    const st = await settings(sb);
    const [evs, photos, soon, members] = await Promise.all([
      st.show_events ? eventsWithPeople(sb, me, false) : [],
      st.show_photos ? sb.from('club_photos').select('*').eq('status', 'visible').order('created_at', { ascending: false }).limit(60) : { data: [] },
      st.show_soon ? soonCameras() : [],
      sb.from('club_members').select(MEMBER_PUBLIC).eq('status', 'active').not('username', 'is', null).order('joined_at', { ascending: false }).limit(300),
    ]);
    const ms = members.data || [], byId = {};
    for (const m of ms) byId[m.id] = m;
    const pl = photos.data || [];
    let liked = {};
    if (pl.length) {
      const lk = await sb.from('club_photo_likes').select('photo_id').eq('member_id', me.id).in('photo_id', pl.map((p) => p.id));
      for (const l of lk.data || []) liked[l.photo_id] = 1;
    }
    sb.from('club_members').update({ last_seen_at: new Date().toISOString() }).eq('id', me.id).then(() => {});
    return send(res, 200, { ok: true, me: meView(me), settings: st, events: evs, soon,
      photos: pl.map((p) => ({ id: p.id, image_url: p.image_url, camera_title: p.camera_title, caption: p.caption, location: p.location, like_count: p.like_count,
        created_at: p.created_at, liked: !!liked[p.id], mine: p.member_id === me.id, by: byId[p.member_id] ? { username: byId[p.member_id].username, avatar_url: byId[p.member_id].avatar_url } : null })),
      members: st.show_members ? ms : [], member_count: ms.length });
  }
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'Method' });
  const b = await readJson(req);

  if (a === 'profile') {
    const username = s(b.username, 20).toLowerCase();
    if (!USER_RE.test(username)) return send(res, 400, { ok: false, error: 'Kullanıcı adı 3-20 karakter olmalı; küçük harf, rakam, nokta ve alt çizgi kullanabilirsin.' });
    const taken = await sb.from('club_members').select('id').eq('username', username).neq('id', me.id).limit(1);
    if (taken.data && taken.data.length) return send(res, 409, { ok: false, error: 'Bu kullanıcı adı alınmış.' });
    const row = { username, name: s(b.name, 60), city: s(b.city, 60), instagram: cleanInsta(b.instagram), bio: s(b.bio, 200) };
    if (b.email != null && (b.email === '' || EMAIL_RE.test(s(b.email, 120)))) row.email = s(b.email, 120).toLowerCase();
    if (b.avatar && String(b.avatar).startsWith('data:')) row.avatar_url = await saveImage(sb, PUB, 'avatar', b.avatar);
    const u = await sb.from('club_members').update(row).eq('id', me.id).select('*').single();
    if (u.error) throw u.error;
    return send(res, 200, { ok: true, me: meView(u.data) });
  }
  if (!me.username) return send(res, 409, { ok: false, error: 'Önce kullanıcı adını seç.' });

  if (a === 'rsvp') {
    const id = s(b.id, 40);
    const { data: ev } = await sb.from('club_events').select('id, capacity, status').eq('id', id).maybeSingle();
    if (!ev || ev.status !== 'published') return send(res, 404, { ok: false, error: 'Etkinlik bulunamadı' });
    if (b.going) {
      if (ev.capacity > 0) {
        const c = await sb.from('club_event_rsvps').select('member_id').eq('event_id', id).limit(ev.capacity + 1);
        const rows = c.data || [];
        if (rows.length >= ev.capacity && !rows.some((r) => r.member_id === me.id)) return send(res, 409, { ok: false, error: 'Kontenjan doldu.' });
      }
      const ins = await sb.from('club_event_rsvps').upsert({ event_id: id, member_id: me.id });
      if (ins.error) throw ins.error;
    } else {
      await sb.from('club_event_rsvps').delete().eq('event_id', id).eq('member_id', me.id);
    }
    const evs = await eventsWithPeople(sb, me, false);
    return send(res, 200, { ok: true, event: evs.find((e) => e.id === id) || null });
  }
  if (a === 'photo') {
    if (b.delete) {
      await sb.from('club_photos').delete().eq('id', s(b.id, 40)).eq('member_id', me.id);
      return send(res, 200, { ok: true });
    }
    const camera = s(b.camera_title, 80);
    if (!camera) return send(res, 400, { ok: false, error: 'Hangi kamerayla çektiğini seç.' });
    const url = await saveImage(sb, PUB, 'photo', b.image);
    const ins = await sb.from('club_photos').insert({ member_id: me.id, image_url: url, camera_title: camera, caption: s(b.caption, 200), location: s(b.location, 80) }).select('*').single();
    if (ins.error) throw ins.error;
    return send(res, 200, { ok: true, photo: ins.data });
  }
  if (a === 'like') {
    const id = s(b.id, 40);
    const ex = await sb.from('club_photo_likes').select('photo_id').eq('photo_id', id).eq('member_id', me.id).maybeSingle();
    if (ex.data) await sb.from('club_photo_likes').delete().eq('photo_id', id).eq('member_id', me.id);
    else await sb.from('club_photo_likes').insert({ photo_id: id, member_id: me.id });
    const c = await sb.from('club_photo_likes').select('member_id').eq('photo_id', id).limit(5000);
    const n = (c.data || []).length;
    await sb.from('club_photos').update({ like_count: n }).eq('id', id);
    return send(res, 200, { ok: true, liked: !ex.data, like_count: n });
  }
  if (a === 'logout') {
    const h = String(req.headers.authorization || '');
    await sb.from('club_sessions').delete().eq('token', h.slice(7).trim());
    return send(res, 200, { ok: true });
  }
  return send(res, 404, { ok: false, error: 'Bilinmeyen islem' });
}
