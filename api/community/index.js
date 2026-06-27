// RetroCameraLand Topluluk v2 - TEK dispatcher fonksiyon (Vercel Hobby 12-fonksiyon limiti).
// Tum mantik /lib/community/*.js icinde. vercel.json rewrite'lari
// /apps/hesabim/community/<action> -> /api/community/index?action=<action> yonlendirir.
import * as session from '../../lib/community/session.js';
import * as cameras from '../../lib/community/cameras.js';
import * as photos from '../../lib/community/photos.js';
import * as profile from '../../lib/community/profile.js';
import * as feedback from '../../lib/community/feedback.js';

const ROUTES = {
  session: session.run,
  cameras: cameras.list,         // puana gore sirali kameralar (+marka filtresi)
  brands: cameras.brands,        // marka kategorileri
  camera: cameras.detail,        // kamera detayi + foto karti
  'camera-vote': cameras.vote,   // kameraya begeni
  'camera-waitlist': cameras.waitlist, // bekleme listesi
  'camera-photo': photos.upload, // kameranin kartina foto yukle
  feed: photos.feed,             // global foto akisi
  'photo-like': photos.like,     // foto begen
  comments: photos.comments,     // foto yorumlari (GET/POST)
  profile: profile.get,          // kullanici profili
  'my-camera': profile.addCamera,// profile kamera ekle/cikar
  feedback: feedback.submit,     // Time Capsule geri bildirim
  stats: feedback.stats,         // dashboard istatistik (RCL_ALIM_KEY)
};

export default async function handler(req, res) {
  const action = String((req.query && req.query.action) || '').replace(/\/+$/, '');
  const fn = ROUTES[action];
  if (!fn) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.status(404).json({ ok: false, error: 'bilinmeyen islem: ' + action });
    return;
  }
  return fn(req, res);
}
