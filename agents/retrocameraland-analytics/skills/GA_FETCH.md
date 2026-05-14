# Skill: GA Verisi Çekme

## Purpose
GA4 API'den günlük trafik, kullanıcı ve davranış verilerini çeker.

## Trigger
- Günlük 09:00 (LaunchAgent)
- Manuel: `python3 agents/retrocameraland-analytics/scripts/fetch_and_update.py`

## Steps

### 1. Credentials Kontrolü
```python
# Gerekli dosyalar:
# - agents/retrocameraland-analytics/data/imports/ga_credentials.json
# - agents/retrocameraland-analytics/data/imports/ga_config.json
```
Eğer yoksa hata logla ve dur.

### 2. Çekilen Metrikler

| Metrik | Dimension | Dönem |
|--------|-----------|-------|
| sessions | date | son 90 gün (günlük seri) |
| activeUsers | date | son 90 gün |
| screenPageViews | date | son 90 gün |
| bounceRate | — | 7d, 30d, 90d özet |
| averageSessionDuration | — | 7d, 30d, 90d özet |
| sessions | sessionSource, sessionMedium | 30d |
| sessions, screenPageViews | pagePath | 30d (top 20) |
| sessions | deviceCategory | 30d |
| sessions | country | 30d (top 10) |

### 3. Çıktı
`agents/retrocameraland-analytics/data/ga_data.json` dosyasını oluştur/güncelle.

### 4. Dashboard Güncelleme
`retrocameraland-analytics-dashboard.html` içindeki data bloğunu güncelle.

## Error Handling
- API erişim hatası → `outputs/YYYY-MM-DD_ga-error.log` yaz
- Boş veri → önceki günün verisini koru, log yaz
- Credentials eksik → setup talimatlarını logla
