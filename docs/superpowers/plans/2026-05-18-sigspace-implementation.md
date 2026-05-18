# SIGSPACE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build SIGSPACE — a video game where a pixel character sits in cyberspace surrounded by real live signal data (IP connections, DNS, Bluetooth, threats), navigated via a 5-notch frequency dial, deployed as a single HTML file on GitHub Pages with a Cloudflare Worker as the API proxy.

**Architecture:** Pure HTML5 Canvas 2D, single `index.html`, no build system, no npm, no frameworks. Orbital mechanics borrowed from solar system animation pattern (nodes orbit character via `cos`/`sin` on `requestAnimationFrame`). Cloudflare Worker handles CORS + API key injection. All hosting is free tier.

**Tech Stack:** HTML5 Canvas 2D, Vanilla JS, GitHub Pages, Cloudflare Workers (free tier), ip-api.com (no key), Cloudflare DoH (no key), ipinfo.io (free key), AbuseIPDB (free key)

**Spec:** `docs/superpowers/specs/2026-05-17-sigspace-design.md`
**Checkpoint:** `project_index.json` (root) — update `resume_at` + task `done` flags after each task

---

## File Map

| File | Responsibility |
|------|---------------|
| `index.html` | Entire game: canvas engine, character, orbital nodes, 5 realms, frequency dial, all fetch calls |
| `worker/index.js` | Cloudflare Worker: CORS proxy for ipinfo.io + AbuseIPDB, injects keys from env vars |
| `worker/wrangler.toml` | Worker config: name, routes, compatibility |
| `project_index.json` | AI session checkpoint + per-task progress board |
| `SETUP.md` | One-time setup instructions: repo creation, Pages enable, Worker deploy, secrets |
| `.gitignore` | Ignore: `apikeys.json`, `.env`, `node_modules`, `__pycache__` |
| `README.md` | What SIGSPACE is + live URL |

---

## Task 1: Repo + Scaffold

**Files:**
- Create: `index.html` (empty shell)
- Create: `project_index.json`
- Create: `.gitignore`
- Create: `README.md`
- Create: `SETUP.md`
- Create: `worker/index.js` (empty shell)
- Create: `worker/wrangler.toml`

- [ ] **Step 1.1: Create GitHub repo via CLI**

```bash
cd /Users/andresblitz/Documents/sigspace
gh repo create blitzandres/sigspace --public --description "SIGSPACE — real signal data as a video game world" --source . --remote origin --push
```

Expected: repo created at `https://github.com/blitzandres/sigspace`, remote `origin` set.

- [ ] **Step 1.2: Create `.gitignore`**

```
apikeys.json
.env
node_modules/
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 1.3: Create `project_index.json`**

```json
{
  "project": "SIGSPACE",
  "version": "0.1.0",
  "thesis_ref": "blitzandres/signet-thesis",
  "bt_ref": "blitzandres/bluth-scan",
  "netwatch_ref": "blitzandres/netwatch",
  "last_session": "2026-05-18",
  "resume_at": "task_2",
  "notes": "Task 1 done: repo created, scaffold committed.",
  "api_keys_ref": "Cloudflare Worker env vars — set via: wrangler secret put IPINFO_TOKEN && wrangler secret put ABUSEIPDB_KEY",
  "infrastructure": {
    "frontend_url": "https://blitzandres.github.io/sigspace",
    "worker_url": "https://sigspace.blitzandres.workers.dev",
    "github_pages": "enabled on main branch",
    "all_free_tier": true
  },
  "phases": {
    "task_1_scaffold": { "done": true, "name": "Repo + scaffold" },
    "task_2_canvas_engine": { "done": false, "name": "Canvas engine + game loop" },
    "task_3_character": { "done": false, "name": "Pixel character + terminal" },
    "task_4_orbital_nodes": { "done": false, "name": "Orbital node system" },
    "task_5_freq_dial": { "done": false, "name": "Frequency dial + transitions" },
    "task_6_carrier": { "done": false, "name": "CARRIER realm — ip-api.com" },
    "task_7_topology": { "done": false, "name": "TOPOLOGY realm — live connections" },
    "task_8_stream": { "done": false, "name": "STREAM realm — DNS meteors" },
    "task_9_bluetooth": { "done": false, "name": "BLUETOOTH realm — BLE nodes" },
    "task_10_threat": { "done": false, "name": "THREAT realm — AbuseIPDB" },
    "task_11_worker": { "done": false, "name": "Cloudflare Worker — API proxy" },
    "task_12_deploy": { "done": false, "name": "Deploy: Pages + Worker + secrets" }
  }
}
```

- [ ] **Step 1.4: Create `SETUP.md`**

```markdown
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
```

- [ ] **Step 1.5: Create `README.md`**

```markdown
# SIGSPACE

A video game where you exist as a pixel character inside your own network.
Real signal data floats around you in cyberspace. Tune the frequency dial to switch dimensions.

**Live:** https://blitzandres.github.io/sigspace

**Thesis:** [SIGNET](https://github.com/blitzandres/signet-thesis) — Signal Intelligence Network Visualization
```

- [ ] **Step 1.6: Create empty `index.html` shell**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SIGSPACE</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #000; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
  <canvas id="c"></canvas>
  <script>
    // SIGSPACE — engine loads here in Task 2
    console.log('SIGSPACE boot');
  </script>
</body>
</html>
```

- [ ] **Step 1.7: Create `worker/wrangler.toml`**

```toml
name = "sigspace"
main = "index.js"
compatibility_date = "2024-01-01"

[vars]
ALLOWED_ORIGIN = "https://blitzandres.github.io"
```

- [ ] **Step 1.8: Create empty `worker/index.js` shell**

```javascript
export default {
  async fetch(request, env) {
    return new Response('SIGSPACE worker online', { status: 200 });
  }
};
```

- [ ] **Step 1.9: Commit**

```bash
git add -A
git commit -m "feat: scaffold repo — index.html shell, worker shell, project_index"
git push origin main
```

- [ ] **Step 1.10: Update `project_index.json`** — set `task_1_scaffold.done = true`, `resume_at = "task_2"`

---

## Task 2: Canvas Engine + Game Loop

**Files:**
- Modify: `index.html` — replace the `<script>` block

- [ ] **Step 2.1: Add the full canvas engine to `index.html`**

Replace the `<script>` block with:

```javascript
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');

// ── State ──────────────────────────────────────────────────
const S = {
  W: 0, H: 0, cx: 0, cy: 0,   // canvas dimensions + center
  freq: 0,                       // current frequency (0–4)
  freqNames: ['CARRIER','TOPOLOGY','STREAM','BLUETOOTH','THREAT'],
  freqColors: ['#00aaff','#00ffaa','#ffaa00','#aa66ff','#ff3333'],
  nodes: [],                     // orbital nodes for current realm
  particles: [],                 // connection trail particles
  meteors: [],                   // STREAM realm DNS meteors
  transition: 0,                 // 0=stable, >0=glitch anim frames remaining
  t: 0,                          // frame counter
  data: {}                       // fetched real data per realm
};

// ── Resize ─────────────────────────────────────────────────
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  S.W = canvas.width;
  S.H = canvas.height;
  S.cx = S.W / 2;
  S.cy = S.H / 2;
}
window.addEventListener('resize', resize);
resize();

// ── Game Loop ──────────────────────────────────────────────
function loop() {
  ctx.fillStyle = '#04080f';
  ctx.fillRect(0, 0, S.W, S.H);
  drawGrid();
  drawNodes();
  drawCharacter();
  drawDial();
  if (S.transition > 0) { drawGlitch(); S.transition--; }
  S.t++;
  requestAnimationFrame(loop);
}

// ── Grid ───────────────────────────────────────────────────
function drawGrid() {
  ctx.save();
  ctx.strokeStyle = 'rgba(0,170,255,0.05)';
  ctx.lineWidth = 1;
  const step = 60;
  for (let x = S.cx % step; x < S.W; x += step) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, S.H); ctx.stroke();
  }
  for (let y = S.cy % step; y < S.H; y += step) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(S.W, y); ctx.stroke();
  }
  ctx.restore();
}

// ── Placeholder draw functions (filled in later tasks) ─────
function drawNodes() {}
function drawCharacter() {}
function drawDial() {}
function drawGlitch() {}

// ── Keyboard ───────────────────────────────────────────────
window.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') switchFreq((S.freq + 1) % 5);
  if (e.key === 'ArrowLeft')  switchFreq((S.freq + 4) % 5);
});

function switchFreq(next) {
  S.freq = next;
  S.transition = 20;
  S.nodes = [];
  loadRealm(next);
}

function loadRealm(f) {
  // filled in per realm tasks
}

// ── Boot ───────────────────────────────────────────────────
loop();
loadRealm(0);
```

- [ ] **Step 2.2: Open in browser and verify**

Open `index.html` directly (file://) or via `python3 -m http.server 8080`.
Expected: Black canvas with faint blue grid lines, no errors in console.

- [ ] **Step 2.3: Commit**

```bash
git add index.html
git commit -m "feat: canvas engine — game loop, grid, resize, freq switching skeleton"
git push origin main
```

- [ ] **Step 2.4: Update `project_index.json`** — `task_2_canvas_engine.done = true`, `resume_at = "task_3"`

---

## Task 3: Pixel Character + Terminal

**Files:**
- Modify: `index.html` — replace `drawCharacter()` placeholder

- [ ] **Step 3.1: Replace `drawCharacter()` with full implementation**

```javascript
function drawCharacter() {
  const x = S.cx, y = S.cy;
  const col = S.freqColors[S.freq];
  const pulse = 0.7 + 0.3 * Math.sin(S.t * 0.05);

  // glow aura
  ctx.save();
  ctx.shadowBlur = 30 * pulse;
  ctx.shadowColor = col;

  // desk / terminal (isometric slab — 3 parallelograms)
  const dw = 44, dh = 14;
  ctx.fillStyle = '#0a1a2e';
  ctx.beginPath();
  ctx.moveTo(x - dw, y + 14);
  ctx.lineTo(x,      y + 14 - dh/2);
  ctx.lineTo(x + dw, y + 14);
  ctx.lineTo(x,      y + 14 + dh/2);
  ctx.closePath(); ctx.fill();

  // desk top edge highlight
  ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.globalAlpha = 0.4;
  ctx.beginPath();
  ctx.moveTo(x - dw, y + 14);
  ctx.lineTo(x,      y + 14 - dh/2);
  ctx.lineTo(x + dw, y + 14);
  ctx.stroke();
  ctx.globalAlpha = 1;

  // monitor screen (glowing rect)
  ctx.fillStyle = col;
  ctx.globalAlpha = 0.15 * pulse;
  ctx.fillRect(x - 14, y - 10, 28, 18);
  ctx.globalAlpha = 1;
  ctx.strokeStyle = col; ctx.lineWidth = 1.5;
  ctx.strokeRect(x - 14, y - 10, 28, 18);

  // monitor scanlines
  ctx.strokeStyle = col; ctx.lineWidth = 0.5; ctx.globalAlpha = 0.3;
  for (let i = y - 8; i < y + 8; i += 3) {
    ctx.beginPath(); ctx.moveTo(x - 13, i); ctx.lineTo(x + 13, i); ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // character body
  ctx.fillStyle = '#c8d8f0';
  ctx.fillRect(x - 5, y - 22, 10, 12);  // torso

  // head
  ctx.beginPath();
  ctx.arc(x, y - 27, 6, 0, Math.PI * 2);
  ctx.fillStyle = '#e8e8e8';
  ctx.fill();

  // arms
  ctx.fillStyle = '#c8d8f0';
  ctx.fillRect(x - 10, y - 20, 4, 8);   // left arm (toward desk)
  ctx.fillRect(x + 6,  y - 20, 4, 8);   // right arm

  // eyes (tiny glowing dots)
  ctx.fillStyle = col;
  ctx.shadowBlur = 6; ctx.shadowColor = col;
  ctx.fillRect(x - 3, y - 29, 2, 2);
  ctx.fillRect(x + 1, y - 29, 2, 2);

  ctx.restore();
}
```

- [ ] **Step 3.2: Verify in browser**

Expected: Pixel character at center sitting at a small desk with a glowing monitor. Color should match current frequency (blue by default).

- [ ] **Step 3.3: Commit**

```bash
git add index.html
git commit -m "feat: pixel character + isometric terminal at canvas center"
git push origin main
```

- [ ] **Step 3.4: Update `project_index.json`** — `task_3_character.done = true`, `resume_at = "task_4"`

---

## Task 4: Orbital Node System

**Files:**
- Modify: `index.html` — replace `drawNodes()` placeholder, add `spawnNodes()` helper

The orbital pattern is based on the solar system demo: each node has `{ angle, speed, distance, label, color, size }`. Every frame: `x = cx + distance * cos(angle)`, `y = cy + distance * sin(angle)`, `angle += speed`.

- [ ] **Step 4.1: Add orbital node system**

Add these functions inside the `<script>` block, replacing `drawNodes()`:

```javascript
// ── Orbital Node System ────────────────────────────────────
function spawnNodes(dataArray) {
  // dataArray: [{ label, sublabel, color, size, speed }]
  S.nodes = dataArray.map((d, i) => ({
    label:    d.label    || '???',
    sublabel: d.sublabel || '',
    color:    d.color    || S.freqColors[S.freq],
    size:     d.size     || 6,
    distance: 120 + (i % 4) * 55 + Math.random() * 30,
    angle:    (i / dataArray.length) * Math.PI * 2 + Math.random() * 0.5,
    speed:    (d.speed || 0.004) * (Math.random() > 0.5 ? 1 : -1),
    pulseOff: Math.random() * Math.PI * 2
  }));
}

function drawNodes() {
  const col = S.freqColors[S.freq];

  S.nodes.forEach(node => {
    node.angle += node.speed;
    const nx = S.cx + node.distance * Math.cos(node.angle);
    const ny = S.cy + node.distance * Math.sin(node.angle);
    const pulse = 0.7 + 0.3 * Math.sin(S.t * 0.04 + node.pulseOff);

    // orbit ring (faint)
    ctx.save();
    ctx.strokeStyle = `rgba(${hexToRgb(col)},0.06)`;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 8]);
    ctx.beginPath();
    ctx.arc(S.cx, S.cy, node.distance, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // connection line from character to node
    ctx.strokeStyle = `rgba(${hexToRgb(node.color)},0.15)`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(S.cx, S.cy);
    ctx.lineTo(nx, ny);
    ctx.stroke();

    // node glow
    ctx.shadowBlur = 14 * pulse;
    ctx.shadowColor = node.color;

    // node circle
    ctx.beginPath();
    ctx.arc(nx, ny, node.size * pulse, 0, Math.PI * 2);
    ctx.fillStyle = node.color;
    ctx.globalAlpha = 0.85;
    ctx.fill();
    ctx.globalAlpha = 1;

    // label
    ctx.shadowBlur = 0;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#aaccee';
    ctx.textAlign = 'center';
    ctx.fillText(node.label, nx, ny - node.size - 6);
    if (node.sublabel) {
      ctx.fillStyle = '#556677';
      ctx.fillText(node.sublabel, nx, ny - node.size - 17);
    }

    ctx.restore();

    // spawn trail particle occasionally
    if (Math.random() < 0.08) {
      S.particles.push({ x: nx, y: ny, vx: (Math.random()-0.5)*0.8,
        vy: (Math.random()-0.5)*0.8, life: 30, color: node.color });
    }
  });

  // draw + age particles
  S.particles = S.particles.filter(p => p.life > 0);
  S.particles.forEach(p => {
    ctx.save();
    ctx.globalAlpha = p.life / 30 * 0.6;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    p.x += p.vx; p.y += p.vy; p.life--;
  });
}

// ── Helpers ────────────────────────────────────────────────
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `${r},${g},${b}`;
}
```

- [ ] **Step 4.2: Add test data to `loadRealm()` so nodes appear**

Replace the `loadRealm` function temporarily:

```javascript
function loadRealm(f) {
  S.nodes = [];
  S.particles = [];
  // Test: spawn 6 placeholder nodes
  spawnNodes([
    { label: '8.8.8.8',      sublabel: 'Google DNS',  color: '#00aaff', size: 8,  speed: 0.005 },
    { label: '1.1.1.1',      sublabel: 'Cloudflare',  color: '#00ffaa', size: 7,  speed: 0.004 },
    { label: '104.21.44.1',  sublabel: 'Cloudflare',  color: '#00aaff', size: 6,  speed: 0.003 },
    { label: 'netflix.com',  sublabel: 'CDN',          color: '#ffaa00', size: 9,  speed: 0.006 },
    { label: '185.220.101',  sublabel: 'TOR ⚠',        color: '#ff3333', size: 7,  speed: -0.004 },
    { label: '192.168.1.1',  sublabel: 'Router 🏠',    color: '#aa66ff', size: 8,  speed: 0.003 }
  ]);
}
```

- [ ] **Step 4.3: Verify in browser**

Expected: 6 glowing nodes orbiting the character with dashed orbit rings, fading trail particles, connection lines. Press `←` `→` — nodes clear, same 6 re-spawn with new frequency color.

- [ ] **Step 4.4: Commit**

```bash
git add index.html
git commit -m "feat: orbital node system with trail particles"
git push origin main
```

- [ ] **Step 4.5: Update `project_index.json`** — `task_4_orbital_nodes.done = true`, `resume_at = "task_5"`

---

## Task 5: Frequency Dial + Glitch Transition

**Files:**
- Modify: `index.html` — replace `drawDial()` and `drawGlitch()` placeholders

- [ ] **Step 5.1: Replace `drawDial()` with full implementation**

```javascript
function drawDial() {
  const col = S.freqColors[S.freq];
  const dialY = S.H - 60;
  const dialW = 320;
  const dialX = S.cx - dialW / 2;
  const notchW = dialW / 5;

  ctx.save();

  // dial background
  ctx.fillStyle = 'rgba(4,8,15,0.85)';
  ctx.strokeStyle = col;
  ctx.lineWidth = 1;
  ctx.shadowBlur = 10; ctx.shadowColor = col;
  roundRect(ctx, dialX - 10, dialY - 18, dialW + 20, 52, 6);
  ctx.fill(); ctx.stroke();
  ctx.shadowBlur = 0;

  // frequency label (big, above dial)
  ctx.font = 'bold 13px monospace';
  ctx.fillStyle = col;
  ctx.textAlign = 'center';
  ctx.shadowBlur = 8; ctx.shadowColor = col;
  ctx.fillText(`FREQ: ${S.freqNames[S.freq]}`, S.cx, dialY - 28);
  ctx.shadowBlur = 0;

  // notch marks
  for (let i = 0; i < 5; i++) {
    const nx = dialX + notchW * i + notchW / 2;
    const active = i === S.freq;
    ctx.fillStyle = active ? col : 'rgba(100,140,180,0.4)';
    ctx.font = active ? 'bold 10px monospace' : '9px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(S.freqNames[i], nx, dialY + 22);

    // tick mark
    ctx.strokeStyle = active ? col : 'rgba(100,140,180,0.3)';
    ctx.lineWidth = active ? 2 : 1;
    ctx.beginPath();
    ctx.moveTo(nx, dialY);
    ctx.lineTo(nx, dialY + (active ? 10 : 6));
    ctx.stroke();

    // active notch glow dot
    if (active) {
      ctx.beginPath();
      ctx.arc(nx, dialY + 12, 4, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.shadowBlur = 12; ctx.shadowColor = col;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // keyboard hint
  ctx.font = '9px monospace';
  ctx.fillStyle = 'rgba(100,140,180,0.5)';
  ctx.textAlign = 'center';
  ctx.fillText('← → to tune', S.cx, dialY + 36);

  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}
```

- [ ] **Step 5.2: Replace `drawGlitch()` with full implementation**

```javascript
function drawGlitch() {
  const intensity = S.transition / 20;
  ctx.save();

  // horizontal scanline tears
  for (let i = 0; i < 6 * intensity; i++) {
    const y = Math.random() * S.H;
    const h = Math.random() * 8 + 2;
    const offset = (Math.random() - 0.5) * 40 * intensity;
    ctx.drawImage(canvas, 0, y, S.W, h, offset, y, S.W, h);
  }

  // color channel split overlay
  ctx.globalAlpha = 0.12 * intensity;
  ctx.fillStyle = '#ff0044';
  ctx.fillRect(-4, 0, S.W, S.H);
  ctx.fillStyle = '#0044ff';
  ctx.fillRect(4, 0, S.W, S.H);

  // static noise dots
  ctx.globalAlpha = 0.15 * intensity;
  for (let i = 0; i < 200 * intensity; i++) {
    ctx.fillStyle = Math.random() > 0.5 ? '#ffffff' : S.freqColors[S.freq];
    ctx.fillRect(Math.random() * S.W, Math.random() * S.H, 2, 2);
  }

  // frequency text flash
  ctx.globalAlpha = intensity;
  ctx.font = `bold ${28 + Math.random()*10}px monospace`;
  ctx.fillStyle = S.freqColors[S.freq];
  ctx.textAlign = 'center';
  ctx.fillText(S.freqNames[S.freq], S.cx + (Math.random()-0.5)*10, S.cy - 80);

  ctx.restore();
}
```

- [ ] **Step 5.3: Also add click/tap on dial notches**

Add inside the `<script>` after the keyboard listener:

```javascript
canvas.addEventListener('click', e => {
  const dialY = S.H - 60;
  const dialW = 320;
  const dialX = S.cx - dialW / 2;
  const notchW = dialW / 5;
  if (e.clientY > dialY - 20 && e.clientY < dialY + 45) {
    const clicked = Math.floor((e.clientX - dialX) / notchW);
    if (clicked >= 0 && clicked < 5 && clicked !== S.freq) switchFreq(clicked);
  }
});
```

- [ ] **Step 5.4: Verify in browser**

Expected: Dial appears at bottom with 5 labeled notches, active notch glows, pressing `←` `→` triggers glitch/static transition animation then nodes reload. Clicking a notch also switches.

- [ ] **Step 5.5: Commit**

```bash
git add index.html
git commit -m "feat: frequency dial + glitch transition animation"
git push origin main
```

- [ ] **Step 5.6: Update `project_index.json`** — `task_5_freq_dial.done = true`, `resume_at = "task_6"`

---

## Task 6: CARRIER Realm — Real IP Data

**Files:**
- Modify: `index.html` — replace `loadRealm()` test stub with real CARRIER fetch

ip-api.com returns: `{ ip, city, country, isp, as, lat, lon, timezone }`. No API key needed.

- [ ] **Step 6.1: Replace `loadRealm()` with CARRIER implementation**

```javascript
async function loadRealm(f) {
  S.nodes = [];
  S.particles = [];
  S.meteors = [];

  if (f === 0) await loadCarrier();
  else if (f === 1) await loadTopology();
  else if (f === 2) await loadStream();
  else if (f === 3) await loadBluetooth();
  else if (f === 4) await loadThreat();
}

async function loadCarrier() {
  let geo = S.data.carrier;
  if (!geo) {
    try {
      const r = await fetch('https://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,isp,as,query,lat,lon,timezone');
      geo = await r.json();
      S.data.carrier = geo;
    } catch(e) {
      geo = { query:'?.?.?.?', city:'Unknown', country:'Unknown', isp:'Unknown', as:'AS???' };
    }
  }

  const flag = countryFlag(geo.countryCode || 'UN');
  spawnNodes([
    { label: geo.query,     sublabel: `${flag} ${geo.city}, ${geo.country}`, color: '#00aaff', size: 14, speed: 0.0015 },
    { label: 'YOUR NODE',   sublabel: 'origin',     color: '#00ffaa', size: 10, speed: 0 },
    { label: geo.isp || '?', sublabel: 'ISP',       color: '#00aaff', size: 8,  speed: 0.002 },
    { label: (geo.as||'').split(' ')[0], sublabel: 'ASN',color:'#aa66ff',size:7,speed:0.003},
    { label: geo.timezone||'',sublabel:'timezone',  color: '#445566', size: 5,  speed: -0.001 },
    { label: `${geo.lat?.toFixed(2)},${geo.lon?.toFixed(2)}`, sublabel:'geo coords',color:'#334455',size:5,speed:0.002}
  ]);

  // fix YOUR NODE at center (distance=0 makes it sit on character)
  S.nodes[1].distance = 0;
  S.nodes[1].speed = 0;
}

function countryFlag(code) {
  if (!code || code.length !== 2) return '🌐';
  return String.fromCodePoint(...[...code.toUpperCase()].map(c => 0x1F1E0 + c.charCodeAt(0) - 65));
}

// Stub the other realm loaders (filled in later tasks)
async function loadTopology()  { spawnNodes([{label:'[TOPOLOGY]',sublabel:'→ task 7',color:'#00ffaa',size:8,speed:0.003}]); }
async function loadStream()    { spawnNodes([{label:'[STREAM]',  sublabel:'→ task 8',color:'#ffaa00',size:8,speed:0.003}]); }
async function loadBluetooth() { spawnNodes([{label:'[BT]',      sublabel:'→ task 9',color:'#aa66ff',size:8,speed:0.003}]); }
async function loadThreat()    { spawnNodes([{label:'[THREAT]',  sublabel:'→ task 10',color:'#ff3333',size:8,speed:0.003}]); }
```

- [ ] **Step 6.2: Verify CARRIER realm**

Open browser. Freq 0 (CARRIER) should show your real public IP, city, ISP, ASN as orbital nodes. Check browser console for any CORS errors from ip-api.com (there should be none — it allows all origins).

Expected nodes: your real IP large at center-ish, city/country label, ISP name, ASN code.

- [ ] **Step 6.3: Commit**

```bash
git add index.html
git commit -m "feat: CARRIER realm — real IP geo from ip-api.com, no key needed"
git push origin main
```

- [ ] **Step 6.4: Update `project_index.json`** — `task_6_carrier.done = true`, `resume_at = "task_7"`

---

## Task 7: TOPOLOGY Realm — Live Connections

**Files:**
- Modify: `index.html` — replace `loadTopology()` stub

Strategy: Try NetWatch local backend first (`http://localhost:5001/api/connections`). If CORS blocked or offline, fall back to WebRTC STUN to get local IPs, then show simulated topology enriched with ip-api.com batch lookup (max 10 IPs per call).

- [ ] **Step 7.1: Replace `loadTopology()` with full implementation**

```javascript
async function loadTopology() {
  let connections = [];

  // Try NetWatch local backend first
  try {
    const r = await Promise.race([
      fetch('http://localhost:5001/api/connections'),
      new Promise((_,rej) => setTimeout(rej, 1500, new Error('timeout')))
    ]);
    if (r.ok) {
      const d = await r.json();
      connections = (d.connections || d || []).slice(0, 12);
    }
  } catch(e) { /* offline */ }

  // Fallback: simulated connections with realistic IPs
  if (!connections.length) {
    connections = [
      { dst_ip:'8.8.8.8',   dst_host:'dns.google',     bytes:1240, proto:'UDP' },
      { dst_ip:'1.1.1.1',   dst_host:'cloudflare.com', bytes:3200, proto:'TCP' },
      { dst_ip:'17.57.144.1',dst_host:'apple.com',     bytes:8800, proto:'TCP' },
      { dst_ip:'151.101.1.67',dst_host:'reddit.com',   bytes:4200, proto:'TCP' },
      { dst_ip:'52.20.1.44', dst_host:'aws.com',       bytes:12000,proto:'TCP' },
      { dst_ip:'104.21.14.1',dst_host:'cloudflare-cdn',bytes:6700, proto:'TCP' },
    ];
  }

  // Enrich with geo (ip-api batch, free, max 100 per call, no key)
  const ips = connections.map(c => c.dst_ip || c.ip).filter(Boolean).slice(0, 10);
  let geoMap = {};
  try {
    const r = await fetch('https://ip-api.com/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ips.map(q => ({ query: q, fields: 'status,country,countryCode,city,isp,query' })))
    });
    const geos = await r.json();
    geos.forEach(g => { if (g.status === 'success') geoMap[g.query] = g; });
  } catch(e) {}

  const nodes = connections.map((c, i) => {
    const ip = c.dst_ip || c.ip || '?';
    const geo = geoMap[ip] || {};
    const flag = countryFlag(geo.countryCode);
    const label = c.dst_host || ip;
    const sublabel = geo.city ? `${flag} ${geo.city}` : (c.proto || '');
    const isThreat = false;
    return {
      label: label.length > 18 ? label.slice(0,18)+'…' : label,
      sublabel,
      color: isThreat ? '#ff3333' : '#00ffaa',
      size: 5 + Math.min(12, Math.log2((c.bytes || 1000) / 100)),
      speed: 0.002 + i * 0.0003
    };
  });

  spawnNodes(nodes);
}
```

- [ ] **Step 7.2: Verify**

With NetWatch offline: should show 6 simulated nodes with geo labels.
With NetWatch running locally: should show real connections.
Either way no console errors, nodes orbit properly.

- [ ] **Step 7.3: Commit**

```bash
git add index.html
git commit -m "feat: TOPOLOGY realm — live connections from NetWatch or simulated fallback"
git push origin main
```

- [ ] **Step 7.4: Update `project_index.json`** — `task_7_topology.done = true`, `resume_at = "task_8"`

---

## Task 8: STREAM Realm — DNS Meteors

**Files:**
- Modify: `index.html` — replace `loadStream()`, add `drawMeteors()`, modify `loop()`

DNS over HTTPS via Cloudflare: `GET https://1.1.1.1/dns-query?name=google.com&type=A` with header `Accept: application/dns-json`. No key. Cycles through 24 domains every 3 seconds.

- [ ] **Step 8.1: Add meteor system + replace `loadStream()`**

Add after the `S` state object initialization:

```javascript
const DNS_DOMAINS = [
  'google.com','youtube.com','github.com','apple.com','microsoft.com',
  'cloudflare.com','netflix.com','twitter.com','reddit.com','amazon.com',
  'discord.com','slack.com','zoom.us','dropbox.com','spotify.com',
  'instagram.com','facebook.com','linkedin.com','twitch.tv','tiktok.com',
  'icloud.com','akamai.com','fastly.com','cdn.jsdelivr.net'
];
let _dnsIdx = 0;
let _dnsTimer = null;

async function loadStream() {
  if (_dnsTimer) clearInterval(_dnsTimer);
  S.meteors = [];
  spawnNodes([]); // no orbital nodes — meteors are the show
  pumpDNS();
  _dnsTimer = setInterval(pumpDNS, 2800);
}

async function pumpDNS() {
  if (S.freq !== 2) { clearInterval(_dnsTimer); return; }
  const domain = DNS_DOMAINS[_dnsIdx % DNS_DOMAINS.length];
  _dnsIdx++;
  try {
    const r = await fetch(`https://1.1.1.1/dns-query?name=${domain}&type=A`, {
      headers: { 'Accept': 'application/dns-json' }
    });
    const d = await r.json();
    const answers = d.Answer || [];
    const ip = answers.find(a => a.type === 1)?.data || '?';
    const ttl = answers[0]?.TTL || 0;
    spawnMeteor(domain, ip, ttl);
  } catch(e) {
    spawnMeteor(domain, 'NXDOMAIN', 0);
  }
}

function spawnMeteor(domain, ip, ttl) {
  const side = Math.floor(Math.random() * 4);
  let sx, sy, ex, ey;
  if (side === 0) { sx = Math.random()*S.W; sy = -20; ex = S.cx+(Math.random()-0.5)*200; ey = S.cy+(Math.random()-0.5)*100; }
  else if (side===1){ sx=S.W+20; sy=Math.random()*S.H; ex=S.cx+(Math.random()-0.5)*200; ey=S.cy+(Math.random()-0.5)*100; }
  else if (side===2){ sx=Math.random()*S.W; sy=S.H+20; ex=S.cx+(Math.random()-0.5)*200; ey=S.cy+(Math.random()-0.5)*100; }
  else { sx=-20; sy=Math.random()*S.H; ex=S.cx+(Math.random()-0.5)*200; ey=S.cy+(Math.random()-0.5)*100; }

  const isDNS = ['google.com','cloudflare.com','apple.com','microsoft.com'].some(d => domain.includes(d));
  const isCDN = ['akamai','fastly','cdn','cloudflare','amazon'].some(k => (domain+ip).includes(k));
  const col = isDNS ? '#00aaff' : isCDN ? '#ffaa00' : '#00ffaa';

  S.meteors.push({ x:sx, y:sy, tx:ex, ty:ey, domain, ip, ttl, color:col,
    life:120, maxLife:120, size: 2 + Math.random()*2 });
}

function drawMeteors() {
  S.meteors = S.meteors.filter(m => m.life > 0);
  S.meteors.forEach(m => {
    const prog = 1 - (m.life / m.maxLife);
    const x = m.x + (m.tx - m.x) * prog;
    const y = m.y + (m.ty - m.y) * prog;
    const alpha = Math.min(1, m.life / 20);

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.shadowBlur = 8; ctx.shadowColor = m.color;

    // meteor dot
    ctx.beginPath();
    ctx.arc(x, y, m.size, 0, Math.PI * 2);
    ctx.fillStyle = m.color;
    ctx.fill();

    // tail
    ctx.strokeStyle = m.color; ctx.lineWidth = 1.5; ctx.globalAlpha = alpha * 0.4;
    ctx.beginPath();
    const tailX = m.x + (m.tx - m.x) * Math.max(0, prog - 0.1);
    const tailY = m.y + (m.ty - m.y) * Math.max(0, prog - 0.1);
    ctx.moveTo(tailX, tailY); ctx.lineTo(x, y); ctx.stroke();

    // domain label near target
    if (prog > 0.6) {
      ctx.globalAlpha = alpha * (prog - 0.6) / 0.4;
      ctx.shadowBlur = 0;
      ctx.font = '9px monospace';
      ctx.fillStyle = m.color;
      ctx.textAlign = 'left';
      ctx.fillText(m.domain, x + 6, y - 2);
      ctx.fillStyle = '#445566';
      ctx.fillText(m.ip, x + 6, y + 9);
    }
    ctx.restore();
    m.life--;
  });
}
```

- [ ] **Step 8.2: Add `drawMeteors()` call to the game loop**

In the `loop()` function, add `if (S.freq === 2) drawMeteors();` after `drawNodes();`:

```javascript
function loop() {
  ctx.fillStyle = '#04080f';
  ctx.fillRect(0, 0, S.W, S.H);
  drawGrid();
  drawNodes();
  if (S.freq === 2) drawMeteors();
  drawCharacter();
  drawDial();
  if (S.transition > 0) { drawGlitch(); S.transition--; }
  S.t++;
  requestAnimationFrame(loop);
}
```

- [ ] **Step 8.3: Verify**

Switch to freq 2 (STREAM). Every ~3 seconds a DNS query fires and a glowing text meteor flies from an edge toward the character. Label shows domain + resolved IP. No orbital nodes in this realm.

- [ ] **Step 8.4: Commit**

```bash
git add index.html
git commit -m "feat: STREAM realm — DNS meteors via Cloudflare DoH, real domain resolution"
git push origin main
```

- [ ] **Step 8.5: Update `project_index.json`** — `task_8_stream.done = true`, `resume_at = "task_9"`

---

## Task 9: BLUETOOTH Realm — BLE Neural Field

**Files:**
- Modify: `index.html` — replace `loadBluetooth()` stub

Try bluth-scan local backend. If offline, use simulated BLE devices. RSSI maps to orbital distance (stronger = closer).

- [ ] **Step 9.1: Replace `loadBluetooth()` with full implementation**

```javascript
async function loadBluetooth() {
  let devices = [];

  // Try bluth-scan local backend
  try {
    const r = await Promise.race([
      fetch('http://localhost:5050/api/devices'),
      new Promise((_,rej) => setTimeout(rej, 1500, new Error('timeout')))
    ]);
    if (r.ok) {
      const d = await r.json();
      devices = (d.devices || d || []).slice(0, 10);
    }
  } catch(e) { /* offline */ }

  // Fallback: realistic simulated BLE environment
  if (!devices.length) {
    devices = [
      { name: 'AirPods Pro',    rssi: -42, address: 'AA:BB:CC:01' },
      { name: 'Apple Watch',    rssi: -48, address: 'AA:BB:CC:02' },
      { name: 'Mi Band 7',      rssi: -61, address: 'AA:BB:CC:03' },
      { name: 'Unknown Device', rssi: -74, address: 'DE:AD:BE:EF' },
      { name: 'iPhone 15',      rssi: -55, address: 'AA:BB:CC:04' },
      { name: 'BLE Beacon',     rssi: -82, address: 'BA:DC:0F:FE' },
    ];
  }

  const nodes = devices.map((d, i) => {
    const rssi = d.rssi || -70;
    // RSSI -30 (strong) → distance 80, RSSI -90 (weak) → distance 260
    const distance = 80 + (Math.abs(rssi) - 30) * (180/60);
    const strength = Math.max(0, Math.min(1, (rssi + 30) / -60));
    // color: green (strong) → yellow → red (weak)
    const r = Math.round(strength * 255);
    const g = Math.round((1 - strength) * 200 + 55);
    const color = `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}44`;

    return {
      label: d.name || 'Unknown',
      sublabel: `${rssi} dBm`,
      color: '#aa66ff',
      size: 4 + (1 - strength) * 8,
      speed: 0.003 + i * 0.0002,
      _distance: distance
    };
  });

  spawnNodes(nodes);
  // Override distances with RSSI-derived values
  nodes.forEach((n, i) => { if (S.nodes[i]) S.nodes[i].distance = n._distance; });
}
```

- [ ] **Step 9.2: Verify**

Freq 4 (BLUETOOTH): 6 orbital nodes at varying distances — closer = stronger signal. Labels show device name + RSSI. With bluth-scan running locally, shows real devices.

- [ ] **Step 9.3: Commit**

```bash
git add index.html
git commit -m "feat: BLUETOOTH realm — BLE nodes from bluth-scan or simulated RSSI field"
git push origin main
```

- [ ] **Step 9.4: Update `project_index.json`** — `task_9_bluetooth.done = true`, `resume_at = "task_10"`

---

## Task 10: THREAT Realm — Dark Signal

**Files:**
- Modify: `index.html` — replace `loadThreat()` stub

Uses AbuseIPDB via the Cloudflare Worker (Task 11). Until Worker is deployed, falls back to a curated list of known-bad IP classes + simulated threat scoring to make the realm functional immediately.

- [ ] **Step 10.1: Replace `loadThreat()` with full implementation**

```javascript
const WORKER_URL = 'https://sigspace.blitzandres.workers.dev';

async function loadThreat() {
  // Seed with IPs from CARRIER data + known suspicious ranges
  const seedIPs = [
    ...(S.data.carrier ? [] : []),
    '185.220.101.50',  // known TOR exit
    '194.165.16.11',   // known scanner
    '45.142.212.100',  // known bad
    '91.108.56.196',   // telegram (legit)
    '140.82.112.4',    // github (legit)
    '8.8.8.8',         // google (legit)
  ];

  const nodes = [];
  for (const ip of seedIPs.slice(0, 8)) {
    let score = 0, isp = '', country = '';

    // Try Worker proxy for AbuseIPDB
    try {
      const r = await Promise.race([
        fetch(`${WORKER_URL}/api/abuseipdb?ip=${ip}`),
        new Promise((_,rej) => setTimeout(rej, 2000, new Error('timeout')))
      ]);
      if (r.ok) {
        const d = await r.json();
        score = d.abuseConfidenceScore || 0;
        isp = d.isp || '';
        country = d.countryCode || '';
      }
    } catch(e) {
      // Worker not deployed yet — use heuristic
      score = ['185.220','194.165','45.142','91.108'].some(p => ip.startsWith(p)) ? 75 : 5;
    }

    const isThreat = score > 25;
    const flag = countryFlag(country);
    nodes.push({
      label: ip,
      sublabel: `${flag} ${isThreat ? '⚠ THREAT' : '✓ clean'} ${score}%`,
      color: isThreat ? '#ff3333' : '#00aaff',
      size: isThreat ? 9 + score/20 : 6,
      speed: isThreat ? -0.005 : 0.003  // threats orbit backwards
    });
  }

  spawnNodes(nodes);
}
```

- [ ] **Step 10.2: Verify**

Freq 5 (THREAT): Known TOR IPs appear as large red nodes orbiting backwards. Google/GitHub appear as small blue nodes. AbuseIPDB data shown when Worker is running; heuristic shown otherwise.

- [ ] **Step 10.3: Commit**

```bash
git add index.html
git commit -m "feat: THREAT realm — AbuseIPDB via Worker, heuristic fallback"
git push origin main
```

- [ ] **Step 10.4: Update `project_index.json`** — `task_10_threat.done = true`, `resume_at = "task_11"`

---

## Task 11: Cloudflare Worker — API Proxy

**Files:**
- Modify: `worker/index.js` — full CORS proxy for ipinfo.io + AbuseIPDB

- [ ] **Step 11.1: Write full Worker implementation**

Replace `worker/index.js`:

```javascript
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
```

- [ ] **Step 11.2: Deploy the Worker via wrangler CLI**

```bash
cd /Users/andresblitz/Documents/sigspace/worker
npm install wrangler --save-dev
npx wrangler login
npx wrangler deploy
```

Expected output: `Deployed sigspace to https://sigspace.blitzandres.workers.dev`

- [ ] **Step 11.3: Set API secrets**

```bash
npx wrangler secret put IPINFO_TOKEN
# (paste your ipinfo.io token, press Enter)

npx wrangler secret put ABUSEIPDB_KEY
# (paste your AbuseIPDB key, press Enter)
```

- [ ] **Step 11.4: Test the Worker**

```bash
curl https://sigspace.blitzandres.workers.dev/
# Expected: {"status":"ok","service":"sigspace-worker"}

curl "https://sigspace.blitzandres.workers.dev/api/ipinfo?ip=8.8.8.8"
# Expected: JSON with Google IP info

curl "https://sigspace.blitzandres.workers.dev/api/abuseipdb?ip=8.8.8.8"
# Expected: JSON with abuseConfidenceScore
```

- [ ] **Step 11.5: Commit Worker**

```bash
cd /Users/andresblitz/Documents/sigspace
git add worker/
git commit -m "feat: Cloudflare Worker — CORS proxy for ipinfo.io + AbuseIPDB, keys in env"
git push origin main
```

- [ ] **Step 11.6: Update `project_index.json`** — `task_11_worker.done = true`, `resume_at = "task_12"`

---

## Task 12: Deploy to GitHub Pages + Final Wiring

**Files:**
- Modify: `index.html` — confirm `WORKER_URL` is correct
- Modify: `project_index.json` — all tasks done

- [ ] **Step 12.1: Enable GitHub Pages via CLI**

```bash
gh api repos/blitzandres/sigspace/pages \
  --method POST \
  --field source='{"branch":"main","path":"/"}' \
  --header "Accept: application/vnd.github+json"
```

Expected: `{"url":"https://blitzandres.github.io/sigspace", "status":"queued"}`

- [ ] **Step 12.2: Wait for Pages to go live**

```bash
gh api repos/blitzandres/sigspace/pages | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('html_url'))"
```

Expected: `built https://blitzandres.github.io/sigspace`

- [ ] **Step 12.3: Confirm `WORKER_URL` in `index.html` is correct**

The line `const WORKER_URL = 'https://sigspace.blitzandres.workers.dev';` should match exactly what `wrangler deploy` printed in Task 11.2.

- [ ] **Step 12.4: Smoke test the live URL**

Open `https://blitzandres.github.io/sigspace` in browser.

Checklist:
- [ ] Game loads (no blank screen, no console errors)
- [ ] Character visible at center with glowing terminal
- [ ] CARRIER (freq 0): real IP, city, ISP shown as orbital nodes
- [ ] TOPOLOGY (freq 1): 6+ connection nodes orbiting
- [ ] STREAM (freq 2): DNS meteors firing every ~3s
- [ ] BLUETOOTH (freq 3): BLE nodes at RSSI-derived distances
- [ ] THREAT (freq 4): red threat nodes + blue clean nodes
- [ ] `←` `→` keys switch realms with glitch transition
- [ ] Clicking dial notches works
- [ ] Worker health: `curl https://sigspace.blitzandres.workers.dev/` returns `{"status":"ok"}`

- [ ] **Step 12.5: Final commit**

```bash
git add -A
git commit -m "feat: all 5 realms live — SIGSPACE deployed to GitHub Pages + Cloudflare Worker"
git push origin main
```

- [ ] **Step 12.6: Update `project_index.json`** — all tasks done, `resume_at = "complete"`, add live URL to notes

---

## Self-Review Checklist (completed inline)

- **Spec coverage:** All 8 spec sections covered: architecture ✓, 5 realms ✓, character ✓, dial ✓, project_index.json ✓, API keys via Worker ✓, perception design principles (embedded in color/size/pulse choices) ✓, out-of-scope exclusions respected ✓
- **Placeholder scan:** No TBD/TODO. All code blocks are complete. All file paths are exact.
- **Type consistency:** `spawnNodes()` called identically in all realm loaders. `S.nodes`, `S.meteors`, `S.particles` cleared consistently in `loadRealm()`. `S.freq` index 0–4 matches `S.freqNames` and `S.freqColors` arrays throughout. `hexToRgb()` helper used correctly in `drawNodes()`.
- **Missing:** `project_index.json` update step included in every task. `wrangler.toml` doesn't require `package.json` but `npm install wrangler` does — covered in Task 11.2.
