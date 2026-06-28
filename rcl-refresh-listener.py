#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL — GÜNCELLEME DİNLEYİCİSİ (Mac tarafı köprü)
Panel butonu Vercel'e sinyal yazar; bu script (LaunchAgent ile 60sn'de bir) sinyali yoklar.
Yeni istek varsa rcl-refresh-all.py'yi çalıştırır (5 platform fetch + canlıya push).
Sadece GET yapar -> anahtar gerekmez. Dedup lokalde (.rcl_refresh_seen).
flock ile aynı anda iki refresh çalışmaz.
"""
import json
import os
import subprocess
import sys
import fcntl
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "https://rclhq.vercel.app/api/refresh"
EMAIL_ENDPOINT = "https://rclhq.vercel.app/api/email-send"
SEEN_FILE = os.path.join(ROOT, ".rcl_refresh_seen")
EMAIL_SEEN_FILE = os.path.join(ROOT, ".rcl_email_seen")
LOCK_FILE = "/tmp/rcl-refresh-listener.lock"
PY = sys.executable or "python3"


def log(m):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {m}", flush=True)


def _env(key, d=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, d)


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read()) or {}


def _post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read() or b"{}")
    except Exception:
        return {}


def process_refresh():
    try:
        req_at = _get(ENDPOINT).get("requested_at")
    except Exception as e:
        log(f"refresh yoklama hatası: {e}"); return
    if not req_at:
        return
    last = open(SEEN_FILE).read().strip() if os.path.exists(SEEN_FILE) else ""
    if req_at == last:
        return
    log(f"Yeni güncelleme isteği: {req_at} -> rcl-refresh-all")
    subprocess.run([PY, os.path.join(ROOT, "rcl-refresh-all.py")], cwd=ROOT)
    with open(SEEN_FILE, "w") as f:
        f.write(req_at)
    log("Güncelleme tamam.")


def process_email_queue():
    try:
        q = _get(EMAIL_ENDPOINT).get("queue") or []
    except Exception as e:
        log(f"e-posta yoklama hatası: {e}"); return
    seen = set()
    if os.path.exists(EMAIL_SEEN_FILE):
        try:
            seen = set(json.load(open(EMAIL_SEEN_FILE)))
        except Exception:
            pass
    key = _env("RCL_ALIM_KEY")
    pending = [it for it in q if it.get("status") == "pending" and str(it.get("id")) not in seen]
    for it in pending:
        iid = str(it.get("id")); theme = it.get("theme"); seg = it.get("segment", "all"); at = it.get("scheduled_at")
        log(f"E-posta isteği #{iid}: {theme} -> {seg} {'(zamanlı '+at+')' if at else '(şimdi)'}")
        args = [PY, os.path.join(ROOT, "rcl-campaign.py"), "schedule", theme, "--segment", seg]
        args += (["--at", at] if at else ["--now"])
        try:
            r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=300)
            out = r.stdout or ""
            res = {}
            try:
                res = json.loads(out[out.index("{"):])  # JSON kısmı (loglardan sonra)
            except Exception:
                res = {"raw": (r.stderr or out)[-300:]}
            status = "done" if (res.get("ok") and not any(c.get("error") for c in res.get("chunks", []))) else "error"
            if key:
                _post(EMAIL_ENDPOINT, {"key": key, "action": "complete", "id": it.get("id"),
                                       "status": status, "result": res})
            log(f"  -> {status}")
        except Exception as e:
            log(f"  HATA: {e}")
            if key:
                _post(EMAIL_ENDPOINT, {"key": key, "action": "complete", "id": it.get("id"),
                                       "status": "error", "result": {"error": str(e)[:200]}})
        seen.add(iid)
    if pending:
        json.dump(sorted(seen), open(EMAIL_SEEN_FILE, "w"))


def main():
    # Aynı anda tek çalışma
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 0
    process_refresh()
    process_email_queue()
    return 0


if __name__ == "__main__":
    sys.exit(main())
