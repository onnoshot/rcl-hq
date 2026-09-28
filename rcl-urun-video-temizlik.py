#!/usr/bin/env python3
"""
rcl-urun-video-temizlik.py
Stoktaki urun aciklamalarina MINIMAL mudahale:
  1) Eslesen YouTube videosunu gomer (giris paragrafinin hemen altina)
  2) Bos <p>, &nbsp;, fazla <br> gibi markup artiklarini temizler
  3) Instagram adresini instagram.com/retrocameraland bicimine getirir

ONEMLI: Icerik YENIDEN YAPILANDIRILMAZ. Kondisyon ve kutu icerigi dahil
hicbir metne dokunulmaz. Guvenlik icin, uygulamadan once gorunur metnin
degismedigi dogrulanir; degismisse o urun ATLANIR.

Kullanim:
  python3 rcl-urun-video-temizlik.py --dry-run
  python3 rcl-urun-video-temizlik.py --apply
"""
import argparse, html, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrocameraland_api import shopify

SCRATCH = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7227e27a-4e21-448e-ad28-4066a72ddada/scratchpad"

IG_OLD = re.compile(r"https?://(?:www\.)?instagram\.com/retrocameraland/?", re.I)
IG_NEW = "https://instagram.com/retrocameraland"

VIDEO_CSS_ID = "rcl-vid-style"
VIDEO_CSS = ('<style id="rcl-vid-style">.rcl-vid{position:relative;width:100%;aspect-ratio:16/9;'
             'border-radius:14px;overflow:hidden;background:rgba(128,128,128,.18);margin:24px 0;}'
             '.rcl-vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}</style>')


def video_block(vid, title):
    return (VIDEO_CSS + f'<div class="rcl-vid"><iframe src="https://www.youtube.com/embed/{vid}" '
            f'title="{html.escape(title)} - Retro Camera Land" loading="lazy" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')


def tidy(b):
    """Sadece bos markup artiklarini siler. Metin iceren hicbir dugume dokunmaz."""
    b = re.sub(r"<meta[^>]*>", "", b, flags=re.I)                      # aciklamaya sizmis <meta>
    b = re.sub(r"<p[^>]*>\s*(?:&nbsp;| |<br\s*/?>)*\s*</p>", "", b, flags=re.I)
    b = re.sub(r"<h([1-6])[^>]*>\s*(?:&nbsp;| |<br\s*/?>)*\s*</h\1>", "", b, flags=re.I)
    b = re.sub(r"<div[^>]*>\s*</div>", "", b, flags=re.I)
    b = re.sub(r"(?:<br\s*/?>\s*){2,}", "<br>", b, flags=re.I)         # ardisik <br> -> tek
    b = re.sub(r"\s*<br\s*/?>\s*(</(?:p|h[1-6]|li|td)>)", r"\1", b, flags=re.I)  # sondaki <br>
    b = re.sub(r"\n{3,}", "\n\n", b)
    return b.strip()


def insert_video(b, block):
    """Giris paragrafinin hemen altina yerlestirir; yoksa en basa."""
    if "youtube.com/embed" in b:
        return b
    m = re.search(r"</p>", b, re.I)
    if m:
        return b[:m.end()] + "\n" + block + "\n" + b[m.end():]
    return block + "\n" + b


def visible_text(h):
    """Karsilastirma icin gorunur metin (etiketler, stil ve iframe haric)."""
    h = re.sub(r"<(style|script|iframe|svg)\b.*?</\1>", " ", h or "", flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", h).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    matches = {m["pid"]: m for m in json.load(open(f"{SCRATCH}/video_matches.json"))}
    prods = shopify("GET", "products.json?limit=250&status=active"
                           "&fields=id,title,handle,body_html,variants")["products"]
    instock = [p for p in prods if any((v.get("inventory_quantity") or 0) > 0 for v in p["variants"])]
    # Z700EXR kopyasi ayni kamera -> ayni video
    for p in instock:
        if "Z700EXR" in p["title"].replace(" ", "") and p["id"] not in matches:
            src = next((m for m in matches.values() if "Z700 EXR" in m["product"]), None)
            if src: matches[p["id"]] = {**src, "pid": p["id"]}

    changed = skipped = 0
    for p in instock:
        orig = p["body_html"] or ""
        new = tidy(orig)
        new = IG_OLD.sub(IG_NEW, new)
        m = matches.get(p["id"])
        if m:
            new = insert_video(new, video_block(m["video_id"], p["title"]))

        # GUVENLIK KONTROLU: gorunur metin birebir ayni kalmali
        if visible_text(orig) != visible_text(new):
            print(f"  ✗ ATLANDI (metin degisirdi): {p['title'][:44]}")
            skipped += 1
            continue
        if new == orig:
            continue

        diffs = []
        if IG_OLD.search(orig): diffs.append("instagram")
        if len(new) != len(tidy(orig)) or tidy(orig) != orig: diffs.append("bosluk")
        if m: diffs.append(f"video:{m['video_id']}")
        print(f"  ✓ {p['title'][:40]:<42} {', '.join(diffs)}")
        changed += 1
        if a.apply:
            shopify("PUT", f"products/{p['id']}.json",
                    {"product": {"id": p["id"], "body_html": new}})
            time.sleep(0.15)
        elif a.dry_run:
            open(f"{SCRATCH}/vid_preview_{p['id']}.html", "w", encoding="utf-8").write(new)

    print(f"\n{changed} urun guncellendi, {skipped} atlandi")


if __name__ == "__main__":
    main()
