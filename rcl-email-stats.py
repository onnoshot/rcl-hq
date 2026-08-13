#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Email Stats — kampanya + Brevo istatistiklerini HQ dashboard'a besler.
Çıktı: data-script bloğuna `const EMAIL = {...}` (marker'lı) yazar.
Çalıştır: python3 rcl-email-stats.py   (HEARTBEAT/cron'a eklenebilir)
"""
import os, sys, json, re, urllib.request, urllib.parse
from datetime import datetime, date, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DB = os.path.join(ROOT, "rcl-campaigns.json")
GROWTH_DB = os.path.join(ROOT, ".rcl_email_growth.json")
from rcl_config import write_block, publish   # ANA KAYNAK yolu + marker + push rcl_config.py'de (tek yer)

def _env(key, d=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="): return line.split("=", 1)[1].strip()
    except Exception: pass
    return os.environ.get(key, d)

BREVO_KEY = _env("BREVO_API_KEY")
DAILY_LIMIT = 300  # Brevo free plan sabit günlük gönderim kotası

def brevo_get(path):
    try:
        req = urllib.request.Request("https://api.brevo.com/v3" + path)
        req.add_header("api-key", BREVO_KEY); req.add_header("accept", "application/json")
        return json.loads(urllib.request.urlopen(req, timeout=20).read())
    except Exception:
        return {}

def brevo_stats(tag):
    return brevo_get(f"/smtp/statistics/aggregatedReport?tag={urllib.parse.quote(tag)}&days=90")

def pct(a, b): return round(a / b * 100, 1) if b else 0.0

def build_campaigns():
    try: camps = json.load(open(CAMPAIGN_DB))
    except Exception: camps = []
    rows = []
    t_sent = t_deliv = t_open = t_click = t_hard = t_soft = t_spam = 0
    for c in camps:
        s = brevo_stats(c["id"]) if (BREVO_KEY and c.get("sent")) else {}
        deliv = s.get("delivered", 0); opens = s.get("uniqueOpens", s.get("uniqueViews", 0)); clicks = s.get("uniqueClicks", 0)
        sent = c.get("sent", 0) or s.get("requests", 0)
        prev = ""
        try:
            prev = open(os.path.join(ROOT, "outputs", c["id"] + "_preview.html"), encoding="utf-8").read()
        except Exception:
            pass
        rows.append({
            "id": c["id"], "name": c.get("name", ""), "subject": c.get("subject", ""),
            "date": c.get("created", "")[:10], "status": c.get("status", "draft"),
            "sent": sent, "delivered": deliv, "opens": opens, "clicks": clicks,
            "open_rate": pct(opens, deliv), "click_rate": pct(clicks, deliv),
            "discount": c.get("discount"), "preview_html": prev,
        })
        t_sent += sent; t_deliv += deliv; t_open += opens; t_click += clicks
        t_hard += s.get("hardBounces", 0) or 0; t_soft += s.get("softBounces", 0) or 0
        t_spam += s.get("spamReports", 0) or 0
    rows.sort(key=lambda r: r["date"], reverse=True)
    # Sablon karti "Onizle" butonu icin: her tema anahtarinin EN YENI onizlemesi
    previews = {}
    for c in sorted(camps, key=lambda c: c.get("created", ""), reverse=True):
        th = c.get("theme", "")
        if not th or th in previews:
            continue
        try:
            previews[th] = open(os.path.join(ROOT, "outputs", c["id"] + "_preview.html"), encoding="utf-8").read()
        except Exception:
            pass
    return rows, previews, {
        "sent": t_sent, "delivered": t_deliv, "opened": t_open, "clicked": t_click,
        "hard_bounces": t_hard, "soft_bounces": t_soft, "spam": t_spam,
    }

def build_account():
    acc = brevo_get("/account")
    plan = (acc.get("plan") or [{}])[0].get("type", "")
    return {"email": acc.get("email", ""), "plan": plan}

def build_audience_and_lists():
    total_contacts = brevo_get("/contacts?limit=1").get("count", 0)
    flat = []
    offset = 0
    while offset <= 500:
        r = brevo_get(f"/contacts/lists?limit=50&offset={offset}")
        ls = r.get("lists", [])
        if not ls: break
        flat.extend(ls)
        offset += 50
    master = next((l for l in flat if l.get("name", "") == "RCL-Tum-Aboneler"), None)
    master_count = master.get("uniqueSubscribers", 0) if master else 0
    list_rows = sorted(
        [{"name": l.get("name", ""), "count": l.get("uniqueSubscribers", 0)} for l in flat],
        key=lambda x: x["count"], reverse=True,
    )
    return {"master_list": master_count, "total_contacts": total_contacts}, list_rows

def build_suppression():
    codes = {}
    offset = 0
    total = 0
    while offset <= 1000:
        r = brevo_get(f"/smtp/blockedContacts?limit=50&offset={offset}")
        cs = r.get("contacts", [])
        if not cs: break
        for c in cs:
            code = (c.get("reason") or {}).get("code", "unknown")
            codes[code] = codes.get(code, 0) + 1
        total += len(cs)
        offset += 50
    return {
        "blocked": total,
        "hard_bounces": codes.get("hardBounce", 0),
        "unsubscribed": codes.get("unsubscribedViaEmail", 0),
        "spam": codes.get("spam", 0) + codes.get("adminBlock", 0),
    }

def build_timeline(days=30):
    r = brevo_get(f"/smtp/statistics/reports?days={days}")
    by_date = {row["date"]: row for row in r.get("reports", [])}
    out = []
    today = date.today()
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        row = by_date.get(d, {})
        out.append({
            "date": d,
            "requests": row.get("requests", 0),
            "delivered": row.get("delivered", 0),
            "opens": row.get("uniqueOpens", 0),
            "clicks": row.get("uniqueClicks", 0),
        })
    return out

def build_quota():
    r = brevo_get("/smtp/statistics/aggregatedReport?days=1")
    used = r.get("requests", 0)
    pct_used = round(used / DAILY_LIMIT * 100) if DAILY_LIMIT else 0
    return {"limit": DAILY_LIMIT, "used": used, "remaining": max(DAILY_LIMIT - used, 0), "pct": pct_used}

def build_growth(master_list_count):
    today = date.today().isoformat()
    try:
        hist = json.load(open(GROWTH_DB))
    except Exception:
        hist = []
    if not hist or hist[-1]["date"] != today:
        hist.append({"date": today, "subscribers": master_list_count})
    else:
        hist[-1]["subscribers"] = master_list_count
    hist = hist[-90:]
    try:
        json.dump(hist, open(GROWTH_DB, "w"))
    except Exception:
        pass
    return hist

def build_pipeline(account_ok, camp_count):
    return [
        {"step": "Brevo API Bağlantısı", "detail": "bağlı" if account_ok else "anahtar/erişim sorunu", "ok": account_ok},
        {"step": "Kampanya Veritabanı", "detail": f"{camp_count} kampanya", "ok": camp_count > 0},
        {"step": "İstatistik Senkronizasyonu", "detail": "her kampanya için Brevo raporu çekildi", "ok": account_ok},
        {"step": "Canlıya Yayın", "detail": "ANA KAYNAK güncellendi", "ok": True},
    ]

def build_alerts(deliverability, suppression, quota):
    alerts = []
    br = deliverability["bounce_rate"]
    if br > 4:
        alerts.append({"level": "critical", "msg": f"Geri dönme oranı %{br} — liste hijyeni gerekiyor (sektör eşiği %4)."})
    elif br > 2:
        alerts.append({"level": "warn", "msg": f"Geri dönme oranı %{br} — izlemede tut (sektör eşiği %2)."})
    if suppression["spam"] > 0:
        alerts.append({"level": "warn", "msg": f"{suppression['spam']} şikayet (spam) bildirimi var."})
    if quota["pct"] >= 90:
        alerts.append({"level": "warn", "msg": f"Günlük gönderim kotasının %{quota['pct']}'i kullanıldı."})
    return alerts

def build():
    rows, previews, funnel = build_campaigns()
    account = build_account()
    account_ok = bool(account.get("email"))
    audience, lists = build_audience_and_lists()
    account["total_contacts"] = audience["total_contacts"]
    suppression = build_suppression()
    timeline = build_timeline(30)
    quota = build_quota()
    growth = build_growth(audience["master_list"])
    pipeline = build_pipeline(account_ok, len(rows))

    deliverability = {
        "delivery_rate": pct(funnel["delivered"], funnel["sent"]),
        "bounce_rate": pct(funnel["hard_bounces"] + funnel["soft_bounces"], funnel["sent"]),
        "open_rate": pct(funnel["opened"], funnel["delivered"]),
        "click_rate": pct(funnel["clicked"], funnel["delivered"]),
    }
    alerts = build_alerts(deliverability, suppression, quota)

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "totals": {"campaigns": len(rows), "sent": funnel["sent"], "delivered": funnel["delivered"],
                   "open_rate": pct(funnel["opened"], funnel["delivered"]),
                   "click_rate": pct(funnel["clicked"], funnel["delivered"]),
                   "subscribers_target": 0},
        "campaigns": rows,
        "previews": previews,
        "account": account,
        "audience": audience,
        "deliverability": deliverability,
        "funnel": {"sent": funnel["sent"], "delivered": funnel["delivered"],
                   "opened": funnel["opened"], "clicked": funnel["clicked"]},
        "pipeline": pipeline,
        "lists": lists,
        "alerts": alerts,
        "quota": quota,
        "timeline": timeline,
        "growth": growth,
        "suppression": suppression,
    }

def inject(data):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    body = body.replace("</", "<\\/")  # gömülü HTML'deki </script> data-script'i bozmasın (JSON.parse geri çözer)
    write_block("EMAIL", f"const EMAIL = {body};")   # SADECE ANA KAYNAK; canliya publish ile gider
    print("  ✓ ANA KAYNAK guncellendi (EMAIL)")

if __name__ == "__main__":
    d = build()
    print(f"EMAIL: {d['totals']['campaigns']} kampanya · gönderilen {d['totals']['sent']} · "
          f"açılma %{d['totals']['open_rate']} · tıklama %{d['totals']['click_rate']} · "
          f"{d['account'].get('total_contacts',0)} Brevo kişi · {d['audience'].get('master_list',0)} ana liste")
    inject(d)
    publish("email-stats")
