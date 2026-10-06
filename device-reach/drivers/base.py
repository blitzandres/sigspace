from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

# Canonical capability / action identifiers shared by every driver and the UI.
CAP_POWER_OFF = "power_off"
CAP_POWER_ON = "power_on"     # Wake-on-LAN / network wake
CAP_PLAY = "play"
CAP_PAUSE = "pause"
CAP_STOP = "stop"
CAP_NEXT = "next"
CAP_PREV = "prev"
CAP_VOLUME_UP = "volume_up"
CAP_VOLUME_DOWN = "volume_down"
CAP_MUTE = "mute"
CAP_KEY = "key"       # send a named remote key, params: {"key": "KEY_HOME"}
CAP_LAUNCH = "launch" # launch an app, params: {"app": "<id>"}
CAP_SEND = "send"     # send an arbitrary payload/text to the node, params: {"payload": ...}

ALL_CAPS = [
    CAP_POWER_OFF, CAP_POWER_ON, CAP_PLAY, CAP_PAUSE, CAP_STOP,
    CAP_NEXT, CAP_PREV, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE,
    CAP_KEY, CAP_LAUNCH, CAP_SEND,
]


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
    capabilities: list[str] = field(default_factory=list)
    state: dict | None = None          # e.g. {"power": "on", "playback": "idle", "volume": 20}
    meta: dict | None = None

    # Back-compat: older UI reads can_power_off directly.
    @property
    def can_power_off(self) -> bool:
        return CAP_POWER_OFF in (self.capabilities or [])

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["meta"] = d.get("meta") or {}
        d["state"] = d.get("state") or {}
        d["capabilities"] = d.get("capabilities") or []
        d["can_power_off"] = self.can_power_off
        return d


class Driver:
    name = "base"

    def discover(self) -> list[Device]:
        return []

    # Preferred entry point. action is one of the CAP_* strings.
    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict[str, Any]:
        params = params or {}
        if action == CAP_POWER_OFF:
            return self.power_off(device)
        return {"ok": False, "error": f"action '{action}' not implemented", "driver": self.name}

    # Kept for back-compat with the original /api/poweroff path.
    def power_off(self, device: Device) -> dict[str, Any]:
        return {"ok": False, "error": "not implemented", "driver": self.name}
