from __future__ import annotations

from .base import (
    Device, Driver,
    CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE,
)

# Google Cast (Chromecast / Cast-enabled TVs & speakers).
# Optional: needs `pip install pychromecast`. If it isn't installed, the driver
# simply discovers nothing and never errors, so the rest of device-reach is fine.
try:
    import pychromecast  # type: ignore
except Exception:  # pragma: no cover
    pychromecast = None

CAPS = [CAP_PLAY, CAP_PAUSE, CAP_STOP, CAP_VOLUME_UP, CAP_VOLUME_DOWN, CAP_MUTE]


class CastDriver(Driver):
    name = "cast"

    def __init__(self):
        self._by_id: dict[str, object] = {}

    def discover(self) -> list[Device]:
        if pychromecast is None:
            return []
        out = []
        try:
            casts, browser = pychromecast.get_chromecasts(timeout=4)
            for cc in casts:
                try:
                    info = cc.cast_info
                    did = f"cast:{info.uuid}"
                    self._by_id[did] = cc
                    out.append(Device(
                        id=did, name=info.friendly_name or "Cast device",
                        kind="media", driver=self.name,
                        host=str(info.host), port=int(info.port or 8009),
                        capabilities=CAPS, meta={"model": info.model_name},
                    ))
                except Exception:
                    continue
            try:
                pychromecast.discovery.stop_discovery(browser)
            except Exception:
                pass
        except Exception:
            return []
        return out

    def send_action(self, device: Device, action: str, params: dict | None = None) -> dict:
        cc = self._by_id.get(device.id)
        if cc is None or pychromecast is None:
            return {"ok": False, "driver": self.name, "error": "cast device not connected"}
        try:
            cc.wait(timeout=4)
            mc = cc.media_controller
            if action == CAP_PLAY:
                mc.play()
            elif action == CAP_PAUSE:
                mc.pause()
            elif action == CAP_STOP:
                mc.stop()
            elif action == CAP_VOLUME_UP:
                cc.volume_up()
            elif action == CAP_VOLUME_DOWN:
                cc.volume_down()
            elif action == CAP_MUTE:
                cc.set_volume_muted(True)
            else:
                return {"ok": False, "driver": self.name, "error": f"unsupported action '{action}'"}
            return {"ok": True, "driver": self.name, "action": action}
        except Exception as e:
            return {"ok": False, "driver": self.name, "error": str(e)}
