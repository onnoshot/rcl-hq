#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCL Kamerani Sat - ASCII-safe Shopify section builder.

Shopify editorune yapistirilan Turkce liquid cift-kodlanir. Bu script
source.liquid icindeki tum non-ASCII karakterleri baglama gore escape eder:
  - <script>...</script> ve {% schema %}...{% endschema %} icinde -> \\uXXXX
  - geri kalan (HTML/Liquid metni) -> &#NNNN;
Cikti: kamera-sat.liquid  (Shopify editorune dogrudan yapistirilabilir)
"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'source.liquid')
OUT = os.path.join(HERE, 'kamera-sat.liquid')


def find_regions(text):
    """JS/schema bolgelerinin (start,end) araliklarini dondurur."""
    spans = []
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', text, re.DOTALL | re.IGNORECASE):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r'\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}', text, re.DOTALL):
        spans.append((m.start(), m.end()))
    spans.sort()
    return spans


def esc_html(s):
    return ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s)


def esc_js(s):
    out = []
    for c in s:
        o = ord(c)
        if o < 128:
            out.append(c)
        elif o <= 0xFFFF:
            out.append('\\u%04x' % o)
        else:  # astral plane -> surrogate pair
            o -= 0x10000
            out.append('\\u%04x\\u%04x' % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return ''.join(out)


def build(text):
    spans = find_regions(text)
    result = []
    pos = 0
    for start, end in spans:
        result.append(esc_html(text[pos:start]))   # HTML disinda
        result.append(esc_js(text[start:end]))      # JS/schema icinde
        pos = end
    result.append(esc_html(text[pos:]))
    return ''.join(result)


def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        src = f.read()
    out = build(src)
    # guvenlik: ciktida hic non-ASCII kalmamali
    bad = [(i, repr(ch)) for i, ch in enumerate(out) if ord(ch) > 127]
    if bad:
        print('UYARI: %d non-ASCII karakter kaldi: %s' % (len(bad), bad[:5]), file=sys.stderr)
    with open(OUT, 'w', encoding='ascii') as f:
        f.write(out)
    print('OK -> %s (%d byte, %d non-ASCII)' % (OUT, len(out), len(bad)))


if __name__ == '__main__':
    main()
