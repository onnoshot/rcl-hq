#!/usr/bin/env python3
"""
RCL SEO Toplu Güncelleme — Claude tarafından yazılmış içerikler
Meta açıklama + içerik genişletme + FAQ + iç linkler

Çalıştır:
  python3 rcl_seo_bulk_update.py             # kuru test (yazma yok)
  python3 rcl_seo_bulk_update.py --live      # gerçek güncelleme
  python3 rcl_seo_bulk_update.py --live --from 50  # 50. makaleden başla
"""

import argparse, json, re, sys, time, urllib.request, urllib.error
from datetime import datetime

# ── Kimlik bilgileri ──────────────────────────────────────────────────────────
TOKEN   = "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"
STORE   = "retrocameraland.myshopify.com"
BLOG_ID = "91197866123"
TG_TOKEN   = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID = "7904534693"

SITE = "retrocameraland.com"

# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM 1: Elle yazılmış içerik genişletmeleri (en kötü makaleler)
# Her makale ID'si → {body_append, faq_html, meta}
# ─────────────────────────────────────────────────────────────────────────────
MANUAL_UPDATES = {

# ── Olympus SP-320 (57w → tam içerik) ────────────────────────────────────────
572013248651: {
"meta": "Olympus SP-320 incelemesi: 7.1MP CCD sensör, PASM manuel modlar ve prosümer kompakt özellikler. Retro kamera tutkunları için Türkiye'de fiyatı ve kullanım rehberi.",
"body_append": """
<h2>Olympus SP-320 Teknik Özellikleri</h2>
<p>Olympus SP-320, 2006 yılında piyasaya çıkan ve hobi fotoğrafçılarını hedef alan bir prosümer kompakt kameradır. 7.1 megapiksellik CCD sensörü, günümüzde bile doğal renkler ve yumuşak geçişler sunar. Kameranın en büyük avantajı, tam manuel kontrol (P/A/S/M modları) ile kompakt taşınabilirliği bir arada sunmasıdır.</p>
<ul>
  <li><strong>Sensör:</strong> 7.1 MP CCD</li>
  <li><strong>Lens:</strong> Olympus 3x optik zoom, 38-114mm (35mm eşd.)</li>
  <li><strong>Modlar:</strong> Program, Diyafram öncelikli, Enstantane öncelikli, Tam Manuel</li>
  <li><strong>Ekran:</strong> 2.5 inç LCD</li>
  <li><strong>Pil:</strong> Li-ion LI-42B</li>
  <li><strong>Hafıza:</strong> xD-Picture Card</li>
</ul>

<h2>CCD Sensörün Önemi: Neden SP-320 Tercih Edilmeli?</h2>
<p>Olympus SP-320'nin kalbi olan CCD sensör, modern CMOS sensörlerden çok farklı bir renk bilimi sunar. Cilt tonları daha sıcak, gökyüzü mavisi daha derin ve gölgeler daha yumuşak geçişlidir. Y2K estetiğini sevenler için bu kamera, filtre uygulamadan doğal nostaljik kare üretir.</p>
<p>Özellikle portre ve sokak fotoğrafçılığında SP-320'nin renk karakteri diğer dönem kameralarından öne çıkar. Olympus'un doğal renk işleme algoritması, fotoğraflara filmle çekilmiş hissi verir.</p>

<h2>Kimler İçin Uygun?</h2>
<p>Olympus SP-320, tam otomatik modda kullanmak isteyenler kadar manuel kontrol öğrenmek isteyen başlangıç seviyesi fotoğrafçılar için de idealdir. Diyafram öncelikli (A) mod ile alan derinliğini kontrol edebilir, enstantane öncelikli (S) modla hareket dondurmayı deneyebilirsiniz.</p>
<p>Retro kamera koleksiyonunuza güçlü bir prosümer model eklemek istiyorsanız, SP-320 nadir bulunan ve değerini koruyan bir seçenektir. <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunda</a> test edilmiş ve çalışır durumda Olympus modellerini inceleyebilirsiniz.</p>

<h2>SP-320 ile Çekim İpuçları</h2>
<p>En iyi sonuçları almak için şu ipuçlarını deneyin: Diyafram öncelikli (A) modda düşük f değerleri (f/2.8) ile arka plan bulanıklığı yaratın; enstantane öncelikli (S) modda 1/500s ile hareket dondurun. ISO 100'de en temiz görüntüyü, ISO 400'de ise o karakteristik dijital grenli Y2K dokusunu elde edersiniz.</p>
<p>Olympus SP-320'yi <a href="https://retrocameraland.com/collections/dijital-kameralar">dijital kamera koleksiyonumuzda</a> bulabilirsiniz. Her ürün, atölyemizde temizlenerek kontrol edilmektedir.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>Olympus SP-320 hangi hafıza kartını kullanır?</h3>
<p>SP-320, xD-Picture Card kullanır. Bu Olympus'a özgü format, standart SD kartten farklıdır. Kart boyutları 16MB ile 2GB arasındadır. Kamerayı alırken kart dahil olup olmadığını mutlaka sorun.</p>
<h3>Olympus SP-320'de hangi pil kullanılır?</h3>
<p>LI-42B veya muadili LI-40B Li-ion batarya kullanır. Bu bataryalar artık yaygın olarak piyasada bulunabilmektedir. Orijinal Olympus şarj aleti ile birlikte sahiplenmek ideal seçimdir.</p>
<h3>PASM modları yeni başlayanlar için uygun mu?</h3>
<p>Kesinlikle. SP-320'nin P (Program) modu tam otomatik olarak çalışır ve adım adım A, S ve M modlarına geçişi kolaylaştırır. Manuel fotoğrafçılığa geçiş yapmak isteyenler için harika bir öğrenme platformudur.</p>
<h3>SP-320 video çeker mi?</h3>
<p>Evet, 640x480 piksel (VGA) çözünürlüğünde video kaydı yapar. Retro video estetiği isteyenler için bu çözünürlük, dönemin karakteristik görüntü kalitesini mükemmel biçimde yansıtır.</p>
<h3>Olympus SP-320 ve SP-350 arasındaki fark nedir?</h3>
<p>SP-350, SP-320'nin 8MP sensörlü halefidir. Temel işlevler ve tasarım benzerdir; SP-350 biraz daha yüksek çözünürlük sunar. Her ikisi de aynı prosümer kalite anlayışını paylaşır.</p>
""",
},

# ── Öğrenciler İçin Uygun Fiyatlı Kamera (153w → genişletme) ─────────────────
567036543115: {
"meta": "Uygun fiyatlı dijital kamera önerileri: öğrenciler ve içerik üreticiler için Canon, Fujifilm, Kodak retro modelleri. Y2K estetiği için başlangıç rehberi retrocameraland.com'da.",
"body_append": """
<h2>Neden Retro Dijital Kamera?</h2>
<p>Uygun fiyatlı dijital kamera arayanlar için retro modeller hem bütçe dostu hem de estetik açıdan eşsiz seçenekler sunar. Modern akıllı telefonlar her ne kadar gelişmiş kameralar barındırsa da, 2000'lerin dijital kompaktlarının verdiği CCD renk karakteri ve Y2K görsel dili tamamen farklı bir deneyim sunmaktadır.</p>

<h2>Bütçe Dostu Model Önerileri</h2>
<h3>Canon IXUS / PowerShot Serisi</h3>
<p>Canon'un ikonik IXUS ve PowerShot serileri, hem şık alüminyum tasarımlarıyla hem de güvenilir görüntü kaliteleriyle öğrenciler arasında en popüler seçeneklerden biridir. SD400, SD1000 ve IXUS 65 gibi modeller sosyal medya içerikleri için mükemmel CCD renkleri üretir. Ortalama fiyat aralığı 1.200 – 3.500 TL arasında değişmektedir.</p>
<h3>Fujifilm FinePix Serisi</h3>
<p>Fujifilm'in renk bilimi, dünya genelinde fotoğrafçılar tarafından övgüyle karşılanmaktadır. FinePix F serisi ve Z serisi modelleri, canlı renk tonları ve kompakt tasarımlarıyla içerik üreticilerinin gözdesidir. Özellikle FinePix F50fd ve F100fd, uygun fiyatlarıyla başlangıç için idealdir.</p>
<h3>Kodak EasyShare Serisi</h3>
<p>Kodak EasyShare modelleri, kullanımı son derece basit ve ekonomik seçenekler sunar. V ve C serisi modeller, günlük çekimler ve sosyal medya paylaşımları için yeterli kalite sağlar. 500-1.500 TL aralığındaki bu modellerle koleksiyona giriş yapmak oldukça kolaydır.</p>
<h3>Casio Exilim Serisi</h3>
<p>Ultra ince tasarımlarıyla dikkat çeken Casio Exilim modelleri, özellikle selfie ve grup çekimleri için idealdir. Hafif yapısı ve şık görünümüyle sırt çantasına kolayca sığan Exilim EX-Z serisini mutlaka inceleyin.</p>

<h2>Nereden Satın Almalı?</h2>
<p>Test edilmiş, çalışır durumda ve garanti ile satılan retro dijital kameralar için <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunu</a> inceleyebilirsiniz. Her ürün, atölyemizde kontrol edildikten sonra satışa sunulmaktadır. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera kategorimizde</a> bütçenize uygun onlarca seçenek sizi bekliyor.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>Öğrenci bütçesiyle en iyi retro kamera hangisi?</h3>
<p>1.000-2.000 TL bütçesiyle Canon PowerShot A serisi veya Fujifilm FinePix F serisi ideal başlangıç noktalarıdır. Her iki marka da giriş dostu arayüzleri ve zengin ikinci el piyasasıyla öğrencilere en uygun seçenekleri sunar.</p>
<h3>Retro kameraların pili ve kartı nereden bulunur?</h3>
<p>Çoğu model standart AA pil veya yaygın Li-ion batarya kullanır. Hafıza kartları (SD veya xD) elektronik marketlerde kolayca bulunabilir. Satın almadan önce hangi kart formatını kullandığını kontrol edin.</p>
<h3>İçerik üretimi için hangi özelliklere dikkat etmeli?</h3>
<p>Y2K estetiği için CCD sensörlü modeller tercih edilmelidir. Bunun yanı sıra flaş özelliği güçlü, ekranı net ve kullanımı basit modeller sosyal medya içerik üretimi için en verimli seçimdir.</p>
<h3>Retro kamera ile çekilen fotoğraflar direkt paylaşılabilir mi?</h3>
<p>Evet. SD kart okuyucu veya USB kablosuyla fotoğrafları bilgisayar veya telefona aktarıp anında paylaşabilirsiniz. Bazı modeller doğrudan USB bağlantısıyla şarj ve veri aktarımı destekler.</p>
<h3>Hangi sosyal medya platformu retro fotoğraflar için en uygun?</h3>
<p>Instagram ve TikTok, Y2K retro estetiğinin en yoğun olarak paylaşıldığı platformlardır. Pinterest ise moodboard oluşturma ve retro fotoğraf ilhamı için idealdir. Her platform için karesel (1:1) format en çok tercih edilendir.</p>
""",
},

# ── Türkiye'de En Popüler Retro Kameralar (222w → genişletme) ────────────────
567036641419: {
"meta": "Türkiye'de en popüler retro kamera modelleri ve 2025 fiyatları: Canon, Fujifilm, Sony, Nikon. retrocameraland.com'dan test edilmiş, çalışır durumda ürünlerle hızlı teslimat.",
"body_append": """
<h2>Neden Retro Kameralar Bu Kadar Popüler?</h2>
<p>Türkiye'de retro kamera trendi, özellikle 2023 sonrasında büyük ivme kazandı. Instagram ve TikTok içerik üreticileri, akıllı telefonların yapay zekâ destekli "mükemmel" görsellerine alternatif olarak 2000'lerin doğal, grenli ve renkli CCD fotoğraflarını tercih etmeye başladı. Bu trendi körükleyen başka bir etken de Y2K modasının tüm dünyada yeniden yükselmesi.</p>

<h2>En Popüler 5 Model ve Fiyat Rehberi</h2>
<h3>1. Canon IXUS / PowerShot Serisi</h3>
<p>Canon'un kompakt IXUS ve PowerShot serisi, Türkiye'de en geniş kullanıcı kitlesine sahip retro kamera ailesini oluşturmaktadır. Alüminyum gövde, güvenilir optik ve DIGIC işlemci kombinasyonu, bu seriyi hem görsel hem teknik açıdan öne çıkarır. <strong>Ortalama fiyat: 1.800 – 4.500 TL</strong></p>
<h3>2. Fujifilm FinePix Serisi</h3>
<p>Fujifilm renk biliminin retro dijital fotoğrafçılıktaki etkisi tartışılmazdır. Film simülasyonu içermeyen eski FinePix modelleri bile karakteristik Fujifilm renk tonlarını taşır; cilt tonları sıcak, yeşiller derin ve gökyüzü mavisi kendine özgüdür. <strong>Ortalama fiyat: 1.500 – 3.800 TL</strong></p>
<h3>3. Sony Cyber-shot Serisi</h3>
<p>Carl Zeiss lens ortaklığıyla üretilen Sony Cyber-shot modelleri, keskinlik ve renk doygunluğu konusunda döneminin en üst seviye kompaktları arasındaydı. T, W ve N serileri, bugün koleksiyonerlerin en çok aradığı modeller arasındadır. <strong>Ortalama fiyat: 1.200 – 3.500 TL</strong></p>
<h3>4. Nikon Coolpix Serisi</h3>
<p>Nikon'un meşhur renk bilimini taşıyan Coolpix modelleri, özellikle portre ve günlük çekim konusunda üstün performans gösterir. S, P ve L serileri farklı ihtiyaçlara hitap eden geniş bir yelpaze sunar. <strong>Ortalama fiyat: 1.000 – 2.800 TL</strong></p>
<h3>5. Kodak EasyShare Serisi</h3>
<p>Giriş seviyesindeki bütçeler için Kodak EasyShare modelleri, sade tasarımları ve kullanımı kolay arayüzleriyle öne çıkar. Özellikle V serisi, hem kompakt tasarım hem de iyi görüntü kalitesiyle dikkat çeker. <strong>Ortalama fiyat: 800 – 2.000 TL</strong></p>

<h2>Türkiye'de Nereden Satın Alınır?</h2>
<p>İkinci el platformlarda (Sahibinden, Dolap) retro kamera arayışında oldukça dikkatli olunmalıdır. Test edilmemiş kameralar, lens hatası veya ölü batarya gibi sorunlarla gelebilir. En güvenli seçenek için <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunu</a> inceleyebilirsiniz; tüm ürünler atölyemizde kontrol edilmekte ve garantili olarak satışa sunulmaktadır. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera kategorimizde</a> fiyat bilgisine ulaşabilirsiniz.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>Türkiye'de retro kamera fiyatları neden yükseliyor?</h3>
<p>Küresel Y2K trendi ve içerik üretici talebinin artmasıyla retro dijital kamera fiyatları 2022'den itibaren istikrarlı bir yükseliş göstermektedir. Nadir ve aranılan modeller özellikle hızlı değer kazanmaktadır.</p>
<h3>Türkiye'de garantili retro kamera satın alınabilir mi?</h3>
<p>Evet, Retrocameraland olarak tüm ürünleri atölyemizde test ettikten sonra garantili satıyoruz. Teknik sorun yaşanması durumunda destek hizmeti sağlamaktayız.</p>
<h3>Hangi retro kamera modeli Türkiye'de en çok aranıyor?</h3>
<p>Sony Cyber-shot W serisi, Canon IXUS 75/85/95 ve Fujifilm FinePix Z serisi Türkiye'de en çok aranan retro kamera modelleri arasında yer almaktadır.</p>
<h3>Kargo ve teslimat süresi ne kadardır?</h3>
<p>Tüm siparişler aynı gün veya ertesi iş günü kargoya verilmektedir. Türkiye genelinde 1-3 iş günü içinde teslim yapılmaktadır.</p>
<h3>İkinci el kamera alırken nelere dikkat etmeli?</h3>
<p>Lens hareketi ve netlik kontrolü, batarya şarj kapasitesi, hafıza kartı uyumluluğu ve LCD ekran durumu mutlaka test edilmelidir. Retrocameraland'da tüm bu kontroller satış öncesinde yapılmaktadır.</p>
""",
},

# ── Y2K Dijital Kameralar (131w) ──────────────────────────────────────────────
564389806219: {
"meta": "Y2K dijital kameralar: 2000'lerin ruhunu geri getiren fotoğraf akımı. CCD sensörlü retro kameraların Instagram ve TikTok'ta neden bu kadar popüler olduğunu keşfedin.",
"body_append": """
<h2>Y2K Kamera Trendi Neden Bu Kadar Güçlü?</h2>
<p>Y2K dijital kameralar, sosyal medyanın en güçlü nostalji trendlerinden birini temsil ediyor. Mükemmel keskinlik arayan akıllı telefon kameralarının aksine, 2000'lerin kompakt dijital kameraları fotoğraflara benzersiz bir karakter ve doku katar. Düşük çözünürlük, doğal renk patlamaları ve flaşın yarattığı dramatik ışık oyunu — hepsini bir arada Y2K dijital kameralarda bulursunuz.</p>

<h2>Y2K Estetiğinin Teknik Sırrı: CCD Sensör</h2>
<p>Günümüz kameralarında kullanılan CMOS sensörlerin aksine, 2000'lerin kameralarında yer alan <strong>CCD (Charge-Coupled Device) sensörler</strong> fotoğraflara son derece özel bir renk karakteri katar:</p>
<ul>
  <li>Daha yumuşak ve pastel renk geçişleri</li>
  <li>Doğal dijital grain (taneli doku)</li>
  <li>Aşırı işlenmemiş, ham ve samimi görüntüler</li>
  <li>Flaş kullanımında o ikonik "patlayan" renk doygunluğu</li>
</ul>
<p>Bu özellikler, fotoğrafları sanki film kamerayla çekilmiş gibi göstererek Y2K estetiğinin temel taşını oluşturur.</p>

<h2>En İyi Y2K Kamera Markaları</h2>
<h3>Canon PowerShot A Serisi</h3>
<p>Canon'un A serisi, Y2K fotoğrafçılığının simgesi haline gelmiştir. A510, A520, A540 gibi modeller, güçlü flaş performansı ve AA pil kullanımıyla pratik ve erişilebilir seçeneklerdir.</p>
<h3>Sony Cyber-shot DSC-W ve DSC-S Serisi</h3>
<p>Sony'nin Y2K dönemine ait Cyber-shot modelleri, Carl Zeiss lens avantajıyla keskin ve renkli kareler üretir. DSC-W55, W80 ve W150 modelleri özellikle grup ve parti fotoğrafları için tercih edilmektedir.</p>
<h3>Nikon Coolpix Serisi</h3>
<p>Nikon'un Coolpix serisindeki CCD modeller, Nikon'a özgü mavi tonlaması ve derin renk paleti ile öne çıkar. L ve S serileri geniş kullanıcı tabanıyla kolayca bulunabilir.</p>

<h2>Y2K Look İçin Temel İpuçları</h2>
<p>Y2K estetiğini yakalamak için: (1) Flaşı her zaman açık kullanın — gündüz bile. (2) ISO'yu 200-400 arasında tutun. (3) Tarih damgası özelliğini aktif edin. (4) Doğal ışıkta çekim yaparken bile dolgu flaşı kullanın. Bu dört kural, o ikonik 2000'ler havasını anında yaratır.</p>
<p><a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonumuzda</a> seçili Y2K kamera modellerini, <a href="https://retrocameraland.com/collections/dijital-kameralar">dijital kamera kategorimizden</a> inceleyebilirsiniz.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>Y2K kamera trendi ne zaman başladı?</h3>
<p>Y2K kamera trendi, 2020-2021 yıllarında TikTok'ta başlayarak Instagram'a yayıldı. Bella Hadid, Dua Lipa gibi ünlülerin retro kamera fotoğraflarını paylaşmasıyla küresel bir kültürel fenomene dönüştü.</p>
<h3>Y2K fotoğrafı için en iyi kamera hangisi?</h3>
<p>Canon PowerShot A serisi, Sony Cyber-shot W serisi ve Fujifilm FinePix Z serisi, Y2K estetiği için en sık önerilen modellerdir. CCD sensörlü olması, Y2K look için temel kriterdir.</p>
<h3>Y2K kameralar Türkiye'de bulunuyor mu?</h3>
<p>Evet, Retrocameraland olarak Türkiye'de test edilmiş ve çalışır durumda Y2K kamera modellerini satmaktayız. Kargolu satış ile Türkiye'nin her iline hızlı teslimat yapılmaktadır.</p>
<h3>Y2K fotoğraf estetiği için akıllı telefon yeterli mi?</h3>
<p>Filtreler ve uygulamalarla Y2K efekti taklit edilebilir; ancak gerçek CCD sensörlü bir retro kameranın ürettiği doğal doku ve renk karakteri, yazılımla elde edilemez.</p>
<h3>CCD sensörlü kameralar hâlâ üretiliyor mu?</h3>
<p>Hayır. Büyük kamera üreticileri 2010'ların başında CCD sensörü neredeyse tamamen bırakarak CMOS teknolojisine geçiş yaptı. Bu yüzden CCD sensörlü retro modeller artık koleksiyonluk değer taşımaktadır.</p>
""",
},

# ── Vintage Dijital Kameralarla Sosyal Medyada Fark Yaratmanın 7 Yolu ─────────
564389937291: {
"meta": "Vintage dijital kameralarla sosyal medyada fark yaratmanın 7 yolu: retro fotoğrafçılık ipuçları, Y2K estetik rehberi ve en iyi kamera önerileri retrocameraland.com'dan.",
"body_append": """
<h2>Vintage Kamera ile Fark Yaratan İçerik Üretmenin Sırrı</h2>
<p>Vintage dijital kameralarla sosyal medyada öne çıkmak, telefon kareleri denizinde gerçek anlamda farklılaşmanın en güçlü yollarından biridir. 2000'lerin kompakt kameralarının ürettiği görüntüler, doğal grain, sıcak renk tonları ve o karakteristik flaş patlamasıyla algoritmaların bile dikkatini çeken içerikler yaratır.</p>

<h2>Hangi Platform İçin Hangi Çekim Tekniği?</h2>
<h3>Instagram için</h3>
<p>Instagram'da karesel format (1:1) ve portrait format (4:5) en çok etkileşim alan oranlardır. Vintage kameranızla çerçeveleme yaparken bu oranları aklınızda tutun. Flaşlı gece çekimleri ve mavi saatte yapılan doğal ışık çekimleri Instagram'da en yüksek etkileşimi alan retro kare tiplerdir.</p>
<h3>TikTok ve Reels için</h3>
<p>Video çeken vintage modeller için Sanyo Xacti ve Sony Cyber-shot gibi kameralar ideal seçimdir. 640x480 veya 720p çözünürlükteki retro video görüntüleri, TikTok'ta "aesthetic" ve "vintage" içerik kategorilerinde viral olma potansiyeli taşır. Sessiz çekim yapan modeller ise üzerine müzik eklenerek mood videoları için kullanılabilir.</p>
<h3>Pinterest için</h3>
<p>Pinterest'te uzun dikdörtgen format (2:3) tercih edilir. Vintage kameralarla çekilen yatay ve dikey kompozisyonlar, moodboard ve retro estetik pinboard'larda yüksek kaydetme ve paylaşım sayısına ulaşmaktadır.</p>

<h2>Sosyal Medyada Viral Retro Kare İçin 3 Altın Kural</h2>
<p>1. <strong>Doğal ışık + flaş kombinasyonu:</strong> Gündüz dışarıda flaşınızı açık tutarak konunuzu arka plandan ayırın. 2. <strong>Hareket ve anlık kare:</strong> Retro kameralar hareketi "dondurmak" yerine hafif bulanıklaştırır — bu da o canlı, spontane his yaratır. 3. <strong>Minimum düzenleme:</strong> Çektiğiniz ham görüntüye sadık kalın; filtre eklemek yerine kameranın ürettiği doğal renkleri kullanın.</p>
<p>Hangi vintage modelin sosyal medya içerik üretimine en uygun olduğunu öğrenmek için <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunu</a> ziyaret edebilirsiniz. Uzman ekibimiz size en uygun modeli bulmada yardımcı olacaktır. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kameralar sayfamıza</a> göz atın.</p>

<h2>Sık Sorulan Sorular</h2>
<h3>Vintage kamera ile çekilen fotoğraflar doğrudan sosyal medyaya yüklenebilir mi?</h3>
<p>Evet. SD kart, USB kablo veya kart okuyucu ile fotoğrafları telefona veya bilgisayara aktarıp anında paylaşabilirsiniz. Bazı modellerde Bluetooth veya Wi-Fi aktarımı da mevcuttur.</p>
<h3>Hangi vintage kamera sosyal medya için en çok tercih ediliyor?</h3>
<p>Canon PowerShot A ve IXUS serileri, Fujifilm FinePix Z serisi ve Sony Cyber-shot W serisi sosyal medya içerik üreticileri tarafından en çok tercih edilen modellerdir.</p>
<h3>Vintage kamera fotoğrafları düzenlenmeli mi?</h3>
<p>Çoğu durumda minimal düzenleme önerilir: hafif kontrast ve parlaklık ayarı yeterlidir. Kameranın doğal renk karakterini bozmamak için aşırı filtreden kaçının.</p>
<h3>Gece çekimlerinde vintage kamera kullanılabilir mi?</h3>
<p>Evet, güçlü flaş özelliğine sahip modeller gece çekim için uygundur. Flaş açıkken gece ortamlarında o ikonik kırmızı gözlü, patlayan renkli Y2K kareleri elde edebilirsiniz.</p>
<h3>Hangi vintage kamera videoyu da destekler?</h3>
<p>Sanyo Xacti HD1/CG20, Sony Cyber-shot W serisi ve Canon PowerShot A serisi hem fotoğraf hem video çekimi yapabilen popüler modellerdir.</p>
""",
},

# ── Telefon mu Dijital Fotoğraf Makinesi mi? (591w → meta + FAQ düzeltme) ──────
564390232203: {
"meta": "Telefon mu dijital fotoğraf makinesi mi? CCD sensörlü retro kameraların 2025'te akıllı telefonlara karşı gerçek avantajları — kapsamlı karşılaştırma rehberi.",
"body_append": """
<h2>Sık Sorulan Sorular</h2>
<h3>Dijital fotoğraf makinesi mi yoksa telefon kamerası mı daha iyi?</h3>
<p>Her ikisinin farklı güçlü yönleri vardır. Hız ve pratiklik için telefon; renk karakteri, alan derinliği ve CCD estetiği için dijital kamera tercih edilir. Y2K ve retro içerik üretimi için dijital kamera her zaman önde gelir.</p>
<h3>CCD sensörlü kameralar neden bu kadar değerli?</h3>
<p>CCD sensörler artık üretilmediğinden, bu sensörlere sahip retro kameralar koleksiyonluk değer taşır. Yazılımla taklit edilemeyen doğal renk karakterleri ve film benzeri dokular, bu kameraları fotoğraf tutkunları arasında vazgeçilmez kılmaktadır.</p>
<h3>Retro dijital kamera ile profesyonel kalite fotoğraf çekilebilir mi?</h3>
<p>Sosyal medya ve günlük kullanım için kesinlikle yeterli kalite sağlarlar. Baskı kalitesi veya profesyonel stüdyo çekimleri için modern DSLR veya aynasız kameralar daha uygundur.</p>
<h3>Eski dijital kameraların telefona göre en büyük avantajı nedir?</h3>
<p>Yapay zekâ işlemesinden arındırılmış, ham ve samimi görüntü kalitesi; gerçek optik alan derinliği; benzersiz renk karakteri ve koleksiyonluk değer — bu dört unsur eski dijital kameraları akıllı telefonlara karşı güçlü kılan temel avantajlardır.</p>
<h3>Türkiye'de eski dijital kamera nereden satın alınır?</h3>
<p><a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunda</a> test edilmiş ve garantili eski dijital kamera modellerini bulabilirsiniz. Tüm ürünler atölyemizde kontrol edildikten sonra satışa sunulmaktadır. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera sayfamızı</a> ziyaret edin.</p>
""",
},

# ── Sanyo Xacti (236w → meta + içerik) ───────────────────────────────────────
568394973323: {
"meta": "Sanyo Xacti serisi incelemesi: dünyanın ilk kompakt HD videosunu çeken retro camcorder. Vlog içerik üreticileri için Y2K video estetiği ve pistol grip tasarımı rehberi.",
"body_append": """
<h2>Sanyo Xacti ile İçerik Üretmenin Avantajları</h2>
<p>Sanyo Xacti serisi, içerik üreticileri için üç temel avantaj sunar: ergonomik tutuş, karakteristik retro video dokusu ve dayanıklı SD kart tabanlı depolama. Modern 4K kameraların soğuk ve dijital görüntülerinin aksine, Xacti'nin CCD sensörlü videoları o nostaljik 2000'ler MTV klibi havasını doğal olarak üretir.</p>
<p>Kamerayı <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonumuzda</a> veya <a href="https://retrocameraland.com/collections/dijital-kameralar">dijital kamera kategorimizden</a> inceleyebilirsiniz.</p>
""",
},

# ── Nikon Coolpix 2500 (274w → meta + içerik) ────────────────────────────────
568394907787: {
"meta": "Nikon Coolpix 2500 incelemesi: döner lensli efsane retro kamera. Selfie kültürünü başlatan Nikon swivel serisi — Y2K estetik için mükemmel compact kamera rehberi.",
"body_append": """
<h2>Nikon Coolpix 2500 Nereden Satın Alınır?</h2>
<p>Nikon Coolpix 2500 ve diğer döner lensli Coolpix modelleri, <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonumuzda</a> zaman zaman stoklanmaktadır. Compact Flash kart uyumluluğunu kontrol ederek alım yapın. Tüm ürünlerimiz test edilmiş ve çalışır durumdadır. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera kategorimizi</a> takip edin.</p>
""",
},

# ── Y2K Look Nasıl Elde Edilir (352w → meta) ─────────────────────────────────
568394875019: {
"meta": "Y2K look nasıl elde edilir: patlayan flaş, tarih damgası ve pozlama ayarları. Retro dijital kamerayla Bella Hadid estetiği için adım adım teknik rehber.",
"body_append": """
<p>Bu teknikleri uygulamak için <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonumuzda</a> doğru retro kamerayı bulabilirsiniz. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera kategorimizde</a> Y2K estetiği için ideal modeller sizi bekliyor.</p>
""",
},

# ── İkinci El Kamera Alırken Dikkat (373w → meta) ────────────────────────────
568394842251: {
"meta": "İkinci el dijital kompakt kamera alırken dikkat edilecekler: lens hatası, pil türü, hafıza kartı uyumu. 2026 güncel rehberi retrocameraland.com uzmanları tarafından.",
"body_append": """
<p>Güvenli alışveriş için tüm bu kontrolleri sizin yerinize yapan <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunu</a> incelemeyi unutmayın. <a href="https://retrocameraland.com/collections/dijital-kameralar">Dijital kamera sayfamızda</a> garantili ürünler sizi bekliyor.</p>
""",
},

}

# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM 2: Kalan makalelere otomatik meta + FAQ + link ekleme
# ─────────────────────────────────────────────────────────────────────────────

def generate_meta(title, tags, body_clean):
    """Başlık ve içeriğe göre 148-163 karakter meta açıklama üretir."""
    title_l = title.lower()
    tags_l   = tags.lower()

    brands = ["sony", "canon", "fujifilm", "nikon", "olympus", "casio",
              "kodak", "panasonic", "samsung", "sanyo", "ricoh", "pentax"]
    found_brand = next((b for b in brands if b in title_l), None)

    # Kamera inceleme yazısı
    if any(k in title_l for k in ["inceleme", "incelemesi", "review"]):
        model = title.split(":")[0].strip() if ":" in title else title.split("—")[0].strip()
        model = model[:45]
        base = f"{model} incelemesi: teknik özellikler, renk kalitesi ve Y2K estetiği."
        ext  = " retrocameraland.com'da test edilmiş, çalışır durumda — hızlı kargo ile."
        meta = (base + ext)[:163]

    # Fiyat / karşılaştırma yazısı
    elif any(k in title_l for k in ["fiyat", "karşılaştırma", "vs", "hangisi"]):
        base = f"{title[:55]} — Türkiye fiyatları, teknik karşılaştırma ve satın alma rehberi."
        ext  = " retrocameraland.com'da garantili seçenekler."
        meta = (base + ext)[:163]

    # Rehber / ipuçları yazısı
    elif any(k in title_l for k in ["rehberi", "rehber", "ipuçları", "nasıl", "yol", "adım"]):
        base = title[:60] + " — Kapsamlı rehber ve pratik ipuçları."
        ext  = " retrocameraland.com uzmanları tarafından hazırlandı."
        meta = (base + ext)[:163]

    # Genel kamera yazısı
    elif found_brand:
        brand_c = found_brand.capitalize()
        base = f"{brand_c} retro dijital kamera: renk karakteri, teknik özellikler ve Y2K estetiği."
        ext  = " retrocameraland.com'dan garantili satış, Türkiye geneli hızlı teslimat."
        meta = (base + ext)[:163]

    # Genel içerik
    else:
        base = title[:65] + " — retrocameraland.com'un uzman rehberi."
        ext  = " Türkiye'nin en kapsamlı retro kamera kaynağı, garantili ürünler."
        meta = (base + ext)[:163]

    # Minimum uzunluk kontrolü
    if len(meta) < 148:
        ext2 = " Türkiye'nin retro kamera uzmanı retrocameraland.com'da inceleyin."
        meta = (meta.rstrip(".") + ext2)[:163]

    return meta


def build_internal_link_block():
    return (
        '\n<p>Retrocameraland koleksiyonumuzu keşfetmek için '
        '<a href="https://retrocameraland.com/collections/all">tüm kamera koleksiyonumuza</a> '
        'veya <a href="https://retrocameraland.com/collections/dijital-kameralar">'
        'dijital kamera kategorimize</a> göz atabilirsiniz.</p>\n'
    )


def add_links_to_body(body_html):
    """Eğer iç link yoksa uygun konuma ekle."""
    il = len(re.findall(r'href="https://retrocameraland\.com', body_html))
    if il >= 2:
        return body_html
    block = build_internal_link_block()
    # Sondan 3. </p> sonrasına ekle; yoksa sona ekle
    matches = list(re.finditer(r'</p>', body_html, re.I))
    if len(matches) >= 3:
        pos = matches[-3].end()
        return body_html[:pos] + block + body_html[pos:]
    return body_html + block


# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM 3: Shopify yardımcı fonksiyonları
# ─────────────────────────────────────────────────────────────────────────────

def shopify(method, path, body=None):
    url  = f"https://{STORE}/admin/api/2024-01/{path}"
    data = json.dumps(body).encode() if body else None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("X-Shopify-Access-Token", TOKEN)
            req.add_header("Content-Type",  "application/json")
            req.add_header("Accept",        "application/json")
            with urllib.request.urlopen(req, timeout=30) as r:
                link = r.headers.get("Link", "")
                return json.loads(r.read()), link
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(12 * (attempt + 1))
            else:
                raise RuntimeError(f"Shopify {method} {path} → {e.code}: {e.read().decode()[:200]}")
    raise RuntimeError("Shopify 3 denemede başarısız")


def fetch_all_articles():
    articles = []
    path = (f"blogs/{BLOG_ID}/articles.json?"
            "limit=250&fields=id,title,body_html,tags,handle")
    while path:
        data, link = shopify("GET", path)
        articles.extend(data.get("articles", []))
        path = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r'page_info=([^&>]+)', part)
                if m:
                    path = (f"blogs/{BLOG_ID}/articles.json?"
                            f"limit=250&fields=id,title,body_html,tags,handle"
                            f"&page_info={m.group(1)}")
        if path:
            time.sleep(0.5)
    return articles


def get_metafields(article_id):
    data, _ = shopify("GET", f"articles/{article_id}/metafields.json")
    return data.get("metafields", [])


def upsert_meta(article_id, metafields, value):
    ex = next((m for m in metafields
               if m.get("namespace") == "seo" and m.get("key") == "description"), None)
    body = {"metafield": {"value": value, "type": "single_line_text_field"}}
    if ex:
        body["metafield"]["id"] = ex["id"]
        shopify("PUT", f"articles/{article_id}/metafields/{ex['id']}.json", body)
    else:
        body["metafield"].update({"namespace": "seo", "key": "description"})
        shopify("POST", f"articles/{article_id}/metafields.json", body)
    time.sleep(0.5)


def update_body(article_id, new_body):
    shopify("PUT", f"blogs/{BLOG_ID}/articles/{article_id}.json",
            {"article": {"id": article_id, "body_html": new_body}})
    time.sleep(0.6)


def score_quick(title, meta, body):
    """Hızlı skor tahmini."""
    s = 0
    clean = re.sub(r'<[^>]+>', ' ', body); clean = re.sub(r'\s+', ' ', clean).strip()
    wc = len(clean.split())
    tl = len(title); ml = len(meta)
    if tl >= 45: s += 20
    if ml >= 140: s += 15
    if wc >= 1500: s += 20
    elif wc >= 1000: s += 13
    elif wc >= 700: s += 7
    h2 = len(re.findall(r'<h2', body, re.I))
    h3 = len(re.findall(r'<h3', body, re.I))
    if h2 >= 5: s += 10
    elif h2 >= 3: s += 6
    if h3 >= 2: s += 5
    elif h3 == 1: s += 2
    if re.search(r'(sık sorulan|Sıkça Sorulan|SSS|FAQ|<h[23][^>]*>.*soru)', body, re.I): s += 10
    il = len(re.findall(r'href="https://retrocameraland\.com', body))
    if il >= 2: s += 5
    elif il == 1: s += 2
    if 0.5 <= (clean.lower().count(title.split()[0].lower()) / max(wc, 1) * 100) <= 4: s += 10
    return s, wc


def telegram(msg):
    try:
        data = json.dumps({"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
        req  = urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# ANA AKIŞ
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live",  action="store_true", help="Shopify'a gerçekten yaz")
    parser.add_argument("--from",  dest="start_from", type=int, default=0,
                        help="N. makaleden başla")
    parser.add_argument("--limit", type=int, default=999)
    args = parser.parse_args()

    t0 = time.time()
    log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
    mode_tag = "[LIVE]" if args.live else "[DRY-RUN]"

    log("=" * 60)
    log(f"RCL SEO Toplu Güncelleme {mode_tag}")
    log("=" * 60)

    log("📥 Makaleler çekiliyor...")
    articles = fetch_all_articles()
    log(f"  Toplam: {len(articles)} makale")

    updated_meta = updated_body = 0
    skipped = 0
    results = []

    batch = articles[args.start_from : args.start_from + args.limit]
    log(f"  İşlenecek: {len(batch)} makale ({args.start_from}–{args.start_from+len(batch)-1})")

    for i, a in enumerate(batch):
        art_id    = a["id"]
        title     = a["title"]
        tags      = a.get("tags", "")
        body      = a.get("body_html") or ""
        clean_txt = re.sub(r'<[^>]+>', ' ', body)
        clean_txt = re.sub(r'\s+', ' ', clean_txt).strip()

        old_s, wc = score_quick(title, "", body)

        log(f"\n[{i+1}/{len(batch)}] ID:{art_id} [{old_s}] {title[:50]}")

        try:
            metafields = get_metafields(art_id) if args.live else []
            time.sleep(0.3)

            cur_meta = next(
                (m["value"] for m in metafields
                 if m.get("namespace") == "seo" and m.get("key") == "description"), "")

            # ── Elle yazılmış güncelleme varsa ──
            if art_id in MANUAL_UPDATES:
                upd = MANUAL_UPDATES[art_id]
                new_meta = upd.get("meta", cur_meta)
                new_body = body
                if upd.get("body_append"):
                    new_body = body + upd["body_append"]
                new_body = add_links_to_body(new_body)

                log(f"   ✍ Özel içerik uygulanıyor ({len(new_body.split())} kelime)")
                if args.live:
                    if new_meta != cur_meta:
                        upsert_meta(art_id, metafields, new_meta)
                        updated_meta += 1
                    if new_body != body:
                        update_body(art_id, new_body)
                        updated_body += 1
                else:
                    log(f"   [DRY] meta: {new_meta[:80]}…")

            # ── Otomatik güncelleme (meta eksikse veya kısaysa) ──
            else:
                changes = []
                new_meta = cur_meta
                new_body = body

                # Meta açıklama kontrolü
                if len(cur_meta) < 140:
                    new_meta = generate_meta(title, tags, clean_txt[:500])
                    log(f"   → Meta ({len(new_meta)}kar): {new_meta[:80]}…")
                    changes.append("meta")

                # İç link kontrolü
                il = len(re.findall(r'href="https://retrocameraland\.com', body))
                if il < 2:
                    new_body = add_links_to_body(new_body)
                    changes.append("link")

                if not changes:
                    log("   ✓ Zaten yeterli, atlanıyor")
                    skipped += 1
                    continue

                if args.live:
                    if "meta" in changes and new_meta != cur_meta:
                        upsert_meta(art_id, metafields, new_meta)
                        updated_meta += 1
                    if "link" in changes and new_body != body:
                        update_body(art_id, new_body)
                        updated_body += 1
                else:
                    log(f"   [DRY] değişiklikler: {', '.join(changes)}")

            new_s, new_wc = score_quick(title, new_meta, new_body)
            gain = new_s - old_s
            log(f"   📈 Skor: {old_s} → {new_s} (+{gain}) | {new_wc}w")
            results.append({"id": art_id, "title": title,
                            "old": old_s, "new": new_s, "gain": gain})

        except Exception as e:
            log(f"   ❌ HATA: {e}")

        time.sleep(0.8)

    # ── Özet ──────────────────────────────────────────────────────────────────
    elapsed = int(time.time() - t0)
    avg_gain = (sum(r["gain"] for r in results) // len(results)) if results else 0
    log("\n" + "=" * 60)
    log(f"✅ Tamamlandı {mode_tag}")
    log(f"   Meta güncellendi : {updated_meta}")
    log(f"   Body güncellendi : {updated_body}")
    log(f"   Atlandı (ok)     : {skipped}")
    log(f"   Ort. kazanım     : +{avg_gain} puan")
    log(f"   Süre             : {elapsed}s")
    log("=" * 60)

    if args.live:
        telegram(
            f"<b>📊 SEO Toplu Güncelleme Tamamlandı</b>\n"
            f"Meta: {updated_meta} | Body: {updated_body} | Atlandı: {skipped}\n"
            f"Ort. kazanım: +{avg_gain} puan | {elapsed}s"
        )


if __name__ == "__main__":
    main()
