# SIGSPACE

A video game where you exist as a pixel character inside your own network.
Real signal data floats around you in cyberspace. Tune the frequency dial to switch dimensions.

**Live:** https://blitzandres.github.io/sigspace

**Thesis:** [SIGNET](https://github.com/blitzandres/signet-thesis) — Signal Intelligence Network Visualization

## Local preview (idle-safe)

From the repo root:

    python3 scripts/idle-server.py

Then open http://127.0.0.1:8765/

The server exits after 1 hour with no requests so it does not sit on your machine. Any page load resets the timer.

Optional: PORT=9000 IDLE_SECONDS=3600 python3 scripts/idle-server.py

## Signals backend

Cloudflare Worker: https://sigspace.andres-491.workers.dev

- GET / — health
- GET /api/geo — your IP geo (ip-api via the worker, no mixed-content block)
- GET /api/geo?ip= — lookup one address
- POST /api/geo/batch — JSON list of IPs for TOPOLOGY
- GET /api/doh?name= — Cloudflare DoH for STREAM meteors
- GET /api/abuseipdb?ip= — threat scores
- GET /api/ipinfo?ip= — ipinfo.io (needs IPINFO_TOKEN)

The frontend tries the Worker first, then public CORS APIs, then a simulated fallback so the realms still render offline.

Deploy the worker after pulling:

    cd worker
    wrangler deploy

Secrets stay out of git:

    wrangler secret put IPINFO_TOKEN
    wrangler secret put ABUSEIPDB_KEY

## Realms

- CARRIER — your IP, city, ISP, ASN
- TOPOLOGY — live connections from NetWatch, or a fallback map
- STREAM — DNS meteors via Cloudflare DoH
- BLUETOOTH — BLE nodes from bluth-scan, or a simulated RSSI field
- THREAT — AbuseIPDB via the Worker

## Device reach (TV / local power-off)

Local companion that discovers TVs and media devices on your LAN and powers them off from the DEVICE realm.

```bash
cd device-reach
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open the idle preview and tune to **DEVICE**. Click a node → **POWER OFF**.

- API: `http://127.0.0.1:5070/`
- Samsung is prioritized (accept the Allow prompt on the TV the first time)
- Also: Roku, LG webOS, UPnP MediaRenderer, plus simulated demos when nothing is found
- Idle exit after 1 hour with no requests (`IDLE_SECONDS`)
