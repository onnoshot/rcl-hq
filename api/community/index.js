// RetroCameraLand Topluluk - TEK dispatcher fonksiyon (Vercel Hobby 12-fonksiyon limiti icin).
// Tum community mantigi /lib/community/*.js icinde (fonksiyon sayilmaz). vercel.json rewrite'lari
// /apps/hesabim/community/* isteklerini buraya action parametresiyle yonlendirir.
import * as award from '../../lib/community/award.js';
import * as discourseSso from '../../lib/community/discourse-sso.js';
import * as feed from '../../lib/community/feed.js';
import * as leaderboard from '../../lib/community/leaderboard.js';
import * as moderate from '../../lib/community/moderate.js';
import * as page from '../../lib/community/page.js';
import * as profile from '../../lib/community/profile.js';
import * as session from '../../lib/community/session.js';
import * as sitemap from '../../lib/community/sitemap.js';
import * as upload from '../../lib/community/upload.js';
import * as vote from '../../lib/community/vote.js';

const ROUTES = {
  session: session.run,
  feed: feed.run,
  vote: vote.run,
  upload: upload.run,
  profile: profile.run,
  leaderboard: leaderboard.run,
  sitemap: sitemap.run,
  'discourse-sso': discourseSso.run,
  page: page.run,
  moderate: moderate.run,
  award: award.run,
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
