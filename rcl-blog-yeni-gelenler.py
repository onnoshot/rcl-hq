#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL "Yeni Gelenler" Blog Seti  (hub + 4 marka spoke)
====================================================
Siteye son eklenen 15 retro dijital kamera uzerine, dogrulanmis teknik
bilgiyle yazilmis, yuksek SEO + AI-arama (AEO) optimizasyonlu bloglar.

Yapi (hub-and-spoke ic baglanti):
  HUB   : 15 modelin tam rehberi (tum urunlere + 4 spoke'a link)
  SPOKE : Sony CCD / Fujifilm Z serisi / Canon kompakt klasikleri / Samsung NX2000 aynasiz

Her blog:
  - H1 + uzun-kuyruk SEO basligi, meta aciklama, SEO metafield
  - H2 yapisi, karsilastirma tablosu, hizli secim
  - FAQ + JSON-LD (Article + FAQPage + BreadcrumbList)
  - Gercek stok urune deep-link (/products/...)
  - Diger bloglara ic baglanti (hub<->spoke)
  - Kararsizlar icin finder CTA -> /pages/hangi-kamera-bana-uygun
  - Daha once kullanilmamis Pinterest gorseli + SOCIAL_BLOCK

Kullanim:
  python3 rcl-blog-yeni-gelenler.py --dry   # onizleme (yayinlamaz)
  python3 rcl-blog-yeni-gelenler.py         # CANLI yayinla
"""
import sys, json, argparse
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
BLOG_URL = f"{SITE}/blogs/news"
FINDER   = f"{SITE}/pages/hangi-kamera-bana-uygun"
LOGO     = f"{SITE}/cdn/shop/files/retrocameraland_banner.jpg"
import time
TODAY    = time.strftime("%Y-%m-%d")
SCRATCH  = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/3fe01917-04fa-4237-875d-a5b9095fcb93/scratchpad"

def P(handle):  # urun deep-link
    return f"{SITE}/products/{handle}"

# ── finder CTA ────────────────────────────────────────────────────────────────
def finder_cta(line):
    return (
      '<div style="background:linear-gradient(135deg,#15110d,#2a2018);color:#fff;'
      'border-radius:18px;padding:34px 28px;margin:46px 0;text-align:center;">'
      '<div style="font-size:13px;letter-spacing:.16em;font-weight:700;color:#e9836f;'
      'text-transform:uppercase;margin-bottom:10px;">AI KAMERA ESLESTIRICI</div>'
      '<h3 style="margin:0 0 12px;font-size:24px;font-weight:800;color:#fff;line-height:1.2;">'
      'Hala kararsiz misin?</h3>'
      f'<p style="margin:0 auto 22px;max-width:520px;font-size:16px;line-height:1.6;color:#d8d0c8;">{line}</p>'
      f'<a href="{FINDER}" style="display:inline-block;background:#d8472f;color:#fff;'
      'padding:15px 34px;border-radius:100px;text-decoration:none;font-weight:700;font-size:16px;">'
      'Sana ozel kamerani bul &#8594;</a>'
      '<div style="margin-top:14px;font-size:13px;color:#9a9088;">'
      '6 kisa soru &bull; ~1 dakika &bull; ucretsiz &bull; uyelik yok</div>'
      '</div>'
    )

# ── ic baglanti kutusu (ilgili yazilar) ──────────────────────────────────────
def related_box(items):
    lis = "".join(
        f'<li style="margin:8px 0;"><a href="{BLOG_URL}/{h}" '
        f'style="color:#c0392b;font-weight:600;text-decoration:none;">{t}</a></li>'
        for h, t in items)
    return (
      '<div style="background:#f8f4f0;border:1px solid #ece3d8;border-radius:14px;'
      'padding:22px 26px;margin:40px 0;">'
      '<div style="font-size:13px;letter-spacing:.12em;font-weight:700;color:#9a7b55;'
      'text-transform:uppercase;margin-bottom:10px;">İLGİLİ REHBERLER</div>'
      f'<ul style="margin:0;padding-left:18px;font-size:16px;line-height:1.5;">{lis}</ul>'
      '</div>'
    )

# ── JSON-LD ───────────────────────────────────────────────────────────────────
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
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q,
                           "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList",
             "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": BLOG_URL},
                {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    def tag(d): return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
    return "\n" + tag(article) + tag(faq) + tag(crumb)

def faq_html(faqs):
    out = ['<h2>Sıkça Sorulan Sorular</h2>']
    for q, a in faqs:
        out.append(f'<h3>{q}</h3>\n<p>{a}</p>')
    return "\n".join(out)

def closer(keyword):
    return (
      '<h2>Doğru Kamerayı Seçmek: Test Edilmiş ve Stoktan</h2>'
      f'<p>RetroCameraLand\'da listelenen tüm {keyword} seçenekleri, satıştan önce '
      'fonksiyon testinden geçer ve kondisyonu şeffaf biçimde paylaşılır; yani aldığın kamera '
      'sadece güzel görünmez, çalışır. <a href="' + SITE + '/collections/all">Tüm koleksiyonu</a> '
      'inceleyebilir ya da kararsızsan <a href="' + FINDER + '">AI Kamera Eşleştirici</a> ile '
      'birkaç kısa soruyu yanıtlayıp profiline en uygun üç modeli yüzdesel uyum skoruyla '
      'görebilirsin.</p>'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  HANDLE'LAR (hub<->spoke ic baglanti icin)
# ══════════════════════════════════════════════════════════════════════════════
H_HUB    = "yeni-gelen-retro-dijital-kameralar-2026-15-model-rehberi"
H_SONY   = "sony-cybershot-ccd-rehberi-t20-t300-w150"
H_FUJI   = "fujifilm-finepix-z-serisi-y2k-dokunmatik-digicam-rehberi"
H_CANON  = "canon-dijital-kompakt-klasikleri-ixus-ixy-elph-g7"
H_NX     = "butceyle-aynasiz-samsung-nx2000-lens-degistirilebilir-retro"

T_HUB   = "Yeni Gelen Retro Dijital Kameralar (2026): 15 Modelin Rehberi"
T_SONY  = "Sony Cyber-shot CCD Rehberi: T20, T300 ve W150 Karşılaştırması"
T_FUJI  = "Fujifilm FinePix Z Serisi: Y2K Dokunmatik Digicam Rehberi"
T_CANON = "Canon Dijital Kompakt Klasikleri: IXUS, IXY, ELPH ve G7"
T_NX    = "Bütçeyle Aynasız: Samsung NX2000 ile Lens Değiştirilebilir Retro"

POSTS = []

# ══════════════════════════════════════════════════════════════════════════════
# 1 ── HUB : 15 MODELIN TAM REHBERI
# ══════════════════════════════════════════════════════════════════════════════
POSTS.append(dict(
  handle=H_HUB, title="Retrocameraland'e Yeni Gelen Retro Dijital Kameralar (2026): 15 Modelin Tam Rehberi",
  keyword="yeni retro dijital kamera",
  img_kw="vintage digicam collection ccd cameras y2k aesthetic flatlay",
  pin_hero="sony cybershot ccd",
  tags="yeni retro kamera 2026, ccd dijital kamera, y2k kamera, digicam, sony fujifilm canon, retro fotograf makinesi, retrocameraland",
  meta_desc="2026'da Retrocameraland'e yeni gelen 15 retro dijital kamera: Sony, Fujifilm, Canon, Samsung ve Panasonic CCD/CMOS modelleri. Hangi kamera kime uygun, fiyat ve özelliklerle tam rehber.",
  related=[(H_SONY, T_SONY), (H_FUJI, T_FUJI), (H_CANON, T_CANON), (H_NX, T_NX)],
  faqs=[
    ("2026'da en çok aranan retro dijital kamera tipi hangisi?",
     "Y2K estetiği nedeniyle CCD sensörlü kompakt \"digicam\"ler en çok aranan tip. CCD sensör, sıcak ten tonları ve hafif grenle modern telefonların veremediği nostaljik bir doku verir. Bütçesi geniş olup gerçek görüntü kalitesi isteyenler ise APS-C aynasız Samsung NX2000 gibi lens değiştirilebilir modellere yöneliyor."),
    ("CCD ve CMOS retro kamera arasındaki fark nedir?",
     "CCD sensörler (Sony T-W serisi, Fujifilm Z90, Canon IXUS gibi) klasik sıcak Y2K rengini ve karakterli grenini verir; gündüz ve iyi ışıkta en güçlüdür. CMOS sensörler (Canon ELPH 300 HS, Lumix TZ91, Samsung NX2000) düşük ışıkta daha temiz çeker ve genelde HD/4K video sunar. Nostaljik doku için CCD, gece performansı ve video için CMOS tercih edilir."),
    ("Yeni başlayan biri bu 15 model arasından hangisini almalı?",
     "Yeni başlayanlar için kullanımı kolay, otomatik modu güçlü bir CCD kompakt idealdir: Sony Cyber-shot W150, Fujifilm FinePix Z90 veya Panasonic LS70 \"tak ve çek\" rahatlığı sunar. Daha ileri gitmek ve lens değiştirmek isteyenler için Samsung NX2000 bütçe dostu bir başlangıçtır."),
    ("Bu kameralar çalışır durumda mı, garantili mi?",
     "Evet. RetroCameraLand'da listelenen her kamera satıştan önce fonksiyon testinden geçer ve kozmetik/teknik kondisyonu şeffaf biçimde paylaşılır. Amaç, sadece güzel görünen değil, yıllarca çalışan bir kamera teslim etmektir."),
  ],
  body="""<p>RetroCameraLand koleksiyonuna 2026'da 15 yeni retro dijital kamera eklendi: Sony, Fujifilm, Canon, Samsung, Panasonic ve Olympus'tan, çoğu CCD sensörlü klasik kompakt, bir tanesi ise APS-C aynasız bir sistem kamerası. Bu rehberde her modeli kullanım amacına göre grupladık; <strong>hangi kameranın kime uygun</strong> olduğunu hızlıca görebilir, ilgini çekeni tek tıkla inceleyebilirsin. Markaya özel detaylı karşılaştırmalar için bölüm sonlarındaki rehberlere göz at.</p>

<h2>Hangi Kamera Kime Uygun? (Hızlı Tablo)</h2>
<table style="width:100%%;border-collapse:collapse;margin:20px 0;font-size:15px;">
<tr style="background:#15110d;color:#fff;"><th style="padding:11px;text-align:left;">İhtiyacın</th><th style="padding:11px;text-align:left;">Öne Çıkan Modeller</th></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Y2K dokunmatik digicam estetiği</td><td style="padding:10px;border-bottom:1px solid #eee;">Fujifilm Z90, Z700EXR, Sony T300</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Günlük & başlangıç (tak-çek)</td><td style="padding:10px;border-bottom:1px solid #eee;">Sony W150, Panasonic LS70</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Seyahat & uzun zoom</td><td style="padding:10px;border-bottom:1px solid #eee;">Panasonic Lumix TZ91 (30x), Olympus VR-340 (10x)</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Gece & parti (temiz, az gren)</td><td style="padding:10px;border-bottom:1px solid #eee;">Canon ELPH 300 HS (CMOS)</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Manuel kontrol / meraklı</td><td style="padding:10px;border-bottom:1px solid #eee;">Canon PowerShot G7</td></tr>
<tr><td style="padding:10px;">Lens değiştirilebilir / DSLR hissi</td><td style="padding:10px;">Samsung NX2000 (APS-C aynasız)</td></tr>
</table>

<h2>Sony Cyber-shot: CCD Sıcaklığı ve Zeiss Lens</h2>
<p>Yeni gelen üç Sony, klasik Cyber-shot çizgisinin farklı kullanıcılarına hitap ediyor. <a href="%s">Sony Cyber-shot DSC-T20</a> (2007, 8.1 MP CCD, kayan kapaklı ultra-ince gövde) cebe giren retro şıklık isteyenler için. <a href="%s">Sony Cyber-shot DSC-T300</a> (2008, 10.1 MP CCD, devasa 3.5&quot; dokunmatik ekran ve 5x Carl Zeiss zoom) dönemin amiral gemisi dokunmatik kompaktı. <a href="%s">Sony Cyber-shot DSC-W150</a> (2008, 8.1 MP CCD, 30mm geniş açı Zeiss + optik vizör) ise her işe uygun, ekonomik başlangıç modeli. Üçünün ayrıntılı karşılaştırması için Sony rehberimize bak.</p>

<h2>Fujifilm FinePix Z: Y2K Dokunmatik Digicam'in Kalbi</h2>
<p>Fujifilm'in FinePix Z serisi, sosyal medyayı saran Y2K dokunmatik digicam estetiğinin tam merkezinde. <a href="%s">Fujifilm FinePix Z700EXR</a> (2010, 12 MP Super CCD EXR, 3.5&quot; dokunmatik) ve <a href="%s">Fujifilm FinePix Z90</a> (2011, 14 MP CCD, kayan kapaklı 3.0&quot; dokunmatik) sıcak film tonu ve pratik dokunmatik arayüzleriyle selfie ve sosyal paylaşım dostu. Daha erken dönem, fiziksel tuşlu bir koleksiyon parçası arayanlar için <a href="%s">Fujifilm FinePix V10</a> (2006, 5.1 MP Super CCD HR) otantik mid-2000s dokusu sunar.</p>

<h2>Canon: Ultra-İnce IXUS'tan Manuel Kontrollü G7'ye</h2>
<p>Canon tarafı geniş bir yelpaze sunuyor. <a href="%s">Canon Digital IXUS i</a> (2003, 4 MP CCD) kibrit kutusu boyutunda, zoomsuz, en diskret Y2K cep kamerası. <a href="%s">Canon IXY 1000</a> (2006, 10 MP CCD, titanyum gövde) premium yapı kalitesi isteyen koleksiyoncular için. <a href="%s">Canon PowerShot ELPH 300 HS</a> (2011, 12 MP BSI CMOS) gece ve partide daha temiz, az grenli sonuç ve Full HD video verir. <a href="%s">Canon PowerShot G7</a> (2006, 10 MP CCD) ise fiziksel ISO çarkı, tam manuel modlar ve hot shoe ile meraklı kullanıcının kamerası. Detaylar için Canon rehberine göz at.</p>

<h2>Seyahat ve Zoom: Panasonic ve Olympus</h2>
<p>Tek kamerayla geniş açıdan uzak detaya kadar her şeyi çekmek isteyenler için zoom önemli. <a href="%s">Panasonic Lumix DC-TZ91</a> (2017, 20.3 MP BSI CMOS) listedeki en modern makine: 30x optik zoom (24-720mm), 4K video, elektronik vizör ve eğilebilir dokunmatik ekran. <a href="%s">Olympus VR-340</a> (2012, 16 MP CCD) ince gövdede 10x zoom ile cep dostu bir gezi kamerası. <a href="%s">Panasonic Lumix DMC-LS70</a> (2007, 7.2 MP CCD) ise sade, bütçe dostu bir retro digicam.</p>

<h2>Lens Değiştirilebilir Tek Model: Samsung NX2000</h2>
<p>Bu 15 modelin içindeki tek sistem kamerası: <a href="%s">Samsung NX2000</a> (2013, 20.3 MP APS-C CMOS). Diğerlerinin aksine lens değiştirilebilir; büyük APS-C sensörü sayesinde gerçek arka plan bulanıklığı (bokeh), geniş dinamik aralık ve düşük ışıkta net sonuç verir. \"Bütçeyle DSLR kalitesi\" arayanlar için ayrı bir kategoride. Ayrıntılar için aynasız rehberimize bak.</p>
""" % (
    P("sony-cybershot-dsc-t20"), P("sony-cybershot-dsc-t300"), P("sony-cybershot-dsc-w150"),
    P("fujifilm-finepix-z700exr"), P("fujifilm-finepix-z90-digicam"), P("fujifilm-finepix-v10"),
    P("canon-ixus-i"), P("canon-ixy-1000"), P("canon-powershot-elph-300-hs"), P("canon-powershot-g7"),
    P("panasonic-lumix-dc-tz91"), P("olympus-vr-340"), P("panasonic-dmc-ls70"),
    P("samsung-nx2000"),
  ),
  cta_line="15 model arasında kaybolduysan dert değil: 6 kısa soruyla profiline en uygun retro kamerayı yüzdesel uyum skoruyla bulalım.",
))

# ══════════════════════════════════════════════════════════════════════════════
# 2 ── SONY SPOKE
# ══════════════════════════════════════════════════════════════════════════════
POSTS.append(dict(
  handle=H_SONY, title="Sony Cyber-shot CCD Rehberi: DSC-T20, T300 ve W150 Karşılaştırması (2026)",
  keyword="Sony Cyber-shot CCD kamera",
  img_kw="sony cybershot ccd digicam y2k carl zeiss",
  pin_hero="Sony Cybershot DSC-W150",
  tags="sony cybershot, ccd dijital kamera, carl zeiss lens, dsc-t300 dokunmatik, y2k kamera, sony w150, retrocameraland",
  meta_desc="Sony Cyber-shot DSC-T20, T300 ve W150 arasındaki fark nedir, hangisini almalısın? CCD sensör, Carl Zeiss zoom ve dokunmatik ekran karşılaştırmasıyla 2026 alım rehberi.",
  related=[(H_HUB, T_HUB), (H_FUJI, T_FUJI), (H_CANON, T_CANON)],
  faqs=[
    ("Sony DSC-T300 ile DSC-W150 arasındaki fark nedir, hangisini almalıyım?",
     "T300 daha premium: 10.1 MP CCD, 3.5\" tam dokunmatik ekran ve kayan metal kapaklı ince gövde; parti, sosyal anlar ve dokunmatik kullanımı sevenler için. W150 daha ekonomik ve çok yönlü: 8.1 MP CCD, 30mm geniş açı Carl Zeiss lens ve optik vizör; günlük her işe uygun, vizör sevenler ve başlangıç için ideal. Lüks dokunmatik istiyorsan T300, geniş açı ve değer istiyorsan W150."),
    ("Sony Cyber-shot T20 dokunmatik ekranlı mı?",
     "Hayır. DSC-T20 (2007) fiziksel tuşlu, 2.5\" LCD'li ince bir modeldir; dokunmatik ekran T-serisinin sonraki modeli T300 ile gelir. T20'yi seçenlerin çoğu fiziksel tuş kontrolünü ve daha kompakt gövdeyi tercih eder."),
    ("Bu Sony modelleri hangi sensöre sahip, neden CCD önemli?",
     "Üçü de Sony'nin Super HAD CCD sensörünü ve Carl Zeiss Vario-Tessar lensini kullanır. CCD sensör, sıcak ten tonları, doygun renkler ve o karakteristik Y2K flaş estetiğini doğal olarak verir; bu yüzden modern telefon karelerinden hemen ayrışan nostaljik bir doku elde edersin."),
    ("Gece ve parti fotoğrafı için bu Sony'ler iyi mi?",
     "Evet, özellikle dahili flaşla çekilen yakın kareler o klasik Y2K parti dokusunu verir. CCD sensör nedeniyle yüksek ISO'da bir miktar gren olur, ama bu gren retro estetiğin bir parçasıdır. Daha temiz gece sonucu isteyenler CMOS modellere (ör. Canon ELPH 300 HS) bakabilir."),
  ],
  body="""<p>Sony Cyber-shot, 2000'lerin en sevilen kompakt kamera serilerinden biri ve CCD sensörü ile Carl Zeiss lensi sayesinde bugün Y2K estetiğinin en güvenilir kaynaklarından. RetroCameraLand'a yeni gelen üç model -<strong>DSC-T20, DSC-T300 ve DSC-W150</strong>- aynı aileden gelse de farklı kullanıcılara hitap ediyor. Bu rehberde üçünü yan yana koyup hangisinin sana uygun olduğunu netleştiriyoruz.</p>

<h2>Üçü Bir Arada: Hızlı Karşılaştırma</h2>
<table style="width:100%%;border-collapse:collapse;margin:20px 0;font-size:15px;">
<tr style="background:#15110d;color:#fff;"><th style="padding:11px;text-align:left;">Model</th><th style="padding:11px;text-align:left;">Yıl</th><th style="padding:11px;text-align:left;">Sensör</th><th style="padding:11px;text-align:left;">Zoom</th><th style="padding:11px;text-align:left;">Ekran</th></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">DSC-T20</td><td style="padding:10px;border-bottom:1px solid #eee;">2007</td><td style="padding:10px;border-bottom:1px solid #eee;">8.1 MP CCD</td><td style="padding:10px;border-bottom:1px solid #eee;">3x Zeiss</td><td style="padding:10px;border-bottom:1px solid #eee;">2.5&quot; (tuşlu)</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">DSC-T300</td><td style="padding:10px;border-bottom:1px solid #eee;">2008</td><td style="padding:10px;border-bottom:1px solid #eee;">10.1 MP CCD</td><td style="padding:10px;border-bottom:1px solid #eee;">5x Zeiss</td><td style="padding:10px;border-bottom:1px solid #eee;">3.5&quot; dokunmatik</td></tr>
<tr><td style="padding:10px;">DSC-W150</td><td style="padding:10px;">2008</td><td style="padding:10px;">8.1 MP CCD</td><td style="padding:10px;">5x Zeiss (30mm geniş)</td><td style="padding:10px;">2.7&quot; + vizör</td></tr>
</table>

<h2>Sony DSC-T20: Cebe Giren İnce Klasik</h2>
<p><a href="%s">Sony Cyber-shot DSC-T20</a>, kayan kapaklı T-serisi tasarımının kompakt bir temsilcisi. 8.1 MP Super HAD CCD ve 3x Carl Zeiss Vario-Tessar lensiyle sıcak, doygun renkler verir. Dokunmatik değil; fiziksel tuş kontrolünü sevenler ve mümkün olan en ince gövdeyi isteyenler için ideal. Super SteadyShot stabilizasyonu, gün içi anlık karelerde netliği korur. Cebinde taşıyıp her an çıkarabileceğin bir günlük kamera arıyorsan T20 mantıklı bir seçim.</p>

<h2>Sony DSC-T300: Dokunmatik Amiral Gemisi</h2>
<p><a href="%s">Sony Cyber-shot DSC-T300</a>, serinin üst segment modeli. Dönemin en büyük ekranlarından biri olan 3.5&quot; geniş dokunmatik LCD ile neredeyse tamamen dokunarak kullanılır. 10.1 MP CCD ve 5x Carl Zeiss zoom, hem geniş sahneleri hem uzaktaki detayı toparlar; Smile Shutter (gülümseme algılayınca otomatik çekim) gibi özellikleriyle sosyal anlar için eğlencelidir. Lüks bir dokunmatik retro kamera deneyimi isteyenlerin ilk durağı.</p>

<h2>Sony DSC-W150: Geniş Açılı, Vizörlü Çok Yönlü</h2>
<p><a href="%s">Sony Cyber-shot DSC-W150</a>, W-serisinin dengeli ve ekonomik temsilcisi. 8.1 MP CCD ve 30mm'den başlayan geniş açı Carl Zeiss lensiyle manzara, grup ve iç mekan karelerinde rahat eder. W-serisinin önemli avantajı optik vizör: güneşli günlerde ekran zorlandığında vizörden net kadrajlama yaparsın. \"Tak ve çek\" rahatlığı ve geniş açı isteyen başlangıç kullanıcısı için en mantıklısı.</p>

<h2>Hangisini Almalısın? Hızlı Karar</h2>
<ul>
<li><strong>En ince, fiziksel tuşlu klasik:</strong> DSC-T20</li>
<li><strong>Büyük dokunmatik ekran, premium his, parti/sosyal:</strong> DSC-T300</li>
<li><strong>Geniş açı, vizör, ekonomik her-işe-uygun:</strong> DSC-W150</li>
</ul>
""" % (P("sony-cybershot-dsc-t20"), P("sony-cybershot-dsc-t300"), P("sony-cybershot-dsc-w150")),
  cta_line="T20, T300, W150... Hangi Sony sana göre? Birkaç soruyla tarzına en uygun CCD kamerayı senin için seçelim.",
))

# ══════════════════════════════════════════════════════════════════════════════
# 3 ── FUJIFILM SPOKE
# ══════════════════════════════════════════════════════════════════════════════
POSTS.append(dict(
  handle=H_FUJI, title="Fujifilm FinePix Z Serisi: Y2K Dokunmatik Digicam Rehberi (Z90, Z700EXR, V10)",
  keyword="Fujifilm FinePix Y2K dokunmatik kamera",
  img_kw="fujifilm finepix z y2k touchscreen digicam pink aesthetic",
  pin_hero="Fujifilm Finepix Z90",
  tags="fujifilm finepix, y2k dokunmatik kamera, z serisi digicam, super ccd, film tonu, selfie kamera, retrocameraland",
  meta_desc="Fujifilm FinePix Z90, Z700EXR ve V10 karşılaştırması: Y2K dokunmatik digicam estetiği, Super CCD film tonu ve hangi modelin sana uygun olduğu. 2026 alım rehberi.",
  related=[(H_HUB, T_HUB), (H_SONY, T_SONY), (H_CANON, T_CANON)],
  faqs=[
    ("Fujifilm FinePix Z90 ile Z700EXR arasındaki fark nedir, hangisini almalıyım?",
     "Z700EXR (2010) 12 MP Super CCD EXR sensörü ve 3.5\" büyük dokunmatik ekranıyla daha geniş ekran ve EXR mod esnekliği (yüksek çözünürlük / geniş dinamik aralık / düşük gürültü) sunar. Z90 (2011) 14 MP CCD, 3.0\" dokunmatik ve kayan kapaklı daha kompakt bir gövdedir; tek dokunuşla yükleme tuşu vardır. Daha büyük ekran istiyorsan Z700EXR, daha kompakt ve pratik gövde istiyorsan Z90."),
    ("Fujifilm FinePix V10 dokunmatik mi ve hangi yıl çıktı?",
     "V10 2006'da çıktı ve dokunmatik DEĞİLDİR; tuş ve yön pediyle kullanılır. 5.1 MP Super CCD HR sensörü ve hatta gömülü oyunlarıyla otantik bir mid-2000s digicam'dir. Dokunmatik Y2K estetiği istiyorsan Z serisine (Z90/Z700EXR), erken dönem koleksiyon parçası istiyorsan V10'a bak."),
    ("Fujifilm CCD kameraların rengi neden bu kadar seviliyor?",
     "Fujifilm, fotoğraf tarihinin en sevilen film renklerini üreten markadır ve bu \"film tonu\" mirası dijital CCD kompaktlarına da yansır. Sonuç; sıcak, nostaljik ve filmsi bir renk karakteridir. Bu yüzden FinePix CCD kareleri düzenlemeye gerek kalmadan doğrudan estetik görünür."),
    ("Y2K estetiği ve selfie için en uygun Fujifilm hangisi?",
     "Büyük dokunmatik ekran ve pratik paylaşım için Z serisi öne çıkar. Z700EXR'nin 3.5\" ekranı ve Z90'ın kompakt dokunmatik gövdesi, selfie ve sosyal medya içeriği için idealdir. İkisi de o sıcak Y2K digicam tonunu doğrudan verir."),
  ],
  body="""<p>Sosyal medyayı saran o sıcak, dokunmatik, kayan kapaklı dijital kamera estetiğinin adı çoğu zaman tek bir seriye çıkar: <strong>Fujifilm FinePix Z</strong>. Fujifilm'in efsane film rengi mirasını, dönemin en şık digicam gövdelerinde sunan bu kameralar, bugün Y2K içerik üreticilerinin favorisi. RetroCameraLand'a yeni gelen üç Fujifilm -Z90, Z700EXR ve V10- arasında hangisinin sana uygun olduğunu birlikte bakalım.</p>

<h2>Üç Fujifilm Bir Arada: Hızlı Karşılaştırma</h2>
<table style="width:100%%;border-collapse:collapse;margin:20px 0;font-size:15px;">
<tr style="background:#15110d;color:#fff;"><th style="padding:11px;text-align:left;">Model</th><th style="padding:11px;text-align:left;">Yıl</th><th style="padding:11px;text-align:left;">Sensör</th><th style="padding:11px;text-align:left;">Ekran</th><th style="padding:11px;text-align:left;">Tarz</th></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Z700EXR</td><td style="padding:10px;border-bottom:1px solid #eee;">2010</td><td style="padding:10px;border-bottom:1px solid #eee;">12 MP Super CCD EXR</td><td style="padding:10px;border-bottom:1px solid #eee;">3.5&quot; dokunmatik</td><td style="padding:10px;border-bottom:1px solid #eee;">Büyük ekran, selfie</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Z90</td><td style="padding:10px;border-bottom:1px solid #eee;">2011</td><td style="padding:10px;border-bottom:1px solid #eee;">14 MP CCD</td><td style="padding:10px;border-bottom:1px solid #eee;">3.0&quot; dokunmatik</td><td style="padding:10px;border-bottom:1px solid #eee;">Kompakt, kayan kapak</td></tr>
<tr><td style="padding:10px;">V10</td><td style="padding:10px;">2006</td><td style="padding:10px;">5.1 MP Super CCD HR</td><td style="padding:10px;">3.0&quot; (tuşlu)</td><td style="padding:10px;">Erken dönem koleksiyon</td></tr>
</table>

<h2>Fujifilm FinePix Z90: Kompakt Dokunmatik Y2K İkonu</h2>
<p><a href="%s">Fujifilm FinePix Z90</a>, Y2K dokunmatik digicam estetiğinin tam ortasında. 14 MP CCD sensör, 28mm'den başlayan 5x geniş açı zoom ve 3.0&quot; dokunmatik ekranıyla cebe giren, şık bir günlük kamera. Kayan kapağı açtığında çekime hazır; tek dokunuşla yükleme tuşu ve dokunmatik arayüzü pratik kullanım sunar. Klasik Fujifilm CCD renginin sıcak, nostaljik tonunu doğrudan verdiği için çekip aninda paylaşmak isteyen içerik üreticileri için ideal.</p>

<h2>Fujifilm FinePix Z700EXR: Büyük Dokunmatik Ekran ve EXR Esnekliği</h2>
<p><a href="%s">Fujifilm FinePix Z700EXR</a>, 3.5&quot; büyük dokunmatik ekranıyla seride ferah bir kullanım sunar; selfie ve kadrajlama daha kolaydır. 12 MP Super CCD EXR sensörünün özel yanı, koşula göre mod değiştirebilmesi: yüksek çözünürlük, geniş dinamik aralık veya düşük gürültü modları arasında geçiş yapar. Hem o sıcak Fujifilm tonunu istiyor hem de büyük ekranlı, esnek bir digicam arıyorsan Z700EXR güçlü bir aday.</p>

<h2>Fujifilm FinePix V10: Erken Dönem Koleksiyon Parçası</h2>
<p><a href="%s">Fujifilm FinePix V10</a>, 2006'nın otantik mid-2000s digicam'i. 5.1 MP Super CCD HR sensörü ve kare, iki tonlu metal gövdesiyle gerçek bir dönem nesnesi. Dokunmatik değil; tuşlarla kontrol edilir ve hatta gömülü oyunlar gibi döneme özgü detaylar barındırır. Daha düşük çözünürlük seni korkutmasın: o ham, sıcak Super CCD dokusu tam da erken Y2K estetiğini sevenlerin aradığı şey. Koleksiyon ve karakter arayanlar için.</p>

<h2>Hangi Fujifilm Sana Göre?</h2>
<ul>
<li><strong>Kompakt, pratik, günlük Y2K:</strong> FinePix Z90</li>
<li><strong>Büyük ekran, selfie, EXR esnekliği:</strong> FinePix Z700EXR</li>
<li><strong>Erken dönem koleksiyon ve ham doku:</strong> FinePix V10</li>
</ul>
""" % (P("fujifilm-finepix-z90-digicam"), P("fujifilm-finepix-z700exr"), P("fujifilm-finepix-v10")),
  cta_line="Dokunmatik mi, kompakt mı, koleksiyonluk mu? Birkaç soruyla Y2K tarzına en uygun Fujifilm'i bulalım.",
))

# ══════════════════════════════════════════════════════════════════════════════
# 4 ── CANON SPOKE
# ══════════════════════════════════════════════════════════════════════════════
POSTS.append(dict(
  handle=H_CANON, title="Canon Dijital Kompakt Klasikleri: IXUS i, IXY 1000, ELPH 300 HS ve PowerShot G7",
  keyword="Canon retro kompakt dijital kamera",
  img_kw="canon ixus powershot ccd digicam vintage compact",
  pin_hero="Canon IXUS",
  tags="canon ixus, canon powershot g7, manuel kontrol kamera, ccd dijital kamera, y2k canon, titanyum kamera, retrocameraland",
  meta_desc="Canon IXUS i, IXY 1000, PowerShot ELPH 300 HS ve PowerShot G7 karşılaştırması: ultra-ince Y2K cep kamerasından manuel kontrollü meraklı kamerasına Canon retro kompakt rehberi.",
  related=[(H_HUB, T_HUB), (H_SONY, T_SONY), (H_FUJI, T_FUJI)],
  faqs=[
    ("Manuel kontrol ve ISO çarkı olan eski Canon kompakt hangisi?",
     "Canon PowerShot G7 (2006). Fiziksel ISO çarkı, kontrol tekerleği, tam manuel modlar (M/Av/Tv) ve hot shoe (harici Speedlite flaş takılabilir) ile meraklı kullanıcının kamerasıdır. 10 MP CCD ve 6x optik zoom sunar. DSLR'a yan kamera ya da pozlamayı tamamen kendi kontrol etmek isteyenler için idealdir."),
    ("Canon Digital IXUS i'nin optik zoomu var mı?",
     "Hayır. IXUS i (2003) sabit odak uzaklıklı, yani zoomsuz bir lense sahiptir; bu, kibrit kutusu boyutundaki ultra-ince gövdesinin bedelidir. 4 MP CCD ile en küçük, en diskret Y2K cep kamerası arayanlar için bir tarz objesidir. Zoom isteyenler IXY 1000 veya ELPH 300 HS'e bakmalıdır."),
    ("Gece ve parti için CCD mi yoksa CMOS Canon kompakt mı daha iyi?",
     "Gece ve düşük ışıkta CMOS daha avantajlı. Canon PowerShot ELPH 300 HS (2011) BSI CMOS sensörü ve HS System'iyle yüksek ISO'da gürültüyü belirgin azaltır ve Full HD video çeker; gece/parti için daha temiz sonuç verir. CCD modeller (IXUS i, IXY 1000, G7) ise gündüz sıcak Y2K renginde öne çıkar."),
    ("Canon IXY 1000 hangi modelle aynı, neden özel?",
     "IXY 1000, Canon'un titanyum gövdeli PowerShot SD900 / Digital IXUS 900 Ti modelinin Japonya adıdır (2006). 10 MP CCD ve DIGIC III işlemciye sahiptir. Onu özel kılan, hafif ama dayanıklı titanyum kasası ve premium yapı kalitesidir; koleksiyoncuların ve üst düzey his arayanların favorisidir."),
  ],
  body="""<p>Canon'un dijital kompakt mirası, fotoğrafa yeni başlayanın cep kamerasından, pozlamanın her ayarını eliyle kontrol eden meraklının makinesine kadar uzanır. RetroCameraLand'a yeni gelen dört Canon tam da bu yelpazeyi temsil ediyor: <strong>ultra-ince IXUS i, titanyum IXY 1000, temiz çeken ELPH 300 HS ve manuel kontrollü PowerShot G7</strong>. Hangisinin sana uygun olduğunu birlikte netleştirelim.</p>

<h2>Dört Canon Bir Arada: Hızlı Karşılaştırma</h2>
<table style="width:100%%;border-collapse:collapse;margin:20px 0;font-size:15px;">
<tr style="background:#15110d;color:#fff;"><th style="padding:11px;text-align:left;">Model</th><th style="padding:11px;text-align:left;">Yıl</th><th style="padding:11px;text-align:left;">Sensör</th><th style="padding:11px;text-align:left;">Zoom</th><th style="padding:11px;text-align:left;">Karakter</th></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">Digital IXUS i</td><td style="padding:10px;border-bottom:1px solid #eee;">2003</td><td style="padding:10px;border-bottom:1px solid #eee;">4 MP CCD</td><td style="padding:10px;border-bottom:1px solid #eee;">Yok (sabit)</td><td style="padding:10px;border-bottom:1px solid #eee;">En küçük, diskret</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">IXY 1000</td><td style="padding:10px;border-bottom:1px solid #eee;">2006</td><td style="padding:10px;border-bottom:1px solid #eee;">10 MP CCD</td><td style="padding:10px;border-bottom:1px solid #eee;">3x</td><td style="padding:10px;border-bottom:1px solid #eee;">Titanyum, premium</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee;">ELPH 300 HS</td><td style="padding:10px;border-bottom:1px solid #eee;">2011</td><td style="padding:10px;border-bottom:1px solid #eee;">12 MP BSI CMOS</td><td style="padding:10px;border-bottom:1px solid #eee;">5x (24mm geniş)</td><td style="padding:10px;border-bottom:1px solid #eee;">Temiz gece, Full HD</td></tr>
<tr><td style="padding:10px;">PowerShot G7</td><td style="padding:10px;">2006</td><td style="padding:10px;">10 MP CCD</td><td style="padding:10px;">6x</td><td style="padding:10px;">Manuel kontrol, hot shoe</td></tr>
</table>

<h2>Canon Digital IXUS i: Kibrit Kutusu Boyutunda Y2K</h2>
<p><a href="%s">Canon Digital IXUS i</a>, 2003'ün en diskret cep kamerası. Kibrit kutusu boyutundaki ultra-ince gövdesi dikkat çekmeden çekim yapmana izin verir. 4 MP CCD ve sabit lens (zoom yok) ile sade ama karakterli: erken dönem Canon CCD'sinin sıcak ten tonları ve kontrastlı görünümü, otantik bir digicam estetiği sunar. En küçük, en tarz odaklı Y2K kamerayı isteyen sokak ve günlük çekim severler için bir obje niteliğinde.</p>

<h2>Canon IXY 1000: Titanyum Gövdeli Premium Kompakt</h2>
<p><a href="%s">Canon IXY 1000</a> (Digital IXUS 900 Ti olarak da bilinir), 2006'nın lüks kompaktı. Onu sıradan kompaktlardan ayıran şey titanyum gövdesi: hafif, dayanıklı ve elde premium bir his. 10 MP CCD, DIGIC III işlemci ve 3x zoomla Canon'un o sıcak, doygun renklerini verir; Touch Control Dial ile şık bir kullanım sunar. Yapı kalitesine önem veren koleksiyoncular ve üst düzey his arayanlar için.</p>

<h2>Canon PowerShot ELPH 300 HS: Gece ve Video İçin CMOS</h2>
<p><a href="%s">Canon PowerShot ELPH 300 HS</a>, listedeki en \"modern\" davranan kompakt. 12 MP BSI CMOS sensörü ve HS System'i sayesinde düşük ışıkta gürültüyü belirgin azaltır; gece ve parti karelerinde diğer CCD modellere göre daha temiz sonuç verir. 24mm'den başlayan 5x geniş açı zoom ve Full HD 1080p video da ekler. Hem retro his hem temiz gece performansı ve video isteyenler için dengeli bir seçim.</p>

<h2>Canon PowerShot G7: Meraklının Manuel Kompaktı</h2>
<p><a href="%s">Canon PowerShot G7</a>, bu dörtlünün en \"ciddi\" makinesi. Fiziksel ISO çarkı, kontrol tekerleği, tam manuel modlar (M/Av/Tv) ve hot shoe (harici Speedlite flaş) ile pozlamanın her ayarını sen kontrol edersin. 10 MP CCD, DIGIC III ve 6x optik zoom (35-200mm), optik stabilizasyonla birlikte tutarlı sonuç verir. Fotoğrafı sadece otomatik çekmek değil, öğrenmek ve yönetmek isteyen meraklı kullanıcının ya da DSLR'a yan kamera arayanın tercihi.</p>

<h2>Hangi Canon Sana Göre?</h2>
<ul>
<li><strong>En küçük, diskret Y2K cep kamerası:</strong> Digital IXUS i</li>
<li><strong>Premium titanyum his, koleksiyon:</strong> IXY 1000</li>
<li><strong>Temiz gece + Full HD video:</strong> PowerShot ELPH 300 HS</li>
<li><strong>Manuel kontrol, harici flaş, öğrenmek:</strong> PowerShot G7</li>
</ul>
""" % (P("canon-ixus-i"), P("canon-ixy-1000"), P("canon-powershot-elph-300-hs"), P("canon-powershot-g7")),
  cta_line="Diskret cep kamerası mı, manuel kontrol mü, temiz gece mi? Birkaç soruyla sana en uygun Canon'u seçelim.",
))

# ══════════════════════════════════════════════════════════════════════════════
# 5 ── SAMSUNG NX2000 SPOKE (aynasiz)
# ══════════════════════════════════════════════════════════════════════════════
POSTS.append(dict(
  handle=H_NX, title="Bütçeyle Aynasız: Samsung NX2000 ile Lens Değiştirilebilir Retro Fotoğraf",
  keyword="bütçe dostu aynasız fotoğraf makinesi",
  img_kw="samsung nx2000 mirrorless aps-c camera white",
  pin_hero="samsung nx2000",
  tags="bütçe dostu aynasız, samsung nx2000, aps-c aynasız kamera, lens degistirilebilir, dslr kalitesi, baslangic aynasiz, retrocameraland",
  meta_desc="Samsung NX2000 incelemesi: APS-C sensörlü, lens değiştirilebilir bütçe dostu aynasız fotoğraf makinesi. DSLR kalitesinde fotoğrafa uygun fiyatlı giriş arayanlar için 2026 rehberi.",
  related=[(H_HUB, T_HUB), (H_CANON, T_CANON), (H_SONY, T_SONY)],
  faqs=[
    ("Bütçesi sınırlı biri için lens değiştirilebilir uygun fiyatlı aynasız hangisi olmalı?",
     "Samsung NX2000 bu ihtiyaç için güçlü bir seçenek. APS-C boyutunda 20.3 MP CMOS sensörü kompakt kameralardan çok daha büyüktür; lens değiştirilebilir NX mount sayesinde tek gövdeyle farklı lenslere geçebilirsin. İkinci el/retro fiyatlarla, yeni başlayan biri için DSLR kalitesine uygun maliyetli bir giriş sunar."),
    ("Samsung NX2000 DSLR kalitesinde fotoğraf çeker mi?",
     "Büyük ölçüde evet. APS-C sensörü pek çok giriş seviyesi DSLR ile aynı boyuttadır; bu da geniş dinamik aralık, güzel arka plan bulanıklığı (bokeh) ve düşük ışıkta net sonuç demektir. Kompakt digicam'lerin veremediği bu \"büyük sensör hissini\", aynasız ve daha hafif bir gövdede sunar."),
    ("Samsung NX2000 ile hangi lensler kullanılır?",
     "Samsung NX mount lensleri kullanır. Kit lensi genelde 20-50mm f/3.5-5.6'dır (günlük ve manzara için ideal, 35mm karşılığı ~31-77mm). İsteğe bağlı 50-200mm tele lens portre ve uzak konular için eklenebilir. Lens değiştirebilmek, tek kamerayla geniş bir çekim yelpazesi açar."),
    ("Aynasız kamera mı yoksa retro CCD kompakt mı almalıyım?",
     "Önceliğin görüntü kalitesi, lens esnekliği ve düşük ışık ise APS-C aynasız Samsung NX2000 daha doğru. Önceliğin nostaljik Y2K dokusu, cebe giren küçük gövde ve \"tak-çek\" basitliği ise CCD kompaktlar (Sony Cyber-shot, Fujifilm FinePix Z) daha uygun. İkisi farklı amaçlara hizmet eder; ne aradığına göre seç."),
  ],
  body="""<p>Yeni gelen 15 retro kameranın çoğu cebe giren CCD kompaktlar; ama aralarında kategorik olarak farklı, çok daha iddialı bir model var: <strong>Samsung NX2000</strong>. Bu bir kompakt değil, lens değiştirilebilir APS-C aynasız sistem kamerası. \"Telefonun ötesine geçmek, gerçek görüntü kalitesi ve lens esnekliği istiyorum ama bütçem sınırlı\" diyorsan, bu rehber tam sana göre.</p>

<h2>Neden NX2000 Diğerlerinden Farklı?</h2>
<p><a href="%s">Samsung NX2000</a> (2013), 20.3 MP APS-C CMOS sensörü taşır. Bu sensör, kompakt kameralardaki küçük sensörlerin yaklaşık 13 katı büyüklüğünde; pek çok giriş seviyesi DSLR ile aynı boyutta. Pratikte bu şu demek: daha geniş dinamik aralık, ışığı daha iyi toplama, düşük ışıkta daha az gürültü ve konuyu arka plandan ayıran gerçek bokeh. Kompakt bir digicam'in veremeyeceği \"büyük sensör hissini\", 228 gramlık hafif bir gövdede sunar.</p>

<h2>Lens Değiştirilebilir Olmak Ne Kazandırır?</h2>
<p>NX2000'in en büyük avantajı sabit lensli olmaması. Samsung NX mount sayesinde tek gövdeyle farklı lenslere geçebilirsin: kit lensi 20-50mm (35mm karşılığı ~31-77mm) günlük, sokak ve manzara için idealken; isteğe bağlı 50-200mm tele lens portre ve uzaktaki konular için kapı açar. Yani kamera, ihtiyacın büyüdükçe seninle birlikte büyüyebilen bir sistem.</p>

<h2>Kullanım Kolaylığı: Dev Dokunmatik Ekran ve WiFi</h2>
<p>NX2000, dönemine göre cömert bir 3.7&quot; büyük dokunmatik LCD ile gelir; menüler ve odak noktası seçimi telefon kullanır gibi sezgiseldir. Yerleşik WiFi/NFC ile fotoğrafları telefona aktarıp paylaşmak kolaydır. Minimal düğmeli, sade gövdesi, ilk ciddi kamerasını alan biri için korkutucu değil davetkar bir deneyim sunar.</p>

<h2>Kimler İçin İdeal?</h2>
<ul>
<li><strong>İlk ciddi kamerasını alan:</strong> Telefon ve kompaktın ötesine geçmek isteyen</li>
<li><strong>Bütçeyle DSLR kalitesi arayan:</strong> Büyük sensör + lens esnekliği, uygun maliyetle</li>
<li><strong>Portre ve içerik üreticisi:</strong> Bokeh ve düşük ışık performansı isteyen blog/sosyal medya üreticisi</li>
<li><strong>Öğrenmek isteyen:</strong> Lens ve manuel ayarlarla deney yapmak isteyen</li>
</ul>
<p>Nostaljik Y2K dokusu ve cebe giren basitlik senin önceliğinse, CCD kompaktlara (Sony Cyber-shot veya Fujifilm FinePix Z serisi) bakman daha mantıklı olabilir. Ama hedefin görüntü kalitesi ve büyüyebilen bir sistemse, NX2000 bu listedeki en akıllı \"uzun vadeli\" tercih.</p>
""" % (P("samsung-nx2000"),),
  cta_line="Aynasız mı yoksa retro CCD kompakt mı sana uygun? Birkaç soruyla ihtiyacına en uygun kamerayı bulalım.",
))

# ══════════════════════════════════════════════════════════════════════════════
def build_html(p, image_url):
    parts = [f'<h1>{p["title"]}</h1>', p["body"].strip(),
             closer(p["keyword"]), faq_html(p["faqs"]),
             related_box(p["related"]), finder_cta(p["cta_line"]), SOCIAL_BLOCK,
             schema_blocks(p["title"], p["handle"], p["meta_desc"], image_url, p["faqs"])]
    return "\n\n".join(parts)

def pick_image(p):
    if not PIN_OK:
        return None, "pinterest yok"
    try:
        url, desc, score = find_unused_pinterest_image(p["img_kw"], p["pin_hero"])
        return url, f"{desc} (score={score})"
    except Exception as e:
        return None, f"gorsel hata: {e}"

def publish(p, dry=False):
    img_url, img_note = pick_image(p)
    html = build_html(p, img_url)
    if dry:
        out = f"{SCRATCH}/preview_{p['handle']}.html"
        try:
            open(out, "w", encoding="utf-8").write(
                f"<!doctype html><meta charset=utf-8><title>{p['title']}</title>"
                f"<div style='max-width:760px;margin:40px auto;font-family:-apple-system,sans-serif;padding:0 16px'>"
                + (f"<img src='{img_url}' style='width:100%;border-radius:12px;margin-bottom:20px'>" if img_url else "")
                + f"{html}</div>")
        except Exception:
            pass
        words = len(html.split())
        log(f"  [DRY] {p['title'][:48]} | ~{words} kelime | gorsel: {img_note}")
        log(f"        onizleme: {out}")
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
    return {"status": "ok", "id": art["id"], "handle": art["handle"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="Yayinlamadan onizleme uret")
    args = ap.parse_args()
    log(f"=== RCL Yeni Gelenler Blog Seti ({'DRY' if args.dry else 'CANLI'}) — {len(POSTS)} blog ===")
    results = []
    for p in POSTS:
        results.append(publish(p, dry=args.dry))
        if not args.dry:
            time.sleep(2)
    ok = sum(1 for r in results if r.get("status") in ("ok", "dry"))
    log(f"=== Tamamlandi: {ok}/{len(POSTS)} ===")
