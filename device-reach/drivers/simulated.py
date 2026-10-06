from __future__ import annotations

from .base import (
    Device, Driver,
    CAP_POWER_OFF, CAP_POWER_ON, CAP_PLAY, CAP_PAUSE, CAP_STOP,
    CAP_NEXT, CAP_PREV, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE,
    CAP_KEY, CAP_LAUNCH, CAP_SEND,
)

# In-memory playback/power/volume state so the demo buttons feel real.
_STATE: dict[str, dict] = {}


def _st(dev_id: str) -> dict:
    return _STATE.setdefault(dev_id, {"power": "on", "playback": "idle", "volume": 22, "muted": False})


class SimulatedDriver(Driver):
    """No hardware is ever touched. Used for the safe default field and the website preview."""
    name = "simulated"

    def discover(self) -> list[Device]:
        specs = [
            ("sim:living-room-tv", "Living Room TV", "tv",
             [CAP_POWER_OFF, CAP_POWER_ON, CAP_PLAY, CAP_PAUSE, CAP_STOP,
              CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_LAUNCH]),
            ("sim:bedroom-roku", "Bedroom Roku", "tv",
             [CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV,
              CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE, CAP_KEY, CAP_LAUNCH]),
            ("sim:soundbar", "Soundbar", "media",
             [CAP_POWER_OFF, CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE]),
            ("sim:office-cast", "Office Cast", "media",
             [CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_NEXT, CAP_PREV, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_SEND]),
            ("sim:desk-lamp-node", "Desk Lamp Node", "node",
             [CAP_POWER_OFF, CAP_POWER_ON, CAP_SEND]),
            ("sim:lab-host", "Lab Host", "host",
             [CAP_POWER_ON, CAP_SEND]),
        ]
        out = []
        for did, name, kind, caps in specs:
            st = _st(did)
            out.append(Device(
                id=did, name=f"{name} (sim)", kind=kind, driver=self.name,
                host="127.0.0.1", port=0, capabilities=caps, state=dict(st),
                meta={"demo": True, "rssi": -42 - (len(did) % 30)},
            ))
        return out

    def power_off(self, device: Device) -> dict:
        return self.send_action(device, CAP_POWER_OFF)

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        params = params or {}
        st = _st(device.id)
        note = "Simulated. No hardware touched."
        if action == CAP_POWER_OFF:
            st["power"] = "off"; st["playback"] = "idle"
        elif action == CAP_POWER_ON:
            st["power"] = "on"
        elif action == CAP_PLAY:
            st["playback"] = "playing"
        elif action == CAP_PAUSE:
            st["playback"] = "paused"
        elif action == CAP_STOP:
            st["playback"] = "idle"
        elif action in (CAP_NEXT, CAP_PREV):
            st["playback"] = "playing"
        elif action == CAP_VOLUME_UP:
            st["volume"] = min(100, st.get("volume", 22) + 3)
        elif action == CAP_VOLUME_DOWN:
            st["volume"] = max(0, st.get("volume", 22) - 3)
        elif action == CAP_MUTE:
            st["muted"] = not st.get("muted", False)
        elif action in (CAP_KEY, CAP_LAUNCH, CAP_SEND):
            note = f"Simulated {action}: {params or '(no params)'}. No hardware touched."
        else:
            return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
        return {"ok": True, "driver": self.name, "action": action, "state": dict(st), "note": note}
