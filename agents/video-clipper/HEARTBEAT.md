# Video Clipper Heartbeat

## Schedule
Talep bazlı — kullanıcı bir video verip "kesit çıkar" dediğinde çalışır. Cron/otomatik döngü yok (kaynak video her seferinde insan tarafından sağlanıyor).

## Each Cycle

### 1. Read Context
- Kullanıcının verdiği video yolunu ve istenen klip sayısı/süre aralığını doğrula
- Kendi `MEMORY.md`'sini oku — geçmiş çalıştırmalardan zoom/kadraj ayarlarına dair öğrenilmiş bir şey var mı?

### 2. Assess State
- Video mevcut mu, ffprobe ile çözünürlük/süre/fps doğrulanabiliyor mu?
- Kaynak zaten dikeyse (9:16) reframe gereksiz — kullanıcıyı uyar
- Kaynak çok kısaysa (< min-dur) tüm videoyu tek klip olarak işle

### 3. Execute Skill
- Her zaman önce `HIGHLIGHT_DETECTION` çalışır (aday kesitleri bulur, puanlar)
- Ardından her seçilen aday için `SPEAKER_REFRAME` çalışır (dikey klip üretir)
- `scripts/make_short.py` bu iki skill'i tek komutta zincirler

### 4. Log to Journal
- Kaç klip üretildi, hangi zaman aralıklarından, hangi skorlarla
- Kullanıcının onayladığı/reddettiği klipler (geri bildirim varsa)
- Karşılaşılan teknik sorunlar (yüz tespit edilemedi, ffmpeg hatası vb.)

## Weekly Review
Bu agent talep bazlı çalıştığı için haftalık değil, **her çalıştırma sonrası** kullanıcıdan kısa geri bildirim istenir (hangi klipler işe yaradı, hangi kadrajlar kötüydü).

### 1. Gather Data
Kullanıcının hangi klipleri kullandığı/attığı, kadraj/zoom hakkında verdiği yorumlar.

### 2. Score Against Targets
| Metric | Target | Bu çalıştırma | Durum |
|--------|--------|----------------|-------|

### 3. Analyze Wins and Misses
- **Wins:** Hangi TARGET_FACE_FRACTION / EMA_ALPHA değerleri iyi sonuç verdi?
- **Misses:** Hangi sahne tiplerinde (ör. konuşmacı kameradan uzaklaşıyor, birden fazla kişi) kadraj bozuldu?

### 4. Update Memory
Doğrulanmış kalibrasyon değerlerini ve sahne tiplerine özel notları `MEMORY.md`'ye ekle.

### 5. Log Weekly Summary to Journal
Yalnızca birikmiş, tekrar eden bir öğrenme varsa journal'a özet gir.

## Escalation Rules
- Yüz hiç tespit edilemiyorsa (video boyunca face_presence ~0) — insana haber ver, elle kadraj/zaman aralığı iste
- Kaynak video 4K'dan düşükse ve kullanıcı 2160x3840 istiyorsa — yukarı ölçeklemenin kalite kaybına yol açacağını belirt
- Çıktı kalitesi hakkında kullanıcıdan olumsuz geri bildirim 2 çalıştırma üst üste gelirse — SPEAKER_REFRAME parametrelerini gözden geçir

## Rules
- Her çalıştırmadan önce kaynak videonun var olduğunu ve ffprobe ile okunabildiğini doğrula
- Bir çalıştırmada tüm zinciri (tespit + reframe) çalıştır, yarım bırakma
- Emin değilsen aday kesitleri kullanıcıya onaylat, körü körüne hepsini üretme
- outputs/ dışına asla yazma, kaynak dosyaya asla dokunma
