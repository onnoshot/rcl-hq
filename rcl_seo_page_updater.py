#!/usr/bin/env python3
"""RetroCameraLand — Shopify SEO Sayfa Güncelleyici"""

import json
import urllib.request
import urllib.error
import time

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"


def shopify_request(method, path, data=None):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.read().decode()[:300]}")
        raise


def update_page(page_id, title, body_html=None):
    data = {"page": {"id": page_id, "title": title}}
    if body_html is not None:
        data["page"]["body_html"] = body_html
    result = shopify_request("PUT", f"pages/{page_id}.json", data)
    print(f"  ✓ Başlık: {result['page']['title']}")


def upsert_metafield(page_id, namespace, key, value):
    existing = shopify_request("GET", f"pages/{page_id}/metafields.json")
    field = next(
        (m for m in existing.get("metafields", [])
         if m["namespace"] == namespace and m["key"] == key),
        None
    )
    if field:
        shopify_request("PUT", f"metafields/{field['id']}.json", {
            "metafield": {"id": field["id"], "value": value, "type": "single_line_text_field"}
        })
    else:
        shopify_request("POST", f"pages/{page_id}/metafields.json", {
            "metafield": {
                "namespace": namespace, "key": key,
                "value": value, "type": "single_line_text_field"
            }
        })
    print(f"  ✓ {namespace}.{key} metafield ayarlandı")


# ─── SAYFA VERİLERİ ──────────────────────────────────────────────────────────

PAGES = [
    {
        "id": 139501437067,
        "title": "Affiliate Programı | Creator İş Birliği | RetroCameraLand",
        "seo_title": "Creator Affiliate Programı | RetroCameraLand",
        "meta_description": "RetroCameraLand affiliate programına katıl, her satışta %5 komisyon kazan. Y2K dijital kamera topluluğuna dahil ol, içerik üret, kazanç sağla.",
        "body_html": """<div class="rcl-affiliate">
  <h1>RetroCameraLand Creator &amp; Affiliate Programı</h1>
  <p>RetroCameraLand olarak içerik üreticileriyle uzun vadeli, şeffaf ve keyifli iş birlikleri kuruyoruz. Y2K dijital kamera kültürünü yaratıcı içeriklerinizle büyütmenize destek olmak istiyoruz.</p>

  <h2>Affiliate Programı Nasıl Çalışır?</h2>
  <p>Süreç hızlı, basit ve tamamen sizin temposunuza uygun ilerler. <strong>Her onaylı satış için %5 komisyon</strong> kazanabilir; dilerseniz ürün deneyimi ve özel içerik fırsatlarına da dahil olabilirsiniz.</p>

  <h2>Creator Ortağı Olmanın Avantajları</h2>
  <ul>
    <li>Her onaylı satışta <strong>%5 nakit komisyon</strong></li>
    <li>Takipçilerinize özel indirim kodu</li>
    <li>Ücretsiz ürün deneyimi fırsatları</li>
    <li>İçerik kolaborasyon davetleri</li>
    <li>Şeffaf raporlama ve zamanında ödeme</li>
  </ul>

  <h2>Kimler Başvurabilir?</h2>
  <p>YouTube, Instagram, TikTok veya Pinterest'te fotoğraf, retro kamera veya Y2K kültürü üzerine içerik üretenler programa başvurabilir. Takipçi sayısından çok içerik kalitesine ve topluluğa katkıya bakıyoruz.</p>

  <h2>Nasıl Başvururum?</h2>
  <p>Instagram üzerinden <a href="https://www.instagram.com/retrocameraland" target="_blank">@retrocameraland</a>'e DM atarak başvurabilirsiniz. Topluluğumuzda seni görmekten mutluluk duyarız.</p>
</div>"""
    },
    {
        "id": 122706788491,
        "title": "Retro Dijital Kamera Aksesuarları | RetroCameraLand",
        "seo_title": "Retro Kamera Aksesuarları | RetroCameraLand",
        "meta_description": "Retro dijital kameranız için tüm aksesuarlar: bellek kartı okuyucu, şarj aleti, USB kablosu ve tripod. RetroCameraLand'de uygun fiyatlarla.",
        "body_html": """<div class="rcl-accessories">
  <h1>Retro Dijital Kamera Aksesuarları</h1>
  <p>Kameranızın performansını ve kullanım konforunu artıran aksesuarlar RetroCameraLand'de sizi bekliyor. Bellek kartı okuyucudan şarj aletine, tripoddan aktarım kablosuna kadar ihtiyacınız olan her şey burada.</p>

  <h2>Aksesuar Kategorileri</h2>
  <ul>
    <li><strong>Kart Okuyucu &amp; Adaptörler</strong> — SD, xD, CF ve diğer eski kart formatları için okuyucular</li>
    <li><strong>Şarj Aleti &amp; Batarya</strong> — Orijinal veya uyumlu şarj cihazları ve yedek bataryalar</li>
    <li><strong>USB &amp; Aktarım Kabloları</strong> — Kameradan bilgisayara hızlı fotoğraf aktarımı</li>
    <li><strong>Tripod &amp; Standlar</strong> — Masaüstü ve tam boy tripodlar</li>
    <li><strong>Çanta &amp; Kılıf</strong> — Kameranızı koruyan taşıma çantaları</li>
  </ul>

  <h2>Hangi Aksesuar Bana Uygun?</h2>
  <p>2000'li yılların dijital kameralarının çoğu artık standart dışı batarya veya bellek kartı kullanır. Doğru aksesuar seçimi kameranızın uzun süre sorunsuz çalışması için kritik öneme sahiptir.</p>
  <p>Hangi aksesuarın kameranıza uyduğundan emin değilseniz Instagram üzerinden bize ulaşın; kısa sürede yanıt verelim.</p>

  <h2>Uyumlu Markalar</h2>
  <p>Kodak, Canon, Nikon, Olympus, Sony, Fujifilm, Pentax ve daha birçok retro dijital kamera markasına uyumlu aksesuarlar stoklarımızda bulunmaktadır.</p>
</div>"""
    },
    {
        "id": 123655585931,
        "title": "Çocuk Kamerası | Dijital Fotoğraf Makinesi Çocuklar İçin | RetroCameraLand",
        "seo_title": "Çocuk İçin Dijital Kamera | RetroCameraLand",
        "meta_description": "Çocuklar için dayanıklı, hafif ve kullanımı kolay dijital fotoğraf makineleri. RetroCameraLand'de çocuk kamerası modellerini uygun fiyatlarla keşfet.",
        "body_html": """<div class="rcl-kids">
  <h1>Çocuklar İçin Dijital Kamera</h1>
  <p>Çocuğunuzun yaratıcılığını ve görsel keşif yeteneğini fotoğrafla geliştirin. RetroCameraLand'deki çocuk kamerası modelleri; dayanıklı, hafif ve kullanımı kolay tasarımlarıyla küçük fotoğrafçılar için idealdir.</p>

  <h2>Çocuk Kamerası Seçerken Dikkat Edilmesi Gerekenler</h2>
  <ul>
    <li><strong>Dayanıklılık:</strong> Düşmeye ve çarpmaya dayanıklı gövde</li>
    <li><strong>Kolay Kullanım:</strong> Büyük butonlar, sezgisel arayüz</li>
    <li><strong>Hafif Tasarım:</strong> Küçük ellere uygun ağırlık ve boyut</li>
    <li><strong>Uzun Pil Ömrü:</strong> Uzun süre şarjsız kullanım</li>
    <li><strong>Görüntü Kalitesi:</strong> Net ve renkli fotoğraflar için yeterli çözünürlük</li>
  </ul>

  <h2>Kaç Yaşından İtibaren Kamera Kullanılabilir?</h2>
  <p>4–6 yaş arası çocuklar ilk dijital kameralarını kullanmaya başlayabilir. Bu yaş grubuna özel tasarlanmış modeller hem güvenli hem eğlencelidir. 8 yaş ve üzeri için daha gelişmiş özellikler sunan modeller de mevcuttur.</p>

  <h2>Neden RetroCameraLand?</h2>
  <p>Her ürün satışa sunulmadan önce titizlikle test edilir ve doğrulanır. Çocuğunuzun yaşına ve ilgi alanına göre doğru modeli bulmak için müşteri hizmetlerimizle iletişime geçebilirsiniz.</p>
</div>"""
    },
    {
        "id": 118761128075,
        "title": "Gizlilik Tercihleriniz | Çerez Ayarları | RetroCameraLand",
        "seo_title": "Gizlilik Tercihleriniz | RetroCameraLand",
        "meta_description": "RetroCameraLand gizlilik tercihlerinizi yönetin. Çerez tercihlerinizi ve kişisel veri paylaşım ayarlarınızı buradan güncelleyebilirsiniz.",
        "body_html": None,
    },
    {
        "id": 118761521291,
        "title": "KVKK Politikası | Kişisel Veri Koruma | RetroCameraLand",
        "seo_title": "KVKK Gizlilik Politikası | RetroCameraLand",
        "meta_description": "RetroCameraLand KVKK politikası. Kişisel verilerinizin nasıl toplandığını, işlendiğini ve korunduğunu öğrenin. 6698 sayılı Kanun kapsamında haklarınız.",
        "body_html": None,
    },
    {
        "id": 144965664907,
        "title": "Hakkımızda | Retro Dijital Kamera Uzmanı | RetroCameraLand",
        "seo_title": "Hakkımızda | Retro Dijital Kamera | RetroCameraLand",
        "meta_description": "RetroCameraLand; Kodak, Canon, Olympus gibi ikonik markaların 2000'li yıl dijital kameralarını test edip fotoğraf severlerle buluşturan Türkiye'nin retro kamera uzmanıdır.",
        "body_html": """<div class="rcl-about">
  <h1>RetroCameraLand Hakkında</h1>
  <p>Türkiye'nin dijital retro kamera uzmanı olarak 2000'li yılların ikonik kameralarını bulup test ederek fotoğraf severlerle buluşturuyoruz.</p>

  <h2>Biz Kimiz?</h2>
  <p>RetroCameraLand; Kodak, Canon, Nikon, Olympus, Sony, Fujifilm ve Pentax gibi markaların <strong>nadir, koleksiyonluk ve test edilmiş dijital kameralarını</strong> araştırıp Türkiye'deki fotoğraf severlere ulaştıran bir e-ticaret mağazasıdır.</p>
  <p>Her kamera satışa sunulmadan önce titizlikle incelenir, test edilir ve dürüst açıklamalarla listelenir. Alıcı ne aldığını tam olarak bilir.</p>

  <h2>Neden RetroCameraLand?</h2>
  <ul>
    <li><strong>Test Edilmiş Ürünler:</strong> Her kamera ekibimiz tarafından incelenir</li>
    <li><strong>Şeffaf Açıklamalar:</strong> Kusurlar ve kullanım izleri dürüstçe belirtilir</li>
    <li><strong>Hızlı &amp; Güvenli Kargo:</strong> Siparişiniz özenle paketlenir, hızla kargoya verilir</li>
    <li><strong>Aktif Topluluk:</strong> YouTube ve Instagram'daki içerik ekosistemi</li>
    <li><strong>Kolay İade:</strong> Memnun kalmazsanız sorunsuz iade süreci</li>
  </ul>

  <h2>Vizyonumuz</h2>
  <p>Dijital retro fotoğrafçılık kültürünü Türkiye'de büyütmek ve her fotoğraf severin elinde o dönemi yansıtan ikonik bir kamera olmasını sağlamak.</p>

  <h2>Bizi Takip Edin</h2>
  <p><a href="https://www.instagram.com/retrocameraland" target="_blank">Instagram</a> ve <a href="https://www.youtube.com/@RetroCameraLand" target="_blank">YouTube</a>'da bizi takip ederek retro kamera dünyasına dair içerikleri kaçırmayın.</p>
</div>"""
    },
    {
        "id": 119297998987,
        "title": "Hikayemiz | Y2K Dijital Kamera Kültürü | RetroCameraLand",
        "seo_title": "Hikayemiz | Y2K Kamera Kültürü | RetroCameraLand",
        "meta_description": "RetroCameraLand'in hikayesi: 2000'lerin dijital ruhu bugünün estetiğiyle. Kodak, Canon, Olympus — test edilmiş, koleksiyonluk retro dijital kameralar.",
        "body_html": """<div class="rcl-story">
  <h1>Hikayemiz: 2000'lerin Dijital Ruhu, Bugünün Estetiğiyle</h1>
  <p>Retro Camera Land, eski dijital kameraların zamansız estetiğini yeniden hayata döndürmek için kuruldu. 2000'li yılların ikonik dijital kompakt kameralarını buluyoruz, test ediyoruz ve fotoğraf severlerle buluşturuyoruz.</p>

  <h2>Y2K Kamerasının Sihri</h2>
  <p>Kodak, Canon, Nikon, Olympus, Sony, Fujifilm, Pentax ve daha birçok markanın <strong>nadir, temiz ve koleksiyonluk</strong> dijital modelleri bizde yeniden hayat buluyor. Bu kameralar yalnızca teknik birer araç değil; o dönemin ruhunu, dokusunu ve renk paletini taşıyan birer hikâye anlatıcısı.</p>

  <h2>Neden Bu Kameralar?</h2>
  <p>2000'li yılların dijital kompakt kameraları kendine özgü bir görsel dil üretir: hafif grenli dokular, sıcak ya da soğuk renk tonları, analog fotoğrafa yakın doğal bir yumuşaklık. Bu estetik bugünün içerik dünyasında yeniden moda oldu ve biz bu kültürü Türkiye'de büyütmeye kararlıyız.</p>

  <h2>Güvenden Doğan Bir Topluluk</h2>
  <p>Her kamera satışa sunulmadan önce titizlikle incelenir ve test edilir. Kusurlar açıkça belirtilir, fotoğraflar gerçeği yansıtır. RetroCameraLand'i tercih edenler ne aldıklarını tam olarak bilirler.</p>

  <h2>Birlikte Büyüyoruz</h2>
  <p>YouTube ve Instagram'da binlerce retro kamera meraklısıyla bir aradayız. Satın almak için değil, yalnızca paylaşmak ve keşfetmek için de bize katılabilirsin.</p>
</div>"""
    },
    {
        "id": 118690283659,
        "title": "İletişim & Destek | RetroCameraLand",
        "seo_title": "İletişim & Müşteri Desteği | RetroCameraLand",
        "meta_description": "RetroCameraLand ile iletişime geç. Sipariş, ürün, kargo veya iş birliği için bize ulaşın. Hızlı yanıt, güvenilir destek.",
        "body_html": """<div class="rcl-contact">
  <h1>İletişim &amp; Destek</h1>
  <p>Sipariş, ürün, kargo veya iş birliği konularında bize ulaşabilirsiniz. Ekibimiz en kısa sürede geri dönüş yapar.</p>

  <h2>Bize Ulaşın</h2>
  <p><strong>Instagram DM:</strong> <a href="https://www.instagram.com/retrocameraland" target="_blank">@retrocameraland</a></p>
  <p>En hızlı yanıt Instagram DM üzerinden verilmektedir. Şikâyet, soru ve iş birliği teklifleri için aynı adresi kullanabilirsiniz.</p>

  <h2>Sıkça Sorulan Sorular</h2>

  <h3>Kargo ne zaman gelir?</h3>
  <p>Siparişler genellikle 1–3 iş günü içinde kargoya verilir. Kargo süresi taşıyıcı ve bölgeye göre 1–3 iş günü ek süre alabilir. Ayrıntı için <a href="/pages/kargo-ve-iade">Kargo ve İade</a> sayfamızı inceleyin.</p>

  <h3>Kameramı nasıl satarım?</h3>
  <p><a href="/pages/kamerani-sat">Kameranı Sat</a> sayfamızdaki formu doldurarak kameranızın değerini öğrenebilirsiniz. Ekibimiz kısa sürede dönüş yapar.</p>

  <h3>İade nasıl yapılır?</h3>
  <p>14 gün içinde, ürün orijinal koşullarında iade edilebilir. İade talebi için bize Instagram DM üzerinden ulaşın. Detaylar için <a href="/pages/kargo-ve-iade">Kargo ve İade</a> politikamızı okuyun.</p>

  <h3>Creator veya affiliate iş birliği için ne yapmalıyım?</h3>
  <p><a href="https://www.instagram.com/retrocameraland" target="_blank">@retrocameraland</a>'e Instagram DM atabilirsiniz. <a href="/pages/affilate">Affiliate Programı</a> sayfamızı da incelemenizi öneririz.</p>
</div>"""
    },
    {
        "id": 144967893131,
        "title": "Kameranı Sat | İkinci El Retro Dijital Kamera | RetroCameraLand",
        "seo_title": "Kameranı Sat | Retro Dijital Kamera | RetroCameraLand",
        "meta_description": "Eski dijital kameranı sat! RetroCameraLand'de kameranı 1 dakikada değerlendir. Hızlı geri dönüş, güvenli süreç, adil fiyat.",
        "body_html": None,
    },
    {
        "id": 118762078347,
        "title": "Kargo ve İade Politikası | RetroCameraLand",
        "seo_title": "Kargo ve İade Politikası | RetroCameraLand",
        "meta_description": "RetroCameraLand kargo ve iade politikası. 14 gün iade hakkı. Hızlı kargo, kolay iade süreci ve mesafeli satış sözleşmesi bilgileri.",
        "body_html": None,
    },
    {
        "id": 143619948683,
        "title": "Bağlantılar | Instagram, YouTube, Pinterest | RetroCameraLand",
        "seo_title": "RetroCameraLand | Sosyal Medya Bağlantıları",
        "meta_description": "RetroCameraLand resmi sosyal medya hesapları: Instagram, YouTube, Pinterest ve resmi mağaza bağlantıları.",
        "body_html": None,
    },
]


def main():
    print("=== RetroCameraLand SEO Sayfa Güncelleyici ===\n")
    for page in PAGES:
        print(f"▶ {page['title']}")
        try:
            update_page(page["id"], page["title"], page.get("body_html"))
            upsert_metafield(page["id"], "global", "title_tag", page["seo_title"])
            upsert_metafield(page["id"], "global", "description_tag", page["meta_description"])
        except Exception as e:
            print(f"  ✗ HATA: {e}")
        print()
        time.sleep(0.6)

    print("=== Tüm sayfalar güncellendi ✓ ===")


if __name__ == "__main__":
    main()
