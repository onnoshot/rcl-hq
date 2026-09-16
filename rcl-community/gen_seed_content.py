#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Time Capsule - canli topluluk seed uretici (duzgun Turkce icerik).
~95 Turk kullanici + oylar + bekleme listesi + begeniler + Turkce yorumlar + kamera anilari
+ Wikimedia Commons'tan GERCEK "bu kamerayla cekilmis" ornek kareler (real_photos.json).
Uretilen seed_content.sql IDEMPOTENT'tir: bastan 'seed-%' verisini siler, yeniden kurar.
Kullanim: python3 gen_seed_content.py  ->  supabase/seed_content.sql
"""
import json, os, random, uuid

HERE = os.path.dirname(__file__)
CAMS = json.load(open(os.path.join(HERE, "cameras_seed.json")))
OUT = os.path.join(HERE, "supabase", "seed_content.sql")
RP = os.path.join(HERE, "real_photos.json")
NS = uuid.UUID("8f1c0c2e-0000-4000-8000-000000000001")
rnd = random.Random(20260627)

def q(s):
    if s is None:
        return "null"
    return "'" + str(s).replace("'", "''") + "'"

TR_MAP = str.maketrans({"ı": "i", "İ": "i", "ğ": "g", "Ğ": "g", "ş": "s", "Ş": "s",
                        "ç": "c", "Ç": "c", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u"})
def slug(s):
    return s.lower().translate(TR_MAP)

# ---------------- Turk kullanicilar (duzgun Turkce isimler) ----------------
FIRST = ["Elif","Mertcan","Zeynep","Ahmet","Deniz","Ece","Can","İrem","Baran","Selin","Burak","Defne","Kaan","Melis","Emre",
 "Naz","Tolga","Cansu","Berk","Aslı","Onur","Pelin","Yiğit","Sena","Furkan","Ada","Mert","Gizem","Arda","Damla",
 "Eren","Ayşe","Sarp","İpek","Kerem","Beren","Umut","Ezgi","Cem","Derya","Berkay","Buse","Alp","Sude","Efe",
 "Esra","Tunç","Merve","Sinan","Yağmur","Bora","Nehir","Doruk","Lara","Miraç","Ceyda","Kuzey","Eylül","Tarık","Begüm",
 "Halil","Ela","Volkan","Duru","Serkan","İlayda","Murat","Göksu","Hakan","Aysu","Okan","Beril","Çağlar","Nil","Ozan",
 "Simge","Yusuf","Çağla","Devrim","Toprak","Aleyna","Korhan","Melike","Batuhan","Ceren","Ufuk","Sıla","Anıl","İdil","Erdem",
 "Selim","Gökçe","Rıza","Zehra","Cihan","Büşra","Tan","Özge"]
LAST = ["Kaya","Demir","Yıldız","Aksoy","Poyraz","Şahin","Çelik","Arslan","Doğan","Kurt","Öztürk","Yılmaz","Aydın","Korkmaz",
 "Eren","Taş","Polat","Sarı","Aslan","Bulut","Çetin","Güler","Kara","Koç","Özkan","Sezer","Tekin","Yavuz","Acar","Bal",
 "Avcı","Uçar","Erdoğan","Toprak","Güneş","Çakır","Şimşek","Yalçın","Özdemir","Kılıç","Turan","Ateş","Bozkurt","Çınar",
 "Sönmez","Duran","Erol","Kaplan","Akın","Yıldırım"]
NICK = ["objektif","analog","film","kadraj","shots","foto","35mm","pozitif","obscura","apertur","poz","kare","deklansor",
 "vizor","grenli","diyafram","negatif","retro","ccd","enstantane","flu","kontrast","optik","zoom","piksel","ayna","lens"]
CITY = ["İstanbul","İzmir","Ankara","Bursa","Muğla","Antalya","Eskişehir","Sapanca","Çanakkale","Trabzon","Adana","Konya",
 "Bodrum","Çeşme","Kaş","Edirne","Mersin","Sinop","Amasra","Gaziantep","Kayseri","Samsun","Balıkesir","Tekirdağ"]
LOC = ["İstanbul, Moda sahili","İstanbul, Kadıköy","İstanbul, Balat","İstanbul, Galata","İstanbul, Cihangir","İstanbul, Bebek",
 "İzmir, Alsancak","İzmir, Kordon","İzmir, Konak","Ankara, Tunalı","Ankara, Kuğulu Park","Bursa, Cumalıkızık",
 "Muğla, Akyaka","Antalya, Kaleiçi","Antalya, Konyaaltı","Eskişehir, Porsuk","Sapanca gölü","Çeşme, Alaçatı","Kaş limanı",
 "Bodrum, Gümbet","Kapadokya, Göreme","Amasra sahili","Çanakkale, Bozcaada","Trabzon, Uzungöl","Sinop kalesi",
 "Datça","Edirne, Selimiye","Mersin, Kızkalesi","Samsun sahili","Foça, eski sokaklar","Ayvalık, Cunda","Safranbolu"]

NOTE = [
 "Film bitmek üzereyken yakaladım, son kare hep en iyisi oluyor.","Gün batımında ışık tam istediğim gibi vurdu.",
 "Hiç planlamadığımız bir kaçamaktı, en sevdiğim kare oldu.","Sabahın köründe sahil bomboştu, sadece ben ve deniz.",
 "Flaş patlayınca o nostaljik hava çıktı işte.","Arkadaşlarla kaybolduğumuz o akşamdan kalan tek kare.",
 "Bir fincan kahve ve bu manzara, başka bir şey istemedim.","Yağmurdan sonra renkler bambaşka oldu.",
 "O an orada olmak yetiyordu, deklanşöre sonra bastım.","Eski mahalle, yeni bir göz. Burayı çok özlemişim.",
 "Kalabalığın içinde tek sessiz an buydu.","Bu kamerayla ilk çekimim, renklerine bayıldım.",
 "Annemin eski albümünden çıkmış gibi durdu, çok sevdim.","Sokak lambası yanınca kare kendiliğinden oluştu.",
 "Tatilin son günü, bavul yarı kapalıyken çektim.","Pili biterken zar zor yetişti ama değer.",
 "Telefonla aynı an çekildi ama bunda ruh var.","Küçük bir an ama ben günlerce baktım.",
 "Denize girmeden önce son kare, su damlası bile var.","Gece modu yok diye korktum, sonuç sürpriz oldu.",
 "Pazar sabahı, kimseler yokken.","Konser çıkışı, kulaklar çınlıyordu hâlâ.",
 "Karlı bir gün, parmaklarım donuyordu ama durmadım.","Camların ardından süzülen ışık tam zamanında geldi.",
 "Bu sokaktan her gün geçiyorum ama ilk kez böyle gördüm.","Yol kenarında durduk sırf bu manzara için.",
 "Eski bir kasette dinlediğimiz şarkı çalarken çektim.","Dedemin balkonundan, hep aynı saat aynı ışık.",
 "Bir anda döndü ve güldü, işte o an.","Vapur geçerken martılar da kadraja girdi.",
 "Sonbaharın ilk yaprağı yere düşmeden.","Lunaparkta ışıklar yanınca çocuk gibi sevindim.",
 "Hiçbir filtre bu rengi veremezdi.","Kaybolduğumuz ara sokakta bulduğumuz hazine.",
 "Rüzgâr saçları dağıttı, kare daha da güzel oldu.","Çaydanlık fokurdarken pencereden dışarı baktım.",
]

REAL_NOTE = [
 "Bu kamerayla çekilmiş bir örnek kare; CCD'nin rengini hiç böyle görmemiştim.",
 "Modelin gerçek kapasitesini gösteren bir kare, detaylar şaşırttı.",
 "İşte bu sensörün imzası; güneş vurunca renkler patlıyor.",
 "Örnek bir çekim ama bence çoğu modern kameradan iyi.",
 "Bu makinenin doğal tonlarını en iyi anlatan kare bu.",
 "Net, dengeli ve nostaljik; tam aradığım his.",
 "Kameranın dinamik aralığı sandığımdan çok daha iyiymiş.",
 "Bu kareyi görünce listeye ekledim, ikna oldum.",
 "Grenli ama tatlı bir doku, dijital ama film gibi.",
 "Örnek çekim olarak paylaşıyorum; renk geçişleri çok yumuşak.",
]

COMMENT = [
 "renkler çok iyi çıkmış, hangi modda çektin","valla efsane olmuş, eline sağlık","CCD tadı her karede belli",
 "bu kamerayı ben de alıyorum artık, ikna oldum","kadraj harika, nokta atışı","o an orada gibi hissettim",
 "ışığı çok iyi yakalamışsın","grenli dokusuna bayıldım","aynısı bende de var, gece biraz zor ama gündüz mükemmel",
 "bu nostalji başka hiçbir şeyde yok","telefonla bunu çekemezdin, işte fark bu","arşive bayıldım böyle devam",
 "hangi ayarları kullandın merak ettim","tam Y2K havası, çok sevdim","bu kareyi çerçeveletmelisin",
 "flaş patlaması çok yakışmış","renk geçişleri inanılmaz","keşke ben de oradaymışım","favori karem bu oldu",
 "objektifin yumuşaklığı belli oluyor","sokak fotoğrafçılığı tam senin işin","ilk bakışta film sandım",
 "bu model gerçekten değerini biliyor","kompozisyon çok dengeli","detaylar net, ışık dengesi güzel",
 "bunu poster yapardım","aaa burayı biliyorum, harika çıkmış","gerçekten zamanda yolculuk gibi",
 "beğendim, takip ediyorum artık","bu kamerayı listeye ekledim senin sayende","tonlar çok doğal durmuş",
 "her fotoğrafında ayrı bir hikâye var","abartmıyorum en iyi kare bu","çok atmosferik olmuş",
 "işin sırrı kamerada mı gözde mi karar veremedim","bunu görünce dışarı çıkasım geldi","ellerine sağlık gerçekten",
 "klasik bir güzellik","modern kameralar bu hissi veremiyor","gözüm doldu valla, çocukluğum",
]

N_USERS = 95
users = []
used_handles = set()
av = list(range(1, 71)); rnd.shuffle(av)
for i in range(N_USERS):
    fn = rnd.choice(FIRST); ln = rnd.choice(LAST)
    if rnd.random() < 0.55:
        h = slug(fn) + "." + rnd.choice(NICK)
    else:
        h = slug(fn) + "." + slug(ln)
    if h in used_handles:
        h = h + str(rnd.randint(2, 99))
    used_handles.add(h)
    users.append({
        "uid": "seed-u%02d" % i, "handle": h, "name": fn + " " + ln,
        "city": rnd.choice(CITY), "avatar": "https://i.pravatar.cc/150?img=%d" % av[i % len(av)],
        "days": rnd.randint(20, 560),
    })

cam_handles = [c["handle"] for c in CAMS]
weights = [max(1, int(c.get("base_score", 0))) for c in CAMS]
def pick_weighted_unique(k):
    out, seen, guard = [], set(), 0
    while len(out) < k and guard < k * 40:
        guard += 1
        h = rnd.choices(cam_handles, weights=weights, k=1)[0]
        if h not in seen:
            seen.add(h); out.append(h)
    return out

# ---------------- anilar: picsum (genel) + Wikimedia (gercek ornek kareler) ----------------
photos = []
pcount = 0
cams_sorted = sorted(CAMS, key=lambda c: -c.get("base_score", 0))
for idx, c in enumerate(cams_sorted):
    n = rnd.randint(2, 5) if idx < 55 else (rnd.randint(1, 2) if idx < 80 else rnd.randint(0, 1))
    for _ in range(n):
        u = rnd.choice(users)
        y = rnd.choice([2023, 2024, 2024, 2025, 2025, 2026])
        photos.append({
            "id": str(uuid.uuid5(NS, c["handle"] + "p" + str(pcount))),
            "cam": c["handle"], "uid": u["uid"],
            "url": "https://picsum.photos/seed/tcp%d/900/1150" % pcount,
            "date": "%04d-%02d-%02d" % (y, rnd.randint(1, 12), rnd.randint(1, 28)),
            "loc": rnd.choice(LOC), "note": rnd.choice(NOTE), "days": rnd.randint(3, 520),
        })
        pcount += 1

# GERCEK ornek kareler (Wikimedia Commons - "Taken with X" kategorileri, hotlink + lisansli)
real_n = 0
if os.path.exists(RP):
    real = json.load(open(RP))
    valid = set(cam_handles)
    for handle, pics in real.items():
        if handle not in valid:
            continue
        for j, pic in enumerate(pics):
            u = rnd.choice(users)
            y = rnd.choice([2023, 2024, 2025, 2025, 2026])
            credit = "Foto: %s, %s / Wikimedia Commons" % (pic.get("artist", "Wikimedia"), pic.get("license", "CC"))
            note = rnd.choice(REAL_NOTE) + "  (" + credit + ")"
            photos.append({
                "id": str(uuid.uuid5(NS, handle + "r" + str(j))),
                "cam": handle, "uid": u["uid"], "url": pic["url"],
                "date": "%04d-%02d-%02d" % (y, rnd.randint(1, 12), rnd.randint(1, 28)),
                "loc": None, "note": note, "days": rnd.randint(3, 480),
            })
            real_n += 1

# ---------------- SQL ----------------
L = []; W = L.append
W("-- Time Capsule SEED ICERIK v3 (canli topluluk) - OTOMATIK URETILDI: gen_seed_content.py")
W("-- schema_v2 + seed_cameras'dan SONRA calistir. IDEMPOTENT: 'seed-%' verisini siler, yeniden kurar.")
W("-- Gercek ornek kareler: Wikimedia Commons (CC lisansli, altyazida kaynak belirtilir).")
W("begin;")
W("delete from profiles where customer_id like 'seed-%';  -- cascade: oy/foto/begeni/yorum/bekleme")
W("")
W("-- ===== KULLANICILAR (%d Turk hesabi) =====" % len(users))
vals = ",".join("(%s,%s,%s,%s,%s,now() - interval '%d days')" % (
    q(u["uid"]), q(u["handle"]), q(u["name"]), q(u["avatar"]), q(u["city"]), u["days"]) for u in users)
W("insert into profiles (customer_id,handle,display_name,avatar_url,city,member_since) values\n%s\non conflict (customer_id) do nothing;" % vals)
W("")
W("-- ===== ANILAR (%d foto: %d genel + %d Wikimedia gercek ornek) =====" % (len(photos), len(photos)-real_n, real_n))
for p in photos:
    W("insert into camera_photos (id,camera_id,customer_id,image_url,taken_date,location,note,status,created_at) "
      "select %s::uuid,c.id,%s,%s,%s,%s,%s,'approved',now() - interval '%d days' from cameras c where c.handle=%s;" % (
        q(p["id"]), q(p["uid"]), q(p["url"]), q(p["date"]), q(p["loc"]), q(p["note"]), p["days"], q(p["cam"])))
W("")
W("-- ===== OYLAR (camera_votes) =====")
vote_rows = []
for u in users:
    for h in pick_weighted_unique(rnd.randint(8, 34)):
        vote_rows.append((u["uid"], h))
for i in range(0, len(vote_rows), 150):
    vv = ",".join("(%s,%s)" % (q(a), q(b)) for a, b in vote_rows[i:i+150])
    W("insert into camera_votes (voter_id,camera_id) select v.uid,c.id from (values %s) v(uid,h) "
      "join cameras c on c.handle=v.h on conflict do nothing;" % vv)
W("")
W("-- ===== BEKLEME LISTESI (camera_waitlist) =====")
wait_rows = []
for u in users:
    if rnd.random() < 0.7:
        for h in pick_weighted_unique(rnd.randint(1, 6)):
            wait_rows.append((u["uid"], h))
for i in range(0, len(wait_rows), 150):
    vv = ",".join("(%s,%s)" % (q(a), q(b)) for a, b in wait_rows[i:i+150])
    W("insert into camera_waitlist (customer_id,camera_id) select v.uid,c.id from (values %s) v(uid,h) "
      "join cameras c on c.handle=v.h on conflict do nothing;" % vv)
W("")
W("-- ===== BEGENILER (photo_likes) =====")
like_rows = []
for p in photos:
    others = [u["uid"] for u in users if u["uid"] != p["uid"]]
    for uid in rnd.sample(others, rnd.randint(3, min(32, len(others)))):
        like_rows.append((p["id"], uid))
for i in range(0, len(like_rows), 200):
    vv = ",".join("(%s::uuid,%s)" % (q(pid), q(uid)) for pid, uid in like_rows[i:i+200])
    W("insert into photo_likes (photo_id,customer_id) values %s on conflict do nothing;" % vv)
W("")
W("-- ===== YORUMLAR (photo_comments, Turkce) =====")
com_rows = []
for p in photos:
    others = [u["uid"] for u in users if u["uid"] != p["uid"]]
    for uid in rnd.sample(others, min(rnd.randint(0, 4), len(others))):
        com_rows.append((p["id"], uid, rnd.choice(COMMENT), p["days"], rnd.randint(1, 240)))
for i in range(0, len(com_rows), 120):
    vv = ",".join("(%s::uuid,%s,%s,now() - interval '%d days' + interval '%d hours')" % (
        q(pid), q(uid), q(body), max(0, d - 1), hrs) for pid, uid, body, d, hrs in com_rows[i:i+120])
    W("insert into photo_comments (photo_id,customer_id,body,created_at) values %s;" % vv)
W("")
W("commit;")
W("update cameras c set photo_count=(select count(*) from camera_photos p where p.camera_id=c.id and p.status='approved');")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK ->", OUT)
print("  kullanici:%d  ani:%d (gercek ornek:%d)  oy:%d  bekleme:%d  begeni:%d  yorum:%d" % (
    len(users), len(photos), real_n, len(vote_rows), len(wait_rows), len(like_rows), len(com_rows)))
