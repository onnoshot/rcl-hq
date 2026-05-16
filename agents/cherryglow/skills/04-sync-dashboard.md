# Skill: Dashboard Senkronizasyonu

## Amaç
Blog yazıldıktan sonra `scripts/sync_to_dashboard.py` çalıştır.
Script dashboard BLOG_SEO verisini günceller, commit eder, push eder.

---

## Çalıştırma

```bash
cd /Users/onnoshot/Downloads/Agentlar
python3 agents/cherryglow/scripts/sync_to_dashboard.py
```

## Script Ne Yapar?

1. `agents/cherryglow/data/brain.json` okur
2. `rcl-dashboard/index.html` içindeki `const BLOG_SEO = {...};` bloğunu bulur
3. `BLOG_SEO.posts` listesine Cherry'nin bloglarını ekler/günceller
4. `BLOG_SEO.monthly` verisini günceller
5. `BLOG_SEO.total_posts` sayısını artırır
6. Dosyayı kaydeder
7. `git add + commit + push` yapar (rcl-dashboard reposu)
8. Vercel otomatik deploy eder

## Dashboard'da Ne Görünür?

- **Blog Performans** sekmesi: Cherry'nin blogları kart grid'inde görünür
- Her kart: başlık, tahmini görüntülenme, organik trafik, SEO skoru
- **Patron** paneli: toplam blog sayısı, ortalama SEO, kelime sayısı güncellenir
- **Geçmiş** sekmesi: yazılan tüm bloglar kronolojik olarak

## Hata Durumu

Script başarısız olursa:
1. Hata mesajını oku
2. `rcl-dashboard/index.html` dosyasını kontrol et (JS sözdizimi?)
3. `node --check` ile doğrula
4. Manuel olarak git push yap
