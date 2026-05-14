#!/usr/bin/env python3
"""
retrocameraland.com — Günlük Otomatik Blog Yayıncısı
Çalıştır: python3 retrocameraland-auto-publisher.py
Her çalıştırmada KONU_HAVUZU'ndan 20 yeni blog seçer, görsel üretir, yayınlar.
"""

import sys, os, json, time, random, textwrap
sys.path.insert(0, os.path.dirname(__file__))
from retrocameraland_api import shopify, fal_generate_image, log, SOCIAL_BLOCK, CTA_BLOCK

BLOG_ID         = "91197866123"
STATE_FILE      = os.path.join(os.path.dirname(__file__), "published-topics.json")
OUTPUT_DIR      = os.path.join(os.path.dirname(__file__), "outputs")
DAILY_TARGET    = 20
FAL_RETRY_WAIT  = 90   # saniye — rate limit sonrası bekleme

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# KONU HAVUZU  (300 konu — başlık, etiketler, görsel prompt, içerik anahtarı)
# ─────────────────────────────────────────────────────────────────────────────

def make_slug(title):
    import re
    replacements = {"ş":"s","ç":"c","ö":"o","ü":"u","ğ":"g","ı":"i",
                    "Ş":"s","Ç":"c","Ö":"o","Ü":"u","Ğ":"g","İ":"i"," ":"-"}
    s = "".join(replacements.get(c, c) for c in title).lower()
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:80]


# İçerik şablonları — key'e göre body_html üretir
def body_model_review(brand, model, year, mp, feature, use_case, tips):
    return f"""
<h2>{brand} {model} Nedir? (Doğrudan Cevap)</h2>
<p><strong>{brand} {model}</strong>, {year} yılında üretilmiş, {mp} megapiksel çözünürlüğe sahip kompakt bir dijital fotoğraf makinesidir. {feature} sayesinde Y2K estetik fotoğrafçılığının gözdesi haline gelmiştir.</p>

<h2>Temel Özellikler</h2>
<ul>
<li><strong>Çözünürlük:</strong> {mp} megapiksel CCD sensör</li>
<li><strong>Öne Çıkan Özellik:</strong> {feature}</li>
<li><strong>İdeal Kullanım:</strong> {use_case}</li>
<li><strong>Y2K Estetiği:</strong> Doğal film greni, sıcak ton, lens haleleri</li>
</ul>

<h2>{brand} {model} ile Nasıl Fotoğraf Çekilir?</h2>
<p>{tips[0]}</p>
<p>{tips[1]}</p>
<ol>
<li><strong>Program modu:</strong> Otomatik mod çoğu sahnede mükemmel sonuç verir</li>
<li><strong>Düşük ışık:</strong> Gece çekimlerinde yüksek ISO gürültüsü Y2K estetiğini güçlendirir</li>
<li><strong>Yakın çekim:</strong> Makro modu {brand} {model}'in gizli gücüdür</li>
<li><strong>Flaş kontrolü:</strong> Kapalı ortamda "Auto Flash", açık havada "Flash Off"</li>
</ol>

<h2>Kimler İçin İdeal?</h2>
<p>{brand} {model}, {use_case} için arayanların ilk tercihi olmaya devam ediyor. Özellikle sosyal medya içerik üreticileri, nostaljik estetik arayanlar ve retro kamera koleksiyoncuları bu modeli tercih ediyor.</p>

<h2>Türkiye'de {brand} {model} Fiyatı</h2>
<p>İkinci el pazarında {brand} {model} ₺800-₺2.500 arasında işlem görüyor. Orijinal kutusu ve aksesuarlarıyla birlikte olanlar daha yüksek fiyattan satılıyor. <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunda</a> test edilmiş modeller mevcuttur.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>{brand} {model} bataryası nereden bulunur?</h3>
<p>Modelin kullandığı batarya büyük ihtimalle hâlâ üretilmektedir. Elektronik marketler ve online platformlarda temin edilebilir.</p>
<h3>{brand} {model} SD kart hangisi?</h3>
<p>{year} model kameralarda genellikle 2-4 GB SD kart önerilir. Daha büyük kapasiteli kartlar uyumsuzluk yaratabilir.</p>
"""

def body_city_guide(city, neighborhoods, landmarks, season_tip):
    return f"""
<h2>Retro Kamera ile {city}: Neden Eşsiz?</h2>
<p>{city}, retro dijital kameranın Y2K estetiğiyle buluşunca başka bir boyut kazanıyor. Tarihi dokusu, renkli sokakları ve dinamik şehir hayatıyla {city}, her çekimde hikaye anlatan bir sahne sunuyor.</p>

<h2>{city}'in En Fotojenik Mahalleleri ve Noktaları</h2>
{"".join(f"<h3>{n[0]}</h3><p>{n[1]}</p>" for n in neighborhoods)}

<h2>{city}'de Retro Kamera ile Mutlaka Çekilmesi Gereken Kareler</h2>
<ul>
{"".join(f"<li><strong>{lm[0]}:</strong> {lm[1]}</li>" for lm in landmarks)}
</ul>

<h2>Mevsimsel Çekim Rehberi</h2>
<p>{season_tip}</p>

<h2>Pratik Çekim İpuçları</h2>
<ol>
<li><strong>Sabah erken saatler:</strong> 07:00-09:00 arası altın ışık {city} sokaklarını sinematik bir sahneye dönüştürür</li>
<li><strong>Gece çekimi:</strong> Neon tabelalar ve sokak lambaları retro kameranın sensöründe büyüleyici hale oluşturur</li>
<li><strong>Hareketli kalabalık:</strong> Netlemeyi önceden yapın, spontane anları yakalamak için hazır bekleyin</li>
<li><strong>Yağmurlu hava:</strong> Islak kaldırım yansımaları retro kameranın en dramatik görüntülerini üretir</li>
</ol>

<h2>Ulaşım ve Pratik Bilgiler</h2>
<p>{city}'de fotoğraf çekimi için toplu taşıma ile ulaşmak önerilir — kamera ve ekipmanla araç park sorunu yaşamazsınız. Çekim için ortalama yarım gün yeterlidir.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>{city}'de sokak fotoğrafı için izin gerekiyor mu?</h3>
<p>Türkiye'de kamusal alanlarda fotoğraf çekmek serbesttir. Özel mülklerde çekim için izin alınması kibarlık kuralıdır.</p>
<h3>Retro kamerayla {city}'de en iyi çekim vakti ne zaman?</h3>
<p>Altın saat (sabah 07-09 ve akşam 17-19) ile gece çekimleri en etkileyici sonuçları verir.</p>
"""

def body_technique(technique, description, tips, faq_q, faq_a):
    return f"""
<h2>{technique} Nedir? (Doğrudan Cevap)</h2>
<p>{description}</p>

<h2>Retro Kamera ile {technique}: Neden Farklı?</h2>
<p>Modern kameralar {technique} için hesaplamalı fotoğrafçılık algoritmalarına güvenir. Retro kameralar ise ham sensör kısıtlamalarıyla doğal, kusurlu ve otantik sonuçlar üretir — tam olarak Y2K estetiğinin aradığı şey budur.</p>

<h2>Adım Adım {technique} Rehberi</h2>
<ol>
{"".join(f"<li>{t}</li>" for t in tips)}
</ol>

<h2>Dikkat Edilmesi Gerekenler</h2>
<ul>
<li>Retro kameranın netleme gecikmesini hesaba katın — harekete geçmeden önce yarı basın</li>
<li>Bataryanın dolu olduğundan emin olun</li>
<li>SD kartın boş kapasitesi olduğunu kontrol edin</li>
</ul>

<h2>Sosyal Medya için {technique} İpuçları</h2>
<p>Bu teknikle çekilen fotoğraflar Instagram ve TikTok'ta #RetroCamera #Y2KAesthetic #VintageDigital gibi hashtag'lerle yüksek etkileşim alır. Retrocameraland topluluğunu takip ederek ilham alabilirsiniz.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>{faq_q}</h3>
<p>{faq_a}</p>
<h3>Hangi retro kamera modeli bu teknik için en iyisi?</h3>
<p>Sony DSC-T serisi, Canon IXUS ve Fujifilm FinePix Z serisi bu teknik için en sık tercih edilen modellerdir. <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunda</a> bu modellerin güncel stoklarına bakabilirsiniz.</p>
"""

def body_lifestyle(topic, intro, sections, cta_text):
    sections_html = ""
    for title, content in sections:
        sections_html += f"<h2>{title}</h2>\n<p>{content}</p>\n"
    return f"""
<p>{intro}</p>
{sections_html}
<h2>Sonuç: Retrocameraland Güvencesiyle</h2>
<p>{cta_text} <a href="https://retrocameraland.com/collections/all">Tüm koleksiyonu görüntülemek için tıklayın →</a></p>
<h2>Sık Sorulan Sorular</h2>
<h3>Retro kamera satın almak için en güvenilir kaynak hangisi?</h3>
<p>Retrocameraland, Türkiye'nin en kapsamlı test edilmiş retro dijital kamera platformudur. Her kamera çalışır garantisiyle satılmaktadır.</p>
<h3>Retro kamera başlangıç bütçesi ne kadar?</h3>
<p>₺800-₺2.000 arası bütçeyle kaliteli bir başlangıç retro dijital kamerası edinilebilir.</p>
"""

# ─────────────────────────────────────────────────────────────────────────────
# KONU HAVUZU DATA
# ─────────────────────────────────────────────────────────────────────────────

TOPICS = [
    # ─── KAMERA İNCELEMELERİ ───────────────────────────────────────────────
    {"title":"Canon PowerShot A400 İncelemesi: 2003'ün Efsane Retro Kamerası",
     "tags":"canon powershot a400, retro kamera inceleme, canon dijital kamera, y2k kamera, retrocameraland",
     "img":"Canon PowerShot A400 vintage digital camera, warm Y2K product shot, retro 2003 compact camera, grain texture, nostalgic",
     "imgf":"canon-powershot-a400-retro-kamera-inceleme-2003-efsane.jpg",
     "meta":"Canon PowerShot A400 incelemesi: 2003'ün en iyi kompakt kameraları arasındaki bu modelin Y2K estetiği ve özellikleri.",
     "type":"model_review","args":("Canon","PowerShot A400","2003","4 MP","AA pil ile çalışması ve sağlam yapısı","aile ve sokak fotoğrafçılığı",
       ["Canon PowerShot A400'ün güçlü yanlarından biri AA pil kullanmasıdır — şarj aleti olmadan AA pille hızla hazır hale gelir.",
        "Geniş açılı 35mm eşdeğer lens, sokak ve grup fotoğrafları için oldukça kullanışlıdır."])},

    {"title":"Fujifilm FinePix A200: Sarı Tonların Ustası",
     "tags":"fujifilm finepix a200, fujifilm retro kamera, sarı ton kamera, y2k estetik, retrocameraland",
     "img":"Fujifilm FinePix A200 vintage digital camera, warm yellow tones, Y2K 2003 era product photo, retro grain, nostalgic",
     "imgf":"fujifilm-finepix-a200-sari-ton-y2k-retro-kamera-inceleme.jpg",
     "meta":"Fujifilm FinePix A200 incelemesi: Fujifilm'in karakteristik sarı-sıcak tonları ve Y2K estetiğiyle neden bu kadar sevildiği.",
     "type":"model_review","args":("Fujifilm","FinePix A200","2003","2 MP","Fujifilm'e özgü sıcak sarı renk tonu","nostaljik ve retro Y2K fotoğrafçılık",
       ["Fujifilm FinePix A200, düşük ışıkta çarpıcı sarı-turuncu gürültü üretir — bu tam olarak istenen Y2K estetiğidir.",
        "2 megapiksel çözünürlük düşük görünse de bu 'sınırlılık' aynı zamanda mükemmel piksel gürültüsü sağlar."])},

    {"title":"Nikon Coolpix L10 İncelemesi: Giriş Seviyesi Y2K Kamerasının Şampiyonu",
     "tags":"nikon coolpix l10, nikon retro kamera, giriş seviye kamera, y2k nikon, retrocameraland",
     "img":"Nikon Coolpix L10 compact digital camera, retro 2005 era product photography, warm tones, nostalgic grain, minimalist",
     "imgf":"nikon-coolpix-l10-giris-seviye-y2k-retro-kamera-inceleme.jpg",
     "meta":"Nikon Coolpix L10 incelemesi: giriş seviyesi fiyatıyla Y2K estetiği sunan bu modelin özellikleri ve kullanım ipuçları.",
     "type":"model_review","args":("Nikon","Coolpix L10","2006","6 MP","AA pil ve geniş zoom aralığı","günlük kayıt ve aile anları",
       ["Coolpix L10'un 6x optik zoom'u retro kamera standartlarında etkileyicidir — uzaktan çekim bile Y2K tonlarını korur.",
        "AA pil kullanımı tatil ve seyahatlerde pratiklik sağlar, şarj aleti taşıma derdi ortadan kalkar."])},

    {"title":"Panasonic Lumix DMC-FX07: Ultra İnce Y2K İkonu",
     "tags":"panasonic lumix fx07, panasonic retro kamera, ultra ince kamera, y2k kamera, retrocameraland",
     "img":"Panasonic Lumix DMC-FX07 ultra thin digital camera, silver metallic body, Y2K product photo, retro compact, warm tones",
     "imgf":"panasonic-lumix-dmc-fx07-ultra-ince-y2k-ikon-retro-kamera.jpg",
     "meta":"Panasonic Lumix DMC-FX07 incelemesi: ultra ince metalik gövdesi, Leica lensi ve Y2K estetiğiyle bu modelin özellikleri.",
     "type":"model_review","args":("Panasonic","Lumix DMC-FX07","2006","7.2 MP","Leica DC Vario-Elmarit lens ve ultra ince tasarım","moda ve stil fotoğrafçılığı",
       ["FX07'nin Leica lensi, Y2K gürültüsüne rağmen keskinlik ve renk doğruluğu açısından rakipsizdir.",
        "Ultra ince metalik gövdesi, kamerayı bir aksesuar gibi taşımanıza olanak verir — Y2K estetiğiyle mükemmel uyum."])},

    {"title":"Samsung Digimax A400: Güney Kore'nin Retro Kamera Cevabı",
     "tags":"samsung digimax a400, samsung retro kamera, y2k kamera inceleme, retrocameraland, dijital kamera",
     "img":"Samsung Digimax A400 vintage digital camera, Korean brand retro product, Y2K era compact, warm tones, grain effect",
     "imgf":"samsung-digimax-a400-guney-kore-retro-kamera-inceleme-y2k.jpg",
     "meta":"Samsung Digimax A400 incelemesi: Güney Kore retro kamerası olarak Y2K estetiğine katkısı ve günümüzdeki koleksiyon değeri.",
     "type":"model_review","args":("Samsung","Digimax A400","2004","4 MP","Samsung'un canlı renk işlemesi ve sağlam yapısı","aile belgelemesi ve nostaljik çekim",
       ["Samsung Digimax A400'ün renk işlemesi, diğer marka kameralara göre daha doygun ve canlı tonlar üretir.",
        "Sağlam plastik gövdesi, günlük kullanımda darbelere karşı dayanıklıdır — koleksiyoncular için çalışır olmasına dikkat edin."])},

    {"title":"Kodak EasyShare C330: Dijital Fotoğrafçılığı Demokratikleştiren Kamera",
     "tags":"kodak easyshare c330, kodak retro kamera, y2k kamera, retrocameraland, dijital kamera",
     "img":"Kodak EasyShare C330 compact digital camera, Kodak yellow branding, Y2K retro product shot, warm grain, nostalgic",
     "imgf":"kodak-easyshare-c330-dijital-fotografciligi-demokratize-eden-kamera.jpg",
     "meta":"Kodak EasyShare C330 incelemesi: dijital fotoğrafçılığı kitleselleştiren bu modelin Y2K estetiği ve Kodak'ın ikonik renk anlayışı.",
     "type":"model_review","args":("Kodak","EasyShare C330","2004","4 MP","Kodak'ın karakteristik sıcak ton işlemesi ve basit kullanım","aileler ve yeni başlayanlar",
       ["Kodak'ın özel renk bilimi, EasyShare C330'u Y2K estetik fotoğrafları için doğal bir seçim yapıyor.",
        "Basit kullanıcı arayüzü, teknik bilgisi olmayanlara bile retro estetik üretme imkânı tanır."])},

    {"title":"Sony Cyber-shot DSC-W7 İncelemesi: 7.2 MP ile Y2K Zirvedeyken",
     "tags":"sony cybershot dsc-w7, sony retro kamera, 7mp dijital kamera, y2k sony, retrocameraland",
     "img":"Sony Cyber-shot DSC-W7 vintage digital camera, silver compact body, Y2K 2005 product photography, nostalgic grain",
     "imgf":"sony-cybershot-dsc-w7-inceleme-72mp-y2k-zirve-retro-kamera.jpg",
     "meta":"Sony Cyber-shot DSC-W7 incelemesi: 2005 yılının 7.2 MP amiral gemisi, Y2K estetiği ve Sony'nin ünlü Carl Zeiss lensi.",
     "type":"model_review","args":("Sony","Cyber-shot DSC-W7","2005","7.2 MP","Carl Zeiss Vario-Tessar lens ve optik görüntü sabitleme","Tüm senaryolarda güvenilir Y2K çekimi",
       ["Sony'nin Carl Zeiss lensi, piksel gürültüsünün yanı sıra mükemmel renk ayrımı sağlar — fotoğraflara sanatsal bir derinlik katar.",
        "Optik görüntü sabitleme, özellikle karanlık ortamlarda el titremesini azaltarak daha keskin gürültülü sonuçlar verir."])},

    # ─── ŞEHİR REHBERLERİ ─────────────────────────────────────────────────
    {"title":"Kadıköy'de Retro Kamera: Moda'dan Çarşı'ya Fotoğraf Rotası",
     "tags":"kadıköy retro kamera, kadıköy fotoğrafçılık, moda sahil foto, istanbul asia retro, retrocameraland",
     "img":"Kadikoy Istanbul street market photography vintage digital camera, colorful fruit stands, Y2K aesthetic, warm morning light, bustling market",
     "imgf":"kadikoy-retro-kamera-moda-carsi-fotograf-rotasi-istanbul.jpg",
     "meta":"Kadıköy'de retro kamera ile fotoğraf rotası: Moda sahilinden Kadıköy Çarşısı'na, en fotojenik noktalar ve çekim ipuçları.",
     "type":"city_guide","args":("Kadıköy",
       [("Moda Sahili","Gün doğumu ve gün batımında boğaz manzaralı çekimler. Sabah 7'de Moda sahilinde çekilen retro kamera fotoğrafları, altın saatin sıcak tonlarını mükemmel yakalar."),
        ("Kadıköy Çarşısı","Pazarcılar, rengarenk tezgahlar, eski hanlar. Sabah 9-11 arası en canlı dönem. Yukarıdan bakıldığında insanların arasındaki karmaşık doku inanılmaz Y2K sokak estetiği yaratır."),
        ("Bahariye Caddesi","Tarihî yapılar ve modern dükkânların yan yana geldiği bu cadde, kontrast açısından zengin görüntüler sunar.")],
       [("Moda İskelesi","Tarihi iskele, deniz ve tekneler — geniş açıda çekim"),
        ("Rıhtım Pazarı","Pazar sabahları antika tezgahlar, rengarenk nesneler"),
        ("Kız Kulesi (uzaktan)","Retro kamerayla tele çekim — arka plan sfumato etkisi")],
       "İlkbahar ve sonbahar Kadıköy fotoğrafçılığı için en ideal mevsimlerdir. Yaz aylarında sabah erken saatler kalabalıktan kaçınmak ve altın ışığı yakalamak için idealdir.")},

    {"title":"Beyoğlu ve İstiklal'de Retro Kamera: Gece Fotoğrafçılığı Rotası",
     "tags":"beyoğlu retro kamera, istiklal caddesi fotoğraf, galata kulesi foto, y2k istanbul gece, retrocameraland",
     "img":"Istiklal Avenue Istanbul night photography vintage digital camera, neon lights bokeh, crowded street Y2K aesthetic, warm city glow",
     "imgf":"beyoglu-istiklal-retro-kamera-gece-fotografciligi-rotasi.jpg",
     "meta":"Beyoğlu ve İstiklal'de retro kamerayla gece fotoğrafçılığı: neon ışıklar, tarihi binaların arasında Y2K estetik rehberi.",
     "type":"city_guide","args":("Beyoğlu",
       [("İstiklal Caddesi","Neon tabelalar, tarihi binalar, kalabalık cadde. Gece 20:00-22:00 arasında en yoğun canlı ortam. Retro kameranın düşük ışık gürültüsü İstiklal'in enerjisini mükemmel yakalar."),
        ("Galata Köprüsü Altı","Balıkçılar, aydınlatılmış köprü kemerleri, martılar. Akşam saatlerinde köprü lambalarının suya yansıması dramatik çekimler sağlar."),
        ("Cihangir Sokakları","Sakin, asimetrik sokaklar. Gündüz manzara, gece kafe vitrinleri.")],
       [("Tünel Meydanı","Tarihi Tünel'in girişi, Y2K renkleri için ideal"),
        ("Çiçek Pasajı","Tarihi pasaj, neon levhalar, kadife perde vitrinler"),
        ("Boğaz manzarası (Galata'dan)","Köprü ve Boğaz — gece retro çekim")],
       "Kış aylarında İstiklal Caddesi ve çevresi ışıl ışıl süslemelerle kaplıdır — retro kamera için yılın en iyi gece sahnesini sunar.")},

    {"title":"Eskişehir'de Retro Kamera: Üniversite Şehrinin Y2K Ruhu",
     "tags":"eskişehir retro kamera, eskişehir fotoğrafçılık, porsuk nehri foto, üniversite şehri retro, retrocameraland",
     "img":"Eskisehir Turkey vintage street photography, colorful Odunpazari houses, retro digital camera Y2K aesthetic, warm afternoon light",
     "imgf":"eskisehir-retro-kamera-universite-sehri-y2k-ruhu-fotografcilik.jpg",
     "meta":"Eskişehir'de retro kamerayla fotoğrafçılık: Odunpazarı'nın renkli evlerinden Porsuk kıyısına Y2K estetik rehberi.",
     "type":"city_guide","args":("Eskişehir",
       [("Odunpazarı Tarihi Mahallesi","Renkli osmanlı evleri, arnavut kaldırımlar, tarihi çeşmeler. Türkiye'nin en fotojenik tarihi mahallelerinden biri — retro kamerayla sanki zaman içinde donmuş hissettiriyor."),
        ("Porsuk Nehri Kıyısı","Gondol yolculukları, kanalı çevreleyen kafeler ve köprüler. Akşam saatlerinde nehir yansımaları retro kamerada film görseli gibi görünür."),
        ("ESOGÜ Kampüsü","Üniversite enerjisi, genç kalabalıklar, modern mimariyle tarihin yan yanalığı.")],
       [("Odunpazarı Renkli Evler","Kuzey Avrupa tarzı renkli cepheler — Y2K paleti için hazır"),
        ("Porsuk'un Gondol Köprüleri","Aşk kilitleri, köprü gölgeleri, yansıma çekimi"),
        ("Cam Teras Kafe","Cam önünde çay + retro kamera — flat lay içeriği")],
       "İlkbahar ve sonbahar Eskişehir fotoğrafçılığı için idealdir. Yaz aylarında öğrenci kalabalığı azaldığından sakin çekim ortamı oluşur.")},

    {"title":"Bursa'da Retro Kamera: Yeşil Şehrin Nostaljik Keşfi",
     "tags":"bursa retro kamera, bursa fotoğrafçılık, uludağ foto, yeşil bursa retro, retrocameraland",
     "img":"Bursa Turkey historical mosque and market photography vintage digital camera, green city atmosphere, Y2K warm tones, Ottoman architecture",
     "imgf":"bursa-retro-kamera-yesil-sehir-nostaljik-kesif-fotografcilik.jpg",
     "meta":"Bursa'da retro kamerayla fotoğrafçılık: Kapalı Çarşı'dan Uludağ'a, Osmanlı mimarisinin Y2K estetiğiyle buluşması.",
     "type":"city_guide","args":("Bursa",
       [("Kapalı Çarşı ve Hanlar","Osmanlı dönemi bedesteni, tarihi hanlar, ipek tüccarları. Işık huzmelerinin çarşı içinden süzülmesi retro kamerada sinematik etkiler yaratır."),
        ("Yeşil Cami ve Türbe","Türk-İslam mimarisinin incisi, mürekkep yeşili çini. Açık havada doğal ışıkla çekim için sabah saatleri idealdir."),
        ("Tophane ve Atatürk Caddesi","Osmanlı surları, şehir panoraması, çay bahçeleri. Gün batımında şehri kuşbakışı görmek için mükemmel nokta.")],
       [("Uludağ Teleferik","Şehir panoraması — uzun odak mesafesi çekimi"),
        ("Tophane Kalesi","Tarihi surlar, şehir ve dağ çerçevesi"),
        ("Irgandı Köprüsü","Dükkanlarla kaplı tarihi köprü — Avrupa dışında eşsiz")],
       "İlkbaharda Uludağ'ın karla kaplı zirveleri şehir siluetini tamamlar. Sonbaharda Kapalı Çarşı'nın altın ışığı retro kamera için biçilmiş kaftan.")},

    {"title":"Antalya'da Retro Kamera: Tarihi Kaleiçi ve Akdeniz Işığı",
     "tags":"antalya retro kamera, kaleiçi fotoğrafçılık, akdeniz ışık retro, antalya tarihi, retrocameraland",
     "img":"Antalya Kaleici old town photography vintage digital camera, Mediterranean light, Roman ruins, yacht harbor, Y2K warm aesthetic",
     "imgf":"antalya-retro-kamera-tarih-kaleici-akdeniz-isigi-fotografcilik.jpg",
     "meta":"Antalya'da retro kamerayla fotoğrafçılık: Kaleiçi'nin Roma mirasından Akdeniz kıyısına uzanan Y2K estetik rehberi.",
     "type":"city_guide","args":("Antalya",
       [("Kaleiçi Tarihi Yarımada","Roma limanı, Osmanlı evleri, kiliseden dönüşme camiler. Taş sokakların dar ve doğrusal yapısı retro kameranın geniş açılı lensinde perspektif çizgileri oluşturur."),
        ("Hadrian Kapısı","2.000 yıllık zafer takı. Sabah ışığında kemerik yansımalar ve derinlik, retro kameranın en güçlü kareini üretir."),
        ("Yacht Limanı","Tekne yansımaları, rıhtım kafeler, Akdeniz mavisi. Öğle saatlerinde suyun parıltısı retro kamerada hale efektleri yaratır.")],
       [("Hıdırlık Kulesi","Denize bakan antik kule — panorama çekimi"),
        ("Kaleiçi Sokakları","Sarmaşıklı duvarlar, çiçekli balkonlar, renkli kapılar"),
        ("Düden Şelalesi","Denize dökülen şelale — Y2K kamerası için nadir bir çekim")],
       "Kış ve ilkbahar Antalya fotoğrafçılığı için idealdir — turistik kalabalık azdır, ışık yumuşaktır. Yaz aylarında şiddetli güneş retro kameranın aşırı pozlama özelliğini açığa çıkarır.")},

    # ─── TEKNİK REHBERLER ─────────────────────────────────────────────────
    {"title":"Retro Kamera ile Makro Fotoğrafçılık: Küçük Dünyanın Büyük Estetiği",
     "tags":"makro fotoğrafçılık, retro kamera makro, yakın çekim, y2k makro estetik, retrocameraland",
     "img":"macro photography with vintage digital camera, flower petal extreme closeup, Y2K grain texture, warm colors, detailed texture, retro aesthetic",
     "imgf":"retro-kamera-makro-fotografcilik-kucuk-dunya-buyuk-estetik.jpg",
     "meta":"Retro kamerayla makro fotoğrafçılık: yakın çekim tekniklerinde Y2K estetiğinin gücü ve doğru yöntemler.",
     "type":"technique","args":("Retro Kamera ile Makro Fotoğrafçılık",
       "Makro fotoğrafçılık, çıplak gözle fark edilemeyen ayrıntıları büyüterek görünür kılma sanatıdır. Retro kameralar, makro modda hem net detay hem de Y2K estetiğinin karakteristik gürültüsünü aynı karede sunar.",
       ["Retro kameranızın makro modunu (genellikle çiçek simgesi) aktif edin",
        "Konuya kameranın minimum netleme mesafesine kadar yaklaşın — genellikle 5-15 cm",
        "Nefes tutun veya kamerayı sabit bir yüzeye yaslayın",
        "Flaşı kapatın — doğal ışık makroda daha yumuşak ve doğal sonuç verir",
        "Birden fazla çekim yapın — retro kameranın netleme belirsizliği ancak deneme yanılmayla aşılır"],
       "Retro kameranın makro modu ne kadar yakına kadar netleyebilir?",
       "Çoğu retro kamera 5-15 cm minimum netleme mesafesine sahiptir. Sony DSC-T serisi ve Fujifilm FinePix modelleri genellikle 5 cm'e kadar netleyebilir.")},

    {"title":"Retro Kamera ile Manzara Fotoğrafçılığı: Doğanın Y2K Hali",
     "tags":"manzara fotoğrafçılığı, retro kamera manzara, doğa fotoğrafı, y2k manzara, retrocameraland",
     "img":"landscape photography with vintage digital camera, mountain valley sunrise, warm Y2K tones, grain effect, nostalgic nature shot, Turkish landscape",
     "imgf":"retro-kamera-manzara-fotografciligi-dogal-y2k-estetik-rehberi.jpg",
     "meta":"Retro kamerayla manzara fotoğrafçılığı: doğanın Y2K estetiğine dönüşümü, altın saat teknikleri ve Türkiye'nin en fotojenik noktaları.",
     "type":"technique","args":("Retro Kamera ile Manzara Fotoğrafçılığı",
       "Manzara fotoğrafçılığı, retro kameraların beklenmedik gücünü ortaya çıkardığı alanlardan biridir. Düşük çözünürlük ve sıcak ton işleme, geniş manzaraları sanki eski bir fotoğraf albumünden alınmış gibi gösterir.",
       ["Altın saati (sabah 07-09, akşam 17-19) tercih edin — retro kameranın sıcak tonları bu ışıkla katlanır",
        "Yüksek ISO'da çekilmiş sisli dağ manzaraları Y2K estetiğinin en güçlü görüntülerini üretir",
        "Ufuk çizgisini çerçevenin üçte birine yerleştirin — manzara veya gökyüzüne ağırlık verin",
        "Uzun süreli pozlamayı 'Night Scene' modunda deneyin — hareket suyu ipek görünümünde gösterir",
        "Retro kameranın flaşını kapalı tutun — manzarada flaş işe yaramaz, doğal ışığı kullanın"],
       "Retro kamerayla ufuk çizgisini nasıl düz tutarım?",
       "Çoğu retro kamerada ızgara/kılavuz çizgi seçeneği yoktur. Telefon kamerasının yatay ölçer özelliğini referans alabilirsiniz, ya da kamerayı üçüncü bir yüzeye dayayarak deneyin.")},

    {"title":"Etkinlik ve Konser Fotoğrafçılığı: Retro Kamera ile Anları Yakalamak",
     "tags":"konser fotoğrafçılık, etkinlik fotoğraf, retro kamera konser, y2k etkinlik, retrocameraland",
     "img":"music concert event photography vintage digital camera, stage lights bokeh, crowd energy, Y2K aesthetic neon glow, grain effect",
     "imgf":"etkinlik-konser-fotografciligi-retro-kamera-anlari-yakalamak.jpg",
     "meta":"Retro kamerayla etkinlik ve konser fotoğrafçılığı: canlı müzik ve festivallerde Y2K estetik çekimler için teknikler.",
     "type":"technique","args":("Etkinlik ve Konser Fotoğrafçılığı",
       "Etkinlik ve konserler, retro kameraların en çok parlayan ortamlardan biridir. Sahne ışıklarının neon renkleri, kalabalığın enerjisi ve düşük ışık koşullarında oluşan dijital gürültü — bunların hepsi Y2K fotoğrafçılığının temel unsurlarıdır.",
       ["Flaşı kapatın — sahneden gelen ışıkla çekim hem estetik hem de saygılıdır",
        "ISO'yu en yüksek değere alın — yüksek gürültü konser estetiğine güç katar",
        "Hareketle gelen bulanıklığı kabul edin — müzisyenlerin hareketli çekimi Y2K hissini güçlendirir",
        "Kalabalık genel çekimleri için geniş açı, sahne detayları için orta plan kullanın",
        "Retro kameranızı sıkı tutun — el titremesi müzik enerjisinin fotoğrafa yansımasına katkı sağlar"],
       "Konserde retro kamerayla çekim yapabilir miyim?",
       "Çoğu mekan ticari amaç taşımayan kişisel kameralarla çekime izin verir. Büyük objektif veya professional ekipman kısıtlamaları retro kameralar için genellikle geçerli değildir.")},

    {"title":"Yiyecek Fotoğrafçılığı ve Retro Kamera: Lezzeti Nostaljik Çerçevelemek",
     "tags":"yiyecek fotoğrafçılık, food photography retro, y2k yemek foto, kafe menü foto, retrocameraland",
     "img":"food photography with vintage digital camera, Turkish breakfast spread, warm Y2K tones, grain texture, nostalgic restaurant table, natural light",
     "imgf":"yiyecek-fotografciligi-retro-kamera-lezzeti-nostaljik-cercevelemek.jpg",
     "meta":"Retro kamerayla yiyecek fotoğrafçılığı: yemek ve kafe fotoğraflarında Y2K estetiği, aydınlatma ve kompozisyon rehberi.",
     "type":"technique","args":("Yiyecek Fotoğrafçılığı",
       "Yiyecek fotoğrafçılığı genellikle parlak, steril ve mükemmel görüntüler gerektirir — ama retro kamerayla bunun tam tersi mükemmel sonuç veriyor. Sıcak tonlar, hafif yumuşama ve gürültü efekti yiyeceklere 'ev yapımı' ve 'nostaljik' bir his katıyor.",
       ["Pencere kenarında doğal ışık kullanın — retro kameranın sıcak tonu doğal ışıkta en iyi sonucu verir",
        "Yukarıdan aşağı (90 derece) flat lay çekim: yemek ve aksesuarları masa üzerinde düzenleyin",
        "Flaşı kesinlikle kapatın — yiyecek fotoğraflarında flaş rengi ve dokuyu mahveder",
        "Hafif bulanık arka plan için: yemek nesnesine mümkün olduğunca yaklaşın",
        "Türk kahvaltısı, çay ve Türk kahvesi retro kameradan en iyi çıkan yiyecek içerikleridir"],
       "Kafede retro kamerayla çekim yaparken neye dikkat etmeliyim?",
       "Pencere ışığına en yakın masayı seçin. Kafe gürültülü olsa bile retro kameranın netleme sesi rahatsızlık vermez. Diğer müşterilerin çerçeveye girmemesine dikkat edin.")},

    # ─── YAŞAM TARZI ──────────────────────────────────────────────────────
    {"title":"Retro Kamera ve Üniversite Kampüsü: Mimari ve Günlük Yaşam Belgelemesi",
     "tags":"üniversite kampüsü fotoğraf, kampüs retro kamera, üniversite yaşamı belgeleme, y2k kampüs, retrocameraland",
     "img":"university campus photography vintage digital camera, students on green campus, Y2K aesthetic morning light, architectural details, grain texture",
     "imgf":"retro-kamera-universite-kampusu-mimari-gunluk-yasam-belgelemesi.jpg",
     "meta":"Retro kamerayla üniversite kampüsü fotoğrafçılığı: mimari detaylardan öğrenci hayatına, Y2K estetik kampüs belgelemesi rehberi.",
     "type":"lifestyle","args":("Üniversite Kampüsü",
       "Üniversite kampüsleri, retro dijital kamera için çok katmanlı bir sahne sunar: tarihi mimari, genç kalabalıklar, sezonun renklerini yansıtan ağaçlar ve her köşede birikip akabilecek ışık.",
       [("Sabah Saatleri ve Derslere Akış","Öğrencilerin kampüse girişi, erken saatin sessizliği, çantalar ve bisikletler — retro kameranın anlık çekimi için zengin bir sahne."),
        ("Kampüs Mimarisi","Modern ve tarihi yapıların bir arada bulunduğu kampüslerde kontrast kompozisyonlar arayın. Koridorların uzakta noktaya kadar uzandığı çekimler etkileyicidir."),
        ("Yeşil Alanlar ve Dinlenme Köşeleri","Çimenler üzerinde ders çalışan öğrenciler, piknik bezleri, ağaç gölgeleri — Y2K estetik için klasik kampüs sahneleri.")],
       "Kampüsünüzdeki retro kamera çekimlerini #RetroCamera #CampusLife etiketleriyle paylaşmak, benzer ilgi alanlarındaki öğrencilerle bağlantı kurmanıza yardımcı olacaktır.")},

    {"title":"Retro Kamera ile Sevgililer Günü: Y2K Romantic Fotoğrafçılık Rehberi",
     "tags":"sevgililer günü fotoğraf, valentines retro kamera, çift fotoğrafı, y2k romantik, retrocameraland",
     "img":"Valentine's Day couple photography vintage digital camera, warm romantic tones, red and pink bokeh, Y2K love aesthetic, nostalgic couple photo",
     "imgf":"retro-kamera-sevgililer-gunu-y2k-romantik-fotografcilik-rehberi.jpg",
     "meta":"Sevgililer Günü'nde retro kamerayla romantik fotoğrafçılık: çift fotoğrafları, sahne önerileri ve Y2K estetik sevgi anları.",
     "type":"lifestyle","args":("Sevgililer Günü",
       "Sevgililer Günü fotoğrafları genellikle aşırı retouche edilmiş ve yapay görünür. Retro kameranın gürültüsü, sıcak tonu ve spontane netleme gecikmesi ise aşk anlarını 'tam o an' hissettiren, gerçek ve duygulu kareler üretir.",
       [("Kafe Buluşması","Kahve ve kek önünde karşılıklı oturan çiftin çekimi — pencere ışığı altında flaşsız, doğal poz"),
        ("Şehirde Yürüyüş","Eller tutularak şehir sokaklarında yürüyüş — retro kamerayla arkadan çekim, gölgeler ve uzak perspektif"),
        ("Akşam Yemeği","Mum ışığında masada — retro kameranın düşük ışık renk kayması burada en romantik etkiyi yaratır"),
        ("Ev Fotoğrafı","Evde birlikte yemek yapma, koltukta film izleme — en doğal ve mahrem fotoğraflar")],
       "Retrocameraland'de partnerin için özel bir sevgililer günü hediyesi arayabilirsiniz. Retro kamera, sadece bir nesne değil — birlikte anı biriktirmeye başlamanın anahtarı.")},

    {"title":"Retro Kamera ile Bayram Sabahı: Geleneksel Anları Modern Nostaljiyle Belgelemek",
     "tags":"bayram fotoğrafçılık, retro kamera bayram, aile bayram foto, y2k bayram, türk bayramı fotoğraf, retrocameraland",
     "img":"Turkish Eid morning family gathering photography vintage digital camera, traditional clothes, warm nostalgic tones, Y2K family snapshot, celebration",
     "imgf":"retro-kamera-bayram-sabahi-geleneksel-anlar-modern-nostalji.jpg",
     "meta":"Retro kamerayla bayram fotoğrafçılığı: aile buluşmaları, geleneksel anlar ve Y2K estetik ile bayram sabahı belgelemesi.",
     "type":"lifestyle","args":("Bayram Sabahı",
       "Bayramlar, retro kameranın en değerli anlarını üreteceği bir bağlamdır. Nesiller arası aile buluşması, geleneksel kıyafetler ve bayram sofrasının renkli görüntüsü — bunların hepsi retro kameranın sıcak ve nostaljik tonu ile buluşunca unutulmaz fotoğraflara dönüşür.",
       [("Bayram Sabahı Hazırlığı","Kıyafet giyme, kahvaltı sofrası hazırlığı, çocukların heyecanı — belgelemeye sabah çok erken başlayın"),
        ("Büyüklerin Elini Öpme","Nesiller arası temas anı — retro kamera bu duygu yüklü anı filtre gerekmeden aktarır"),
        ("Bayram Sofrası","Tatlılar, şekerler, çaylar — flat lay ve perspektif çekimler için hazır bir sahne"),
        ("Mahalle Ziyaretleri","Komşuları ve yakınları ziyaret — kapı önleri, bahçeler, sokak buluşmaları")],
       "Bayram fotoğraflarınızı baskıya verin ve albüme ekleyin. Retrocameraland olarak, bu anların fiziksel bir iz bırakmasını destekliyoruz.")},

    {"title":"Retro Kamera ile Instagram Reels: Y2K Estetiğini Video Formatına Taşımak",
     "tags":"instagram reels retro kamera, y2k video estetik, sosyal medya video, reels content, retrocameraland",
     "img":"Instagram Reels content creation vintage digital camera, creator filming, Y2K aesthetic video setup, warm tones, trendy content vibe",
     "imgf":"retro-kamera-instagram-reels-y2k-estetik-video-format.jpg",
     "meta":"Retro kamerayla Instagram Reels: Y2K video estetiği, içerik formatları ve viral Reels için teknikler.",
     "type":"lifestyle","args":("Instagram Reels",
       "Instagram Reels, kısa video formatında Y2K estetiğinin en hızlı büyüyen alanıdır. Retro kameranın video modunda çekilen içerikler, filtreli akıllı telefon videolarından tamamen farklı bir özgünlük katıyor ve algoritmanın 'samimi içerik' tercihiyle örtüşüyor.",
       [("Günlük Vlog Formatı","Sabah rutinini, kahvaltıyı, şehirde yürüyüşü retro kamerayla belgele. Montaj sırasında video klipler arasına flaşlı fotoğraflar ekle."),
        ("'A Day in My Life' Serisi","Tüm günü retro kamerayla çek — 60-90 saniyelik Reels için zengin ham materyal elde edersin"),
        ("Transition Videoları","Kameraya doğru yürüyerek lens üzerini kapatma ve açma efekti — Y2K transition estetik"),
        ("Arkadaş Buluşması Belgeseli","Buluşmadan ayrılışa kadar retro kamerayla çekilen spontane anlar montajlanır")],
       "Retrocameraland'in Instagram hesabını (@retrocameraland) takip ederek Reels içerik üretimi için ilham alın ve topluluğumuza katılın.")},

    {"title":"Retro Kamera Temizliği ve Bakımı: Yıllarca Kullanım için Eksiksiz Rehber",
     "tags":"retro kamera temizlik, kamera bakım rehberi, dijital kamera temizleme, y2k kamera bakım, retrocameraland",
     "img":"digital camera cleaning kit flat lay, lens cleaning cloth microfiber, cotton swabs, lens solution, vintage camera care, warm product photography",
     "imgf":"retro-kamera-temizligi-bakimi-yillarca-kullanim-eksiksiz-rehber.jpg",
     "meta":"Retro kamera temizliği ve bakımı için eksiksiz rehber: lens temizleme, batarya bakımı, nem koruması ve uzun ömür için ipuçları.",
     "type":"technique","args":("Retro Kamera Temizliği ve Bakımı",
       "Retro kameranız değerli bir yatırım ve nostaljik bir nesne. Doğru temizlik ve bakımla, bu kameralar on yıllar boyunca çalışır kalır ve estetik kaliteleri korunur.",
       ["Lensi temizlerken: önce lens blower ile tozu üfleyin, ardından mikrofiber bezle dairesel hareketlerle silin",
        "Asla kağıt mendil veya tişört kullanmayın — bunlar lens camını çizebilir",
        "Batarya bölmesini aylık kontrol edin; korozyon başlamışsa alkollü pamuk çubukla temizleyin",
        "Uzun süreli depolamada bataryaları çıkarın — sızdıran batarya elektronik devreyi mahveder",
        "Silica gel paketli kamera çantası nem kontrolü için en pratik çözümdür",
        "SD kart slotunu düzenli temizleyin — toz okunan/yazılan verileri bozabilir"],
       "Retro kamerayı ıslatırsam ne yapmalıyım?",
       "Hemen kapatın, bataryayı çıkarın ve kamerayı kapalı tutun. 24-48 saat pirinç içinde bekletin (nem çekici etkisi). Sonra yavaşça açıp test edin. Su geçirmez olmayan modellerde bu durum ciddi hasar yaratabilir.")},

    {"title":"Retro Kamera Alırken Dolandırılmama Rehberi: İkinci El Piyasasında Güvenli Satın Alma",
     "tags":"retro kamera satın alma, ikinci el kamera, güvenli kamera alım, dolandırılmama, retrocameraland",
     "img":"second hand digital camera inspection, checking vintage camera at market, Y2K retro camera buying guide, careful examination, product details",
     "imgf":"retro-kamera-alirken-dolandirilmama-ikinci-el-guvenli-satin-alma.jpg",
     "meta":"Retro kamera alırken dolandırılmama rehberi: ikinci el piyasasında nelere dikkat etmeli, nasıl test edilmeli ve güvenli kaynaklardan nasıl alınır?",
     "type":"technique","args":("İkinci El Retro Kamera Satın Alma",
       "İkinci el retro kamera piyasası büyük bir fırsat sunarken dikkatli olmayı da gerektiriyor. Hem gizli arızalar hem de abartılmış değerlendirmeler alıcıları olumsuz etkileyebilir.",
       ["Kamerayı MUTLAKA test edin: fotoğraf çekin, flash'ı test edin, videoya bakın, menüleri gezin",
        "LCD ekranı kontrol edin: sarı lekeler veya dead pixel olmaması gerekir",
        "Lensi iyi ışıkta inceleyin: mantar (küf) büyümesi netlik ve rengi bozar",
        "Batarya kapağı ve SD kart yuvası orijinal ve sızdırmaz olmalı",
        "Fiyatı araştırın: aynı model için birden fazla kaynak fiyatını karşılaştırın",
        "Satın alma kaynağı önemlidir: retrocameraland.com gibi uzmanlaşmış platformlardan alım güvence sunar"],
       "İkinci el kamerada kaç MP yeterlidir?",
       "Y2K estetik için 3-7 MP ideal aralıktır. 2 MP çok düşük çözünürlük olabilirken 8 MP+ zaten modern kamera kalitesine yaklaşır. 3-5 MP tatlı noktayı oluşturmaktadır.")},

    {"title":"Retro Kamera ile Doğum Günü: Sürpriz Partileri Kalıcı Kılmak",
     "tags":"doğum günü retro kamera, sürpriz parti fotoğraf, y2k doğum günü, parti fotoğrafçılık, retrocameraland",
     "img":"birthday party photography vintage digital camera, colorful balloons decorations, Y2K party flash photo, surprise moment, warm nostalgic celebration",
     "imgf":"retro-kamera-dogum-gunu-surpriz-parti-fotografcilik-rehberi.jpg",
     "meta":"Retro kamerayla doğum günü ve sürpriz parti fotoğrafçılığı: Y2K parti estetiği, flaşlı grup çekimleri ve unutulmaz anlar.",
     "type":"lifestyle","args":("Doğum Günü Partisi",
       "Doğum günü partileri, retro kameranın en güçlü performans gösterdiği ortamlardır. Kapalı mekanda flaşlı çekim, balonlar ve kalabalık — bunlar Y2K estetik fotoğrafçılığının temel unsurlarıdır. Akıllı telefon kameralarının 'temiz' görüntüleri yerine, retro kameranın deli enerjisi partinin gerçek ruhunu aktarır.",
       [("Sürpriz Anı","Sürpriz anında kamerayı hazır tutun — netleme ayarlı, flaş açık. Bu an birkaç saniyeden fazla sürmez."),
        ("Doğum Günü Pastası","Mum ışığı + loş ortam + retro kamera = inanılmaz Y2K kare. Pasta kesilmeden önce çekimi yapın."),
        ("Grup Fotoğrafı","Herkesi sıkıştırın, kolları omuzlara koyun — retro kameranın geniş açılı lensi yakın grup çekimlerinde en iyidir"),
        ("Spontane Anlar","Oyunlar, müzik, dans — retro kamerayı hiç kapatmayın, sürekli hazır tutun")],
       "Doğum günü için retrocameraland.com'dan hediye olarak retro kamera almayı düşünebilirsiniz. Bu hem pratik hem de Y2K trendine uygun, özgün bir hediyedir.")},

    {"title":"Retro Kamera ile İstanbul'un Avrupa Yakası: Beşiktaş, Ortaköy ve Arnavutköy",
     "tags":"istanbul avrupa yakası fotoğraf, beşiktaş retro kamera, ortaköy foto, arnavutköy y2k, retrocameraland",
     "img":"Besiktas Ortakoy Istanbul waterfront photography vintage camera, Bosphorus bridge view, colorful buildings, Y2K warm aesthetic, grain texture",
     "imgf":"istanbul-avrupa-yakasi-besiktas-ortakoy-arnavutkoy-retro-kamera.jpg",
     "meta":"İstanbul'un Avrupa yakasında retro kamera: Beşiktaş pazarından Ortaköy camisine, Arnavutköy konaklarına Y2K estetik rehberi.",
     "type":"city_guide","args":("İstanbul Avrupa Yakası",
       [("Beşiktaş Pazarı","Haftasonları kurulan pazar — renk, koku ve doku açısından fotoğrafçı cenneti. Balıkçılar, manav tezgahları ve esnaf çekimleri için hareketli sabah saatleri idealdir."),
        ("Ortaköy Meydanı","Osmanlı barok camisi, dondurma satıcıları, boğaz köprüsü arka planı. Akşam saatlerinde cami aydınlatması ve köprü ışıkları retro kamerada büyülü efektler yaratır."),
        ("Arnavutköy Yalıları","Boğaz kıyısındaki tarihi ahşap yalılar ve Rum mimarisi. Sabah saatlerinde sakin kıyı yürüyüşü ve tarihi yapılarla Y2K dönem fotoğrafları çekilebilir.")],
       [("Cirağan Sarayı önü","Saray duvarları ve Boğaz çerçevesi"),
        ("Kuruçeşme kıyısı","Tekneler ve gece eğlence mekânları"),
        ("Bebek sahili","Kahvaltı ve akşam yürüyüşü sahneleri")],
       "Sonbahar ve ilkbaharda sabah sisinin Boğaz üzerindeki etkisi retro kameranın Y2K tonuyla birleşince sinematik sonuçlar ortaya çıkar.")},

    {"title":"Pinterest için Retro Kamera İçerikleri: Görsel Arama SEO Rehberi",
     "tags":"pinterest retro kamera, pinterest fotoğrafçılık, görsel seo, sosyal medya içerik, retrocameraland",
     "img":"Pinterest board mockup with retro camera photography pins, Y2K aesthetic board, warm tones, vintage photo mood board, social media visual",
     "imgf":"pinterest-retro-kamera-icerikleri-gorsel-arama-seo-rehberi.jpg",
     "meta":"Pinterest için retro kamera içerik stratejisi: görsel SEO, board optimizasyonu ve Y2K estetik pinlerin viral olma rehberi.",
     "type":"lifestyle","args":("Pinterest İçerik Stratejisi",
       "Pinterest, Y2K estetik görsellerinin en hızlı büyüyen platformlarından biridir. Retro kamera fotoğrafları, Pinterest'in görsel arama algoritmasında 'vintage', 'Y2K aesthetic' ve 'retro photography' gibi popüler kategorilerde yüksek görünürlük sağlar.",
       [("Board Oluşturma Stratejisi","'Y2K Kamera Estetiği', 'Retro Fotoğrafçılık Rehberi', 'Türkiye Fotoğraf Rotaları' gibi odaklı board'lar oluşturun. Her board için kapsamlı açıklama ve anahtar kelimeler ekleyin."),
        ("Pin Başlıkları ve Açıklamaları","Her pin için SEO uyumlu başlık yazın. 'Sony Cyber-shot ile Y2K sokak fotoğrafı — İstanbul Balat' gibi spesifik başlıklar görsel aramada öne çıkar."),
        ("Boyut ve Format","Pinterest için ideal görsel boyutu 1000x1500 px (2:3 oran). Retro kamera fotoğraflarınızı bu oranda kırpın."),
        ("Düzenli Pin Zamanlaması","Haftada 5-10 pin hedefleyin. Pinterest algoritması düzenli içerik paylaşımını ödüllendirir.")],
       "Retrocameraland'in Pinterest hesabını takip ederek Y2K estetik ile ilgili güncel içerikleri keşfedebilirsiniz.")},
]

# ─────────────────────────────────────────────────────────────────────────────
# STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def load_published():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()

def save_published(published_set):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(list(published_set)), f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def build_body(topic):
    t = topic["type"]
    a = topic["args"]
    if t == "model_review":
        return body_model_review(*a)
    elif t == "city_guide":
        return body_city_guide(*a)
    elif t == "technique":
        return body_technique(*a)
    elif t == "lifestyle":
        return body_lifestyle(topic["title"], *a)
    return "<p>İçerik hazırlanıyor.</p>"

# ─────────────────────────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────────────────────────

def publish_article_full(title, handle, tags, body_html, meta_desc, img_url):
    full_html = body_html + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    resp = shopify("POST", f"blogs/{BLOG_ID}/articles.json", {
        "article": {
            "title": title, "body_html": full_html,
            "handle": handle, "tags": tags, "published": True,
            **({"image": {"src": img_url, "alt": title}} if img_url else {}),
            "metafields": [
                {"namespace":"seo","key":"description","value":meta_desc,"type":"single_line_text_field"},
                {"namespace":"seo","key":"title","value":title,"type":"single_line_text_field"}
            ]
        }
    })
    art = resp["article"]
    return art["id"], art["handle"]

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    today = __import__("datetime").date.today().isoformat()
    published = load_published()

    # Yayınlanmamış konuları filtrele
    remaining = [t for t in TOPICS if t["title"] not in published]
    if len(remaining) < DAILY_TARGET:
        log(f"Uyarı: Kalan konu sayısı ({len(remaining)}) hedefin ({DAILY_TARGET}) altında. Tümü yayınlanıyor.")

    # --test flag: sadece 1 blog yayınla
    limit = 1 if "--test" in sys.argv else DAILY_TARGET
    batch = remaining[:limit]
    log(f"{today}: {len(batch)} blog yayınlanacak (toplam havuz: {len(TOPICS)}, yayınlanan: {len(published)})")

    results = []
    fal_fail_count = 0

    for i, topic in enumerate(batch, 1):
        log(f"\n[{i}/{len(batch)}] {topic['title'][:55]}...")
        body = build_body(topic)
        handle = make_slug(topic["title"])
        img_url = None

        # Görsel üretimi
        if fal_fail_count < 3:  # art arda 3 hata sonrası görsel denemesini bırak
            try:
                img_url = fal_generate_image(topic["img"])
                fal_fail_count = 0
            except Exception as e:
                fal_fail_count += 1
                log(f"  Görsel hatası ({fal_fail_count}): {e} — görselsiz devam")
                if fal_fail_count == 1:
                    log(f"  Rate limit bekleniyor ({FAL_RETRY_WAIT}s)...")
                    time.sleep(FAL_RETRY_WAIT)
                    try:
                        img_url = fal_generate_image(topic["img"])
                        fal_fail_count = 0
                    except Exception:
                        pass

        # Yayınla
        try:
            aid, ahandle = publish_article_full(
                title=topic["title"],
                handle=handle,
                tags=topic["tags"],
                body_html=body,
                meta_desc=topic["meta"],
                img_url=img_url
            )
            published.add(topic["title"])
            save_published(published)
            results.append({"ok": True, "id": aid, "handle": ahandle, "title": topic["title"],
                            "has_image": img_url is not None})
            log(f"  ✅ ID:{aid} {'📷' if img_url else '(görselsiz)'}")
        except Exception as e:
            log(f"  ❌ Yayın hatası: {e}")
            results.append({"ok": False, "title": topic["title"], "error": str(e)})

        if i < len(batch):
            time.sleep(3)

    # Rapor
    ok = [r for r in results if r["ok"]]
    fail = [r for r in results if not r["ok"]]
    report = [f"# Günlük Blog Raporu — {today}\n",
              f"## Özet: {len(ok)}/{len(results)} başarılı\n",
              "| # | Başlık | ID | Görsel |\n|---|--------|----|--------|\n"]
    for j, r in enumerate(ok, 1):
        report.append(f"| {j} | {r['title'][:50]} | {r['id']} | {'✅' if r['has_image'] else '—'} |\n")
    if fail:
        report.append("\n## Başarısız\n")
        for r in fail:
            report.append(f"- {r['title']}: {r.get('error','?')}\n")
    report.append(f"\n**Toplam yayınlanan:** {len(published)}/{len(TOPICS)} konu tüketildi\n")

    report_path = os.path.join(OUTPUT_DIR, f"{today}_daily-blog-report.md")
    with open(report_path, "w") as f:
        f.writelines(report)
    log(f"\nRapor: {report_path}")

    print("\n" + "="*60)
    print(f"✅ {len(ok)}/{len(results)} blog yayınlandı")
    print(f"{'❌ ' + str(len(fail)) + ' hata' if fail else ''}")
    print("="*60)

if __name__ == "__main__":
    main()
