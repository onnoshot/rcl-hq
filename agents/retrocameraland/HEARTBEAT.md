# Retrocameraland Content Agent — Heartbeat

## Schedule
- **Ürün açıklamaları:** Talep üzerine (insan `data/imports/` klasörüne yeni ürün listesi bıraktığında)
- **Blog yazısı:** Haftalık (Salı günleri tercih edilir)
- **Kitle araştırması:** Aylık (ayın ilk Pazartesi günü)
- **Haftalık gözden geçirme:** Pazartesi sabahı, günlük döngüden önce

## Each Cycle

### 1. Read Context
- `journal/` içindeki son 3 girişi oku — insan geri bildirimi, onay/ret kararları
- `knowledge/STRATEGY.md` oku — güncel öncelikler değişti mi?
- `knowledge/AUDIENCE.md` oku — hedef kitle tanımı güncel mi?
- Kendi `MEMORY.md` dosyasını oku — geçmiş döngülerden öğrenilen kalıplar

### 2. Assess State
- `data/imports/` içinde işlenmemiş ürün verisi var mı? → PRODUCT_DESCRIPTION skill'ini çalıştır
- Blog takviminde bu hafta için yazı var mı? → BLOG_WRITING skill'ini çalıştır
- Kitle araştırması güncelliğini yitirdi mi (>30 gün)? → AUDIENCE_RESEARCH skill'ini çalıştır
- Yukarıdakilerin hiçbiri yoksa → haftalık gözden geçirme yap, MEMORY.md'yi güncelle

### 3. Execute Skill

**Karar ağacı:**
```
data/imports/ içinde işlenmemiş ürün var?
  → EVET: PRODUCT_DESCRIPTION skill'ini çalıştır
  → HAYIR:
      Blog takviminde boşluk var mı?
        → EVET: BLOG_WRITING skill'ini çalıştır (önce AUDIENCE_RESEARCH çıktısını oku)
        → HAYIR:
            Kitle araştırması >30 gün önce yapıldıysa → AUDIENCE_RESEARCH skill'ini çalıştır
            Aksi takdirde → haftalık gözden geçirme yap
```

- Bir döngüde yalnızca 1 skill çalıştır (güçlü bir neden olmadıkça birleştirme)
- Skill tamamlanınca çıktıyı `outputs/` klasörüne kaydet, journal'a giriş yaz

### 4. Log to Journal
Her döngü sonunda `journal/YYYY-MM-DD_HHMM.md` oluştur ve şunları yaz:
- Bu döngüde ne yapıldı
- Çıktının nerede olduğu (dosya yolu)
- İnsan onayı için bekleyen çıktılar
- Bir sonraki döngüde yapılması gereken

---

## Weekly Review (Pazartesi, günlük döngüden önce)

### 1. Gather Data
- `outputs/` klasöründeki son 7 günün çıktılarını listele
- İnsan onaylı / reddedilmiş içerikleri say
- `journal/` girişlerinde geri bildirim not etmişse topla

### 2. Score Against Targets

| Metric | Target | Bu Hafta | Durum |
|--------|--------|----------|-------|
| Blog yazısı sayısı | 1/hafta | ? | — |
| Ürün açıklaması onay oranı | >80% | ? | — |
| İnsan geri bildirimi | Var/Yok | — | — |

### 3. Analyze Wins and Misses
- **Kazananlar:** Onaylanan içeriklerde ortak özellik var mı? → MEMORY.md'ye kaydet
- **Kaçırılanlar:** Reddedilen içeriklerde ortak sorun var mı? → hipotezi MEMORY.md'ye kaydet

### 4. Update Memory
Doğrulanan kalıpları MEMORY.md'nin ilgili bölümlerine ekle.

### 5. Log Weekly Summary to Journal
- Üretilen içerik sayısı
- Onay/ret oranı
- Bu haftanın en önemli öğrenimi
- Gelecek hafta için öneri

---

## Monthly Review
- 4 haftalık gözden geçirmeyi karşılaştır
- KPI'lar hedeften uzaklaşıyorsa insana bildir
- Kitle araştırmasını güncelle (AUDIENCE_RESEARCH skill)
- Ayın en iyi ve en kötü performanslı içerik formatını not et

---

## Escalation Rules
- 2+ hafta üst üste blog takvimi doldurulamazsa → insana bildir
- Onay oranı %50'nin altına düşerse → insan feedback iste
- Yeni ürün kategorisi gelirse (bilinen kategorilerde değilse) → AUDIENCE_RESEARCH çalıştır
- Bir görev mevcut skill'lerin hiçbirine uymuyorsa → insana ilet
- İçerik talebi etik sınır yaratıyorsa → doğrudan insana eskalasyon

## Rules
- Her döngüde önce journal'ı oku, sonra hareket et
- Döngü başına 1 skill (güçlü neden olmadıkça)
- Emin değilsen araştırma yap, tahmin yürütme
- AGENT.md'deki bir hedefe hizmet etmeyen skill çalıştırma
