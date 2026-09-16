# Skill: Speaker Reframe

## Purpose
Seçilen bir zaman aralığını, her alt-sahne (kamera kesimi) için sabit bir kadraj hesaplayıp yatay (16:9) kaynaktan dikey (varsayılan 2160x3840, 9:16) bir klibe dönüştürmek — kadraj sahne içinde hiç kaymaz, sadece kesim noktalarında değişir.

## Serves Goals
- Kadraj kalitesi
- Üretim maliyeti (yerel işlem, kredi harcamaz)

## Process
1. Seçilen zaman aralığını, videonun genelindeki sahne kesim noktalarıyla (HIGHLIGHT_DETECTION'ın bulduğu `boundaries`) alt-sahnelere böl. 1 saniyeden kısa alt-sahneler (kesim noktası tam kare sınırında değilse oluşan sahte mikro-kesitler) komşusuna birleştirilir.
2. Her alt-sahne için: sahne boyunca ~0.4 sn aralıklarla örnek kareler al, her birinde `YuNet` ile yüz tespit et.
3. Alt-sahnedeki tüm örneklerin **medyan** yüz konumu ve boyutunu al (tek karelik sapmalardan etkilenmesin diye ortalama değil medyan).
4. Bu medyan değerden **tek, sabit** bir kırpma kutusu hesapla (yüz boyutuna göre zoom seviyesi, kadrajın ~%38'inde yüz için baş payı) — bu kutu o alt-sahnenin tamamında değişmez.
5. Alt-sahnede hiç yüz bulunamazsa (ör. geniş plan/B-roll), zoom yapmadan orijinal görüntünün merkezinden standart 9:16 kırpma uygulanır.
6. Kare kare yazım geçişinde her karenin ait olduğu alt-sahnenin sabit kutusunu kullan — hiçbir yumuşatma/kayma yok, kadraj yalnızca alt-sahne değiştiğinde (kamera kesimi = genelde konuşan kişi değişimi) değişir.
7. Kırpılan bölgeyi hedef çözünürlüğe `LANCZOS4` ile ölçekle, ham kareleri `ffmpeg` pipe'ına yaz; `ffmpeg` aynı anda orijinal ses parçasını segment için mux'lar.

## Outputs
- `.mp4` dikey klip (H.264, AAC ses, hedef çözünürlükte)

## Quality Bar
- Çıktı çözünürlüğü tam olarak istenen genişlik/yükseklik.
- Bir alt-sahne içinde kadraj **hiç** kaymaz/titremez — tamamen sabit.
- Kadraj yalnızca gerçek bir kamera kesiminde değişir, ani/keyfi sıçrama olmaz.
- Ses, görüntüyle senkronize ve orijinal kaliteyle korunmuş.

## Tools
- `scripts/reframe_speaker.py` — CLI + `reframe()` fonksiyonu (`shot_boundaries` parametresiyle çağrılır)
- Bağımlılık: `ffmpeg`, `opencv-python`, `models/face_detection_yunet.onnx`

## Integration
`HIGHLIGHT_DETECTION`'ın seçtiği her aday pencere + o videonun tam sahne sınırları listesi (`boundaries`) birlikte verilir; `scripts/make_short.py` bu zinciri otomatikleştirir ve çıktıları `outputs/`'a tarih damgalı isimlerle yazar.

## Learnings
- **v1 (kare-kare EMA takip) kullanıcı tarafından reddedildi:** "yüz hareket ettikçe ekran onunla kayıyor, titreşim oluyor" geri bildirimi üzerine sürekli takip yerine sahne-başına-sabit-kadraj yaklaşımına geçildi (2026-07-16). Detay: [[../MEMORY.md]]
