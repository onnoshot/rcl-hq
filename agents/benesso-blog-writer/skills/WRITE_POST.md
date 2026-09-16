# Skill: Write Post (TR + EN)

## Purpose
Verilen keyword için SEO-odaklı, okunabilir bir blog yazısı üretmek — Türkçe ve İngilizce olarak.

## Serves Goals
- İçerik üretimi (günlük 3 yazı)
- Organik trafik artışı

## Inputs
- KEYWORD_RESEARCH skill'den gelen hedef keyword (TR + EN karşılığı)
- `knowledge/STRATEGY.md` — marka sesi, ton, yasaklı konular
- `MEMORY.md` — geçmişte iyi performans gösteren format/yapı

## Process

### TR yazı için:
1. Keyword'ü analiz et: kullanıcı niyeti nedir? (bilgi, satın alma, karşılaştırma)
2. Başlık yaz: keyword H1'de, tıklanabilir, 60 karakter altı
3. Giriş paragrafı: keyword ilk 100 kelimede geçmeli, okuyucuyu içine çek
4. Ana içerik: 3-5 H2 başlıkla organize et, 600-800 kelime
5. Kapanış: net bir CTA (ürün sayfasına link veya "daha fazla keşfet")
6. Meta description: 150-160 karakter, keyword içermeli

### EN yazı için:
7. Aynı yapıyı EN keyword karşılığıyla tekrarla
8. Doğrudan çeviri değil — EN kullanıcı niyetine göre yeniden yaz
9. EN meta description: 150-160 karakter

### Kalite kontrol:
10. TR ve EN her ikisi 400+ kelime mi?
11. Keyword başlıkta ve ilk paragrafta geçiyor mu?
12. Uydurma istatistik veya tarih var mı? → Kaldır

## Outputs
- TR blog içeriği (başlık + meta + body HTML)
- EN blog içeriği (başlık + meta + body HTML)
- SHOPIFY_PUBLISH skill'e input olarak geçer

## Quality Bar
- Minimum 400, ideal 600-800 kelime (her dil için ayrı ayrı)
- Keyword H1 başlıkta geçmeli
- İçerik özgün — daha önce yayınlanan yazılarla örtüşmemeli
- Marka sesi: samimi, bilgili ama akademik değil; kahve tutkusunu yansıtmalı
- Hiçbir yazı "AI tarafından yazıldı" hissi vermemeli

## Tools
- Claude API (yazı üretimi) — scripts/publish.py içinde çağrılır
- Dış tool yok; tek girdi dosyalar

## Integration
- KEYWORD_RESEARCH skill'den keyword alır
- Çıktıyı SHOPIFY_PUBLISH skill'e verir
- Başarılı yayın sonrası outputs/ klasörüne arşiv kopyası yazılır

## Benesso Marka Sesi Notları
- Kahveyi bir yaşam tarzı olarak sun, ürün satışı gibi değil
- Bilimsel ama erişilebilir: "çalışmalar gösteriyor ki" değil, "fark edeceksin ki"
- Türkçe: samimi "sen" dili; EN: conversational second person "you"
- Abartılı iddialar yasak: "dünyanın en iyi kahvesi" gibi ifadeler kullanma
