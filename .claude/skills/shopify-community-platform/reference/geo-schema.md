# GEO / SEO for UGC community pages (2026)

Structural advantage: AI engines disproportionately cite UGC/forums (Reddit ~49% of Google AI Overviews,
~46.7% of Perplexity top-10 sources). Your owned community can capture the same mechanics — IF it's
publicly indexed (login-gated content earns ~0 citations) and server-rendered.

## Crawler access (prerequisite — do first, in robots.txt.liquid)

Loop `robots.default_groups` and ADD rules (don't hardcode, preserve Shopify auto-updates). Explicitly
`Allow`: `OAI-SearchBot` (ChatGPT live cite), `PerplexityBot` + `Perplexity-User`, `ClaudeBot` +
`Claude-SearchBot` + `Claude-User`. Do NOT block `Googlebot` or `Google-Extended` (AI-Overviews token).
Ensure `/community/` + forum subdomain are crawlable. App-proxy pages aren't in Shopify's sitemap → host
your own and add a `Sitemap:` line.

## JSON-LD blocks (inject via Liquid; ESCAPE every UGC string with `| escape` / `| json`)

### Monthly contest — Event
```json
{"@context":"https://schema.org","@type":"Event",
 "name":"Haziran 2026 Aylık Analog Fotoğraf Yarışması",
 "description":"... Bu ayın teması: Şehir Işıkları. Kazanan topluluk oylamasıyla belirlenir; ödül 1000 TL hediye çeki.",
 "startDate":"2026-06-01T00:00:00+03:00","endDate":"2026-06-30T23:59:59+03:00",
 "eventStatus":"https://schema.org/EventScheduled",
 "eventAttendanceMode":"https://schema.org/OnlineEventAttendanceMode",
 "location":{"@type":"VirtualLocation","url":"https://retrocameraland.com/community/yarisma/2026-haziran"},
 "image":["https://retrocameraland.com/cdn/contest/2026-haziran.jpg"],"inLanguage":"tr",
 "organizer":{"@type":"Organization","name":"RetroCameraLand","url":"https://retrocameraland.com",
   "sameAs":["https://www.instagram.com/retrocameraland","https://www.youtube.com/@retrocameraland"]},
 "url":"https://retrocameraland.com/community/yarisma/2026-haziran"}
```

### Member profile — ProfilePage → Person
```json
{"@context":"https://schema.org","@type":"ProfilePage",
 "dateCreated":"2025-03-12T10:00:00+03:00","dateModified":"2026-06-25T14:00:00+03:00",
 "mainEntity":{"@type":"Person","name":"Mert Kaya","alternateName":"mertkaya","identifier":"user-4821",
   "description":"İstanbul merkezli analog film fotoğrafçısı",
   "image":"https://retrocameraland.com/cdn/avatars/mertkaya.jpg",
   "interactionStatistic":{"@type":"InteractionCounter","interactionType":"https://schema.org/FollowAction","userInteractionCount":215},
   "agentInteractionStatistic":{"@type":"InteractionCounter","interactionType":"https://schema.org/WriteAction","userInteractionCount":47}}}
```

### Member photo — ImageObject + creator
```json
{"@context":"https://schema.org","@type":"ImageObject",
 "contentUrl":"https://retrocameraland.com/cdn/photos/abc.jpg",
 "creator":{"@type":"Person","name":"Mert Kaya","url":"https://retrocameraland.com/community/profil/mertkaya"},
 "contentLocation":{"@type":"Place","name":"İstanbul, Türkiye"},
 "dateCreated":"2026-06-18","caption":"Canon AE-1 ile çekilmiş gece şehir fotoğrafı","inLanguage":"tr",
 "interactionStatistic":{"@type":"InteractionCounter","interactionType":"https://schema.org/LikeAction","userInteractionCount":34}}
```

### Forum thread — DiscussionForumPosting (Discourse emits this natively)
Required: `author.name`, `datePublished`, one of `text`/`image`/`video`. Recommended: nested `comment`,
`commentCount`, `interactionStatistic`. **2026 rule:** use `QAPage` ONLY for one-question/many-answers;
otherwise `DiscussionForumPosting`. New `digitalSourceType` flags AI-generated content (omit for human).

## Indexation hygiene (UGC at scale = index-bloat ranking risk)

- Self-referencing canonical on pages with genuine unique value (rich profile, captioned photo + metadata
  + comments, substantive thread).
- `noindex,follow` (not nofollow) on: empty/near-empty profiles, context-free single photos, thin threads,
  tag/filter/archive pages. Never canonicalize thread→parent or paginated→page1.
- `rel="ugc nofollow"` on user outbound links. `noindex` internal search/login/dashboards.
- Type-split sitemaps under an index (`profiles.xml`, `photos.xml`, `image.xml`), honest `<lastmod>` only
  (priority/changefreq ignored; false bumps waste crawl budget). Image sitemap may list CDN URLs.

## GEO editorial tactics (Princeton GEO study — measured gains)

Highest ROI: **cite reliable hyperlinked sources (+30–40%)**, **expert quotations (+30–40%)**,
**statistics/quantitative data (+30–40%)**. Keyword stuffing / padding = zero or negative. Plus:
answer-first first ~200 words, question-shaped Turkish H2/H3 matching real queries
("Canon AE-1 light seal nasıl değiştirilir?"), 50–150-word self-contained passages, FAQ + FAQPage,
first-hand experience language (model names, settings, before/after), honest `dateModified` freshness
(pages <30 days earn ~3.2x more citations — but never fake-bump), `inLanguage:"tr"` + hreflang,
`Organization` `sameAs` for entity clarity.

llms.txt: Shopify auto-generates `/llms.txt` + `/agents.md` natively since May 2026 (customize via
`llms.txt.liquid`). Ship it, but a ~300k-domain study found NO citation correlation — value is dev tooling,
not ranking.

## Performance (image-heavy feed)

INP is the top risk: optimistic UI on like buttons + `scheduler.yield()` before background writes. LCP:
`fetchpriority="high"` + AVIF/WebP + srcset on hero photo, never lazy it. CLS: explicit dims / locked
aspect ratios + `content-visibility:auto` on off-screen rows. Infinite scroll via IntersectionObserver
sentinel, not scroll events. Image alt auto-composed from the camera+location fields.
