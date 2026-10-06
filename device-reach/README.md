# device-reach

The REACH brain for SIGSPACE. A local companion that **passively listens on every
frequency your Mac can hear** and surfaces *everything* in range — then lets you
**control** the devices that expose actions (play, pause, stop, volume, mute, launch,
power off/on, send payload).

Runs only on the computer you start it on, binds to `127.0.0.1`, and serves a live
control panel at `/` plus a small JSON API.

## Two layers, one safety model

- **Passive discovery (read-only) is ALWAYS ON — even while disarmed.** Listening and
  scanning never change anything, so the reached list is always rich.
- **Control ACTIONS to real devices require ARM.** `POST /api/arm {"confirm":true}`
  (or start with `REACH_ARMED=1`). Simulated devices are controllable anytime.
- Binds `127.0.0.1` only. Idle-exits after 1h (`IDLE_SECONDS`). Never served on the
  public website — that ships a mock preview (`../preview/device-reach.html`).

## Discovery sources (free, passive)

| Source | Finds | Needs |
|--------|-------|-------|
| **ble** | AirTags / Apple Find-My tags, phones advertising, BLE beacons, headphones, watches — name, UUID, RSSI, manufacturer/company id (Apple `0x004C` → "Apple device / AirTag likely"), service UUIDs | `bleak`; macOS Bluetooth permission (first run) |
| **mdns** | Bonjour services: AirPlay/RAOP, Google Cast, Spotify Connect, HomeKit `_hap`, Continuity `_companion-link`, printers `_ipp`, Sonos, etc. — service type, host, model | `zeroconf` |
| **ssdp** | any UPnP/DLNA device on the LAN (read-only) | — |
| **cast** | Google Cast / Chromecast (also controllable) | optional `pychromecast` |
| **upnp** | UPnP MediaRenderers (controllable) | — |
| **lan** | every LAN host via ping-sweep + `arp` + reverse-DNS + offline OUI vendor lookup — phone, laptop, IoT by IP+MAC+vendor | — |
| **wifi** | connected Wi-Fi network (+ nearby APs when macOS Location allows) | — |
| samsung / roku / lg-webos | smart TVs (controllable) | — |
| simulated | safe demo field (fallback when nothing real is found) | — |

Every reached device carries: `name`, `kind`, `category`, `driver`/`sources`,
`identifier` (MAC/UUID/IP), `rssi`, `vendor`, `capabilities` (empty = observe-only),
`last_seen`. Sources run concurrently in the background; results are merged and
de-duped by identifier/host. Observe-only devices (no actions) still appear as reached.

### OUI vendor table

`data/oui.json` is a compact consumer-electronics subset distilled from the free
Wireshark `manuf` database (no paid API). Drop a fuller `data/oui_extra.json`
(`{PREFIX6: vendor}`) to enrich it. Randomized/private MACs are flagged as such.

## Run locally

```bash
cd device-reach
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py            # http://127.0.0.1:5070/  (DISARMED; passive scan on)
```

Open `http://127.0.0.1:5070/` for the panel. Filter/scroll the reached list, grouped by
**Media & TVs / Phones & Wearables / Tags & Beacons / Network hosts / Other**. To command
a real device, click **ARM REAL CONTROL** (or `curl -X POST .../api/arm -d '{"confirm":true}'`).

> **macOS Bluetooth:** the first BLE scan triggers a system permission dialog for the
> Python running the venv. Approve it (or System Settings → Privacy & Security →
> Bluetooth). Until then `ble` reports a permission note in `/api/status → scan_errors`.
> Nearby Wi-Fi AP scanning needs Location permission on current macOS; without it the
> `wifi` source reports the connected network only.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | live control panel (panel.html) |
| GET | `/healthz` | health + counts |
| GET | `/api/status` | armed, sources, sources_active, actions, counts, categories, **scan_errors**, scanning |
| GET | `/api/devices` | merged reached devices (passive, always populated) |
| POST | `/api/rescan` | kick an immediate background scan |
| POST | `/api/arm` / `/api/disarm` | toggle real-control arming |
| POST | `/api/action` | `{id, action, params}` → act on a controllable device |
| POST | `/api/poweroff` | legacy shortcut for `power_off` |

Actions: `power_off, power_on, play, pause, stop, next, prev, volume_up, volume_down,
mute, key, launch, send`. Observe-only devices reject actions with `400 observe_only`.

## Cyber-security note

Passive listening is read-only and safe. Control actions can turn devices on/off and
push commands on your network, so run on a trusted network only, keep it bound to
`127.0.0.1`, don't expose port 5070 or tunnel it publicly, and disarm/quit when done.
`reach_nodes.json` (custom http/WoL hosts) and scan results are never committed.
See `../NOTICE-device-reach.md` for third-party protocol credits.
