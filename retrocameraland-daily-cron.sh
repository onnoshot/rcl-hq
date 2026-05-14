#!/bin/bash
# retrocameraland günlük blog yayınlama — sabah 10:00 LaunchAgent tarafından çağrılır

export PATH="/usr/local/bin:/usr/bin:/bin:/Users/onnoshot/.local/bin:$PATH"
export HOME="/Users/onnoshot"

LOG_DIR="/Users/onnoshot/Downloads/Agentlar/outputs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d')_cron-run.log"

echo "[$(date)] Günlük blog görevi başladı" >> "$LOG_FILE"

/Users/onnoshot/.local/bin/claude \
  --dangerously-skip-permissions \
  -p "Retrocameraland.com için günlük 20 blog yayınlama görevi.

## Çalışma Dizini
/Users/onnoshot/Downloads/Agentlar

## API Bilgileri (sabit — değiştirme)
- Shopify Token: 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
- Store: retrocameraland.myshopify.com
- Blog ID: 91197866123
- Fal.ai Key: 65067257-e286-49f2-aa12-4318001c2999:8c8bf90fa5a185945f52f4cb1f978580
- Fal.ai Model: fal-ai/nano-banana-2

## Adımlar

### 1. Daha önce yayınlanan başlıkları oku
Dosya: /Users/onnoshot/Downloads/Agentlar/published-topics.json
Yoksa boş liste kabul et.

### 2. 20 FARKLI ve YENİ blog konusu seç (daha önce yayınlanmamış)
Konu havuzu (sınırlı değil — yaratıcı ol):
- Retro kamera model incelemeleri (Sony, Canon, Fujifilm, Olympus, Nikon, Casio, Kodak, Panasonic, Samsung vs.)
- Y2K estetik kültür, trend analizleri
- Türkiye şehirleri ve mahalle fotoğraf rotaları
- Kahve kültürü + fotoğrafçılık
- Üniversite ve gençlik yaşamı
- Hediye rehberleri (bayram, doğum günü, sevgililer günü, mezuniyet vs.)
- Kamera bakım, temizlik, teknik ipuçları
- Sosyal medya içerik üretimi (TikTok, Instagram, Pinterest)
- Seyahat fotoğrafçılığı
- Mevsimsel içerikler
- Analog vs. dijital karşılaştırma
- Fotoğraf teknikleri (portre, sokak, manzara, macro, gece)
- Baskı ve fotoğraf albümü kültürü
- Retro kamera toplulukları ve etkinlikler

### 3. Her blog için Python scripti oluştur ve çalıştır
Dosya yolu: /tmp/rcl_post_N.py (N = 1..20)

Script şablonu:
\`\`\`python
import sys
sys.path.insert(0, '/Users/onnoshot/Downloads/Agentlar')
from retrocameraland_api import publish_article

publish_article(
    title='BAŞLIK',
    handle='slug',
    tags='tag1, tag2, retrocameraland',
    body_html='''HTML İÇERİK (min 700 kelime, Türkçe, H1/H2/H3/liste/tablo)''',
    meta_desc='150-160 karakter meta açıklama',
    image_prompt='Detaylı İngilizce Fal.ai prompt, Y2K/retro estetik',
    image_filename='seo-uyumlu-dosya-adi.jpg'
)
\`\`\`

İçerik gereksinimleri:
- Türkçe, 700-1200 kelime
- SEO optimize başlık ve içerik
- AI arama için doğrudan cevap paragrafları + FAQ
- body_html içinde sosyal medya kutusu:
  <div style=\"background:#f8f4f0;border-left:4px solid #c8a882;padding:20px 24px;margin:40px 0;border-radius:0 8px 8px 0;\"><p style=\"margin:0 0 8px 0;font-weight:700;\">📸 Retrocameraland'i Takip Edin</p><p style=\"margin:0;line-height:1.8;\">📷 <a href=\"https://instagram.com/retrocameraland\">instagram.com/retrocameraland</a><br>▶️ <a href=\"https://youtube.com/@retrocameraland\">youtube.com/@retrocameraland</a><br>🎵 <a href=\"https://tiktok.com/@retrocameraland\">tiktok.com/@retrocameraland</a></p></div>
- body_html içinde CTA:
  <div style=\"text-align:center;margin:48px 0;\"><a href=\"https://retrocameraland.com/collections/all\" style=\"background:#1a1a1a;color:#fff;padding:16px 36px;border-radius:6px;text-decoration:none;font-weight:700;font-size:17px;\">🛒 Tüm Koleksiyonu Gör →</a></div>
- image_filename: SEO uyumlu, Türkçe karakter yok, tire-ayrılmış

### 4. Yayınlanan başlıkları kaydet
\`\`\`python
import json, os
path = '/Users/onnoshot/Downloads/Agentlar/published-topics.json'
existing = json.load(open(path)) if os.path.exists(path) else []
new_titles = ['başlık1', 'başlık2']
json.dump(existing + new_titles, open(path, 'w'), ensure_ascii=False, indent=2)
\`\`\`

### 5. Rapor yaz
Dosya: /Users/onnoshot/Downloads/Agentlar/outputs/$(date +%Y-%m-%d)_daily-blog-report.md
Format: başarılı/başarısız sayıları, ID listesi, toplam yayın sayısı.

## Kurallar
- Hata olursa devam et, sonraki bloğu yayınla
- Tüm 20 blog yayınlanana kadar dur
- Her konu benzersiz ve daha önce yayınlanmamış olmalı" \
  >> "$LOG_FILE" 2>&1

echo "[$(date)] Görev tamamlandı" >> "$LOG_FILE"
