#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Kamera Bulucu Segment Bloglari
==================================
Kamera bulucu quiz'inin hedef kitlelerine (kullanim amaci / estetik / ortam)
gore, daha once yazilmamis persona + satin-alma-niyeti bloglari.

Her blog:
  - Yuksek SEO: uzun-kuyruk anahtar kelime H1/meta, H2 yapisi, FAQ
  - JSON-LD: Article + FAQPage + BreadcrumbList
  - 3+ gercek stok urune deep-link (/products/...)
  - Sonunda KARARSIZLAR icin finder CTA -> /pages/hangi-kamera-bana-uygun
  - Sosyal medya blogu (SOCIAL_BLOCK) otomatik eklenir
  - DAHA ONCE KULLANILMAMIS Pinterest gorseli (find_unused_pinterest_image)

Kullanim:
  python3 rcl-blog-kamera-bulucu-segment.py --dry   # onizleme (yayinlamaz)
  python3 rcl-blog-kamera-bulucu-segment.py         # CANLI yayinla
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

# ── Kararsizlar icin finder CTA (her blogun sonunda) ──────────────────────────
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

# ── JSON-LD schema (Article + FAQPage + BreadcrumbList) ───────────────────────
def schema_blocks(title, handle, meta_desc, image, faqs):
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
    return "\n" + tag(article) + tag(faq) + tag(crumb)

def faq_html(faqs):
    out = ['<h2>Sikca Sorulan Sorular</h2>']
    for q, a in faqs:
        out.append(f'<h3>{q}</h3>\n<p>{a}</p>')
    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════════
#  BLOGLAR  (kamera bulucu segmentlerine birebir karsilik gelir)
# ══════════════════════════════════════════════════════════════════════════════
POSTS = []

# 1 ── SEYAHAT  (use=travel, env=mixed) ───────────────────────────────────────
POSTS.append(dict(
  title="Seyahat İçin En İyi Retro Dijital Kamera: 2026 Gezi Rehberi",
  handle="seyahat-icin-en-iyi-retro-dijital-kamera-2026-gezi-rehberi",
  keyword="seyahat için retro kamera",
  segment="Kullanım amacı: Seyahat & gezi (kamera bulucu)",
  tags="seyahat kamerasi, gezi kamerasi, retro kamera seyahat, kompakt zoom kamera, su gecirmez kamera, dayanikli kamera, retrocameraland",
  meta_desc="Seyahatte cantanda yer kaplamayan, optik zoomlu ve dayanikli retro dijital kamera mi ariyorsun? 2026 gezi rehberi: hangi model hangi gezgine uygun.",
  img_kw="travel retro digital camera olympus panasonic compact",
  pin_hero="Sony Cybershot DSC-W150",
  faqs=[
    ("Seyahatte telefon yerine neden retro kamera?",
     "Telefon her ani ayni mukemmel ama duygusuz tonla cekiyor. Retro CCD kameralarin sicak renkleri ve filmsi dokusu, gezi fotograflarini yillar sonra bakildiginda 'o ani hissettiren' karelere donusturur. Ayrica fotograf cekmek icin telefonu acmamak, anin icinde kalmani saglar."),
    ("Seyahat icin en onemli ozellik nedir: zoom mu, dayaniklilik mi?",
     "Sehir ve muze gezilerinde optik zoom (uzaktaki detaylar icin), doga ve deniz tatilinde ise su/darbe dayanikliligi one cikar. Karisik bir rotada her ikisini dengeleyen, cebe sigan kompakt bir model en mantiklisidir."),
    ("Ucakta retro kamera tasimak sorun olur mu?",
     "Hayir. Kamera ve yedek pilleri el bagajinda tasiman yeterli; lityum piller kabin bagajinda olmalidir. Kompakt CCD kameralar kucuk ve hafif oldugu icin gezi cantasinda neredeyse yer kaplamaz."),
  ],
  body="""<p>Bir geziye cikarken en cok pisman olunan sey, fotograflarin "herkesinki gibi" cikmasidir. Telefon kameralari teknik olarak mukemmel ama hepsi ayni: asiri keskin, ayni HDR tonu, ayni duygu. <strong>Seyahat icin retro dijital kamera</strong> ise tam tersini yapar; cantanda yer kaplamaz, sicak filmsi renkler verir ve gezini bir hatira albumune cevirir. Bu rehberde, gezgin tipine gore hangi retro kameranin neden uygun oldugunu anlatiyoruz.</p>

<h2>Seyahat Kamerasinda Aranan 4 Ozellik</h2>
<ul>
<li><strong>Hafiflik ve kompaktlik:</strong> Tum gun boynunda veya cebinde tasiyacaksin; gramaj onemli.</li>
<li><strong>Optik zoom:</strong> Sehir, muze ve manzara cekiminde uzaktaki detayi kaybetmeden yakinlastirir.</li>
<li><strong>Dayaniklilik:</strong> Deniz, kum ve yagmur icin su/darbe dayanikli govde bir artidir.</li>
<li><strong>Pil ve kart kolayligi:</strong> Yedek pil ve SD kart bulmasi kolay modeller yolda stres yaratmaz.</li>
</ul>

<h2>Sehir ve Kultur Gezileri İçin: Optik Zoomlu Kompaktlar</h2>
<p>Avrupa sokaklarinda, tarihi yapilarin tepe detaylarinda veya kalabalik bir meydanda uzaktaki bir kareyi yakalamak istediginde optik zoom kurtaricidir. <a href="https://retrocameraland.com/products/olympus-vr-340">Olympus VR-340</a> genis acidan baslayan yuksek zoom araligiyla hem dar sokaklari hem uzaktaki cati detaylarini tek kamerayla cozer. Daha uzun menzil isteyenler icin <a href="https://retrocameraland.com/products/panasonic-lumix-dc-tz91">Panasonic Lumix DC-TZ91</a>, seyahat-zoom kategorisinin en yetenekli modellerinden biridir; 30x zoomu sayesinde manzara ve sokak portresini ayni cantadan cikarir.</p>

<h2>Deniz, Doga ve Macera İçin: Dayanikli Modeller</h2>
<p>Tatilin denizde, havuzda veya doga yuruyusunde geciyorsa su ve darbeye dayanikli bir govde her seyi degistirir. <a href="https://retrocameraland.com/products/lumix-dmc-ft10">Lumix DMC-FT10</a> sigligi kucuk derinliklerde ve yagmurda gonul rahatligiyla cekim yapmani saglar. Daha uygun butceli, hava kosullarina direncli bir secenek arayanlar icin <a href="https://retrocameraland.com/products/kodak-zx1-weather-resistant">Kodak Zx1 (weather-resistant)</a>, gezi videosu ve fotografi birlikte cekmek isteyen maceraperestler icin pratik bir yol arkadasidir.</p>

<h2>Hafif Seyahat ve Gunluk Tasima İçin: Cep Dostu Klasikler</h2>
<p>Cantani hafif tutmak istiyorsan, cebe giren bir CCD kompakt en mantiklisidir. <a href="https://retrocameraland.com/products/sony-cybershot-dsc-w150">Sony Cybershot DSC-W150</a> dengeli zoomu, canli renkleri ve guvenilir otomatik moduyla "tak ve cek" rahatligi sunar; gun boyu boynunda tasimak yormaz. Hem gezi hem gunluk kullanim icin tek kamera arayanlarin ilk durağidir.</p>

<h2>Gezgine Gore Hizli Secim</h2>
<ul>
<li><strong>Sehir & muze gezgini:</strong> Optik zoomlu kompakt (VR-340, Lumix TZ91)</li>
<li><strong>Deniz & doga maceracisi:</strong> Su/darbe dayanikli model (Lumix FT10, Kodak Zx1)</li>
<li><strong>Minimalist gezgin:</strong> Cep dostu CCD klasik (Sony W150)</li>
</ul>
<p>Tum bu modeller satistan once fonksiyon testinden gecer ve kondisyonu seffaf bicimde paylasilir; yani yolda seni yarida birakmaz.</p>
"""))

# 2 ── GECE & PARTI  (use=night, env=citynight, aes=y2k) ──────────────────────
POSTS.append(dict(
  title="Gece ve Parti İçin En İyi Retro Kamera: Flaşlı Y2K Estetiği Rehberi",
  handle="gece-parti-icin-en-iyi-retro-kamera-flasli-y2k-estetigi",
  keyword="gece parti için retro kamera",
  segment="Kullanım amacı: Gece & parti / Ortam: Gece şehir ışıkları (kamera bulucu)",
  tags="gece kamerasi, parti kamerasi, flasli kamera, y2k estetik, ccd flas, gece fotografi, retrocameraland",
  meta_desc="Partide, konserde ve gece sokaginda o flasli Y2K dokusunu veren retro kamera mi ariyorsun? Gece icin en iyi CCD flas modelleri ve cekim ipuclari.",
  img_kw="y2k flash party night ccd camera aesthetic",
  pin_hero="Canon IXUS",
  faqs=[
    ("Gece cekiminde retro kamera telefondan iyi mi?",
     "Teknik olarak modern telefonlar gece modunda daha 'temiz' cikar; ama o temizlik karakteri yok eder. Retro CCD kameranin sert flasi, derin golgeleri ve hafif greni, partinin enerjisini ve Y2K dokusunu telefonun veremeyecegi bicimde yakalar. Burada amac mukemmellik degil, his."),
    ("Flasli Y2K estetigi nasil elde edilir?",
     "Dahili flasi acik tut, gece veya los ortamda yakin mesafeden cek. Konuya 1-2 metre mesafe, sert flas isigi ve koyu arka plan kombinasyonu o klasik 2000'ler parti karesini verir. CCD sensorun renk karakteri bu efekti dogal olarak tamamlar."),
    ("Gece kamerasinda hangi yil araligi daha iyi?",
     "Genelde 2009 ve oncesi CCD kompaktlar, o nostaljik flas-grain dokusunu daha belirgin verir. Daha yeni modeller daha temiz cekse de Y2K hissi icin biraz daha eski sensorler tercih edilir."),
  ],
  body="""<p>Gece hayatinin fotografi bir tuhaf: telefonla cektiginde ya cok karanlik ya da yapay derecede aydinlik cikiyor, ve hicbiri o anin enerjisini tasimi yor. Oysa Instagram'i saran o <strong>flasli Y2K parti estetigi</strong> tam olarak retro CCD kameralarin isidir. Sert flas, koyu arka plan, hafif gren ve canli renkler... Bu rehberde gece ve parti icin en iyi retro kameralari ve o dokuyu nasil yakalayacagini anlatiyoruz.</p>

<h2>Gece Kamerasinda Flas Neden Bu Kadar Onemli?</h2>
<p>Y2K estetiginin kalbinde dahili flas vardir. CCD sensorle birlesen sert flas isigi, on plani patlatir, arka plani koyu birakir ve o karakteristik "2000'ler parti polaroid" gorunumunu yaratir. Modern telefonlarin yumusak yapay aydinlatmasinin aksine bu sert kontrast, anin ham enerjisini dondurur.</p>

<h2>Parti ve Ev Eglencesi İçin: Klasik Flas Kompaktlari</h2>
<p>Kalabalik bir parti, dogum gunu veya ev toplantisinda hizli, guclu flasli bir kompakt istersin. <a href="https://retrocameraland.com/products/canon-ixus-i">Canon IXUS i</a> ultra ince govdesi ve guclu flasiyla cebe atilir, anlik kareleri kacirmaz. Daha canli ve net renk karakteri arayanlar icin <a href="https://retrocameraland.com/products/sony-cybershot-dsc-w150">Sony Cybershot DSC-W150</a> gece portrelerinde yuzleri net ve enerjik cikarir.</p>

<h2>Gece Şehir ve Sokak İçin: Karakterli CCD Modeller</h2>
<p>Neon tabelalar, gece sokagi, sehir isiklari... Bu sahneler retro kamerada filmsi bir parlama kazanir. <a href="https://retrocameraland.com/products/casio-exilim-ex-z110">Casio Exilim EX-Z110</a> hizli ve pratik yapisiyla sokakta spontane gece kareleri icin idealdir. Daha buyuk sensor ve zoom isteyenler <a href="https://retrocameraland.com/products/sony-cybershot-dsc-t300">Sony Cybershot DSC-T300</a> ile gece sehir manzaralarini ve grup karelerini rahatca toplar.</p>

<h2>Flaşlı Gece Karesi İçin 4 Hızlı İpucu</h2>
<ol>
<li><strong>Flasi her zaman acik tut:</strong> Gece icin otomatik degil, zorunlu flas modunu sec.</li>
<li><strong>Yakin dur:</strong> Konuya 1-2 metre mesafe, en iyi flas sonucunu verir.</li>
<li><strong>Koyu arka plan ara:</strong> Arkasi karanlik olan kareler o klasik Y2K patlamasini verir.</li>
<li><strong>Seri cek:</strong> Gece hareketli; ayni ani birkac kez cekip en iyisini sec.</li>
</ol>
"""))

# 3 ── PORTRE & SEVDIKLERIN  (use=portrait, aes=warm) ─────────────────────────
POSTS.append(dict(
  title="Portre ve İnsan Çekimi İçin En İyi Retro Kamera: Sıcak Ten Tonları Rehberi",
  handle="portre-insan-cekimi-icin-en-iyi-retro-kamera-sicak-ten-tonlari",
  keyword="portre için retro kamera",
  segment="Kullanım amacı: Portre & sevdiklerin / Estetik: Sıcak retro renkler (kamera bulucu)",
  tags="portre kamerasi, insan cekimi, sicak ten tonu, retro portre, canon fujifilm kodak, retro kamera, retrocameraland",
  meta_desc="Sevdiklerinin yuzunu sicak, samimi ten tonlariyla cekmek mi istiyorsun? Portre icin en iyi retro kameralar ve dogal renk veren CCD modeller rehberi.",
  img_kw="portrait warm skin tone canon fujifilm kodak film",
  pin_hero="Fujifilm Finepix Z90",
  faqs=[
    ("Portre cekiminde hangi marka sicak ten tonu verir?",
     "Geleneksel olarak Canon yumusak ve sicak ten tonlariyla, Fujifilm efsane film simulasyonu renkleriyle, Kodak ise nostaljik sicak tonlariyla portrede one cikar. Bu markalarin CCD kompaktlari, yuzleri dogal ve samimi gosterir."),
    ("Portre icin yuksek megapiksel sart mi?",
     "Hayir. Sosyal medya ve baski icin 6-10 MP fazlasiyla yeterlidir. Portrede onemli olan cozunurluk degil, sensorun renk karakteri ve ten tonu islemesidir. Dusuk MP'li bir CCD bile cok daha 'insancil' bir his verebilir."),
    ("Sevgilim/ailem icin hediye olarak portre kamerasi uygun mu?",
     "Cok uygun. Sicak tonlu, kullanimi kolay bir CCD kompakt; ciftlerin ve ailelerin birlikte ani biriktirmesi icin anlamli bir hediyedir. Otomatik modlari guclu modeller, fotografla yeni ilgilenen biri icin de stressizdir."),
  ],
  body="""<p>Bir insanin yuzunu cektiginde aslinda bir duyguyu cekersin. Ve o duygunun sicak mi yoksa soguk mu gorunecegini buyuk olcude kameranin renk karakteri belirler. Telefonlar yuzleri cogu zaman fazla puruzsuz ve soguk gosterir; <strong>portre icin retro kamera</strong> ise sicak ten tonlari, yumusak gecisler ve samimi bir doku verir. Bu rehberde sevdiklerini en guzel haliyle olumsuzlestirecek retro kameralari topladik.</p>

<h2>Portrede "Sıcak Ten Tonu" Ne Demek?</h2>
<p>Sicak ten tonu, ciltteki kirmizi-sari dengenin dogal ve insancil cikmasidir. Soguk bir sensor yuzu solgun ve hastane isigi gibi gosterirken, sicak karakterli bir CCD sensor ayni yuzu gun batimi isigi gibi yumusatir. Portrede aradigin sey genelde keskinlik degil, bu sicaklik ve yumusakliktir.</p>

<h2>Yumuşak ve Samimi Portreler İçin: Canon ve Fujifilm</h2>
<p>Canon'un renk bilimi, ten tonlarini yumusak ve sicak gostermesiyle unludur. <a href="https://retrocameraland.com/products/canon-ixus-i">Canon IXUS i</a> yakin plan yuz cekimlerinde dogal bir sicaklik verir. Film renklerini sevenler icin ise <a href="https://retrocameraland.com/products/fujifilm-finepix-z90-digicam">Fujifilm Finepix Z90</a>, Fujifilm'in efsane renk karakterini dokunmatik ekranli pratik bir govdede sunar; ozellikle ikili ve grup portrelerinde tonlari cok hos cikarir.</p>

<h2>Nostaljik ve Duygusal Kareler İçin: Kodak Sıcaklığı</h2>
<p>Kodak ismi fotografta sicaklikla esanlamlidir. <a href="https://retrocameraland.com/products/kodak-easyshare-v603">Kodak EasyShare V603</a>, o nostaljik solmus-album tonlariyla aile ve sevgili portrelerine duygusal bir derinlik katar. Yillar sonra bakildiginda "bu fotograf o gunu hissettiriyor" dedirten kareler tam olarak bu tur sensorlerden cikar.</p>

<h2>Daha Net ve Detaylı Portre İçin: Dengeli Modeller</h2>
<p>Biraz daha cozunurluk ve zoom isteyenler icin <a href="https://retrocameraland.com/products/sony-cybershot-dsc-t300">Sony Cybershot DSC-T300</a>, yuz detayini koruyarak sicak ortam isigini dengeli sekilde toplar. Hem gunduz disari hem los ic mekan portrelerinde esnek bir secimdir.</p>

<h2>Portre Çekiminde 3 Küçük Sır</h2>
<ol>
<li><strong>Dogal isiga yan dur:</strong> Pencereden gelen yumusak isik, ten tonunu en guzel haliyle aydinlatir.</li>
<li><strong>Gozlere odaklan:</strong> Netlemeyi goz hizasinda kilitle; portrede gozler her seydir.</li>
<li><strong>Altin saati kullan:</strong> Gun batiminda cekilen portreler, retro kamerada film gibi gorunur.</li>
</ol>
"""))

# 4 ── SINEMATIK FILM TONU  (aes=cine) ────────────────────────────────────────
POSTS.append(dict(
  title="Sinematik Film Tonu Veren Retro Kameralar: Filmsi Renkler Rehberi 2026",
  handle="sinematik-film-tonu-veren-retro-kameralar-filmsi-renkler-2026",
  keyword="sinematik film tonu retro kamera",
  segment="Estetik: Sinematik film tonu (kamera bulucu)",
  tags="sinematik kamera, film tonu, filmsi renkler, fujifilm olympus kodak, cine estetik, retro kamera, retrocameraland",
  meta_desc="Karelerin bir film sahnesinden cikmis gibi gorunsun mu istiyorsun? Sinematik film tonu veren retro CCD kameralar ve o dramatik renkleri yakalama rehberi.",
  img_kw="cinematic film tone moody fujifilm olympus kodak color",
  pin_hero="Olympus retro camera",
  faqs=[
    ("Sinematik film tonu telefon ile elde edilemez mi?",
     "Telefonda uygulamayla 'film filtresi' eklenebilir ama bu sonradan zorlanmis bir efekttir. Retro CCD kameralar bu tonlari sensor seviyesinde, dogal olarak uretir; bu yuzden sonuc daha inandirici ve duzenlemeye gerek birakmadan sinematiktir."),
    ("Hangi markalar daha sinematik renk verir?",
     "Fujifilm film simulasyonu mirasiyla, Olympus keskin ama dramatik kontrastiyla ve Kodak sicak film tonlariyla sinematik estetikte one cikar. Bu uc marka, 'film karesi' hissi arayanlarin ilk tercihidir."),
    ("Sinematik cekim icin hangi isik en iyisi?",
     "Yumusak ve yonlu isik. Gun batimi, golgeli pencere kenari veya los ic mekan; bu kosullar retro sensorun dramatik tonlama yetenegini ortaya cikarir. Sert ogle gunesinden ziyade altin saat sinematik his icin idealdir."),
    ("Dusuk megapiksel sinematik gorunumu bozar mi?",
     "Aksine, cogu zaman destekler. Sinematik his cozunurlukten degil tonlama ve atmosferden gelir. 5-8 MP bir CCD sensor, yumusak gecisleri ve hafif greniyle bir film karesine modern yuksek-MP sensorlerden daha yakin durur. Onemli olan netlik degil, duygudur."),
  ],
  body="""<p>Bazi fotograflara bakarsin ve sanki bir filmden alinmis bir kare gibidir: tonlar yumusak, renkler dramatik, atmosfer derin. Bu his rastlanti degil; <strong>sinematik film tonu veren retro kameralarin</strong> sensor karakteristiginden gelir. Bu rehberde, karelerini bir film sahnesine cevirecek CCD modelleri ve o tonlari nasil yakalayacagini anlatiyoruz.</p>

<h2>"Sinematik Ton" Aslında Nedir?</h2>
<p>Sinematik gorunum; yumusak renk gecisleri, kontrollu kontrast ve hafif soluk, atmosferik bir palettir. Modern dijital genelde her seyi keskin ve canli yapar; sinema ise tonu ve duyguyu one cikarir. Retro CCD sensorler bu "film karesi" hissini dogal olarak verdigi icin son yillarda yeniden cok arananiyor.</p>

<h2>Film Simülasyonu Mirası İçin: Fujifilm</h2>
<p>Fujifilm, fotograf tarihinin en sevilen film renklerini ureten markadir ve bu miras dijital kompaktlarina da yansir. <a href="https://retrocameraland.com/products/fujifilm-finepix-z700-exr">Fujifilm Finepix Z700 EXR</a> zengin renk islemesiyle sahnelere film hissi katar. Daha eski, daha karakterli bir doku arayanlar icin <a href="https://retrocameraland.com/products/fujifilm-finepix-4700-zoom">Fujifilm Finepix 4700 Zoom</a>, erken donem CCD'nin o ham sinematik tonunu sunar.</p>

<h2>Dramatik Kontrast İçin: Olympus</h2>
<p>Olympus sensorleri keskin netligin yaninda dramatik bir kontrast karakteri tasir; bu da golge-isik geciselerini sinematiklestirir. <a href="https://retrocameraland.com/products/olympus-sp-320">Olympus SP-320</a>, los ortamlarda ve golgeli sahnelerde tonlari derinlestirerek "film noir" tadinda kareler verir.</p>

<h2>Sıcak Film Paleti İçin: Kodak</h2>
<p>Bir sahneye nostaljik sinema sicakligi katmak istiyorsan Kodak vazgecilmezdir. <a href="https://retrocameraland.com/products/kodak-easyshare-v603">Kodak EasyShare V603</a>, solmus film tonlari ve sicak paletiyle gunluk sahneleri bile bir donem filmi karesine cevirir.</p>

<h2>Daha Sinematik Çekmek İçin 3 İpucu</h2>
<ol>
<li><strong>Altin saatte cek:</strong> Gun dogumu ve batimi, sinematik tonun en kolay yoludur.</li>
<li><strong>Bos alan birak:</strong> Konuyu kenara koyup negatif alan birakmak, kareye sinema kompozisyonu hissi verir.</li>
<li><strong>Tonu bozma:</strong> Cekimi asiri duzenleme; retro sensorun verdigi tonu oldugu gibi birak, sihir orada.</li>
</ol>
"""))

# 5 ── İCERIK & VLOG  (use=content, occasion=work) ────────────────────────────
POSTS.append(dict(
  title="İçerik Üreticiler ve Vlog İçin En İyi Retro Kamera: 2026 Sosyal Medya Rehberi",
  handle="icerik-ureticiler-vlog-icin-en-iyi-retro-kamera-2026",
  keyword="içerik üretici için retro kamera",
  segment="Kullanım amacı: İçerik & vlog / Vesile: İş & içerik (kamera bulucu)",
  tags="vlog kamerasi, icerik ureticisi, retro kamera vlog, tiktok kamera, y2k icerik, dikey video, retrocameraland",
  meta_desc="TikTok, Reels ve YouTube icin dikkat ceken Y2K estetigi mi ariyorsun? Icerik ureticiler ve vlog icin en iyi retro kameralar, video destekli modeller rehberi.",
  img_kw="content creator vlog y2k camera tiktok aesthetic setup",
  pin_hero="lumix tz91 retro",
  faqs=[
    ("Retro kamera ile sosyal medya icerigi gercekten daha cok ilgi ceker mi?",
     "Evet. Y2K estetigi su an TikTok ve Instagram'da guclu bir trend; herkesin telefon karesi arasinda retro CCD dokusu aninda fark edilir ve durduurucu etki yaratir. 'Bu hangi kamera?' yorumlari etkilesimi de yukseltir."),
    ("Vlog icin video destegi olan retro kamera var mi?",
     "Var. Bazi gec donem CCD kompaktlari ve adanmis kameralar HD video kaydedebilir; dokunmatik ekran ve genis aci, vlog ve selfie cekimini kolaylastirir. Tamamen video odakli icin video kayit ozelligi guclu modelleri tercih et."),
    ("Icerik uretimi icin tek kamera yeterli mi yoksa aksesuar da gerekli mi?",
     "Bir kompakt cogu icerik icin yeterlidir; ama sabit ve titremesiz cekim icin kucuk bir tripod isini cok kolaylastirir. Masaustu kurulum ve vlog cekimleri icin hafif bir tripod neredeyse zorunludur."),
  ],
  body="""<p>Sosyal medyada dikkat cekmek artik "iyi" video cekmekten ibaret degil; "farkli" gorunmek gerekiyor. Milyonlarca puruzsuz telefon karesinin arasinda, <strong>retro kameranin Y2K dokusu</strong> aninda fark edilir ve durdurur. Icerik ureticiler ve vlogger'lar bu yuzden CCD kameralara yoneliyor. Bu rehberde, profiline gore en uygun icerik kamerasini ve kurulumunu anlatiyoruz.</p>

<h2>İçerik Üretiminde Retro Kamera Neden Kazandırır?</h2>
<p>Y2K estetigi su an en guclu gorsel trendlerden biri. Retro CCD dokusu; flasli geceler, filmsi renkler ve o nostaljik gren, telefon karelerinden hemen ayrisir. Bu ayrisma hem izlenmeyi hem "hangi kamera bu?" yorumlarini getirir; yani hem estetik hem etkilesim kazandirir.</p>

<h2>TikTok ve Reels İçin: Pratik ve Dokunmatik Modeller</h2>
<p>Hizli icerik akisi icin dokunmatik ekranli, pratik bir model isini kolaylastirir. <a href="https://retrocameraland.com/products/fujifilm-finepix-z90-digicam">Fujifilm Finepix Z90</a> dokunmatik ekrani, ince govdesi ve canli renkleriyle gunluk Reels ve fotograf icerigi icin idealdir; cekip aninda paylasacagin estetigi dogrudan verir.</p>

<h2>Genis Açı ve Zoom İçin: Vlog Esnekliği</h2>
<p>Vlog ve gezi icerigi cesitli planlar gerektirir: genis selfie acisi, uzaktan detay, sokak plani. <a href="https://retrocameraland.com/products/panasonic-lumix-dc-tz91">Panasonic Lumix DC-TZ91</a> genis acisi, yuksek zoomu ve dokunmatik ekraniyla tek basina bir vlog studyosudur; sehirde gezerken hem genis hem yakin plani tek cantadan cikarir.</p>

<h2>Video Odaklı İçerik İçin: HD Kayıt</h2>
<p>Agirlikli olarak video uretiyorsan, video tarafi guclu bir model istersin. <a href="https://retrocameraland.com/products/sanyo-xacti-vpc-hd1">Sanyo Xacti VPC-HD1</a>, dikey tutusu ve HD video karakteriyle retro his veren vlog kayitlari icin ilginc bir secimdir.</p>

<h2>Kurulumunu Tamamla: Tripod</h2>
<p>Titremesiz, sabit ve hands-free cekim icin kucuk bir tripod sart. <a href="https://retrocameraland.com/products/ulanzi-vlog-tripod">Ulanzi Vlog Tripod</a> hafif, katlanabilir yapisiyla hem masaustu hem el cubugu olarak kullanilir; icerik kurulumunu tamamlayan kucuk ama kritik bir parcadir.</p>

<h2>İçerik Üreticisi İçin Hızlı Eşleştirme</h2>
<ul>
<li><strong>Foto + kisa video agirlikli:</strong> Fujifilm Z90 (dokunmatik, pratik)</li>
<li><strong>Gezi & vlog:</strong> Lumix TZ91 (genis aci + zoom)</li>
<li><strong>Video odakli:</strong> Sanyo Xacti VPC-HD1 + Ulanzi tripod</li>
</ul>
"""))

# 6 ── LOS IC MEKAN / KAFE  (env=indoor, aes=dreamy/warm) ─────────────────────
POSTS.append(dict(
  title="Loş Kafe ve İç Mekan İçin En İyi Retro Kamera: Atmosfer Fotoğrafçılığı Rehberi",
  handle="los-kafe-ic-mekan-icin-en-iyi-retro-kamera-atmosfer-fotografciligi",
  keyword="loş iç mekan için retro kamera",
  segment="Ortam: Loş iç mekan / Estetik: Rüya gibi & sıcak (kamera bulucu)",
  tags="los mekan kamerasi, kafe fotografi, ic mekan retro kamera, atmosfer fotografi, sicak ton, flas, retrocameraland",
  meta_desc="Kafe kosesinde, ev sicakliginda ve los atolyede atmosferi yakalayan retro kamera mi ariyorsun? Los ic mekan icin en iyi modeller ve cekim ipuclari.",
  img_kw="cozy cafe dim indoor warm film camera aesthetic moody",
  pin_hero="canon ixus retro",
  faqs=[
    ("Los ortamda retro kamera nasil iyi cekim yapar?",
     "Los mekanda iki yol vardir: dahili flasla on plani aydinlatmak (Y2K kafe karesi) veya sabit tutarak mevcut sicak isikla atmosferik cekmek. Flasli modeller los ortamda guvenli sonuc verir; sabit cekimde ise masaya yaslanmak veya kucuk tripod kullanmak netligi artirir."),
    ("Kafe fotografinda sicak ton neden onemli?",
     "Kafelerin ahsap, kahve ve sari isik atmosferi sicak tonla cok daha davetkar gorunur. Sicak karakterli CCD sensorler bu ambiyansi dogal olarak abartmadan guzellestirir; soguk bir sensor ayni sahneyi kasvetli gosterebilir."),
    ("Los mekanda yuksek ISO gren sorun mu?",
     "Sorun degil, aksine bir estetik. Los ortamda yukselen ISO ile gelen hafif gren, retro ve filmsi hissin parcasidir. Modern kameralarda kacinilan bu doku, atmosfer fotografciliginda bilerek tercih edilir."),
    ("Kafe icinde flas kullanmak rahatsiz edici olur mu?",
     "Kalabalik ve sessiz mekanlarda flasi olcuyle kullanmak nezaket geregidir; bir-iki kare yeterlidir. Cevreyi rahatsiz etmek istemiyorsan flasi kapatip mevcut sicak isikla, kamerayi sabit tutarak atmosferik cekim yapabilirsin. Iki yontemi de denemek en saglikli yaklasimdir."),
  ],
  body="""<p>Los bir kafe kosesi, pencereden suzulen yumusak isik, buharli bir fincan... Bu sahneler bir atmosfer tasir ve o atmosferi yakalamak telefonla cogu zaman mumkun olmaz; ya cok karanlik ya da yapay cikar. <strong>Los ic mekan icin retro kamera</strong>, sicak tonlari ve flasli karakteriyle bu ambiyansi oldugu gibi dondurur. Bu rehberde kafe, ev ve atolye gibi los mekanlar icin en iyi retro kameralari topladik.</p>

<h2>Loş Mekanda Çekimin İki Yolu</h2>
<p>Birinci yol <strong>flas</strong>: dahili flasla on plani patlatip o klasik Y2K kafe karesini yakalarsin. Ikinci yol <strong>atmosferik cekim</strong>: flasi kapatip mevcut sicak isikla, kamerayi sabit tutarak ortamin ambiyansini korursun. Iyi bir los-mekan kamerasi her ikisini de iyi yapar.</p>

<h2>Flaşlı Kafe Estetiği İçin: Güçlü Flaş Kompaktları</h2>
<p>Masadaki yemegi, arkadasini veya fincani flasla cektigin o net Y2K karesi icin guvenilir bir flas sart. <a href="https://retrocameraland.com/products/canon-ixus-i">Canon IXUS i</a> ince govdesi ve hizli flasiyla kafe icinde aninda kare yakalar. Daha sicak, nostaljik bir ton isteyenler icin <a href="https://retrocameraland.com/products/kodak-easyshare-v603">Kodak EasyShare V603</a>, los ortami sicak film tonuyla davetkar gosterir.</p>

<h2>Atmosferik ve Sıcak Cekimler İçin: Dengeli Modeller</h2>
<p>Flas kullanmadan ortamin sicak isigini korumak istiyorsan, dengeli bir sensor istersin. <a href="https://retrocameraland.com/products/nikon-coolpix-885">Nikon Coolpix 885</a>, dogal renk gecisleriyle los mekanin ambiyansini koruyarak cekim yapar. Daha canli ve net bir sonuc arayanlar icin <a href="https://retrocameraland.com/products/sony-cybershot-dsc-w150">Sony Cybershot DSC-W150</a>, los ic mekanda bile yuzleri ve detaylari toparlar.</p>

<h2>Loş Mekan Fotoğrafçılığı İçin 4 İpucu</h2>
<ol>
<li><strong>Dirsegini masaya daya:</strong> Los ortamda en buyuk dusman titremedir; govdeyi sabitle.</li>
<li><strong>Pencere isigini kullan:</strong> Konuyu pencereden gelen yumusak isiga yan oturt.</li>
<li><strong>Greni kucumseme:</strong> Yukselen ISO ile gelen hafif gren, atmosferi guclendirir.</li>
<li><strong>Flasi dene ve karsilastir:</strong> Ayni kareyi flasli ve flassiz cek; mekana gore birini sec.</li>
</ol>
"""))

# ── finder CTA satirlari (her bloga ozel) ─────────────────────────────────────
CTA_LINES = {
  POSTS[0]["handle"]: "Sehir mi, deniz mi, minimalist gezi mi? 6 kisa soruyla rotana ve tarzina en uygun seyahat kamerasini saniyeler icinde ogren.",
  POSTS[1]["handle"]: "Parti mi, gece sokagi mi, konser mi? Birkac soruyla gece tarzina en uygun flasli retro kamerayi senin icin secelim.",
  POSTS[2]["handle"]: "Sicak portreler, sevgili kareleri veya aile anilari... Profiline en uygun portre kamerasini birkac soruyla bulalim.",
  POSTS[3]["handle"]: "Sinematik tonu hangi sahnede ariyorsun? Kisa bir testle sana en uygun film-tonlu retro kamerayi onerelim.",
  POSTS[4]["handle"]: "Foto mu, vlog mu, dikey video mu? Icerik tarzina en uygun retro kamerayi 1 dakikada eslesterelim.",
  POSTS[5]["handle"]: "Kafe kosesi, los atolye, ev sicakligi... Cekim ortamina en uygun retro kamerayi birkac soruyla bulalim.",
}

# ══════════════════════════════════════════════════════════════════════════════
def segment_closer(p):
    return (
      '<h2>Doğru Kamerayı Seçmek: Test Edilmiş ve Stoktan</h2>'
      f'<p>RetroCameraLand\'da listelenen tüm {p["keyword"]} secenekleri, satistan once '
      'fonksiyon testinden gecer ve kondisyonu seffaf bicimde paylasilir; yani aldigin kamera '
      'sadece guzel gorunmez, calisir. <a href="https://retrocameraland.com/collections/all">Tum '
      'koleksiyonu</a> inceleyebilir ya da kararsizsan <a href="' + FINDER + '">AI Kamera '
      'Esleştirici</a> ile birkac kisa soruyu yanitlayip profiline en uygun uc modeli yuzdesel '
      'uyum skoruyla gorebilirsin. Boylece yanlis model alma riskini ortadan kaldirir, dogrudan '
      'sana uygun olana odaklanirsin.</p>'
    )

def build_html(p, image_url):
    parts = []
    parts.append(f'<h1>{p["title"]}</h1>')
    parts.append(p["body"].strip())
    parts.append(segment_closer(p))
    parts.append(faq_html(p["faqs"]))
    parts.append(finder_cta(CTA_LINES[p["handle"]]))
    parts.append(SOCIAL_BLOCK)
    parts.append(schema_blocks(p["title"], p["handle"], p["meta_desc"], image_url, p["faqs"]))
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
        out = f"/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/80b2a8a5-312b-4798-ad46-677790ac725e/scratchpad/preview_{p['handle']}.html"
        try:
            open(out, "w", encoding="utf-8").write(
                f"<!doctype html><meta charset=utf-8><title>{p['title']}</title>"
                f"<div style='max-width:760px;margin:40px auto;font-family:-apple-system,sans-serif;padding:0 16px'>{html}</div>")
        except Exception:
            pass
        log(f"  [DRY] {p['title'][:50]} | gorsel: {img_note} | onizleme: {out}")
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
    ap.add_argument("--dry", action="store_true", help="Yayinlamadan onizleme uret")
    args = ap.parse_args()

    log(f"{'DRY-RUN' if args.dry else 'CANLI YAYIN'} — {len(POSTS)} segment blogu")
    results = []
    for i, p in enumerate(POSTS, 1):
        log(f"\n[{i}/{len(POSTS)}] {p['segment']}")
        try:
            results.append(publish(p, dry=args.dry))
        except Exception as e:
            log(f"  HATA: {e}")
            results.append({"status": "error", "title": p["title"], "error": str(e)})
        if not args.dry and i < len(POSTS):
            time.sleep(2)

    print("\n" + "=" * 64)
    ok = sum(1 for r in results if r["status"] in ("ok", "dry"))
    for r in results:
        mark = "OK " if r["status"] in ("ok", "dry") else "XX "
        print(f"  {mark} {r['title'][:54]}")
    print(f"\nToplam: {ok}/{len(results)} basarili")
    print("=" * 64)
