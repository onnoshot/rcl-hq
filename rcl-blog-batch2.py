#!/usr/bin/env python3
"""Batch 2: Nikon (6) + Casio (8) = 14 ürün"""
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

# ── Nikon Coolpix 885 ────────────────────────────────────────────────────────
{"title":"Nikon Coolpix 885 İncelemesi: Döner Gövde Tasarımı ve Erken Dönem CCD Nostaljisi",
"handle":"nikon-coolpix-885-inceleme-doner-govde-erken-donem-ccd",
"tags":"Nikon, Nikon Coolpix 885, erken dönem dijital kamera, döner gövde, retro kamera, Coolpix serisi",
"meta_desc":"Nikon Coolpix 885 incelemesi: 3.2MP CCD, benzersiz döner gövde ve 2002 dönemi mühendisliği. Dijital fotoğraf tarihinin nadir koleksiyon parçası.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0194_ONN04929.jpg?v=1765241256",
"body":"""
<p>2002 yılında Nikon, kompakt kameranın gövdesini iki parçaya bölerek tüm tasarım kurallarını çiğnedi. <strong>Nikon Coolpix 885</strong>, döner gövdesiyle hem selfie çekimini hem yüksek açı kadrajlamayı olağanüstü kolaylaştıran, döneminin en yaratıcı modellerinden biri.</p>

<h2>Nikon Coolpix 885 Nedir?</h2>
<p>2002 çıkışlı Coolpix 885, 3.2 megapiksel CCD sensör ve Nikon'un karakteristik döner gövde tasarımıyla öne çıkan bir kompakt kameradır. Lens grubu gövdenin üst yarısında, ekran ve kontroller alt yarısında yer alır; ikisi 270 dereceye kadar döner. Bu mekanizma selfie çekimini modern telefon çağından önce mümkün kıldı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 3.2 MP CCD</li>
<li><strong>Lens:</strong> Nikkor 3x optik zoom (38–115mm)</li>
<li><strong>Gövde:</strong> Döner mekanizma (270°)</li>
<li><strong>Ekran:</strong> 1.5" renkli LCD</li>
<li><strong>Hafıza:</strong> CompactFlash kart</li>
<li><strong>Pil:</strong> CR-V3 lityum veya 2x AA</li>
</ul>

<h2>Döner Gövde: Selfie'nin Büyükbabası</h2>
<p>Coolpix 885'in döner sistemi, kullanıcının kendi fotoğrafını çekerken ekranı görebileceği şekilde tasarlanmıştı. Bugün selfie kamera dediğimiz kavramın 2002'deki mekanik versiyonu bu. Bunun yanı sıra zemin seviyesinde veya başın üzerinde yüksek açıdan kadraj kurmak, ekrana bakarak mümkün hale geliyordu.</p>

<h2>Koleksiyon Açısından Önemi</h2>
<p>Coolpix serisi döner gövde tasarımını sadece birkaç yıl sürdürdü. Bu tasarım geçici bir dönem ürünü olduğundan bugün çalışır durumda bulunan örnekler giderek nadir hale geliyor. Mekanizmanın bütünlüğü koleksiyon değerini doğrudan etkiliyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Nikon Coolpix seri koleksiyoncuları</li>
<li>Döner gövdeli kamera tarihi meraklıları</li>
<li>Erken dönem (2000-2003) dijital kamera koleksiyonu kuranlar</li>
<li>Alışılmadık mekanik tasarımları seven koleksiyoncular</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Nikon Coolpix 885'in döner mekanizması bozulur mu?</h3>
<p>Zamanla menteşe gevşeyebilir. Satın almadan önce her iki yönde pürüzsüz döndüğünü test etmek önerilir.</p>
<h3>CompactFlash kart nereden bulunur?</h3>
<p>İkinci el elektronik platformlarında ve bazı fotoğrafçılık dükkanlarında CF kartlar hâlâ satılmaktadır.</p>
<h3>Coolpix 885 hâlâ fotoğraf çekebilir mi?</h3>
<p>Çalışır durumda olanlarda evet. CR-V3 pil veya 2 AA pil ile çalışır; CF kart takıp kullanabilirsiniz.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-885" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix 885'i İncele →</a></div>
"""},

# ── Nikon Coolpix P5100 ──────────────────────────────────────────────────────
{"title":"Nikon Coolpix P5100 İncelemesi: Manuel Kontrol, RAW Desteği ve Prosümer Kompakt",
"handle":"nikon-coolpix-p5100-inceleme-manuel-raw-desteği-prosumer",
"tags":"Nikon, Nikon Coolpix P5100, RAW kamera, prosümer kompakt, retro kamera, manuel kontrol",
"meta_desc":"Nikon Coolpix P5100 incelemesi: 12.1MP CCD, RAW çekim desteği, manuel kontroller. Nikon'un prosümer kompakt kamerasını fotoğrafçı gözüyle inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/snikon1.jpg?v=1757813691",
"body":"""
<p>Kompakt kamerada RAW çekim istemek o dönem lüks sayılırdı. <strong>Nikon Coolpix P5100</strong>, tam da bunu sunan prosümer bir modeli — manuel kontrollerle tam hakimiyet, RAW ile sınırsız post-işleme özgürlüğü.</p>

<h2>Nikon Coolpix P5100 Nedir?</h2>
<p>2007 çıkışlı P5100, Nikon'un Coolpix P serisinin prosümer temsilcisi. 12.1 megapiksel CCD sensör, NRW (Nikon RAW) format desteği, PASM modu ve görüntü sabitleyiciyle hem hobi fotoğrafçılarına hem de CCD döneminin RAW kalitesini yaşamak isteyenlere hitap ediyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD (1/1.72" — büyük sensör)</li>
<li><strong>Format:</strong> NRW RAW + JPEG</li>
<li><strong>Lens:</strong> Nikkor 3.5x optik zoom (28–99mm)</li>
<li><strong>Modlar:</strong> P / S / A / M (tam manuel)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>ISO:</strong> 64–3200</li>
<li><strong>Stabilizasyon:</strong> VR (Vibration Reduction) optik</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>RAW Çekim: Neden Oyunu Değiştirir?</h2>
<p>JPEG, kamera içinde işlenmiş ve sıkıştırılmış bir görüntüdür. RAW ise sensörün ham verisi — post-işlemede pozlamayı, rengi, gölgeleri ve açıkları çok daha geniş aralıkta düzeltebilirsiniz. P5100'ün NRW dosyaları modern Lightroom ve Capture One'da açılır.</p>

<h2>1/1.72" Büyük CCD Sensör</h2>
<p>P5100'ün en kritik teknik avantajı sensör boyutu. 1/1.72" CCD, tipik kompakt kameraların 1/2.5" sensöründen belirgin biçimde büyük — bu düşük ışıkta daha az gürültü, daha geniş dinamik aralık demek.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>CCD döneminde RAW çekim yapmak isteyenler</li>
<li>Manuel kontrollü kompakt kamera arayanlar</li>
<li>Nikon P serisi koleksiyoncuları</li>
<li>Post-işleme kontrolü önemseyen retro fotoğrafçılar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Nikon NRW formatı Lightroom'da açılır mı?</h3>
<p>Evet, Adobe Lightroom Classic ve CC, Nikon NRW formatını tam destekler. Capture One ve diğer RAW işleyiciler de uyumludur.</p>
<h3>P5100 DSLR kalitesi verir mi?</h3>
<p>DSLR ile kıyaslanamaz ama kompakt sınıfının üzerinde bir görüntü kalitesi sunar. Büyük CCD sensörü ve RAW desteği bu farkı yaratıyor.</p>
<h3>P5100 pili nerede?</h3>
<p>EN-EL5 Li-ion pil kullanır. Hâlâ üretilen ve üçüncü parti alternatifleri bulunan geniş uyumlu bir pil.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-p5100" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix P5100'ü İncele →</a></div>
"""},

# ── Nikon Coolpix S100 ───────────────────────────────────────────────────────
{"title":"Nikon Coolpix S100 İncelemesi: GPS, Wi-Fi ve 16MP ile Modern Özellikler Kompakt Gövdede",
"handle":"nikon-coolpix-s100-inceleme-gps-wifi-16mp-kompakt",
"tags":"Nikon, Nikon Coolpix S100, GPS kamera, Wi-Fi kamera, retro kamera, Coolpix S serisi",
"meta_desc":"Nikon Coolpix S100 incelemesi: 16MP CMOS, dahili GPS, Wi-Fi ve Full HD video. Nikon'un akıllı özelliklerle donattığı premium kompakt kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0000_GenerativeFill5.jpg?v=1758553917",
"body":"""
<p>Akıllı telefon çağından önce, fotoğraflarınızın nerede çekildiğini hatırlamak için not tutmanız gerekiyordu. <strong>Nikon Coolpix S100</strong> bu sorunu kendi içinde çözdü: dahili GPS, çekilen her fotoğrafa koordinat bilgisi ekliyor.</p>

<h2>Nikon Coolpix S100 Nedir?</h2>
<p>2011 çıkışlı S100, Nikon'un S serisinin teknoloji meraklılarına yönelik premium modeli. 16 megapiksel CMOS sensör, dahili GPS, Wi-Fi bağlantısı ve 5x optik zoom ile döneminin en kapsamlı özellik setlerinden birini sunuyordu.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 16 MP CMOS</li>
<li><strong>Optik Zoom:</strong> 5x (28–140mm)</li>
<li><strong>GPS:</strong> Dahili, her fotoğrafa koordinat kaydeder</li>
<li><strong>Wi-Fi:</strong> Dahili, kablosuz veri aktarımı</li>
<li><strong>Ekran:</strong> 3.5" dokunmatik OLED</li>
<li><strong>Video:</strong> Full HD 1080/30p</li>
<li><strong>Stabilizasyon:</strong> VR optik</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
</ul>

<h2>GPS ile Coğrafi Etiketleme</h2>
<p>S100'ün GPS sistemi, fotoğraf çekildiği anda enlem ve boylamı kaydeder. Google Haritalar, Lightroom veya iOS/Android Fotoğraflar uygulamasında bu koordinatlar üzerinden fotoğrafları haritada görüntüleyebilirsiniz. Seyahat günlükleriniz artık tam otomatik.</p>

<h2>3.5" OLED Dokunmatik Ekran</h2>
<p>Kompakt kamerada 3.5 inç OLED son derece nadirdi. OLED'in siyah derinliği ve renk canlılığı, parlak güneş altında bile ekranı okunabilir kılıyor; bu durum kadraj kurmayı çok kolaylaştırıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğraflarını konumla etiketlemek isteyenler</li>
<li>GPS özellikli kompakt kamera koleksiyoncuları</li>
<li>Wi-Fi bağlantılı retro kamera arayanlar</li>
<li>Nikon S serisi teknoloji meraklıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>S100'ün GPS'i ne kadar süre alır?</h3>
<p>İlk konum tespiti 30–90 saniye sürebilir. Sonraki çekimlerde daha hızlı güncellenir. GPS açık kaldığında pil tüketimi artar.</p>
<h3>Nikon S100 Wi-Fi nasıl kullanılır?</h3>
<p>Nikon Transfer uygulaması ile aynı Wi-Fi ağındaki bilgisayara doğrudan gönderir. Telefona aktarım için ek uygulama gerekebilir.</p>
<h3>S100 için yedek pil var mı?</h3>
<p>EN-EL12 Li-ion pil kullanır. Bu model birçok Nikon kompakt kamerayla ortak olduğundan kolayca temin edilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-s100" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix S100'ü İncele →</a></div>
"""},

# ── Nikon Coolpix S3100 ──────────────────────────────────────────────────────
{"title":"Nikon Coolpix S3100 İncelemesi: Renkli Gövde, Basit Arayüz ve CCD Retro Tonu",
"handle":"nikon-coolpix-s3100-inceleme-renkli-govde-ccd-retro-tonu",
"tags":"Nikon, Nikon Coolpix S3100, retro kamera, y2k kamera, Coolpix S serisi, renkli kamera",
"meta_desc":"Nikon Coolpix S3100 incelemesi: 14MP CCD, 5x zoom ve renkli şık gövde. Günlük kullanım ve retro estetik için ideal başlangıç kamerası.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-1_0012_ONN03039.jpg?v=1757546058",
"body":"""
<p>Nikon'un S3100'ü, karmaşık menüler ve teknik ayarlar olmadan iyi fotoğraf çekmek isteyenler için tasarlandı. Sade ve erişilebilir, ama CCD görüntü kalitesinden ödün vermiyor.</p>

<h2>Nikon Coolpix S3100 Nedir?</h2>
<p>2011 çıkışlı S3100, 14 megapiksel CCD sensör ve 5x optik zoom ile giriş seviyesi kompakt kamera segmentini hedefleyen Nikon modelidir. Renkli gövde seçenekleri ve dokunmatik arayüzüyle genç kullanıcılara ve ailelere yönelik tasarlanmış.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 14 MP CCD</li>
<li><strong>Optik Zoom:</strong> 5x (26–130mm)</li>
<li><strong>Ekran:</strong> 2.7" dokunmatik LCD</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Sahne Modları:</strong> Easy Auto + 16 sahne modu</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
<li><strong>Pil:</strong> EN-EL19 Li-ion</li>
</ul>

<h2>Easy Auto Modu: Kamera Kendi Seçiyor</h2>
<p>S3100'ün Easy Auto modu, sahneyi analiz ederek otomatik olarak en uygun ayarı seçiyor. Gündüz mü, gece mi, portre mi, manzara mı — kamera karar veriyor, siz sadece basıyorsunuz. Bu özellik kamerayı özellikle aileler ve başlangıç kullanıcıları için erişilebilir kılıyor.</p>

<h2>CCD Tonu ile Aile Fotoğrafları</h2>
<p>S3100'ün CCD sensörü, cilt tonlarını özellikle başarılı işliyor. Sıcak, yumuşak ve doğal — filtre uygulamadan bile "vintage albüm" hissini veren fotoğraflar üretiyor. Aile fotoğraflarında bu etki çok değerli.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>İlk retro kompaktını arayan başlangıç kullanıcıları</li>
<li>Aile fotoğrafları için sade kamera arayanlar</li>
<li>Renkli ve şık gövde tercih edenler</li>
<li>Nikon S serisi koleksiyonu tamamlamak isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>S3100 kaç yıl kullanılabilir?</h3>
<p>CCD sensör ve mekanik kısımlar dayanıklıdır. Çalışır durumda olanlar on yıl ve daha uzun kullanılabilir.</p>
<h3>Nikon Coolpix S3100 hangi pil?</h3>
<p>EN-EL19 Li-ion pil. Birçok Nikon kompakt modelle ortak, kolayca bulunabilir.</p>
<h3>5x zoom yeterli mi?</h3>
<p>Günlük fotoğrafçılık için yeterli. Spor veya uzak mesafe çekimleri için daha yüksek zoom tercih edilebilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-s3200" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix S3100'ü İncele →</a></div>
"""},

# ── Nikon Coolpix S9 ─────────────────────────────────────────────────────────
{"title":"Nikon Coolpix S9 İncelemesi: 2005'in Ultra İnce Nikon Kompaktı ve CCD Karakteri",
"handle":"nikon-coolpix-s9-inceleme-2005-ultra-ince-ccd-karakter",
"tags":"Nikon, Nikon Coolpix S9, ultra ince kamera, retro kamera, 2005 kamera, Coolpix S serisi",
"meta_desc":"Nikon Coolpix S9 incelemesi: 6MP CCD ve ultra ince metal gövde. 2005'in en şık Nikon kompaktını ve koleksiyon değerini detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0050_ONN00494_6563fee0-673a-4096-b6d0-6d23b16affca.jpg?v=1750452421",
"body":"""
<p>2005 yılında Nikon, ultra ince kompakt yarışına S9 ile katıldı. Metal gövde, premium his ve CCD görüntü kalitesiyle bu model o dönemin en çok konuşulan Nikon kompaktlarından biriydi.</p>

<h2>Nikon Coolpix S9 Nedir?</h2>
<p>2005 çıkışlı Coolpix S9, 6 megapiksel CCD sensör ve Nikkor 3x optik zoom ile ince alüminyum gövdede şıklık ve performansı bir araya getiren bir kompakt kameradır. S serisiyle Nikon, "şık ve ince" kategorisine ciddi bir giriş yaptı.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 6 MP CCD</li>
<li><strong>Lens:</strong> Nikkor 3x optik zoom (35–105mm)</li>
<li><strong>Ekran:</strong> 2.5" LCD</li>
<li><strong>Gövde:</strong> İnce alüminyum</li>
<li><strong>Hafıza:</strong> SD kart</li>
<li><strong>Pil:</strong> EN-EL8 Li-ion</li>
</ul>

<h2>2005'te "Ultra İnce" Ne Anlama Geliyordu?</h2>
<p>Bugün her telefon ultra ince. Ama 2005'te metalden bu kadar ince bir kamera üretmek ciddi mühendislik gerektiriyordu. S9'un kalınlığı yaklaşık 18mm — bu, döneminin rekabetçi modellerinden belirgin şekilde daha ince. Bu inceliği metal gövdeyle elde etmek ise ayrıca değer katıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>2005 dönemi ultra ince Nikon koleksiyoncuları</li>
<li>Metal gövdeli, premium hissiyatlı retro kamera arayanlar</li>
<li>Y2K estetik koleksiyonuna şık model eklemek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Nikon Coolpix S9 hangi pil kullanır?</h3>
<p>EN-EL8 Li-ion pil. Bazı üçüncü parti alternatifleri mevcuttur ancak orijinal pilin performansı en iyi sonucu verir.</p>
<h3>S9'da SD kart boyutu ne olmalı?</h3>
<p>2 GB SD kart ideal. Daha büyük kapasiteli kartlarda uyumsuzluk yaşanabilir.</p>
<h3>Coolpix S9 ile gece fotoğrafı nasıl?</h3>
<p>Gece Sahne modunda sabit yüzeyle iyi sonuçlar verir. El titrediğinde CCD greni belirginleşir — retro estetik için bu beklenen bir sonuç.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-s9" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix S9'u İncele →</a></div>
"""},

# ── Nikon Coolpix S4000 ──────────────────────────────────────────────────────
{"title":"Nikon Coolpix S4000 İncelemesi: Dokunmatik Ekran, 12MP CCD ve Şık Kompakt Tasarım",
"handle":"nikon-coolpix-s4000-inceleme-dokunmatik-12mp-ccd-kompakt",
"tags":"Nikon, Nikon Coolpix S4000, dokunmatik kamera, retro kamera, 12MP CCD, Coolpix S serisi",
"meta_desc":"Nikon Coolpix S4000 incelemesi: 12MP CCD, dokunmatik ekran ve şık ince gövde. Nikon'un kullanıcı dostu kompakt kamerasını detaylıca inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0013_ONN00336.jpg?v=1774655364",
"body":"""
<p>Nikon S4000, dokunmatik ekranı kamerayla barıştıran modellerden biri. Sade menüsü, şık tasarımı ve 12MP CCD'siyle Y2K koleksiyonunun pratik ve estetik bir üyesi.</p>

<h2>Nikon Coolpix S4000 Nedir?</h2>
<p>2010 çıkışlı S4000, 12 megapiksel CCD sensör ve dokunmatik 3 inç LCD ekranla kullanıcı deneyimini basitleştirmeye odaklanmış bir kompakt kamera. İnce gövdesi ve çoklu renk seçenekleriyle geniş bir kitleye hitap etmek için tasarlanmış.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12 MP CCD</li>
<li><strong>Optik Zoom:</strong> 4x (27–108mm)</li>
<li><strong>Ekran:</strong> 3.0" dokunmatik LCD</li>
<li><strong>Efektler:</strong> 13 in-camera filtre efekti</li>
<li><strong>Sahne Modları:</strong> 16 farklı sahne modu</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>13 Kamera İçi Filtre: Lightroom Öncesi Dönem</h2>
<p>S4000'in kamera içi filtre efektleri, Instagram ve Lightroom preset'leri popüler olmadan önce fotoğraflara stil katmanın yoluydu. Çoğu zaman bu filtreler bugünün vintage preset'lerini andırıyor — CCD sensör zaten doğal bir filtre görevi gördüğünden sonuçlar beklenmedik kadar iyi.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Dokunmatik arayüzlü sade kamera arayanlar</li>
<li>12MP CCD retro tonu seven içerik üreticileri</li>
<li>Nikon S serisi koleksiyoncuları</li>
<li>İlk retro kamerasını arayan başlangıç kullanıcıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>S4000 CCD mi CMOS mu?</h3>
<p>CCD sensör kullanır. Bu, o dönem kompakt Nikon modellerinin büyük çoğunluğu için geçerli.</p>
<h3>Dokunmatik ekran hassas mi?</h3>
<p>Rezistif dokunmatik teknoloji; kapasitif ekranlardan daha az hassas ama kullanımına alıştıktan sonra işlevsel.</p>
<h3>S4000 pili nerede bulunur?</h3>
<p>EN-EL19 Li-ion pil — birçok Nikon modelle ortak, kolayca temin edilebilir.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/nikon-coolpix-s4000" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix S4000'i İncele →</a></div>
"""},

# ── Casio Exilim EX-Z85 ──────────────────────────────────────────────────────
{"title":"Casio Exilim EX-Z85 İncelemesi: İnce Gövde, CCD ve Casio'nun Güvenilir Kompaktı",
"handle":"casio-exilim-ex-z85-inceleme-ince-govde-ccd-kompakt",
"tags":"Casio, Casio Exilim EX-Z85, Casio Exilim, retro kamera, y2k kamera, CCD kompakt",
"meta_desc":"Casio Exilim EX-Z85 incelemesi: 12.1MP CCD, ince alüminyum gövde ve pratik kullanım. Casio'nun güvenilir Z serisi kompaktını detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a-1_0005_ONN06262.jpg?v=1765745832",
"body":"""
<p>Casio'nun Exilim Z serisi, on yıl boyunca "ince, hafif ve güvenilir kompakt" tarifini karşıladı. <strong>Casio Exilim EX-Z85</strong>, bu serinin kalitesini 12MP CCD'de sunuyor.</p>

<h2>Casio Exilim EX-Z85 Nedir?</h2>
<p>2009-2010 yılları arasında üretilen EX-Z85, 12.1 megapiksel CCD sensör, 3x optik zoom ve ince alüminyum gövdesiyle günlük kompakt kamera standartlarını karşılayan sağlam bir Casio modelidir.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD</li>
<li><strong>Optik Zoom:</strong> 3x (35–105mm)</li>
<li><strong>Ekran:</strong> 2.6" LCD</li>
<li><strong>ISO:</strong> 64–1600</li>
<li><strong>Video:</strong> 640×480 VGA</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
<li><strong>Pil:</strong> NP-80 Li-ion (Casio ortak pil)</li>
</ul>

<h2>Casio CCD: Exilim Serisinin Renk Kimliği</h2>
<p>Casio'nun Exilim kameraları, CCD döneminde sıcak ve biraz doygun bir renk karakteri üretiyordu. Bu renk kimliği bugün sosyal medyada "Casio look" olarak biliniyor. Z85, bu karakteri 12MP çözünürlükte sunuyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Casio Exilim Z serisi koleksiyoncuları</li>
<li>"Casio look" CCD tonu arayanlar</li>
<li>Günlük kullanım için güvenilir kompakt isteyenler</li>
<li>Bütçe dostu retro CCD kamera arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Casio EX-Z85 hangi kart kullanır?</h3>
<p>SD ve SDHC kart uyumludur. 4-8 GB yeterli kapasiteyi karşılar.</p>
<h3>NP-80 pil nereden bulunur?</h3>
<p>Casio'nun ortak pil modeli; üçüncü parti alternatifleri kolayca temin edilebilir.</p>
<h3>EX-Z85 ile makro çekim yapılır mı?</h3>
<p>Evet, yaklaşık 10 cm'ye kadar makro modu mevcuttur.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-z85" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio Exilim EX-Z85'i İncele →</a></div>
"""},

# ── Casio Exilim EX-Z4 ───────────────────────────────────────────────────────
{"title":"Casio Exilim EX-Z4 İncelemesi: Nano Boyut, Büyük CCD Karakter",
"handle":"casio-exilim-ex-z4-inceleme-nano-boyut-ccd-karakter",
"tags":"Casio, Casio Exilim EX-Z4, mini kamera, retro kamera, y2k kamera, Casio Exilim Z serisi",
"meta_desc":"Casio Exilim EX-Z4 incelemesi: Ultra kompakt boyut ve CCD görüntü kalitesi. Cebe sığan retro kamerayı ve koleksiyon değerini inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0009_ONN05114.jpg?v=1765237507",
"body":"""
<p>Bazı kameralar var, boyutlarını görünce "bu kadar küçüğe nasıl sığdırdılar?" dedirtir. <strong>Casio Exilim EX-Z4</strong>, Exilim serisinin nano boyutlu, ceplerden çıkmayan modeli.</p>

<h2>Casio Exilim EX-Z4 Nedir?</h2>
<p>Ultra kompakt Exilim Z serisi içinde EX-Z4, minimum boyutu maksimum taşınabilirlikle buluşturan bir modeldir. CCD sensörü, pratik zoom aralığı ve Casio'nun sağlam yapısıyla günlük taşıma için ideal.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> CCD</li>
<li><strong>Form:</strong> Ultra kompakt — kredi kartı boyutuna yakın</li>
<li><strong>Optik Zoom:</strong> 3x</li>
<li><strong>Ekran:</strong> LCD</li>
<li><strong>Hafıza:</strong> SD kart</li>
</ul>

<h2>Neden Bu Kadar Küçük?</h2>
<p>Casio, Exilim serisinde optik tasarımında ince profilli lens sistemi kullanarak gövdeyi olağanüstü küçültebildi. Sonuç: cebin arka bölmesine sığan, ağırlığı hissedilmeyen bir kamera. Bu boyut bugün "nano digicam" koleksiyonunun olmazsa olmazı.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>En küçük retro dijital kamerayı arayan koleksiyoncular</li>
<li>Casio Exilim nano serisi tamamcıları</li>
<li>Günlük taşıma için gizli kamera arayanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>EX-Z4 çektiği fotoğraflar ne boyut?</h3>
<p>CCD çözünürlüğüne bağlı olarak sosyal medya paylaşımı için yeterli. Büyük baskı beklentisi olmamalı.</p>
<h3>Casio Exilim Z4 pili hâlâ bulunuyor mu?</h3>
<p>Casio NP serisi piller üçüncü parti olarak temin edilebiliyor.</p>
<h3>Bu kamera koleksiyon mu, kullanım mı amaçlı?</h3>
<p>Her ikisi de. Çalışır durumdaki örnekler rahatlıkla çekim yapabilir; aynı zamanda minyatür boyutuyla koleksiyonun en dikkat çekici parçaları arasında.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-z4" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio Exilim EX-Z4'ü İncele →</a></div>
"""},

# ── Casio Exilim EX-Z110 ─────────────────────────────────────────────────────
{"title":"Casio Exilim EX-Z110 İncelemesi: Geniş Açı, CCD ve Casio'nun Seyahat Kompaktı",
"handle":"casio-exilim-ex-z110-inceleme-genis-aci-ccd-seyahat",
"tags":"Casio, Casio Exilim EX-Z110, geniş açı kamera, retro kamera, seyahat kamerası, Casio Exilim",
"meta_desc":"Casio Exilim EX-Z110 incelemesi: 12.1MP CCD ve 26mm geniş açı başlangıç. Seyahat ve günlük kullanım için ideal Casio kompakt kamerasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0102_ONN05021.jpg?v=1765239294",
"body":"""
<p>26mm geniş açı, dar sokaklarda, geniş iç mekânlarda ve grup fotoğraflarında oyunu değiştiriyor. <strong>Casio Exilim EX-Z110</strong>, bu avantajı CCD görüntü kalitesiyle birleştiriyor.</p>

<h2>Casio Exilim EX-Z110 Nedir?</h2>
<p>EX-Z110, 12.1 megapiksel CCD sensör ve 26mm'den başlayan geniş açı lensiyle seyahat ve günlük kullanım için optimize edilmiş bir Casio kompakt kameradır. Geniş açı başlangıcı Z serisinin standart 35mm'sinden belirgin biçimde daha geniş.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD</li>
<li><strong>Lens:</strong> 4x optik zoom, 26–104mm (geniş açı!)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>ISO:</strong> 64–1600</li>
<li><strong>Video:</strong> 640×480 VGA</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>26mm Geniş Açı: Seyahatin Gizli Silahı</h2>
<p>Dar bir cadde, büyük bir katedrali, geniş bir meydan — 26mm tüm bunları tek karede toplar. 35mm başlangıçlı kompaktlardan belirgin ölçüde daha geniş perspektif sunan bu lens, seyahat fotoğrafçılığında "bir adım geri çekilme" ihtiyacını ortadan kaldırıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Seyahat fotoğrafçılığı için geniş açılı retro kompakt arayanlar</li>
<li>Casio Exilim Z serisi koleksiyoncuları</li>
<li>Mimari ve manzara çekimi için CCD kompakt isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>26mm geniş açı neden önemli?</h3>
<p>Dar mekânlarda, dar sokaklarda ve grup çekimlerinde geniş açı, geriye adım atmanıza gerek kalmadan daha fazla sahneyi çerçevelemenizi sağlar. Özellikle şehir seyahatlerinde büyük avantaj.</p>
<h3>Z110 SD kart mı kullanır?</h3>
<p>Evet, SD ve SDHC kart uyumludur.</p>
<h3>Casio EX-Z110'un pili hangisi?</h3>
<p>NP-80 Li-ion — Casio'nun geniş uyumlu pil modeli.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-z110" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio Exilim EX-Z110'u İncele →</a></div>
"""},

# ── Casio Exilim EX-H10 ──────────────────────────────────────────────────────
{"title":"Casio Exilim EX-H10 İncelemesi: 10x Süper Zoom, Uzun Pil Ömrü ve CCD Güç",
"handle":"casio-exilim-ex-h10-inceleme-10x-super-zoom-uzun-pil",
"tags":"Casio, Casio Exilim EX-H10, süper zoom kamera, retro kamera, uzun pil ömrü, Casio H serisi",
"meta_desc":"Casio Exilim EX-H10 incelemesi: 12.1MP CCD, 10x optik zoom ve 1000+ kare pil ömrü. Casio'nun süper zoom kampiyonu hakkında her şey.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/0004_Generative_Fill_3.jpg?v=1759848327",
"body":"""
<p>1000'den fazla kare — tek şarjla. <strong>Casio Exilim EX-H10</strong>, dönemindeki kompakt kameraların pil ömrü rekorunu kırdı ve bunu 10x optik zoom ile birleştirdi.</p>

<h2>Casio Exilim EX-H10 Nedir?</h2>
<p>2009 çıkışlı EX-H10, Casio'nun H serisi içinde pil verimliliği ve zoom kapasitesini birleştiren modelidir. 12.1 megapiksel CCD, 10x optik zoom ve Casio'nun özel pil tasarımıyla tek şarjda 1000+ kare çekim iddiasıyla piyasaya girdi.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 12.1 MP CCD</li>
<li><strong>Optik Zoom:</strong> 10x (24–240mm)</li>
<li><strong>Pil Ömrü:</strong> ~1000 kare (CIPA standardı)</li>
<li><strong>Ekran:</strong> 3.0" LCD</li>
<li><strong>Stabilizasyon:</strong> Anti-shake optik</li>
<li><strong>ISO:</strong> 64–3200</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC</li>
</ul>

<h2>1000 Kare: Seyahatte Ne Anlama Geliyor?</h2>
<p>Ortalama bir turistin günlük çekimi 200-300 kare. EX-H10 tek şarjla 3-5 günlük seyahati rahatlıkla karşılıyor. Yedek pil, şarj cihazı, güç bankası — bunların hiçbirine ihtiyaç duymadan. Uzun yürüyüşlerde, kampüs turlarında, günlük şehir gezmelerinde pil endişesi yaşanmıyor.</p>

<h2>24mm Geniş Açı + 10x Zoom</h2>
<p>24mm'den başlayıp 240mm'ye uzanan bu lens aralığı, pratik olarak her sahneyi kapsıyor. Manzara genişliğinden telefoto detayına tek kamerayla geçiş yapabiliyorsunuz.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Uzun seyahat ve trekking için pil dayanımı öncelikli kamera arayanlar</li>
<li>Süper zoom + CCD kalitesi kombinasyonu isteyenler</li>
<li>Casio H serisi koleksiyoncuları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>EX-H10'un 1000 kare iddiası gerçek mi?</h3>
<p>CIPA standardı testlerde doğrulanmış. Gerçek kullanımda flash sıklığına ve LCD parlaklığına bağlı olarak 700-900 kare arasında değişebilir.</p>
<h3>10x zoom ile görüntü titremesi olur mu?</h3>
<p>Optik anti-shake sistemi titreşimi önemli ölçüde azaltır. 10x üzerinde sabit bir yüzey önerilir.</p>
<h3>EX-H10 hâlâ satın alınmaya değer mi?</h3>
<p>Pil ömrü ve zoom kapasitesi açısından bugün bile pratik kullanım için değerli. CCD tonu arayanlar için de özellikli bir seçim.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-h10" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio Exilim EX-H10'u İncele →</a></div>
"""},

# ── Casio Exilim EX-Z50 ──────────────────────────────────────────────────────
{"title":"Casio Exilim EX-Z50 İncelemesi: 2005'in Ultra İnce Casio Kompaktı ve CCD Altın Çağı",
"handle":"casio-exilim-ex-z50-inceleme-2005-ultra-ince-ccd-altin-cag",
"tags":"Casio, Casio Exilim EX-Z50, ultra ince kamera, retro kamera, 2005 kamera, CCD altın çağı",
"meta_desc":"Casio Exilim EX-Z50 incelemesi: 5MP CCD ve 2005'in ultra ince Casio şıklığı. CCD altın çağının parlayan yıldızı olan bu modeli detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-2_0165_ONN01282.jpg?v=1758546375",
"body":"""
<p>2005'te Casio, kamerayı neredeyse kredi kartı kalınlığına indirdi. <strong>Casio Exilim EX-Z50</strong>, CCD'nin altın çağında ince tasarımın zirvelerinden biri.</p>

<h2>Casio Exilim EX-Z50 Nedir?</h2>
<p>2005 çıkışlı EX-Z50, 5 megapiksel CCD ve Casio'nun karakteristik ultra ince alüminyum gövdesiyle Z serisinin CCD altın çağı içindeki en rafine modellerinden biri. Döneminin en ince kompakt kameraları arasında gösterilen Z50, bugün koleksiyon değeri bakımından öne çıkıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 5 MP CCD</li>
<li><strong>Optik Zoom:</strong> 3x (35–105mm)</li>
<li><strong>Ekran:</strong> 2.0" LCD</li>
<li><strong>Gövde Kalınlığı:</strong> ~17mm (ultra ince)</li>
<li><strong>Gövde:</strong> Alüminyum</li>
<li><strong>Hafıza:</strong> SD kart</li>
</ul>

<h2>CCD Altın Çağında EX-Z50'nin Yeri</h2>
<p>2003-2007 arası, CCD sensörlü kompakt kameraların en olgun dönemiydi. İşlemci gücü yeterliydi, sensör kalitesi zirvedeydi, gövde tasarımları rafine bir noktaya ulaşmıştı. EX-Z50, bu dönemin en başarılı örneklerinden biri olarak koleksiyonlarda onurlu bir yer alıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>CCD altın çağı koleksiyonu kuranlar</li>
<li>Ultra ince 2005 dönemi Casio arayanlar</li>
<li>5MP CCD'nin özgün renk tonunu deneyimlemek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>EX-Z50 ile iyi fotoğraf çekilir mi?</h3>
<p>5MP, sosyal medya ve küçük baskılar için yeterli. CCD'nin sıcak tonu fotoğraflara özgün bir karakter katiyor.</p>
<h3>Pil durumu nasıl?</h3>
<p>NP-20 Li-ion pil; ikinci el platformlardan veya üçüncü parti olarak temin edilebilir.</p>
<h3>Koleksiyon değeri artıyor mu?</h3>
<p>İnce metal gövdeli 2005 dönemi Casio modelleri giderek nadir bulunan koleksiyon parçaları haline geliyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-z50" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio Exilim EX-Z50'yi İncele →</a></div>
"""},

# ── Casio Exilim EX-N10 Gold ─────────────────────────────────────────────────
{"title":"Casio Exilim EX-N10 Gold Edition İncelemesi: Altın Renk ve Lüks Y2K Estetiği",
"handle":"casio-exilim-ex-n10-gold-inceleme-altin-renk-lux-y2k",
"tags":"Casio, Casio Exilim EX-N10, altın renk kamera, Gold Edition, lüks kamera, retro kamera koleksiyon",
"meta_desc":"Casio Exilim EX-N10 Gold Edition incelemesi: Altın renkli şık gövde ve CCD görüntü kalitesi. Y2K estetik koleksiyonunun en lüks parçasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Untitled-1_0009_ONN03042s.jpg?v=1757546603",
"body":"""
<p>Koleksiyonunuza altın rengi katmak istiyorsanız, tek seçenek yok. Ama <strong>Casio Exilim EX-N10 Gold Edition</strong>, bu rengi hem estetik hem karakter olarak taşıyan özel bir model.</p>

<h2>Casio Exilim EX-N10 Gold Edition Nedir?</h2>
<p>EX-N10'un Gold Edition versiyonu, Casio'nun sınırlı renk seçeneğiyle sunduğu lüks görünümlü bir kompakt kameradır. CCD sensörü, ince gövdesi ve altın rengiyle Y2K koleksiyonlarında göz alıcı bir yer alıyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Renk:</strong> Gold Edition (sınırlı seri)</li>
<li><strong>Sensör:</strong> CCD</li>
<li><strong>Gövde:</strong> İnce alüminyum, altın kaplama finish</li>
<li><strong>Zoom:</strong> Optik zoom</li>
<li><strong>Hafıza:</strong> SD kart</li>
</ul>

<h2>Altın Renk ve Koleksiyon Önemi</h2>
<p>Kamera dünyasında altın veya champagne renk varyantları her zaman sınırlı üretildi. Bu sınırlılık zamanla koleksiyon değerini artırıyor. EX-N10 Gold, standart siyah veya gümüş versiyonlara kıyasla çok daha az örnekle piyasaya çıktı — bu da onu nadir bir koleksiyon parçası yapıyor.</p>

<h2>Y2K Altın Estetik</h2>
<p>Y2K döneminin renk estetiğinde altın, gümüş ve şampanya tonları önemli bir yer tutuyordu. EX-N10 Gold bu estetiği mükemmel biçimde temsil ediyor — rafta durduğunda koleksiyonun odak noktası haline geliyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Altın veya lüks görünümlü kamera koleksiyoncuları</li>
<li>Y2K altın-gümüş renk estetiği arayanlar</li>
<li>Casio Exilim nadir renk varyantı tamamcıları</li>
<li>Koleksiyona göz alıcı bir parça eklemek isteyenler</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Gold Edition standart versiyondan teknik olarak farklı mı?</h3>
<p>Yalnızca renk ve finish farklı; teknik özellikler standarttır. Koleksiyon değeri renk nadirliğinden kaynaklanıyor.</p>
<h3>Altın kaplama zamanla solar mı?</h3>
<p>Doğal kullanımda minimal solma olabilir. İyi saklanan örnekler orijinal parlaklığını korur.</p>
<h3>Casio EX-N10 pili?</h3>
<p>NP-80 Li-ion pil — Casio'nun en yaygın kullanılan pil modeli.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-n10-gold" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio EX-N10 Gold'u İncele →</a></div>
"""},

# ── Casio QV-R300 ────────────────────────────────────────────────────────────
{"title":"Casio QV-R300 İncelemesi: Erken Dönem Casio CCD ve Dijital Fotoğraf Tarihinden Bir Sayfa",
"handle":"casio-qv-r300-inceleme-erken-donem-casio-ccd-tarih",
"tags":"Casio, Casio QV-R300, Casio QV serisi, erken dönem dijital kamera, retro kamera koleksiyon, CCD kamera",
"meta_desc":"Casio QV-R300 incelemesi: Casio'nun erken dönem QV serisinden 3.2MP CCD kompakt. Dijital fotoğraf tarihinin koleksiyon parçasını inceledik.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0039_ONN05084.jpg?v=1765238285",
"body":"""
<p>Casio, QV serisiyle dijital kamera tarihine adını yazan markalardan biri. <strong>Casio QV-R300</strong>, bu serinin olgunlaştığı dönemden kalma, karakterli ve koleksiyon değeri taşıyan bir model.</p>

<h2>Casio QV-R300 Nedir?</h2>
<p>Casio QV-R serisi, QV (QuickVideo) serisinin fotoğraf odaklı versiyonunu temsil ediyordu. R300, 3.2 megapiksel CCD sensör ve Casio'nun o dönemki kompakt tasarım anlayışıyla günlük kullanım için üretilmiş bir kameradır.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 3.2 MP CCD</li>
<li><strong>Lens:</strong> 3x optik zoom</li>
<li><strong>Ekran:</strong> 1.6" LCD</li>
<li><strong>Hafıza:</strong> SD kart</li>
<li><strong>Pil:</strong> AA × 2 adet</li>
</ul>

<h2>Casio QV Serisi ve Tarihsel Önemi</h2>
<p>Casio'nun QV serisi, 1995'te QV-10 ile dünya genelinde kitlesel dijital kamera dönemini başlattığı kabul edilen modeldir. QV-R300, bu mirasın 2000'lerin başındaki devamı. Bu serinin herhangi bir modelini koleksiyona eklemek, dijital fotoğraf tarihine dokunmak demek.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Casio QV serisi tarih koleksiyoncuları</li>
<li>Erken dönem dijital kamera meraklıları</li>
<li>AA pil kullanışlılığı arayanlar</li>
<li>Dijital fotoğraf tarihi araştırmacıları</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>Casio QV-R300 bugün kullanılabilir mi?</h3>
<p>Çalışır durumda olanlarda evet. AA pil kolayca temin edilir; SD kart takılı kullanılabilir.</p>
<h3>QV ve Exilim serisi farkı nedir?</h3>
<p>QV serisi Exilim öncesi dönemin daha büyük ve ağır modellerini kapsıyor. Exilim 2000'lerin başında ultra ince tasarımıyla QV'nin yerini aldı.</p>
<h3>Koleksiyon değeri var mı?</h3>
<p>Casio QV serisi erken dönem dijital koleksiyonların değerli parçaları. Çalışır durumda olanlar nadir sayılıyor.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-qv-r300" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio QV-R300'ü İncele →</a></div>
"""},

# ── Casio Exilim EX-FR100CT ──────────────────────────────────────────────────
{"title":"Casio Exilim EX-FR100CT İncelemesi: Geniş Açı, Suya Dayanıklı Action Kamera Alternatifi",
"handle":"casio-exilim-ex-fr100ct-inceleme-genis-aci-action-kamera",
"tags":"Casio, Casio Exilim EX-FR100CT, action kamera, su geçirmez kamera, geniş açı kamera, Casio Exilim FR serisi",
"meta_desc":"Casio Exilim EX-FR100CT incelemesi: Ayrılabilir ekran, 204° ultra geniş açı ve su geçirmez yapı. Casio'nun action kamerasını detaylıca anlattık.",
"image_src":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Casio_0003_Layer1.jpg?v=1755817580",
"body":"""
<p>GoPro'nun hâkim olduğu piyasaya Casio kendi cevabını verdi. <strong>Casio Exilim EX-FR100CT</strong>, ayrılabilir ekran modülü ve 204 derecelik ultra geniş açısıyla standart action kameralardan farklılaşan cesur bir tasarım.</p>

<h2>Casio Exilim EX-FR100CT Nedir?</h2>
<p>FR100CT, Casio'nun FR (Freestyle) serisinin bir üyesi. Kamera gövdesi ve LCD ekran birbirinden ayrılabiliyor — ekranı selfie için ters çevirebilir, ya da kamerayı uzaktan kontrol edebilirsiniz. Su geçirmez yapısı ve geniş açı lensiyle spor ve outdoor çekimler için tasarlanmış.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> CMOS</li>
<li><strong>Açı:</strong> 204° ultra geniş (fisheye benzeri)</li>
<li><strong>Su Geçirmezlik:</strong> 5 metreye kadar</li>
<li><strong>Ekran:</strong> Ayrılabilir 2.7" LCD modülü</li>
<li><strong>Bağlantı:</strong> Bluetooth (uzaktan kontrol)</li>
<li><strong>Video:</strong> Full HD 1080p</li>
<li><strong>Hafıza:</strong> microSD</li>
</ul>

<h2>Ayrılabilir Ekran: Pratik mi?</h2>
<p>FR100CT'nin ekran modülünü gövdeden ayırabilirsiniz. Ekranı selfie kolunuza veya direğe takıp kameranın gövdesini farklı açıya yerleştirebilirsiniz. Bluetooth bağlantısıyla ekrandan uzaktan çekim yapılabiliyor. Bu sistem, standart action kameralara göre daha esnek kadraj kurma imkânı sunuyor.</p>

<h2>204°: Neden Bu Kadar Geniş?</h2>
<p>204 derecelik açı, hemisferi neredeyse tamamen kapsıyor. Kask üstü çekimlerde, dalış görüntülerinde ya da selfie kullanımında bu geniş açı ortamın tamamını tek karede topluyor. Distorsiyon belirgin ama bu action kamera estetiğinin bir parçası.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Action kamera arayanlar ama GoPro dışında alternatif isteyenler</li>
<li>Dalış, sörf, snowboard gibi su sporları çekenleri</li>
<li>Casio FR serisi meraklıları ve koleksiyoncuları</li>
<li>Ayrılabilir ekran esnekliğine ihtiyaç duyanlar</li>
</ul>

<h2>Sık Sorulan Sorular</h2>
<h3>EX-FR100CT GoPro'dan üstün mü?</h3>
<p>Farklı güçleri var. Ayrılabilir ekran FR100CT'ye özgü büyük avantaj; GoPro ise daha geniş aksesuar ekosistemine sahip.</p>
<h3>5 metre su geçirmezliği yeterli mi?</h3>
<p>Yüzme, snorkeling ve sığ dalış için evet. Derin dalış (scuba) için özel dalış kılıfı gerekir.</p>
<h3>Casio EX-FR100CT pil ömrü?</h3>
<p>Normal kullanımda 1-2 saatlik video veya yaklaşık 300-400 kare fotoğraf çekimi sunar.</p>
<div style="text-align:center;margin:40px 0;"><a href="https://retrocameraland.com/products/casio-exilim-ex-fr100ct" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Casio EX-FR100CT'yi İncele →</a></div>
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
    log("\n=== BATCH 2 SONUÇ ===")
    ok = sum(1 for r in results if r["status"]=="ok")
    for r in results:
        log(f"  {'✅' if r['status']=='ok' else '❌'} {r['title'][:55]}")
    log(f"\n{ok}/{len(POSTS)} yayınlandı.")

if __name__ == "__main__":
    run()
