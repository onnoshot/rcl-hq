#!/usr/bin/env python3
"""
Benesso — "Kahve Künyesi" → coffee.* metafield doldurucu.

Ürünlerin body_html'indeki künye bloğunu (Ülke, Bölge, Yöre, Rakım, Varyete,
İşleme Yöntemi, Tadım Notları, Üretici, Kavurma) parse edip Shopify
metafield'larına yazar. Spec Lab teması bu metafield'ları okuyarak künye/coffee-spec,
tat notu chip'leri ve köken haritasını render eder.

Idempotent: var olan metafield'ı günceller, yoksa oluşturur. Aynı değerse atlar.

Kullanım:
  export SHOPIFY_TOKEN=shpat_xxx
  export SHOPIFY_STORE=benessocoffee.myshopify.com   # opsiyonel, varsayılan bu
  python3 populate_coffee_metafields.py --dry-run      # sadece göster
  python3 populate_coffee_metafields.py                # uygula
  python3 populate_coffee_metafields.py --handle kenya-kathakwa-washed-yoresel-filtre-kahve
"""
import os, re, sys, json, time, html, argparse, urllib.request, urllib.error

STORE = os.environ.get("SHOPIFY_STORE", "benessocoffee.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_TOKEN", "")
API = "2024-10"
NS = "coffee"

# Künye etiketi -> (metafield key, type)
LABELS = {
    "ülke": "country", "ulke": "country", "country": "country",
    "bölge": "region", "bolge": "region", "region": "region",
    "yöre": "locality", "yore": "locality", "istasyon": "locality",
    "rakım": "altitude", "rakim": "altitude", "altitude": "altitude",
    "varyete": "varietal", "varyetel": "varietal", "variety": "varietal", "tür": "varietal",
    "işleme yöntemi": "process", "isleme yontemi": "process", "işleme": "process", "isleme": "process", "process": "process",
    "tadım notları": "tasting_notes", "tadim notlari": "tasting_notes", "tat notları": "tasting_notes", "notlar": "tasting_notes",
    "üretici": "producer", "uretici": "producer", "çiftlik": "producer", "ciftlik": "producer", "producer": "producer",
    "kavurma": "roast", "kavrum": "roast", "roast": "roast",
}

# Köken -> (lat, lng) — origin map / PDF pin için
COUNTRY_COORDS = {
    "ethiopia": (8.6, 39.9), "etiyopya": (8.6, 39.9), "kenya": (-0.5, 37.9),
    "rwanda": (-2.0, 29.9), "ruanda": (-2.0, 29.9), "yemen": (15.5, 47.6),
    "colombia": (4.6, -74.1), "kolombiya": (4.6, -74.1), "costa rica": (9.9, -84.1),
    "kosta rika": (9.9, -84.1), "brazil": (-14.2, -51.9), "brezilya": (-14.2, -51.9),
    "indonesia": (-2.5, 118.0), "endonezya": (-2.5, 118.0), "guatemala": (15.5, -90.2),
    "el salvador": (13.8, -88.9), "mexico": (23.6, -102.5), "meksika": (23.6, -102.5),
    "madagascar": (-18.8, 46.8), "madagaskar": (-18.8, 46.8), "panama": (8.5, -80.8),
    "honduras": (15.2, -86.2), "peru": (-9.2, -75.0), "türkiye": (39.0, 35.0), "turkey": (39.0, 35.0),
}


def req(method, path, body=None):
    url = "https://%s/admin/api/%s/%s" % (STORE, API, path)
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("X-Shopify-Access-Token", TOKEN)
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode()), resp.headers
    except urllib.error.HTTPError as e:
        print("  ! HTTP %s: %s" % (e.code, e.read().decode()[:200]))
        return None, {}


def all_products(handle=None):
    out, path = [], "products.json?limit=250&fields=id,title,handle,body_html,product_type"
    while path:
        data, headers = req("GET", path)
        if not data:
            break
        for p in data.get("products", []):
            if handle and p["handle"] != handle:
                continue
            out.append(p)
        link = headers.get("Link", "")
        m = re.search(r'<[^>]*[?&]page_info=([^>&]+)[^>]*>;\s*rel="next"', link)
        path = ("products.json?limit=250&page_info=%s" % m.group(1)) if m else None
        time.sleep(0.3)
    return out


def parse_kunye(body_html):
    if not body_html:
        return {}
    text = re.sub(r"<\s*br\s*/?>", "\n", body_html, flags=re.I)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    fields = {}
    for line in text.split("\n"):
        if ":" not in line:
            continue
        label, _, value = line.partition(":")
        # Türkçe "İ".lower() bileşik noktalı i (̇) üretir; temizle
        norm = label.strip().lower().replace("̇", "").replace("i̇", "i")
        key = LABELS.get(norm)
        value = value.strip()
        if key and value and key not in fields:
            fields[key] = value
    # köken koordinatları
    if "country" in fields:
        coords = COUNTRY_COORDS.get(fields["country"].strip().lower())
        if coords:
            fields["lat"], fields["lng"] = str(coords[0]), str(coords[1])
    return fields


def existing_metafields(pid):
    data, _ = req("GET", "products/%s/metafields.json?namespace=%s" % (pid, NS))
    out = {}
    if data:
        for m in data.get("metafields", []):
            out[m["key"]] = m
    return out


def upsert(pid, key, value, existing, dry):
    mtype = "number_decimal" if key in ("lat", "lng") else "single_line_text_field"
    cur = existing.get(key)
    if cur and str(cur.get("value")) == str(value):
        return "skip"
    if dry:
        return "would-set"
    if cur:
        req("PUT", "metafields/%s.json" % cur["id"], {"metafield": {"id": cur["id"], "value": value, "type": mtype}})
        return "update"
    req("POST", "products/%s/metafields.json" % pid,
        {"metafield": {"namespace": NS, "key": key, "value": value, "type": mtype}})
    return "create"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--handle", help="Sadece bu handle")
    args = ap.parse_args()
    if not TOKEN:
        sys.exit("HATA: SHOPIFY_TOKEN ortam değişkeni gerekli.")

    products = all_products(args.handle)
    print("%d ürün taranıyor (%s)%s\n" % (len(products), STORE, "  [DRY-RUN]" if args.dry_run else ""))
    total = {"create": 0, "update": 0, "skip": 0, "would-set": 0}
    for p in products:
        fields = parse_kunye(p.get("body_html"))
        if not fields:
            continue
        existing = {} if args.dry_run else existing_metafields(p["id"])
        actions = []
        for key, value in fields.items():
            res = upsert(p["id"], key, value, existing, args.dry_run)
            total[res] = total.get(res, 0) + 1
            if res != "skip":
                actions.append("%s=%s" % (key, value[:24]))
        if actions:
            print("• %s" % p["title"])
            print("    " + " | ".join(actions))
        if not args.dry_run:
            time.sleep(0.4)
    print("\nÖzet:", json.dumps(total, ensure_ascii=False))
    if args.dry_run:
        print("Uygulamak için --dry-run olmadan tekrar çalıştır.")


if __name__ == "__main__":
    main()
