# Skill: Tasarım Denetimi & Geri Bildirim (DESIGN_AUDIT)

## Purpose
Mevcut tasarım çıktılarını marka kılavuzuna, görsel tutarlılık kurallarına ve sektör standartlarına göre denetlemek; somut iyileştirme önerileri üretmek.

## Serves Goals
- Görsel tutarlılık (%100 marka kılavuzu uyumu)
- Müşteri memnuniyeti (≤2 revizyon turu)

## Inputs
- `outputs/` — Denetlenecek tasarım çıktıları veya spesifikasyonlar
- `outputs/` — Müşterinin marka kimliği kılavuzu (BRAND_IDENTITY çıktısı)
- `data/imports/` — Varsa müşteri revizyon talepleri veya geri bildirimleri
- `data/imports/` — Varsa mevcut müşteri tasarımları (audit edilecek materyaller)
- `MEMORY.md` — Geçmişte tespit edilen tekrar eden hatalar

## Process

1. **Denetim kapsamı belirleme:** Hangi çıktılar denetlenecek? Listele:
   - Belirli bir materyal mi (ör. kartvizit taslağı)?
   - Tüm kurumsal kit mi?
   - Sosyal medya şablonları mı?
   - Müşterinin mevcut marka materyalleri mi (onboarding denetimi)?

2. **Renk uyum denetimi:**
   - Kullanılan renkler marka paletindeki HEX/CMYK değerleriyle eşleşiyor mu?
   - Renk sapması var mı? (ör. %15+ fark tespit edilirse flag)
   - Metin-arka plan kontrast oranı WCAG AA standardını karşılıyor mu? (4.5:1 metin, 3:1 büyük metin)
   - Yetkisiz renk kullanımı var mı (palette dışı)?

3. **Tipografi denetimi:**
   - Kullanılan fontlar marka kılavuzundaki fontlarla eşleşiyor mu?
   - Font ağırlıkları kılavuzdaki hiyerarşiye uyuyor mu?
   - Boyut skalası tutarlı mı (heading → subheading → body mantığı)?
   - Satır yüksekliği ve karakter aralığı okunabilirlik için yeterli mi?
   - Yasaklı font kullanımı var mı?

4. **Logo kullanım denetimi:**
   - Logo clearspace kuralına uyuluyor mu?
   - Logo minimum boyut kuralı ihlal edilmiş mi?
   - Logo renk versiyonu doğru kullanılmış mı (renkli zemin üzerinde ters versiyon gibi)?
   - Logo bozulmuş (stretch/skew) mu?
   - Yasaklı logo kullanımları var mı?

5. **Görsel hiyerarşi denetimi:**
   - Göz ilk nereye gidiyor? Bu istenilen mi?
   - Başlık → alt başlık → gövde metin hiyerarşisi net mi?
   - CTA (call to action) unsuru görsel olarak öne çıkıyor mu?
   - Odak noktası belirsiz ya da çok mu fazla?

6. **Boşluk ve düzen denetimi:**
   - Kenar boşlukları (margin/padding) tutarlı mı?
   - Elementler arasındaki boşluklar sistematik mi (8px grid gibi)?
   - Fazla kalabalık (crowded) veya fazla boş (lonely) alan var mı?
   - Asimetrik düzenler kasıtlı mı yoksa hata mı?

7. **Platform/baskı uyum denetimi (varsa):**
   - Baskı materyallerinde bleed ve safe zone uygulandı mı?
   - Dijital çıktılar için çözünürlük yeterli mi?
   - Sosyal medya boyutları platform spesifikasyonlarıyla eşleşiyor mu?

8. **Skor ve özet:** Her denetim kategorisi için değerlendirme:

   | Kategori | Durum | Kritik Sorun | Öneri |
   |----------|-------|--------------|-------|
   | Renk uyumu | ✅ / ⚠️ / ❌ | — | — |
   | Tipografi | ✅ / ⚠️ / ❌ | — | — |
   | Logo kullanımı | ✅ / ⚠️ / ❌ | — | — |
   | Görsel hiyerarşi | ✅ / ⚠️ / ❌ | — | — |
   | Boşluk/düzen | ✅ / ⚠️ / ❌ | — | — |
   | Platform uyumu | ✅ / ⚠️ / ❌ | — | — |

   - ✅ Uyumlu  ⚠️ İyileştirilebilir  ❌ Kritik sorun (düzeltilmeden yayınlanamaz)

9. **Revizyon önceliklendirme:**
   - ❌ Kritik sorunlar: düzeltilmeden onay verilmez
   - ⚠️ İyileştirmeler: müşteri tercihe göre uygular
   - Not: tekrar eden sorunları `MEMORY.md`'ye kaydet

## Outputs
- `outputs/YYYY-MM-DD_uniqbee-design_design-audit-[müşteri]-[materyal].md` — Denetim raporu

**Belge yapısı:**
```
1. Denetim Kapsamı
2. Denetim Skoru (kategori tablosu)
3. Kritik Sorunlar (❌) — her sorun için: tespit, neden sorun, nasıl düzeltilir
4. İyileştirme Önerileri (⚠️) — öncelik sırasıyla
5. Onaylanan Unsurlar (✅) — neyin iyi çalıştığı
6. Revizyon Adımları (sıralı eylem listesi)
7. Hafıza Güncellemesi (tekrar eden hataların notu)
```

## Quality Bar
- Her ❌ kritik sorun için spesifik düzeltme adımı yazılmış olmalı.
- Denetim kılavuzsuz yapılmaz — marka kılavuzu olmadan audit başlamaz.
- "Beğenmedim" veya "güzel değil" gibi öznel yorumlar kullanılmaz — her gözlem kılavuza veya standarda dayandırılır.
- Rapor, bir tasarımcının doğrudan uygulayabileceği somutlukta olmalı.

## Tools
- WCAG renk kontrast kuralları referans alınır (4.5:1 metin, 3:1 büyük metin, 7:1 AAA).
- Logo clearspace: genellikle logo yüksekliğinin %10-20'si minimum boşluk.
- 8px veya 4px temel grid sistemi referans alınır.

## Integration
- BRAND_IDENTITY çıktısını referans kılavuz olarak kullanır.
- Revizyon talepleri geldiğinde ilk çalıştırılır — neyin değişmesi gerektiğini netleştirir.
- Tespit edilen tekrar eden hatalar `MEMORY.md`'ye kaydedilir ve ileride önleyici olarak kullanılır.
- Aylık periyodik denetimde tüm aktif projelerin çıktılarını tarar.
