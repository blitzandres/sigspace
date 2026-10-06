from __future__ import annotations

import socket

from .base import Device, Driver, CAP_POWER_ON
from . import config

# Wake-on-LAN: broadcasts a magic packet to a MAC you listed in config.
# This is the "power ON" counterpart to the TV power-off drivers.


def _magic(mac: str) -> bytes:
    clean = mac.replace(":", "").replace("-", "").replace(".", "").strip()
    raw = bytes.fromhex(clean)
    return b"\xff" * 6 + raw * 16


class WolDriver(Driver):
    name = "wol"

    def discover(self) -> list[Device]:
        out = []
        for n in config.load().get("wol_nodes", []) or []:
            try:
                out.append(Device(
                    id=f"wol:{n['id']}", name=n.get("name") or n["id"],
                    kind=n.get("kind", "host"), driver=self.name,
                    host=n.get("broadcast", "255.255.255.255"),
                    port=int(n.get("port", 9)), capabilities=[CAP_POWER_ON],
                    meta={"mac": n.get("mac"), "config": n},
                ))
            except Exception:
                continue
        return out

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        if action != CAP_POWER_ON:
            return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
        mac = (device.meta or {}).get("mac")
        if not mac:
            return {"ok": False, "driver": self.name, "error": "node has no mac"}
        try:
            pkt = _magic(mac)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(pkt, (device.host or "255.255.255.255", device.port or 9))
            s.close()
            return {"ok": True, "driver": self.name, "action": CAP_POWER_ON, "mac": mac,
                    "note": "Magic packet sent."}
        except Exception as e:
            return {"ok": False, "driver": self.name, "error": str(e)}
