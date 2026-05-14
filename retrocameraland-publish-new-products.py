#!/usr/bin/env python3
"""
Son eklenen 5 ürün için blog yazılarını Shopify'a yayınlar.
Çalıştır: python3 retrocameraland-publish-new-products.py
"""
import sys
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log, SOCIAL_BLOCK, CTA_BLOCK

BLOG_ID = "91197866123"


def publish_with_product_image(title, handle, tags, body_html, meta_desc, image_src):
    full_html = body_html + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    payload = {
        "article": {
            "title": title,
            "body_html": full_html,
            "handle": handle,
            "tags": tags,
            "published": True,
            "metafields": [
                {"namespace": "seo", "key": "description", "value": meta_desc, "type": "single_line_text_field"},
                {"namespace": "seo", "key": "title",       "value": title,    "type": "single_line_text_field"},
            ]
        }
    }
    if image_src:
        payload["article"]["image"] = {"src": image_src, "alt": title}
    resp = shopify("POST", f"blogs/{BLOG_ID}/articles.json", payload)
    art = resp["article"]
    log(f"  ✅ ID:{art['id']} → {art['handle']}")
    return art["id"], art["handle"]

POSTS = [
    {
        "title": "JVC GZ-MC200E İncelemesi: Mikro Kaset ve Fotoğraf Bir Arada Gelen Dijital Efsane",
        "handle": "jvc-gz-mc200e-inceleme-mikro-kaset-retro-kamera",
        "tags": "JVC, retro kamera inceleme, dijital kamera, y2k kamera, JVC GZ-MC200E",
        "meta_desc": "JVC GZ-MC200E incelemesi: Küp formlu bu eşsiz cihaz hem video hem fotoğraf çekiyor. 2000'lerin en ilginç hibrit kamerası hakkında her şey.",
        "image_src": "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/jvc_gz_mc200e.jpg?v=1776634747",
        "body": """
<p>Bazı cihazlar var, bir türe sığmaz. JVC GZ-MC200E de tam olarak böyle bir cihaz — ne sadece kamera, ne sadece video. İkisi aynı anda, tek gövdede.</p>

<h2>JVC GZ-MC200E Nedir?</h2>
<p>2003 yılında piyasaya çıkan <strong>JVC GZ-MC200E</strong>, Micro MV kaset formatıyla video çekerken aynı anda 2MP çözünürlükte fotoğraf da kaydedebilen hibrit bir dijital cihaz. Dönemin teknoloji dergileri "kamera mı, video mu?" sorusunu yanıtlayamadı — çünkü cevap ikisi birden.</p>

<p>Küp formundaki kompakt gövdesiyle çantada en az yer kaplayan video+fotoğraf kombinasyonu unvanını uzun yıllar elinde tuttu. Bugün koleksiyoncular arasında nadir bulunan ve çalışır durumdaki örnekleri hızla değer kazanan bir model.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Format:</strong> Micro MV Kaset</li>
<li><strong>Fotoğraf Çözünürlüğü:</strong> 2.0 Megapiksel</li>
<li><strong>Optik Zoom:</strong> 10x</li>
<li><strong>Ekran:</strong> 2.5" renkli LCD</li>
<li><strong>Bağlantı:</strong> USB, AV çıkışı</li>
<li><strong>Boyut:</strong> Gerçek anlamda avuç içi — 80 x 80 x 62 mm</li>
</ul>

<h2>Y2K Koleksiyonunda Neden Özel Bir Yeri Var?</h2>
<p>JVC GZ-MC200E, standart bir retro kamera değil. Micro MV kasetten video çekip aynı anda fotoğraf arşivi oluşturabilmesi, 2003 için harika bir mühendislik harikasıydı. Bugün bu kaseti oynatacak cihaz bulmak da neredeyse imkânsız — bu da GZ-MC200E'yi saf bir koleksiyon objesi konumuna taşıyor.</p>

<p>Küp formlu siyah plastik gövdesi, dönemin Sony Mavica serisiyle kıyaslanabilir bir "müze parçası" statüsüne ulaşmış durumda.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>2000'ler teknoloji nostalji koleksiyonu kuranlar</li>
<li>JVC veya Micro MV format meraklıları</li>
<li>Hibrit cihaz tarihi araştıranlar</li>
<li>Y2K estetik koleksiyoncuları</li>
</ul>

<p>Çalışır durumda, orijinal görünümünü koruyan bir örnek için aşağıdaki bağlantıya göz atabilirsin.</p>

<div style="text-align:center;margin:40px 0;">
<a href="https://retrocameraland.com/products/jvc-gz-mc200e" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">JVC GZ-MC200E'yi İncele →</a>
</div>
"""
    },
    {
        "title": "Canon PowerShot SD400 İncelemesi: Mini Elde Dev Performans, Retro Kompaktın Gözdesi",
        "handle": "canon-powershot-sd400-inceleme-retro-kompakt-kamera",
        "tags": "Canon, Canon PowerShot SD400, retro kamera inceleme, kompakt dijital kamera, y2k kamera",
        "meta_desc": "Canon PowerShot SD400 incelemesi: 2005'in en ince kompakt kamerası. DIGIC II işlemci, 5MP çözünürlük ve alüminyum gövde. Retro koleksiyonların vazgeçilmezi.",
        "image_src": "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Canon_PowerShot_SD400.jpg?v=1776634523",
        "body": """
<p>2005 yılında Canon'un "bu kadar küçük gövdeye bu kadar performans nasıl sığdı?" dedirten cevabıydı. <strong>Canon PowerShot SD400</strong>, IXUS serisinin Amerika versiyonu — ve bugün retro kompakt koleksiyonlarının en çok aranan modellerinden biri.</p>

<h2>Canon PowerShot SD400 Nedir?</h2>
<p>SD400, Canon'un ikonik Digital ELPH / IXUS ailesinin 2005 model yılı temsilcisi. Ultra ince alüminyum gövdesi, DIGIC II görüntü işlemcisi ve 5 megapiksellik CCD sensörüyle döneminin en dengeli kompakt kamerası unvanını kazandı.</p>

<p>Gümüş alüminyum kasası bugün hâlâ prestijli duruyor — parmak izine dirençli yüzeyi, düğme yerleşimi ve dönemin en iyi LCD ekranlarından biri ile tasarım açısından kusursuz bir koleksiyon objesi.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 5.0 MP CCD</li>
<li><strong>İşlemci:</strong> DIGIC II</li>
<li><strong>Optik Zoom:</strong> 3x (37–111mm eşdeğer)</li>
<li><strong>Ekran:</strong> 1.8" TFT LCD</li>
<li><strong>Hafıza:</strong> SD kart</li>
<li><strong>Boyut:</strong> 86.8 x 57.2 x 17.3 mm (gerçekten ultra ince)</li>
</ul>

<h2>CCD Renk Tonu: Dijital Filtre Değil, Gerçek Karakteri</h2>
<p>SD400'ün 5MP CCD sensörü, bugünkü akıllı telefon kameraların asla taklit edemeyeceği bir renk karakteri üretiyor. Sıcak tonlar, doğal cilt renkleri, hafif gren — bu "kusurlar" aslında fotoğraflarınıza benzersiz bir kimlik kazandırıyor.</p>

<p>Preset filtreler değil, gerçek donanım karakteri. Vintage look için Lightroom preset almana gerek yok; SD400 bunu otomatik yapıyor.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>CCD renk tonu seven retro fotoğrafçılar</li>
<li>Canon IXUS / Digital ELPH seri koleksiyoncuları</li>
<li>Ultra kompakt ve taşınabilir retro kamera arayanlar</li>
<li>Y2K estetik içerik üreticileri</li>
</ul>

<div style="text-align:center;margin:40px 0;">
<a href="https://retrocameraland.com/products/canon-powershot-sd400" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon PowerShot SD400'ü İncele →</a>
</div>
"""
    },
    {
        "title": "Nikon Coolpix S52c İncelemesi: Metal Şıklık, Wi-Fi ve CCD Renk Tonu Bir Arada",
        "handle": "nikon-coolpix-s52c-inceleme-metal-retro-dijital-kamera",
        "tags": "Nikon, Nikon Coolpix S52c, retro kamera inceleme, dijital kamera, y2k kamera, Nikon Coolpix",
        "meta_desc": "Nikon Coolpix S52c incelemesi: 9MP CCD, Wi-Fi ve ince metal gövde. 2008'in en şık kompakt kamerası bugün retro koleksiyonların parlayan yıldızı.",
        "image_src": "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/nikon_coolpix_s52c_6be43bae-02dc-4161-812b-1994de37f5c8.jpg?v=1776634318",
        "body": """
<p>Bazı kameralar sadece fotoğraf çekmez; üzerinde taşıdığın tarzı da yansıtır. <strong>Nikon Coolpix S52c</strong>, tam olarak bu hissi veren modellerden biri — ince metal gövdesi, premium düğme yerleşimi ve döneminin en gelişmiş özellik setiyle bugün de dikkat çekiyor.</p>

<h2>Nikon Coolpix S52c Nedir?</h2>
<p>2008 yılında piyasaya çıkan S52c, Nikon'un S serisi kompakt kameralarının zirvelerinden biri. 9.1 megapiksel CCD sensör, Wi-Fi ile doğrudan fotoğraf paylaşımı (dönemine göre inanılmaz!) ve ince alüminyum gövdesiyle döneminin en premium kompakt kameraları arasındaydı.</p>

<p>"c" harfi connectivity'den geliyor — yani akıllı telefon olmadan, kameradan doğrudan online fotoğraf gönderme. 2008 için bu gerçekten devrimci bir özellikti.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 9.1 MP CCD</li>
<li><strong>Optik Zoom:</strong> 3x (35–105mm eşdeğer)</li>
<li><strong>Ekran:</strong> 3.0" LCD (dönemine göre büyük!)</li>
<li><strong>Bağlantı:</strong> Wi-Fi 802.11b/g, USB</li>
<li><strong>Yüz Tanıma:</strong> Var (o dönem için gelişmiş)</li>
<li><strong>Gövde:</strong> Metal, ince profil</li>
</ul>

<h2>9MP CCD ile Retro Görüntü Kalitesi</h2>
<p>S52c'nin CCD sensörü, modern CMOS sensörlerden çok farklı bir renk karakteri sunuyor. Doygun ama doğal tonlar, hafif vinyetting efekti, deri dokusunu yumuşatan işleme algoritması — bunlar bugün hiçbir Lightroom preset'inin birebir kopyalayamadığı gerçek donanım özellikleri.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Metal gövdeli premium retro kamera arayanlar</li>
<li>Nikon Coolpix S serisi koleksiyoncuları</li>
<li>Yüksek çözünürlüklü CCD fotoğraf seven retro fotoğrafçılar</li>
<li>Teknoloji tarihi meraklıları (Wi-Fi özellikli ilk kameralar)</li>
</ul>

<div style="text-align:center;margin:40px 0;">
<a href="https://retrocameraland.com/products/nikon-coolpix-s52c" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Nikon Coolpix S52c'yi İncele →</a>
</div>
"""
    },
    {
        "title": "Retro Kameranı Telefonuna Bağla: USB-C Kart Okuyucu ile Fotoğraflarını Saniyeler İçinde Aktar",
        "handle": "usb-c-kart-okuyucu-retro-kamera-fotograf-aktarma",
        "tags": "kart okuyucu, USB-C, SD kart, retro kamera aksesuar, fotoğraf aktarma",
        "meta_desc": "Retro dijital kameranı telefonuna bağlamanın en kolay yolu: USB-C 3'ü 1 arada kart okuyucu. SD, MicroSD ve USB desteğiyle tüm vintage kameralarla uyumlu.",
        "image_src": "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/sd_kart_okuyucu.jpg?v=1775047519",
        "body": """
<p>Sony Cyber-shot, Canon IXUS, Casio Exilim ile çektiğin o eşsiz CCD tonlarındaki fotoğraflar kamerada kalmasın. <strong>USB-C 3'ü 1 Arada Kart Okuyucu</strong> ile saniyeler içinde telefonuna veya bilgisayarına aktar.</p>

<h2>Neden Bir Kart Okuyucuya İhtiyacın Var?</h2>
<p>2000'lerin retro kameralarının büyük çoğunluğu USB kablosuyla bilgisayara bağlanıyor — ama bu her zaman pratik değil. Bazı modellerin kablosu kaybolmuş, bazıları sürücü istiyor, bazılarının pili bitince bağlantı kopuyor.</p>

<p>Çözüm basit: SD kartı kameradan çıkar, kart okuyucuya tak, telefonuna veya laptopuna bağla. Kablo yok, sürücü yok, şarj sorunu yok.</p>

<h2>Hangi Kameralarla Çalışır?</h2>
<ul>
<li><strong>SD kart kullananlar:</strong> Canon IXUS, PowerShot, Nikon Coolpix, Olympus, Panasonic Lumix serileri</li>
<li><strong>MicroSD kullananlar:</strong> Bazı Casio Exilim ve Sony modelleri</li>
<li><strong>USB flash disk:</strong> Direkt veri transferi için</li>
</ul>

<h2>Özellikler</h2>
<ul>
<li><strong>Bağlantı:</strong> USB-C (MacBook, iPad Pro, Android telefon, Windows laptop uyumlu)</li>
<li><strong>Desteklenen Kartlar:</strong> SD / SDHC / SDXC, MicroSD / MicroSDHC / MicroSDXC</li>
<li><strong>Ek Slot:</strong> USB-A girişi (flash disk aktarımı)</li>
<li><strong>Hız:</strong> USB 3.0 destekli, hızlı transfer</li>
<li><strong>Boyut:</strong> Anahtar büyüklüğünde, çantada kaybolmaz</li>
</ul>

<h2>Retro Fotoğraf Akışını Kolaylaştırır</h2>
<p>Vintage kamera → SD kart → Kart okuyucu → Telefon/Laptop. Bu kadar. Fotoğraflarını Instagram'a, TikTok'a veya arşivine aktarmak için başka hiçbir şeye ihtiyacın yok. CCD renk tonlarını olduğu gibi koru, sadece boyut küçültmek veya hafif düzeltme için Lightroom kullan.</p>

<div style="text-align:center;margin:40px 0;">
<a href="https://retrocameraland.com/products/usb-c-3-in-1-kart-okuyucu-sd-microsd" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Kart Okuyucuyu İncele →</a>
</div>
"""
    },
    {
        "title": "Canon IXUS 160 İncelemesi: Zarif Tasarım, Pratik Kullanım ve Gerçek Retro Dijital Ruh",
        "handle": "canon-ixus-160-inceleme-retro-dijital-kompakt-kamera",
        "tags": "Canon, Canon IXUS 160, retro kamera inceleme, IXUS serisi, kompakt kamera, dijital kamera",
        "meta_desc": "Canon IXUS 160 incelemesi: İnce beyaz gövde, 20MP sensör ve DIGIC 4+ işlemci. Günlük kullanım için mükemmel retro kompakt kamerayı detaylıca inceledik.",
        "image_src": "https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Basliksiz-1_0012_ONN06831.jpg?v=1774467391",
        "body": """
<p>Büyük ekipman taşımadan, sadece anı yakalamak istediğin günler için mükemmel bir yoldaş. <strong>Canon IXUS 160 Beyaz</strong>, şık tasarımı ve pratik kullanımıyla retro dijital kamera koleksiyonuna doğal bir katkı.</p>

<h2>Canon IXUS 160 Nedir?</h2>
<p>Canon'un uzun soluklu IXUS serisinin 2015 model yılı temsilcisi olan IXUS 160, sadeliği ve güvenilirliği ön plana alan bir kompakt kamera. İnce beyaz alüminyum gövdesi, 20MP sensörü ve 8x optik zoom'uyla aile fotoğraflarından tatil çekimlerine, sokak fotoğrafçılığından yakın plan çekimlere kadar her senaryoda yeterli performansı sunuyor.</p>

<p>Bugün koleksiyon değeri kazanmaya başlayan IXUS 160, özellikle beyaz renk varyantıyla vintage estetik arayanların ilgisini çekiyor.</p>

<h2>Teknik Özellikler</h2>
<ul>
<li><strong>Sensör:</strong> 20.0 MP CCD</li>
<li><strong>İşlemci:</strong> DIGIC 4+</li>
<li><strong>Optik Zoom:</strong> 8x (28–224mm eşdeğer)</li>
<li><strong>Ekran:</strong> 2.7" LCD</li>
<li><strong>Video:</strong> 720p HD</li>
<li><strong>Hafıza:</strong> SD / SDHC / SDXC</li>
<li><strong>Pil Ömrü:</strong> ~180 kare (tek şarjla)</li>
</ul>

<h2>Neden Koleksiyonda Yer Almalı?</h2>
<p>IXUS 160, IXUS serisinin "son dönem" klasiklerinden biri. Canon'un bu seriden çekilmesiyle birlikte IXUS modelleri giderek koleksiyon değeri kazanıyor. Beyaz renk versiyonları özellikle nadir — çoğu koleksiyonda siyah veya gümüş bulunuyor.</p>

<p>Üstelik IXUS 160 hâlâ günlük kullanıma elverişli: SD kart okuma hızı yüksek, pil kolayca bulunuyor, arayüz sezgisel. Hem koleksiyon rafında güzel durur, hem de çekmeye devam eder.</p>

<h2>Kimler için İdeal?</h2>
<ul>
<li>Canon IXUS serisi koleksiyoncuları</li>
<li>Hem koleksiyona hem günlük çekime uygun kamera arayanlar</li>
<li>Beyaz / açık renkli kamera estetik arayanlar</li>
<li>20MP CCD kalitesiyle retro look fotoğraf seven içerik üreticileri</li>
</ul>

<div style="text-align:center;margin:40px 0;">
<a href="https://retrocameraland.com/products/canon-ixus-160" style="background:#1a1a1a;color:#fff;padding:14px 32px;border-radius:6px;text-decoration:none;font-weight:700;font-size:16px;">Canon IXUS 160'ı İncele →</a>
</div>
"""
    },
]


def run():
    results = []
    for i, p in enumerate(POSTS, 1):
        log(f"\n[{i}/{len(POSTS)}] {p['title'][:60]}...")
        try:
            aid, handle = publish_with_product_image(
                title=p["title"],
                handle=p["handle"],
                tags=p["tags"],
                body_html=p["body"],
                meta_desc=p["meta_desc"],
                image_src=p.get("image_src"),
            )
            results.append({"status": "ok", "id": aid, "handle": handle, "title": p["title"]})
        except Exception as e:
            log(f"  ❌ HATA: {e}")
            results.append({"status": "error", "title": p["title"], "error": str(e)})

    log("\n\n=== SONUÇ ===")
    for r in results:
        if r["status"] == "ok":
            log(f"  ✅ {r['title'][:55]} → /blogs/news/{r['handle']}")
        else:
            log(f"  ❌ {r['title'][:55]} → {r['error']}")

    ok = sum(1 for r in results if r["status"] == "ok")
    log(f"\n{ok}/{len(POSTS)} yazı başarıyla yayınlandı.")


if __name__ == "__main__":
    run()
