// RetroCameraLand - Retro Club sunucu mantigi. api/messages.js icinden cagrilir (Vercel 12-fonksiyon siniri).
// Uye:   kart numarasi = uyeligin anahtari. Ilk giriste uyelik olusur, sonraki girislerde ayni uyelik acilir.
// Panel: x-rcl-key (RCL_ALIM_KEY). Tablolar: rcl-community/supabase/schema_club.sql + schema_club_v3.sql
import crypto from 'node:crypto';

const PUB = 'club-public', PRIV = 'club-private';
const KINDS = ['bulusma', 'kurs', 'workshop', 'gezi'];
const KIND_TR = { bulusma: 'Buluşma', kurs: 'Kurs', workshop: 'Workshop', gezi: 'Gezi' };
const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 0/O, 1/I yok: karttan okunurken karismasin
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const USER_RE = /^[a-z0-9._]{3,20}$/;
const SITE = 'https://retrocameraland.com/pages/retro-club';
const CARD_HANDLE = 'retro-club-card'; // magazadaki kart urunu (tek seferlik ucretli uyelik)
const MEMBER_PUBLIC = 'id, username, name, country, city, instagram, bio, avatar_url, cover_url, camera_model, camera_image_url, profile, member_no, joined_at';
const DEFAULT_SETTINGS = {
  welcome_title: 'Hoş geldin',
  welcome_text: 'Retro Club üyelerine özel alan.',
  announcement: '',
  show_events: true, show_soon: true, show_members: true,
};

// Rozet katalogu. core: seviye yolculugunda sayilan cekirdek rozetler. admin: yalnizca panelden verilir.
export const BADGES = [
  { id: 'kurucu', name: 'Kurucu Üye', desc: 'Kulübün ilk 250 üyesinden biri.' },
  { id: 'kimlik', name: 'Tam Kadro', desc: 'Profilini fotoğrafın, şehrin ve kameranla tamamla.', core: true },
  { id: 'ilk-bulusma', name: 'İlk Buluşma', desc: 'İlk kulüp etkinliğine katıl.', core: true },
  { id: 'kursiyer', name: 'Kursiyer', desc: 'Bir kurs ya da workshop tamamla.', core: true },
  { id: 'gezgin', name: 'Gezgin', desc: 'Bir kulüp gezisine katıl.', core: true },
  { id: 'mudavim', name: 'Müdavim', desc: 'Beş etkinliğe katıl.', core: true },
  { id: 'usta', name: 'Usta', desc: 'Üç kurs ya da workshop tamamla.', core: true },
  { id: 'sehir-baskani', name: 'Şehir Başkanı', desc: 'Şehrindeki üyeleri buluşturan kişi. Kulüp ekibi verir.', admin: true, city: true },
  { id: 'elci', name: 'Kulüp Elçisi', desc: 'Kulübü yeni insanlarla tanıştıranlara verilir.', admin: true },
  { id: 'ayin-uyesi', name: 'Ayın Üyesi', desc: 'Ayın en aktif üyesine kulüp ekibi verir.', admin: true },
  { id: 'egitmen', name: 'Eğitmen', desc: 'Kulüpte kurs ya da workshop veren üye.', admin: true },
  { id: 'koleksiyoner', name: 'Koleksiyoner', desc: 'Dikkat çeken bir retro kamera koleksiyonu olan üye.', admin: true },
  { id: 'efsane', name: 'Efsane', desc: 'Kulübe iz bırakan katkılar için.', admin: true },
];
const BADGE_BY_ID = Object.fromEntries(BADGES.map((b) => [b.id, b]));
// Cekirdek rozet sayisina gore seviyeler ve acilan ayricaliklar.
export const LEVELS = [
  { need: 0, name: 'Çaylak', perk: 'Takvim, üyeler haritası ve erken erişim senin.' },
  { need: 2, name: 'Kadrajcı', perk: 'Profilinde seviye nişanı ve etkinliklerde öncelikli yer.' },
  { need: 4, name: 'Etkinlik Kurucusu', perk: 'Kendi etkinliğini oluşturup kulübe önerebilirsin.', propose: true },
  { need: 6, name: 'Yol Arkadaşı', perk: 'RetroCameraLand ekibiyle yurt dışı seyahati çekilişine katılma hakkı.' },
];
const ACCENTS = ['#cc0000', '#ff9f0a', '#30d158', '#0a84ff', '#bf5af2', '#c7c7cc'];
const SKINS = ['gece', 'krom', 'film', 'flas'];
const TAGS = ['Sokak', 'Portre', 'Gece', 'Seyahat', 'Konser', 'Doğa', 'Mimari', 'Günlük', 'Flaş', 'Moda', 'Video', 'Siyah beyaz'];

const s = (v, max) => String(v == null ? '' : v).trim().slice(0, max || 120);
const esc = (x) => String(x || '-').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pad4 = (n) => ('0000' + (n || 0)).slice(-Math.max(4, String(n || 0).length));
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
// Uyenin sectigi gorunum tercihleri: yalnizca bilinen alanlar ve degerler saklanir.
function cleanProfile(p, prev) {
  const o = Object.assign({}, prev || {});
  if (!p || typeof p !== 'object') return o;
  if (ACCENTS.indexOf(p.accent) >= 0) o.accent = p.accent;
  if (SKINS.indexOf(p.skin) >= 0) o.skin = p.skin;
  if (Array.isArray(p.tags)) o.tags = p.tags.filter((t) => TAGS.indexOf(t) >= 0).slice(0, 5);
  if (p.open != null) o.open = !!p.open;
  if (p.showcase != null) o.showcase = BADGE_BY_ID[p.showcase] ? p.showcase : '';
  if (Array.isArray(p.collection)) o.collection = p.collection.map((c) => s(c, 80)).filter(Boolean).slice(0, 6);
  return o;
}
const shopImg = (u) => /^https:\/\/cdn\.shopify\.com\/[^\s"'<>]+$/.test(String(u || '')) ? s(u, 400) : '';

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
        sender: { email: process.env.BREVO_SENDER_EMAIL || 'bilgi@retrocameraland.com', name: 'Retro Camera Land' },
        to: [{ email: to }], subject, htmlContent: html,
      }),
    });
    return r.ok;
  } catch (e) { return false; }
}
const LOGO = 'https://rclhq.vercel.app/club-avatars/rcl-logo-mail.png';
const F_SANS = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const F_MONO = "font-family:'SF Mono',Menlo,Consolas,'Courier New',monospace";
// Tum kulup e-postalarinin kabugu: siyah zemin, ustte Retro Camera Land logosu.
const mailWrap = (inner, preheader) => '<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark"><title>Retro Camera Land</title></head>' +
  '<body style="margin:0;padding:0;background:#000000">' +
  '<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#000000">' + esc(preheader || 'Retro Club') + '</div>' +
  '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#000000"><tr><td align="center" style="padding:28px 14px 40px">' +
  '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px">' +
  '<tr><td align="center" style="padding:6px 0 26px"><a href="https://retrocameraland.com" style="text-decoration:none"><img src="' + LOGO + '" width="150" alt="Retro Camera Land" style="display:block;border:0;width:150px;height:auto;' + F_SANS + ';font-size:20px;font-weight:700;color:#ffffff"></a></td></tr>' +
  '<tr><td style="' + F_SANS + ';color:#f5f5f7">' + inner + '</td></tr>' +
  '<tr><td align="center" style="padding:34px 0 0;' + F_SANS + ';font-size:12px;line-height:1.6;color:#6e6e73">Retro Camera Land · Retro Club<br><a href="https://retrocameraland.com" style="color:#6e6e73;text-decoration:underline">retrocameraland.com</a></td></tr>' +
  '</table></td></tr></table></body></html>';
const mailH1 = (t) => '<h1 style="margin:0 0 12px;font-size:30px;line-height:1.1;letter-spacing:-.03em;font-weight:700;color:#ffffff">' + t + '</h1>';
const mailP = (t) => '<p style="margin:0 0 18px;font-size:16px;line-height:1.55;color:#c7c7cc">' + t + '</p>';
const mailBtn = (label) => '<table role="presentation" cellpadding="0" cellspacing="0"><tr><td bgcolor="#cc0000" style="border-radius:100px"><a href="' + SITE + '" style="display:inline-block;padding:16px 34px;' + F_SANS + ';font-size:16px;font-weight:600;color:#ffffff;text-decoration:none;border-radius:100px">' + label + '</a></td></tr></table>';
// Kartin kendisi: uye numarasi (varsa) ve kart numarasi ustunde.
function mailCard(name, memberNo, code) {
  const lbl = 'margin:0 0 5px;font-size:10px;letter-spacing:.24em;color:#8e8e93;' + F_SANS;
  return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="#141416" style="border-collapse:separate;border-radius:22px;border:1px solid #34343a;background-color:#141416;background-image:linear-gradient(135deg,#26262b 0%,#0e0e10 52%,#1d1d21 100%);box-shadow:0 30px 60px -30px #cc0000">' +
    '<tr><td style="padding:24px 24px 22px">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>' +
    '<td style="font-size:11px;font-weight:600;letter-spacing:.3em;color:#d1d1d6;' + F_SANS + '">RETRO CLUB</td>' +
    '<td align="right"><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#cc0000"></span></td></tr></table>' +
    '<p style="margin:30px 0 0;font-size:22px;font-weight:600;letter-spacing:-.02em;color:#ffffff;' + F_SANS + '">' + esc(name || 'Kulüp üyesi') + '</p>' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:26px"><tr>' +
    (memberNo ? '<td valign="bottom" width="38%"><p style="' + lbl + '">ÜYE NO</p><p style="margin:0;font-size:30px;line-height:1;letter-spacing:.04em;color:#ffffff;' + F_MONO + '">' + esc(pad4(memberNo)) + '</p></td>' : '') +
    '<td valign="bottom"><p style="' + lbl + '">KART NUMARASI</p><p style="margin:0;font-size:19px;line-height:1.3;letter-spacing:.1em;color:#ffffff;white-space:nowrap;' + F_MONO + '">' + esc(code) + '</p></td></tr></table>' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:26px;border-top:1px solid #2c2c31"><tr>' +
    '<td style="padding-top:14px;font-size:10px;letter-spacing:.2em;color:#8e8e93;' + F_SANS + '">ÜYE KARTI · ' + new Date().getFullYear() + '</td>' +
    '<td align="right" style="padding-top:12px"><img src="' + LOGO + '" width="62" alt="Retro Camera Land" style="display:block;border:0;width:62px;height:auto"></td></tr></table>' +
    '</td></tr></table>';
}
// Kart e-postasi: panelden gonderilen (uye numarali) ve satin alim sonrasi (numarasiz) ayni tasarimi kullanir.
function cardMail(name, memberNo, codes) {
  const list = Array.isArray(codes) ? codes : [codes], first = esc(String(name || '').split(' ')[0]);
  const step = (n, t) => '<tr><td width="34" valign="top" style="padding:11px 0;border-top:1px solid #1f1f23;font-size:13px;color:#cc0000;' + F_MONO + '">0' + n + '</td><td style="padding:11px 0;border-top:1px solid #1f1f23;font-size:15px;line-height:1.45;color:#e5e5ea;' + F_SANS + '">' + t + '</td></tr>';
  return mailWrap(
    '<p style="margin:0 0 14px;font-size:11px;font-weight:600;letter-spacing:.26em;color:#cc0000">RETRO CLUB · ÜYE KARTIN</p>' +
    mailH1((first ? first + ', ' : '') + 'artık kulüptesin.') +
    mailP('Bu kart senin için hazırlandı. ' + (memberNo ? 'Üzerindeki üye numarası yalnızca sana ait; kulüpte seni bu numarayla tanıyacağız.' : 'Kart numaran yalnızca sana ait; kulübün kapısını o açar.')) +
    list.map((c) => '<div style="margin:0 0 14px">' + mailCard(name, memberNo, c) + '</div>').join('') +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0 26px;border-bottom:1px solid #1f1f23">' +
    step(1, 'Aşağıdaki düğmeyle kulübün kapısına gel.') + step(2, 'Kart numaranı yaz: <span style="color:#ffffff;white-space:nowrap;' + F_MONO + '">' + esc(list[0]) + '</span>') + step(3, 'Adını, şehrini ve kameranı seç. Gerisi içeride.') + '</table>' +
    mailBtn('Kulübe gir') +
    '<p style="margin:30px 0 8px;font-size:11px;font-weight:600;letter-spacing:.26em;color:#8e8e93">İÇERİDE SENİ BEKLEYENLER</p>' +
    mailP('Buluşmalar, kurslar ve geziler. Şehrindeki üyeler. Katıldıkça kazandığın rozetler. Yeni gelen kameraları herkesten bir hafta önce görme hakkı.') +
    '<p style="margin:0;font-size:13px;line-height:1.55;color:#8e8e93">Bu e-postayı sakla. Kart numaran tek kişiliktir; kimseyle paylaşma. Başka bir cihazda aynı numarayla girersin.</p>',
    'Üye kartın hazır. Kulübün kapısı sana açık.');
}

async function eventsWithPeople(sb, me, includeAll) {
  let q = sb.from('club_events').select('*').order('starts_at', { ascending: true }).limit(80);
  if (!includeAll) q = q.eq('status', 'published').gte('starts_at', new Date(Date.now() - 6 * 3600 * 1000).toISOString());
  const { data: evs } = await q;
  const list = evs || [];
  if (!list.length) return [];
  const { data: rs } = await sb.from('club_event_rsvps').select('event_id, member_id, created_at').in('event_id', list.map((e) => e.id));
  const ids = [...new Set((rs || []).map((r) => r.member_id).concat(list.map((e) => e.proposed_by).filter(Boolean)))];
  const people = {};
  if (ids.length) {
    const { data: ms } = await sb.from('club_members').select(MEMBER_PUBLIC).in('id', ids);
    for (const m of ms || []) people[m.id] = m;
  }
  return list.map((e) => {
    const att = (rs || []).filter((r) => r.event_id === e.id).sort((a, b) => a.created_at.localeCompare(b.created_at))
      .map((r) => people[r.member_id]).filter(Boolean);
    return Object.assign({}, e, { attendees: att, going: !!(me && att.some((a) => a.id === me.id)), full: e.capacity > 0 && att.length >= e.capacity,
      proposer: e.proposed_by && people[e.proposed_by] ? people[e.proposed_by].username : '' });
  });
}
// Ziyaretciye yalnizca tanitim: ad, tur, ay ve gorsel. Yer, saat ve aciklama uyelere ozel.
const publicEvent = (e) => ({ id: e.id, kind: e.kind, title: e.title, starts_at: String(e.starts_at).slice(0, 7) + '-15T12:00:00Z', cover_url: e.cover_url });
async function shopifyGql(query, variables) {
  const store = process.env.SHOPIFY_STORE, token = process.env.SHOPIFY_ACCESS_TOKEN;
  if (!store || !token) return null;
  const r = await fetch('https://' + store + '/admin/api/2024-10/graphql.json', {
    method: 'POST', headers: { 'X-Shopify-Access-Token': token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  return r.json();
}
async function soonCameras() {
  try {
    const j = await shopifyGql('{products(first:20,query:"status:draft AND tag:club-onizleme",sortKey:UPDATED_AT,reverse:true){nodes{title vendor featuredImage{url} priceRangeV2{minVariantPrice{amount}}}}}');
    return ((j && j.data && j.data.products && j.data.products.nodes) || []).map((p) => ({
      title: p.title, brand: p.vendor || '', image: (p.featuredImage && p.featuredImage.url) || '',
      price: Number(p.priceRangeV2 && p.priceRangeV2.minVariantPrice && p.priceRangeV2.minVariantPrice.amount) || 0,
    }));
  } catch (e) { return []; }
}

// ---- rozetler ----
// Gecmis etkinliklere katilim: { member_id: { total, course, trip } }
async function attendance(sb) {
  const { data: evs } = await sb.from('club_events').select('id, kind').eq('status', 'published').lt('starts_at', new Date().toISOString()).limit(1000);
  const kind = {}; for (const e of evs || []) kind[e.id] = e.kind;
  const ids = Object.keys(kind), out = {};
  if (!ids.length) return out;
  const { data: rs } = await sb.from('club_event_rsvps').select('event_id, member_id').in('event_id', ids).limit(20000);
  for (const r of rs || []) {
    const o = out[r.member_id] || (out[r.member_id] = { total: 0, course: 0, trip: 0 });
    o.total++;
    if (kind[r.event_id] === 'kurs' || kind[r.event_id] === 'workshop') o.course++;
    if (kind[r.event_id] === 'gezi') o.trip++;
  }
  return out;
}
async function awardsByMember(sb) {
  const { data } = await sb.from('club_member_badges').select('id, member_id, badge, city, note, awarded_at').order('awarded_at', { ascending: true }).limit(10000);
  const out = {};
  for (const a of data || []) (out[a.member_id] || (out[a.member_id] = [])).push(a);
  return out;
}
function progressOf(m, st) {
  st = st || { total: 0, course: 0, trip: 0 };
  const filled = [m.avatar_url, m.city, m.camera_model, m.bio].filter(Boolean).length;
  return {
    'kimlik': [filled, 4], 'ilk-bulusma': [Math.min(st.total, 1), 1], 'kursiyer': [Math.min(st.course, 1), 1],
    'gezgin': [Math.min(st.trip, 1), 1], 'mudavim': [Math.min(st.total, 5), 5], 'usta': [Math.min(st.course, 3), 3],
  };
}
function badgesOf(m, st, awards) {
  const got = [], seen = {};
  const add = (id, city) => { const k = id + '|' + (city || ''); if (!seen[k] && BADGE_BY_ID[id]) { seen[k] = 1; got.push(city ? { id, city } : { id }); } };
  if (m.member_no <= 250) add('kurucu');
  const pr = progressOf(m, st);
  for (const id of Object.keys(pr)) if (pr[id][0] >= pr[id][1]) add(id);
  for (const a of awards || []) add(a.badge, a.city);
  return got;
}
function levelOf(badges) {
  const core = new Set(badges.filter((b) => BADGE_BY_ID[b.id].core).map((b) => b.id)).size;
  let idx = 0;
  LEVELS.forEach((l, i) => { if (core >= l.need) idx = i; });
  return { index: idx, core, name: LEVELS[idx].name, propose: LEVELS.some((l, i) => i <= idx && l.propose) };
}
function meView(m) {
  return { id: m.id, username: m.username || '', name: m.name, email: m.email, country: m.country || 'TR', city: m.city, instagram: m.instagram, bio: m.bio,
    avatar_url: m.avatar_url, cover_url: m.cover_url || '', camera_model: m.camera_model || '', camera_image_url: m.camera_image_url || '', profile: m.profile || {},
    member_no: m.member_no, joined_at: m.joined_at, card_code: m.card_code, needs_setup: !m.username, intro_seen: !!m.intro_seen };
}
async function memberCount(sb) {
  const { count } = await sb.from('club_members').select('id', { count: 'exact', head: true }).eq('status', 'active').not('username', 'is', null);
  return count || 0;
}

export async function handle(action, req, res, ctx) {
  const { sb, send, readJson, isAdmin, tgSend } = ctx;
  const a = action.replace(/^club\./, '');

  // ================= HERKESE ACIK =================
  if (a === 'health') {
    const { error } = await sb.from('club_members').select('country, intro_seen').limit(1);
    const { error: e2 } = await sb.from('club_member_badges').select('id').limit(1);
    return send(res, error || e2 ? 503 : 200, { ok: !(error || e2) });
  }
  // Karsilama sayfasi: yayindaki etkinlik afisleri (katilimci bilgisi yok) ve uye sayisi.
  if (a === 'events' && req.method === 'GET') {
    const { data } = await sb.from('club_events').select('*').eq('status', 'published')
      .gte('starts_at', new Date(Date.now() - 6 * 3600 * 1000).toISOString()).order('starts_at', { ascending: true }).limit(12);
    // Sayacin etrafindaki profil bulutu: yalniz acilis hesaplarinin gorselleri (isim yok, gercek uye fotografi yok).
    const { data: av } = await sb.from('club_members').select('avatar_url').eq('status', 'active').eq('is_seed', true).not('avatar_url', 'is', null).limit(100);
    return send(res, 200, { ok: true, events: (data || []).map(publicEvent), member_count: await memberCount(sb),
      avatars: (av || []).map((m) => m.avatar_url) });
  }
  if (a === 'ics' && req.method === 'GET') {
    const { data: e } = await sb.from('club_events').select('*').eq('id', s(req.query.id, 40)).eq('status', 'published').maybeSingle();
    if (!e) return send(res, 404, { ok: false, error: 'Etkinlik bulunamadı' });
    const t = (d) => new Date(d).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    const x = (v) => String(v || '').replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n').replace(/([,;])/g, '\\$1');
    const end = e.ends_at || new Date(new Date(e.starts_at).getTime() + 2 * 3600 * 1000).toISOString();
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//RetroCameraLand//Retro Club//TR', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
      'UID:' + e.id + '@retrocameraland.com', 'DTSTAMP:' + t(Date.now()), 'DTSTART:' + t(e.starts_at), 'DTEND:' + t(end),
      'SUMMARY:' + x('Retro Club: ' + e.title), 'LOCATION:' + x([e.place, e.city].filter(Boolean).join(', ')),
      'DESCRIPTION:' + x((e.description ? e.description + '\n\n' : '') + SITE), 'URL:' + SITE,
      'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + x(e.title), 'TRIGGER:-P1D', 'END:VALARM',
      'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + x(e.title), 'TRIGGER:-PT2H', 'END:VALARM', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    res.status(200).setHeader('Content-Type', 'text/calendar; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="retro-club-etkinlik.ics"');
    res.setHeader('Cache-Control', 'no-store');
    return res.end(ics);
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
      const row = { card_code: code, via: card.batch === 'basvuru' ? 'application' : (card.batch === 'satis' ? 'purchase' : 'card') };
      if (card.member_no) row.member_no = card.member_no; // panelden ayrilmis uye numarasi
      if (EMAIL_RE.test(card.email || '')) row.email = card.email;
      const ins = await sb.from('club_members').insert(row).select('*').single();
      if (ins.error) { // ayni anda iki istek: digerinin olusturdugunu al
        const again = await sb.from('club_members').select('*').eq('card_code', code).maybeSingle();
        if (!again.data) throw ins.error;
        member = again.data;
      } else { member = ins.data; isNew = true; }
      await sb.from('club_cards').update({ status: 'used', used_at: new Date().toISOString() }).eq('code', code);
      if (card.batch === 'basvuru') { // basvurudan gelen uye: bilgileri hazir gelsin
        const { data: app } = await sb.from('club_applications').select('name, email, city, instagram, camera_model').eq('card_code', code).maybeSingle();
        if (app) {
          const pre = { name: app.name, email: app.email, city: app.city, instagram: app.instagram, camera_model: app.camera_model };
          await sb.from('club_members').update(pre).eq('id', member.id); Object.assign(member, pre);
        }
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
  // Retro Club Card satin alan: siparis numarasi + e-posta ile kart numarasini alir (siparis basina bir kez uretilir).
  if (a === 'claim' && req.method === 'POST') {
    const b = await readJson(req);
    if (b.website) return send(res, 200, { ok: true });
    const email = s(b.email, 120).toLowerCase(), num = s(b.order, 20).replace(/[^0-9]/g, '');
    if (!num || !EMAIL_RE.test(email)) return send(res, 400, { ok: false, error: 'Sipariş numaranı ve siparişte kullandığın e-postayı yaz.' });
    let j = null;
    try {
      j = await shopifyGql('query($q:String!){orders(first:1,query:$q){nodes{id name email cancelledAt displayFinancialStatus customer{firstName} lineItems(first:30){nodes{quantity product{handle}}}}}}', { q: 'name:#' + num });
    } catch (e) { j = null; }
    if (!j || j.errors || !j.data) return send(res, 503, { ok: false, error: 'Sipariş şu an doğrulanamadı. Biraz sonra tekrar dene ya da sohbetten bize yaz.' });
    const o = j.data.orders.nodes[0];
    const miss = 'Bu bilgilerle bir Retro Club Card siparişi bulamadık. Numarayı ve e-postayı kontrol et.';
    if (!o || String(o.email || '').toLowerCase() !== email || o.cancelledAt) return send(res, 404, { ok: false, error: miss });
    const qty = Math.min(5, o.lineItems.nodes.filter((l) => l.product && l.product.handle === CARD_HANDLE).reduce((n, l) => n + l.quantity, 0));
    if (!qty) return send(res, 404, { ok: false, error: miss });
    if (o.displayFinancialStatus !== 'PAID') return send(res, 409, { ok: false, error: 'Siparişinin ödemesi henüz onaylanmadı. Onaylanınca kartın tanımlanır.' });
    const prev = await sb.from('club_card_orders').select('card_code, idx').eq('order_id', o.id).order('idx');
    let codes = (prev.data || []).map((r) => r.card_code);
    if (!codes.length) {
      codes = []; while (codes.length < qty) { const c = makeCode(); if (codes.indexOf(c) < 0) codes.push(c); }
      const c = await sb.from('club_cards').insert(codes.map((code) => ({ code, batch: 'satis', note: o.name, email })));
      if (c.error) throw c.error;
      const ins = await sb.from('club_card_orders').insert(codes.map((code, idx) => ({ order_id: o.id, idx, order_name: o.name, email, card_code: code })));
      if (ins.error) { // ayni anda ikinci istek: ilk uretileni ver, fazlaliklari iptal et
        await sb.from('club_cards').update({ status: 'void' }).in('code', codes);
        const again = await sb.from('club_card_orders').select('card_code').eq('order_id', o.id).order('idx');
        codes = (again.data || []).map((r) => r.card_code);
      } else {
        const nm = (o.customer && o.customer.firstName) || '';
        await sendMail(email, 'Retro Club kartın hazır', cardMail(nm, null, codes));
        await tgSend('<b>Retro Club - kart satışı</b>\nSipariş: ' + esc(o.name) + '\n' + esc(email) + '\nKart: <code>' + codes.join(', ') + '</code>');
      }
    }
    return send(res, 200, { ok: true, codes });
  }

  // ================= PANEL =================
  if (a.startsWith('admin')) {
    if (!isAdmin(req)) return send(res, 401, { ok: false, error: 'Yetkisiz' });
    if (a === 'admin' && req.method === 'GET') {
      const [apps, members, cards, evs, st, att, awards] = await Promise.all([
        sb.from('club_applications').select('*').order('created_at', { ascending: false }).limit(200),
        sb.from('club_members').select('*').order('joined_at', { ascending: false }).limit(2000),
        sb.from('club_cards').select('*').order('created_at', { ascending: false }).limit(3000),
        eventsWithPeople(sb, null, true), settings(sb), attendance(sb), awardsByMember(sb),
      ]);
      if (apps.error) throw apps.error;
      const appList = apps.data || [];
      await Promise.all(appList.filter((x) => x.selfie_path).slice(0, 60).map(async (x) => {
        const sg = await sb.storage.from(PRIV).createSignedUrl(x.selfie_path, 3600);
        x.selfie_url = (sg.data && sg.data.signedUrl) || '';
      }));
      const ms = (members.data || []).map((m) => Object.assign({}, m, { badges: badgesOf(m, att[m.id], awards[m.id]), awards: awards[m.id] || [], attended: (att[m.id] || { total: 0 }).total }));
      const nos = ms.map((m) => m.member_no).concat((cards.data || []).map((c) => c.member_no || 0));
      return send(res, 200, { ok: true, applications: appList, members: ms, cards: cards.data || [], events: evs, settings: st, kinds: KINDS,
        badges: BADGES, levels: LEVELS, next_no: Math.max(100, ...nos) + 1 });
    }
    if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'Method' });
    const b = await readJson(req);
    if (a === 'admin.application') {
      const { data: app } = await sb.from('club_applications').select('*').eq('id', s(b.id, 40)).maybeSingle();
      if (!app) return send(res, 404, { ok: false, error: 'Başvuru bulunamadı' });
      if (app.status !== 'pending') return send(res, 409, { ok: false, error: 'Bu başvuru zaten sonuçlandı' });
      const now = new Date().toISOString();
      if (b.decision === 'approve') { // kart uretilir; kart maili panelden uye numarasi yazilarak ayrica gonderilir
        const code = makeCode();
        const c = await sb.from('club_cards').insert({ code, batch: 'basvuru', note: app.email, email: app.email });
        if (c.error) throw c.error;
        await sb.from('club_applications').update({ status: 'approved', card_code: code, reviewed_at: now, review_note: s(b.note, 300) }).eq('id', app.id);
        return send(res, 200, { ok: true, code });
      }
      if (b.decision === 'reject') {
        if (app.selfie_path) await sb.storage.from(PRIV).remove([app.selfie_path]);
        await sb.from('club_applications').update({ status: 'rejected', reviewed_at: now, review_note: s(b.note, 300), selfie_path: '' }).eq('id', app.id);
        const mailed = await sendMail(app.email, 'Retro Club başvurun hakkında', mailWrap(
          mailH1('Merhaba ' + esc(app.name) + ',') + mailP('Başvurunu inceledik ancak şu an onaylayamadık. Retro dijital kameranla çektiğin net bir selfie ile yeniden başvurabilirsin.'), 'Başvurun hakkında'));
        return send(res, 200, { ok: true, mailed });
      }
      return send(res, 400, { ok: false, error: 'Karar eksik' });
    }
    // Kart maili: secilen karta uye numarasi atanir ve kart gorunumlu e-posta gonderilir.
    // Kaynak: code (var olan kart) ya da yalnizca email (yeni kart uretilir).
    if (a === 'admin.cardmail') {
      const no = Math.floor(Number(b.member_no));
      if (!(no >= 1 && no <= 999999)) return send(res, 400, { ok: false, error: 'Üye numarasını yaz.' });
      let code = normCode(b.code), email = s(b.email, 120).toLowerCase(), name = s(b.name, 60);
      let card = null, member = null;
      if (code) {
        card = (await sb.from('club_cards').select('*').eq('code', code).maybeSingle()).data;
        if (!card || card.status === 'void') return send(res, 404, { ok: false, error: 'Kart bulunamadı' });
        member = (await sb.from('club_members').select('*').eq('card_code', code).maybeSingle()).data;
        if (!email) email = (member && member.email) || card.email || '';
        if (!name) name = (member && member.name) || '';
        if (!name && card.batch === 'basvuru') {
          const ap = (await sb.from('club_applications').select('name').eq('card_code', code).maybeSingle()).data;
          name = (ap && ap.name) || '';
        }
      }
      if (!EMAIL_RE.test(email)) return send(res, 400, { ok: false, error: 'Geçerli bir e-posta adresi gerekli.' });
      const [tm, tc] = await Promise.all([
        sb.from('club_members').select('id, card_code').eq('member_no', no).limit(1),
        sb.from('club_cards').select('code').eq('member_no', no).limit(1),
      ]);
      if ((tm.data || []).some((m) => m.card_code !== code) || (tc.data || []).some((c) => c.code !== code))
        return send(res, 409, { ok: false, error: 'Bu üye numarası başka birinde. Farklı bir numara yaz.' });
      const now = new Date().toISOString();
      if (!code) {
        code = makeCode();
        const c = await sb.from('club_cards').insert({ code, batch: 'panel', note: name || email, email, member_no: no, mailed_at: now });
        if (c.error) throw c.error;
      } else {
        const u = await sb.from('club_cards').update({ member_no: no, email, mailed_at: now }).eq('code', code);
        if (u.error) throw u.error;
        if (member && member.member_no !== no) {
          const um = await sb.from('club_members').update({ member_no: no }).eq('id', member.id);
          if (um.error) throw um.error;
        }
      }
      const mailed = await sendMail(email, 'Retro Club kartın hazır', cardMail(name, no, code));
      return send(res, 200, { ok: true, code, mailed });
    }
    if (a === 'admin.badge') {
      const bd = BADGE_BY_ID[s(b.badge, 30)], mid = s(b.member_id, 40);
      if (b.revoke) {
        const d = await sb.from('club_member_badges').delete().eq('id', s(b.id, 40));
        if (d.error) throw d.error;
        return send(res, 200, { ok: true });
      }
      if (!bd || !mid) return send(res, 400, { ok: false, error: 'Üye ve rozet seç.' });
      const city = bd.city ? s(b.city, 60) : '';
      if (bd.city && !city) return send(res, 400, { ok: false, error: 'Bu rozet için şehir yaz.' });
      const ins = await sb.from('club_member_badges').upsert({ member_id: mid, badge: bd.id, city, note: s(b.note, 200) }, { onConflict: 'member_id,badge,city', ignoreDuplicates: true });
      if (ins.error) throw ins.error;
      return send(res, 200, { ok: true });
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
    if (a === 'admin.settings') {
      const v = {
        welcome_title: s(b.welcome_title, 80), welcome_text: s(b.welcome_text, 300), announcement: s(b.announcement, 300),
        show_events: !!b.show_events, show_soon: !!b.show_soon, show_members: !!b.show_members,
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
    const [evs, soon, members, att, awards] = await Promise.all([
      st.show_events ? eventsWithPeople(sb, me, false) : [],
      st.show_soon ? soonCameras() : [],
      sb.from('club_members').select(MEMBER_PUBLIC).eq('status', 'active').not('username', 'is', null).order('joined_at', { ascending: false }).limit(2000),
      attendance(sb), awardsByMember(sb),
    ]);
    const ms = (members.data || []).map((m) => { const bs = badgesOf(m, att[m.id], awards[m.id]); return Object.assign({}, m, { badges: bs, level: levelOf(bs).index }); });
    const myBadges = badgesOf(me, att[me.id], awards[me.id]);
    sb.from('club_members').update({ last_seen_at: new Date().toISOString() }).eq('id', me.id).then(() => {});
    return send(res, 200, { ok: true, me: Object.assign(meView(me), { badges: myBadges, level: levelOf(myBadges), progress: progressOf(me, att[me.id]), attended: (att[me.id] || { total: 0 }).total }),
      settings: st, events: evs, soon, members: st.show_members ? ms : [], member_count: ms.length,
      catalog: { badges: BADGES, levels: LEVELS, accents: ACCENTS, skins: SKINS, tags: TAGS, kinds: KIND_TR } });
  }
  // Canli sayac: uye sayisi + son katilanlar (uyeler sekmesi bunu araliklarla sorar).
  if (a === 'pulse' && req.method === 'GET') {
    const { data } = await sb.from('club_members').select('id, username, city, avatar_url, joined_at').eq('status', 'active').not('username', 'is', null).order('joined_at', { ascending: false }).limit(10);
    return send(res, 200, { ok: true, member_count: await memberCount(sb), recent: data || [] });
  }
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'Method' });
  const b = await readJson(req);

  if (a === 'profile') {
    const username = s(b.username, 20).toLowerCase();
    if (!USER_RE.test(username)) return send(res, 400, { ok: false, error: 'Kullanıcı adı 3-20 karakter olmalı; küçük harf, rakam, nokta ve alt çizgi kullanabilirsin.' });
    const taken = await sb.from('club_members').select('id').eq('username', username).neq('id', me.id).limit(1);
    if (taken.data && taken.data.length) return send(res, 409, { ok: false, error: 'Bu kullanıcı adı alınmış.' });
    const city = s(b.city, 60), camera = s(b.camera_model, 80);
    if (!me.username && (!city || !camera)) return send(res, 400, { ok: false, error: 'Şehrini ve kullandığın kamerayı seç.' });
    const row = { username, name: s(b.name, 60), country: s(b.country, 2).toUpperCase() || 'TR', city, instagram: cleanInsta(b.instagram), bio: s(b.bio, 200),
      camera_model: camera, profile: cleanProfile(b.profile, me.profile) };
    if (b.email != null && (b.email === '' || EMAIL_RE.test(s(b.email, 120)))) row.email = s(b.email, 120).toLowerCase();
    if (b.avatar && String(b.avatar).startsWith('data:')) row.avatar_url = await saveImage(sb, PUB, 'avatar', b.avatar);
    if (b.cover && String(b.cover).startsWith('data:')) row.cover_url = await saveImage(sb, PUB, 'cover', b.cover);
    else if (b.cover === '') row.cover_url = '';
    // kamera gorseli: uyenin yukledigi foto ya da magazadaki urun gorseli
    if (b.camera_image && String(b.camera_image).startsWith('data:')) row.camera_image_url = await saveImage(sb, PUB, 'camera', b.camera_image);
    else if (b.camera_image_url != null) row.camera_image_url = shopImg(b.camera_image_url) || (String(b.camera_image_url) === me.camera_image_url ? me.camera_image_url : '');
    const u = await sb.from('club_members').update(row).eq('id', me.id).select('*').single();
    if (u.error) throw u.error;
    return send(res, 200, { ok: true, me: meView(u.data) });
  }
  if (!me.username) return send(res, 409, { ok: false, error: 'Önce kullanıcı adını seç.' });

  if (a === 'intro') {
    await sb.from('club_members').update({ intro_seen: true }).eq('id', me.id);
    return send(res, 200, { ok: true });
  }
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
  // Seviyesi yeten uye etkinlik onerir; taslak olarak panele duser, ekip yayinlar.
  if (a === 'propose') {
    const [att, awards] = await Promise.all([attendance(sb), awardsByMember(sb)]);
    if (!levelOf(badgesOf(me, att[me.id], awards[me.id])).propose) return send(res, 403, { ok: false, error: 'Etkinlik oluşturmak için Etkinlik Kurucusu seviyesine ulaşmalısın.' });
    const title = s(b.title, 120), starts = new Date(b.starts_at);
    if (!title || isNaN(starts.getTime()) || starts.getTime() < Date.now()) return send(res, 400, { ok: false, error: 'Başlık ve ileri bir tarih gerekli.' });
    const open = await sb.from('club_events').select('id').eq('proposed_by', me.id).eq('status', 'draft').limit(3);
    if ((open.data || []).length >= 3) return send(res, 409, { ok: false, error: 'Onay bekleyen üç önerin var. Önce onların sonuçlanmasını bekle.' });
    const row = { kind: KINDS.indexOf(b.kind) >= 0 ? b.kind : 'bulusma', title, description: s(b.description, 2000), starts_at: starts.toISOString(),
      place: s(b.place, 160), city: s(b.city, 60) || me.city, capacity: Math.max(0, Math.min(500, Number(b.capacity) || 0)), status: 'draft', proposed_by: me.id };
    if (b.cover && String(b.cover).startsWith('data:')) row.cover_url = await saveImage(sb, PUB, 'event', b.cover);
    const ins = await sb.from('club_events').insert(row);
    if (ins.error) throw ins.error;
    await tgSend('<b>Retro Club - etkinlik önerisi</b>\n@' + esc(me.username) + ': ' + esc(title) + '\n' + esc(row.city) + '\n\n<i>Panelde Etkinlikler sekmesinden yayınla.</i>');
    return send(res, 200, { ok: true });
  }
  if (a === 'logout') {
    const h = String(req.headers.authorization || '');
    await sb.from('club_sessions').delete().eq('token', h.slice(7).trim());
    return send(res, 200, { ok: true });
  }
  return send(res, 404, { ok: false, error: 'Bilinmeyen islem' });
}
