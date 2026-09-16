#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Dijital Kamera Bakim Rehberi (interaktif, animasyonlu, mobil uyumlu)
=========================================================================
Tek seferlik ozel blog: retro dijital kameralarin ne kadar keyifli bir ugras
oldugunu, kullaniminin kolayligini ve basit bakimla yillarca sorunsuz
calisacagini anlatir. Standart segment bloglarindan farkli olarak:
  - Scroll-reveal animasyonlari (IntersectionObserver, prefers-reduced-motion'a saygili)
  - Interaktif bakim checklist'i: tiklanabilir, localStorage'da kalici, canli
    ilerleme cubugu (% tamamlandi)
  - Acilir/kapanir (accordion) SSS
  - Musteri etkilesimi: yorum bolumune (blog zaten commentable) davet + CTA
  - JSON-LD: Article + HowTo + FAQPage + BreadcrumbList
  - Tum CSS/JS tek bir .rcl-care-2026 sarmalayicisina scoped (tema ile catisma yok)

Kullanim:
  python3 rcl-blog-bakim-rehberi.py --dry   # onizleme (yayinlamaz)
  python3 rcl-blog-bakim-rehberi.py         # CANLI yayinla
"""
import sys, time, json, argparse, os
sys.path.insert(0, "/Users/onnoshot/Downloads/Agentlar")
from retrocameraland_api import shopify, log, SOCIAL_BLOCK

try:
    from pinterest_image_fetcher import find_unused_pinterest_image
    PIN_OK = True
except Exception as e:
    log(f"Pinterest fetcher yuklenemedi: {e}")
    PIN_OK = False

BLOG_ID  = "91197866123"
SITE     = "https://retrocameraland.com"
BLOG_URL = f"{SITE}/blogs/retro-dijital-kamera"   # RCL blog handle: retro-dijital-kamera (news DEGIL)
FINDER   = f"{SITE}/pages/hangi-kamera-bana-uygun"
LOGO     = f"{SITE}/cdn/shop/files/retrocameraland_banner.jpg"
TODAY    = time.strftime("%Y-%m-%d")

TITLE    = "Retro Dijital Kamera Bakımı Nasıl Yapılır? Yıllarca Sorunsuz Kullanım Rehberi"
HANDLE   = "retro-dijital-kamera-bakimi-nasil-yapilir-yillarca-sorunsuz-kullanim-rehberi"
KEYWORD  = "retro dijital kamera bakımı"
TAGS     = "kamera bakimi, retro kamera bakimi, ccd kamera bakimi, dijital kamera temizligi, kamera saklama, retrocameraland"
META_DESC = "Retro dijital kamerani yillarca sorunsuz kullanmak icin gereken 7 basit bakim adimi: pil, nem, lens temizligi ve daha fazlasi. Interaktif ve kolay bakim rehberi."
IMG_KW   = "vintage digital camera care maintenance cleaning cozy desk"
PIN_HERO = "camera cleaning kit vintage desk"

CHECKLIST = [
    ("Kullanmadığın zaman pili çıkar",
     "Kamerayi uzun sure (2 haftadan fazla) kullanmayacaksan pili disari cikar. Bosalan bir pil govdede akarsa kontaklara zarar verebilir; bu, ikinci el kameralarda en sik gordugumuz onlenebilir arizadir."),
    ("Nemden uzak, kuru bir yerde sakla",
     "Nem, lens icine bulanikligin ve devre karti sorunlarinin bas nedenidir. Kamerani kilifinde, mumkunse icine kucuk bir silika jel paketi koyarak kuru bir dolapta sakla; banyo veya nemli depo gibi yerlerden uzak tut."),
    ("Lensi sadece mikrofiber bezle temizle",
     "Parmak, mendil veya gomlek kenari lens yuzeyinde ince cizikler birakabilir. Tozu once uflemeyle (ya da yumusak fircayla) uzaklastir, sonra kuru bir mikrofiber bezle hafifce sil. Asla direkt lensin uzerine sivi sikma."),
    ("Pil ve kart kontaklarini temiz tut",
     "Pil yuvasindaki metal kontaklarda toz veya oksitlenme birikirse kamera acilmayabilir ya da kart okunamayabilir. Ayda bir, kuru bir pamuklu cubukla bu kontaklari hafifce silmek kucuk ama etkili bir aliskanliktir."),
    ("Hafiza kartini duzenli kontrol et",
     "Fotograflarini bilgisayarina aktardiktan sonra karti kamerada formatla (bilgisayarda degil, kameranin kendi menusunden); bu, dosya sistemi hatalarini onler ve kartin omrunu uzatir."),
    ("Duz surdurmekten koru: askı veya kılıf kullan",
     "Retro kameralarin govdesi bugunun telefonlari kadar darbeye dayanikli tasarlanmamistir. Boyun/bilek askisini takip etmek ve tasirken yumusak bir kilif kullanmak, en yaygin hasar nedenini -dusme- buyuk olcude ortadan kaldirir."),
    ("Yilda bir kez tam fonksiyon kontrolu yap",
     "Yilda bir, kamerayi ac, tum modlari (flas, zoom, video, kart okuma) tek tek dene. Kucuk bir sorunu erken fark etmek, buyuk bir arizaya donusmeden onune gecmenin en kolay yoludur."),
]

FAQS = [
    ("Retro dijital kamera bakımı gerçekten zor mu?",
     "Hayir, tam tersine oldukca kolay. Yukaridaki 7 adimin cogu ayda birkac dakikani alan basit aliskanliklardir: pili cikarmak, kuru saklamak, lensi yumusak bezle silmek. Karmasik bir ekipman veya teknik bilgi gerekmez."),
    ("Bakım yapmazsam kamera gerçekten bozulur mu?",
     "En sik goruleun ariza nedenleri tam olarak bakimsizliktan kaynaklanir: akan pil kontaklari kirletir, nem lens icine bulanikliga yol acar, dususler govdeyi hasarlar. Bu 7 basit adima dikkat eden bir kullanici, kamerasini yillarca sorunsuz kullanabilir."),
    ("İkinci el bir retro kamera alırken neye dikkat etmeliyim?",
     "RetroCameraLand'da satistan once her kamera fonksiyon testinden gecer ve kondisyonu seffaf bicimde paylasilir; yani aldigin kamera zaten saglikli bir baslangic noktasindan gelir. Senin gorevin bu rehberdeki aliskanliklarla o saglikli durumu korumak."),
    ("Retro kamera kullanmak yeni başlayanlar için zor mu?",
     "Hayir. Cogu retro dijital kompakt tam otomatik moda sahiptir: ac, kadrajla, cek. Ayar ogrenmene gerek kalmadan ilk kareden itibaren o sicak, filmsi retro tonu elde edersin -tam da bu kolaylik, bu ugrasi bu kadar sevilir kilan sey."),
]

# ── finder CTA ─────────────────────────────────────────────────────────────
def finder_cta():
    return (
      '<div class="rcl-care-cta">'
      '<div class="rcl-care-cta-tag">AI KAMERA ESLESTIRICI</div>'
      '<h3>Henüz bir retro kameran yok mu?</h3>'
      '<p>Bu bakim aliskanliklarini uygulayacagin ilk retro kamerani secmek icin '
      '6 kisa soruyu yanitla, sana en uygun uc modeli yuzdesel uyum skoruyla gorelim.</p>'
      f'<a href="{FINDER}" class="rcl-care-cta-btn">Sana özel kamerani bul &#8594;</a>'
      '<div class="rcl-care-cta-sub">6 kisa soru &bull; ~1 dakika &bull; ucretsiz &bull; uyelik yok</div>'
      '</div>'
    )

# ── JSON-LD: Article + HowTo + FAQPage + BreadcrumbList ───────────────────
def schema_blocks(image):
    url = f"{BLOG_URL}/{HANDLE}"
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": TITLE, "description": META_DESC,
        "image": image or LOGO, "datePublished": TODAY, "dateModified": TODAY,
        "author":   {"@type": "Organization", "name": "RetroCameraLand", "url": SITE},
        "publisher": {"@type": "Organization", "name": "RetroCameraLand",
                      "logo": {"@type": "ImageObject", "url": LOGO}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    howto = {
        "@context": "https://schema.org", "@type": "HowTo",
        "name": "Retro Dijital Kamera Bakımı Nasıl Yapılır?",
        "description": META_DESC,
        "step": [
            {"@type": "HowToStep", "name": q, "text": a}
            for q, a in CHECKLIST
        ],
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQS
        ],
    }
    crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": BLOG_URL},
            {"@type": "ListItem", "position": 3, "name": TITLE, "item": url},
        ],
    }
    def tag(d): return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
    return "\n" + tag(article) + tag(howto) + tag(faq) + tag(crumb)

# ── checklist + faq HTML parcalari (JS/CSS tarafinda islenecek) ──────────
def checklist_items_html():
    out = []
    for i, (t, d) in enumerate(CHECKLIST):
        out.append(
            f'<li class="rcl-care-item" data-reveal>'
            f'<label class="rcl-care-check">'
            f'<input type="checkbox" data-idx="{i}">'
            f'<span class="rcl-care-box" aria-hidden="true"></span>'
            f'<span class="rcl-care-text"><strong>{t}</strong><br>{d}</span>'
            f'</label></li>'
        )
    return "\n".join(out)

def faq_items_html():
    out = []
    for i, (q, a) in enumerate(FAQS):
        out.append(
            f'<div class="rcl-care-faq-item" data-reveal>'
            f'<button class="rcl-care-faq-q" aria-expanded="false" data-faq="{i}">'
            f'<span>{q}</span><span class="rcl-care-faq-icon">+</span></button>'
            f'<div class="rcl-care-faq-a" id="rcl-care-faq-a-{i}"><p>{a}</p></div>'
            f'</div>'
        )
    return "\n".join(out)

STYLE_SCRIPT = """
<style>
.rcl-care-2026{--rc-ink:#1c1712;--rc-warm:#d8472f;--rc-warm2:#e9836f;--rc-cream:#faf6f1;--rc-line:#e7ddd2;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:var(--rc-ink);max-width:820px;margin:0 auto;line-height:1.7;}
.rcl-care-2026 *{box-sizing:border-box;}
.rcl-care-2026 h1{font-size:clamp(26px,5vw,40px);font-weight:800;line-height:1.15;margin:0 0 18px;}
.rcl-care-2026 h2{font-size:clamp(21px,3.6vw,28px);font-weight:800;margin:44px 0 16px;}
.rcl-care-2026 p{font-size:16px;margin:0 0 14px;}
.rcl-care-2026 .rcl-care-lede{font-size:clamp(17px,2.4vw,19px);color:#4a4038;}

.rcl-care-2026 [data-reveal]{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease;}
.rcl-care-2026 [data-reveal].rcl-in{opacity:1;transform:translateY(0);}
@media (prefers-reduced-motion:reduce){.rcl-care-2026 [data-reveal]{opacity:1;transform:none;transition:none;}}

.rcl-care-hero{background:linear-gradient(135deg,#2a2018,#15110d);color:#fff;border-radius:20px;padding:38px 28px;margin:0 0 32px;text-align:center;position:relative;overflow:hidden;}
.rcl-care-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 30% 20%,rgba(233,131,111,.25),transparent 60%);animation:rclGlow 6s ease-in-out infinite;}
@keyframes rclGlow{0%,100%{opacity:.6}50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.rcl-care-hero::before{animation:none;}}
.rcl-care-hero-tag{position:relative;font-size:12px;letter-spacing:.16em;font-weight:700;color:var(--rc-warm2);text-transform:uppercase;margin-bottom:12px;}
.rcl-care-hero h1{position:relative;color:#fff;}
.rcl-care-hero p{position:relative;color:#d8d0c8;max-width:560px;margin:14px auto 0;font-size:16px;}

.rcl-care-3col{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:28px 0 8px;}
@media (max-width:640px){.rcl-care-3col{grid-template-columns:1fr;}}
.rcl-care-3col .rc-card{background:var(--rc-cream);border:1px solid var(--rc-line);border-radius:14px;padding:20px 18px;transition:transform .3s ease,box-shadow .3s ease;}
.rcl-care-3col .rc-card:hover{transform:translateY(-4px);box-shadow:0 10px 24px rgba(0,0,0,.08);}
.rcl-care-3col .rc-emoji{font-size:26px;display:block;margin-bottom:8px;}
.rcl-care-3col strong{display:block;font-size:15.5px;margin-bottom:4px;}
.rcl-care-3col span.rc-sub{font-size:13.5px;color:#6b6058;}

.rcl-care-progress-wrap{position:sticky;top:8px;z-index:5;background:#fff;border:1px solid var(--rc-line);border-radius:14px;padding:14px 18px;margin:8px 0 22px;box-shadow:0 4px 16px rgba(0,0,0,.05);}
.rcl-care-progress-top{display:flex;justify-content:space-between;align-items:center;font-size:13.5px;font-weight:700;margin-bottom:8px;}
.rcl-care-progress-track{height:10px;background:var(--rc-line);border-radius:100px;overflow:hidden;}
.rcl-care-progress-fill{height:100%;width:0%;background:linear-gradient(90deg,var(--rc-warm),var(--rc-warm2));border-radius:100px;transition:width .5s cubic-bezier(.4,0,.2,1);}
.rcl-care-progress-msg{margin-top:8px;font-size:13px;color:#6b6058;min-height:18px;}

.rcl-care-list{list-style:none;padding:0;margin:0 0 12px;display:flex;flex-direction:column;gap:12px;}
.rcl-care-item{border:1px solid var(--rc-line);border-radius:14px;background:#fff;transition:border-color .25s ease,background .25s ease;}
.rcl-care-item:has(input:checked){background:#fbf3ef;border-color:#f0c9bc;}
.rcl-care-check{display:flex;align-items:flex-start;gap:14px;padding:16px 18px;cursor:pointer;}
.rcl-care-check input{position:absolute;opacity:0;width:1px;height:1px;}
.rcl-care-box{flex:0 0 24px;width:24px;height:24px;border-radius:8px;border:2px solid var(--rc-line);position:relative;transition:background .25s ease,border-color .25s ease,transform .2s ease;}
.rcl-care-check input:checked + .rcl-care-box{background:var(--rc-warm);border-color:var(--rc-warm);transform:scale(1.05);}
.rcl-care-box::after{content:'';position:absolute;left:6px;top:2px;width:6px;height:11px;border:solid #fff;border-width:0 2.5px 2.5px 0;transform:rotate(45deg) scale(0);transition:transform .2s ease .05s;}
.rcl-care-check input:checked + .rcl-care-box::after{transform:rotate(45deg) scale(1);}
.rcl-care-text{font-size:15px;}
.rcl-care-text strong{font-size:15.5px;}
.rcl-care-check input:checked ~ .rcl-care-text strong{text-decoration:line-through;text-decoration-color:var(--rc-warm2);opacity:.65;}

.rcl-care-faq-item{border-bottom:1px solid var(--rc-line);}
.rcl-care-faq-q{width:100%;text-align:left;background:none;border:none;padding:18px 4px;font-size:16px;font-weight:700;font-family:inherit;color:var(--rc-ink);display:flex;justify-content:space-between;align-items:center;cursor:pointer;gap:12px;}
.rcl-care-faq-icon{flex:0 0 auto;font-size:20px;color:var(--rc-warm);transition:transform .3s ease;}
.rcl-care-faq-q[aria-expanded="true"] .rcl-care-faq-icon{transform:rotate(45deg);}
.rcl-care-faq-a{max-height:0;overflow:hidden;transition:max-height .35s ease;}
.rcl-care-faq-a p{padding:0 4px 16px;color:#4a4038;font-size:15px;}

.rcl-care-cta{background:linear-gradient(135deg,#15110d,#2a2018);color:#fff;border-radius:18px;padding:34px 28px;margin:46px 0;text-align:center;}
.rcl-care-cta-tag{font-size:13px;letter-spacing:.16em;font-weight:700;color:var(--rc-warm2);text-transform:uppercase;margin-bottom:10px;}
.rcl-care-cta h3{margin:0 0 12px;font-size:24px;font-weight:800;color:#fff;line-height:1.2;}
.rcl-care-cta p{margin:0 auto 22px;max-width:520px;font-size:16px;line-height:1.6;color:#d8d0c8;}
.rcl-care-cta-btn{display:inline-block;background:var(--rc-warm);color:#fff;padding:15px 34px;border-radius:100px;text-decoration:none;font-weight:700;font-size:16px;transition:transform .2s ease;}
.rcl-care-cta-btn:hover{transform:scale(1.04);}
.rcl-care-cta-sub{margin-top:14px;font-size:13px;color:#9a9088;}

.rcl-care-comment{background:var(--rc-cream);border:1px dashed #cbb89f;border-radius:14px;padding:22px 20px;margin:36px 0;text-align:center;}
.rcl-care-comment strong{display:block;font-size:16px;margin-bottom:6px;}
.rcl-care-comment span{font-size:14px;color:#6b6058;}
</style>

<script>
(function(){
  var root = document.currentScript ? document.currentScript.closest('.rcl-care-2026') : null;
  if(!root){ var roots = document.querySelectorAll('.rcl-care-2026'); root = roots[roots.length-1]; }
  if(!root) return;

  // scroll-reveal
  try{
    var items = root.querySelectorAll('[data-reveal]');
    if('IntersectionObserver' in window){
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('rcl-in'); io.unobserve(e.target); } });
      }, {threshold:.15});
      items.forEach(function(el){ io.observe(el); });
    } else {
      items.forEach(function(el){ el.classList.add('rcl-in'); });
    }
  }catch(e){}

  // interaktif bakim checklist + ilerleme cubugu (localStorage kalici)
  try{
    var KEY = 'rclCareChecklist2026';
    var boxes = root.querySelectorAll('.rcl-care-check input[type=checkbox]');
    var fill = root.querySelector('.rcl-care-progress-fill');
    var label = root.querySelector('.rcl-care-progress-label');
    var msg = root.querySelector('.rcl-care-progress-msg');
    var saved = {};
    try{ saved = JSON.parse(localStorage.getItem(KEY) || '{}'); }catch(e){}

    function update(){
      var total = boxes.length, done = 0;
      boxes.forEach(function(b){ if(b.checked) done++; });
      var pct = total ? Math.round(done/total*100) : 0;
      if(fill) fill.style.width = pct + '%';
      if(label) label.textContent = done + '/' + total + ' tamamlandı (%' + pct + ')';
      if(msg){
        if(pct === 0) msg.textContent = 'Uyguladığın adımları işaretle, ilerlemeni takip et.';
        else if(pct < 100) msg.textContent = 'Güzel gidiyor, devam et — kameran teşekkür ediyor.';
        else msg.textContent = 'Harika! Bu 7 adıma dikkat ettiğin sürece kameran yıllarca sorunsuz çalışır.';
      }
    }
    boxes.forEach(function(b){
      var idx = b.getAttribute('data-idx');
      if(saved[idx]) b.checked = true;
      b.addEventListener('change', function(){
        saved[idx] = b.checked;
        try{ localStorage.setItem(KEY, JSON.stringify(saved)); }catch(e){}
        update();
      });
    });
    update();
  }catch(e){}

  // accordion SSS
  try{
    var qs = root.querySelectorAll('.rcl-care-faq-q');
    qs.forEach(function(btn){
      btn.addEventListener('click', function(){
        var expanded = btn.getAttribute('aria-expanded') === 'true';
        var panel = root.querySelector('#rcl-care-faq-a-' + btn.getAttribute('data-faq'));
        qs.forEach(function(other){
          if(other !== btn){
            other.setAttribute('aria-expanded','false');
            var op = root.querySelector('#rcl-care-faq-a-' + other.getAttribute('data-faq'));
            if(op) op.style.maxHeight = null;
          }
        });
        btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        if(panel) panel.style.maxHeight = expanded ? null : panel.scrollHeight + 'px';
      });
    });
  }catch(e){}
})();
</script>
"""

def build_html(image_url):
    parts = []
    parts.append('<div class="rcl-care-2026">')
    parts.append(
      '<div class="rcl-care-hero" data-reveal>'
      '<div class="rcl-care-hero-tag">RCL BAKIM REHBERİ</div>'
      f'<h1>{TITLE}</h1>'
      '<p>Retro dijital kamera edinmek küçük ama gerçek bir keyif; her anı sıcak, '
      'filmsi bir dokunuşla kaydediyor ve kullanımı düşündüğünden çok daha kolay. '
      'Bu rehberdeki 7 basit alışkanlıkla o kamera yıllarca yanında kalır.</p>'
      '</div>'
    )
    parts.append(
      '<p class="rcl-care-lede">Bir retro kamera edinmek bir uğraştan çok bir keyif halini alır: '
      'her tıkta o sıcak, nostaljik tonu görmek, anı "sıradan" değil "hatırlanacak" kılar. '
      'İyi haber şu: bu kameraları kullanmak zor değil — çoğu tam otomatik moda sahip, '
      'aç-kadrajla-çek kadar basit. Ve satın aldıktan sonra birkaç küçük alışkanlığa dikkat '
      'edersen, bu kamera yıllarca hiç sorun çıkarmadan yanında olur. Aşağıdaki 7 adım tam '
      'olarak bunun için var.</p>'
    )
    parts.append(
      '<div class="rcl-care-3col">'
      '<div class="rc-card" data-reveal><span class="rc-emoji">📸</span><strong>Anı güzel kaydeder</strong>'
      '<span class="rc-sub">Sıcak, filmsi renk karakteri her kareyi bir hatıraya çevirir.</span></div>'
      '<div class="rc-card" data-reveal><span class="rc-emoji">✅</span><strong>Kullanımı çok kolay</strong>'
      '<span class="rc-sub">Tam otomatik mod: aç, kadrajla, çek. Teknik bilgi gerekmez.</span></div>'
      '<div class="rc-card" data-reveal><span class="rc-emoji">🛠️</span><strong>Uzun yıllar dayanır</strong>'
      '<span class="rc-sub">Basit bakım alışkanlıklarıyla yıllarca sorunsuz çalışır.</span></div>'
      '</div>'
    )
    parts.append('<h2>Bakım Checklist’i: Adımları İşaretle</h2>')
    parts.append(
      '<p>Aşağıdaki 7 adımı uyguladıkça işaretle — ilerlemen tarayıcında kalıcı olarak kaydedilir, '
      'siteye her döndüğünde kaldığın yerden devam edersin.</p>'
    )
    parts.append(
      '<div class="rcl-care-progress-wrap">'
      '<div class="rcl-care-progress-top"><span>Bakım İlerlemen</span>'
      '<span class="rcl-care-progress-label">0/7 tamamlandı (%0)</span></div>'
      '<div class="rcl-care-progress-track"><div class="rcl-care-progress-fill"></div></div>'
      '<div class="rcl-care-progress-msg">Uyguladığın adımları işaretle, ilerlemeni takip et.</div>'
      '</div>'
    )
    parts.append(f'<ul class="rcl-care-list">{checklist_items_html()}</ul>')
    parts.append(
      '<h2>Neden Bu Kadar Kolay?</h2>'
      '<p>Retro dijital kameraların en sevilen yanı, "vintage" olmalarına rağmen kullanımlarının '
      'hiç eskimemiş olması. Otomatik pozlama, otomatik odak ve basit menüler sayesinde ilk '
      'kareden itibaren o aradığın sıcak tonu alırsın; hiçbir ayarla uğraşmana gerek kalmaz. '
      'Karmaşık olan tek şey bakım değil — bakım da yukarıdaki 7 basit alışkanlıktan ibaret.</p>'
    )
    parts.append('<h2>Sıkça Sorulan Sorular</h2>')
    parts.append(f'<div class="rcl-care-faq">{faq_items_html()}</div>')
    parts.append(finder_cta())
    parts.append(
      '<div class="rcl-care-comment" data-reveal>'
      '<strong>Sıra sende 👇</strong>'
      '<span>Kendi retro kameranla ilgili bir bakım ipucun mu var, yoksa bir sorun mu takıldı '
      'aklına? Aşağıdaki yorum bölümünden paylaş — birlikte daha uzun bir bakım listesi '
      'oluşturalım.</span>'
      '</div>'
    )
    parts.append(SOCIAL_BLOCK)
    parts.append(STYLE_SCRIPT)
    parts.append('</div>')  # /.rcl-care-2026
    parts.append(schema_blocks(image_url))
    return "\n\n".join(parts)

def pick_image():
    if not PIN_OK:
        return None, "pinterest yok"
    url, desc, score = find_unused_pinterest_image(IMG_KW, PIN_HERO)
    return url, f"{desc} (score={score})"

def publish(dry=False):
    img_url, img_note = pick_image()
    html = build_html(img_url)
    if dry:
        out = f"/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/b69db648-5a59-420b-9e27-7493a363a0da/scratchpad/preview_{HANDLE}.html"
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(
                f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                f"<title>{TITLE}</title>"
                f"<div style='max-width:900px;margin:40px auto;padding:0 16px'>{html}</div>")
        except Exception:
            pass
        log(f"  [DRY] {TITLE[:50]} | gorsel: {img_note} | onizleme: {out}")
        return {"status": "dry", "title": TITLE, "image": img_url}
    payload = {"article": {
        "title": TITLE, "body_html": html, "handle": HANDLE,
        "tags": TAGS, "published": True,
        "metafields": [
            {"namespace": "seo", "key": "description", "value": META_DESC, "type": "single_line_text_field"},
            {"namespace": "seo", "key": "title",       "value": TITLE,     "type": "single_line_text_field"},
        ]}}
    if img_url:
        payload["article"]["image"] = {"src": img_url, "alt": TITLE}
    r = shopify("POST", f"blogs/{BLOG_ID}/articles.json", payload)
    art = r["article"]
    log(f"  OK ID:{art['id']} -> {art['handle']} | gorsel: {img_note}")
    return {"status": "ok", "id": art["id"], "handle": art["handle"], "title": TITLE}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="Yayinlamadan onizleme uret")
    args = ap.parse_args()
    log(f"{'DRY-RUN' if args.dry else 'CANLI YAYIN'} — Bakim Rehberi")
    try:
        r = publish(dry=args.dry)
        log(f"\nSonuc: {r['status']} — {r['title']}")
    except Exception as e:
        log(f"HATA: {e}")
        sys.exit(1)
