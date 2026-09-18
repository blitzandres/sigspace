from __future__ import annotations

import socket
from urllib.parse import urlparse

import requests

from .base import Device, Driver

SSDP = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 2\r\n"
    "ST: urn:lge-com:service:webos-second-screen:1\r\n"
    "\r\n"
)


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
                id=did,
                name=f"LG webOS {host}",
                kind="tv",
                driver=self.name,
                host=host,
                port=3000,
                can_power_off=True,
                meta={
                    "location": loc,
                    "note": "First power-off may need on-TV pairing approval.",
                },
            )
        return list(found.values())

    def power_off(self, device: Device) -> dict:
        try:
            r = requests.post(
                f"http://{device.host}:3000/ssap://system/turnOff",
                timeout=3,
            )
            return {
                "ok": r.status_code < 400,
                "driver": self.name,
                "status": r.status_code,
                "action": "turnOff",
                "note": "If this fails, open the LG pairing prompt once and retry.",
            }
        except Exception as e:
            return {
                "ok": False,
                "driver": self.name,
                "error": str(e),
                "note": "LG often needs a paired client key for reliable power-off.",
            }

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
