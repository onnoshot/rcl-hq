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
SEEN_FILE = os.path.join(ROOT, ".rcl_refresh_seen")
LOCK_FILE = "/tmp/rcl-refresh-listener.lock"


def log(m):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {m}", flush=True)


def get_requested():
    req = urllib.request.Request(ENDPOINT, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return (json.loads(r.read()) or {}).get("requested_at")


def main():
    # Aynı anda tek çalışma
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 0  # önceki refresh sürüyor

    try:
        req_at = get_requested()
    except Exception as e:
        log(f"yoklama hatası: {e}")
        return 0
    if not req_at:
        return 0  # henüz hiç istek yok (tablo boş)

    last = ""
    if os.path.exists(SEEN_FILE):
        try:
            last = open(SEEN_FILE).read().strip()
        except Exception:
            pass
    if req_at == last:
        return 0  # yeni istek yok (zaten işlendi)

    log(f"Yeni güncelleme isteği: {req_at} -> rcl-refresh-all çalışıyor")
    subprocess.run([sys.executable or "python3", os.path.join(ROOT, "rcl-refresh-all.py")], cwd=ROOT)
    with open(SEEN_FILE, "w") as f:
        f.write(req_at)
    log("Güncelleme tamam.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
