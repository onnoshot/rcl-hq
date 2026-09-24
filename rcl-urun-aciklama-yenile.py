#!/usr/bin/env python3
"""
rcl-urun-aciklama-yenile.py
Stoktaki urunlerin aciklamalarini Apple-vari sade sablona tasir.

Kural: HICBIR TEKNIK VERI UYDURULMAZ. Mevcut aciklamadaki metin birebir tasinir,
sadece kabuk (baslik/duzen/stil) degisir. "Kutu Icerigi" listesi ve kondisyon
metni harfi harfine korunur.

Kullanim:
  python3 rcl-urun-aciklama-yenile.py --dry-run
  python3 rcl-urun-aciklama-yenile.py --only "Samsung ST10"
  python3 rcl-urun-aciklama-yenile.py --apply
"""
import argparse, html, json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrocameraland_api import shopify

SCRATCH = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7227e27a-4e21-448e-ad28-4066a72ddada/scratchpad"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿️←-⇿⬀-⯿]")

CSS = """<style>
/* Tema rengini miras alir: acik/koyu tema fark etmez. Sabit renk YOK. */
.rcl-pd{font-size:17px;line-height:1.55;letter-spacing:-.01em;max-width:720px;margin:0 auto;padding:8px 0 4px;}
.rcl-pd *{box-sizing:border-box;}
.rcl-pd p{margin:0 0 18px;}
.rcl-pd h2{font-size:26px;line-height:1.2;font-weight:650;letter-spacing:-.02em;margin:48px 0 14px;color:inherit;}
.rcl-pd h3{font-size:18px;line-height:1.3;font-weight:600;letter-spacing:-.01em;margin:28px 0 10px;}
.rcl-pd ul{margin:0 0 18px;padding-left:20px;}
.rcl-pd li{margin:0 0 8px;}
.rcl-pd a{color:inherit;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;opacity:.9;}
.rcl-pd a:hover{opacity:1;}
.rcl-pd-lead{font-size:21px;line-height:1.42;font-weight:450;letter-spacing:-.015em;margin:0 0 26px;}
.rcl-pd-video{position:relative;width:100%;aspect-ratio:16/9;border-radius:14px;overflow:hidden;
  background:rgba(128,128,128,.18);margin:26px 0;}
.rcl-pd-video iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}
.rcl-pd-specs{display:grid;grid-template-columns:1fr;margin:22px 0 26px;border-top:1px solid rgba(128,128,128,.32);}
.rcl-pd-specs > div{display:flex;justify-content:space-between;align-items:baseline;gap:18px;
  padding:13px 2px;border-bottom:1px solid rgba(128,128,128,.32);}
.rcl-pd-specs .k{font-size:15px;opacity:.62;flex:0 0 auto;}
.rcl-pd-specs .v{font-size:15px;font-weight:550;text-align:right;}
.rcl-pd-specs .full{display:block;font-size:15px;}
.rcl-pd-hl{display:grid;grid-template-columns:1fr;gap:1px;background:rgba(128,128,128,.28);
  border:1px solid rgba(128,128,128,.28);border-radius:14px;overflow:hidden;margin:22px 0 26px;}
.rcl-pd-hl > div{background:rgba(128,128,128,.10);padding:20px 22px;}
.rcl-pd-hl strong{display:block;font-size:16px;font-weight:600;margin-bottom:5px;}
.rcl-pd-hl span{display:block;font-size:15px;line-height:1.5;opacity:.7;}
@media(min-width:640px){.rcl-pd-hl{grid-template-columns:1fr 1fr;}}
.rcl-pd-note{background:rgba(128,128,128,.12);border-radius:14px;padding:22px 24px;margin:24px 0;}
.rcl-pd-note p:last-child{margin-bottom:0;}
.rcl-pd-cond{display:flex;align-items:baseline;gap:12px;margin:0 0 14px;flex-wrap:wrap;}
.rcl-pd-cond b{font-size:30px;font-weight:600;letter-spacing:-.02em;line-height:1;}
.rcl-pd-cond span{font-size:15px;opacity:.66;}
.rcl-pd-box{border:1px solid rgba(128,128,128,.32);border-radius:14px;padding:22px 24px;margin:22px 0 26px;}
.rcl-pd-box ul{margin:0;padding-left:20px;}
.rcl-pd-box li{margin:0 0 9px;font-size:16px;}
.rcl-pd-box li:last-child{margin-bottom:0;}
.rcl-pd-faq{border-top:1px solid rgba(128,128,128,.32);margin-top:22px;}
.rcl-pd-faq details{border-bottom:1px solid rgba(128,128,128,.32);}
.rcl-pd-faq summary{cursor:pointer;list-style:none;padding:17px 34px 17px 2px;position:relative;
  font-size:16.5px;font-weight:550;letter-spacing:-.01em;}
.rcl-pd-faq summary::-webkit-details-marker{display:none;}
.rcl-pd-faq summary::after{content:"";position:absolute;right:8px;top:50%;width:8px;height:8px;
  border-right:1.6px solid currentColor;border-bottom:1.6px solid currentColor;opacity:.55;
  transform:translateY(-70%) rotate(45deg);transition:transform .2s;}
.rcl-pd-faq details[open] summary::after{transform:translateY(-30%) rotate(-135deg);}
.rcl-pd-faq p{margin:0 0 18px;font-size:16px;opacity:.72;padding-right:8px;}
.rcl-pd-social{font-size:15px;margin:30px 0 0;opacity:.66;}
@media(max-width:480px){
  .rcl-pd{font-size:16.5px;}
  .rcl-pd h2{font-size:23px;margin:40px 0 12px;}
  .rcl-pd-lead{font-size:19px;}
  .rcl-pd-specs > div{flex-direction:column;gap:2px;padding:11px 2px;}
  .rcl-pd-specs .v{text-align:left;}
  .rcl-pd-hl > div{padding:18px 18px;}
  .rcl-pd-box,.rcl-pd-note{padding:18px 18px;}
}
</style>"""

GUVENCE = ("<div class=\"rcl-pd-note\"><p><strong>RetroCameraLand güvencesi.</strong> Tüm kameralar uzman "
  "ekibimiz tarafından test edilip kondisyon kontrolünden geçirilir: kozmetik durum, lens temizliği ve "
  "tüm fonksiyonlar ayrı ayrı kontrol edilir. Satın alma sürecinden teslimat sonrasına kadar 7/24 destek "
  "veriyoruz; kullanım, bakım ve uyumlu aksesuar için her zaman ulaşabilirsiniz.</p></div>")

SOCIAL = ('<p class="rcl-pd-social">Daha fazla nadir vintage dijital kamera ve örnek çekim için: '
  '<a href="https://www.instagram.com/retrocameraland/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Instagram" rel="noopener" target="_blank">Instagram</a> · '
  '<a href="https://www.youtube.com/@RetroCameraLand?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Youtube" rel="noopener" target="_blank">YouTube</a> · '
  '<a href="https://www.tiktok.com/@retrocameraland?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Tiktok" rel="noopener" target="_blank">TikTok</a> · '
  '<a href="https://pinterest.com/retrocameraland/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Pinterest" rel="noopener" target="_blank">Pinterest</a></p>')

FAQ_AKTARIM = ("<details><summary>Çektiğim fotoğrafları telefonuma nasıl aktarırım?</summary>"
  "<p>Hafıza kartını bir kart okuyucuya takıp telefonunuza bağlayarak. Kameranızın kart formatına uygun "
  "okuyucuya ihtiyacınız var; <a href=\"https://retrocameraland.com/products/y2k-digicam-fotograf-video-aktarici-xd-cf-sd-ms-destekli-all-in-one-kart-okuyucu\">Y2K Digicam Aktarıcı</a> "
  "xD, CF, SD ve Memory Stick formatlarını birlikte destekliyor. Adım adım anlatım için "
  "<a href=\"https://retrocameraland.com/blogs/retro-dijital-kamera/kameradan-telefona-fotograf-aktarma-2026\">aktarım rehberimize</a> göz atabilirsiniz.</p></details>")


def clean(s):
    """Emojileri ve fazla bosluklari temizler, metni korur."""
    s = EMOJI.sub("", s)
    return re.sub(r"\s+", " ", s).strip(" ·-–—:•")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def parse_sections(body):
    """body_html -> [(baslik, ic_html)]; ilk baslik oncesi 'lead' olarak doner."""
    body = re.sub(r"<style[^>]*>.*?</style>", "", body or "", flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    # Bazi urunlerde bolum basliklari <h2> degil kalin paragraf:
    # <p>[emoji] <strong>Kutu Icerigi</strong></p>  -> gercek basliga cevir
    body = re.sub(r"<p[^>]*>\s*(?:[^<]{0,4})?\s*<strong>([^<]{3,60})</strong>\s*</p>",
                  r"<h3>\1</h3>", body, flags=re.I)
    parts = re.split(r"<h[1-4][^>]*>(.*?)</h[1-4]>", body, flags=re.S | re.I)
    lead = parts[0]
    secs = []
    for i in range(1, len(parts) - 1, 2):
        secs.append((clean(parts[i]), parts[i + 1]))
    return lead, secs


def tr_lower(s):
    """Turkce guvenli kucultme.

    Python'da "İ".lower() -> "i" + U+0307 (birlesik nokta) verir; bu yuzden
    "Kutu İçeriği" basligi r"kutu içeri" kalibiyla ESLESMIYORDU ve kutu icerigi
    yanlislikla teknik ozellik tablosuna dusuyordu."""
    return (s.replace("İ", "i").replace("I", "ı").lower()
             .replace("\u0307", ""))


def classify(title):
    t = tr_lower(strip_tags(title))
    if re.search(r"kutu içeri|paket", t) and "kondisyon" not in t: return "box"
    if re.search(r"kondisyon", t): return "cond"
    if re.search(r"teknik|özellik|öne çıkan|neden bu|neden sevil", t): return "spec"
    if re.search(r"kimler için|kullanım deneyim", t): return "who"
    # "RetroCameraLand Yorumu" magazanin kendi uzman degerlendirmesi: KORUNUR.
    # Sadece her urunde tekrarlanan kalip metinler (guvence/teslimat/kargo) atilir,
    # cunku onlarin yerine standart blok konuyor.
    if re.search(r"yorumu|degerlendirme|değerlendirme", t): return "editorial"
    if re.search(r"güvence|teslimat|sipariş|kargo", t): return "skip"
    if re.search(r"takip|sosyal", t): return "skip"
    if re.search(r"sorulan soru|s\.s\.s", t): return "faq"
    return "prose"


def bullets(hhtml):
    hhtml = re.sub(r"<(svg|script|style)\b.*?</\1>", " ", hhtml, flags=re.S | re.I)
    out = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", hhtml, re.S | re.I):
        txt = clean(re.sub(r"<(?!/?(strong|b|em|i|a)\b)[^>]+>", " ", li))
        if txt: out.append(txt)
    return out


def paras(hhtml):
    """Metin bloklarini etiket tipinden BAGIMSIZ cikarir.

    Bazi urunler 'Premium Product Story Block' denen ozel tasarimda ve metni
    <p> yerine <div>/<span> icinde tutuyor; sadece <p> arayan bir ayristirici
    bu urunlerin icerigini sessizce siliyordu (HP R827: 2863 -> 418 kelime)."""
    hhtml = re.sub(r"<(svg|script|style|noscript)\b.*?</\1>", " ", hhtml, flags=re.S | re.I)
    # Once gercek metin etiketlerini dene. Sarmalayici <div>, icindeki <p>'leri
    # regex eslesmesinde yutuyordu (finditer eslesme icine tekrar bakmaz), bu yuzden
    # p/li/td bulunursa div/span taramasina hic inilmiyor.
    out, seen = [], set()
    # once gercek metin etiketleri, SONRA div/span: boylece hem sarmalayici div'in
    # yuttugu <p>'ler hem de sadece div/span kullanan ozel sablonlar yakalanir
    for m in list(re.finditer(r"<(p|li|td)\b[^>]*>(.*?)</\1>", hhtml, re.S | re.I)) + \
             list(re.finditer(r"<(div|span|small)\b[^>]*>(.*?)</\1>", hhtml, re.S | re.I)):
        inner = m.group(2)
        # icinde baska bir metin blogu varsa onu atla, cocuklari zaten gelecek
        if re.search(r"<(p|div|li|table|ul|ol)\b", inner, re.I): continue
        txt = re.sub(r"\s+", " ", re.sub(r"<(?!/?(strong|b|em|i|a|br)\b)[^>]+>", " ", inner)).strip()
        txt = EMOJI.sub("", txt).strip()
        key = strip_tags(txt).lower()[:80]
        if len(strip_tags(txt)) > 25 and key not in seen:
            seen.add(key)
            out.append(txt)
    return out


def tile_pairs(hhtml):
    """'Premium Product Story Block' sablonundaki etiket/deger cifti kutularini okur.

    Bu urunlerde teknik veriler <li> degil, ardisik <div class="...tileK">Sensor</div>
    <div class="...tileV">7.2 MP CCD</div> yapisinda duruyor; sadece <li> arayan
    ayristirici bu degerleri (7.2 MP, 5.1 MP, 3x zoom...) sessizce dusuruyordu."""
    hhtml = re.sub(r"<(svg|script|style)\b.*?</\1>", " ", hhtml, flags=re.S | re.I)
    out = []
    pat = (r'<div[^>]*class="[^"]*tileK[^"]*"[^>]*>(.*?)</div>\s*'
           r'<div[^>]*class="[^"]*tileV[^"]*"[^>]*>(.*?)</div>'
           r'(?:\s*<div[^>]*class="[^"]*tileP[^"]*"[^>]*>(.*?)</div>)?')
    for k, v, note in re.findall(pat, hhtml, re.S | re.I):
        k, v, note = clean(strip_tags(k)), clean(strip_tags(v)), clean(strip_tags(note or ""))
        if not (k and v): continue
        # tileP aciklama notu da korunur; yoksa sessizce kaybolur
        out.append(f"{k}: {v}" + (f" — {note}" if note else ""))
    return out


def spec_rows(items):
    rows = []
    for it in items:
        m = re.match(r"^\s*(?:<strong>)?([^:<]{2,34}?)(?:</strong>)?\s*[:：]\s*(.+)$", it)
        if m:
            rows.append(f'<div><span class="k">{clean(m.group(1))}</span>'
                        f'<span class="v">{m.group(2).strip()}</span></div>')
        else:
            rows.append(f'<div><span class="full">{it}</span></div>')
    return '<div class="rcl-pd-specs">' + "".join(rows) + "</div>" if rows else ""


def faq_block(hhtml, is_camera):
    items = []
    for m in re.finditer(r"<p[^>]*>\s*<strong>(.*?)</strong>\s*(?:<br\s*/?>)?\s*(.*?)</p>", hhtml, re.S | re.I):
        q, a = clean(m.group(1)), re.sub(r"\s+", " ", m.group(2)).strip()
        if q and a and len(strip_tags(a)) > 15:
            items.append(f"<details><summary>{q}</summary><p>{a}</p></details>")
    if is_camera:
        items.append(FAQ_AKTARIM)
    return '<div class="rcl-pd-faq">' + "".join(items) + "</div>" if items else ""


def koleksiyon(model, is_camera):
    if not is_camera: return ""
    return (f"<h2>Koleksiyon değeri</h2>"
      f"<p>{model} üretimden kalktı ve bu modeller artık yalnızca ikinci el olarak dolaşımda. "
      f"CCD kuşağı kompakt kameraların üretimi büyük ölçüde sona erdiği için aynı görüntü karakterini "
      f"üreten yeni bir cihaz da yok.</p>"
      f"<p>Bu, kamerayı bir yatırım aracı yapmaz. Ama çalışır durumda, test edilmiş ve tam set bir ünite "
      f"bulmak her geçen yıl zorlaşıyor. Stoğumuzdaki her kamera tek adet.</p>")


def build(product, video_id=None):
    """Icerigi KORUYARAK yeniden duzenler.

    Ilke: kalip metinler (guvence/teslimat/sosyal) disinda HICBIR sey atilmaz.
    Onceki surum sadece tanidigi bolumleri aliyordu ve urunlerin %40 metnini
    sessizce dusuruyordu; artik taninmayan bolumler de basligiyla korunuyor."""
    body = product["body_html"] or ""
    title = product["title"]
    is_camera = not re.search(r"kart okuyucu|aktarıcı|tripod|şarj cihaz|batarya", title, re.I)

    lead_html, secs = parse_sections(body)
    lead_ps = paras(lead_html)
    lead_specs = bullets(lead_html) or tile_pairs(lead_html)

    box_html = cond_html = faq_html = ""
    mid = []          # bolumler, ORIJINAL SIRASIYLA
    cond_score = None

    for h, content in secs:
        kind = classify(h)
        if kind == "skip":
            continue
        if kind == "box" and not box_html:
            ul = re.search(r"<ul[^>]*>.*?</ul>", content, re.S | re.I)
            if ul:
                box_html = f'<h2>Kutu İçeriği</h2><div class="rcl-pd-box">{ul.group(0)}</div>'
                continue
        if kind == "cond" and not cond_html:
            ul = re.search(r"<ul[^>]*>.*?</ul>", content, re.S | re.I)
            m = re.search(r"(\d{1,2}[.,]\d)\s*/\s*10", strip_tags(content))
            cond_score = m.group(1).replace(",", ".") if m else None
            ps = [re.sub(r"<strong>\s*Kondisyon:.*?</strong>\s*", "", x) for x in paras(content)]
            inner = "".join(f"<p>{x}</p>" for x in ps if strip_tags(x))
            cond_html = "<h2>Kondisyon</h2>"
            if cond_score:
                cond_html += (f'<div class="rcl-pd-cond"><b>{cond_score}</b><span>/ 10 &nbsp;·&nbsp; '
                              f'RetroCameraLand ekibi tarafından test edildi</span></div>')
            cond_html += inner or (ul.group(0) if ul else "")
            if ul and re.search(r"kutu", h, re.I) and not box_html:
                box_html = f'<h2>Kutu İçeriği</h2><div class="rcl-pd-box">{ul.group(0)}</div>'
            continue
        if kind == "faq" and not faq_html:
            faq_html = faq_block(content, is_camera)
            continue
        # taninmayan/diger tum bolumler: basligi + TUM icerigi korunur
        items = bullets(content) or tile_pairs(content)
        ps = paras(content)
        if not items and not ps:
            continue
        head = clean(h)
        blk = f"<h2>{head[:1].upper() + head[1:].lower() if head.isupper() else head}</h2>" if head else ""
        if items: blk += spec_rows(items)
        blk += "".join(f"<p>{x}</p>" for x in ps)
        mid.append(blk)

    if not faq_html and is_camera:
        faq_html = '<div class="rcl-pd-faq">' + FAQ_AKTARIM + "</div>"

    out = [CSS, '<div class="rcl-pd">']
    if lead_ps:
        out.append(f'<p class="rcl-pd-lead">{lead_ps[0]}</p>')
        out += [f"<p>{x}</p>" for x in lead_ps[1:]]
    if video_id:
        out.append(f'<div class="rcl-pd-video"><iframe src="https://www.youtube.com/embed/{video_id}" '
                   f'title="{html.escape(title)} - Retro Camera Land" loading="lazy" '
                   f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                   f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')
    if lead_specs:
        out.append("<h2>Teknik özellikler</h2>" + spec_rows(lead_specs))
    out += mid
    out.append(koleksiyon(title, is_camera))
    out.append(cond_html)
    out.append(box_html)
    out.append(GUVENCE)
    if faq_html:
        out.append("<h2>Sık sorulan sorular</h2>" + faq_html)
    out.append(SOCIAL)
    out.append("</div>")
    return "\n".join(x for x in out if x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    prods = json.load(open(f"{SCRATCH}/instock_products.json"))
    matches = {m["pid"]: m for m in json.load(open(f"{SCRATCH}/video_matches.json"))}
    # Z700EXR kopyasi ayni kamera -> ayni video
    for p in prods:
        if "Z700EXR" in p["title"].replace(" ", ""):
            src = next((m for m in matches.values() if "Z700 EXR" in m["product"]), None)
            if src and p["id"] not in matches:
                matches[p["id"]] = {**src, "pid": p["id"]}

    for p in prods:
        if a.only and a.only.lower() not in p["title"].lower(): continue
        if p["title"] == "Sony Cyber-shot DSC-T9": continue   # elle yazilan ornek korunur
        vid = matches.get(p["id"], {}).get("video_id")
        new = build(p, vid)
        old_words = len(strip_tags(p["body_html"] or "").split())
        new_words = len(strip_tags(new).split())
        flag = "video" if vid else "     "
        print(f"  {p['title'][:38]:<40} {old_words:>4} → {new_words:>4} kelime  {flag}")
        if a.apply:
            shopify("PUT", f"products/{p['id']}.json", {"product": {"id": p["id"], "body_html": new}})
        elif a.dry_run:
            open(f"{SCRATCH}/pd_preview_{p['id']}.html", "w", encoding="utf-8").write(new)


if __name__ == "__main__":
    main()
