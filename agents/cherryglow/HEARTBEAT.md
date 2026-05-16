# CherryGlow — Heartbeat (Her Blog Döngüsü)

## Çalıştırma

Kullanıcı "bir blog yaz", "sıradaki konuyu yaz" veya "X konusunda blog yaz" dediğinde bu döngüyü çalıştır.

---

## Adım 1: BAĞLAM OKU

```
READ:
- topics.md → hangi konu pending?
- data/brain.json → geçmiş SEO skorları, kullanılan keywordler, öğrenmeler
- journal/ → son journal girişleri (varsa)
```

**Karar:** Hangi konuyu yazacağım? Neden bu? (KPI'ya en katkılı konu önce gelir)

---

## Adım 2: ARAŞTIR (skill: 01-seo-research.md)

Araştırma sırasız değil, sistematik:

1. **Rakip analiz** — Konu için Brave Search ile TR top 5 sonuç analiz et
   - Her sonucun başlığı + açıklaması → içerik boşluklarını tespit et
2. **PAA soruları** — "People Also Ask" formatında soru listesi çıkar (≥7 soru)
3. **Anahtar kelime haritası** — Primary KW + 5 secondary KW + 3 LSI KW belirle
4. **Rakip zayıflıkları** — Rakiplerin yazmadığı veya yüzeysel geçtiği noktalar
5. **Eşsiz açı** — Bu blogda rakiplerden farkımız ne olacak?

Araştırma sonucu → `data/research-cache.json` güncelle

---

## Adım 3: YAPI PLANLA

Blog planını düşünce olarak yaz (kullanıcıya gösterme, sadece kendine notla):

```
H1: [Primary KW önde, 55-60 karakter]
Meta: [150-160 karakter, CTA içerir]
H2 listesi: [6-8 H2, her biri 250-400 kelime hedef]
FAQ soruları: [5 soru, araştırmadan gelen PAA]
CTA noktaları: [retrocameraland.com linkleri nerede olacak]
```

---

## Adım 4: YAZ (skill: 02-blog-writer.md)

**KRITIK:** Blog'u tek seferde, paragraf paragraf, gerçekten yaz. Her H2 bölümü:
- En az 250 kelime
- Somut örnekler, ürün adları, teknik detaylar
- "—" (em-dash) karakteri YASAK, yerine virgül kullan

Toplam hedef: **2400+ kelime** (minimum 2200)

Yazım sırası:
1. H1 + giriş (70-100 kelime, primary KW ilk 100 kelimede)
2. Her H2 bölümü (250+ kelime, 2-3 H3 ile desteklenir)
3. FAQ bölümü (5+ soru, her cevap 70-90 kelime)
4. Sonuç (100+ kelime, retrocameraland.com CTA)

---

## Adım 5: PUAN (skill: 03-seo-scorer.md)

Blog bittikten sonra puanla:

| Kontrol | Puan | Durum |
|---------|------|-------|
| Kelime sayısı ≥ 2200 | 20 | |
| H1 var, primary KW önde | 10 | |
| 6+ H2 bölümü | 10 | |
| Primary KW yoğunluğu 1-2% | 15 | |
| 5+ secondary KW kullanımı | 10 | |
| 5+ FAQ (cevaplı) | 15 | |
| 2+ retrocameraland.com bağlantısı | 10 | |
| Em-dash yok | 5 | |
| Meta description 150-160 karakter | 5 | |
| **Toplam** | **/100** | |

**Hedef: 90+.** Eksikse → Adım 4'e dön, zayıf bölümü genişlet.

---

## Adım 6: KAYDET & AKTAR (skill: 04-sync-dashboard.md)

1. Blog'u `outputs/YYYY-MM-DD_cherryglow_[slug].md` olarak kaydet
2. `data/brain.json` güncelle (title, date, seo, wc, slug, topics_covered, kw_used)
3. `topics.md` güncelle → konu "done" işaretle
4. Journal girişi yaz → `journal/YYYY-MM-DD_HHMM.md`
5. `scripts/sync_to_dashboard.py` çalıştır → dashboard BLOG_SEO güncellenir, commit+push

---

## Haftalık Gözden Geçirme

Her 7 günde bir (user "haftalık rapor" dediğinde):
- En yüksek/düşük SEO skorları
- Hangi konular kaldı?
- Öğrenmeler: hangi yapı daha iyi skor aldı?
- Öneri: sıradaki 3 konu

---

## Eskalasyon Kuralları

- SEO skoru < 80 → blog'u revize et, yeniden puan
- Araştırma sonuç vermezse → farklı arama terimi dene (EN veya TR)
- Dashboard sync başarısız → scripti tekrar çalıştır, sonra uyar
