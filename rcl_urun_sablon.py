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
.rcl-p-cond{display:flex;align-items:center;gap:20px;margin:20px 0 22px;flex-wrap:wrap;}
.rcl-p-ring{position:relative;flex:0 0 auto;width:92px;height:92px;}
.rcl-p-ring svg{width:92px;height:92px;transform:rotate(-90deg);display:block;}
.rcl-p-ring circle{fill:none;stroke-width:5;stroke-linecap:round;}
.rcl-p-ring .bg{stroke:currentColor;opacity:.14;}
.rcl-p-ring .fg{stroke:currentColor;stroke-dasharray:var(--circ);stroke-dashoffset:var(--circ);
  animation:rcl-ring 1.25s cubic-bezier(.22,.9,.3,1) .2s forwards;}
@keyframes rcl-ring{to{stroke-dashoffset:var(--off);}}
.rcl-p-ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:25px;font-weight:600;letter-spacing:-.02em;
  animation:rcl-fade .6s ease-out .75s both;}
.rcl-p-ring b small{font-size:12px;font-weight:500;opacity:.45;margin-left:1px;}
@keyframes rcl-fade{from{opacity:0;transform:scale(.86);}to{opacity:1;transform:scale(1);}}
.rcl-p-cond__x{flex:1 1 220px;min-width:200px;}
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
.rcl-p-specs .f{font-size:15px;}
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
.rcl-p-social{font-size:15px;margin:28px 0 0;opacity:.62;}

@media(prefers-reduced-motion:reduce){
  .rcl-p-ring .fg{animation:none;stroke-dashoffset:var(--off);}
  .rcl-p-ring b,.rcl-p-badge{animation:none;opacity:1;transform:none;}
  .rcl-p-tested .tick{animation:none;stroke-dashoffset:0;}
}
@media(max-width:480px){
  .rcl-p{font-size:16.5px;}
  .rcl-p h2{font-size:22px;margin:38px 0 12px;}
  .rcl-p-lead{font-size:19px;}
  .rcl-p-specs > div{flex-direction:column;gap:3px;padding:11px 2px;}
  .rcl-p-specs .v{text-align:left;}
  .rcl-p-box,.rcl-p-note{padding:18px;}
  .rcl-p-cond{gap:16px;}
}
</style>"""

GUVENCE = ('<div class="rcl-p-note"><p><strong>RetroCameraLand güvencesi.</strong> Tüm ürünler uzman ekibimiz '
  'tarafından test edilip kondisyon kontrolünden geçirilir: kozmetik durum, lens temizliği ve tüm fonksiyonlar '
  'ayrı ayrı kontrol edilir. Satın alma sürecinden teslimat sonrasına kadar 7/24 destek veriyoruz.</p></div>')

SOCIAL = ('<p class="rcl-p-social">Daha fazla nadir vintage dijital kamera ve örnek çekim için: '
  '<a href="https://instagram.com/retrocameraland?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Instagram" rel="noopener" target="_blank">Instagram</a> · '
  '<a href="https://www.youtube.com/@RetroCameraLand?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Youtube" rel="noopener" target="_blank">YouTube</a> · '
  '<a href="https://www.tiktok.com/@retrocameraland?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Tiktok" rel="noopener" target="_blank">TikTok</a> · '
  '<a href="https://pinterest.com/retrocameraland/?utm_source=ajan&amp;utm_medium=ai&amp;utm_campaign=Links&amp;utm_content=Pinterest" rel="noopener" target="_blank">Pinterest</a></p>')

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
    whole, _, frac = str(score).partition(".")
    num = f"{whole}<small>.{frac}</small>" if frac else whole
    return (f'<div class="rcl-p-ring" style="--circ:{CIRC:.1f};--off:{off:.1f};" '
            f'role="img" aria-label="Kondisyon {score} / 10">'
            f'<svg viewBox="0 0 92 92" aria-hidden="true">'
            f'<circle class="bg" cx="46" cy="46" r="{R}"/>'
            f'<circle class="fg" cx="46" cy="46" r="{R}"/></svg>'
            f'<b>{num}</b></div>')


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
