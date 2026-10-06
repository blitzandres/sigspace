from __future__ import annotations

import json
import subprocess
import time

from .base import Device


class WifiDriver:
    """Best-effort Wi-Fi context on macOS. Nearby-AP scanning now needs Location
    permission (and the old `airport -s` is gone on current macOS), so this degrades
    gracefully: it reports the connected network and notes when a full scan is blocked.
    """
    name = "wifi"

    def __init__(self):
        self.last_error = ""

    def discover(self) -> list[Device]:
        self.last_error = ""
        try:
            out = subprocess.run(
                ["system_profiler", "-json", "SPAirPortDataType"],
                capture_output=True, text=True, timeout=8).stdout
            data = json.loads(out or "{}")
        except Exception as e:
            self.last_error = "Wi-Fi info unavailable: " + str(e)[:120]
            return []
        now = time.time()
        devices = []
        nearby_found = False
        try:
            ifaces = data.get("SPAirPortDataType", [])[0].get("spairport_airport_interfaces", [])
        except Exception:
            ifaces = []
        for iface in ifaces:
            cur = iface.get("spairport_current_network_information") or {}
            ssid = cur.get("_name")
            if ssid:
                rssi = None
                sig = cur.get("spairport_signal_noise") or ""
                try:
                    rssi = int(str(sig).split("dBm")[0].strip())
                except Exception:
                    rssi = None
                devices.append(Device(
                    id="wifi:ap:" + ssid, name="Wi-Fi: " + ssid, kind="node", driver=self.name,
                    identifier="ssid:" + ssid, rssi=rssi, last_seen=now, capabilities=[],
                    meta={"icon": "📶", "connected": True,
                          "channel": cur.get("spairport_network_channel", "")},
                ))
            others = iface.get("spairport_airport_other_local_wireless_networks") or []
            for net in others:
                nearby_found = True
                nm = net.get("_name")
                if not nm:
                    continue
                devices.append(Device(
                    id="wifi:ap:" + nm, name="Wi-Fi: " + nm, kind="node", driver=self.name,
                    identifier="ssid:" + nm, last_seen=now, capabilities=[],
                    meta={"icon": "📶", "connected": False,
                          "channel": net.get("spairport_network_channel", "")},
                ))
        if not nearby_found:
            self.last_error = ("Nearby Wi-Fi AP scan is restricted on this macOS "
                               "(needs Location permission); showing connected network only.")
        return devices

    def send_action(self, device, action, params=None):
        return {"ok": False, "driver": self.name, "error": "observe-only (Wi-Fi)"}
