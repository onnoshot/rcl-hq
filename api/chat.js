export const config = { runtime: 'edge' };

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default async function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });

  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'GROQ_API_KEY not configured' }), {
      status: 500, headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  try {
    const body = await req.json();

    // Map Anthropic model names -> Groq equivalents
    const modelMap = {
      'claude-haiku-4-5-20251001': 'llama-3.1-8b-instant',
      'claude-haiku-4-5':         'llama-3.1-8b-instant',
      'claude-sonnet-4-6':        'llama-3.3-70b-versatile',
      'claude-opus-4-7':          'llama-3.3-70b-versatile',
    };
    const model = modelMap[body.model] || body.model || 'llama-3.1-8b-instant';

    // Build OpenAI-compatible messages (Groq uses OpenAI format)
    const messages = [];
    if (body.system) messages.push({ role: 'system', content: body.system });
    (body.messages || []).forEach(function(m) { messages.push(m); });

    const groqBody = {
      model,
      max_tokens: body.max_tokens || 1024,
      messages,
      stream: !!body.stream,
    };

    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
      body: JSON.stringify(groqBody),
    });

    // ── Streaming: convert OpenAI SSE -> Anthropic SSE (frontend expects Anthropic format) ──
    if (body.stream) {
      const reader = resp.body.getReader();
      const enc = new TextEncoder();

      const stream = new ReadableStream({
        async start(ctrl) {
          const dec = new TextDecoder();
          let buf = '';
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              buf += dec.decode(value, { stream: true });
              const lines = buf.split('\n');
              buf = lines.pop();
              for (const line of lines) {
                if (!line.startsWith('data:')) continue;
                const raw = line.slice(5).trim();
                if (raw === '[DONE]') {
                  ctrl.enqueue(enc.encode('data: {"type":"message_stop"}\n\n'));
                  break;
                }
                try {
                  const evt = JSON.parse(raw);
                  const text = evt.choices?.[0]?.delta?.content;
                  if (text) {
                    const out = { type: 'content_block_delta', delta: { type: 'text_delta', text } };
                    ctrl.enqueue(enc.encode('data: ' + JSON.stringify(out) + '\n\n'));
                  }
                } catch (_) {}
              }
            }
          } finally {
            ctrl.close();
          }
        }
      });

      return new Response(stream, {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', ...CORS },
      });
    }

    // ── Non-streaming: convert Groq response -> Anthropic response shape ──
    const data = await resp.json();
    if (!resp.ok) {
      return new Response(JSON.stringify({ error: data.error?.message || JSON.stringify(data) }), {
        status: resp.status, headers: { 'Content-Type': 'application/json', ...CORS },
      });
    }
    const text = data.choices?.[0]?.message?.content || '';
    // Return Anthropic-shaped response so cgFetchJSON can parse content[0].text
    const anthropicShape = { content: [{ type: 'text', text }] };
    return new Response(JSON.stringify(anthropicShape), {
      status: 200, headers: { 'Content-Type': 'application/json', ...CORS },
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }
}
