from __future__ import annotations

import socket
from urllib.parse import urlparse

import requests

from .base import (
    Device, Driver,
    CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP,
    CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE,
)

SSDP = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 2\r\n"
    "ST: urn:lge-com:service:webos-second-screen:1\r\n"
    "\r\n"
)

# webOS SSAP URIs (reverse-engineered second-screen protocol).
SSAP = {
    CAP_POWER_OFF: "ssap://system/turnOff",
    CAP_PLAY: "ssap://media.controls/play",
    CAP_PAUSE: "ssap://media.controls/pause",
    CAP_STOP: "ssap://media.controls/stop",
    CAP_VOLUME_UP: "ssap://audio/volumeUp",
    CAP_VOLUME_DOWN: "ssap://audio/volumeDown",
    CAP_MUTE: "ssap://audio/setMute",
}
CAPS = [CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP,
        CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE]
PAIR_NOTE = "First action may need on-TV pairing approval; LG often needs a paired client key."


class LgWebosDriver(Driver):
    name = "lg-webos"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP, timeout=2.0):
            host = urlparse(loc).hostname
            if not host:
                continue
            did = f"lg:{host}"
            found[did] = Device(
                id=did, name=f"LG webOS {host}", kind="tv", driver=self.name,
                host=host, port=3000, capabilities=CAPS,
                meta={"location": loc, "note": PAIR_NOTE},
            )
        return list(found.values())

    def power_off(self, device: Device) -> dict:
        return self.send_action(device, CAP_POWER_OFF)

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        uri = SSAP.get(action)
        if not uri:
            return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
        try:
            r = requests.post(f"http://{device.host}:3000/{uri}", timeout=3)
            return {"ok": r.status_code < 400, "driver": self.name, "status": r.status_code,
                    "action": action, "note": PAIR_NOTE}
        except Exception as e:
            return {"ok": False, "driver": self.name, "error": str(e), "note": PAIR_NOTE}

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
