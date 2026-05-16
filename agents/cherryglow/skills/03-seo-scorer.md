# Skill: SEO Puanlama

## Amaç
Blog bittikten sonra puanla. 90 altıysa revize et.

---

## Puanlama Tablosu

| # | Kontrol | Max Puan | Nasıl Hesaplanır |
|---|---------|----------|-----------------|
| 1 | Kelime sayısı | 20 | ≥2200: 20p / 1800-2199: 14p / 1500-1799: 8p / <1500: 0p |
| 2 | H1 var, primary KW önde | 10 | H1 başlığında KW ilk 3 kelimede: 10p / var ama geç: 5p / yok: 0p |
| 3 | 6+ H2 bölümü | 10 | ≥6 H2: 10p / 4-5 H2: 6p / <4: 0p |
| 4 | Primary KW yoğunluğu | 15 | %1-2: 15p / %0.5-1 veya %2-3: 8p / dışı: 0p |
| 5 | 5+ secondary KW | 10 | ≥5 KW, her biri 2+x: 10p / 3-4 KW: 6p / <3: 0p |
| 6 | 5+ FAQ (cevaplı) | 15 | ≥5 soru+cevap: 15p / 3-4: 8p / <3: 0p |
| 7 | retrocameraland.com 2+ link | 10 | ≥2 link: 10p / 1: 5p / 0: 0p |
| 8 | Em-dash yok | 5 | "—" yok: 5p / var: 0p |
| 9 | Meta description | 5 | 150-160 karakter: 5p / var ama yanlış uzunluk: 2p / yok: 0p |
| **TOPLAM** | | **100** | |

---

## Kontrol Yöntemi

```
1. Kelime say: md dosyasındaki toplam kelime sayısı
2. H1 kontrol: "# " ile başlayan satır — primary KW var mı?
3. H2 say: "## " ile başlayan satır sayısı
4. KW yoğunluğu: (primary_kw_tekrar / toplam_kelime) × 100
   - Türkçe suffixler için kök kontrolü (ilk 4+ karakter)
5. Secondary KW: her birinin metin içinde tekrar sayısı
6. FAQ: "**Soru" veya "**Q:" formatındaki satırlar
7. Link: "retrocameraland.com" geçiş sayısı
8. Em-dash: "—" karakter var mı?
9. Meta desc: YAML frontmatter'daki meta_description uzunluğu
```

---

## Sonuç Formatı

```
## SEO Puanı: [SKOR]/100 [durum emojiyle değil, yazıyla]

| Kontrol | Puan | Not |
|---------|------|-----|
| Kelime: [WC] | [puan]/20 | [OK / Eksik] |
| H1 KW | [puan]/10 | [OK / Eksik] |
| H2 sayısı: [n] | [puan]/10 | [OK / Eksik] |
| KW yoğunluğu: %[X] | [puan]/15 | [OK / Eksik] |
| Secondary KWs | [puan]/10 | [OK / Eksik] |
| FAQ sayısı: [n] | [puan]/15 | [OK / Eksik] |
| İç linkler: [n] | [puan]/10 | [OK / Eksik] |
| Em-dash | [puan]/5 | [OK / Var] |
| Meta desc | [puan]/5 | [OK / Eksik] |

**Revizyon gerekiyor mu?** [Evet — şu bölümleri genişlet: ... / Hayır, yayına hazır]
```

---

## 90 Altıysa

1. Hangi kontroller eksik? → O bölümleri genişlet
2. FAQ eksikse → 5 soru yaz
3. Kelime eksikse → en zayıf H2'yi 2 H3 ekleyerek genişlet
4. Linkler eksikse → doğal geçiş cümlesi ekle
5. Tekrar puan → 90+ olana kadar
