# HMT CUP 2027 — Web Sitesi Geliştirme Brifi (v2)

Bu döküman, kullanıcının orijinal geliştirme promptunun üzerine kararlaştırılan eksikleri tamamlar. Orijinal prompt hâlâ geçerli; burada sadece **değişen/eklenen** kararlar var.

## Karara Bağlanan Noktalar

| Konu | Karar |
|---|---|
| Turnuva yılı | **2027** (tüm metinlerde bu kullanılacak) |
| Barındırma | Yeni ayrı proje: `hmt-cup-web/` → yeni Vercel projesi (`hmt-cup-2027` veya benzeri). `outputs/HMT_CUP/` (satış sunumu) dokunulmadan kalır |
| Domain | Kullanıcıdan alınmadı → geçici olarak Vercel subdomain'de yayında olacak, gerçek domain (örn. hmtcup.com / hmtcup.com.tr) bağlanınca DNS ayarı ayrıca yapılır |
| Logo | Önce 3 konsept üretilecek (Higgsfield/GPT Image 2), onay alındıktan sonra tüm görsellerde referans olarak kullanılacak |
| Backend | Yeni Supabase projesi kurulacak (`subscribers` tablosu + admin okuma) |
| Marka renkleri | Mevcut satış sunumundan (`outputs/HMT_CUP_Dijital_Strateji.html`) devralındı — aşağıda |

## Devralınan Marka Sistemi (mevcut strateji dökümanından)

```
--red-primary:   #CC0000
--red-bright:    #E82020   (hover/glow)
--red-dark:      #A50000
--ink:           #111111   (koyu zemin)
--gold-accent:   #D4A843   (ödül/prestij vurgusu, kullanım az)
--blue-accent:   #1A73E8   (gerekirse link/bilgi rengi, kullanım az)

Font: Bebas Neue (başlık/display) + Montserrat (gövde metin)
```

Bu palet zaten "koyu zemin + kırmızı vurgu, Champions League hissi" yönüyle örtüştüğü için birebir korunacak — sıfırdan renk kararı almaya gerek yok. Logo konseptleri de bu paletle üretilecek.

## Orijinal Promptta Bulunan ve Tamamlanan Eksikler

1. **Popup tetikleme mantığı** (orijinalde "belli süre sonra veya scroll noktasında" diye belirsiz bırakılmış):
   - Tetik: 15 saniye **VEYA** sayfanın %50'sine scroll — hangisi önce gerçekleşirse
   - Kapatılınca 7 gün boyunca tekrar gösterilmez (localStorage)
   - Zaten formu doldurmuş kullanıcıya bir daha gösterilmez

2. **Dashboard koruması**: Tam auth sistemi yerine basit şifre korumalı (tek admin şifresi, env variable + cookie session) — orijinal promptun "basit şifre/login" talebiyle örtüşüyor, over-engineering yapılmayacak.

3. **İstatistik sayıları (Turnuva Nedir bölümü)**: Kaç takım / kaç saha / hangi şehir gibi rakamlar promptta yok. **Antalya, 5-6 saha** biliniyor (Tesis bölümünden), takım sayısı/kategori sayısı henüz kullanıcıdan alınmadı — placeholder ile başlanacak (`XX+ Takım`, `X Kategori` gibi), gerçek rakamlar geldiğinde tek satır değişecek.

4. **Gerçek görsel/video yokluğu**: Turnuva 2027'de ilk kez yapılacağı için maç/kutlama/röportaj görsellerinin hiçbiri gerçek olamaz — tamamı Higgsfield/GPT Image 2 ile üretilecek "aspirasyonel" görsel. Bu görseller belirli, tanınabilir gerçek kişileri (ünlü oyuncu/hoca) temsil etmeyecek; jenerik/temsili sporcu ve saha sahneleri olacak — sahte onay/impersonation riski yok.

5. **Video içerik planı ile tutarlılık**: Mevcut strateji dökümanındaki Instagram video kategorileri (röportaj, saha atmosferi, vb.) ile site galerisi görsel dili tutarlı olacak — aynı "evren" hissi iki kanalda da korunacak.

6. **E-posta formu alanları**: E-posta zorunlu + isim opsiyonel (promptta zaten önerilmişti, onaylandı — doldurma oranını düşürmemek için tek zorunlu alan kalıyor).

## Teknik Stack (netleştirildi)

- Next.js 15 (App Router) + TypeScript
- Tailwind CSS
- Framer Motion (scroll reveal, parallax, sayı sayma)
- Supabase (yeni proje — `subscribers` tablosu: email, name, source, created_at)
- Vercel deploy
- next/image ile WebP/AVIF otomatik optimizasyon (Higgsfield çıktıları buraya beslenecek)

## Sonraki Adımlar (bu brief onaylandıktan sonra)

1. 3 logo konsepti üret → kullanıcı onayı
2. Next.js iskeleti + Tailwind + brand token'ları kur
3. Supabase projesi + `subscribers` tablosu + RLS
4. Bölümleri sırayla kodla (Hero → Turnuva Nedir → ... → Footer)
5. Popup + form entegrasyonu
6. `/admin` dashboard (şifreli, CSV export)
7. İçerik görselleri üret + optimize et + yerleştir
8. Mobil performans testi (Playwright + Lighthouse) → Vercel deploy
