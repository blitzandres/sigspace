from __future__ import annotations

import socket
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, quote

import requests

from .base import (
    Device, Driver,
    CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV,
    CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_LAUNCH,
)

SSDP = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 2\r\n"
    "ST: roku:ecp\r\n"
    "\r\n"
)

# ECP (External Control Protocol) keypress names — Roku's documented remote keys.
KEY_MAP = {
    CAP_PLAY: "Play",        # Play is a toggle on Roku; Pause reuses it
    CAP_PAUSE: "Play",
    CAP_STOP: "Back",
    CAP_NEXT: "Fwd",
    CAP_PREV: "Rev",
    CAP_VOLUME_UP: "VolumeUp",
    CAP_VOLUME_DOWN: "VolumeDown",
    CAP_MUTE: "VolumeMute",
    CAP_POWER_OFF: "PowerOff",
}
CAPS = [CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV,
        CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_LAUNCH]


class RokuDriver(Driver):
    name = "roku"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP, timeout=2.0):
            host = urlparse(loc).hostname
            if not host:
                continue
            info = self._device_info(host)
            if not info:
                continue
            name = info.get("user-device-name") or info.get("model-name") or f"Roku {host}"
            did = f"roku:{host}"
            found[did] = Device(
                id=did, name=name, kind="tv", driver=self.name, host=host, port=8060,
                capabilities=CAPS,
                meta={"model": info.get("model-name"), "serial": info.get("serial-number")},
            )
        return list(found.values())

    def power_off(self, device: Device) -> dict:
        return self.send_action(device, CAP_POWER_OFF)

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        params = params or {}
        try:
            if action == CAP_LAUNCH:
                app = params.get("app")
                if not app:
                    return {"ok": False, "driver": self.name, "error": "launch needs params.app"}
                r = requests.post(f"http://{device.host}:8060/launch/{quote(str(app))}", timeout=3)
                return {"ok": r.status_code in (200, 202, 204), "driver": self.name,
                        "status": r.status_code, "action": "launch", "app": app}
            if action == CAP_KEY:
                key = params.get("key") or "Home"
            else:
                key = KEY_MAP.get(action)
            if not key:
                return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
            r = requests.post(f"http://{device.host}:8060/keypress/{quote(key)}", timeout=3)
            return {"ok": r.status_code in (200, 202, 204), "driver": self.name,
                    "status": r.status_code, "action": action, "key": key}
        except Exception as e:
            return {"ok": False, "driver": self.name, "error": str(e)}

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

    def _device_info(self, host: str) -> dict | None:
        try:
            r = requests.get(f"http://{host}:8060/query/device-info", timeout=2)
            if r.status_code != 200:
                return None
            root = ET.fromstring(r.text)
            return {child.tag: (child.text or "") for child in root}
        except Exception:
            return None
