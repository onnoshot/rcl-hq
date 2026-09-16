# DESIGN_SYSTEM — RCL HQ Dashboard "Apple Noir / Liquid Glass"

Tek statik HTML dosyası (`retrocameraland-hq-dashboard.html`), inline CSS + vanilla JS, Vercel.
React/Tailwind/Framer Motion YOK — tüm hareket saf CSS (`transition`, `@keyframes`, `backdrop-filter`, `cubic-bezier`) + vanilla JS ile. Tüm token'lar `:root`'a girer.

## 1. Tipografi
```css
--font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", system-ui, sans-serif;
--font-mono: "SF Mono", ui-monospace, "JetBrains Mono", Menlo, monospace;
```
| Rol | boyut | weight | line-height | letter-spacing |
|---|---|---|---|---|
| Display | 2.5rem | 700 | 1.05 | -0.02em |
| Sayfa başlığı | 1.5rem | 650 | 1.15 | -0.018em |
| Bölüm etiketi | 0.75rem | 600 | 1.3 | 0.04em (UPPERCASE) |
| Gövde | 0.9375rem | 450 | 1.5 | -0.006em |
| Nav öğesi | 0.84rem | 500 | 1.0 | -0.01em |
| Caption | 0.8125rem | 450 | 1.4 | 0 |
| Mono/sayı | 0.875rem | 500 | 1.4 | `font-variant-numeric: tabular-nums` |
Optik kural: başlık büyüdükçe tracking negatife, küçük caps etiketlerde pozitife.

## 2. Spacing & Radius
```css
--s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px; --s-5:20px; --s-6:24px; --s-8:32px;
--r-nav:10px; --r-button:10px; --r-card:16px; --r-modal:20px; --r-pill:999px;
```
Nav öğe padding `9px 12px`, ikon-yazı gap `11px`. Kart padding `20–24px`. Sidebar `248px` açık / `64px` kapalı.

## 3. Renk / Yüzey (koyu, 4 katman)
```css
--bg-base:#0A0A0C; --bg-sidebar:#0E0E11;
--bg-elev-1:rgba(255,255,255,0.03); --bg-elev-2:rgba(255,255,255,0.06);
--glass-bg:rgba(22,22,26,0.55); --glass-blur:blur(28px) saturate(180%); --glass-border:rgba(255,255,255,0.08);
--border-1:rgba(255,255,255,0.06); --border-2:rgba(255,255,255,0.12);
--text-1:rgba(255,255,255,0.92); --text-2:rgba(255,255,255,0.60); --text-3:rgba(255,255,255,0.38);
```
**Marka aksanı = vermilyon** (Apple mavisi değil, RCL kimliği): `--red:#FF453A`, `--accent-soft:rgba(255,69,58,0.15)`, `--accent-glow:rgba(255,69,58,0.45)`. Seçili durumda aksan = vermilyon.

## 4. Hareket Token'ları
```css
--ease-out:   cubic-bezier(0.22, 1, 0.36, 1);    /* hover, fade — Apple decel */
--ease-inout: cubic-bezier(0.4, 0, 0.2, 1);      /* sekme/sayfa geçişi */
--ease-spring:cubic-bezier(0.34, 1.56, 0.64, 1); /* ~%10 overshoot — basma bırakma, ikon */
--ease-snappy:cubic-bezier(0.32, 0.72, 0, 1);    /* sidebar collapse, drawer */
--dur-hover:140ms; --dur-press:90ms; --dur-tab:260ms; --dur-sidebar:340ms; --stagger:40ms;
```
Liste girişi stagger: `transition-delay: calc(var(--i) * var(--stagger))` (JS index `--i`).

## 5. Sidebar nav-item anatomisi
- **default**: `color:var(--text-2)`, ikon `--text-3`, stroke 1.75, 18px, 24-grid.
- **hover**: `background:var(--bg-elev-2)`, yazı/ikon `--text-1`, ikon `transform:scale(1.08)` (Dock hissi), `--dur-hover --ease-out`.
- **pressed**: `transform:scale(0.97)` `--dur-press`.
- **active/selected**: dolgu cam pill `background:var(--accent-soft)` + sol aksan çubuğu (`::before`, 3px, vermilyon, glow); ikon vermilyon. Çubuk `@keyframes navbar` ile açılır.
- **focus-visible**: 2px offset + 2px aksan ring (klavye).
- **collapse/expand**: `width` `--ease-snappy`/`--dur-sidebar`; label `opacity`+`translateX(-4px)`+`pointer-events` (display animasyonu YOK).

## 6. İkonlar
Tek set: **Lucide** (ISC≈MIT), inline SVG `<path>`, 24px grid, `stroke-width:1.75`, `stroke:currentColor`, `fill:none`, round cap/join. Runtime kütüphane yok (dosya self-contained kalsın). Tüm nav + kart ikonları aynı geometri/kalınlık.

## 7. Cam kart reçetesi
```css
.glass{position:relative;background:var(--glass-bg);backdrop-filter:var(--glass-blur);-webkit-backdrop-filter:var(--glass-blur);
  border:1px solid var(--glass-border);border-radius:var(--r-card);
  box-shadow:0 1px 0 rgba(255,255,255,.05) inset, 0 8px 32px rgba(0,0,0,.40), 0 1px 2px rgba(0,0,0,.30);}
.glass::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;
  background:linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,0) 40%);
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none;}
@supports not (backdrop-filter:blur(1px)){.glass{background:rgba(22,22,26,.92)}}
```
`mask-composite:xor` = üstte parlak, aşağı solan 1px specular kenar (visionOS hissi).

## 8. Açık kaynak referansları (permissive)
- **Lucide** (`lucide-icons/lucide`, ISC) — ikon geometrisi (24px/2px).
- **open-props** (`argyleink/open-props`, MIT) — easing token'ları (`--ease-out-3` = yukarıdaki `--ease-out`, elastic spring).
- **liquid-glass CSS demoları** (MIT) — `backdrop-filter blur()+saturate()` + inset sheen + masked-gradient border katmanı.

## Uygulama notu
Menü (FAZ 1) + bu token'lar `:root`'a uygulandı (2026-06-30). Sonraki: tüm ortak component'leri (.card/.glass, buton, input, tablo, modal) bu reçeteye getir; her sayfayı veri/boş/hata/loading state için doğrula; 320/768/1024/1440 mobil.

---

## Mobile (2026-06-30, gerçek-cihaz hissi)

Hedef: tek statik HTML, mobil Safari/Chrome, native uygulama hissi. Tüm değerler kütüphanesiz.

**1. Dokunma hedefleri:** min `44×44px` (iOS), tercih `48px`; görsel ikon küçükse padding ile kutuya tamamla. Tappable öğeler arası gap min `8px` (önerilen `12px`). İçerik kenar boşluğu `16px` (≥390px'de `20px`). Bottom-nav yüksekliği `56px` + safe-area. Tap-slop: `<10px` hareket = tap.

**2. Safe-area / çentik:** `<meta viewport ... viewport-fit=cover>`. Token: `--sa-t/-b/-l/-r: env(safe-area-inset-*,0px)`. Fixed header `padding-top:var(--sa-t)`; bottom-nav `height:calc(56px+var(--sa-b));padding-bottom:var(--sa-b)`; scroll alanı `padding-bottom:calc(56px+var(--sa-b)+16px)`.

**3. Gesture (vanilla JS):** swipe = mesafe `>60px` veya hız `>0.3px/ms`, süre `<500ms`, `|dx|>|dy|*1.5` (yatay kilit). touchstart/touchend delta. pull-to-refresh sadece `scrollTop===0`, bırakma `dy>70px`. long-press `setTimeout(500ms)`, `>10px` hareketle iptal. Okuma için `{passive:true}`.

**4. Bottom-nav:** 5 öğe + "Daha Fazla" sheet (`border-radius:20px 20px 0 0;max-height:80dvh`, swipe-down kapat, drag handle 36×5px). Tab `min-height:56px`, dikey ikon+etiket, etiket `10px`, ikon `24px`, aktif üst pill `32×3px` aksan. `:active{transform:scale(.92)}`.

**5. Mobil blur:** `backdrop-filter` fixed+scroll = iOS jank. Mobilde blur **≤10px** (`@media(max-width:768px)`), her zaman `-webkit-` çiftle, `transform:translateZ(0)` ile katman, `will-change` SADECE nav/header'da, scrollda full-viewport blur YOK. `@supports not` opak fallback.

**6. Hareket/haptik-hissi:** tap `100–150ms` `cubic-bezier(.2,0,0,1)`; press `:active{transform:scale(.96)}` (kart .97, ikon .92); `-webkit-overflow-scrolling:touch;overscroll-behavior:contain`; onay = 120ms scale 1→1.06→1 pulse; hata = 300ms 3x shake; `prefers-reduced-motion` korumalı.

**7. Breakpoint (mobile-first):** base 320 (tek kolon, bottom-nav, 15px) → 390 (gutter 20, 16px, 2-col stat) → 768 (2–3 col) → **1024 (bottom-nav→sidebar)** → 1440 (max içerik 1320px, 4-col). Grid `1→2→3→4`.

**8. Klavye:** `100vh` YASAK → `min-height:100svh;min-height:100dvh`. `visualViewport.resize` ile `--kb` hesapla, klavye açıkken bottom-nav'ı gizle/yukarı it.

**9. Açık kaynak:** davidfig/vanilla-gesture (MIT, swipe/long-press threshold), argab/swipe (MIT, fixedTimeout guard), SleepWalker swipe gist (eksen kilidi). Sadece desen/değer ödünç, kütüphane bağımlılığı yok.
