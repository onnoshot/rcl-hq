#!/bin/zsh
# RCL kampanya otomatik devam: "partial" kampanyaları günlük (Brevo 300/gün) tamamlar.
# Sadece zaten başlatılmış (partial) kampanyaları sürdürür; taslakları ASLA göndermez.
# Bitince (status=sent) hiçbir şey yapmaz. Sonra dashboard stats + deploy çalıştırır.
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
ROOT=/Users/onnoshot/Downloads/Agentlar
cd "$ROOT" || exit 1

PARTIALS=$("$PY" -c "import json;[print(c['id']) for c in json.load(open('rcl-campaigns.json')) if c.get('status')=='partial']" 2>/dev/null)
if [ -z "$PARTIALS" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M')] partial kampanya yok, devam edilecek bir şey yok."
  exit 0
fi
echo "$PARTIALS" | while read -r cid; do
  [ -z "$cid" ] && continue
  echo "[$(date '+%Y-%m-%d %H:%M')] Devam ediliyor: $cid"
  "$PY" rcl-campaign.py send "$cid"
done
# istatistik + canlı deploy
zsh "$ROOT/rcl-email-stats-cron.sh"
