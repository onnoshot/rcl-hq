#!/usr/bin/env python3
"""Batch 1: Sony (7) + Canon (6) = 13 ürün"""
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

# ── Sony Cyber-shot DSC-T70 ──────────────────────────────────────────────────
{"title":"Sony Cyber-shot DSC-T70 İncelemesi: Slider Tasarım ve Carl Zeiss Lens ile Zamansız Şıklık",
"handle":"sony-cyber-shot-dsc-t70-inceleme-slider-carl-zeiss",
"tags":"Sony, Sony Cyber-shot DSC-T70, Sony T serisi, retro kamera, y2k kamera, CCD kamera",
"meta_desc":"Sony Cyber-shot DSC-T70 incelemesi: 8MP CCD, Carl Zeiss lens ve slider kapak. Sony T serisinin ikonik modeli hakkında bilmeniz gereken her şey.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0138_ONN04985.jpg?v=1765239724",
"body":"""
<p>Sony'nin T serisi, kompakt kamera tasarımının en cesur yorumlarından biriydi. <strong>Sony Cyber-shot DSC-T70</strong>, slider mekanizmalı kapağı, ince alüminyum gövdesi ve Carl Zeiss lensiyle bugün koleksiyoncuların gözdesi olmaya devam ediyor.</p>

<h2>Sony Cyber-shot DSC-T70 Nedir?</h2>
<p>2008 yılında çıkan T70, Sony'nin ikonik T serisinin orta segment modeli. 8.1 megapiksel CCD sensör, Carl Zeiss Vario-Tessar lens ve 3 inç dokunmatik ekranla döneminin en kapsamlı özellik setini sunuyordu. Slider kapak mekanizması; lensi korurken kamerayı açma ritüelini de eşsiz kılıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 8.1 MP CCD</li>
<li><strong>Lens:</strong> Carl Zeiss Vario-Tessar 3x optik zoom (35–105mm)</li>
<li><strong>Ekran:</strong> 3.0" dokunmatik LCD</li>
<li><strong>Stabilizasyon:</strong> SteadyShot optik</li>
<li><strong>Yüz Tanıma:</strong> Var (8 yüze kadar)</li>
<li><strong>Hafıza:</strong> Memory Stick Pro Duo + SD</li>
<li><strong>Tasarım:</strong> Slider mekanizmalı metal gövde</li>
</ul>

<h2>Carl Zeiss Optik: Farkı Nedir?</h2>
<p>Carl Zeiss lensleri, renk geçişlerini ve kontrastı rakip kompakt kameralara kıyasla belirgin biçimde daha doğru işler. T70'de bu fark özellikle açık havada, gölge-ışık geçişlerinde ve cilt tonlarında kendini gösteriyor. Dijital filtre değil, gerçek optik kalite.</p>

<h2>Y2K Koleksiyonunda T70'in Yeri</h2>
<p>T serisinin her modeli bugün koleksiyon değeri taşıyor. T70, orta segment olmasına rağmen optik kalitesiyle üst segment rakiplerini zorluyor. Siyah alüminyum gövdesi, rafta ya da çantada her zaman prestijli duruyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Sony T serisi koleksiyonu tamamlamak isteyenler</li>
<li>Carl Zeiss lens kalitesini retro formatta arayanlar</li>
<li>Slider tasarımlı, dokunmatik ekranlı Y2K kamera meraklıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Sony DSC-T70 hangi pili kullanır?</h3>
<p>NP-BD1 / NP-FD1 Li-ion pil. Hâlâ temin edilebilir ve uyumlu alternatifleri mevcut.</p>
<h3>T70 ile gece çekimi nasıl?</h3>
<p>ISO 1600'de CCD'ye özgü sıcak gren belirginleşir; retro estetik için bu bir avantaj sayılır.</p>
<h3>DSC-T70 Memory Stick mi SD kart mı?</h3>
<p>Her ikisini de destekler. SD kart günümüzde çok daha pratik ve kolayca bulunabilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cyber-shot-dsc-t70" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-T70'i İncele →</a></div>
"""},

# ── Sony Cyber-shot DSC-TX9 ──────────────────────────────────────────────────
{"title":"Sony Cyber-shot DSC-TX9 İncelemesi: 3D Fotoğraf ve Full HD Video Destekli Retro Kompakt",
"handle":"sony-cyber-shot-dsc-tx9-inceleme-3d-fullhd-retro",
"tags":"Sony, Sony Cyber-shot DSC-TX9, Sony TX serisi, retro kamera, y2k kamera, Full HD kamera",
"meta_desc":"Sony Cyber-shot DSC-TX9 incelemesi: 12MP Exmor CMOS, Full HD 1080p video ve 3D fotoğraf özelliği. Sony TX serisinin en yetenekli modeli.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0189_ONN04934.jpg?v=1765241927",
"body":"""
<p>2010 yılında 3D televizyonlar yaygınlaşmaya başlarken Sony, kompakt kamerasına 3D fotoğraf özelliği ekledi. <strong>Sony Cyber-shot DSC-TX9</strong>, hem Full HD video hem 3D içerik hem de ince T serisi tasarımıyla döneminin en iddialı modellerinden biri.</p>

<h2>Sony Cyber-shot DSC-TX9 Nedir?</h2>
<p>2010 çıkışlı TX9, Sony'nin T/TX serisinin CMOS sensöre geçişini simgeleyen modeldir. 12.2 MP Exmor R CMOS sensör, 1080/60i Full HD video kaydı ve Sweep Panorama özelliğiyle öne çıkar. Slider kapak tasarımı T serisinin DNA'sını korur.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.2 MP Exmor R CMOS (backlit)</li>
<li><strong>Lens:</strong> Carl Zeiss Vario-Tessar 4x optik zoom (25–100mm)</li>
<li><strong>Video:</strong> Full HD 1080/60i AVCHD</li>
<li><strong>Ekran:</strong> 3.5" dokunmatik OLED</li>
<li><strong>3D Fotoğraf:</strong> 3D Sweep Panorama</li>
<li><strong>Stabilizasyon:</strong> SteadyShot optik</li>
<li><strong>Hafıza:</strong> Memory Stick Micro + microSD</li>
</ul>

<h2>Exmor R CMOS ve Backlit Sensör Avantajı</h2>
<p>TX9, T serisi içinde CCD'den CMOS'a geçişin önemli bir noktasında duruyor. Backlit (BSI) Exmor R sensör, düşük ışıkta CCD'ye göre çok daha az gürültü üretiyor. Bu, gece ve iç mekân çekimlerinde TX9'u serisinin diğer modellerinden belirgin şekilde üstün kılıyor.</p>

<h2>3.5 İnç OLED Ekran</h2>
<p>Kompakt kamerada OLED ekran kullanımı, 2010 için son derece nadirdi. OLED'in doğal kontrastı ve siyah derinliği, kadraj kurarken ve fotoğraf incelemelerinde gerçek bir avantaj sağlıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Full HD video destekli retro kompakt arayanlar</li>
<li>Sony TX/T serisi koleksiyoncuları</li>
<li>OLED ekranlı kamera meraklıları</li>
<li>Backlit CMOS sensör tercih eden düşük ışık fotoğrafçıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>TX9 ile 3D fotoğraf nasıl çalışır?</h3>
<p>Sweep Panorama modunda kamerayı yavaşça kaydırırsınız; TX9 tek lens ile iki perspektif yakalayarak 3D MPO formatında görüntü oluşturur. 3D TV veya uyumlu ekranda izlenebilir.</p>
<h3>Sony DSC-TX9 pili nereden bulunur?</h3>
<p>NP-BN1 pil kullanır. Bu model Sony'nin geniş uyumlu pili olduğundan orijinal ve üçüncü parti alternatifleri kolayca bulunur.</p>
<h3>TX9 AVCHD video kaydeder mi?</h3>
<p>Evet, 1080/60i AVCHD formatında video kaydeder. Bu format Adobe Premiere ve Final Cut Pro dahil tüm profesyonel video editörlerinde açılır.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cyber-shot-dsc-tx9" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-TX9'u İncele →</a></div>
"""},

# ── Sony Cybershot DSC-S600 ──────────────────────────────────────────────────
{"title":"Sony Cybershot DSC-S600 İncelemesi: Klasik Tasarım, CCD Güvenilirliği ve Retro Çekicilik",
"handle":"sony-cybershot-dsc-s600-inceleme-klasik-tasarim-ccd",
"tags":"Sony, Sony Cybershot DSC-S600, Sony S serisi, retro kamera, y2k kamera, CCD kamera",
"meta_desc":"Sony Cybershot DSC-S600 incelemesi: 6MP CCD, 3x optik zoom ve klasik Sony tasarımı. Y2K döneminin güvenilir point-and-shoot kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0082_ONN05041.jpg?v=1765238886",
"body":"""
<p>Her kameranın bir ruhu vardır. <strong>Sony Cybershot DSC-S600</strong>'ün ruhu güvenilirlik. 2006 yılından bu yana çalışmaya devam eden binlerce örneğiyle, bu kamera Sony'nin "her koşulda çalışır" felsefesininin somut kanıtı.</p>

<h2>Sony Cybershot DSC-S600 Nedir?</h2>
<p>2006 çıkışlı DSC-S600, Sony'nin S serisinin orta segment modeli. 6.0 megapiksel CCD sensör, 3x optik zoom (38–114mm) ve AA pil kullanımıyla günlük fotoğrafçılık için tasarlanmış, sade ve güvenilir bir kompakt kamera.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 6.0 MP CCD</li>
<li><strong>Lens:</strong> Sony 3x optik zoom (38–114mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Pil:</strong> AA × 2 adet (her yerde bulunur!)</li>
<li><strong>Hafıza:</strong> Memory Stick Duo + 32MB dahili</li>
<li><strong>Flaş:</strong> Dahili otomatik</li>
<li><strong>Video:</strong> 640×480 VGA</li>
</ul>

<h2>AA Pil: Seyahatin Gizli Kahramanı</h2>
<p>DSC-S600, özel lityum pil değil standart AA pil kullanır. Dünyanın herhangi bir köyünde, herhangi bir markette AA pil bulunur. Uzun seyahatlerde, hafta sonu kamp gezilerinde ya da şehir dışı maceralarında pil sorunu yaşamazsınız.</p>

<h2>6MP CCD ile Retro Fotoğraf Karakteri</h2>
<p>S600'ün 6MP CCD sensörü, modern kameraların kliniğinden uzak, sıcak ve filmsi bir renk karakteri sunuyor. Cilt tonları yumuşak, gökyüzü doğal, gölgeler detaylı. Bu "kusurlu mükemmellik" bugün sosyal medyada en çok aranan estetik.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>AA pil avantajı isteyenler (seyahat, kamp)</li>
<li>Sony S serisi koleksiyoncuları</li>
<li>Sade arayüzlü, düşünmeden çeken kamera arayanlar</li>
<li>Retro CCD tonu için bütçe dostu seçenek arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Sony DSC-S600 kaç MP?</h3>
<p>6.0 megapiksel CCD sensör. Sosyal medya paylaşımı ve A4 baskı için fazlasıyla yeterli çözünürlük.</p>
<h3>Memory Stick Duo kart nereden bulunur?</h3>
<p>Memory Stick Duo kartlar ikinci el platformlarda ve bazı elektronik marketlerde hâlâ satılmaktadır. SD adaptörle de kullanılabilir.</p>
<h3>S600 gece fotoğrafı nasıl?</h3>
<p>Gece Sahne modunda, sabit bir yüzeyle iyi sonuçlar verir. Flaş olmadan, düşük ışıkta CCD greni belirginleşir — bu retro look için bir özellik sayılır.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cybershot-dsc-s600" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-S600'ü İncele →</a></div>
"""},

# ── Sony Cyber-shot DSC-W110 ─────────────────────────────────────────────────
{"title":"Sony Cyber-shot DSC-W110 İncelemesi: Kompakt W Serisi, CCD Kalitesi ve Günlük Kullanım Kolaylığı",
"handle":"sony-cyber-shot-dsc-w110-inceleme-kompakt-w-serisi-ccd",
"tags":"Sony, Sony Cyber-shot DSC-W110, Sony W serisi, retro kamera, y2k kamera, CCD kompakt",
"meta_desc":"Sony Cyber-shot DSC-W110 incelemesi: 7.2MP CCD, 3x optik zoom ve sade kompakt tasarım. Sony'nin en kullanışlı günlük kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0129_ONN04994.jpg?v=1765239564",
"body":"""
<p>Sony'nin W serisi, "kamera kullanmayı bilmiyorum" diyenlerin bile mükemmel fotoğraf çektiği modellerdi. <strong>Sony Cyber-shot DSC-W110</strong>, bu serinin en başarılı denge noktalarından biri — yeterince küçük, yeterince yetenekli, yeterince Sony.</p>

<h2>Sony Cyber-shot DSC-W110 Nedir?</h2>
<p>2008 çıkışlı DSC-W110, 7.2 megapiksel CCD sensörlü, ince alüminyum gövdeli kompakt bir kameradır. Sony'nin Smart Zoom teknolojisi ve Scene Selection modlarıyla her ortamda iyi sonuç verecek şekilde optimize edilmiş.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 7.2 MP CCD (1/2.5")</li>
<li><strong>Lens:</strong> Carl Zeiss Vario-Tessar 3x zoom (35–105mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>ISO:</strong> 80–3200</li>
<li><strong>Yüz Tanıma:</strong> Var</li>
<li><strong>Hafıza:</strong> Memory Stick Duo Pro</li>
<li><strong>Pil Ömrü:</strong> ~220 kare</li>
</ul>

<h2>Carl Zeiss Vario-Tessar W110'da Ne Anlama Geliyor?</h2>
<p>Sony, W110 gibi orta segment modellere bile Zeiss optik standardını uyguladı. Bu lens renk saflığı ve kontrast açısından benzer fiyatlı rakip kompaktların önünde. Özellikle parlak gün ışığında ve portre çekimlerinde fark belirgin.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>İlk retro kompakta başlamak isteyenler</li>
<li>Sony W serisi koleksiyoncuları</li>
<li>Günlük sosyal medya çekimi için CCD tonu arayanlar</li>
<li>Zeiss lens kalitesini uygun bütçede isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Sony DSC-W110 fiyatı ne kadar olmalıydı?</h3>
<p>2008'de yaklaşık 200 USD civarında satışa çıktı. Bugün ikinci el pazarında çok daha erişilebilir fiyatlarda bulunuyor.</p>
<h3>W110 SD kart kullanır mı?</h3>
<p>Memory Stick Duo Pro kullanır; SD kart adaptörle takılabilir ancak doğal yuvası Memory Stick içindir.</p>
<h3>W110 ile makro çekim yapılabilir mi?</h3>
<p>Evet, Makro modu 8 cm mesafeden netlik sağlar. CCD sensörün renk işlemesiyle yakın plan çekimler etkileyici sonuçlar verir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cyber-shot-dsc-w110" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-W110'u İncele →</a></div>
"""},

# ── Sony Cybershot DSC-S85 ───────────────────────────────────────────────────
{"title":"Sony Cybershot DSC-S85 İncelemesi: 2002'nin Retro Efsanesi, CCD ve Manuel Kontrol",
"handle":"sony-cybershot-dsc-s85-inceleme-2002-retro-efsane-manuel",
"tags":"Sony, Sony Cybershot DSC-S85, erken dönem dijital kamera, retro kamera, y2k kamera, manuel kamera",
"meta_desc":"Sony Cybershot DSC-S85 incelemesi: 4MP CCD, manuel odak ve 2002 yılı mühendisliği. Y2K döneminin en değerli koleksiyon kameralarından birini inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0024_ONN05099.jpg?v=1765238094",
"body":"""
<p>2002 yılında 4 megapiksel, bir kamerada premium sayılırdı. <strong>Sony Cybershot DSC-S85</strong>, o dönemin en yetenekli tüketici modellerinden biriydi — ve bugün erken dönem dijital fotoğrafın kapsülü olarak koleksiyoncular arasında özel bir yer tutuyor.</p>

<h2>Sony Cybershot DSC-S85 Nedir?</h2>
<p>2001-2002 yıllarında üretilen DSC-S85, 4.1 megapiksel CCD sensör, döner gövde tasarımı ve geniş manuel kontrol seçenekleriyle döneminin prosümer seviyesindeydi. Carl Zeiss Vario-Sonnar lens ve Sony'nin özel "Memory Stick" formatıyla dijital fotoğraf tarihinin önemli bir sayfasını temsil ediyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 4.1 MP CCD (1/1.8" — büyük sensör!)</li>
<li><strong>Lens:</strong> Carl Zeiss Vario-Sonnar 3x zoom (34–102mm)</li>
<li><strong>Gövde:</strong> Döner tasarım (ekran ve lens bağımsız döner)</li>
<li><strong>Ekran:</strong> 1.8" renkli LCD</li>
<li><strong>ISO:</strong> 100–400</li>
<li><strong>Pil:</strong> InfoLITHIUM NP-FM50</li>
<li><strong>Hafıza:</strong> Memory Stick</li>
</ul>

<h2>1/1.8" Büyük Sensör: 2002'de Neden Önemliydi?</h2>
<p>DSC-S85'in 1/1.8" CCD sensörü, bugünkü kompakt kameraların büyük çoğunluğundan fiziksel olarak daha büyük. Büyük sensör = daha fazla ışık = daha iyi görüntü kalitesi. Bu boyut, S85'i döneminde prosümer seviyesine taşıyan ana faktördü.</p>

<h2>Erken Dönem Dijital Koleksiyonunun Köşe Taşı</h2>
<p>DSC-S85, "ilk iyi dijital kameralar" döneminin temsilcisi. Bu modeli koleksiyonuna eklemek, 2000'lerin başı dijital fotoğraf tarihini elinizin altında tutmak demek. Döner gövde tasarımı ve manuel kontroller, bugünkü kompaktların büyük çoğunluğunda bulunmuyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Erken dönem dijital kamera tarihi koleksiyoncuları</li>
<li>Büyük CCD sensörlü retro kamera arayanlar</li>
<li>Manuel kontrollü, prosümer seviye vintage kompakt isteyenler</li>
<li>Sony Cybershot seri tarihi meraklıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Sony DSC-S85 hâlâ kullanılabilir mi?</h3>
<p>Evet. Çalışır durumdaki örnekler bugün de fotoğraf çekebilir. Memory Stick kart ve uyumlu pil temin edebilirseniz tam işlevsel.</p>
<h3>DSC-S85'in döner gövdesi ne işe yarar?</h3>
<p>Ekran ve gövde ayrı ayrı döner; bu sayede selfie, yüksek açı ve alçak açı çekimlerde vizörü kullanmadan kadraj kurulabilir.</p>
<h3>S85 pili nereden bulunur?</h3>
<p>NP-FM50 pil modeli. Eski Sony model olmasına rağmen hâlâ üçüncü parti alternatifleri üretilmekte.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cybershot-dsc-s85" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-S85'i İncele →</a></div>
"""},

# ── Sony Cybershot DSC-W200 ──────────────────────────────────────────────────
{"title":"Sony Cybershot DSC-W200 İncelemesi: 12MP CCD, Geniş Lens ve Premium Kompakt Deneyimi",
"handle":"sony-cybershot-dsc-w200-inceleme-12mp-ccd-genis-lens",
"tags":"Sony, Sony Cybershot DSC-W200, Sony W serisi, retro kamera, 12MP CCD, kompakt kamera inceleme",
"meta_desc":"Sony Cybershot DSC-W200 incelemesi: 12MP CCD sensör, 3x Carl Zeiss zoom ve şık alüminyum gövde. W serisinin zirvesindeki modeli detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/sonycybershot.jpg?v=1759849244",
"body":"""
<p>W serisi içinde 12 megapiksele ulaşmak, 2008 için küçük bir başarı değildi. <strong>Sony Cybershot DSC-W200</strong>, serisinin o dönemki zirve modeli — ve bugün 12MP CCD'nin sunduğu görüntü karakteriyle ayrı bir yerde duruyor.</p>

<h2>Sony Cybershot DSC-W200 Nedir?</h2>
<p>2008 yılında çıkan DSC-W200, Sony W serisinin o dönemki amiral gemisi. 12.1 megapiksel CCD sensör, Carl Zeiss Vario-Tessar lens ve ince alüminyum gövdesiyle kompakt kamera sınıfının üst basamağındaydı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD (1/2.3")</li>
<li><strong>Lens:</strong> Carl Zeiss Vario-Tessar 3x (35–105mm)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>ISO:</strong> 80–3200</li>
<li><strong>Yüz Tanıma:</strong> Var (8 yüze kadar)</li>
<li><strong>Stabilizasyon:</strong> SteadyShot optik</li>
<li><strong>Gövde:</strong> Alüminyum, ince profil</li>
</ul>

<h2>12MP CCD: Retro Görüntünün Doruğu</h2>
<p>CCD sensörlerin piksel sayısı arttıkça her piksel biraz küçülür ve gürültü artar — bu W200'de de geçerli. Ancak bu "gürültü" retro fotoğrafçılar için tam da istedikleri filmsi gren. Aynı zamanda 12MP çözünürlük, büyük baskı ve detaylı kırpma işlemleri için güçlü bir temel sunuyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Yüksek çözünürlüklü CCD retro kamera arayanlar</li>
<li>Sony W serisi koleksiyonu tamamlamak isteyenler</li>
<li>Büyük boy baskı için retro dijital kamera arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>W200 hangi formatlarda fotoğraf kaydeder?</h3>
<p>JPEG formatında kaydeder. RAW desteklemez — bu dönem Sony kompakt kameralarının genel özelliği.</p>
<h3>Sony DSC-W200 ile panorama çekilir mi?</h3>
<p>Hayır, panorama özelliği sonraki modellerde geldi. W200'de standart çekim modları mevcut.</p>
<h3>W200 için SD kart mi Memory Stick mi?</h3>
<p>Memory Stick Pro Duo kullanır. Adapatörle microSD de çalıştırılabilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-cybershot-dsc-w200" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony DSC-W200'ü İncele →</a></div>
"""},

# ── Sony VLOG Camcorder ──────────────────────────────────────────────────────
{"title":"Sony VLOG Kamera İncelemesi: Hafif, Kompakt ve Her Anı Kaydetmeye Hazır",
"handle":"sony-vlog-kamera-inceleme-hafif-kompakt-kayit",
"tags":"Sony, Sony VLOG kamera, vlog kamera, retro kamera, kompakt video kamera, günlük vlog",
"meta_desc":"Sony VLOG kamerası incelemesi: Hafif gövde, kullanışlı video özellikleri ve retrocameraland garantisiyle günlük vlog çekimleri için ideal kompakt kamera.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0015_ONN01435.jpg?v=1757178676",
"body":"""
<p>Her anı kaydetmek için profesyonel ekipman gerekmez. Bir vlog kamera yeterli — hafif, kompakt, her an hazır. <strong>Sony VLOG Camcorder</strong>, günlük hayatı, seyahati ve özel anları kayıt altına almak için pratik bir çözüm sunuyor.</p>

<h2>Sony VLOG Kamera Nedir?</h2>
<p>Bu kompakt Sony video kamerası, günlük vlog çekimleri için optimize edilmiş hafif bir camcorder. Küçük gövdesi ve pratik kontrolleriyle çanta veya cebe sığar, her an hızlıca çekime başlayabilirsiniz.</p>

<h2>Özellikler</h2>
<ul>
<li><strong>Form Faktörü:</strong> Ultra kompakt camcorder</li>
<li><strong>Kullanım:</strong> Günlük vlog, seyahat, anı kaydı</li>
<li><strong>Bağlantı:</strong> USB ile bilgisayara aktarım</li>
<li><strong>Gövde:</strong> Hafif plastik, tek el kullanımına uygun</li>
</ul>

<h2>Vlog Çekimlerinde Kompakt Kameranın Avantajı</h2>
<p>Büyük kameralar dikkat çeker, insanları rahatsız eder. Küçük ve gösterişsiz bir kamera ise doğal anları yakalamanıza izin verir. Bu Sony camcorder, sahneyi bozmadan anı kayıt altına almanın en pratik yolu.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Günlük hayatını video ile belgelemek isteyenler</li>
<li>Seyahat vlogleri için hafif kamera arayanlar</li>
<li>İlk kamerasını arayan başlangıç seviyesi kullanıcılar</li>
<li>Ailesinin anılarını kaydetmek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Bu kamera sosyal medya videoları için uygun mu?</h3>
<p>Günlük vlog ve anı kayıtları için evet. Profesyonel prodüksiyon kalitesi beklemeden, samimi ve spontane içerikler için ideal.</p>
<h3>Kayıtlar nerede saklanır?</h3>
<p>Dahili hafızaya veya harici kart desteğiyle SD karta kaydedilir.</p>
<h3>Pil ne kadar süre dayanır?</h3>
<p>Normal kullanımda birkaç saatlik çekim imkânı sunar. Uzun çekimler için şarjlı yedek pil bulundurmak önerilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/sony-x200-camcoder" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Sony VLOG Kamerayı İncele →</a></div>
"""},

# ── Canon PowerShot V1 ───────────────────────────────────────────────────────
{"title":"Canon PowerShot V1 İncelemesi: 2024'ün En Yetenekli Kompakt Kamerası Türkiye'de",
"handle":"canon-powershot-v1-inceleme-2024-en-yetenekli-kompakt",
"tags":"Canon, Canon PowerShot V1, modern kompakt kamera, 1 inç sensör, 4K video, ND filtre",
"meta_desc":"Canon PowerShot V1 incelemesi: 1 inç sensör, dahili ND filtre ve 4K video. 2024'ün en çok konuşulan kompakt kamerasını detaylıca inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/powershot_v1_0013_Layer1.jpg?v=1758420998",
"body":"""
<p>Canon onlarca yıl sonra kompakt kamera kategorisine ciddi bir ürünle geri döndü. <strong>Canon PowerShot V1</strong>, hem yaratıcı fotoğrafçıların hem de vloggerların beklediği o kamera.</p>

<h2>Canon PowerShot V1 Nedir?</h2>
<p>2024 yılında tanıtılan PowerShot V1, 1 inç CMOS sensör, dahili değişken ND filtre ve 4K video özelliklerini kompakt bir gövdede bir araya getiriyor. Canon'un "yaratıcı kompakt" vizyonunu yeniden tanımlayan bu model, Türkiye'de Retrocameraland aracılığıyla edinilebilir.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 1 inç CMOS (yüksek performans)</li>
<li><strong>Video:</strong> 4K 30fps / FHD 120fps yavaş çekim</li>
<li><strong>Dahili ND Filtre:</strong> 1.5–6 stop, sahaya özel ayar</li>
<li><strong>Lens:</strong> 16–50mm f/2.8–5.6 (geniş açı başlangıç)</li>
<li><strong>Stabilizasyon:</strong> Optik + dijital hibrit IS</li>
<li><strong>Ekran:</strong> 3" döner dokunmatik LCD</li>
<li><strong>Bağlantı:</strong> Wi-Fi, Bluetooth, USB-C</li>
</ul>

<h2>Dahili ND Filtre: Neden Oyunun Kurallarını Değiştiriyor?</h2>
<p>ND filtre, aşırı parlak ortamlarda pozlamayı kontrol etmenizi sağlar. Normalde ayrı satın alınan bu aksesuar V1'de dahili geliyor — lensin önünde taşımanız gereken cam parçaları yok, değiştirme derdi yok. Parlak güneşte bile f/2.8'de çekim yapabilirsiniz.</p>

<h2>4K ve Yavaş Çekim: İçerik Üreticilerin Tercihi</h2>
<p>FHD 120fps yavaş çekim, normal hızın 4 katı yavaşlatma imkânı verir. Dalga, araç hareketi, dans adımları — sıradan anlar sinematik sekanslar haline gelir. 4K 30fps ise YouTube ve sosyal medya için doğrudan yayına hazır kalite.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Vlog ve sosyal medya içerik üreticileri</li>
<li>Seyahat fotoğrafçıları (kompakt ama güçlü)</li>
<li>Hem fotoğraf hem video kalitesi arayanlar</li>
<li>1 inç sensör kalitesini cebe sığar boyutta isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Canon PowerShot V1 telefon kamerasından neden üstün?</h3>
<p>1 inç sensör, telefon sensörlerinden 4-7 kat daha büyük. Bu; daha iyi arka plan bulanıklığı, daha az gürültü ve daha geniş dinamik aralık demek. Dahili ND filtre telefonda bulunmuyor.</p>
<h3>V1 RAW çekim destekler mi?</h3>
<p>Evet, CR3 RAW formatında çekim destekler. Lightroom ve Capture One ile tam uyumlu.</p>
<h3>Canon PowerShot V1 Türkiye'de garantisi var mı?</h3>
<p>Retrocameraland'den alınan V1, satış garantisiyle sunulmaktadır. Detaylar için ürün sayfasını inceleyebilirsiniz.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-powershot-v1" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon PowerShot V1'i İncele →</a></div>
"""},

# ── Canon PowerShot A480 ─────────────────────────────────────────────────────
{"title":"Canon PowerShot A480 İncelemesi: AA Pilli, Sade Tasarımlı Y2K Kompakt Kamera",
"handle":"canon-powershot-a480-inceleme-aa-pilli-y2k-kompakt",
"tags":"Canon, Canon PowerShot A480, Canon A serisi, retro kamera, y2k kamera, AA pil kamera",
"meta_desc":"Canon PowerShot A480 incelemesi: 10MP CCD, AA pil ve Canon'un güvenilir A serisi mühendisliği. Başlangıç retro kamera arayan herkes için ideal seçim.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0103_ONN01344.jpg?v=1757178561",
"body":"""
<p>Canon'un A serisi, onlarca yıl boyunca "ilk kamerasını alan herkes için" standardını belirledi. <strong>Canon PowerShot A480</strong>, bu mirasın 2009'daki temsilcisi — sade, güvenilir ve AA pile dayalı.</p>

<h2>Canon PowerShot A480 Nedir?</h2>
<p>2009 çıkışlı PowerShot A480, 10 megapiksel CCD sensör ve 3x optik zoomla (35–105mm) giriş seviyesi kompakt kamera segmentini temsil eden bir Canon modelidir. AA pil kullanımı ve dayanıklı plastik gövdesiyle uzun ömürlü kullanım için tasarlanmış.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 10 MP CCD</li>
<li><strong>Lens:</strong> Canon 3x optik zoom (35–105mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Pil:</strong> AA × 2 adet</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>ISO:</strong> 80–1600</li>
<li><strong>Sahne Modları:</strong> 15 farklı sahne modu</li>
</ul>

<h2>Canon A Serisi Güvenilirliği</h2>
<p>A serisi kameralar; plastik gövdeleri, AA pil kullanımları ve sezgisel arayüzleriyle on yıllarca "bir şeylere düşen, suda ıslanmayan ama yine de çalışan kamera" ününü korudu. A480 bu geleneği devam ettiriyor.</p>

<h2>10MP CCD ile Türkiye Retro Fotoğraf Topluluğunda Neden Popüler?</h2>
<p>Türkiye'deki Y2K kamera meraklıları arasında Canon A serisi, "herkesin koleksiyonunda olması gereken" kategorisinde değerlendiriliyor. Erişilebilir fiyatı ve CCD görüntü kalitesiyle başlangıç için mükemmel bir seçim.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Retro kamera koleksiyonuna AA pilli model eklemek isteyenler</li>
<li>Canon A serisi nostaljisi yaşayanlar</li>
<li>Bütçe dostu ilk CCD kamera arayanlar</li>
<li>Çocuklara veya öğrencilere kamera hediye etmek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Canon PowerShot A480 kaç MP?</h3>
<p>10 megapiksel CCD. Sosyal medya ve A4 baskı için yeterli çözünürlük.</p>
<h3>A480 SD kart kullanır mı?</h3>
<p>Evet, SD ve SDHC kart kullanır. 4-8 GB SD kart yeterli.</p>
<h3>A480 ile video çekilir mi?</h3>
<p>Evet, 640×480 (VGA) formatta video kaydeder. Video kalitesi günümüz standartlarında düşük ama retro estetik için yeterli.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-powershot-a480" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon PowerShot A480'i İncele →</a></div>
"""},

# ── Canon PowerShot A20 ──────────────────────────────────────────────────────
{"title":"Canon PowerShot A20 İncelemesi: 2001'den Kalma Dijital Fotoğraf Tarihi",
"handle":"canon-powershot-a20-inceleme-2001-dijital-tarih-koleksiyon",
"tags":"Canon, Canon PowerShot A20, erken dönem dijital kamera, koleksiyon kamera, retro kamera, 2001 kamera",
"meta_desc":"Canon PowerShot A20 incelemesi: 2001 yılından kalma 1.3MP CCD ve CompactFlash kart. Dijital fotoğraf tarihinin en değerli erken dönem koleksiyonlarından biri.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/canonon1.jpg?v=1753753972",
"body":"""
<p>2001. İnternet yeni yaygınlaşıyor, dijital kameralar lüks. <strong>Canon PowerShot A20</strong>, o dönemde bir kameranın yapabileceği her şeyi yapıyordu — ve bugün dijital fotoğraf tarihinin küçük ama değerli bir parçası.</p>

<h2>Canon PowerShot A20 Nedir?</h2>
<p>2001 yılında çıkan PowerShot A20, Canon'un tüketici segmentindeki ilk başarılı A serisi modellerinden biri. 1.3 megapiksel CCD, CompactFlash kart ve AA pil kombinasyonu, döneminin standart kompakt kamera formülüydü. Bugün ise bu kamera erken dijital dönemin mükemmel bir müze parçası.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 1.3 MP CCD</li>
<li><strong>Lens:</strong> Canon 3x optik zoom (35–105mm)</li>
<li><strong>Hafıza:</strong> CompactFlash (CF) kart</li>
<li><strong>Pil:</strong> AA × 4 adet</li>
<li><strong>Ekran:</strong> 1.8" renkli LCD</li>
<li><strong>Bağlantı:</strong> USB (veri aktarımı)</li>
</ul>

<h2>1.3 Megapiksel: Dönemin Lüksü, Bugünün Nostaljisi</h2>
<p>Bugün telefonlarımızda 50MP+ sensörler var. Ama 2001'de 1.3MP, bir tüketici kamerası için ciddi bir çözünürlüktü. Bu kamerayla çekilen fotoğraflar, o dönemin estetik anlayışını — piksel saydırılabilir boyutda, ama karakterli — mükemmel biçimde yansıtıyor.</p>

<h2>CompactFlash Kart: Koleksiyonun Tamamlayıcısı</h2>
<p>A20, SD kart öncesi dönemin standardı olan CompactFlash kullanıyor. Bu kartlar bugün hâlâ bulunabiliyor ve All-in-One kart okuyucularla modern bilgisayarlara bağlanabiliyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Erken dönem Canon dijital kamera koleksiyoncuları</li>
<li>2000'lerin başı dijital fotoğraf tarihini yaşatmak isteyenler</li>
<li>"Piksel sayılabilir" retro estetik arayanlar</li>
<li>Dijital fotoğraf müzesi kuran koleksiyoncular</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Canon PowerShot A20 çektiği fotoğraflar nereye kaydedilir?</h3>
<p>CompactFlash kart veya 8MB dahili hafızaya. CF kart All-in-One kart okuyucuyla modern bilgisayara aktarılabilir.</p>
<h3>A20 hâlâ fotoğraf çekebilir mi?</h3>
<p>Çalışır durumdaki örnekler evet. AA pil takılı ve CF kart mevcutsa tam işlevsel çalışır.</p>
<h3>PowerShot A20 koleksiyon değeri var mı?</h3>
<p>Evet, erken dönem Canon dijital modelleri (2000-2003) giderek değer kazanan koleksiyon parçaları. Özellikle orijinal kutusuyla birlikte olanlar prim yapıyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-powershot-a20-dijital-fotograf-makinesi" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon PowerShot A20'yi İncele →</a></div>
"""},

# ── Canon PowerShot SX160 IS ─────────────────────────────────────────────────
{"title":"Canon PowerShot SX160 IS İncelemesi: 16x Süper Zoom ve Güçlü Seyahat Kompaktı",
"handle":"canon-powershot-sx160-is-inceleme-16x-super-zoom-seyahat",
"tags":"Canon, Canon PowerShot SX160 IS, süper zoom kamera, seyahat kamerası, retro kamera, Canon SX serisi",
"meta_desc":"Canon PowerShot SX160 IS incelemesi: 16MP CCD, 16x optik zoom ve AA pil. Seyahat fotoğrafçılığı için güçlü süper zoom retro kompakt kamera.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0185_ONN01262.jpg?v=1757180114",
"body":"""
<p>16x optik zoom demek, karşı sokaktaki tabela yazısını okumak demek. <strong>Canon PowerShot SX160 IS</strong>, seyahat, doğa ve spor fotoğrafçılığına meraklı olanların vazgeçemeyeceği bir süper zoom kompakt.</p>

<h2>Canon PowerShot SX160 IS Nedir?</h2>
<p>2012 çıkışlı SX160 IS, 16 megapiksel CCD sensör ve 16x optik zoom (28–448mm eşdeğer) lens kombinasyonuyla uzak mesafeli çekimler için optimize edilmiş bir kompakt kamera. IS (Image Stabilizer) özelliği yüksek zoomda titreşimi azaltır.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 16 MP CCD</li>
<li><strong>Optik Zoom:</strong> 16x (28–448mm eşdeğer)</li>
<li><strong>Dijital Zoom:</strong> 4x (toplam 64x)</li>
<li><strong>Stabilizasyon:</strong> Optik IS (Image Stabilizer)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Pil:</strong> AA × 2 adet</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
</ul>

<h2>28–448mm: Hangi Sahneler için?</h2>
<p>28mm'deki geniş açı; manzara, mimari ve grup fotoğrafları için ideal. 448mm'deki maksimum zoom ise; kuş fotoğrafçılığı, spor çekimleri, dağdaki detaylar ve sahne fotoğrafçılığı için kullanılabilir. Tek kamerayla bu aralığı kapatmak, seyahatte büyük avantaj.</p>

<h2>AA Pil ile Seyahat Özgürlüğü</h2>
<p>Uçakta, şarj aleti kısıtlaması ya da adaptor sorunu yok. Dünyanın herhangi bir yerinde AA pil alıp devam edebilirsiniz. SX160 IS bu yönüyle seyahat fotoğrafçılığında pratik bir tercih.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğrafçılığı için süper zoom kamera arayanlar</li>
<li>Doğa ve yaban hayatı fotoğrafçıları</li>
<li>Spor ve uzak mesafe çekimi yapanlar</li>
<li>AA pilli güvenilir kamera tercih edenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>16x zoom ile titreşim sorunu olur mu?</h3>
<p>Optik IS sistemi titreşimi önemli ölçüde azaltır. Yine de 16x ve üzerinde sabit bir yüzey veya monopod kullanmak netliği artırır.</p>
<h3>SX160 ile RAW çekim yapılabilir mi?</h3>
<p>Hayır, JPEG formatında kaydeder. Canon'un SX serisi o dönem RAW desteklemiyordu.</p>
<h3>Hangi SD kart boyutu önerilir?</h3>
<p>16 veya 32 GB SDHC kart, 16MP çekimler için yeterli. SDXC kartlarla uyumluluk modele göre değişebilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-powershot-sx160-is" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon SX160 IS'i İncele →</a></div>
"""},

# ── Canon IXUS 285 HS ────────────────────────────────────────────────────────
{"title":"Canon IXUS 285 HS İncelemesi: 20MP, Wi-Fi ve IXUS'un Güçlü Son Nesli",
"handle":"canon-ixus-285-hs-inceleme-20mp-wifi-son-nesil-ixus",
"tags":"Canon, Canon IXUS 285 HS, IXUS serisi, Wi-Fi kamera, modern kompakt, 20MP kamera",
"meta_desc":"Canon IXUS 285 HS incelemesi: 20MP CMOS, 12x optik zoom, Wi-Fi ve NFC. Canon'un son nesil IXUS modeli akıllı bağlantı özellikleriyle öne çıkıyor.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/canon1.jpg?v=1754059585",
"body":"""
<p>Canon IXUS serisinin son nesli, şıklık geleneğini korurken akıllı bağlantı teknolojilerini bünyesine kattı. <strong>Canon IXUS 285 HS</strong>, Wi-Fi ve NFC'li kompakt kamera arayanların tercihi.</p>

<h2>Canon IXUS 285 HS Nedir?</h2>
<p>2016 çıkışlı IXUS 285 HS, Canon'un uzun soluklu IXUS serisinin son ve en güçlü modellerinden biri. 20.2 megapiksel CMOS sensör, 12x optik zoom, Wi-Fi ve NFC ile hem çekim kalitesi hem akıllı özellikler açısından güçlü bir paket sunuyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 20.2 MP CMOS</li>
<li><strong>İşlemci:</strong> DIGIC 4+</li>
<li><strong>Optik Zoom:</strong> 12x (25–300mm eşdeğer)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Video:</strong> Full HD 1080/30p</li>
<li><strong>Bağlantı:</strong> Wi-Fi, NFC</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
<li><strong>Stabilizasyon:</strong> Optik IS</li>
</ul>

<h2>Wi-Fi ile Anında Telefona Aktar</h2>
<p>IXUS 285 HS'in Wi-Fi özelliği, Canon Camera Connect uygulamasıyla doğrudan telefona aktarım sağlar. Kablo bağlantısına, kart okuyucuya gerek kalmadan fotoğraflar anında Instagram'a veya depolama alanınıza gidiyor.</p>

<h2>12x Zoom ile 25mm Geniş Açı</h2>
<p>25mm'den başlayan geniş açı, IXUS 285 HS'i seyahat ve manzara fotoğrafçılığı için özellikle güçlü kılıyor. 12x optik zoom ise mesafeli çekimlerde de yetersiz kalmıyor. Bu aralık çoğu günlük senaryoyu rahatlıkla karşılar.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Wi-Fi'li ve akıllı özellikli kompakt kamera arayanlar</li>
<li>IXUS serisinin son teknolojisini isteyenler</li>
<li>Seyahat için geniş zoom aralıklı şık kamera arayanlar</li>
<li>Hem koleksiyon hem günlük kullanım için modern kompakt isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>IXUS 285 HS ile RAW çekim yapılır mı?</h3>
<p>Hayır, JPEG formatında çekim yapar. Canon'un kompakt IXUS serisi RAW desteklemez.</p>
<h3>NFC özelliği ne işe yarar?</h3>
<p>NFC destekli Android telefonu kameraya dokundurarak anında Wi-Fi bağlantısı kurulur. Uygulama açma veya şifre girme gerekmez.</p>
<h3>IXUS 285 HS'in pili ne kadar dayanır?</h3>
<p>NB-11LH pil ile yaklaşık 220 kare çekim imkânı sunar. Uzun çekimler için yedek pil tavsiye edilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-ixus-285-hs" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon IXUS 285 HS'i İncele →</a></div>
"""},

# ── Canon Ixy IXUS Digital PC1060 ───────────────────────────────────────────
{"title":"Canon Ixy IXUS Digital PC1060 İncelemesi: Japonya'dan Gelen Nadir IXUS Versiyonu",
"handle":"canon-ixy-ixus-digital-pc1060-inceleme-nadir-japon-versiyonu",
"tags":"Canon, Canon Ixy, Canon IXUS Digital, nadir kamera, Japonya versiyonu, retro kamera koleksiyon",
"meta_desc":"Canon Ixy IXUS Digital PC1060 incelemesi: Japonya'ya özel nadir model, CCD sensör ve klasik IXUS tasarımı. Koleksiyonların en ilginç parçalarından biri.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0020_ONN00329.jpg?v=1774655366",
"body":"""
<p>Aynı kamera, farklı isimle. Canon, Japonya pazarı için IXUS serisini "Ixy" adıyla satıyordu. <strong>Canon Ixy IXUS Digital PC1060</strong>, bu çift kimlikli modelin koleksiyoncular için özel anlamı olan versiyonu.</p>

<h2>Canon Ixy IXUS Digital PC1060 Nedir?</h2>
<p>Canon'un IXUS serisinin Japonya pazarına özel "Ixy Digital" versiyonu. PC1060 model numarası ile tanınan bu kamera, CCD sensörlü klasik kompakt yapısıyla IXUS'un özünü korurken Japonya'ya özel renk ve paketleme seçenekleriyle küresel pazardan ayrışıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> CCD (Klasik IXUS kalitesi)</li>
<li><strong>Lens:</strong> Canon optik zoom</li>
<li><strong>Gövde:</strong> İnce alüminyum — klasik IXUS formu</li>
<li><strong>Hafıza:</strong> SD kart</li>
<li><strong>Menşei:</strong> Japonya pazarı özel versiyonu</li>
</ul>

<h2>Japon Pazarı Versiyonlarının Koleksiyon Değeri</h2>
<p>Canon, Japonya'da Ixy markasıyla sattığı modelleri bazen farklı renkler, farklı aksesuar paketleri ve zaman zaman donanım farklılıklarıyla piyasaya sürdü. Bu modeller küresel pazarda çok az sayıda dağıtıldığından koleksiyoncular arasında nadir sayılıyor.</p>

<h2>IXUS DNA: Neden Her Zaman Özel?</h2>
<p>IXUS serisi, compact kamera tasarımında bir etalon. Ultra ince alüminyum gövde, hassas düğme yerleşimi, güvenilir Canon mühendisliği. PC1060, bu mirası Japon pazarına özgü kimliğiyle taşıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Canon Ixy / IXUS seri koleksiyoncuları</li>
<li>Japonya pazarı özel versiyonları meraklıları</li>
<li>Nadir ve az bulunan kompakt kamera arayanlar</li>
<li>CCD görüntü kaliteli klasik IXUS sahiplenmek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Ixy ve IXUS arasındaki fark nedir?</h3>
<p>Yalnızca pazar adı farklı. Ixy Japonya, IXUS Avrupa ve küresel pazar için kullanılan isim. Donanım özünde aynı Canon mühendisliği.</p>
<h3>PC1060 Japonya'da mı üretildi?</h3>
<p>Canon kameraları çeşitli fabrikalardan üretilir; "Japonya versiyonu" üretim yerini değil pazarlama bölgesini belirtir.</p>
<h3>Bu model için yedek parça bulunabilir mi?</h3>
<p>Standart IXUS/Ixy serisi parçaları ve piller hâlâ temin edilebilir. Kart uyumluluğu SD/SDHC standarttır.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/canon-ixy-ixus-digital-pc1060" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon Ixy PC1060'ı İncele →</a></div>
"""},

]

def run():
    results = []
    for i, p in enumerate(POSTS, 1):
        log(f"\n[{i}/{len(POSTS)}] {p['title'][:65]}...")
        try:
            aid, handle = pub(p["title"], p["handle"], p["tags"], p["meta_desc"], p.get("image_src"), p["body"])
            results.append({"status":"ok","id":aid,"handle":handle,"title":p["title"]})
        except Exception as e:
            log(f"  ❌ {e}")
            results.append({"status":"error","title":p["title"],"error":str(e)})
    log("\n=== BATCH 1 SONUÇ ===")
    ok = sum(1 for r in results if r["status"]=="ok")
    for r in results:
        icon = "✅" if r["status"]=="ok" else "❌"
        log(f"  {icon} {r['title'][:55]}")
    log(f"\n{ok}/{len(POSTS)} yayınlandı.")

if __name__ == "__main__":
    run()
