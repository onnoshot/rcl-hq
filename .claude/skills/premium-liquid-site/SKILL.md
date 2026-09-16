---
name: premium-liquid-site
description: Build award-grade, Apple/Liquid-Glass style marketing & portfolio websites from an existing brand or competitor site. Use when the user wants a "muhteşem / üst düzey / premium" website, wants to redesign an existing site, scrape its content/images, or asks for liquid-glass / Apple-minimal aesthetic with high-end animations and top-tier mobile. Covers research → asset scrape → design system → build → multi-viewport screenshot QA → deploy.
---

# Premium Liquid-Glass Site Builder

A repeatable playbook for producing a single self-contained, production-grade static site
(`index.html` + `css/styles.css` + `js/data.js` + `js/main.js` + `assets/`) with an
Apple-minimal, liquid-glass aesthetic, cinematic animations and flawless mobile.

Deploy target matches the user's existing pipeline: **static files → GitHub → Vercel**.

## Phase 1 — Research the source (don't guess the brand)
1. `WebFetch` the homepage for: nav links, hero media, sections, services, contact, socials, slogan.
2. `WebSearch` the brand name to learn what it actually *is* (people mislabel — verify before designing).
3. `WebFetch` every sub-page (about, services, portfolio list, each portfolio detail) for copy + image URLs.
4. `curl -s <url> -o /tmp/x.html` + `grep -oE` to pull raw asset URLs the markdown view hides
   (`\.mp4|\.webm`, `og:image`, `wp-content/uploads/...\.(webp|jpg|png)`). WordPress slider images
   are lazy-loaded — fetch each portfolio detail page individually to get the real gallery URLs.

## Phase 2 — Scrape all assets (idempotent)
- Write a `download-assets.sh` with a `dl(url,out)` helper that **skips if `-s "$out"`**, sends a real
  `User-Agent` + `Referer`, and counts ok/fail. Organize as `assets/projects/<slug>/{hero,1,2,...}.<ext>`.
- Always copy any user-provided local logo into `assets/brand/`.
- Verify with a node script that every path referenced in `data.js` exists (0 missing) before building.

## Phase 3 — Design system (tokens in `:root`)
- **Palette**: near-black canvas (`#070608`), one warm metal accent (gold `#cda873`), off-white text.
  Carry the brand's *existing* accent if it has one.
- **Type**: a serif display (Playfair Display) + a geometric grotesk (Space Grotesk). Big clamp() sizes.
- **Liquid glass**: `backdrop-filter:blur(22px) saturate(140%)`, 1px translucent borders, inset top
  highlight + deep drop shadow, animated blurred gradient orbs (`.aurora`) behind everything, subtle grain.
- **Motion**: `--ease:cubic-bezier(.22,1,.36,1)`. Preloader, scroll-reveal (IntersectionObserver, staggered
  `data-d`), hero Ken-Burns crossfade slider, animated stat counters, marquees, magnetic/shine buttons,
  card hover zoom, glass lightbox modal + fullscreen zoom, custom cursor (pointer:fine only), scroll
  progress bar, back-to-top. **Always** honor `prefers-reduced-motion`.

## Phase 4 — Build structure
Data-driven: keep all projects/refs/feed in `js/data.js` arrays so the gallery, filters, lightbox and
Instagram grid render from one source. Sections: preloader → glass nav (+ full-screen mobile menu) →
hero → trust marquee → stats → about → manifesto quote → process → services → filterable bento portfolio
(click → lightbox with description + gallery) → references marquee + cities → interactive Instagram grid →
video/CTA band → contact (glass form → `wa.me` / `mailto`) → footer. Add JSON-LD `ProfessionalService`,
OG tags, semantic headings.

## Phase 5 — Multi-viewport screenshot QA (the differentiator)
Headless Chrome can't scroll, and `100svh` hero fills any tall window, so:
1. Serve: `python3 -m http.server 8787 &`
2. Add a gated reveal fallback so crawlers/QA see content (`if(!("IntersectionObserver" in window))...`).
3. Capture at a **normal viewport height** (`--window-size=1440,900`) for the hero, and for full-page use a
   tall window only after temporarily capping the hero height — otherwise svh eats the page.
   `--headless --screenshot=out.png --virtual-time-budget=6000`.
4. Slice tall PNGs with PIL (`Image.crop`) into bands and `Read` each. Check mobile at `390` wide and the
   lightbox (position:fixed, so a 1440×1000 viewport shot shows it).
5. Validate JS with `node --check` for every script.

## Notes / gotchas
- No real hero video on most WP/RevSlider sites — recreate the "video" feel with a Ken-Burns crossfade
  image slider. Tell the user this explicitly.
- Instagram is JS-rendered/login-walled → can't scrape live posts. Build an *interactive showcase* grid
  from the brand's own project images + verified follower count + official profile link/embed.
- Keep everything self-contained and relative-pathed so it deploys to Vercel with zero config.

## Reference implementation
`nihat-yildiz-web/` in this repo is a complete worked example of this playbook.
