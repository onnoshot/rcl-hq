#!/usr/bin/env python3
"""
rcl_urun_sablon.py — ayristirilmis urun icerigini Apple-vari sablona kurar.

Kurallar:
  * Kondisyon puani ve kutu icerigi metinleri ASLA degistirilmez, sadece tasinir.
  * "Kutu Icerigi" en uste konur (kullanici istegi).
  * Kondisyon animasyonlu halka ile gosterilir; puan yoksa metin rozeti kullanilir.
  * Siniflandirilamayan her blok "leftover" olarak yine basilir -> kayipsizlik.
  * Renk SABITLENMEZ, temadan miras alinir (magaza temasi koyu).
"""
import html as _html
import re

from rcl_urun_icerik import strip_tags, clean_txt, tr_lower

CSS = """<style>
/* Renkler temadan miras alinir; ara tonlar opacity ile verilir. */
.rcl-p{font-size:17px;line-height:1.55;letter-spacing:-.01em;max-width:720px;margin:0 auto;padding:6px 0 4px;}
.rcl-p *{box-sizing:border-box;}
.rcl-p p{margin:0 0 17px;}
.rcl-p h2{font-size:25px;line-height:1.22;font-weight:650;letter-spacing:-.02em;margin:46px 0 14px;color:inherit;}
.rcl-p h3{font-size:17.5px;font-weight:600;letter-spacing:-.01em;margin:26px 0 9px;}
.rcl-p ul{margin:0 0 17px;padding-left:20px;}
.rcl-p li{margin:0 0 8px;}
.rcl-p a{color:inherit;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;opacity:.88;}
.rcl-p a:hover{opacity:1;}
.rcl-p-lead{font-size:21px;line-height:1.4;font-weight:450;letter-spacing:-.015em;margin:0 0 24px;}

/* --- Kutu icerigi (en ust) --- */
.rcl-p-box{border:1px solid rgba(128,128,128,.28);border-radius:16px;padding:20px 22px;margin:22px 0 28px;
  background:rgba(128,128,128,.05);}
.rcl-p-box h3{margin:0 0 14px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.55;font-weight:600;}
.rcl-p-box ul{margin:0;padding:0;list-style:none;}
.rcl-p-box li{margin:0 0 11px;padding-left:26px;position:relative;font-size:16px;line-height:1.45;}
.rcl-p-box li:last-child{margin-bottom:0;}
.rcl-p-box li::before{content:"";position:absolute;left:2px;top:.46em;width:9px;height:5px;
  border-left:1.7px solid currentColor;border-bottom:1.7px solid currentColor;
  transform:rotate(-45deg);opacity:.55;}

/* --- Kondisyon halkasi (animasyonlu) --- */
.rcl-p-cond{display:flex;align-items:flex-start;gap:22px;margin:18px 0 24px;}
.rcl-p-ring{position:relative;flex:0 0 auto;width:92px;height:92px;}
.rcl-p-ring svg{width:92px;height:92px;transform:rotate(-90deg);display:block;}
.rcl-p-ring circle{fill:none;stroke-width:5;stroke-linecap:round;}
.rcl-p-ring .bg{stroke:currentColor;opacity:.14;}
.rcl-p-ring .fg{stroke:currentColor;stroke-dasharray:var(--circ);stroke-dashoffset:var(--circ);
  animation:rcl-ring 1.25s cubic-bezier(.22,.9,.3,1) .2s forwards;}
@keyframes rcl-ring{to{stroke-dashoffset:var(--off);}}
.rcl-p-ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:25px;font-weight:600;letter-spacing:-.03em;line-height:1;
  animation:rcl-fade .6s ease-out .75s both;}
.rcl-p-score{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;gap:7px;}
.rcl-p-scale{font-size:11px;letter-spacing:.07em;text-transform:uppercase;opacity:.4;
  animation:rcl-fade .6s ease-out .9s both;}
@keyframes rcl-fade{from{opacity:0;transform:scale(.86);}to{opacity:1;transform:scale(1);}}
.rcl-p-cond__x{flex:1 1 auto;min-width:0;}
.rcl-p-cond__x p{margin:0 0 9px;}
.rcl-p-cond__x p:last-child{margin-bottom:0;}
.rcl-p-tested{display:inline-flex;align-items:center;gap:7px;font-size:13px;opacity:.6;margin-bottom:9px;}
.rcl-p-tested svg{flex:0 0 auto;}
.rcl-p-tested .tick{stroke-dasharray:14;stroke-dashoffset:14;animation:rcl-draw .55s ease-out 1.1s forwards;}
@keyframes rcl-draw{to{stroke-dashoffset:0;}}
.rcl-p-badge{display:inline-block;padding:7px 15px;border:1px solid rgba(128,128,128,.32);border-radius:999px;
  font-size:14px;font-weight:550;animation:rcl-fade .6s ease-out .2s both;}

/* --- Video --- */
.rcl-p-vid{position:relative;width:100%;aspect-ratio:16/9;border-radius:14px;overflow:hidden;
  background:rgba(128,128,128,.16);margin:26px 0;}
.rcl-p-vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}

/* --- Teknik ozellikler --- */
.rcl-p-specs{margin:20px 0 26px;border-top:1px solid rgba(128,128,128,.28);}
.rcl-p-specs > div{display:flex;justify-content:space-between;align-items:baseline;gap:20px;
  padding:13px 2px;border-bottom:1px solid rgba(128,128,128,.28);}
.rcl-p-specs .k{font-size:15px;opacity:.6;flex:0 0 auto;}
.rcl-p-specs .v{font-size:15px;font-weight:550;text-align:right;}
.rcl-p-specs .f{font-size:15.5px;line-height:1.5;position:relative;padding-left:17px;}
.rcl-p-specs .f::before{content:"";position:absolute;left:2px;top:.62em;width:4px;height:4px;
  border-radius:50%;background:currentColor;opacity:.4;}
.rcl-p-specs .n{display:block;font-size:13.5px;opacity:.55;font-weight:400;margin-top:3px;}

.rcl-p-note{background:rgba(128,128,128,.11);border-radius:14px;padding:20px 22px;margin:26px 0;}
.rcl-p-note p:last-child{margin-bottom:0;}

.rcl-p-faq{border-top:1px solid rgba(128,128,128,.28);margin-top:20px;}
.rcl-p-faq details{border-bottom:1px solid rgba(128,128,128,.28);}
.rcl-p-faq summary{cursor:pointer;list-style:none;padding:16px 34px 16px 2px;position:relative;
  font-size:16.5px;font-weight:550;letter-spacing:-.01em;}
.rcl-p-faq summary::-webkit-details-marker{display:none;}
.rcl-p-faq summary::after{content:"";position:absolute;right:8px;top:50%;width:8px;height:8px;
  border-right:1.6px solid currentColor;border-bottom:1.6px solid currentColor;opacity:.5;
  transform:translateY(-70%) rotate(45deg);transition:transform .22s;}
.rcl-p-faq details[open] summary::after{transform:translateY(-30%) rotate(-135deg);}
.rcl-p-faq p{margin:0 0 17px;font-size:16px;opacity:.72;padding-right:8px;}
.rcl-p-soc{margin:34px 0 4px;padding-top:22px;border-top:1px solid rgba(128,128,128,.24);
  display:flex;flex-direction:column;align-items:center;gap:14px;text-align:center;}
.rcl-p-soc__t{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;opacity:.42;}
.rcl-p-soc__r{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;}
.rcl-p-soc__i{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;
  border:1px solid rgba(128,128,128,.26);border-radius:50%;color:inherit;opacity:.62;
  text-decoration:none;transition:opacity .2s,transform .2s,border-color .2s;}
.rcl-p-soc__i svg{width:18px;height:18px;}
.rcl-p-soc__i:hover{opacity:1;transform:translateY(-2px);border-color:rgba(128,128,128,.5);}
@media(prefers-reduced-motion:reduce){.rcl-p-soc__i{transition:none;}.rcl-p-soc__i:hover{transform:none;}}

@media(prefers-reduced-motion:reduce){
  .rcl-p-ring .fg{animation:none;stroke-dashoffset:var(--off);}
  .rcl-p-ring b,.rcl-p-badge{animation:none;opacity:1;transform:none;}
  .rcl-p-tested .tick{animation:none;stroke-dashoffset:0;}
}
@media(max-width:560px){
  .rcl-p{font-size:16px;line-height:1.58;}
  .rcl-p h2{font-size:21px;line-height:1.26;margin:40px 0 12px;}
  .rcl-p h3{font-size:16.5px;margin:22px 0 8px;}
  .rcl-p p{margin:0 0 15px;}
  .rcl-p-lead{font-size:18.5px;line-height:1.45;margin:0 0 22px;}

  /* Kondisyon: halka ustte, metin TAM GENISLIK (yan yana iken satirlar
     3 kelimeye dusuyor ve okunmuyordu) */
  .rcl-p-cond{flex-direction:column;align-items:flex-start;gap:14px;margin:16px 0 22px;}
  .rcl-p-ring,.rcl-p-ring svg{width:74px;height:74px;}
  .rcl-p-ring b{font-size:22px;}
  .rcl-p-cond__x{width:100%;}

  .rcl-p-box{padding:18px 18px;border-radius:14px;}
  .rcl-p-box li{font-size:15.5px;padding-left:24px;}
  .rcl-p-note{padding:18px;border-radius:14px;}
  .rcl-p-specs > div{flex-direction:column;align-items:flex-start;gap:2px;padding:12px 2px;}
  .rcl-p-specs .v{text-align:left;font-size:15.5px;}
  .rcl-p-specs .k{font-size:13px;letter-spacing:.02em;opacity:.5;}
  .rcl-p-faq summary{font-size:16px;padding:15px 30px 15px 2px;}
  .rcl-p-faq p{font-size:15.5px;}
}
</style>"""

GUVENCE = ('<div class="rcl-p-note"><p><strong>RetroCameraLand güvencesi.</strong> Tüm ürünler uzman ekibimiz '
  'tarafından test edilip kondisyon kontrolünden geçirilir: kozmetik durum, lens temizliği ve tüm fonksiyonlar '
  'ayrı ayrı kontrol edilir. Satın alma sürecinden teslimat sonrasına kadar 7/24 destek veriyoruz.</p></div>')

SOCIAL_ICONS = {
 "instagram": ('https://instagram.com/retrocameraland', 'Instagram',
   '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
   '<circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/>'),
 "youtube": ('https://www.youtube.com/@RetroCameraLand', 'YouTube',
   '<rect x="2" y="5" width="20" height="14" rx="4.5"/>'
   '<path d="M10.2 9.3v5.4l4.6-2.7z" fill="currentColor" stroke="none"/>'),
 "tiktok": ('https://www.tiktok.com/@retrocameraland', 'TikTok',
   '<path d="M14 3.5v10.9a3.6 3.6 0 1 1-3-3.55"/><path d="M14 3.5c.4 2.4 2 4 4.4 4.2"/>'),
 "pinterest": ('https://pinterest.com/retrocameraland/', 'Pinterest',
   '<circle cx="12" cy="12" r="9"/><path d="M10.4 20c-.5-1.7.1-3.6.6-5.4.4-1.6-.5-2.6-.5-3.6 0-1.5 1-2.6 2.2-2.6 1.1 0 1.8.8 1.8 2 0 1.3-.8 3.2-1.2 4.9-.3 1.4.7 2.3 2 2.3 2.2 0 3.7-2.8 3.7-5.6 0-2.5-1.8-4.4-4.7-4.4-3.3 0-5.3 2.3-5.3 4.9 0 1 .3 1.7.8 2.3"/>'),
 "x": ('https://x.com/retrocameraland', 'X',
   '<path d="M4 4l16 16M20 4L4 20"/>'),
 "linkedin": ('https://www.linkedin.com/company/109991351/', 'LinkedIn',
   '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7.5 10.5v6"/>'
   '<circle cx="7.5" cy="7.4" r="1" fill="currentColor" stroke="none"/>'
   '<path d="M11.5 16.5v-3.2a2.3 2.3 0 0 1 4.6 0v3.2"/><path d="M11.5 16.5v-6"/>'),
 "facebook": ('https://www.facebook.com/people/Retro-Camera-Land/61577258224362/', 'Facebook',
   '<circle cx="12" cy="12" r="9"/><path d="M14.8 8.4h-1.5c-.8 0-1.3.5-1.3 1.3V12m-1.7 0h4.2M12 12v7"/>'),
}


def social_strip():
    """Minimal SVG ikon seridi — tum RCL sosyal hesaplari."""
    items = []
    for key, (url, label, path) in SOCIAL_ICONS.items():
        items.append(
            f'<a class="rcl-p-soc__i" href="{url}?utm_source=urun&amp;utm_medium=sosyal&amp;utm_campaign=rcl" '
            f'target="_blank" rel="noopener" aria-label="{label}" title="{label}">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg></a>')
    return ('<div class="rcl-p-soc"><span class="rcl-p-soc__t">Retrocameraland\'i takip edin</span>'
            '<div class="rcl-p-soc__r">' + "".join(items) + '</div></div>')


SOCIAL = social_strip()

FAQ_AKTARIM = ('<details><summary>Çektiğim fotoğrafları telefonuma nasıl aktarırım?</summary>'
  '<p>Hafıza kartını bir kart okuyucuya takıp telefonunuza bağlayarak. Kameranızın kart formatına uygun '
  'okuyucuya ihtiyacınız var; <a href="https://retrocameraland.com/products/y2k-digicam-fotograf-video-aktarici-xd-cf-sd-ms-destekli-all-in-one-kart-okuyucu">Y2K Digicam Aktarıcı</a> '
  'xD, CF, SD ve Memory Stick formatlarını birlikte destekliyor. Adım adım anlatım için '
  '<a href="https://retrocameraland.com/blogs/retro-dijital-kamera/kameradan-telefona-fotograf-aktarma-2026">aktarım rehberimize</a> göz atabilirsiniz.</p></details>')

TICK_SVG = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
  'stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
  '<circle cx="12" cy="12" r="9" opacity=".45"/><path class="tick" d="M8 12.3l2.6 2.6L16 9.5"/></svg>')

R = 42.0
CIRC = 2 * 3.14159265 * R


def cond_ring(score):
    """Kondisyon halkasi. Puan METNI degistirilmez, oldugu gibi basilir."""
    off = CIRC * (1 - float(score) / 10.0)
    num = str(score)
    return (f'<div class="rcl-p-score">'
            f'<div class="rcl-p-ring" style="--circ:{CIRC:.1f};--off:{off:.1f};" '
            f'role="img" aria-label="Kondisyon {score} / 10">'
            f'<svg viewBox="0 0 92 92" aria-hidden="true">'
            f'<circle class="bg" cx="46" cy="46" r="{R}"/>'
            f'<circle class="fg" cx="46" cy="46" r="{R}"/></svg>'
            f'<b>{num}</b></div>'
            f'<span class="rcl-p-scale">10 üzerinden</span></div>')


def spec_rows(items, tiles):
    rows = []
    for t in tiles:
        note = f'<span class="n">{t["note"]}</span>' if t.get("note") else ""
        rows.append(f'<div><span class="k">{t["k"]}</span>'
                    f'<span class="v">{t["v"]}{note}</span></div>')
    for it in items:
        m = re.match(r"^\s*(?:<strong>)?([^:<]{2,32}?)(?:</strong>)?\s*[:：]\s*(.+)$", it)
        if m:
            rows.append(f'<div><span class="k">{clean_txt(m.group(1))}</span>'
                        f'<span class="v">{m.group(2).strip()}</span></div>')
        else:
            rows.append(f'<div><span class="f">{it}</span></div>')
    return f'<div class="rcl-p-specs">{"".join(rows)}</div>' if rows else ""


def faq_from(blocks, is_camera):
    items = []
    for b in blocks:
        h = b.get("html", "")
        m = re.match(r"\s*<strong>(.*?)</strong>\s*(?:<br\s*/?>)?\s*(.+)$", h, re.S | re.I)
        if m and len(strip_tags(m.group(2))) > 12:
            items.append(f"<details><summary>{clean_txt(strip_tags(m.group(1)))}</summary>"
                         f"<p>{m.group(2).strip()}</p></details>")
    if is_camera:
        items.append(FAQ_AKTARIM)
    return f'<div class="rcl-p-faq">{"".join(items)}</div>' if items else ""


def render_blocks(blocks):
    out = []
    for b in blocks:
        if b["kind"] == "p":
            out.append(f'<p>{b["html"]}</p>')
        elif b["kind"] == "list":
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in b["items"]) + "</ul>")
        elif b["kind"] == "table":
            out.append(b["raw"])
    return "".join(out)


# ── SSS uretimi ───────────────────────────────────────────────────────────────
# Sorularin cevaplari YALNIZCA o urunun kendi verisinden (kondisyon, kutu
# icerigi, teknik ozellikler) uretilir. Veri yoksa soru hic sorulmaz; boylece
# musteriyi yaniltacak bir cevap olusmasi imkansiz.

def _spec_find(specs, *keys):
    for s in specs:
        low = s.lower()
        if any(k in low for k in keys):
            return s.split(":", 1)[1].strip() if ":" in s else s.strip()
    return None


def build_faq(title, score, cond_text, box_items, specs, is_cam):
    qs = []
    short = re.sub(r"\s*\(.*?\)\s*", " ", title).strip()

    if score or cond_text:
        parts = []
        if score:
            parts.append(f"Bu ünite {score}/10 kondisyonda.")
        if cond_text:
            parts.append(cond_text.strip())
        parts.append("Her ürün RetroCameraLand ekibi tarafından tek tek test edilip onaylanır.")
        qs.append((f"{short} çalışır durumda mı, test edildi mi?", " ".join(parts)))

    if box_items:
        lst = ", ".join(box_items[:-1]) + (" ve " + box_items[-1] if len(box_items) > 1 else box_items[0])
        qs.append(("Kutudan neler çıkıyor?",
                   f"{lst}. Ürün RetroCameraLand özel paketlemesiyle gönderilir."))

    card = _spec_find(specs, "hafıza", "kart", "depolama", "memory")
    if card and is_cam:
        qs.append(("Hangi hafıza kartını kullanıyor?",
                   f"{card} Kartınız yoksa uyumlu bir kart için bize yazabilirsiniz."))

    vid = _spec_find(specs, "video")
    if vid and is_cam:
        qs.append(("Video çekebiliyor mu?", f"Evet. {vid}"))

    bat = _spec_find(specs, "batarya", "pil", "güç")
    if bat and is_cam:
        qs.append(("Bataryası nasıl, şarj aleti dahil mi?",
                   f"{bat} Şarj için gereken parçalar kutu içeriğinde listelenmiştir."))

    if is_cam:
        qs.append(("Çektiğim fotoğrafları telefonuma nasıl aktarırım?",
                   'Hafıza kartını bir kart okuyucuya takıp telefonunuza bağlayarak. '
                   '<a href="https://retrocameraland.com/products/y2k-digicam-fotograf-video-aktarici-xd-cf-sd-ms-destekli-all-in-one-kart-okuyucu">Y2K Digicam Aktarıcı</a> '
                   'xD, CF, SD ve Memory Stick formatlarını birlikte destekliyor; adım adım anlatım için '
                   '<a href="https://retrocameraland.com/blogs/retro-dijital-kamera/kameradan-telefona-fotograf-aktarma-2026">aktarım rehberimize</a> göz atabilirsiniz.'))
        qs.append(("Bu model hâlâ üretiliyor mu?",
                   f"Hayır, {short} üretimden kalktı ve yalnızca ikinci el olarak bulunuyor. "
                   "Stoğumuzdaki her kamera tek adettir."))

    if not is_cam:
        # Aksesuarlarda kondisyon/kutu verisi olmayabiliyor: sorular teknik
        # ozelliklerden uretiliyor, yoksa hic sorulmuyor.
        comp = _spec_find(specs, "uyum", "destek", "giriş", "kart")
        if comp:
            qs.append(("Hangi cihaz ve kartlarla uyumlu?",
                       f"{comp} Emin değilseniz kameranızın modelini yazın, biz kontrol edelim."))
        setup = _spec_find(specs, "kurulum", "tak-çalıştır", "plug", "bağlantı")
        if setup:
            qs.append(("Kurulum veya yazılım gerekiyor mu?", f"{setup}"))
        speed = _spec_find(specs, "hız", "gbps", "usb 3", "aktarım")
        if speed:
            qs.append(("Aktarım hızı nasıl?", f"{speed}"))
        qs.append(("Retro kameramla çalışır mı?",
                   "Retro dijital kameraların büyük çoğunluğuyla uyumludur. Kameranızın kart "
                   "formatından emin değilseniz "
                   '<a href="https://retrocameraland.com/blogs/retro-dijital-kamera/kameradan-telefona-fotograf-aktarma-2026">aktarım rehberimizdeki</a> '
                   "kart formatı tablosuna bakabilir ya da bize yazabilirsiniz."))

    qs.append(("Kargo ve iade nasıl işliyor?",
               "Siparişler özenli paketlemeyle hazırlanıp hızlı kargoya verilir. İade ve değişim "
               'koşulları için <a href="https://retrocameraland.com/policies/refund-policy">iade politikamıza</a> '
               "göz atabilir, aklınıza takılan her konuda bize yazabilirsiniz."))

    items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qs)
    return f'<div class="rcl-p-faq">{items}</div>'
