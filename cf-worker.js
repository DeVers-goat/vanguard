/**
 * Vanguard Sync Worker
 * Deploy this on Cloudflare Workers (free tier).
 * Set GITHUB_TOKEN as a secret environment variable in the Worker settings.
 *
 * This handles habits.json, books.json, reviews.json syncing to GitHub
 * without exposing the GitHub token to the browser.
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const ALLOWED_FILES = ['habits.json', 'books.json', 'reviews.json'];
const REPO = 'DeVers-goat/morning-habits';
export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);

    // GET /read?file=habits.json — read a file (bypasses CDN cache via API)
    if (request.method === 'GET' && url.pathname === '/read') {
      const file = url.searchParams.get('file');
      if (!ALLOWED_FILES.includes(file)) {
        return new Response('Forbidden', { status: 403, headers: CORS });
      }

      const apiUrl = `https://api.github.com/repos/${REPO}/contents/${file}`;
      const resp = await fetch(apiUrl, {
        headers: {
          'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github+json',
          'User-Agent': 'Vanguard-App',
        },
        cf: { cacheTtl: 0, cacheEverything: false },
      });
      if (!resp.ok) return new Response('Not found', { status: 404, headers: CORS });
      const data = await resp.json();
      const content = JSON.parse(decodeURIComponent(escape(atob(data.content.replace(/\n/g, '')))));

      return new Response(JSON.stringify(content), {
        headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    // POST /sync — write a file to GitHub
    if (request.method === 'POST' && url.pathname === '/sync') {
      let body;
      try { body = await request.json(); } catch {
        return new Response('Bad request', { status: 400, headers: CORS });
      }
      const { file, content } = body;
      if (!ALLOWED_FILES.includes(file) || !content) {
        return new Response('Forbidden', { status: 403, headers: CORS });
      }

      const apiBase = `https://api.github.com/repos/${REPO}/contents/${file}`;
      const headers = {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Vanguard-App',
      };

      const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(content, null, 2))));

      // Retry up to 3 times on SHA conflict (409)
      let putResp;
      for (let attempt = 0; attempt < 3; attempt++) {
        const getResp = await fetch(apiBase, { headers });
        const sha = getResp.ok ? (await getResp.json()).sha : undefined;
        putResp = await fetch(apiBase, {
          method: 'PUT',
          headers,
          body: JSON.stringify({
            message: `Auto-sync ${file}`,
            content: encoded,
            ...(sha ? { sha } : {}),
          }),
        });
        if (putResp.status !== 409) break; // success or non-conflict error
      }

      return new Response(
        JSON.stringify({ ok: putResp.ok, status: putResp.status }),
        { status: putResp.ok ? 200 : 500, headers: { ...CORS, 'Content-Type': 'application/json' } }
      );
    }

    // POST /ai — proxy to Claude API (ANTHROPIC_API_KEY stored as Cloudflare secret)
    if (request.method === 'POST' && url.pathname === '/ai') {
      let body;
      try { body = await request.json(); } catch {
        return new Response('Bad request', { status: 400, headers: CORS });
      }
      const { messages, system } = body;
      if (!messages || !Array.isArray(messages)) {
        return new Response('Bad request', { status: 400, headers: CORS });
      }
      const resp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'anthropic-version': '2023-06-01',
          'x-api-key': env.ANTHROPIC_API_KEY,
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-6',
          max_tokens: 4000,
          ...(system ? { system } : {}),
          messages,
        }),
      });
      const data = await resp.json();
      return new Response(JSON.stringify(data), {
        status: resp.status,
        headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404, headers: CORS });
  }
};
