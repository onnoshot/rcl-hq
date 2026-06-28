#!/usr/bin/env python3
"""
Retrocameraland — Instagram Veri Çekici
Saatlik çalışır: profil istatistikleri + son gönderiler → dashboard günceller.
"""

import fcntl
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE    = os.path.join(SCRIPT_DIR, "ig_token.json")
from rcl_config import write_block, publish   # yol / marker / push hepsi rcl_config.py'de (tek yer)

MONTH_TR = {
    "01":"Oca","02":"Şub","03":"Mar","04":"Nis","05":"May","06":"Haz",
    "07":"Tem","08":"Ağu","09":"Eyl","10":"Eki","11":"Kas","12":"Ara",
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def ig_get(path, token):
    url = f"https://graph.facebook.com/v25.0/{path}"
    if "?" in url:
        url += f"&access_token={token}"
    else:
        url += f"?access_token={token}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_profile(ig_id, token):
    data = ig_get(f"{ig_id}?fields=username,name,followers_count,media_count", token)
    return {
        "username":       data["username"],
        "name":           data.get("name", "Retro Camera Land"),
        "followers":      data["followers_count"],
        "media_count":    data["media_count"],
    }


def fetch_recent_posts(ig_id, token, n=12):
    data = ig_get(
        f"{ig_id}/media?fields=id,timestamp,like_count,comments_count,media_type,permalink,media_url,thumbnail_url,caption&limit={n}",
        token
    )
    posts = []
    for p in data.get("data", []):
        ts  = p["timestamp"][:10]
        dt  = datetime.strptime(ts, "%Y-%m-%d")
        mon = MONTH_TR[dt.strftime("%m")]
        img = p.get("thumbnail_url") if p.get("media_type") == "VIDEO" else p.get("media_url")
        posts.append({
            "id":        p["id"],
            "date":      f"{dt.day} {mon} {dt.year}",
            "type":      p["media_type"],
            "likes":     p.get("like_count", 0),
            "comments":  p.get("comments_count", 0),
            "url":       p["permalink"],
            "image":     img or "",
            "caption":   (p.get("caption") or "")[:200],
        })
    return posts


def build_data(profile, posts):
    total_likes    = sum(p["likes"] for p in posts)
    total_comments = sum(p["comments"] for p in posts)
    avg_likes      = round(total_likes / len(posts)) if posts else 0
    type_counts    = {}
    for p in posts:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    return {
        "updated_at":     datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "username":       profile["username"],
        "name":           profile["name"],
        "followers":      profile["followers"],
        "media_count":    profile["media_count"],
        "avg_likes":      avg_likes,
        "total_engagement": total_likes + total_comments,
        "type_counts":    type_counts,
        "posts":          posts,
        "follower_goal":  10000,
    }


def update_dashboard(data):
    # ANA KAYNAGA yaz; data.js publish() icinde ANA KAYNAKTAN turetilir
    write_block("INSTAGRAM", f"const INSTAGRAM = {json.dumps(data, ensure_ascii=False, indent=2)};")
    log("ANA KAYNAK guncellendi (INSTAGRAM)")
    return True


def main():
    log("=== Retrocameraland Instagram Fetch ===")
    cfg   = load_token()
    token = cfg["page_access_token"]
    ig_id = cfg["ig_business_id"]

    log("Profil çekiliyor...")
    profile = fetch_profile(ig_id, token)
    log(f"  @{profile['username']} | {profile['followers']:,} takipçi | {profile['media_count']} gönderi")

    log("Son gönderiler çekiliyor...")
    posts = fetch_recent_posts(ig_id, token, n=12)
    log(f"  {len(posts)} gönderi | ort. {round(sum(p['likes'] for p in posts)/len(posts))} beğeni")

    data = build_data(profile, posts)
    update_dashboard(data)
    publish("instagram", log)
    log("=== Tamamlandı ✓ ===")


if __name__ == "__main__":
    main()
