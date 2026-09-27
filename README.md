# SIGSPACE

**Real signal data as a video game world.**

SIGSPACE puts you inside your own network as a pixel character. Real signal
data (your carrier, live connections, DNS lookups, nearby Bluetooth devices
and threat intel) floats around you as orbiting nodes in cyberspace. Turn the
frequency dial to jump between dimensions ("realms").

- **Live:** https://blitzandres.github.io/sigspace
- **Project page:** https://andresblitz.com/projects/sigspace/
- **Thesis:** [SIGNET](https://github.com/blitzandres/signet-thesis) (Signal Intelligence Network Visualization)

## Realms

| Freq | Realm | Data source |
|------|-------|-------------|
| 0 | **CARRIER** | Your public IP, ISP, ASN, timezone and geo from [ip-api.com](https://ip-api.com) (no key needed) |
| 1 | **TOPOLOGY** | Live network connections from a local [NetWatch](https://github.com/blitzandres/netwatch) instance (`http://localhost:5001`), with a simulated fallback |
| 2 | **STREAM** | DNS "meteors", with real domain resolution via Cloudflare DNS-over-HTTPS |
| 3 | **BLUETOOTH** | Nearby BLE devices from a local [bluth-scan](https://github.com/blitzandres/bluth-scan) instance (`http://localhost:5050`), with a simulated RSSI field fallback |
| 4 | **THREAT** | IP reputation from AbuseIPDB via the Cloudflare Worker proxy, with a heuristic fallback |

## Project layout

```
index.html           # the whole game (canvas engine, character, realms, UI)
worker/              # Cloudflare Worker: CORS proxy for ipinfo.io + AbuseIPDB (keys live in Worker secrets)
  index.js
  wrangler.toml
docs/superpowers/    # design spec + implementation plan
project_index.json   # project status / metadata
SETUP.md             # one-time GitHub Pages + Worker setup
```

## Run locally

The frontend is one static page, so any static file server works:

```bash
git clone https://github.com/blitzandres/sigspace.git
cd sigspace
python3 -m http.server 8000
# open http://localhost:8000
```

Optional, for live local data instead of the simulated fallbacks:

- Run **NetWatch** on port `5001` to feed the TOPOLOGY realm.
- Run **bluth-scan** on port `5050` to feed the BLUETOOTH realm.

## Worker (THREAT realm)

The THREAT realm calls a small Cloudflare Worker (`worker/`) so API keys never
ship to the browser. See [SETUP.md](SETUP.md) for deploy steps. In short:

```bash
cd worker
npx wrangler login
npx wrangler deploy
npx wrangler secret put IPINFO_TOKEN
npx wrangler secret put ABUSEIPDB_KEY
```

Wrangler's local `.wrangler/` state directory is gitignored. Don't commit it.
