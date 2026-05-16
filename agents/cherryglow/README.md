# CherryGlow — VS Code Blog Yazarı

## Nasıl Çalışır?

**Runtime:** Claude Code (bu VS Code oturumu)
**Dashboard:** rclhq.vercel.app — sadece sonuçları gösterir

---

## Blog Yazdırma

Bana şunu söyle:
- `"bir blog yaz"` → topics.md'den en öncelikli konuyu yazar
- `"analog kamera hakkında blog yaz"` → o konuyu yazar
- `"sıradaki konuyu yaz"` → kuyruktan bir sonrakini yazar

Her blog için yaptıklarım:
1. Brave Search ile 5+ rakip analizi
2. PAA sorularını çıkarma
3. Keyword haritası
4. 2400+ kelimelik Türkçe blog yazma
5. SEO puanlama (90+ hedef)
6. `outputs/` klasörüne kaydetme
7. Dashboard'a senkronizasyon

---

## Çıktı Dosyaları

```
agents/cherryglow/
├── outputs/
│   └── YYYY-MM-DD_cherryglow_[slug].md   ← her blog buraya
├── data/
│   └── brain.json                         ← tüm geçmiş
├── topics.md                              ← konu kuyruğu
└── MEMORY.md                              ← öğrenmeler
```

---

## Dashboard Güncelleme

Blog yazıldıktan sonra otomatik çalışır:
```bash
python3 agents/cherryglow/scripts/sync_to_dashboard.py
```

Dashboard'da görünecekler:
- **Blog Performans** sekmesi: her blogun tahmini görüntülenme/organik/siparis istatistikleri
- **Geçmiş** sekmesi: yazılan tüm blogların kart listesi
- **Patron** paneli: toplam blog, ort. SEO, kelime sayısı

---

## Konu Eklemek

`topics.md` dosyasına `[ ]` formatında ekle.

---

## Skor Sistemi

| Puan | Durum |
|------|-------|
| 90-100 | Yayına hazır |
| 80-89 | Revizyon gerekli |
| <80 | Kabul edilmez, yeniden yaz |
