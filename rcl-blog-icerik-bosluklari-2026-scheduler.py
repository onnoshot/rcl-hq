#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Icerik Bosluklari 2026 — Zamanlanmis Yayinlayici
=====================================================
com.rcl.icerik-bosluklari-2026.plist tarafindan gunde 2 kez (10:00 / 22:00)
tetiklenir. Her calistiginda state dosyasindaki index'e gore SIRADAKI blogu
yayinlar, index'i ilerletir. 10 yazi bitince launchd job'unu kendi kendine
sokup (bootout) devre disi birakir. Idempotent:ayni index iki kez yayinlanmaz.
"""
import sys, os, json, subprocess, time, importlib.util

sys.path.insert(0, "/Users/onnoshot/Downloads/Agentlar")

_spec = importlib.util.spec_from_file_location(
    "rcl_blog_icerik_bosluklari_2026",
    "/Users/onnoshot/Downloads/Agentlar/rcl-blog-icerik-bosluklari-2026.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
POSTS, publish, log = _mod.POSTS, _mod.publish, _mod.log

STATE_FILE = "/Users/onnoshot/Downloads/Agentlar/.rcl_icerik_bosluklari_state.json"
LABEL = "com.rcl.icerik-bosluklari-2026"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, encoding="utf-8"))
        except Exception:
            pass
    return {"next_index": 0, "published": []}

def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def unload_self():
    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{LABEL}"], capture_output=True)

def main():
    state = load_state()
    idx = state["next_index"]
    if idx >= len(POSTS):
        log(f"Tum yazilar yayinlandi ({len(POSTS)}/{len(POSTS)}). Job kapatiliyor.")
        unload_self()
        return
    p = POSTS[idx]
    log(f"[{idx+1}/{len(POSTS)}] Yayinlaniyor: {p['title'][:60]}")
    try:
        result = publish(p, dry=False)
        state["published"].append({
            "index": idx, "handle": result.get("handle"), "id": result.get("id"),
            "title": p["title"], "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        state["next_index"] = idx + 1
        save_state(state)
        log(f"  OK -> {result.get('handle')}")
    except Exception as e:
        log(f"  HATA (index {idx} tekrar denenecek): {e}")
        # state ilerletilmedi -> bir sonraki tetiklemede ayni yazi tekrar denenir
        return
    if state["next_index"] >= len(POSTS):
        log("Son yazi da yayinlandi. Job kapatiliyor.")
        unload_self()

if __name__ == "__main__":
    main()
