from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Device:
    id: str
    name: str
    kind: str
    driver: str
    host: str
    port: int
    reachable: bool = True
    in_reach: bool = True
    can_power_off: bool = True
    meta: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["meta"] = d.get("meta") or {}
        return d


class Driver:
    name = "base"

    def discover(self) -> list[Device]:
        return []

    def power_off(self, device: Device) -> dict[str, Any]:
        return {"ok": False, "error": "not implemented", "driver": self.name}
