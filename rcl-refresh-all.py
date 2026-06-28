#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL — HER ŞEYİ GÜNCELLE
Tüm platform fetch'lerini sırayla çalıştırır (Shopify · YouTube · Instagram · GA4 · E-posta).
Her biri kendi bloğunu ANA KAYNAĞA yazar + publish() ile canlıya push eder (sayaç +1).
Panel butonu -> Vercel /api/refresh -> Mac dinleyici (rcl-refresh-listener) BUNU çağırır.
Elle de çalıştırılabilir: python3 rcl-refresh-all.py
"""
import os
import sys
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python3"

# Sıra: önce stok/satış (Shopify), sonra sosyal + analitik + e-posta
SCRIPTS = [
    ("Shopify",   "retrocameraland-shopify-fetch.py"),
    ("YouTube",   "retrocameraland-youtube-fetch.py"),
    ("Instagram", "retrocameraland-instagram-fetch.py"),
    ("GA4",       "retrocameraland-ga4-hq-fetch.py"),
    ("E-posta",   "rcl-email-stats.py"),
]


def log(m):
    print(f"[{datetime.now():%H:%M:%S}] {m}", flush=True)


def main():
    log("=== HER ŞEYİ GÜNCELLE başladı ===")
    ok, fail = [], []
    for name, script in SCRIPTS:
        path = os.path.join(ROOT, script)
        if not os.path.exists(path):
            log(f"  ATLANDI {name}: {script} yok")
            continue
        log(f"  → {name} güncelleniyor...")
        try:
            r = subprocess.run([PY, path], cwd=ROOT, capture_output=True, text=True, timeout=300)
            if r.returncode == 0:
                ok.append(name); log(f"  ✓ {name} tamam")
            else:
                fail.append(name)
                tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
                log(f"  ✗ {name} HATA: {tail[0][:160]}")
        except subprocess.TimeoutExpired:
            fail.append(name); log(f"  ✗ {name} zaman aşımı")
        except Exception as e:
            fail.append(name); log(f"  ✗ {name} hata: {e}")
    # Son adım: HERMES CEO — taze veriyi analiz et + canlıya yayınla (kredi yoksa zarif atla)
    hermes = os.path.join(ROOT, "rcl-hermes-ceo.py")
    if os.path.exists(hermes):
        log("  → Hermes CEO analiz ediyor...")
        try:
            r = subprocess.run([PY, hermes, "--publish"], cwd=ROOT, capture_output=True, text=True, timeout=300)
            if r.returncode == 0:
                ok.append("Hermes"); log("  ✓ Hermes tamam")
            else:
                tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
                log(f"  ~ Hermes atlandı: {tail[0][:160]}")
        except Exception as e:
            log(f"  ~ Hermes atlandı: {e}")

    log(f"=== Bitti — başarılı: {', '.join(ok) or '-'} | hatalı: {', '.join(fail) or '-'} ===")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
