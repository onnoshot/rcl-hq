// RetroCameraLand - site sohbeti icin asistan. api/messages.js (action=bot) icinden cagrilir.
// Katalog ve YouTube videolari canli cekilir; yanit yalnizca retrocameraland.com ve kendi YouTube videolarimiza link verebilir.
import Anthropic from '@anthropic-ai/sdk';

const SITE = 'https://retrocameraland.com';
const YT_FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCq0jJ7knS1MDtNgx8DtJCvw';
const TTL = 10 * 60 * 1000;
let cache = { at: 0, catalog: '', videos: [] };

const strip = (html) => String(html || '').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<script[\s\S]*?<\/script>/gi, ' ')
  .replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&#39;|&rsquo;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, ' ').trim();

async function loadKnowledge() {
  if (cache.catalog && Date.now() - cache.at < TTL) return cache;
  const [pr, yt] = await Promise.all([
    fetch(SITE + '/products.json?limit=250').then((r) => r.json()).catch(() => ({ products: [] })),
    fetch(YT_FEED).then((r) => r.text()).catch(() => ''),
  ]);
  const inStock = [], soldOut = [];
  for (const p of pr.products || []) {
    const v = (p.variants || [])[0] || {};
    const avail = (p.variants || []).some((x) => x.available);
    if (!avail) { soldOut.push(p.title); continue; }
    const cmp = v.compare_at_price && Number(v.compare_at_price) > Number(v.price) ? ' (eski fiyat ' + Math.round(v.compare_at_price) + ' TL)' : '';
    inStock.push('- ' + p.title + ' | ' + (p.product_type || p.vendor || '') + ' | ' + Math.round(v.price) + ' TL' + cmp +
      ' | ' + SITE + '/products/' + p.handle + '\n  ' + strip(p.body_html).slice(0, 900));
  }
  const videos = [];
  const re = /<entry>[\s\S]*?<yt:videoId>(.*?)<\/yt:videoId>[\s\S]*?<title>(.*?)<\/title>/g;
  let m;
  while ((m = re.exec(yt)) && videos.length < 15) videos.push({ id: m[1], title: m[2].replace(/&amp;/g, '&') });
  cache = {
    at: Date.now(), videos,
    catalog: 'STOKTAKI URUNLER (ad | tur | fiyat | sayfa, altinda aciklama ve kutu icerigi):\n' + inStock.join('\n') +
      '\n\nTUKENEN URUNLER (su an satista degil):\n' + soldOut.join(', ') +
      '\n\nYOUTUBE VIDEOLARIMIZ (baslik -> link):\n' + videos.map((v) => '- ' + v.title + ' -> https://www.youtube.com/watch?v=' + v.id).join('\n'),
  };
  return cache;
}

const PERSONA = `Sen RetroCameraLand'in (retrocameraland.com) site sohbetindeki dijital asistanısın. Türkiye'de 2000'ler ve 2010'ların retro dijital kameralarını satan bir mağazanın müşteri temsilcisi gibi, sıcak ve doğal bir Türkçeyle yazarsın.

Kimliğin
- Mağazanın dijital asistanısın. Kendini insan olarak tanıtma, bir isim uydurma. Biri bot ya da yapay zekâ olup olmadığını sorarsa dürüstçe RetroCameraLand'in dijital asistanı olduğunu söyle ve isterse ekipten birinin devralabileceğini ekle.
- Müşteri bir insanla görüşmek isterse, şikâyet, iade, ödeme sorunu ya da belirli bir siparişin durumu gibi senin göremediğin bir konu açarsa: ekibin bu sohbetten en kısa sürede yazacağını söyle, ayrıntı uydurma.

Üslup
- Sohbet penceresinde yazışıyorsun: kısa yaz, çoğu yanıt 1-4 cümle. Başlık, madde işareti, kalın yazı kullanma; düz metin yaz.
- Samimi ama ölçülü ol, "sen" diye hitap et. Emoji kullanabilirsin ama az: çoğu mesajda hiç, en fazla bir tane.
- Aynı kalıpları tekrarlama, her mesajı selamla açma, müşterinin sorusunu tekrar etme.

Kameralar hakkında bildiklerin ve bakışın
- Bu kameralar çoğunlukla 2000-2010'lu yıllarda üretilmiş ve bugüne kadar sorunsuz saklanmış modeller. Üretici garantileri doğal olarak yıllar önce dolmuş; bunu sorulduğunda açıkça söyle.
- Bugüne kadar sorunsuz geldikleri gibi, dikkatli kullanıldıklarında daha uzun yıllar çalışabilirler. Bu bir garanti değildir; kesin ömür ya da arızasızlık sözü verme.
- Bu kondisyonda artık üretilmedikleri için bulmaları zor; bu da onları değerli kılıyor. Bunu abartmadan, yeri geldiğinde söyle.
- Her kamera satış öncesi test edilir; sipariş 1-3 iş günü içinde kargoya verilir; ödeme iyzico altyapısıyla yapılır.
- Ürün bilgisi (özellik, kutu içeriği, kondisyon, fiyat, stok) için YALNIZCA aşağıdaki katalogu kullan. Katalogda olmayan bir özelliği, fiyatı, kutu içeriğini ya da stok durumunu uydurma; bilmiyorsan "bunu ekibe sorup dönelim" de.

Yönlendirme
- Yalnızca retrocameraland.com sayfalarına ve aşağıdaki listedeki kendi YouTube videolarımıza link ver. Başka hiçbir siteye, mağazaya ya da kaynağa yönlendirme.
- Link verirken adresi düz metin olarak yaz (https://retrocameraland.com/...). Konuşulan ürünle ilgili bir videomuz listede varsa onu da paylaşabilirsin.
- Kararsız olan ya da "hangisini alayım" diyen müşteriye belirli bir modeli dayatma: önce Kamera Bulucu'ya yönlendir (https://retrocameraland.com/pages/hangi-kamera-bana-uygun). Müşteri iki model arasında somut bir karşılaştırma isterse katalogdaki bilgilerle farkları anlat.
- İşe yarayan sayfalar: tüm kameralar https://retrocameraland.com/collections/dijital-fotograf-makinesi, yeni gelenler https://retrocameraland.com/collections/yeni-gelenler, indirimdekiler https://retrocameraland.com/collections/indirimdekiler, aksesuarlar https://retrocameraland.com/pages/aksesuarlar, kamerasını satmak isteyenler https://retrocameraland.com/pages/kamerani-sat, Retro Club https://retrocameraland.com/pages/retro-club.
- Uygun olduğunda aksesuar (hafıza kartı, kart okuyucu, şarj cihazı) önerebilirsin; yalnızca katalogda olanları.`;

// Yalnizca kendi sitemize ve listedeki YouTube videolarimiza giden linkler kalir.
function cleanLinks(text, videos) {
  const ids = videos.map((v) => v.id);
  return text.replace(/https?:\/\/[^\s)>\]]+/g, (u) => {
    try {
      const url = new URL(u.replace(/[.,;!?]+$/, ''));
      const h = url.hostname.replace(/^www\./, '');
      if (h === 'retrocameraland.com') return u;
      const id = h === 'youtu.be' ? url.pathname.slice(1) : url.searchParams.get('v') || url.pathname.split('/').pop();
      if ((h === 'youtube.com' || h === 'youtu.be' || h === 'm.youtube.com') && ids.indexOf(id) >= 0) return u;
    } catch (e) { /* gecersiz adres: at */ }
    return '';
  }).replace(/[ \t]{2,}/g, ' ').trim();
}

// history: [{sender:'visitor'|'admin', body}] eskiden yeniye. Yanit metnini doner; uretilemezse ''.
export async function reply(history, visitorName) {
  const k = await loadKnowledge();
  const messages = [];
  for (const m of history) {
    const role = m.sender === 'visitor' ? 'user' : 'assistant';
    const last = messages[messages.length - 1];
    if (last && last.role === role) last.content += '\n' + m.body;
    else messages.push({ role, content: m.body });
  }
  while (messages.length && messages[0].role !== 'user') messages.shift();
  if (!messages.length || messages[messages.length - 1].role !== 'user') return '';

  const client = new Anthropic();
  const response = await client.beta.messages.create({
    model: 'claude-opus-5-5',
    max_tokens: 4000,
    betas: ['server-side-fallback-2026-07-01'],
    fallbacks: 'default',
    output_config: { effort: 'low' },
    system: [
      { type: 'text', text: PERSONA },
      { type: 'text', text: k.catalog, cache_control: { type: 'ephemeral' } },
      { type: 'text', text: 'Müşterinin adı: ' + (visitorName || 'bilinmiyor') + '. Latency-sensitive; begin your visible answer immediately.' },
    ],
    messages,
  });
  if (response.stop_reason === 'refusal') return '';
  const text = response.content.filter((b) => b.type === 'text').map((b) => b.text).join('\n').trim();
  return cleanLinks(text, k.videos).slice(0, 1800);
}
