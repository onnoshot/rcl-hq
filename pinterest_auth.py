#!/usr/bin/env python3
"""
pinterest_auth.py — Pinterest OAuth 2.0 kurulum scripti (tek seferlik).

Kullanım:
  python3 pinterest_auth.py

Gereksinimler:
  .env dosyasında PINTEREST_CLIENT_ID ve PINTEREST_CLIENT_SECRET olmalı.

Çıktı:
  .env'e PINTEREST_ACCESS_TOKEN yazar ve bağlantıyı test eder.
"""

import os, sys, json, base64, webbrowser, urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')

def load_env():
    env = {}
    try:
        for line in open(ENV_FILE).readlines():
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

def save_env_key(key, value):
    env = load_env()
    env[key] = value
    lines = [f"{k}={v}\n" for k, v in env.items()]
    with open(ENV_FILE, 'w') as f:
        f.writelines(lines)
    print(f"  ✓ {key} .env'e kaydedildi")

def get_env(key):
    return load_env().get(key) or os.environ.get(key, '')


# ── OAuth 2.0 flow ────────────────────────────────────────────────────────────
REDIRECT_URI = "http://localhost:8085/callback"
AUTH_URL     = "https://www.pinterest.com/oauth/"
TOKEN_URL    = "https://api.pinterest.com/v5/oauth/token"
SCOPES       = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

captured_code = [None]

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "/callback" in self.path:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            captured_code[0] = params.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "<h2>✅ Yetkilendirme başarılı! Bu sekmeyi kapatabilirsiniz.</h2>"
            self.wfile.write(msg.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # sessiz


def exchange_code(client_id, client_secret, code):
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    body  = urllib.parse.urlencode({
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    req.add_header("Authorization", f"Basic {creds}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def test_token(access_token):
    req = urllib.request.Request("https://api.pinterest.com/v5/user_account")
    req.add_header("Authorization", f"Bearer {access_token}")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def list_boards(access_token):
    req = urllib.request.Request("https://api.pinterest.com/v5/boards?page_size=100")
    req.add_header("Authorization", f"Bearer {access_token}")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


# ── Ana akış ─────────────────────────────────────────────────────────────────
def main():
    print("\n=== Pinterest OAuth Kurulumu ===\n")

    client_id     = get_env("PINTEREST_CLIENT_ID")
    client_secret = get_env("PINTEREST_CLIENT_SECRET")

    if not client_id:
        client_id = input("Pinterest Client ID: ").strip()
        save_env_key("PINTEREST_CLIENT_ID", client_id)
    if not client_secret:
        client_secret = input("Pinterest Client Secret: ").strip()
        save_env_key("PINTEREST_CLIENT_SECRET", client_secret)

    # Mevcut token varsa test et
    existing_token = get_env("PINTEREST_ACCESS_TOKEN")
    if existing_token:
        print(f"\n⚡ Mevcut token bulundu. Test ediliyor...")
        try:
            user = test_token(existing_token)
            print(f"  ✓ Bağlı hesap: {user.get('username','?')} ({user.get('account_type','?')})")
            boards = list_boards(existing_token)
            board_list = boards.get("items", [])
            print(f"  ✓ Board sayısı: {len(board_list)}")
            for b in board_list:
                print(f"    - {b['name']} (id: {b['id']})")
            print("\n✅ Token geçerli, yeniden auth gerekmez.")
            return
        except Exception as e:
            print(f"  ✗ Token geçersiz: {e} — yeniden auth yapılıyor...")

    # OAuth URL oluştur
    params = urllib.parse.urlencode({
        "client_id":     client_id,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         SCOPES,
    })
    auth_url = f"{AUTH_URL}?{params}"

    # Callback server başlat
    server = HTTPServer(("localhost", 8085), CallbackHandler)
    t = Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    print(f"\n🌐 Tarayıcı açılıyor... (Açılmazsa şu URL'yi kopyala):\n{auth_url}\n")
    webbrowser.open(auth_url)
    print("⏳ Pinterest yetkilendirmesi bekleniyor...")

    import time
    for _ in range(300):  # 5 dakika bekle
        if captured_code[0]:
            break
        time.sleep(1)

    server.shutdown()

    if not captured_code[0]:
        print("✗ Zaman aşımı — yetkilendirme yapılmadı.")
        sys.exit(1)

    print(f"\n✓ Kod alındı, token çekiliyor...")
    try:
        token_data = exchange_code(client_id, client_secret, captured_code[0])
        access_token = token_data.get("access_token")
        if not access_token:
            print(f"✗ Token alınamadı: {token_data}")
            sys.exit(1)

        save_env_key("PINTEREST_ACCESS_TOKEN", access_token)
        # Refresh token varsa kaydet
        refresh_token = token_data.get("refresh_token")
        if refresh_token:
            save_env_key("PINTEREST_REFRESH_TOKEN", refresh_token)

        # Test et
        user   = test_token(access_token)
        boards = list_boards(access_token)
        board_list = boards.get("items", [])

        print(f"\n🎉 Başarılı!")
        print(f"  Hesap: {user.get('username','?')} ({user.get('account_type','?')})")
        print(f"  Boardlar ({len(board_list)}):")
        for b in board_list:
            print(f"    - {b['name']} (id: {b['id']})")

    except Exception as e:
        print(f"✗ Hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
