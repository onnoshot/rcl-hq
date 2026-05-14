#!/usr/bin/env python3
"""Batch 4: Panasonic (5) + Sanyo (4) + Kodak (5) = 14 ürün"""
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

# ── Panasonic Lumix DMC-LZ7 ──────────────────────────────────────────────────
{"title":"Panasonic Lumix DMC-LZ7 İncelemesi: 6x Zoom, Leica Lens ve Lumix'in Güvenilir Seyahat Kompaktı",
"handle":"panasonic-lumix-dmc-lz7-inceleme-6x-zoom-leica-seyahat",
"tags":"Panasonic, Panasonic Lumix DMC-LZ7, Lumix LZ serisi, Leica lens, retro kamera, seyahat kamerası",
"meta_desc":"Panasonic Lumix DMC-LZ7 incelemesi: 7.2MP CCD, Leica DC Vario-Elmarit 6x zoom. Lumix'in seyahat odaklı kompakt kamerasını detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0124_ONN04999.jpg?v=1765239445",
"body":"""
<p>Leica optikli, 6x zoomlu ve Panasonic güvencesiyle <strong>Lumix DMC-LZ7</strong>, seyahatte yanından ayırmak istemeyeceğiniz kompakt kameralardan biri.</p>

<h2>Panasonic Lumix DMC-LZ7 Nedir?</h2>
<p>2007 çıkışlı DMC-LZ7, 7.2 megapiksel CCD sensör ve Leica DC Vario-Elmarit 6x optik zoom lensiyle Lumix'in LZ (Long Zoom) serisinin güçlü temsilcisi. Seyahat fotoğrafçılığı için dengeli bir zoom aralığı ve Leica optik kalitesi sunuyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 7.2 MP CCD</li>
<li><strong>Lens:</strong> Leica DC Vario-Elmarit 6x (35–210mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Stabilizasyon:</strong> MEGA O.I.S. optik</li>
<li><strong>ISO:</strong> 80–1600</li>
<li><strong>Video:</strong> VGA 30fps</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>Leica DC Vario-Elmarit: LZ Serisinin Farkı</h2>
<p>Lumix LZ serisi, rakip uzun zoom kompaktlarına karşı en güçlü argümanı Leica optikle sundu. Elmarit serisi lensler renk saflığı, kontrast ve vinjeting kontrolü açısından kompakt kamera dünyasında ayrı bir yerde duruyor.</p>

<h2>6x Zoom ile Seyahat Esnekliği</h2>
<p>35mm'den başlayan geniş açı ve 210mm'ye uzanan telefoto, seyahatte karşılaşılan sahnelerin büyük çoğunluğunu karşılıyor. Pazar yerleri, mimarî detaylar, uzaktaki dağ silüetleri — hepsini tek lensle kadraya alabilirsiniz.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Leica lens kaliteli retro seyahat kompaktı arayanlar</li>
<li>Lumix LZ serisi koleksiyoncuları</li>
<li>6x uzun zoom tercih eden günlük kullanıcılar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>LZ7 pili hangisi?</h3>
<p>DMW-BCE10E Li-ion pil. Hâlâ üçüncü parti alternatifleri mevcut.</p>
<h3>Leica ismi kalite farkı yaratıyor mu?</h3>
<p>Evet, Leica DC sertifikasyonu belirli optik kalite standartlarını karşıladığını garantiliyor. Sonuçlarda özellikle kontrast ve renk doğruluğunda fark belirgin.</p>
<h3>MEGA O.I.S. ne kadar etkili?</h3>
<p>Panasonic'in optik stabilizasyonu, el titremesini belirgin ölçüde azaltır. 6x zoomda etkisi özellikle hissedilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/panasonic-lumix-dmc-lz7" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Lumix DMC-LZ7'yi İncele →</a></div>
"""},

# ── Panasonic Lumix DMC-LS75 ─────────────────────────────────────────────────
{"title":"Panasonic Lumix DMC-LS75 İncelemesi: AA Pilli, Geniş Açılı ve Güvenilir Günlük Kompakt",
"handle":"panasonic-lumix-dmc-ls75-inceleme-aa-pilli-genis-aci-kompakt",
"tags":"Panasonic, Panasonic Lumix DMC-LS75, Lumix LS serisi, AA pil kamera, retro kamera, günlük kompakt",
"meta_desc":"Panasonic Lumix DMC-LS75 incelemesi: 7.2MP CCD, AA pil ve Leica optik. Seyahatte pil endişesi yaşatmayan Lumix'in güvenilir kompaktını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0098_ONN05025.jpg?v=1765239114",
"body":"""
<p>Şarj edilmesi gereken özel pil değil, dünyenin her köşesinde bulunan AA pil. <strong>Panasonic Lumix DMC-LS75</strong>, bu basit ama çok değerli özelliğiyle seyahat fotoğrafçılarının tercihi.</p>

<h2>Panasonic Lumix DMC-LS75 Nedir?</h2>
<p>2007 çıkışlı DMC-LS75, 7.2 megapiksel CCD sensör ve Leica DC Vario-Elmarit lens ile AA pil kullanan geniş açılı bir Lumix kompakttır. LS serisi, özellikle seyahat sırasında pil erişim kolaylığı arayanlar için tasarlandı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 7.2 MP CCD</li>
<li><strong>Lens:</strong> Leica DC Vario-Elmarit 3x (28–84mm)</li>
<li><strong>Pil:</strong> AA × 2 adet</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Stabilizasyon:</strong> MEGA O.I.S. optik</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>28mm Geniş Açı ve AA Pil Kombinasyonu</h2>
<p>Bu iki özellik birlikte çok güçlü bir seyahat paketi oluşturuyor. 28mm geniş açı ile dar sokakları ve geniş meydanları rahatça çerçeveleyebilirsiniz; AA pil ile ise herhangi bir ülkede, herhangi bir süpermarketten pil alıp devam edebilirsiniz.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Uzun seyahat ve trekking için AA pilli kamera arayanlar</li>
<li>Lumix LS serisi koleksiyoncuları</li>
<li>Leica optik kaliteli AA pilli kompakt isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>AA pil ne kadar dayanır?</h3>
<p>Kaliteli alkalin AA pil ile yaklaşık 150-200 kare çekim beklenilebilir. Lithium AA piller daha uzun ömürlü.</p>
<h3>LS75 SD kart mı kullanır?</h3>
<p>Evet, SD ve SDHC kart uyumludur.</p>
<h3>28mm mi 35mm mi daha iyi?</h3>
<p>Seyahat ve mimari için 28mm belirgin avantaj. Portre ve günlük çekim için fark daha az hissedilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/panasonic-lumix-dmc-ls75" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Lumix DMC-LS75'i İncele →</a></div>
"""},

# ── Panasonic Lumix DMC FX10 ─────────────────────────────────────────────────
{"title":"Panasonic Lumix DMC-FX10 İncelemesi: Ultra İnce Leica Lens ve CCD Mükemmeliyeti",
"handle":"panasonic-lumix-dmc-fx10-inceleme-ultra-ince-leica-ccd",
"tags":"Panasonic, Panasonic Lumix DMC-FX10, ultra ince kamera, Leica lens, retro kamera, FX serisi",
"meta_desc":"Panasonic Lumix DMC-FX10 incelemesi: 6MP CCD, Leica DC Vario-Elmarit ve ultra ince alüminyum gövde. Lumix FX serisinin şıklığını ve kalitesini inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/lumix_leica.jpg?v=1759849574",
"body":"""
<p>Ultra ince gövdede Leica optik kalitesi. <strong>Panasonic Lumix DMC-FX10</strong>, Lumix'in en iddialı premium kompakt serisinin karakteristik modeli.</p>

<h2>Panasonic Lumix DMC-FX10 Nedir?</h2>
<p>2006 çıkışlı DMC-FX10, 6.0 megapiksel CCD sensör ve Leica DC Vario-Elmarit 3.6x optik zoom lensini ultra ince bir alüminyum gövdede buluşturan bir Lumix kompakttır. FX (Flexible) serisi, ince tasarım ve Leica lens kalitesinin birleştiği premium Lumix modellerini kapsıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 6 MP CCD</li>
<li><strong>Lens:</strong> Leica DC Vario-Elmarit 3.6x (28–100mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Stabilizasyon:</strong> MEGA O.I.S.</li>
<li><strong>ISO:</strong> 80–1600</li>
<li><strong>Kalınlık:</strong> ~21mm (ultra ince)</li>
<li><strong>Gövde:</strong> Alüminyum</li>
</ul>

<h2>Leica Vario-Elmarit + Ultra İnce: Premium Kompakta Yeni Standart</h2>
<p>FX10, Leica optik kalitesini ultra ince bir gövdeye sığdırmasıyla döneminin premium kompakt segmentinde özel bir yer edindi. Alüminyum kasası ve Leica ismi, o dönem kompakt kamera raflarında hemen dikkat çekiyordu.</p>

<h2>28mm Geniş Açı: FX Serisinin Avantajı</h2>
<p>FX10'un 28mm başlangıcı, standart 35mm'li rakiplerine belirgin avantaj sağlıyor. Seyahat, mimari ve günlük çekim için bu geniş açı hem kullanışlı hem de yaratıcı yeni kadrajlara kapı açıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Ultra ince Leica lens kaliteli kamera arayanlar</li>
<li>Lumix FX serisi koleksiyoncuları</li>
<li>Premium CCD kompakt koleksiyonu kuranlar</li>
<li>Cebine sığar boyutta geniş açı Lumix isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>FX10 pili hangisi?</h3>
<p>DMW-BCF10E Li-ion pil. Panasonic'in yaygın pil modeli.</p>
<h3>Leica ismi gerçekten bir fark yaratıyor mu?</h3>
<p>Leica DC sertifikasyonu belirli optik test standartlarını gerektiriyor. Sonuçlarda özellikle kontrast ve renk tutarlılığında fark gözlemlenebilir.</p>
<h3>FX10 ile gece çekimi nasıl?</h3>
<p>MEGA O.I.S. stabilizasyon yardımıyla orta ışıklı ortamlarda iyi sonuç verir. Düşük ISO'da temiz görüntü sunar.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/panasonic-lumix-dmc-fx10" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Lumix DMC-FX10'u İncele →</a></div>
"""},

# ── Panasonic LUMIX DC-TZ99 ──────────────────────────────────────────────────
{"title":"Panasonic LUMIX DC-TZ99 İncelemesi: 30x Zoom, EVF ve 2024'ün En Güçlü Seyahat Kompaktı",
"handle":"panasonic-lumix-dc-tz99-inceleme-30x-zoom-evf-seyahat",
"tags":"Panasonic, Panasonic LUMIX DC-TZ99, 30x zoom, EVF kamera, modern kompakt, 4K video, seyahat kamerası",
"meta_desc":"Panasonic LUMIX DC-TZ99 incelemesi: 30x Leica zoom, dahili EVF vizör ve 4K video. Seyahat kompaktında en iyi özellikleri bir arada sunan güçlü model.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/lumix_tz99.jpg?v=1758419651",
"body":"""
<p>30x optik zoom, dahili vizör (EVF) ve 4K video — bunların hepsi tek kompakt gövdede. <strong>Panasonic LUMIX DC-TZ99</strong>, seyahat fotoğrafçılığında "tek kamera ile her şey" idealini en iyi karşılayan modern kompaktlardan biri.</p>

<h2>Panasonic LUMIX DC-TZ99 Nedir?</h2>
<p>TZ (Travel Zoom) serisinin zirve modeli olan DC-TZ99, 20.3 megapiksel 1 inç CMOS sensör, 30x Leica DC Vario-Elmar optik zoom, dahili EVF (Electronic Viewfinder) ve 4K video özelliklerini kompakt bir gövdede birleştiriyor. Seyahat kompaktı kategorisinin günümüzdeki en kapsamlı paketi.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 20.3 MP 1 inç CMOS (büyük sensör!)</li>
<li><strong>Lens:</strong> Leica DC Vario-Elmar 30x (24–720mm)</li>
<li><strong>Vizör:</strong> Dahili EVF (Electronic Viewfinder)</li>
<li><strong>Video:</strong> 4K 30fps / FHD 60fps</li>
<li><strong>Ekran:</strong> 3" döner dokunmatik LCD</li>
<li><strong>Stabilizasyon:</strong> Hibrit O.I.S. (optik + dijital)</li>
<li><strong>Bağlantı:</strong> Wi-Fi, Bluetooth, USB-C</li>
<li><strong>RAW:</strong> Destekler</li>
</ul>

<h2>1 İnç Sensör + 30x Zoom: Eşsiz Kombinasyon</h2>
<p>Kompakt kameralarda 30x zoom genellikle küçük sensörle geliyor. TZ99'un 1 inç sensörü bu denklemi değiştiriyor — büyük sensör sayesinde düşük ışık performansı, dinamik aralık ve genel görüntü kalitesi rakip kompaktların çok üzerinde. Leica lens kalitesi de bu paketi tamamlıyor.</p>

<h2>Dahili EVF: Neden Önemli?</h2>
<p>Parlak güneş altında LCD ekranlar neredeyse görünmez hale gelir. Dahili EVF, güneşli plajda, kar pistinde veya karşı güneşe bakarak çekerken kadrajı net görmenizi sağlar. Bu özellik kompaktta nadir bulunuyor ve TZ99'u rakiplerinden ayırıyor.</p>

<h2>24–720mm Aralığı</h2>
<p>24mm geniş açı manzara ve mimari; 720mm ise uzak kuşlar, sahne detayları ve spor için kullanılabilir. Bu aralık, DSLR dünyasında birden fazla lens gerektirirdi.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğrafçılığında "tek kamera" çözümü arayanlar</li>
<li>Büyük sensörlü, geniş zoomlu kompakt isteyenler</li>
<li>4K video ve RAW çekim destekli modern kompakt tercih edenler</li>
<li>EVF vizörlü kompakt kamera arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>TZ99 rakibi TZ100'den üstün mü?</h3>
<p>TZ99, TZ100'ün halefi ve daha gelişmiş özelliklere sahip — daha iyi AF sistemi, güncel arayüz ve bağlantı seçenekleri.</p>
<h3>RAW çekim Lightroom'da açılır mı?</h3>
<p>Evet, Panasonic RW2 RAW formatı Adobe Lightroom ve Capture One'da tam desteklenir.</p>
<h3>30x zoom için tripod gerekli mi?</h3>
<p>Hibrit O.I.S. ile 300-400mm'ye kadar elle tutuş pratikte mümkün. 600mm+ için monopod veya tripod önerilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/panasonic-lumix-dc-tz99" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">LUMIX DC-TZ99'u İncele →</a></div>
"""},

# ── Lumix DMC-FT3 ────────────────────────────────────────────────────────────
{"title":"Panasonic Lumix DMC-FT3 İncelemesi: 12 Metre Su Geçirmez, GPS'li Outdoor Kamera",
"handle":"panasonic-lumix-dmc-ft3-inceleme-12m-su-gecirmez-gps-outdoor",
"tags":"Panasonic, Panasonic Lumix DMC-FT3, su geçirmez kamera, GPS kamera, outdoor kamera, Lumix FT serisi",
"meta_desc":"Panasonic Lumix DMC-FT3 incelemesi: 12.1MP CCD, 12 metre su geçirmezlik ve dahili GPS. Dalış ve outdoor için Leica lensli güçlü dayanıklı kamera.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0025_ONN00324.jpg?v=1774655360",
"body":"""
<p>12 metre derinliğe kadar su geçirmez, 2 metreden düşmeye dayanıklı ve üstelik GPS'li. <strong>Panasonic Lumix DMC-FT3</strong>, dayanıklı kamera kategorisinin en kapsamlı özellik setlerinden birini sunuyor.</p>

<h2>Panasonic Lumix DMC-FT3 Nedir?</h2>
<p>2011 çıkışlı DMC-FT3 (bazı pazarlarda TS3 olarak anılır), Lumix'in FT serisi dayanıklı kameralarının ikinci nesil modeli. 12.1 megapiksel CCD, Leica DC Vario-Elmarit lens, 12 metre su geçirmezlik ve dahili GPS ile outdoor fotoğrafçılığın en eksiksiz kompaktlarından biri.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD</li>
<li><strong>Lens:</strong> Leica DC Vario-Elmarit 4.6x (28–128mm)</li>
<li><strong>Su Geçirmezlik:</strong> 12 metreye kadar</li>
<li><strong>Darbe Dayanımı:</strong> 2 metreden düşmeye</li>
<li><strong>Soğuk Dayanımı:</strong> -10°C</li>
<li><strong>GPS:</strong> Dahili, fotoğraflara koordinat kaydeder</li>
<li><strong>Video:</strong> Full HD 1080/60p</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
</ul>

<h2>12 Metre: Gerçek Dalış Kamerası</h2>
<p>FT10 5 metreye dayanıklıydı. FT3 bunu 12 metreye çıkardı. Bu, hobici dalış (snorkeling + sığ scuba) için gerçek bir güvenlik marjı. Kıbrıs, Maldivler veya Bodrum dalış turlarında ek dalış kılıfına ihtiyaç duymadan kullanabilirsiniz.</p>

<h2>Dahili GPS ile Fotoğraf Haritası</h2>
<p>FT3'ün dahili GPS'i, çekilen her fotoğrafa GPS koordinatı ekler. Dağ yürüyüşlerinde, seyahatte veya dalış noktalarını kayıt altına almak için çok kullanışlı. Google Haritalar veya Lightroom'da fotoğrafların nerede çekildiğini harita üzerinde görüntüleyebilirsiniz.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Dalış ve su sporları fotoğrafçıları</li>
<li>GPS'li outdoor kamera arayanlar</li>
<li>Dağ yürüyüşü ve kamp meraklıları</li>
<li>Lumix FT serisi dayanıklı kamera koleksiyoncuları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>12 metre su altında fotoğraf kalitesi nasıl?</h3>
<p>CCD ve Leica lens kombinasyonu su altında da iyi sonuç verir. Derinlik arttıkça mavi filtreli görüntü için flaş veya kırmızı filtre düzeltici önerilebilir.</p>
<h3>GPS açık kaldığında pil ne kadar sürer?</h3>
<p>GPS aktif olduğunda pil tüketimi artar. GPS olmadan 300+ kare, GPS açık halde bu sayı düşer.</p>
<h3>FT3 contaları kontrol edilmeli mi?</h3>
<p>Su altı kullanımından önce conta bütünlüğü mutlaka kontrol edilmeli. İkinci el örneklerde conta servisi yaptırılmış olması tercih edilmeli.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/lumix-dmc-ft3-waterproof" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Lumix DMC-FT3'ü İncele →</a></div>
"""},

# ── Sanyo Xacti CG100 EX ─────────────────────────────────────────────────────
{"title":"Sanyo Xacti CG100 EX İncelemesi: Dikey Gövde, Hibrit Çekim ve Y2K Özgünlüğü",
"handle":"sanyo-xacti-cg100-ex-inceleme-dikey-hibrit-y2k-ozgunluk",
"tags":"Sanyo, Sanyo Xacti CG100, Xacti serisi, hibrit kamera, retro kamera, dikey gövde kamera",
"meta_desc":"Sanyo Xacti CG100 EX incelemesi: Dikey gövde, 10MP CCD ve hibrit fotoğraf-video. Xacti serisinin en özgün modelini Y2K koleksiyon perspektifinden inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0048_ONN05075.jpg?v=1765238382",
"body":"""
<p>Xacti serisi, kameranın nasıl tutulması gerektiğine dair bütün kuralları yeniden yazdı. <strong>Sanyo Xacti CG100 EX</strong>, dikey gövdesiyle döneminin en özgün kameralarından biri ve bugün koleksiyonların dikkat çekici parçası.</p>

<h2>Sanyo Xacti CG100 EX Nedir?</h2>
<p>2009-2010 civarında üretilen CG100 EX, Sanyo'nun CG (Color Gradation) serisinin 10 megapiksellik modeli. Dikey (camcorder tarzı) gövde tasarımı, hem fotoğraf hem HD video çekimi ve Sanyo'nun karakteristik hibrit kamera felsefesiyle öne çıkıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 10 MP CCD</li>
<li><strong>Video:</strong> 720p HD (MPEG-4)</li>
<li><strong>Optik Zoom:</strong> 5x</li>
<li><strong>Ekran:</strong> 2.7" döner LCD</li>
<li><strong>Gövde:</strong> Dikey (camcorder grip)</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>Dikey Gövde Tasarımının Ergonomi Avantajı</h2>
<p>Video çekerken dikey tutuş çok daha doğal ve sabit. CG100 EX, işaret parmağı deklanşöre, baş parmak zoom kontrolüne otururken elde neredeyse hiç yorulma hissettirmiyor. Bu ergonomi, uzun video kayıtlarında belirgin avantaj.</p>

<h2>Döner LCD ile Vlogging'in 2009 Hali</h2>
<p>Döner ekran, kameranızın neyi çektiğini görerek selfie ve vlog çekim yapmanıza imkân tanıyor. 2009 yılında bu kameraya sahip olmak, bugünün vlogging kamerası ekosistemine 15 yıl önce katılmak demekti.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Sanyo Xacti serisi koleksiyoncuları</li>
<li>Dikey gövde tasarımı seven kamera meraklıları</li>
<li>Y2K hibrit kamera (fotoğraf + video) arayanlar</li>
<li>Ergonomik video çekimi için retro kamera isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>CG100 EX ile fotoğraf mı video mu daha iyi?</h3>
<p>Her ikisi de yeterli kalitede. Video için dikey gövde avantajı belirgin; fotoğraf kalitesi CCD sensör karakteriyle tatmin edici.</p>
<h3>Döner ekran ne kadar döner?</h3>
<p>LCD ekran yaklaşık 270 derece döner — selfie pozisyonu dahil her açıda kullanılabilir.</p>
<h3>SD kart boyutu önerisi?</h3>
<p>HD video için 8 GB veya daha büyük SDHC kart önerilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sanyo-xacti-cg100-ex" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sanyo Xacti CG100 EX'i İncele →</a></div>
"""},

# ── Sanyo Xacti VPC-HD1 ──────────────────────────────────────────────────────
{"title":"Sanyo Xacti VPC-HD1 İncelemesi: 2006'da HD Video Devrimini Getiren İlk Kompakt Kamera",
"handle":"sanyo-xacti-vpc-hd1-inceleme-2006-hd-video-devrim-kompakt",
"tags":"Sanyo, Sanyo Xacti VPC-HD1, HD video kamera, 2006 kamera, retro kamera, dijital video tarihi",
"meta_desc":"Sanyo Xacti VPC-HD1 incelemesi: 2006'da tüketicilere HD video sunan ilk kompakt kamera. Dijital video tarihinin önemli bir koleksiyon parçası.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0066_ONN05057.jpg?v=1765238616",
"body":"""
<p>2006 yılında, HD video profesyonellerin ayrıcalığıydı. Sanyo Xacti VPC-HD1 bunu değiştirdi — dünyanın ilk HD video kaydeden kompakt kameralarından biri olarak tarihe geçti.</p>

<h2>Sanyo Xacti VPC-HD1 Nedir?</h2>
<p>2006 çıkışlı VPC-HD1, 1.07 megapiksel CCD sensör ve 720p HD MPEG-4 video kaydıyla tüketici segmentinde HD video erişimini demokratikleştiren tarihi bir modeldir. Sanyo'nun dikey Xacti gövdesiyle birleşince döneminin en iddialı kompakt video kamerası haline geldi.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Video:</strong> 720p HD MPEG-4 (1280×720)</li>
<li><strong>Fotoğraf:</strong> 1.07 MP CCD</li>
<li><strong>Optik Zoom:</strong> 10x</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Gövde:</strong> Dikey Xacti tasarımı</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Üretim Yılı:</strong> 2006</li>
</ul>

<h2>Tüketiciye HD Video: 2006'daki Devrim</h2>
<p>2006'dan önce HD video için en az birkaç bin dolar harcamanız gerekiyordu. VPC-HD1, bu teknoloji çıtasını radikal biçimde indirdi. Youtube 2005'te kurulmuştu; HD video içeriği henüz nadir ve değerliydi. Bu kamera o dönemde öncü içerik üreticilerin silahıydı.</p>

<h2>Dijital Video Tarihinin Koleksiyon Parçası</h2>
<p>VPC-HD1, "tüketiciye sunulan ilk HD video kompaktları" kategorisinde özel bir yer tutmaktadır. Koleksiyon açısından teknik performans değil, tarihsel konum belirleyici. Dijital video tarihini yaşatmak isteyenler için bu model vazgeçilmez.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Dijital video tarihi koleksiyoncuları</li>
<li>Sanyo Xacti seri tamamcıları</li>
<li>İlk HD video kameralarından biri arayanlar</li>
<li>Teknoloji tarihi meraklıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>VPC-HD1'in HD videoları modern bilgisayarda oynatılır mı?</h3>
<p>Evet, MPEG-4 format olduğu için VLC, QuickTime ve diğer modern oynatıcılarda açılır.</p>
<h3>Fotoğraf kalitesi nasıl?</h3>
<p>1.07MP fotoğraf için tasarlanmamış — bu model video odaklı. Fotoğraf koleksiyon ve belgeleme amaçlı yeterli.</p>
<h3>Koleksiyon değeri artar mı?</h3>
<p>"İlk HD tüketici kamerası" kategorisi giderek değer kazanıyor. Çalışır durumda örnekler nadir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sanyo-xacti-vpc-hd1" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sanyo Xacti VPC-HD1'i İncele →</a></div>
"""},

# ── Sanyo Xacti VPC-E6EX ─────────────────────────────────────────────────────
{"title":"Sanyo Xacti VPC-E6EX İncelemesi: Giriş Seviyesi Xacti, Dikey Gövde ve CCD",
"handle":"sanyo-xacti-vpc-e6ex-inceleme-giris-xacti-dikey-ccd",
"tags":"Sanyo, Sanyo Xacti VPC-E6EX, Xacti E serisi, retro kamera, giriş seviyesi, dikey kamera",
"meta_desc":"Sanyo Xacti VPC-E6EX incelemesi: 6MP CCD ve Xacti'nin tanınan dikey gövde tasarımı. Xacti serisine giriş için ideal koleksiyon başlangıç noktası.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0057_ONN05066.jpg?v=1765238518",
"body":"""
<p>Xacti'nin dikey gövde felsefesini uygun bütçede deneyimlemek isteyenler için. <strong>Sanyo Xacti VPC-E6EX</strong>, serinin giriş modeli olarak koleksiyona ilk adım için doğru seçim.</p>

<h2>Sanyo Xacti VPC-E6EX Nedir?</h2>
<p>Sanyo Xacti'nin E serisinin 6 megapiksel modeli. Dikey gövde tasarımı, CCD sensör ve video çekim yeteneğiyle Xacti serisinin temel özelliklerini barındırıyor. E serisi, CG ve FH serilerine göre daha erişilebilir fiyat noktasında konumlanıyordu.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 6 MP CCD</li>
<li><strong>Gövde:</strong> Dikey Xacti tasarımı</li>
<li><strong>Zoom:</strong> Optik zoom</li>
<li><strong>Video:</strong> VGA / SD kalite</li>
<li><strong>Hafıza:</strong> SD kart</li>
</ul>

<h2>Xacti Serisine Giriş Noktası</h2>
<p>Xacti koleksiyonu genellikle HD ve FHD modeller üzerinden oluşturuluyor ama E serisi giriş modelleri seride tamamlayıcı bir yer tutuyor. Dikey gövde estetiğini ve Xacti marka kimliğini koleksiyona eklemek için E6EX pratik bir başlangıç.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Sanyo Xacti serisi tam koleksiyon oluşturanlar</li>
<li>Dikey gövde tasarımı bütçe dostu arayanlar</li>
<li>İlk Xacti deneyimi için giriş seviyesi model isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>E6EX ile HD video çekilir mi?</h3>
<p>Hayır, E serisi SD kalitede video kaydeder. HD için CG veya FH serisine yönelmek gerekiyor.</p>
<h3>Xacti E6EX pili nereden bulunur?</h3>
<p>Sanyo DB-L20 pil. Üçüncü parti alternatifleri mevcuttur.</p>
<h3>Dikey gövde fotoğraf çekim için kullanışlı mı?</h3>
<p>Başta alışık olmayabilirsiniz ama ergonomik yapısıyla kısa sürede alışılıyor. Video için belirgin avantaj; fotoğraf için daha çok tercih meselesi.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sanyo-xacti-vpc-e6ex" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sanyo Xacti VPC-E6EX'i İncele →</a></div>
"""},

# ── Sanyo Xacti CG20 ─────────────────────────────────────────────────────────
{"title":"Sanyo Xacti CG20 İncelemesi: Full HD Video ve 14MP ile Xacti Serisinin Olgunluğu",
"handle":"sanyo-xacti-cg20-inceleme-fullhd-14mp-xacti-olgunluk",
"tags":"Sanyo, Sanyo Xacti CG20, Full HD video, 14MP kamera, retro kamera, Xacti CG serisi",
"meta_desc":"Sanyo Xacti CG20 incelemesi: 14MP CCD ve Full HD 1080p video. Xacti serisinin olgunluk dönemindeki güçlü modelini ve koleksiyon değerini anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0135_ONN01312.jpg?v=1757178850",
"body":"""
<p>Xacti serisi olgunlaştıkça her nesilde hem daha yüksek megapiksel hem daha iyi video kalitesi geldi. <strong>Sanyo Xacti CG20</strong>, bu olgunluk döneminin en güçlü örneklerinden biri.</p>

<h2>Sanyo Xacti CG20 Nedir?</h2>
<p>CG20, Sanyo'nun CG serisinin 14 megapiksellik modeli. Full HD 1080p video kaydı ve 14MP CCD fotoğraf çözünürlüğüyle Xacti serisinin hibrit kamera felsefesini en yüksek kalitede sunuyor. Dikey gövde tasarımı korunmuş, özellik seti genişlemiş.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 14 MP CCD</li>
<li><strong>Video:</strong> Full HD 1080p</li>
<li><strong>Optik Zoom:</strong> 5x</li>
<li><strong>Ekran:</strong> 2.7" döner LCD</li>
<li><strong>Gövde:</strong> Dikey Xacti tasarımı</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>14MP + Full HD: Hibrit Kameranın Olgunluğu</h2>
<p>CG serisi, CG-10'un 10MP'sinden CG20'nin 14MP'sine çıkarken video da 720p'den 1080p'ye geçti. CG20, Sanyo'nun hibrit kamera konusunda ulaştığı en yüksek nokta — ve bu da Xacti koleksiyonunun amiral gemisi konumuna taşıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Sanyo Xacti CG serisi tamamcıları</li>
<li>Full HD video + 14MP fotoğraf hibrit kamera arayanlar</li>
<li>Xacti serisinin en güçlü modeli isteyen koleksiyoncular</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>CG20 ile CG10 arasındaki temel fark nedir?</h3>
<p>14MP vs 10MP çözünürlük ve Full HD vs 720p video. CG20 her açıdan üstün; koleksiyon değeri olarak da CG serisinin zirvesi.</p>
<h3>Full HD video için ne kadar SD kart gerekli?</h3>
<p>Full HD video hızlı kart doldurur. 16 GB veya daha büyük Class 10 SDHC kart önerilir.</p>
<h3>CG20 pili hangisi?</h3>
<p>Sanyo DB-L50 Li-ion pil. İkinci el platformlardan temin edilebilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sanyo-xacti-cg20" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sanyo Xacti CG20'yi İncele →</a></div>
"""},

# ── Kodak EasyShare M1063 ─────────────────────────────────────────────────────
{"title":"Kodak EasyShare M1063 İncelemesi: Kodak'ın Sade ve Güvenilir Y2K Kompaktı",
"handle":"kodak-easyshare-m1063-inceleme-sade-guvenilir-y2k-kompakt",
"tags":"Kodak, Kodak EasyShare M1063, Kodak EasyShare, retro kamera, y2k kamera, CCD kompakt",
"meta_desc":"Kodak EasyShare M1063 incelemesi: 10MP CCD ve Kodak'ın güvenilir kompakt tasarımı. EasyShare serisinin kalıcı modelini ve Y2K koleksiyondaki yerini anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a-1_0010_ONN06256.jpg?v=1765746382",
"body":"""
<p>Kodak'ın en uzun soluklu koleksiyonu EasyShare serisiydi. <strong>Kodak EasyShare M1063</strong>, bu serinin sade, güvenilir ve sıcak Kodak renk karakterini taşıyan başarılı modellerinden biri.</p>

<h2>Kodak EasyShare M1063 Nedir?</h2>
<p>2008-2009 civarında üretilen M1063, 10.0 megapiksel CCD sensör ve Kodak'ın Retinar asisli lens sistemiyle günlük kullanım için optimize edilmiş bir kompakt kameradır. EasyShare serisi, USB dock sistemiyle kolay aktarım için tasarlanmıştı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 10 MP CCD</li>
<li><strong>Optik Zoom:</strong> 3x (35–105mm)</li>
<li><strong>Ekran:</strong> 2.4" LCD</li>
<li><strong>ISO:</strong> 64–1600</li>
<li><strong>Video:</strong> 640×480 VGA</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Pil:</strong> KLIC-7001 Li-ion</li>
</ul>

<h2>Kodak'ın Renk Karakteri: Sıcak ve Canlı</h2>
<p>Kodak, film döneminde renk biliminde dünya standardını belirleyen markadı. Bu birikim dijital dönemde de görüntü işleme algoritmalarına yansıdı. EasyShare kameraların çektiği fotoğraflar, Kodak'ın geleneksel sıcak renk paletini dijital çağa taşıyor — canlı ama yapay olmayan renkler.</p>

<h2>EasyShare Dock Sistemi</h2>
<p>EasyShare serisi, USB dock aksesuarıyla bilgisayara tek dokunuşta bağlantı sunan orijinal bir ekosistem kurmuştu. Bu sistem, retro fotoğraf koleksiyonculuğu için nostaljik bir deneyim sunuyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Kodak EasyShare seri koleksiyoncuları</li>
<li>Kodak renk karakterini CCD'de arayanlar</li>
<li>Sade ve güvenilir giriş seviyesi retro kompakt isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Kodak EasyShare M1063 hangi pili kullanır?</h3>
<p>KLIC-7001 Li-ion pil. Bazı üçüncü parti alternatifleri mevcuttur.</p>
<h3>EasyShare dock olmadan kullanılır mı?</h3>
<p>Evet, USB kablosu veya SD kart okuyucu ile de veri aktarımı yapılabilir. Dock isteğe bağlı aksesuar.</p>
<h3>M1063 SD kart kullanır mı?</h3>
<p>Evet, SD ve SDHC kart uyumludur.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/kodak-easyshare-m1063" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kodak EasyShare M1063'ü İncele →</a></div>
"""},

# ── Kodak ZX1 ────────────────────────────────────────────────────────────────
{"title":"Kodak ZX1 İncelemesi: Hava Koşullarına Dayanıklı Pocket Video Kamera",
"handle":"kodak-zx1-inceleme-hava-dayanikli-pocket-video",
"tags":"Kodak, Kodak ZX1, dayanıklı kamera, hava geçirmez kamera, video kamera, outdoor kamera",
"meta_desc":"Kodak ZX1 incelemesi: Suya ve toza dayanıklı kompakt video kamera. Outdoor maceralar için cebe sığan Kodak video çözümünü detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/kodak6_1391386e-1642-42ee-96f1-4ed01f48cd13.jpg?v=1758551693",
"body":"""
<p>Küçük. Dayanıklı. Her yere gitmeye hazır. <strong>Kodak ZX1</strong>, outdoor maceralar için tasarlanmış, cebe sığan video odaklı bir Kodak.</p>

<h2>Kodak ZX1 Nedir?</h2>
<p>Kodak ZX1, "Weather-Resistant" etiketiyle piyasaya çıkmış, suya ve toza belirli ölçüde dayanıklı kompakt bir video kameradır. HD video kaydıyla outdoor aktiviteleri, spor ve günlük yaşamı belgelemek için tasarlanmış.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Dayanıklılık:</strong> Hava koşullarına dirençli (su ve toz)</li>
<li><strong>Video:</strong> HD (1280×720)</li>
<li><strong>Form:</strong> Cebe sığar kompakt</li>
<li><strong>Hafıza:</strong> microSD kart</li>
<li><strong>Batarya:</strong> AA pil</li>
</ul>

<h2>Neden Pocket Video Kamera?</h2>
<p>GoPro tarzı aksiyon kameraları geniş açı ve su altı için iyidir ama günlük vlog için bazen fazla iddialı ve pahalı. ZX1 gibi kompakt video kameralar, günlük outdoor aktiviteleri, piknikler, doğa yürüyüşleri için daha uygun ölçekli bir çözüm sunuyor.</p>

<h2>Kodak Renk Karakteri Videoda</h2>
<p>Kodak'ın geleneksel sıcak renk anlayışı video işlemesinde de kendini gösteriyor. Açık hava çekimlerinde doğal ve sıcak tonlar, Kodak markalı bir video kameradan beklenen görsel karakter.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Açık hava aktiviteleri için kompakt video kamera arayanlar</li>
<li>Kodak koleksiyonuna video kamera eklemek isteyenler</li>
<li>AA pilli dayanıklı video kamera tercih edenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>ZX1 suya tamamen dayanıklı mı?</h3>
<p>"Weather-Resistant" yağmur ve sis için koruma sağlar, su altı değil. Dalış veya yüzme için uygun değil.</p>
<h3>ZX1 videoları bilgisayara nasıl aktarılır?</h3>
<p>microSD kart okuyucu veya USB bağlantısıyla. Kodak Video kameralar standart video formatı kullandığından aktarım kolaydır.</p>
<h3>HD video için ne kadar microSD gerekli?</h3>
<p>8 GB microSD yeterli başlangıç noktası; 16 GB daha uzun çekimler için idealdir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/kodak-zx1-weather-resistant" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kodak ZX1'i İncele →</a></div>
"""},

# ── Kodak Slice R502 ─────────────────────────────────────────────────────────
{"title":"Kodak Slice R502 İncelemesi: Dokunmatik Ekran ve Şık Tasarımla Kodak'ın Premium Kompaktı",
"handle":"kodak-slice-r502-inceleme-dokunmatik-sik-premium-kompakt",
"tags":"Kodak, Kodak Slice R502, Kodak Slice serisi, dokunmatik kamera, premium kompakt, retro kamera",
"meta_desc":"Kodak Slice R502 incelemesi: 12MP, geniş dokunmatik ekran ve Slice'ın şık ince tasarımı. Kodak'ın premium kompakt serisini ve koleksiyon değerini inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/kodak_slice.jpg?v=1772495717",
"body":"""
<p>Kodak, Slice serisiyle kompakt kameranın nasıl görünmesi gerektiğine dair kendi cevabını verdi. <strong>Kodak Slice R502</strong>, dokunmatik ekranı ve ince gövdesiyle döneminin en şık Kodak kompaktlarından biri.</p>

<h2>Kodak Slice R502 Nedir?</h2>
<p>Slice serisi, Kodak'ın premium kompakt kategorisindeki en iddialı girişimiydi. R502, 12 megapiksel sensör ve geniş dokunmatik ekranıyla hem Kodak renk karakterini hem modern arayüzü bir arada sunuyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12 MP</li>
<li><strong>Ekran:</strong> Geniş dokunmatik LCD</li>
<li><strong>Tasarım:</strong> İnce Slice gövdesi</li>
<li><strong>Optik Zoom:</strong> 5x</li>
<li><strong>Hafıza:</strong> SD kart</li>
</ul>

<h2>Slice Tasarımı: Kodak'ın Premium Cevabı</h2>
<p>Slice serisi, Kodak'ın Sony T serisi ve Canon IXUS'a premium kompakt segmentindeki yanıtıydı. Geniş dokunmatik ekran, ince gövde ve şık çizgiler — bu özellikler Slice'ı standart EasyShare modellerinden belirgin biçimde ayırıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Kodak Slice serisi koleksiyoncuları</li>
<li>Premium Kodak kompaktının özelliklerini arayanlar</li>
<li>Dokunmatik ekranlı şık Kodak kamera isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Kodak Slice R502 hangi serinin ürünü?</h3>
<p>Slice serisi, Kodak'ın premium kompakt aralığı. EasyShare serisinden tasarım ve özellikler açısından belirgin biçimde ayrılıyor.</p>
<h3>Dokunmatik ekran hassas mi?</h3>
<p>Rezistif dokunmatik teknoloji; günümüz kapasitif ekranlardan farklı ama işlevsel.</p>
<h3>R502 SD kart kullanır mı?</h3>
<p>Evet, SD kart uyumludur.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/kodak-slice-r502" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kodak Slice R502'yi İncele →</a></div>
"""},

# ── Kodak EasyShare Z950 ─────────────────────────────────────────────────────
{"title":"Kodak EasyShare Z950 İncelemesi: 10x Zoom, Seyahat Kompaktı ve Kodak Renk Sıcaklığı",
"handle":"kodak-easyshare-z950-inceleme-10x-zoom-seyahat-kodak-renk",
"tags":"Kodak, Kodak EasyShare Z950, Kodak Z serisi, süper zoom kamera, seyahat kamerası, retro kamera",
"meta_desc":"Kodak EasyShare Z950 incelemesi: 12MP CCD, 10x optik zoom ve Kodak'ın sıcak renk karakteri. Seyahat fotoğrafçılığı için Kodak'ın süper zoom kompaktı.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0019_ONN00330.jpg?v=1774655348",
"body":"""
<p>Kodak'ın Z serisi, EasyShare ailesinin uzun zoom modelleriyle seyahat fotoğrafçılığına yönelik çözüm sunuyordu. <strong>Kodak EasyShare Z950</strong>, bu serinin en yetenekli örneklerinden biri.</p>

<h2>Kodak EasyShare Z950 Nedir?</h2>
<p>Z950, 12 megapiksel CCD sensör ve 10x optik zoom (35–350mm) ile seyahat ve outdoor fotoğrafçılığı için tasarlanmış bir Kodak kompakttır. Kodak'ın karakteristik renk işlemesi ve güvenilir mühendisliğiyle uzun zoom kategorisinde güçlü bir seçenek.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12 MP CCD</li>
<li><strong>Optik Zoom:</strong> 10x (35–350mm)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Stabilizasyon:</strong> Dijital</li>
<li><strong>ISO:</strong> 64–1600</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>Kodak Renk Karakteri ile 10x Zoom</h2>
<p>Z950'nin en güçlü yönü, Kodak'ın sıcak ve canlı renk işlemesini 10x zoom kapasiteyle birleştirmesidir. Seyahat sahnelerinde — pazar yerleri, manzaralar, yerel yaşam detayları — bu kombinasyon belirgin bir avantaj sağlıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğrafçılığı için Kodak süper zoom arayanlar</li>
<li>Kodak Z serisi koleksiyoncuları</li>
<li>10x zoom + CCD kalitesi kombinasyonu isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Z950 pili hangisi?</h3>
<p>KLIC-7004 Li-ion pil. Bazı Kodak modellerle ortak; üçüncü parti alternatifleri mevcut.</p>
<h3>10x zoom ile görüntü titremesi olur mu?</h3>
<p>Dijital stabilizasyon mevcut, optik değil. Yüksek zoomda sabit yüzey önerilir.</p>
<h3>Z950 SD kart kullanır mı?</h3>
<p>Evet, SD ve SDHC kart uyumludur.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/kodak-easyshare-z950" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kodak EasyShare Z950'yi İncele →</a></div>
"""},

# ── Kodak Pixpro FZ55 ────────────────────────────────────────────────────────
{"title":"Kodak Pixpro FZ55 İncelemesi: 2024'ün En Uygun Fiyatlı Yeni Kompakt Kamerası",
"handle":"kodak-pixpro-fz55-inceleme-uygun-fiyatli-yeni-kompakt",
"tags":"Kodak, Kodak Pixpro FZ55, Kodak Pixpro, yeni kompakt kamera, 5x zoom, günlük kamera",
"meta_desc":"Kodak Pixpro FZ55 incelemesi: 16MP, 5x optik zoom ve Kodak Pixpro serisinin güvenilir kalitesi. Piyasadaki en uygun fiyatlı yeni kompakt kamerayı inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/fz55s2.jpg?v=1750201577",
"body":"""
<p>Akıllı telefon çağında kompakt kamera almak hâlâ mantıklı mı? <strong>Kodak Pixpro FZ55</strong>, bu soruya "evet" diyenler için tasarlanmış, uygun fiyatlı ve modern bir kompakt.</p>

<h2>Kodak Pixpro FZ55 Nedir?</h2>
<p>Günümüzde üretilen Kodak Pixpro FZ55, 16 megapiksel sensör ve 5x optik zoom ile temel kompakt kamera ihtiyaçlarını karşılayan modern bir modeldir. Sade arayüzü, kompakt boyutu ve uygun fiyatıyla hediye veya başlangıç kamerası olarak öne çıkıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 16 MP</li>
<li><strong>Optik Zoom:</strong> 5x (28–140mm)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>Video:</strong> Full HD 1080p</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
<li><strong>Yüz Tanıma:</strong> Var</li>
<li><strong>Pil:</strong> Li-ion (şarj edilebilir)</li>
</ul>

<h2>Neden 2024'te Kompakt Kamera?</h2>
<p>Telefon kamerasından vazgeçmeyin ama kompakt kameranın sunduğu optik zoom, fiziksel butonlar ve özel fotoğraf modu deneyimini de yaşayın. Çocuklara veya yaşlı aile fertlerine hediye için, seyahat için veya "kameraya özel çekim" hissini arayan herkes için FZ55 ideal başlangıç noktası.</p>

<h2>Yeni Üretim: Garanti Avantajı</h2>
<p>İkinci el retro kameraların aksine FZ55, günümüzde üretilen ve satış garantisi sunan bir model. Aksesuar bulunması kolay, servisi mümkün.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>İlk kompakt kamerasını almak isteyenler</li>
<li>Çocuklara kamera hediye etmek isteyenler</li>
<li>Uygun fiyatlı, modern ve sade kompakt arayanlar</li>
<li>Retro koleksiyonun yanına "kullanım için" modern bir kamera isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>FZ55 telefon kamerasından iyi mi?</h3>
<p>Genel fotograf kalitesinde telefon üstün olabilir; ama 5x optik zoom, fiziksel deklanşör ve bağımsız kamera deneyimi telefonda yok. Farklı kullanım senaryoları için tamamlayıcı.</p>
<h3>Kodak Pixpro FZ55 fiyatı nedir?</h3>
<p>Retrocameraland'deki güncel fiyat için ürün sayfasını inceleyebilirsiniz.</p>
<h3>Garanti koşulları nedir?</h3>
<p>Retrocameraland'den satın alınan FZ55, satış garantisiyle sunulmaktadır. Detaylar için ürün sayfası ve mağaza koşulları geçerlidir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/kodak-pixpro-fz55-dijital-fotograf-makinesi-siyah" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kodak Pixpro FZ55'i İncele →</a></div>
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
    log("\n=== BATCH 4 SONUÇ ===")
    ok = sum(1 for r in results if r["status"]=="ok")
    for r in results:
        log(f"  {'✅' if r['status']=='ok' else '❌'} {r['title'][:55]}")
    log(f"\n{ok}/{len(POSTS)} yayınlandı.")

if __name__ == "__main__":
    run()
