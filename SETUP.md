# SIGSPACE Setup

## One-time steps (run once, then forget)

### 1. Enable GitHub Pages
```bash
gh api repos/blitzandres/sigspace/pages \
  --method POST \
  --field source='{"branch":"main","path":"/"}' \
  --header "Accept: application/vnd.github+json"
```

### 2. Deploy Cloudflare Worker
```bash
cd worker
npm install wrangler -g   # one-time
wrangler login            # browser auth
wrangler deploy
```

### 3. Set API secrets (keys never touch files)
```bash
wrangler secret put IPINFO_TOKEN    # paste your key from ipinfo.io
wrangler secret put ABUSEIPDB_KEY   # paste your key from abuseipdb.com
```

### Free API keys
- ipinfo.io: https://ipinfo.io/signup (50k/month free)
- AbuseIPDB: https://www.abuseipdb.com/register (1k/day free)
- ip-api.com: no key needed (45 req/min free)
- Cloudflare DoH: no key needed (unlimited free)
