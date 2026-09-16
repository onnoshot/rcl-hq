#!/usr/bin/env python3
"""
RCL GEO/AEO Deploy — AI-arama görünürlüğü altyapısı
- templates/robots.txt.liquid → Shopify default kuralları + AI crawler'larına explicit Allow + llms.txt referansı
- /pages/llms-txt          → llms.txt içeriği (Shopify root /llms.txt servis edemez; sayfa + robots referansı ile çözülür)

Çalıştırma:  python3 rcl-geo-deploy.py            (CANLIYA yazar)
             python3 rcl-geo-deploy.py --dry      (sadece ne yazacağını gösterir)
"""
import sys
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import shopify, log

THEME_ID = '147158499467'
DRY = '--dry' in sys.argv

# AI arama motorlarını besleyen crawler'lar — content'i okumalarına explicit izin,
# hassas yolları (cart/checkout/admin) Shopify default'larıyla aynı şekilde kapalı tut.
AI_BOTS = [
    'GPTBot',          # ChatGPT eğitim/crawl
    'OAI-SearchBot',   # ChatGPT canlı arama
    'ChatGPT-User',    # ChatGPT tarama (kullanıcı tetikli)
    'ClaudeBot',       # Claude eğitim/crawl
    'Claude-Web',      # Claude canlı
    'anthropic-ai',    # Anthropic
    'PerplexityBot',   # Perplexity indeks
    'Perplexity-User', # Perplexity canlı
    'Google-Extended', # Gemini / AI Overviews
    'Applebot-Extended',
    'cohere-ai',
    'Bytespider',      # TikTok/Doubao
]

DISALLOW_PATHS = ['/admin', '/cart', '/orders', '/checkout', '/checkouts/',
                  '/carts', '/account', '/*/account', '/services/', '/*?*sort_by*',
                  '/search']


def build_robots_liquid():
    lines = []
    # 1) Shopify default gruplarını koru (cart/checkout disallow + sitemap dahil)
    lines.append('{% for group in robots.default_groups %}')
    lines.append('  {{- group.user_agent }}')
    lines.append('  {% for rule in group.rules -%}')
    lines.append('    {{ rule }}')
    lines.append('  {% endfor -%}')
    lines.append('  {%- if group.sitemap != blank %}')
    lines.append('    {{ group.sitemap }}')
    lines.append('  {% endif %}')
    lines.append('{% endfor %}')
    lines.append('')
    lines.append('# === RCL GEO/AEO: AI arama motorlarina acik davet ===')
    for bot in AI_BOTS:
        lines.append(f'User-agent: {bot}')
        for d in DISALLOW_PATHS:
            lines.append(f'Disallow: {d}')
        lines.append('Allow: /')
        lines.append('')
    lines.append('# AI ozet dosyasi')
    lines.append('# llms.txt: https://retrocameraland.com/pages/llms-txt')
    lines.append('Sitemap: https://retrocameraland.com/sitemap.xml')
    return '\n'.join(lines) + '\n'


LLMS_TXT = """# RetroCameraLand

> Türkiye'nin öncü retro ve vintage dijital kamera mağazası. 2000'ler dönemi CCD sensörlü kompakt dijital kameralar (digicam), Y2K estetik fotoğraf makineleri ve test edilmiş ikinci el kameralar satıyoruz. Her ürün satıştan önce test edilir ve çalışır durumda gönderilir.

## Hakkında
RetroCameraland, retro/Y2K dijital kamera (digicam) alıcıları için İstanbul merkezli, Türkiye geneline kargo yapan bir online mağazadır. Canon (IXUS, PowerShot), Fujifilm (FinePix), Casio (Exilim), Agfa gibi markaların CCD sensörlü modellerini bulundurur. Hedef kitle: Y2K/retro fotoğraf estetiği isteyen içerik üreticileri, koleksiyonerler ve ilk digicam'ini arayanlar.

## Sık sorulan sorulara cevaplar
- İstanbul'da CCD digicam nereden alınır: https://retrocameraland.com/blogs/news
- Retro/Y2K dijital kamera nedir, CCD vs CMOS farkı: https://retrocameraland.com/pages/faq
- Tüm çalışır kamera koleksiyonu: https://retrocameraland.com/collections/all

## Önemli sayfalar
- Tüm ürünler: https://retrocameraland.com/collections/all
- Blog (satın alma rehberleri): https://retrocameraland.com/blogs/news
- Sık sorulan sorular: https://retrocameraland.com/pages/faq

## İletişim
- Web: https://retrocameraland.com
- E-posta: bilgi@retrocameraland.com
- Instagram: https://www.instagram.com/retrocameraland/
- YouTube: https://www.youtube.com/@RetroCameraLand
"""

LLMS_PAGE_HTML = "<pre style='white-space:pre-wrap;font-family:monospace;font-size:14px;'>" + \
    LLMS_TXT.replace('<', '&lt;').replace('>', '&gt;') + "</pre>"


def deploy_robots():
    log('1/2 templates/robots.txt.liquid → AI crawler allow + llms referansi')
    content = build_robots_liquid()
    if DRY:
        log('  [DRY] robots.txt.liquid icerigi:')
        print('-' * 60); print(content); print('-' * 60)
        return
    shopify('PUT', f'themes/{THEME_ID}/assets.json',
            {'asset': {'key': 'templates/robots.txt.liquid', 'value': content}})
    log('  ✅ robots.txt.liquid yazildi (canli: /robots.txt)')


def deploy_llms_page():
    log('2/2 /pages/llms-txt → llms.txt icerigi')
    if DRY:
        log('  [DRY] llms.txt icerigi:')
        print('-' * 60); print(LLMS_TXT); print('-' * 60)
        return
    pages = shopify('GET', 'pages.json?handle=llms-txt&fields=id,handle')
    existing = pages.get('pages', [])
    body = {'page': {'title': 'llms.txt', 'handle': 'llms-txt',
                     'body_html': LLMS_PAGE_HTML, 'published': True}}
    if existing:
        pid = existing[0]['id']
        shopify('PUT', f'pages/{pid}.json', body)
        log(f'  ✅ /pages/llms-txt guncellendi (ID:{pid})')
    else:
        r = shopify('POST', 'pages.json', body)
        log(f'  ✅ /pages/llms-txt olusturuldu (ID:{r["page"]["id"]})')


if __name__ == '__main__':
    log('=== RCL GEO Deploy basliyor' + (' [DRY RUN]' if DRY else '') + ' ===')
    deploy_robots()
    deploy_llms_page()
    log('=== Tamamlandi ===')
    if not DRY:
        log('Dogrula: https://retrocameraland.com/robots.txt')
