from __future__ import annotations

import base64
import json
import socket
from urllib.parse import urlparse

import requests

from .base import (
    Device, Driver,
    CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV,
    CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_SEND,
)

try:
    import websocket  # websocket-client
except Exception:  # pragma: no cover
    websocket = None

SSDP = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 2\r\n"
    "ST: urn:samsung.com:device:RemoteControlReceiver:1\r\n"
    "\r\n"
)

APP_NAME_B64 = base64.b64encode(b"SIGSPACE").decode()

# Samsung Tizen remote key names (reverse-engineered WS protocol; see samsung-tv-ws-api).
KEY_MAP = {
    CAP_POWER_OFF: "KEY_POWER",
    CAP_PLAY: "KEY_PLAY",
    CAP_PAUSE: "KEY_PAUSE",
    CAP_STOP: "KEY_STOP",
    CAP_NEXT: "KEY_FF",
    CAP_PREV: "KEY_REWIND",
    CAP_VOLUME_UP: "KEY_VOLUP",
    CAP_VOLUME_DOWN: "KEY_VOLDOWN",
    CAP_MUTE: "KEY_MUTE",
}
CAPS = [CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV,
        CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_SEND]

ALLOW_NOTE = ("On the TV: Settings → General → External Device Manager → "
              "Device Connect Manager → allow SIGSPACE.")


class SamsungDriver(Driver):
    name = "samsung"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP, timeout=2.2):
            host = urlparse(loc).hostname
            if not host:
                continue
            self._add(found, host, loc)
        if not found:
            for host in self._guess_hosts():
                if self._alive(host):
                    self._add(found, host, None)
        return list(found.values())

    def _add(self, found: dict, host: str, loc: str | None):
        name = self._name(host) or f"Samsung TV {host}"
        did = f"samsung:{host}"
        found[did] = Device(
            id=did, name=name, kind="tv", driver=self.name, host=host, port=8001,
            capabilities=CAPS, meta={"location": loc, "brand": "Samsung"},
        )

    def power_off(self, device: Device) -> dict:
        return self.send_action(device, CAP_POWER_OFF)

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        params = params or {}
        if action == CAP_SEND:
            text = str(params.get("payload") or params.get("text") or "")
            if not text:
                return {"ok": False, "driver": self.name, "error": "send needs params.payload"}
            return self._ws_text(device.host, text)
        key = params.get("key") if action == CAP_KEY else KEY_MAP.get(action)
        if not key:
            return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
        return self._send_key(device.host, key, action)

    def _send_key(self, host: str, key: str, action: str) -> dict:
        ws_result = self._ws_cmd(host, {
            "method": "ms.remote.control",
            "params": {"Cmd": "Click", "DataOfCmd": key,
                       "Option": "false", "TypeOfRemote": "SendRemoteKey"},
        })
        if ws_result.get("ok"):
            ws_result["action"] = action
            ws_result["key"] = key
            return ws_result
        # REST fallback (older sets).
        try:
            r = requests.post(
                f"http://{host}:8001/api/v2/channels/samsung.remote.control",
                json={"method": "ms.remote.control",
                      "params": {"Cmd": "Click", "DataOfCmd": key,
                                 "Option": "false", "TypeOfRemote": "SendRemoteKey"}},
                timeout=3)
            if r.status_code < 500:
                return {"ok": r.status_code < 400, "driver": self.name, "status": r.status_code,
                        "action": action, "key": key, "note": ALLOW_NOTE, "ws": ws_result}
        except Exception as e:
            ws_result.setdefault("error", str(e))
        return {"ok": False, "driver": self.name, "action": action, "key": key,
                "error": ws_result.get("error") or "no endpoint accepted", "note": ALLOW_NOTE}

    def _ws_text(self, host: str, text: str) -> dict:
        b64 = base64.b64encode(text.encode()).decode()
        res = self._ws_cmd(host, {
            "method": "ms.remote.control",
            "params": {"Cmd": b64, "TypeOfRemote": "SendInputString",
                       "DataOfCmd": "base64"},
        })
        res["action"] = CAP_SEND
        res["note"] = res.get("note") or "Text sent to the focused on-screen field."
        return res

    def _ws_cmd(self, host: str, payload: dict) -> dict:
        if websocket is None:
            return {"ok": False, "driver": self.name, "error": "websocket-client not installed"}
        paths = [
            f"ws://{host}:8001/api/v2/channels/samsung.remote.control?name={APP_NAME_B64}",
            f"wss://{host}:8002/api/v2/channels/samsung.remote.control?name={APP_NAME_B64}",
        ]
        last = None
        for url in paths:
            try:
                ws = websocket.create_connection(url, timeout=4, sslopt={"cert_reqs": 0})
                try:
                    try:
                        ws.settimeout(1.5); ws.recv()
                    except Exception:
                        pass
                    ws.send(json.dumps(payload))
                    try:
                        reply = ws.recv()
                    except Exception:
                        reply = ""
                    return {"ok": True, "driver": self.name, "transport": "websocket",
                            "url": url.split("?")[0], "reply": (reply or "")[:200],
                            "note": "Accept Allow on the TV once if prompted."}
                finally:
                    ws.close()
            except Exception as e:
                last = str(e)
        return {"ok": False, "driver": self.name, "error": last or "ws failed"}

    def _name(self, host: str) -> str | None:
        try:
            r = requests.get(f"http://{host}:8001/api/v2/", timeout=2)
            if r.ok:
                data = r.json()
                return (data.get("device") or {}).get("name") or data.get("name")
        except Exception:
            return None
        return None

    def _alive(self, host: str) -> bool:
        try:
            r = requests.get(f"http://{host}:8001/api/v2/", timeout=0.25)
            return r.status_code < 500
        except Exception:
            return False

    def _guess_hosts(self) -> list[str]:
        hosts: list[str] = []
        try:
            local = socket.gethostbyname(socket.gethostname())
            if local and not local.startswith("127."):
                prefix = ".".join(local.split(".")[:3])
                for i in list(range(2, 30)) + list(range(100, 120)):
                    hosts.append(f"{prefix}.{i}")
        except Exception:
            pass
        return hosts[:12]

    def _ssdp_locations(self, payload: str, timeout: float = 2.0) -> list[str]:
        locs: set[str] = set()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        try:
            sock.sendto(payload.encode(), ("239.255.255.250", 1900))
            while True:
                try:
                    data, _ = sock.recvfrom(65535)
                except socket.timeout:
                    break
                text = data.decode(errors="ignore")
                for line in text.split("\r\n"):
                    if line.lower().startswith("location:"):
                        locs.add(line.split(":", 1)[1].strip())
        finally:
            sock.close()
        return list(locs)
