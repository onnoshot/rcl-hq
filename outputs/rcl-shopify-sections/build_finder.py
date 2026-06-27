# -*- coding: utf-8 -*-
"""RetroCameraLand - "AI Kamera Eslestirici" (Camera Soulmate Finder).
Interactive, animated, color-morphing quiz section. Looks like a real AI but
just shuffles in-stock cameras from /products.js and assigns match percentages.

v3:
  - Proper Turkish content (real diacritics in the Python source; output stays
    PURE ASCII via E() -> &#NNNN; for HTML and json.dumps(ensure_ascii) -> \\uXXXX
    for JS/JSON-LD, so Shopify never double-encodes).
  - Multi-select questions (pick several per question) + continue button.
  - Slower, more realistic animations and richer effects.
  - Results are guaranteed to come ONLY from live in-stock cameras: the analyze
    step awaits the /products.js fetch; the hardcoded fallback is used solely if
    the live fetch fails entirely (offline).
  - Theme-proof readable colors (ID-scoped !important color hardening).

JS code itself contains NO Turkish literals -> all UI strings live in the DATA
object (json.dumps ensure_ascii). Static HTML Turkish goes through E().
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://retrocameraland.com"

def E(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "".join(ch if ord(ch) < 128 else "&#%d;" % ord(ch) for ch in s)

def ld(o):
    return json.dumps(o, ensure_ascii=True, separators=(",", ":"))

# ============================================================ ICONS
IC = {
 "spark": '<path d="M12 2l1.9 5.6L19.5 9.5 13.9 11.4 12 17l-1.9-5.6L4.5 9.5 10.1 7.6 12 2z"/><path d="M19 14l.8 2.3L22 17l-2.2.7L19 20l-.8-2.3L16 17l2.2-.7L19 14z"/>',
 "street": '<path d="M3 21h18"/><path d="M6 21V8l6-4 6 4v13"/><path d="M10 21v-5h4v5"/><circle cx="12" cy="10" r="1.3"/>',
 "travel": '<path d="M2 16l8-2 4-9 2 1-2 8 6-1 1 2-19 5z"/>',
 "portrait": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
 "night": '<path d="M21 12.8A8.5 8.5 0 1111.2 3a6.6 6.6 0 009.8 9.8z"/><path d="M18 4l.6 1.6L20 6l-1.4.4L18 8l-.6-1.6L16 6l1.4-.4L18 4z"/>',
 "vlog": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/><circle cx="8" cy="12" r="2.2"/>',
 "y2k": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 12h10M12 7v10"/><circle cx="8" cy="8" r="1"/><circle cx="16" cy="16" r="1"/>',
 "cine": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18M7 5v14M17 5v14"/>',
 "sharp": '<path d="M9 3H4v5M15 3h5v5M9 21H4v-5M15 21h5v-5"/><circle cx="12" cy="12" r="3"/>',
 "dreamy": '<path d="M6 16a4 4 0 010-8 5 5 0 019.6-1.3A4 4 0 1117 16H6z"/>',
 "warm": '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
 "sun": '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
 "indoor": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "citynight": '<path d="M3 21V9l5-3v4l5-4v6l8-3v12z"/><path d="M7 13v0M11 13v0M16 14v0"/>',
 "mixed": '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 010 18M3 12h18"/>',
 "pocket": '<rect x="6" y="3" width="12" height="18" rx="3"/><path d="M9 3v4h6V3"/>',
 "balance": '<path d="M12 3v18M5 7h14M5 7l-2 6h4zM19 7l-2 6h4z"/>',
 "quality": '<path d="M12 2l2.6 6.3L21 9l-5 4.4L17.5 21 12 17l-5.5 4L8 13.4 3 9l6.4-.7z"/>',
 "budget": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M7 12h0M17 12h0"/>',
 "mid": '<path d="M4 18V9M10 18V5M16 18v-6M20 18v-9"/>',
 "premium": '<path d="M5 7l3 3 4-6 4 6 3-3-2 12H7z"/>',
 "best": '<circle cx="12" cy="9" r="5"/><path d="M9 13l-1 8 4-2 4 2-1-8"/>',
 "check": '<path d="M5 13l4 4L19 7"/>',
 "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "cam": '<path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 011 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V9a1 1 0 011-1z"/><circle cx="12" cy="13" r="3.4"/>',
 "redo": '<path d="M21 12a9 9 0 11-3-6.7M21 4v5h-5"/>',
 "sharei": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/>',
 "gift": '<rect x="3" y="9" width="18" height="12" rx="1.5"/><path d="M3 13h18M12 9v12M12 9S9.5 4 7 5.4 8 9 12 9zM12 9s2.5-5 5-3.6S16 9 12 9z"/>',
 "heart": '<path d="M12 21s-7.5-5-9.5-9.6C1 8 3 4.5 6.4 5A4.3 4.3 0 0112 7a4.3 4.3 0 015.6-2c3.4-.5 5.4 3 3.9 6.4C19.5 16 12 21 12 21z"/>',
 "wallet": '<path d="M3 7a2 2 0 012-2h12a2 2 0 012 2"/><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M16 12.5h4M16 12.5a1.6 1.6 0 000 3H21v-3z"/>',
 "coins": '<ellipse cx="9" cy="6.5" rx="6" ry="3"/><path d="M3 6.5v5c0 1.7 2.7 3 6 3M3 11.5v5c0 1.7 2.7 3 6 3"/><circle cx="16" cy="15" r="5.5"/>',
 "sliders": '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2.2"/><circle cx="8" cy="17" r="2.2"/>',
 "seed": '<path d="M12 22V11"/><path d="M12 11C12 7 9 4 4 4c0 5 3 7 8 7z"/><path d="M12 13c0-3 3-6 8-6 0 4-3 6-8 6z"/>',
 "work": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2"/>',
 "selfie": '<circle cx="12" cy="8" r="4"/><path d="M5 21a7 7 0 0114 0"/><circle cx="12" cy="8" r="1.4"/>',
}

# ============================================================ QUIZ DATA (proper Turkish)
PALETTE = {
 "vermilion":"#d8472f","teal":"#2c766b","violet":"#6f4ff0","rose":"#d6447f",
 "amber":"#cf7a1e","cyan":"#1593b0","indigo":"#3f51c9","emerald":"#15915f",
}
def P(k): return PALETTE[k]

PROFILE = {
 "title":"Önce biraz tanışalım",
 "sub":"Sana gerçekten uyan kamerayı bulabilmem için seni biraz tanımam gerek. Bu küçük bilgiler, önerini kişiselleştirmemi sağlıyor.",
 "name_label":"Sana nasıl hitap edeyim?",
 "name_ph":"Adını yaz...",
 "age_label":"Yaş aralığın",
 "ages":["18 altı","18-24","25-34","35-44","45+"],
 "gender_label":"Cinsiyetin",
 "genders":["Kadın","Erkek","Belirtmek istemiyorum"],
 "city_label":"Hangi şehirde yaşıyorsun?",
 "city_ph":"Şehrini yaz...",
 "cities":["İstanbul","Ankara","İzmir","Bursa","Antalya","Adana","Konya","Gaziantep",
           "Eskişehir","Muğla","Trabzon","Samsun","Kayseri","Denizli","Mersin","Sakarya"],
 "cta":"Teste başla",
 "need_more":"Devam etmek için adını, yaş aralığını ve cinsiyetini seç.",
}

QUESTIONS = [
 {"k":"use","q":"Kameran en çok ne için yanında olacak?",
  "sub":"Bu kameranın hayatında nerede yer alacağını anlamak istiyorum. Sana en çok uyan 1-2 tanesini seç.",
  "opts":[
    {"v":"daily","label":"Günlük & sokak","sub":"Şehirde gezerken yakaladığın spontane, filtresiz anlar","hue":P("vermilion"),"icon":"street",
     "why":"günlük sokak anlarını özgürce yakalamak"},
    {"v":"travel","label":"Seyahat & gezi","sub":"Çantanda yer kaplamayan, her yere gelen hafif yol arkadaşı","hue":P("teal"),"icon":"travel",
     "why":"seyahatlerini hafif ve şık bir kameraya emanet etmek"},
    {"v":"portrait","label":"Portre & sevdiklerin","sub":"İnsan yüzleri, sıcak ten tonları, samimi bakışlar","hue":P("rose"),"icon":"portrait",
     "why":"portre ve insan çekiminde sıcaklık aramak"},
    {"v":"night","label":"Gece & parti","sub":"Flaşın patladığı, enerjinin tavan yaptığı gece kareleri","hue":P("violet"),"icon":"night",
     "why":"gece ve parti anının enerjisini dondurmak"},
    {"v":"content","label":"İçerik & vlog","sub":"Instagram, TikTok ve video için akan, dikkat çeken içerik","hue":P("amber"),"icon":"vlog",
     "why":"akan içerik ve vlog üretmek"},
  ]},
 {"k":"budget","q":"Aklındaki bütçe ne civarında?",
  "sub":"Sana sadece şu an stokta olan ve bütçene oturan modelleri önereceğim. Net değilse en uygununu seç.",
  "opts":[
    {"v":"b1","label":"8.000 TL'ye kadar","sub":"İlk adımı atmak için uygun fiyatlı, sağlam başlangıç","hue":P("emerald"),"icon":"coins",
     "why":"uygun bütçeyle doğru başlangıç"},
    {"v":"b2","label":"8.000 - 13.000 TL","sub":"Fiyat ve karakter dengesi en iyi olan orta segment","hue":P("teal"),"icon":"wallet",
     "why":"fiyat-karakter dengesi"},
    {"v":"b3","label":"13.000 - 20.000 TL","sub":"Daha yüksek çözünürlük ve daha zengin özellikler","hue":P("cyan"),"icon":"budget",
     "why":"daha zengin özellik beklentin"},
    {"v":"b4","label":"20.000 TL ve üzeri","sub":"En üst seviye, koleksiyonluk ve özellikli modeller","hue":P("violet"),"icon":"premium",
     "why":"en üst seviye bir model isteğin"},
    {"v":"b5","label":"Net değil, en uygununu öner","sub":"Sen tarzıma göre en mantıklısını seç","hue":P("amber"),"icon":"balance",
     "why":"tarzına en uygun fiyat"},
  ]},
 {"k":"aes","q":"Hangi görüntü estetiği seni çekiyor?",
  "sub":"Karelerinin ruhu nasıl olsun? Bu, kameranın renk karakterini belirliyor.",
  "opts":[
    {"v":"y2k","label":"Y2K flaş & grain","sub":"2000'lerin o dijital, hafif grenli, flaşlı nostaljisi","hue":P("violet"),"icon":"y2k",
     "why":"o flaşlı Y2K grain dokusu"},
    {"v":"cine","label":"Sinematik film tonu","sub":"Bir film karesinden çıkmış gibi yumuşak, dramatik tonlar","hue":P("teal"),"icon":"cine",
     "why":"sinematik film tonları"},
    {"v":"sharp","label":"Temiz & keskin","sub":"Net, canlı, her detayın okunduğu modern berraklık","hue":P("cyan"),"icon":"sharp",
     "why":"temiz ve net kareler"},
    {"v":"dreamy","label":"Rüya gibi & soft","sub":"Hayal gibi, yumuşak ışıklı, masalsı bir hava","hue":P("rose"),"icon":"dreamy",
     "why":"rüya gibi yumuşak ışık"},
    {"v":"warm","label":"Sıcak retro renkler","sub":"Solmuş bir fotoğraf albümünün sıcaklığındaki tonlar","hue":P("amber"),"icon":"warm",
     "why":"sıcak retro renk paleti"},
  ]},
 {"k":"env","q":"Çoğunlukla nasıl bir ışıkta çekeceksin?",
  "sub":"Işık, bir kameranın karakterini belirleyen en önemli şey. Flaş ve sensör seçimini buna göre yapıyorum.",
  "opts":[
    {"v":"day","label":"Gündüz dışarısı","sub":"Güneş altında, bol ışıklı sokaklar ve açık hava","hue":P("cyan"),"icon":"sun",
     "why":"gündüz ışığında canlı renkler"},
    {"v":"indoor","label":"Loş iç mekan","sub":"Kafe köşeleri, ev sıcaklığı, atölye loşluğu","hue":P("amber"),"icon":"indoor",
     "why":"loş mekanlarda atmosfer"},
    {"v":"citynight","label":"Gece şehir ışıkları","sub":"Neon tabelalar, gece hayatı, parıldayan şehir","hue":P("violet"),"icon":"citynight",
     "why":"gece şehir ışıklarında parlama"},
    {"v":"mixed","label":"Karışık / her yer","sub":"Belli bir yer yok; ışık nereye giderse oraya","hue":P("teal"),"icon":"mixed",
     "why":"her ortama uyum sağlama"},
  ]},
 {"k":"level","q":"Fotoğrafla aran nasıl?",
  "sub":"Deneyim seviyene göre, kullanımı sana en oturacak kamerayı seçiyorum.",
  "opts":[
    {"v":"first","label":"İlk ciddi kameram olacak","sub":"Basit, otomatik, eline alır almaz çekebileceğin bir kamera isterim","hue":P("emerald"),"icon":"seed",
     "why":"kolay ve otomatik kullanım"},
    {"v":"casual","label":"Arada bir çekerim","sub":"Temel ayarları bilirim, pratik ama karakterli olsun yeter","hue":P("teal"),"icon":"mid",
     "why":"pratik ama karakterli kullanım"},
    {"v":"pro","label":"Deneyimliyim, kontrol isterim","sub":"Manuel ayarlar, zoom ve detay benim için önemli","hue":P("indigo"),"icon":"sliders",
     "why":"kontrol ve detaya verdiğin önem"},
  ]},
 {"k":"occasion","q":"Bu kamera kimin için?",
  "sub":"Son bir şey: bu kamerayı neden aldığını bilmek, öneriyi tam yerine oturtmamı sağlıyor.",
  "opts":[
    {"v":"self","label":"Kendim için","sub":"Kendime güzel bir kamera alıyorum","hue":P("vermilion"),"icon":"selfie",
     "why":"kendine değer vermen"},
    {"v":"gift","label":"Hediye edeceğim","sub":"Sevdiğim birini mutlu edecek bir hediye arıyorum","hue":P("rose"),"icon":"gift",
     "why":"sevdiğin birine özel bir hediye"},
    {"v":"couple","label":"Sevgilim / eşim için","sub":"İkimizin anılarını biriktireceğimiz bir kamera","hue":P("rose"),"icon":"heart",
     "why":"birlikte anı biriktirme isteğin"},
    {"v":"work","label":"İçerik / işim için","sub":"Sosyal medya, satış veya işim için üreteceğim","hue":P("amber"),"icon":"work",
     "why":"içerik ve iş üretimi"},
    {"v":"collection","label":"Koleksiyon / merak","sub":"Retro kameralara meraklıyım, arşivime katacağım","hue":P("violet"),"icon":"y2k",
     "why":"retro kameralara olan tutkun"},
  ]},
]

ANALYZE = {
 "label":"ANALİZ",
 "steps":[
   "Canlı stok veritabanına bağlanılıyor",
   "Şu an satışta olan {n} kamera taranıyor",
   "{name} için kişisel kamera profili oluşturuluyor",
   "{use} kullanımına göre modeller filtreleniyor",
   "Bütçe ve deneyim seviyen eşleştiriliyor",
   "Renk karakteri ve sensör dokusu hizalanıyor",
   "Marka ve özellik eşleşme skorları hesaplanıyor",
   "Sana en uygun üç model seçiliyor",
 ],
 "use_short":{"daily":"günlük","travel":"seyahat","portrait":"portre","night":"gece","content":"içerik"},
}

RESULTS = {
 "eyebrow":"EŞLEŞME TAMAMLANDI",
 "title":"{name}, senin için 3 mükemmel eşleşme buldum",
 "sub":"Şu an stokta olan kameralar arasından, verdiğin cevaplara göre en uyumlu üç tanesi:",
 "best_badge":"EN UYUMLU",
 "match":"uyum",
 "view":"İncele",
 "all_cta":"Tüm kameraları gör",
 "redo":"Testi tekrarla",
 # rank-based templates; {trait}=brand character, {cam}=model name, {feat}=concrete matched feature.
 # Each of the 3 cards gets a different template, trait AND feature, so every recommendation reads uniquely.
 "reasons":[
   "En yüksek uyum burada {name}! {cam}, {trait} ile öne çıkıyor. {use} isteğinle birebir örtüşüyor ve {feat} tam senin için. Bence aradığın kamera bu.",
   "{cam} çok güçlü bir eşleşme {name}. {trait} sayesinde {aes} hissini zahmetsizce yakalarsın; üstelik {feat}. Tarzını her karede yansıtacak bir model.",
   "Farklı bir karakter ama tam isabet: {cam}. {trait} ve {feat} ile {use} senin için çok daha keyifli olacak. Listeden çıkarmadan önce bir kez daha bak.",
 ],
 # dinamik {feat} (somut eslesen ozellik) cumleleri - JS bunlari sayilarla doldurur ({z}=zoom,{mp}=MP,{y}=yil)
 "feats_dyn":{
   "zoom":"{z}x optik zoomuyla uzaktaki kareleri bile yakalaman",
   "water":"suya ve darbeye dayanıklı gövdesiyle her yere gelebilmesi",
   "flash":"güçlü flaşıyla gece ve loş ortamda parlaması",
   "video":"video kaydı desteğiyle içerik üretimine uygun olması",
   "touch":"dokunmatik ekranıyla ilk dakikadan pratik kullanımı",
   "slim":"cebe giren ince gövdesiyle hep yanında olabilmesi",
   "mp":"{mp} megapiksellik sensörüyle net ve detaylı kareler vermesi",
   "ccd":"{y} model gerçek CCD sensör dokusu",
   "macro":"makro yeteneğiyle yakın detayları ortaya çıkarması",
   "mp_default":"{mp} megapiksellik CCD sensörü",
   "default":"o gerçek 2000'ler CCD karakteri",
 },
 # brand -> image-character phrase, in nominative (so it fits "{trait} ile" / "{trait} sayesinde")
 "traits":{
   "sony":"Sony'nin canlı ve net renk karakteri",
   "canon":"Canon'un yumuşak, sıcak ten tonları",
   "fujifilm":"Fujifilm'in efsane film simülasyonu renkleri",
   "fuji":"Fujifilm'in efsane film simülasyonu renkleri",
   "olympus":"Olympus'un keskin, kontrastlı netliği",
   "panasonic":"Lumix'in geniş açısı ve yüksek detay netliği",
   "lumix":"Lumix'in geniş açısı ve yüksek detay netliği",
   "kodak":"Kodak'ın nostaljik, sıcak film tonları",
   "nikon":"Nikon'un doğal ve dengeli renk geçişleri",
   "casio":"Casio'nun hızlı, pratik günlük karakteri",
   "sanyo":"Sanyo'nun gerçek retro CCD dokusu",
   "hp":"kompakt gövdesindeki pratik günlük kullanım rahatlığı",
   "traveler":"sade gövdesindeki saf CCD karakteri",
   "_default":"kendine has o filmsi CCD karakteri",
 },
 "friend":"Sevgili dost",
}

SEO = {
 "h2":"Hangi retro dijital kamera sana uygun?",
 "p":("RetroCameraLand AI Kamera Eşleştirici, sana birkaç kısa soru sorar; kullanım amacını, bütçeni, "
      "estetik tercihini, çekim ortamını ve deneyim seviyeni anlayıp şu an stokta bulunan, test edilmiş "
      "2000'ler CCD dijital kameraları arasından profiline en uygun üç modeli yüzdesel uyum skoruyla önerir. "
      "Günlük sokak fotoğrafçılığından gece parti estetiğine, Y2K flaş dokusundan sinematik film tonlarına "
      "kadar tarzını anlar ve sadece bütçene oturan, gerçekten uyumlu modelleri gösterir. "
      "Tüm kameralar satıştan önce fonksiyon testinden geçer ve kondisyonu şeffaf biçimde paylaşılır."),
 "cats_head":"Popüler kullanım senaryoları",
 "cats":[
   ("Günlük & sokak için kamera","Spontane anlar ve sokak fotoğrafçılığı için hafif, hızlı CCD kompaktlar.","/collections/all"),
   ("Seyahat kamerası","Çantada yer kaplamayan, her ortama uyum sağlayan gezi kameraları.","/collections/all"),
   ("Gece & parti estetiği","Flaşlı gece karakteri ve Y2K dokusu için ideal modeller.","/collections/all"),
   ("İçerik & vlog","Sosyal medya ve video içerik üretimi için pratik seçimler.","/collections/all"),
 ],
 "faq_head":"Sıkça sorulan sorular",
 "faq":[
   ("AI Kamera Eşleştirici nasıl çalışır?",
    "Birkaç kısa soruyla kullanım amacını, bütçeni, estetik tercihini, çekim ortamını, deneyim seviyeni ve kameranın kimin için olduğunu anlar; ardından şu an stokta olan kameraların marka, model ve özelliklerini analiz ederek profiline gerçekten uyan üç modeli yüzdesel uyum skoruyla sıralar. Önerilen modeller bütçene göre filtrelenir."),
   ("Önerilen kameralar gerçekten stokta mı?",
    "Evet. Eşleştirici, mağazanın canlı ürün listesinden yalnızca şu an satın alınabilir, stokta olan kameraları değerlendirir; önerilen her modele tek tıkla ulaşabilirsin."),
   ("Hangi retro kamera yeni başlayanlar için uygundur?",
    "Yeni başlayanlar için otomatik modları güçlü, cebe sığan ve kullanımı kolay CCD kompaktlar idealdir. Eşleştirici, profiline göre bu modelleri öncelikle önerir."),
   ("CCD kamera nedir ve neden tercih edilir?",
    "CCD sensörlü 2000'ler kompakt kameraları; flaşlı gece estetiği, filmsi renkler ve hızlı point-and-shoot pratikliğiyle Y2K dokusunu birebir yakalar. Bu nostaljik görüntü karakteri modern telefon kameralarından belirgin şekilde farklıdır."),
   ("Test ücretsiz mi ve üye olmam gerekir mi?",
    "Tamamen ücretsizdir ve üyelik gerektirmez. Sorulara saniyeler içinde cevap verir, anında kişiselleştirilmiş kamera önerini alırsın."),
 ],
}

SHARE = {
 "btn":"Sonucu paylaş",
 "title":"Sonucunu paylaş",
 "making":"Görsel hazırlanıyor...",
 "fail":"Görsel oluşturulamadı.",
 "img_title1":"Bana en uygun",
 "img_title2":"retro kameralar",
 "cta_line":"Sen de testini yap",
 "site":"retrocameraland.com",
 "hashtags":"#retrocamera #retrokamera #ccdkamera",
 # 9:16 minimalist hikaye gorseli metinleri
 "brandmark":"RETROCAMERALAND",
 "badge":"EN UYUMLU",
 "match_word":"uyum",
 "eyebrow":"AI KAMERA EŞLEŞTİRİCİ",
 "more":"+ sana özel 2 öneri daha",
 "q1":"Peki senin",
 "q2":"kameran hangisi?",
 "try_cta":"retrocameraland.com",
 "try_sub":"Ücretsiz teste başla, saniyeler içinde öğren",
 "dl":"Görseli indir",
 "native":"Paylaş",
 "ig_note":"Görsel indirildi. Instagram uygulamasından hikaye/gönderi olarak paylaşabilirsin.",
 # kisa one cikan ozellik (markaya gore) - paylasim gorseli + metin
 "feats":{
   "sony":"Canlı, net renkler","canon":"Yumuşak sıcak ten tonları","fujifilm":"Efsane film renkleri",
   "fuji":"Efsane film renkleri","olympus":"Keskin, kontrastlı netlik","panasonic":"Geniş açı, yüksek detay",
   "lumix":"Geniş açı, yüksek detay","kodak":"Nostaljik sıcak tonlar","nikon":"Doğal renk geçişleri",
   "casio":"Hızlı, pratik günlük","sanyo":"Gerçek retro CCD dokusu","hp":"Kompakt, pratik kullanım",
   "traveler":"Saf CCD karakteri","_default":"Filmsi CCD karakteri",
 },
}

HERO = {
 "pill":"AI KAMERA EŞLEŞTİRİCİ",
 "words":["Sana","özel","kameranı","birlikte","bulalım."],
 "lead":("Birkaç kısa soru cevapla; tarzını, bütçeni ve ihtiyacını anlayıp şu an stokta olan retro "
         "dijital kameralar arasından sana en uygun üç modeli yüzdesel uyum skoruyla önereyim. "
         "Tamamen ücretsiz, üyelik yok."),
 "cta":"Teste başla",
 "meta":["~1 dakika","6 soru","Sana özel sonuç","Stoktan gerçek öneri"],
}

# Son care: canli /products.js VE /products.json ikisi de basarisiz olursa kullanilir.
# Yalniz olarak gercek, o anda stokta olan modellerden olusur (build aninda dogrulandi).
FALLBACK = [
 {"title":"Sony Cybershot DSC-W150","handle":"sony-cybershot-dsc-w150","brand":"Sony","price":"13.490 TL","year":2008,"mp":8.1,"zoom":5,"flash":True,"video":True,"water":False,"touch":False,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Sony_Cybershot_DSC-W150_a22d220f-24c2-40d1-b3b9-225938451637.jpg"},
 {"title":"Canon IXUS i","handle":"canon-ixus-i","brand":"Canon","price":"11.490 TL","year":2003,"mp":4.0,"zoom":0,"flash":True,"video":True,"water":False,"touch":False,"slim":True,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/canon_ixus_i.jpg"},
 {"title":"Fujifilm Finepix Z90","handle":"fujifilm-finepix-z90-digicam","brand":"Fujifilm","price":"16.490 TL","year":2011,"mp":14.0,"zoom":5,"flash":True,"video":True,"water":False,"touch":True,"slim":True,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/Fujifilm_Finepix_Z90_8c8d60c4-60e6-4122-9bad-9224cae2f990.jpg"},
 {"title":"Olympus VR-340","handle":"olympus-vr-340","brand":"Olympus","price":"17.990 TL","year":2012,"mp":16.0,"zoom":10,"flash":True,"video":True,"water":False,"touch":False,"wide":True,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/olympus_retrocamera_6c48f30e-b083-4fa4-bc6c-dd2d837ffc05.jpg"},
 {"title":"Panasonic Lumix DC-TZ91","handle":"panasonic-lumix-dc-tz91","brand":"Lumix","price":"28.490 TL","year":2017,"mp":20.3,"zoom":30,"flash":False,"video":True,"water":False,"touch":True,"wide":True,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/lumiz_tz91_retrocameraland.jpg"},
 {"title":"Kodak EasyShare V603","handle":"kodak-easyshare-v603","brand":"Kodak","price":"10.490 TL","year":2006,"mp":6.1,"zoom":3,"flash":True,"video":True,"water":False,"touch":False,
  "image":"https://cdn.shopify.com/s/files/1/0686/3198/6315/files/a_0161_ONN04962.jpg"},
]

# ============================================================ JSON-LD
ORG = {"@context":"https://schema.org","@type":"Organization","name":"RetroCameraLand","url":SITE,
 "logo":SITE+"/cdn/shop/files/retrocameraland_banner.jpg","slogan":"Geçmiş hâlâ yaşıyor."}
WEBAPP = {"@context":"https://schema.org","@type":"WebApplication","name":"RetroCameraLand AI Kamera Eşleştirici",
 "applicationCategory":"ShoppingApplication","operatingSystem":"Web","url":SITE+"/pages/hangi-kamera-bana-uygun",
 "offers":{"@type":"Offer","price":"0","priceCurrency":"TRY"},
 "description":"Ücretsiz test ile kullanım amacını, bütçeni ve tarzını anlayıp şu an stokta olan retro dijital CCD kameralar arasından sana en uygun üç modeli yüzdesel uyum skoruyla öneren akıllı kamera eşleştirici.",
 "provider":{"@type":"Organization","name":"RetroCameraLand","url":SITE}}
HOWTO = {"@context":"https://schema.org","@type":"HowTo","name":"AI Kamera Eşleştirici ile sana uygun retro kamerayı bul",
 "totalTime":"PT1M","step":[
  {"@type":"HowToStep","position":1,"name":"Profilini gir","text":"Adını, yaşını, cinsiyetini ve şehrini gir."},
  {"@type":"HowToStep","position":2,"name":"Kullanım amacını seç","text":"Kamerayı ne için kullanacağını seç: günlük, seyahat, portre, gece veya içerik."},
  {"@type":"HowToStep","position":3,"name":"Tarzını ve bütçeni belirle","text":"Bütçeni, estetik tercihini, çekim ortamını, deneyim seviyeni ve kameranın kimin için olduğunu seç."},
  {"@type":"HowToStep","position":4,"name":"Önerini al","text":"Stoktaki kameralar arasından bütçene oturan ve profiline en uygun üç model yüzdesel uyum skoruyla listelenir."}]}
def faq_ld():
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in SEO["faq"]]}
BREAD = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Ana Sayfa","item":SITE+"/"},
  {"@type":"ListItem","position":2,"name":"Hangi Kamera Bana Uygun?","item":SITE+"/pages/hangi-kamera-bana-uygun"}]}

# ============================================================ CSS
CSS = r"""
{%- style -%}
#rcl-fnd-__SID__{
  --ac: {{ section.settings.accent | default: '#d8472f' }};
  --ac2: color-mix(in srgb, var(--ac) 40%, #ffffff);
  --bg: {{ section.settings.bg | default: '#faf8f4' }};
  --card: {{ section.settings.card | default: '#ffffff' }};
  --ink: {{ section.settings.ink | default: '#15110d' }};
  --mut: color-mix(in srgb, var(--ink) 72%, transparent);
  --stroke: color-mix(in srgb, var(--ink) 14%, transparent);
  --glass: color-mix(in srgb, var(--card) 74%, transparent);
  --blur: {{ section.settings.glass_blur | default: 18 }}px;
  --r: 26px;
  position:relative; isolation:isolate; overflow:hidden; background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue","Inter",sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}
@supports (transition: --ac 1s){
  @property --ac{syntax:'<color>';inherits:true;initial-value:#d8472f;}
  #rcl-fnd-__SID__{transition:--ac 1.4s cubic-bezier(.4,0,.2,1);}
}
#rcl-fnd-__SID__ *{box-sizing:border-box;}
#rcl-fnd-__SID__ button{font:inherit;color:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent;}
#rcl-fnd-__SID__ .pad{padding:clamp(40px,6vw,90px) clamp(15px,5vw,40px);}
#rcl-fnd-__SID__ .wrap{max-width:1080px;margin:0 auto;position:relative;z-index:2;}
#rcl-fnd-__SID__ a{color:inherit;text-decoration:none;}

/* drifting aurora (slower) */
#rcl-fnd-__SID__ .aurora{position:absolute;inset:-30% -12% 0 -12%;z-index:0;pointer-events:none;filter:blur(74px);opacity:.55;}
#rcl-fnd-__SID__ .aurora span{position:absolute;border-radius:50%;display:block;mix-blend-mode:multiply;}
#rcl-fnd-__SID__ .aurora span:nth-child(1){width:48vw;height:48vw;left:-8%;top:-8%;background:radial-gradient(circle,var(--ac2),transparent 64%);animation:fd1 38s ease-in-out infinite;}
#rcl-fnd-__SID__ .aurora span:nth-child(2){width:44vw;height:44vw;right:-10%;top:0;background:radial-gradient(circle,color-mix(in srgb,var(--ac) 55%,#fff),transparent 64%);animation:fd2 46s ease-in-out infinite;}
#rcl-fnd-__SID__ .aurora span:nth-child(3){width:40vw;height:40vw;left:28%;top:46%;background:radial-gradient(circle,color-mix(in srgb,var(--ac2) 85%,#fff),transparent 60%);animation:fd1 52s ease-in-out infinite reverse;}
@keyframes fd1{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(6%,7%) scale(1.12)}}
@keyframes fd2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-7%,5%) scale(1.16)}}
#rcl-fnd-__SID__ .grain{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:.05;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}

#rcl-fnd-__SID__ .glass{background:var(--glass);-webkit-backdrop-filter:blur(var(--blur)) saturate(165%);backdrop-filter:blur(var(--blur)) saturate(165%);border:1px solid var(--stroke);box-shadow:0 1px 0 rgba(255,255,255,.55) inset,0 26px 70px -38px rgba(15,20,25,.5);border-radius:var(--r);}

/* ---------- APP shell ---------- */
#rcl-fnd-__SID__ .app{position:relative;max-width:880px;margin:0 auto;}
#rcl-fnd-__SID__ .app::before{content:"";position:absolute;left:50%;top:46%;width:min(120%,820px);aspect-ratio:1;transform:translate(-50%,-50%);z-index:0;border-radius:50%;
  background:conic-gradient(from 0deg,color-mix(in srgb,var(--ac) 26%,transparent),transparent 30%,color-mix(in srgb,var(--ac2) 60%,transparent) 55%,transparent 75%,color-mix(in srgb,var(--ac) 26%,transparent));
  filter:blur(72px);opacity:.5;animation:frot 48s linear infinite;pointer-events:none;}
@keyframes frot{to{transform:translate(-50%,-50%) rotate(360deg)}}

#rcl-fnd-__SID__ .prog{position:relative;z-index:2;height:7px;border-radius:100px;background:color-mix(in srgb,var(--ink) 10%,transparent);overflow:hidden;margin:0 auto 30px;max-width:520px;opacity:0;transform:translateY(-6px);transition:opacity .6s,transform .6s;}
#rcl-fnd-__SID__ .app.started .prog{opacity:1;transform:none;}
#rcl-fnd-__SID__ .prog i{display:block;height:100%;width:0;border-radius:100px;background:linear-gradient(90deg,var(--ac2),var(--ac));box-shadow:0 0 16px color-mix(in srgb,var(--ac) 65%,transparent);transition:width 1s cubic-bezier(.3,.8,.3,1);}
#rcl-fnd-__SID__ .prog i::after{content:"";position:absolute;}

#rcl-fnd-__SID__ .stage{position:relative;z-index:2;display:grid;grid-template-columns:minmax(0,1fr);align-items:center;min-height:clamp(460px,66vh,600px);}
#rcl-fnd-__SID__ .scr{grid-area:1/1;width:100%;min-width:0;transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1),filter .7s;}
#rcl-fnd-__SID__ .scr.enter{opacity:0;transform:translateY(40px) scale(.955);filter:blur(14px);}
#rcl-fnd-__SID__ .scr.leave{opacity:0;transform:translateY(-30px) scale(.955);filter:blur(14px);pointer-events:none;}

/* ---------- shared pills/buttons ---------- */
#rcl-fnd-__SID__ .pill{display:inline-flex;align-items:center;gap:9px;font-size:12.5px;font-weight:650;letter-spacing:.16em;color:var(--ac);padding:10px 18px;border-radius:100px;text-transform:uppercase;}
#rcl-fnd-__SID__ .pill .dot{width:7px;height:7px;border-radius:50%;background:var(--ac);box-shadow:0 0 0 4px color-mix(in srgb,var(--ac) 22%,transparent);animation:fpulse 3s ease-in-out infinite;}
@keyframes fpulse{0%,100%{box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 30%,transparent)}50%{box-shadow:0 0 0 11px color-mix(in srgb,var(--ac) 0%,transparent)}}

#rcl-fnd-__SID__ .pbtn{position:relative;display:inline-flex;align-items:center;gap:11px;padding:17px 34px;border-radius:100px;background:var(--ink);color:var(--bg);border:0;font-size:clamp(16px,3.6vw,17px);font-weight:600;transition:transform .45s cubic-bezier(.2,.7,.2,1),box-shadow .45s,opacity .4s;box-shadow:0 20px 44px -20px var(--ink);overflow:hidden;}
#rcl-fnd-__SID__ .pbtn::after{content:"";position:absolute;top:0;left:-120%;width:60%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.3),transparent);transform:skewX(-18deg);animation:fsheen 4.6s ease-in-out infinite;}
@keyframes fsheen{0%,55%{left:-120%}100%{left:150%}}
#rcl-fnd-__SID__ .pbtn:hover{transform:translateY(-3px) scale(1.02);box-shadow:0 30px 60px -22px var(--ink);}
#rcl-fnd-__SID__ .pbtn:active{transform:translateY(-1px) scale(.99);}
#rcl-fnd-__SID__ .pbtn svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}
#rcl-fnd-__SID__ .pbtn[disabled]{opacity:.35;pointer-events:none;box-shadow:none;transform:none;}
#rcl-fnd-__SID__ .pbtn[disabled]::after{display:none;}
#rcl-fnd-__SID__ .sbtn{display:inline-flex;align-items:center;gap:9px;padding:15px 26px;border-radius:100px;background:var(--card);border:1px solid var(--stroke);font-size:15px;font-weight:560;transition:background .4s,transform .4s,border-color .4s;}
#rcl-fnd-__SID__ .sbtn:hover{border-color:color-mix(in srgb,var(--ac) 50%,var(--stroke));transform:translateY(-2px);}
#rcl-fnd-__SID__ .sbtn svg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}

/* attention-grabbing red, breathing start button (grows/shrinks, glow blinks) */
#rcl-fnd-__SID__ .startbtn{background:var(--ac);box-shadow:0 18px 44px -16px var(--ac);animation:fbtnpulse 2.2s ease-in-out infinite;}
@keyframes fbtnpulse{0%,100%{transform:scale(1);box-shadow:0 18px 44px -16px var(--ac),0 0 0 0 color-mix(in srgb,var(--ac) 55%,transparent)}50%{transform:scale(1.05);box-shadow:0 26px 62px -16px var(--ac),0 0 0 18px color-mix(in srgb,var(--ac) 0%,transparent)}}
#rcl-fnd-__SID__ .startbtn:hover{animation-play-state:paused;transform:scale(1.07);box-shadow:0 30px 66px -16px var(--ac);}
#rcl-fnd-__SID__ .startbtn::after{animation-duration:3.2s;}
#rcl-fnd-__SID__ .shareb svg{stroke:currentColor;stroke-width:1.8;fill:none;}

/* social share modal */
#rcl-fnd-__SID__ .shmask{position:fixed;inset:0;z-index:99999;display:none;place-items:center;padding:18px;background:rgba(12,14,17,.62);-webkit-backdrop-filter:blur(7px);backdrop-filter:blur(7px);animation:fmaskin .35s ease;}
#rcl-fnd-__SID__ .shmask.on{display:grid;}
@keyframes fmaskin{from{opacity:0}to{opacity:1}}
#rcl-fnd-__SID__ .shcard{width:100%;max-width:420px;max-height:92vh;overflow:auto;background:var(--card);border-radius:24px;border:1px solid var(--stroke);padding:20px;box-shadow:0 50px 120px -30px rgba(0,0,0,.7);animation:fcardup .4s cubic-bezier(.2,.8,.3,1);}
@keyframes fcardup{from{opacity:0;transform:translateY(24px) scale(.97)}to{opacity:1;transform:none}}
#rcl-fnd-__SID__ .shhead{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}
#rcl-fnd-__SID__ .shhead b{font-size:18px;font-weight:740;letter-spacing:-.01em;}
#rcl-fnd-__SID__ .shx{width:34px;height:34px;border-radius:50%;border:1px solid var(--stroke);background:var(--card);font-size:20px;line-height:1;display:grid;place-items:center;}
#rcl-fnd-__SID__ .shx:hover{background:color-mix(in srgb,var(--ink) 6%,transparent);}
#rcl-fnd-__SID__ .shload{display:flex;align-items:center;justify-content:center;gap:10px;min-height:220px;color:var(--mut);font-size:15px;font-weight:540;}
#rcl-fnd-__SID__ .shload .sp{width:12px;height:12px;border-radius:50%;border:2px solid color-mix(in srgb,var(--ac) 30%,transparent);border-top-color:var(--ac);animation:fspin .8s linear infinite;}
#rcl-fnd-__SID__ .shimg{width:100%;border-radius:16px;display:block;border:1px solid var(--stroke);}
#rcl-fnd-__SID__ .shrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:9px;margin-top:14px;}
#rcl-fnd-__SID__ .shbtn{display:flex;flex-direction:column;align-items:center;gap:7px;padding:13px 6px;border-radius:14px;border:1px solid var(--stroke);background:var(--card);font-size:12px;font-weight:600;cursor:pointer;transition:transform .25s,border-color .25s,background .25s;}
#rcl-fnd-__SID__ .shbtn:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--ac) 55%,var(--stroke));background:color-mix(in srgb,var(--ac) 7%,var(--card));}
#rcl-fnd-__SID__ .shbtn svg{width:24px;height:24px;}

/* ---------- INTRO ---------- */
#rcl-fnd-__SID__ .intro{position:relative;text-align:center;max-width:680px;margin:0 auto;display:flex;flex-direction:column;align-items:center;}
#rcl-fnd-__SID__ .sparks{position:absolute;inset:-6% 0 0 0;pointer-events:none;z-index:-1;}
#rcl-fnd-__SID__ .sparks i{position:absolute;width:7px;height:7px;border-radius:50%;background:var(--ac);opacity:0;filter:blur(.3px);box-shadow:0 0 10px color-mix(in srgb,var(--ac) 70%,transparent);animation:fspark 7s ease-in-out infinite;}
#rcl-fnd-__SID__ .sparks i:nth-child(1){left:12%;top:18%;animation-delay:.4s}
#rcl-fnd-__SID__ .sparks i:nth-child(2){left:84%;top:26%;animation-delay:1.8s;width:5px;height:5px}
#rcl-fnd-__SID__ .sparks i:nth-child(3){left:20%;top:62%;animation-delay:3.1s;width:5px;height:5px}
#rcl-fnd-__SID__ .sparks i:nth-child(4){left:78%;top:68%;animation-delay:4.6s}
@keyframes fspark{0%,100%{opacity:0;transform:translateY(8px) scale(.6)}40%,60%{opacity:.7;transform:translateY(-6px) scale(1)}}
#rcl-fnd-__SID__ .intro .pill{animation:frise 1s .05s both;}
#rcl-fnd-__SID__ h1.htl{font-size:clamp(34px,8.4vw,68px);line-height:1.04;letter-spacing:-.035em;font-weight:740;margin:18px 0 0;}
#rcl-fnd-__SID__ h1.htl .w{display:inline-block;animation:fwordrise 1.15s both;}
#rcl-fnd-__SID__ h1.htl .w:nth-child(1){animation-delay:.12s}
#rcl-fnd-__SID__ h1.htl .w:nth-child(2){animation-delay:.28s}
#rcl-fnd-__SID__ h1.htl .w:nth-child(3){animation-delay:.44s}
#rcl-fnd-__SID__ h1.htl .w:nth-child(4){animation-delay:.60s}
#rcl-fnd-__SID__ h1.htl .w:nth-child(5){animation-delay:.76s}
#rcl-fnd-__SID__ h1.htl .w:last-child{background:linear-gradient(100deg,var(--ac),color-mix(in srgb,var(--ac) 42%,var(--ink)));-webkit-background-clip:text;background-clip:text;}
@keyframes fwordrise{0%{opacity:0;transform:translateY(48%) rotate(2deg);filter:blur(8px)}100%{opacity:1;transform:none;filter:blur(0)}}
#rcl-fnd-__SID__ .hl{max-width:540px;margin:22px auto 0;font-size:clamp(15.5px,4vw,19px);line-height:1.62;color:var(--mut);animation:frise 1s .7s both;}
#rcl-fnd-__SID__ .hmeta{display:flex;flex-wrap:wrap;gap:9px;justify-content:center;margin-top:24px;animation:frise 1s .85s both;}
#rcl-fnd-__SID__ .hmeta span{font-size:13px;font-weight:560;color:var(--mut);padding:9px 16px;border-radius:100px;border:1px solid var(--stroke);background:var(--glass);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);display:inline-flex;align-items:center;gap:8px;}
#rcl-fnd-__SID__ .hmeta span::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--ac);}
#rcl-fnd-__SID__ .intro .cta-wrap{margin-top:30px;animation:frise 1s 1s both;}
#rcl-fnd-__SID__ .strip{position:relative;width:100%;max-width:560px;margin:34px auto 0;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);animation:frise 1s 1.15s both;}
#rcl-fnd-__SID__ .strip .tr{display:flex;gap:12px;width:max-content;animation:fmq 40s linear infinite;}
#rcl-fnd-__SID__ .strip:hover .tr{animation-play-state:paused;}
#rcl-fnd-__SID__ .strip img{width:74px;height:74px;border-radius:14px;object-fit:cover;border:1px solid var(--stroke);background:var(--card);}
@keyframes fmq{to{transform:translateX(-50%)}}
@keyframes frise{0%{opacity:0;transform:translateY(26px)}100%{opacity:1;transform:none}}

/* ---------- question heads ---------- */
#rcl-fnd-__SID__ .qhead{text-align:center;max-width:620px;margin:0 auto 26px;}
#rcl-fnd-__SID__ .qcount{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--ac);text-transform:uppercase;padding:7px 14px;border-radius:100px;background:color-mix(in srgb,var(--ac) 12%,transparent);}
#rcl-fnd-__SID__ .qttl{font-size:clamp(23px,6vw,38px);letter-spacing:-.025em;font-weight:720;margin:14px 0 0;line-height:1.12;}
#rcl-fnd-__SID__ .qsub{margin:10px 0 0;color:var(--mut);font-size:clamp(14.5px,3.6vw,16px);line-height:1.5;}
#rcl-fnd-__SID__ .qmulti{display:inline-flex;align-items:center;gap:7px;margin-top:12px;font-size:12.5px;font-weight:560;color:var(--ac);padding:6px 13px;border-radius:100px;border:1px dashed color-mix(in srgb,var(--ac) 45%,var(--stroke));}
#rcl-fnd-__SID__ .qmulti::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--ac);}

/* ---------- option grid ---------- */
#rcl-fnd-__SID__ .opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(228px,1fr));gap:13px;max-width:760px;margin:0 auto;}
#rcl-fnd-__SID__ .opt{position:relative;text-align:left;padding:20px;border-radius:20px;background:var(--card);border:1.5px solid var(--stroke);overflow:hidden;display:flex;align-items:center;gap:15px;transform-style:preserve-3d;transition:transform .45s cubic-bezier(.2,.7,.2,1),border-color .45s,box-shadow .45s;animation:foptin .85s both;}
@keyframes foptin{0%{opacity:0;transform:translateY(26px) scale(.96)}100%{opacity:1;transform:none}}
#rcl-fnd-__SID__ .opt::before{content:"";position:absolute;inset:0;border-radius:inherit;opacity:0;transition:opacity .45s;background:radial-gradient(460px circle at var(--mx,50%) var(--my,50%),color-mix(in srgb,var(--oh,var(--ac)) 22%,transparent),transparent 60%);}
#rcl-fnd-__SID__ .opt::after{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;border-radius:4px;background:var(--oh,var(--ac));transform:scaleY(0);transform-origin:center;transition:transform .45s cubic-bezier(.2,.7,.2,1);}
#rcl-fnd-__SID__ .opt:hover{transform:translateY(-5px);border-color:color-mix(in srgb,var(--oh,var(--ac)) 60%,var(--stroke));box-shadow:0 30px 56px -32px color-mix(in srgb,var(--oh,var(--ac)) 60%,#0000);}
#rcl-fnd-__SID__ .opt:hover::before{opacity:1;}
#rcl-fnd-__SID__ .opt:hover::after{transform:scaleY(.55);}
#rcl-fnd-__SID__ .opt.sel{border-color:var(--oh,var(--ac));box-shadow:0 0 0 3px color-mix(in srgb,var(--oh,var(--ac)) 24%,transparent),0 24px 48px -30px color-mix(in srgb,var(--oh,var(--ac)) 70%,#0000);animation:fpop .5s cubic-bezier(.3,1.4,.5,1);}
@keyframes fpop{0%{transform:scale(1)}45%{transform:scale(1.035)}100%{transform:scale(1)}}
#rcl-fnd-__SID__ .opt.sel::after{transform:scaleY(.7);}
#rcl-fnd-__SID__ .opt.sel .oic{background:var(--oh,var(--ac));color:#fff;}
#rcl-fnd-__SID__ .opt .oic{flex:none;width:52px;height:52px;border-radius:15px;display:grid;place-items:center;background:color-mix(in srgb,var(--oh,var(--ac)) 14%,var(--card));color:var(--oh,var(--ac));transition:background .4s,color .4s,transform .4s;}
#rcl-fnd-__SID__ .opt:hover .oic{transform:scale(1.07) rotate(-3deg);}
#rcl-fnd-__SID__ .opt .oic svg{width:26px;height:26px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;animation:ficon 5s ease-in-out infinite;}
#rcl-fnd-__SID__ .opt:nth-child(2) .oic svg{animation-delay:.6s}
#rcl-fnd-__SID__ .opt:nth-child(3) .oic svg{animation-delay:1.2s}
#rcl-fnd-__SID__ .opt:nth-child(4) .oic svg{animation-delay:1.8s}
#rcl-fnd-__SID__ .opt:nth-child(5) .oic svg{animation-delay:2.4s}
@keyframes ficon{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-2.5px) rotate(2deg)}}
#rcl-fnd-__SID__ .opt.sel .oic svg{animation:ficonpop .55s cubic-bezier(.3,1.5,.5,1);}
@keyframes ficonpop{0%{transform:scale(1)}40%{transform:scale(1.25) rotate(-8deg)}100%{transform:scale(1)}}
/* soft animated glow ring on selected option icon */
#rcl-fnd-__SID__ .opt.sel .oic{box-shadow:0 0 0 0 color-mix(in srgb,var(--oh,var(--ac)) 45%,transparent);animation:ficonglow 1.8s ease-out infinite;}
@keyframes ficonglow{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--oh,var(--ac)) 50%,transparent)}100%{box-shadow:0 0 0 12px color-mix(in srgb,var(--oh,var(--ac)) 0%,transparent)}}
#rcl-fnd-__SID__ .opt .ot{display:flex;flex-direction:column;gap:3px;min-width:0;}
#rcl-fnd-__SID__ .opt .ol{font-size:clamp(16px,4.2vw,17px);font-weight:640;letter-spacing:-.01em;}
#rcl-fnd-__SID__ .opt .os{font-size:13.5px;color:var(--mut);line-height:1.4;}
#rcl-fnd-__SID__ .opt .ok{position:absolute;top:13px;right:13px;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--oh,var(--ac));color:#fff;opacity:0;transform:scale(.4);transition:opacity .4s,transform .45s cubic-bezier(.3,1.5,.5,1);}
#rcl-fnd-__SID__ .opt.sel .ok{opacity:1;transform:none;}
#rcl-fnd-__SID__ .opt .ok svg{width:13px;height:13px;fill:none;stroke:currentColor;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;}
#rcl-fnd-__SID__ .qnext{display:flex;justify-content:center;margin-top:24px;animation:frise .8s .25s both;}

/* ---------- profile form ---------- */
#rcl-fnd-__SID__ .pform{max-width:540px;margin:0 auto;display:grid;gap:20px;}
#rcl-fnd-__SID__ .field{animation:foptin .75s both;}
#rcl-fnd-__SID__ .field label{display:block;font-size:14.5px;font-weight:640;margin-bottom:11px;}
#rcl-fnd-__SID__ .field input{width:100%;padding:16px 18px;border-radius:15px;border:1.5px solid var(--stroke);background:var(--card);font-size:16px;color:var(--ink);transition:border-color .4s,box-shadow .4s;}
#rcl-fnd-__SID__ .field input::placeholder{color:color-mix(in srgb,var(--ink) 42%,transparent);}
#rcl-fnd-__SID__ .field input:focus{outline:0;border-color:var(--ac);box-shadow:0 0 0 4px color-mix(in srgb,var(--ac) 16%,transparent);}
#rcl-fnd-__SID__ .chips{display:flex;flex-wrap:wrap;gap:9px;}
#rcl-fnd-__SID__ .chip{padding:12px 19px;border-radius:100px;border:1.5px solid var(--stroke);background:var(--card);font-size:14.5px;font-weight:540;transition:all .35s cubic-bezier(.2,.7,.2,1);}
#rcl-fnd-__SID__ .chip:hover{border-color:color-mix(in srgb,var(--ac) 55%,var(--stroke));transform:translateY(-2px);}
#rcl-fnd-__SID__ .chip.sel{background:var(--ac);color:#fff;border-color:var(--ac);box-shadow:0 14px 28px -14px var(--ac);transform:translateY(-1px);}
#rcl-fnd-__SID__ .pact{display:flex;flex-direction:column;align-items:center;gap:12px;margin-top:8px;}
#rcl-fnd-__SID__ .hint{font-size:13px;color:var(--ac);min-height:18px;text-align:center;font-weight:540;}

/* ---------- analyze ---------- */
#rcl-fnd-__SID__ .anz{text-align:center;max-width:520px;margin:0 auto;display:grid;place-items:center;gap:28px;}
#rcl-fnd-__SID__ .ringwrap{position:relative;width:clamp(190px,54vw,232px);aspect-ratio:1;display:grid;place-items:center;}
#rcl-fnd-__SID__ .ringwrap::before,#rcl-fnd-__SID__ .ringwrap::after{content:"";position:absolute;inset:0;border-radius:50%;border:1.5px solid color-mix(in srgb,var(--ac) 32%,transparent);animation:fpulsering 3s ease-out infinite;}
#rcl-fnd-__SID__ .ringwrap::after{animation-delay:1.5s;}
@keyframes fpulsering{0%{transform:scale(.82);opacity:.85}100%{transform:scale(1.4);opacity:0}}
#rcl-fnd-__SID__ .ring{position:relative;width:100%;height:100%;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--ac) calc(var(--p,0)*1%),color-mix(in srgb,var(--ink) 10%,transparent) 0);transition:background .15s linear;animation:fbreath 4s ease-in-out infinite;}
@keyframes fbreath{0%,100%{transform:scale(1)}50%{transform:scale(1.025)}}
#rcl-fnd-__SID__ .ring::before{content:"";position:absolute;inset:16px;border-radius:50%;background:var(--bg);box-shadow:inset 0 2px 14px rgba(0,0,0,.06);}
#rcl-fnd-__SID__ .ring .pv{position:relative;z-index:2;font-size:clamp(42px,13vw,52px);font-weight:760;letter-spacing:-.03em;}
#rcl-fnd-__SID__ .ring .pv small{font-size:22px;font-weight:640;}
#rcl-fnd-__SID__ .ring .pl{position:relative;z-index:2;font-size:11px;letter-spacing:.18em;color:var(--mut);text-transform:uppercase;margin-top:2px;}
#rcl-fnd-__SID__ .ascan{position:absolute;inset:-7px;border-radius:50%;border:2px solid transparent;border-top-color:var(--ac);border-right-color:color-mix(in srgb,var(--ac) 40%,transparent);animation:fspin 1.4s linear infinite;}
@keyframes fspin{to{transform:rotate(360deg)}}
#rcl-fnd-__SID__ .orbit{position:absolute;inset:0;animation:fspin 4.4s linear infinite;}
#rcl-fnd-__SID__ .orbit:nth-of-type(2){animation-duration:6.2s;animation-direction:reverse;}
#rcl-fnd-__SID__ .orbit:nth-of-type(3){animation-duration:8s;}
#rcl-fnd-__SID__ .orbit i{position:absolute;top:-5px;left:50%;width:11px;height:11px;margin-left:-5px;border-radius:50%;background:var(--ac);box-shadow:0 0 14px color-mix(in srgb,var(--ac) 80%,transparent);}
#rcl-fnd-__SID__ .orbit:nth-of-type(2) i{background:var(--ac2);width:8px;height:8px;}
#rcl-fnd-__SID__ .orbit:nth-of-type(3) i{background:color-mix(in srgb,var(--ac) 60%,#fff);width:6px;height:6px;top:auto;bottom:-4px;}
#rcl-fnd-__SID__ .astep{font-size:clamp(15px,4vw,16.5px);font-weight:560;min-height:24px;display:flex;align-items:center;gap:10px;justify-content:center;}
#rcl-fnd-__SID__ .astep .sp{width:8px;height:8px;border-radius:50%;background:var(--ac);animation:fpulse 1.4s ease-in-out infinite;}
#rcl-fnd-__SID__ .astep .atxt{transition:opacity .35s;}
#rcl-fnd-__SID__ .athumbs{position:relative;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;overflow:hidden;border-radius:16px;padding:4px;}
#rcl-fnd-__SID__ .athumbs::after{content:"";position:absolute;top:0;bottom:0;left:-40%;width:32%;background:linear-gradient(100deg,transparent,color-mix(in srgb,var(--ac) 38%,transparent),transparent);animation:fsweep 2.4s ease-in-out infinite;}
@keyframes fsweep{0%{left:-40%}100%{left:120%}}
#rcl-fnd-__SID__ .athumbs img{width:56px;height:56px;border-radius:12px;object-fit:cover;border:1px solid var(--stroke);opacity:.5;animation:fblink 2s ease-in-out infinite;}
@keyframes fblink{0%,100%{opacity:.3;transform:scale(.9)}50%{opacity:1;transform:scale(1)}}

/* ---------- results ---------- */
#rcl-fnd-__SID__ .rhead{text-align:center;max-width:640px;margin:0 auto 30px;}
#rcl-fnd-__SID__ .rttl{font-size:clamp(24px,6vw,40px);letter-spacing:-.025em;font-weight:740;margin:12px 0 0;line-height:1.1;}
#rcl-fnd-__SID__ .rsub{margin:12px 0 0;color:var(--mut);font-size:clamp(14.5px,3.6vw,17px);line-height:1.55;}
#rcl-fnd-__SID__ .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;align-items:stretch;}
#rcl-fnd-__SID__ .rc{position:relative;display:flex;flex-direction:column;border-radius:22px;overflow:hidden;background:var(--card);border:1.5px solid var(--stroke);opacity:0;transform:translateY(36px) scale(.96);animation:fcardin 1s cubic-bezier(.2,.8,.3,1) forwards;transition:box-shadow .5s,transform .45s;}
@keyframes fcardin{to{opacity:1;transform:none}}
#rcl-fnd-__SID__ .rc:hover{box-shadow:0 40px 80px -38px rgba(15,20,25,.55);transform:translateY(-6px);}
#rcl-fnd-__SID__ .rc.best{border-color:color-mix(in srgb,var(--ac) 60%,var(--stroke));box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 18%,transparent);}
#rcl-fnd-__SID__ .rc.best::before{content:"";position:absolute;inset:0;z-index:4;pointer-events:none;background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.5) 48%,transparent 62%);transform:translateX(-100%);animation:fshimmer 4.5s ease-in-out 1.4s infinite;}
@keyframes fshimmer{0%{transform:translateX(-100%)}50%,100%{transform:translateX(120%)}}
#rcl-fnd-__SID__ .rc .rank{position:absolute;top:13px;left:13px;z-index:3;font-size:11px;font-weight:740;letter-spacing:.1em;padding:6px 12px;border-radius:100px;background:var(--ink);color:var(--bg);}
#rcl-fnd-__SID__ .rc.best .rank{background:var(--ac);color:#fff;}
#rcl-fnd-__SID__ .rimg{position:relative;aspect-ratio:1;background:linear-gradient(160deg,color-mix(in srgb,var(--ac) 11%,var(--card)),var(--card));overflow:hidden;}
#rcl-fnd-__SID__ .rimg img{width:100%;height:100%;object-fit:cover;transition:transform .7s ease;}
#rcl-fnd-__SID__ .rc:hover .rimg img{transform:scale(1.07);}
#rcl-fnd-__SID__ .mbadge{position:absolute;right:12px;bottom:12px;z:3;z-index:3;display:flex;align-items:center;gap:8px;padding:9px 14px;border-radius:100px;background:color-mix(in srgb,var(--bg) 86%,transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border:1px solid var(--stroke);}
#rcl-fnd-__SID__ .mbadge b{font-size:20px;font-weight:760;letter-spacing:-.02em;color:var(--ac);}
#rcl-fnd-__SID__ .mbadge span{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;}
#rcl-fnd-__SID__ .rbody{padding:18px;display:flex;flex-direction:column;gap:11px;flex:1;}
#rcl-fnd-__SID__ .rbrand{font-size:11px;font-weight:740;letter-spacing:.13em;color:var(--ac);text-transform:uppercase;}
#rcl-fnd-__SID__ .rname{font-size:clamp(17px,4.4vw,19px);font-weight:660;letter-spacing:-.01em;line-height:1.2;}
#rcl-fnd-__SID__ .rbar{height:7px;border-radius:100px;background:color-mix(in srgb,var(--ink) 10%,transparent);overflow:hidden;}
#rcl-fnd-__SID__ .rbar i{display:block;height:100%;width:0;border-radius:100px;background:linear-gradient(90deg,var(--ac2),var(--ac));transition:width 1.4s cubic-bezier(.3,.8,.3,1);}
#rcl-fnd-__SID__ .rwhy{font-size:14px;line-height:1.56;color:var(--mut);flex:1;}
#rcl-fnd-__SID__ .rprice{font-size:19px;font-weight:720;letter-spacing:-.01em;}
#rcl-fnd-__SID__ .rc .vbtn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:14px 18px;border-radius:100px;background:var(--ink);color:var(--bg);font-size:15px;font-weight:580;transition:transform .4s,box-shadow .4s;}
#rcl-fnd-__SID__ .rc.best .vbtn{background:var(--ac);box-shadow:0 16px 32px -16px var(--ac);}
#rcl-fnd-__SID__ .rc .vbtn:hover{transform:translateY(-2px);}
#rcl-fnd-__SID__ .rc .vbtn svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}
#rcl-fnd-__SID__ .ract{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:32px;animation:frise 1s .8s both;}

/* ---------- SEO block ---------- */
#rcl-fnd-__SID__ .seo{margin-top:clamp(56px,8vw,100px);}
#rcl-fnd-__SID__ .seo h2{font-size:clamp(24px,5.4vw,36px);letter-spacing:-.025em;font-weight:720;margin:0;line-height:1.12;}
#rcl-fnd-__SID__ .seo p.lede{margin:16px 0 0;color:var(--mut);font-size:clamp(15px,3.6vw,17px);line-height:1.66;max-width:780px;}
#rcl-fnd-__SID__ .sm{font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--ac);text-transform:uppercase;}
#rcl-fnd-__SID__ .cats{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px;margin-top:20px;}
#rcl-fnd-__SID__ .cat{padding:22px;border-radius:18px;transition:transform .5s,box-shadow .5s;}
#rcl-fnd-__SID__ .cat:hover{transform:translateY(-4px);box-shadow:0 28px 54px -32px rgba(15,20,25,.45);}
#rcl-fnd-__SID__ .cat h3{margin:0;font-size:17px;font-weight:640;letter-spacing:-.01em;}
#rcl-fnd-__SID__ .cat p{margin:8px 0 0;font-size:14px;color:var(--mut);line-height:1.5;}
#rcl-fnd-__SID__ .cat .go{margin-top:13px;display:inline-flex;align-items:center;gap:7px;font-size:13.5px;font-weight:580;color:var(--ac);}
#rcl-fnd-__SID__ .cat .go svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;transition:transform .4s;}
#rcl-fnd-__SID__ .cat:hover .go svg{transform:translateX(4px);}
#rcl-fnd-__SID__ .faq{margin-top:18px;display:grid;gap:11px;}
#rcl-fnd-__SID__ .item .q{width:100%;border:0;background:transparent;text-align:left;padding:20px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px;}
#rcl-fnd-__SID__ .item .q span{font-size:clamp(15px,4vw,17px);font-weight:580;letter-spacing:-.01em;}
#rcl-fnd-__SID__ .pm{flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;background:color-mix(in srgb,var(--ac) 12%,var(--card));color:var(--ac);transition:transform .45s cubic-bezier(.2,.7,.2,1);}
#rcl-fnd-__SID__ .pm svg{width:14px;height:14px;stroke:currentColor;stroke-width:2.4;fill:none;stroke-linecap:round;}
#rcl-fnd-__SID__ .item[aria-expanded="true"] .pm{transform:rotate(45deg);}
#rcl-fnd-__SID__ .item .a{overflow:hidden;height:0;transition:height .45s cubic-bezier(.2,.7,.2,1);}
#rcl-fnd-__SID__ .item .a-in{padding:0 22px 22px;color:var(--mut);font-size:15px;line-height:1.62;}

/* ---------- responsive ---------- */
@media (max-width:820px){
  #rcl-fnd-__SID__ .cards{grid-template-columns:1fr;max-width:430px;margin:0 auto;}
  #rcl-fnd-__SID__ .stage{min-height:540px;}
}
@media (max-width:560px){
  #rcl-fnd-__SID__ .opts{grid-template-columns:1fr;}
  #rcl-fnd-__SID__ .opt{padding:16px 18px;}
  #rcl-fnd-__SID__ .opt .oic{width:46px;height:46px;border-radius:13px;}
  #rcl-fnd-__SID__ .opt .oic svg{width:23px;height:23px;}
  #rcl-fnd-__SID__ .pad{padding-left:14px;padding-right:14px;}
  #rcl-fnd-__SID__ .qnext .pbtn,#rcl-fnd-__SID__ .ract .pbtn,#rcl-fnd-__SID__ .ract .sbtn{width:100%;justify-content:center;}
}
@media (prefers-reduced-motion:reduce){
  #rcl-fnd-__SID__ *{animation-duration:.001s!important;animation-iteration-count:1!important;transition-duration:.001s!important;}
  #rcl-fnd-__SID__ h1.htl .w,#rcl-fnd-__SID__ .intro .pill,#rcl-fnd-__SID__ .hl,#rcl-fnd-__SID__ .hmeta,#rcl-fnd-__SID__ .intro .cta-wrap,#rcl-fnd-__SID__ .strip,#rcl-fnd-__SID__ .field,#rcl-fnd-__SID__ .opt,#rcl-fnd-__SID__ .rc,#rcl-fnd-__SID__ .qnext,#rcl-fnd-__SID__ .ract{opacity:1!important;transform:none!important;filter:none!important;}
  #rcl-fnd-__SID__ .app::before,#rcl-fnd-__SID__ .aurora,#rcl-fnd-__SID__ .sparks i{animation:none!important;}
}

/* ====================================================================
   COLOR HARDENING - last in source so it wins ties. Every selector is
   ID-scoped (specificity >= 1,0,1) so it beats any host-theme element/
   class rule even with !important (themes almost never use IDs). Keeps
   every RCL text readable no matter how aggressive the theme CSS is.
   ==================================================================== */
#rcl-fnd-__SID__ h1,#rcl-fnd-__SID__ h2,#rcl-fnd-__SID__ h3,#rcl-fnd-__SID__ h4,#rcl-fnd-__SID__ h5,#rcl-fnd-__SID__ h6,#rcl-fnd-__SID__ p,#rcl-fnd-__SID__ span,#rcl-fnd-__SID__ a,#rcl-fnd-__SID__ li,#rcl-fnd-__SID__ div,#rcl-fnd-__SID__ label,#rcl-fnd-__SID__ small,#rcl-fnd-__SID__ b,#rcl-fnd-__SID__ strong,#rcl-fnd-__SID__ em,#rcl-fnd-__SID__ button,#rcl-fnd-__SID__ input{-webkit-text-fill-color:currentColor!important;}
/* ink (primary) broad default */
#rcl-fnd-__SID__ h1,#rcl-fnd-__SID__ h2,#rcl-fnd-__SID__ h3,#rcl-fnd-__SID__ h4,#rcl-fnd-__SID__ h5,#rcl-fnd-__SID__ h6,#rcl-fnd-__SID__ p,#rcl-fnd-__SID__ span,#rcl-fnd-__SID__ a,#rcl-fnd-__SID__ li,#rcl-fnd-__SID__ div,#rcl-fnd-__SID__ label,#rcl-fnd-__SID__ small,#rcl-fnd-__SID__ b,#rcl-fnd-__SID__ strong,#rcl-fnd-__SID__ em,#rcl-fnd-__SID__ button,#rcl-fnd-__SID__ input{color:var(--ink)!important;}
#rcl-fnd-__SID__ .field input::placeholder{color:color-mix(in srgb,var(--ink) 42%,transparent)!important;-webkit-text-fill-color:color-mix(in srgb,var(--ink) 42%,transparent)!important;}
/* muted */
#rcl-fnd-__SID__ .hl,#rcl-fnd-__SID__ .qsub,#rcl-fnd-__SID__ .rsub,#rcl-fnd-__SID__ .lede,#rcl-fnd-__SID__ .opt .os,#rcl-fnd-__SID__ .rwhy,#rcl-fnd-__SID__ .cat p,#rcl-fnd-__SID__ .item .a-in,#rcl-fnd-__SID__ .ring .pl,#rcl-fnd-__SID__ .mbadge span,#rcl-fnd-__SID__ .hmeta span{color:var(--mut)!important;}
/* accent */
#rcl-fnd-__SID__ .pill,#rcl-fnd-__SID__ .qcount,#rcl-fnd-__SID__ .qmulti,#rcl-fnd-__SID__ .sm,#rcl-fnd-__SID__ .rbrand,#rcl-fnd-__SID__ .cat .go,#rcl-fnd-__SID__ .hint,#rcl-fnd-__SID__ .mbadge b,#rcl-fnd-__SID__ .pm{color:var(--ac)!important;}
/* option icon uses its per-answer hue */
#rcl-fnd-__SID__ .opt .oic{color:var(--oh,var(--ac))!important;}
/* text on filled (dark/accent) backgrounds */
#rcl-fnd-__SID__ .pbtn,#rcl-fnd-__SID__ .rc .vbtn,#rcl-fnd-__SID__ .rank{color:var(--bg)!important;}
#rcl-fnd-__SID__ .startbtn{color:#fff!important;}
#rcl-fnd-__SID__ .sbtn{color:var(--ink)!important;}
#rcl-fnd-__SID__ .rc.best .rank,#rcl-fnd-__SID__ .chip.sel,#rcl-fnd-__SID__ .opt.sel .oic,#rcl-fnd-__SID__ .opt .ok{color:#fff!important;}
/* Kill any host-theme gradient-heading effect: themes that do
   `h2{background:<gradient>;-webkit-background-clip:text;-webkit-text-fill-color:transparent}`
   make our titles invisible. Force solid ink fill on every heading. */
#rcl-fnd-__SID__ h1,#rcl-fnd-__SID__ h2,#rcl-fnd-__SID__ h3,#rcl-fnd-__SID__ h4,#rcl-fnd-__SID__ h5,#rcl-fnd-__SID__ h6{background:none!important;background-image:none!important;-webkit-background-clip:border-box!important;background-clip:border-box!important;-webkit-text-fill-color:var(--ink)!important;}
/* Re-establish OUR gradient on the last hero word only (higher specificity beats the reset). */
#rcl-fnd-__SID__ h1.htl .w:last-child{background:linear-gradient(100deg,var(--ac),color-mix(in srgb,var(--ac) 42%,var(--ink)))!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-fill-color:transparent!important;}
{%- endstyle -%}
"""

# ============================================================ JS
JS = r"""
<script>
(function(){
  var root=document.getElementById("rcl-fnd-__SID__");
  if(!root||root.dataset.init)return; root.dataset.init="1";
  var D=__DATA__;
  var rm=window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches;
  var hov=window.matchMedia&&matchMedia("(hover:hover)").matches;
  var SVG=D.svg;
  function svg(k,cls){return '<svg class="'+(cls||"")+'" viewBox="0 0 24 24" aria-hidden="true">'+(SVG[k]||"")+'</svg>';}
  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c];});}

  var app=root.querySelector(".app");
  var stage=root.querySelector(".stage");
  var bar=root.querySelector(".prog i");
  var state={name:"",age:"",gender:"",city:"",ans:[]};
  var stock=[];
  var SID=(Math.random().toString(36).slice(2)+Date.now().toString(36)); // tarayici oturum id'si

  // Tamamlanan testi HQ dashboard'a (Vercel Blob) kaydet - engellemez, hatasi yutulur.
  function logSubmission(picks){
    if(!D.log_url)return;
    try{
      var lab=function(qi){return (state.ans[qi]||[]).map(function(o){return o.label;});};
      var top=(picks&&picks[0])||{};
      var payload={sid:SID,name:state.name,age:state.age,gender:state.gender,city:state.city,
        use:lab(0),budget:lab(1),aes:lab(2),env:lab(3),level:lab(4),occasion:lab(5),
        top_brand:top.brand||"",top_price:(top.priceN||priceOf(top||{})||0),
        recommended:(picks||[]).map(function(c){return {title:c.title,brand:c.brand,pct:c.pct,handle:c.handle};}),
        source:"shopify",page:(window.location&&window.location.pathname)||""};
      fetch(D.log_url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload),keepalive:true}).catch(function(){});
    }catch(e){}
  }

  function fmtPrice(raw,cents){var n=parseFloat(raw);if(isNaN(n))return"";if(cents)n=n/100;n=Math.round(n);return n.toLocaleString("tr-TR")+" TL";}
  function fnum(s){var n=parseFloat(String(s==null?"":s).replace(",","."));return isNaN(n)?0:n;}
  // Canli urunun aciklama/etiket/basligindan gercek ozellikleri cikar (eslestirme bunlara dayanir).
  function parseFeat(p){
    var txt=(String(p.description||p.body_html||"")+" "+String(p.title||"")+" "+[].concat(p.tags||[]).join(" ")).toLowerCase();
    var f={};
    var ym=txt.match(/\b(19|20)\d{2}\b/); f.year=ym?+ym[0]:0;
    var mp=txt.match(/(\d{1,2}(?:[.,]\d)?)\s*(?:mp|megapiksel|mega\s?pixel)/); f.mp=mp?fnum(mp[1]):0;
    var zm=txt.match(/(\d{1,3})\s*x\s*(?:optik|optical|leica|zoom)/); f.zoom=zm?+zm[1]:0;
    f.flash=/fla[s\u015F]|flash/.test(txt);
    f.water=/su ge[c\u00E7]irmez|waterproof|weather|dayan[\u0131i]kl/.test(txt);
    f.video=/vlog|video|720p|1080p|film\s?kayd/.test(txt);
    f.touch=/dokunmatik|touch/.test(txt);
    f.macro=/makro|macro/.test(txt);
    f.wide=/geni[s\u015F] a[c\u00E7][\u0131i]|wide|ultra geni/.test(txt);
    f.slim=/ince|slim|cep boy|kompakt|ultra-ince|ultra ince/.test(txt);
    return f;
  }
  function norm(arr,cents){
    var out=[];
    (arr||[]).forEach(function(p){
      var type=String(p.type||p.product_type||"").toLowerCase();
      var title=String(p.title||"");
      if(type.indexOf("aksesuar")>=0)return;
      if(/hediye|gift|\u00E7anta|kart|pil|adapt|temizli/i.test(title))return;
      var avail=("available" in p)? !!p.available : (p.variants||[]).some(function(v){return v.available;});
      if(!avail)return;
      var im=p.featured_image||p.image||(p.images&&p.images[0]&&(p.images[0].src||p.images[0]))||"";
      if(im&&typeof im==="object")im=im.src||"";
      if(im&&im.indexOf("//")===0)im="https:"+im;
      if(!im)return;
      var priceRaw=(p.price!=null)?p.price:(p.variants&&p.variants[0]&&p.variants[0].price);
      var priceN=cents?(fnum(priceRaw)/100):fnum(priceRaw);
      var price=(typeof p.price==="string"&&/TL/.test(p.price))?p.price:fmtPrice(priceRaw,cents);
      var tags=p.tags||[];
      var brand=p.brand||(Array.isArray(tags)&&tags[0])||p.vendor||"RetroCameraLand";
      var f=parseFeat(p);
      out.push({title:title,handle:p.handle||"",image:im,price:price,priceN:priceN,brand:brand,
        year:f.year,mp:f.mp,zoom:f.zoom,flash:f.flash,water:f.water,video:f.video,touch:f.touch,macro:f.macro,wide:f.wide,slim:f.slim});
    });
    return out;
  }
  function img(u,w){if(!u)return u;return u+((u.indexOf("?")>=0)?"&":"?")+"width="+w;}
  // Canli stok: SADECE su an stokta (available) olan kameralar. Onerilen 3 model bundan secilir.
  // 1) /products.js (fiyat kurus) -> bos/hatali ise 2) /products.json (fiyat ondalik) yedek kaynak.
  // Ikisi de cokerse statik FALLBACK (build aninda dogrulanmis, stokta olan modeller).
  function fetchJs(){
    return fetch("/products.js?limit=250",{headers:{"Accept":"application/json"},cache:"no-store"})
      .then(function(r){return r.ok?r.json():null;})
      .then(function(d){ if(d) stock=norm(d.products||d,true); }).catch(function(){});
  }
  function fetchJson(){
    return fetch("/products.json?limit=250",{headers:{"Accept":"application/json"},cache:"no-store"})
      .then(function(r){return r.ok?r.json():null;})
      .then(function(d){ if(d) stock=norm(d.products||d,false); }).catch(function(){});
  }
  var stockReady=(window.__RCL_STOCK__)
    ? Promise.resolve(stock=norm(window.__RCL_STOCK__,false))
    : fetchJs().then(function(){ return (stock&&stock.length)?null:fetchJson(); });

  function swap(el){
    var old=stage.firstElementChild;
    el.classList.add("scr","enter");
    stage.appendChild(el);
    void el.offsetWidth;
    el.classList.remove("enter");
    if(old){old.classList.add("leave");setTimeout(function(){if(old.parentNode)old.parentNode.removeChild(old);},760);}
    try{var top=app.getBoundingClientRect().top;if(top<-30||top>160)app.scrollIntoView({behavior:rm?"auto":"smooth",block:"start"});}catch(e){}
  }
  function setProg(p){bar.style.width=Math.round(p*100)+"%";}
  function setAccent(hue){if(hue)root.style.setProperty("--ac",hue);}
  var STEPS=D.questions.length+1;          // profil + sorular (qcount gosterimi)
  var TOTAL=D.questions.length+2;          // + sonuc (ilerleme cubugu paydasi)

  var sb=root.querySelector(".startbtn");
  if(sb)sb.addEventListener("click",function(){app.classList.add("started");state.ans=[];showProfile();});

  function showProfile(){
    setProg(1/TOTAL);
    var P=D.profile;
    var el=document.createElement("div");
    var ages=P.ages.map(function(a){return '<button type="button" class="chip" data-g="age" data-v="'+esc(a)+'">'+esc(a)+'</button>';}).join("");
    var gens=P.genders.map(function(a){return '<button type="button" class="chip" data-g="gender" data-v="'+esc(a)+'">'+esc(a)+'</button>';}).join("");
    var dl=P.cities.map(function(c){return '<option value="'+esc(c)+'">';}).join("");
    function f(i){return 'style="animation-delay:'+(i*90)+'ms"';}
    el.innerHTML=''
      +'<div class="qhead"><span class="qcount">'+esc(D.t.step)+' 1 / '+STEPS+'</span>'
      +'<h2 class="qttl">'+esc(P.title)+'</h2><p class="qsub">'+esc(P.sub)+'</p></div>'
      +'<div class="pform">'
      +'<div class="field" '+f(0)+'><label>'+esc(P.name_label)+'</label><input type="text" autocomplete="given-name" maxlength="40" placeholder="'+esc(P.name_ph)+'" data-f="name"></div>'
      +'<div class="field" '+f(1)+'><label>'+esc(P.age_label)+'</label><div class="chips">'+ages+'</div></div>'
      +'<div class="field" '+f(2)+'><label>'+esc(P.gender_label)+'</label><div class="chips">'+gens+'</div></div>'
      +'<div class="field" '+f(3)+'><label>'+esc(P.city_label)+'</label><input type="text" list="rclcities-__SID__" maxlength="40" placeholder="'+esc(P.city_ph)+'" data-f="city"><datalist id="rclcities-__SID__">'+dl+'</datalist></div>'
      +'<div class="pact" '+f(4)+'><button type="button" class="pbtn" data-cont disabled>'+esc(P.cta)+svg("arrow")+'</button>'
      +'<div class="hint"></div></div></div>';
    swap(el);
    var nameI=el.querySelector('[data-f="name"]'),cityI=el.querySelector('[data-f="city"]');
    var cont=el.querySelector("[data-cont]"),hint=el.querySelector(".hint");
    function refresh(){state.name=nameI.value.trim();state.city=cityI.value.trim();cont.disabled=!(state.name&&state.age&&state.gender);if(!cont.disabled)hint.textContent="";}
    nameI.addEventListener("input",refresh);cityI.addEventListener("input",refresh);
    el.querySelectorAll(".chip").forEach(function(c){
      c.addEventListener("click",function(){var g=c.getAttribute("data-g");
        el.querySelectorAll('.chip[data-g="'+g+'"]').forEach(function(x){x.classList.remove("sel");});
        c.classList.add("sel");state[g]=c.getAttribute("data-v");refresh();});
    });
    cont.addEventListener("click",function(){if(cont.disabled){hint.textContent=P.need_more;return;}state.ans=[];showQuestion(0);});
    if(!rm)setTimeout(function(){try{nameI.focus({preventScroll:true});}catch(e){}},560);
  }

  function tilt(b){
    if(rm||!hov)return;
    b.addEventListener("pointermove",function(ev){var r=b.getBoundingClientRect();
      var px=(ev.clientX-r.left)/r.width,py=(ev.clientY-r.top)/r.height;
      b.style.setProperty("--mx",(px*100)+"%");b.style.setProperty("--my",(py*100)+"%");
      b.style.transform="translateY(-5px) perspective(720px) rotateX("+((py-.5)*-6)+"deg) rotateY("+((px-.5)*7)+"deg)";});
    b.addEventListener("pointerleave",function(){b.style.transform="";});
  }
  // MULTI-SELECT question: toggle options, continue button advances.
  function showQuestion(qi){
    setProg((qi+2)/TOTAL);
    var Q=D.questions[qi];
    var last=qi===D.questions.length-1;
    var el=document.createElement("div");
    var opts=Q.opts.map(function(o,i){
      return '<button type="button" class="opt" style="--oh:'+o.hue+';animation-delay:'+(i*95)+'ms" data-i="'+i+'" aria-pressed="false">'
        +'<span class="oic">'+svg(o.icon)+'</span>'
        +'<span class="ot"><span class="ol">'+esc(o.label)+'</span><span class="os">'+esc(o.sub)+'</span></span>'
        +'<span class="ok">'+svg("check")+'</span></button>';
    }).join("");
    el.innerHTML=''
      +'<div class="qhead"><span class="qcount">'+esc(D.t.step)+' '+(qi+2)+' / '+STEPS+'</span>'
      +'<h2 class="qttl">'+esc(Q.q)+'</h2><p class="qsub">'+esc(Q.sub)+'</p>'
      +'<span class="qmulti">'+esc(D.t.multi)+'</span></div>'
      +'<div class="opts">'+opts+'</div>'
      +'<div class="qnext"><button type="button" class="pbtn qcont" disabled>'+esc(last?D.t.see_results:D.t.next)+svg("arrow")+'</button></div>';
    swap(el);
    var sel=[];
    var cont=el.querySelector(".qcont");
    el.querySelectorAll(".opt").forEach(function(b){
      tilt(b);
      b.addEventListener("click",function(){
        var i=+b.getAttribute("data-i");
        var at=sel.indexOf(i);
        if(at>=0){sel.splice(at,1);b.classList.remove("sel");b.setAttribute("aria-pressed","false");}
        else{sel.push(i);b.classList.add("sel");b.setAttribute("aria-pressed","true");setAccent(Q.opts[i].hue);}
        cont.disabled=sel.length===0;
      });
    });
    cont.addEventListener("click",function(){
      if(!sel.length)return;
      state.ans[qi]=sel.map(function(i){return Q.opts[i];});
      if(last)showAnalyze();else showQuestion(qi+1);
    });
  }

  function firstOf(qi){var a=state.ans[qi];return (a&&a[0])||{};}
  function vals(qi){return (state.ans[qi]||[]).map(function(o){return o.v;});}
  function has(qi,v){return vals(qi).indexOf(v)>=0;}

  // ---- GERCEK ESLESTIRME MOTORU ----
  // Soru sirasi: 0=use 1=budget 2=aes 3=env 4=level 5=occasion
  // Marka karakter vektoru (estetik egilimi + kullanim egilimi) - sayisal, dile bagimsiz.
  var BRAND={
    sony:{aes:{sharp:3,y2k:2,cine:1},use:{daily:2,night:2,travel:1,content:1}},
    canon:{aes:{warm:2,dreamy:1,y2k:1,sharp:1},use:{portrait:3,daily:2}},
    fujifilm:{aes:{cine:3,dreamy:2,warm:2},use:{portrait:2,travel:1,daily:1}},
    fuji:{aes:{cine:3,dreamy:2,warm:2},use:{portrait:2,travel:1,daily:1}},
    olympus:{aes:{sharp:2,cine:1,warm:1},use:{travel:2,daily:1,portrait:1}},
    lumix:{aes:{sharp:2,cine:1},use:{travel:3,content:2,daily:1}},
    panasonic:{aes:{sharp:2,cine:1},use:{travel:3,content:2,daily:1}},
    kodak:{aes:{warm:3,dreamy:2,y2k:2},use:{daily:1,content:1,travel:1}},
    nikon:{aes:{sharp:1,y2k:2,warm:1},use:{daily:2,night:1,portrait:1}},
    casio:{aes:{y2k:3,sharp:1},use:{daily:3,night:1}},
    sanyo:{aes:{y2k:1,sharp:1},use:{content:3,night:1,travel:1}},
    konica:{aes:{warm:2,y2k:1},use:{daily:1,portrait:1}},
    jvc:{aes:{y2k:1},use:{content:2}},
    hp:{aes:{y2k:1},use:{daily:1}},
    traveler:{aes:{y2k:2,warm:1},use:{daily:1,travel:1}},
    minton:{aes:{y2k:1},use:{daily:1}},
    rollei:{aes:{cine:1,warm:1},use:{daily:1}},
    pentax:{aes:{sharp:1},use:{travel:1,daily:1}},
    samsung:{aes:{sharp:1,y2k:1},use:{daily:1,content:1}},
    agfa:{aes:{warm:2,dreamy:1},use:{daily:1}}
  };
  function brandKey(b){b=String(b||"").toLowerCase();for(var k in BRAND){if(b.indexOf(k)>=0)return k;}return "";}
  function budgetRange(){
    if(has(1,"b1"))return [0,8000];
    if(has(1,"b2"))return [8000,13000];
    if(has(1,"b3"))return [13000,20000];
    if(has(1,"b4"))return [20000,1e9];
    return null; // b5 / bos -> sinir yok
  }
  function priceOf(c){if(c.priceN)return c.priceN;var m=String(c.price||"").replace(/[^\d]/g,"");return m?+m:0;}

  function scoreCam(c){
    var s=0, bk=brandKey(c.brand), bp=BRAND[bk]||{aes:{},use:{}};
    var uses=vals(0), aes=vals(2), envs=vals(3);
    aes.forEach(function(a){ s+=(bp.aes[a]||0)*2.2; });          // marka x estetik
    uses.forEach(function(u){ s+=(bp.use[u]||0)*1.6; });          // marka x kullanim
    uses.forEach(function(u){                                     // kullanim x ozellik
      if(u==="travel"){ if(c.zoom>=10)s+=4; else if(c.zoom>=5)s+=2.5; if(c.water)s+=3; if(c.slim)s+=1; }
      else if(u==="daily"){ if(c.slim)s+=3; if(c.zoom&&c.zoom<=5)s+=1.5; if(c.flash)s+=1; }
      else if(u==="night"){ if(c.flash)s+=4; if(c.year&&c.year<=2009)s+=1.5; }
      else if(u==="portrait"){ if(c.macro)s+=2; if(bk==="canon"||bk==="fujifilm"||bk==="fuji"||bk==="kodak")s+=2.5; if(c.mp>=10)s+=1; }
      else if(u==="content"){ if(c.video)s+=3; if(c.touch)s+=2; if(c.wide)s+=2; if(c.zoom>=10)s+=1.5; }
    });
    aes.forEach(function(a){                                      // estetik x ozellik
      if(a==="y2k"){ if(c.year&&c.year<=2008)s+=3; if(c.flash)s+=1.5; if(c.mp&&c.mp<=8)s+=1; }
      else if(a==="sharp"){ if(c.mp>=12)s+=3; else if(c.mp>=8)s+=1.5; }
      else if(a==="dreamy"){ if(c.mp&&c.mp<=8)s+=2; if(c.year&&c.year<=2007)s+=1.5; }
      else if(a==="cine"){ if(bk==="fujifilm"||bk==="fuji"||bk==="olympus"||bk==="kodak")s+=2.5; }
      else if(a==="warm"){ if(bk==="kodak"||bk==="canon"||bk==="fujifilm"||bk==="fuji")s+=2.5; }
    });
    envs.forEach(function(e){                                     // ortam x ozellik
      if(e==="citynight"||e==="indoor"){ if(c.flash)s+=3; }
      else if(e==="day"){ if(c.mp>=10)s+=1.5; }
      else if(e==="mixed"){ if(c.zoom>=5)s+=1.5; if(c.water)s+=1; }
    });
    if(has(4,"first")){ if(c.touch)s+=2; if(c.zoom>=20)s-=2.5; if(c.mp&&c.mp<=12)s+=1; }  // deneyim
    else if(has(4,"pro")){ if(c.zoom>=10)s+=2; if(c.mp>=14)s+=1.5; }
    else if(has(4,"casual")){ s+=0.5; }
    if(has(5,"work")){ if(c.video)s+=2; if(c.wide)s+=1; }         // vesile (hafif)
    if(has(5,"collection")){ if(c.year&&c.year<=2008)s+=1.5; }
    if(has(5,"gift")||has(5,"couple")){ if(c.slim)s+=1; }
    var br=budgetRange(), pr=priceOf(c);                          // butce
    if(br&&pr){
      if(pr>=br[0]&&pr<=br[1]) s+=6;
      else if(pr<br[0]) s+=2;
      else { var over=(pr-br[1])/Math.max(1,br[1]); s-=Math.min(8,over*14); }
    }
    return s;
  }
  function pickCameras(){
    // SADECE canli stoktaki kameralar; fallback yalniz canli cekim tamamen basarisiz olursa.
    var pool=(stock&&stock.length)?stock.slice():D.fallback.slice();
    if(pool.length<=3){var pk=pool.slice(0,3);pk.forEach(function(c,i){c.r=i;c.pct=[96,90,85][i]||82;});return pk;}
    // skor + kucuk jitter (ayni profil her seferinde birebir ayni dizilmesin)
    var scored=pool.map(function(c){return {c:c,s:scoreCam(c)+Math.random()*1.2};});
    scored.sort(function(a,b){return b.s-a.s;});
    var top=scoreCam(scored[0].c)||1;
    // #1 en iyi; #2/#3 farkli marka ama yine yuksek skor (uyumlu fakat farkli)
    var picks=[scored[0].c], used={}; used[brandKey(scored[0].c.brand)||scored[0].c.title]=1;
    for(var i=1;i<scored.length&&picks.length<3;i++){var bk=brandKey(scored[i].c.brand)||scored[i].c.title;if(used[bk])continue;used[bk]=1;picks.push(scored[i].c);}
    for(var j=1;j<scored.length&&picks.length<3;j++){if(picks.indexOf(scored[j].c)<0)picks.push(scored[j].c);}
    picks.forEach(function(c,i){
      var f=Math.max(0,Math.min(1,scoreCam(c)/(top||1)));
      var base=[[93,99],[86,93],[80,89]][i]||[78,86];
      c.r=i; c.pct=Math.round(base[0]+(base[1]-base[0])*f);
    });
    if(picks[1]&&picks[1].pct>=picks[0].pct)picks[1].pct=picks[0].pct-2;
    if(picks[2]&&picks[2].pct>=picks[1].pct)picks[2].pct=picks[1].pct-2;
    picks.forEach(function(c){if(c.pct<70)c.pct=70;});
    return picks;
  }
  function brandTrait(brand){
    var b=String(brand||"").toLowerCase(),tr=D.results.traits;
    for(var k in tr){ if(k!=="_default"&&b.indexOf(k)>=0) return tr[k]; }
    return tr._default;
  }
  // kameranin somut eslesen ozelligini, kullanim/estetik baglamina gore sec (metinler DATA'dan)
  function featOf(c){
    var FD=D.results.feats_dyn,uses=vals(0),aes=vals(2),envs=vals(3),F=[];
    var travel=uses.indexOf("travel")>=0,daily=uses.indexOf("daily")>=0,night=uses.indexOf("night")>=0,
        content=uses.indexOf("content")>=0,portrait=uses.indexOf("portrait")>=0;
    if((travel||envs.indexOf("mixed")>=0)&&c.zoom>=5)F.push(FD.zoom.replace("{z}",c.zoom));
    if(travel&&c.water)F.push(FD.water);
    if((night||envs.indexOf("citynight")>=0||envs.indexOf("indoor")>=0)&&c.flash)F.push(FD.flash);
    if(content&&c.video)F.push(FD.video);
    if(content&&c.touch)F.push(FD.touch);
    if(daily&&c.slim)F.push(FD.slim);
    if(aes.indexOf("sharp")>=0&&c.mp>=12)F.push(FD.mp.replace("{mp}",c.mp));
    if(aes.indexOf("y2k")>=0&&c.year&&c.year<=2008)F.push(FD.ccd.replace("{y}",c.year));
    if(portrait&&c.macro)F.push(FD.macro);
    if(!F.length)F.push(c.mp?FD.mp_default.replace("{mp}",c.mp):FD["default"]);
    return F[c.r%F.length]||F[0];
  }
  function reasonFor(c){
    var name=state.name||D.results.friend;
    var u=firstOf(0),a=firstOf(2);
    var t=D.results.reasons[c.r%D.results.reasons.length];
    return t.replace(/\{name\}/g,name).replace(/\{use\}/g,u.why||"tarzin").replace(/\{aes\}/g,a.why||"estetik tercihin").replace(/\{feat\}/g,featOf(c)).replace(/\{trait\}/g,brandTrait(c.brand)).replace(/\{cam\}/g,c.title||"bu model").replace(/\{brand\}/g,c.brand||"bu model");
  }
  function showAnalyze(){
    setProg(.97);
    var uh=firstOf(0).hue; if(uh)setAccent(uh);
    var A=D.analyze;
    var el=document.createElement("div");
    el.innerHTML=''
      +'<div class="anz">'
      +'<div class="ringwrap"><div class="orbit"><i></i></div><div class="orbit"><i></i></div><div class="orbit"><i></i></div>'
      +'<div class="ring"><div class="ascan"></div><div><div class="pv">0<small>%</small></div><div class="pl">'+esc(A.label)+'</div></div></div></div>'
      +'<div class="astep"><span class="sp"></span><span class="atxt">'+esc(A.steps[0])+'</span></div>'
      +'<div class="athumbs"></div></div>';
    swap(el);
    var ring=el.querySelector(".ring"),pv=el.querySelector(".pv"),atxt=el.querySelector(".atxt"),thumbs=el.querySelector(".athumbs");
    var pool=(stock&&stock.length)?stock:D.fallback;
    var tj=pool.slice();for(var i=tj.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=tj[i];tj[i]=tj[j];tj[j]=t;}
    thumbs.innerHTML=tj.slice(0,5).map(function(c,i){return '<img alt="" loading="lazy" style="animation-delay:'+(i*220)+'ms" src="'+esc(img(c.image,130))+'">';}).join("");
    var n=(stock&&stock.length)||"40+";
    var useShort=(A.use_short&&firstOf(0).v&&A.use_short[firstOf(0).v])||"";
    var steps=A.steps.map(function(s){return s.replace("{n}",n).replace("{name}",state.name||D.results.friend).replace("{use}",useShort);});
    var dur=rm?600:6500,t0=null,si=-1;
    var animDone=new Promise(function(res){
      function frame(ts){
        if(!t0)t0=ts;var p=Math.min((ts-t0)/dur,1),e=1-Math.pow(1-p,2.2),pct=Math.round(e*100);
        ring.style.setProperty("--p",pct);pv.innerHTML=pct+'<small>%</small>';
        var idx=Math.min(steps.length-1,Math.floor(p*steps.length));
        if(idx!==si){si=idx;atxt.style.opacity="0";setTimeout(function(){atxt.textContent=steps[idx];atxt.style.opacity="1";},180);}
        if(p<1)requestAnimationFrame(frame);else res();
      }
      requestAnimationFrame(frame);
    });
    // wait for BOTH the animation and the live stock before showing results
    Promise.all([animDone,stockReady]).then(function(){setTimeout(showResults,300);});
  }

  function showResults(){
    setProg(1);
    var R=D.results;
    var picks=pickCameras();
    logSubmission(picks);
    var name=state.name||R.friend;
    var el=document.createElement("div");
    var cards=picks.map(function(c,i){
      var best=i===0,url=c.handle?(D.products_base+c.handle):D.shop_url;
      return '<article class="rc'+(best?' best':'')+'" style="animation-delay:'+(i*200)+'ms">'
        +'<div class="rank">'+(best?esc(R.best_badge):("#"+(i+1)))+'</div>'
        +'<div class="rimg"><img alt="'+esc(c.title)+'" loading="lazy" src="'+esc(img(c.image,640))+'">'
        +'<div class="mbadge"><b data-pct="'+c.pct+'">%0</b><span>'+esc(R.match)+'</span></div></div>'
        +'<div class="rbody"><div class="rbrand">'+esc(c.brand)+'</div>'
        +'<div class="rname">'+esc(c.title)+'</div>'
        +'<div class="rbar"><i data-w="'+c.pct+'"></i></div>'
        +'<p class="rwhy">'+esc(reasonFor(c))+'</p>'
        +(c.price?('<div class="rprice">'+esc(c.price)+'</div>'):'')
        +'<a class="vbtn" href="'+esc(url)+'">'+esc(R.view)+svg("arrow")+'</a></div></article>';
    }).join("");
    el.innerHTML=''
      +'<div class="rhead"><span class="qcount">'+esc(R.eyebrow)+'</span>'
      +'<h2 class="rttl">'+esc(R.title.replace("{name}",name))+'</h2>'
      +'<p class="rsub">'+esc(R.sub)+'</p></div>'
      +'<div class="cards">'+cards+'</div>'
      +'<div class="ract"><a class="pbtn" href="'+esc(D.shop_url)+'">'+esc(R.all_cta)+svg("arrow")+'</a>'
      +'<button type="button" class="sbtn shareb" data-share>'+svg("sharei")+esc(D.share.btn)+'</button>'
      +'<button type="button" class="sbtn" data-redo>'+svg("redo")+esc(R.redo)+'</button></div>';
    swap(el);
    var shareBtn=el.querySelector("[data-share]");
    if(shareBtn)shareBtn.addEventListener("click",function(){openShare(picks);});
    setTimeout(function(){
      el.querySelectorAll(".rbar i").forEach(function(b){b.style.width=b.getAttribute("data-w")+"%";});
      el.querySelectorAll(".mbadge b").forEach(function(bd){
        var t=+bd.getAttribute("data-pct"),s=null,du=1500;
        function st(ts){if(!s)s=ts;var p=Math.min((ts-s)/du,1),e=1-Math.pow(1-p,3);bd.textContent="%"+Math.round(t*e);if(p<1)requestAnimationFrame(st);}
        requestAnimationFrame(st);
      });
    },560);
    el.querySelector("[data-redo]").addEventListener("click",function(){state.ans=[];root.style.removeProperty("--ac");showProfile();});
  }

  // ---------- PAYLASIM: 3 kameranin sosyal medya gorseli + paylas butonlari ----------
  var SICN={
    share:'<path d="M18 8a3 3 0 10-2.83-4H15a3 3 0 00.18 1.06L8.7 8.8a3 3 0 100 6.4l6.48 3.74A3 3 0 1018 17a2.96 2.96 0 00-1.78.6l-6.48-3.74a3 3 0 000-1.72l6.48-3.74A2.99 2.99 0 0018 8z"/>',
    wa:'<path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 018.413 3.488 11.82 11.82 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26l-.999 3.648 3.978-1.715zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.148-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>',
    x:'<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>',
    fb:'<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>',
    th:'<path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.36-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285 1.33-3.082.88-.76 2.119-1.207 3.583-1.291a13.85 13.85 0 013.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844 0-1.992.232-2.721 1.32l-1.696-1.164c.98-1.454 2.568-2.256 4.478-2.256h.044c3.194.02 5.097 1.975 5.287 5.388.108.046.216.094.323.146 1.51.71 2.616 1.793 3.199 3.13.81 1.868.886 4.943-1.622 7.485-1.918 1.94-4.252 2.95-7.247 2.97z"/>',
    ig:'<path d="M12 2.163c3.204 0 3.584.012 4.85.07 1.366.062 2.633.334 3.608 1.31.975.975 1.247 2.242 1.31 3.608.058 1.266.069 1.646.069 4.85s-.012 3.584-.07 4.85c-.062 1.366-.334 2.633-1.31 3.608-.975.975-2.242 1.247-3.608 1.31-1.266.058-1.646.069-4.85.069s-3.584-.012-4.85-.07c-1.366-.062-2.633-.334-3.608-1.31-.975-.975-1.247-2.242-1.31-3.608C2.175 15.647 2.163 15.267 2.163 12s.012-3.584.07-4.85c.062-1.366.334-2.633 1.31-3.608.975-.975 2.242-1.247 3.608-1.31C8.416 2.175 8.796 2.163 12 2.163zm0 1.802c-3.146 0-3.519.012-4.76.069-1.024.047-1.58.218-1.95.362-.49.19-.84.418-1.207.785-.367.367-.595.717-.785 1.207-.144.37-.315.926-.362 1.95-.057 1.241-.069 1.614-.069 4.76s.012 3.519.069 4.76c.047 1.024.218 1.58.362 1.95.19.49.418.84.785 1.207.367.367.717.595 1.207.785.37.144.926.315 1.95.362 1.241.057 1.614.069 4.76.069s3.519-.012 4.76-.069c1.024-.047 1.58-.218 1.95-.362.49-.19.84-.418 1.207-.785.367-.367.595-.717.785-1.207.144-.37.315-.926.362-1.95.057-1.241.069-1.614.069-4.76s-.012-3.519-.069-4.76c-.047-1.024-.218-1.58-.362-1.95-.19-.49-.418-.84-.785-1.207-.367-.367-.717-.595-1.207-.785-.37-.144-.926-.315-1.95-.362-1.241-.057-1.614-.069-4.76-.069zm0 3.063A4.972 4.972 0 1012 16.97a4.972 4.972 0 000-9.943zm0 8.2A3.23 3.23 0 1112 8.77a3.23 3.23 0 010 6.458zm6.323-8.392a1.162 1.162 0 11-2.324 0 1.162 1.162 0 012.324 0z"/>',
    dl:'<path d="M12 3a1 1 0 011 1v9.585l3.293-3.292a1 1 0 111.414 1.414l-5 5a1 1 0 01-1.414 0l-5-5a1 1 0 111.414-1.414L11 13.585V4a1 1 0 011-1zM5 19a1 1 0 100 2h14a1 1 0 100-2H5z"/>'
  };
  function shareFeat(brand){var b=String(brand||"").toLowerCase(),f=D.share.feats;for(var k in f){if(k!=="_default"&&b.indexOf(k)>=0)return f[k];}return f._default;}
  function loadImg(src){return new Promise(function(res){var im=new Image();im.crossOrigin="anonymous";im.onload=function(){res(im);};im.onerror=function(){res(null);};im.src=src;});}
  function rr(c,x,y,w,h,r){c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath();}
  function cover(c,im,x,y,w,h,r){if(!im){c.save();rr(c,x,y,w,h,r);c.clip();c.fillStyle="#eceae4";c.fillRect(x,y,w,h);c.restore();return;}var ir=im.width/im.height,tr=w/h,sw,sh,sx,sy;if(ir>tr){sh=im.height;sw=sh*tr;sx=(im.width-sw)/2;sy=0;}else{sw=im.width;sh=sw/tr;sx=0;sy=(im.height-sh)/2;}c.save();rr(c,x,y,w,h,r);c.clip();c.drawImage(im,sx,sy,sw,sh,x,y,w,h);c.restore();}
  var FONT="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
  // 9:16 (1080x1920) minimalist, ortalanmis hikaye gorseli: RCL logo + en uyumlu kamera + teste tesvik.
  function buildShareImage(picks){
    var hero=picks[0]||{};
    return loadImg(img(hero.image,720)).then(function(im){
      var W=1080,H=1920,cv=document.createElement("canvas");cv.width=W;cv.height=H;var x=cv.getContext("2d");
      var S=D.share,CX=W/2;
      var AC=(getComputedStyle(root).getPropertyValue("--ac")||"").trim()||"#d8472f",INK="#15110d",MUT="#8c857b";
      function hex2rgb(h){h=h.replace("#","");if(h.length===3)h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2];return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}
      var ar=hex2rgb(AC),rgba=function(a){return "rgba("+ar[0]+","+ar[1]+","+ar[2]+","+a+")";};
      // arka plan + yumusak vurgu isiklari
      x.fillStyle="#f7f4ef";x.fillRect(0,0,W,H);
      var g1=x.createRadialGradient(CX,-60,40,CX,-60,920);g1.addColorStop(0,rgba(.16));g1.addColorStop(1,rgba(0));x.fillStyle=g1;x.fillRect(0,0,W,760);
      var g2=x.createRadialGradient(CX,H+80,40,CX,H+80,820);g2.addColorStop(0,rgba(.12));g2.addColorStop(1,rgba(0));x.fillStyle=g2;x.fillRect(0,H-620,W,620);
      x.textBaseline="alphabetic";
      function cen(t,y,font,col,track){x.font=font;x.fillStyle=col;
        if(track){var ws=0,i;for(i=0;i<t.length;i++)ws+=x.measureText(t[i]).width+track;ws-=track;var sx=CX-ws/2;x.textAlign="left";
          for(i=0;i<t.length;i++){x.fillText(t[i],sx,y);sx+=x.measureText(t[i]).width+track;}x.textAlign="left";}
        else{x.textAlign="center";x.fillText(t,CX,y);x.textAlign="left";}}
      function fit(t,max,start,min,weight){var fs=start;do{x.font=weight+" "+fs+"px "+FONT;}while(x.measureText(t).width>max&&(fs-=2)>min);return fs;}
      // --- LOGO: kamera lensi marki + wordmark ---
      var ly=150;
      x.lineWidth=6;x.strokeStyle=AC;x.beginPath();x.arc(CX,ly,40,0,7);x.stroke();
      x.lineWidth=5;x.strokeStyle=INK;x.beginPath();x.arc(CX,ly,22,0,7);x.stroke();
      x.fillStyle=AC;x.beginPath();x.arc(CX,ly,7,0,7);x.fill();
      x.fillStyle="rgba(255,255,255,.9)";x.beginPath();x.arc(CX-9,ly-9,4,0,7);x.fill();
      cen(S.brandmark,ly+82,"800 30px "+FONT,INK,8);
      cen(S.eyebrow,ly+120,"700 19px "+FONT,AC,5);
      // --- HERO KART: en uyumlu kamera ---
      var cardS=640,cx=CX-cardS/2,cyc=350;
      x.save();x.shadowColor="rgba(20,17,13,.20)";x.shadowBlur=80;x.shadowOffsetY=42;
      x.fillStyle="#ffffff";rr(x,cx,cyc,cardS,cardS,52);x.fill();x.restore();
      x.strokeStyle="rgba(20,17,13,.06)";x.lineWidth=1.5;rr(x,cx,cyc,cardS,cardS,52);x.stroke();
      cover(x,im,cx+44,cyc+44,cardS-88,cardS-88,32);
      // dairesel uyum rozeti (kart sag-ust)
      var bx=cx+cardS-30,by=cyc+30,br2=82;
      x.save();x.shadowColor=rgba(.45);x.shadowBlur=34;x.fillStyle=AC;x.beginPath();x.arc(bx,by,br2,0,7);x.fill();x.restore();
      x.fillStyle="#fff";x.textAlign="center";
      x.font="800 46px "+FONT;x.fillText("%"+(hero.pct||0),bx,by+6);
      x.font="700 18px "+FONT;x.fillText(S.match_word,bx,by+34);x.textAlign="left";
      // --- SONUC METNI ---
      var ty=cyc+cardS+96;
      // EN UYUMLU pill (ortali)
      x.font="800 22px "+FONT;var pbw=x.measureText(S.badge).width+44;
      x.fillStyle=AC;rr(x,CX-pbw/2,ty-34,pbw,46,23);x.fill();
      x.fillStyle="#fff";x.textAlign="center";x.textBaseline="middle";x.fillText(S.badge,CX,ty-10);x.textBaseline="alphabetic";x.textAlign="left";
      // kamera adi (gerekirse 2 satir)
      var name=hero.title||"",fs=fit(name,W-150,60,30,"800");x.font="800 "+fs+"px "+FONT;
      var words=name.split(" "),line="",lines=[];
      words.forEach(function(w){var t=line?line+" "+w:w;if(x.measureText(t).width>W-150&&line){lines.push(line);line=w;}else line=t;});
      if(line)lines.push(line);lines=lines.slice(0,2);
      var ny=ty+70;lines.forEach(function(l,i){cen(l,ny+i*(fs+10),"800 "+fs+"px "+FONT,INK);});
      var afterName=ny+(lines.length-1)*(fs+10)+50;
      cen(String(hero.brand||"").toUpperCase(),afterName,"700 26px "+FONT,AC,3);
      cen(S.more,afterName+46,"500 27px "+FONT,MUT);
      // --- ALT CTA: denemeye tesvik ---
      x.strokeStyle="rgba(20,17,13,.10)";x.lineWidth=2;x.beginPath();x.moveTo(CX-70,1610);x.lineTo(CX+70,1610);x.stroke();
      cen(S.q1,1690,"800 52px "+FONT,INK);
      cen(S.q2,1752,"800 52px "+FONT,AC);
      cen(S.try_sub,1804,"500 28px "+FONT,MUT);
      // url pill
      x.font="800 30px "+FONT;var uw=x.measureText(S.try_cta).width+72;
      x.save();x.shadowColor=rgba(.4);x.shadowBlur=30;x.shadowOffsetY=14;
      x.fillStyle=INK;rr(x,CX-uw/2,1840,uw,66,33);x.fill();x.restore();
      x.fillStyle="#fff";x.textAlign="center";x.textBaseline="middle";x.fillText(S.try_cta,CX,1874);x.textBaseline="alphabetic";x.textAlign="left";
      return cv;
    });
  }
  function openShare(picks){
    var S=D.share,mask=root.querySelector(".shmask");
    if(!mask){mask=document.createElement("div");mask.className="shmask";root.appendChild(mask);
      mask.addEventListener("click",function(e){if(e.target===mask)close();});}
    function close(){mask.classList.remove("on");document.body.style.overflow="";}
    mask.innerHTML='<div class="shcard"><div class="shhead"><b>'+esc(S.title)+'</b><button class="shx" type="button" aria-label="Kapat">&#215;</button></div><div class="shbody"><div class="shload"><span class="sp"></span>'+esc(S.making)+'</div></div></div>';
    mask.classList.add("on");document.body.style.overflow="hidden";
    mask.querySelector(".shx").addEventListener("click",close);
    buildShareImage(picks).then(function(cv){
      var url=cv.toDataURL("image/png");
      cv.toBlob(function(blob){
        var pageUrl=(window.location&&window.location.href)||"https://retrocameraland.com/pages/hangi-kamera-bana-uygun";
        var names=picks.map(function(c){return c.title+" %"+c.pct;}).join(", ");
        var text="RetroCameraLand AI testine gore bana en uygun retro kameralar: "+names+". Sen de ogren:";
        var body=mask.querySelector(".shbody");
        if(!body)return;
        body.innerHTML='<img class="shimg" alt="" src="'+url+'"><div class="shrow"></div>';
        var rowEl=body.querySelector(".shrow"),enc=encodeURIComponent;
        function add(label,path,fn){var b=document.createElement("button");b.type="button";b.className="shbtn";b.innerHTML='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'+path+'</svg><span>'+esc(label)+'</span>';b.addEventListener("click",fn);rowEl.appendChild(b);}
        function dl(){var a=document.createElement("a");a.href=url;a.download="retrocameraland-kamera.png";document.body.appendChild(a);a.click();a.remove();}
        var file=blob?new File([blob],"retrocameraland-kamera.png",{type:"image/png"}):null;
        var canFiles=!!(file&&navigator.canShare&&navigator.canShare({files:[file]}));
        if(canFiles)add(S.native,SICN.share,function(){navigator.share({files:[file],text:text+" "+pageUrl}).catch(function(){});});
        add("WhatsApp",SICN.wa,function(){window.open("https://wa.me/?text="+enc(text+" "+pageUrl),"_blank","noopener");});
        add("X",SICN.x,function(){window.open("https://twitter.com/intent/tweet?text="+enc(text)+"&url="+enc(pageUrl),"_blank","noopener");});
        add("Facebook",SICN.fb,function(){window.open("https://www.facebook.com/sharer/sharer.php?u="+enc(pageUrl),"_blank","noopener");});
        add("Threads",SICN.th,function(){window.open("https://www.threads.net/intent/post?text="+enc(text+" "+pageUrl),"_blank","noopener");});
        add("Instagram",SICN.ig,function(){if(canFiles){navigator.share({files:[file]}).catch(function(){});}else{dl();setTimeout(function(){alert(S.ig_note);},120);}});
        add(S.dl,SICN.dl,dl);
      },"image/png");
    }).catch(function(){var b=mask.querySelector(".shbody");if(b)b.innerHTML='<div class="shload">'+esc(S.fail)+'</div>';});
  }

  root.querySelectorAll(".seo .item").forEach(function(it){
    var b=it.querySelector(".q"),p=it.querySelector(".a");
    b.addEventListener("click",function(){var o=it.getAttribute("aria-expanded")==="true";
      it.setAttribute("aria-expanded",o?"false":"true");
      p.style.height=o?"0px":(p.firstElementChild.offsetHeight+"px");});
  });
  window.addEventListener("resize",function(){
    root.querySelectorAll('.seo .item[aria-expanded="true"] .a').forEach(function(p){p.style.height=p.firstElementChild.offsetHeight+"px";});});
})();
</script>
"""

# ============================================================ DATA object
def opt_clean(o):
    return {"v":o["v"],"label":o["label"],"sub":o["sub"],"hue":o["hue"],"icon":o["icon"],"why":o["why"]}

DATA = {
 "t":{"step":"ADIM","friend":RESULTS["friend"],"next":"Devam et","see_results":"Sonuçları gör",
      "multi":"Sana en çok uyan 1-2 tanesini seç","pers_fb":"kendine has tarzın"},
 "share":SHARE,
 "profile":PROFILE,
 "questions":[{"k":q["k"],"q":q["q"],"sub":q["sub"],"opts":[opt_clean(o) for o in q["opts"]]} for q in QUESTIONS],
 "analyze":{"label":ANALYZE["label"],"steps":ANALYZE["steps"],"use_short":ANALYZE["use_short"]},
 "results":{"eyebrow":RESULTS["eyebrow"],"title":RESULTS["title"],"sub":RESULTS["sub"],
            "best_badge":RESULTS["best_badge"],"match":RESULTS["match"],"view":RESULTS["view"],
            "all_cta":RESULTS["all_cta"],"redo":RESULTS["redo"],"reasons":RESULTS["reasons"],
            "feats_dyn":RESULTS["feats_dyn"],"traits":RESULTS["traits"],"friend":RESULTS["friend"]},
 "svg":IC,
 "fallback":FALLBACK,
 "shop_url":"__SHOP_URL__",
 "products_base":"__PROD_BASE__",
 "log_url":"__LOG_URL__",
}

# ============================================================ HTML BUILD
def build_html():
    H=[]
    H.append(CSS)
    H.append('<section id="rcl-fnd-__SID__">')
    H.append('<div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>')
    H.append('<div class="grain" aria-hidden="true"></div>')
    H.append('<div class="pad"><div class="wrap">')

    H.append('<div class="app">')
    H.append('<div class="prog"><i></i></div>')
    H.append('<div class="stage">')
    H.append('<div class="scr intro">')
    H.append('<div class="sparks" aria-hidden="true"><i></i><i></i><i></i><i></i></div>')
    H.append('<span class="pill glass"><span class="dot"></span>%s</span>' % E(HERO["pill"]))
    H.append('<h1 class="htl">%s</h1>' % "".join('<span class="w">%s</span> ' % E(w) for w in HERO["words"]))
    H.append('<p class="hl">%s</p>' % E(HERO["lead"]))
    H.append('<div class="hmeta">%s</div>' % "".join('<span>%s</span>' % E(m) for m in HERO["meta"]))
    H.append('<div class="cta-wrap"><button type="button" class="pbtn startbtn">%s'
             '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg></button></div>' % (E(HERO["cta"]), IC["spark"]))
    strip = "".join('<img loading="lazy" width="74" height="74" alt="" src="%s">'
                    % (c["image"] + "?width=160") for c in FALLBACK)
    H.append('<div class="strip" aria-hidden="true"><div class="tr">%s%s</div></div>' % (strip, strip))
    H.append('</div>')  # intro
    H.append('</div>')  # stage
    H.append('</div>')  # app

    H.append('<div class="seo">')
    H.append('<span class="sm">%s</span>' % E("KAMERA REHBERİ"))
    H.append('<h2>%s</h2>' % E(SEO["h2"]))
    H.append('<p class="lede">%s</p>' % E(SEO["p"]))
    H.append('<div style="margin-top:30px"><span class="sm">%s</span>' % E(SEO["cats_head"]))
    H.append('<div class="cats">')
    for t,d,u in SEO["cats"]:
        H.append('<a class="cat glass" href="%s"><h3>%s</h3><p>%s</p><span class="go">%s'
                 '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg></span></a>'
                 % (u, E(t), E(d), E("Keşfet"), IC["arrow"]))
    H.append('</div></div>')
    PLUS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>'
    H.append('<div style="margin-top:34px"><h2 style="font-size:clamp(22px,5vw,30px)">%s</h2>' % E(SEO["faq_head"]))
    H.append('<div class="faq">')
    for q,a in SEO["faq"]:
        H.append('<div class="item glass" aria-expanded="false"><button type="button" class="q">'
                 '<span>%s</span><span class="pm">%s</span></button>'
                 '<div class="a"><div class="a-in">%s</div></div></div>' % (E(q), PLUS, E(a)))
    H.append('</div></div>')
    H.append('</div>')  # seo

    H.append('</div></div>')  # wrap pad

    H.append('<script type="application/ld+json">%s</script>' % ld(ORG))
    H.append('<script type="application/ld+json">%s</script>' % ld(WEBAPP))
    H.append('<script type="application/ld+json">%s</script>' % ld(HOWTO))
    H.append('<script type="application/ld+json">%s</script>' % ld(faq_ld()))
    H.append('__BREADCRUMB__')
    H.append('</section>')

    js = JS.replace("__DATA__", json.dumps(DATA, ensure_ascii=True, separators=(",", ":")))
    H.append(js)
    return "".join(H)

CORE = build_html()

# ============================================================ LIQUID OUTPUT
SCHEMA = {"name":"RCL Kamera Bulucu","tag":"section","class":"rcl-finder-section","settings":[
 {"type":"header","content":"Renkler"},
 {"type":"color","id":"accent","label":"Vurgu (baslangic)","default":"#d8472f"},
 {"type":"color","id":"bg","label":"Arka plan","default":"#faf8f4"},
 {"type":"color","id":"card","label":"Kart","default":"#ffffff"},
 {"type":"color","id":"ink","label":"Metin","default":"#15110d"},
 {"type":"header","content":"Cam efekti"},
 {"type":"range","id":"glass_blur","min":0,"max":40,"step":2,"unit":"px","label":"Cam bulanikligi","default":18},
 {"type":"header","content":"Baglantilar"},
 {"type":"url","id":"shop_url","label":"Tum kameralar (koleksiyon)"},
 {"type":"text","id":"products_base","label":"Urun yolu","default":"/products/"},
 {"type":"header","content":"Veri toplama (HQ dashboard)"},
 {"type":"text","id":"log_endpoint","label":"Kayit API adresi","default":"https://rclhq.vercel.app/api/finder-log",
  "info":"Bos birakirsan test sonuclari kaydedilmez."},
 {"type":"header","content":"SEO"},
 {"type":"checkbox","id":"show_breadcrumb","label":"Breadcrumb schema ciktisi","default":True},
],"presets":[{"name":"RCL Kamera Bulucu"}]}

def to_liquid(core):
    s = core.replace("__SID__", "{{ section.id }}")
    s = s.replace("__SHOP_URL__", "{{ section.settings.shop_url | default: '/collections/all' }}")
    s = s.replace("__PROD_BASE__", "{{ section.settings.products_base | default: '/products/' }}")
    s = s.replace("__LOG_URL__", "{{ section.settings.log_endpoint | default: 'https://rclhq.vercel.app/api/finder-log' }}")
    bc = ("{%- if section.settings.show_breadcrumb -%}<script type=\"application/ld+json\">"
          + ld(BREAD) + "</script>{%- endif -%}")
    s = s.replace("__BREADCRUMB__", bc)
    return s + "\n{% schema %}\n" + json.dumps(SCHEMA, ensure_ascii=True, indent=2) + "\n{% endschema %}\n"

liquid = to_liquid(CORE)
bad = [c for c in liquid if ord(c) > 127]
assert not bad, "non-ascii in liquid: %r" % bad[:8]
open(os.path.join(HERE, "rcl-camera-finder.liquid"), "w").write(liquid)
print("liquid bytes=", len(liquid))

# ============================================================ PREVIEW OUTPUT
stock_path = "/private/tmp/claude-501/-Users-onnoshot-Downloads-Agentlar/54157e29-604c-473a-b6ab-fe1e9917f94d/scratchpad/rcl_stock_live.json"
try:
    real_stock = json.load(open(stock_path))
except Exception:
    real_stock = []

def to_preview(core):
    s = core.replace("__SID__", "prev")
    s = s.replace("__SHOP_URL__", SITE + "/collections/all")
    s = s.replace("__PROD_BASE__", SITE + "/products/")
    s = s.replace("__LOG_URL__", "")  # onizlemede kayit gonderme
    prev_vals = {"accent":"#d8472f","bg":"#faf8f4","card":"#ffffff","ink":"#15110d","glass_blur":"18"}
    for sid, val in prev_vals.items():
        s = re.sub(r"\{\{\s*section\.settings\." + sid + r"\b[^}]*\}\}", val, s)
    s = s.replace("__BREADCRUMB__", '<script type="application/ld+json">' + ld(BREAD) + "</script>")
    s = s.replace("{%- style -%}", "<style>").replace("{%- endstyle -%}", "</style>")
    return s

prev_core = to_preview(CORE)
stock_js = json.dumps(real_stock, ensure_ascii=True, separators=(",", ":"))
doc = (
 "<!doctype html><html lang=\"tr\"><head><meta charset=\"utf-8\">"
 "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
 "<title>RetroCameraLand - AI Kamera Eslestirici (Onizleme)</title>"
 "<style>html,body{margin:0;background:#faf8f4;}</style>"
 "<script>window.__RCL_STOCK__=" + stock_js + ";</script>"
 "</head><body>" + prev_core + "</body></html>"
)
open(os.path.join(HERE, "preview-rcl-camera-finder.html"), "w").write(doc)
print("preview bytes=", len(doc), "stock items=", len(real_stock))
print("OK")
