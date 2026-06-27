# Marka logoları (opsiyonel)

Bu klasöre resmi marka logosu PNG'leri koy; build otomatik base64 gömer ve
hem sonuç kartlarında hem de paylaşım görselinde gösterir. Dosya yoksa şık
metin marka adına döner.

Dosya adı = marka anahtarı (küçük harf, .png):
  sony.png  canon.png  fujifilm.png  olympus.png  lumix.png
  kodak.png  nikon.png  casio.png  sanyo.png  panasonic.png ...

İpuçları:
- Şeffaf arka planlı (PNG alfa) olsun.
- Yatay/wordmark logo tercih et; ~200-600px genişlik yeterli (build küçültür).
- Paylaşım görseli SİYAH zeminde; logo beyaz çip içinde gösterilir, bu yüzden
  koyu/renkli logo da sorunsuz görünür.
- Sonuç kartları AÇIK zeminde; koyu/renkli logo iyi durur.
- Kazıma yok: resmi marka varlık/press-kit PNG'lerini kullan.

Ekledikten sonra:  python3 build_finder.py
