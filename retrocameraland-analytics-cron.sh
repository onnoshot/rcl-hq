#!/bin/bash
# Retrocameraland HQ Dashboard — Günlük otomatik veri güncelleme
# Her gün 09:00'da çalışır (com.retrocameraland.analytics LaunchAgent)

export PATH="/usr/local/bin:/usr/bin:/bin:/Users/onnoshot/.local/bin:$PATH"
export HOME="/Users/onnoshot"

BASE="$HOME/Downloads/Agentlar"
LOG_DIR="$BASE/outputs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date '+%Y-%m-%d')_analytics-cron.log"

echo "[$(date)] === Analytics güncelleme başladı ===" >> "$LOG"

# Ağ bekleme: DNS çözülene kadar bekle (LaunchAgent erken başlama sorunu)
for i in $(seq 1 12); do
    if python3 -c "import socket; socket.setdefaulttimeout(5); socket.getaddrinfo('www.googleapis.com',443)" 2>/dev/null; then
        break
    fi
    echo "[$(date)] Ağ bekleniyor ($i/12)..." >> "$LOG"
    sleep 10
done

python3 - >> "$LOG" 2>&1 <<'PYEOF'
import os, json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, MetricAggregation
)

TOKEN_PATH  = os.path.expanduser("~/.config/ga4/token.json")
DASHBOARD   = "/Users/onnoshot/Downloads/Agentlar/retrocameraland-analytics-dashboard.html"
DATA_PATH   = "/Users/onnoshot/Downloads/Agentlar/agents/retrocameraland-analytics/data/ga_data.json"
SCOPES      = ["https://www.googleapis.com/auth/analytics.readonly"]
PROPERTY_ID = "493627571"

print(f"[{datetime.now().strftime('%H:%M:%S')}] GA4 bağlanıyor...")
creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_PATH, "w") as f: f.write(creds.to_json())
client = BetaAnalyticsDataClient(credentials=creds)

def run(dims, metrics, start, end, limit=500, agg=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
        metric_aggregations=agg or [],
    )
    return client.run_report(req)

def kpi(start, end):
    r = run([], ["sessions","activeUsers","newUsers","screenPageViews","bounceRate","averageSessionDuration"],
            start, end, agg=[MetricAggregation.TOTAL])
    row = r.totals[0].metric_values if r.totals else r.rows[0].metric_values
    return {
        "sessions": int(float(row[0].value)),
        "activeUsers": int(float(row[1].value)),
        "newUsers": int(float(row[2].value)),
        "screenPageViews": int(float(row[3].value)),
        "bounceRate": round(float(row[4].value), 4),
        "averageSessionDuration": round(float(row[5].value), 1),
    }

print(f"[{datetime.now().strftime('%H:%M:%S')}] KPI özet çekiliyor...")
p7  = kpi("6daysAgo",  "today")
p30 = kpi("29daysAgo", "today")
p90 = kpi("89daysAgo", "today")

print(f"[{datetime.now().strftime('%H:%M:%S')}] Günlük seri...")
r = run(["date"], ["sessions","activeUsers"], "89daysAgo", "today")
daily = sorted([{"date": row.dimension_values[0].value, "sessions": int(float(row.metric_values[0].value)), "users": int(float(row.metric_values[1].value))} for row in r.rows], key=lambda x: x["date"])

print(f"[{datetime.now().strftime('%H:%M:%S')}] Kaynaklar...")
r = run(["sessionDefaultChannelGrouping"], ["sessions"], "29daysAgo", "today")
rows = sorted([(row.dimension_values[0].value, int(float(row.metric_values[0].value))) for row in r.rows], key=lambda x: -x[1])
total_s = sum(x[1] for x in rows)
sources = [{"name": n, "sessions": s, "pct": round(s/total_s*100,1)} for n,s in rows]

print(f"[{datetime.now().strftime('%H:%M:%S')}] Sayfalar...")
r = run(["pagePath"], ["sessions","screenPageViews","bounceRate","averageSessionDuration"], "29daysAgo", "today", limit=20)
top_pages = sorted([{"path": row.dimension_values[0].value, "sessions": int(float(row.metric_values[0].value)), "pageviews": int(float(row.metric_values[1].value)), "bounceRate": round(float(row.metric_values[2].value)*100,1), "avgDuration": round(float(row.metric_values[3].value))} for row in r.rows], key=lambda x: -x["sessions"])[:15]

print(f"[{datetime.now().strftime('%H:%M:%S')}] Cihaz & ülke...")
r = run(["deviceCategory"], ["sessions"], "29daysAgo", "today")
devs = [(row.dimension_values[0].value, int(float(row.metric_values[0].value))) for row in r.rows]
dtotal = sum(d[1] for d in devs)
devices = {k: {"sessions": v, "pct": round(v/dtotal*100,1)} for k,v in devs}

r = run(["country"], ["sessions"], "29daysAgo", "today", limit=10)
countries = sorted([{"name": row.dimension_values[0].value, "sessions": int(float(row.metric_values[0].value))} for row in r.rows], key=lambda x: -x["sessions"])

ga_data = {
    "updated_at": datetime.now().isoformat(),
    "property_id": PROPERTY_ID,
    "period_7d": p7, "period_30d": p30, "period_90d": p90,
    "daily": daily, "sources": sources, "top_pages": top_pages,
    "devices": devices, "countries": countries, "ai_insights": "",
}

os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(ga_data, f, ensure_ascii=False, indent=2)

with open(DASHBOARD, encoding="utf-8") as f: html = f.read()
sm = "/* ─── DATA BLOCK START ─── */"; em = "/* ─── DATA BLOCK END ─── */"
s = html.find(sm); e = html.find(em)
if s == -1 or e == -1:
    print(f"HATA: Marker bulunamadı: {DASHBOARD}")
else:
    html = html[:s] + f"{sm}\nconst GA_DATA = {json.dumps(ga_data, ensure_ascii=False)};\n{em}" + html[e+len(em):]
    with open(DASHBOARD, "w", encoding="utf-8") as f: f.write(html)

print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Dashboard güncellendi — {p30['sessions']:,} oturum (30 gün)")
PYEOF

echo "[$(date)] === Tamamlandı ===" >> "$LOG"
