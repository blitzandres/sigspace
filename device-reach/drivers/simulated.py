from __future__ import annotations

from .base import Device, Driver


class SimulatedDriver(Driver):
    name = "simulated"

    def discover(self) -> list[Device]:
        return [
            Device(
                id="sim:living-room-tv",
                name="Living Room TV (sim)",
                kind="tv",
                driver=self.name,
                host="127.0.0.1",
                port=0,
                meta={"demo": True},
            ),
            Device(
                id="sim:bedroom-roku",
                name="Bedroom Roku (sim)",
                kind="tv",
                driver=self.name,
                host="127.0.0.1",
                port=0,
                meta={"demo": True},
            ),
            Device(
                id="sim:soundbar",
                name="Soundbar (sim)",
                kind="media",
                driver=self.name,
                host="127.0.0.1",
                port=0,
                meta={"demo": True},
            ),
        ]

    def power_off(self, device: Device) -> dict:
        return {
            "ok": True,
            "driver": self.name,
            "action": "PowerOff",
            "note": "Simulated. No hardware touched.",
            "id": device.id,
        }
