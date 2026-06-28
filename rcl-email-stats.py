#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Email Stats — kampanya + Brevo istatistiklerini HQ dashboard'a besler.
Çıktı: data-script bloğuna `const EMAIL = {...}` (marker'lı) yazar.
Çalıştır: python3 rcl-email-stats.py   (HEARTBEAT/cron'a eklenebilir)
"""
import os, sys, json, re, urllib.request, urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DB = os.path.join(ROOT, "rcl-campaigns.json")
from rcl_config import write_block, publish   # ANA KAYNAK yolu + marker + push rcl_config.py'de (tek yer)

def _env(key, d=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="): return line.split("=", 1)[1].strip()
    except Exception: pass
    return os.environ.get(key, d)

BREVO_KEY = _env("BREVO_API_KEY")

def brevo_stats(tag):
    try:
        url = f"https://api.brevo.com/v3/smtp/statistics/aggregatedReport?tag={urllib.parse.quote(tag)}&days=90"
        req = urllib.request.Request(url)
        req.add_header("api-key", BREVO_KEY); req.add_header("accept", "application/json")
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception:
        return {}

def pct(a, b): return round(a / b * 100, 1) if b else 0.0

def build():
    try: camps = json.load(open(CAMPAIGN_DB))
    except Exception: camps = []
    rows, t_sent = [], 0; t_deliv = t_open = t_click = 0
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
    rows.sort(key=lambda r: r["date"], reverse=True)
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "totals": {"campaigns": len(camps), "sent": t_sent, "delivered": t_deliv,
                   "open_rate": pct(t_open, t_deliv), "click_rate": pct(t_click, t_deliv),
                   "subscribers_target": 0},
        "campaigns": rows,
    }

def inject(data):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    body = body.replace("</", "<\\/")  # gömülü HTML'deki </script> data-script'i bozmasın (JSON.parse geri çözer)
    write_block("EMAIL", f"const EMAIL = {body};")   # SADECE ANA KAYNAK; canliya publish ile gider
    print("  ✓ ANA KAYNAK guncellendi (EMAIL)")

if __name__ == "__main__":
    d = build()
    print(f"EMAIL: {d['totals']['campaigns']} kampanya · gönderilen {d['totals']['sent']} · "
          f"açılma %{d['totals']['open_rate']} · tıklama %{d['totals']['click_rate']}")
    inject(d)
    publish("email-stats")
