from __future__ import annotations

import requests

from .base import Device, Driver, CAP_SEND
from . import config

# A fully generic, user-defined control node. You describe each device and the
# HTTP request behind each button in reach_nodes.json; nothing is hardcoded and
# nothing is discovered automatically, so this only reaches hosts you listed.


class HttpNodeDriver(Driver):
    name = "http"

    def discover(self) -> list[Device]:
        out = []
        for n in config.load().get("http_nodes", []) or []:
            try:
                acts = list((n.get("actions") or {}).keys())
                out.append(Device(
                    id=f"http:{n['id']}", name=n.get("name") or n["id"],
                    kind=n.get("kind", "node"), driver=self.name,
                    host=n.get("host", ""), port=int(n.get("port", 0) or 0),
                    capabilities=acts, meta={"config": n},
                ))
            except Exception:
                continue
        return out

    def power_off(self, device: Device) -> dict:
        return self.send_action(device, "power_off")

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        params = params or {}
        cfg = (device.meta or {}).get("config") or {}
        spec = (cfg.get("actions") or {}).get(action)
        if not spec:
            return {"ok": False, "driver": self.name, "error": f"action '{action}' not configured"}
        method = (spec.get("method") or "POST").upper()
        base = spec.get("url") or f"http://{device.host}:{device.port or 80}{spec.get('path', '/')}"
        kwargs: dict = {"timeout": 4}
        headers = dict(spec.get("headers") or {})
        if spec.get("body_from_payload"):
            kwargs["json"] = params.get("payload")
        elif spec.get("json") is not None:
            kwargs["json"] = spec["json"]
        elif spec.get("body") is not None:
            kwargs["data"] = spec["body"]
        if headers:
            kwargs["headers"] = headers
        try:
            r = requests.request(method, base, **kwargs)
            return {"ok": r.status_code < 400, "driver": self.name, "status": r.status_code,
                    "action": action, "url": base}
        except Exception as e:
            return {"ok": False, "driver": self.name, "error": str(e), "action": action}
