#!/usr/bin/env python3
"""
Telegram bot — Groq (Llama 3.3 70B) ile konuşma
Sadece chat ID 7904534693'ten gelen mesajlara yanıt verir.
Komutlar: /reset — konuşma geçmişini sıfırla
"""

import json, re, time, logging, os
import requests
from groq import Groq

TG_TOKEN   = "8696617266:AAG34_ybLGuchVT2zrni8lUoJBbyPfD6DvQ"
TG_CHAT_ID = 7904534693
GROQ_KEY   = "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"
MODEL      = "llama-3.3-70b-versatile"
HISTORY_FILE = os.path.expanduser("~/.config/claude-bot/history.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.expanduser("~/Downloads/Agentlar/outputs/claude-telegram-bot.log")),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)

client = Groq(api_key=GROQ_KEY)

def load_history():
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def tg_send(text):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"},
        timeout=15,
    )

def tg_get_updates(offset):
    r = requests.get(
        f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates",
        params={"offset": offset, "timeout": 30, "allowed_updates": ["message"]},
        timeout=40,
    )
    return r.json().get("result", [])

SYSTEM_PROMPT = (
    "Sen yardımcı bir asistansın. Türkçe konuş. "
    "Yanıtlarını Telegram HTML formatıyla yaz: "
    "kalın için <b>metin</b>, italik için <i>metin</i>, kod için <code>metin</code>. "
    "Liste yaparken • veya 1. 2. 3. kullan; kesinlikle ** # __ gibi markdown işaretleri kullanma. "
    "Başlıkları <b>başlık</b> şeklinde yaz."
)

def md_to_html(text):
    # ```kod blokları```
    text = re.sub(r"```(?:\w+)?\n?(.*?)```", lambda m: f"<pre>{_esc(m.group(1).strip())}</pre>", text, flags=re.DOTALL)
    # `inline kod`
    text = re.sub(r"`([^`\n]+)`", lambda m: f"<code>{_esc(m.group(1))}</code>", text)
    # **kalın** veya __kalın__
    text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<b>{m.group(1) or m.group(2)}</b>", text)
    # *italik* veya _italik_  (tek yıldız/alt çizgi)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", lambda m: f"<i>{m.group(1) or m.group(2)}</i>", text)
    # ### Başlık satırları
    text = re.sub(r"^#{1,6}\s+(.+)$", lambda m: f"<b>{m.group(1)}</b>", text, flags=re.MULTILINE)
    return text

def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def ask_groq(history, user_msg):
    history.append({"role": "user", "content": user_msg})
    context = history[-20:]
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + context,
        max_tokens=1024,
    )
    reply = resp.choices[0].message.content
    reply = md_to_html(reply)
    history.append({"role": "assistant", "content": reply})
    return reply, history

def main():
    log.info("Bot başlatıldı.")
    tg_send("🤖 Bot aktif. Merhaba!")
    history = load_history()
    offset = 0

    while True:
        try:
            updates = tg_get_updates(offset)
        except Exception as e:
            log.warning(f"getUpdates hatası: {e}")
            time.sleep(5)
            continue

        for upd in updates:
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "").strip()

            if chat_id != TG_CHAT_ID or not text:
                continue

            log.info(f"Mesaj: {text[:80]}")

            if text == "/reset":
                history = []
                save_history(history)
                tg_send("Konuşma geçmişi sıfırlandı.")
                continue

            try:
                reply, history = ask_groq(history, text)
                save_history(history)
                tg_send(reply)
            except Exception as e:
                log.error(f"Groq hatası: {e}")
                tg_send(f"Hata oluştu: {e}")

if __name__ == "__main__":
    main()
