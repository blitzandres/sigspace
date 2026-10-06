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
- DEVICE — TVs and controllable nodes in reach (control panel), safe preview by default

## Device reach (control panel)

A local companion (`device-reach/`) that discovers controllable devices on **your own
LAN** and lets you **play, pause, stop, change volume, mute, launch apps, power off / on,
and send a payload** to each one — from the SIGSPACE **DEVICE** realm or the dedicated
Control Panel.

**Safe by default / cyber note.** This is the one piece that can reach real hardware.
It is **never** served or active on the public website, binds to `127.0.0.1` only, and
starts **DISARMED** — it shows only a simulated field and refuses real actions until you
explicitly arm it on your own machine. Run it only on a network you trust; disarm or
quit when done. Full details and the API are in [`device-reach/README.md`](device-reach/README.md)
and credits are in [`NOTICE-device-reach.md`](NOTICE-device-reach.md).

```bash
cd device-reach
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py          # DISARMED on http://127.0.0.1:5070
# then, on purpose:
curl -X POST http://127.0.0.1:5070/api/arm -H 'Content-Type: application/json' -d '{"confirm":true}'
```

In SIGSPACE, tune to **DEVICE**, flip **LIVE** (bottom-right), click a node, and use its
buttons (▶ ⏸ ⏹ 🔊 ⏻ 📡). Drivers: samsung · roku · lg-webos · cast · upnp · http · wol ·
ssdp · simulated. Custom http/WoL nodes go in `reach_nodes.json` (git-ignored).

### Website preview (mock, no live connections)

`preview/device-reach.html` is a self-contained, nstarlive-style control panel that runs
on **mock data only** — every button acts on simulated devices, nothing touches the
network. This is what's safe to show on GitHub Pages / andresblitz.com. Open it from the
DEVICE realm ("OPEN CONTROL PANEL") or directly:
<https://blitzandres.github.io/sigspace/preview/device-reach.html>.
