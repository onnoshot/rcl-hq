# Skill: Görsel Konsept Geliştirme (VISUAL_CONCEPT)

## Purpose
Bir marka veya kampanya için görsel yön belirlemek: moodboard, konsept özeti, yaratıcı yön ve tasarım stratejisi oluşturmak — tüm tasarım çalışmalarının başladığı temel skill.

## Serves Goals
- Marka kimliği kalitesi (ilk tur onay ≥80%)
- Müşteri memnuniyeti (≤2 revizyon turu)

## Inputs
- `data/imports/` — Müşteri brief'i (marka değerleri, hedef kitle, rakipler, referans görseller, sevilen/sevilmeyen örnekler)
- `data/imports/` — Varsa sektör araştırması veya pazar analizi
- `knowledge/AUDIENCE.md` — Hedef kitle profili ve beklentileri
- `knowledge/STRATEGY.md` — Ajans stratejik öncelikleri
- `MEMORY.md` — Geçmişte hangi konsept yönlerinin onaylandığı

## Process

1. **Brief derinleştirme:** Müşteri brief'ini analiz et ve şu soruları yanıtla:
   - Marka kiminle konuşuyor? (yaş, yaşam biçimi, değerleri)
   - Marka ne hissettirmeli? (3 duygu sıfatı — ör. güvenli + heyecan verici + dürüst)
   - Marka ne hissettirmemeli? (anti-değerler — ör. ucuz, karmaşık, agresif)
   - Rakipler görsel olarak ne yapıyor? Müşteri nasıl farklılaşacak?

2. **Referans analizi:** Müşterinin paylaştığı "sevdikleri" ve "sevmedikleri" görselleri analiz et:
   - Sevdikleri: ortak özellikler neler? (renk sıcaklığı, şekil dili, boşluk kullanımı, tipografi tarzı)
   - Sevmedikleri: kaçınılacak özellikler neler?
   - Bu gözlemleri moodboard yönlendirmesi olarak yaz.

3. **Konsept alternatifleri geliştirme:** 2-3 farklı görsel konsept yönü tanımla. Her konsept için:
   - **Konsept adı:** 2-3 kelimelik özlü başlık (ör. "Minimal Güç", "Sıcak Uzmanlık", "Dijital Cesaret")
   - **Konsept özeti:** 2-3 cümle — bu yön ne anlatıyor ve neden bu marka için uygun?
   - **Anahtar kelimeler:** 5-7 sıfat (ör. temiz, sert, güvenilir, modern, Avrupa)
   - **Renk yönü:** palette taslağı — sıcak/soğuk, doygun/pastel, kontrastlı/yumuşak
   - **Tipografi yönü:** serif/sans-serif, geometric/humanist, bold/light
   - **Fotoğraf/görsel dil:** sektörel fotoğraf stilleri, çekim açısı, ton
   - **Referans esini:** bu konsepti hatırlatan 2-3 marka veya estetik örneği

4. **Moodboard tanımı:** Seçilen konsept için moodboard içeriği:
   - Renk paleti önizlemesi (5-7 ton)
   - Tipografi örnek kombinasyonu (başlık + gövde birlikte)
   - Görsel atmosfer: fotoğraf/illüstrasyon tonunu tanımlayan 3-5 kelime
   - Doku/yüzey önerileri (mat/parlak, granül/düz)
   - Layout eğilimi: minimal beyaz alan / yoğun grid / asimetrik / simetrik

5. **Konsept önerisi sunumu:** Müşteriye sunulacak konsept briefingi hazırla:
   - Neden bu yönü seçtik (iş gerekçesi)
   - Bu konseptin marka değerleriyle nasıl örtüştüğü
   - Olası riskler veya dikkat edilmesi gerekenler
   - Müşterinin geri bildirim vermesi için açık sorular

6. **Karar logu:** Onaylanan konsept kararlarını `MEMORY.md`'ye ve `journal/`'a yaz.

## Outputs
- `outputs/YYYY-MM-DD_uniqbee-design_visual-concept-[müşteri].md` — Görsel konsept briefingi

**Belge yapısı:**
```
1. Brief Özeti ve Analiz
2. Referans Analizi (sevilen / sevilmeyen)
3. Konsept A — [İsim]: Özet, Anahtar Kelimeler, Renk/Tipografi Yönü, Referans Esini
4. Konsept B — [İsim]: (aynı format)
5. Konsept C — [İsim]: (varsa, aynı format)
6. Moodboard Tanımı (seçilen veya önerilen konsept için)
7. Önerilen Konsept Gerekçesi
8. Müşteri için Açık Sorular
```

## Quality Bar
- En az 2 farklı konsept yönü sunulmalı — tek seçenek sunulmaz.
- Her konsept için renk yönü, tipografi yönü ve görsel dil ayrı ayrı tanımlanmış olmalı.
- Konsept önerisi "biz bunu seviyoruz" değil, iş gerekçesiyle desteklenmeli.
- Müşteriye en az 2 açık soru yöneltilmeli — belirsizlikler giderilmeden BRAND_IDENTITY'ye geçilmez.
- Referans analizi brief'teki görsellere dayalı olmalı — varsayımlara dayanmamalı.

## Tools
- Renk ilişkilendirme için renk psikolojisi referansları (kültürel bağlam dahil — Türk pazarına özgü çağrışımlar not edilir).
- Tipografi sınıflandırması: Serif / Sans-Serif / Slab Serif / Script / Display kategorileri kullanılır.

## Integration
- Tüm tasarım çalışmalarının başlangıç noktasıdır — diğer tüm skill'ler bu çıktıyı temel alır.
- BRAND_IDENTITY skill'i bu konsept kararlarını somut tasarım sistemine dönüştürür.
- Onaylanan konsept `MEMORY.md`'ye kaydedilir; ilerideki müşteriler için kalıp oluşturur.
