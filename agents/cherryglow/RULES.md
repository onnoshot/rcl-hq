# CherryGlow — Kurallar

## YAPILACAKLAR

- Her blog için Brave Search ile GERÇEK araştırma yap (en az 5 kaynak)
- PAA sorularını araştırmadan çıkar, uydurma
- 2200+ kelime yaz — kısaca geç değil, derinlemesine anlat
- Her H2'de somut ürün adları, teknik bilgi, gerçek örnek kullan
- retrocameraland.com'u doğal ve bağlamsal olarak 3+ kez geç
- SEO skoru 90 altıysa revize et, yayınlama
- Her blog için brain.json güncelle
- Dashboard sync'i her blog sonrası çalıştır

## YAPILMAYACAKLAR

- "—" em-dash karakteri ASLA kullanma (virgülle değiştir)
- Genel, yüzeysel, ya da fluffy içerik yazma
- Keyword stuffing yapma (doğal yerleşim, 1-2% yoğunluk)
- Başkasının içeriğini kopyalama (özgün, rakiplerden farklı açı)
- knowledge/ klasörüne yazma
- Başka ajanların dosyalarını değiştirme
- Onay olmadan externally publish etme

## Dosya Adlandırma

Outputlar: `YYYY-MM-DD_cherryglow_[slug].md`
- slug: küçük harf, tire ile ayrılmış, 3-6 kelime
- Örnek: `2026-05-17_cherryglow_analog-kamera-baslangic-rehberi.md`

## Kalite Standardı

Her blog şunları MUTLAKA içermeli:
- [ ] H1 (primary KW önde)
- [ ] 6+ H2 (her biri 250+ kelime)
- [ ] 5+ FAQ (cevaplı, 70-90 kelime/cevap)
- [ ] 2+ retrocameraland.com bağlantısı (satın al, incele CTA)
- [ ] Meta description (150-160 karakter)
- [ ] SEO skoru 90+

## Dashboard Entegrasyonu

Blog yazıldıktan sonra:
1. `scripts/sync_to_dashboard.py` çalıştır
2. Script `rcl-dashboard/index.html` içindeki BLOG_SEO verisini günceller
3. Git commit + push → Vercel otomatik deploy
4. Panelde "Blog Performans" sekmesi güncellenir
