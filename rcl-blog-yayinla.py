#!/usr/bin/env python3
"""
rcl-blog-yayinla.py — elle yazilmis blog yazilarini semalariyla birlikte yayinlar.

AI aramalari (AEO/GEO) icin: cevap-onde giris, soru bicimli H2'ler, karsilastirma
tablosu, acilir SSS + Article/FAQPage/BreadcrumbList semalari.

Kullanim:
  python3 rcl-blog-yayinla.py --dry-run
  python3 rcl-blog-yayinla.py --only kac-yil
  python3 rcl-blog-yayinla.py --apply
"""
import argparse, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrocameraland_api import shopify, BLOG_ID, SOCIAL_BLOCK

SCRATCH = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/7227e27a-4e21-448e-ad28-4066a72ddada/scratchpad"
BASE = "https://retrocameraland.com/blogs/retro-dijital-kamera/"

CSS = """<style>
.rcl-g{--acc:#E10600;font-size:16.5px;line-height:1.68;letter-spacing:-.01em;max-width:940px;margin:0 auto;}
.rcl-g *{box-sizing:border-box;}
.rcl-g h2{color:var(--acc);font-weight:800;font-size:25px;line-height:1.25;margin:42px 0 14px;scroll-margin-top:80px;}
.rcl-g h3{font-weight:700;font-size:18px;margin:24px 0 9px;}
.rcl-g p{margin:0 0 15px;}
.rcl-g a{color:var(--acc);}
.rcl-g ul,.rcl-g ol{margin:0 0 16px;padding-left:22px;}
.rcl-g li{margin:0 0 8px;}
.rcl-lead{font-size:19px;line-height:1.5;margin:0 0 22px;}
.rcl-ans{border:1px solid rgba(128,128,128,.28);border-left:5px solid var(--acc);border-radius:12px;
  padding:16px 18px;margin:20px 0;background:rgba(128,128,128,.05);}
.rcl-ans strong{font-weight:800;}
.rcl-toc{margin:22px 0;padding:16px 18px;border:1px dashed rgba(128,128,128,.4);border-radius:14px;}
.rcl-toc strong{display:block;margin-bottom:9px;font-size:14px;}
.rcl-toc ol{margin:0;padding-left:20px;columns:2;column-gap:26px;}
.rcl-toc li{margin:0 0 6px;break-inside:avoid;}
.rcl-toc a{color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,.6);}
.rcl-tip{border:1px solid rgba(128,128,128,.28);border-left:5px solid var(--acc);border-radius:12px;
  padding:13px 16px;margin:16px 0;font-size:15.5px;}
.rcl-tw{overflow-x:auto;margin:18px 0;-webkit-overflow-scrolling:touch;}
.rcl-g table{width:100%;border-collapse:collapse;font-size:15px;min-width:520px;}
.rcl-g th,.rcl-g td{padding:11px 13px;border:1px solid rgba(128,128,128,.3);text-align:left;vertical-align:top;}
.rcl-g th{background:rgba(128,128,128,.1);font-weight:700;}
.rcl-g details{border:1px solid rgba(128,128,128,.3);border-radius:12px;margin:0 0 10px;overflow:hidden;}
.rcl-g summary{cursor:pointer;padding:14px 16px;font-weight:700;font-size:16px;list-style:none;
  display:flex;justify-content:space-between;gap:12px;}
.rcl-g summary::-webkit-details-marker{display:none;}
.rcl-g summary::after{content:"+";color:var(--acc);font-size:21px;line-height:1;}
.rcl-g details[open] summary::after{content:"−";}
.rcl-g details>p{margin:14px 16px;}
.rcl-pick{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0;}
.rcl-pick a{flex:1 1 230px;border:1px solid rgba(128,128,128,.3);border-radius:12px;padding:13px 15px;
  text-decoration:none;color:inherit;font-weight:600;font-size:14.5px;}
.rcl-pick a span{display:block;font-weight:400;font-size:13px;opacity:.7;margin-top:3px;}
.rcl-pick a:hover{border-color:var(--acc);}
.rcl-cta{text-align:center;margin:30px 0;padding:22px 18px;border-radius:14px;
  background:rgba(128,128,128,.08);border:1px solid rgba(128,128,128,.25);}
.rcl-cta a{display:inline-block;background:#141416;color:#fff;padding:14px 28px;border-radius:8px;
  text-decoration:none;font-weight:700;font-size:15px;}
@media(max-width:640px){.rcl-toc ol{columns:1;}.rcl-g h2{font-size:22px;}.rcl-lead{font-size:17.5px;}}
</style>"""


def schemas(post):
    url = BASE + post["handle"]
    out = [{
        "@context": "https://schema.org", "@type": "Article",
        "headline": post["title"], "description": post["meta"],
        "author": {"@type": "Organization", "name": "Retrocameraland", "url": "https://retrocameraland.com"},
        "publisher": {"@type": "Organization", "name": "Retrocameraland", "url": "https://retrocameraland.com"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "inLanguage": "tr-TR",
    }]
    faqs = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", post["body"], re.S)
    if faqs:
        out.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": re.sub(r"<[^>]+>", "", q).strip(),
             "acceptedAnswer": {"@type": "Answer",
                                "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", a)).strip()}}
            for q, a in faqs[:10]]})
    out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Anasayfa", "item": "https://retrocameraland.com"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://retrocameraland.com/blogs/retro-dijital-kamera"},
        {"@type": "ListItem", "position": 3, "name": post["title"], "item": url}]})
    return "\n".join('<script type="application/ld+json">' +
                     json.dumps(s, ensure_ascii=False).replace("</", "<\\/") + "</script>" for s in out)


def full_html(post):
    return CSS + '\n<div class="rcl-g">\n' + post["body"] + "\n</div>\n" + schemas(post) + "\n" + SOCIAL_BLOCK


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    posts = json.load(open(f"{SCRATCH}/yeni_bloglar.json", encoding="utf-8"))
    src = open("rcl-seo-blog-agent.py", encoding="utf-8").read().splitlines(keepends=True)
    ns = {"re": re}
    exec("".join(src[518:636]), ns)          # score_seo + AI_SLOP_PATTERNS

    for p in posts:
        if a.only and a.only not in p["handle"]:
            continue
        html = full_html(p)
        sc, det = ns["score_seo"](p["title"], p["meta"], html, p["kw"])
        words = len(re.sub(r"<[^>]+>", " ", p["body"]).split())
        bad = [d for d in det if d.startswith("✗")]
        print(f"  {p['handle'][:42]:<44} SEO {sc}/100 · {words} kelime"
              + (f"  ⚠ {bad}" if bad else ""))
        if a.apply:
            r = shopify("POST", f"blogs/{BLOG_ID}/articles.json", {"article": {
                "title": p["title"], "handle": p["handle"], "body_html": html,
                "tags": p["tags"], "published": True,
                "metafields": [
                    {"namespace": "global", "key": "title_tag", "value": p["title"], "type": "single_line_text_field"},
                    {"namespace": "global", "key": "description_tag", "value": p["meta"], "type": "single_line_text_field"}]}})
            print(f"      → {BASE}{r['article']['handle']}")
            time.sleep(0.4)


if __name__ == "__main__":
    main()
