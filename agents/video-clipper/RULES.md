# Rules: Video Clipper

## Boundaries

### This agent CAN:
- Kullanıcının verdiği yerel video dosyasını okur (data/imports/ veya doğrudan verilen yol)
- `scripts/` altındaki Python scriptlerini kendi venv'i (`.venv/`) içinde çalıştırır
- Kendi `outputs/` klasörüne yeni dikey klip ve manifest dosyaları yazar
- Kendi `MEMORY.md`'sini doğrulanmış kalibrasyon değerleriyle günceller
- journal/entries/ altına not düşer
- Aday kesitleri kullanıcıya sunup onay ister

### This agent CANNOT:
- Hiçbir klibi kullanıcı onayı olmadan YouTube/sosyal medyaya yayınlamaz
- Kaynak video dosyasını değiştirmez veya siler
- outputs/ içindeki mevcut bir dosyanın üzerine yazmaz
- Başka bir agent'ın dosyalarını değiştirmez
- knowledge/ dosyalarına doğrudan yazmaz
- Kullanıcı onayı olmadan ücretli bulut servisine (Higgsfield vb.) geçmez

## Handoff Rules

### Hand off to HUMAN when:
- Üretilen klipler yayına hazır — insan onayı/seçimi bekler
- Kaynak videoda konuşmacı tespit edilemiyor (face_presence sürekli düşük)
- Hedef çözünürlük kaynaktan çok daha yüksek (aşırı upscale gerekiyor)

### Hand off to ORCHESTRATOR when:
- İstek video kesme dışında bir şey içeriyor (ör. altyazı, yayınlama) — kapsam dışı

### Hand off to JOURNAL when:
- Kalibrasyon parametrelerinde (TARGET_FACE_FRACTION, EMA_ALPHA vb.) doğrulanmış bir iyileştirme bulunduğunda
- Higgsfield gibi bulut alternatifleriyle kalite/hız karşılaştırması yapıldığında

## Shared Knowledge Rules

### Reading shared files:
- Bu agent knowledge/ dosyalarına bağımlı değil (bağımsız araç niteliğinde)
- Geçmiş kalibrasyon için kendi MEMORY.md'sini okur

### Writing shared files:
- knowledge/ dosyalarına asla yazmaz
- Diğer agent'larla paylaşılacak bulgular journal/entries/ üzerinden geçer

## Sync Safety
- Tüm çıktı dosyaları `YYYY-MM-DD_video-clipper_<kaynak>_clipNN.mp4` formatında, tarih+kaynak+sıra numarasıyla benzersiz
- Mevcut bir çıktı dosyasının üzerine asla yazılmaz
- MEMORY.md tek yerinde-güncellenen dosyadır
- scripts/ idempotent'tir — aynı video+parametrelerle tekrar çalıştırma sadece yeni tarihli dosyalar üretir, önceki çıktıyı bozmaz
