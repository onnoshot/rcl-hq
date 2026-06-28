#!/usr/bin/env python3
"""
Retrocameraland — GA4 → HQ Dashboard fetch.
HQ dashboard'daki GA4_TRAFFIC + BLOG_SEO marker bloklarını canlı GA4 verisiyle günceller.
OAuth token: ~/.config/ga4/token.json  (analytics.readonly)

GA4_TRAFFIC: tamamen GA4'ten yeniden üretilir.
BLOG_SEO:    GA4 trafik alanları (views/organic/bounce/avg_dur) tazelenir;
             'seo' skorları + total_posts + aylık 'posts' sayıları mevcut bloktan
             başlık eşleşmesiyle TAŞINIR (bunlar GA4'te yok).

Kullanım:
    python3 retrocameraland-ga4-hq-fetch.py            # çek, yaz, push
    python3 retrocameraland-ga4-hq-fetch.py --dry-run  # sadece çek + özet yazdır
    python3 retrocameraland-ga4-hq-fetch.py --no-push   # yaz ama push etme
"""
import os, re, sys, json, time, shutil, subprocess, urllib.request
from datetime import datetime
from collections import defaultdict

from rcl_config import DASHBOARD_HTML as DASHBOARD, SHOPIFY_TOKEN, MARKERS, publish  # token/yol/marker/push tek yer: rcl_config.py
TOKEN_PATH = os.path.expanduser("~/.config/ga4/token.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROPERTY_ID = "493627571"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
SHOPIFY_STORE = "retrocameraland.myshopify.com"

def _shopify(path):
    req = urllib.request.Request(f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}")
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    return json.load(urllib.request.urlopen(req, timeout=30))

def fetch_shopify_articles():
    """Yayınlanmış TÜM blog makaleleri: title, handle, published_at."""
    arts = []
    for b in _shopify("blogs.json").get("blogs", []):
        since = 0
        while True:
            data = _shopify(f"blogs/{b['id']}/articles.json?limit=250&since_id={since}"
                            "&fields=id,title,handle,published_at")
            batch = data.get("articles", [])
            if not batch:
                break
            for a in batch:
                if a.get("published_at"):
                    arts.append({"title": a["title"], "handle": (a.get("handle") or "").lower(),
                                 "published_at": a["published_at"]})
            since = batch[-1]["id"]
            if len(batch) < 250:
                break
    return arts

GA4_START, GA4_END   = MARKERS["GA4_TRAFFIC"]
BLOG_START, BLOG_END = MARKERS["BLOG_SEO"]

TR_MONTHS = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
             "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

# GA4 default-channel -> dashboard bucket (name, color)
BUCKETS = [
    ("Organic",  "#30D158", {"Organic Search"}),
    ("Direct",   "#D4AF37", {"Direct"}),
    ("Social",   "#BF5AF2", {"Organic Social", "Paid Social", "Organic Video"}),
    ("Paid",     "#FF9F0A", {"Paid Search", "Cross-network"}),
    ("Referral", "#5AC8FA", {"Referral", "Email"}),
    ("Other",    "#6E6E73", {"Unassigned", "Organic Shopping", "Audio", "Mobile Push Notifications"}),
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def client():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return BetaAnalyticsDataClient(credentials=creds)


def _run(cl, dims, mets, start, end, limit=2000, agg=None, dimfilter=None):
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest, MetricAggregation, Filter, FilterExpression)
    kw = {}
    if dimfilter:
        field, substr = dimfilter
        kw["dimension_filter"] = FilterExpression(filter=Filter(
            field_name=field,
            string_filter=Filter.StringFilter(value=substr,
                match_type=Filter.StringFilter.MatchType.CONTAINS, case_sensitive=False)))
    return cl.run_report(RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in mets],
        limit=limit, metric_aggregations=agg or [], **kw))


def _agg_total():
    from google.analytics.data_v1beta.types import MetricAggregation
    return [MetricAggregation.TOTAL]


def fmt_dur(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def bucket_of(channel):
    for name, _c, members in BUCKETS:
        if channel in members:
            return name
    return "Other"


def build_ga4_traffic(cl):
    # 30d KPI totals
    r = _run(cl, [], ["sessions", "bounceRate", "averageSessionDuration"],
             "29daysAgo", "today", agg=_agg_total())
    row = (r.totals[0].metric_values if r.totals else r.rows[0].metric_values)
    sessions_30 = int(float(row[0].value))
    bounce_30   = round(float(row[1].value) * 100, 1)
    avgdur_30   = int(round(float(row[2].value)))

    # 30d channels -> buckets
    r = _run(cl, ["sessionDefaultChannelGroup"], ["sessions"], "29daysAgo", "today")
    bsum = {name: 0 for name, _c, _m in BUCKETS}
    organic_search = 0
    for x in r.rows:
        ch = x.dimension_values[0].value
        s = int(float(x.metric_values[0].value))
        bsum[bucket_of(ch)] += s
        if ch == "Organic Search":
            organic_search += s
    tot = sum(bsum.values()) or 1
    sources = [{"name": name, "color": color,
                "sessions": bsum[name], "pct": round(bsum[name] / tot * 100, 1)}
               for name, color, _m in BUCKETS]
    organic_pct = round(organic_search / tot * 100, 1)

    # monthly (last 4 calendar months): all sessions + organic search sessions
    r = _run(cl, ["yearMonth"], ["sessions"], "120daysAgo", "today")
    m_all = {x.dimension_values[0].value: int(float(x.metric_values[0].value)) for x in r.rows}
    r = _run(cl, ["yearMonth", "sessionDefaultChannelGroup"], ["sessions"], "120daysAgo", "today")
    m_org = {}
    for x in r.rows:
        if x.dimension_values[1].value == "Organic Search":
            m_org[x.dimension_values[0].value] = int(float(x.metric_values[0].value))
    months = sorted(m_all.keys())[-4:]
    monthly = []
    for ym in months:
        y, mo = int(ym[:4]), int(ym[4:6])
        monthly.append({"label": f"{TR_MONTHS[mo]} {str(y)[2:]}",
                        "sessions": m_all[ym], "organic": m_org.get(ym, 0)})

    return {
        "updated_at": datetime.now().isoformat(),
        "kpi_30d": {"visitors": sessions_30, "organic_pct": organic_pct,
                    "bounce_rate": bounce_30, "avg_session_sec": avgdur_30},
        "monthly": monthly,
        "sources": sources,
    }, organic_search


def _art_handle(path):
    """GA4 pagePath -> makale handle (son segment). /blogs/{blog}/{article}"""
    p = path.split("?")[0].rstrip("/")
    return p.split("/")[-1].lower()


def build_blog_seo(cl, prev, organic_search_30):
    # Önceki SEO skorlarını taşı (GA4'te yok; yayın anında hesaplanmış). 50 karakterle eşle.
    prev_seo = {}
    for p in prev.get("posts", []):
        prev_seo[(p.get("title") or "")[:50]] = p.get("seo", 86)

    # 1) Yetkili liste: TÜM yayınlı Shopify makaleleri
    articles = fetch_shopify_articles()
    log(f"  Shopify: {len(articles)} yayınlı blog makalesi")

    # 2) GA4 blog sayfa metrikleri — makale handle bazlı (TR sayfalar, /en hariç)
    def is_tr(path):
        return "/blogs/" in path and not path.startswith("/en")

    ga = {}
    r = _run(cl, ["pagePath"], ["screenPageViews", "bounceRate", "averageSessionDuration"],
             "29daysAgo", "today", dimfilter=("pagePath", "/blogs/"))
    for x in r.rows:
        path = x.dimension_values[0].value
        if not is_tr(path):
            continue
        h = _art_handle(path)
        pv = int(float(x.metric_values[0].value))
        cur = ga.setdefault(h, {"views": 0, "bw": 0.0, "dw": 0.0})
        cur["views"] += pv
        cur["bw"] += float(x.metric_values[1].value) * 100 * pv
        cur["dw"] += float(x.metric_values[2].value) * pv

    org = {}
    r = _run(cl, ["pagePath", "sessionDefaultChannelGroup"], ["sessions"],
             "29daysAgo", "today", dimfilter=("pagePath", "/blogs/"))
    for x in r.rows:
        path = x.dimension_values[0].value
        if is_tr(path) and x.dimension_values[1].value == "Organic Search":
            h = _art_handle(path)
            org[h] = org.get(h, 0) + int(float(x.metric_values[0].value))

    # 3) posts = TÜM makaleler + (varsa) GA4 trafiği
    posts = []
    for a in articles:
        h = a["handle"]
        g = ga.get(h)
        views = g["views"] if g else 0
        bounce = round(g["bw"] / views, 1) if (g and views) else 0.0
        dur_sec = int(round(g["dw"] / views)) if (g and views) else 0
        posts.append({
            "title": a["title"][:90],
            "views": views,
            "organic": org.get(h, 0),
            "bounce": bounce,
            "avg_dur_sec": dur_sec,
            "avg_dur": fmt_dur(dur_sec),
            "orders": 0,
            "seo": prev_seo.get(a["title"][:50], 86),
        })
    posts.sort(key=lambda p: -p["views"])
    # Shopify erişilemezse önceki listeye düş (boş bırakma)
    total_posts = len(posts) if posts else prev.get("total_posts", len(prev.get("posts", [])))
    if not posts:
        posts = prev.get("posts", [])

    # 4) Aylık: yayın tarihinden post sayısı (gerçek) + GA4 blog trafiği
    posts_by_month = defaultdict(int)
    for a in articles:
        ym = (a.get("published_at") or "")[:7].replace("-", "")  # YYYYMM
        if len(ym) == 6:
            posts_by_month[ym] += 1
    r = _run(cl, ["yearMonth"], ["sessions"], "120daysAgo", "today", dimfilter=("pagePath", "/blogs/"))
    m_tr = {x.dimension_values[0].value: int(float(x.metric_values[0].value)) for x in r.rows}
    months = sorted(m_tr.keys())[-4:]
    monthly = []
    for ym in months:
        y, mo = int(ym[:4]), int(ym[4:6])
        monthly.append({"label": f"{TR_MONTHS[mo]} {str(y)[2:]}",
                        "posts": posts_by_month.get(ym, 0), "traffic": m_tr[ym]})

    return {
        "updated_at": datetime.now().isoformat(),
        "total_posts": total_posts,
        "monthly_organic": organic_search_30,
        "posts": posts,
        "monthly": monthly,
    }


def read_block(html, start, end, varname):
    s = html.find(start); e = html.find(end)
    if s == -1 or e == -1:
        return None
    seg = html[s + len(start):e]
    m = re.search(r"const \w+ = (\{.*\});", seg, re.S)
    return json.loads(m.group(1)) if m else None


def write_block(html, start, end, varname, obj):
    s = html.find(start); e = html.find(end)
    block = f"{start}\nconst {varname} = {json.dumps(obj, ensure_ascii=False)};\n{end}"
    return html[:s] + block + html[e + len(end):]


def main():
    dry = "--dry-run" in sys.argv
    nopush = "--no-push" in sys.argv or dry
    log("=== GA4 → HQ Dashboard ===")
    cl = client()
    log("GA4_TRAFFIC çekiliyor...")
    ga4, org_search = build_ga4_traffic(cl)
    log(f"  30g: {ga4['kpi_30d']['visitors']:,} oturum | organik %{ga4['kpi_30d']['organic_pct']} "
        f"| bounce %{ga4['kpi_30d']['bounce_rate']} | {ga4['kpi_30d']['avg_session_sec']}sn")
    log(f"  kaynaklar: " + ", ".join(f"{s['name']} {s['sessions']}(%{s['pct']})" for s in ga4['sources']))
    log(f"  aylık: " + ", ".join(f"{m['label']}:{m['sessions']}/{m['organic']}org" for m in ga4['monthly']))

    html = open(DASHBOARD, encoding="utf-8").read()
    prev_blog = read_block(html, BLOG_START, BLOG_END, "BLOG_SEO") or {}
    log("BLOG_SEO çekiliyor...")
    blog = build_blog_seo(cl, prev_blog, org_search)
    log(f"  {len(blog['posts'])} blog yazısı | {blog['monthly_organic']:,} organik (30g) | "
        f"toplam {blog['total_posts']} yayınlı yazı")
    if blog["posts"][:3]:
        for p in blog["posts"][:3]:
            log(f"    · {p['views']}v {p['organic']}org seo{p['seo']} — {p['title'][:42]}")

    if dry:
        log("DRY-RUN — dosya yazılmadı."); return

    html = write_block(html, GA4_START, GA4_END, "GA4_TRAFFIC", ga4)
    html = write_block(html, BLOG_START, BLOG_END, "BLOG_SEO", blog)
    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"HQ dashboard güncellendi: {DASHBOARD}")
    if not nopush:
        publish("ga4", log, write_data_js=False)
    log("=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
