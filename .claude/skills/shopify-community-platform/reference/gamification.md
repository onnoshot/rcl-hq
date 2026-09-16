# Gamification & Community UX — design spec

## The engagement loop (Hooked model: trigger → action → variable reward → investment)

Two psychological levers do most of the work: **loss aversion** (a streak/standing you don't want to
abandon) and **variable reward** (an uncertain, shifting leaderboard is the slot-machine pull).

### Dual-cadence prize loop (the addictive-but-fair core)

| Cadence | Mechanic | Reward | Role |
|---|---|---|---|
| Daily | browse + vote up to N; keep a participation streak | XP / streak | habit trigger, low friction |
| **Weekly** | most-liked photo of the week | **1000 TL gift card** | frequent attainable reward; fresh zero every Monday keeps latecomers in |
| **Monthly** | most-liked photo of the month | **5000 TL gift card** | aspirational; drives the upload investment |
| Seasonal | monthly theme ("Şehir Işıkları", "Film'de Portre") | badge + homepage feature | kills blank-canvas friction, refreshes competition |

Why dual cadence: a single monthly prize decides the board early and latecomers disengage (the contest
death-spiral). The weekly reset gives everyone a fresh zero, so engagement stays flat-to-rising across the
month. This is exactly how Duolingo's weekly leagues stop "I'm too far behind" dropout.

UX glue that keeps mid-pack users invested: always show **"sen #14"** (your own rank), a top-3 podium with
the prize callout, and a countdown to weekly close (urgency = loss aversion).

## Badge taxonomy (camera-shop flavored — rename per brand)

Two axes come FREE from the Shopify customer object (no backend): tenure from `customer.created_at`,
purchases from `customer.orders_count`. A third axis is earned from contest behavior.

**Axis 1 — Tenure**
| Threshold | Name idea |
|---|---|
| 0–1 mo | Fresh Roll |
| 3 mo | Test Shots |
| 6 mo | First Development |
| 1 yr | Archivist |
| 2 yr | Master of the Darkroom |
| 3+ yr | Curator |

**Axis 2 — Purchases**
| Orders | Name idea |
|---|---|
| 1 | Collector |
| 3 | Enthusiast |
| 5 | Camera Hoarder |
| 10 | Vault Keeper |
| 20+ | Legendary Collector |

**Axis 3 — Achievement (high engagement)**
- Week Winner / Month Winner (gold, stackable counts)
- Featured (photo chosen for homepage hero)
- Sharpshooter (10+ uploads)
- Globetrotter (uploads from 5+ distinct locations — uses the required location field)
- Brand Loyalist: Sony / Canon / Nikon / Leica (most uploads of one make — uses the required camera field)
- Streak (N consecutive weeks participating)

## Anti-vote-fraud stack (ordered by strength)

1. **Identity gate** — only logged-in members vote (no anonymous/IP votes). Strongest shield by far.
2. `UNIQUE(photo_id, voter_id)` — one vote per member per photo (DB constraint, not IP limits).
3. **No self-vote** — block `voter_id == submitter_id` at API + DB trigger.
4. **Vote-velocity anomaly** — flag photos whose like-rate spikes with no correlated profile views; nightly
   query over `votes(photo_id, created_at)` → human review.
5. **Vote-ring / collusion** — graph check: a cluster that votes only for each other → flag.
6. **Eligibility freeze** — only members who joined before the contest started can vote in it (stops
   mid-contest account spinning).
7. **Human verification before issuing any gift card** — one Telegram tap per week.

If membership = "all registered" (not customers-only), lean harder on 4–7, since the order-history shield
from rule 1 is weaker.

## Mobile-first UX patterns

- **Feed:** masonry/justified grid (Behance/500px), lazy + infinite scroll, double-tap-to-like + persistent
  heart with live count. Tap → full-screen viewer with the metadata strip (camera model, location).
- **Upload (minimize friction):** pick/drag → instant preview → **exifr auto-fills camera model + location**
  (the two required fields) → theme tag + caption → submit → "inceleniyor" → appears after moderation.
- **Leaderboard:** Bu Hafta / Bu Ay tabs, top-3 podium + prize callout, sticky your-own-rank row.
- **Profile:** upload grid, badge shelf, tenure + order-count stats, auto "submission style" summary
  (most-used make + top location), total likes received.
- **Homepage/hero:** current theme + countdown to weekly close, animated featured-photo carousel of last
  week's top shots, live "X üye oy veriyor" social proof, single primary CTA "Fotoğrafını yükle".
  SF Pro, monochrome + minimal brand accent, scroll-revealed sections.
