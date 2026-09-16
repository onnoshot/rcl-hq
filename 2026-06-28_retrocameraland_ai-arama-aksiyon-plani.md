# Retrocameraland — Yapay Zeka Aramaları (GEO/AEO) Büyüme Aksiyon Planı

Tarih: 2026-06-28 · Hazırlayan: Hermes (CEO analiz) + derin internet/rakip/site araştırması
Kapsam: AI aramalarından gelen trafiği artırmak ve bu aramalardaki sonuçları (metin, görsel, SEO) kusursuzlaştırmak.

---

## 0. Yönetici Özeti (tek sayfa)

**Gerçek:** RCL'nin AI-arama trafiği KÜÇÜK ama HIZLI büyüyor ve YÜKSEK NİYETLİ. Son 90 günde 579 oturum yapay zeka motorlarından geldi; bunun **~%95'i ChatGPT**. Perplexity, Copilot ve Bing'den pratikte **sıfır**, Gemini ve Claude'dan çok az. ChatGPT trafiği yıllık ~5 kat büyüdü (Tem'25: 2 → May'26: 245 oturum/ay).

**Neden önemli:** AI trafiği site ortalamasından daha iyi dönüşüyor. ChatGPT'den gelen 550 oturum 1 sipariş (14.490 TL, ortalamanın üstü sepet) getirdi; oturum başına dönüşüm site ortalamasının ~1.8 katı. Bu kanal büyüdükçe değeri orantısız artacak.

**Üç cümlelik teşhis:**
1. **Altyapı iyi durumda** (robots tüm AI botlarına açık, schema büyük ölçüde doğru, içerik sunucu-tarafı HTML). Engel yok; eksik olan zenginleştirme.
2. **İçerik tarafında RCL Türkçe "nereden/hangisi" sorgularını #1 kazanıyor** ama **karşılaştırma sorguları, model-bazlı inceleme/örnek-foto sorguları ve site-dışı otorite (Reddit, Trustpilot, listicle) tamamen boş** — yani AI bizi "kendi sayfamızı sıralıyor" ama "tavsiye edilen mağaza olarak alıntılamıyor".
3. **AI çoğunlukla İngilizce `/en/` sayfalarına ve global kitleye yönlendiriyor** (Türkiye 301, ama Filipinler/ABD/G.Kore/Almanya da var) — İngilizce içerik AI'da daha çok alıntılanıyor, bu büyütülmeli.

**En yüksek kaldıraçlı 5 hamle (detaylar aşağıda):**
1. Ürün schema'sında **stok-gerçek çelişkisini düzelt** (InStock derken sayfada "tükendi") + **AggregateRating/Review ekle**. (Düzeltme + en büyük "alıntılanabilirlik" kaldıracı)
2. **Marka-vs-marka karşılaştırma kütüphanesi** kur (Canon vs Sony vs Nikon vs Fuji "hangisini almalı") — TR ve EN. Türkçede sahibi yok.
3. **Model-bazlı inceleme + örnek foto sayfaları** (sattığımız her kamera için). Rakip 20 yıllık statik arşiv siteleri; taze + schema'lı + satın-al deep-link'li sayfa kazanır.
4. **Site-dışı otorite:** r/Digicams katılımı, Trustpilot profili, "best digicam" listicle'larına girme, YouTube tohumlama. AI ürün tavsiyelerinde üçüncü-taraf onayına büyük ağırlık veriyor.
5. **AI görünürlük ölçümü kur** (GA4 AI kanalı + ücretsiz izleme) ki yaptığımızın etkisini görelim.

---

## 1. Veri: AI aramaları nereden geliyor, insanlar ne arıyor

### 1.1 Kaynak kırılımı (GA4, son 90 gün)
| Kaynak | Oturum | Not |
|---|---|---|
| **chatgpt.com** | **~549** | Tüm AI trafiğinin ~%95'i. (329 "(not set)" + 124 referral + 96 ai-assistant) |
| gemini.google.com | 10 | Çok düşük |
| claude.ai | 7 | Çok düşük |
| bing organic | 13 | Çok düşük |
| **perplexity / copilot** | **0** | Tamamen boş — fırsat/kör nokta |
| **AI toplam** | **579** | ~193/ay ve büyüyor |

> Önemli ölçüm notu: GA4'ün hazır "AI Assistant" kanalı bunun sadece 104'ünü yakalıyor; gerçek sayı ~5 katı. ChatGPT yönlendirmeleri "(not set)"/"referral" olarak yanlış sınıflanıyor. **Aksiyon: GA4'te özel "AI Trafiği" kanal grubu tanımla** (kaynak regex: `chatgpt|openai|perplexity|gemini|claude|copilot|bing|you.com`), Referral'ın ÜSTÜNE al.

### 1.2 Büyüme trendi (ChatGPT, aylık oturum)
```
Tem'25:  2    Eki'25: 16    Oca'26: 123    Nis'26: 152
Ağu'25: 20    Kas'25: 57    Şub'26: 106    May'26: 245  <- zirve
Eyl'25: 28    Ara'25: 82    Mar'26: 115    Haz'26: 150 (kısmi ay)
```
Yıllık ~5 kat bileşik büyüme. Bu kanal yatırım yapılırsa orantısız büyür.

### 1.3 AI nereye yönlendiriyor (gerçek landing page'ler)
- Çoğunluk **`/en/blogs/retro-dijital-kamera/...`** İngilizce blog sayfaları (rehber-2026, kameradan-telefona-aktarma, canon-ixus, modeller-fiyatlari).
- Ardından **ürün sayfaları** (nikon-coolpix-885, casio-exilim-ex-z85, sony-cybershot-s85, kodak-slice-r502).
- **Çıkarım:** AI, bilgi/rehber içeriğini alıntılayıp oradan ürüne köprü kuruyor. İngilizce içerik AI'da daha görünür.

### 1.4 Kim geliyor + nasıl davranıyor
- Ülke: **Türkiye 301**, Filipinler 20, ABD 20, G.Kore 17, Almanya 14, ... (global kuyruk gerçek).
- Etkileşim: ChatGPT %79.5 (site %88), 132 sn, 3.3 sayfa/oturum — sağlam.
- **Dönüşüm: 550 oturum → 1 sipariş, 14.490 TL.** Oturum başına dönüşüm site ortalamasının ~1.8 katı, sepet ~%14 yüksek. AI trafiği premium ve satın almaya yakın.

---

## 2. Nerede İYİYİZ / Nerede KÖTÜYÜZ

### İyi (koruyalım)
- **robots.txt tüm AI botlarına açık** (OAI-SearchBot, GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended, bingbot). Kaza yok. Sitemap bildirilmiş.
- **Schema temeli sağlam:** ürünlerde Product+Offer (fiyat, para birimi, `itemCondition: UsedCondition`), BreadcrumbList, OfferShippingDetails; bloglarda Article + **FAQPage** + datePublished/Modified; ana sayfada WebSite+Organization+sameAs; SSS sayfasında FAQPage.
- **Fiyat/stok/spec görünür düz HTML'de** (JS-only değil) — AI okuyabiliyor.
- **TR/EN paritesi gerçek** (makine fallback değil, tam çeviri + paralel schema). hreflang tam (tr/en/de/fr/it/ja/pt/ar).
- **İçerik tonu doğal**, AI-slop değil; soru-tipi H2'ler, cevap-önce açılışlar, iç linkler var.
- **Native `/llms.txt` (kök) mevcut** ve doğru (agentic commerce / UCP).
- **Türkçe "nereden alınır" ve "en iyi modeller 2026" sorgularında #1**.

### Kötü / Eksik (düzeltilecek)
| Sorun | Etki | Tür |
|---|---|---|
| **Offer `availability: InStock` ama sayfa "tükendi" diyor** | AI'yı ve Google'ı yanıltır, güven düşürür | Hata (acil) |
| **Hiçbir yerde AggregateRating/Review YOK** (schema + görünür) | Ürün tavsiyesinde en büyük eksik | Kritik |
| **Karşılaştırma sorgularında tamamen yokuz** (Canon mı Sony mi) | En yüksek-niyetli karar içeriği rakiplerde/forumlarda | Kritik içerik boşluğu |
| **Model-bazlı inceleme/örnek-foto sayfası yok** (DSC-S85, Coolpix 885...) | Her SKU bir sorgu; hepsi DPReview/PBase'e gidiyor | Büyük boşluk |
| **Site-dışı sıfır otorite:** Reddit yok, Trustpilot yok, hiçbir bağımsız listicle'da yok | AI üçüncü-taraf onayına ağırlık verir; biz "kendi sayfamızı" sıralıyoruz | Kritik |
| Rehberlerde **hiç `<table>` yok** (spec/karşılaştırma tablosu) | AI tabloyu öncelikli çıkarır | Orta |
| Koleksiyon sayfalarında **ItemList/CollectionPage schema yok** | AI kataloğu sayamıyor ("RCL ne satıyor") | Orta |
| Ürün sayfalarında **on-page FAQ bloğu yok** (blogda var) | Ürün-seviyesi AI cevabını beslemiyor | Orta |
| **İsimlendirilmiş/kodlanmış test-kalite sistemi yok** (KEH/Kamerastore gibi) | E-E-A-T + alıntı yemi kaçıyor | Orta |
| `/pages/llms-txt` (HTML) yanıltıcı, içerik indeksi değil | Düşük | Küçük |
| Yazar E-E-A-T zayıf (jenerik "RetroCameraLand") | Otorite sinyali | Küçük |

---

## 3. Rakipler ne yapıyor, biz ne yapmıyoruz

**Türkiye:** Hiçbir Türk rakip (küratörlü + test/garanti + gerçek e-ticaret + derin SEO + koleksiyon konumlandırma) kombinasyonunu bizim gibi yapmıyor. En yakın içerik rakibi **mndstore.com** (blog yazıyor), en yakın topluluk rakibi **@digicameraistanbul** (~23K IG ama SEO yok). **Türkçe CCD/digicam bilgi katmanı neredeyse tamamen sahipsiz — bunu biz almalıyız.**

**Global liderlerin yaptığı, bizde olmayanlar:**
1. **İsimlendirilmiş kalite/derecelendirme sistemi** (KEH "BGN/EX+", Kamerastore "Restored/Certified") + açıklayıcı sayfa → güveni arama territoryasına çevirir.
2. **Radikal test-şeffaflığı içeriği** (Kamerastore "nasıl test ediyoruz") → E-E-A-T + kazanılmış medya.
3. **Model-bazlı örnek-foto galerileri** (Classic DigiCam, ExploreCams) → yüksek AI-alıntı değeri; bizim tek-adet envanterimizle eşsiz eşleşir.
4. **Marka-vs-marka karşılaştırma rehberleri** (Vintage Camera Hut) → en çok aranan karar sorgusu, Türkçe sahibi yok.
5. **Yapılandırılmış model/spec veritabanı** (digicamdb, Digicam Finder) → AI'nın gerçek için kazıdığı kaynak; Türkçesi yok.
6. **Ürün sayfasında ölçek + sosyal kanıt** (SoCal "30.000 satıldı, %97 beş yıldız", görünür garanti rozeti).
7. **İçerik-beslemeli büyük IG/TikTok topluluğu + çekilişler** (MPB ~221K, Digicam Vault ~157K).
8. **Yaratıcı-liderliğinde "markaya göre look" video içeriği** (TikTok/Reels) — metin zenginiz, video formatında zayıf.

**Trend tarafı (2026):** CCD/Y2K trendi kalıcı platoda; ikinci-el kompakt fiyatları ~20x arttı (bizim "tek adet, test edilmiş" modeli iyi zamanlanmış). **Yeni tehdit:** Instagram'ın AI "Flash" filtresi (May'26) viral oldu — look'u bedava taklit ediyor → **gerçeklik + donanım deneyimi + küratörlük** üzerinden farklılaşmalıyız. "Gerçek CCD vs Instagram AI flash filtresi" içeriği henüz kimsede yok; hızlı alınır.

---

## 4. AKSIYON PLANI (fazlı, önceliklendirilmiş)

### FAZ 0 — Acil düzeltmeler (bu hafta, düşük efor)
0.1 **Stok-schema senkronu:** Satışta olmayan üründe Offer `availability` = `OutOfStock` döndür; `priceValidUntil` ekle. (Tema/şablon düzeltmesi; tüm ürünlere yayılır.)
0.2 **GA4 "AI Trafiği" özel kanalı** tanımla (regex yukarıda), Referral üstüne al; ChatGPT'nin bozuk UTM'i için `utm_medium=(not set)` OR koşulu ekle. Böylece gerçek AI etkisini ölçeriz.
0.3 **Google Search Console "Generative AI" raporunu** kontrol et (AI Overviews maruziyeti GA4'te görünmez; gerçekten sıfır mı yoksa ölçüm körlüğü mü öğren).
0.4 `/pages/llms-txt` HTML sayfasını ya sil ya da **küratörlü içerik indeksine** çevir (en iyi rehberler + top koleksiyonlar + SSS linkleri).

### FAZ 1 — On-site AEO zenginleştirme (1-3 hafta, yüksek kaldıraç)
1.1 **Ürün schema'sına AggregateRating + Review ekle** ve **görünür yorum bloğu** koy. Yorum uygulaması (Judge.me/Loox) kur veya gerçek müşteri yorumlarını + müşteri örnek fotoğraflarını topla; yıldız + adet HTML'de görünsün. (Tek en büyük alıntılanabilirlik kaldıracı.)
1.2 **Mevcut 300+ blogu çıkarılabilirlik için yeniden yapılandır** (zaten otorite var): her H2 soru-tipi, altında 40-75 kelimelik kendi kendine yeten doğrudan cevap, içine **istatistik + uzman alıntısı + kaynak** enjekte et. Princeton GEO çalışması: alıntı +%41, istatistik +%32, kaynak +%30 görünürlük. → `rcl-blog-refresh.py` ile yarı-otomatik yapılabilir.
1.3 **Spec ve karşılaştırma tabloları ekle:** amiral rehbere model-karşılaştırma tablosu (MP, yıl, sensör, fiyat); her ürüne spec tablosu. (AI tabloyu 2.5-4.2x daha çok alıntılıyor.)
1.4 **Koleksiyon sayfalarına ItemList + BreadcrumbList schema** ekle (AI kataloğu sayabilsin).
1.5 **Ürün sayfalarına on-page FAQ bloğu + FAQPage schema** (ör. "885 video için iyi mi? batarya tipi? garanti?").
1.6 **Yazar E-E-A-T:** rehberlerde isimli yazar + kısa biyografi + `sameAs`.

### FAZ 2 — İçerik motoru: AI'nın alıntılayacağı yeni varlıklar (2-8 hafta)
2.1 ✅ **TAMAMLANDI (2026-08-23):** Marka-vs-marka karşılaştırma kütüphanesi otomatik blog motoruna gömüldü — `rcl-seo-blog-agent.py`'de `content_type: brand_comparison` yeni bir konu-tipi rotasyonunda (model_review/brand_comparison/buying_guide/general_photography, 4'te 1 oranında) düzenli üretiliyor. Karşılaştırma tablosu + gerçek stok fiyatlarıyla otomatik. TR şimdilik; EN paritesi henüz yok.
2.2 **Model-bazlı inceleme + örnek-foto sayfaları** (sattığımız her kamera): "Sony DSC-S85 inceleme + örnek fotoğraflar", "Nikon Coolpix 885 örnek çekimler". Product+Review schema + satın-al deep-link. Rakip 20 yıllık statik siteler; taze içerik kazanır. **Tek-adet envanterle eşsiz:** her kameranın gerçek örnek karelerini koyabiliriz.
2.3 **Türkçe CCD/digicam model veritabanı** (spec + yıl + örnek galeri). AI'nın gerçek için kazıyacağı kaynak; Türkçesi yok. → programmatic-seo şablonu ile ölçekte üretilebilir.
2.4 **"Gerçek CCD vs Instagram AI flash filtresi" açıklayıcısı** (TR + EN) — viral anı yakala, farklılaşma argümanı.
2.5 **İsimlendirilmiş test/kalite-derecelendirme sayfası** ("RCL Kalite Standardı: nasıl test ediyoruz, 10/10 ne demek") — KEH/Kamerastore modeli; güveni arama territoryasına çevir, E-E-A-T + alıntı yemi.
2.6 **"CCD fotoğraf makinesi" disambiguasyon sayfası** (Türkçede "CCD kamera" CCTV/güvenliğe kaçıyor — niyeti netleştir).
2.7 **Sezonsal hediye rehberi** ("nostaljik / retro dijital kamera hediyesi") — pazaryeri-hakimiyetindeki hediye sorgusunu zorla.
> Mevcut tema kararı korunuyor: her 2 blogtan 1'i öğrenci/sevgili temasında (THEME_DEADLINE 2026-07-01) — yeni içerikler bununla uyumlu planlanmalı.

### FAZ 3 — Site-dışı otorite (en büyük tek kaldıraç, sürekli)
3.1 **Reddit r/Digicams + r/VintageCameras:** şeffaf markalı hesap, bir çeyrek boyunca gerçek uzmanlıkla ısıt (CCD renk bilimi, 2005-dönemi tedarik, örnek kareler), küçük bir alt-toplulukta AMA. AI motorları digicam tavsiyesinde Reddit'i #1 alıntılıyor. (F5Bot ile marka takibi — ücretsiz.)
3.2 **Trustpilot profili aç** + müşterileri yönlendir (4.0+, 50+ yorum hedefi). Rakiplerin var, bizim yok. Hem alıcı hem AI güven sinyali.
3.3 **"Best CCD / retro digicam" listicle'larına gir:** yazarlara doğrudan ulaş + ürün tohumla; özgün linklenebilir veri üret ("2026 CCD digicam fiyat durumu", sensör-yaşlanma çalışması) → dijital PR.
3.4 **YouTube tohumlama:** "CCD look" uygulamalı demolar (e-ticaret AI Overview'ların #1 kaynağı YouTube).
3.5 **Entity inşası:** Organization sameAs (Wikipedia/Wikidata/Crunchbase/LinkedIn), tutarlı marka bahisleri. AI bizi "tanınan varlık" yapmadan tavsiye edemez.

### FAZ 4 — Görsel strateji (metin kadar önemli)
4.1 **Model başına gerçek örnek-foto galerileri** (RAW look, flaşlı gece, gündüz) — hem AI multi-modal seçimini (+%156) hem alıcı kararını besler.
4.2 **Ürün sayfasında "gerçek ürünün fotoğrafı" vurgusu** (stok görseli değil; tek-adet, gerçek kondisyon). Vitrin görsel yenileme (cutout, #F0F6FC) projesiyle uyumlu tut.
4.3 **Test-şeffaflığı görselleri** (kamera test masası, "10/10 ne demek" görsel anlatım).
4.4 **Karşılaştırma görselleri/infografik** (Canon vs Sony renk paleti yan yana).
4.5 **Sosyal/video varlıkları** (Lacivert/beyaz lüks minimal stil DNA'sı; script+sans-serif font) — "markaya göre look" Reels.
> Görseller AI tarafında alt-text + görünür caption + ImageObject schema ile sunulmalı; AI görseli sadece dosya değil, bağlamıyla okur.

### FAZ 5 — Ölçüm & izleme (sürekli)
5.1 GA4 AI kanalı (Faz 0.2) + aylık AI-oturum/dönüşüm raporu (Hermes panele eklenebilir).
5.2 **Ücretsiz AI görünürlük izleme:** Hall (ücretsiz, 25 prompt), gerekirse Otterly (~$25/ay). Aylık TR+EN ~15-20 satın-alma-niyetli prompt sepetini 3 motorda çalıştır, marka bahsi/pozisyon/sentiment kaydet.
5.3 **Sunucu loglarında AI bot ziyaretlerini doğrula** (OAI-SearchBot, PerplexityBot, ClaudeBot, bingbot) — kazımıyorlarsa alıntı da yok.
5.4 **Bing Webmaster Tools + IndexNow** kur (Copilot + Yandex'i besler, ChatGPT'yi de güçlendirir).

---

## 5. 30 / 60 / 90 Gün Takvimi

**0-30 gün (temel + acil):**
- Faz 0 tamamı (stok-schema bug, GA4 AI kanalı, GSC AI raporu, llms-txt).
- Faz 1.1 (yorum/AggregateRating), 1.3 (tablolar), 1.4 (ItemList).
- Faz 3.2 (Trustpilot aç), 3.1 başlat (Reddit hesabı ısıtma).
- İlk 2 karşılaştırma rehberi (2.1) + ilk 5 model inceleme sayfası (2.2, en çok AI-trafiği alan ürünler: nikon-coolpix-885, casio-exilim-ex-z85, sony-cybershot-s85, kodak-slice-r502, canon-ixus).

**30-60 gün (içerik motoru):**
- 300+ blog yeniden-yapılandırma dalga 1 (1.2) — en çok AI-trafiği alan 30 yazı.
- 10 karşılaştırma + 20 model inceleme sayfası daha.
- "Gerçek CCD vs AI flash" (2.4) + test-kalite sayfası (2.5).
- Örnek-foto galerileri dalga 1 (4.1).
- Reddit AMA + ilk listicle outreach (3.3), YouTube ilk 2 demo (3.4).

**60-90 gün (otorite + ölçek):**
- Türkçe CCD model veritabanı (2.3) programmatic.
- Blog yeniden-yapılandırma dalga 2 + EN paritesi.
- Entity/Wikidata (3.5), IndexNow/Bing (5.4).
- AI görünürlük izleme rutini (5.2) + ilk aylık rapor; ne işe yaradığını ölç, ikiye katla.

---

## 6. KPI'lar (başarıyı nasıl ölçeriz)

| KPI | Bugün (90g) | 90 gün hedef | 180 gün hedef |
|---|---|---|---|
| AI-arama oturumu / ay | ~193 | 350 | 600+ |
| AI kaynak çeşitliliği | ~%95 ChatGPT | Perplexity+Gemini'den ölçülebilir trafik | 3+ motor anlamlı |
| AI'da marka bahis oranı (TR+EN prompt sepeti) | ölçülmüyor | baseline + %30 | tavsiye edilen mağaza |
| Model inceleme / karşılaştırma sayfası | ~0 | 30 | 80 |
| Trustpilot yorum | 0 | 30 | 60 |
| Reddit/listicle bağımsız bahis | 0 | 5 | 15 |
| AI trafiği dönüşüm (oturum başı) | ~%0.18 | korunur/artar | site ort. üstü kalıcı |

---

## 7. Mevcut otomasyonla bağlantı (ne ile yapılır)
- Blog yeniden-yapılandırma + görsel/SEO: `rcl-blog-refresh.py` (235 blog, geri alınabilir), `rcl-blog-qa-monitor.py` (5 boyut denetim).
- Yeni içerik üretimi: `programmatic-seo` + `content-creator` skill'leri; GEO yayını: `rcl-geo-publish-batch.py`, `rcl-geo-deploy.py`.
- Ürün şablonu: onaylı `RCL Shopify ürün açıklama şablonu` (spec tablosu + FAQ ekleyerek genişlet).
- Schema/section: `schema-markup` skill + Shopify MCP (`validate_theme`).
- Ölçüm: GA4 fetch script'i genişlet (AI kanalı), Hermes paneline AI-trafiği kartı.

---

## Ek: Kaynak özeti
GEO/AEO 2026 (Zyppy 54-çalışma, Princeton GEO, Ahrefs marka-vs-backlink, Seer 800K yanıt/yorum, OpenAI bot/feed dokümanları, Shopify agentic storefronts); rakipler (MPB, KEH, Kamerastore, Vintage Camera Hut, SoCal, Digicam Vault; TR: mndstore, @digicameraistanbul); trend (Phoblographer, Dazed, r/Digicams, Instagram Flash filtresi). Tam URL listeleri araştırma çıktılarında.
