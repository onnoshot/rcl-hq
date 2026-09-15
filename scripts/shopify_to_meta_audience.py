#!/usr/bin/env python3
"""
Retrocameraland — Shopify → Meta Value-Based Audience CSV
Tüm müşterileri Shopify'dan çeker, Meta Custom Audience formatında CSV üretir.

Kullanım:
    python3 scripts/shopify_to_meta_audience.py
Çıktı:
    outputs/meta_audience_YYYY-MM-DD.csv
"""

import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

SHOPIFY_TOKEN = "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"
SHOPIFY_STORE = "retrocameraland.myshopify.com"

SCRIPT_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"meta_audience_{datetime.now().strftime('%Y-%m-%d')}.csv")

HEADERS = [
    "email", "email", "email",
    "phone", "phone", "phone",
    "madid",
    "fn", "ln",
    "zip", "ct", "st", "country",
    "dob", "doby", "gen", "age",
    "uid",
    "value",
]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def shopify_get(path):
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/{path}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()), r.headers.get("Link", "")


def fetch_all_customers():
    """Tüm müşterileri sayfalayarak çek."""
    customers = []
    path = "customers.json?limit=250&fields=id,email,first_name,last_name,phone,default_address,total_spent"
    while path:
        log(f"  Çekiliyor: {path[:80]}...")
        data, link_header = shopify_get(path)
        batch = data.get("customers", [])
        customers.extend(batch)
        log(f"  {len(customers)} müşteri toplandı")
        # Sonraki sayfa var mı?
        path = None
        if 'rel="next"' in link_header:
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    url = part.strip().split(";")[0].strip().strip("<>")
                    path = url.replace(f"https://{SHOPIFY_STORE}/admin/api/2024-01/", "")
                    break
    return customers


def customer_to_row(c):
    addr = c.get("default_address") or {}
    email   = (c.get("email") or "").strip().lower()
    phone   = (c.get("phone") or addr.get("phone") or "").strip()
    fn      = (c.get("first_name") or "").strip()
    ln      = (c.get("last_name") or "").strip()
    zip_    = (addr.get("zip") or "").strip()
    city    = (addr.get("city") or "").strip()
    prov    = (addr.get("province_code") or addr.get("province") or "").strip()
    country = (addr.get("country_code") or "").strip()
    uid     = str(c.get("id", ""))
    value   = c.get("total_spent") or "0.00"

    return [
        email, "", "",      # email x3
        phone, "", "",      # phone x3
        "",                 # madid
        fn, ln,
        zip_, city, prov, country,
        "", "", "", "",     # dob, doby, gen, age
        uid,
        value,
    ]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log("=== Shopify → Meta Audience CSV ===")
    log("Müşteriler çekiliyor...")
    customers = fetch_all_customers()
    log(f"Toplam {len(customers)} müşteri bulundu")

    # Sadece en az e-posta veya telefonu olan müşterileri al
    valid = [c for c in customers if c.get("email") or c.get("phone")]
    log(f"{len(valid)} müşteri CSV'ye yazılacak (e-posta veya telefonu olanlar)")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for c in valid:
            writer.writerow(customer_to_row(c))

    log(f"Tamamlandı → {OUTPUT_FILE}")
    log("")
    log("Meta'ya yükleme adımları:")
    log("  1. Ads Manager → Audiences → Create Audience → Customer List")
    log("  2. 'Yes, include value column' seç")
    log("  3. CSV dosyasını yükle")
    log("  4. Sütun eşleştirmelerini doğrula ve 'Upload & Create' tıkla")


if __name__ == "__main__":
    main()
