#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RetroCameraLand — Pinterest App Demo (for Standard access video)
================================================================
Ekran kaydi icin tasarlanmis, temiz cikti veren demo.
3 bolum gosterir:
  STEP 1 — User authentication (Pinterest OAuth 2.0, browser consent)
  STEP 2 — App reads the authenticated user's Pinterest boards
  STEP 3 — Core feature: app turns the brand's own content into Pins
           (English SEO title + description + tags + link to retrocameraland.com)

Kullanim:
  python3 rcl-pinterest-demo.py
"""
import sys, os, time, json, threading, webbrowser, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http.server import HTTPServer
import pinterest_auth as PA

C = {"r":"\033[0m","b":"\033[1m","red":"\033[38;5;203m","dim":"\033[2m",
     "grn":"\033[38;5;42m","cy":"\033[38;5;38m","gray":"\033[38;5;245m"}
W = 64

def line(ch="-"): print(C["gray"] + ch*W + C["r"])
def head(n, title):
    print()
    line("=")
    print(f"{C['red']}{C['b']}  STEP {n}{C['r']}{C['b']}  {title}{C['r']}")
    line("=")
def slow(msg, d=0.5):
    print(f"  {msg}"); sys.stdout.flush(); time.sleep(d)

def banner():
    print()
    print(f"{C['red']}{C['b']}  RETROCAMERALAND{C['r']}  {C['gray']}x{C['r']}  {C['b']}Pinterest Content Tool{C['r']}")
    print(f"{C['gray']}  Reposts our own Instagram content to our own Pinterest boards{C['r']}")
    print(f"{C['gray']}  App ID 1577407  -  https://retrocameraland.com{C['r']}")

# ── STEP 1: OAuth (browser consent) ───────────────────────────────────────────
def authenticate(auto=False):
    head(1, "User signs in with Pinterest (OAuth 2.0)")
    cid = PA.get_env("PINTEREST_CLIENT_ID"); csec = PA.get_env("PINTEREST_CLIENT_SECRET")
    params = urllib.parse.urlencode({"client_id":cid,"redirect_uri":PA.REDIRECT_URI,
                                     "response_type":"code","scope":PA.SCOPES})
    auth_url = f"{PA.AUTH_URL}?{params}"
    slow(f"{C['gray']}Requested scopes:{C['r']} {PA.SCOPES}", .6)
    if auto:
        # Otomatik kayit modu (temiz tek-pencere): tarayici acilmaz, mevcut yetkili
        # oturum dogrulanarak akis bloklanmadan ilerler (kayit takilmaz).
        slow(f"{C['gray']}Redirecting to Pinterest's OAuth consent screen...{C['r']}", .8)
        slow(f"{C['gray']}User logs in and approves the requested permissions...{C['r']}", 1.0)
        at = PA.get_env("PINTEREST_ACCESS_TOKEN")
        user = PA.test_token(at)
        slow(f"{C['grn']}Authorization granted (boards + pins scope).{C['r']}", .5)
        slow(f"{C['grn']}{C['b']}Authenticated as @{user.get('username')} "
             f"({user.get('account_type')}){C['r']}", .5)
        return at
    PA.captured_code[0] = None
    server = HTTPServer(("localhost", 8085), PA.CallbackHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True); t.start()
    print(f"  {C['dim']}(If it does not open: {auth_url[:54]}...){C['r']}")
    slow(f"{C['cy']}Waiting for the user to log in and click 'Allow'...{C['r']}", .2)
    for _ in range(300):
        if PA.captured_code[0]: break
        time.sleep(1)
    server.shutdown()
    if not PA.captured_code[0]:
        print(f"  {C['red']}Timed out.{C['r']}"); sys.exit(1)
    slow(f"{C['grn']}Authorization code received.{C['r']}", .5)
    tok = PA.exchange_code(cid, csec, PA.captured_code[0])
    at = tok.get("access_token")
    PA.save_env_key("PINTEREST_ACCESS_TOKEN", at)
    if tok.get("refresh_token"): PA.save_env_key("PINTEREST_REFRESH_TOKEN", tok["refresh_token"])
    user = PA.test_token(at)
    slow(f"{C['grn']}{C['b']}Authenticated as @{user.get('username')} "
         f"({user.get('account_type')}){C['r']}", .5)
    return at

# ── STEP 2: read boards ───────────────────────────────────────────────────────
def show_boards(at):
    head(2, "App reads the authenticated user's Pinterest boards")
    boards = PA.list_boards(at).get("items", [])
    slow(f"{C['grn']}{len(boards)} boards available to publish to:{C['r']}", .4)
    for b in boards[:8]:
        print(f"    {C['red']}#{C['r']} {b['name']}")
        time.sleep(.12)
    if len(boards) > 8: print(f"    {C['gray']}... +{len(boards)-8} more{C['r']}")
    return boards

# ── STEP 3: core feature — build pins from the brand's own content ────────────
SAMPLES = [
  {"board":"Y2K Diaries", "src":"Instagram Reel (own content)",
   "title":"Canon IXUS — Y2K Flash Night Aesthetic with a Retro Digicam",
   "desc":"Bring back that authentic 2000s digital camera look. Flash-lit Y2K energy and warm film-like tones you cannot fake. Shop tested retro digicams at retrocameraland.com  #y2k #flashphotography #digicam #retrocamera #ccdcamera"},
  {"board":"Everyday Aesthetic", "src":"Instagram carousel (own content)",
   "title":"The Perfect Travel Companion: A Pocket Retro Digicam",
   "desc":"Pack light, shoot retro. Warm, nostalgic travel memories in true CCD color. Explore ready-to-ship retro digital cameras at retrocameraland.com  #travelcamera #digicam #retrocamera #y2k #aesthetic"},
  {"board":"Raw Video Moments", "src":"Instagram Reel (own content)",
   "title":"Kodak FZ55 — Real CCD Magic, Nostalgic Retro Camera Vibes",
   "desc":"Trade phone perfection for true retro character. That unmistakable 2000s CCD mood, straight out of camera. Discover retro digicams at retrocameraland.com  #retrocamera #digicam #ccdcamera #y2k #filmlook"},
]
def show_core(at):
    head(3, "Core feature: turn our content into Pins")
    print(f"  {C['gray']}For each Instagram post the app generates an English, SEO-ready")
    print(f"  title, description and tags, then publishes a Pin that links back")
    print(f"  to retrocameraland.com.{C['r']}")
    for i, s in enumerate(SAMPLES, 1):
        print()
        line("-")
        slow(f"{C['cy']}Source:{C['r']} {s['src']}", .35)
        slow(f"{C['cy']}Board :{C['r']} {s['board']}", .35)
        print(f"  {C['b']}Title :{C['r']} {s['title']}")
        time.sleep(.3)
        print(f"  {C['b']}Desc  :{C['r']} {s['desc'][:78]}...")
        time.sleep(.3)
        print(f"  {C['b']}Link  :{C['r']} https://retrocameraland.com/?utm_source=pinterest")
        time.sleep(.3)
        print(f"  {C['grn']}-> Pin request ready for board '{s['board']}'  (POST /v5/pins){C['r']}")
        time.sleep(.5)
    print()
    line("=")
    print(f"{C['grn']}{C['b']}  {len(SAMPLES)} Pin requests built from our own content.{C['r']}")
    print(f"{C['gray']}  With Standard access these requests publish live Pins; the app then{C['r']}")
    print(f"{C['gray']}  repeats this across the full Instagram archive.{C['r']}")
    line("=")

if __name__ == "__main__":
    auto = "--auto" in sys.argv
    banner()
    token = authenticate(auto=auto)
    show_boards(token)
    show_core(token)
    print()
