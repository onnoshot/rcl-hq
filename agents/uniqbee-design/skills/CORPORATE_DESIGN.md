# Skill: Kurumsal Tasarım Kiti (CORPORATE_DESIGN)

## Purpose
Müşterinin marka kimliğini fiziksel ve dijital kurumsal materyallere uygulamak: kartvizit, antetli kağıt, sunum şablonu, e-posta imzası, teklif şablonu ve benzeri kurumsal temas noktaları.

## Serves Goals
- Kurumsal tasarım verimliliği (brief'ten taslağa ≤48 saat)
- İçerik çeşitliliği (≥5 farklı kategori/ay)

## Inputs
- `outputs/` — Müşterinin marka kimliği kılavuzu (BRAND_IDENTITY çıktısı)
- `data/imports/` — Müşteri brief'i: hangi materyaller isteniyor, baskı/dijital tercihi, boyut kısıtları
- `data/imports/` — Varsa şirket bilgileri (ad, adres, telefon, web sitesi, sosyal medya)
- `MEMORY.md` — Geçmişte işe yarayan kurumsal tasarım kalıpları

## Process

1. **Materyal listesi belirleme:** Brief'ten hangi kurumsal materyallerin üretileceğini listele. Standart kit:
   - Kartvizit (ön + arka, 85×55 mm, 3.5×2 inch)
   - Antetli kağıt / letterhead (A4)
   - E-posta imzası (HTML spesifikasyonu)
   - Sunum şablonu (kapak + iç sayfa + son sayfa)
   - Teklif/fatura şablonu
   - Zarf tasarımı (DL + C4)
   - Klasör kapağı / folder

2. **Izgara sistemi tanımlama:** Her materyal için:
   - Kenar boşlukları (margin)
   - Güvenli alan (safe zone / bleed için baskı materyallerinde 3mm)
   - Sütun yapısı
   - Beyaz alan (white space) stratejisi

3. **Hiyerarşi kurma:** Her materyalde görsel hiyerarşiyi tanımla:
   - 1. seviye: Logo / marka adı
   - 2. seviye: Ana mesaj / başlık
   - 3. seviye: İletişim bilgileri / destekleyici içerik

4. **Tipografi uygulaması:** BRAND_IDENTITY kılavuzundaki font sistemini uygula:
   - Başlık hiyerarşisi: H1 → H2 → H3 boyut ve ağırlık tablosu
   - Gövde metni: boyut, satır yüksekliği, karakter aralığı
   - Vurgu metni kuralları

5. **Renk uygulaması:** Marka renk paletini kurumsal materyallere uygula:
   - Baskı renkleri: CMYK değerleri ve Pantone karşılıkları
   - Dijital renkler: RGB/HEX değerleri
   - Arka plan - metin kontrast uyumu (WCAG AA)

6. **Logo yerleşimi:** Her materyal için logo:
   - Konumu (ör. sol üst köşe, ortalanmış)
   - Minimum boyutu
   - Clearspace kuralı uygulaması

7. **Her materyal için spesifikasyon yazma:** Tasarımcıya veya araçlara aktarılabilecek detaylı spesifikasyon:
   - Boyutlar ve birimler
   - Renk değerleri
   - Font boyutları ve ağırlıkları
   - Nesne konumları (x, y koordinatları veya tanımlayıcı yönlendirmeler)
   - Baskı için: CMYK, bleed, safe zone, çözünürlük (300 DPI)
   - Dijital için: RGB/HEX, 72-144 DPI, dosya formatı önerileri (PNG/SVG/PDF)

8. **Mockup açıklaması:** Her materyal için gerçekçi bir uygulama bağlamı tanımla (ör. "kartvizit beyaz mat laminasyon, 400gr kuşe kağıt üzerinde").

## Outputs
- `outputs/YYYY-MM-DD_uniqbee-design_corporate-kit-[müşteri].md` — Tüm kurumsal materyal spesifikasyonları

**Belge yapısı:**
```
1. Materyal Listesi ve Öncelik Sırası
2. Izgara & Kenar Boşlukları Sistemi
3. Kartvizit Spesifikasyonu (ön + arka)
4. Antetli Kağıt Spesifikasyonu
5. E-posta İmzası Spesifikasyonu (HTML kodu dahil)
6. Sunum Şablonu Spesifikasyonu (kapak + iç + son)
7. Teklif/Fatura Şablonu Spesifikasyonu
8. Ek Materyaller (varsa)
9. Baskı Notları (baskıevi için teknik gereksinimler)
```

## Quality Bar
- Her materyal için baskı ve dijital sürüm ayrı ayrı belirtilmiş olmalı.
- Tüm renk değerleri hem CMYK (baskı) hem HEX/RGB (dijital) olarak verilmiş olmalı.
- E-posta imzası spesifikasyonu doğrudan HTML koduna dönüştürülebilir düzeyde olmalı.
- Sunum şablonu en az kapak + içerik + son sayfa olmak üzere 3 sayfa tipi içermeli.
- Tüm ölçüler tutarlı birimle (mm veya px) verilmiş olmalı.

## Tools
- E-posta imzası için satır içi CSS (inline CSS) spesifikasyonu yaz — harici stylesheet desteklenmiyor.
- Baskı materyalleri için her zaman 3mm bleed alanı ekle.
- Kartvizit için standart boyut: 85×55mm (Türkiye/Avrupa) veya 3.5×2 inch (ABD).

## Integration
- BRAND_IDENTITY skill'inin çıktısına bağlıdır — kılavuz olmadan çalıştırma.
- SOCIAL_MEDIA_DESIGN skill'iyle renk ve tipografi tutarlılığını korur.
- DESIGN_AUDIT skill'i bu çıktıları marka kılavuzuna göre denetler.
