# device-reach — third-party protocol credits

device-reach talks to consumer devices over their documented / community-reverse-
engineered local protocols. No third-party source code is vendored into this repo;
we implement the protocols directly with `requests` / `websocket-client` and credit
the projects whose reverse-engineering work documents them.

| Protocol / idea | Reference project | License | How we use it |
|-----------------|-------------------|---------|---------------|
| Samsung Tizen WebSocket remote (`ms.remote.control`, `SendRemoteKey`, `SendInputString`, token/Allow pairing) | [xchwarze/samsung-tv-ws-api](https://github.com/xchwarze/samsung-tv-ws-api) (≈434★, top result for the Samsung WS API) | LGPL-3.0 | We adopted the documented **message/key format** for `drivers/samsung.py`. We do **not** copy its code; we send the same JSON frames via `websocket-client`. |
| Roku External Control Protocol (ECP: `/keypress/*`, `/launch/*`, `/query/device-info`) | Roku ECP (public spec) / community `python-roku` | MIT (python-roku) / public spec | `drivers/roku.py` posts ECP keypress/launch requests. |
| LG webOS SSAP second-screen URIs | Home Assistant `webostv` / `aiowebostv` ecosystem | Apache-2.0 | `drivers/lg_webos.py` uses SSAP URIs; full control normally needs a paired client key. |
| UPnP AVTransport (Play/Pause/Stop/Next/Previous SOAP) | UPnP Forum AVTransport:1 (public spec) | public spec | `drivers/upnp_av.py` issues standard SOAP actions. |
| Google Cast | [home-assistant/core](https://github.com/home-assistant/core) ecosystem via `pychromecast` | Apache-2.0 / MIT | Optional `drivers/cast.py` uses `pychromecast` if installed. |
| Wake-on-LAN magic packet | public spec (AMD Magic Packet) | public spec | `drivers/wol.py` builds the 6×0xFF + 16×MAC packet. |

Because `samsung-tv-ws-api` is LGPL-3.0, we deliberately kept it as a **reference for
the wire format only** rather than importing it, so this repo carries no LGPL code.
If you prefer, you can `pip install samsung-tv-ws-api` and swap it into
`drivers/samsung.py` under its own license.
