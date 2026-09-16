#!/usr/bin/env python3
"""
Panasonic Lumix DC-TZ91 — YouTube videolu, yuksek SEO blog yazisi (tek makale)
Video: https://youtu.be/LLXSMuhZAko
"""
import sys
sys.path.insert(0, "/Users/onnoshot/Downloads/Agentlar")
from retrocameraland_api import shopify, log, SOCIAL_BLOCK, CTA_BLOCK

BLOG_ID = "91197866123"
IMAGE   = "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/panasonic-lumix-dc-tz91-vitrin.jpg?v=1782612130"
VIDEO   = "LLXSMuhZAko"
URL     = "https://retrocameraland.com/blogs/retro-dijital-kamera/panasonic-lumix-dc-tz91-inceleme"
TITLE   = "Panasonic Lumix DC-TZ91 Incelemesi: 30x Zoom, 20MP ve 4K Gucu Cep Boyutunda"
HANDLE  = "panasonic-lumix-dc-tz91-inceleme"
META    = "Panasonic Lumix DC-TZ91 incelemesi: 20.3MP sensor, 24-720mm 30x LEICA zoom, 4K video, EVF ve katlanan ekran. Seyahat-zoom kompaktinin tum detaylari + video."
TAGS    = "Panasonic,Lumix,DC-TZ91,TZ91,Travel Zoom,Seyahat Kamerasi,30x Zoom,4K,Kompakt Kamera,Inceleme,Dijital Fotograf Makinesi,LEICA"

VIDEO_EMBED = f"""
<div style="position:relative;width:100%;max-width:760px;margin:32px auto;padding-bottom:42.85%;height:0;overflow:hidden;border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.18);">
<iframe src="https://www.youtube.com/embed/{VIDEO}" title="Panasonic Lumix DC-TZ91 Video Inceleme" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy" style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe>
</div>
<p style="text-align:center;font-size:14px;color:#777;margin-top:-12px;">Panasonic Lumix DC-TZ91 ile cekilmis ornek fotograflar ve video kayitlari yukaridaki videoda.</p>
"""

SCHEMA = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{TITLE}",
  "description": "{META}",
  "image": "{IMAGE}",
  "datePublished": "2026-06-29",
  "dateModified": "2026-06-29",
  "author": {{"@type":"Organization","name":"Retrocameraland","url":"https://retrocameraland.com"}},
  "publisher": {{"@type":"Organization","name":"Retrocameraland","logo":{{"@type":"ImageObject","url":"https://retrocameraland.com/logo.png"}}}},
  "mainEntityOfPage": {{"@type":"WebPage","@id":"{URL}"}}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Panasonic Lumix DC-TZ91 Video Inceleme",
  "description": "Panasonic Lumix DC-TZ91 ile cekilmis ornek fotograflar, video kayitlari, 30x zoom ve 4K performansi.",
  "thumbnailUrl": "https://i.ytimg.com/vi/{VIDEO}/hqdefault.jpg",
  "uploadDate": "2026-06-29",
  "contentUrl": "https://youtu.be/{VIDEO}",
  "embedUrl": "https://www.youtube.com/embed/{VIDEO}",
  "publisher": {{"@type":"Organization","name":"Retrocameraland","logo":{{"@type":"ImageObject","url":"https://retrocameraland.com/logo.png"}}}}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type":"ListItem","position":1,"name":"Anasayfa","item":"https://retrocameraland.com"}},
    {{"@type":"ListItem","position":2,"name":"Retro Dijital Kamera Blog","item":"https://retrocameraland.com/blogs/retro-dijital-kamera"}},
    {{"@type":"ListItem","position":3,"name":"Panasonic Lumix DC-TZ91 Incelemesi","item":"{URL}"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"Panasonic Lumix DC-TZ91 kac megapiksel ve hangi sensore sahip?","acceptedAnswer":{{"@type":"Answer","text":"DC-TZ91, 20.3 megapiksel 1/2.3 inc MOS sensor kullanir. Bu sensor, 30x optik zoom ile birlestiginde hem genis acida hem uzak mesafede yuksek detay sunar."}}}},
    {{"@type":"Question","name":"DC-TZ91 4K video cekebiliyor mu?","acceptedAnswer":{{"@type":"Answer","text":"Evet. Panasonic Lumix DC-TZ91, 4K 30p video ve 4K Photo modunu destekler. 4K Photo ile videodan 8MP kareleri durdurup fotograf olarak kaydedebilirsiniz."}}}},
    {{"@type":"Question","name":"TZ91 ile ZS70 ayni kamera mi?","acceptedAnswer":{{"@type":"Answer","text":"Evet. Panasonic ayni modeli farkli pazarlarda farkli isimle satar: Avrupa'da TZ91, Kuzey Amerika'da ZS70, Japonya'da TZ90 olarak bilinir. Teknik ozellikleri aynidir."}}}},
    {{"@type":"Question","name":"DC-TZ91'in zoom menzili nedir?","acceptedAnswer":{{"@type":"Answer","text":"24-720mm karsiligi 30x optik LEICA DC Vario-Elmar lens sunar. Genis acidan ultra-tele zoom'a kadar tek kamerayla cogu sahneyi cekebilirsiniz; i.Zoom ile 60x'e kadar uzar."}}}},
    {{"@type":"Question","name":"DC-TZ91'i Retrocameraland'dan satin alabilir miyim?","acceptedAnswer":{{"@type":"Answer","text":"Evet. Stok durumunu ve guncel fiyati gormek icin urun sayfasini ziyaret edebilirsiniz: retrocameraland.com/products/panasonic-lumix-dc-tz91"}}}}
  ]
}}
</script>
"""

BODY = f"""<h1>Panasonic Lumix DC-TZ91 Incelemesi: 30x Zoom, 20MP ve 4K Gucu Cep Boyutunda</h1>

<p>Tek bir kompakt kamerayla hem genis manzarayi hem de uzaktaki bir kus, bir konser sahnesi ya da bir mac anini cekebilmeyi hayal edin. <strong>Panasonic Lumix DC-TZ91</strong>, tam olarak bunu vaat eden bir "seyahat-zoom" (travel zoom) kamerasidir. 2017'de tanitilan bu model, cebe sigan govdesine 24-720mm karsiligi 30x optik LEICA zoom, 20.3MP sensor ve 4K video gucunu sigdirir. Asagidaki videoda DC-TZ91 ile cekilmis ornek fotograflari ve video kayitlarini detayli sekilde gorebilirsiniz.</p>

{VIDEO_EMBED}

<h2>Panasonic Lumix DC-TZ91 Nedir?</h2>
<p>DC-TZ91, Panasonic'in efsanevi TZ (Travel Zoom) serisinin en dengeli uyelerinden biridir. Serinin amaci basit ama iddiali: tatilde, sokakta veya gunluk hayatta tasimak istemeyeceginiz kadar agir bir ayna degistirilebilir lensli sistem yerine, ceket cebine giren tek bir kamerayla her seyi cekebilmek. TZ91 bu felsefenin olgun bir temsilcisidir. Ayni model Kuzey Amerika'da <strong>ZS70</strong>, Japonya'da TZ90 adiyla satilir; ucu de teknik olarak aynidir.</p>

<h2>Teknik Ozellikler</h2>
<ul>
<li><strong>Sensor:</strong> 20.3MP 1/2.3" MOS</li>
<li><strong>Lens:</strong> 24-720mm esdegeri 30x LEICA DC Vario-Elmar (f/3.3-6.4)</li>
<li><strong>Zoom:</strong> 30x optik + i.Zoom ile ~60x</li>
<li><strong>Video:</strong> 4K 30p (UHD) + 4K Photo modu</li>
<li><strong>Vizor:</strong> 0.20" 1166k nokta elektronik vizor (EVF)</li>
<li><strong>Ekran:</strong> 3.0" 1040k nokta, yukari 180 derece katlanan dokunmatik LCD (selfie/vlog)</li>
<li><strong>Sabitleme:</strong> 5 eksenli Power O.I.S. optik goruntu sabitleyici</li>
<li><strong>Odak yardimi:</strong> Post Focus ve Focus Stacking</li>
<li><strong>ISO:</strong> 80-3200 (genisletilmis 6400)</li>
<li><strong>Pil:</strong> Yaklasik 380 kare (CIPA)</li>
</ul>

<h2>30x Zoom: Tek Kameranin En Buyuk Avantaji</h2>
<p>DC-TZ91'i siradan bir kompakttan ayiran en kritik ozellik, 24-720mm'lik devasa zoom menzilidir. 24mm genis acida dar bir sokagi, bir ic mekani veya grup fotografini rahatca kadrajlarsiniz; ayni kamerayla 720mm tele uca gectiginizde uzaktaki bir detayi yaninizdaymis gibi cekersiniz. i.Zoom devreye girdiginde bu menzil yaklasik 60x'e kadar uzar. Telefonunuzun dijital zoom'unda kaybettiginiz detayi, burada gercek optik zoom ile korursunuz. Bu menzili tek bir cep kamerasinda bulmak, TZ91'i seyahat edenler ve "tek kamerayla her seyi cekmek isteyenler" icin ideal kilar.</p>

<h2>20MP Sensor ve LEICA Lens Kalitesi</h2>
<p>30x gibi yuksek bir zoom oraninda en buyuk risk goruntu kalitesinin dusmesidir; Panasonic bunu LEICA DC Vario-Elmar optigi ve 20.3MP MOS sensoruyle dengeler. Genis acida netlik yuksektir, renkler Panasonic'in dogal renk isleme karakterini tasir. Tele ucta f/6.4 acikligi nedeniyle bol isik istense de, 5 eksenli Power O.I.S. sabitleyici elde cekimde belirgin fark yaratir ve 720mm'de bile kullanilabilir kareler verir.</p>

<h2>4K Video ve 4K Photo Modu</h2>
<p>TZ91, 2017 yili bir cep kamerasi icin etkileyici bir sekilde <strong>4K 30p video</strong> kaydeder. Asil zekice ozellik ise 4K Photo modudur: kamera 4K cozunurlukte saniyede 30 kare yakalar, siz de sonradan en iyi ani secip 8MP'lik bir fotograf olarak kaydedersiniz. Hizli hareket eden cocuklar, evcil hayvanlar veya spor anlari icin "kaciran kare" derdini buyuk olcude ortadan kaldirir. Yukari 180 derece katlanan ekran sayesinde vlog ve selfie cekimleri de rahattir.</p>

<h2>Elektronik Vizor ve Manuel Kontroller</h2>
<p>Cogu kompakt kamerada bulunmayan bir ayricalik: TZ91'in dahili <strong>elektronik vizoru (EVF)</strong> vardir. Gunes altinda LCD ekranin yansidigi durumlarda vizordan bakarak net kadraj kurabilirsiniz. Ustelik tam manuel pozlama (P/A/S/M), RAW cekim ve fiziksel kontrol halkasi ile TZ91 sadece "otomatik basit kamera" degil, ogrenmek isteyenler icin gercek bir fotografcilik araci sunar.</p>

<h2>Kimler Icin?</h2>
<ul>
<li>Tatilde tek kamerayla hem manzara hem uzak detay cekmek isteyen seyahat tutkunlari</li>
<li>Telefondan gercek bir optik zoom farki arayanlar</li>
<li>4K video ve vlog (katlanan ekran) isteyen icerik ureticileri</li>
<li>Manuel kontrol ve EVF ile fotografcilik ogrenmek isteyenler</li>
<li>Agir ayna sistemlerini tasimak istemeyen gunluk kullanicilar</li>
</ul>

<h2>Koleksiyonumuzdaki Diger Panasonic Lumix Modelleri</h2>
<p>Eger Panasonic'in renk karakterini ve guvenilir kompakt mekanigini seviyorsaniz, <a href="/products/panasonic-lumix-dc-tz91">Panasonic Lumix DC-TZ91</a> disinda su modellere de goz atabilirsiniz: bir ust seri olarak <a href="/products/panasonic-lumix-dc-tz99">Panasonic LUMIX DC-TZ99</a>, daha sade bir zoom kompakti olarak <a href="/products/panasonic-lumix-dmc-lz7">Panasonic Lumix DMC-LZ7</a>. Tum retro ve modern dijital fotograf makinelerini ise <a href="/collections/dijital-fotograf-makinesi">dijital fotograf makinesi koleksiyonumuzda</a> bulabilirsiniz.</p>

<h2>Sik Sorulan Sorular (FAQ)</h2>
<h3>Panasonic Lumix DC-TZ91 kac megapiksel?</h3>
<p>DC-TZ91, 20.3 megapiksel 1/2.3 inc MOS sensor kullanir. Bu cozunurluk, 30x zoom menzilinde bile yeterli detay ve hafif kirpma payi birakir.</p>
<h3>TZ91 ile ZS70 ayni kamera mi?</h3>
<p>Evet. Panasonic ayni modeli farkli pazarlarda farkli adlandirir: Avrupa'da TZ91, Kuzey Amerika'da ZS70, Japonya'da TZ90. Teknik ozellikleri aynidir.</p>
<h3>DC-TZ91 4K video cekebiliyor mu?</h3>
<p>Evet, 4K 30p video kaydeder ve 4K Photo modunu destekler. 4K Photo ile videodan 8MP kareleri secip fotograf olarak kaydedebilirsiniz.</p>
<h3>30x zoom pratikte ne ise yarar?</h3>
<p>24mm genis acida manzara ve ic mekan, 720mm tele ucta ise uzaktaki kus, sahne veya mac detayini cekersiniz. i.Zoom ile menzil ~60x'e uzar. Telefonun dijital zoom'undan farkli olarak detay kaybolmaz.</p>
<h3>DC-TZ91'i retrocameraland.com'dan satin alabilir miyim?</h3>
<p>Evet. Stok durumu ve guncel fiyat icin urun sayfasini ziyaret edin: <a href="/products/panasonic-lumix-dc-tz91">Panasonic Lumix DC-TZ91 urun sayfasi</a>.</p>

{SCHEMA}"""

def main():
    full = BODY + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    payload = {"article": {
        "title": TITLE, "body_html": full, "handle": HANDLE,
        "tags": TAGS, "published": True,
        "image": {"src": IMAGE, "alt": TITLE},
        "metafields": [
            {"namespace": "seo", "key": "description", "value": META, "type": "single_line_text_field"},
            {"namespace": "seo", "key": "title", "value": TITLE, "type": "single_line_text_field"},
        ],
    }}
    r = shopify("POST", f"blogs/{BLOG_ID}/articles.json", payload)
    art = r["article"]
    log(f"  OK {art['id']} -> {art['handle']}")
    print("LIVE:", f"https://retrocameraland.com/blogs/retro-dijital-kamera/{art['handle']}")

if __name__ == "__main__":
    main()
