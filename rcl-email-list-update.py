#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL ABONE LISTESI GUNCELLEME
============================
Shopify "customers_export*.csv" -> temiz abone listesi -> rcl-email-list.json + Brevo master liste.

Kullanim:
  python3 rcl-email-list-update.py [CSV_YOLU]      # yol verilmezse ~/Downloads'taki EN YENI customers_export*.csv
  python3 rcl-email-list-update.py --dry           # yaz/Brevo'ya gonderme, sadece raporla

Ne yapar:
  1. CSV'yi okur, "Accepts Email Marketing = yes" olanlari suzer
  2. Temizler: kucuk harf, bosluk kirpma, .con->.com vb. yazim duzeltmesi, gecerlilik regex, tekillestirme
  3. Eski rcl-email-list.json'i arsivler, yenisini yazar
  4. Brevo'da "RCL-Tum-Aboneler" master listesine import eder (mevcutlar guncellenir, async tamamlanmasi beklenir)
  5. Delta raporlar (eklenen / cikan)
NOT: Brevo abonelikten-cikan/bounce kisileri otomatik bastirir (emailBlacklisted) -> onlara gonderim yapilmaz.
"""
import os, sys, csv, json, re, glob, time, urllib.request, urllib.error
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LIST_PATH = os.path.join(ROOT, "rcl-email-list.json")
ARCHIVE_DIR = os.path.join(ROOT, "outputs", "email-list-archive")
DOWNLOADS = os.path.expanduser("~/Downloads")
MASTER_LIST_NAME = "RCL-Tum-Aboneler"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
# yaygin alan-adi yazim hatalari -> dogru
TYPO_FIX = {
    ".con": ".com", ".vom": ".com", ".comm": ".com", ".cm": ".com", ".co m": ".com",
    "gmail.cm": "gmail.com", "gmail.co": "gmail.com", "gmial.com": "gmail.com",
    "gmai.com": "gmail.com", "gmail.con": "gmail.com", "hotmial.com": "hotmail.com",
    "hotmail.con": "hotmail.com", "yahoo.con": "yahoo.com", "outlook.con": "outlook.com",
    "icloud.con": "icloud.com",
}


def _env(key, d=""):
    try:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, d)

BREVO_KEY = _env("BREVO_API_KEY")


def brevo(method, path, body=None):
    req = urllib.request.Request("https://api.brevo.com/v3/" + path,
                                 data=json.dumps(body).encode() if body is not None else None, method=method)
    req.add_header("api-key", BREVO_KEY)
    req.add_header("content-type", "application/json")
    req.add_header("accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            t = r.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_msg": e.read().decode()[:200]}
    except Exception as e:
        return {"_error": 0, "_msg": str(e)[:200]}


def brevo_suppressed():
    """Brevo'da BASTIRILAN adresler kumesi: abonelikten cikan/blacklist (emailBlacklisted)
    + sert bounce/spam ile bloklananlar (blockedContacts). Bunlara bir daha gonderilmez,
    dolayisiyla listeden de cikarilirlar (deliverability'yi korur)."""
    if not BREVO_KEY:
        return set()
    supp = set()
    # 1) emailBlacklisted (abonelikten cikan / manuel kara liste)
    off = 0
    while True:
        d = brevo("GET", f"contacts?limit=500&offset={off}")
        cs = d.get("contacts") or []
        for c in cs:
            if c.get("emailBlacklisted") and c.get("email"):
                supp.add(c["email"].lower())
        if len(cs) < 500 or d.get("_error"):
            break
        off += 500
    # 2) blockedContacts (sert bounce / spam vb.)
    off = 0
    while True:
        d = brevo("GET", f"smtp/blockedContacts?limit=100&offset={off}")
        cs = d.get("contacts") or []
        for c in cs:
            if c.get("email"):
                supp.add(c["email"].lower())
        if len(cs) < 100 or d.get("_error"):
            break
        off += 100
    return supp


def clean_email(raw):
    """Temizle + yazim duzelt. Gecersizse None."""
    if not raw:
        return None
    e = raw.strip().lower().replace(" ", "")
    if e.count("@") != 1:
        return None
    for bad, good in TYPO_FIX.items():
        if e.endswith(bad):
            e = e[: -len(bad)] + good
            break
    return e if EMAIL_RE.match(e) else None


def find_csv(arg):
    if arg and os.path.exists(arg):
        return arg
    cands = sorted(glob.glob(os.path.join(DOWNLOADS, "customers_export*.csv")), key=os.path.getmtime, reverse=True)
    return cands[0] if cands else None


def parse_csv(path):
    """Pazarlama izinli + temiz + tekil e-postalar."""
    raw_emails, skipped = [], 0
    with open(path, encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh)
        cols = {c.strip().lower(): c for c in (r.fieldnames or [])}
        ecol = cols.get("email")
        mcol = next((cols[c] for c in cols if "accepts email marketing" in c or c == "email marketing"), None)
        if not ecol:
            raise SystemExit("HATA: CSV'de 'Email' kolonu yok")
        for row in r:
            consent = str(row.get(mcol, "")).strip().lower() if mcol else "yes"
            if consent not in ("yes", "subscribed", "true", "1"):
                continue
            e = clean_email(row.get(ecol, ""))
            if e:
                raw_emails.append(e)
            elif row.get(ecol, "").strip():
                skipped += 1
    # tekillestir, sirayi koru
    seen, out = set(), []
    for e in raw_emails:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out, skipped


def brevo_sync_master(emails, log=print):
    """Master listeye import (mevcutlar guncellenir), async tamamlanmasini bekler."""
    if not BREVO_KEY:
        log("  ! BREVO_API_KEY yok, Brevo atlandi")
        return None
    lists = brevo("GET", "contacts/lists?limit=50")
    lid = next((l["id"] for l in (lists.get("lists") or []) if l.get("name") == MASTER_LIST_NAME), None)
    if not lid:
        r = brevo("POST", "contacts/lists", {"name": MASTER_LIST_NAME, "folderId": 1})
        lid = r.get("id")
        log(f"  master liste olusturuldu: {MASTER_LIST_NAME} (id {lid})")
    if not lid:
        log("  ! master liste olusturulamadi")
        return None
    before = brevo("GET", f"contacts/lists/{lid}").get("totalSubscribers", 0) or 0
    r = brevo("POST", "contacts/import", {"listIds": [lid], "updateExistingContacts": True,
                                          "jsonBody": [{"email": e} for e in emails]})
    if r.get("_error"):
        log(f"  ! Brevo import hatasi: {r.get('_msg')}")
        return lid
    for _ in range(40):
        time.sleep(2)
        now = brevo("GET", f"contacts/lists/{lid}").get("totalSubscribers", 0) or 0
        if now >= min(before + 1, len(emails)) and now >= before:
            if now >= len(emails) * 0.95 or now > before:
                break
    final = brevo("GET", f"contacts/lists/{lid}").get("totalSubscribers", 0)
    log(f"  Brevo master liste: {final} abone (önce {before})")
    return lid


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    csv_path = find_csv(args[0] if args else None)
    if not csv_path:
        raise SystemExit("HATA: CSV bulunamadi. Yol ver veya ~/Downloads'a customers_export*.csv koy.")
    print(f"Kaynak CSV: {csv_path}")

    emails, skipped = parse_csv(csv_path)
    print(f"Pazarlama izinli + temiz + tekil: {len(emails)} abone  (gecersiz atlanan: {skipped})")

    # ── BASTIRILAN ADRESLERI CIKAR (otomatik liste temizligi) ─────────────────
    supp = brevo_suppressed()
    if supp:
        before_n = len(emails)
        emails = [e for e in emails if e not in supp]
        cleaned = before_n - len(emails)
        print(f"Brevo bastirilan (bounce/abonelikten cikan): {len(supp)} adres -> listeden {cleaned} cikarildi")

    # delta
    old = []
    if os.path.exists(LIST_PATH):
        try:
            old = json.load(open(LIST_PATH))
        except Exception:
            old = []
    olds, news = set(e.lower() for e in old), set(emails)
    added = sorted(news - olds)
    removed = sorted(olds - news)
    print(f"Onceki liste: {len(old)}  ->  Yeni: {len(emails)}   (+{len(added)} eklenen / -{len(removed)} cikan)")
    if added[:8]:
        print("  eklenen ornek:", ", ".join(added[:8]))
    if removed[:8]:
        print("  cikan ornek:  ", ", ".join(removed[:8]))

    if dry:
        print("\n--dry: hicbir sey yazilmadi / Brevo'ya gonderilmedi.")
        return

    # arsivle + yaz
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    if old:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(ARCHIVE_DIR, f"rcl-email-list-{ts}.json"), "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False, indent=2)
    with open(LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(emails, f, ensure_ascii=False, indent=2)
    print(f"✓ rcl-email-list.json guncellendi ({len(emails)} abone), eski surum arsivlendi")

    # Brevo
    print("Brevo master listeye import ediliyor...")
    brevo_sync_master(emails)
    print("✓ Tamamlandi.")


if __name__ == "__main__":
    main()
