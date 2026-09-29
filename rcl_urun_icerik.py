#!/usr/bin/env python3
"""
rcl_urun_icerik.py — urun aciklamasi ayristirici + yeniden insa edici.

TASARIM ILKESI: kayipsizlik. Ayristirici her metin dugumunu bir kovaya koyar;
siniflandiramadigi dugumler "leftover" kovasina gider ve ciktida yine basilir.
Boylece "tanimadigim seyi sessizce at" hatasi yapisal olarak imkansiz hale gelir.
(Onceki surum sadece tanidigi bolumleri aliyor ve iceriğin ~%40'ini dusuruyordu.)

Akis:
  1) style/script/svg temizle
  2) tileK/tileV/tileP spec kutularini cikar (ozel sablonlu urunler)
  3) kalin-paragraf basliklari (<p><strong>X</strong></p>) gercek basliga cevir
  4) div/section/header/article sarmalayicilarini AC (unwrap) -> duz dizi
  5) h1-6 / p / ul / ol / table dizisini bolumlere ayir
  6) sablonu kur, artiklari ekle
  7) kapsama dogrula: orijinaldeki her cumle ciktida var mi?
"""
import html as _html
import re

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿️←-⇿⬀-⯿]")
INLINE_OK = r"strong|b|em|i|a|br|code|sup|sub|small|u"


def tr_lower(s):
    """Turkce guvenli kucultme: Python'da 'İ'.lower() -> 'i'+U+0307 verir."""
    return s.replace("İ", "i").replace("I", "ı").lower().replace("̇", "")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def clean_txt(s):
    return re.sub(r"\s+", " ", EMOJI.sub("", s or "")).strip(" ·-–—:• ")


def sentences(h):
    """Karsilastirma icin cumleler. <style>/<script> icerigi ICERIK DEGILDIR:
    CSS kodunu cumle sayarsak kapsama olcumu yaniltici cikiyor."""
    h = re.sub(r"<(style|script|noscript)\b.*?</\1>", " ", h or "", flags=re.S | re.I)
    t = EMOJI.sub("", strip_tags(h))
    t = re.sub(r"[.#@][-\w]+\s*\{[^}]*\}", " ", t)      # kacak CSS kurallari
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", t) if len(x.strip()) > 40]


def tile_pairs(h):
    """Ozel sablondaki etiket/deger/not uclulerini okur."""
    pat = (r'<div[^>]*class="[^"]*tileK[^"]*"[^>]*>(.*?)</div>\s*'
           r'<div[^>]*class="[^"]*tileV[^"]*"[^>]*>(.*?)</div>'
           r'(?:\s*<div[^>]*class="[^"]*tileP[^"]*"[^>]*>(.*?)</div>)?')
    out = []
    for k, v, n in re.findall(pat, h, re.S | re.I):
        k, v, n = clean_txt(strip_tags(k)), clean_txt(strip_tags(v)), clean_txt(strip_tags(n or ""))
        if k and v:
            out.append({"k": k, "v": v, "note": n})
    return out


def flatten(h):
    """Sarmalayicilari acip duz blok dizisi birakir."""
    h = re.sub(r"<(style|script|svg|noscript)\b.*?</\1>", " ", h or "", flags=re.S | re.I)
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    h = re.sub(r"<meta[^>]*>|<link[^>]*>", " ", h, flags=re.I)
    # <details><summary>Soru</summary>Cevap</details> -> SSS paragraf formatina
    # (T9 gibi onceden donusturulmus urunlerde sorular <summary> icinde duruyor
    #  ve blok ayristiricisi onlari gormuyordu)
    h = re.sub(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>",
               lambda m: "<p><strong>" + strip_tags(m.group(1)) + "</strong> "
                         + re.sub(r"</?p\b[^>]*>", " ", m.group(2)) + "</p>",
               h, flags=re.S | re.I)
    # kalin paragraf basligi -> h3
    h = re.sub(r"<p[^>]*>\s*(?:[^<]{0,4})?\s*<strong>([^<]{3,70})</strong>\s*</p>",
               r"<h3>\1</h3>", h, flags=re.I)
    # sarmalayicilari ac
    h = re.sub(r"</?(div|section|header|article|figure|main|aside|span|small|font|center)\b[^>]*>",
               " ", h, flags=re.I)
    return h


def blocks_of(h):
    """Duzlestirilmis HTML -> sirali blok listesi.

    Bloklar ARASINDA kalan serbest metin de yakalanir: sarmalayici <div>'ler
    acildiginda dogrudan div icindeki metin bloksuz kaliyor ve onceki surumde
    sessizce kayboluyordu (Lumix FT10 / Sanyo HD1'de bolumler bos cikiyordu)."""
    out = []
    pat = re.compile(r"<(h[1-6])\b[^>]*>(.*?)</\1>|<(p)\b[^>]*>(.*?)</\3>|"
                     r"<(ul|ol)\b[^>]*>(.*?)</\5>|<(table)\b[^>]*>(.*?)</\7>",
                     re.S | re.I)

    def loose(seg):
        """Bloklar arasindaki basibos metni pseudo-paragraf olarak ekler."""
        txt = re.sub(rf"<(?!/?(?:{INLINE_OK})\b)[^>]+>", " ", seg or "")
        txt = EMOJI.sub("", txt)
        if len(strip_tags(txt)) > 18:
            out.append({"kind": "p", "html": re.sub(r"\s+", " ", txt).strip(), "loose": True})

    last = 0
    for m in pat.finditer(h):
        loose(h[last:m.start()])
        last = m.end()
        if m.group(1):
            t = clean_txt(strip_tags(m.group(2)))
            if t: out.append({"kind": "h", "level": int(m.group(1)[1]), "text": t})
        elif m.group(3):
            inner = re.sub(rf"<(?!/?(?:{INLINE_OK})\b)[^>]+>", " ", m.group(4))
            inner = EMOJI.sub("", inner)
            if len(strip_tags(inner)) > 2:
                out.append({"kind": "p", "html": re.sub(r"\s+", " ", inner).strip()})
        elif m.group(5):
            items = []
            for li in re.findall(r"<li[^>]*>(.*?)</li>", m.group(6), re.S | re.I):
                li = EMOJI.sub("", re.sub(rf"<(?!/?(?:{INLINE_OK})\b)[^>]+>", " ", li))
                items.append(re.sub(r"\s+", " ", li).strip(" ·-–—•"))
            items = [i for i in items if strip_tags(i)]
            if items: out.append({"kind": "list", "items": items, "raw": m.group(0)})
        elif m.group(7):
            out.append({"kind": "table", "raw": m.group(0)})
    loose(h[last:])
    return out


SEC = [
    ("box",  r"kutu içeri|kutu icer|paket içeri|kutudan çıkacak"),
    ("cond", r"kondisyon|ürün durumu|urun durumu"),
    ("spec", r"teknik|özellik|ozellik|öne çıkan|one cikan|neden bu|neden sevil|desteklenen format"),
    ("who",  r"kimler için|kimler icin|kullanım deneyim|kullanim deneyim"),
    ("faq",  r"sorulan soru|s\.s\.s|sss"),
    ("drop", r"güvence|guvence|teslimat|sipariş|siparis|kargo|takip ed|sosyal|hemen satın|hemen satin|"
             r"bizi takip|bizi izle|iletişim|iletisim|© ?\d{4}|telif|ekosistem"),
]


def classify(text):
    t = tr_lower(text)
    for name, pat in SEC:
        if re.search(pat, t):
            return name
    return "other"


def parse(body):
    """body_html -> yapisal sozluk. Hicbir metin dusurulmez."""
    tiles = tile_pairs(body or "")
    h = flatten(body or "")
    blocks = blocks_of(h)

    doc = {"lead": [], "sections": [], "tiles": tiles}
    cur = None
    for b in blocks:
        if b["kind"] == "h":
            cur = {"title": b["text"], "kind": classify(b["text"]), "blocks": []}
            doc["sections"].append(cur)
        elif cur is None:
            doc["lead"].append(b)
        else:
            cur["blocks"].append(b)
    return doc


def all_text(doc):
    """Belgedeki tum metin (siralamayi korur)."""
    out = []
    for b in doc["lead"]:
        out.append(strip_tags(b.get("html", "")) or " ".join(b.get("items", [])))
    for s in doc["sections"]:
        out.append(s["title"])
        for b in s["blocks"]:
            out.append(strip_tags(b.get("html", "")) or " ".join(b.get("items", [])))
    for t in doc["tiles"]:
        out.append(f"{t['k']} {t['v']} {t.get('note','')}")
    return [x for x in out if x]


def cond_score(doc):
    """Kondisyon puanini OKUR; degeri asla degistirmez.

    Magazada uc ayri yazim var: "8.4 / 10", ters "10/9.8" ve sadece metin
    ("mukemmel kondisyonda"). Once kondisyon bolumu, sonra tum belge taranir."""
    prio = []
    for s in doc["sections"]:
        if s["kind"] in ("cond", "box"):
            prio.append(s["title"])
            prio += [strip_tags(b.get("html", "")) or " ".join(b.get("items", [])) for b in s["blocks"]]
    for hay in (prio, all_text(doc)):
        for t in hay:
            m = re.search(r"(?<![\d/])(\d{1,2}(?:[.,]\d)?)\s*/\s*10(?![\d/])", t)
            if m:
                v = float(m.group(1).replace(",", "."))
                if 0 < v <= 10: return f"{v:g}"
            m = re.search(r"(?<![\d/])10\s*/\s*(\d{1,2}(?:[.,]\d)?)(?![\d/])", t)
            if m:
                v = float(m.group(1).replace(",", "."))
                if 0 < v <= 10: return f"{v:g}"
    return None


def coverage(original, rebuilt):
    """Orijinaldeki cumlelerin kacinin ciktida oldugunu doner."""
    o = sentences(original)
    n = " ".join(sentences(rebuilt))
    missing = [s for s in o if s[:50] not in n]
    return len(o), missing
