# Skill: Trafik Analizi

## Purpose
GA4 verisini okuyarak trafik trendlerini, anomalileri ve kaynak dağılımını analiz eder.

## Trigger
- Günlük fetch sonrası (her döngü)
- Haftalık derin analiz (Pazartesi)

## Steps

### 1. Günlük Kontrol
`data/ga_data.json` oku:
- Dünün session sayısı vs. 7 günlük ortalaması
- %20'den fazla sapma varsa → anomali tespit et
- Hangi kaynak en çok trafik getirdi?

### 2. Trend Analizi (Haftalık)
- Bu hafta vs. geçen hafta karşılaştır (MEMORY.md'den baseline)
- Organik pay hesapla: `organic_sessions / total_sessions * 100`
- En hızlı büyüyen sayfa/kaynak belirle

### 3. Anomali Tespiti

| Durum | Eşik | Eylem |
|-------|------|-------|
| Trafik spike | +%100 tek günde | Log + journal notu |
| Trafik düşüşü | -%40 tek günde | Journal'a ACİL not |
| Bounce rate artışı | >%80 üç gün | İnsana bildir |
| Yeni kaynak | İlk kez görünüyor | Journal'a not |

### 4. SEO Sağlığı
- Organik trafik payı: hedef >%50
- Top landing page'ler organik mi?
- Direct trafik payı yüksekse: branded arama mı?

## Output Format
Bulgular `outputs/YYYY-MM-DD_analytics-report.md` içine yazılır.
Anomaliler `journal/YYYY-MM-DD_HHMM.md` içine de taşınır.
