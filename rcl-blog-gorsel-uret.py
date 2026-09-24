#!/usr/bin/env python3
"""
rcl-blog-gorsel-uret.py
Higgsfield Z Image ile blog kapak + yazı içi görselleri üretir, SEO dosya adıyla
Shopify'a yükler ve gövdeye yerleştirir.

Neden Z Image: 0.15 kredi/görsel (gpt_image_2 6.5, nano_banana_2_lite 1.0) ve
2048x1152 fotogerçekçi çıktı veriyor. Blog için 1200px (kapak) / 1024px (gövde)
JPEG'e indiriliyor — ~90-150 KB, Core Web Vitals dostu.

Kullanım:
  python3 rcl-blog-gorsel-uret.py --article 598555295883
  python3 rcl-blog-gorsel-uret.py --article dijital-kameradan-telefona-... --body 3
  python3 rcl-blog-gorsel-uret.py --son 5              # kapağı olmayan son 5 yazı
  python3 rcl-blog-gorsel-uret.py --article 123 --dry-run

Gereksinimler:
  - higgsfield CLI (auth login yapılmış)
  - Shopify token: kapak için write_content, GÖVDE görselleri için write_files
"""

import argparse, base64, json, os, re, subprocess, sys, tempfile, time
import urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retrocameraland_api as api
from retrocameraland_api import shopify, BLOG_ID

HF_MODEL = "z_image"
COVER_PX = 1200
BODY_PX  = 1024


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ── SEO dosya adı ────────────────────────────────────────────────────────────
TR_MAP = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")

def seo_filename(article_handle, slot, ext="jpg"):
    """SEO uyumlu dosya adı: makale-handle + slot eki, ASCII, tireli, <=90 kar."""
    base = f"{article_handle}-{slot}".translate(TR_MAP).lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:90].strip("-")
    return f"{base}.{ext}"


# ── Higgsfield ───────────────────────────────────────────────────────────────
def hf_generate(prompt, aspect="16:9", timeout=420):
    """Z Image ile üret, sonuç URL'ini döndür."""
    r = subprocess.run(
        ["higgsfield", "generate", "create", HF_MODEL,
         "--prompt", prompt, "--aspect_ratio", aspect, "--wait"],
        capture_output=True, text=True, timeout=timeout,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Higgsfield hata: {r.stderr.strip()[:200]}")
    urls = re.findall(r"https://\S+\.(?:png|jpg|jpeg|webp)", r.stdout)
    if not urls:
        raise RuntimeError(f"Higgsfield URL dondurmedi: {r.stdout.strip()[:200]}")
    return urls[-1]


def download_and_resize(url, out_path, max_px):
    """İndir → JPEG'e çevir + yeniden boyutlandır (sips, macOS yerleşik)."""
    raw = out_path + ".src"
    with urllib.request.urlopen(url, timeout=120) as r, open(raw, "wb") as f:
        f.write(r.read())
    subprocess.run(["sips", "-s", "format", "jpeg", "-Z", str(max_px),
                    "-s", "formatOptions", "85", raw, "--out", out_path],
                   capture_output=True, check=True)
    os.remove(raw)
    return os.path.getsize(out_path)


# ── Shopify yükleme ──────────────────────────────────────────────────────────
def upload_cover(article_id, jpg_path, filename, alt):
    """Kapak görseli — write_content yeterli, dosya adı korunur."""
    b64 = base64.b64encode(open(jpg_path, "rb").read()).decode()
    r = shopify("PUT", f"blogs/{BLOG_ID}/articles/{article_id}.json",
                {"article": {"id": article_id,
                             "image": {"attachment": b64, "filename": filename, "alt": alt}}})
    return r["article"]["image"]["src"]


def upload_file(jpg_path, filename, alt):
    """Gövde görseli — Shopify Files (write_files gerekir), kalıcı CDN URL döner."""
    # 1) staged upload hedefi al
    q1 = """mutation($input:[StagedUploadInput!]!){ stagedUploadsCreate(input:$input){
      stagedTargets{ url resourceUrl parameters{ name value } } userErrors{ message } } }"""
    v1 = {"input": [{"filename": filename, "mimeType": "image/jpeg",
                     "resource": "FILE", "httpMethod": "POST",
                     "fileSize": str(os.path.getsize(jpg_path))}]}
    d = _graphql(q1, v1)
    tgt = d["data"]["stagedUploadsCreate"]["stagedTargets"][0]

    # 2) dosyayı staged hedefe multipart POST et
    boundary = "----rclblog" + str(int(time.time() * 1000))
    body = b""
    for p in tgt["parameters"]:
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{p["name"]}"'
                 f'\r\n\r\n{p["value"]}\r\n').encode()
    body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
             f'filename="{filename}"\r\nContent-Type: image/jpeg\r\n\r\n').encode()
    body += open(jpg_path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(tgt["url"], data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    urllib.request.urlopen(req, timeout=120).read()

    # 3) Files'a kaydet
    q2 = """mutation($files:[FileCreateInput!]!){ fileCreate(files:$files){
      files{ id fileStatus ... on MediaImage { image { url width height } } }
      userErrors{ field message } } }"""
    v2 = {"files": [{"originalSource": tgt["resourceUrl"], "contentType": "IMAGE",
                     "filename": filename, "alt": alt}]}
    d = _graphql(q2, v2)
    errs = d["data"]["fileCreate"]["userErrors"]
    if errs:
        raise RuntimeError(f"fileCreate: {errs}")
    fid = d["data"]["fileCreate"]["files"][0]["id"]

    # 4) işlenmesini bekle (READY olunca url gelir)
    q3 = """query($id:ID!){ node(id:$id){ ... on MediaImage {
      fileStatus image { url width height } } } }"""
    for _ in range(30):
        time.sleep(2)
        n = _graphql(q3, {"id": fid})["data"]["node"]
        if n and n.get("fileStatus") == "READY" and (n.get("image") or {}).get("url"):
            return n["image"]["url"]
    raise TimeoutError(f"Dosya READY olmadi: {filename}")


def _graphql(query, variables):
    req = urllib.request.Request(
        f"https://{api.SHOPIFY_STORE}/admin/api/2026-07/graphql.json",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"X-Shopify-Access-Token": api.SHOPIFY_TOKEN,
                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if d.get("errors"):
        raise RuntimeError(str(d["errors"])[:300])
    return d


# ── Prompt üretimi ───────────────────────────────────────────────────────────
STYLE = ("Photorealistic, soft natural window light, shallow depth of field, "
         "warm neutral tones, clean minimal styling, no text, no logos, "
         "no readable brand names, sharp detail, lifestyle product photography")

BODY_ANGLES = [
    "macro close-up of hands using the subject on a light wooden desk",
    "overhead flat lay of the subject with related accessories neatly arranged",
    "candid lifestyle scene, a person using the subject near a cafe window",
    "three-quarter product shot of the subject on a neutral surface",
]

def cover_prompt(title):
    return (f"Editorial hero image for an article about: {title}. "
            f"A 2000s silver compact digital camera as the main subject with relevant "
            f"accessories on a light oak desk. {STYLE}")

def body_prompt(title, i):
    return (f"Image for a section of an article about: {title}. "
            f"{BODY_ANGLES[i % len(BODY_ANGLES)]}. {STYLE}")


# ── Gövdeye yerleştirme ──────────────────────────────────────────────────────
def figure_html(src, alt, width=BODY_PX):
    return (f'\n<figure style="margin:36px 0;">'
            f'<img src="{src}&width={width}" alt="{alt}" width="{width}" height="{int(width*9/16)}" '
            f'loading="lazy" style="width:100%;height:auto;border-radius:12px;display:block;">'
            f'</figure>\n')


def insert_images(body_html, images):
    """Görselleri H2'ler arasına dengeli dağıtarak yerleştirir (ilk H2 hariç)."""
    h2s = [m.start() for m in re.finditer(r"<h2[^>]*>", body_html, re.I)]
    if len(h2s) < 2 or not images:
        return body_html + "".join(figure_html(s, a) for s, a in images)
    # ilk H2'yi atla, kalanları eşit aralıklarla seç
    spots = h2s[1:]
    step = max(1, len(spots) // len(images))
    chosen = [spots[min(i * step, len(spots) - 1)] for i in range(len(images))]
    for pos, (src, alt) in sorted(zip(chosen, images), reverse=True):
        body_html = body_html[:pos] + figure_html(src, alt) + body_html[pos:]
    return body_html


# ── Ana akış ─────────────────────────────────────────────────────────────────
def get_article(ref):
    if str(ref).isdigit():
        return shopify("GET", f"blogs/{BLOG_ID}/articles/{ref}.json")["article"]
    d = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,handle,image")
    for a in d["articles"]:
        if a["handle"] == ref:
            return shopify("GET", f"blogs/{BLOG_ID}/articles/{a['id']}.json")["article"]
    raise SystemExit(f"Makale bulunamadi: {ref}")


def process(article, n_body, dry_run, skip_cover=False):
    aid, title, handle = article["id"], article["title"], article["handle"]
    log(f"── {title[:65]}")
    tmp = tempfile.mkdtemp(prefix="rclimg_")

    if not skip_cover:
        fn = seo_filename(handle, "kapak")
        alt = f"{title} - kapak görseli"
        log(f"  kapak üretiliyor...")
        if dry_run:
            log(f"    [dry-run] {fn} ← {cover_prompt(title)[:70]}...")
        else:
            u = hf_generate(cover_prompt(title))
            p = os.path.join(tmp, fn)
            kb = download_and_resize(u, p, COVER_PX) // 1024
            src = upload_cover(aid, p, fn, alt)
            log(f"    ✓ {fn} ({kb} KB) → {src.split('/')[-1][:50]}")

    if n_body:
        log(f"  {n_body} gövde görseli üretiliyor...")
        images = []
        for i in range(n_body):
            fn = seo_filename(handle, f"gorsel-{i+1}")
            alt = f"{title} - görsel {i+1}"
            if dry_run:
                log(f"    [dry-run] {fn} ← {body_prompt(title, i)[:70]}...")
                continue
            u = hf_generate(body_prompt(title, i))
            p = os.path.join(tmp, fn)
            kb = download_and_resize(u, p, BODY_PX) // 1024
            src = upload_file(p, fn, alt)
            images.append((src, alt))
            log(f"    ✓ {fn} ({kb} KB)")
        if images:
            body = insert_images(article["body_html"], images)
            shopify("PUT", f"blogs/{BLOG_ID}/articles/{aid}.json",
                    {"article": {"id": aid, "body_html": body}})
            log(f"    ✓ {len(images)} görsel gövdeye yerleştirildi")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", help="makale id veya handle")
    ap.add_argument("--son", type=int, help="kapağı olmayan son N makale")
    ap.add_argument("--body", type=int, default=0, help="yazı içi görsel sayısı")
    ap.add_argument("--skip-cover", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.article:
        targets = [get_article(a.article)]
    elif a.son:
        d = shopify("GET", f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,handle,image")
        missing = [x for x in d["articles"] if not x.get("image")][: a.son]
        log(f"Kapağı olmayan {len(missing)} makale seçildi")
        targets = [get_article(x["id"]) for x in missing]
    else:
        raise SystemExit("--article veya --son gerekli")

    for art in targets:
        try:
            process(art, a.body, a.dry_run, a.skip_cover)
        except Exception as e:
            log(f"  ✗ HATA: {str(e)[:160]}")


if __name__ == "__main__":
    main()
