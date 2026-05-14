#!/usr/bin/env python3
import sys, time, urllib.request, urllib.error, json
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log, SOCIAL_BLOCK, CTA_BLOCK

BLOG_ID = "91197866123"

def publish_no_image(title, handle, tags, body_html, meta_desc):
    full_html = body_html + "\n" + SOCIAL_BLOCK + "\n" + CTA_BLOCK
    resp = shopify("POST", f"blogs/{BLOG_ID}/articles.json", {
        "article": {
            "title": title, "body_html": full_html,
            "handle": handle, "tags": tags, "published": True,
            "metafields": [
                {"namespace":"seo","key":"description","value":meta_desc,"type":"single_line_text_field"},
                {"namespace":"seo","key":"title","value":title,"type":"single_line_text_field"}
            ]
        }
    })
    art = resp["article"]
    log(f"  ✅ ID:{art['id']} → {art['handle']} (görselsiz)")
    return art["id"], art["handle"]

POSTS = [
    {
        "title": "Retro Kamera Koleksiyonculuğu: Vintage Dünyasına İlk Adım",
        "handle": "retro-kamera-koleksiyonculugu-vintage-dunyasina-giris",
        "tags": "retro kamera koleksiyonu, vintage kamera, kamera koleksiyoncusu, y2k koleksiyon, retrocameraland",
        "meta_desc": "Retro kamera koleksiyonculuğuna nasıl başlanır? Değerli modeller, saklama yöntemleri ve Türkiye'de retro kamera topluluğu hakkında her şey.",
        "body": """
<h2>Retro Kamera Koleksiyonculuğu Neden Popüler?</h2>
<p>Retro dijital kamera koleksiyonculuğu 2022-2025 yılları arasında dünya genelinde patladı. eBay verilerine göre 2000-2010 arası dijital kamera satışları bu dönemde %280 artış gösterdi. Türkiye'de de retro kamera toplulukları hızla büyüyor — çünkü bu kameralar hem nostaljik bir bağ hem estetik bir nesne hem de giderek artan koleksiyon değeri taşıyor.</p>
<h2>Hangi Retro Kameralar Değer Kazanıyor?</h2>
<ul>
<li><strong>Sony Mavica serisi:</strong> Floppy disk kullanan ilk dijital kameralar — müze değerinde</li>
<li><strong>Apple QuickTake 100/150:</strong> Apple'ın tek ve nadir dijital kamerası</li>
<li><strong>Casio QV-10:</strong> İlk tüketici LCD ekranlı dijital kamera (1995)</li>
<li><strong>Olympus C-2020Z:</strong> Erken dönem profesyonel kompakt, fotoğrafçı topluluklarında efsane</li>
</ul>
<h2>Koleksiyon Kurma Stratejisi</h2>
<ol>
<li><strong>Tema belirleyin:</strong> "Tüm Sony DSC modelleri" veya "Su geçirmez kameralar" gibi odaklı koleksiyonlar daha değerlidir</li>
<li><strong>Orijinal kutu ve aksesuarlar:</strong> Orijinal kutusunu korumanız değeri 2-3 katına çıkarır</li>
<li><strong>Çalışır durumda satın alın:</strong> Koleksiyonda yer alan her kamera çalışır olmalıdır</li>
</ol>
<h2>Koleksiyonu Nasıl Saklarsınız?</h2>
<ul>
<li>Silica gel ile nem kontrolü yapılan kamera çantası veya vitrini</li>
<li>Bataryaları çıkararak saklama (sızıntı kamerayı mahveder)</li>
<li>Doğrudan güneş ışığından uzak, 18-24°C arası sıcaklık</li>
<li>Her 3 ayda bir kamerayı açıp test edin</li>
</ul>
<h2>Türkiye'de Retro Kamera Topluluğu</h2>
<p><a href="https://retrocameraland.com/collections/all">Retrocameraland</a>, Türkiye'nin en kapsamlı retro dijital kamera koleksiyonunu sunan platform olarak bu topluluğun odak noktasına yerleşmiştir.</p>
<h2>Sık Sorulan Sorular</h2>
<h3>Koleksiyona ne kadar bütçeyle başlanır?</h3>
<p>₺1.000-₺3.000 arası bütçeyle 3-5 farklı modelden oluşan değerli bir koleksiyon kurulabilir.</p>
<h3>Retro kamera değer kazandı mı?</h3>
<p>Evet, 2020 sonrasında belirli modeller %200-500 değer artışı gösterdi. Bu trend devam etmektedir.</p>
"""},
    {
        "title": "Retro Kamera ile Yaz Tatili: Deniz, Güneş ve Y2K Estetiği",
        "handle": "retro-kamera-yaz-tatili-deniz-gunes-y2k-estetik",
        "tags": "yaz tatili retro kamera, deniz fotoğrafı, tatil fotoğrafçılık, y2k yaz, ege akdeniz fotoğraf, retrocameraland",
        "meta_desc": "Yaz tatilinde retro kamerayla deniz fotoğrafı çekmek: Ege ve Akdeniz kıyılarında Y2K estetik tatil belgelemesi için tam rehber.",
        "body": """
<h2>Neden Tatilde Retro Kamera?</h2>
<p>Akıllı telefon kameraları tatil fotoğraflarını mükemmelleştiriyor ama bu "mükemmellik" aynı zamanda duygusuzlaştırıyor. <strong>Retro kameranın</strong> aşırı pozlanmış güneş ışığı, yüzlerdeki mutlu bulanıklık ve suyun Y2K ton işlemesi, tatil anlarını gerçek hissiyatıyla aktarır.</p>
<h2>Su Geçirmez Modeller</h2>
<p>Olympus Stylus SW serisi veya Pentax Optio W serisi gibi su geçirmez modeller havuz ve sığ deniz için idealdir. Su geçirmez kamera yoksa normal modelleri ziplock poşet içinde taşıyabilirsiniz.</p>
<h2>Türkiye'nin En Fotojenik Tatil Bölgeleri</h2>
<table style="width:100%;border-collapse:collapse;margin:20px 0;">
<tr style="background:#f0ebe4;"><th style="padding:10px;text-align:left;">Bölge</th><th style="padding:10px;text-align:left;">Öne Çıkan Çekim</th></tr>
<tr><td style="padding:10px;border-bottom:1px solid #e8e0d8;">Ölüdeniz (Fethiye)</td><td style="padding:10px;">Turkuaz lagün, renk cümbüşü</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #e8e0d8;">Bodrum</td><td style="padding:10px;">Beyaz duvarlar, mavi panjurlar, yelkenliler</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #e8e0d8;">Kaş</td><td style="padding:10px;">Kristal su altı, tekne turları</td></tr>
<tr><td style="padding:10px;">Alaçatı</td><td style="padding:10px;">Renkli çiçekler, taş sokaklar, sörf</td></tr>
</table>
<h2>Yaz Fotoğrafçılığı için İpuçları</h2>
<ol>
<li><strong>Aşırı pozlamayı kucaklayın:</strong> Güneşe karşı çekim yapıldığında retro kameranın aşırı pozlaması mükemmel gökyüzü efekti verir</li>
<li><strong>Altın saat:</strong> Gün batımında Ege kıyısının renkleri retro kamerada film gibi görünür</li>
<li><strong>Gölge oyunları:</strong> Güneş şemsiyesi gölgesinde oturan arkadaşların çekimi — kontrastlı Y2K estetiği</li>
</ol>
<h2>Sık Sorulan Sorular</h2>
<h3>Retro kamera havuzda kullanılır mı?</h3>
<p>Olympus Stylus SW gibi su geçirmez modeller kullanılabilir. Normal modeller su geçirmez değildir.</p>
<h3>Tatilde batarya ne kadar sürer?</h3>
<p>Çoğu retro kamera 150-300 çekim yapar. Yedek batarya taşımanız önerilir.</p>
"""},
    {
        "title": "Sonbahar Fotoğrafçılığı: Retro Kamera ile Yaprak Döküm Sezonu",
        "handle": "sonbahar-fotografciligi-retro-kamera-yaprak-dokum-sezonu",
        "tags": "sonbahar fotoğraf, yaprak döküm fotoğrafçılık, retro kamera sonbahar, belgrad ormanı fotoğraf, y2k sonbahar, retrocameraland",
        "meta_desc": "Retro kamerayla sonbahar fotoğrafçılığı: yaprak döküm sezonunda en etkileyici Y2K estetik çekimler için lokasyonlar, teknikler ve ipuçları.",
        "body": """
<h2>Retro Kamera ve Sonbahar: Mükemmel Uyum</h2>
<p>Sonbahar, retro kameraların en iyi performans gösterdiği mevsimdir. Turuncu ve sarı yaprak tonları, retro kameranın doğal sıcak renk işlemesiyle birleşince film kalitesinde görüntüler ortaya çıkar. <strong>Y2K estetiğinin</strong> en çok beğenilen içeriklerinden biri sonbahar yürüyüşü belgeselleridir.</p>
<h2>Sonbahar için Retro Kamera Teknikleri</h2>
<p>Yaprakların arasından süzülen güneş ışığını kullanmak için kameranızı güneşe 45-90 derece açıyla yöneltin. Retro kameranın lens haleleri bu durumda büyülü hale efekti yaratır. Islak yapraklar ve yağmurlu arka planlar ise retro kamerada özellikle dramatik görünür.</p>
<h2>Türkiye'de Sonbahar Fotoğrafçılığı için Lokasyonlar</h2>
<ul>
<li><strong>Belgrad Ormanı (İstanbul):</strong> 5.500 hektar orman, sonbaharda sarı-kırmızı renk cümbüşü</li>
<li><strong>Abant Gölü (Bolu):</strong> Göl yansımaları ve sarı yapraklı huş ağaçları</li>
<li><strong>Yedigöller (Bolu):</strong> Türkiye'nin en güzel sonbahar fotoğraf destinasyonu</li>
<li><strong>Uludağ etekleri (Bursa):</strong> Sarı ginkgo yaprakları ve tarihi ahşap köprüler</li>
</ul>
<h2>Sonbahar İçerik Fikirleri</h2>
<ol>
<li>🍂 Sonbahar yürüyüşü vlog tarzı fotoğraf serisi</li>
<li>☕ Orman kafe + retro kamera flat lay</li>
<li>🌧️ Yağmurlu pencere arkasından şehir manzarası</li>
</ol>
<h2>Sık Sorulan Sorular</h2>
<h3>Yaprak dökümü için en iyi zaman?</h3>
<p>İstanbul için Ekim-Kasım, Bolu ve Abant için Eylül sonu-Ekim ideal dönemlerdir.</p>
"""},
    {
        "title": "Retro Kamera ile Mezuniyet Fotoğrafları: Unutulmaz Anlar için Rehber",
        "handle": "retro-kamera-mezuniyet-fotograflari-unutulmaz-anlar-rehberi",
        "tags": "mezuniyet fotoğrafı, retro kamera mezuniyet, lise üniversite mezuniyet, y2k mezuniyet, hediye retro kamera, retrocameraland",
        "meta_desc": "Mezuniyette retro kamerayla çekim rehberi: lise ve üniversite mezuniyetinde Y2K estetik fotoğrafçılık, hediye fikirleri ve özel anlar.",
        "body": """
<h2>Mezuniyet Fotoğrafçılığında Neden Retro Kamera?</h2>
<p>Mezuniyet, bir kez yaşanan ve fotoğrafların yıllar sonra defalarca bakılacağı nadir anlardan biridir. <strong>Retro kameranın</strong> gerçekçi, sıcak ve biraz deli çekimleri, o günün duygusunu çok daha güçlü aktarır. "Bu fotoğrafa baktığımda o anı hissediyorum" dedirten görüntüler retro kameradan çıkar.</p>
<h2>Mezuniyet Günü için Çekim Planı</h2>
<p>Cüppe giyim, saç-makyaj, aile buluşması anları — belgeleme tören başlamadan önce başlar. Diploma alma anında netlemeyi önceden ayarlayın. Kep atma anı için seri çekim modunu açın. Tören sonrası flaşlı kutlama fotoğrafları Y2K estetiğinin zirvesidir.</p>
<h2>Mezuniyet Hediyesi Olarak Retro Kamera</h2>
<p>Mezuniyete özel en özgün hediye fikirlerinden biri retro kamera. <a href="https://retrocameraland.com/collections/all">Retrocameraland koleksiyonunda</a> lise veya üniversite mezunu genç için ideal modeller bulunuyor.</p>
<ul>
<li>Mezuniyetten sonraki yeni hayat dönemini nostaljik olarak belgelemek için ideal</li>
<li>Y2K trendiyle uyumlu, Instagram ve TikTok için hazır estetik</li>
<li>Akıllı telefondan farklı, özgün ve dikkat çekici bir hediye</li>
</ul>
<h2>Sık Sorulan Sorular</h2>
<h3>Mezuniyet için en iyi retro kamera hangisi?</h3>
<p>Sony DSC-T serisi veya Canon IXUS 800 IS hem kapalı hem açık ortamda iyi performans verir.</p>
<h3>Mezuniyet fotoğraflarını baskıya vermeli miyim?</h3>
<p>Kesinlikle evet. Retro kameranın özgün estetiği baskıda çok daha güçlü etki yaratır.</p>
"""}
]

results = []
for i, p in enumerate(POSTS, 1):
    log(f"\n[{i}/{len(POSTS)}] {p['title'][:55]}...")
    try:
        aid, handle = publish_no_image(
            title=p["title"], handle=p["handle"], tags=p["tags"],
            body_html=p["body"], meta_desc=p["meta_desc"]
        )
        results.append({"status":"ok","id":aid,"handle":handle,"title":p["title"]})
    except Exception as e:
        log(f"  HATA: {e}")
        results.append({"status":"error","title":p["title"],"error":str(e)})
    if i < len(POSTS):
        time.sleep(2)

print("\n" + "="*60)
for r in results:
    if r["status"] == "ok":
        print(f"  ✅ ID:{r['id']} — {r['title'][:50]}")
    else:
        print(f"  ❌ {r['title'][:50]}: {r['error']}")
print(f"\nToplam: {sum(1 for r in results if r['status']=='ok')}/{len(results)} başarılı")
print("="*60)
