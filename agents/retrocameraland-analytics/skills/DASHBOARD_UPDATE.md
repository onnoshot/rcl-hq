# Skill: Dashboard Güncelleme

## Purpose
Günlük GA4 verisiyle `retrocameraland-analytics-dashboard.html` dosyasını günceller.

## Trigger
- Günlük fetch_and_update.py çalıştıktan sonra (otomatik)
- Manuel yenileme gerektiğinde

## Mechanism
Python scripti (`scripts/fetch_and_update.py`) şu bloğu değiştirir:

```html
/* ─── DATA BLOCK START ─── */
const GA_DATA = { ... };
/* ─── DATA BLOCK END ─── */
```

Bu blok dışındaki HTML/CSS/JS'ye dokunulmaz.

## Data Structure
```json
{
  "updated_at": "ISO timestamp",
  "period_7d":  { "sessions", "users", "pageviews", "bounceRate", "avgDuration" },
  "period_30d": { ... },
  "period_90d": { ... },
  "daily": [ {"date": "YYYYMMDD", "sessions": N}, ... ],
  "sources": [ {"name": "google / organic", "sessions": N, "pct": N}, ... ],
  "top_pages": [ {"path": "/...", "sessions": N, "pageviews": N, "bounceRate": N}, ... ],
  "devices": { "mobile": N, "desktop": N, "tablet": N },
  "countries": [ {"name": "Turkey", "sessions": N}, ... ],
  "ai_insights": "..."
}
```

## Verification
Scriptin başarıyla çalıştığını doğrula:
1. `data/ga_data.json` günün tarihiyle güncellendi mi?
2. Dashboard HTML'deki `updated_at` değeri bugünün tarihi mi?
3. Dashboard tarayıcıda açıldığında veri gösteriyor mu?
