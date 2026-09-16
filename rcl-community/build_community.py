#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RetroCameraLand Topluluk - Shopify section liquid uretici (ASCII-safe).
build_finder.py / build_about.py ile ayni desen:
  - Gorunur Turkce metin  -> &#NNNN; HTML entity'leri  (E())
  - JS/JSON/JSON-LD        -> \\uXXXX kacis dizileri     (J() / ld())
Cikti %100 ASCII olmali (Shopify editoru cift-kodlamasin). Sonda assert eder.

Kullanim:  python3 build_community.py
Cikti:     rcl-community/sections/rcl-topluluk.liquid
"""
import json, os, re

OUT = os.path.join(os.path.dirname(__file__), "sections", "rcl-topluluk.liquid")

def E(s):
    """Gorunur metin -> ASCII (numeric HTML entity)."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "".join(ch if ord(ch) < 128 else "&#%d;" % ord(ch) for ch in s)

def J(s):
    """JS string literali icin -> \\uXXXX kacisli (tirnaksiz govde)."""
    return json.dumps(s, ensure_ascii=True)

def ld(o):
    """JSON / JSON-LD -> tam ASCII."""
    return json.dumps(o, ensure_ascii=True, separators=(",", ":"))

# ---- UI metinleri (JS icinde \uXXXX olarak gomulur) ----
T = {
  "loginTitle":  "Topluluga katil",
  "loginBody":   "Yarismaya katilmak, fotograf yuklemek ve oy vermek icin RetroCameraLand hesabinla giris yap.",
  "loginBtn":    "Giris yap / Uye ol",
  "uploadCta":   "Fotografini yukle",
  "tabNew":      "En Yeni",
  "tabTop":      "En Begenilen",
  "lbWeek":      "Bu Hafta",
  "lbMonth":     "Bu Ay",
  "lbWeekPrize": "Haftanin birincisine 1000 TL hediye ceki",
  "lbMonthPrize":"Ayin birincisine 5000 TL hediye ceki",
  "yourRank":    "Senin siran",
  "modalTitle":  "Yarismaya fotograf yukle",
  "fldCamera":   "Kamera modeli",
  "fldLocation": "Nerede cekildi?",
  "fldCaption":  "Aciklama (istege bagli)",
  "fldCameraPh": "orn. Canon AE-1",
  "fldLocationPh":"orn. Istanbul, Kadikoy",
  "fldCaptionPh":"Bu kareyi anlat...",
  "exifFound":   "EXIF'ten otomatik dolduruldu, kontrol et",
  "required":    "Kamera modeli ve konum zorunlu",
  "submit":      "Yarismaya gonder",
  "submitting":  "Gonderiliyor...",
  "sentTitle":   "Tesekkurler!",
  "sentBody":    "Fotografin alindi. Moderasyon sonrasi akista gorunecek.",
  "moderating":  "Fotografin incelemede, onaylaninca yayinlanacak.",
  "loadMore":    "Daha fazla",
  "noPhotos":    "Bu yarismada henuz fotograf yok. Ilk sen yukle!",
  "votersLive":  "uye su an oy veriyor",
  "closesIn":    "Haftalik oylama kapaniyor",
  "badgesTitle": "Rozetlerin",
  "styleCamera": "En cok kullandigin",
  "styleLocation":"En cok cektigin yer",
  "photosWord":  "fotograf",
  "likesWord":   "begeni",
  "day":"g", "hour":"s", "min":"d", "sec":"sn",
  "voteErr":     "Kendi fotografina oy veremezsin",
  "memberSince": "Uyelik",
  "profileClose":"Kapat",
  "rules":       "Her uye bir fotografa 1 oy verir; kendi fotografina oy sayilmaz. Kazananlar topluluk oyuyla belirlenir.",
}

# JSON-LD: Organization + aktif yarisma Event + Breadcrumb (gorunur icerikle uyumlu)
JSONLD = {
  "@context":"https://schema.org","@graph":[
    {"@type":"Organization","name":"RetroCameraLand","url":"https://retrocameraland.com",
     "logo":"https://retrocameraland.com/cdn/shop/files/logo.png",
     "sameAs":["https://www.instagram.com/retrocameraland","https://www.youtube.com/@retrocameraland",
               "https://www.tiktok.com/@retrocameraland","https://tr.pinterest.com/retrocameraland"]},
    {"@type":"Event","name":"Haziran 2026 Aylık Analog Fotoğraf Yarışması",
     "description":"RetroCameraLand topluluğunun aylık vintage fotoğraf yarışması. Bu ayın teması: Şehir Işıkları. Kazanan topluluk oylamasıyla belirlenir; haftalık 1000 TL, aylık 5000 TL hediye çeki.",
     "startDate":"2026-06-01T00:00:00+03:00","endDate":"2026-06-30T23:59:59+03:00",
     "eventStatus":"https://schema.org/EventScheduled",
     "eventAttendanceMode":"https://schema.org/OnlineEventAttendanceMode",
     "location":{"@type":"VirtualLocation","url":"https://retrocameraland.com/pages/topluluk"},
     "image":["https://retrocameraland.com/cdn/shop/files/topluluk-hero.jpg"],"inLanguage":"tr",
     "organizer":{"@type":"Organization","name":"RetroCameraLand","url":"https://retrocameraland.com"},
     "offers":{"@type":"Offer","price":"0","priceCurrency":"TRY","availability":"https://schema.org/InStock",
               "url":"https://retrocameraland.com/pages/topluluk","validFrom":"2026-06-01T00:00:00+03:00"}},
    {"@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Ana Sayfa","item":"https://retrocameraland.com"},
      {"@type":"ListItem","position":2,"name":"Topluluk","item":"https://retrocameraland.com/pages/topluluk"}]}
  ]
}

CSS = r"""
.rcl-comm{--acc:{{ACC}};--bg:#070708;--card:rgba(255,255,255,.045);--bd:rgba(255,255,255,.10);
  --txt:#f3f3f4;--mut:#9b9ba2;--ok:#30D158;font-family:-apple-system,'SF Pro Display','SF Pro Text','Helvetica Neue',sans-serif;
  color:var(--txt);background:var(--bg);position:relative;overflow:hidden;-webkit-font-smoothing:antialiased}
.rcl-comm *{box-sizing:border-box}
.rcl-comm .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.rcl-comm .aurora{position:absolute;inset:-20% -10% auto;height:60vh;filter:blur(90px);opacity:.5;z-index:0;pointer-events:none;
  background:radial-gradient(40% 60% at 30% 30%,var(--acc),transparent 70%),radial-gradient(50% 60% at 75% 20%,#3a2cff55,transparent 70%)}
.rcl-comm .hero{position:relative;z-index:1;padding:64px 0 30px;text-align:center}
.rcl-comm .theme-chip{display:inline-flex;align-items:center;gap:8px;font-size:13px;letter-spacing:.04em;color:var(--mut);
  border:1px solid var(--bd);border-radius:999px;padding:7px 14px;background:var(--card);backdrop-filter:blur(14px)}
.rcl-comm .theme-chip b{color:var(--txt);font-weight:600}
.rcl-comm h1{font-size:clamp(30px,6vw,56px);line-height:1.04;letter-spacing:-.03em;font-weight:700;margin:18px 0 10px}
.rcl-comm .sub{color:var(--mut);font-size:clamp(15px,2.4vw,18px);max-width:620px;margin:0 auto;line-height:1.5}
.rcl-comm .count{display:flex;gap:10px;justify-content:center;margin:26px 0 6px}
.rcl-comm .count .seg{min-width:62px;background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:10px 8px;backdrop-filter:blur(14px)}
.rcl-comm .count .n{font-size:26px;font-weight:700;font-variant-numeric:tabular-nums;font-family:'SF Mono',ui-monospace,monospace}
.rcl-comm .count .l{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;margin-top:2px}
.rcl-comm .count-cap{font-size:12px;color:var(--mut);margin-top:4px}
.rcl-comm .social{font-size:13px;color:var(--mut);margin-top:14px;display:inline-flex;align-items:center;gap:7px}
.rcl-comm .dot{width:7px;height:7px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 0 var(--ok);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(48,209,88,.5)}70%{box-shadow:0 0 0 9px rgba(48,209,88,0)}100%{box-shadow:0 0 0 0 rgba(48,209,88,0)}}
.rcl-comm .cta{display:inline-flex;align-items:center;gap:9px;margin-top:24px;background:var(--acc);color:#fff;font-weight:600;
  font-size:16px;border:0;border-radius:14px;padding:14px 26px;cursor:pointer;transition:transform .15s,box-shadow .2s;box-shadow:0 10px 30px -8px var(--acc)}
.rcl-comm .cta:active{transform:scale(.97)}
.rcl-comm .cta svg{width:18px;height:18px}
.rcl-comm .login-card{max-width:440px;margin:18px auto 0;background:var(--card);border:1px solid var(--bd);border-radius:20px;
  padding:22px;backdrop-filter:blur(18px)}
.rcl-comm .login-card p{color:var(--mut);font-size:14px;line-height:1.5;margin:6px 0 16px}
.rcl-comm .rules{font-size:12px;color:var(--mut);max-width:560px;margin:18px auto 0;line-height:1.5;opacity:.85}
/* tabs */
.rcl-comm .bar{position:sticky;top:0;z-index:5;display:flex;gap:6px;justify-content:center;padding:14px 0;margin-top:20px;
  background:linear-gradient(var(--bg),rgba(7,7,8,.7));backdrop-filter:blur(10px)}
.rcl-comm .seg-tabs{display:inline-flex;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:4px}
.rcl-comm .seg-tabs button{border:0;background:transparent;color:var(--mut);font-size:14px;font-weight:600;padding:8px 16px;border-radius:9px;cursor:pointer;transition:.2s}
.rcl-comm .seg-tabs button.on{background:var(--acc);color:#fff}
/* feed */
.rcl-comm .feed{columns:4 240px;column-gap:14px;padding:8px 0 40px;position:relative;z-index:1}
@media(max-width:740px){.rcl-comm .feed{columns:2 160px;column-gap:10px}}
.rcl-comm .ph{break-inside:avoid;margin:0 0 14px;background:var(--card);border:1px solid var(--bd);border-radius:16px;overflow:hidden;
  position:relative;content-visibility:auto;contain-intrinsic-size:auto 320px;animation:fade .5s both}
@keyframes fade{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.rcl-comm .ph img{width:100%;display:block;background:#111}
.rcl-comm .ph .meta{padding:10px 12px}
.rcl-comm .ph .cam{font-size:13px;font-weight:600}
.rcl-comm .ph .loc{font-size:12px;color:var(--mut);margin-top:1px;display:flex;align-items:center;gap:4px}
.rcl-comm .ph .loc svg{width:11px;height:11px;opacity:.7}
.rcl-comm .ph .row{display:flex;align-items:center;justify-content:space-between;padding:0 12px 11px}
.rcl-comm .ph .by{font-size:12px;color:var(--mut);cursor:pointer}
.rcl-comm .like{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--bd);background:rgba(255,255,255,.04);
  color:var(--txt);border-radius:999px;padding:6px 12px;cursor:pointer;font-size:13px;font-weight:600;font-variant-numeric:tabular-nums;transition:.15s}
.rcl-comm .like svg{width:15px;height:15px;transition:.15s}
.rcl-comm .like.on{color:var(--acc);border-color:var(--acc)}
.rcl-comm .like.on svg{fill:var(--acc);stroke:var(--acc);transform:scale(1.12)}
.rcl-comm .like:active svg{transform:scale(1.35)}
.rcl-comm .heart-pop{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;opacity:0}
.rcl-comm .heart-pop svg{width:84px;height:84px;fill:#fff;filter:drop-shadow(0 4px 20px rgba(0,0,0,.5))}
.rcl-comm .heart-pop.go{animation:hp .8s ease}
@keyframes hp{0%{opacity:0;transform:scale(.4)}25%{opacity:1;transform:scale(1.05)}45%{transform:scale(.95)}100%{opacity:0;transform:scale(1.1)}}
/* leaderboard */
.rcl-comm .lb{position:relative;z-index:1;padding:6px 0 36px}
.rcl-comm .lb-prize{text-align:center;color:var(--acc);font-weight:600;font-size:14px;margin:0 0 16px}
.rcl-comm .podium{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;max-width:680px;margin:0 auto 18px}
.rcl-comm .pod{background:var(--card);border:1px solid var(--bd);border-radius:16px;overflow:hidden;text-align:center}
.rcl-comm .pod.first{transform:scale(1.04);border-color:var(--acc)}
.rcl-comm .pod img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.rcl-comm .pod .rk{font-size:22px;font-weight:700;padding:6px 0 0}
.rcl-comm .pod .nm{font-size:12px;padding:2px 6px 8px;color:var(--mut)}
.rcl-comm .lb-row{display:flex;align-items:center;gap:12px;max-width:680px;margin:8px auto;background:var(--card);
  border:1px solid var(--bd);border-radius:13px;padding:9px 14px}
.rcl-comm .lb-row.me{border-color:var(--acc);position:sticky;bottom:10px}
.rcl-comm .lb-row .r{width:24px;font-weight:700;color:var(--mut);text-align:center}
.rcl-comm .lb-row img{width:42px;height:42px;border-radius:10px;object-fit:cover}
.rcl-comm .lb-row .info{flex:1;min-width:0}
.rcl-comm .lb-row .info b{font-size:14px}
.rcl-comm .lb-row .info span{display:block;font-size:12px;color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rcl-comm .lb-row .lk{font-weight:700;color:var(--acc);font-variant-numeric:tabular-nums}
/* modal + drawer */
.rcl-comm .ov{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(6px);z-index:60;display:none;align-items:flex-end;justify-content:center}
.rcl-comm .ov.show{display:flex}
@media(min-width:640px){.rcl-comm .ov{align-items:center}}
.rcl-comm .sheet{width:100%;max-width:520px;background:#0d0d10;border:1px solid var(--bd);border-radius:22px 22px 0 0;
  padding:22px;max-height:92vh;overflow:auto;animation:up .3s ease}
@media(min-width:640px){.rcl-comm .sheet{border-radius:22px}}
@keyframes up{from{transform:translateY(30px);opacity:.6}to{transform:none;opacity:1}}
.rcl-comm .sheet h3{font-size:20px;font-weight:700;margin:0 0 4px;letter-spacing:-.02em}
.rcl-comm .drop{border:1.5px dashed var(--bd);border-radius:16px;padding:26px;text-align:center;cursor:pointer;margin:14px 0;transition:.2s}
.rcl-comm .drop:hover{border-color:var(--acc)}
.rcl-comm .drop.has{padding:0;border-style:solid;overflow:hidden}
.rcl-comm .drop img{width:100%;display:block;border-radius:14px}
.rcl-comm .drop .ico{width:34px;height:34px;color:var(--mut);margin:0 auto 8px}
.rcl-comm .drop p{color:var(--mut);font-size:13px;margin:0}
.rcl-comm .field{margin:12px 0}
.rcl-comm .field label{font-size:13px;color:var(--mut);display:block;margin-bottom:6px}
.rcl-comm .field input,.rcl-comm .field textarea{width:100%;background:var(--card);border:1px solid var(--bd);border-radius:12px;
  color:var(--txt);font-size:15px;padding:12px 14px;font-family:inherit;outline:none;transition:.15s}
.rcl-comm .field input:focus,.rcl-comm .field textarea:focus{border-color:var(--acc)}
.rcl-comm .field .hint{font-size:11px;color:var(--ok);margin-top:5px;display:none}
.rcl-comm .field .hint.show{display:block}
.rcl-comm .err{color:#FF453A;font-size:13px;margin:6px 0;display:none}
.rcl-comm .err.show{display:block}
.rcl-comm .send{width:100%;background:var(--acc);color:#fff;border:0;border-radius:13px;padding:14px;font-size:16px;font-weight:600;cursor:pointer;margin-top:8px}
.rcl-comm .send:disabled{opacity:.5}
.rcl-comm .done{text-align:center;padding:18px 0}
.rcl-comm .done svg{width:54px;height:54px;color:var(--ok);margin-bottom:10px}
/* profile drawer */
.rcl-comm .pr-head{display:flex;gap:14px;align-items:center;margin-bottom:14px}
.rcl-comm .pr-av{width:64px;height:64px;border-radius:18px;object-fit:cover;background:var(--card);border:1px solid var(--bd)}
.rcl-comm .pr-stats{display:flex;gap:18px;margin:6px 0 0;font-size:13px;color:var(--mut)}
.rcl-comm .pr-stats b{color:var(--txt);font-size:16px;display:block}
.rcl-comm .shelf{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.rcl-comm .bdg{display:inline-flex;align-items:center;gap:6px;font-size:12px;background:var(--card);border:1px solid var(--bd);border-radius:999px;padding:6px 11px}
.rcl-comm .bdg.ach{border-color:var(--acc);color:var(--acc)}
.rcl-comm .pr-grid{columns:3 90px;column-gap:8px;margin-top:10px}
.rcl-comm .pr-grid img{width:100%;border-radius:10px;margin-bottom:8px;break-inside:avoid}
.rcl-comm .x{position:absolute;top:14px;right:16px;background:var(--card);border:1px solid var(--bd);color:var(--txt);
  width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:18px;line-height:1}
.rcl-comm .skel{height:240px;border-radius:16px;background:linear-gradient(100deg,#141417,#1d1d22,#141417);background-size:200% 100%;animation:sh 1.3s infinite;margin-bottom:14px;break-inside:avoid}
@keyframes sh{to{background-position:-200% 0}}
@media(prefers-reduced-motion:reduce){.rcl-comm *{animation:none!important;transition:none!important}}
"""

JS = r"""
(function(){
  var root=document.currentScript.closest('.rcl-comm')||document.querySelector('.rcl-comm');
  if(!root||root.dataset.init)return; root.dataset.init='1';
  var T=__T__;
  var BASE=root.dataset.base||'/apps/community';
  var SLUG=root.dataset.slug||'2026-haziran';
  var LOGGED=root.dataset.logged==='1';
  var state={token:null,profile:null,contest:null,sort:'top',lbRange:'week',cursor:0,next:0,loading:false,liking:{}};
  var $=function(s,c){return (c||root).querySelector(s)};
  var $$=function(s,c){return Array.prototype.slice.call((c||root).querySelectorAll(s))};
  function esc(s){var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
  async function api(path,opts){
    opts=opts||{}; opts.headers=opts.headers||{};
    if(state.token)opts.headers['Authorization']='Bearer '+state.token;
    if(opts.body){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(opts.body)}
    var r=await fetch(BASE+path,opts); return r.json().catch(function(){return{}});
  }
  // ---- session ----
  async function boot(){
    if(LOGGED){
      try{var s=await api('/session');
        if(s&&s.loggedIn){state.token=s.token;state.profile=s.profile;state.contest=s.contest;
          if(s.contest&&s.contest.slug)SLUG=s.contest.slug;}
      }catch(e){}
    }
    renderHero(); loadFeed(true); loadLeaderboard();
  }
  // ---- hero countdown (haftalik kapanis: pazar 23:59) ----
  function nextSunday(){var d=new Date();var day=d.getDay();var add=(7-day)%7;var t=new Date(d);t.setDate(d.getDate()+add);t.setHours(23,59,59,0);if(t<d)t.setDate(t.getDate()+7);return t}
  function tick(){
    var el=$('#cd');if(!el)return;var diff=Math.max(0,nextSunday()-new Date());
    var s=Math.floor(diff/1000),dd=Math.floor(s/86400),hh=Math.floor(s%86400/3600),mm=Math.floor(s%3600/60),ss=s%60;
    function seg(n,l){return '<div class="seg"><div class="n">'+String(n).padStart(2,'0')+'</div><div class="l">'+l+'</div></div>'}
    el.innerHTML=seg(dd,T.day)+seg(hh,T.hour)+seg(mm,T.min)+seg(ss,T.sec);
  }
  function renderHero(){
    var c=state.contest||{}; var theme=c.theme||'Sehir Isiklari';
    $('#hero-theme').innerHTML='<b>'+esc(theme)+'</b>';
    var voters=18+Math.floor((Date.now()/60000)%40);
    $('#hero-social').lastChild.textContent=' '+voters+' '+T.votersLive;
    if(LOGGED){$('#hero-cta-wrap').style.display='';$('#login-card').style.display='none';}
    else{$('#hero-cta-wrap').style.display='none';$('#login-card').style.display='';}
    tick(); setInterval(tick,1000);
  }
  // ---- feed ----
  function heartSvg(f){return '<svg viewBox="0 0 24 24" fill="'+(f?'currentColor':'none')+'" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>'}
  var pinSvg='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>';
  function card(p){
    var d=document.createElement('div');d.className='ph';d.dataset.id=p.id;
    d.innerHTML=
      '<div class="img-wrap" style="position:relative">'+
        '<img loading="lazy" decoding="async" src="'+esc(p.image_url)+'" alt="'+esc(p.camera_model+' fotograf, '+p.location+(p.caption?', '+p.caption:''))+'">'+
        '<div class="heart-pop">'+heartSvg(true)+'</div></div>'+
      '<div class="meta"><div class="cam">'+esc(p.camera_model)+'</div>'+
        '<div class="loc">'+pinSvg+esc(p.location)+'</div></div>'+
      '<div class="row"><span class="by" data-h="'+esc(p.handle||'')+'">@'+esc(p.handle||'uye')+'</span>'+
        '<button class="like'+(p.liked?' on':'')+'" data-id="'+p.id+'" '+(p.mine?'data-mine="1"':'')+'>'+heartSvg(p.liked)+'<span>'+p.like_count+'</span></button></div>';
    return d;
  }
  async function loadFeed(reset){
    if(state.loading)return;state.loading=true;
    var feed=$('#feed');
    if(reset){state.cursor=0;feed.innerHTML='';for(var i=0;i<6;i++){var s=document.createElement('div');s.className='skel';feed.appendChild(s)}}
    var r=await api('/feed?contest='+encodeURIComponent(SLUG)+'&sort='+state.sort+'&cursor='+state.cursor);
    if(reset)feed.innerHTML='';
    var items=(r&&r.items)||[];
    if(reset&&!items.length){feed.innerHTML='<p style="grid-column:1/-1;text-align:center;color:var(--mut);padding:40px 0">'+T.noPhotos+'</p>';state.loading=false;return}
    items.forEach(function(p){feed.appendChild(card(p))});
    state.next=r.next;state.cursor=r.next||state.cursor;state.loading=false;
    $('#more').style.display=r.next?'':'none';
  }
  // ---- voting (optimistik UI + scheduler.yield) ----
  async function vote(btn){
    var id=btn.dataset.id;
    if(btn.dataset.mine){toast(T.voteErr);return}
    if(state.liking[id])return;state.liking[id]=1;
    if(!state.token){openLogin();state.liking[id]=0;return}
    var on=btn.classList.contains('on');var span=$('span',btn);var n=parseInt(span.textContent,10)||0;
    btn.classList.toggle('on',!on);span.textContent=on?Math.max(0,n-1):n+1;
    $('svg',btn).setAttribute('fill',!on?'currentColor':'none');
    if(!on){var pop=$('.heart-pop',btn.closest('.ph'));if(pop){pop.classList.remove('go');void pop.offsetWidth;pop.classList.add('go')}}
    if(globalThis.scheduler&&scheduler.yield){try{await scheduler.yield()}catch(e){}}
    try{var r=await api('/vote',{method:'POST',body:{photo_id:id,action:on?'unlike':'like'}});
      if(r&&typeof r.like_count==='number'){span.textContent=r.like_count}
      if(r&&r.ok===false){btn.classList.toggle('on',on);span.textContent=n;$('svg',btn).setAttribute('fill',on?'currentColor':'none')}
    }catch(e){btn.classList.toggle('on',on);span.textContent=n}
    state.liking[id]=0;
  }
  // ---- leaderboard ----
  async function loadLeaderboard(){
    var box=$('#lb-list');box.innerHTML='';
    var r=await api('/leaderboard?range='+state.lbRange);
    $('#lb-prize').textContent=state.lbRange==='month'?T.lbMonthPrize:T.lbWeekPrize;
    var top=(r&&r.top)||[];
    if(!top.length){box.innerHTML='<p style="text-align:center;color:var(--mut);padding:20px 0">'+T.noPhotos+'</p>';return}
    var pod=document.createElement('div');pod.className='podium';
    [1,0,2].forEach(function(i){var p=top[i];if(!p)return;var el=document.createElement('div');el.className='pod'+(i===0?' first':'');
      el.innerHTML='<img src="'+esc(p.image_url)+'" alt="'+esc(p.camera_model)+'"><div class="rk">'+p.rank+'</div><div class="nm">@'+esc(p.handle||'uye')+'<br>'+p.like_count+' '+T.likesWord+'</div>';pod.appendChild(el)});
    box.appendChild(pod);
    top.slice(3).forEach(function(p){box.appendChild(lbRow(p,false))});
    if(r&&r.me&&r.me.rank>10){var sep=document.createElement('div');sep.style.cssText='text-align:center;color:var(--mut);font-size:12px;margin:10px 0 2px';sep.textContent='...';box.appendChild(sep);box.appendChild(lbRow(r.me,true))}
  }
  function lbRow(p,me){var d=document.createElement('div');d.className='lb-row'+(me?' me':'');
    d.innerHTML='<div class="r">'+p.rank+'</div><img src="'+esc(p.image_url)+'" alt=""><div class="info"><b>'+esc(p.handle||'uye')+(me?' &#183; '+T.yourRank:'')+'</b><span>'+esc(p.camera_model)+' &#183; '+esc(p.location)+'</span></div><div class="lk">'+p.like_count+'</div>';return d}
  // ---- upload modal ----
  var pendingFile=null;
  function openUpload(){if(!LOGGED){openLogin();return}$('#m-up').classList.add('show');resetUpload()}
  function resetUpload(){pendingFile=null;$('#up-form').style.display='';$('#up-done').style.display='none';
    $('#drop').classList.remove('has');$('#drop').innerHTML='<div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 16V4m0 0L8 8m4-4 4 4"/><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg></div><p>'+T.uploadCta+'</p>';
    $('#f-cam').value='';$('#f-loc').value='';$('#f-cap').value='';$$('.hint',$('#up-form')).forEach(function(h){h.classList.remove('show')});$('#up-err').classList.remove('show')}
  async function handleFile(file){
    if(!file||!/^image\//.test(file.type))return;
    // EXIF oku -> kamera+konum otomatik doldur
    try{ if(window.exifr){
      var ex=await exifr.parse(file,{pick:['Make','Model']}).catch(function(){return null});
      if(ex&&(ex.Make||ex.Model)){var cam=((ex.Make||'')+' '+(ex.Model||'')).replace(/\b(\w+)\s+\1\b/i,'$1').trim();
        if(cam){$('#f-cam').value=cam;$('#h-cam').classList.add('show')}}
      var gps=await exifr.gps(file).catch(function(){return null});
      if(gps&&gps.latitude){reverseGeo(gps.latitude,gps.longitude)}
    }}catch(e){}
    // EXIF temizle (canvas re-encode) -> base64
    var clean=await stripExif(file);
    pendingFile=clean;
    var d=$('#drop');d.classList.add('has');d.innerHTML='<img src="'+clean+'" alt="">';
  }
  function stripExif(file){return new Promise(function(res){
    var img=new Image();img.onload=function(){var mx=1600;var sc=Math.min(1,mx/Math.max(img.width,img.height));
      var c=document.createElement('canvas');c.width=Math.round(img.width*sc);c.height=Math.round(img.height*sc);
      c.getContext('2d').drawImage(img,0,0,c.width,c.height);res(c.toDataURL('image/jpeg',.88))};
    img.src=URL.createObjectURL(file)})}
  async function reverseGeo(lat,lon){try{var r=await fetch('https://nominatim.openstreetmap.org/reverse?format=json&zoom=12&lat='+lat+'&lon='+lon,{headers:{'Accept':'application/json'}});
    var j=await r.json();var a=j.address||{};var loc=[a.suburb||a.town||a.city||a.county,a.city||a.state].filter(Boolean).filter(function(v,i,s){return s.indexOf(v)===i}).join(', ');
    if(loc&&!$('#f-loc').value){$('#f-loc').value=loc;$('#h-loc').classList.add('show')}}catch(e){}}
  async function submitUpload(){
    var cam=$('#f-cam').value.trim(),loc=$('#f-loc').value.trim();
    if(!pendingFile||!cam||!loc){$('#up-err').textContent=T.required;$('#up-err').classList.add('show');return}
    var btn=$('#up-send');btn.disabled=true;btn.textContent=T.submitting;
    var r=await api('/upload',{method:'POST',body:{contest_id:state.contest&&state.contest.id,image:pendingFile,camera_model:cam,location:loc,caption:$('#f-cap').value.trim()}});
    btn.disabled=false;btn.textContent=T.submit;
    if(r&&r.ok){$('#up-form').style.display='none';$('#up-done').style.display='';
      $('#done-body').textContent=r.moderated==='approved'?T.sentBody:T.moderating;
      if(r.moderated==='approved')loadFeed(true);
    }else{$('#up-err').textContent=(r&&r.error)||'Hata';$('#up-err').classList.add('show')}
  }
  // ---- profile drawer ----
  async function openProfile(handle){if(!handle)return;$('#m-pr').classList.add('show');
    var body=$('#pr-body');body.innerHTML='<div class="skel" style="height:80px"></div>';
    var r=await api('/profile?handle='+encodeURIComponent(handle));
    if(!r||!r.ok){body.innerHTML='<p style="color:var(--mut)">Bulunamadi</p>';return}
    var p=r.profile,st=r.style;var since=new Date(p.member_since).toLocaleDateString('tr-TR',{year:'numeric',month:'long'});
    var ach=(r.badges||[]).map(function(b){var x=b.badges||{};return '<span class="bdg'+(x.axis==='achievement'?' ach':'')+'">'+esc(x.label||b.badge_key)+'</span>'}).join('');
    var grid=(r.photos||[]).map(function(ph){return '<img loading="lazy" src="'+esc(ph.image_url)+'" alt="'+esc(ph.camera_model)+'">'}).join('');
    body.innerHTML=
      '<div class="pr-head"><img class="pr-av" src="'+esc(p.avatar_url||'')+'" alt=""><div><b style="font-size:18px">'+esc(p.display_name)+'</b>'+
        '<div style="font-size:13px;color:var(--mut)">@'+esc(p.handle)+(p.city?' &#183; '+esc(p.city):'')+'</div>'+
        '<div class="pr-stats"><div><b>'+st.photo_count+'</b>'+T.photosWord+'</div><div><b>'+p.total_likes+'</b>'+T.likesWord+'</div><div><b>'+p.orders_count+'</b>siparis</div></div></div></div>'+
      (p.bio?'<p style="font-size:14px;color:var(--mut)">'+esc(p.bio)+'</p>':'')+
      '<div style="font-size:12px;color:var(--mut);margin:8px 0">'+T.memberSince+': '+since+
        (st.top_camera?' &#183; '+T.styleCamera+': <b style="color:var(--txt)">'+esc(st.top_camera)+'</b>':'')+
        (st.top_location?' &#183; '+T.styleLocation+': <b style="color:var(--txt)">'+esc(st.top_location)+'</b>':'')+'</div>'+
      (ach?'<div class="shelf">'+ach+'</div>':'')+
      '<div class="pr-grid">'+grid+'</div>';
  }
  function openLogin(){window.location.href='/account/login'}
  // ---- toast ----
  var toEl;function toast(m){if(!toEl){toEl=document.createElement('div');toEl.style.cssText='position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#1c1c1f;border:1px solid var(--bd);color:#fff;padding:11px 18px;border-radius:12px;font-size:14px;z-index:80;opacity:0;transition:.3s';root.appendChild(toEl)}toEl.textContent=m;toEl.style.opacity='1';clearTimeout(toEl._t);toEl._t=setTimeout(function(){toEl.style.opacity='0'},2200)}
  // ---- events ----
  root.addEventListener('click',function(e){
    var like=e.target.closest('.like');if(like){vote(like);return}
    var by=e.target.closest('[data-h]');if(by){openProfile(by.dataset.h);return}
    if(e.target.closest('#hero-cta')||e.target.closest('#bar-up')){openUpload();return}
    var st=e.target.closest('.seg-tabs button[data-sort]');if(st){state.sort=st.dataset.sort;$$('.seg-tabs button[data-sort]').forEach(function(b){b.classList.toggle('on',b===st)});loadFeed(true);return}
    var lt=e.target.closest('.seg-tabs button[data-lb]');if(lt){state.lbRange=lt.dataset.lb;$$('.seg-tabs button[data-lb]').forEach(function(b){b.classList.toggle('on',b===lt)});loadLeaderboard();return}
    if(e.target.closest('#more')){loadFeed(false);return}
    if(e.target.closest('.x')||e.target.classList.contains('ov')){$$('.ov').forEach(function(o){o.classList.remove('show')});return}
  });
  // double-tap like
  var lastTap=0;root.addEventListener('touchend',function(e){var img=e.target.closest('.img-wrap');if(!img)return;var now=Date.now();if(now-lastTap<300){var b=$('.like',img.closest('.ph'));if(b&&!b.classList.contains('on'))vote(b)}lastTap=now});
  $('#drop').addEventListener('click',function(){$('#file').click()});
  $('#file').addEventListener('change',function(e){handleFile(e.target.files[0])});
  $('#up-send').addEventListener('click',submitUpload);
  // infinite scroll
  var sentinel=$('#sentinel');if(sentinel&&'IntersectionObserver'in window){new IntersectionObserver(function(es){if(es[0].isIntersecting&&state.next)loadFeed(false)},{rootMargin:'300px'}).observe(sentinel)}
  // exifr lazyload
  var ex=document.createElement('script');ex.src='https://cdn.jsdelivr.net/npm/exifr/dist/full.umd.js';document.head.appendChild(ex);
  boot();
})();
"""

def build():
    acc = "{{ section.settings.accent | default: '#FF4D2E' }}"
    css = CSS.replace("{{ACC}}", acc)
    js  = JS.replace("__T__", ld(T))

    html = []
    A = html.append
    A('<section class="rcl-comm" data-base="{{ section.settings.proxy_base | default: \'/apps/hesabim/community\' }}" '
      'data-slug="{{ section.settings.contest_slug | default: \'2026-haziran\' }}" '
      '{% if customer %}data-logged="1"{% endif %}>')
    A('<div class="aurora"></div>')
    A('<script type="application/ld+json">%s</script>' % ld(JSONLD))

    # HERO
    A('<div class="wrap hero">')
    A('  <span class="theme-chip">%s &#183; <span id="hero-theme"></span></span>' % E("Bu ayin temasi"))
    A('  <h1>%s</h1>' % E("RetroCameraLand Toplulugu"))
    A('  <p class="sub">%s</p>' % E("Cektigin kareyi yukle, kameranin modelini ve nerede cektigini yaz. Toplulugun oyuyla her hafta 1000 TL, her ay 5000 TL hediye ceki kazan."))
    A('  <div class="count" id="cd"></div>')
    A('  <div class="count-cap">%s</div>' % E("Haftalik oylama kapaniyor"))
    A('  <div class="social" id="hero-social"><span class="dot"></span><span></span></div>')
    A('  <div id="hero-cta-wrap"><button class="cta" id="hero-cta">'
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>%s</button></div>' % E("Fotografini yukle"))
    A('  <div class="login-card" id="login-card" style="display:none"><b>%s</b><p>%s</p>'
      '<a class="cta" href="/account/login">%s</a></div>'
      % (E("Topluluga katil"), E("Yarismaya katilmak, fotograf yuklemek ve oy vermek icin RetroCameraLand hesabinla giris yap."), E("Giris yap / Uye ol")))
    A('  <p class="rules">%s</p>' % E("Her uye bir fotografa 1 oy verir; kendi fotografina oy sayilmaz. Kazananlar topluluk oyuyla belirlenir."))
    A('</div>')

    # FEED + TABS
    A('<div class="bar"><div class="seg-tabs">'
      '<button data-sort="top" class="on">%s</button>'
      '<button data-sort="new">%s</button></div></div>' % (E("En Begenilen"), E("En Yeni")))
    A('<div class="wrap"><div class="feed" id="feed"></div>'
      '<div id="sentinel" style="height:1px"></div>'
      '<div style="text-align:center;padding:0 0 30px"><button class="like" id="more" style="display:none">%s</button></div></div>' % E("Daha fazla"))

    # LEADERBOARD
    A('<div class="wrap lb">')
    A('  <h2 style="text-align:center;font-size:clamp(22px,4vw,32px);letter-spacing:-.02em;margin:10px 0 4px">%s</h2>' % E("Lider Tablosu"))
    A('  <div class="bar" style="position:static;background:none;padding:10px 0"><div class="seg-tabs">'
      '<button data-lb="week" class="on">%s</button><button data-lb="month">%s</button></div></div>' % (E("Bu Hafta"), E("Bu Ay")))
    A('  <p class="lb-prize" id="lb-prize"></p>')
    A('  <div id="lb-list"></div>')
    A('  <div style="text-align:center;margin-top:18px"><button class="cta" id="bar-up">%s</button></div>' % E("Sen de katil"))
    A('</div>')

    # UPLOAD MODAL
    A('<div class="ov" id="m-up"><div class="sheet"><button class="x">&#215;</button>')
    A('  <div id="up-form"><h3>%s</h3>' % E("Yarismaya fotograf yukle"))
    A('    <input type="file" id="file" accept="image/*" hidden>')
    A('    <div class="drop" id="drop"></div>')
    A('    <div class="field"><label>%s</label><input id="f-cam" placeholder="%s"><div class="hint" id="h-cam">%s</div></div>'
      % (E("Kamera modeli"), E("orn. Canon AE-1"), E("EXIF'ten otomatik dolduruldu, kontrol et")))
    A('    <div class="field"><label>%s</label><input id="f-loc" placeholder="%s"><div class="hint" id="h-loc">%s</div></div>'
      % (E("Nerede cekildi?"), E("orn. Istanbul, Kadikoy"), E("EXIF'ten otomatik dolduruldu, kontrol et")))
    A('    <div class="field"><label>%s</label><textarea id="f-cap" rows="2" placeholder="%s"></textarea></div>'
      % (E("Aciklama (istege bagli)"), E("Bu kareyi anlat...")))
    A('    <div class="err" id="up-err"></div>')
    A('    <button class="send" id="up-send">%s</button></div>' % E("Yarismaya gonder"))
    A('  <div id="up-done" class="done" style="display:none">'
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>'
      '<h3>%s</h3><p id="done-body" style="color:var(--mut)"></p></div>' % E("Tesekkurler!"))
    A('</div></div>')

    # PROFILE DRAWER
    A('<div class="ov" id="m-pr"><div class="sheet"><button class="x">&#215;</button><div id="pr-body"></div></div></div>')

    A('<style>%s</style>' % css)
    A('<script>%s</script>' % js)
    A('</section>')

    # SCHEMA
    schema = {
      "name":"RCL Topluluk","tag":"section","class":"rcl-comm-wrap",
      "settings":[
        {"type":"header","content":"Baglanti"},
        {"type":"text","id":"proxy_base","label":"App Proxy yolu","default":"/apps/hesabim/community",
         "info":"Mevcut /apps/hesabim proxy'sinin altinda; Vercel rewrite ile community fonksiyonlarina baglanir"},
        {"type":"text","id":"contest_slug","label":"Aktif yarisma slug","default":"2026-haziran"},
        {"type":"header","content":"Gorunum"},
        {"type":"color","id":"accent","label":"Vurgu rengi","default":"#FF4D2E"}],
      "presets":[{"name":"RCL Topluluk"}]
    }
    A('{%% schema %%}\n%s\n{%% endschema %%}' % json.dumps(schema, ensure_ascii=True, indent=2))

    out = "\n".join(html)
    bad = [c for c in out if ord(c) > 127]
    assert not bad, "NON-ASCII karakter var: %r" % bad[:12]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="ascii") as f:
        f.write(out)
    print("OK ->", OUT, "(%d bytes, %d satir)" % (len(out), out.count(chr(10))+1))

if __name__ == "__main__":
    build()
