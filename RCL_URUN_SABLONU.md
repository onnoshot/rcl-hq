# RCL Ürün İçerik Şablonu

Retrocameraland ürün açıklamalarının standardı. Yeni ürün eklenirken bu yapı birebir uygulanır.

## Bölüm sırası (değişmez)

| # | Bölüm | Kaynak |
|---|-------|--------|
| 1 | Giriş cümlesi | Modelin dönemi ve öne çıkan tek özelliği — araştırma |
| 2 | **Kutu İçeriği** | **Mağaza sahibi verir. ASLA değiştirilmez.** |
| 3 | **Kondisyon** | **Mağaza sahibi verir (puan + açıklama). ASLA değiştirilmez.** Animasyonlu halka |
| 4 | Video | Kanalda model adıyla eşleşen video varsa gömülür |
| 5 | Teknik özellikler | Model adına göre araştırılır, doğrulanır |
| 6 | RetroCameraLand yorumu | Kondisyon + kutu içeriği + özelliklerden yazılır |
| 7 | Sık sorulan sorular | Ürünün kendi verisinden üretilir |
| 8 | Güvence + sosyal | Standart blok, her üründe aynı |

## Değişmez kurallar

1. **Kutu içeriği ve kondisyon metni harfi harfine korunur.** Yeniden yazılmaz, özetlenmez, düzeltilmez.
2. **Teknik veri uydurulmaz.** Model için güvenilir kaynak bulunamazsa o satır yazılmaz
   (örnek: Traveler DC-830 — teknik tablo olmadan yayında).
3. **Emoji kullanılmaz.** `°`, `©`, `®` gibi meşru semboller kalır.
4. **Renk sabitlenmez.** Tema koyu; tüm renkler `inherit` + `opacity` ile verilir, aksi halde
   siyah zeminde siyah yazı oluşur.
5. **Abartı yok.** "Yatırım aracı", "değerlenecek" gibi ifadeler kullanılmaz; kıtlık gerçeği yeterli.

## Teknik detaylar

- CSS sınıf öneki `rcl-p`, `<style>` bloğu açıklamanın içinde
- Kondisyon halkası: SVG `stroke-dasharray` animasyonu, puan ortada, altında "10 ÜZERİNDEN"
- Mobil kırılım 560px: halka üstte, metin tam genişlikte
- `prefers-reduced-motion` desteklenir
- Sosyal şerit: 7 hesap (Instagram, YouTube, TikTok, Pinterest, X, LinkedIn, Facebook), daire içinde SVG

## Yeni ürün akışı

1. Mağaza sahibi HQ dashboard → **Yeni Ürün** sayfasını doldurur
2. "Çıktıyı oluştur" → "Kopyala"
3. Çıktı Claude'a yapıştırılır
4. Claude modeli araştırır, teknik özellikleri doğrular, içeriği + meta başlık + meta açıklama
   + handle + etiketleri hazırlar

### Çıktı formatı

```
### RCL YENI URUN ###
MODEL: Canon PowerShot A480
RENK: Gümüş
TIP: kamera
KONDISYON: 9.2
FIYAT: 11490
KONDISYON_NOTU: Gövdede hafif kullanım izleri var, lens ve tüm fonksiyonlar sorunsuz.
KUTU_ICERIGI:
- Canon PowerShot A480
- Orijinal batarya
- Universal şarj aleti
DEGERLENDIRME: AA pille çalışması büyük avantaj, ünite çok temiz.
### SON ###
```

`KONDISYON_NOTU`, `KUTU_ICERIGI` ve `DEGERLENDIRME` birebir kullanılır.
`MODEL` araştırmanın girdisidir.

## SEO çıktısı (Claude hazırlar)

- **Meta başlık**: 45-60 karakter, model adı başta
- **Meta açıklama**: 120-160 karakter, model + ayırt edici özellik + kondisyon vurgusu
- **Handle**: `marka-model-varyant` (küçük harf, tireli, ASCII)
- **Etiketler**: marka, seri, sensör tipi, kullanım alanı

## İlgili dosyalar

| Dosya | İş |
|-------|-----|
| `rcl_urun_icerik.py` | Mevcut açıklamayı ayrıştırır (kayıpsız, artık-kovası mantığı) |
| `rcl_urun_sablon.py` | CSS, kondisyon halkası, SSS üreticisi, sosyal şerit |
| `rcl-urun-standart.py` | Şablonu kurar, kutu/kondisyon korumasını doğrular |
| `rcl-urun-video-temizlik.py` | Video gömme + markup temizliği (minimal müdahale) |
| `retrocameraland-hq-dashboard.html` | "Yeni Ürün" giriş sayfası + kârlılık hesabı |
