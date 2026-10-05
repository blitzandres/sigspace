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
    "ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n"
    "\r\n"
)

STOP_SOAP = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>0</InstanceID>
    </u:Stop>
  </s:Body>
</s:Envelope>"""


class UpnpDriver(Driver):
    name = "upnp"

    def discover(self) -> list[Device]:
        found: dict[str, Device] = {}
        for loc in self._ssdp_locations(SSDP, timeout=2.0):
            host = urlparse(loc).hostname
            port = urlparse(loc).port or 1400
            if not host:
                continue
            did = f"upnp:{host}:{port}"
            found[did] = Device(
                id=did,
                name=f"MediaRenderer {host}",
                kind="media",
                driver=self.name,
                host=host,
                port=port,
                meta={"location": loc},
            )
        return list(found.values())

    def power_off(self, device: Device) -> dict:
        loc = (device.meta or {}).get("location")
        if not loc:
            return {"ok": False, "driver": self.name, "error": "missing location"}
        control = loc.rsplit("/", 1)[0] + "/MediaRenderer/AVTransport/Control"
        try:
            r = requests.post(
                control,
                data=STOP_SOAP,
                headers={
                    "Content-Type": 'text/xml; charset="utf-8"',
                    "SOAPACTION": '"urn:schemas-upnp-org:service:AVTransport:1#Stop"',
                },
                timeout=3,
            )
            return {
                "ok": r.status_code < 400,
                "driver": self.name,
                "status": r.status_code,
                "action": "AVTransport.Stop",
                "note": "Stops media. Full power-off depends on the device.",
            }
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
