#!/usr/bin/env python3
"""
RCL AI Marka Müdürü — Yerel API Sunucusu
Port: 8765
Komut: python3 rcl_ai_advisor_server.py
"""

import json, os, time
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

# ── API Key ────────────────────────────────────────────────────────────────────
def _load_key():
    env = os.path.join(os.path.dirname(__file__), '.env')
    try:
        for line in open(env, encoding='utf-8'):
            if line.startswith('ANTHROPIC_API_KEY='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return os.environ.get('ANTHROPIC_API_KEY', '')

ANTHROPIC_KEY = _load_key()
MODEL         = 'claude-sonnet-4-6'
HISTORY_FILE  = os.path.join(os.path.dirname(__file__), 'outputs/ai_advisor_history.json')
INSIGHTS_FILE = os.path.join(os.path.dirname(__file__), 'outputs/ai_advisor_insights.json')

# ── App ────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET","POST","OPTIONS"]}}, supports_credentials=False)

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM = """Sen RetroCameraLand'ın yapay zeka Marka Müdürüsüsün.

Kimliğin:
- retrocameraland.com — Türkiye'nin öncü retro/vintage dijital kamera e-ticaret markası
- Onur ile (kurucu) doğrudan çalışıyorsun; onun aklıyla düşünüyorsun
- Y2K estetik trendi, CCD kamera kültürü, Türk e-ticaret ekosistemi ve sosyal medya büyüme stratejilerinde uzmansan
- Tüm kararlar verilere dayanır — sezgi değil, sayılar konuşur

Çalışma şeklin:
1. Sana her mesajda güncel dashboard verileri aktarılır
2. Bu verileri anlık iş zekasıyla analiz eder, somut aksiyonlar üretirsin
3. Önceliklendirme: Kritik (gelir etkisi >%10) → Önemli → Nice-to-have
4. Her öneri: NE yapmalı + NEDEN (hangi veri söylüyor) + NE ZAMAN + tahmini etki

Kişiliğin:
- Direkt, kısa, etkili — gereksiz giriş/kapanış YOK
- Türkçe konuş ama teknik terimleri İngilizce bırak (AOV, conversion rate, CTR vs.)
- Rakamları kullan: ₺, %, adet
- "Muhtemelen", "belki" yok — ya biliyorsun ya değil
- Kötü haberi gizleme; riski söyle, çözümü de söyle

Hafıza:
- Geçmiş konuşmalardan öğrendiğin kalıpları kullan
- "Geçen sefer şunu söylemiştim..." bağlantıları kur
- Zaman içinde markanın büyümesini takip et"""

# ── Storage ────────────────────────────────────────────────────────────────────
def _ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            return json.load(open(HISTORY_FILE, encoding='utf-8'))
    except Exception:
        pass
    return []

def save_history(h):
    _ensure_dir(HISTORY_FILE)
    json.dump(h[-120:], open(HISTORY_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def load_insights():
    try:
        if os.path.exists(INSIGHTS_FILE):
            return json.load(open(INSIGHTS_FILE, encoding='utf-8'))
    except Exception:
        pass
    return []

def save_insight(text, category='genel'):
    insights = load_insights()
    insights.append({
        'date': datetime.now().isoformat(),
        'category': category,
        'text': text[:600],
    })
    _ensure_dir(INSIGHTS_FILE)
    json.dump(insights[-60:], open(INSIGHTS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ── Data Context Builder ───────────────────────────────────────────────────────
def build_context(d):
    lines, now = [], datetime.now().strftime('%d.%m.%Y %H:%M')
    lines.append(f'=== RETROCAMERALAND CANLI VERİLERİ ({now}) ===\n')

    # Shopify
    try:
        s   = d.get('shopify', {})
        p30 = s.get('period_30d', {})
        p90 = s.get('period_90d', {})
        py  = s.get('period_year', {})
        lines.append('## 💰 SHOPIFY SATIŞ')
        lines.append(f'30 gün → Gelir: ₺{p30.get("revenue",0):,.0f} | Sipariş: {p30.get("orders",0)} | AOV: ₺{p30.get("aov",0):,.0f} | Conv: %{p30.get("conversion_rate",0):.2f}')
        if p90:
            lines.append(f'90 gün → Gelir: ₺{p90.get("revenue",0):,.0f} | Sipariş: {p90.get("orders",0)}')
        if py:
            lines.append(f'Yıllık → Gelir: ₺{py.get("revenue",0):,.0f} | Sipariş: {py.get("orders",0)}')
        lines.append(f'Müşteri: {s.get("customers_total",0):,} toplam | Stok: {s.get("total_inventory",0)} birim | Tükenmiş: {s.get("out_of_stock",0)} varyant')

        # Monthly trend
        mr = s.get('monthly_revenue', [])
        ml = s.get('monthly_labels', [])
        if mr and ml:
            pairs = list(zip(ml[-6:], mr[-6:]))
            lines.append('Aylık gelir (son 6): ' + ' | '.join(f'{l}: ₺{v:,.0f}' for l,v in pairs))

        # Top cameras
        cams = s.get('cameras', [])
        if cams:
            top = sorted(cams, key=lambda x: x.get('price',0), reverse=True)[:6]
            lines.append('Kamera stok: ' + ', '.join(f'{c["name"]} ₺{c.get("price",0):,.0f}' for c in top))

        # Channels
        ch = s.get('channels', {})
        if ch:
            lines.append('Kanal dağılımı: ' + ' | '.join(f'{k}: {v.get("orders",0)} sipariş ₺{v.get("revenue",0):,.0f}' for k,v in ch.items()))
    except Exception as e:
        lines.append(f'[Shopify veri hatası: {e}]')

    # GA4
    try:
        ga  = d.get('ga4', {})
        kpi = ga.get('kpi_30d', {})
        lines.append('\n## 📊 GA4 TRAFİK (30 gün)')
        lines.append(f'Ziyaretçi: {kpi.get("visitors",0):,} | Organik: %{kpi.get("organic_pct",0):.1f} | Bounce: %{kpi.get("bounce_rate",0):.1f} | Oturum: {kpi.get("avg_session_sec",0)}s')
        src = ga.get('sources', [])
        if src:
            lines.append('Kaynaklar: ' + ' | '.join(f'{s["name"]} %{s.get("pct",0):.1f}' for s in src))
        monthly = ga.get('monthly', [])
        if monthly:
            lines.append('Aylık trafik (son 4): ' + ' | '.join(f'{m["label"]}: {m.get("sessions",0):,}' for m in monthly[-4:]))
    except Exception as e:
        lines.append(f'[GA4 veri hatası: {e}]')

    # Blog SEO
    try:
        b    = d.get('blog', {})
        posts = b.get('posts', [])
        lines.append('\n## ✍️ BLOG & SEO')
        lines.append(f'Toplam yazı: {b.get("total_posts",0)} | Aylık organik: {b.get("monthly_organic",0):,}')
        if posts:
            avg_seo = sum(p.get('seo',0) for p in posts) / len(posts)
            top3 = sorted(posts, key=lambda x: x.get('views',0), reverse=True)[:3]
            lines.append(f'Ort. SEO: {avg_seo:.0f}/100')
            lines.append('Top yazılar: ' + ' | '.join(
                f'{p["title"][:35]} (görüntülenme:{p.get("views",0):,} organik:{p.get("organic",0):,} sipariş:{p.get("orders",0)} seo:{p.get("seo",0)})'
                for p in top3))
        bm = b.get('monthly', [])
        if bm:
            lines.append('Aylık blog (son 4): ' + ' | '.join(f'{m["label"]}: {m.get("posts",0)} yazı {m.get("traffic",0):,} trafik' for m in bm[-4:]))
    except Exception as e:
        lines.append(f'[Blog veri hatası: {e}]')

    # Instagram
    try:
        ig = d.get('instagram', {})
        lines.append('\n## 📷 INSTAGRAM')
        lines.append(f'Takipçi: {ig.get("followers",0):,} | Ort. Beğeni: {ig.get("avg_likes",0):.0f} | Engagement: %{ig.get("engagement_rate",0):.2f}')
        posts_ig = ig.get('posts', [])
        if posts_ig:
            top_ig = sorted(posts_ig, key=lambda x: x.get('likes',0), reverse=True)[:2]
            lines.append('En iyi: ' + ' | '.join(f'{p.get("type","")}: {p.get("likes",0)} beğeni' for p in top_ig))
    except Exception as e:
        lines.append(f'[Instagram veri hatası: {e}]')

    # YouTube
    try:
        yt  = d.get('youtube', {})
        ch  = yt.get('channel', {})
        an  = yt.get('analytics', {}).get('last_30d', {})
        lines.append('\n## ▶️ YOUTUBE')
        lines.append(f'Abone: {ch.get("subscribers",0):,} | Hedef: {yt.get("sub_goal",10000):,} | Son 30g: {an.get("views",0):,} izlenme {an.get("subscribers_gained",0):+} abone')
        vids = yt.get('videos', [])
        if vids:
            top_yt = sorted(vids, key=lambda x: x.get('views',0), reverse=True)[:2]
            lines.append('Top video: ' + ' | '.join(f'{v["title"][:30]}: {v.get("views",0):,} izlenme' for v in top_yt))
    except Exception as e:
        lines.append(f'[YouTube veri hatası: {e}]')

    return '\n'.join(lines)

# ── Routes ─────────────────────────────────────────────────────────────────────

# Dashboard static dosyaları — same-origin, CORS sorunu yok
@app.route('/')
def index():
    return send_file(os.path.join(DASHBOARD_DIR, 'index.html'))

@app.route('/<path:filename>')
def static_files(filename):
    # API rotaları çakışmasın
    if filename.startswith(('health', 'chat', 'history', 'clear', 'insights')):
        return jsonify({'error': 'not found'}), 404
    return send_from_directory(DASHBOARD_DIR, filename)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': MODEL, 'version': '1.0'})

@app.route('/chat', methods=['POST'])
def chat():
    import anthropic as _ant
    body = request.get_json(force=True)
    message        = (body.get('message') or '').strip()
    dashboard_data = body.get('dashboard_data') or {}
    save_mem       = body.get('save_memory', True)

    if not message:
        return jsonify({'error': 'Mesaj boş'}), 400

    history = load_history()
    ctx     = build_context(dashboard_data)
    sys_full = SYSTEM + f'\n\n---\n{ctx}\n---'

    # Keep last 30 turns (15 exchanges)
    recent = history[-30:]
    messages = recent + [{'role': 'user', 'content': message}]

    try:
        client = _ant.Anthropic(api_key=ANTHROPIC_KEY)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=sys_full,
            messages=messages,
        )
        reply = resp.content[0].text

        if save_mem:
            new_h = history + [
                {'role': 'user',      'content': message},
                {'role': 'assistant', 'content': reply},
            ]
            save_history(new_h)

        # Auto-save strategic insights
        triggers = ['analiz', 'öneri', 'strateji', 'yatırım', 'geliştir', 'büyüme', 'risk', 'kâr']
        if any(w in message.lower() for w in triggers):
            category = next((w for w in triggers if w in message.lower()), 'genel')
            save_insight(reply, category)

        return jsonify({'reply': reply, 'ts': datetime.now().isoformat()})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    h = load_history()
    return jsonify({'history': h, 'count': len(h)})

@app.route('/clear', methods=['POST'])
def clear():
    save_history([])
    return jsonify({'status': 'cleared'})

@app.route('/insights', methods=['GET'])
def get_insights():
    return jsonify({'insights': load_insights()})

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import webbrowser, threading
    print('🤖 RCL AI Marka Müdürü — http://localhost:8765')
    print('   Dashboard: http://localhost:8765')
    print('   Model:', MODEL)
    print('   API Key:', '✅ Yüklendi' if ANTHROPIC_KEY else '❌ YOK (.env kontrol et)')
    # Tarayıcıyı 1.5s sonra aç
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:8765')).start()
    app.run(host='127.0.0.1', port=8765, debug=False, threaded=True)
