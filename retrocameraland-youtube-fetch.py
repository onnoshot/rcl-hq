#!/usr/bin/env python3
"""
Retrocameraland — YouTube Veri Çekici
Channel stats + son videolar + Analytics (etkinleştirilince otomatik devreye girer).

Kullanım:
    python3 retrocameraland-youtube-fetch.py
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE    = os.path.join(SCRIPT_DIR, "yt_token.json")
CLIENT_SECRET = os.path.join(SCRIPT_DIR, "yt_client_secret.json")
DASHBOARD_HTML = os.path.join(SCRIPT_DIR, "retrocameraland-hq-dashboard.html")
DATA_JS        = "/Users/onnoshot/Downloads/rcl-dashboard/data.js"

START_MARKER  = "/* ─── YOUTUBE DATA START ─── */"
END_MARKER    = "/* ─── YOUTUBE DATA END ─── */"

CHANNEL_ID    = "UCq0jJ7knS1MDtNgx8DtJCvw"
SCOPES        = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
MONTH_TR = {
    "01":"Oca","02":"Şub","03":"Mar","04":"Nis","05":"May","06":"Haz",
    "07":"Tem","08":"Ağu","09":"Eyl","10":"Eki","11":"Kas","12":"Ara",
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def wait_for_network(host="www.googleapis.com", retries=12, delay=10):
    import socket
    for i in range(retries):
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(host, 443)
            return True
        except OSError:
            if i == 0:
                log("Ağ bekleniyor...")
            time.sleep(delay)
    log("HATA: Ağa bağlanılamadı, çıkılıyor.")
    sys.exit(1)


def get_credentials():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def fetch_channel_stats(yt):
    resp = yt.channels().list(
        part="snippet,statistics,brandingSettings",
        mine=True
    ).execute()
    items = resp.get("items", [])
    if not items:
        return {}
    ch = items[0]
    st = ch["statistics"]
    return {
        "title":       ch["snippet"]["title"],
        "channel_id":  ch["id"],
        "subscribers": int(st.get("subscriberCount", 0)),
        "total_views": int(st.get("viewCount", 0)),
        "video_count": int(st.get("videoCount", 0)),
    }


def fetch_recent_videos(yt, n=10):
    search_resp = yt.search().list(
        channelId=CHANNEL_ID,
        part="snippet",
        order="date",
        maxResults=n,
        type="video"
    ).execute()

    items = search_resp.get("items", [])
    if not items:
        return []

    vid_ids = ",".join(i["id"]["videoId"] for i in items)
    stats_resp = yt.videos().list(
        part="statistics,snippet,contentDetails",
        id=vid_ids
    ).execute()

    videos = []
    for v in stats_resp.get("items", []):
        sn = v["snippet"]
        st = v["statistics"]
        pub = sn["publishedAt"][:10]
        dt = datetime.strptime(pub, "%Y-%m-%d")
        mon = MONTH_TR[dt.strftime("%m")]
        videos.append({
            "id":       v["id"],
            "title":    sn["title"][:60],
            "date":     f"{dt.day} {mon} {dt.year}",
            "views":    int(st.get("viewCount", 0)),
            "likes":    int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "url":      f"https://youtu.be/{v['id']}",
        })
    return videos


def fetch_analytics(ya):
    """YouTube Analytics — eğer API etkinleştirilmişse."""
    today  = datetime.today().strftime("%Y-%m-%d")
    d30    = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    # monthly dimension requires both start and end to be 1st of a month
    now = datetime.today()
    month_end   = now.replace(day=1).strftime("%Y-%m-%d")          # 1st of current month
    six_ago     = (now.replace(day=1) - timedelta(days=150)).replace(day=1)
    d180        = six_ago.strftime("%Y-%m-%d")

    def query(start, end, metrics, dimensions=None, filters=None):
        kwargs = dict(ids="channel==MINE", startDate=start, endDate=end, metrics=metrics)
        if dimensions:
            kwargs["dimensions"] = dimensions
            kwargs["sort"] = dimensions
        if filters:
            kwargs["filters"] = filters
        return ya.reports().query(**kwargs).execute()

    # Son 30 gün özet
    r30 = query(d30, today, "views,estimatedMinutesWatched,subscribersGained,subscribersLost,averageViewDuration")
    row30 = (r30.get("rows") or [[0,0,0,0,0]])[0]

    # Son 365 gün izlenme saati — creatorContentType dimension ile tüm içerik tipleri
    d365 = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    r365 = query(d365, today, "estimatedMinutesWatched", dimensions="creatorContentType")
    rows365 = r365.get("rows") or []
    # Her satır: [contentType, minutes]
    min_by_type = {row[0]: int(row[1]) for row in rows365}
    min_long   = min_by_type.get("videoOnDemand", 0)
    min_shorts = min_by_type.get("shorts", 0)
    min_live   = min_by_type.get("liveStream", 0)
    min_total  = sum(min_by_type.values())
    watch_hours_year        = round(min_total  / 60, 1)
    watch_hours_year_long   = round(min_long   / 60, 1)
    watch_hours_year_shorts = round(min_shorts / 60, 1)
    log(f"  365g: {watch_hours_year_long}h VOD + {watch_hours_year_shorts}h Shorts + {round(min_live/60,1)}h Live = {watch_hours_year}h toplam")

    # Aylık trend (son 6 ay)
    rm = query(d180, month_end, "views,estimatedMinutesWatched,subscribersGained", dimensions="month")
    monthly = []
    for row in (rm.get("rows") or []):
        key = row[0]  # YYYY-MM
        dt  = datetime.strptime(key, "%Y-%m")
        monthly.append({
            "label":       f"{MONTH_TR[dt.strftime('%m')]} {dt.strftime('%y')}",
            "views":       int(row[1]),
            "watch_min":   int(row[2]),
            "subs_gained": int(row[3]),
        })

    return {
        "last_30d": {
            "views":          int(row30[0]),
            "watch_hours":    round(int(row30[1]) / 60, 1),
            "subs_gained":    int(row30[2]),
            "subs_lost":      int(row30[3]),
            "avg_view_sec":   int(row30[4]),
        },
        "watch_hours_year":        watch_hours_year,
        "watch_hours_year_long":   watch_hours_year_long,
        "watch_hours_year_shorts": watch_hours_year_shorts,
        "monthly": monthly,
    }


def build_yt_data():
    creds = get_credentials()
    yt    = build("youtube",         "v3", credentials=creds)
    ya    = build("youtubeAnalytics","v2", credentials=creds)

    log("Kanal istatistikleri çekiliyor...")
    channel = fetch_channel_stats(yt)
    log(f"  {channel.get('title')} | {channel.get('subscribers'):,} abone | {channel.get('total_views'):,} izlenme")

    log("Son videolar çekiliyor...")
    videos = fetch_recent_videos(yt, n=10)
    log(f"  {len(videos)} video getirildi")

    analytics = {}
    try:
        log("Analytics verisi çekiliyor...")
        analytics = fetch_analytics(ya)
        log(f"  Son 30g: {analytics['last_30d']['views']:,} izlenme, "
            f"{analytics['last_30d']['subs_gained']:+} abone")
    except HttpError as e:
        if "accessNotConfigured" in str(e) or "disabled" in str(e):
            log("  ⚠ YouTube Analytics API henüz etkin değil — atlanıyor")
        else:
            log(f"  ⚠ Analytics hatası: {e}")

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "channel":    channel,
        "analytics":  analytics,
        "videos":     videos,
        "sub_goal":   10000,
    }


def update_file(path, block):
    if not os.path.exists(path):
        log(f"HATA: Dosya bulunamadı: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    si = content.find(START_MARKER)
    ei = content.find(END_MARKER)
    if si == -1 or ei == -1:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(content[:si] + block + content[ei + len(END_MARKER):])
    log(f"Güncellendi: {path}")
    return True


def update_dashboard(data):
    block = f"{START_MARKER}\nconst YOUTUBE = {json.dumps(data, ensure_ascii=False, indent=2)};\n{END_MARKER}"
    update_file(DASHBOARD_HTML, block)
    update_file(DATA_JS, block)
    return True


def git_push():
    import subprocess, shutil
    dash_dir = "/Users/onnoshot/Downloads/rcl-dashboard"
    git = ["git", "-c", "credential.helper=osxkeychain"]
    try:
        shutil.copy(DASHBOARD_HTML, f"{dash_dir}/index.html")
        subprocess.run(git + ["add", "data.js", "index.html"], cwd=dash_dir, check=True, capture_output=True)
        r = subprocess.run(git + ["commit", "-m", f"data: youtube {datetime.now().strftime('%Y-%m-%dT%H:%M')}"],
                           cwd=dash_dir, capture_output=True)
        if r.returncode != 0:
            log("Git commit: değişiklik yok, push atlandı")
            return
        subprocess.run(git + ["push"], cwd=dash_dir, check=True, capture_output=True)
        log("Git push tamamlandı")
    except subprocess.CalledProcessError as e:
        log(f"Git push hatası: {e.stderr.decode().strip()}")


def main():
    log("=== Retrocameraland YouTube Fetch ===")
    wait_for_network()
    data = build_yt_data()
    update_dashboard(data)
    git_push()
    log("=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
