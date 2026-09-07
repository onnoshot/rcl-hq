#!/usr/bin/env python3
"""UniqBee Dashboard — GA4 trafik çekici.
Didi + Mare GA4 mülklerinden günlük ziyaretçi + trafik kaynağı çeker,
UniqBee Dashboard ingest endpoint'ine POST eder (o da Blob'a yazar).
Servis hesabı: ~/.config/ga4/ga4-reader.json (mülklere Viewer erişimi verilmeli).
Günlük çalıştır (LaunchAgent). Idempotent.
"""
import os, json, urllib.request, urllib.error, datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SA_PATH = os.path.expanduser("~/.config/ga4/ga4-reader.json")
INGEST_URL = "https://uniqbee-dashboard.vercel.app/api/traffic-ingest"
UNIQBEE_KEY = os.environ.get("UNIQBEE_KEY", "uniqbee2026panel")
PROPS = {"didi": "545397093", "mare": "542527885", "uniqbee": "534476710"}

creds = service_account.Credentials.from_service_account_file(
    SA_PATH, scopes=["https://www.googleapis.com/auth/analytics.readonly"])


def report(pid, body):
    creds.refresh(Request())
    req = urllib.request.Request(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{pid}:runReport",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + creds.token, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def fetch_brand(pid):
    # günlük ziyaretçi (son 30 gün)
    daily_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "date"}], "metrics": [{"name": "activeUsers"}],
        "orderBys": [{"dimension": {"dimensionName": "date"}}]})
    daily = []
    for row in daily_r.get("rows", []):
        d = row["dimensionValues"][0]["value"]  # YYYYMMDD
        iso = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
        daily.append({"date": iso, "users": int(row["metricValues"][0]["value"])})
    # toplamlar (bugün / 7g / 30g, deduplike)
    tot_r = report(pid, {
        "dateRanges": [{"startDate": "today", "endDate": "today", "name": "today"},
                       {"startDate": "6daysAgo", "endDate": "today", "name": "d7"},
                       {"startDate": "29daysAgo", "endDate": "today", "name": "d30"}],
        "metrics": [{"name": "activeUsers"}]})
    totals = {"today": 0, "d7": 0, "d30": 0}
    for row in tot_r.get("rows", []):
        totals[row["dimensionValues"][0]["value"]] = int(row["metricValues"][0]["value"])
    # trafik kaynağı (son 30 gün, oturum)
    ch_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "sessionDefaultChannelGroup"}], "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 8})
    channels = [{"name": row["dimensionValues"][0]["value"],
                 "sessions": int(row["metricValues"][0]["value"])} for row in ch_r.get("rows", [])]
    # buton tıklamaları (cta_click_* özel event'leri, son 30 gün)
    cl_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "eventName"}], "metrics": [{"name": "eventCount"}],
        "dimensionFilter": {"filter": {"fieldName": "eventName",
            "stringFilter": {"matchType": "BEGINS_WITH", "value": "cta_click_"}}},
        "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}], "limit": 15})
    clicks = [{"name": row["dimensionValues"][0]["value"],
               "count": int(row["metricValues"][0]["value"])} for row in cl_r.get("rows", [])]
    data = {"updatedAt": datetime.datetime.utcnow().isoformat() + "Z",
            "totals": totals, "daily": daily, "channels": channels, "clicks": clicks}
    data.update(fetch_extra(pid))
    return data


def fetch_extra(pid):
    # en çok ziyaret edilen sayfalar (giriş sayfası, son 30 gün)
    pg_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "landingPage"}], "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 8})
    top_pages = [{"path": row["dimensionValues"][0]["value"],
                  "sessions": int(row["metricValues"][0]["value"])} for row in pg_r.get("rows", [])]
    # cihaz dağılımı
    dv_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "deviceCategory"}], "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}]})
    devices = [{"name": row["dimensionValues"][0]["value"],
                "sessions": int(row["metricValues"][0]["value"])} for row in dv_r.get("rows", [])]
    # ülke dağılımı
    ct_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "country"}], "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 6})
    countries = [{"name": row["dimensionValues"][0]["value"],
                  "sessions": int(row["metricValues"][0]["value"])} for row in ct_r.get("rows", [])]
    # etkileşim: ort. oturum süresi + hemen çıkma oranı
    eg_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "metrics": [{"name": "averageSessionDuration"}, {"name": "bounceRate"}]})
    eg_row = (eg_r.get("rows") or [{}])[0].get("metricValues", [])
    avg_duration = float(eg_row[0]["value"]) if len(eg_row) > 0 else 0
    bounce_rate = float(eg_row[1]["value"]) if len(eg_row) > 1 else 0
    # en az bir CTA'ya tıklayan benzersiz kullanıcı sayısı
    eu_r = report(pid, {
        "dateRanges": [{"startDate": "29daysAgo", "endDate": "today"}],
        "metrics": [{"name": "activeUsers"}],
        "dimensionFilter": {"filter": {"fieldName": "eventName",
            "stringFilter": {"matchType": "BEGINS_WITH", "value": "cta_click_"}}}})
    eu_rows = eu_r.get("rows") or []
    engaged_users = int(eu_rows[0]["metricValues"][0]["value"]) if eu_rows else 0
    return {"topPages": top_pages, "devices": devices, "countries": countries,
            "engagement": {"avgDuration": avg_duration, "bounceRate": bounce_rate, "engagedUsers": engaged_users}}


def ingest(brand, data):
    req = urllib.request.Request(INGEST_URL, data=json.dumps({"brand": brand, "data": data}).encode(),
        headers={"Content-Type": "application/json", "x-uniqbee-key": UNIQBEE_KEY})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


if __name__ == "__main__":
    for brand, pid in PROPS.items():
        try:
            data = fetch_brand(pid)
            res = ingest(brand, data)
            print(f"✓ {brand}: bugün={data['totals']['today']} 7g={data['totals']['d7']} "
                  f"30g={data['totals']['d30']} | kanal={len(data['channels'])} | tıklama={len(data['clicks'])} | ingest={res.get('ok')}")
        except urllib.error.HTTPError as e:
            print(f"✗ {brand}: HTTP {e.code} — {e.read().decode()[:160]}")
        except Exception as e:
            print(f"✗ {brand}: {e}")
    print("Tamam.")
