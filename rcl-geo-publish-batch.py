#!/usr/bin/env python3
"""GEO içerik takvimi #2, #3, #11 — toplu yayın."""
import sys
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import publish_article

# Mobil tablo sarıcı stili
TW_OPEN = '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:24px 0;"><table style="width:100%;border-collapse:collapse;min-width:480px;">'
TH = lambda *cols: '<thead><tr style="background:#f8f4f0;">' + ''.join(f'<th style="padding:12px;text-align:left;border-bottom:2px solid #c8a882;">{c}</th>' for c in cols) + '</tr></thead>'
def TR(*cols):
    return '<tr>' + ''.join(f'<td style="padding:12px;border-bottom:1px solid #eee;">{c}</td>' for c in cols) + '</tr>'
TW_CLOSE = '</tbody></table></div>'

ARTICLES = []

# ─────────────────────────────────────────────────────────────────────────────
# #2 — En İyi CCD Digicam Modelleri (2026)
# ─────────────────────────────────────────────────────────────────────────────
ARTICLES.append(dict(
    title="En İyi CCD Digicam Modelleri (2026 Listesi)",
    handle="en-iyi-ccd-digicam-modelleri-2026",
    tags="CCD digicam, en iyi digicam, retro dijital kamera, Y2K kamera, kamera önerisi",
    meta="2026'da alınabilecek en iyi CCD digicam modelleri: Canon, Fujifilm ve Casio'dan test edilmiş, karaktere göre seçilmiş retro dijital kamera listesi.",
    image="best CCD digicam cameras collection on warm wooden surface, Canon Fujifilm Casio compact cameras, Y2K nostalgic aesthetic, soft film grain, retro color grade",
    body=f"""
<h2>En İyi CCD Digicam Modelleri (2026 Listesi)</h2>
<p>"En iyi digicam hangisi?" sorusunu o kadar çok duydum ki, sonunda elimden geçen yüzlerce makineyi tek bir mantıkla sıraladım: karakter. Çünkü CCD digicam dünyasında "en iyi" megapiksel değil, sana hangi rengi, hangi dokuyu verdiğidir. İlk yıllarda ben de spec tablolarına bakıyordum; bugün önce makinenin çektiği kareye bakıyorum. Bu liste de o mantıkla kuruldu — markaya göre değil, <strong>ne istediğine göre</strong>.</p>
<p>Aşağıdaki modellerin hepsi satıştan önce test edilmiş ve çalışır durumda. Bütçe ve istediğin tona göre seç.</p>

<h2>Hızlı karşılaştırma</h2>
{TW_OPEN}{TH('Model','Karakter','Kime uygun')}
<tbody>
{TR('<a href="/products/canon-powershot-sd400">Canon PowerShot SD400</a>','Dengeli, temiz Y2K rengi','İlk digicam alacaklar')}
{TR('<a href="/products/fujifilm-finepix-t200">Fujifilm FinePix T200</a>','Filmsi, yumuşak ton','Pastel/film look sevenler')}
{TR('<a href="/products/canon-ixus-160">Canon IXUS 160</a>','Hızlı, sağlam, net','Sosyal medya içeriği')}
{TR('<a href="/products/casio-exilim-ex-z50">Casio Exilim EX-Z50</a>','Sıcak, karakterli CCD','Bütçe dostu karakter')}
{TR('<a href="/products/canon-powershot-g7">Canon PowerShot G7</a>','Manuel kontrol, retro-pro','Ciddi çekim yapanlar')}
{TW_CLOSE}

<h2>Markaya göre öne çıkanlar</h2>
<h3>Canon — en dengeli renk</h3>
<p>Canon'un IXUS ve PowerShot serisi, "yanlış yapmak istemiyorum" diyenler için en güvenli liman. <a href="/products/canon-powershot-sd400">Canon PowerShot SD400</a> ince metal gövdesi ve o döneme has yumuşak geçişleriyle tam bir klasik. Daha sağlam ve hızlı bir gündelik makine istiyorsan <a href="/products/canon-ixus-160">Canon IXUS 160</a> taşıması rahat, çekimi hızlı.</p>
<h3>Fujifilm — en filmsi ton</h3>
<p>Fuji'nin renk bilimi efsane; FinePix serisi en "analog" hisli karelerin kapısı. <a href="/products/fujifilm-finepix-t200">Fujifilm FinePix T200</a> pastel ve sıcak tonları seven içerik üreticilerinin uygun fiyatlı favorisi.</p>
<h3>Casio — beklenmedik karakter</h3>
<p>Casio Exilim serisi yıllarca hafife alındı ama CCD sıcaklığını en saf haliyle veren modeller burada. <a href="/products/casio-exilim-ex-z50">Casio Exilim EX-Z50</a> fiyatına göre şaşırtıcı derecede karakterli kareler üretiyor.</p>

<h2>Sık sorulan sorular</h2>
<h3>En iyi CCD digicam markası hangisi?</h3>
<p>Tek bir doğru yok. Canon dengeli ve güvenilir renk verir, Fujifilm en filmsi tonlara sahiptir, Casio ise uygun fiyata karakter sunar. İçeriğinin tonuna göre seçmek, markaya bağlı kalmaktan daha doğru bir yaklaşımdır.</p>
<h3>Kaç megapiksel yeterli?</h3>
<p>CCD digicam'lerde megapiksel neredeyse hiç önemli değil. 5-12 MP arası modeller sosyal medya ve baskı için fazlasıyla yeterli. Önemli olan sensörün rengi ve karakteridir, çözünürlük değil. Yüksek megapiksel kovalamak bu kameralarda anlamsızdır.</p>
<h3>Yeni mi ikinci el mi almalıyım?</h3>
<p>CCD digicam'ler artık üretilmiyor; hepsi ikinci el. Bu yüzden en kritik konu makinenin test edilmiş ve çalışır olması. Satıştan önce test edilen, kondisyonu şeffaf paylaşılan bir kaynaktan almak riski sıfıra yakın indirir.</p>

<h2>Özetle</h2>
<p>İlk makineni arıyorsan Canon SD400 ya da Fuji T200 ile güvenli başla; karakter ve bütçe önemliyse Casio EX-Z50'ye bak; manuel kontrol istiyorsan Canon G7 seni tatmin eder. <a href="/collections/all">Tüm koleksiyonu</a> inceleyip örnek karelerle hangisinin sana uyduğunu görebilirsin.</p>
"""))

# ─────────────────────────────────────────────────────────────────────────────
# #3 — 10.000 TL Altı En Estetik Retro Dijital Kameralar
# ─────────────────────────────────────────────────────────────────────────────
ARTICLES.append(dict(
    title="10.000 TL Altı En Estetik Retro Dijital Kameralar",
    handle="10000-tl-alti-retro-dijital-kameralar",
    tags="ucuz retro kamera, 10000 tl kamera, bütçe digicam, Y2K kamera, retro dijital kamera",
    meta="10.000 TL altı en estetik retro dijital kameralar: düşük bütçeyle Y2K ve CCD estetiğini yakalayabileceğin test edilmiş digicam önerileri.",
    image="affordable retro digital cameras under budget on pastel background, Fujifilm Canon Casio compact digicam, Y2K aesthetic, nostalgic film grain",
    body=f"""
<h2>10.000 TL Altı En Estetik Retro Dijital Kameralar</h2>
<p>"Bütçem kısıtlı ama o retro görüntüyü istiyorum" — bu cümleyi yüzlerce kez duydum ve her seferinde aynı şeyi söyledim: o estetik için pahalı makineye gerek yok. CCD sensörün sıcak rengi 8.000 TL'lik bir gövdede de var, 30.000 TL'lik bir gövdede de. İlk digicam'imi düşük bütçeyle almıştım ve hâlâ en sevdiğim karelerin bazıları o makineden çıktı. Bu liste, az parayla en çok karakteri veren modeller için.</p>

<h2>10.000 TL altı öne çıkanlar</h2>
{TW_OPEN}{TH('Model','Yaklaşık fiyat','Neden bu liste')}
<tbody>
{TR('<a href="/products/fujifilm-finepix-1700z">Fujifilm FinePix 1700Z</a>','~8.500 TL','Erken dönem Fuji, ham nostaljik doku')}
{TR('<a href="/products/canon-powershot-a480">Canon PowerShot A480</a>','~9.500 TL','Basit, güvenilir, temiz Canon rengi')}
{TR('<a href="/products/casio-exilim-ex-z85">Casio Exilim EX-Z85</a>','~9.500 TL','Ucuz ama karakterli CCD tonu')}
{TR('<a href="/products/fujifilm-finepix-z10fd">Fujifilm FinePix Z10FD</a>','~9.990 TL','Renkli gövde, sosyal medya dostu')}
{TR('<a href="/products/agfa-optima-104">Agfa Optima 104</a>','~7.990 TL','Listenin en uygunu, nadir marka')}
{TW_CLOSE}

<h2>Hangisini seçmeli?</h2>
<h3>En filmsi ton istiyorsan</h3>
<p><a href="/products/fujifilm-finepix-1700z">Fujifilm FinePix 1700Z</a> erken dönem Fuji'nin o ham, işlenmemiş dokusunu verir; düşük megapiksel burada bir kusur değil, estetik. Daha modern ama yine sıcak bir Fuji istersen <a href="/products/fujifilm-finepix-z10fd">FinePix Z10FD</a> renkli gövdesiyle hem şık hem pratik.</p>
<h3>"Yanlış yapmak istemiyorum" diyorsan</h3>
<p><a href="/products/canon-powershot-a480">Canon PowerShot A480</a> bu bütçenin en güvenli seçimi — basit menü, temiz renk, AA pille çalışır (şarj derdi yok). İlk digicam için ideal.</p>
<h3>En düşük bütçe ama karakter şart diyorsan</h3>
<p><a href="/products/casio-exilim-ex-z85">Casio Exilim EX-Z85</a> ve <a href="/products/agfa-optima-104">Agfa Optima 104</a> listenin en uygunları; küçük bütçeyle CCD sıcaklığını yakalamanın en hızlı yolu.</p>

<h2>Sık sorulan sorular</h2>
<h3>Ucuz digicam kalitesiz mi olur?</h3>
<p>Hayır. CCD digicam'lerde fiyat çoğunlukla nadirlik ve gövde tasarımıyla ilgilidir, görüntü karakteriyle değil. 8.000 TL'lik bir makine de o filmsi, sıcak rengi verir. Önemli olan makinenin test edilmiş ve çalışır olmasıdır.</p>
<h3>Düşük megapiksel sorun olur mu?</h3>
<p>Sosyal medya ve normal baskı için olmaz. 4-8 MP arası modeller Instagram, TikTok ve hatta orta boy baskı için fazlasıyla yeterli. Retro estetikte düşük çözünürlük çoğu zaman görüntüye katkı bile sağlar.</p>
<h3>Pil ve hafıza kartı dahil mi?</h3>
<p>Kutu içeriği her üründe ayrı belirtilir. Bazı modeller AA pille çalışır (kart ve pil bulması kolay), bazıları özel pil ister. Satın almadan önce ürün sayfasındaki kutu içeriği notuna bakman yeterli.</p>

<h2>Özetle</h2>
<p>Retro görüntü için bütçe bir engel değil. Filmsi ton istiyorsan Fuji 1700Z, güvenli başlangıç istiyorsan Canon A480, en uygun fiyat istiyorsan Casio EX-Z85 ya da Agfa Optima 104. <a href="/collections/all">Koleksiyonun tamamını</a> gözden geçirip stoktaki uygun fiyatlı makineleri görebilirsin.</p>
"""))

# ─────────────────────────────────────────────────────────────────────────────
# #11 — Digicam Fiyatları 2026
# ─────────────────────────────────────────────────────────────────────────────
ARTICLES.append(dict(
    title="Digicam Fiyatları 2026: Ne Kadara Alınır?",
    handle="digicam-fiyatlari-2026",
    tags="digicam fiyatları, retro kamera fiyat, CCD kamera fiyat, dijital kamera fiyatları 2026",
    meta="Digicam fiyatları 2026: retro dijital kamera ne kadara alınır? Bütçe bandlarına göre güncel CCD digicam fiyat rehberi ve örnek modeller.",
    image="vintage digital cameras arranged by price tiers on neutral background, retro CCD compact cameras, clean editorial product photography, Y2K aesthetic",
    body=f"""
<h2>Digicam Fiyatları 2026: Ne Kadara Alınır?</h2>
<p>"Bu makineler neden bu kadar pahalandı?" sorusu bana en sık gelen sorulardan biri. 2026'da retro digicam fiyatları, birkaç yıl öncesine göre belirgin yükseldi — çünkü artık üretilmiyorlar, stok sınırlı ve TikTok/Instagram talebi patladı. Ben de çarşıda yıllar içinde aynı modelin fiyatının ikiye katlandığını gördüm. Bu rehber, hangi bütçeyle ne alabileceğini netleştirsin diye.</p>
<p>Kısaca: çalışır, test edilmiş bir retro digicam'in giriş bandı bugün <strong>~8.000 TL</strong>'den başlıyor; karakterli orta segment <strong>11.000–16.000 TL</strong>, nadir ve premium modeller ise <strong>20.000 TL üzeri</strong>.</p>

<h2>Bütçe bandlarına göre fiyatlar</h2>
{TW_OPEN}{TH('Bütçe', 'Ne alınır', 'Örnek model')}
<tbody>
{TR('8.000–10.000 TL','Giriş seviyesi, basit CCD','<a href="/products/fujifilm-finepix-1700z">Fuji FinePix 1700Z</a>, <a href="/products/canon-powershot-a480">Canon A480</a>')}
{TR('10.000–13.000 TL','Karakterli orta segment','<a href="/products/canon-powershot-sd400">Canon SD400</a>, <a href="/products/casio-exilim-ex-z50">Casio EX-Z50</a>')}
{TR('13.000–17.000 TL','Sağlam gövde / manuel kontrol','<a href="/products/canon-ixus-160">Canon IXUS 160</a>, <a href="/products/canon-powershot-g7">Canon G7</a>')}
{TR('20.000 TL+','Nadir / premium modeller','<a href="/products/canon-ixus-285-hs">Canon IXUS 285 HS</a>')}
{TW_CLOSE}

<h2>Fiyatı ne belirliyor?</h2>
<p>Bir digicam'in fiyatı megapikseliyle değil, üç şeyle belirlenir: <strong>nadirlik</strong> (kaç tane kaldı), <strong>kondisyon</strong> (çalışıyor mu, kozmetik durumu) ve <strong>talep</strong> (sosyal medyada popüler mi). Bu yüzden 5 megapiksel bir makine, 16 megapiksel bir başkasından pahalı olabilir. Test edilmiş ve çalışır garantili bir makine, "ucuz ama belki bozuk" bir ilandan her zaman daha mantıklıdır.</p>

<h2>Sık sorulan sorular</h2>
<h3>Retro digicam fiyatları neden artıyor?</h3>
<p>Bu kameralar artık üretilmiyor; mevcut stok sınırlı ve azalıyor. Aynı zamanda TikTok ve Instagram'da Y2K estetiğinin popülerleşmesi talebi ciddi artırdı. Arz sabit, talep yüksek olunca fiyatlar yükseliyor — özellikle temiz, çalışır örneklerde.</p>
<h3>En ucuz çalışır digicam ne kadar?</h3>
<p>2026 itibarıyla test edilmiş, çalışır bir giriş seviyesi CCD digicam yaklaşık 8.000 TL'den başlıyor. Bunun altındaki ilanlar genelde test edilmemiş ya da sorunlu makineler oluyor; bu yüzden çok düşük fiyatlara temkinli yaklaşmak gerekiyor.</p>
<h3>Pahalı model her zaman daha mı iyi çeker?</h3>
<p>Hayır. Yüksek fiyat çoğunlukla nadirlik ve gövde tasarımıyla ilgilidir, görüntü kalitesiyle değil. 10.000 TL'lik bir Casio, 20.000 TL'lik bir modelden daha karakterli kareler verebilir. Önemli olan istediğin tona uyan sensör, fiyat etiketi değil.</p>

<h2>Özetle</h2>
<p>2026'da retro digicam almak için makul bir başlangıç bütçesi 10.000–13.000 TL; bu bandda hem karakter hem güven var. Daha düşük bütçeyle de mümkün, sadece test edilmiş bir kaynaktan al. Güncel fiyatları ve stoğu <a href="/collections/all">koleksiyon sayfamızdan</a> canlı görebilirsin.</p>
"""))


if __name__ == '__main__':
    results = []
    for i, a in enumerate(ARTICLES, 1):
        print(f"\n=== {i}/{len(ARTICLES)}: {a['title']} ===")
        art_id, handle = publish_article(
            a['title'], a['handle'], a['tags'], a['body'].strip(),
            a['meta'], a['image'], a['handle'] + ".jpg")
        results.append((a['title'], handle))
    print("\n\n=== YAYINLANANLAR ===")
    for t, h in results:
        print(f"- {t}\n  https://retrocameraland.com/blogs/retro-dijital-kamera/{h}")
