# device-reach

Local companion for SIGSPACE. It discovers controllable devices on **your own LAN**
and lets the SIGSPACE **DEVICE** realm (and the Control Panel) **play, pause, stop,
change volume, mute, launch apps, power off / on, and send a payload** to a device —
but only on the computer you run it on, and only after you explicitly arm it.

> **This is the part that can reach real hardware. It is OFF the internet, OFF by
> default, and never runs on the public website.** The website only ever shows a
> safe *preview* with mock devices.

## Safe by default

- Starts **DISARMED**. While disarmed it exposes only the *simulated* field and
  refuses every real action with HTTP `423 Locked`. No LAN discovery happens either.
- You arm it on purpose: `POST /api/arm {"confirm": true}` (or start with
  `REACH_ARMED=1`). Disarm any time: `POST /api/disarm`.
- Binds to `127.0.0.1` only — not reachable from other machines.
- Idle-exits after 1 hour with no requests (`IDLE_SECONDS`) so it never lingers.
- Talks only to devices on your local network (and only the custom hosts you list
  yourself). It never calls the public internet to control anything.

## Connection drivers

| Driver   | Discovers                        | Controls |
|----------|----------------------------------|----------|
| samsung  | Samsung Tizen TVs (SSDP / probe) | power off, play, pause, stop, next/prev, vol ±, mute, any key, **send text** |
| roku     | Roku TVs & players (SSDP + ECP)  | power off, play, pause, stop, next/prev, vol ±, mute, key, **launch app** |
| lg-webos | LG webOS TVs (SSDP)              | power off, play, pause, stop, vol ±, mute (pairing may be needed) |
| cast     | Google Cast / Chromecast *(opt)* | play, pause, stop, next/prev, vol ±, mute |
| upnp     | UPnP/DLNA MediaRenderers         | play, pause, stop, next, prev |
| http     | **your** custom nodes (config)   | any action you define → an HTTP request (incl. **send payload**) |
| wol      | **your** Wake-on-LAN hosts       | **power on** (magic packet) |
| ssdp     | any UPnP device (read-only)      | — (visibility only, no control) |
| simulated| always                           | everything, as a no-op demo |

Samsung is prioritised (Andrés). The first real action on a TV may show an **Allow**
prompt on the screen — accept it once.

### Custom nodes (http / wol)

Copy `reach_nodes.example.json` to `reach_nodes.json` and edit. That file is
git-ignored (it can contain MAC addresses and local hostnames) and is the **only**
set of custom hosts device-reach will ever touch. Nothing in it is auto-discovered.

## Run locally

```bash
cd device-reach
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py          # starts DISARMED on http://127.0.0.1:5070
```

Then open SIGSPACE, tune to **DEVICE**, flip the **LIVE** switch (bottom-right), and
arm control:

```bash
curl -X POST http://127.0.0.1:5070/api/arm -H 'Content-Type: application/json' -d '{"confirm":true}'
```

Click a node to see its buttons (▶ ⏸ ⏹ 🔊 ⏻ 📡). Disarm with `/api/disarm`, or just
quit the process.

Optional Google Cast support: `.venv/bin/pip install pychromecast`.

## API

| Method | Path            | Purpose |
|--------|-----------------|---------|
| GET    | `/`             | health + armed state + drivers |
| GET    | `/api/status`   | armed, drivers, action types, device count |
| GET    | `/api/devices`  | devices in reach (simulated only while disarmed) |
| POST   | `/api/rescan`   | force a fresh scan |
| POST   | `/api/arm`      | `{"confirm":true}` → enable real discovery + control |
| POST   | `/api/disarm`   | back to safe/simulated |
| POST   | `/api/action`   | `{"id","action","params"}` → run an action on a device |
| POST   | `/api/poweroff` | legacy shortcut for `action: power_off` |

Actions: `power_off, power_on, play, pause, stop, next, prev, volume_up,
volume_down, mute, key, launch, send`. A device only accepts the actions it
advertises in its `capabilities`.

## Cyber-security note

This companion can turn devices on/off and push commands/payloads on your network,
so treat it like any other remote-control tool:

- Run it **only on a network you trust**, and keep it bound to `127.0.0.1`.
- It is disarmed until you arm it; disarm or quit when you're done.
- Do not expose port 5070 to the internet or put it behind a public tunnel.
- `reach_nodes.json` may hold local hosts/MACs — it stays out of git by design.
- The public SIGSPACE website never ships this code or connects to it; the site's
  DEVICE realm is a **preview** (mock devices) with LIVE off by default.

See `../NOTICE-device-reach.md` for third-party protocol credits and licenses.
