#!/usr/bin/env python3
"""
RCL Schema Markup Updater
- theme.liquid      → Organization + WebSite JSON-LD
- product-information.liquid → Brand + condition enhancement
- snippets/rcl-article-schema.liquid → Article + FAQPage (yeni)
- main-blog-post.liquid → snippet render
- FAQ sayfası → Shopify Pages API
"""
import sys, os
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log

THEME_ID = '147158499467'

def get_asset(key):
    r = shopify('GET', f'themes/{THEME_ID}/assets.json?asset[key]={key}')
    return r['asset'].get('value', '')

def put_asset(key, value):
    shopify('PUT', f'themes/{THEME_ID}/assets.json', {
        'asset': {'key': key, 'value': value}
    })
    log(f'  ✅ {key} güncellendi')

# ── 1. theme.liquid — Organization + WebSite schema ──────────────────────────
def update_theme_liquid():
    log('1/4 theme.liquid → Organization + WebSite schema ekleniyor...')
    content = get_asset('layout/theme.liquid')

    if 'rcl-org-schema' in content:
        log('  ℹ️  Zaten mevcut, atlanıyor')
        return

    SCHEMA = '''
  <!-- RCL: Organization + WebSite Schema — rcl-org-schema -->
  {% unless request.design_mode %}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://retrocameraland.com/#organization",
        "name": "RetroCameraLand",
        "url": "https://retrocameraland.com",
        "logo": {
          "@type": "ImageObject",
          "url": "https://retrocameraland.com/cdn/shop/files/rcl-logo.png",
          "width": 300,
          "height": 100
        },
        "description": "Türkiye'nin öncü retro ve vintage dijital kamera mağazası. Y2K estetik kameralar, CCD sensörlü kompakt dijital kameralar, 2000'ler dönemi retro fotoğraf makineleri.",
        "sameAs": [
          "https://www.instagram.com/retrocameraland/",
          "https://www.youtube.com/@RetroCameraLand",
          "https://www.tiktok.com/@retrocameraland",
          "https://pinterest.com/retrocameraland/",
          "https://www.linkedin.com/company/retro-camera-land/"
        ],
        "contactPoint": {
          "@type": "ContactPoint",
          "contactType": "customer service",
          "availableLanguage": ["Turkish", "English"]
        },
        "address": {
          "@type": "PostalAddress",
          "addressCountry": "TR",
          "addressLocality": "İstanbul"
        }
      },
      {
        "@type": "WebSite",
        "@id": "https://retrocameraland.com/#website",
        "url": "https://retrocameraland.com",
        "name": "RetroCameraLand — Retro Dijital Kamera Mağazası",
        "description": "Türkiye'de retro dijital kamera, Y2K estetik kamera ve vintage kompakt kamera satışı.",
        "publisher": {"@id": "https://retrocameraland.com/#organization"},
        "inLanguage": "tr-TR",
        "potentialAction": {
          "@type": "SearchAction",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://retrocameraland.com/search?q={search_term_string}"
          },
          "query-input": "required name=search_term_string"
        }
      }
    ]
  }
  </script>
  {% endunless %}
  <!-- /RCL: Organization + WebSite Schema -->
'''
    # </head>'den önce ekle
    new_content = content.replace('</head>', SCHEMA + '\n</head>', 1)
    put_asset('layout/theme.liquid', new_content)

# ── 2. product-information.liquid — Brand + Condition enhancement ─────────────
def update_product_schema():
    log('2/4 product-information.liquid → Brand + Condition ekleniyor...')
    content = get_asset('sections/product-information.liquid')

    if 'rcl-product-extra-schema' in content:
        log('  ℹ️  Zaten mevcut, atlanıyor')
        return

    EXTRA = '''
{%- comment -%}rcl-product-extra-schema: Brand + Condition + Breadcrumb{%- endcomment -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "{{ shop.url }}{{ product.url }}#product",
  "name": {{ product.title | json }},
  "description": {{ product.description | strip_html | truncate: 300 | json }},
  "brand": {
    "@type": "Brand",
    "name": {{ product.vendor | default: "RetroCameraLand" | json }}
  },
  "sku": {{ product.selected_or_first_available_variant.sku | default: product.id | json }},
  "itemCondition": "https://schema.org/UsedCondition",
  "url": "{{ shop.url }}{{ product.url }}",
  "image": [
    {% for img in product.images limit:3 %}
      "{{ img | image_url: width: 1200 }}"{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ],
  "offers": {
    "@type": "Offer",
    "@id": "{{ shop.url }}{{ product.url }}#offer",
    "url": "{{ shop.url }}{{ product.url }}",
    "priceCurrency": "TRY",
    "price": {{ product.price | divided_by: 100.0 | json }},
    "priceValidUntil": "{{ 'now' | date: '%Y' | plus: 1 }}-12-31",
    "availability": {% if product.available %}"https://schema.org/InStock"{% else %}"https://schema.org/OutOfStock"{% endif %},
    "seller": {
      "@type": "Organization",
      "name": "RetroCameraLand",
      "url": "https://retrocameraland.com"
    },
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": 0,
        "currency": "TRY"
      },
      "deliveryTime": {
        "@type": "ShippingDeliveryTime",
        "handlingTime": {
          "@type": "QuantitativeValue",
          "minValue": 1,
          "maxValue": 2,
          "unitCode": "DAY"
        },
        "transitTime": {
          "@type": "QuantitativeValue",
          "minValue": 1,
          "maxValue": 3,
          "unitCode": "DAY"
        }
      },
      "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "TR"
      }
    }
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": "https://retrocameraland.com"},
    {"@type": "ListItem", "position": 2, "name": "Tüm Ürünler", "item": "https://retrocameraland.com/collections/all"},
    {"@type": "ListItem", "position": 3, "name": {{ product.title | json }}, "item": "{{ shop.url }}{{ product.url }}"}
  ]
}
</script>
'''
    # Mevcut structured_data satırından sonra ekle
    old = '<script type="application/ld+json">\n  {{ closest.product | structured_data }}\n</script>'
    new = old + '\n' + EXTRA
    if old in content:
        new_content = content.replace(old, new, 1)
    else:
        # Fallback — başa ekle
        new_content = EXTRA + '\n' + content
    put_asset('sections/product-information.liquid', new_content)

# ── 3. snippets/rcl-article-schema.liquid — Yeni dosya ───────────────────────
def create_article_schema_snippet():
    log('3/4 snippets/rcl-article-schema.liquid oluşturuluyor...')

    SNIPPET = '''{% comment %}
  rcl-article-schema.liquid
  Article JSON-LD + FAQPage (JS ile h3 sorulardan dinamik)
{% endcomment %}
{% if article %}

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "{{ shop.url }}{{ article.url }}#article",
  "headline": {{ article.title | json }},
  "name": {{ article.title | json }},
  "description": {{ article.excerpt_or_content | strip_html | truncate: 160 | json }},
  "datePublished": "{{ article.published_at | date: '%Y-%m-%dT%H:%M:%S+03:00' }}",
  "dateModified": "{{ article.updated_at | date: '%Y-%m-%dT%H:%M:%S+03:00' }}",
  "url": "{{ shop.url }}{{ article.url }}",
  "inLanguage": "tr-TR",
  "author": {
    "@type": "Organization",
    "name": "RetroCameraLand",
    "url": "https://retrocameraland.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "RetroCameraLand",
    "url": "https://retrocameraland.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://retrocameraland.com/cdn/shop/files/rcl-logo.png"
    }
  },
  "image": {
    "@type": "ImageObject",
    "url": {% if article.image %}"{{ article.image | image_url: width: 1200 }}"{% else %}"https://retrocameraland.com/cdn/shop/files/rcl-og.jpg"{% endif %},
    "width": 1200,
    "height": 630
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ shop.url }}{{ article.url }}"
  },
  "isPartOf": {
    "@type": "Blog",
    "name": "RetroCameraLand Blog",
    "url": "{{ shop.url }}/blogs/{{ blog.handle }}"
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": "https://retrocameraland.com"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://retrocameraland.com/blogs/news"},
    {"@type": "ListItem", "position": 3, "name": {{ article.title | json }}, "item": "{{ shop.url }}{{ article.url }}"}
  ]
}
</script>

<script>
(function() {
  // FAQPage schema: yazıdaki h3 sorular + p cevaplardan dinamik oluştur
  function buildFAQSchema() {
    var content = document.querySelector(
      '.article-template__content, .blog-post-content, [class*="blog-post-content"], .rte'
    );
    if (!content) return;

    var headings = content.querySelectorAll('h3');
    if (headings.length < 2) return;

    var items = [];
    headings.forEach(function(h) {
      var q = h.textContent.trim();
      if (q.length < 8 || q.length > 250) return;

      var answerParts = [];
      var el = h.nextElementSibling;
      var limit = 0;
      while (el && el.tagName !== 'H2' && el.tagName !== 'H3' && limit < 5) {
        var txt = el.textContent.trim();
        if (txt.length > 10) answerParts.push(txt);
        el = el.nextElementSibling;
        limit++;
      }
      var answer = answerParts.join(' ').slice(0, 500).trim();
      if (answer.length > 20) {
        items.push({
          '@type': 'Question',
          'name': q,
          'acceptedAnswer': {'@type': 'Answer', 'text': answer}
        });
      }
    });

    if (items.length < 2) return;

    var schema = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      'mainEntity': items
    };

    var s = document.createElement('script');
    s.type = 'application/ld+json';
    s.textContent = JSON.stringify(schema, null, 0);
    document.head.appendChild(s);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildFAQSchema);
  } else {
    buildFAQSchema();
  }
})();
</script>

{% endif %}
'''
    put_asset('snippets/rcl-article-schema.liquid', SNIPPET)

# ── 4. main-blog-post.liquid — Snippet'i başa ekle ───────────────────────────
def update_blog_post_section():
    log('4/4 main-blog-post.liquid → rcl-article-schema snippet bağlanıyor...')
    content = get_asset('sections/main-blog-post.liquid')

    if "render 'rcl-article-schema'" in content:
        log('  ℹ️  Zaten mevcut, atlanıyor')
        return

    INSERT = "{%- render 'rcl-article-schema' -%}\n"
    new_content = INSERT + content
    put_asset('sections/main-blog-post.liquid', new_content)

# ── 5. FAQ Sayfası oluştur ────────────────────────────────────────────────────
def create_faq_page():
    log('5/5 FAQ sayfası oluşturuluyor...')

    # Sayfa zaten var mı kontrol et
    pages = shopify('GET', 'pages.json?handle=faq&fields=id,title,handle')
    for p in pages.get('pages', []):
        if 'sık' in p['title'].lower() or 'faq' in p['handle'].lower():
            log(f'  ℹ️  FAQ sayfası zaten mevcut: /pages/{p["handle"]}')
            return

    BODY = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type":"Question","name":"Retro dijital kamera nedir?","acceptedAnswer":{"@type":"Answer","text":"Retro dijital kamera, 2000'li yıllarda üretilmiş CCD sensörlü kompakt dijital kameralardır. Y2K estetiğiyle tanınan bu kameralar, grain dokulu ve sıcak tonlu fotoğraflar çeker. Sony Cyber-shot, Canon PowerShot, Fujifilm FinePix ve Canon IXUS serisi en popüler modellerdir."}},
    {"@type":"Question","name":"Y2K kamera ne demek?","acceptedAnswer":{"@type":"Answer","text":"Y2K kamera, 1999–2005 yılları arasında üretilen ve o dönemin karakteristik fotoğraf estetiğini yaratan CCD sensörlü dijital kameralardır. Yüksek doygunluk, film grain ve parlak renkler bu kameraların ayırt edici özelliğidir. Özellikle Instagram ve TikTok içerik üreticileri arasında popülerdir."}},
    {"@type":"Question","name":"Retrocameraland'den nasıl satın alabilirim?","acceptedAnswer":{"@type":"Answer","text":"retrocameraland.com adresimizden tüm koleksiyonumuzu inceleyebilir, sepetinize ekleyerek kredi kartı veya havale ile ödeme yapabilirsiniz. Tüm ürünler Türkiye'ye kargo ile gönderilmektedir."}},
    {"@type":"Question","name":"Kameralar garanti kapsamında mı?","acceptedAnswer":{"@type":"Answer","text":"Tüm kameralarımız satış öncesinde test edilmekte ve çalışır durumda olduğu doğrulanmaktadır. İkinci el ürünler oldukları için resmi garanti kapsam dışındadır; ancak teslimatta yaşanan sorunlarda 7 gün iade garantisi sunmaktayız."}},
    {"@type":"Question","name":"Hangi ödeme yöntemleri kabul ediliyor?","acceptedAnswer":{"@type":"Answer","text":"Kredi kartı (Visa, Mastercard, American Express), banka havalesi ve EFT ile ödeme yapabilirsiniz. Tüm ödemeler Shopify'ın güvenli altyapısı üzerinden işlenmektedir."}},
    {"@type":"Question","name":"Kargo süresi ne kadar?","acceptedAnswer":{"@type":"Answer","text":"Siparişler 1-2 iş günü içinde kargoya verilmektedir. Kargo süresi ise bulunduğunuz şehre göre 1-3 iş günüdür. Kargo takip numarası sipariş onayı sonrası e-posta ile iletilmektedir."}},
    {"@type":"Question","name":"En popüler retro kamera modelleri hangileridir?","acceptedAnswer":{"@type":"Answer","text":"Türkiye'de en çok aranan retro kamera modelleri: Sony Cyber-shot DSC-T9, Canon PowerShot SD400, Fujifilm FinePix T200, Canon IXUS serisi ve Fujifilm FinePix Z700 EXR'dir. Bu modeller Y2K estetiği için özellikle tercih edilmektedir."}},
    {"@type":"Question","name":"CCD kamera ile CMOS kamera arasındaki fark nedir?","acceptedAnswer":{"@type":"Answer","text":"CCD sensörlü kameralar, CMOS sensörlere kıyasla daha sıcak tonlar, yüksek renk doygunluğu ve karakteristik grain dokusu üretir. Bu özellikler Y2K ve retro fotoğraf estetiğinin temelini oluşturur. 2000'li yıllarda üretilen kompakt kameraların büyük çoğunluğu CCD sensör kullanır."}}
  ]
}
</script>

<h2>Retro Dijital Kamera Hakkında Sık Sorulan Sorular</h2>

<h3>Retro dijital kamera nedir?</h3>
<p>Retro dijital kamera, 2000'li yıllarda üretilmiş CCD sensörlü kompakt dijital kameralardır. Y2K estetiğiyle tanınan bu kameralar, grain dokulu ve sıcak tonlu fotoğraflar çeker. Sony Cyber-shot, Canon PowerShot, Fujifilm FinePix ve Canon IXUS serisi en popüler modellerdir.</p>

<h3>Y2K kamera ne demek?</h3>
<p>Y2K kamera, 1999–2005 yılları arasında üretilen ve o dönemin karakteristik fotoğraf estetiğini yaratan CCD sensörlü dijital kameralardır. Yüksek doygunluk, film grain ve parlak renkler bu kameraların ayırt edici özelliğidir. Özellikle Instagram ve TikTok içerik üreticileri arasında popülerdir.</p>

<h3>Retrocameraland'den nasıl satın alabilirim?</h3>
<p>retrocameraland.com adresimizden tüm koleksiyonumuzu inceleyebilir, sepetinize ekleyerek kredi kartı veya havale ile ödeme yapabilirsiniz. Tüm ürünler Türkiye'ye kargo ile gönderilmektedir.</p>

<h3>Kameralar garanti kapsamında mı?</h3>
<p>Tüm kameralarımız satış öncesinde test edilmekte ve çalışır durumda olduğu doğrulanmaktadır. İkinci el ürünler oldukları için resmi garanti kapsam dışındadır; ancak teslimatta yaşanan sorunlarda 7 gün iade garantisi sunmaktayız.</p>

<h3>Hangi ödeme yöntemleri kabul ediliyor?</h3>
<p>Kredi kartı (Visa, Mastercard, American Express), banka havalesi ve EFT ile ödeme yapabilirsiniz. Tüm ödemeler Shopify'ın güvenli altyapısı üzerinden işlenmektedir.</p>

<h3>Kargo süresi ne kadar?</h3>
<p>Siparişler 1-2 iş günü içinde kargoya verilmektedir. Kargo süresi ise bulunduğunuz şehre göre 1-3 iş günüdür. Kargo takip numarası sipariş onayı sonrası e-posta ile iletilmektedir.</p>

<h3>En popüler retro kamera modelleri hangileridir?</h3>
<p>Türkiye'de en çok aranan retro kamera modelleri: Sony Cyber-shot DSC-T9, Canon PowerShot SD400, Fujifilm FinePix T200, Canon IXUS serisi ve Fujifilm FinePix Z700 EXR'dir. Bu modeller Y2K estetiği için özellikle tercih edilmektedir.</p>

<h3>CCD kamera ile CMOS kamera arasındaki fark nedir?</h3>
<p>CCD sensörlü kameralar, CMOS sensörlere kıyasla daha sıcak tonlar, yüksek renk doygunluğu ve karakteristik grain dokusu üretir. Bu özellikler Y2K ve retro fotoğraf estetiğinin temelini oluşturur. 2000'li yıllarda üretilen kompakt kameraların büyük çoğunluğu CCD sensör kullanır.</p>
"""

    result = shopify('POST', 'pages.json', {
        'page': {
            'title': 'Sık Sorulan Sorular',
            'handle': 'faq',
            'body_html': BODY,
            'published': True,
        }
    })
    p = result.get('page', {})
    log(f'  ✅ FAQ sayfası oluşturuldu: /pages/{p.get("handle","?")} (ID: {p.get("id","?")})')

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    log('=== RCL Schema Updater başlıyor ===')
    update_theme_liquid()
    update_product_schema()
    create_article_schema_snippet()
    update_blog_post_section()
    create_faq_page()
    log('=== Tamamlandı ===')
