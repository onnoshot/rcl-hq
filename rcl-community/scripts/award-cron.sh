#!/bin/bash
# RCL Topluluk - kazanana odul kodunu paylas (haftalik/aylik).
# award.js kazanani bulur, ONCEDEN HAZIRLANMIS sabit kodu (OZELWIN1000 / WIN5000) kazanana
# e-postayla yollar + sana Telegram'a bildirir. Cek BASMAZ. Idempotent (ayni donem 2 kez gondermez).
# Kullanim: award-cron.sh week | month
set -e
RANGE="${1:-week}"
BASE="${RCL_COMMUNITY_BASE:-https://rclhq.vercel.app}"
curl -s "${BASE}/api/community/award?range=${RANGE}" >/dev/null 2>&1 || true
echo "$(date '+%Y-%m-%d %H:%M') odul kodu paylasildi: ${RANGE}"
