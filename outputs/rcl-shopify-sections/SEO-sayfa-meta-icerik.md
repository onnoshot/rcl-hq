# RCL Sayfa SEO + GEO — Meta Açıklamaları & İçerikler

İki sayfanın Shopify'daki **Arama motoru listeleme (SEO)** alanlarını ve gövde içeriklerini
güçlü Google SEO + GEO (yapay zekâ arama motorları: ChatGPT, Perplexity, Gemini, Google AI Overviews)
uyumlu olacak şekilde doldurmak için hazır metinler.

**Nereye giriliyor?** Shopify Admin → **Online Store → Pages → (sayfa)** → en altta
**"Search engine listing" / "Arama motoru listelemesini düzenle"** bölümü:
- *Page title* = aşağıdaki **Sayfa başlığı (meta title)**
- *Description* = aşağıdaki **Meta açıklama**
- *URL handle* = aşağıdaki handle (zaten doğruysa dokunma)

---

## 1) Hangi Kamera Bana Uygun?  ·  handle: `hangi-kamera-bana-uygun`

### Sayfa başlığı (meta title) — 48 karakter
```
Hangi Kamera Bana Uygun? | AI Retro Kamera Testi
```

### Meta açıklama — 152 karakter
```
5 soruluk ücretsiz AI testiyle sana en uygun retro dijital CCD kamerayı saniyeler içinde bul. Stoktaki modeller arasından yüzdesel uyumla kişisel öneri al.
```

**Alternatif başlık seçenekleri:**
- `Sana Hangi Retro Dijital Kamera Uygun? | AI Test`
- `Bana Uygun Kamera Testi | RetroCameraLand AI`

**Alternatif meta açıklama:**
```
Tarzını, bütçeni ve ihtiyacını anlayan yapay zekâ, stoktaki retro dijital kameralar arasından sana en uygun 3 modeli yüzdesel uyumla önerir. Ücretsiz, üyelik yok.
```

### Gövde içeriği — GEREK YOK ✅
Bu sayfanın taranabilir SEO içeriği (H2 "Hangi retro dijital kamera sana uygun?" + açıklama +
4 kategori iç-link + 5 SSS akordeon + JSON-LD: WebApplication, HowTo, FAQPage, Organization, Breadcrumb)
**zaten `rcl-camera-finder` section'ı tarafından üretiliyor.** Sayfa gövdesine ekstra metin eklemene
gerek yok; yalnızca yukarıdaki iki meta alanını doldurman yeterli.

> İstersen sayfa gövdesi (rich-text) en üstüne tek cümlelik GEO girişi ekleyebilirsin:
> `RetroCameraLand AI Kamera Eşleştirici; kullanım amacın, bütçen, estetik tercihin, çekim ortamın ve deneyim seviyene göre şu an stokta olan retro dijital CCD kameralar arasından sana en uygun üç modeli yüzdesel uyum skoruyla öneren ücretsiz bir akıllı kamera bulma testidir.`

---

## 2) Time Capsule (Topluluk)  ·  handle: `topluluk`

### Sayfa başlığı (meta title) — 49 karakter
```
Time Capsule | Dünyanın İlk Dijital Kamera Arşivi
```

### Meta açıklama — 150 karakter
```
2000'lerin CCD dijital kameralarını ve onlarla çekilen kareleri bir araya getiren dünyanın ilk retro kamera arşivi ve topluluğu. Keşfet, beğen, anını sakla.
```

**Alternatif başlık seçenekleri:**
- `Time Capsule | Retro Dijital Kamera Topluluğu`
- `Dijital Kamera Anıları Arşivi | Time Capsule`

**Alternatif meta açıklama:**
```
Y2K dijital kameralarının ve fotoğraflarının yaşadığı ilk topluluk. Yüzlerce CCD kamerayı keşfet, beğenerek sırala, çektiğin kareyi yükle; rozet ve indirim kazan.
```

### Gövde içeriği — JSON-LD eklendi ✅ + (opsiyonel) GEO metni
Time Capsule sayfası bir uygulama olduğu için taranabilir metni zayıftı. Bunu güçlendirmek için
section'a **Organization + BreadcrumbList + FAQPage (5 soru-cevap)** JSON-LD'si **eklendi**
(GEO/AI aramaları için). Mevcut tanıtım paragrafı da korunuyor.

Sayfanın gövde (rich-text) içeriğini de doldurmak istersen — *diğer sayfalardaki gibi güçlü SEO metni*
— aşağıdaki HTML'i **Pages → Time Capsule → içerik (kod görünümü `<>`)** alanına yapıştır:

```html
<h2>Time Capsule nedir?</h2>
<p><strong>Time Capsule</strong>, 2000'lerin CCD dijital kameralarını ve onlarla çekilen kareleri
tek bir dijital arşivde toplayan <strong>dünyanın ilk retro kamera topluluğudur</strong>. Y2K
estetiğini ve dijital fotoğrafçılığın o ilk büyülü dönemini yaşatmak için yüzlerce kamerayı belgeler,
en sevilenleri topluluk beğenileriyle sıralar ve herkesin anısını silinmeyecek şekilde geleceğe taşır.</p>

<h2>Toplulukta neler yapabilirsin?</h2>
<ul>
  <li><strong>Keşfet:</strong> Yüzlerce retro dijital kamerayı marka, model ve yıla göre incele.</li>
  <li><strong>Beğen &amp; sırala:</strong> En sevdiğin kameralara beğeni vererek topluluk sıralamasını belirle.</li>
  <li><strong>Anını paylaş:</strong> Çektiğin kareyi tarihi, yeri ve o ana dair düşüncenle kameranın kartına yükle.</li>
  <li><strong>Görevle kazan:</strong> Görevleri tamamladıkça rozet topla, sana özel indirim kodlarının kilidini aç.</li>
</ul>

<h2>CCD dijital kamera nedir?</h2>
<p>CCD sensörlü 2000'ler kompakt kameraları; flaşlı gece estetiği, filmsi renkler ve hızlı
point-and-shoot pratikliğiyle <strong>Y2K görüntü karakterini</strong> birebir yakalar. Bu nostaljik
doku, modern telefon kameralarından belirgin biçimde farklıdır ve son yıllarda yeniden popülerleşmiştir.</p>

<h2>Sıkça sorulan sorular</h2>
<p><strong>Time Capsule'e nasıl katılırım?</strong><br>
RetroCameraLand hesabınla ücretsiz giriş yaparak katılırsın; ardından kameraları keşfeder, beğenir ve
çektiğin fotoğrafları yükleyebilirsin.</p>
<p><strong>Time Capsule ücretsiz mi?</strong><br>
Evet, tamamen ücretsizdir. RetroCameraLand üyeliğiyle anında katılırsın.</p>
<p><strong>Hangi kamera bana uygun, nasıl öğrenirim?</strong><br>
<a href="/pages/hangi-kamera-bana-uygun">AI Kamera Eşleştirici testimizi</a> doldurarak sana en uygun
retro dijital kamerayı saniyeler içinde öğrenebilirsin.</p>
```

> Not: Yukarıdaki HTML iç-link olarak Kamera Bulucu testine bağ veriyor → iki sayfa birbirini besler
> (iç linkleme = SEO sinyali). FAQ kısmı GEO için soru-cevap formatında.

---

## GEO/AEO İpuçları (her iki sayfa için)
- **Net, iddialı cümleler** kullan ("dünyanın ilk…", "5 soruda…") → AI motorları bunları alıntılar.
- **Varlık (entity) zenginliği:** marka adları (Sony, Canon, Fujifilm, Kodak…), "CCD", "Y2K", "2000'ler"
  geçsin → konu otoritesi.
- **Soru-cevap blokları** (FAQPage şeması) zaten her iki section'da var → AI Overviews/Perplexity için ideal.
- robots.txt ve llms.txt'de bu iki sayfanın AI crawler'lara açık olduğundan emin ol (mevcut GEO kurulumunda var).
- İç linkleme: Kamera Bulucu ↔ Time Capsule ↔ koleksiyon/ürün sayfaları.
