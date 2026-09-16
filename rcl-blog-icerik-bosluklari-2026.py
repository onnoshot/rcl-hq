#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Icerik Bosluklari 2026 — 10 Blog
=====================================
Rakip/arama-talebi arastirmasindan cikan, mevcut 297 blogda karsiligi
olmayan 10 yeni konu basligi. Hepsi:
  - SEO: H1/H2 yapisi, uzun-kuyruk anahtar kelime, meta aciklama
  - SGE/AEO: ust kisimda "Kisa Cevap" kutusu (AI Overview icin direkt cevap)
  - JSON-LD: Article + FAQPage + BreadcrumbList (+ HowTo, uygun olanlarda)
  - Animasyonlu + etkilesimli: reveal-on-scroll, acilir FAQ akordiyon,
    tiklanabilir kontrol listesi, gauge bar, sekmeli karsilastirma
  - Gercek stok urunlere deep-link (/products/...)
  - Sonunda AI Kamera Eslestirici finder CTA + sosyal medya bloku

Kullanim:
  python3 rcl-blog-icerik-bosluklari-2026.py --dry     # onizleme (yayinlamaz)
  python3 rcl-blog-icerik-bosluklari-2026.py --index 3 # sadece 3. yaziyi yayinla
  python3 rcl-blog-icerik-bosluklari-2026.py           # tumunu sirayla yayinla
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
BLOG_URL = f"{SITE}/blogs/retro-dijital-kamera"
FINDER   = f"{SITE}/pages/hangi-kamera-bana-uygun"
LOGO     = f"{SITE}/cdn/shop/files/retrocameraland_banner.jpg"
TODAY    = time.strftime("%Y-%m-%d")

# ═══════════════════════════════════════════════════════════════════════════
#  ORTAK STIL + ETKILESIM KUTU KUTUPHANESI
# ═══════════════════════════════════════════════════════════════════════════
def interactive_style():
    return """<style>
:root{--rclart-ink:#1a1410;--rclart-sub:#5a5048;--rclart-accent:#d8472f;--rclart-accent2:#e9836f;--rclart-paper:#f8f4f0;--rclart-line:#e6dcd0;}
@keyframes rclartFade{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes rclartGrow{from{width:0}to{width:var(--pct)}}
.rclart-reveal{animation:rclartFade .6s ease both}
.rclart-quickbox{background:var(--rclart-paper);border:1px solid var(--rclart-line);border-left:5px solid var(--rclart-accent);
  border-radius:0 14px 14px 0;padding:20px 24px;margin:26px 0;}
.rclart-quickbox .rclart-tag{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
  color:var(--rclart-accent);margin-bottom:8px;display:block;}
.rclart-quickbox p{margin:0;line-height:1.7;color:var(--rclart-ink);font-size:16px}
details.rclart-faq{border:1px solid var(--rclart-line);border-radius:12px;margin:10px 0;overflow:hidden;background:#fff}
details.rclart-faq summary{cursor:pointer;padding:16px 20px;font-weight:700;list-style:none;
  display:flex;justify-content:space-between;align-items:center;gap:12px;color:var(--rclart-ink)}
details.rclart-faq summary::-webkit-details-marker{display:none}
details.rclart-faq summary::after{content:'+';font-size:22px;line-height:1;color:var(--rclart-accent);
  transition:transform .25s ease;flex:0 0 auto}
details.rclart-faq[open] summary::after{transform:rotate(45deg)}
details.rclart-faq .rclart-a{padding:0 20px 18px;margin:0;color:var(--rclart-sub);line-height:1.75}
.rclart-checklist{margin:20px 0}
.rclart-checklist label{display:flex;gap:12px;align-items:flex-start;padding:13px 16px;
  border:1px solid var(--rclart-line);border-radius:10px;margin:8px 0;cursor:pointer;transition:.2s;background:#fff}
.rclart-checklist label:hover{border-color:var(--rclart-accent2)}
.rclart-checklist input{margin-top:3px;accent-color:var(--rclart-accent);width:18px;height:18px;flex:0 0 auto}
.rclart-checklist input:checked ~ span{text-decoration:line-through;opacity:.5}
.rclart-gaugerow{margin:18px 0}
.rclart-gaugerow .rclart-glabel{display:flex;justify-content:space-between;font-weight:700;
  font-size:14px;margin-bottom:6px;color:var(--rclart-ink)}
.rclart-gauge{height:11px;border-radius:6px;background:#ece1d5;overflow:hidden}
.rclart-gauge i{display:block;height:100%;border-radius:6px;
  background:linear-gradient(90deg,var(--rclart-accent2),var(--rclart-accent));width:var(--pct);
  animation:rclartGrow 1.1s cubic-bezier(.22,1,.36,1) both;animation-delay:.15s}
.rclart-gaugerow .rclart-gdesc{font-size:13.5px;color:var(--rclart-sub);margin-top:6px;line-height:1.6}
.rclart-tabs{margin:22px 0}
.rclart-tabnav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.rclart-tabnav label{padding:9px 18px;border-radius:100px;background:var(--rclart-paper);
  border:1px solid var(--rclart-line);font-weight:700;font-size:13.5px;cursor:pointer;color:var(--rclart-sub);transition:.2s}
.rclart-tabs input{position:absolute;opacity:0;pointer-events:none}
.rclart-panel{display:none;border:1px solid var(--rclart-line);border-radius:14px;padding:20px 22px;background:#fff}
.rclart-howto{counter-reset:rclstep;margin:20px 0}
.rclart-howto .rclart-step{position:relative;padding:6px 0 22px 44px;border-left:2px solid var(--rclart-line);margin-left:16px}
.rclart-howto .rclart-step:last-child{border-color:transparent;padding-bottom:0}
.rclart-howto .rclart-step::before{counter-increment:rclstep;content:counter(rclstep);
  position:absolute;left:-17px;top:0;width:32px;height:32px;border-radius:50%;
  background:var(--rclart-accent);color:#fff;font-weight:800;font-size:14px;display:flex;
  align-items:center;justify-content:center}
.rclart-howto h4{margin:0 0 6px;font-size:16.5px;color:var(--rclart-ink)}
.rclart-howto p{margin:0;color:var(--rclart-sub);line-height:1.7;font-size:15px}
@media (prefers-reduced-motion:reduce){.rclart *{animation:none!important}}
</style>"""

def quickbox(text):
    return (f'<div class="rclart-quickbox rclart-reveal"><span class="rclart-tag">Kisa Cevap</span>'
            f'<p>{text}</p></div>')

def faq_accordion(faqs):
    out = ['<h2>Sikca Sorulan Sorular</h2><div class="rclart">']
    for i, (q, a) in enumerate(faqs):
        open_attr = " open" if i == 0 else ""
        out.append(f'<details class="rclart-faq"{open_attr}><summary>{q}</summary>'
                    f'<p class="rclart-a">{a}</p></details>')
    out.append('</div>')
    return "\n".join(out)

def checklist(items):
    out = ['<div class="rclart-checklist rclart-reveal">']
    for i, item in enumerate(items):
        out.append(f'<label><input type="checkbox" id="cl{i}"><span>{item}</span></label>')
    out.append('</div>')
    return "\n".join(out)

def gauge_rows(rows):
    # rows: list of (label, pct_int, desc)
    out = ['<div class="rclart">']
    for label, pct, desc in rows:
        out.append(
          f'<div class="rclart-gaugerow rclart-reveal"><div class="rclart-glabel"><span>{label}</span>'
          f'<span>{pct}/100</span></div><div class="rclart-gauge"><i style="--pct:{pct}%"></i></div>'
          f'<div class="rclart-gdesc">{desc}</div></div>'
        )
    out.append('</div>')
    return "\n".join(out)

def tabs(tab_list):
    # tab_list: list of (label, html) — pure CSS, no JS: radio + general-sibling selector
    n = len(tab_list)
    ids = [f"rcltab{i}" for i in range(n)]
    pids = [f"rclpanel{i}" for i in range(n)]
    css_rules = []
    for i in range(n):
        css_rules.append(
          f'#{ids[i]}:checked ~ .rclart-tabnav label[for="{ids[i]}"]{{background:var(--rclart-accent);'
          f'color:#fff;border-color:var(--rclart-accent)}}\n'
          f'#{ids[i]}:checked ~ #{pids[i]}{{display:block}}'
        )
    style = f'<style>{"".join(css_rules)}</style>'
    inputs = "".join(
        f'<input type="radio" name="rclgrp" id="{ids[i]}"{" checked" if i == 0 else ""}>'
        for i in range(n)
    )
    nav = ['<div class="rclart-tabnav">']
    for i, (label, _) in enumerate(tab_list):
        nav.append(f'<label for="{ids[i]}">{label}</label>')
    nav.append('</div>')
    panels = [f'<div class="rclart-panel" id="{pids[i]}">{html}</div>' for i, (_, html) in enumerate(tab_list)]
    return (f'<div class="rclart-tabs rclart-reveal">{style}{inputs}'
            + "".join(nav) + "".join(panels) + '</div>')

def howto_steps(steps):
    # steps: list of (title, desc)
    out = ['<div class="rclart-howto rclart-reveal">']
    for title, desc in steps:
        out.append(f'<div class="rclart-step"><h4>{title}</h4><p>{desc}</p></div>')
    out.append('</div>')
    return "\n".join(out)

def reveal(html):
    return f'<div class="rclart-reveal">{html}</div>'

# ── finder CTA ────────────────────────────────────────────────────────────
def finder_cta(line):
    return (
      '<div style="background:linear-gradient(135deg,#15110d,#2a2018);color:#fff;'
      'border-radius:18px;padding:34px 28px;margin:46px 0;text-align:center;">'
      '<div style="font-size:13px;letter-spacing:.16em;font-weight:700;color:#e9836f;'
      'text-transform:uppercase;margin-bottom:10px;">AI KAMERA ESLESTIRICI</div>'
      f'<h3 style="margin:0 0 12px;font-size:24px;font-weight:800;color:#fff;line-height:1.2;">'
      'Hala kararsiz misin?</h3>'
      f'<p style="margin:0 auto 22px;max-width:520px;font-size:16px;line-height:1.6;color:#d8d0c8;">{line}</p>'
      f'<a href="{FINDER}" style="display:inline-block;background:#d8472f;color:#fff;'
      'padding:15px 34px;border-radius:100px;text-decoration:none;font-weight:700;font-size:16px;">'
      'Sana ozel kamerani bul &#8594;</a>'
      '<div style="margin-top:14px;font-size:13px;color:#9a9088;">'
      '6 kisa soru &bull; ~1 dakika &bull; ucretsiz &bull; uyelik yok</div>'
      '</div>'
    )

# ── JSON-LD (Article + FAQPage + BreadcrumbList [+ HowTo]) ─────────────────
def schema_blocks(title, handle, meta_desc, image, faqs, howto=None):
    url = f"{BLOG_URL}/{handle}"
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": meta_desc,
        "image": image or LOGO, "datePublished": TODAY, "dateModified": TODAY,
        "author":   {"@type": "Organization", "name": "RetroCameraLand", "url": SITE},
        "publisher": {"@type": "Organization", "name": "RetroCameraLand",
                      "logo": {"@type": "ImageObject", "url": LOGO}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": BLOG_URL},
            {"@type": "ListItem", "position": 3, "name": title, "item": url},
        ],
    }
    def tag(d): return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
    out = tag(article) + tag(faq) + tag(crumb)
    if howto:
        ho = {
            "@context": "https://schema.org", "@type": "HowTo",
            "name": howto["name"],
            "step": [
                {"@type": "HowToStep", "name": s[0], "text": s[1]}
                for s in howto["steps"]
            ],
        }
        out += tag(ho)
    return "\n" + out

# ══════════════════════════════════════════════════════════════════════════
#  10 BLOG
# ══════════════════════════════════════════════════════════════════════════
POSTS = []

# 1 ── PIL ARTIK URETILMIYORSA ──────────────────────────────────────────────
POSTS.append(dict(
  title="Eski Dijital Kamerada Pil Artık Üretilmiyorsa Ne Yapmalısın? (2026 Rehberi)",
  handle="eski-dijital-kamerada-pil-artik-uretilmiyorsa-ne-yapmalisin",
  keyword="eski dijital kamera pil",
  tags="dijital kamera pil, retro kamera batarya, kamera sarj cihazi, universal batarya, ccd kamera bakim, retrocameraland",
  meta_desc="15-20 yillik dijital kameranin orijinal pili artik uretilmiyor mu? Universal sarj cihazi, ucuncu parti pil guvenligi ve pil omrunu uzatma rehberi.",
  img_kw="vintage digital camera battery charger y2k aesthetic flatlay",
  pin_hero="retro kamera batarya sarj",
  quick="Cogu 2000'ler CCD kompaktin orijinal markali pili artik uretici tarafindan uretilmiyor; ama dogru voltaj/amper degerine sahip universal bir sarj cihaziyla guvenilir ucuncu parti muadil piller sorunsuz kullanilabilir. Onemli olan pili asiri sarj etmemek ve kontaklari duzenli temizlemek.",
  faqs=[
    ("Orijinal pil bulunmazsa kamera artik kullanilamaz mi?",
     "Kullanilir. Neredeyse her markanin (Canon, Sony, Casio, Nikon) eski modelleri icin ucuncu parti muadil piller hala satiliyor; tek sart dogru model/voltaj eslesmesidir. Universal bir sarj cihazi bu ureticiler arasi uyumu tek cihazda cozer."),
    ("Ucuncu parti pil orijinalinden daha mi kotu?",
     "Kalite saticidan saticiya degisir ama guvenilir bir kaynaktan alinan muadil pil, gunluk kullanimda fark yaratmaz. Asil dikkat edilmesi gereken sey kapasite abartisi olmayan, gercekci mAh degeri belirten urunlerdir."),
    ("Universal sarj cihazi her kamerada calisir mi?",
     "Cogu kompakt dijital kameranin lityum-ion pili icin evet, cunku bu cihazlar ayarlanabilir kontak ve voltaj tespitiyle calisir. Yine de sarj cihazini almadan once kameranin pil modelini (govde uzerinde veya pilin uzerinde yazan kod) kontrol etmek en saglikli yontemdir."),
    ("Pili uzun sure kullanmadan saklarsam bozulur mu?",
     "Lityum-ion piller tamamen bos veya tamamen dolu halde uzun sure beklerse kapasite kaybeder. Kamerani aylarca kullanmayacaksan pili yaklasik yari dolulukta cikarip serin, kuru bir yerde saklamak en dogrusudur."),
  ],
  howto=dict(name="Eski dijital kamerada pil sorununu cozme",
    steps=[
      ("Pil kodunu kontrol et", "Pilin veya kameranin alt/yan yuzeyindeki model kodunu not al; universal sarj cihazi alirken bu kod referans olur."),
      ("Kontaklari temizle", "Pil ve kamera uzerindeki metal kontaklari kuru bir bez veya pamukla hafifce sil; oksitlenme cogu 'sarj olmuyor' sikayetinin gercek nedenidir."),
      ("Universal sarj cihazi kullan", "Marka-ozel orijinal sarj cihazi yerine ayarlanabilir kontakli bir universal sarj cihaziyla pili sarj et."),
      ("Guvenilir ucuncu parti pil sec", "Kapasitesi gercekci (abartisiz) belirtilen, kamera modeliyle esleşen bir muadil pil tercih et."),
      ("Dogru sakla", "Kullanmadiginda pili yari dolu halde, serin ve kuru bir yerde sakla; tam bosken uzun sure birakma."),
    ]),
  body="""<p>Bir 2005 model kompaktı raftan indirip actiginda karsina cikan ilk problem genelde sarj degil, pilin kendisidir: kutudaki orijinal pil artik hicbir yerde satilmiyor. <strong>Eski dijital kamerada pil artik uretilmiyorsa</strong> panik etmene gerek yok; bu, retro kamera koleksiyonculugunun en yaygin ve en kolay cozulen sorunlarindan biri.</p>

<h2>Neden Orijinal Piller Artık Bulunmuyor?</h2>
<p>Kamera ureticileri bir modeli piyasadan cektikten belirli bir sure sonra o modele ozel pil uretimini de durdurur. 15-20 yillik bir CCD kompakt icin bu tamamen normaldir; sorun kamerada degil, tedarik zincirinin dogal omrundedir. Ama ayni pil formatini (voltaj, boyut, kapasite araligi) kullanan onlarca marka oldugu icin, "orijinal yok" demek "cozum yok" demek degildir.</p>

<h2>Universal Sarj Cihazı Nasıl Çalışır?</h2>
<p>Universal sarj cihazlari, ayarlanabilir kizaklari ve otomatik voltaj algilamasiyla onlarca farkli lityum-ion pil modelini tek cihazda sarj edebilir. Boylece marka-ozel orijinal sarj aletine bagimli kalmadan, elindeki pili (orijinal ya da muadil) guvenle doldurabilirsin. <a href="https://retrocameraland.com/products/universal-kamera-batarya-sarj-cihaz">Universal Kamera Batarya Şarj Cihazı</a> tam olarak bu ihtiyaci karsilamak icin tasarlanmis pratik bir cozumdur.</p>

<h2>Üçüncü Parti Pil Almadan Önce Kontrol Et</h2>
<p>Muadil pil alirken iki seye dikkat et: model uyumu ve kapasite gerceklik. Kameranin (ornegin <a href="https://retrocameraland.com/products/canon-ixus-160">Canon IXUS 160</a> veya <a href="https://retrocameraland.com/products/sony-cybershot-dsc-w150">Sony Cybershot DSC-W150</a> gibi bir modelin) pil kodunu esas al, "her kameraya uyar" gibi belirsiz aciklamali urunlerden kacin. Gercekci kapasiteli, net model esleşmesi belirtilen pil, kamerani yillarca sorunsuz calistirir.</p>

<h2>Pil Ömrünü Uzatmanın Yolları</h2>
""" + howto_steps([
  ("Tam bos birakma", "Lityum-ion pil, tamamen bosken uzun sure beklerse geri donusu olmayan kapasite kaybi yasayabilir."),
  ("Asiri isidan koru", "Direkt gunes isigi veya sicak arac ici gibi ortamlarda birakmak pil omrunu kisaltir."),
  ("Duzenli kullan", "Nadiren kullanilan kamerayi ayda bir kez calistirip pilini bosaltip doldurmak, pilin 'uyumasini' engeller."),
  ("Kontaklari temiz tut", "Kirli veya oksitlenmis kontaklar sarj sorununu pil arizasi gibi gostere bilir; once temizlik dene."),
]) + """
"""
))

# 2 ── DOLANDIRICILIK KONTROL LISTESI ───────────────────────────────────────
POSTS.append(dict(
  title="İkinci El Dijital Kamera Alırken Dolandırıcılık Kontrol Listesi: Lens ve Sensörü Nasıl Test Edersin",
  handle="ikinci-el-dijital-kamera-alirken-dolandiricilik-kontrol-listesi",
  keyword="ikinci el dijital kamera dolandiricilik",
  tags="ikinci el kamera, kamera dolandiricilik, lens testi, sensor kontrolu, guvenli alisveris, retrocameraland",
  meta_desc="Ikinci el dijital kamera alirken nelere dikkat etmelisin? Lens, sensor ve pil testinden fotograf kalitesine 8 maddelik guvenli satin alma kontrol listesi.",
  img_kw="secondhand digital camera inspection lens test y2k",
  pin_hero="ikinci el dijital kamera kontrol",
  quick="Ikinci el dijital kamera alirken en riskli 3 nokta lens (cizik/kuf), sensor (olu piksel/leke) ve pil-sarj devresidir. Satin almadan once kameranin acilis testini, birkac test cekimini ve kart okuma hizini kontrol etmek, sonradan yasanacak surprizlerin buyuk kismini onler.",
  faqs=[
    ("Ilanda 'calisir durumda' yazmasi yeterli mi?",
     "Yeterli degil. 'Calisir durumda' cok genis bir tanimdir; kamerayi actigi, lens actigi ve birkac fotograf cektigi anlamina gelebilir ama sensor lekesi veya kart okuma sorununu kapsamayabilir. Satin almadan once mutlaka test cekimi goruntusu veya video isteyin."),
    ("Uzaktan (kargoyla) alirken lens/sensor nasil kontrol edilir?",
     "Saticidan duz beyaz bir yuzeye (duvar, gokyuzu) karsi cekilmis bir test fotografi isteyin; leke, karartma veya cizgiler bu fotografta net gorulur. Ayni zamanda kamerayi acip kapatma videosu, lens motorunun duzgun calistigini gosterir."),
    ("Fiyat piyasa ortalamasinin cok altindaysa ne anlama gelir?",
     "Mutlaka dolandiricilik degildir ama dikkatli olmayi gerektirir. Asiri dusuk fiyat genelde ya gizlenen bir arizayi ya da aciklanmamis eksik aksesuari (sarj aleti, kart) isaret eder; saticidan neden bu fiyatta oldugunu acikca sormak makul bir haktir."),
    ("Iade hakkim olmadan kamerayi test edebilir miyim?",
     "Fiziksel bulusarak alisverislerde kamerayi teslim almadan once acip test cekmek tamamen normal bir talep; iyi niyetli hicbir satici buna itiraz etmez. Kargo ile alisveriste ise Turkiye'de mesafeli satis sozlesmesi kapsaminda cayma hakkinin oldugu, kayitli e-ticaret siteleri daha guvenli bir secenektir."),
  ],
  howto=dict(name="Ikinci el dijital kamerada dolandiricilik kontrolu",
    steps=[
      ("Test fotografi iste", "Duz, tek renkli bir yuzeye (duvar/gokyuzu) cekilmis orijinal bir kare iste; sensor lekesi ve karartma burada belirginlesir."),
      ("Acilis-kapanis videosu iste", "Lens motorunun takilmadan, sessizce acilip kapandigini gosteren kisa bir video kontrol icin yeterlidir."),
      ("Kart yuvasini sor", "Hangi kart tipini kabul ettigini ve okuma hizinin normal oldugunu (yavas/hata vermeyen) dogrula."),
      ("Pil ve sarj durumunu netlestir", "Orijinal pil dahil mi, sarj devresi calisiyor mu, kac dakika/kare dayanıyor gibi net sorular sor."),
      ("Fiyati piyasayla karsilastir", "Ayni modelin farkli ilanlardaki fiyat araligina bak; asiri dusuk fiyatin nedenini mutlaka sor."),
    ]),
  body="""<p>Ikinci el pazarindaki en buyuk risk, urunu elinle tutmadan karar vermek zorunda kalmandir. Ozellikle 15-20 yillik bir CCD kompaktta lens ve sensorun gercek durumunu fotograftan anlamak zordur. <strong>Ikinci el dijital kamera alirken dolandiricilik</strong> riskini azaltmanin yolu, sistematik bir kontrol listesi uygulamaktan geciyor.</p>

<h2>Satın Almadan Önce: 8 Maddelik Kontrol Listesi</h2>
<p>Asagidaki maddeleri saticiya sormadan veya kendin kontrol etmeden karar verme; her biri isaretlendikce ne kadar guvende oldugunu gorursun.</p>
""" + checklist([
  "Duz bir yuzeye cekilmis test fotografi istedim (leke/karartma kontrolu)",
  "Lens acilis-kapanis videosu istedim (motor sorunu kontrolu)",
  "Ekranda cizik veya olu piksel olup olmadigini sordum",
  "Kart yuvasinin hangi kart tipini kabul ettigini ogrendim",
  "Pilin orijinal olup olmadigini ve sarj suresini sordum",
  "Aksesuar listesini (kutu, sarj, kablo, kart) netlestirdim",
  "Fiyati benzer ilanlarla karsilastirdim",
  "Saticinin iade/degisim politikasini ogrendim",
]) + """

<h2>Lens Testi Nasıl Yapılır?</h2>
<p>Lens sorunlarinin buyuk kismi (cizik, kuf, gevseklik) ilk bakista fark edilmez. Kamerayi actiginda lens motorunun sessizce, takilmadan cikmasi ve odaklanirken sarsintisiz calismasi iyi bir isarettir. Test fotografinda kenarlarda bulaniklik veya merkeze dogru donuk bir alan varsa, bu genelde lens ici kirlenme veya hizalanma sorununa isaret eder.</p>

<h2>Sensör ve CCD Benek Kontrolü</h2>
<p>Duz, acik renkli bir yuzeye (bos duvar, bulutlu gokyuzu) cekilen bir kare, sensor uzerindeki toz beneklerini veya olu pikselleri en net gosteren testtir. Kucuk toz benekleri normaldir ve genelde sorun yaratmaz; ama sabit, hep ayni yerde cikan koyu leke veya renk degisimi daha ciddi bir sensor sorununu isaret edebilir.</p>

<h2>Güvenilir Bir Satıcının 3 İşareti</h2>
<p>Sorularina acik ve detayli cevap veriyor, test fotografi/video paylasmaktan cekinmiyor ve fiyatin nedenini rahatca aciklayabiliyorsa, guvenilir bir satici profiline uyuyordur. RetroCameraLand'da listelenen her kamera zaten <a href="https://retrocameraland.com/collections/all">satistan once fonksiyon testinden gecer</a> ve kondisyonu seffaf sekilde paylasilir; yani bu kontrol listesini kendin uygulama zahmetine girmeden ayni guveni bulabilirsin.</p>
"""
))

# 3 ── DURUM NOTU REHBERI ────────────────────────────────────────────────────
POSTS.append(dict(
  title="İlanlarda 'Mükemmel / İyi / Orta' Durum Ne Anlama Gelir? Kamera Durum Rehberi",
  handle="kamera-ilanlarinda-durum-notu-ne-anlama-gelir-mukemmel-iyi-orta",
  keyword="kamera durum notu ne demek",
  tags="kamera durum notu, ikinci el kamera kondisyon, kozmetik durum, fonksiyonel durum, retrocameraland",
  meta_desc="Mukemmel, iyi ve orta durum notlari fiyati nasil etkiler? Kozmetik ve fonksiyonel durum arasindaki fark ve hangi notu secmen gerektigini anlatan rehber.",
  img_kw="camera condition grading cosmetic wear y2k digicam",
  pin_hero="kamera durum kondisyon",
  quick="Durum notlari iki farkli seyi olcer: kozmetik durum (govdedeki iz, cizik, boya solmasi) ve fonksiyonel durum (lens, sensor, pil, dugmelerin calisip calismadigi). 'Mukemmel' iki alanda da en ust seviyeyi, 'Orta' ise genelde fonksiyonel olarak saglam ama kozmetik olarak belirgin izli bir kamerayi ifade eder.",
  faqs=[
    ("Kozmetik durum fotograf kalitesini etkiler mi?",
     "Hayir. Govdedeki cizik veya boya solmasi cekilen fotografin kalitesini degistirmez; sadece kameranin gorunumunu etkiler. Fonksiyonel olarak saglam, kozmetik olarak 'orta' bir kamera, gunluk kullanim icin mukemmel bir secim olabilir."),
    ("En dusuk durum notunu almak riskli mi?",
     "Riskli degil, sadece farkli bir profile hitap eder. Butce oncelikliysen ve gorunum senin icin onemli degilse, fonksiyonel testi gecmis dusuk kozmetik notlu bir kamera, ayni modelin 'mukemmel' versiyonuna gore onemli olcude tasarruf saglar."),
    ("Durum notunu kim belirliyor, objektif bir olcum mu?",
     "Cogu zaman saticinin gozlemine dayanir; bu yuzden aciklamalarin detayli ve fotografli olmasi onemlidir. Guvenilir saticilar hem kozmetik hem fonksiyonel durumu ayri ayri, net dille aciklar."),
    ("Ayni durum notuna sahip iki kamera neden farkli fiyatlanabilir?",
     "Marka, model nadirligi, aksesuar tamlik (kutu, sarj, kart) ve talep de fiyati etkiler; durum notu sadece bir bileşendir. Iki 'iyi' durumdaki kamera, farkli modeller oldugunda farkli piyasa degerine sahip olabilir."),
  ],
  body="""<p>Ikinci el kamera ilanlarinda gordugun "Mukemmel", "Iyi" veya "Orta" gibi etiketler ilk bakista basit gorunur ama aslinda iki farkli boyutu bir arada tasir. <strong>Kamera durum notu ne demek</strong> sorusunu dogru anlamak, hem dogru fiyati hem dogru beklentiyi belirlemenin anahtaridir.</p>

<h2>Durum Notları Neden Karışık Görünür?</h2>
<p>Bir kamera kozmetik olarak yipranmis ama fonksiyonel olarak kusursuz olabilir; ya da tam tersi, govdesi parlak ama lens ici tozlu olabilir. Iyi bir durum notu bu ikisini ayirir. Asagidaki gorsel olcek, bu rehberde kullandigimiz tanimlayici bir cerceve sunar; her satici kendi kelimeleriyle ifade etse de mantik hep aynidir.</p>

<h2>Kozmetik Durum vs Fonksiyonel Durum</h2>
""" + gauge_rows([
  ("Mukemmel &mdash; govde", 92, "Belirgin cizik veya iz yok, boyalar orijinal parlakliginda; fonksiyonel olarak da tum ozellikler eksiksiz calisiyor."),
  ("Iyi &mdash; govde", 68, "Kullanimdan kaynaklanan hafif izler, kose asinmasi olabilir; fonksiyonel olarak tam calisir durumda."),
  ("Orta &mdash; govde", 38, "Gozle gorulur cizik/asinma var, boyada solma olabilir; fonksiyonel testten gecmis ama kozmetik olarak en dusuk seviye."),
]) + """

<h2>Hangi Durum Notu Sana Uygun?</h2>
<p>Kamerayi vitrin objesi veya koleksiyon parcasi olarak degil, gunluk cekim araci olarak kullanacaksan, kozmetik durumun senin icin onceligi dusuk olabilir. Bu durumda fonksiyonel testten gecmis, "Orta" kozmetik notlu bir model butceni koruyarak ayni cekim deneyimini sunar. Hediye olarak veya sergilenecek bir parca ariyorsan "Mukemmel" segment daha mantiklidir.</p>

<h2>Fotoğrafta Görmediğin Şeyi Nasıl Sorarsın?</h2>
<p>Iyi bir ilan fotografi bile ekrandaki kucuk cizikleri veya lens ici tozu gostermeyebilir. "Lens ici temiz mi, ekran cizikli mi, tum dugmeler tepki veriyor mu" gibi somut sorular sormak, "durum notu"nun arkasindaki gercek detayi ortaya cikarir. <a href="https://retrocameraland.com/collections/all">RetroCameraLand koleksiyonunda</a> her urunun kozmetik ve fonksiyonel durumu ayri ayri, net dille belirtilir; boylece tahmin yurutmene gerek kalmaz.</p>
"""
))

# 4 ── INSTAGRAMDAN ALMAK GUVENLI MI ────────────────────────────────────────
POSTS.append(dict(
  title="Instagram veya DM Üzerinden İkinci El Kamera Almak Güvenli mi?",
  handle="instagramdan-ikinci-el-kamera-almak-guvenli-mi",
  keyword="instagramdan kamera almak guvenli mi",
  tags="instagram alisveris, dm satis, ikinci el kamera guvenligi, online odeme guvenligi, retrocameraland",
  meta_desc="Instagram DM'den ikinci el dijital kamera almak risk tasir mi? Odeme guvenligi, iade hakki ve saticinin seffafligini degerlendirme rehberi.",
  img_kw="instagram shopping safety online payment y2k camera",
  pin_hero="instagram alisveris guvenlik",
  quick="Instagram DM uzerinden alisveris illa riskli degildir ama e-ticaret sitesine kiyasla iki guvence eksiktir: yasal cayma hakki ve kayitli odeme altyapisi. Havale/EFT ile onceden odeme yapmadan once saticinin gecmis satislarini, yorumlarini ve iletisim seffafligini degerlendirmek onemlidir.",
  faqs=[
    ("Instagram'dan alisveris yapmak yasal olarak korumasiz mi?",
     "Tamamen korumasiz degil ama kayitli bir e-ticaret sitesine gore daha zayif. Turkiye'de mesafeli satis sozlesmesi ve cayma hakki, kayitli isletmelerin e-ticaret siteleri icin daha net isler; bireysel bir Instagram hesabindan alisveriste bu haklarin takibi daha zordur."),
    ("Sadece havale/EFT isteyen satici kirmizi bayrak midir?",
     "Tek basina kesin bir dolandiricilik isareti degildir ama dikkat gerektirir. Kapida odeme, guvenli odeme sistemi (escrow) veya kredi karti gibi alternatif secenek sunmayip sadece onceden havale israr eden bir satici, ek arastirma yapmani gerektirir."),
    ("Satici hesabinin eski ve takipcili olmasi guven verir mi?",
     "Kismen. Uzun sureli, aktif ve gercek etkilesimli bir hesap iyi bir isarettir ama tek basina yeterli degildir; asil onemli olan urunun kondisyonunu seffaf sekilde gosterip iade/degisim konusunda net konusabilmesidir."),
    ("E-ticaret sitesinden almak neden daha guvenli sayilir?",
     "Kayitli bir e-ticaret sitesi fatura keser, mesafeli satis sozlesmesi kapsaminda cayma hakki sunar ve kargo takip numarasiyla teslimat surecini belgeler. Bu ucu bir arada sunmayan bir DM satisinda, sorun cikinca elindeki kanit ve haklar daha sinirli olur."),
  ],
  body="""<p>Y2K estetigi Instagram ve TikTok'ta o kadar buyudu ki, bircok satici artik dogrudan sosyal medya hesabi uzerinden, DM'le kamera satiyor. <strong>Instagramdan kamera almak guvenli mi</strong> sorusunun cevabi "duruma gore" ama neye dikkat etmen gerektigini bilmek riski buyuk olcude azaltir.</p>

<h2>DM Üzerinden Alışverişin Riskleri Nelerdir?</h2>
<p>Sosyal medya DM'i temelde bir alisveris altyapisi degil, bir iletisim aracidir. Fatura kesme, iade sureci, kargo takibi gibi adimlarin hicbiri otomatik degildir; hepsi saticinin insafina ve iyi niyetine dayanir. Bu, her DM satisinin kotu niyetli oldugu anlamina gelmez ama e-ticaret sitesine kiyasla senin elindeki guvenceler azalir.</p>

<h2>Ödeme Güvenliği: Neden Sadece Havale Riskli?</h2>
<p>Havale/EFT geri donusu olmayan bir odeme yontemidir; para gonderildikten sonra urun gelmezse iadesi neredeyse imkansizdir. Kredi karti veya güvenli odeme sistemi uzerinden yapilan odemelerde ise banka/odeme saglayicisi tarafinda itiraz ve iade mekanizmalari calisir. Mumkunse bu tur bir odeme secenegi sunan saticilari tercih etmek akillica bir onlemdir.</p>

<h2>İade ve Garanti Hakkın Var mı?</h2>
<p>Kayitli bir e-ticaret sitesinden alisveriste Turkiye'de mesafeli satis sozlesmesi kapsaminda belirli bir cayma hakkin bulunur; bu hak faturali, izlenebilir bir islemi gerektirir. Bireysel bir sosyal medya hesabindan yapilan satiste bu surecin isleyisi tamamen saticinin insafina kalir; onceden "sorun olursa ne yapariz" sorusunu acikca sormak sart.</p>

<h2>Şeffaf Bir Satıcının 5 İşareti</h2>
<p>Urunun gercek fotograf/videosunu paylasiyor, fiyat ve kondisyon konusunda net konusuyor, iletisim bilgileri (telefon, e-posta, adres) dogrulanabilir, gecmis satislarina dair referans gosterebiliyor ve odeme konusunda esneklik sunuyorsa guvenilir bir profile yakindir. Bunlarin hicbirini saglamiyorsa, o satin alma icin bir kez daha dusunmek makuldur.</p>

<h2>E-ticaret Sitesi vs Sosyal Medya Hesabı</h2>
<p>Ikisi de mesru satis kanallari olabilir ama sundugu guvenceler farklidir. <a href="https://retrocameraland.com/collections/all">Kayitli bir e-ticaret sitesinde</a> fatura, cayma hakki, kargo takibi ve seffaf durum bilgisi bir arada gelir; bu da ozellikle kargo ile, yuz yuze gormeden yapilan alisverislerde onemli bir fark yaratir.</p>
"""
))

# 5 ── LENS ERROR ────────────────────────────────────────────────────────────
POSTS.append(dict(
  title="'Lens Error, Restart Camera' ve Benzeri Arıza Kodları: Evde Denenebilecek Çözümler",
  handle="lens-error-restart-camera-hatasi-ve-benzeri-ariza-kodlari-cozumleri",
  keyword="lens error restart camera hatasi",
  tags="lens error, kamera ariza kodu, canon powershot hata, kamera tamiri, retrocameraland",
  meta_desc="Kamerada Lens Error, Restart Camera yaziyor mu? Evde deneyebilecegin 5 basit adim ve ne zaman profesyonel destege ihtiyac oldugunu anlatan rehber.",
  img_kw="camera lens error message troubleshooting compact digicam",
  pin_hero="kamera lens error hata",
  quick="'Lens Error, Restart Camera' mesaji genelde lens mekanizmasinin acilirken bir engelle karsilasmasindan (toz, hafif darbe, kum) kaynaklanir. Pil cikar-tak ve kart cikar-tak gibi basit adimlar sorunun yaklasik yarisini cozer; hata devam ederse lens motorunda fiziksel bir sorun var demektir ve servis gerekir.",
  faqs=[
    ("Bu hata sadece Canon kameralarda mi cikar?",
     "Hayir, ama Canon PowerShot serisinde sikca goruldugu icin bu isimle en cok anilan marka odur. Ayni tur hata, lens mekanizmasi disari cikan hemen her kompakt dijital kamerada (Sony, Nikon, Casio dahil) farkli mesajlarla ortaya cikabilir."),
    ("Pil cikar-tak yontemi neden ise yarar?",
     "Bu yontem kameranin ic devresini sifirlar ve lens motorunu bastan baslatir. Hata gecici bir yazilim/motor senkronizasyon sorunundan kaynaklaniyorsa bu basit reset cogu zaman yeterli olur."),
    ("Lens icine kum veya toz kacmissa evde temizlenebilir mi?",
     "Yuzeysel toz icin lens cevresini yumusak bir fircayla temizlemek denenebilir ama lens mekanizmasinin icini acmak riskli ve garantiyi bozan bir islemdir. Kum/toz lens disliye kadar ilerlediyse profesyonel temizlik gerekir."),
    ("Hata her seferinde farkli bir kare numarasiyla cikiyor, bu ne anlama gelir?",
     "Bazi modeller hata koduyla birlikte bir referans numarasi gosterir; bu numara servis teknisyeni icin arizanin turunu (motor, sensor, odaklama) tanimlamada yardimci olur. Servise goturmeden once bu numarayi not almak faydali olur."),
  ],
  howto=dict(name="Lens Error hatasini evde cozme adimlari",
    steps=[
      ("Kamerayi kapat ve pili cikar", "Kamerayi kapattiktan sonra pili 30 saniye cikar, ardindan tekrar tak; bu basit reset hatalarin buyuk kismini cozer."),
      ("Hafiza kartini cikar-tak", "Kart ile ilgili bir okuma hatasi bazen lens hatasi gibi gorunebilir; karti cikarip temiz kontaklarla tekrar tak."),
      ("Lens cevresini temizle", "Lens etrafindaki gorunur tozu, kum tanesini yumusak bir fircayla nazikce temizle; lens mekanizmasini zorlama."),
      ("Duz ve sabit zeminde tekrar dene", "Kamerayi duz bir yuzeye koyup ac; egik veya bastirilarak tutulan kamerada lens motoru daha zor calisir."),
      ("Hala cozulmuyorsa servise goturme zamanidir", "Yukaridaki adimlar isi ise yaramadiysa sorun fiziksel bir hizalama veya motor arizasidir; kendin acmaya calismak yerine servise danis."),
    ]),
  body="""<p>Kamerani actiginda lens disari cikmiyor, ekranda "Lens Error, Restart Camera" ya da benzer bir uyari beliriyorsa, ilk tepki genelde panik olur. Oysa <strong>lens error restart camera hatasi</strong> ikinci el CCD kompaktlarda oldukca yaygin bir durum ve cogu zaman evde, aletsiz cozulebiliyor.</p>

<h2>'Lens Error' Hatası Neden Çıkar?</h2>
<p>Bu hata, lens mekanizmasi acilirken beklenen konuma ulasamadiginda tetiklenir. En yaygin nedenler: lens disari cikarken bir engelle (parmak, kilif, kum tanesi) karsilasmasi, kamerayi acikken dusurmek/carpmak, ya da uzun sure kullanilmayan bir kamerada mekanizmanin hafifce sikismasi. Cogu durumda bu, kalici bir ariza degil, gecici bir senkronizasyon sorunudur.</p>

<h2>Evde Deneyebileceğin 5 Adım</h2>
""" + howto_steps([
  ("Kamerayi kapat ve pili cikar", "Kamerayi kapattiktan sonra pili 30 saniye cikar, ardindan tekrar tak; bu basit reset hatalarin buyuk kismini cozer."),
  ("Hafiza kartini cikar-tak", "Kart ile ilgili bir okuma hatasi bazen lens hatasi gibi gorunebilir; karti cikarip temiz kontaklarla tekrar tak."),
  ("Lens cevresini temizle", "Lens etrafindaki gorunur tozu, kum tanesini yumusak bir fircayla nazikce temizle; lens mekanizmasini zorlama."),
  ("Duz ve sabit zeminde tekrar dene", "Kamerayi duz bir yuzeye koyup ac; egik veya bastirilarak tutulan kamerada lens motoru daha zor calisir."),
  ("Hala cozulmuyorsa servise goturme zamanidir", "Yukaridaki adimlar ise yaramadiysa sorun fiziksel bir hizalama veya motor arizasidir; kendin acmaya calismak yerine servise danis."),
]) + f"""

<h2>Denenmemesi Gereken Yöntem: Kameraya Vurmak</h2>
<p>Internette sikca gordugun "kamerayi avucuna vur, lens yerine oturur" tarzi yontemler bazen kisa vadede ise yarar gibi gorunse de, aslinda lens hizalamasini daha da bozma riski tasir. Bu yontemi denemeden once mutlaka yukaridaki guvenli adimlari sirayla dene; pil/kart cikar-tak ve temizlik cogu zaman yeterlidir.</p>

<h2>Ne Zaman Servise Götürmelisin?</h2>
<p>Yukaridaki adimlardan sonra hata devam ediyorsa, ekranda tekrarlayan bir hata kodu goruyorsan ya da lens gozle gorulur sekilde egri/sikismis duruyorsa, sorun artik yazilimsal degil fiziksel bir hizalama veya motor arizasidir. Bu noktada kendin mudahale etmek yerine profesyonel bir servise danismak, kamerayi daha fazla zarar gormekten korur. <a href="https://retrocameraland.com/products/canon-powershot-a480">Canon PowerShot A480</a> veya <a href="https://retrocameraland.com/products/canon-powershot-sd400">Canon PowerShot SD400</a> gibi modeller alirken bu tur bir gecmisi olup olmadigini saticiya sormak da onleyici bir adimdir; RetroCameraLand'daki tum modeller zaten bu testten gecirilerek satisa sunulur.</p>
"""
))

# 6 ── DIGICAM VS FILM VS INSTAX VS TELEFON ─────────────────────────────────
POSTS.append(dict(
  title="Digicam vs Film Kamera vs Instax vs Telefon: Hangisi Ne Zaman Kullanılır?",
  handle="digicam-vs-film-kamera-vs-instax-vs-telefon-hangisi-ne-zaman",
  keyword="digicam vs film kamera vs telefon",
  tags="digicam karsilastirma, film kamera, instax, telefon kamera, hangi kamera, retrocameraland",
  meta_desc="Digicam, film kamera, instax ve telefon arasindaki fark ne? Maliyet, hiz, estetik ve tasinabilirlik acisindan 4 aracin karsilastirmali rehberi.",
  img_kw="digicam film camera instax phone comparison flatlay y2k",
  pin_hero="digicam film instax karsilastirma",
  quick="Kisa cevap: telefon gunluk ve anlik cekim icin en pratik, film kamera 'yavaslatilmis' ve bilincli cekim deneyimi icin, instax aninda fiziksel baski icin, digicam ise ikisinin ortasinda; dusuk maliyetli, sinirsiz kare cekebilen ama yine de karakterli/filmsi bir gorunum sunan secenektir.",
  faqs=[
    ("Digicam mi film kamera mi daha uygun maliyetli?",
     "Digicam belirgin sekilde daha uygun maliyetlidir; bir kez kamera ve hafiza karti aldiktan sonra kare basi ek maliyet yoktur. Film kamerada ise her rulo film ve banyo islemi ayri bir maliyet olusturur, bu da uzun vadede toplam maliyeti yukseltir."),
    ("Instax neden fotografcilar arasinda hala populer?",
     "Instax'in en buyuk avantaji ani, fiziksel bir cikti vermesidir; cektigin karе saniyeler icinde elinde somut bir fotografa donusur. Digicam ve telefon dijital kaldigi icin bu ani fiziksel tatmini saglayamaz."),
    ("Sosyal medya icin hangisi daha cok one cikiyor?",
     "Su anda TikTok ve Instagram'da digicam estetigi guclu bir trend; cunku telefon karelerinin arasinda hemen fark ediliyor. Film kamera de benzer bir ilgi goruyor ama banyo/tarama sureci paylasima kadar zaman kaybettirebiliyor."),
    ("Dorduyu birlikte kullanmak mantikli mi?",
     "Cok mantikli olabilir. Bircok icerik ureticisi gunluk anlar icin telefonu, ozel gunler icin digicami, bilincli/sanatsal cekimler icin film kamerayi ve aninda hediye edilecek kareler icin instax'i bir arada kullaniyor; her aracin kendine ozgu bir yeri var."),
  ],
  body="""<p>Dört farklı aracı aynı çizgide karşılaştırmak zor görünebilir çünkü aslında dördü de farklı bir ihtiyaca cevap veriyor. <strong>Digicam vs film kamera vs telefon</strong> sorusu genelde "hangisi daha iyi" degil, "hangisi ne zaman daha dogru" sorusuna donusmeli.</p>

<h2>Dördünü Aynı Çizgide Karşılaştırmak Neden Zor?</h2>
<p>Telefon teknik mukemmellik ve aninda paylasim sunar; film kamera yavaslik ve bilincli cekim deneyimi sunar; instax fiziksel, aninda cikti sunar; digicam ise bu ucunun arasinda, dusuk maliyetli ama karakterli bir orta yol sunar. Dogru arac, "en iyi" degil "o an ihtiyacina en uygun" olandir.</p>

<h2>Hızlı Karşılaştırma</h2>
""" + tabs([
  ("Maliyet", "<p><strong>Telefon:</strong> Kamerayla birlikte gelir, ek maliyet yok. <strong>Digicam:</strong> Tek seferlik kamera+kart maliyeti, sonrasi ucretsiz. <strong>Instax:</strong> Her karede film maliyeti (surekli tekrar eden gider). <strong>Film kamera:</strong> Rulo + banyo maliyeti en yuksek toplam maliyeti olusturur.</p>"),
  ("Hiz / Aninda Sonuc", "<p><strong>Telefon:</strong> Aninda ekranda, aninda paylasim. <strong>Digicam:</strong> Aninda ekranda, aktarim gerektirir. <strong>Instax:</strong> Saniyeler icinde fiziksel baski. <strong>Film kamera:</strong> Banyo/tarama surecine kadar sonucu goremezsin.</p>"),
  ("Estetik / Doku", "<p><strong>Telefon:</strong> Keskin, puruzsuz, 'mukemmel' dijital gorunum. <strong>Digicam:</strong> CCD sensor karakteri, hafif gren, sicak Y2K tonlari. <strong>Instax:</strong> Klasik anlik-fotograf dokusu, hafif belirsizlik. <strong>Film kamera:</strong> En derin ton gecisleri ve filmsi gren, kullanilan filme gore degisir.</p>"),
  ("Taşınabilirlik", "<p><strong>Telefon:</strong> Zaten cebinde, ek agirlik yok. <strong>Digicam:</strong> Kucuk ve hafif, cebe sigar. <strong>Instax:</strong> Biraz daha hacimli, film kutusuyla birlikte tasinir. <strong>Film kamera:</strong> Modeline gore degisir, genelde en hacimli secenektir.</p>"),
]) + """

<h2>Hangi An Hangi Aracı İster?</h2>
<p>Gunluk, plansiz anlar icin telefon en pratigi; parti, konser veya gece sokagi icin <a href="https://retrocameraland.com/products/canon-ixus-i">bir digicam</a> hem karakter hem kolaylik sunar; dogum gunu veya arkadas bulusmasinda hemen elden ele gezecek fiziksel bir hatira icin instax dogru secim; bilinçli, planli bir fotograf gezisi icin ise film kameranin yavas ritmi en cok tatmin veren deneyimi verir.</p>

<h2>Neden Çoğu Kişi Digicamı İlk Tercih Ediyor?</h2>
<p>Digicam, dusuk giris maliyeti, sinirsiz kare cekebilme ve yine de telefon'dan belirgin sekilde farkli bir estetik sunmasi nedeniyle bu dorduzlu arasinda en "pratik giris noktasi" olarak one cikiyor. <a href="https://retrocameraland.com/collections/all">RetroCameraLand koleksiyonunda</a> farkli marka ve fiyat araliklarinda test edilmis modelleri inceleyebilirsin.</p>
"""
))

# 7 ── CCD FOTOGRAF DUZENLEME WORKFLOW ──────────────────────────────────────
POSTS.append(dict(
  title="CCD Dijital Kamera Fotoğraflarını Düzenleme: Basit Workflow Rehberi",
  handle="ccd-fotograflari-duzenleme-basit-workflow-rehberi",
  keyword="ccd fotograf duzenleme",
  tags="ccd fotograf duzenleme, digicam workflow, fotograf aktarma, retro fotograf duzenleme, retrocameraland",
  meta_desc="CCD dijital kameranin JPEG fotograflarini nasil duzenlersin? Aktarmadan renk ayarina 5 adimlik basit workflow ve hangi ayarlara dokunmaman gerektigi rehberi.",
  img_kw="editing ccd digicam photos workflow laptop y2k aesthetic",
  pin_hero="ccd fotograf duzenleme workflow",
  quick="CCD kameralarin cogu sadece JPEG kaydeder, yani RAW gibi genis duzenleme payi yoktur. Dogru workflow; fotograflari kart okuyucuyla aktarmak, orijinallerini yedeklemek ve sonra sadece kontrast/beyaz dengesi gibi hafif ayarlarla sensorun kendi karakterini korumaktir; asiri duzenleme CCD'nin ozgun dokusunu yok eder.",
  faqs=[
    ("CCD kameralarin cogu RAW cekebilir mi?",
     "Hayir, 2000'ler donemi tuketici CCD kompaktlarinin buyuk cogunlugu sadece JPEG formatinda kaydeder. Bu, duzenleme esnekligini sinirlar ama ayni zamanda CCD'nin kendine ozgu renk isleme karakterini de fotografta korur."),
    ("Telefonla kart okumak yerine neden kart okuyucu kullanmaliyim?",
     "Kart okuyucu, dogrudan ve kayipsiz bir aktarim saglar; bazi telefon/kablo kombinasyonlari dosya sikistirma veya format donusumu yapabilir. Bir <a href='https://retrocameraland.com/products/usb-c-3-in-1-kart-okuyucu-sd-microsd'>USB-C kart okuyucu</a> ile aktarilan fotograf, kameranin urettigi orijinal dosyanin birebir aynisidir."),
    ("Duzenleme yaparken hangi ayarlara dokunmamaliyim?",
     "Asiri keskinlestirme (sharpening) ve agresif gurultu azaltma (noise reduction) CCD'nin karakteristik gren dokusunu ve yumusak gecislerini yok eder. Bu iki ayari mumkun oldugunca minimumda tutmak, fotografin 'digicam hissini' korur."),
    ("Duzenlemeden once dosyalarimi neden yedeklemeliyim?",
     "JPEG uzerinde yapilan duzenlemeler geri donusu zor olabilir; orijinal dosyayi kaybedersen o kareyi bir daha asla ayni haliyle goremezsin. Aktarim sonrasi ilk is olarak orijinalleri ayri bir klasorde yedeklemek, deneme-yanilma yapabilmeni saglar."),
  ],
  howto=dict(name="CCD fotograflarini duzenleme workflow'u",
    steps=[
      ("Hafiza kartini cikar", "Cekim bittikten sonra kamerayi kapat ve hafiza kartini nazikce cikar."),
      ("Kart okuyucuyla aktar", "Kart okuyucu araciligiyla fotograflari bilgisayara veya telefona kayipsiz sekilde aktar."),
      ("Orijinalleri yedekle", "Aktarilan orijinal JPEG dosyalarini ayri bir klasorde yedekle, uzerlerinde direkt calisma."),
      ("Hafif duzenleme yap", "Kontrast, beyaz dengesi ve pozlama gibi temel ayarlarda kucuk oynamalar yap; keskinlestirme ve gurultu azaltmayi minimumda tut."),
      ("Disari aktar ve paylas", "Duzenlenmis versiyonu ayri bir dosya olarak disari aktar, orijinali koru."),
    ]),
  body="""<p>CCD sensorlu bir dijital kamerayla cekim yaptiktan sonra karsina cikan soru genelde su olur: bu fotograflari nasil duzenlemeliyim ki o ozel dokuyu bozmayayim? <strong>CCD fotograf duzenleme</strong> aslinda "az ile cok yapmak" prensibine dayanir.</p>

<h2>Neden CCD Fotoğrafları 'Az' Düzenlenmeli?</h2>
<p>CCD sensorlerin cogu, modern CMOS sensorlere gore daha sinirli dinamik aralikta ama daha belirgin bir renk karakterinde JPEG uretir. Bu dosyalar zaten kendi icinde bir "isleme" sureciyle olusturulmustur; ustune agresif duzenleme eklemek, o kendine ozgu sicakligi ve dokuyu genelde bozar, guclendirmez.</p>

<h2>Fotoğrafları Kameradan Aktarma</h2>
<p>Ilk adim dogru aktarim. Kamerayi dogrudan bilgisayara kabloyla baglamak yerine bir kart okuyucu kullanmak, hem daha hizlidir hem de dosyalarin orijinal halini korur. <a href="https://retrocameraland.com/products/y2k-digicam-fotograf-video-aktarici-xd-cf-sd-ms-destekli-all-in-one-kart-okuyucu">Y2K Digicam Fotoğraf/Video Aktarıcı</a> gibi coklu format destekleyen bir kart okuyucu, farkli marka kameralarin (xD, CF, SD, MS) kartlarini tek cihazdan aktarmani saglar.</p>

<h2>5 Adımda Basit Düzenleme Workflow'u</h2>
""" + howto_steps([
  ("Hafiza kartini cikar", "Cekim bittikten sonra kamerayi kapat ve hafiza kartini nazikce cikar."),
  ("Kart okuyucuyla aktar", "Kart okuyucu araciligiyla fotograflari bilgisayara veya telefona kayipsiz sekilde aktar."),
  ("Orijinalleri yedekle", "Aktarilan orijinal JPEG dosyalarini ayri bir klasorde yedekle, uzerlerinde direkt calisma."),
  ("Hafif duzenleme yap", "Kontrast, beyaz dengesi ve pozlama gibi temel ayarlarda kucuk oynamalar yap; keskinlestirme ve gurultu azaltmayi minimumda tut."),
  ("Disari aktar ve paylas", "Duzenlenmis versiyonu ayri bir dosya olarak disari aktar, orijinali koru."),
]) + """

<h2>Dokunmaman Gereken 2 Ayar</h2>
<p>Asiri keskinlestirme (sharpening), CCD'nin yumusak gecislerini yapay ve sert gosterir; agresif gurultu azaltma (noise reduction) ise fotografin karakteristik greni'ni siler ve sonuc plastik bir gorunum alir. Bu iki ayari dokunmadan veya cok hafif birakmak, "digicam hissini" korumanin en basit yoludur.</p>
"""
))

# 8 ── DUGUN VE ETKINLIKLERDE DIGICAM ────────────────────────────────────────
POSTS.append(dict(
  title="Düğün ve Etkinliklerde Digicam Kullanımı: Fotoğrafçılar İçin Pratik Rehber",
  handle="dugun-ve-etkinliklerde-digicam-kullanimi-fotografcilar-icin-rehber",
  keyword="dugunde digicam kullanimi",
  tags="dugun fotografciligi, etkinlik kamerasi, digicam dugun, misafir kamerasi, retrocameraland",
  meta_desc="Dugun ve etkinliklerde misafir masasina digicam koymak neden trend? Dayanikli modeller, yedek pil stratejisi ve pratik kurulum onerileri rehberi.",
  img_kw="wedding event digicam guest table y2k disposable style",
  pin_hero="dugun digicam misafir kamerasi",
  quick="Dugun ve etkinliklerde digicam kullaniminin iki yaygin yolu var: misafir masalarina birakilan 'herkes cekebilsin' kamerasi ve profesyonel fotografcinin ana ekipmana ek olarak kullandigi ikinci, karakterli kamera. Her iki kullanimda da dayanikli, guclu flasli ve pil/kart yedegi hazir bir kurulum onemlidir.",
  faqs=[
    ("Digicam tek kullanimlik fotograf makinesinin yerini mi aliyor?",
     "Buyuk olcude evet; digicam tekrar kullanilabilir olmasi ve daha yuksek goruntu kalitesi sunmasi nedeniyle tek kullanimlik film makinelerine tercih ediliyor. Misafirlerin cektigi kareler kamerada kalir, dugun sonrasi toplu sekilde aktarilabilir."),
    ("Misafir masasina birakilan kamerada pil bitmesi sorun olur mu?",
     "Uzun bir etkinlikte pil bitmesi olasi bir durumdur; bu yuzden yedek, onceden sarj edilmis bir pil bulundurmak ve gerekirse etkinlik ortasinda kamerayi kontrol edip pili degistirmek pratik bir cozumdur."),
    ("Profesyonel fotografcilar neden ana ekipmanlarina ek digicam kullaniyor?",
     "Digicamin verdigi filmsi, spontane doku, profesyonel kameranin kusursuz ama bazen 'soguk' hissedilen karelerine sicak bir kontrast olusturuyor. Bircok fotografci bu yuzden kutlama anlarinda ek olarak digicam ile de kare aliyor."),
    ("Birden fazla misafir ayni kamerayi kullanacaksa hangi ozellik onemli?",
     "Basit ve sezgisel bir arayuz, guclu otomatik flas ve genis hafiza karti kapasitesi en onemli ucludur. Karmasik menu ayari gerektirmeyen, tek tusla cekim yapan modeller misafirler icin en pratigidir."),
  ],
  body="""<p>Dugun masalarinda tek kullanimlik fotograf makinesinin yerini artik tekrar kullanilabilir digicamlar aliyor. <strong>Dugunde digicam kullanimi</strong>, hem misafirlerin kendi acisindan anlari yakalamasina hem de profesyonel fotografcinin ana kareye ek bir doku katmasina imkan taniyor.</p>

<h2>Düğünlerde Digicam Trendi Neden Bu Kadar Büyüdü?</h2>
<p>Telefon fotograflarinin hepsi birbirine benzedigi icin, misafirlerin cektigi digicam kareleri dugun albumune beklenmedik, samimi ve karakterli bir katman ekliyor. Ayrica tek kullanimlik film makinesinin aksine, digicam ekrandan aninda kontrol edilebiliyor ve tekrar tekrar kullanilabiliyor; bu da hem cift hem de organizasyon acisindan daha surdurulebilir bir secim.</p>

<h2>Misafir Masası İçin Dayanıklı Modeller</h2>
<p>Misafir masasina birakilacak bir kamerada en onemli ozellikler basitlik ve guclu flastir; herkesin karmasik ayarlarla ugrasmadan tek tusla cekim yapabilmesi gerekir. <a href="https://retrocameraland.com/products/canon-ixus-i">Canon IXUS i</a> ince govdesi ve hizli flasiyla, <a href="https://retrocameraland.com/products/sony-cybershot-dsc-w150">Sony Cybershot DSC-W150</a> ise sezgisel otomatik moduyla bu kullanim icin uygun secenekler.</p>

<h2>Profesyonel Fotoğrafçının İkinci Kamerası Olarak Digicam</h2>
<p>Profesyonel ekipmanin yaninda tasinan bir digicam, dugunun daha rahat, kurgusuz anlarini yakalamak icin kullanilir; damat hazirligi, kokteyl saatindeki sohbetler, gece pistindeki flasli kareler gibi. Genis zoomlu <a href="https://retrocameraland.com/products/panasonic-lumix-dc-tz91">Panasonic Lumix DC-TZ91</a>, hem detay hem genel plan cekebildigi icin bu ikinci kamera rolune uygun bir secim.</p>

<h2>Etkinlik İçin Pil ve Kart Stratejisi</h2>
<p>Uzun suren bir etkinlikte pilin veya kartin dolmasi kacinilmazdir; onceden sarj edilmis yedek pil ve bos, yuksek kapasiteli bir <a href="https://retrocameraland.com/products/sandisk-8gb-sdhc-class4-hafiza-karti">SanDisk 8GB SDHC hafiza karti</a> bulundurmak, etkinligin ortasinda "kart doldu" krizini onler. Kamerayi darbe ve nemden korumak icin <a href="https://retrocameraland.com/products/boona-profesyonel-kamera-cantasi-waterproof">Boona su gecirmez kamera cantasi</a> da tasima sirasinda ek guvence saglar.</p>
"""
))

# 9 ── LENS KUFU ─────────────────────────────────────────────────────────────
POSTS.append(dict(
  title="Kamera Lensinde Küf veya Buğu Nasıl Anlaşılır? Temizlik ve Önleme Rehberi",
  handle="kamera-lensinde-kuf-veya-bugu-nasil-anlasilir-temizlik-onleme-rehberi",
  keyword="kamera lensinde kuf",
  tags="lens kufu, lens temizligi, kamera nem, kamera bakimi, ccd lens, retrocameraland",
  meta_desc="Kamera lensinde bulaniklik veya ag gibi izler mi var? Lens kufunu evde anlama, guvenli temizlik sinirlari ve nem/kufu onleme rehberi.",
  img_kw="camera lens mold haze inspection macro y2k digicam",
  pin_hero="kamera lens kuf nem",
  quick="Lens kufu genelde lens yuzeyinde ince, ag benzeri veya tuylu bir desen olarak; lens buğusu ise daha genel, sisli bir bulaniklik olarak kendini gosterir. Yuzeysel toz evde yumusak bir bezle temizlenebilir ama lens ici kuf, mercekler arasina ilerlemisse ev kosullarinda guvenle mudahale edilemez ve profesyonel temizlik gerektirir.",
  faqs=[
    ("Lens kufu ile toz arasindaki fark nedir?",
     "Toz genelde kucuk, dagitilmis noktalar seklinde gorunur ve fotograf kalitesini cok az etkiler. Kuf ise ag benzeri, dallanan bir desen olusturur ve zamanla buyuyerek fotograflarda belirgin bulaniklik ve kontrast kaybina yol acar."),
    ("Kufu evde kendim temizleyebilir miyim?",
     "Lens yuzeyindeki hafif tozu yumusak bir fircayla temizleyebilirsin ama kuf mercekler arasina (lens grubunun ic kismina) ilerlediyse, kamerayi acmadan mudahale etmen mumkun degildir. Ic kismi acmaya calismak, hizalamayi bozma riski tasir."),
    ("Kuflu bir lens kamerayi tamamen kullanilmaz mi yapar?",
     "Hafif ve kucuk bir kuf lekesi cogu zaman fotograf kalitesini az etkiler ve kamera kullanilabilir kalir. Ancak kuf zamanla buyudukce kontrast kaybi ve bulaniklik artar; bu yuzden erken fark edildiginde mudahale etmek onemlidir."),
    ("Nem oraninin dusuk oldugu bir evde bile kuf olusabilir mi?",
     "Evet, cunku kufun asil tetikleyicisi kamera ic hacmindeki hapsolmus nemdir; kamera uzun sure kapali bir kutu veya cantada, nemli havayla birlikte kapali kalirsa evin genel nem orani dusuk olsa bile lens icinde kuf olusabilir."),
  ],
  howto=dict(name="Lens kufunu anlama ve onleme",
    steps=[
      ("Isik testi yap", "Lensi guclu bir isik kaynagina (telefon feneri) tutup mercegin icine bak; ag benzeri veya tuylu desenler kufu, sisli genel bulaniklik ise buguyu isaret eder."),
      ("Yuzeysel tozu temizle", "Lens disindaki tozu yumusak, tuysuz bir bezle nazikce sil; ic kismi acmaya calisma."),
      ("Nem alici kullan", "Kamerayi sakladigin cantaya veya kutuya kucuk bir nem alici paket koymak, ic hacimde nem birikmesini engeller."),
      ("Duzenli havalandir", "Kamerani uzun sure kapali tutmak yerine ara sira acip disari cikarmak, ic hacimdeki nemin birikmesini onler."),
      ("Ciddi kuf durumunda servise danis", "Kuf mercekler arasina ilerlediyse kendin mudahale etmek yerine profesyonel lens temizligi yapan bir servise goturmelisin."),
    ]),
  body="""<p>Ikinci el bir kamera aldiginda veya uzun sure kullanmadigin bir kamerayi raftan indirdiginde, lensin icinde beklenmedik bir bulaniklik gorebilirsin. <strong>Kamera lensinde kuf</strong> ozellikle nemli ortamlarda saklanan eski kameralarda oldukca yaygin bir sorundur ama her zaman kamerayi kullanilmaz hale getirmez.</p>

<h2>Lens Küfü Nasıl Oluşur?</h2>
<p>Kuf, kamera icindeki hapsolmus nem ve organik parcaciklarin (toz, parmak izi yagi) bir araya gelmesiyle olusur. Ozellikle nemli iklimlerde, kapali bir cantada uzun sure saklanan kameralar bu ortami sunar. Zamanla mercek yuzeyinde ag benzeri, dallanan bir desen olarak buyur.</p>

<h2>Evde Nasıl Anlarsın?</h2>
<p>Lensi guclu bir isik kaynagina (telefon feneri gibi) tutup icine dikkatlice baktiginda, ag benzeri veya tuylu bir desen goruyorsan bu kuftur. Daha genel, sisli ve homojen bir bulaniklik ise genelde nem/buğu kaynaklidir ve kamera kuru bir ortama alindiginda kendiliginden gecebilir.</p>

<h2>Kendin Temizleyebileceğin Sınır Nerede Biter?</h2>
<p>Lens disindaki, gorunen yuzeydeki hafif tozu yumusak bir bezle silmek guvenlidir. Ama kuf mercek gruplari arasina, kameranin ic kismina ilerlediyse, evde kendi baslarina acmaya calismak hem hizalamayi bozma hem de daha fazla nem/kir sokma riski tasir. Bu noktada is profesyonel bir lens temizlik servisine kalir.</p>

<h2>Nem ve Küfü Önlemenin Yolları</h2>
""" + howto_steps([
  ("Isik testi yap", "Lensi guclu bir isik kaynagina (telefon feneri) tutup mercegin icine bak; ag benzeri veya tuylu desenler kufu, sisli genel bulaniklik ise buguyu isaret eder."),
  ("Nem alici kullan", "Kamerayi sakladigin cantaya veya kutuya kucuk bir nem alici paket koymak, ic hacimde nem birikmesini engeller."),
  ("Duzenli havalandir", "Kamerani uzun sure kapali tutmak yerine ara sira acip disari cikarmak, ic hacimdeki nemin birikmesini onler."),
  ("Uygun cantada sakla", "Nem gecirmez, havalandirmali bir kamera cantasi kullanmak, uzun donem saklamada en etkili onlemlerden biridir."),
]) + """
<p>Uzun sureli saklama veya tasima icin <a href="https://retrocameraland.com/products/boona-profesyonel-kamera-cantasi-waterproof">Boona su gecirmez kamera cantasi</a> gibi nem gecirmez bir coruma kullanmak, hem kuf hem nem riskini onemli olcude azaltir. RetroCameraLand'da satisa sunulan tum <a href="https://retrocameraland.com/collections/all">modeller</a> zaten satis oncesi lens ve sensor kontrolunden gecirilir.</p>
"""
))

# 10 ── ISTANBUL DISINDA SEHIR REHBERI ──────────────────────────────────────
POSTS.append(dict(
  title="İstanbul Dışında İkinci El Retro Kamera: Ankara, İzmir, Bursa Rehberi",
  handle="istanbul-disinda-ikinci-el-retro-kamera-ankara-izmir-bursa-rehberi",
  keyword="ankara izmir bursa ikinci el retro kamera",
  tags="ankara retro kamera, izmir retro kamera, bursa retro kamera, turkiye kargo, retrocameraland",
  meta_desc="Ankara, Izmir veya Bursa'da yasiyorsan ikinci el retro dijital kamerayi nereden, nasil guvenle alirsin? Kargo ile alisveris ve sehir bazli rehber.",
  img_kw="turkey city retro digicam shopping y2k aesthetic",
  pin_hero="ankara izmir bursa retro kamera",
  quick="Ankara, Izmir, Bursa gibi buyuk sehirlerde niş retro/Y2K dijital kamera secenegi Istanbul'a gore daha sinirlidir; ama kargo ile alisveris, test edilmis ve garantili urun sunan bir e-ticaret sitesinden alindiginda bu farki tamamen ortadan kaldirir. Onemli olan saticinin fonksiyon testi ve iade politikasidir, sehir degil.",
  faqs=[
    ("Ankara veya Izmir'de fiziksel retro kamera magazasi var mi?",
     "Niş retro/Y2K dijital kamera segmentinde fiziksel magaza secenekleri sehirlere gore cok sinirlidir ve genelde Istanbul'da yogunlasir. Bu yuzden buyuk sehirler disindaki alicilarin buyuk cogunlugu kargo ile online alisverise yoneliyor."),
    ("Kargo ile gelen kameranin kondisyonundan nasil emin olurum?",
     "Kondisyon aciklamasinin fotografli ve detayli oldugu, fonksiyon testinden gectigi belirtilen ilanlari tercih et; iade politikasi net olan saticilar bu konuda ek guvence saglar."),
    ("Bursa'dan siparis verirsem kargo suresi ne kadar surer?",
     "Kargo suresi secilen kargo firmasina ve stok durumuna gore degisir; siparis verirken tahmini teslimat suresini saticiyla netlestirmek en saglikli yontemdir."),
    ("Sehir disindan alinan kamerada garanti/iade hakkim var mi?",
     "Kayitli bir e-ticaret sitesinden alinan urunlerde Turkiye'de mesafeli satis sozlesmesi kapsaminda cayma hakkin bulunur; bu hak sehrin neresinde yasadigina bagli degildir, siparisin kayitli ve faturali olmasina baglidir."),
  ],
  body="""<p>Retro/Y2K dijital kamera trendinin buyuk kismi Istanbul merkezli gorunse de, <strong>Ankara Izmir Bursa ikinci el retro kamera</strong> arayan alicilarin sayisi hizla artiyor. Iyi haber su: dogru kaynaktan alindiginda, hangi sehirde yasadiginin pratikte hicbir onemi kalmiyor.</p>

<h2>Büyük Şehirler Dışında Seçim Neden Sınırlı?</h2>
<p>Bu niş, cok ozel bir bilgi ve test surecine dayandigi icin fiziksel magaza secenekleri dogal olarak sinirli ve genelde Istanbul'da yogunlasmis durumda. Ankara, Izmir veya Bursa'da yasayan biri icin yerel bir vitrin gezmek cogu zaman mumkun degil; ama bu sinirlama artik online alisverisle tamamen asilabiliyor.</p>

<h2>Kargo ile Alışveriş: Riskler ve Güvenceler</h2>
<p>Kargo ile alisverisin en buyuk endisesi, urunu elinle gormeden karar vermektir. Bu riski azaltmanin yolu, kondisyonu fotografli ve detayli aciklayan, fonksiyon testinden gectigini belirten ve net bir iade politikasi sunan bir kaynaktan almaktir. <a href="https://retrocameraland.com/collections/all">RetroCameraLand'da</a> her kamera bu surecten gecerek Turkiye'nin her yerine kargoyla gonderiliyor; yani Istanbul'da olman ile Ankara'da olman arasinda urunu alma guveni acisindan fark kalmiyor.</p>

<h2>Ankara İçin Öneriler</h2>
<p>Ankara'da yasayan bir alici icin en pratik yol, ihtiyacina uygun modeli online kataloglardan arastirip kondisyon detaylarini saticiya sormaktir. Kararsizsan <a href="{FINDER}">AI Kamera Eslestirici</a> ile birkac soruyu yanitlayip profiline uygun modelleri hizlica gorebilirsin.</p>

<h2>İzmir İçin Öneriler</h2>
<p>Izmir'de de durum benzer; yerel secenek sinirli oldugundan, saticinin kondisyon seffafligina ve iade politikasina odaklanmak en guvenli yaklasimdir. Deniz ve sahil fotografciligi yapacaksan dayanikli, su/darbe dirençli modelleri tercih etmek de akillica olur.</p>

<h2>Bursa İçin Öneriler</h2>
<p>Bursa'dan siparis verecek alicilar icin de ayni prensip gecerli: kondisyonu net, fonksiyon testinden gecmis bir urun secmek, kargo suresini onceden netlestirmek. Sehir farki, dogru kaynaktan alindiginda satin alma guvenini etkilemez; onemli olan urunun ve saticinin seffafligidir.</p>
""".replace("{FINDER}", FINDER)
))

# ── finder CTA satirlari (her bloga ozel) ─────────────────────────────────
CTA_LINES = {
  POSTS[0]["handle"]: "Pil/sarj derdi olmayan, kolay bakim gerektiren bir model mi ariyorsun? 6 kisa soruyla sana en uygun kamerayi bulalim.",
  POSTS[1]["handle"]: "Test edilmis, kondisyonu seffaf paylasilan bir kamera mi ariyorsun? Birkac soruyla sana uygun modelleri saniyeler icinde gor.",
  POSTS[2]["handle"]: "Kozmetik mi, fonksiyonel mi senin icin daha onemli? Profiline uygun durum notundaki kamerayi birlikte bulalim.",
  POSTS[3]["handle"]: "Guvenli ve seffaf bir kaynaktan almak istiyorsan, birkac soruyla sana uygun modelleri hemen listeleyelim.",
  POSTS[4]["handle"]: "Arizasiz, test edilmis bir kamerayla basla. 6 kisa soruyla sana uygun, guvenilir modelleri bulalim.",
  POSTS[5]["handle"]: "Digicam mi tam sana gore emin degil misin? Kisa bir testle profiline en uygun modeli onerelim.",
  POSTS[6]["handle"]: "Duzenlemeye az ihtiyac duyacagin, karakterli bir CCD kamera mi ariyorsun? Birkac soruyla eslestirelim.",
  POSTS[7]["handle"]: "Etkinlik icin dayanikli ve kolay kullanimli bir model mi lazim? 6 soruyla sana en uygun secenegi bulalim.",
  POSTS[8]["handle"]: "Bakimli, test edilmis bir lens/sensore sahip kamera mi istiyorsun? Kisa testle sana uygun modeli onerelim.",
  POSTS[9]["handle"]: "Hangi sehirde olursan ol, sana uygun kamerayi 6 soruyla bulalim; kargoyla Turkiye'nin her yerine gonderiyoruz.",
}

# ══════════════════════════════════════════════════════════════════════════
def build_html(p, image_url):
    parts = []
    parts.append(interactive_style())
    parts.append(f'<h1>{p["title"]}</h1>')
    parts.append(quickbox(p["quick"]))
    parts.append(p["body"].strip())
    parts.append(faq_accordion(p["faqs"]))
    parts.append(finder_cta(CTA_LINES[p["handle"]]))
    parts.append(SOCIAL_BLOCK)
    parts.append(schema_blocks(p["title"], p["handle"], p["meta_desc"], image_url, p["faqs"],
                                howto=p.get("howto")))
    return "\n\n".join(parts)

def pick_image(p):
    if not PIN_OK:
        return None, "pinterest yok"
    url, desc, score = find_unused_pinterest_image(p["img_kw"], p["pin_hero"])
    return url, f"{desc} (score={score})"

def publish(p, dry=False):
    img_url, img_note = pick_image(p)
    html = build_html(p, img_url)
    if dry:
        out = f"/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7febb5c3-b00a-40eb-b3cd-a1c831995bcc/scratchpad/preview_{p['handle']}.html"
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(
                f"<!doctype html><meta charset=utf-8><title>{p['title']}</title>"
                f"<div style='max-width:760px;margin:40px auto;font-family:-apple-system,sans-serif;padding:0 16px'>{html}</div>")
        except Exception:
            pass
        log(f"  [DRY] {p['title'][:55]} | gorsel: {img_note} | onizleme: {out}")
        return {"status": "dry", "title": p["title"], "image": img_url}
    payload = {"article": {
        "title": p["title"], "body_html": html, "handle": p["handle"],
        "tags": p["tags"], "published": True,
        "metafields": [
            {"namespace": "seo", "key": "description", "value": p["meta_desc"], "type": "single_line_text_field"},
            {"namespace": "seo", "key": "title",       "value": p["title"],     "type": "single_line_text_field"},
        ]}}
    if img_url:
        payload["article"]["image"] = {"src": img_url, "alt": p["title"]}
    r = shopify("POST", f"blogs/{BLOG_ID}/articles.json", payload)
    art = r["article"]
    log(f"  OK ID:{art['id']} -> {art['handle']} | gorsel: {img_note}")
    return {"status": "ok", "id": art["id"], "handle": art["handle"], "title": p["title"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="Yayinlamadan onizleme uret (tumu)")
    ap.add_argument("--index", type=int, default=None, help="Sadece N. yaziyi yayinla (1-10)")
    args = ap.parse_args()

    targets = POSTS if args.index is None else [POSTS[args.index - 1]]
    log(f"{'DRY-RUN' if args.dry else 'CANLI YAYIN'} — {len(targets)} yazi")
    results = []
    for i, p in enumerate(targets, 1):
        log(f"\n[{i}/{len(targets)}] {p['title'][:60]}")
        try:
            results.append(publish(p, dry=args.dry))
        except Exception as e:
            log(f"  HATA: {e}")
            results.append({"status": "error", "title": p["title"], "error": str(e)})
        if not args.dry and i < len(targets):
            time.sleep(2)

    print("\n" + "=" * 64)
    ok = sum(1 for r in results if r["status"] in ("ok", "dry"))
    for r in results:
        mark = "OK " if r["status"] in ("ok", "dry") else "XX "
        print(f"  {mark} {r['title'][:54]}")
    print(f"\nToplam: {ok}/{len(results)} basarili")
    print("=" * 64)
