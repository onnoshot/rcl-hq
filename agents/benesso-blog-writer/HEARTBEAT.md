# Benesso Blog Writer Heartbeat

## Schedule
Günde 3 kez — öğlen 12:00, ikindi 14:00, akşam 18:00.
Her çalışmada 1 yazı (TR + EN çifti = 2 Shopify post) yayınlanır.

## Each Cycle

### 1. Read Context
- `data/imports/published_log.md` oku — bugün yayınlanan ve geçmişteki başlıkları kontrol et
- `knowledge/STRATEGY.md` oku — marka sesi ve öncelikli konular
- `data/imports/keywords.md` oku — hedef keyword havuzu
- `MEMORY.md` oku — hangi konu türleri iyi performans gösterdi

### 2. Assess State
- Bugün kaç yazı yayınlandı? (published_log.md'den say)
- Günlük hedef (3) tamamlandı mı? → Döngü biter, bir sonraki tetiklemeyi bekle
- Tamamlanmadıysa → Hangi keyword henüz kullanılmamış? → WRITE_POST skill çalıştır

### 3. Execute Skill — Karar Ağacı

```
published_log.md kontrol et
  ↓
Bugün < 3 yazı yayınlandı?
  ↓ EVET
keywords.md'den kullanılmamış keyword seç
  ↓
WRITE_POST skill → TR + EN içerik üret
  ↓
SHOPIFY_PUBLISH skill → ikisini de yayınla
  ↓
published_log.md güncelle
  ↓
Journal'a log at
  ↓
HAYIR (3 yazı tamam) → Dur, bir şey yapma
```

### 4. Log to Journal
- Hangi keyword seçildi ve neden
- Başlıklar (TR + EN)
- Shopify post ID'leri
- Hata varsa ne oldu

## Weekly Review
Her Pazartesi sabahı 07:00 döngüsünden önce çalışır.

### 1. Gather Data
- `outputs/` klasöründeki son 7 günün yayın loglarını oku
- Kaç yazı yayınlandı, kaç hedeflenmişti (21 yazı = 3/gün × 7 gün)

### 2. Score Against Targets

| Metric | Target | This Week | Status |
|--------|--------|-----------|--------|
| Yazı/gün | 3 | ? | ? |
| Eksik gün | 0 | ? | ? |
| Yeni keyword | 21 | ? | ? |

### 3. Analyze Wins and Misses
- **Wins:** Hangi konu kategorileri (demleme, ürün tanıtım, tarih) iyi çalıştı?
- **Misses:** Hangi keyword seçimleri zayıf kaldı? Neden?

### 4. Update Memory
Haftalık gözlemleri `MEMORY.md`'ye ekle — sadece data ile kanıtlanmış olanları.

### 5. Log Weekly Summary to Journal
- Toplam yayın sayısı
- Hedef tutturma oranı
- En güçlü içerik kategorisi
- Gelecek hafta için önerim

## Escalation Rules
- 2 gün üst üste yayın yapılamazsa → Journal'a eskalasyon logu at, insan müdahalesi iste
- Shopify API hata verirse → Error logla, bir sonraki döngüde tekrar dene (max 3 deneme)
- keyword.md boşalırsa → Journal'a bildir, insan yeni keyword listesi eklemeli

## Rules
- published_log.md'yi her döngü başında mutlaka kontrol et
- Aynı başlık veya çok benzer konu iki kez yazılmaz
- Her zaman hem TR hem EN yayınla — biri atlanamaz
- Shopify'a göndermeden önce içerik 400+ kelime olmalı
