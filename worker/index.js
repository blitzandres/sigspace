const ALLOWED_ORIGIN = 'https://blitzandres.github.io';

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return corsResponse('', 204, origin);
    }

    // Route: /api/ipinfo?ip=1.2.3.4
    if (url.pathname === '/api/ipinfo') {
      const ip = url.searchParams.get('ip') || '';
      if (!ip.match(/^[\d.a-f:]+$/i)) return corsResponse('bad ip', 400, origin);
      try {
        const r = await fetch(`https://ipinfo.io/${ip}?token=${env.IPINFO_TOKEN}`);
        const data = await r.text();
        return corsResponse(data, r.status, origin, 'application/json');
      } catch(e) {
        return corsResponse(JSON.stringify({error:'upstream failed'}), 502, origin);
      }
    }

    // Route: /api/abuseipdb?ip=1.2.3.4
    if (url.pathname === '/api/abuseipdb') {
      const ip = url.searchParams.get('ip') || '';
      if (!ip.match(/^[\d.a-f:]+$/i)) return corsResponse('bad ip', 400, origin);
      try {
        const r = await fetch(
          `https://api.abuseipdb.com/api/v2/check?ipAddress=${ip}&maxAgeInDays=90`,
          { headers: { 'Key': env.ABUSEIPDB_KEY, 'Accept': 'application/json' } }
        );
        const d = await r.json();
        return corsResponse(JSON.stringify(d.data || {}), r.status, origin, 'application/json');
      } catch(e) {
        return corsResponse(JSON.stringify({error:'upstream failed'}), 502, origin);
      }
    }

    // Health check
    if (url.pathname === '/') {
      return corsResponse(JSON.stringify({status:'ok',service:'sigspace-worker'}), 200, origin, 'application/json');
    }

    return corsResponse('not found', 404, origin);
  }
};

function corsResponse(body, status, origin, contentType = 'text/plain') {
  return new Response(body, {
    status,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': contentType,
      'Cache-Control': 'public, max-age=300'
    }
  });
}
