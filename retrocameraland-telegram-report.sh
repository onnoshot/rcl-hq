#!/bin/bash
# Retrocameraland — Günlük/Haftalık Telegram raporu (gece 00:00)
# Pazartesi: 7 günlük haftalık özet | Diğer günler: dünlük rapor + önceki gün karşılaştırması

export PATH="/usr/local/bin:/usr/bin:/bin:/Users/onnoshot/.local/bin:$PATH"
export HOME="/Users/onnoshot"

BASE="$HOME/Downloads/Agentlar"
LOG_DIR="$BASE/outputs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date '+%Y-%m-%d')_telegram-report.log"

echo "[$(date)] === Telegram raporu başladı ===" >> "$LOG"

python3 - >> "$LOG" 2>&1 <<'PYEOF'
import os, requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, MetricAggregation,
    FilterExpression, Filter
)

TOKEN_PATH  = os.path.expanduser("~/.config/ga4/token.json")
SCOPES      = ["https://www.googleapis.com/auth/analytics.readonly"]
PROPERTY_ID = "493627571"
TG_TOKEN    = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID  = "7904534693"

creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_PATH, "w") as f: f.write(creds.to_json())
client = BetaAnalyticsDataClient(credentials=creds)

DAYS_TR   = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
MONTHS_TR = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]

def b(s):  return f"<b>{s}</b>"
def c(s):  return f"<code>{s}</code>"
def h(s):  return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def date_fmt(d): return f"{d.day} {MONTHS_TR[d.month]} {d.year}"

def trend(curr, prev):
    if not prev: return ""
    pct = (curr - prev) / prev * 100
    if pct >= 0.5:  return f" ↑{pct:.0f}%"
    if pct <= -0.5: return f" ↓{abs(pct):.0f}%"
    return ""

def dur(sec):
    sec = int(sec)
    m, s = divmod(sec, 60)
    return f"{m}dk {s}sn" if m else f"{s}sn"

def run_report(dims, metrics, start, end, limit=500, agg=None, dim_filter=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
        metric_aggregations=agg or [],
        dimension_filter=dim_filter,
    )
    return client.run_report(req)

def get_kpi(start, end):
    r = run_report([], ["sessions","activeUsers","newUsers","screenPageViews","bounceRate","averageSessionDuration"],
                   start, end, agg=[MetricAggregation.TOTAL])
    t = r.totals[0].metric_values if r.totals else None
    if not t: return {}
    return {
        "sessions":    int(float(t[0].value)),
        "activeUsers": int(float(t[1].value)),
        "newUsers":    int(float(t[2].value)),
        "pageviews":   int(float(t[3].value)),
        "bounceRate":  float(t[4].value) * 100,
        "avgDuration": float(t[5].value),
    }

def get_ecommerce(start, end):
    try:
        r = run_report([], ["itemsViewed","addToCarts","checkouts","transactions","purchaseRevenue"],
                       start, end, agg=[MetricAggregation.TOTAL])
        t = r.totals[0].metric_values if r.totals else None
        if not t: return {}
        return {
            "itemsViewed":  int(float(t[0].value)),
            "addToCarts":   int(float(t[1].value)),
            "checkouts":    int(float(t[2].value)),
            "transactions": int(float(t[3].value)),
            "revenue":      float(t[4].value),
        }
    except Exception as ex:
        print(f"  e-ticaret sorgusu atlandı: {ex}")
        return {}

def get_sign_ups(start, end):
    try:
        f = FilterExpression(filter=Filter(
            field_name="eventName",
            string_filter=Filter.StringFilter(value="sign_up", match_type=Filter.StringFilter.MatchType.EXACT)
        ))
        r = run_report(["eventName"], ["eventCount"], start, end, dim_filter=f)
        return int(float(r.rows[0].metric_values[0].value)) if r.rows else 0
    except: return 0

def get_devices(start, end):
    r = run_report(["deviceCategory"], ["sessions"], start, end)
    total = sum(int(float(row.metric_values[0].value)) for row in r.rows) or 1
    return {row.dimension_values[0].value: round(int(float(row.metric_values[0].value)) / total * 100)
            for row in r.rows}

def get_countries(start, end, limit=3):
    r = run_report(["country"], ["sessions"], start, end, limit=limit)
    rows = sorted([(h(row.dimension_values[0].value), int(float(row.metric_values[0].value)))
                   for row in r.rows], key=lambda x: -x[1])
    return rows[:limit]

def get_top_pages(start, end, limit=3):
    r = run_report(["pagePath"], ["sessions"], start, end, limit=100)
    rows = sorted([(h(row.dimension_values[0].value), int(float(row.metric_values[0].value)))
                   for row in r.rows], key=lambda x: -x[1])
    return rows[:limit]

def get_channels(start, end, limit=3):
    r = run_report(["sessionDefaultChannelGrouping"], ["sessions"], start, end)
    total = sum(int(float(row.metric_values[0].value)) for row in r.rows) or 1
    rows  = sorted([(h(row.dimension_values[0].value), int(float(row.metric_values[0].value)))
                    for row in r.rows], key=lambda x: -x[1])
    return [(name, sess, round(sess / total * 100)) for name, sess in rows[:limit]]

def send(msg):
    url  = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    data = resp.json()
    if data.get("ok"):
        print("✓ Telegram gönderildi")
    else:
        print(f"✗ Telegram hatası: {data.get('description')}")

now       = datetime.now()
yesterday = now - timedelta(days=1)
is_monday = now.weekday() == 0

# ─── HAFTALIK RAPOR (Pazartesi) ───────────────────────────────────────────────
if is_monday:
    print("Haftalık rapor modu...")
    kpi  = get_kpi("7daysAgo", "yesterday")
    kpi2 = get_kpi("14daysAgo", "8daysAgo")
    eco  = get_ecommerce("7daysAgo", "yesterday")
    eco2 = get_ecommerce("14daysAgo", "8daysAgo")
    sign_ups  = get_sign_ups("7daysAgo", "yesterday")
    channels  = get_channels("7daysAgo", "yesterday")
    countries = get_countries("7daysAgo", "yesterday")
    top_pages = get_top_pages("7daysAgo", "yesterday")

    week_start = now - timedelta(days=7)
    s,  sp  = kpi.get("sessions",0),    kpi2.get("sessions",0)
    au, aup = kpi.get("activeUsers",0), kpi2.get("activeUsers",0)
    nu      = kpi.get("newUsers",0)
    pv, pvp = kpi.get("pageviews",0),   kpi2.get("pageviews",0)
    br      = kpi.get("bounceRate",0)
    dur_v   = kpi.get("avgDuration",0)

    lines = [
        f"{b('📊 Retrocameraland Haftalık Rapor')}",
        f"📅 {date_fmt(week_start)} – {date_fmt(yesterday)}",
        "",
        f"{b('👥 Ziyaretçiler')}",
        f"• Oturum: {c(f'{s:,}')}{trend(s,sp)}",
        f"• Aktif kullanıcı: {c(f'{au:,}')}",
        f"• Yeni: {c(f'{nu:,}')}  |  Dönen: {c(f'{au-nu:,}')}",
        "",
        f"{b('📄 İçerik')}",
        f"• Sayfa görüntüleme: {c(f'{pv:,}')}{trend(pv,pvp)}",
        f"• Ort. süre: {c(dur(dur_v))} {'✅' if dur_v>=120 else '⚠️'}",
        f"• Bounce rate: {c(f'{br:.1f}%')} {'✅' if br<60 else '⚠️'}",
    ]

    if eco:
        ac, acc = eco.get("addToCarts",0),   eco2.get("addToCarts",0)
        tr, trp = eco.get("transactions",0), eco2.get("transactions",0)
        rev,rvp = eco.get("revenue",0),      eco2.get("revenue",0)
        lines += [
            "",
            f"{b('🛒 E-ticaret')}",
            f"• Sepete ekleme: {c(f'{ac:,}')}{trend(ac,acc)}",
            f"• Satın alma: {c(f'{tr:,}')}{trend(tr,trp)}",
            f"• Gelir: {c(f'₺{rev:,.0f}')}{trend(rev,rvp)}",
            f"• Yeni kayıt: {c(f'{sign_ups:,}')}",
        ]

    if channels:
        lines += ["", f"{b('📈 Kanallar')}"]
        for i, (name, sess, pct) in enumerate(channels, 1):
            lines.append(f"{i}. {name}: {c(f'{pct}%')} ({sess:,} oturum)")

    if top_pages:
        lines += ["", f"{b('📄 İlk 3 Sayfa')}"]
        for i, (path, sess) in enumerate(top_pages, 1):
            short = path[:35] + "…" if len(path) > 37 else path
            lines.append(f"{i}. {c(short)} → {sess:,} oturum")

    if countries:
        lines += ["", f"{b('🌍 İlk 3 Ülke')}"]
        for i, (name, sess) in enumerate(countries, 1):
            lines.append(f"{i}. {name} — {c(f'{sess:,}')} oturum")

    msg = "\n".join(lines)

# ─── GÜNLÜK RAPOR ────────────────────────────────────────────────────────────
else:
    print("Günlük rapor modu...")
    kpi  = get_kpi("yesterday", "yesterday")
    kpi2 = get_kpi("2daysAgo",  "2daysAgo")
    eco  = get_ecommerce("yesterday", "yesterday")
    eco2 = get_ecommerce("2daysAgo",  "2daysAgo")
    sign_ups  = get_sign_ups("yesterday", "yesterday")
    devs      = get_devices("yesterday", "yesterday")
    countries = get_countries("yesterday", "yesterday")
    top_pages = get_top_pages("yesterday", "yesterday")
    channels  = get_channels("yesterday", "yesterday")
    top_ch    = channels[0] if channels else ("Bilinmiyor", 0, 0)

    s,  sp  = kpi.get("sessions",0),    kpi2.get("sessions",0)
    au, aup = kpi.get("activeUsers",0), kpi2.get("activeUsers",0)
    nu      = kpi.get("newUsers",0)
    pv, pvp = kpi.get("pageviews",0),   kpi2.get("pageviews",0)
    br      = kpi.get("bounceRate",0)
    dur_v   = kpi.get("avgDuration",0)
    pps     = pv / s if s else 0
    day_name = DAYS_TR[yesterday.weekday()]

    lines = [
        f"{b('📊 Retrocameraland Günlük Rapor')}",
        f"📅 {date_fmt(yesterday)} ({day_name})",
        "",
        f"{b('👥 Ziyaretçiler')}",
        f"• Oturum: {c(f'{s:,}')}{trend(s,sp)}",
        f"• Aktif kullanıcı: {c(f'{au:,}')}",
        f"• Yeni: {c(f'{nu:,}')}  |  Dönen: {c(f'{au-nu:,}')}",
        "",
        f"{b('📄 İçerik')}",
        f"• Sayfa görüntüleme: {c(f'{pv:,}')}{trend(pv,pvp)}",
        f"• Sayfa / oturum: {c(f'{pps:.1f}')}",
        f"• Ort. süre: {c(dur(dur_v))} {'✅' if dur_v>=120 else '⚠️'}",
        f"• Bounce rate: {c(f'{br:.1f}%')} {'✅' if br<60 else '⚠️'}",
    ]

    if eco:
        iv, ivc = eco.get("itemsViewed",0),  eco2.get("itemsViewed",0)
        ac, acc = eco.get("addToCarts",0),   eco2.get("addToCarts",0)
        ch, chp = eco.get("checkouts",0),    eco2.get("checkouts",0)
        tr, trp = eco.get("transactions",0), eco2.get("transactions",0)
        rev,rvp = eco.get("revenue",0),      eco2.get("revenue",0)
        lines += [
            "",
            f"{b('🛒 E-ticaret')}",
            f"• Ürün görüntüleme: {c(f'{iv:,}')}{trend(iv,ivc)}",
            f"• Sepete ekleme: {c(f'{ac:,}')}{trend(ac,acc)}",
            f"• Checkout: {c(f'{ch:,}')}{trend(ch,chp)}",
            f"• Satın alma: {c(f'{tr:,}')}{trend(tr,trp)}",
            f"• Gelir: {c(f'₺{rev:,.0f}')}{trend(rev,rvp)}",
            f"• Yeni kayıt: {c(f'{sign_ups:,}')}",
        ]

    if devs:
        mob  = devs.get("mobile",0)
        desk = devs.get("desktop",0)
        tab  = devs.get("tablet",0)
        lines += [
            "",
            f"{b('📱 Cihaz')}",
            f"• Mobil: {c(f'{mob}%')}  Masaüstü: {c(f'{desk}%')}  Tablet: {c(f'{tab}%')}",
        ]

    if top_pages:
        lines += ["", f"{b('📄 İlk 3 Sayfa')}"]
        for i, (path, sess) in enumerate(top_pages, 1):
            short = path[:35] + "…" if len(path) > 37 else path
            lines.append(f"{i}. {c(short)} → {sess:,} oturum")

    if countries:
        lines += ["", f"{b('🌍 İlk 3 Ülke')}"]
        for i, (name, sess) in enumerate(countries, 1):
            lines.append(f"{i}. {name} — {c(f'{sess:,}')} oturum")

    lines += [
        "",
        f"📈 En iyi kaynak: {b(top_ch[0])} ({c(f'{top_ch[2]}%')})",
    ]

    msg = "\n".join(lines)

send(msg)
print(f"   KPI: {kpi.get('sessions',0):,} oturum")
PYEOF

echo "[$(date)] === Tamamlandı ===" >> "$LOG"
