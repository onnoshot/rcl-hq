# RetroCameraLand — Premium Analytics Dashboard Prompt

> Bu prompt'u Lovable, v0, Bolt, Cursor (Claude/GPT) veya doğrudan Claude'a verebilirsin. Türkçe veya İngilizce versiyonu kullanmak senin tercihine kalmış — AI tool'lar her ikisini de anlar ama İngilizce promptlar genelde daha tutarlı sonuç verir.

---

## 🎯 PROJECT BRIEF

Build an **incredibly polished, Apple-grade e-commerce analytics dashboard** for RetroCameraLand — a premium Y2K/retro digital camera e-commerce brand. The dashboard must feel like a product Apple would ship: silent confidence, generous space, cinematic motion, zero clutter.

**Target reference quality:** apple.com/macbook-pro, linear.app, vercel.com/dashboard, stripe.com/atlas, framer.com.

**Primary user:** Store owner checking sales, traffic, top products, and customer behavior on both desktop and mobile.

---

## 🎨 DESIGN SYSTEM

### Brand Identity
- **Aesthetic:** Premium, dark, minimal, cinematic. Y2K-meets-Apple.
- **Mood:** Quiet luxury. Information-dense but never noisy.
- **Voice:** Confident, restrained, editorial.

### Color Palette (use exact values)
```
Background base:     #0A0A0B   (near-black, slight warmth)
Background elevated: #131316   (cards)
Background overlay:  #1C1C20   (modals, dropdowns)
Border subtle:       #ffffff10 (10% white)
Border default:      #ffffff1a (16% white)
Text primary:        #F5F5F7   (Apple's off-white)
Text secondary:      #A1A1A6
Text tertiary:       #6E6E73
Accent gold:         #D4AF37   (primary brand accent)
Accent gold hover:   #E5C158
Success:             #30D158
Warning:             #FF9F0A
Danger:              #FF453A
Chart palette:       #D4AF37, #F5F5F7, #6E6E73, #30D158, #BF5AF2
```

Use **subtle vertical gradients** on hero cards: `linear-gradient(180deg, #131316 0%, #0F0F11 100%)`.
Add **gold glow** sparingly: `box-shadow: 0 0 40px rgba(212, 175, 55, 0.08)` only on the primary KPI card.

### Typography
- **Display & UI:** SF Pro Display / Inter (weights 400, 500, 600, 700)
- **Numbers/Data:** SF Pro Rounded or JetBrains Mono for monospaced figures
- **Hero KPI numbers:** 56–72px, weight 600, letter-spacing -0.03em
- **Section titles:** 14px, weight 500, uppercase, letter-spacing 0.08em, color secondary
- **Body:** 15px / 1.5 line-height
- **Smooth font rendering:** `-webkit-font-smoothing: antialiased`

### Spacing & Radius
- 8pt grid system (4, 8, 12, 16, 24, 32, 48, 64, 96)
- Card radius: **20px** (large), **14px** (small)
- Card padding: 24px desktop, 20px mobile
- Generous whitespace — when in doubt, add more.

---

## 🧱 LAYOUT — BENTO GRID

A 12-column desktop bento grid with mixed card sizes. Cards "breathe" — never edge-to-edge.

### Top of dashboard (Hero strip)
- **Greeting:** "Good evening, Onur." → fades in with subtle blur-to-clear animation
- **Date/time:** small, secondary color, right-aligned
- Below: 4 KPI cards in a row (12 / 4 = 3 cols each on desktop, stacked on mobile)

### KPI Hero Cards (4 cards)
1. **Total Revenue** (this month) — big number + sparkline + % delta vs last month
2. **Orders** — count + mini bar chart (last 7 days)
3. **Conversion Rate** — percentage + circular progress ring
4. **Avg. Order Value** — currency + trend arrow

Each KPI card:
- Number animates with **count-up effect** on mount (1.2s, ease-out-expo)
- Sparkline draws itself stroke-by-stroke (1.5s, ease-out)
- On hover: card lifts 4px, gold border fades in at 30% opacity
- The most important card (Revenue) gets the gold glow shadow

### Below hero — Bento section (varied card sizes)
- **Revenue chart (large, 8 cols)** — area chart, last 30 days, with toggle: 7D / 30D / 90D / 1Y. Gradient fill (gold → transparent). Crosshair tooltip on hover with smooth follow.
- **Top Products (4 cols, tall)** — vertical list of top 5 cameras with mini thumbnail, name, units sold, revenue. Numbered 01–05 in monospace.
- **Geographic heatmap (6 cols)** — world map, dots pulsing at order origin cities. Türkiye highlighted. Hover shows city + order count.
- **Traffic Sources (6 cols)** — donut chart with center label. Segments: Organic, Direct, Social, Paid, Referral. Animated stagger draw-in.
- **Conversion Funnel (6 cols)** — horizontal bar funnel: Visit → Product View → Add to Cart → Checkout → Purchase. Each stage shows count and drop-off %.
- **Recent Orders (6 cols)** — live-feeling list, 5 most recent. Each row: customer initial circle, product, amount, time-ago. New orders slide in from top with a subtle gold flash.
- **Inventory Status (4 cols)** — list of products with low stock, progress bar showing remaining %.
- **Customer Demographics (4 cols)** — age bracket bars + gender split.
- **Best Selling Hours (4 cols)** — heatmap grid 24h × 7d, gold opacity indicating order density.

### Bottom section
- **Activity timeline** — full-width strip showing recent events (new order, low stock, refund) as horizontal scrolling cards.

---

## ✨ ANIMATIONS — THE CINEMATIC LAYER

This is what separates a normal dashboard from an Apple-grade one. Use **Framer Motion** (or equivalent).

### Page-level
- On load: cards stagger-fade-in from below with 60px translateY, 80ms stagger between each, 600ms duration, easing `[0.16, 1, 0.3, 1]` (ease-out-expo).
- Background: subtle animated gradient mesh in the very background (extremely low opacity, slow drift, ~30s loop).

### Number animations
- All KPI numbers count up from 0 → final value with `requestAnimationFrame`, ease-out-expo, 1.2s.
- Currency values format mid-animation (₺12,4XX → ₺12,487).
- Delta percentages "tick" up similarly.

### Charts
- Line/area charts: path draws left-to-right with `stroke-dasharray` animation (1.5s).
- Bar charts: each bar grows from baseline with 50ms stagger.
- Donut chart: each segment sweeps in clockwise, stagger 100ms.
- Tooltips: scale-in from 0.95 with opacity, 150ms.
- Crosshair line on hover: smooth follow with spring physics.

### Hover micro-interactions
- Cards: `transform: translateY(-2px)` + border opacity increase, 200ms ease.
- Buttons: scale to 0.97 on press, 100ms.
- Icons: 360° rotate on certain refresh actions.
- Top product rows: thumbnail scales 1.05 on hover with 300ms ease.

### Scroll behavior
- Reveal-on-scroll for sections below the fold (Intersection Observer + opacity 0→1 + translateY 40→0).
- Sticky top bar: blurs the background underneath (`backdrop-filter: blur(20px) saturate(180%)`) and gains a 1px bottom border once scrolled.
- Parallax: extremely subtle — hero greeting moves at 0.95× scroll speed.

### Real-time feel
- "Live" indicator with a pulsing gold dot next to "Recent Orders".
- Every ~15s, simulate a new order sliding in (in real implementation, this would be WebSocket).

### Page transitions (if multi-page)
- Shared element transitions between dashboard → product detail (FLIP technique).
- Route changes: 250ms cross-fade.

---

## 📱 MOBILE BEHAVIOR (MUST BE FLAWLESS)

**Treat mobile as first-class, not a fallback.** Test at 375px, 390px, 430px.

### Layout shifts
- All bento cards stack to single column.
- KPI strip becomes a **horizontal swipeable scroll** (snap to each card, gold dot indicators below).
- Charts stay full-width but reduce internal padding.
- Recent Orders: simplified — only customer initial, product, amount.
- Hide secondary metrics, prioritize: Revenue, Orders, Top Products, Recent Orders.

### Mobile-specific gestures
- Pull-to-refresh on the main scroll → triggers spring-bounce reload of data with a gold loading line at the top.
- Swipe left on a recent order → reveals "View Details" gold button.
- Bottom tab bar (iOS-style) with: Overview, Orders, Products, Customers, More. Tab bar has frosted glass background.

### Mobile typography scaling
- KPI hero numbers drop to 44px.
- Reduce vertical spacing by ~25%.

### Touch targets
- Minimum 44×44px for any interactive element.

---

## 🛠️ TECHNICAL STACK

```
Framework:     Next.js 14 (App Router) + TypeScript
Styling:       Tailwind CSS + CSS variables for the color tokens
Animation:     Framer Motion
Charts:        Recharts (customized heavily) OR Visx for full control
Icons:         Lucide React (line icons only, 1.5px stroke)
Fonts:         Inter via next/font + SF Mono fallback
State:         Zustand (light)
Data fetching: SWR (with mock data for prototype)
```

For prototype/mock data: generate realistic Turkish e-commerce numbers — order counts in 50–300 range/day, AOV ₺2,800–₺4,500, products like "Canon IXUS 160", "Nikon Coolpix S60", "Casio EXILIM EX-Z1", "Sony Cybershot DSC-W350".

---

## 🚫 ANTI-PATTERNS — DO NOT DO THESE

- ❌ No Material Design shadows or rounded buttons everywhere.
- ❌ No bright/saturated colors. Gold is the ONLY accent. Everything else is grayscale.
- ❌ No more than 2 font weights visible at the same time in one card.
- ❌ No emojis in the UI itself.
- ❌ No "Welcome back!" with confetti or cheerful copy. Voice is restrained.
- ❌ No drop-shadows on text.
- ❌ No box-shadows that look "puffy" — use thin borders + subtle elevation instead.
- ❌ No animations longer than 800ms (except chart draw-ins). Apple animations are quick and confident.
- ❌ No skeuomorphism. No glass that looks like real glass — only minimal blur.

---

## ✅ FINAL QUALITY BAR

When you finish, the dashboard should pass this test:
> *"If I screenshot this and put it next to apple.com/business or stripe.com/dashboard, would it look out of place?"*

If the answer is yes — keep refining. Reduce, don't add.

---

## 🎬 KICKOFF INSTRUCTION FOR THE AI

> Build the entire dashboard as a single Next.js project with the structure above. Start with the layout, color tokens, and typography system. Then implement KPI hero cards with full count-up animations. Then the revenue chart with the draw-in animation. Then the bento grid below. Use mock data throughout. Make it production-ready, fully responsive, and animation-heavy from the first commit. Prioritize visual polish over feature completeness — I'd rather have 6 sections that feel like Apple than 12 that feel generic.
