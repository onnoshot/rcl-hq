export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }
  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  const store  = process.env.SHOPIFY_STORE;
  const token  = process.env.SHOPIFY_ACCESS_TOKEN;
  const blogId = process.env.SHOPIFY_BLOG_ID;

  if (!store || !token) {
    return new Response(JSON.stringify({
      error: 'Shopify konfigurasyonu eksik. Vercel\'de SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN ve SHOPIFY_BLOG_ID env degiskenlerini ekleyin.'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }

  try {
    const body = await req.json();
    const { title, body_html, published = true } = body;

    if (!title || !body_html) {
      return new Response(JSON.stringify({ error: 'title ve body_html gerekli' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    const articlePayload = {
      article: {
        title,
        body_html,
        published,
        ...(blogId ? { blog_id: parseInt(blogId) } : {}),
      }
    };

    const resp = await fetch(
      `https://${store}/admin/api/2024-01/articles.json`,
      {
        method: 'POST',
        headers: {
          'X-Shopify-Access-Token': token,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(articlePayload),
      }
    );

    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      status: resp.status,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
}
