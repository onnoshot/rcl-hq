# Retrocameraland Analytics Agent — Heartbeat

## Schedule
- **Günlük veri güncelleme:** Her gün 09:00 (LaunchAgent: com.retrocameraland.analytics)
- **Haftalık trend raporu:** Her Pazartesi, günlük döngüden sonra
- **Aylık derinlemeli analiz:** Ayın ilk Salı günü

## Setup (İlk Kurulum)

### 1. Google Cloud & GA4 API Kurulumu
```
1. console.cloud.google.com → yeni proje oluştur
2. APIs & Services → "Google Analytics Data API" aktif et
3. IAM & Admin → Service Accounts → yeni service account oluştur
4. Service account → Keys → JSON key indir
5. İndirilen JSON'u: agents/retrocameraland-analytics/data/imports/ga_credentials.json olarak kaydet
6. GA4 Admin → Property Access Management → service account email'ini "Viewer" olarak ekle
7. GA4 Property ID'yi öğren (Admin → Property Settings → Property ID)
```

### 2. Config Dosyası Oluştur
`agents/retrocameraland-analytics/data/imports/ga_config.json` dosyasına yaz:
```json
{
  "property_id": "YOUR_GA4_PROPERTY_ID"
}
```

### 3. Python Kütüphanelerini Kur
```bash
pip3 install google-analytics-data google-auth
```

### 4. LaunchAgent Kur
```bash
cp agents/retrocameraland-analytics/scripts/com.retrocameraland.analytics.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.retrocameraland.analytics.plist
```

---

## Each Cycle (Günlük)

### 1. Read Context
- `journal/` içindeki son 2 girişi oku
- `knowledge/STRATEGY.md` oku — öncelikler değişti mi?
- Kendi `MEMORY.md` oku — geçmiş kalıplar

### 2. Fetch & Update
```bash
python3 agents/retrocameraland-analytics/scripts/fetch_and_update.py
```
Bu script:
- GA4 API'den son 7/30/90 günlük veriyi çeker
- `data/ga_data.json` dosyasını günceller
- `retrocameraland-analytics-dashboard.html` içindeki JS data bloğunu günceller

### 3. Analyze
GA_FETCH skill çıktısını oku:
- Dünün trafik rakamı normal mi? Spike veya düşüş var mı?
- Hangi sayfa/kaynak öne çıkıyor?
- Bounce rate eşiği aşıldı mı (>%70)?

### 4. Generate Insights
RECOMMENDATIONS skill'ini çalıştır:
- 3-5 madde halinde bu haftanın önerileri
- Anomali tespit edildiyse acil tespit notu

### 5. Log
`outputs/YYYY-MM-DD_analytics-report.md` oluştur ve journal'a giriş yaz.

---

## Weekly Review (Pazartesi)

### 1. Gather
- Son 7 günlük `data/ga_data.json` geçmişini oku
- Geçen haftayla kıyasla (MEMORY.md'den baseline al)

### 2. Score

| Metric | Target | Bu Hafta | Durum |
|--------|--------|----------|-------|
| Günlük ort. oturum | Büyüme trendi | ? | — |
| Organik trafik payı | >%50 | ? | — |
| Bounce rate | <%60 | ? | — |
| Top performing sayfa | Takip | ? | — |

### 3. Update Memory
Geçen haftayla kıyasla ve MEMORY.md'yi güncelle.

### 4. Log
`outputs/YYYY-MM-DD_weekly-trend.md` oluştur.

---

## Escalation Rules
- Trafik %40'ın üzerinde günlük düşüş → journal'a acil not
- Bounce rate 3 gün üst üste >%80 → insana bildir
- GA4 API erişimi başarısız olursa → hata logunu `outputs/` klasörüne yaz
- Organik trafik 2 hafta üst üste geriliyor → content agent'a sinyal ver
