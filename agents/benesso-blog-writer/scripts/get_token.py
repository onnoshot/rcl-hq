#!/usr/bin/env python3
"""
Shopify Partners App için tek seferlik OAuth token alma scripti.
Çalıştır → tarayıcı açılır → onayla → token ekrana yazdırılır.

Kullanım:
  python3 get_token.py <API_KEY> <API_SECRET>

API_KEY ve API_SECRET: Partners dashboard'dan aldığın değerler.
"""

import sys, threading, webbrowser, urllib.parse, requests
from http.server import HTTPServer, BaseHTTPRequestHandler

SHOP     = "benessocoffee.myshopify.com"
REDIRECT = "http://localhost:3000/callback"
SCOPES   = "write_content,read_content"

token_result = {"value": None}


class OAuthHandler(BaseHTTPRequestHandler):
    api_key    = None
    api_secret = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))

        code = params.get("code")
        if not code:
            self._respond(400, "❌ 'code' parametresi bulunamadı.")
            return

        # Code → Access Token
        r = requests.post(
            f"https://{SHOP}/admin/oauth/access_token",
            json={
                "client_id":     self.api_key,
                "client_secret": self.api_secret,
                "code":          code,
            },
            timeout=15,
        )

        if r.status_code == 200:
            token = r.json().get("access_token", "")
            token_result["value"] = token
            self._respond(200,
                f"✅ Token alındı! Terminale bak.\n\nBu sekmeyi kapatabilirsin.")
            print(f"\n{'='*60}")
            print(f"✅ SHOPIFY ACCESS TOKEN ALINDI:")
            print(f"\n  {token}\n")
            print(f"Bu token'ı publish_drafts.py'ye ver:")
            print(f"  python3 publish_drafts.py {token}")
            print(f"{'='*60}\n")
        else:
            self._respond(500, f"❌ Token alınamadı: {r.text}")
            print(f"HATA: {r.text}")

        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):
        pass  # sunucu loglarını gizle


def main():
    if len(sys.argv) < 3:
        print("Kullanım: python3 get_token.py <API_KEY> <API_SECRET>")
        print("\nPartners dashboard > Uygulamanı seç > API Kimlik Bilgileri bölümünden al.")
        sys.exit(1)

    api_key    = sys.argv[1]
    api_secret = sys.argv[2]

    OAuthHandler.api_key    = api_key
    OAuthHandler.api_secret = api_secret

    auth_url = (
        f"https://{SHOP}/admin/oauth/authorize"
        f"?client_id={api_key}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT)}"
    )

    print(f"\nYerel sunucu başlatılıyor → http://localhost:3000")
    print(f"Tarayıcı açılıyor...")

    server = HTTPServer(("localhost", 3000), OAuthHandler)
    threading.Thread(target=webbrowser.open, args=(auth_url,), daemon=True).start()

    print(f"Shopify'da 'Yükle' veya 'Onayla' butonuna bas...")
    print(f"(Manuel açmak istersen: {auth_url})\n")

    server.serve_forever()


if __name__ == "__main__":
    main()
