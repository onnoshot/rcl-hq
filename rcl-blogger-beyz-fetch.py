#!/usr/bin/env python3
"""
rcl-blogger-beyz-fetch.py — "Blogger Beyz" dashboard sekmesi için veri üretir.

rcl-seo-blog-agent.py'ın outputs/*_seo-blog-*.md raporlarını okur, Shopify'daki
GÜNCEL canlı blog listesiyle kesiştirir (silinmiş/konsolide edilmiş kopyalar
otomatik elenir) ve dashboard'daki BLOGGER_BEYZ JS bloğunu üretir.

Kullanım:
    python3 rcl-blogger-beyz-fetch.py               # üret + yaz + push
    python3 rcl-blogger-beyz-fetch.py --dry-run      # sadece üret + özet yazdır
    python3 rcl-blogger-beyz-fetch.py --no-push      # yaz ama push etme
"""
import os, re, sys, json, glob
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from rcl_config import write_block, publish, MARKERS
from retrocameraland_api import shopify

LOG_DIR = os.path.join(SCRIPT_DIR, 'outputs')
BLOG_ID = 91197866123  # retro-dijital-kamera


def log(m):
    print(f"[{datetime.now():%H:%M:%S}] {m}", flush=True)


def parse_reports():
    """outputs/*_seo-blog-*.md dosyalarından {title, seo, url, handle, date, time} çıkar."""
    entries = []
    for path in sorted(glob.glob(os.path.join(LOG_DIR, '*_seo-blog-*.md'))):
        try:
            text = open(path, encoding='utf-8').read()
        except Exception:
            continue
        m = re.search(r'^# RCL SEO Blog — (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})', text, re.M)
        if not m:
            continue
        date_str, time_str = m.groups()
        for block in re.split(r'\n## ', text)[1:]:
            if block.startswith('❌'):
                continue
            title_line, _, body = block.partition('\n')
            title = title_line.strip()
            seo_m = re.search(r'SEO:\s*(\d+)/100', body)
            url_m = re.search(r'URL:\s*(\S+)', body)
            if not (seo_m and url_m):
                continue
            url = url_m.group(1)
            handle = url.rstrip('/').split('/')[-1]
            entries.append({
                'title': title, 'seo': int(seo_m.group(1)), 'url': url, 'handle': handle,
                'date': date_str, 'time': time_str, 'dt': f'{date_str}T{time_str}:00',
            })
    return entries


def get_live_articles():
    """Şu an canlıdaki blog makalelerini {handle: title} olarak döner."""
    out = {}
    since = 0
    while True:
        data = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit=250&since_id={since}&fields=id,handle,title")
        batch = data.get("articles", [])
        if not batch:
            break
        for a in batch:
            out[a["handle"]] = a["title"]
        since = batch[-1]["id"]
        if len(batch) < 250:
            break
    return out


def build_data():
    log("Raporlar okunuyor...")
    entries = parse_reports()
    log(f"  {len(entries)} rapor kaydı bulundu")

    log("Shopify'dan canlı makale listesi çekiliyor...")
    live = get_live_articles()
    log(f"  {len(live)} canlı makale")

    seen = {}
    for e in entries:
        if e['handle'] in live:
            e['title'] = live[e['handle']]  # her zaman GÜNCEL canlı başlığı kullan
            e['seo'] = min(100, e['seo'])   # score_seo() bazı edge-case'lerde 100'ü aşan
                                             # puan üretiyor (ayrı bir bug) — gösterimde kırp
            seen[e['handle']] = e  # aynı handle birden fazla raporda geçerse sonuncusu kalır
    live_entries = sorted(seen.values(), key=lambda e: e['dt'], reverse=True)

    seos = [e['seo'] for e in live_entries]
    total = len(live_entries)
    avg = round(sum(seos) / total) if total else 0
    best = max(seos) if seos else 0
    worst = min(seos) if seos else 0

    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    today_count = sum(1 for e in live_entries if e['date'] == today)
    week_count = sum(1 for e in live_entries if e['date'] >= week_ago)

    dist = {
        'good': sum(1 for s in seos if s >= 90),
        'mid':  sum(1 for s in seos if 75 <= s < 90),
        'low':  sum(1 for s in seos if s < 75),
    }

    daily = []
    for i in range(13, -1, -1):
        d = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        c = sum(1 for e in live_entries if e['date'] == d)
        daily.append({'date': d, 'count': c})

    last_posts = [
        {'title': e['title'], 'seo': e['seo'], 'url': e['url'], 'date': e['date'], 'time': e['time']}
        for e in live_entries[:15]
    ]

    return {
        'updated_at': now.isoformat(timespec='seconds'),
        'total_live': total,
        'avg_seo': avg,
        'best_seo': best,
        'worst_seo': worst,
        'today_count': today_count,
        'week_count': week_count,
        'distribution': dist,
        'daily': daily,
        'last_posts': last_posts,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-push', action='store_true')
    args = p.parse_args()

    data = build_data()
    log(f"Toplam canlı: {data['total_live']} | Ort. SEO: {data['avg_seo']} | "
        f"Bugün: {data['today_count']} | Bu hafta: {data['week_count']}")

    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        sys.exit(0)

    if 'BLOGGER_BEYZ' not in MARKERS:
        log("⚠ BLOGGER_BEYZ marker'ı rcl_config.py'da tanımlı değil — önce marker'ı ekleyin.")
        sys.exit(1)

    payload = f"const BLOGGER_BEYZ = {json.dumps(data, ensure_ascii=False)};"
    write_block("BLOGGER_BEYZ", payload)
    log("✓ Ana kaynağa yazıldı")

    if not args.no_push:
        publish("blogger-beyz", log=log)
