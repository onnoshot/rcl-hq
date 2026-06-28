#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL DASHBOARD — MERKEZI AYAR & YAYINLAMA  (tek dogru-kaynak)
============================================================
Tum fetch scriptleri (shopify / youtube / instagram / ga4 / email-stats)
BURADAN okur. Yol, token veya marker degisikligini SADECE bu dosyada yap.

Mimari (karisik kablo YOK):
  retrocameraland-hq-dashboard.html   = ANA KAYNAK. UI + tum veri bloklari burada.
                                        Dashboard'u duzenlemek istersen SADECE bunu duzenle.
  her fetch script  -> write_block() ile kendi marker blogunu ANA KAYNAGA yazar
                    -> publish() ile ANA KAYNAGI Vercel repo'suna kopyalar + push eder
  data.js           = ANA KAYNAKTAN turetilir (legacy youtube.html + instagram.html okur)
                      Elle duzenlenmez; publish() her seferinde yeniden uretir.

publish() DAIMA remote ucuna senkron olur (git fetch + reset --hard) -> ASLA catallanmaz.
flock ile es zamanli calismalar serilesir -> push yarisi olmaz.
"""
import os
import shutil
import subprocess
import fcntl
from datetime import datetime

SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))

# ─── YOLLAR (repoyu tasirsan SADECE burayi degistir) ───────────────────────
DASHBOARD_HTML = os.path.join(SCRIPT_DIR, "retrocameraland-hq-dashboard.html")  # ANA KAYNAK
REPO_DIR       = "/Users/onnoshot/Downloads/rcl-dashboard"                       # Vercel'e giden git repo
INDEX_HTML     = os.path.join(REPO_DIR, "index.html")                            # canli panel (ANA KAYNAKTAN kopyalanir)
DATA_JS        = os.path.join(REPO_DIR, "data.js")                               # ANA KAYNAKTAN turetilir
LOCK_FILE      = "/tmp/rcl-dashboard.lock"

# ─── TOKENLAR (rotasyon olunca SADECE burayi degistir) ─────────────────────
SHOPIFY_TOKEN  = "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"

# ─── VERI BLOK MARKERLARI (her feed'in ANA KAYNAKTAKI blogu) ───────────────
MARKERS = {
    "SHOPIFY":     ("/* ─── SHOPIFY DATA START ─── */",     "/* ─── SHOPIFY DATA END ─── */"),
    "YOUTUBE":     ("/* ─── YOUTUBE DATA START ─── */",     "/* ─── YOUTUBE DATA END ─── */"),
    "INSTAGRAM":   ("/* ─── INSTAGRAM DATA START ─── */",   "/* ─── INSTAGRAM DATA END ─── */"),
    "EMAIL":       ("/* ─── EMAIL DATA START ─── */",       "/* ─── EMAIL DATA END ─── */"),
    "GA4_TRAFFIC": ("/* ─── GA4 TRAFFIC DATA START ─── */", "/* ─── GA4 TRAFFIC DATA END ─── */"),
    "BLOG_SEO":    ("/* ─── BLOG SEO DATA START ─── */",    "/* ─── BLOG SEO DATA END ─── */"),
    "BUILD":       ("/* ─── BUILD INFO DATA START ─── */",  "/* ─── BUILD INFO DATA END ─── */"),
}

# Güncelleme sayacı — her publish()'te +1 ("kaçıncı güncelleme")
BUILD_NO_FILE = os.path.join(SCRIPT_DIR, ".rcl_build_no")

# data.js'e yansitilacak bloklar — legacy youtube.html + instagram.html bunlari okur
DATA_JS_BLOCKS = ["YOUTUBE", "SHOPIFY", "INSTAGRAM"]

GIT = ["git", "-c", "credential.helper=osxkeychain"]


def write_block(key, payload_js, path=DASHBOARD_HTML):
    """ANA KAYNAKTAKI <key> marker blogunu yeni icerikle degistirir.
    payload_js: iki marker ARASINA yazilacak JS (ornegin 'const SHOPIFY = {...};')."""
    start, end = MARKERS[key]
    with open(path, encoding="utf-8") as f:
        html = f.read()
    si = html.find(start)
    ei = html.find(end)
    if si == -1 or ei == -1:
        raise RuntimeError(f"{key} marker bulunamadi: {path}")
    block = f"{start}\n{payload_js}\n{end}"
    new = html[:si] + block + html[ei + len(end):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def _extract(html, key):
    start, end = MARKERS[key]
    si = html.find(start)
    ei = html.find(end)
    if si == -1 or ei == -1:
        return None
    return html[si:ei + len(end)]


def _build_data_js():
    """data.js icerigini ANA KAYNAKTAN turetir (DATA_JS_BLOCKS bloklarini cikarir)."""
    with open(DASHBOARD_HTML, encoding="utf-8") as f:
        html = f.read()
    parts = [_extract(html, k) for k in DATA_JS_BLOCKS]
    return "\n\n".join(p for p in parts if p) + "\n"


def _bump_build():
    """Güncelleme sayacını +1 yapar ve ANA KAYNAKTAKI BUILD blogunu günceller (kaçıncı güncelleme + zaman)."""
    try:
        n = int(open(BUILD_NO_FILE).read().strip()) + 1
    except Exception:
        n = 1
    with open(BUILD_NO_FILE, "w") as f:
        f.write(str(n))
    at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        write_block("BUILD", f'const BUILD = {{ "no": {n}, "at": "{at}" }};')
    except Exception:
        pass
    return n


def publish(label, log=print, write_data_js=True):
    """ANA KAYNAGI Vercel repo'suna yayinlar: senkron(fetch+reset) -> kopyala -> commit -> push.
    DAIMA remote ucundan basladigi icin baska oturum/scriptin push'ladigi commit'ler ezilmez,
    repo ASLA catallanmaz. flock ile es zamanli calismalar serilesir."""
    lock_fd = open(LOCK_FILE, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        _bump_build()   # ANA KAYNAK kopyalanmadan ÖNCE sayacı işle
        subprocess.run(GIT + ["fetch", "origin", "main"], cwd=REPO_DIR, capture_output=True)
        subprocess.run(GIT + ["reset", "--hard", "origin/main"], cwd=REPO_DIR, capture_output=True)
        shutil.copy(DASHBOARD_HTML, INDEX_HTML)
        add = ["index.html"]
        if write_data_js:
            with open(DATA_JS, "w", encoding="utf-8") as f:
                f.write(_build_data_js())
            add.append("data.js")
        subprocess.run(GIT + ["add"] + add, cwd=REPO_DIR, check=True, capture_output=True)
        r = subprocess.run(GIT + ["commit", "-m", f"data: {label} {datetime.now():%Y-%m-%dT%H:%M}"],
                           cwd=REPO_DIR, capture_output=True)
        if r.returncode != 0:
            log("Git: degisiklik yok, push atlandi")
            return
        subprocess.run(GIT + ["push"], cwd=REPO_DIR, check=True, capture_output=True)
        log("Git push tamamlandi")
    except subprocess.CalledProcessError as e:
        log(f"Git push hatasi: {e.stderr.decode().strip() if e.stderr else e}")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
