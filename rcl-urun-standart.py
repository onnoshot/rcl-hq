#!/usr/bin/env python3
"""
rcl-urun-standart.py
Stoktaki TUM urunleri tek standarda getirir.

SABIT SIRALAMA (27 urunde ayni):
  Giris -> Kutu Icerigi -> Kondisyon -> Video -> Teknik Ozellikler
        -> RetroCameraLand Yorumu -> Sik Sorulan Sorular -> Guvence -> Sosyal

Bunun disindaki bolumler cikarilir (link listesi, CTA, guven metni tekrari,
urun adini tekrarlayan basliklar, mikro pazarlama bolumleri).

DEGISMEYENLER: kutu icerigi maddeleri ve kondisyon metni/puani birebir tasinir.
Uygulamadan once ikisi de kaynakla karsilastirilir; farklilik varsa urun ATLANIR.

Kullanim:
  python3 rcl-urun-standart.py --dry-run
  python3 rcl-urun-standart.py --only "Samsung ST10"
  python3 rcl-urun-standart.py --apply
"""
import argparse, html as _html, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcl_urun_icerik as C
import rcl_urun_sablon as T
from retrocameraland_api import shopify

SCRATCH = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7227e27a-4e21-448e-ad28-4066a72ddada/scratchpad"
ACCESSORY = re.compile(r"kart okuyucu|aktarıcı|aktarici|tripod|şarj cihaz|sarj cihaz|batarya", re.I)
YORUM_RE = re.compile(r"yorum|değerlendirme|degerlendirme", re.I)


def pick_box(doc):
    """Kutu icerigi maddeleri. Metinler DEGISTIRILMEZ.

    Birden fazla aday olabilir (ornegin "Kozmetik Durum & Paket Icerigi" aslinda
    kondisyon metnidir); adaylar puanlanir: liste > sade baslik > madde sayisi."""
    def items_of(sec):
        for b in sec["blocks"]:
            if b["kind"] == "list":
                return b["items"], True
        items = []
        for b in sec["blocks"]:
            if b["kind"] != "p":
                continue
            txt = re.sub(r"^\s*(paket|kutu)\s*i[çc]eri[^:]*:\s*", "", C.strip_tags(b["html"]), flags=re.I)
            items += [x.strip(" -•·,") for x in re.split(r"\s{2,}|•|·|,\s(?=[A-ZÇĞİÖŞÜ])", txt)
                      if 3 < len(x.strip()) < 120]
        return items, False

    best = None
    for sec in doc["sections"]:
        t = C.tr_lower(sec["title"])
        if not re.search(r"kutu|paket|kutudan", t):
            continue
        items, is_list = items_of(sec)
        if not items:
            continue
        mixed = bool(re.search(r"kozmetik|durum|kondisyon", t))
        score = (2 if is_list else 0) + (0 if mixed else 2) + min(len(items), 8) / 10.0
        if best is None or score > best[0]:
            best = (score, sec, items)
    return (best[1], best[2]) if best else (None, [])


def pick_cond(doc, box_sec):
    """Kondisyon metni. Kaynaktaki cumleler AYNEN korunur.

    Bazi urunlerde kondisyon, kutu bolumunun ICINDE duruyor ("Paket / Kondisyon /
    Teslimat" gibi birlesik basliklar). Bu durumda o bolumun kondisyon satirlari
    ayrica toplanir; yoksa kondisyon sayfadan tamamen dusuyordu."""
    parts = []
    if box_sec:
        for b in box_sec["blocks"]:
            if b["kind"] == "p" and re.search(r"kondisyon", C.tr_lower(C.strip_tags(b["html"]))):
                parts.append(b["html"])
    for s in doc["sections"]:
        if s is box_sec:
            continue
        if s["kind"] == "cond" or re.search(r"kozmetik|durum|kondisyon", C.tr_lower(s["title"])):
            for b in s["blocks"]:
                if b["kind"] == "p":
                    parts.append(b["html"])
                elif b["kind"] == "list":
                    parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in b["items"]) + "</ul>")
    return parts


def pick_specs(doc):
    items = []
    for s in doc["sections"]:
        if s["kind"] == "spec":
            for b in s["blocks"]:
                if b["kind"] == "list":
                    items += b["items"]
    for b in doc["lead"]:
        if b["kind"] == "list":
            items += b["items"]
    return items


def pick_yorum(doc, title, extra):
    """Once kaynaktaki yorum; yoksa elle yazilmis olani kullan."""
    for s in doc["sections"]:
        if YORUM_RE.search(C.tr_lower(s["title"])):
            ps = [b["html"] for b in s["blocks"] if b["kind"] == "p"]
            if ps:
                return "".join(f"<p>{x}</p>" for x in ps)
    txt = extra.get(title)
    return f"<p>{txt}</p>" if txt else ""


def pick_faq(doc, is_cam, title, score, cond_text, box_items, specs):
    """Kaynakta dolu bir SSS varsa korunur; yoksa urunun KENDI verisinden uretilir."""
    for s in doc["sections"]:
        if s["kind"] == "faq":
            html = T.faq_from(s["blocks"], is_cam)
            if html and len(re.findall(r"<summary>", html)) >= 3:
                return html
    return T.build_faq(title, score, cond_text, box_items, specs, is_cam)


def build(product, doc, extra, video_id=None, ov=None):
    title = product["title"]
    is_cam = not ACCESSORY.search(title)
    out = [T.CSS, '<div class="rcl-p">']

    lead = [b["html"] for b in doc["lead"] if b["kind"] == "p"]
    if not lead:                       # giris yoksa ilk duz bolumun metnini kullan
        for s in doc["sections"]:
            if s["kind"] in ("other", "who"):
                ps = [b["html"] for b in s["blocks"] if b["kind"] == "p"]
                if ps:
                    lead = ps[:1]
                    break
    if lead:
        out.append(f'<p class="rcl-p-lead">{lead[0]}</p>')

    box_sec, box_items = pick_box(doc)
    box_items = box_items or (ov or {}).get("box", {}).get(title, [])
    if box_items:
        lis = "".join(f"<li>{i}</li>" for i in box_items)
        out.append(f'<div class="rcl-p-box"><h3>Kutu İçeriği</h3><ul>{lis}</ul></div>')

    score = C.cond_score(doc) or (ov or {}).get("score", {}).get(title)
    cond_parts = pick_cond(doc, box_sec) or \
        ([f'<p>{(ov or {}).get("cond", {})[title]}</p>'] if title in (ov or {}).get("cond", {}) else [])
    if score or cond_parts:
        out.append("<h2>Kondisyon</h2>")
        ring = T.cond_ring(score) if score else ""
        tested = f'<span class="rcl-p-tested">{T.TICK_SVG}RetroCameraLand ekibi tarafından test edildi</span>'
        body = tested + "".join(p if p.startswith("<ul") else f"<p>{p}</p>" for p in cond_parts)
        out.append(f'<div class="rcl-p-cond">{ring}<div class="rcl-p-cond__x">{body}</div></div>')

    if video_id:
        out.append(f'<div class="rcl-p-vid"><iframe src="https://www.youtube.com/embed/{video_id}" '
                   f'title="{_html.escape(title)} - Retro Camera Land" loading="lazy" '
                   f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                   f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')

    specs = pick_specs(doc) or (ov or {}).get("specs", {}).get(title, [])
    rows = T.spec_rows(specs, doc["tiles"])
    if rows:
        out.append("<h2>Teknik özellikler</h2>" + rows)

    yorum = pick_yorum(doc, title, extra)
    if yorum:
        out.append("<h2>RetroCameraLand yorumu</h2>" + yorum)

    cond_plain = C.strip_tags(" ".join(cond_parts))[:400]
    # tile yapisindaki ozellikler de SSS'e beslenir; yoksa ozel sablonlu
    # urunlerde (Y2K Aktarici gibi) sorular uretilemiyordu
    faq_specs = specs + [f"{t['k']}: {t['v']}" for t in doc["tiles"]]
    faq = pick_faq(doc, is_cam, title, score, cond_plain, box_items, faq_specs)
    out.append(T.GUVENCE)
    if faq:
        out.append("<h2>Sık sorulan sorular</h2>" + faq)
    out.append(T.SOCIAL)
    out.append("</div>")
    return "\n".join(x for x in out if x)


def guard(doc, new, score, box_items):
    """Kutu icerigi ve kondisyonun degismedigini dogrular."""
    errs = []
    got = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()
           for x in re.findall(r"<li>(.*?)</li>",
                               (re.search(r'rcl-p-box.*?</ul>', new, re.S) or re.match("", "")).group(0)
                               if re.search(r'rcl-p-box.*?</ul>', new, re.S) else "", re.S)]
    want = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip() for x in box_items]
    if want != got:
        errs.append(f"kutu icerigi degisti ({len(want)}->{len(got)})")
    if score:
        m = re.search(r'aria-label="Kondisyon ([\d.]+) / 10"', new)
        if not m or float(m.group(1)) != float(score):
            errs.append(f"kondisyon puani degisti ({score}->{m.group(1) if m else 'yok'})")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    src = json.load(open(f"{SCRATCH}/backup_before_apple.json"))
    extra = json.load(open(f"{SCRATCH}/yorumlar.json"))
    ov = json.load(open(f"{SCRATCH}/overrides.json"))
    matches = {m["pid"]: m for m in json.load(open(f"{SCRATCH}/video_matches.json"))}
    for p in src:
        if "Z700EXR" in p["title"].replace(" ", "") and p["id"] not in matches:
            s = next((m for m in matches.values() if "Z700 EXR" in m["product"]), None)
            if s: matches[p["id"]] = {**s, "pid": p["id"]}

    ok = skip = 0
    for p in src:
        if a.only and a.only.lower() not in p["title"].lower():
            continue
        doc = C.parse(p["body_html"])
        _, box_items = pick_box(doc)
        box_items = box_items or ov["box"].get(p["title"], [])
        score = C.cond_score(doc) or ov.get("score", {}).get(p["title"])
        new = build(p, doc, extra, matches.get(p["id"], {}).get("video_id"), ov)
        errs = guard(doc, new, score, box_items)
        if errs:
            print(f"  ✗ ATLANDI {p['title'][:34]:<36} {'; '.join(errs)}")
            skip += 1
            continue
        h2 = re.findall(r"<h2>(.*?)</h2>", new)
        print(f"  ✓ {p['title'][:34]:<36} kond:{str(score):<5} kutu:{len(box_items):<2} "
              f"spec:{len(pick_specs(doc) or ov['specs'].get(p['title'], [])) + len(doc['tiles']):<3} yorum:{'E' if 'RetroCameraLand yorumu' in new else '-'} "
              f"H2:{len(h2)}")
        ok += 1
        if a.apply:
            shopify("PUT", f"products/{p['id']}.json", {"product": {"id": p["id"], "body_html": new}})
            time.sleep(0.15)
        elif a.dry_run:
            open(f"{SCRATCH}/st_{p['id']}.html", "w", encoding="utf-8").write(new)
    print(f"\n{ok} hazir, {skip} atlandi")


if __name__ == "__main__":
    main()
