#!/usr/bin/env python3
"""
Retrocameraland Analytics — Günlük GA4 veri çekme ve dashboard güncelleme.

Kurulum:
    pip3 install google-analytics-data google-auth

Gerekli dosyalar:
    agents/retrocameraland-analytics/data/imports/ga_credentials.json  (service account key)
    agents/retrocameraland-analytics/data/imports/ga_config.json       (property_id)

Çalıştırma:
    python3 agents/retrocameraland-analytics/scripts/fetch_and_update.py
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

CREDENTIALS_PATH = os.path.join(BASE_DIR, "data", "imports", "ga_credentials.json")
CONFIG_PATH      = os.path.join(BASE_DIR, "data", "imports", "ga_config.json")
OUTPUT_JSON      = os.path.join(BASE_DIR, "data", "ga_data.json")
DASHBOARD_HTML   = os.path.join(ROOT_DIR, "retrocameraland-analytics-dashboard.html")
OUTPUTS_DIR      = os.path.join(BASE_DIR, "outputs")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_config():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Service account credentials bulunamadı: {CREDENTIALS_PATH}\n"
            "Kurulum için HEARTBEAT.md dosyasına bakın."
        )
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"GA config bulunamadı: {CONFIG_PATH}\n"
            'İçeriği: {"property_id": "YOUR_GA4_PROPERTY_ID"}'
        )
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    property_id = config.get("property_id", "")
    if not property_id or property_id == "YOUR_GA4_PROPERTY_ID":
        raise ValueError("ga_config.json içinde geçerli bir property_id gerekiyor.")
    return property_id


def build_client():
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
    except ImportError:
        raise ImportError(
            "Gerekli paketler yüklü değil.\n"
            "Çalıştır: pip3 install google-analytics-data google-auth"
        )
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def run_report(client, property_id, date_ranges, dimensions, metrics):
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest
    )
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=dr[0], end_date=dr[1]) for dr in date_ranges],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
    )
    return client.run_report(request)


def parse_summary(response, metric_names):
    totals = {}
    if response.totals:
        for i, m in enumerate(metric_names):
            totals[m] = float(response.totals[0].metric_values[i].value)
    return totals


def fetch_period_summary(client, property_id, days):
    end = "today"
    start = f"{days}daysAgo"
    resp = run_report(
        client, property_id,
        [(start, end)],
        [],
        ["sessions", "activeUsers", "screenPageViews", "bounceRate", "averageSessionDuration"],
    )
    return parse_summary(resp, ["sessions", "activeUsers", "screenPageViews", "bounceRate", "averageSessionDuration"])


def fetch_daily_series(client, property_id, days=90):
    resp = run_report(
        client, property_id,
        [("89daysAgo", "today")],
        ["date"],
        ["sessions", "activeUsers"],
    )
    rows = []
    for row in resp.rows:
        rows.append({
            "date": row.dimension_values[0].value,
            "sessions": int(float(row.metric_values[0].value)),
            "users": int(float(row.metric_values[1].value)),
        })
    rows.sort(key=lambda x: x["date"])
    return rows[-days:]


def fetch_sources(client, property_id, days=30):
    resp = run_report(
        client, property_id,
        [("29daysAgo", "today")],
        ["sessionDefaultChannelGrouping"],
        ["sessions"],
    )
    total = sum(float(r.metric_values[0].value) for r in resp.rows)
    sources = []
    for row in resp.rows:
        s = int(float(row.metric_values[0].value))
        sources.append({
            "name": row.dimension_values[0].value,
            "sessions": s,
            "pct": round(s / total * 100, 1) if total else 0,
        })
    sources.sort(key=lambda x: -x["sessions"])
    return sources[:8]


def fetch_top_pages(client, property_id, days=30):
    resp = run_report(
        client, property_id,
        [("29daysAgo", "today")],
        ["pagePath"],
        ["sessions", "screenPageViews", "bounceRate", "averageSessionDuration"],
    )
    pages = []
    for row in resp.rows:
        pages.append({
            "path": row.dimension_values[0].value,
            "sessions": int(float(row.metric_values[0].value)),
            "pageviews": int(float(row.metric_values[1].value)),
            "bounceRate": round(float(row.metric_values[2].value), 1),
            "avgDuration": round(float(row.metric_values[3].value)),
        })
    pages.sort(key=lambda x: -x["sessions"])
    return pages[:20]


def fetch_devices(client, property_id, days=30):
    resp = run_report(
        client, property_id,
        [("29daysAgo", "today")],
        ["deviceCategory"],
        ["sessions"],
    )
    devices = {}
    total = 0
    for row in resp.rows:
        s = int(float(row.metric_values[0].value))
        devices[row.dimension_values[0].value] = s
        total += s
    result = {}
    for k, v in devices.items():
        result[k] = {"sessions": v, "pct": round(v / total * 100, 1) if total else 0}
    return result


def fetch_countries(client, property_id, days=30):
    resp = run_report(
        client, property_id,
        [("29daysAgo", "today")],
        ["country"],
        ["sessions"],
    )
    countries = []
    for row in resp.rows:
        countries.append({
            "name": row.dimension_values[0].value,
            "sessions": int(float(row.metric_values[0].value)),
        })
    countries.sort(key=lambda x: -x["sessions"])
    return countries[:10]


def build_ga_data(client, property_id):
    log("Özet veriler çekiliyor (7d, 30d, 90d)...")
    p7  = fetch_period_summary(client, property_id, 7)
    p30 = fetch_period_summary(client, property_id, 30)
    p90 = fetch_period_summary(client, property_id, 90)

    log("Günlük seri çekiliyor (90 gün)...")
    daily = fetch_daily_series(client, property_id)

    log("Trafik kaynakları çekiliyor...")
    sources = fetch_sources(client, property_id)

    log("Top sayfalar çekiliyor...")
    top_pages = fetch_top_pages(client, property_id)

    log("Cihaz dağılımı çekiliyor...")
    devices = fetch_devices(client, property_id)

    log("Ülke dağılımı çekiliyor...")
    countries = fetch_countries(client, property_id)

    return {
        "updated_at": datetime.now().isoformat(),
        "property_id": property_id,
        "period_7d": p7,
        "period_30d": p30,
        "period_90d": p90,
        "daily": daily,
        "sources": sources,
        "top_pages": top_pages,
        "devices": devices,
        "countries": countries,
        "ai_insights": "",
    }


def update_dashboard(ga_data):
    if not os.path.exists(DASHBOARD_HTML):
        log(f"Dashboard HTML bulunamadı: {DASHBOARD_HTML}")
        return

    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    start_marker = "/* ─── DATA BLOCK START ─── */"
    end_marker   = "/* ─── DATA BLOCK END ─── */"

    start_idx = html.find(start_marker)
    end_idx   = html.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        log("Dashboard HTML'de data block markerlari bulunamadı.")
        return

    new_block = (
        f"{start_marker}\n"
        f"const GA_DATA = {json.dumps(ga_data, ensure_ascii=False, indent=2)};\n"
        f"{end_marker}"
    )

    new_html = html[:start_idx] + new_block + html[end_idx + len(end_marker):]

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)

    log(f"Dashboard güncellendi: {DASHBOARD_HTML}")


def write_output_report(ga_data):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    path = os.path.join(OUTPUTS_DIR, f"{today}_analytics-report.md")

    if os.path.exists(path):
        log(f"Bugünün raporu zaten mevcut: {path}")
        return

    p30 = ga_data["period_30d"]
    p7  = ga_data["period_7d"]

    sessions_30 = int(p30.get("sessions", 0))
    sessions_7  = int(p7.get("sessions", 0))
    users_30    = int(p30.get("activeUsers", 0))
    bounce_30   = round(p30.get("bounceRate", 0) * 100, 1)
    avg_dur_30  = int(p30.get("averageSessionDuration", 0))

    top3_pages = ga_data["top_pages"][:3]
    top3_sources = ga_data["sources"][:3]

    pages_md = "\n".join(
        f"  - `{p['path']}` — {p['sessions']} oturum, %{p['bounceRate']} bounce"
        for p in top3_pages
    )
    sources_md = "\n".join(
        f"  - {s['name']}: {s['sessions']} oturum (%{s['pct']})"
        for s in top3_sources
    )

    content = f"""# Analytics Raporu — {today}

## Özet (Son 30 Gün)
- **Oturumlar:** {sessions_30:,}
- **Kullanıcılar:** {users_30:,}
- **Hemen Çıkma:** %{bounce_30}
- **Ort. Süre:** {avg_dur_30 // 60}d {avg_dur_30 % 60}sn

## Son 7 Gün
- Oturumlar: {sessions_7:,}

## Top Sayfalar (30 Gün)
{pages_md}

## Trafik Kaynakları (30 Gün)
{sources_md}

## AI Tavsiyeleri
{ga_data.get('ai_insights') or '(Henüz üretilmedi — Claude ile çalıştırın)'}

---
_Güncelleme: {ga_data['updated_at']}_
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Rapor yazıldı: {path}")


def main():
    log("=== Retrocameraland Analytics — Veri Çekme Başlıyor ===")

    try:
        property_id = load_config()
        log(f"Property ID: {property_id}")
    except (FileNotFoundError, ValueError) as e:
        log(f"HATA: {e}")
        sys.exit(1)

    try:
        client = build_client()
        log("GA4 client oluşturuldu")
    except (ImportError, Exception) as e:
        log(f"HATA: {e}")
        sys.exit(1)

    try:
        ga_data = build_ga_data(client, property_id)
    except Exception as e:
        log(f"API HATA: {e}")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        today = date.today().strftime("%Y-%m-%d")
        with open(os.path.join(OUTPUTS_DIR, f"{today}_ga-error.log"), "w") as f:
            f.write(str(e))
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ga_data, f, ensure_ascii=False, indent=2)
    log(f"Veri kaydedildi: {OUTPUT_JSON}")

    update_dashboard(ga_data)
    write_output_report(ga_data)

    log("=== Tamamlandı ===")


if __name__ == "__main__":
    main()
