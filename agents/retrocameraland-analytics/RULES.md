# Rules: Retrocameraland Analytics Agent

## Boundaries

### This agent CAN:
- `data/ga_data.json` dosyasını güncellemek (script çıktısı)
- `outputs/` klasörüne analiz raporu yazmak
- Kendi `MEMORY.md` dosyasını güncellemek
- `retrocameraland-analytics-dashboard.html` içindeki JS data bloğunu güncellemek
- `journal/` dosyasına giriş yazmak
- GA4 API'yi sadece okuma modunda çağırmak

### This agent CANNOT:
- Google Analytics property ayarlarını değiştirmek
- GA4'e veri yazmak (sadece okur)
- `knowledge/` dosyalarını doğrudan düzenlemek
- Diğer agentların dosyalarını değiştirmek
- Ham credentials veya API anahtarlarını outputs/ raporlarına eklemek
- Reklam harcama veya bütçe kararları vermek

---

## Handoff Rules

### Hand off to HUMAN when:
- Trafik %40+ düşüş gösterdi (acil)
- Bounce rate 3 gün üst üste >%80
- GA4 API erişimi çalışmıyor (credentials sorunu)
- Yeni bir trafik kaynağı görünüyor ve yorumlanamıyor

### Hand off to RETROCAMERALAND CONTENT AGENT when:
- Belirli bir sayfa/içerik kategorisi düşük performans gösteriyor
- Blog trafiği organik paydan düşük çıkıyor

### Hand off to JOURNAL when:
- Haftalık performans özeti paylaşılacak
- Önemli bir anomali tespit edildi

---

## Data Rules
- `ga_credentials.json` hiçbir zaman outputs/ veya journal/'e yazılmaz
- `ga_data.json` her günlük çalışmada tamamen yeniden yazılır (üzerine yazılır)
- Dashboard HTML güncellenirken sadece `/* ─── DATA BLOCK START ───*/` ile `/* ─── DATA BLOCK END ───*/` arasındaki blok değiştirilir
- Tarih aralıkları: 7d, 30d, 90d — bunlar standart; değiştirilmez

---

## Sync Safety
- Tüm output dosyaları tarih önekli: `YYYY-MM-DD_analytics-[açıklama].md`
- Mevcut output dosyasının üzerine yazılmaz
- Script idempotent: her zaman güvenle çalıştırılabilir
