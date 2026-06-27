// FAZ 2: GET /api/community/award?range=week|month
// Haftalik/aylik kazanani bulur ve ONCEDEN HAZIRLANMIS sabit indirim kodunu kazanana paylasir.
// Cek BASILMAZ (giftCardCreate yok). Kodlar Shopify'da senin elinle hazirlanir:
//   haftalik -> PRIZE_CODE_WEEK  (varsayilan OZELWIN1000, 1000 TL)
//   aylik    -> PRIZE_CODE_MONTH (varsayilan WIN5000,     5000 TL)
// Kazanana Brevo e-postasi + sana Telegram bildirimi gider; kazanan rozeti verilir.
// Cron (LaunchAgent) calistirir. Idempotent: ayni kazanana ayni donemde kod 2 kez gonderilmez.
import { adminClient, sendBrevoEmail, notifyTelegram, fetchShopifyCustomer, cors } from './core.js';

const SITE = 'https://retrocameraland.com';

function winnerEmailHtml(name, code, amount, period) {
  return '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;margin:auto;background:#0d0d10;color:#f3f3f4;border-radius:18px;padding:28px;border:1px solid rgba(255,255,255,.1)">'
    + '<h2 style="margin:0 0 6px;font-size:22px">Tebrikler ' + esc(name) + '!</h2>'
    + '<p style="color:#9b9ba2;font-size:15px;line-height:1.5">RetroCameraLand toplulugunda <b>' + period + '</b> en cok begeni alan fotograf seninki oldu. Odulun:</p>'
    + '<div style="text-align:center;margin:18px 0;background:#FF4D2E;color:#fff;border-radius:14px;padding:18px">'
    + '<div style="font-size:13px;opacity:.85">' + amount + ' indirim kodun</div>'
    + '<div style="font-size:30px;font-weight:800;letter-spacing:.06em;margin-top:4px">' + esc(code) + '</div></div>'
    + '<p style="color:#9b9ba2;font-size:13px">Kodu <a href="' + SITE + '" style="color:#FF4D2E">retrocameraland.com</a> sepetinde kullanabilirsin. Yeni karelerini paylasmaya devam et!</p></div>';
}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])})}

export async function run(req, res) {
  cors(res);
  const range = req.query?.range === 'month' ? 'month' : 'week';
  const code = range === 'month'
    ? (process.env.PRIZE_CODE_MONTH || 'WIN5000')
    : (process.env.PRIZE_CODE_WEEK || 'OZELWIN1000');
  const amount = range === 'month' ? '5000 TL' : '1000 TL';
  const period = range === 'month' ? 'bu ay' : 'bu hafta';
  const view = range === 'month' ? 'leaderboard_month' : 'leaderboard_week';
  const badge = range === 'month' ? 'month_winner' : 'week_winner';
  const db = adminClient();

  const { data: top } = await db.from(view).select('*').limit(1).maybeSingle();
  if (!top) return res.status(200).json({ ok: true, winner: null });

  // idempotent: bu donemde zaten kod gonderildiyse tekrar gonderme
  const periodKey = badge + ':' + top.customer_id + ':' + new Date().toISOString().slice(0, range === 'month' ? 7 : 10);
  const { data: already } = await db.from('user_badges')
    .select('customer_id').eq('customer_id', top.customer_id).eq('badge_key', badge)
    .gte('awarded_at', range === 'month' ? new Date(Date.now() - 31 * 864e5).toISOString() : new Date(Date.now() - 6 * 864e5).toISOString())
    .maybeSingle();

  // dry: sadece aday + kod onizleme (cron olmadan elle test)
  if (req.query?.dry) {
    return res.status(200).json({ ok: true, dry: true, winner: top, code, alreadySent: !!already });
  }
  if (already) {
    return res.status(200).json({ ok: true, winner: top, code, alreadySent: true });
  }

  // kazananin e-postasi
  const cust = await fetchShopifyCustomer(top.customer_id);
  const email = cust?.email || null;
  const name = top.display_name || (cust ? cust.first_name : 'Uye') || 'Uye';

  let mailed = false;
  if (email) mailed = await sendBrevoEmail(email, 'RetroCameraLand: ' + amount + ' odulun seni bekliyor', winnerEmailHtml(name, code, amount, period));

  await db.from('user_badges').upsert(
    [{ customer_id: top.customer_id, badge_key: badge }],
    { onConflict: 'customer_id,badge_key', ignoreDuplicates: true });

  await notifyTelegram(
    '<b>RCL ' + (range === 'month' ? 'AYIN' : 'HAFTANIN') + ' KAZANANI</b>\n' +
    name + ' (@' + (top.handle || '') + ')\n' + top.camera_model + ' @ ' + top.location +
    '\nBegeni: ' + top.like_count + '\nKod: <b>' + code + '</b> (' + amount + ')\n' +
    'E-posta: ' + (email || 'YOK') + (mailed ? ' (gonderildi)' : ' (mail GIDEMEDI - elle ilet)'));

  return res.status(200).json({ ok: true, winner: top, code, amount, mailed });
}
