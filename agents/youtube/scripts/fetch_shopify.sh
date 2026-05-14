#!/bin/bash
# Retrocameraland Shopify Ürün Listesi Çekici
# Çalıştır: bash agents/youtube/scripts/fetch_shopify.sh

STORE="retrocameraland.com"
OUTPUT_DIR="agents/youtube/data/imports"
DATE=$(date +%Y-%m-%d)

echo "Shopify ürünleri çekiliyor..."

PRODUCTS=$(curl -s "https://${STORE}/products.json?limit=250")

cat > "${OUTPUT_DIR}/products.md" << 'HEADER'
# Retrocameraland Ürün Listesi
HEADER

echo "Son güncelleme: ${DATE}" >> "${OUTPUT_DIR}/products.md"
echo "" >> "${OUTPUT_DIR}/products.md"
echo "Bu dosya otomatik oluşturulur. YouTube ajanı okur, asla yazmaz." >> "${OUTPUT_DIR}/products.md"
echo "" >> "${OUTPUT_DIR}/products.md"
echo "---" >> "${OUTPUT_DIR}/products.md"

echo $PRODUCTS | python3 -c "
import sys,json

d=json.load(sys.stdin)
categories={}

for p in d['products']:
    ptype = p.get('product_type','Diğer') or 'Diğer'
    if ptype not in categories:
        categories[ptype]=[]

    price = 'N/A'
    available = False
    for v in p.get('variants',[]):
        price = v.get('price','N/A')
        if v.get('available'):
            available = True
            break

    categories[ptype].append({
        'title': p['title'],
        'handle': p['handle'],
        'description': p.get('body_html','')[:120].replace('<[^>]+>',''),
        'price': price,
        'available': available
    })

for cat, products in categories.items():
    print(f'## {cat}')
    print()
    for p in products:
        stock = '' if p['available'] else ' ⚠️ Stokta yok'
        print(f\"### {p['title']}{stock}\")
        print(f\"- **URL:** retrocameraland.com/products/{p['handle']}\")
        print(f\"- **Fiyat:** ₺{p['price']}\")
        print()
"  >> "${OUTPUT_DIR}/products.md"

echo "Tamamlandı: ${OUTPUT_DIR}/products.md"
