#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Vintage Soru Bloglari
=========================
Kullanicinin gercek arama sorularina (vintage cekim / retro tarz / flasli vintage /
gunluk anilar / telefona aktarim) birebir cevap veren, daha once yazilmamis
persona + niyet bloglari. Ayni format: rcl-blog-kamera-bulucu-segment.py

Her blog:
  - Yuksek SEO/AEO: soru birebir H1, dogrudan cevap paragrafi, FAQ
  - JSON-LD: Article + FAQPage + BreadcrumbList
  - 3+ gercek stok urune deep-link (/products/...)
  - Sonunda KARARSIZLAR icin finder CTA -> /pages/hangi-kamera-bana-uygun
  - Sosyal medya blogu (SOCIAL_BLOCK) otomatik eklenir
  - DAHA ONCE KULLANILMAMIS Pinterest gorseli (find_unused_pinterest_image)

Kullanim:
  python3 rcl-blog-vintage-sorular.py --dry   # onizleme (yayinlamaz)
  python3 rcl-blog-vintage-sorular.py         # CANLI yayinla
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
#  BLOGLAR  (kullanicinin gercek arama sorularina birebir karsilik gelir)
# ══════════════════════════════════════════════════════════════════════════════
POSTS = []

# 1 ── VINTAGE CEKIM YAPAN KAMERALAR NELERDIR (bilgilendirme/AEO) ─────────────
POSTS.append(dict(
  title="Vintage Çekim Yapan Kameralar Nelerdir? 2026 Rehberi",
  handle="vintage-cekim-yapan-kameralar-nelerdir-2026-rehberi",
  keyword="vintage çekim yapan kameralar",
  segment="Bilgilendirme: Vintage kamera türleri (AEO)",
  tags="vintage kamera, ccd kamera, retro dijital kamera, mirrorless retro, vintage cekim, retrocameraland",
  meta_desc="Vintage cekim yapan kameralar hangileridir? CCD dijital kompakt, retro ruhlu mirrorless ve film kameralarin farkini ve hangisinin sana uygun oldugunu ogren.",
  img_kw="vintage camera types ccd film mirrorless retro collection",
  pin_hero="vintage camera collection retro",
  faqs=[
    ("Vintage çekim yapan kamera türleri nelerdir?",
     "Uc ana kategori vardir: (1) 2000'lerin CCD sensorlu dijital kompaktlari — otomatik, ucuz ve o klasik Y2K/vintage renk karakterini veren en erisilebilir yol; (2) retro ruhlu mirrorless kameralar — Olympus PEN gibi modern sensor ile klasik govde tasarimini birlestirir; (3) analog film kameralari — gercek negatif film kullanir, en otantik ama en yavas ve maliyetli yontemdir. Cogu insan icin baslangic noktasi CCD dijital kompakttir."),
    ("CCD dijital kamera ile film kamerası arasındaki fark nedir?",
     "CCD dijital kamera aninda sonuc verir, hafiza kartina kaydeder ve ucretsiz sinirsiz cekim yapar; sensorun kendine ozgu renk islemesi vintage/Y2K tonunu dogal olarak uretir. Film kamerasi ise gercek kimyasal negatif kullanir, banyo/tarama gerektirir, her karenin bir maliyeti vardir ve sonucu gormek gunler surer. Vintage HISSI ariyorsan CCD yeterlidir; vintage SURECI de ariyorsan film kamerasi gerekir."),
    ("Vintage görünüm için en kolay başlangıç hangi kamera türüdür?",
     "CCD dijital kompakt kameralar. Otomatik moda sahiptirler, ogrenme egrisi yoktur, sarj/kart bulmasi kolaydir ve vintage renk karakterini ilk kareden itibaren verir. Mirrorless ve film kameralarina daha sonra, tarzini netlestirdiginde gecebilirsin."),
  ],
  body="""<p>Son yillarda "vintage cekim yapan kameralar" arayisi hizla artiyor; ama bu baslik altinda aslinda birbirinden cok farkli uc tur kamera var. Hangisinin sana uygun oldugunu bilmeden birini almak, ya cok karmasik ya da beklenenden farkli bir sonuca goturebilir. Bu rehberde vintage estetigi ureten kamera turlerini, farklarini ve hangi turun kime uygun oldugunu net bicimde anlatiyoruz.</p>

<h2>1. CCD Dijital Kompaktlar: En Erişilebilir Vintage Yol</h2>
<p>2000'lerin ortasinda uretilen CCD sensorlu dijital kompaktlar, bugun "vintage/Y2K estetik" olarak bilinen o sicak, hafif grenli ve doygun renk tonunu sensor seviyesinde dogal olarak uretir. Modern CMOS sensorlerin aksine CCD, renkleri daha az "temiz" ama daha "karakterli" isler. <a href="https://retrocameraland.com/products/fujifilm-finepix-jv310">Fujifilm FinePix JV310</a> ve <a href="https://retrocameraland.com/products/casio-exilim-ex-z4">Casio Exilim EX-Z4</a> bu kategorinin otomatik, kullanimi kolay ve butce dostu ornekleridir; hicbir teknik bilgi gerektirmeden ilk kareden itibaren vintage sonuc verirler.</p>

<h2>2. Retro Ruhlu Mirrorless Kameralar</h2>
<p>Govde tasarimi klasik olan ama icinde daha modern bir sensor barindiran mirrorless modeller, hem estetik hem esneklik isteyenler icin ortadadir. <a href="https://retrocameraland.com/products/olympus-pen-e-pl1-25mm">Olympus PEN E-PL1</a> klasik gorunumu, degistirilebilir lens secenegi ve daha genis kontrol imkaniyla, CCD kompaktin otesine gecmek isteyenler icin dogal bir sonraki adimdir. <a href="https://retrocameraland.com/products/samsung-nx2000">Samsung NX2000</a> ise dokunmatik ekrani ve wifi ozelligiyle klasik govdeyi modern kullanima baglar.</p>

<h2>3. Analog Film Kameraları: En Otantik ama En Yavaş Yol</h2>
<p>Gercek negatif film kullanan analog kameralar, vintage sureci en oz haliyle yasatir; ancak her karenin bir maliyeti vardir, banyo/tarama gerekir ve sonucu gormek zaman alir. RCL'de agirlik dijital CCD koleksiyonunda olsa da, film deneyimine gecmeden once CCD ile "vintage renk karakteri" konusunda zevkini netlestirmen, yanlis yatirimi onler.</p>

<h2>Hangi Türü Seçmelisin?</h2>
<ul>
<li><strong>Yeni baslayan / butce odakli:</strong> CCD dijital kompakt (JV310, EX-Z4)</li>
<li><strong>Daha fazla kontrol / degistirilebilir lens:</strong> Retro mirrorless (Olympus PEN, Samsung NX2000)</li>
<li><strong>Tam otantik surec:</strong> Analog film kamerasi</li>
</ul>
<p>Cogu kisi icin en mantikli baslangic CCD dijital kompakttir: risksiz, ucretsiz cekim ve aninda sonuc. Tarzini netlestirdikce mirrorless veya filme gecmek her zaman mumkun.</p>
"""))

# 2 ── RETRO TARZ FOTOGRAFLAR ICIN HANGI KAMERAYI ALMALISIN (genel satin alma) ─
POSTS.append(dict(
  title="Retro Tarz Fotoğraflar İçin Hangi Kamerayı Almalısın? 2026 Rehberi",
  handle="retro-tarz-fotograflar-icin-hangi-kamerayi-almalisin-2026",
  keyword="retro tarz fotoğraf kamerası",
  segment="Satın alma: Genel retro tarz kamera rehberi",
  tags="retro kamera, retro fotograf, ccd kamera, y2k estetik, vintage tarz, retrocameraland",
  meta_desc="Retro tarz fotograflar cekmek icin hangi kamerayi almalisin? Butce, deneyim seviyesi ve tarzina gore en uygun retro dijital kamerayi bu rehberle bul.",
  img_kw="retro style photography camera aesthetic warm tones",
  pin_hero="retro film aesthetic camera",
  faqs=[
    ("Retro tarz fotoğraf için en önemli kriter nedir?",
     "Cozunurluk veya megapiksel degil, sensorun renk karakteridir. CCD sensorlu eski dijital kompaktlar, sicak ve doygun bir renk islemesiyle 'retro tarz' dedigimiz gorunumu dogal olarak verir. Bunun disinda kolay kullanim ve tasinabilirlik de gunluk cekimi surdurmen icin onemlidir."),
    ("Yeni başlayanlar için en kolay retro kamera hangisi?",
     "Tam otomatik modu guclu, basit menulu ve hafif bir CCD kompakt en iyi baslangictir. Ayar ogrenmene gerek kalmadan kamerayi acip cekmen yeterlidir; retro renk karakteri zaten sensordan gelir."),
    ("Retro tarz için pahalı bir kamera şart mı?",
     "Hayir. Retro tarzin kaynagi sensorun yasi ve karakteri oldugu icin, uygun butceli 2000'ler CCD kompaktlari, cok daha pahali modern kameralardan daha 'retro' sonuc verir. Onemli olan fiyat degil, dogru sensor karakteridir."),
  ],
  body="""<p>"Retro tarz fotograflar cekmek istiyorum ama hangi kamerayi almaliyim?" sorusunun cevabi aslinda dusundugunden basit: pahali ve yeni bir kamera degil, karakterli bir sensore sahip dogru bir CCD kompakt ariyorsun. Bu rehberde deneyim seviyene ve butcene gore en mantikli secimleri anlatiyoruz.</p>

<h2>Retro Tarzda Aranan 3 Şey</h2>
<ul>
<li><strong>Renk karakteri:</strong> CCD sensorun sicak, doygun ve hafif grenli isleme tarzi.</li>
<li><strong>Kolay kullanim:</strong> Ayar ugrasmadan cekip anin icinde kalabilmek.</li>
<li><strong>Tasinabilirlik:</strong> Her an yaninda tasiyabilecegin kadar hafif ve kompakt olmasi.</li>
</ul>

<h2>Yeni Başlayanlar İçin: Kolay Otomatik Modeller</h2>
<p>İlk retro kameranda karmasik ayarlarla ugrasmak istemezsin. <a href="https://retrocameraland.com/products/nikon-coolpix-s3000">Nikon Coolpix S3000</a> basit menusu ve guvenilir otomatik moduyla "ac ve cek" rahatligi sunar. <a href="https://retrocameraland.com/products/samsung-style-st66">Samsung Style ST66</a> ise ince govdesi ve dokunmatik kontrolleriyle gunluk tasima icin pratik bir secenektir.</p>

<h2>Karakterli Renk Arayanlar İçin</h2>
<p>Daha belirgin bir retro doku istiyorsan, erken donem CCD modelleri tam aradigin sey. <a href="https://retrocameraland.com/products/fujifilm-finepix-jv310">Fujifilm FinePix JV310</a> dogal renk islemesiyle one cikar. <a href="https://retrocameraland.com/products/sanyo-xacti-cg20">Sanyo Xacti CG20</a> ise farkli bir govde tasarimi ve karakterli sonuclariyla koleksiyona ayri bir tarz katar.</p>

<h2>Kompakt ve Cepte Taşınan</h2>
<p>Her an yaninda tasiyabilecegin, cebe sigan bir model istiyorsan <a href="https://retrocameraland.com/products/sony-cyber-shot-dsc-t9">Sony Cyber-shot DSC-T9</a> ince govdesi ve guvenilir otomatik moduyla gunluk tasima icin idealdir. <a href="https://retrocameraland.com/products/hp-photosmart-r827">HP Photosmart R827</a> ise farkli bir renk profili arayanlar icin alternatif bir secimdir.</p>

<h2>Hızlı Seçim Rehberi</h2>
<ul>
<li><strong>İlk retro kameran:</strong> Nikon Coolpix S3000 veya Samsung Style ST66</li>
<li><strong>Belirgin retro renk:</strong> Fujifilm FinePix JV310, Sanyo Xacti CG20</li>
<li><strong>Cepte taşınan minimal:</strong> Sony Cyber-shot DSC-T9, HP Photosmart R827</li>
</ul>
"""))

# 3 ── FLASLI VINTAGE CEKIM ICIN HANGI KAMERAYI ALMALISIN (teknik satin alma) ─
POSTS.append(dict(
  title="Flaşlı Vintage Çekim İçin Hangi Kamerayı Almalısın? Satın Alma Rehberi",
  handle="flasli-vintage-cekim-icin-hangi-kamerayi-almalisin-satin-alma-rehberi",
  keyword="flaşlı vintage çekim kamerası",
  segment="Satın alma: Flaşlı vintage kamera (teknik kriterler)",
  tags="flasli kamera, vintage flas, ccd flas kamera, y2k flas estetigi, retro flas, retrocameraland",
  meta_desc="Flasli vintage cekim icin hangi kamerayi almalisin? Flas gucu, sarj suresi ve yakin mesafe performansina gore en iyi CCD flas kameralari rehberi.",
  img_kw="flash vintage ccd camera close range indoor y2k",
  pin_hero="flash photography vintage camera",
  faqs=[
    ("Flaşlı vintage kamerada nelere dikkat etmeliyim?",
     "Uc teknik ozellige bak: flas menzili (ne kadar uzaga isik atiyor), sarj/recycle suresi (iki flasli kare arasi bekleme) ve yakin mesafe odak performansi (30-50cm gibi yakin objelerde netlik). Bu ucu dengeli olan bir CCD kompakt, flasli vintage cekimde seni yarida birakmaz."),
    ("Her retro kameranın flaşı aynı mı çalışır?",
     "Hayir. Bazi modellerin flasi daha guclu ve genis acili, bazilarinin ise daha zayif ve dar menzillidir. Ayrica sarj suresi de modelden modele degisir; hizli ardisik kare cekmek istiyorsan kisa recycle sureli bir model tercih etmelisin."),
    ("Flaşlı çekim gündüz de işe yarar mı?",
     "Evet. 'Fill flash' teknigiyle gunduz de, ozellikle golgeli yuzlerde veya arka isik durumunda, flas devreye girip yuzu aydinlatir. Flasli vintage estetik sadece gece degil, gunduz ic mekan ve golgeli disari cekimlerde de kullanilabilir."),
  ],
  body="""<p>"Flasli vintage cekim icin hangi kamerayi almaliyim?" sorusuna dogru cevap vermek icin oncelikle hangi OCCASION'da kullanacagina degil, kameranin flas ile ilgili TEKNIK ozelliklerine bakman gerekir. (Gece ve parti gibi belirli bir ortam icin oneri ariyorsan <a href="https://retrocameraland.com/blogs/news/gece-parti-icin-en-iyi-retro-kamera-flasli-y2k-estetigi">gece & parti rehberimize</a> goz atabilirsin.) Bu yazida ise hangi kamerada olceceğin uc kritik flas ozelligini ve o kriterlere gore hangi modellerin one ciktigini anlatiyoruz.</p>

<h2>Flaş Alırken Bakılması Gereken 3 Teknik Özellik</h2>
<ul>
<li><strong>Flaş menzili:</strong> Isigin ne kadar uzaga ulastigi; genis mekanlarda kisa menzil yetersiz kalir.</li>
<li><strong>Şarj / recycle süresi:</strong> İki flasli kare arasindaki bekleme suresi; kisa olmasi ardisik kare cekmeni kolaylastirir.</li>
<li><strong>Yakın mesafe odak:</strong> 30-50cm gibi yakin objelerde netlik; detay ve urun cekimi icin kritik.</li>
</ul>

<h2>Güçlü ve Hızlı Flaş İsteyenler İçin</h2>
<p><a href="https://retrocameraland.com/products/casio-exilim-ex-z4">Casio Exilim EX-Z4</a> hizli sarj suresi ve guvenilir flasiyla ardisik kareler cekmek isteyenler icin pratik bir secimdir. <a href="https://retrocameraland.com/products/kodak-slice-r502">Kodak Slice R502</a> ise genis dokunmatik ekrani ve dengeli flas performansiyla hem kolay kullanim hem guclu isik sunar.</p>

<h2>Yakın Mesafe Detay ve Ürün Çekimi İçin</h2>
<p>Masaustu detay, yemek veya urun tarzi yakin cekimlerde flasin yakin mesafe performansi belirleyicidir. <a href="https://retrocameraland.com/products/sanyo-xacti-vpc-c5">Sanyo Xacti VPC-C5</a> yakin mesafede dengeli isik dagilimiyla bu tur detay kareler icin uygun bir secimdir.</p>

<h2>Günlük Kullanımda Pratik Flaş</h2>
<p>Her gun yaninda tasiyip aninda flasli kare cekmek istiyorsan pratik ve hafif bir model onemlidir. <a href="https://retrocameraland.com/products/traveler-dc-830">Traveler DC-830</a> basit yapisi ve guvenilir flasiyla gunluk kullanim icin dusunulmus, karmasik olmayan bir secimdir.</p>

<h2>Hızlı Seçim Rehberi</h2>
<ul>
<li><strong>Ardışık hızlı kare:</strong> Casio Exilim EX-Z4, Kodak Slice R502</li>
<li><strong>Yakın mesafe / detay:</strong> Sanyo Xacti VPC-C5</li>
<li><strong>Günlük pratik kullanım:</strong> Traveler DC-830</li>
</ul>
"""))

# 4 ── GUNLUK ANILARINI KAYDETMEK ICIN HANGI KAMERAYI ALMALISIN ───────────────
POSTS.append(dict(
  title="Günlük Anılarını Kaydetmek İçin Hangi Kamerayı Almalısın?",
  handle="gunluk-anilarini-kaydetmek-icin-hangi-kamerayi-almalisin",
  keyword="günlük kullanım için kamera",
  segment="Satın alma: Günlük anı / aile kamerası",
  tags="gunluk kamera, aile anilari, kolay kullanim kamera, otomatik kamera, retro gunluk, retrocameraland",
  meta_desc="Gunluk anilarini, aile ve ev icini kaydetmek icin hangi kamerayi almalisin? Kolay kullanimli, hep yaninda tasiyabilecegin retro kameralar rehberi.",
  img_kw="everyday camera daily life family snapshot easy simple",
  pin_hero="everyday casual snapshot camera",
  faqs=[
    ("Günlük kullanım için en önemli özellik nedir?",
     "Yuksek cozunurluk veya zoom degil; kolay otomatik mod, hafiflik ve hizli acilis suresidir. Gunluk anilar cogu zaman aniden yasanir; kamera acilip cekim yapana kadar an gecmis olabilir. Basit ve hizli bir kamera, karmasik ama yavas bir kameradan cok daha degerlidir."),
    ("Telefon yerine günlük anılar için neden ayrı bir kamera?",
     "Telefon fotograflari yillar icinde binlerce baska dosyanin arasinda kaybolur ve hepsi ayni 'mukemmel ama duygusuz' tonda cikar. Ayri bir retro kamera hem o anin kaydini fiziksel/ayri bir yerde tutar hem de sicak renk karakteriyle aniyi daha 'hissedilir' kilar."),
    ("Çocuklu aileler için dayanıklı/kolay bir model var mı?",
     "Evet. Basit menuli, agir olmayan ve otomatik moda guvenen kompakt modeller, cocuklu ev ortaminda hem kullanim kolayligi hem de dusme/carpma riskine karsi daha az endise saglar. Karmasik ayarlari olmayan modelleri tercih etmek, gunluk kullanimda stresi azaltir."),
  ],
  body="""<p>Gunluk hayatin en degerli anlari genelde plansiz gelir: sabah kahvaltisi, evcil hayvanin komik hali, cocugun ilk adimi. Bu anlari yakalamak icin karmasik bir kameraya degil, hizli acilan, kolay kullanilan ve <strong>gunluk anilari kaydetmek icin</strong> tasarlanmis gibi hisseden basit bir kompakta ihtiyacin var. Bu rehberde ev ve gunluk yasam icin en uygun retro kameralari topladik.</p>

<h2>Günlük Kamerada Aranan 3 Şey</h2>
<ul>
<li><strong>Kolay otomatik mod:</strong> Ayar dusunmeden cekip anin icinde kalmak.</li>
<li><strong>Hafiflik:</strong> Cantada veya cepte tasimasi yormamali.</li>
<li><strong>Hızlı açılış:</strong> Ani kacirmamak icin kamera saniyeler icinde hazir olmali.</li>
</ul>

<h2>Her Zaman Cebinde: Ultra Kompaktlar</h2>
<p>Gunluk tasima icin ince ve hafif bir govde sart. <a href="https://retrocameraland.com/products/samsung-style-st66">Samsung Style ST66</a> ince yapisi ve dokunmatik kontrolleriyle her gun cebe atip cikarabilecegin pratik bir modeldir. <a href="https://retrocameraland.com/products/nikon-coolpix-s3000">Nikon Coolpix S3000</a> ise basit menusu ve guvenilir otomatik moduyla ayni rahatligi sunar.</p>

<h2>Aile ve Ev İçi İçin: Kolay Otomatik Modeller</h2>
<p>Ev icinde, kutlamalarda veya aile bulusmalarinda hizli ve sonuc odakli bir kamera istersin. <a href="https://retrocameraland.com/products/hp-photosmart-r827">HP Photosmart R827</a> genis dokunmatik ekrani ve kolay menusuyle aile fotograflarini pratik bicimde toplar.</p>

<h2>Çocuklu Evler İçin Dayanıklı Seçim</h2>
<p>Cocuklu ev ortaminda dayaniklilik ve basitlik on plana cikar. <a href="https://retrocameraland.com/products/olympus-sp-700">Olympus SP-700</a> saglam govdesi ve kolay otomatik moduyla cocuklarin buyume anlarini stressiz bicimde kaydetmeni saglar.</p>

<h2>Hızlı Seçim Rehberi</h2>
<ul>
<li><strong>Cepte her an tasınan:</strong> Samsung Style ST66, Nikon Coolpix S3000</li>
<li><strong>Aile & ev içi:</strong> HP Photosmart R827</li>
<li><strong>Çocuklu ev / dayanıklı:</strong> Olympus SP-700</li>
</ul>
"""))

# 5 ── KOLAYCA FOTOGRAF CEKIP TELEFONA AKTARMAK (wifi + kart okuyucu) ─────────
POSTS.append(dict(
  title="Kolayca Fotoğraf Çekip Telefona Aktarmak İçin Hangi Kamera?",
  handle="kolayca-fotograf-cekip-telefona-aktarmak-icin-hangi-kamera",
  keyword="kamera fotoğrafı telefona aktarma",
  segment="Satın alma: Kolay telefona aktarım (wifi / kart okuyucu)",
  tags="wifi kamera, telefona aktarim, kart okuyucu, samsung wifi kamera, otg aktarici, retrocameraland",
  meta_desc="Cektigin fotograflari kolayca telefonuna aktarmak mi istiyorsun? Wifi'li retro kameralar ve her kamerayla calisan kart okuyucu/aktarici cozumler rehberi.",
  img_kw="wifi camera transfer phone card reader adapter easy",
  pin_hero="wifi camera phone transfer",
  faqs=[
    ("Hangi retro kameralarda wifi ile telefona aktarım var?",
     "Samsung WB350F ve Samsung NX2000 dahili wifi ozelligine sahiptir; Samsung'un mobil uygulamasi uzerinden cektigin fotograflari kabloya gerek kalmadan telefonuna aktarabilirsin. Bu, retro kompakt kameralar arasinda nadir bulunan pratik bir ozelliktir."),
    ("Wifi'siz bir retro kamerayla fotoğraf nasıl telefona aktarılır?",
     "Kameranin hafiza kartini (SD, microSD veya xD/CF gibi eski formatlar) cikarip bir kart okuyucu/OTG aktarici ile telefona takarsin; fotograflar saniyeler icinde telefon galerine aktarilir. Bu yontem wifi'si olmayan TUM retro kameralarda calisir, yani universal bir cozumdur."),
    ("Aktarım için ekstra bir şey almam gerekir mi?",
     "Kameran wifi'li degilse evet, ucuz ve kucuk bir kart okuyucu/adaptor almani oneririz. Ozellikle eski format kartlar (xD, CF, MS) icin tum-bir-arada aktaricilar, herhangi bir retro kamerayi telefonuna kablosuz gibi hizli baglar."),
  ],
  body="""<p>"Kolayca fotograf cekip telefonuma aktarmak istiyorum" diyen biriysen, cevap kameranin kendisi kadar dogru aksesuari secmekte de gizli. Iki yol var: kameranin dahili wifi'si ile direkt aktarim, ya da her kamerayla calisan bir kart okuyucu/adaptor ile aninda aktarim. Bu rehberde ikisini de, hangisinin sana uygun oldugunu anlatiyoruz.</p>

<h2>İki Yol Var: Wifi mi, Kart Okuyucu mu?</h2>
<p><strong>Dahili wifi'li kameralar</strong> fotografi cektigin an telefonuna kablosuz aktarir; en pratik ama sadece belirli modellerde bulunan bir ozelliktir. <strong>Kart okuyucu/adaptor</strong> ise HERHANGI bir retro kamerayla calisir: karti cikar, okuyucuya tak, telefona bagla, saniyeler icinde galeride. Wifi'li bir kamera almasan bile bu ikinci yontemle ayni hizli sonucu alirsin.</p>

<h2>Dahili Wifi'li Modeller: Direkt Aktarım</h2>
<p><a href="https://retrocameraland.com/products/samsung-wb350f">Samsung WB350F</a> dahili wifi'si sayesinde cektigin kareyi anlik olarak telefonuna gonderebilir; ayrica guclu zoomuyla gunluk ve seyahat kullanimina da uygundur. <a href="https://retrocameraland.com/products/samsung-nx2000">Samsung NX2000</a> ise wifi'nin yaninda dokunmatik ekrani ve degistirilebilir lensiyle daha ileri seviye bir secenek sunar; ikisi de kablo aramadan direkt paylasima izin verir.</p>

<h2>Wifi'siz Kameralar İçin: Universal Aktarım Çözümü</h2>
<p>Elindeki veya almayi dusundugun kamera wifi'li degilse endise etme; <a href="https://retrocameraland.com/products/y2k-digicam-fotograf-video-aktarici-xd-cf-sd-ms-destekli-all-in-one-kart-okuyucu">Y2K Digicam Fotoğraf/Video Aktarıcı</a> tam olarak bunun icin var: xD, CF, SD ve MS gibi eski format kartlarin HEPSINI destekleyen bir all-in-one kart okuyucu. Daha standart SD/microSD kartlar icin <a href="https://retrocameraland.com/products/usb-c-3-in-1-kart-okuyucu-sd-microsd">USB-C 3'ü 1 Arada Kart Okuyucu</a> veya <a href="https://retrocameraland.com/products/microsd-sd-kart-okuyucu-yuksek-hizli-tasinabilir-kart-okuma-adaptoru">Type-C/USB SD-MicroSD Kart Okuyucu</a> telefonuna dogrudan takilan, cok ucuz ve hizli bir cozumdur.</p>

<h2>Hangi Yöntem Sana Uygun?</h2>
<ul>
<li><strong>Kablosuz, anlik paylasim istiyorsan:</strong> Samsung WB350F veya Samsung NX2000 (dahili wifi)</li>
<li><strong>Elindeki/alacagin herhangi bir retro kamera icin:</strong> Y2K Digicam Aktarici veya USB-C Kart Okuyucu (universal, ucuz)</li>
</ul>
<p>İkisini birlikte de dusunebilirsin: wifi'li bir kamera alsan bile, yedek olarak cebinde ucuz bir kart okuyucu tasimak, wifi baglanti sorunu yasadiginda seni hic bekletmez.</p>
"""))

# ── finder CTA satirlari (her bloga ozel) ─────────────────────────────────────
CTA_LINES = {
  POSTS[0]["handle"]: "CCD kompakt mi, retro mirrorless mi? Birkac soruyla hangi vintage kamera turunun sana uygun oldugunu ogren.",
  POSTS[1]["handle"]: "Butcen ve deneyim seviyene gore en uygun retro tarz kamerayi 6 kisa soruyla saniyeler icinde bul.",
  POSTS[2]["handle"]: "Flas gucu, mesafe ve kullanim tarzina gore sana en uygun flasli retro kamerayi birlikte secelim.",
  POSTS[3]["handle"]: "Gunluk anilarini en kolay yakalayacagin kamerayi profiline gore birkac soruyla bulalim.",
  POSTS[4]["handle"]: "Wifi mi, kart okuyucu mu? Kullanim tarzina gore en pratik aktarim cozumunu birlikte bulalim.",
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
        out = f"/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/b69db648-5a59-420b-9e27-7493a363a0da/scratchpad/preview_{p['handle']}.html"
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
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

    log(f"{'DRY-RUN' if args.dry else 'CANLI YAYIN'} — {len(POSTS)} vintage-soru blogu")
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
