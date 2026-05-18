# SIGSPACE — Design Spec
**Date:** 2026-05-17
**Project:** blitzandres/sigspace (new private repo)
**Thesis companion:** blitzandres/signet-thesis
**Related:** blitzandres/bluth-scan, blitzandres/netwatch

---

## 1. Concept

SIGSPACE is a video game-style perception layer for real network and signal data. The user exists as a pixel character sitting at a terminal inside cyberspace. The geometry of the world around them IS the data — not a chart of the data, not a table, but the spatial environment itself.

The design insight: video game spatial encoding (proximity, orbits, color, pulse rate, particle trails) allows a human to perceive far more signal information simultaneously than any table or dashboard. You read the world, not the numbers.

This is the playable frontend of the SIGNET thesis — the first 0.01% made visible and navigable.

---

## 2. Technical Architecture

### Stack
- **Single `index.html`** — all HTML, CSS, JS inline. No npm, no build step, no frameworks.
- **HTML5 Canvas 2D** — game loop via `requestAnimationFrame`, ~60fps, ~30–50MB RAM.
- **GitHub Pages** — static hosting, instant deploy via `git push`. Free, zero-config.
- **Public APIs** — all data fetched client-side. No server required.

### Files
```
sigspace/
├── index.html             ← entire game (Canvas 2D engine + all logic)
├── project_index.json     ← AI session checkpoint + feature board
├── apikeys.example.json   ← key shape template (committed, no real values)
├── apikeys.json           ← real keys (gitignored, local only)
├── .gitignore
├── README.md
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-17-sigspace-design.md  ← this file
```

### Repo visibility
- Repo: **private** (`blitzandres/sigspace`)
- GitHub Pages enabled on `main` branch — **requires GitHub Pro for private repos** ($4/mo). If not on Pro, make the repo public (safe — `apikeys.json` is gitignored, no secrets in code).
- `apikeys.json` in `.gitignore` — keys never committed even to private repo

---

## 3. The Game World

### Rendering
- Full-screen canvas, dark void background with faint isometric grid
- **Isometric projection** via 2D canvas math — fake depth, no WebGL required
- Character: ~16×24px pixel-art figure (drawn with canvas primitives — rectangles + circles, no image files), sitting at a glowing terminal at canvas center
- Character glows with a soft pulse matching current signal frequency color

### Space objects
- **Nodes**: glowing spheres (canvas arc fills) floating in orbit around character
- **Lines**: pulsing connection arcs between nodes and character
- **Text labels**: hostnames / IPs / countries rendered near nodes on hover
- **Particles**: small dots traveling along connection lines (traffic flow indicator)
- **Proximity encoding**: closer node = stronger signal / more active connection

### Camera
- Fixed isometric view, no scrolling for MVP
- Everything orbits the character at center

---

## 4. The Frequency Dial

### Mechanic
- Physical dial rendered at bottom center of screen
- 5 notch positions labeled: CARRIER · TOPOLOGY · STREAM · BLUETOOTH · THREAT
- Navigation: keyboard `←` `→` arrows OR click/tap on dial notches
- Switching frequency: 0.5s glitch/static transition animation (canvas noise overlay), then new realm fades in

### The 5 Realms

| Notch | Name | What you perceive | Real data source |
|-------|------|-------------------|-----------------|
| 1 | **CARRIER** | Your node in the internet — lone planet, ISP ring, city label | ip-api.com (public IP, ISP, city, country, ASN) |
| 2 | **TOPOLOGY** | Every live connection as an orbital node — lines pulse with traffic | NetWatch `/api/connections` if local, else WebRTC + ip-api enrichment |
| 3 | **STREAM** | DNS queries flying past as text meteors in real time | Cloudflare DoH `1.1.1.1/dns-query` (HTTPS, no key needed) |
| 4 | **BLUETOOTH** | BLE devices as neural orbs, RSSI encoded as orbital distance | bluth-scan `/api/devices` if local, else simulated with realistic patterns |
| 5 | **THREAT** | Threat IPs as red incoming objects; safe IPs blue | AbuseIPDB API + ipinfo.io threat flags |

### Fallback behavior
If a data source is unreachable (local backend not running, no API key), that realm renders in **"ghost mode"**: faded monochrome nodes with `[NO SIGNAL]` label. The game never crashes — it degrades gracefully.

---

## 5. AI Session Continuity — project_index.json

Every Claude session starts by reading this file. Every session ends with it updated. Structure:

```json
{
  "project": "SIGSPACE",
  "version": "0.1.0",
  "thesis_ref": "blitzandres/signet-thesis",
  "bt_ref": "blitzandres/bluth-scan",
  "netwatch_ref": "blitzandres/netwatch",
  "last_session": "YYYY-MM-DD",
  "resume_at": "phase_X.task_Y",
  "notes": "free text — what was done, what broke, what to try next",
  "api_keys_ref": "apikeys.json (gitignored) — see apikeys.example.json",
  "phases": {
    "phase_1_core_engine": {
      "name": "Canvas engine, character, dial",
      "status": "pending|in_progress|done",
      "tasks": [
        { "id": "1.1", "done": false, "name": "Canvas game loop + isometric grid" },
        { "id": "1.2", "done": false, "name": "Pixel character + terminal glow animation" },
        { "id": "1.3", "done": false, "name": "Frequency dial render + keyboard nav" },
        { "id": "1.4", "done": false, "name": "Glitch transition animation between realms" }
      ]
    },
    "phase_2_carrier_realm": {
      "name": "CARRIER frequency — your IP as a planet",
      "status": "pending",
      "tasks": [
        { "id": "2.1", "done": false, "name": "Fetch ip-api.com on load" },
        { "id": "2.2", "done": false, "name": "Render ISP planet + ASN rings" },
        { "id": "2.3", "done": false, "name": "Geo label (city, country flag emoji)" }
      ]
    },
    "phase_3_topology_realm": {
      "name": "TOPOLOGY frequency — live connections as orbital nodes",
      "status": "pending",
      "tasks": [
        { "id": "3.1", "done": false, "name": "WebRTC local IP discovery" },
        { "id": "3.2", "done": false, "name": "Attempt NetWatch /api/connections (CORS)" },
        { "id": "3.3", "done": false, "name": "Enrich IPs with ip-api.com batch" },
        { "id": "3.4", "done": false, "name": "Render orbital node field + pulse lines" }
      ]
    },
    "phase_4_stream_realm": {
      "name": "STREAM frequency — DNS meteor shower",
      "status": "pending",
      "tasks": [
        { "id": "4.1", "done": false, "name": "DoH query loop — poll 20 common domains (google.com, cloudflare.com, etc.) via Cloudflare DoH every 3s, rotate list" },
        { "id": "4.2", "done": false, "name": "Render DNS meteors flying past character" },
        { "id": "4.3", "done": false, "name": "Color-code by domain type (CDN/social/tracker/system)" }
      ]
    },
    "phase_5_bluetooth_realm": {
      "name": "BLUETOOTH frequency — BLE neural field",
      "status": "pending",
      "tasks": [
        { "id": "5.1", "done": false, "name": "Attempt bluth-scan /api/devices (CORS)" },
        { "id": "5.2", "done": false, "name": "Simulated BLE fallback: 3–8 fake devices, randomized RSSI -40 to -90, device names like 'AirPods', 'Mi Band', 'Unknown', slow drift in orbital position" },
        { "id": "5.3", "done": false, "name": "RSSI → orbital distance mapping" },
        { "id": "5.4", "done": false, "name": "Neural thread rendering (bluth-scan aesthetic)" }
      ]
    },
    "phase_6_threat_realm": {
      "name": "THREAT frequency — dark signal entities",
      "status": "pending",
      "tasks": [
        { "id": "6.1", "done": false, "name": "AbuseIPDB lookup for known-bad IPs" },
        { "id": "6.2", "done": false, "name": "ipinfo.io threat flag enrichment" },
        { "id": "6.3", "done": false, "name": "Red approach-vector animation for threats" },
        { "id": "6.4", "done": false, "name": "Blue safe-node rendering for clean IPs" }
      ]
    },
    "phase_7_deploy": {
      "name": "GitHub Pages deploy + repo setup",
      "status": "pending",
      "tasks": [
        { "id": "7.1", "done": false, "name": "Init git repo, push to blitzandres/sigspace (private)" },
        { "id": "7.2", "done": false, "name": "Enable GitHub Pages on main branch" },
        { "id": "7.3", "done": false, "name": "Add .gitignore (apikeys.json, .env, __pycache__)" },
        { "id": "7.4", "done": false, "name": "Commit apikeys.example.json" }
      ]
    }
  }
}
```

---

## 6. API Keys

### Keys needed
| Key | Service | Free tier | Where used |
|-----|---------|-----------|-----------|
| `ipinfo_token` | ipinfo.io | 50k req/month | TOPOLOGY enrichment (richer data) |
| `abuseipdb_key` | AbuseIPDB | 1k req/day | THREAT realm |
| *(none)* | ip-api.com | 45 req/min, no key | CARRIER primary + TOPOLOGY basic geo |
| *(none)* | Cloudflare DoH | Unlimited, no key | STREAM realm |

### Storage rule
- `apikeys.example.json` committed to repo showing the shape with empty strings
- `apikeys.json` in `.gitignore` — filled locally, read by `fetch('apikeys.json')` at game load
- Keys are read once at startup and stored in a JS module-scope object — never logged, never sent anywhere except their respective APIs

---

## 7. Perception Design Principles

These govern every visual decision in the game:

1. **Proximity = intensity** — closer to character = more active / stronger signal
2. **Pulse rate = data rate** — faster pulse = more packets/connections
3. **Color = signal type** — gold/amber = outbound, blue/cyan = inbound, red = threat, green = healthy/local
4. **Size = importance** — larger node = more connections / higher bandwidth
5. **Motion = time** — particles moving along lines show current flow direction
6. **Ghost mode when offline** — no signal = faded monochrome, never a crash

These map directly to the SIGNET thesis's cross-signal correlation framework — each visual dimension is an independent channel of information the human brain can absorb simultaneously.

---

## 8. Out of Scope (MVP)

- No multiplayer / shared sessions
- No recording / replay
- No mobile touch UI (desktop-first for MVP)
- No WebGL / Three.js (pure Canvas 2D)
- No server-side backend (GitHub Pages static only)
- No real-time Bluetooth without bluth-scan running locally
