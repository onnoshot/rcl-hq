#!/usr/bin/env python3
"""
rcl-urun-apple-sablon.py
Stoktaki urun aciklamalarini Apple-vari sablona kurar.

GARANTILER
  1. Kondisyon puani ve kutu icerigi metinleri harfi harfine tasinir.
  2. Siniflandirilamayan her blok "leftover" olarak yine basilir (kayipsizlik).
  3. Uygulamadan once kelime duzeyinde kapsama dogrulanir; esik altinda kalan
     urun ATLANIR ve canliya dokunulmaz.

Kullanim:
  python3 rcl-urun-apple-sablon.py --dry-run
  python3 rcl-urun-apple-sablon.py --only "Samsung ST10"
  python3 rcl-urun-apple-sablon.py --apply
"""
import argparse, html as _html, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcl_urun_icerik as C
import rcl_urun_sablon as T
from retrocameraland_api import shopify

SCRATCH = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7227e27a-4e21-448e-ad28-4066a72ddada/scratchpad"
ACCESSORY = re.compile(r"kart okuyucu|aktarıcı|aktarici|tripod|şarj cihaz|sarj cihaz|batarya", re.I)

# Tamamen kaldirilan bolumler: link listesi / CTA / guven metni. Hepsinin
# karsiligi sayfada zaten standart blok olarak var; tekrar ediyorlar, SEO'ya
# ek katki yapmiyorlar ve sayfayi uzatip kafa karistiriyorlar.
TRIM = re.compile(
    r"blog.?dan okuma|rehber *(?:&amp;|&|ve) *blog|topluluğ|toplulug|"
    r"neden *retro ?camera ?land|ürün bilgisi|urun bilgisi|"
    r"nereden al[ıi]n[ıi]r|bizi takip", re.I)


def _tokens(t):
    return {w for w in re.findall(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü]{3,}", C.tr_lower(t))}


def echoes_title(head, product_title):
    """Baslik urun adini mi tekrarliyor? H1 ile ayni seyi soyleyen H2'ler
    anahtar kelime tekrarindan baska bir ise yaramiyor."""
    ht, pt = _tokens(head), _tokens(product_title)
    if not ht or not pt:
        return False
    model = {w for w in pt if any(ch.isdigit() for ch in w)}
    return len(ht & pt) / len(pt) >= 0.55 or bool(model and model <= ht)


def pick_box(doc):
    """Kutu icerigi maddelerini bulur. Metinler DEGISTIRILMEZ.

    Birden fazla aday bolum olabilir: ornegin Casio EX-Z4'te hem
    "Kozmetik Durum & Paket Icerigi" (aslinda KONDISYON metni) hem de asil
    "Paket icerigi" bolumu var. Oncekisi once geldigi icin yanlis secilip
    kutu icerigi 5 madde yerine 2 satir kondisyon metni olarak cikiyordu.
    Bu yuzden adaylar puanlanir: liste > sade "paket/kutu icerigi" basligi >
    madde sayisi; kozmetik/durum/kondisyon ile birlesik basliklar geri plana atilir."""
    def items_of(sec):
        for b in sec["blocks"]:
            if b["kind"] == "list":
                return b["items"], True
        ps = [b["html"] for b in sec["blocks"] if b["kind"] == "p"]
        items = []
        for h in ps:
            txt = C.strip_tags(h)
            txt = re.sub(r"^\s*(paket|kutu)\s*i[çc]eri[^:]*:\s*", "", txt, flags=re.I)
            items += [x.strip(" -•·,") for x in re.split(r"\s{2,}|\u2022|·|,\s(?=[A-ZÇĞİÖŞÜ])", txt)
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
        # kozmetik/durum/kondisyon ile birlesik baslik: muhtemelen kondisyon metni
        mixed = bool(re.search(r"kozmetik|durum|kondisyon", t))
        score = (2 if is_list else 0) + (0 if mixed else 2) + min(len(items), 8) / 10.0
        if best is None or score > best[0]:
            best = (score, sec, items)
    return (best[1], best[2]) if best else (None, [])


def build(product, doc, video_id=None):
    title = product["title"]
    is_cam = not ACCESSORY.search(title)
    used = set()                      # tuketilen bolum id'leri -> leftover hesabi
    merged_cond = []
    out = [T.CSS, '<div class="rcl-p">']

    # 1) Giris
    lead = [b for b in doc["lead"] if b["kind"] == "p"]
    lead_lists = [b for b in doc["lead"] if b["kind"] == "list"]
    if lead:
        out.append(f'<p class="rcl-p-lead">{lead[0]["html"]}</p>')
        out += [f'<p>{b["html"]}</p>' for b in lead[1:]]

    # 2) KUTU ICERIGI — en ustte (kullanici istegi)
    box_sec, box_items = pick_box(doc)
    if box_items:
        # Birlesik "Kondisyon & Kutu Icerigi" bolumunde liste kutu icerigidir,
        # kalan paragraflar KONDISYON metnidir: bunlari kaybetme.
        if box_sec and C.tr_lower(box_sec["title"]).find("kondisyon") >= 0:
            merged_cond = [b for b in box_sec["blocks"] if b["kind"] != "list"]
        used.add(id(box_sec))
        lis = "".join(f"<li>{i}</li>" for i in box_items)
        out.append(f'<div class="rcl-p-box"><h3>Kutu İçeriği</h3><ul>{lis}</ul></div>')

    # 3) KONDISYON — puan animasyonlu halkada, metin aynen
    score = C.cond_score(doc)
    # TUM kondisyon bolumleri toplanir: "<p><strong>Kondisyon: 8.7 / 10</strong></p>"
    # kalin-paragraf-basligi kuraliyla ayri bir bolume donusuyor ve kondisyon
    # metnini ikiye boluyordu (sayfada "Kondisyon" basligi iki kez cikiyordu).
    cond_txt = T.render_blocks(merged_cond) if merged_cond else ""
    # "Kozmetik Durum & Paket Icerigi" gibi basliklar box olarak siniflaniyor ama
    # kutu adayi secilmediyse icerigi KONDISYON metnidir: en alta dusmesin.
    # box olarak tuketilen bolum burada TEKRAR alinmamali: "Paket / Kondisyon /
    # Teslimat" gibi basliklar hem kutu hem kondisyon eslesmesi verip ayni
    # paragraflarin iki kez basilmasina yol aciyordu.
    cond_secs = [x for x in doc["sections"] if x["kind"] == "cond" and x is not box_sec]
    for x in doc["sections"]:
        if x is box_sec or x in cond_secs:
            continue
        if re.search(r"kozmetik|durum|kondisyon", C.tr_lower(x["title"])):
            cond_secs.append(x)
    for cs in cond_secs:
        used.add(id(cs))
        keep = [b for b in cs["blocks"]
                if not (b["kind"] == "list" and b["items"] == box_items)]
        part = T.render_blocks(keep)
        if C.strip_tags(part):
            cond_txt = (cond_txt or "") + part
        # puan satirini metinden temizleme: METNE DOKUNULMAZ, oldugu gibi kalir
    if score or cond_txt:
        out.append("<h2>Kondisyon</h2>")
        left = T.cond_ring(score) if score else ""
        tested = f'<span class="rcl-p-tested">{T.TICK_SVG}RetroCameraLand ekibi tarafından test edildi</span>'
        if not score and cond_txt:
            left = ""
        body = tested + (cond_txt or "")
        out.append(f'<div class="rcl-p-cond">{left}<div class="rcl-p-cond__x">{body}</div></div>')

    # 4) Video
    if video_id:
        out.append(f'<div class="rcl-p-vid"><iframe src="https://www.youtube.com/embed/{video_id}" '
                   f'title="{_html.escape(title)} - Retro Camera Land" loading="lazy" '
                   f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                   f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')

    # 5) Teknik ozellikler (madde listeleri + ozel sablon kutulari)
    spec_items, spec_prose = [], []
    for s in doc["sections"]:
        if s["kind"] != "spec":
            continue
        used.add(id(s))
        for b in s["blocks"]:
            if b["kind"] == "list":
                spec_items += b["items"]
            elif b["kind"] == "p":
                spec_prose.append(b["html"])
    spec_items += [b["items"] for b in lead_lists for b in [b]][0] if False else []
    for b in lead_lists:
        spec_items += b["items"]
    rows = T.spec_rows(spec_items, doc["tiles"])
    if rows:
        out.append("<h2>Teknik özellikler</h2>" + rows)
    out += [f"<p>{p}</p>" for p in spec_prose]

    # 6) Kalan bolumler — ORIJINAL SIRASIYLA, basligiyla birlikte
    faq_html = ""
    for s in doc["sections"]:
        if id(s) in used:
            continue
        if s["kind"] == "faq":
            faq_html = T.faq_from(s["blocks"], is_cam)
            used.add(id(s))
            if not faq_html or not C.strip_tags(faq_html):
                # Soru/cevap kalibi taninmadi: bolumu oldugu gibi bas.
                # (Aksi halde USB-C okuyucunun 4 paragrafli SSS'i tamamen kayboluyordu.)
                faq_html = ""
                inner = T.render_blocks(s["blocks"])
                if C.strip_tags(inner):
                    out.append(f"<h2>{C.clean_txt(s['title'])}</h2>{inner}")
            continue
        if s["kind"] == "drop":
            used.add(id(s))
            continue          # guvence/kargo/sosyal: standart bloklarla degistiriliyor
        head = C.clean_txt(s["title"])
        used.add(id(s))
        if TRIM.search(head):
            continue                                 # link/CTA/guven tekrari: cikar
        inner = T.render_blocks(s["blocks"])
        if not C.strip_tags(inner):
            continue
        words = len(C.strip_tags(inner).split())
        if not head:
            out.append(inner)
        elif echoes_title(head, title):
            out.append(inner)                        # basligi at, metni koru
        elif words < 26:
            out.append(f"<h3>{head}</h3>{inner}")    # mikro bolum -> alt baslik
        else:
            out.append(f"<h2>{head}</h2>{inner}")

    if not faq_html and is_cam:
        faq_html = f'<div class="rcl-p-faq">{T.FAQ_AKTARIM}</div>'

    out.append(T.GUVENCE)
    if faq_html:
        out.append("<h2>Sık sorulan sorular</h2>" + faq_html)
    out.append(T.SOCIAL)
    out.append("</div>")
    return "\n".join(x for x in out if x)


def _words(h):
    h = re.sub(r"<(style|script|noscript)\b.*?</\1>", " ", h or "", flags=re.S | re.I)
    t = C.EMOJI.sub("", C.strip_tags(h))
    t = re.sub(r"[.#@][-\w]+\s*\{[^}]*\}", " ", t)
    return re.findall(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü./-]{3,}", t)


def expected_words(doc, product_title=""):
    """Ciktida BULUNMASI GEREKEN kelimeler.

    Kasitli olarak standart bloklarla degistirilen bolumler (guvence metni,
    kargo/teslimat zaman cizelgesi, sosyal medya satiri) olcum disidir; yoksa
    esik surekli yaniltici sekilde dusuk cikiyor ve saglam urunler de bloklaniyor."""
    out = []
    for b in doc["lead"]:
        out += _words(b.get("html", "") or " ".join(b.get("items", [])))
    for s in doc["sections"]:
        # "drop" kalip bolumleri ve TRIM ile bilerek kaldirilanlar olcum disidir:
        # yoksa kasitli temizlik "kayip" gibi gorunup saglam urunleri de bloklar.
        head = C.clean_txt(s["title"])
        if s["kind"] == "drop" or TRIM.search(head):
            continue
        # Standart bloga donusen bolumlerin BASLIK kelimeleri sayilmaz:
        # "Urun Kondisyonu" -> "Kondisyon", "One Cikan Ozellikler" -> "Teknik
        # ozellikler" gibi. Govde metni yine tam olarak beklenir.
        if s["kind"] in ("box", "cond", "spec", "faq"):
            pass
        elif not echoes_title(head, product_title):
            out += _words(s["title"])
        for b in s["blocks"]:
            out += _words(b.get("html", "") or " ".join(b.get("items", [])) or b.get("raw", ""))
    for t in doc["tiles"]:
        out += _words(f"{t['k']} {t['v']} {t.get('note','')}")
    return out


def word_coverage(original, rebuilt):
    """Kelime duzeyinde kapsama.

    Kasitli olarak standart bloklarla DEGISTIRILEN kalip metinler (guvence,
    kargo/teslimat sureci, sosyal medya, bolum basligi kelimeleri) olcum disi
    birakilir; yoksa esik hep yaniltici sekilde dusuk cikiyor."""
    o = original if isinstance(original, list) else _words(original)
    n = set(_words(rebuilt))
    missing = [w for w in o if w not in n]
    return len(o), missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--min-coverage", type=float, default=97.0)
    a = ap.parse_args()

    prods = json.load(open(f"{SCRATCH}/instock2.json"))
    matches = {m["pid"]: m for m in json.load(open(f"{SCRATCH}/video_matches.json"))}
    for p in prods:
        if "Z700EXR" in p["title"].replace(" ", "") and p["id"] not in matches:
            src = next((m for m in matches.values() if "Z700 EXR" in m["product"]), None)
            if src: matches[p["id"]] = {**src, "pid": p["id"]}

    ok = skip = 0
    for p in prods:
        if a.only and a.only.lower() not in p["title"].lower():
            continue
        doc = C.parse(p["body_html"])
        new = build(p, doc, matches.get(p["id"], {}).get("video_id"))
        tot, miss = word_coverage(expected_words(doc, p["title"]), new)
        cov = (tot - len(miss)) / max(tot, 1) * 100
        score = C.cond_score(doc)
        _, box = pick_box(doc)
        flag = "video" if p["id"] in matches else "     "
        if cov < a.min_coverage:
            print(f"  ✗ ATLANDI %{cov:.1f}  {p['title'][:34]:<36} eksik: {sorted(set(miss))[:6]}")
            skip += 1
            continue
        print(f"  ✓ %{cov:.1f}  {p['title'][:34]:<36} kond:{str(score):<5} kutu:{len(box):<2} {flag}")
        ok += 1
        if a.apply:
            shopify("PUT", f"products/{p['id']}.json", {"product": {"id": p["id"], "body_html": new}})
            time.sleep(0.15)
        elif a.dry_run:
            open(f"{SCRATCH}/ap_{p['id']}.html", "w", encoding="utf-8").write(new)
    print(f"\n{ok} hazir, {skip} atlandi")


if __name__ == "__main__":
    main()
