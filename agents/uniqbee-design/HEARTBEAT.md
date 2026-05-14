# UniqBee Design Agent — Heartbeat

## Schedule
- **Talep bazlı:** Yeni müşteri brief'i geldiğinde anında çalışır.
- **Haftalık (Çarşamba):** Aktif projelerin durumunu değerlendirir, pipeline'ı günceller.
- **Aylık (her ayın 1'i):** Tüm çıktıları denetler, KPI'ları ölçer, hafızayı günceller.

## Each Cycle

### 1. Read Context
- `journal/` son 5 girişi oku — onaylanan/reddedilen çıktılar ve müşteri geri bildirimleri var mı?
- `knowledge/STRATEGY.md` oku — aktif müşteriler ve öncelikler değişti mi?
- Kendi `MEMORY.md`'yi oku — geçmişte öğrenilen kalıpları hatırla.
- `data/imports/` tara — yeni brief veya varlık dosyası bırakıldı mı?

### 2. Assess State
- Bekleyen brief var mı? → VISUAL_CONCEPT veya BRAND_IDENTITY skill'ini çalıştır.
- Marka kimliği hazır, kurumsal materyaller eksik mi? → CORPORATE_DESIGN skill'ini çalıştır.
- Sosyal medya içeriği istendi mi? → SOCIAL_MEDIA_DESIGN skill'ini çalıştır.
- Mevcut çıktılarda tutarsızlık şüphesi var mı? → DESIGN_AUDIT skill'ini çalıştır.
- Hiç aktif iş yok mu? → Hafıza güncelle ve journal'a log at.

### 3. Execute Skill
- **Yeni proje başlangıcı:** VISUAL_CONCEPT → BRAND_IDENTITY sırası
- **Devam eden proje:** CORPORATE_DESIGN veya SOCIAL_MEDIA_DESIGN
- **Revizyon talebi:** DESIGN_AUDIT → revize edilmiş skill çalıştır
- **Periyodik kontrol:** DESIGN_AUDIT

### 4. Log to Journal
- Bu döngüde ne yapıldı (hangi skill, hangi müşteri)
- Öne çıkan bulgular veya müşteri tercihleri
- Bir sonraki adım ne olmalı

## Weekly Review (Her Çarşamba)

### 1. Gather Data
- `outputs/` klasöründe hafta içinde üretilen dosyaları say ve listele.
- `journal/` son 7 girişinde onaylanan ve reddedilen çıktıları not al.
- `data/imports/` klasöründe işlenmeyi bekleyen dosya kaldı mı?

### 2. Score Against Targets

| Metrik | Hedef | Bu Hafta | Durum |
|--------|-------|----------|-------|
| İlk tur onay oranı | ≥80% | — | — |
| Brief'ten taslağa süre | ≤48 saat | — | — |
| Marka kılavuzu uyum | %100 | — | — |
| Revizyon turu | ≤2 | — | — |

### 3. Analyze Wins and Misses
- **Wins:** Ne işe yaradı? Kalıbı `MEMORY.md`'ye kaydet.
- **Misses:** Ne ters gitti? Hipotezi `MEMORY.md`'ye kaydet.

### 4. Update Memory
- Onaylanan renk/tipografi tercihlerini kaydet.
- Sektöre özel müşteri eğilimlerini kaydet.
- Revizyon nedenlerini ve tekrar eden hataları kaydet.

### 5. Log Weekly Summary to Journal
- Üretilen çıktı sayısı ve kategoriler
- KPI durumu (hedef vs. gerçek)
- Haftanın en önemli öğrenimi
- Gelecek hafta için öneri

## Monthly Review (Her Ayın 1'i)
- 4 haftalık özeti karşılaştır ve trend analizi yap.
- KPI hedeflerinin güncellenmesi gerekiyor mu?
- Hangi tasarım kategorisi en fazla talep gördü?
- Hangi skill en sık çalıştırıldı ve sonuçları ne oldu?
- Aylık özeti journal'a yaz.

## Escalation Rules
- İki hafta üst üste onay oranı %80'in altına düşerse → insan + orchestrator'a ilet.
- Brief eksik veya çelişkili ise → brief tamamlanmadan başlama; insana sor.
- Bir görev hiçbir skill'e uymuyorsa → orchestrator'a ilet.
- Marka kılavuzu yoksa ve mevcut varlıklardan çıkarılamıyorsa → insana sor.
- Müşteri geri bildirimi tutarsız veya art arda 3+ revizyona yol açıyorsa → insana ilet.

## Rules
- Journal okunmadan asla bir skill çalıştırma.
- Döngü başına bir skill — güçlü neden yoksa kombinasyon yapma.
- Brief yoksa üretme.
- `MEMORY.md`'de hiçbir varsayım önceden doldurulmaz; her kalıp gerçek veriden kazanılır.
- Onay bekleyen bir çıktı varken yeni proje başlatma.
