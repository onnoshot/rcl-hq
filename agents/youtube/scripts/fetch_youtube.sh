#!/bin/bash
# Retrocameraland YouTube Kanal Verisi Çekici
# Çalıştır: bash agents/youtube/scripts/fetch_youtube.sh

API_KEY="AIzaSyCA0MrJDK8hVKRwhkskXQUs5sihRS6xwr0"
CHANNEL_ID="UCq0jJ7knS1MDtNgx8DtJCvw"
OUTPUT_DIR="agents/youtube/data/imports"
DATE=$(date +%Y-%m-%d)

echo "YouTube verisi çekiliyor..."

# 1. Kanal istatistikleri
CHANNEL=$(curl -s "https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id=${CHANNEL_ID}&key=${API_KEY}")

SUBSCRIBERS=$(echo $CHANNEL | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['items'][0]['statistics']['subscriberCount'])")
VIEWS=$(echo $CHANNEL | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['items'][0]['statistics']['viewCount'])")
VIDEOS=$(echo $CHANNEL | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['items'][0]['statistics']['videoCount'])")

# 2. Son 10 videonun performansı
RECENT_VIDEOS=$(curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=${CHANNEL_ID}&order=date&maxResults=10&type=video&key=${API_KEY}")

VIDEO_IDS=$(echo $RECENT_VIDEOS | python3 -c "
import sys,json
d=json.load(sys.stdin)
ids=[item['id']['videoId'] for item in d['items']]
print(','.join(ids))
")

# 3. Video istatistikleri (görüntülenme, izlenme süresi, CTR)
VIDEO_STATS=$(curl -s "https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id=${VIDEO_IDS}&key=${API_KEY}")

# 4. Çıktı dosyasını yaz
cat > "${OUTPUT_DIR}/youtube_stats.md" << EOF
# YouTube Kanal İstatistikleri
Son güncelleme: ${DATE}

## Kanal Özeti
- **Toplam Abone:** ${SUBSCRIBERS}
- **10.000 Hedefine Kalan:** $((10000 - SUBSCRIBERS))
- **Toplam İzlenme:** ${VIEWS}
- **Toplam Video:** ${VIDEOS}

## Son 10 Video
EOF

echo $VIDEO_STATS | python3 -c "
import sys,json
d=json.load(sys.stdin)
for item in d['items']:
    title = item['snippet']['title']
    views = item['statistics'].get('viewCount','N/A')
    likes = item['statistics'].get('likeCount','N/A')
    comments = item['statistics'].get('commentCount','N/A')
    published = item['snippet']['publishedAt'][:10]
    print(f'### {title}')
    print(f'- Yayın Tarihi: {published}')
    print(f'- Görüntülenme: {views}')
    print(f'- Beğeni: {likes}')
    print(f'- Yorum: {comments}')
    print()
" >> "${OUTPUT_DIR}/youtube_stats.md"

echo "Tamamlandı: ${OUTPUT_DIR}/youtube_stats.md"
