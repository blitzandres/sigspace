# SIGSPACE Setup

## Local preview
    python3 scripts/idle-server.py
    # http://127.0.0.1:8765/
    # Shuts down after 1 hour idle

## GitHub Pages
Already enabled on main. Custom domain: vancouver.andresblitz.com

## Cloudflare Worker
    cd worker
    wrangler login
    wrangler deploy

Secrets (keys never touch files):
    wrangler secret put IPINFO_TOKEN
    wrangler secret put ABUSEIPDB_KEY

The Worker also proxies ip-api (HTTP, server-side) and Cloudflare DoH, so GitHub Pages HTTPS can load CARRIER / TOPOLOGY / STREAM without mixed-content failures.

Free APIs:
- ip-api.com: no key (45 req/min), HTTP only, used via the Worker
- ipinfo.io: https://ipinfo.io/signup
- AbuseIPDB: https://www.abuseipdb.com/register
- Cloudflare DoH: no key
