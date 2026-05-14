#!/usr/bin/env python3
"""Batch 3: Fujifilm (6) + Olympus (6) = 12 ürün"""
import sys
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log, SOCIAL_BLOCK, CTA_BLOCK

BLOG_ID = "91197866123"

def pub(title, handle, tags, meta_desc, image_src, body):
    full = body + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    payload = {"article": {"title": title, "body_html": full, "handle": handle,
        "tags": tags, "published": True,
        "metafields": [
            {"namespace":"seo","key":"description","value":meta_desc,"type":"single_line_text_field"},
            {"namespace":"seo","key":"title","value":title,"type":"single_line_text_field"}
        ]}}
    if image_src:
        payload["article"]["image"] = {"src": image_src, "alt": title}
    r = shopify("POST", f"blogs/{BLOG_ID}/articles.json", payload)
    art = r["article"]
    log(f"  ✅ {art['id']} → {art['handle']}")
    return art["id"], art["handle"]

POSTS = [

# ── Fujifilm FinePix Z70 ─────────────────────────────────────────────────────
{"title":"Fujifilm FinePix Z70 İncelemesi: Kaykay Tasarımlı, Renkli ve CCD Kaliteli Y2K Kamera",
"handle":"fujifilm-finepix-z70-inceleme-kaykay-tasarim-renkli-ccd",
"tags":"Fujifilm, Fujifilm FinePix Z70, FinePix Z serisi, retro kamera, y2k kamera, renkli kamera",
"meta_desc":"Fujifilm FinePix Z70 incelemesi: 12MP CCD, kaykay tasarımlı ince gövde ve canlı renk seçenekleri. Fujifilm'in en şık Y2K kompaktını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a-1_0040_ONN06219.jpg?v=1765746106",
"body":"""
<p>Fujifilm Z70, kamerayı bir aksesuar olarak gören kullanıcılar için tasarlandı. "Kaykay" olarak anılan karakteristik ince gövde formu, Z serisinin en tanınan tasarım özelliği.</p>

<h2>Fujifilm FinePix Z70 Nedir?</h2>
<p>2010 çıkışlı FinePix Z70, 12.2 megapiksel CCD sensör, 5x optik zoom ve Fujifilm'in Z serisine özgü ince eğimli gövde tasarımıyla öne çıkan bir kompakt kameradır. Canlı renk seçenekleri (pembe, mavi, kırmızı, siyah) koleksiyon değerini artırıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.2 MP CCD</li>
<li><strong>Optik Zoom:</strong> 5x (33–165mm)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Yüz Tanıma:</strong> Var (10 yüze kadar)</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Pil:</strong> NP-45 Li-ion</li>
</ul>

<h2>Fujifilm CCD Renk Karakteri Z70'de</h2>
<p>Fujifilm'in CCD işleme algoritması, cilt tonlarını ve yeşilleri özellikle başarılı işler. Z70'in çektiği fotoğraflar — filtre uygulamadan — sıcak, doğal ve filmsi bir ton sunuyor. Bu ton bugün "Fujifilm look" olarak aranıyor ve Z70 bu karakteri taşıyan erişilebilir modellerden biri.</p>

<h2>Z Serisi Tasarım Dili</h2>
<p>Z serisinin eğimli gövdesi, parmak altında doğal tutmayı sağlayan ergo bir form oluşturuyor. Bu form diğer kameraların dik köşeli gövdelerinden belirgin biçimde farklı ve rafta özellikle dikkat çekici.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Fujifilm Z serisi renk ve tasarım meraklıları</li>
<li>Canlı renkli Y2K kamera koleksiyonu oluşturanlar</li>
<li>12MP Fujifilm CCD tonunu arayanlar</li>
<li>Şık, eğimli form tasarımı tercih edenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Fujifilm Z70 hangi pil kullanır?</h3>
<p>NP-45 Li-ion pil. Fujifilm'in geniş uyumlu pil modeli; kolayca temin edilir.</p>
<h3>Z70 ile video çekilir mi?</h3>
<p>Evet, 720p HD video kaydeder. Fujifilm'in renk işlemesi videolarda da etkili.</p>
<h3>Renkli versiyonlar arasında koleksiyon değeri farkı var mı?</h3>
<p>Pembe ve kırmızı versiyonlar siyaha kıyasla daha az üretildi ve koleksiyon pazarında prim yapıyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-z70" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix Z70'i İncele →</a></div>
"""},

# ── Fujifilm FinePix 4700 Zoom ───────────────────────────────────────────────
{"title":"Fujifilm FinePix 4700 Zoom İncelemesi: 2001'in 4MP Fujifilm Klasiği ve Altın CCD Çağı",
"handle":"fujifilm-finepix-4700-zoom-inceleme-2001-4mp-altin-ccd-cag",
"tags":"Fujifilm, Fujifilm FinePix 4700, erken dönem dijital kamera, FinePix serisi, retro kamera, 2001 kamera",
"meta_desc":"Fujifilm FinePix 4700 Zoom incelemesi: 2001 yılı 4MP Super CCD ve 6x optik zoom. Fujifilm'in erken dijital dönem koleksiyon kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0178_ONN04945.jpg?v=1765240860",
"body":"""
<p>2001 yılında 4 megapiksel ve 6x optik zoom aynı kamerada bir araya geldiğinde Fujifilm FinePix 4700 ortaya çıktı. O dönem için bu kombinezon harikaydı — bugün ise dijital fotoğraf tarihinin değerli bir sayfası.</p>

<h2>Fujifilm FinePix 4700 Zoom Nedir?</h2>
<p>2001 çıkışlı FinePix 4700 Zoom, Fujifilm'in Super CCD teknolojisini 4.3 megapiksel çözünürlükte ve 6x optik zoom lensle sunan prosümer seviyesindeki erken dönem modelidir. Fujifilm'in "Super CCD" sensörü, piksel dizilimini dönemin rakiplerinden farklı organize ederek daha fazla detay ve dinamik aralık sunmasını sağlıyordu.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 4.3 MP Super CCD (Fujifilm özel teknoloji)</li>
<li><strong>Optik Zoom:</strong> 6x (35–210mm)</li>
<li><strong>Ekran:</strong> 1.8" renkli LCD</li>
<li><strong>Hafıza:</strong> SmartMedia kart</li>
<li><strong>Pil:</strong> CR-V3 veya AA × 4</li>
<li><strong>Bağlantı:</strong> USB</li>
</ul>

<h2>Super CCD: Fujifilm'in Gizli Silahı</h2>
<p>Standart CCD sensörler kare pikseller kullanır; Fujifilm'in Super CCD'si ise eğik (sekizgen) piksel yerleşimi kullanarak her pikselden daha fazla bilgi çıkarmayı başarıyordu. Bu teknoloji, 4.3MP sensörden 6MP'ye eşdeğer çözünürlük elde etmek için tasarlanmıştı.</p>

<h2>SmartMedia Kart: Erken Dönemin Unutulmuş Formatı</h2>
<p>4700, bugün neredeyse yalnızca koleksiyonlarda görülen SmartMedia kart formatını kullanıyor. Bu kartlar ince, naif bir yapıya sahipti ve 2005 sonrasında tamamen piyasadan çekildi. SmartMedia'yı modern bilgisayara aktarmak için All-in-One kart okuyucu gerekiyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Fujifilm Super CCD teknolojisi koleksiyoncuları</li>
<li>2001 dönemi prosümer kamera meraklıları</li>
<li>SmartMedia format koleksiyonu kuranlar</li>
<li>Erken dönem Fujifilm FinePix seri tamamcıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>SmartMedia kart nereden temin edilir?</h3>
<p>İkinci el platformlarda (eBay, Letgo vb.) hâlâ bulunabiliyor. All-in-One kart okuyucu ile aktarım yapılabilir.</p>
<h3>Fujifilm 4700'ün Super CCD'si diğer CCD'lerden üstün mü?</h3>
<p>Dönemine göre evet, dinamik aralık ve detay açısından avantajlıydı. Bugün koleksiyon değeri teknik üstünlükten çok tarihsel öneme dayanıyor.</p>
<h3>6x zoom 2001'de nadir miydi?</h3>
<p>Kesinlikle. 2001'de 6x optik zoom genellikle profesyonel prosümer modellerde bulunuyordu. Bu özellik 4700'ü döneminde ciddi bir tercih yapıyordu.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-4700-zoom" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix 4700 Zoom'u İncele →</a></div>
"""},

# ── Fujifilm FinePix F80 ─────────────────────────────────────────────────────
{"title":"Fujifilm FinePix F80 İncelemesi: 10x Zoom, Geniş Açı ve Fujifilm'in CCD Seyahat Kompaktı",
"handle":"fujifilm-finepix-f80-inceleme-10x-zoom-genis-aci-seyahat",
"tags":"Fujifilm, Fujifilm FinePix F80, süper zoom kamera, seyahat kamerası, retro kamera, F serisi",
"meta_desc":"Fujifilm FinePix F80 incelemesi: 12MP CCD, 27mm geniş açı ve 10x optik zoom. Seyahat ve günlük kullanım için ideal Fujifilm kompaktını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0002_GenerativeFill_7e295d6b-3191-4cfd-897a-859f8d344b09.jpg?v=1759848109",
"body":"""
<p>Seyahatte tek kamera taşımak isteyenler için Fujifilm FinePix F80, 27mm geniş açıdan 270mm telefotoya uzanan geniş bir aralık sunuyor. Fujifilm'in CCD renk işlemesiyle birleşince seyahat fotoğrafçılığının güçlü bir ortağı haline geliyor.</p>

<h2>Fujifilm FinePix F80 Nedir?</h2>
<p>2010 çıkışlı FinePix F80 EXR, 12 megapiksel CCD (EXR format), 27mm başlangıçlı geniş açı lens ve 10x optik zoom ile seyahat kompaktı segmentini hedefleyen bir Fujifilm modelidir. EXR teknolojisi, farklı çekim koşullarına göre sensör optimizasyonu yapabiliyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12 MP EXR CCD</li>
<li><strong>Optik Zoom:</strong> 10x (27–270mm)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>EXR Mod:</strong> HR (Yüksek Çözünürlük), SN (Düşük Gürültü), DR (Geniş Dinamik Aralık)</li>
<li><strong>Stabilizasyon:</strong> Optik</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>EXR Teknolojisi: Fujifilm'in Akıllı Sensörü</h2>
<p>Fujifilm'in EXR sensörü, aynı piksel matrisinde farklı modlarda çalışabiliyor. HR modunda maksimum çözünürlük, SN modunda komşu pikselleri birleştirerek düşük ışık performansı, DR modunda ise aydınlık ve karanlık detayları aynı anda koruma. Bu esneklik, F80'i farklı koşullarda çok yönlü kılıyor.</p>

<h2>27mm Geniş Açı + 10x Zoom: Seyahat Dengesi</h2>
<p>Çoğu 10x zoom kompakt 35mm'den başlar. F80'in 27mm başlangıcı, dar mekânlarda, mimari çekimlerde ve grup fotoğraflarında ihtiyaç duyduğunuz ekstra genişliği sağlıyor. Telefoto ucundaki 270mm ise sahne detayları ve uzak mesafe çekimleri için yeterli.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğrafçılığı için geniş zoom aralıklı kompakt arayanlar</li>
<li>EXR sensör teknolojisini deneyimlemek isteyenler</li>
<li>Fujifilm F serisi koleksiyoncuları</li>
<li>27mm geniş açı + 10x zoom kombinasyonu arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>EXR modu otomatik seçilebilir mi?</h3>
<p>Evet, EXR Auto modunda kamera sahneyi analiz ederek otomatik mod seçer. Manuel olarak da seçilebilir.</p>
<h3>F80 pili hangisi?</h3>
<p>NP-50 Li-ion pil. Kolayca temin edilir.</p>
<h3>10x zoom ve optik stabilizasyon el titremesini önler mi?</h3>
<p>Önemli ölçüde azaltır. 270mm zoomda sabit bir yüzey veya monopod önerilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-f80" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix F80'i İncele →</a></div>
"""},

# ── Fujifilm FinePix Z10FD ───────────────────────────────────────────────────
{"title":"Fujifilm FinePix Z10FD İncelemesi: Yüz Tanıma Öncüsü, İnce Gövde ve CCD Sıcaklığı",
"handle":"fujifilm-finepix-z10fd-inceleme-yuz-tanima-ince-ccd",
"tags":"Fujifilm, Fujifilm FinePix Z10FD, yüz tanıma kamera, FinePix Z serisi, retro kamera, y2k kamera",
"meta_desc":"Fujifilm FinePix Z10FD incelemesi: 7.2MP CCD, otomatik yüz tanıma ve ince tasarım. Fujifilm'in yüz tanıma öncüsü retro kompaktını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0047_ONN01400_1e141fba-5745-4b6b-87a2-ab3fba6d89d0.jpg?v=1757179573",
"body":"""
<p>Akıllı telefonlar yüz tanımayı sıradan hale getirmeden önce Fujifilm bunu 2007'de kompakt kamerasına entegre etti. <strong>Fujifilm FinePix Z10FD</strong>, "FD" yani Face Detection özelliğiyle döneminin akıllı kameralarından biri.</p>

<h2>Fujifilm FinePix Z10FD Nedir?</h2>
<p>2007 çıkışlı Z10FD, 7.2 megapiksel CCD sensör ve Fujifilm'in o dönem öne çıkardığı Face Detection (FD) yüz tanıma teknolojisini barındıran Z serisinin en önemli modellerinden biri. "FD" isim soneki, bu özelliği vurgulamak için özellikle seçildi.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 7.2 MP CCD</li>
<li><strong>Yüz Tanıma:</strong> FD (Face Detection) — 10 yüze kadar</li>
<li><strong>Optik Zoom:</strong> 3x (35–105mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Gövde:</strong> İnce alüminyum</li>
<li><strong>Hafıza:</strong> xD-Picture Card</li>
<li><strong>Pil:</strong> NP-45</li>
</ul>

<h2>2007'de Yüz Tanıma: Devrimci mi?</h2>
<p>Bugün her kamerada olan yüz tanıma, 2007'de Fujifilm'in pazarlama cephesinde büyük yer tutuyordu. Z10FD bu özelliği Z serisine taşıyan model. 10 yüze kadar aynı anda tanıma, her yüze otomatik netlik — bu, aile ve grup çekimlerinde "bulanık yüz" sorununu büyük ölçüde çözdü.</p>

<h2>xD-Picture Card: Koleksiyonun Nadir Formatı</h2>
<p>Z10FD, Fujifilm ve Olympus'un ortak geliştirdiği xD-Picture Card kullanıyor. Bu format artık üretilmiyor; mevcut kartlar ikinci el platformlarda bulunabilir. Fotoğrafları aktarmak için All-in-One kart okuyucu gerekiyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Fujifilm Z serisi koleksiyoncuları</li>
<li>Yüz tanıma teknoloji tarihini merak edenler</li>
<li>xD kart formatını koleksiyonuna dahil etmek isteyenler</li>
<li>7MP Fujifilm CCD tonunu arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Z10FD xD kart olmadan çalışır mı?</h3>
<p>Küçük bir dahili bellek var ama yeterli değil. xD kart olmadan pratik kullanım zor.</p>
<h3>xD kart All-in-One okuyucuyla okunur mu?</h3>
<p>Evet, xD destekli All-in-One kart okuyucular bu kartı okuyabilir. Retrocameraland'de satılan All-in-One kart okuyucu xD formatını destekler.</p>
<h3>Z10FD koleksiyon değeri nedir?</h3>
<p>Z serisi içinde FD modelleri yüz tanıma tarihini temsil etmesiyle değer kazanıyor. xD kart kullanması da bu modeli "nadir format" koleksiyonu için çekici kılıyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-z10fd" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix Z10FD'yi İncele →</a></div>
"""},

# ── Fujifilm FinePix 1700Z ───────────────────────────────────────────────────
{"title":"Fujifilm FinePix 1700Z İncelemesi: 1999'dan Kalma Dijital Fotoğrafın İlk Büyük Adımı",
"handle":"fujifilm-finepix-1700z-inceleme-1999-dijital-ilk-adim",
"tags":"Fujifilm, Fujifilm FinePix 1700Z, erken dönem dijital kamera, 1999 kamera, koleksiyon kamera, FinePix serisi",
"meta_desc":"Fujifilm FinePix 1700Z incelemesi: 1999 yılından kalma 1.5MP Super CCD. Dijital fotoğrafın ilk büyük adımlarından birini temsil eden nadir koleksiyon kamera.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/fuji1.jpg?v=1752883267",
"body":"""
<p>1999. Milenyum eşiğinde, dijital kameralar hâlâ meraklıların nesnesi. <strong>Fujifilm FinePix 1700Z</strong>, o dönemde Fujifilm'in tüketici piyasasına yönelik en önemli modellerinden biriydi — ve bugün dijital fotoğraf tarihinin nadir koleksiyon parçası.</p>

<h2>Fujifilm FinePix 1700Z Nedir?</h2>
<p>1999 piyasaya çıkan FinePix 1700Z, 1.5 megapiksel Super CCD ve 3x optik zoom ile döneminin ciddi bir tüketici kamerasıydı. Fujifilm'in Super CCD teknolojisinin ilk nesil uygulamalarından biri olan bu model, dijital fotoğrafın henüz olgunlaşmadığı bir dönemin ürünü.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 1.5 MP Super CCD (Fujifilm ilk nesil)</li>
<li><strong>Optik Zoom:</strong> 3x (36–108mm)</li>
<li><strong>Ekran:</strong> 1.8" LCD</li>
<li><strong>Hafıza:</strong> SmartMedia kart (16MB dahil)</li>
<li><strong>Pil:</strong> CR-V3 veya AA × 2</li>
<li><strong>Üretim Yılı:</strong> 1999</li>
</ul>

<h2>1999'da 1.5MP: Döneminin Rekabetçi Modeli</h2>
<p>1999'da 1 megapiksel piyasa standartıydı. 1.5MP ile Fujifilm rakiplerine üstünlük kuruyordu. Bugün bu rakamlar nostaljik görünse de, o dönem fotoğraflar gazetelerde, web sitelerinde ve baskılarda kullanılıyordu — ve 1700Z yeterince yeterliydi.</p>

<h2>Dijital Fotoğraf Müzesinin Köşe Taşı</h2>
<p>1700Z, dijital fotoğrafın "erken dönem" koleksiyonunun en önemli örneklerinden biri. 1999 üretimi, çalışır durumda ve orijinal görünümünü koruyan bir dijital kamera bulmak giderek zorlaşıyor. Bu model koleksiyonlarda "dijital fotoğrafın başlangıcını" temsil ediyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>1990'ların sonu dijital fotoğraf tarihi koleksiyoncuları</li>
<li>Fujifilm Super CCD ilk nesil arayanlar</li>
<li>SmartMedia format koleksiyonu kuranlar</li>
<li>Dijital fotoğraf müzesi oluşturmak isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>FinePix 1700Z hâlâ çekim yapabilir mi?</h3>
<p>Çalışır durumda olanlarda evet. CR-V3 veya AA pil ile çalışır; SmartMedia kart gerekiyor.</p>
<h3>SmartMedia kart nereden bulunur?</h3>
<p>İkinci el platformlarda bulunabiliyor. 8 veya 16MB kart günlük çekim için yeterli.</p>
<h3>Bu kameranın fotoğrafları nasıl?</h3>
<p>1.5MP, 800×600 piksel çözünürlük sunar. Görüntüler web ve küçük baskı için yeterli ama büyük format için değil. Koleksiyon açısından teknik kalite değil tarihsel önemi ön planda.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-1700z-dijital-fotograf-makinesi" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix 1700Z'yi İncele →</a></div>
"""},

# ── Fujifilm Finepix XP60 ────────────────────────────────────────────────────
{"title":"Fujifilm FinePix XP60 İncelemesi: Su Geçirmez, Darbeye Dayanıklı Outdoor Kamera",
"handle":"fujifilm-finepix-xp60-inceleme-su-gecirmez-outdoor-kamera",
"tags":"Fujifilm, Fujifilm FinePix XP60, su geçirmez kamera, outdoor kamera, retro kamera, XP serisi",
"meta_desc":"Fujifilm FinePix XP60 incelemesi: 16.4MP CCD, 5 metreye kadar su geçirmezlik ve -10°C soğuk dayanımı. Outdoor meraklıları için ideal retro kompakt.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0001_ONN00348.jpg?v=1774655355",
"body":"""
<p>Havuz, deniz, dağ yürüyüşü ya da karlı hava — <strong>Fujifilm FinePix XP60</strong> bunların hepsinde çalışmak için tasarlandı. Fujifilm'in "her koşulda kamera" cevabı.</p>

<h2>Fujifilm FinePix XP60 Nedir?</h2>
<p>2013 çıkışlı FinePix XP60, 16.4 megapiksel CCD sensör ve Fujifilm'in XP serisine özgü dayanıklılık özellikleriyle donanmış bir outdoor kompakt kameradır. Su geçirmez, darbeye dayanıklı, soğuk dirençli ve toz korumalı dörtlü dayanıklılık standardı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 16.4 MP CCD</li>
<li><strong>Su Geçirmezlik:</strong> 5 metreye kadar (IPX8)</li>
<li><strong>Darbe Dayanımı:</strong> 1.5 metreden düşmeye</li>
<li><strong>Soğuk Dayanımı:</strong> -10°C</li>
<li><strong>Toz Koruması:</strong> Var</li>
<li><strong>Optik Zoom:</strong> 5x (28–140mm)</li>
<li><strong>Video:</strong> Full HD 1080/60p</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
</ul>

<h2>5 Metre Su Geçirmezlik: Tatil Fotoğrafçısının Dostu</h2>
<p>XP60, snorkeling derinliğine kadar su altı çekim yapabilir. Tatil fotoğrafçıları için bu, havuz çekimlerinden sahil su altına kadar geniş bir kullanım anlamına geliyor. Fujifilm'in CCD renk işlemesi su altında da karakterini koruyor — mavi tonlar ve su efektleri etkileyici sonuçlar veriyor.</p>

<h2>Full HD 60fps Video</h2>
<p>1080/60fps video, hareketli sahneleri akıcı kaydeder. Dalgaların içinde, kayak pistinde ya da çocukların koşu anında 60fps belirgin bir akıcılık farkı yaratıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Tatil, plaj ve havuz çekimleri yapanlar</li>
<li>Dağ yürüyüşü, kamp ve outdoor sporcular</li>
<li>Su geçirmez retro CCD kamera arayanlar</li>
<li>Fujifilm XP serisi dayanıklı kamera koleksiyoncuları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>5 metre su geçirmezliği snorkeling için yeterli mi?</h3>
<p>Evet, standart snorkeling 1-3 metrede yapılır. 5 metre sınır güvenli bir tampon sağlıyor. Derin dalış için bu kamera uygun değil.</p>
<h3>XP60 contaları kontrol edilmeli mi?</h3>
<p>Su altı kullanımından önce kapak contalarının hasarsız olduğunu kontrol etmek önemli. İkinci el örneklerde conta bütünlüğü test edilmeli.</p>
<h3>Fujifilm XP60 hâlâ günümüzde kullanılabilir mi?</h3>
<p>Kesinlikle. 16.4MP ve Full HD 60fps bugün de kullanışlı. SD kart ve pil kolayca temin ediliyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/fujifilm-finepix-xp60-waterproof" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Fujifilm FinePix XP60'ı İncele →</a></div>
"""},

# ── Olympus VG-130 ───────────────────────────────────────────────────────────
{"title":"Olympus VG-130 İncelemesi: Şık Tasarım, 14MP CCD ve Olympus Güvenilirliği",
"handle":"olympus-vg-130-inceleme-14mp-ccd-olympus-guvenilirlik",
"tags":"Olympus, Olympus VG-130, Olympus VG serisi, retro kamera, y2k kamera, CCD kompakt",
"meta_desc":"Olympus VG-130 incelemesi: 14MP CCD, 5x optik zoom ve şık kompakt gövde. Olympus'un güvenilir VG serisi retro kamerasını detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a-1_0031_ONN06228.jpg?v=1765745490",
"body":"""
<p>Olympus'un VG serisi, güvenilirlik ve kullanım kolaylığını şık bir gövdeyle birleştirdi. <strong>Olympus VG-130</strong>, bu serinin olgun döneminden kalma dengeli bir kompakt kamera.</p>

<h2>Olympus VG-130 Nedir?</h2>
<p>2011 çıkışlı VG-130, 14.0 megapiksel CCD sensör, 5x optik zoom ve Olympus'un TruePic görüntü işleme teknolojisiyle günlük kompakt kamera segmentinde güçlü bir seçenek. Şık alüminyum gövdesi ve çeşitli renk seçenekleriyle hem tasarım hem pratik kullanım açısından başarılı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 14 MP CCD (1/2.3")</li>
<li><strong>İşlemci:</strong> TruePic III+</li>
<li><strong>Optik Zoom:</strong> 5x (26–130mm)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>Sahneler:</strong> 10 farklı sahne modu</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Pil:</strong> LI-42B / LI-40B Li-ion</li>
</ul>

<h2>26mm Geniş Açı ile Olympus'un Avantajı</h2>
<p>VG-130'un 26mm geniş açılı başlangıcı, pek çok rakip kompaktın 35mm başlangıcına karşı belirgin bir avantaj. Dar mekânlar, grup fotoğrafları ve geniş manzaralar için bu fark her çekimde hissediliyor.</p>

<h2>Olympus TruePic Renk Karakteri</h2>
<p>Olympus'un TruePic işlemcisi, renkleri canlı ama doğallık sınırında tutuyor. Gökyüzü mavi, yapraklar yeşil, ciltler sıcak — abartısız, güvenilir bir renk paleti. Bu tutarlılık Olympus'un markayı diğer kompaktlardan ayıran özelliklerinden biri.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Olympus VG serisi koleksiyoncuları</li>
<li>Geniş açılı (26mm) CCD retro kompakt arayanlar</li>
<li>Günlük kullanım için güvenilir ve şık kamera isteyenler</li>
<li>Y2K estetik koleksiyonuna renk katmak isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>VG-130 hangi pil kullanır?</h3>
<p>LI-42B veya LI-40B Li-ion pil. Olympus'un yaygın pil modeli, kolayca temin edilir.</p>
<h3>Olympus VG-130 ile makro çekim yapılır mı?</h3>
<p>Evet, 10cm'ye kadar makro modu destekler.</p>
<h3>VG-130 fotoğrafları bilgisayara nasıl aktarılır?</h3>
<p>USB kablosu veya SD kart okuyucu ile. Olympus Viewer yazılımı ile de kullanılabilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-vg-130" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus VG-130'u İncele →</a></div>
"""},

# ── Olympus SP-320 ───────────────────────────────────────────────────────────
{"title":"Olympus SP-320 İncelemesi: Prosümer Kompakt, Manuel Kontrol ve CCD Kalitesi",
"handle":"olympus-sp-320-inceleme-prosumer-manuel-ccd-kalite",
"tags":"Olympus, Olympus SP-320, prosümer kamera, manuel kontrol, retro kamera, SP serisi",
"meta_desc":"Olympus SP-320 incelemesi: 7.1MP CCD, PASM manuel modlar ve prosümer kompakt özellikler. Olympus'un fotoğrafçı odaklı retro kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0185_ONN04938.jpg?v=1765241010",
"body":"""
<p>Tam otomatik değil, tam manuel de değil — ama her ikisinden de en iyisini sunuyor. <strong>Olympus SP-320</strong>, fotoğrafçıya kontrol veren, ama kompakt taşınabilirliği koruyabilen bir prosümer model.</p>

<h2>Olympus SP-320 Nedir?</h2>
<p>2006 çıkışlı SP-320, 7.1 megapiksel CCD sensör, P/A/S/M manuel mod desteği ve Olympus'un SP serisine özgü prosümer özellikleriyle hobi fotoğrafçılarını hedefleyen bir kompakt kameradır.</p>

<h2>Teknik Özellikler</html>
<ul>
<li><strong>Sensör:</strong> 7.1 MP CCD (1/2.5")</li>
<li><strong>Modlar:</strong> P / A / S / M (tam manuel)</li>
<li><strong>Lens:</strong> 3x optik zoom (38–114mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>ISO:</strong> 64–1600</li>
<li><strong>Enstantane:</strong> 15s–1/2000s</li>
<li><strong>Hafıza:</strong> xD-Picture Card</li>
<li><strong>Pil:</strong> LI-42B</li>
</ul>

<h2>P/A/S/M Modları: Tam Kontrol</h2>
<p>Aperture Priority (A), Shutter Priority (S) ve tam Manuel (M) modlar, fotoğrafçıya kompakt gövdede DSLR seviyesinde kontrol sunuyor. Alan derinliği için diyafram önceliği, hareket dondurmak için enstantane önceliği — SP-320'de her ikisi de mevcut.</p>

<h2>15 Saniyeye Kadar Uzun Pozlama</h2>
<p>15 saniyelik enstantane, gece manzarası ve ışık boyama çekimleri için yeterli. Tripod ile SP-320 gece fotoğrafçılığında da başarılı sonuçlar veriyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Manuel kontrolü önemseyen retro kompakt kullanıcıları</li>
<li>Olympus SP serisi prosümer koleksiyoncuları</li>
<li>Gece fotoğrafçılığı için uzun pozlama isteyen kompakt kullanıcıları</li>
<li>A/S/M mod desteğiyle öğrenmek isteyen başlangıç fotoğrafçıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Olympus SP-320 RAW destekler mi?</h3>
<p>Hayır, JPEG kaydeder. Olympus'un o dönem kompakt SP modelleri RAW desteklemiyordu.</p>
<h3>SP-320 xD kart mı kullanır?</h3>
<p>Evet, xD-Picture Card kullanır. All-in-One kart okuyucu ile modern bilgisayara aktarım yapılabilir.</p>
<h3>Manuel mod öğrenmek için uygun mu?</h3>
<p>Evet, PASM modlar tam destekleniyor. Kompakt boyutta manuel modu öğrenmek için ideal başlangıç noktası.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-sp-320" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus SP-320'yi İncele →</a></div>
"""},

# ── Olympus SZ-10 ────────────────────────────────────────────────────────────
{"title":"Olympus SZ-10 İncelemesi: 18x Süper Zoom, Geniş Açı ve SZ Serisinin Gücü",
"handle":"olympus-sz-10-inceleme-18x-super-zoom-genis-aci-sz-serisi",
"tags":"Olympus, Olympus SZ-10, süper zoom kamera, 18x zoom, retro kamera, seyahat kamerası",
"meta_desc":"Olympus SZ-10 incelemesi: 14MP CCD, 18x optik zoom ve 25mm geniş açı. Olympus'un güçlü süper zoom kompaktını seyahat fotoğrafçılığı perspektifinden inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/olympus_sz10_57dec200-1d86-4289-b279-e688af355d26.jpg?v=1776638236",
"body":"""
<p>18x optik zoom, gözün göremediği detayları kameranın görmesini sağlar. <strong>Olympus SZ-10</strong>, 25mm geniş açıdan 450mm telefotoya uzanan bu inanılmaz aralığı kompakt bir gövdede sunuyor.</p>

<h2>Olympus SZ-10 Nedir?</h2>
<p>2011 çıkışlı SZ-10, 14 megapiksel CCD sensör ve 18x optik zoom (25–450mm eşdeğer) ile seyahat ve outdoor fotoğrafçılığı için optimize edilmiş bir kompakt kameradır. SZ (Super Zoom) serisinin olgun dönem modeli.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 14 MP CCD</li>
<li><strong>Optik Zoom:</strong> 18x (25–450mm)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Stabilizasyon:</strong> Dual IS (optik + dijital)</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Sahne Modları:</strong> 10+ sahne modu</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
</ul>

<h2>25–450mm: Hangi Sahneler İçin?</h2>
<ul>
<li><strong>25mm:</strong> Geniş manzaralar, mimari, grup fotoğrafları</li>
<li><strong>50–100mm:</strong> Sokak fotoğrafçılığı, portre</li>
<li><strong>200–450mm:</strong> Kuşlar, vahşi hayat, spor, sahne çekimleri</li>
</ul>
<p>Tek kamerayla bu aralığı kapatmak, seyahatte gereksiz ağırlık taşımaktan kurtarıyor.</p>

<h2>Dual IS Stabilizasyon</h2>
<p>SZ-10'un Dual IS sistemi, optik ve dijital stabilizasyonu birleştiriyor. Yüksek zoomda bu kombinasyon, elle tutmayı önemli ölçüde kolaylaştırıyor. Yine de 300mm+ zoomda sabit bir yüzey önerilir.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Geniş zoom aralıklı seyahat kamerası arayanlar</li>
<li>Kuş ve doğa fotoğrafçılığı meraklıları</li>
<li>Olympus SZ serisi koleksiyoncuları</li>
<li>18x zoom'u kompakt gövdede isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>18x zoom ile kuş fotoğrafı çekilir mi?</h3>
<p>Evet, 450mm'ye kadar uzanan telefoto doğa fotoğrafçılığı için kullanılabilir. Sakin kuşlarda çok başarılı; hızlı hareket eden türler için odak hızı sınırlayıcı olabilir.</p>
<h3>SZ-10 pili nereden bulunur?</h3>
<p>LI-50B Li-ion pil. Olympus'un geniş uyumlu pil modeli, kolayca temin edilir.</p>
<h3>18x zoom ile video çekilir mi?</h3>
<p>Evet, video çekiminde de tam optik zoom kullanılabilir. Dual IS sistemi video kaydında da etkin.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-sz-10" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus SZ-10'u İncele →</a></div>
"""},

# ── Olympus SZ-14 ────────────────────────────────────────────────────────────
{"title":"Olympus SZ-14 İncelemesi: 24x Devasa Zoom ve Full HD Video ile SZ Serisinin Zirvesi",
"handle":"olympus-sz-14-inceleme-24x-zoom-fullhd-sz-serisi-zirve",
"tags":"Olympus, Olympus SZ-14, 24x zoom kamera, Full HD kamera, retro kamera, süper zoom",
"meta_desc":"Olympus SZ-14 incelemesi: 16MP CCD, 24x optik zoom ve Full HD 1080p video. Olympus SZ serisinin zirve modeli ve süper zoom kompaktta ne anlama geldiğini anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0062_ONN01385.jpg?v=1758554515",
"body":"""
<p>24x optik zoom, neredeyse konsere gitmeden önden sıradan müzisyen detaylarını yakalamak demek. <strong>Olympus SZ-14</strong>, SZ serisinin en güçlü modeli ve süper zoom kategorisinin nadir temsilcilerinden biri.</p>

<h2>Olympus SZ-14 Nedir?</h2>
<p>2012 çıkışlı SZ-14, 16 megapiksel CCD sensör ve 24x optik zoom (25–600mm eşdeğer) ile SZ serisinin amiral gemisi. Full HD 1080p video kaydı, dual IS stabilizasyon ve geniş 25mm açısıyla hem fotoğraf hem video açısından güçlü bir paket.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 16 MP CCD</li>
<li><strong>Optik Zoom:</strong> 24x (25–600mm)</li>
<li><strong>Video:</strong> Full HD 1080/30p</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Stabilizasyon:</strong> Dual IS</li>
<li><strong>ISO:</strong> 100–3200</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
</ul>

<h2>25–600mm: Seyahatte Her Şey</h2>
<p>600mm eşdeğer zoom, satın alabileceğiniz en uzun kompakt zoom aralıklarından biri. Bir yandan 25mm geniş açı manzara fotoğrafçılığına, öte yandan 600mm telefoto ufukta kaybolan gemileri veya uzak dağ zirvelerini çekmeye imkân tanıyor.</p>

<h2>Full HD Video: SZ Serisinin Farkı</h2>
<p>SZ-14'ün 1080p video kaydı, süper zoom kompaktlar arasında o dönem en iyi videolardan birini sunuyordu. Optik zoom video sırasında da çalışıyor — sahneden yakından canlı performans kaydı mümkün.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>En geniş zoom aralıklı retro kompakt arayanlar</li>
<li>Full HD video destekli süper zoom isteyenler</li>
<li>Olympus SZ serisi koleksiyoncuları</li>
<li>Seyahat, doğa, spor ve sahne fotoğrafçıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>24x zoom elle tutularak kullanılabilir mi?</h3>
<p>Dual IS yardımıyla orta mesafelerde evet. 600mm yakınında sabit yüzey veya monopod kesinlikle önerilir.</p>
<h3>SZ-14 aynı pili mi kullanıyor SZ-10 ile?</h3>
<p>Evet, her ikisi de LI-50B Li-ion pil kullanır — kolayca temin edilir.</p>
<h3>16MP CCD büyük baskı için yeterli mi?</h3>
<p>A3 baskıya kadar yeterli. Daha büyük formatlar için piksel başına kalite sınırlı olabilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-sz-14" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus SZ-14'ü İncele →</a></div>
"""},

# ── Olympus VG-110 ───────────────────────────────────────────────────────────
{"title":"Olympus VG-110 İncelemesi: Giriş Seviyesi Şıklık ve Olympus'un CCD Güvencesi",
"handle":"olympus-vg-110-inceleme-giris-seviyesi-sik-ccd-guvence",
"tags":"Olympus, Olympus VG-110, giriş seviyesi kamera, retro kamera, VG serisi, y2k kamera",
"meta_desc":"Olympus VG-110 incelemesi: 12MP CCD, 4x optik zoom ve ince kompakt gövde. Olympus'un giriş seviyesi retro kompaktını ve Y2K koleksiyondaki yerini inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0083_ONN01364.jpg?v=1757179954",
"body":"""
<p>Her koleksiyonun bir "günlük taşınan" kamerası vardır. <strong>Olympus VG-110</strong>, hem rafta güzel duran hem çantada taşınabilecek, hem de her zaman çekime hazır pratik bir Olympus modeli.</p>

<h2>Olympus VG-110 Nedir?</h2>
<p>2011 çıkışlı VG-110, 12 megapiksel CCD sensör ve 4x optik zoom ile giriş seviyesi kompakt kamera segmentinin güçlü bir temsilcisi. Olympus'un sade ama şık tasarım anlayışı ve TruePic görüntü işleme kalitesi bu modelde de kendini gösteriyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12 MP CCD</li>
<li><strong>Optik Zoom:</strong> 4x (28–112mm)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>ISO:</strong> 80–1600</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Pil:</strong> LI-42B / LI-40B</li>
</ul>

<h2>28mm Geniş Açı ile Olympus'un Tutarlılığı</h2>
<p>VG serisi, giriş seviyesi model olmasına rağmen 28mm geniş açı başlangıcını koruyor. Bu, pek çok rakip giriş modelinin 35mm'sinden belirgin biçimde daha geniş. Dar alanlarda ve grup çekimlerinde bu fark anında hissedilir.</p>

<h2>Olympus TruePic: Tutarlı Renk Kalitesi</h2>
<p>VG-110'un TruePic işlemcisi, Olympus'un daha pahalı modellerinde de kullandığı renk işleme motorunun optimize edilmiş versiyonu. Tutarlı, doğal ve canlı renk karakteri, bu modeli günlük çekim için güvenilir kılıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Olympus VG serisi koleksiyonu tamamlamak isteyenler</li>
<li>İlk retro kompakt kamera arayanlar</li>
<li>Günlük taşıma ve spontane çekim için pratik kamera isteyenler</li>
<li>12MP CCD tonu arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>VG-110 ile VG-130 arasındaki fark nedir?</h3>
<p>VG-130 daha yüksek çözünürlük (14MP vs 12MP) ve ek sahne modlarına sahip. Temel kullanım için VG-110 yeterli.</p>
<h3>Olympus VG-110 pili nereden bulunur?</h3>
<p>LI-42B veya LI-40B — Olympus'un geniş uyumlu pil modeli, kolayca temin edilir.</p>
<h3>VG-110 SD kart boyutu?</h3>
<p>SD ve SDHC uyumlu. 8-16 GB SDHC yeterli kapasite sunar.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-vg-110" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus VG-110'u İncele →</a></div>
"""},

# ── Olympus SP-700 ───────────────────────────────────────────────────────────
{"title":"Olympus SP-700 İncelemesi: 6MP CCD, Geniş Açı ve Prosümer Kontrol Bir Arada",
"handle":"olympus-sp-700-inceleme-6mp-ccd-genis-aci-prosumer",
"tags":"Olympus, Olympus SP-700, prosümer kamera, geniş açı kamera, retro kamera, SP serisi",
"meta_desc":"Olympus SP-700 incelemesi: 6MP CCD, 28mm geniş açı ve PASM manuel kontrol. Olympus SP serisinin kompakt prosümer modelini detaylıca inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0090_ONN05033.jpg?v=1765239010",
"body":"""
<p>Prosümer kontrolü, kompakt taşınabilirliği. <strong>Olympus SP-700</strong>, bu ikisini 2006 yılında 28mm geniş açıyla buluşturan dengeli bir model.</p>

<h2>Olympus SP-700 Nedir?</h2>
<p>2006 çıkışlı SP-700, 6 megapiksel CCD sensör, 28mm geniş açı başlangıçlı 5x optik zoom ve PASM manuel modlarıyla prosümer kompakt segmentinde Olympus'un güçlü çıkışlarından biri. SP serisi, amatör-prosümer arasındaki boşluğu kapatmak için tasarlanmıştı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 6 MP CCD (1/2.5")</li>
<li><strong>Lens:</strong> 5x optik zoom (28–140mm)</li>
<li><strong>Modlar:</strong> P / A / S / M</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Enstantane:</strong> 16s–1/2000s</li>
<li><strong>ISO:</strong> 50–1600</li>
<li><strong>Hafıza:</strong> xD-Picture Card</li>
</ul>

<h2>28mm'den Başlayan Geniş Açı</h2>
<p>SP-700'ün en büyük avantajlarından biri 28mm başlangıcı. Bu, standart 35mm'li kompaktlara kıyasla daha geniş perspektif — sokak fotoğrafçılığında, mimaride, iç mekân çekimlerinde bu fark belirleyici.</p>

<h2>16 Saniye Uzun Pozlama</h2>
<p>M modunda 16 saniyeye kadar uzun pozlama imkânı, gece fotoğrafçılığında çok yönlülük sunuyor. Işıklı yollar, aydınlatılmış binalar, yıldızlı gökyüzü — tripod ile SP-700 çekimde güçlü bir model.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Manuel kontrolü önemseyen CCD kompakt arayanlar</li>
<li>Gece ve uzun pozlama fotoğrafçıları</li>
<li>Olympus SP serisi koleksiyoncuları</li>
<li>28mm geniş açılı prosümer retro kamera arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>SP-700 xD kart mı kullanır?</h3>
<p>Evet, xD-Picture Card. All-in-One kart okuyucu ile modern bilgisayara aktarım yapılabilir.</p>
<h3>6MP yeterli çözünürlük mü?</h3>
<p>Sosyal medya, web kullanımı ve A4 baskı için yeterli. Büyük format baskılar için daha yüksek MP önerilir.</p>
<h3>SP-700 ile sokak fotoğrafçılığı yapılır mı?</h3>
<p>28mm geniş açı ve kompakt gövde, sokak fotoğrafçılığı için ideal bir kombinasyon. Dikkat çekmeden, hızlıca çekim yapılabilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/olympus-sp-700" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Olympus SP-700'ü İncele →</a></div>
"""},

]

def run():
    results = []
    for i, p in enumerate(POSTS, 1):
        log(f"\n[{i}/{len(POSTS)}] {p['title'][:65]}...")
        try:
            aid, handle = pub(p["title"], p["handle"], p["tags"], p["meta_desc"], p.get("image_src"), p["body"])
            results.append({"status":"ok","title":p["title"]})
        except Exception as e:
            log(f"  ❌ {e}")
            results.append({"status":"error","title":p["title"],"error":str(e)})
    log("\n=== BATCH 3 SONUÇ ===")
    ok = sum(1 for r in results if r["status"]=="ok")
    for r in results:
        log(f"  {'✅' if r['status']=='ok' else '❌'} {r['title'][:55]}")
    log(f"\n{ok}/{len(POSTS)} yayınlandı.")

if __name__ == "__main__":
    run()
