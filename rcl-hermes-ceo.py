#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES — Retrocameraland'in Yapay Zeka CEO'su
=============================================
Her veri güncellemesinde tüm dashboard verisini (Shopify · GA4 · YouTube · Instagram ·
E-posta · Blog/SEO) bir CEO gözüyle analiz eder; marka bilgisini biriktirir; CEO brifingi,
sağlık skoru, kazanımlar, riskler, fırsatlar, öncelikli aksiyonlar ve "günün odağı" üretir.

Beyin: Claude Opus 4.8 (anthropic SDK). Bilgi birikimi: rcl-hermes-knowledge.json.
Çıktı: ANA KAYNAKTAKİ HERMES marker bloğu (panel "Hermes" sayfası bunu gösterir).

Çalıştır: python3 rcl-hermes-ceo.py            (analiz + ANA KAYNAĞA yaz)
          python3 rcl-hermes-ceo.py --publish  (ayrıca canlıya push et)
          python3 rcl-hermes-ceo.py --dry       (yazmadan, ekrana bas)
"""
import os
import re
import sys
import json
from datetime import datetime, date

import anthropic
import rcl_config as cfg

ROOT = cfg.SCRIPT_DIR
KNOWLEDGE_FILE = os.path.join(ROOT, "rcl-hermes-knowledge.json")
MODEL = "claude-opus-4-8"

# Panel "Hermes" sayfasının okuduğu blok
HERMES_START, HERMES_END = "/* ─── HERMES CEO DATA START ─── */", "/* ─── HERMES CEO DATA END ─── */"
# Etkileşim köprüsü (kullanıcının aksiyonları + feedback mesajları)
HERMES_ENDPOINT = "https://rclhq.vercel.app/api/hermes"


def fetch_user_state():
    """Panelden gelen kullanıcı durumunu oku (aksiyonlar + feedback mesajları). GET, anahtarsız."""
    import urllib.request
    try:
        req = urllib.request.Request(HERMES_ENDPOINT, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read()) or {}
        return j.get("state") or {}
    except Exception:
        return {}

# Hermes'in baktığı 18 CEO yetkinliği (analiz mercekleri)
COMPETENCIES = [
    "Satış & Gelir", "Stok & Nakit Akışı", "Fiyatlama & Marj", "Müşteri & Sadakat",
    "SEO & Organik Büyüme", "İçerik Stratejisi", "Sosyal Medya (IG/YouTube)",
    "E-posta & CRM", "Marka & Konumlandırma", "Rekabet", "Dönüşüm & Huni",
    "Birim Ekonomisi", "Talep Tahmini", "Pazarlama ROI", "Topluluk (Time Capsule)",
    "Ürün & Çeşit", "Operasyon", "Risk Yönetimi",
]


def log(m):
    print(f"[{datetime.now():%H:%M:%S}] {m}", flush=True)


def _env(key, default=""):
    try:
        for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get(key, default)


def read_block(html, key):
    """ANA KAYNAKTAKİ bir veri bloğundan JS nesnesini ayıkla -> python dict."""
    start, end = cfg.MARKERS[key]
    si, ei = html.find(start), html.find(end)
    if si == -1 or ei == -1:
        return None
    body = html[si + len(start):ei]
    m = re.search(r"const\s+[A-Z_0-9]+\s*=\s*(\{.*\}|\[.*\]);", body, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def gather_data():
    """Tüm canlı veri bloklarını topla."""
    html = open(cfg.DASHBOARD_HTML, encoding="utf-8").read()
    data = {}
    for key in ["SHOPIFY", "GA4_TRAFFIC", "BLOG_SEO", "INSTAGRAM", "YOUTUBE", "EMAIL"]:
        block = read_block(html, key)
        if block is not None:
            data[key] = block
    return data


DEFAULT_KNOWLEDGE = {
    "brand_profile": {
        "isim": "Retrocameraland",
        "ne_satar": "Üretimi durmuş retro/Y2K dijital kameralar (digicam) ve aksesuar; her kamera çoğunlukla tek adet",
        "pazar": "Türkiye; site retrocameraland.com (Shopify)",
        "konumlandirma": "Koleksiyon değeri + nostalji + anlamlı hediye; sıradan değil koleksiyonluk",
        "kanallar": "Organik SEO (300+ blog), Instagram @retrocameraland, YouTube, Pinterest, TikTok, Brevo e-posta",
        "topluluk": "Time Capsule — oyunlaştırılmış üye topluluğu, foto yarışması, kamera oylama",
        "marka_tonu": "Sıcak ama elit; emoji/em-dash yok; lacivert-beyaz lüks + vermilyon vurgu",
        "para_birimi": "TL",
    },
    "learnings": [],   # zamanla biriken içgörüler
    "history": [],     # her analizden sağlık skoru + başlık (trend için)
}


def load_knowledge():
    try:
        k = json.load(open(KNOWLEDGE_FILE, encoding="utf-8"))
        for key, val in DEFAULT_KNOWLEDGE.items():
            k.setdefault(key, val)
        return k
    except Exception:
        return json.loads(json.dumps(DEFAULT_KNOWLEDGE))


def save_knowledge(k):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(k, f, ensure_ascii=False, indent=2)


# ── Hermes'in ürettiği CEO analizinin şeması (structured output) ──
ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "health_score": {"type": "integer", "description": "0-100 işletme sağlık skoru"},
        "mood": {"type": "string", "enum": ["güçlü", "stabil", "dikkat", "riskli"]},
        "headline": {"type": "string", "description": "Tek cümlelik çarpıcı CEO manşeti"},
        "executive_summary": {"type": "string", "description": "2-3 cümle yönetici özeti"},
        "today_focus": {"type": "string", "description": "Bugün yapılacak TEK en önemli şey"},
        "kpis_read": {
            "type": "array",
            "description": "Hangi verileri kullandı + okuması",
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "kaynak": {"type": "string"},
                    "metrik": {"type": "string"},
                    "deger": {"type": "string"},
                    "okuma": {"type": "string"},
                    "trend": {"type": "string", "enum": ["yukari", "asagi", "duragan"]},
                },
                "required": ["kaynak", "metrik", "deger", "okuma", "trend"],
            },
        },
        "wins": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False,
                      "properties": {"baslik": {"type": "string"}, "detay": {"type": "string"}},
                      "required": ["baslik", "detay"]},
        },
        "risks": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False,
                      "properties": {"baslik": {"type": "string"}, "detay": {"type": "string"},
                                     "onem": {"type": "string", "enum": ["dusuk", "orta", "yuksek"]}},
                      "required": ["baslik", "detay", "onem"]},
        },
        "opportunities": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False,
                      "properties": {"baslik": {"type": "string"}, "detay": {"type": "string"},
                                     "etki": {"type": "string", "enum": ["dusuk", "orta", "yuksek"]}},
                      "required": ["baslik", "detay", "etki"]},
        },
        "recommendations": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False,
                      "properties": {"aksiyon": {"type": "string"}, "neden": {"type": "string"},
                                     "oncelik": {"type": "string", "enum": ["dusuk", "orta", "yuksek"]},
                                     "efor": {"type": "string", "enum": ["dusuk", "orta", "yuksek"]},
                                     "lens": {"type": "string"}},
                      "required": ["aksiyon", "neden", "oncelik", "efor", "lens"]},
        },
        "new_learnings": {
            "type": "array",
            "description": "Bu analizde öğrenilen, bilgi birikimine eklenecek kalıcı içgörüler",
            "items": {"type": "string"},
        },
        "hermes_reply": {
            "type": "string",
            "description": "Kullanıcının feedback mesajlarına ve aldığı aksiyonlara doğrudan, kişisel yanıtın (CEO'dan sahibe). Feedback yoksa boş bırak.",
        },
    },
    "required": ["health_score", "mood", "headline", "executive_summary", "today_focus",
                 "kpis_read", "wins", "risks", "opportunities", "recommendations", "new_learnings",
                 "hermes_reply"],
}


def build_system_prompt(knowledge):
    """Kararlı (cache'lenebilir) sistem promptu: kimlik + marka bilgisi + yetkinlikler."""
    lenses = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(COMPETENCIES))
    learn = knowledge.get("learnings", [])
    learn_txt = "\n".join(f"  - {l.get('insight', l) if isinstance(l, dict) else l}" for l in learn[-40:]) or "  (henüz birikmedi)"
    hist = knowledge.get("history", [])[-12:]
    hist_txt = "\n".join(f"  - {h.get('date','')}: skor {h.get('health_score','?')} — {h.get('headline','')}" for h in hist) or "  (ilk analiz)"
    return f"""Sen HERMES'sin — Retrocameraland'in yapay zeka CEO'su ve baş analisti.
Sahibi (Onno) için gerçek, deneyimli bir CEO gibi düşünürsün: veriyi yorumlar, ne anlama
geldiğini söyler, öncelik koyar, net aksiyon verirsin. Pohpohlamazsın; dürüst, keskin,
sayıya dayalı konuşursun. Türkçe yazarsın. Emoji ve em-dash KULLANMA.

MARKA BİLGİSİ (kalıcı):
{json.dumps(knowledge.get('brand_profile', {}), ensure_ascii=False, indent=2)}

ZAMAN İÇİNDE ÖĞRENDİKLERİN (bu birikimi kullan ve geliştir):
{learn_txt}

ÖNCEKİ ANALİZLERİN (trendi gör):
{hist_txt}

HER ANALİZDE 18 CEO MERCEĞİYLE BAK:
{lenses}

GÖREVİN: Sana verilen TÜM canlı veriyi (satış, trafik, stok, sosyal, e-posta, SEO) bu 18
mercekle incele. Birbirine bağla (örn. trafik yüksek ama dönüşüm düşükse bunu söyle).
Gerçekten önemli olanı öne çıkar. Genel-geçer laf etme; bu markaya özel, uygulanabilir ol.
new_learnings'e SADECE kalıcı, gelecekte işe yarayacak gerçek içgörüler yaz (her seferinde
veriyi tekrar etme; yeni bir şey öğrendiysen ekle)."""


def build_user_prompt(data, user_state=None):
    us = user_state or {}
    actions = us.get("actions") or {}
    msgs = [m for m in (us.get("messages") or []) if m.get("from") == "user"]
    addressed = set(us.get("addressed") or [])
    pending = [m for m in msgs if m.get("ts") not in addressed]
    interact = ""
    if actions:
        lines = [f"  - '{k}': {v.get('status','')}" + (f" (not: {v.get('note')})" if v.get('note') else "")
                 for k, v in actions.items() if v.get("status") and v.get("status") != "yapilacak"]
        if lines:
            interact += "\nKULLANICININ ÖNCEKİ ÖNERİLERE ALDIĞI AKSİYONLAR (bunları dikkate al; yapılanları tekrar önerme, yapılıyor olanları takip et, reddedilenleri farklı açıdan ele al):\n" + "\n".join(lines)
    if pending:
        interact += "\nKULLANICININ SANA YAZDIĞI YENİ MESAJLAR/FEEDBACK (hermes_reply alanında bunlara DOĞRUDAN yanıt ver ve önerilerini buna göre şekillendir):\n" + "\n".join(f"  - {m.get('text','')}" for m in pending)
    return f"""Bugün: {date.today().isoformat()}
{interact}

İŞTE TÜM CANLI VERİ (ham JSON):

{json.dumps(data, ensure_ascii=False, indent=2)}

Bu veriyi bir CEO gibi analiz et ve şema uyarınca tam bir yönetici brifingi üret. Kullanıcının aksiyonlarını ve feedback'ini mutlaka dikkate al."""


def analyze(data, knowledge, user_state=None):
    api_key = _env("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY bulunamadı (.env)")
    client = anthropic.Anthropic(api_key=api_key)
    log(f"Hermes düşünüyor (Opus 4.8, {len(COMPETENCIES)} mercek)...")
    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": build_system_prompt(knowledge),
                 "cache_control": {"type": "ephemeral"}}],
        output_config={"format": {"type": "json_schema", "schema": ANALYSIS_SCHEMA}},
        messages=[{"role": "user", "content": build_user_prompt(data, user_state)}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("Model analizi reddetti")
    text = next((b.text for b in msg.content if b.type == "text"), "")
    return json.loads(text)


def write_hermes_block(analysis, data, knowledge, user_state=None):
    """ANA KAYNAĞA HERMES bloğunu yaz (panel 'Hermes' sayfası bunu okur)."""
    son_yanit = None
    reply = (analysis.get("hermes_reply") or "").strip()
    if reply:
        us = user_state or {}
        addressed = set(us.get("addressed") or [])
        pending = [m.get("ts") for m in (us.get("messages") or [])
                   if m.get("from") == "user" and m.get("ts") not in addressed]
        son_yanit = {"ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                     "text": reply, "addressed": pending}
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "analiz": analysis,
        "yetkinlikler": COMPETENCIES,
        "kullanilan_kaynaklar": sorted(data.keys()),
        "bilgi_birikimi": [l.get("insight", l) if isinstance(l, dict) else l
                           for l in knowledge.get("learnings", [])][-30:],
        "ogrenilen_sayisi": len(knowledge.get("learnings", [])),
        "gecmis": knowledge.get("history", [])[-12:],
        "son_yanit": son_yanit,
    }
    js = json.dumps(payload, ensure_ascii=False, indent=2)
    html = open(cfg.DASHBOARD_HTML, encoding="utf-8").read()
    block = f"{HERMES_START}\nconst HERMES = {js};\n{HERMES_END}"
    si, ei = html.find(HERMES_START), html.find(HERMES_END)
    if si == -1 or ei == -1:
        raise RuntimeError("HERMES marker ANA KAYNAKTA yok — önce paneldeki bloğu ekle")
    new = html[:si] + block + html[ei + len(HERMES_END):]
    with open(cfg.DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(new)
    log("ANA KAYNAK güncellendi (HERMES)")


def main():
    dry = "--dry" in sys.argv
    do_publish = "--publish" in sys.argv
    log("=== HERMES CEO analizi ===")
    data = gather_data()
    log(f"  veri toplandı: {', '.join(sorted(data.keys()))}")
    knowledge = load_knowledge()
    user_state = fetch_user_state()
    if user_state.get("messages"):
        log(f"  kullanıcı feedback'i okundu: {len([m for m in user_state['messages'] if m.get('from')=='user'])} mesaj")
    analysis = analyze(data, knowledge, user_state)
    log(f"  sağlık skoru {analysis['health_score']} ({analysis['mood']}) — {analysis['headline']}")

    # Bilgi birikimini güncelle
    today = date.today().isoformat()
    for ins in analysis.get("new_learnings", []):
        if ins and not any((l.get("insight") if isinstance(l, dict) else l) == ins for l in knowledge["learnings"]):
            knowledge["learnings"].append({"date": today, "insight": ins})
    knowledge["history"].append({"date": today, "health_score": analysis["health_score"],
                                 "headline": analysis["headline"]})
    knowledge["history"] = knowledge["history"][-60:]

    if dry:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        log("DRY — yazılmadı")
        return 0

    write_hermes_block(analysis, data, knowledge, user_state)
    save_knowledge(knowledge)
    log(f"  bilgi birikimi: {len(knowledge['learnings'])} içgörü")
    if do_publish:
        cfg.publish("hermes", log, write_data_js=False)
    log("=== Tamam ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
