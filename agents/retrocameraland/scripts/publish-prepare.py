#!/usr/bin/env python3
"""
Blog Publishing Preparation Script for RetroCamera Land

Converts optimized blog markdown to publishable format:
- Extracts JSON-LD schemas
- Generates meta tags (og:, twitter:)
- Creates HTML preview
- Prepares CMS upload format
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

def extract_section(content, section_name):
    """Extract a section from blog markdown."""
    pattern = rf'## {section_name}\n(.*?)(?=\n## |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None

def extract_json_ld(content):
    """Extract JSON-LD schemas from content."""
    schemas = []
    
    # Find all JSON blocks
    json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
    
    for block in json_blocks:
        try:
            schema = json.loads(block)
            schemas.append(schema)
        except json.JSONDecodeError:
            pass
    
    return schemas

def generate_html_preview(blog_data):
    """Generate HTML preview of the blog."""
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{blog_data['title']}</title>
    <meta name="description" content="{blog_data['meta_description']}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{blog_data['title']}">
    <meta property="og:description" content="{blog_data['meta_description']}">
    <meta property="og:image" content="{blog_data['image']}">
    <meta property="og:url" content="{blog_data['url']}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{blog_data['title']}">
    <meta name="twitter:description" content="{blog_data['meta_description']}">
    <meta name="twitter:image" content="{blog_data['image']}">
    
    <!-- JSON-LD Schemas -->
    <script type="application/ld+json">
{json.dumps(blog_data['schemas'][0], ensure_ascii=False, indent=2)}
    </script>
    
    {f'<script type="application/ld+json">{json.dumps(blog_data["schemas"][1], ensure_ascii=False, indent=2)}</script>' if len(blog_data['schemas']) > 1 else ''}
    
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #000; font-size: 2em; margin-bottom: 10px; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .content {{ margin: 30px 0; }}
        h2 {{ color: #000; font-size: 1.4em; margin-top: 30px; margin-bottom: 15px; }}
        h3 {{ color: #333; font-size: 1.2em; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .comparison-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin: 20px 0; }}
        .card {{ border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; background: #f9f9f9; }}
        .card-row {{ margin: 8px 0; padding: 4px 0; border-bottom: 1px solid #eee; }}
    </style>
</head>
<body>
    <article>
        <h1>{blog_data['title']}</h1>
        <div class="meta">
            <p>{blog_data['seo_info']} | Okuma süresi: {blog_data['read_time']} dakika | Yayın tarihi: {blog_data['publish_date']}</p>
        </div>
        <div class="content">
            {blog_data['content_preview']}
        </div>
    </article>
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 0.9em;">
        <p>Retrocameraland © 2025. Tüm hakları saklıdır.</p>
    </footer>
</body>
</html>"""
    return html

def prepare_blog_for_publishing(file_path):
    """Prepare blog file for publishing."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract data
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"
    
    seo_match = re.search(r'\[SEO: ([^\]]+)\]', content)
    seo_info = seo_match.group(1) if seo_match else "SEO: Pending"
    
    read_time_match = re.search(r'Tahmini okuma süresi: (\d+)', content)
    read_time = read_time_match.group(1) if read_time_match else "5"
    
    meta_desc = extract_section(content, "Meta Açıklama")
    
    # Generate blog slug from filename
    blog_slug = file_path.stem.split('_')[3]  # Extract slug from filename
    
    # Prepare data
    blog_data = {
        'title': title,
        'slug': blog_slug,
        'meta_description': meta_desc[:160] if meta_desc else "Retrocameraland blog yazısı",
        'seo_info': seo_info,
        'read_time': read_time,
        'image': f'https://retrocameraland.com/images/blog/{blog_slug}.jpg',
        'url': f'https://retrocameraland.com/blog/{blog_slug}',
        'publish_date': datetime.now().strftime('%d.%m.%Y'),
        'schemas': extract_json_ld(content),
        'content_preview': content[:500] + '...'
    }
    
    # Generate HTML preview
    html_preview = generate_html_preview(blog_data)
    
    # Save preview
    preview_path = file_path.parent / f'{file_path.stem}_preview.html'
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html_preview)
    
    # Generate CMS-ready JSON
    cms_data = {
        'title': blog_data['title'],
        'slug': blog_data['slug'],
        'description': blog_data['meta_description'],
        'featured_image': blog_data['image'],
        'content': content,
        'schemas': blog_data['schemas'],
        'seo': {
            'score': seo_info,
            'read_time': f"{read_time} dakika"
        },
        'publish_date': blog_data['publish_date'],
        'status': 'pending_review'  # Requires manual approval
    }
    
    cms_json_path = file_path.parent / f'{file_path.stem}_cms.json'
    with open(cms_json_path, 'w', encoding='utf-8') as f:
        json.dump(cms_data, f, ensure_ascii=False, indent=2)
    
    return blog_data, preview_path, cms_json_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 publish-prepare.py <blog_file.md>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    print(f"📝 Preparing '{file_path.name}' for publishing...\n")
    
    blog_data, preview_path, cms_json_path = prepare_blog_for_publishing(file_path)
    
    print(f"✅ YAYINLAMA HAZIRLIĞI TAMAMLANDI\n")
    print(f"📄 Blog Başlığı: {blog_data['title']}")
    print(f"🔗 Slug: {blog_data['slug']}")
    print(f"📊 SEO: {blog_data['seo_info']}")
    print(f"⏱️  Okuma Süresi: {blog_data['read_time']} dakika")
    print(f"📅 Yayın Tarihi: {blog_data['publish_date']}\n")
    
    print(f"📦 Çıktı Dosyaları:")
    print(f"  1. HTML Preview: {preview_path}")
    print(f"  2. CMS JSON: {cms_json_path}\n")
    
    print(f"🚀 Sonraki Adımlar:")
    print(f"  1. HTML Preview'ı tarayıcıda aç ve kontrol et")
    print(f"  2. CMS JSON'ı CMS'ye yükle (Shopify, WordPress, etc)")
    print(f"  3. Görseli Instagram'dan seç ve ekle")
    print(f"  4. Yayınla! 🎉\n")

if __name__ == '__main__':
    main()
