// RCL "Stoğa gelince haber ver" — e-posta yakalama endpoint'i (Vercel serverless)
// Tema formundan POST alır, Shopify'da müşteriyi `bekleme:<variant_id>` etiketiyle kaydeder.
// Ayrı veritabanı yok — bekleme listesi = Shopify müşterileri.
//
// Gerekli ortam değişkenleri (Vercel → Settings → Environment Variables):
//   SHOPIFY_STORE  = retrocameraland.myshopify.com
//   SHOPIFY_TOKEN  = shpat_...
//   ALLOW_ORIGIN   = https://retrocameraland.com

const API = "2024-01";

async function shopify(method, path, body) {
  const res = await fetch(`https://${process.env.SHOPIFY_STORE}/admin/api/${API}/${path}`, {
    method,
    headers: {
      "X-Shopify-Access-Token": process.env.SHOPIFY_TOKEN,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`Shopify ${method} ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

export default async function handler(req, res) {
  const origin = process.env.ALLOW_ORIGIN || "*";
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "method" });

  try {
    const { email, variant_id, product_title } = req.body || {};
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !variant_id)
      return res.status(400).json({ error: "geçersiz e-posta veya ürün" });

    const tag = `bekleme:${variant_id}`;
    const q = encodeURIComponent(`email:${email}`);
    const found = await shopify("GET", `customers/search.json?query=${q}&limit=1`);
    const existing = (found.customers || [])[0];

    if (existing) {
      const tags = (existing.tags || "").split(",").map((t) => t.trim()).filter(Boolean);
      if (!tags.includes(tag)) tags.push(tag);
      await shopify("PUT", `customers/${existing.id}.json`, {
        customer: { id: existing.id, tags: tags.join(", ") },
      });
    } else {
      await shopify("POST", "customers.json", {
        customer: {
          email,
          tags: tag,
          note: `Bekleme listesi: ${product_title || variant_id}`,
          email_marketing_consent: { state: "subscribed", opt_in_level: "single_opt_in" },
        },
      });
    }
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: String(e).slice(0, 200) });
  }
}
