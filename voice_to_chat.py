#!/usr/bin/env python3
"""
Sesli Yazı Asistanı — Türkçe ses tanıma  ·  ⌘⇧K ile tetiklenir
Sessizlik → otomatik metin dönüştürme → direkt yazma
"""
import os, sys, math, time, queue, threading, subprocess, wave, tempfile
import tkinter as tk
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from pynput.keyboard import Controller as KbController

_typer           = KbController()
RATE             = 16000
CH               = 1
W, H             = 510, 92
SPEECH_THRESHOLD = 600
SILENCE_AFTER    = 1.8
MIN_SPEECH_SECS  = 0.8

# ── Renk sistemi ─────────────────────────────────────────────────────────────
BG      = "#06080f"   # tam siyaha yakın lacivert
SURFACE = "#0c1120"   # yüzey kartı
BORDER  = "#182035"   # ince çerçeve
C_IDLE  = "#243050"   # pasif (dim mavi-gri)
C_WAIT  = "#4f72f5"   # bekleniyor  — mavi
C_SPEAK = "#9b59f7"   # konuşuyor   — mor
C_PROC  = "#f59e0b"   # işleniyor   — amber
C_DONE  = "#22d37a"   # tamamlandı  — yeşil
C_ERR   = "#ef4444"   # hata        — kırmızı
C_TEXT  = "#dce8ff"   # ana metin
C_DIM   = "#2a3a58"   # soluk ipucu

N_BARS  = 28
BAR_W   = 4
BAR_GAP = 3

mq         = queue.Queue()
recording  = False
frames     = []
recognizer = sr.Recognizer()

try:
    from pynput import keyboard as kb
except ImportError:
    sys.exit("pynput kurulu değil: pip3 install pynput")


# ── Gradient renk: mavi → mor → mavi ─────────────────────────────────────────
def _bar_color(i, n, active: bool) -> str:
    if not active:
        return C_IDLE
    t   = i / max(n - 1, 1)
    mid = 1.0 - abs(2 * t - 1)          # 0→kenar  1→merkez
    r   = int(79  + (168 - 79)  * mid)  # mavi.r → mor.r
    g   = int(110 + (85  - 110) * mid)  # mavi.g → mor.g
    b   = 247
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Rounded rectangle ─────────────────────────────────────────────────────────
def _rr(cv, x1, y1, x2, y2, r, **kw):
    pts = [
        x1+r, y1,   x2-r, y1,
        x2,   y1,   x2,   y1+r,
        x2,   y2-r, x2,   y2,
        x2-r, y2,   x1+r, y2,
        x1,   y2,   x1,   y2-r,
        x1,   y1+r, x1,   y1,
    ]
    return cv.create_polygon(pts, smooth=True, **kw)


# ── Overlay sınıfı ────────────────────────────────────────────────────────────
class Overlay:
    def __init__(self):
        self.win = tk.Tk()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)
        self.win.configure(bg=BG)

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{W}x{H}+{(sw - W) // 2}+{sh - 190}")

        cv = tk.Canvas(self.win, width=W, height=H, bg=BG, highlightthickness=0)
        cv.pack()
        self.cv = cv

        # Arka plan kartı
        _rr(cv, 0, 0, W, H, 18, fill=SURFACE, outline=BORDER, width=1)

        # Üst durum çizgisi
        self.accent = cv.create_line(18, 1, W - 18, 1, fill=C_IDLE, width=2)

        # Durum noktası (sol)
        DOT_CX, DOT_CY, DOT_R = 30, H // 2 - 8, 6
        self.dot_cx = DOT_CX
        self.dot_cy = DOT_CY
        self.dot_r0 = DOT_R
        self.dot = cv.create_oval(
            DOT_CX - DOT_R, DOT_CY - DOT_R,
            DOT_CX + DOT_R, DOT_CY + DOT_R,
            fill=C_IDLE, outline=""
        )
        self._pulsing = False

        # Ana etiket
        MX = W // 2 + 12
        self.lbl_main = cv.create_text(
            MX, 26,
            text="⌘⇧K  →  Konuşmaya başla",
            fill=C_DIM,
            font=("Helvetica Neue", 13, "bold"),
            anchor="center",
        )
        # Alt etiket
        self.lbl_sub = cv.create_text(
            MX, 43,
            text="Türkçe konuşun — durduğunuzda otomatik gönderilir",
            fill=C_DIM,
            font=("Helvetica Neue", 10),
            anchor="center",
        )

        # Waveform barları (merkez hizalı, yukarı + aşağı büyür)
        total = N_BARS * (BAR_W + BAR_GAP) - BAR_GAP
        sx    = (W - total) // 2 + 12
        self.bar_cy = H - 16
        self.bars   = []
        for i in range(N_BARS):
            bx = sx + i * (BAR_W + BAR_GAP)
            b  = cv.create_rectangle(bx, self.bar_cy - 2, bx + BAR_W, self.bar_cy + 2,
                                      fill=C_IDLE, outline="")
            self.bars.append((b, bx))

        # Sağ kısayol rozeti
        cv.create_text(W - 20, H // 2 - 8,
            text="⌘⇧K", fill=C_DIM,
            font=("Helvetica Neue", 8), anchor="center")

        self.tick  = 0
        self.state = "idle"
        self.front = ""
        self.win.withdraw()

    # ── İç yardımcılar ───────────────────────────────────────────────────────

    def _color(self, c):
        self.cv.itemconfig(self.accent, fill=c)
        self.cv.itemconfig(self.dot, fill=c)

    def _bars_flat(self, color=C_IDLE):
        for b, bx in self.bars:
            self.cv.coords(b, bx, self.bar_cy - 2, bx + BAR_W, self.bar_cy + 2)
            self.cv.itemconfig(b, fill=color)

    # ── Durumlar ──────────────────────────────────────────────────────────────

    def start_recording(self):
        self.state = "recording"
        self._color(C_WAIT)
        self.cv.itemconfig(self.lbl_main, text="Bekleniyor...",     fill=C_WAIT)
        self.cv.itemconfig(self.lbl_sub,  text="Konuşmaya başlayın", fill=C_DIM)
        self._bars_flat()
        self.win.deiconify()
        self._fade_in()
        self._start_pulse(C_WAIT)

    def start_processing(self):
        self.state = "processing"
        self._stop_pulse()
        self._color(C_PROC)
        self.cv.itemconfig(self.lbl_main, text="İşleniyor...",         fill=C_PROC)
        self.cv.itemconfig(self.lbl_sub,  text="Ses → metin dönüştürülüyor", fill=C_DIM)
        self._bars_flat(C_PROC)
        self._wave_anim()

    def show_done(self, text):
        self.state = "done"
        self._stop_pulse()
        self._color(C_DONE)
        short = (text[:36] + "…") if len(text) > 36 else text
        self.cv.itemconfig(self.lbl_main, text=f"✓  {short}", fill=C_DONE)
        self.cv.itemconfig(self.lbl_sub,  text="Yazıldı!",     fill=C_DONE)
        self._bars_flat(C_DONE)
        self.win.after(2200, self._dismiss)

    def show_error(self, msg):
        self.state = "error"
        self._stop_pulse()
        self._color(C_ERR)
        self.cv.itemconfig(self.lbl_main, text="✗  Hata",    fill=C_ERR)
        self.cv.itemconfig(self.lbl_sub,  text=msg[:56],     fill=C_DIM)
        self.win.after(4000, self._dismiss)

    # ── Waveform güncelleme ───────────────────────────────────────────────────

    def update_bars(self, rms, speech_started, silence_secs=0.0):
        if self.state != "recording":
            return
        self.tick += 1
        level  = min(rms / 2800.0, 1.0)
        center = (N_BARS - 1) / 2.0

        if speech_started:
            self._color(C_SPEAK)

        for i, (b, bx) in enumerate(self.bars):
            bell    = math.exp(-0.14 * (i - center) ** 2)
            shimmer = 0.6 + 0.4 * abs(math.sin(self.tick * 0.3 + i * 0.8))
            half_h  = int(2 + level * 26 * bell * shimmer) if speech_started else 2
            self.cv.coords(b, bx, self.bar_cy - half_h, bx + BAR_W, self.bar_cy + half_h)
            self.cv.itemconfig(b, fill=_bar_color(i, N_BARS, speech_started))

        if not speech_started:
            self.cv.itemconfig(self.lbl_main, text="Bekleniyor...",      fill=C_WAIT)
            self.cv.itemconfig(self.lbl_sub,  text="Konuşmaya başlayın", fill=C_DIM)
        elif silence_secs > 0.3:
            rem = max(0.0, SILENCE_AFTER - silence_secs)
            self.cv.itemconfig(self.lbl_main, text="Dinleniyor...", fill=C_SPEAK)
            self.cv.itemconfig(self.lbl_sub,
                text=f"Sessizlik — {rem:.0f}s sonra gönderiliyor", fill=C_DIM)
        else:
            self.cv.itemconfig(self.lbl_main, text="Dinleniyor...",            fill=C_SPEAK)
            self.cv.itemconfig(self.lbl_sub,  text="Durunca otomatik gönderilir", fill=C_DIM)

    # ── İşleme dalga animasyonu ───────────────────────────────────────────────

    def _wave_anim(self):
        if self.state != "processing":
            return
        self.tick += 1
        for i, (b, bx) in enumerate(self.bars):
            phase  = self.tick * 0.22 + i * 0.45
            half_h = int(2 + abs(math.sin(phase)) * 11)
            self.cv.coords(b, bx, self.bar_cy - half_h, bx + BAR_W, self.bar_cy + half_h)
        self.win.after(35, self._wave_anim)

    # ── Dot pulse animasyonu ──────────────────────────────────────────────────

    def _start_pulse(self, color):
        self._pulsing = True
        self._pulse(True, color, 0)

    def _stop_pulse(self):
        self._pulsing = False

    def _pulse(self, grow, color, step):
        if not self._pulsing:
            return
        t = step / 14.0
        r = self.dot_r0 + (2 if grow else -2) * math.sin(t * math.pi / 2)
        cx, cy = self.dot_cx, self.dot_cy
        self.cv.coords(self.dot, cx - r, cy - r, cx + r, cy + r)
        self.cv.itemconfig(self.dot, fill=color)
        step += 1
        if step >= 14:
            self.win.after(55, lambda: self._pulse(not grow, color, 0))
        else:
            self.win.after(22, lambda: self._pulse(grow, color, step))

    # ── Fade animasyonları ────────────────────────────────────────────────────

    def _fade_in(self, step=0.1, target=0.95):
        cur = self.win.attributes("-alpha")
        nxt = min(cur + step, target)
        self.win.attributes("-alpha", nxt)
        if nxt < target:
            self.win.after(13, lambda: self._fade_in(step, target))

    def _dismiss(self):
        self._stop_pulse()
        def _f():
            cur = self.win.attributes("-alpha")
            nxt = max(cur - 0.1, 0.0)
            self.win.attributes("-alpha", nxt)
            if nxt > 0.01:
                self.win.after(13, _f)
            else:
                self.win.withdraw()
                self.win.attributes("-alpha", 0.0)
        _f()

    def _paste_after_close(self, text, app):
        self.win.withdraw()
        self.win.attributes("-alpha", 0.0)
        threading.Thread(target=lambda: _do_paste(text, app), daemon=True).start()

    # ── Ana polling döngüsü ───────────────────────────────────────────────────

    def run(self):
        self.win.after(30, self._poll)
        self.win.mainloop()

    def _poll(self):
        global recording, frames
        try:
            while True:
                m = mq.get_nowait()

                if m == "toggle":
                    if not recording:
                        recording, frames = True, []
                        self.front = _frontmost()
                        self.start_recording()
                        threading.Thread(target=_record, daemon=True).start()
                    else:
                        recording = False
                        self.start_processing()
                        snap, front = list(frames), self.front
                        threading.Thread(target=_transcribe, args=(snap, front), daemon=True).start()

                elif m == "auto_stop":
                    if recording:
                        recording = False
                        self.start_processing()
                        snap, front = list(frames), self.front
                        threading.Thread(target=_transcribe, args=(snap, front), daemon=True).start()

                elif isinstance(m, tuple):
                    tag = m[0]
                    if tag == "level":
                        self.update_bars(m[1], m[2], m[3])
                    elif tag == "done":
                        text, app = m[1], m[2]
                        self.show_done(text)
                        self.win.after(350, lambda t=text, a=app: self._paste_after_close(t, a))
                    elif tag == "error":
                        self.show_error(m[1])

        except queue.Empty:
            pass
        self.win.after(30, self._poll)


# ── Ses kaydı ─────────────────────────────────────────────────────────────────
def _record():
    global recording, frames
    speech_started   = False
    first_sound_time = None
    last_sound       = None

    def cb(indata, n, t, s):
        nonlocal speech_started, first_sound_time, last_sound
        if not recording:
            return
        frames.append(indata.copy())
        rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
        if rms > SPEECH_THRESHOLD:
            if not speech_started:
                speech_started   = True
                first_sound_time = time.time()
                print(f"  [konuşma başladı, RMS={rms:.0f}]")
            last_sound = time.time()
        silence_secs = (time.time() - last_sound) if last_sound else 0.0
        mq.put(("level", rms, speech_started, silence_secs))

    with sd.InputStream(samplerate=RATE, channels=CH, dtype="int16", callback=cb):
        while recording:
            time.sleep(0.05)
            if speech_started and last_sound is not None:
                speech_dur   = last_sound - first_sound_time
                silence_secs = time.time() - last_sound
                if speech_dur >= MIN_SPEECH_SECS and silence_secs >= SILENCE_AFTER:
                    print(f"  [sessizlik tetiklendi, konuşma={speech_dur:.1f}s]")
                    mq.put("auto_stop")
                    recording = False
                    break


# ── Transkripsiyon ────────────────────────────────────────────────────────────
def _transcribe(snap, front_app):
    try:
        if not snap:
            mq.put(("error", "Ses kaydı boş — tekrar deneyin"))
            return
        audio = np.concatenate(snap).flatten()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(CH)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(audio.tobytes())
        print(f"  [ses: {len(audio)/RATE:.1f}s]")
        with sr.AudioFile(tmp.name) as source:
            audio_data = recognizer.record(source)
        os.unlink(tmp.name)
        text = recognizer.recognize_google(audio_data, language="tr-TR")
        print(f"  [transkripsiyon]: {text}")
        subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE).communicate(text.encode())
        mq.put(("done", text, front_app))
    except sr.UnknownValueError:
        mq.put(("error", "Ses anlaşılamadı — daha net konuşun"))
    except sr.RequestError as e:
        mq.put(("error", "Google bağlantı hatası — internet var mı?"))
    except Exception as e:
        mq.put(("error", str(e)[:56]))


# ── Yapıştırma ────────────────────────────────────────────────────────────────
def _do_paste(text, app):
    time.sleep(0.4)
    if app:
        subprocess.run(
            ["osascript", "-e", f'tell application "{app}" to activate'],
            capture_output=True
        )
        time.sleep(0.5)
    _typer.type(text)
    print(f"✓ Yazıldı: {text[:60]}")


def _frontmost() -> str:
    r = subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to get name of '
         'first application process whose frontmost is true'],
        capture_output=True, text=True
    )
    name = r.stdout.strip()
    print(f"  frontmost: '{name}'")
    return name


# ── Başlangıç ────────────────────────────────────────────────────────────────
def main():
    overlay = Overlay()

    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:
        pass

    hotkey = kb.HotKey(
        kb.HotKey.parse("<cmd>+<shift>+k"),
        lambda: mq.put("toggle")
    )

    def on_press(key):
        try: hotkey.press(key)
        except Exception: pass

    def on_release(key):
        try: hotkey.release(key)
        except Exception: pass

    listener = kb.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Sesli Yazı Asistanı  —  Türkçe  (Google)")
    print("  ⌘⇧K  →  başlat/durdur")
    print("  Sessizlikte otomatik gönderilir")
    print("  Çıkmak için: Ctrl+C")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    overlay.run()


if __name__ == "__main__":
    main()
