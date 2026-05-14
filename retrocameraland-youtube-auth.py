#!/usr/bin/env python3
"""
Retrocameraland — YouTube OAuth Kurulum
İlk kez çalıştırılır, tarayıcıda Google hesabına izin verilir, token kaydedilir.

Kullanım:
    python3 retrocameraland-youtube-auth.py
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET   = os.path.join(SCRIPT_DIR, "yt_client_secret.json")
TOKEN_FILE      = os.path.join(SCRIPT_DIR, "yt_token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

def main():
    print("=== YouTube OAuth Kurulum ===\n")
    print("Tarayıcı açılacak — Google hesabınla giriş yap ve izin ver.\n")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)

    # Token'ı kaydet
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"\n✅ Token kaydedildi: {TOKEN_FILE}")

    # Test: kanal bilgilerini çek
    print("\n--- Kanal Bilgileri Test ---")
    yt = build("youtube", "v3", credentials=creds)
    resp = yt.channels().list(part="snippet,statistics", mine=True).execute()

    for ch in resp.get("items", []):
        sn   = ch["snippet"]
        st   = ch["statistics"]
        print(f"Kanal    : {sn['title']}")
        print(f"ID       : {ch['id']}")
        print(f"Abone    : {st.get('subscriberCount','?')}")
        print(f"Toplam İz: {st.get('viewCount','?')}")
        print(f"Video    : {st.get('videoCount','?')}")

    print("\n✅ Bağlantı başarılı! Artık saatlik fetch çalışacak.")

if __name__ == "__main__":
    main()
