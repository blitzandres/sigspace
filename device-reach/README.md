# device-reach

Local companion for SIGSPACE: discover TVs and controllable devices on your LAN, then power them off only when they are in reach.

## What it does

- Scans the local network for common smart TVs and cast boxes
- Exposes a tiny Flask API on `http://127.0.0.1:5070`
- SIGSPACE calls this API from the DEVICE realm and the POWER OFF action
- Never talks to public internet hosts for power control

Samsung is prioritized (Andrés). First power-off may show an Allow prompt on the TV.

## Supported drivers (v1)

| Driver | Discover | Power off |
|--------|----------|-----------|
| roku | SSDP + ECP probe | ECP `PowerOff` |
| samsung | SSDP / port 8001 probe | local REST power key when unlocked |
| lg-webos | SSDP | best-effort SSAP power-off (pairing may be required) |
| upnp | SSDP MediaRenderer | UPnP `Stop` / standby when exposed |
| simulated | always | demo only, no hardware |

## Run

```bash
cd device-reach
python3 -m pip install -r requirements.txt
python3 app.py
```

Idle exit matches SIGSPACE: exits after 1 hour with no requests (`IDLE_SECONDS`).

## API

- `GET /` health
- `GET /api/devices` list in-reach devices
- `POST /api/poweroff` JSON `{ "id": "..." }` turn a discovered device off
- `POST /api/rescan` force a fresh LAN scan
