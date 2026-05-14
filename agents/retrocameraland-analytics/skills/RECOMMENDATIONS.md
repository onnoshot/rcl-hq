# Skill: Tavsiye Üretimi

## Purpose
Analytics verisinden somut, uygulanabilir büyüme tavsiyeleri üretir.

## Trigger
- Haftalık analiz sonrası
- Anomali tespit edildiğinde
- Aylık derin analiz

## Input
- `data/ga_data.json` — ham veri
- `outputs/YYYY-MM-DD_analytics-report.md` — trafik analizi
- `knowledge/STRATEGY.md` — öncelikler
- `MEMORY.md` — geçmiş öğrenmeler

## Steps

### 1. Yüksek Fırsat Tespiti
Şu sorulara cevap ver:
- Hangi sayfa yüksek trafik ama yüksek bounce rate alıyor? → İçerik düzeltme fırsatı
- Hangi kanal yüksek session ama düşük süre getiriyor? → Kalite sorunu
- Hangi sayfa az trafik ama düşük bounce rate? → SEO ile büyütme fırsatı

### 2. Tavsiye Formatı
Her tavsiye şu yapıda olmalı:
```
**[Bulgu]** → [Tavsiye] → [Beklenen Etki]
```

Örnek:
```
**/urunler sayfası %72 bounce rate** → Ürün görselleri ve fiyat bilgisini üste taşı →
Beklenen etki: bounce rate'in <%55'e düşmesi, oturum süresinin artması
```

### 3. Önceliklendirme
Max 5 tavsiye. Önceliklendirme kriteri:
1. Etki büyüklüğü (trafik × potansiyel iyileşme)
2. Uygulama kolaylığı (içerik > teknik > tasarım)
3. Stratejiyle uyum (STRATEGY.md ile örtüşme)

### 4. Dashboard'a Yaz
Tavsiyeleri `retrocameraland-analytics-dashboard.html` içindeki `AI_INSIGHTS` bloğuna yaz.

## Output
- Rapor bölümü: `outputs/YYYY-MM-DD_analytics-report.md` içinde "## Tavsiyeler" başlığı
- Dashboard: `AI_INSIGHTS` JS değişkeni güncellenir
