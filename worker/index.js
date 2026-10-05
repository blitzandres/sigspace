const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Cache-Control': 'public, max-age=30',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}

function visitorIp(request) {
  return (
    request.headers.get('CF-Connecting-IP') ||
    request.headers.get('True-Client-IP') ||
    ''
  );
}

const GEO_FIELDS = 'status,message,country,countryCode,regionName,city,isp,as,query,lat,lon,timezone';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') {
      return new Response('', { status: 204, headers: CORS });
    }

    if (url.pathname === '/') {
      return json({ status: 'ok', service: 'sigspace-worker', t: Date.now() });
    }

    if (url.pathname === '/api/ipinfo' || url.pathname === '/api/geo') {
      const ip = url.searchParams.get('ip') || visitorIp(request);
      try {
        const target = ip
          ? `http://ip-api.com/json/${encodeURIComponent(ip)}?fields=${GEO_FIELDS}`
          : `http://ip-api.com/json/?fields=${GEO_FIELDS}`;
        const r = await fetch(target);
        const data = await r.json();
        if (data.status === 'success') return json(data);
        if (ip && env.IPINFO_TOKEN) {
          const r2 = await fetch(`https://ipinfo.io/${ip}?token=${env.IPINFO_TOKEN}`);
          return json(await r2.json(), r2.status);
        }
        return json(data, 502);
      } catch (e) {
        return json({ error: 'upstream failed' }, 502);
      }
    }

    if (url.pathname === '/api/geo/batch' && request.method === 'POST') {
      try {
        const body = await request.json();
        const list = (Array.isArray(body) ? body : body.ips || [])
          .filter(Boolean)
          .slice(0, 10);
        const payload = list.map((q) => ({
          query: q,
          fields: 'status,country,countryCode,city,isp,query',
        }));
        const r = await fetch('http://ip-api.com/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        return json(await r.json());
      } catch (e) {
        return json({ error: 'upstream failed' }, 502);
      }
    }

    if (url.pathname === '/api/doh') {
      const name = (url.searchParams.get('name') || '').toLowerCase();
      if (!/^[a-z0-9.-]{1,253}$/.test(name)) return json({ error: 'bad name' }, 400);
      try {
        const r = await fetch(
          `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(name)}&type=A`,
          { headers: { Accept: 'application/dns-json' } }
        );
        return json(await r.json());
      } catch (e) {
        return json({ error: 'upstream failed' }, 502);
      }
    }

    if (url.pathname === '/api/abuseipdb') {
      const ip = url.searchParams.get('ip') || '';
      if (!/^[\d.a-f:]+$/i.test(ip)) return json({ error: 'bad ip' }, 400);
      try {
        const r = await fetch(
          `https://api.abuseipdb.com/api/v2/check?ipAddress=${ip}&maxAgeInDays=90`,
          { headers: { Key: env.ABUSEIPDB_KEY, Accept: 'application/json' } }
        );
        const d = await r.json();
        return json(d.data || {}, r.status);
      } catch (e) {
        return json({ error: 'upstream failed' }, 502);
      }
    }

    return json({ error: 'not found' }, 404);
  },
};
