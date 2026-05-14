# Skill: Marka Kimliği Sistemi (BRAND_IDENTITY)

## Purpose
Müşteri için kapsamlı bir marka kimliği sistemi oluşturmak: logo mantığı, renk paleti, tipografi, görsel dil ve marka kılavuzu.

## Serves Goals
- Marka kimliği kalitesi (ilk tur onay ≥80%)
- Görsel tutarlılık (%100 marka kılavuzu uyumu)

## Inputs
- `data/imports/` — Müşteri brief'i (sektör, hedef kitle, rakip analizi, tercih edilen ton)
- `data/imports/` — Varsa mevcut logo, renk veya tipografi varlıkları
- `knowledge/AUDIENCE.md` — Hedef kitle segmentleri ve beklentileri
- `MEMORY.md` — Geçmiş müşterilerde işe yarayan marka kalıpları

## Process

1. **Brief analizi:** Müşteri brief'ini oku. Sektör, hedef kitle, rakipler, istenilen ton/duygular ve kısıtlar neler? Eksik bilgi varsa insan aracılığıyla talep et.

2. **Rekabet haritası:** Sektördeki rakiplerin görsel dilini tanımla. Hangi renk/tipografi klişeleri var? Müşteri nasıl farklılaşabilir?

3. **Marka kişiliği tanımı:** 3-5 sıfatla marka kişiliğini tanımla (ör. güvenilir + modern + sıcak). Bu sıfatlar tüm tasarım kararlarının referansı olacak.

4. **Renk paleti tasarımı:**
   - 1 ana renk (brand color) — marka kişiliğini yansıtan
   - 2 destekleyici renk (secondary/accent)
   - 1-2 nötr renk (background/text)
   - Her renk için: HEX, RGB, CMYK ve Pantone (varsa) değerlerini yaz
   - Renk psikolojisi ve sektör uyumunu gerekçelendir

5. **Tipografi sistemi:**
   - Başlık fontu (display/heading): font ailesi + ağırlık + boyut aralığı
   - Gövde fontu (body): font ailesi + ağırlık + satır yüksekliği
   - Vurgu/aksesuar fontu (varsa): kullanım senaryosu
   - Web güvenli alternatifleri belirt
   - Font lisans türünü belirt (Google Fonts / Adobe Fonts / ticari)

6. **Logo konsept yönergesi:**
   - Logo tipi önerisi: wordmark / lettermark / icon + wordmark / emblem
   - Görsel metafor veya sembol önerisi (varsa)
   - Kullanılacak şekil dili: geometrik / organik / dinamik
   - Renk versiyonları: renkli / tek renk / tersine çevrilmiş
   - Minimum boyut ve boşluk kuralları (clearspace)
   - Yasak kullanımlar (don'ts)

7. **Görsel dil tanımı:**
   - Fotoğraf stili: stil sıfatları + örnek kompozisyon kuralları
   - İllüstrasyon tarzı (kullanılıyorsa): flat / line / 3D / el çizimi
   - İkon stili: filled / outline / duo-tone
   - Doku/pattern kullanımı (varsa)

8. **Marka kılavuzu çıktısı:** Tüm kararları tek bir yapılandırılmış belgede topla (aşağıdaki Output formatı).

## Outputs
- `outputs/YYYY-MM-DD_uniqbee-design_brand-identity-[müşteri].md` — Tam marka kimliği kılavuzu

**Belge yapısı:**
```
1. Marka Kişiliği (3-5 sıfat + gerekçe)
2. Renk Paleti (HEX/RGB/CMYK tablosu + kullanım örnekleri)
3. Tipografi Sistemi (font tablosu + boyut skalası)
4. Logo Yönergeleri (konsept + versiyon kuralları + don'ts)
5. Görsel Dil (fotoğraf + illüstrasyon + ikon kuralları)
6. Uygulama Örnekleri (kartvizit, sosyal medya profili, e-posta imzası mockup açıklaması)
```

## Quality Bar
- Her renk değeri HEX + RGB + CMYK olarak verilmiş olmalı.
- Her font ailesi için en az 3 ağırlık/boyut kombinasyonu tanımlanmış olmalı.
- Logo yönergeleri en az 3 "yasak kullanım" içermeli.
- Kılavuz, bir tasarımcıya verildiğinde başka soru sormadan uygulayabilmeli.
- Brief'teki her kısıt karşılanmış olmalı.

## Tools
- Renk erişilebilirlik kontrolü için WCAG AA kontrastı zihinsel olarak değerlendir (4.5:1 metin, 3:1 büyük metin).
- Google Fonts veya Adobe Fonts kataloğundan gerçek font isimleri kullan.

## Integration
- VISUAL_CONCEPT skill'inden gelen moodboard ve konsept kararlarını temel alarak çalışır.
- CORPORATE_DESIGN ve SOCIAL_MEDIA_DESIGN skill'leri bu kılavuzu girdi olarak kullanır.
- DESIGN_AUDIT skill'i bu kılavuza göre uyum denetimi yapar.
