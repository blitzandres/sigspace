from __future__ import annotations

import socket
from urllib.parse import urlparse

import requests

from .base import Device, Driver

# Read-only LAN visibility: lists every UPnP/SSDP device that answers, even ones
# the control drivers don't recognise. No action capabilities are offered here,
# so these nodes appear on the field but expose no play/stop/power buttons.
SSDP_ALL = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 2\r\n"
    "ST: ssdp:all\r\n"
    "\r\n"
)


class SsdpGenericDriver(Driver):
    name = "ssdp"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP_ALL, timeout=2.4):
            u = urlparse(loc)
            host = u.hostname
            if not host:
                continue
            did = f"ssdp:{host}:{u.port or 0}"
            if did in found:
                continue
            name = self._friendly(loc) or f"UPnP {host}"
            found[did] = Device(
                id=did, name=name, kind="node", driver=self.name,
                host=host, port=u.port or 0, capabilities=[],
                meta={"location": loc, "readonly": True},
            )
        return list(found.values())

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        return {"ok": False, "driver": self.name,
                "error": "read-only node; no control actions"}

    def _friendly(self, loc: str) -> str | None:
        try:
            r = requests.get(loc, timeout=1.5)
            if r.ok and "<friendlyName>" in r.text:
                return r.text.split("<friendlyName>", 1)[1].split("</friendlyName>", 1)[0][:48]
        except Exception:
            return None
        return None

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
