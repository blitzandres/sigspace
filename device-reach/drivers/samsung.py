from __future__ import annotations

import base64
import json
import socket
from urllib.parse import urlparse

import requests

from .base import Device, Driver

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


class SamsungDriver(Driver):
    name = "samsung"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP, timeout=2.2):
            host = urlparse(loc).hostname
            if not host:
                continue
            self._add(found, host, loc)
        # light local probe of common LAN prefixes when SSDP is quiet
        if not found:
            for host in self._guess_hosts():
                if self._alive(host):
                    self._add(found, host, None)
        return list(found.values())

    def _add(self, found: dict, host: str, loc: str | None):
        name = self._name(host) or f"Samsung TV {host}"
        did = f"samsung:{host}"
        found[did] = Device(
            id=did,
            name=name,
            kind="tv",
            driver=self.name,
            host=host,
            port=8001,
            meta={"location": loc, "brand": "Samsung"},
        )

    def power_off(self, device: Device) -> dict:
        # Prefer websocket remote control (works on many Tizen sets after one-time Allow).
        ws_result = self._ws_power(device.host)
        if ws_result.get("ok"):
            return ws_result
        # REST fallbacks
        attempts = [
            ("POST", f"http://{device.host}:8001/api/v2/channels/samsung.remote.control", {
                "method": "ms.remote.control",
                "params": {
                    "Cmd": "Click",
                    "DataOfCmd": "KEY_POWER",
                    "Option": "false",
                    "TypeOfRemote": "SendRemoteKey",
                },
            }),
            ("PUT", f"http://{device.host}:8001/api/v2/", {"power": False}),
        ]
        last_err = ws_result.get("error")
        for method, url, body in attempts:
            try:
                r = requests.request(method, url, json=body, timeout=3)
                if r.status_code < 500:
                    return {
                        "ok": r.status_code < 400,
                        "driver": self.name,
                        "status": r.status_code,
                        "action": "KEY_POWER",
                        "note": "Accept the Allow prompt on the TV the first time.",
                        "ws": ws_result,
                    }
            except Exception as e:
                last_err = str(e)
        return {
            "ok": False,
            "driver": self.name,
            "error": last_err or "no endpoint accepted",
            "note": "On the TV: Settings → General → External Device Manager → Device Connect Manager → allow SIGSPACE.",
        }

    def _ws_power(self, host: str) -> dict:
        if websocket is None:
            return {"ok": False, "error": "websocket-client not installed"}
        paths = [
            f"ws://{host}:8001/api/v2/channels/samsung.remote.control?name={APP_NAME_B64}",
            f"wss://{host}:8002/api/v2/channels/samsung.remote.control?name={APP_NAME_B64}",
        ]
        payload = {
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Click",
                "DataOfCmd": "KEY_POWER",
                "Option": "false",
                "TypeOfRemote": "SendRemoteKey",
            },
        }
        last = None
        for url in paths:
            try:
                ws = websocket.create_connection(url, timeout=4, sslopt={"cert_reqs": 0})
                try:
                    # read greeting if any
                    try:
                        ws.settimeout(1.5)
                        ws.recv()
                    except Exception:
                        pass
                    ws.send(json.dumps(payload))
                    try:
                        reply = ws.recv()
                    except Exception:
                        reply = ""
                    return {
                        "ok": True,
                        "driver": self.name,
                        "action": "KEY_POWER",
                        "transport": "websocket",
                        "url": url.split("?")[0],
                        "reply": (reply or "")[:200],
                        "note": "Accept Allow on the TV once if prompted.",
                    }
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
            r = requests.get(f"http://{host}:8001/api/v2/", timeout=0.6)
            return r.status_code < 500
        except Exception:
            return False

    def _guess_hosts(self) -> list[str]:
        # Probe .1/.2 gateway neighborhoods from local interfaces when possible.
        hosts: list[str] = []
        try:
            hostname = socket.gethostname()
            local = socket.gethostbyname(hostname)
            if local and not local.startswith("127."):
                prefix = ".".join(local.split(".")[:3])
                # small window around common DHCP leases
                for i in list(range(2, 30)) + list(range(100, 120)):
                    hosts.append(f"{prefix}.{i}")
        except Exception:
            pass
        return hosts[:40]

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
