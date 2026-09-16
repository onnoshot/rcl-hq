# Design — HMT CUP 2027

Locked design system. Every page redesign reads this before writing code. Amend
this file when the system needs to grow — don't invent per-page.

## Genre
Editorial-luxury-sport (custom, anchored on the existing brand red). Not
generic "Champions League poster" AI-editorial; closer to Nike/Jordan
campaign microsites and Apple product pages — rounded, airy, photography-led,
restrained motion.

## Macrostructure family
- Marketing/info pages (`/turnuva`, `/scout`, `/gelisim`, `/lig`, `/odul`):
  Marquee Hero (short, image-led) → alternating content blocks (never a rigid
  3-col grid every time) → CTA band.
- Home (`/`): Marquee Hero → teaser cards linking out to each page (not full
  content dumped on one page) → Haberdar Ol → footer.
- Gallery (`/galeri`): masonry-ish bento grid, own macrostructure.
- Content is split across real routes — no single-page scroll dump.

## Theme (custom, brand-anchored)
- `--color-paper` (dark base): `#0d0c0b` (warm near-black, not pure `#0a0a0a`)
- `--color-paper-2` (elevated surface): `#17140f`
- `--color-paper-3` (card surface): `#1e1a15`
- `--color-ink` (primary text on dark): `#f7f5f2` (warm off-white, not pure white)
- `--color-ink-dim`: `rgba(247,245,242,0.6)`
- `--color-rule` (hairlines): `rgba(247,245,242,0.10)`
- `--color-accent` (brand red): `#CC0000`
- `--color-accent-bright`: `#E82020`
- `--color-accent-dim`: `#8a1010`
- `--color-gold` (rare, prestige accent only): `#D4A843`
- `--color-focus`: `#E82020`

Accent discipline: red used for ≤5% of any viewport — CTAs, active states,
one accent line per section. Never full-bleed red backgrounds except tiny
badge chips.

## Typography
- Display + body: `-apple-system, BlinkMacSystemFont, "SF Pro Display",
  "SF Pro Text", "Inter", ui-sans-serif, sans-serif` — real SF Pro renders on
  Apple devices; Inter (via next/font) is the loaded web fallback everywhere
  else. No condensed poster caps (Bebas Neue removed).
- Weights: display 650–800, body 400–500, labels/eyebrows 600 uppercase
  tracked +0.08em.
- Headings are roman only — no italics.

## Spacing & radius
4pt scale via Tailwind. Radius tokens (the core "less AI, more premium" lever):
- `--radius-card`: 24px
- `--radius-media`: 20px
- `--radius-pill`: 999px (all buttons)
- `--radius-input`: 16px
- `--radius-chip`: 999px

## Motion
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (`--ease-out`) everywhere.
- Reveal: fade + 16px rise, staggered by 60-80ms in groups — not every element
  individually.
- Stat/infographic cards on `/lig`: animated count-up + subtle pulse, spring
  easing only there (contained, not global).
- `prefers-reduced-motion`: opacity-only ≤150ms.

## Microinteractions stance
- Buttons: pill shape, scale 0.98 on `:active`, no bounce/overshoot.
- Cards: hover = lift 4px + soft shadow, border brightens — no color swap.
- Popup: bottom-sheet on mobile (slide up, spring), centered modal on desktop
  (scale+fade). Dismiss via swipe-down (mobile) or backdrop click (desktop).

## CTA voice
- Primary: filled red pill, white text, uppercase tracked label.
- Secondary: outline pill, white/40% border.
- Never a sharp-cornered rectangle button anywhere in the app.

## Navigation (real mobile-app pattern)
- Mobile: fixed bottom tab bar, 5 destinations (Ana Sayfa · Turnuva · Galeri
  · Lig · İletişim), safe-area padded, active tab = filled icon + red dot.
  Scout & Gelişim reached via cross-links on Home/Turnuva, not buried in a
  hamburger — real apps don't hide destinations behind ≡ menus for a 7-page
  site.
- Desktop: floating glass pill nav, all 7 destinations + CTA.

## What pages MUST share
Logo, accent red + its ≤5% discipline, font stack, radius tokens, CTA pill
shape, section-heading rhythm (eyebrow label → heading, no numbered
left-margin tags), bottom-tab bar / glass nav chrome.

## What pages MAY differ on
Hero archetype (photo-led vs. stat-led vs. quote-led), section order, whether
a page uses the animated-card treatment (only `/lig` and stat rows).

## Honesty constraints (binding, not stylistic)
- No real club names/logos (Galatasaray/Fenerbahçe/Beşiktaş/Trabzonspor etc.)
  anywhere — no confirmed partnership exists. Use generic "Süper Lig
  kulüpleri" / "yurt içi ve yurt dışı scoutlar" language instead.
- `/lig` (fixtures/goal king/assists/replay) has no real data — the tournament
  hasn't happened. Frame every card as "Çok Yakında" / "Turnuva başladığında"
  — never fake a live scoreboard with invented numbers.
- Sports-psychology/development section uses a generic representative role
  ("Spor Psikoloğu"), never a fabricated real name/photo/credential.
- Tournament stats (team count etc.) stay marked as placeholder until the
  user confirms real numbers.

## Exports
Trimmed for this project: this app already has a working Tailwind v4 `@theme`
token block in `src/app/globals.css` — that file IS the tokens export. The
DTCG/shadcn/duplicate-tokens.css ritual is skipped as dead weight for a real
Next.js codebase (nothing else consumes those formats here).
