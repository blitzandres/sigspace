from __future__ import annotations

import json
import os
import subprocess
import sys
import time

from .base import Device

APPLE_COMPANY_ID = 0x004C
COMPANY_VENDORS = {
    0x004C: "Apple", 0x0006: "Microsoft", 0x00E0: "Google", 0x0075: "Samsung",
    0x0171: "Amazon", 0x0157: "Huawei", 0x038F: "Xiaomi", 0x004F: "Garmin",
    0x0087: "Garmin", 0x00D2: "Bose", 0x02D0: "Sony", 0x0A12: "Bose",
}


def _classify(name: str, has_apple: bool):
    n = (name or "").lower()
    if any(x in n for x in ["airpod", "buds", "headphone", "wh-", "wf-", "beats", "soundcore", "jabra"]):
        return "headphones", "🎧"
    if any(x in n for x in ["watch", "band", "fit", "garmin", "whoop"]):
        return "wearable", "⌚"
    if any(x in n for x in ["iphone", "phone", "pixel", "galaxy", "oneplus"]):
        return "phone", "📱"
    if any(x in n for x in ["tv", "roku", "chromecast", "appletv", "bravia", "shield"]):
        return "media", "📺"
    if any(x in n for x in ["airtag", "tag", "tile", "smarttag"]):
        return "tag", "🏷️"
    if has_apple and not name:
        return "tag", "🏷️"      # nameless Apple advertiser → AirTag / Find My likely
    if not name:
        return "beacon", "📡"
    return "unknown", "📶"


class BleScanDriver:
    name = "ble"

    def __init__(self):
        self.last_error = ""

    def discover(self) -> list[Device]:
        self.last_error = ""
        worker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ble_worker.py")
        try:
            proc = subprocess.run(
                [sys.executable, worker, "7.0"],
                capture_output=True, text=True, timeout=14)
        except subprocess.TimeoutExpired:
            self.last_error = "BLE scan timed out"
            return []
        except Exception as e:
            self.last_error = str(e)
            return []
        raw = (proc.stdout or "").strip().splitlines()
        data = None
        for line in reversed(raw):
            try:
                data = json.loads(line); break
            except Exception:
                continue
        if data is None:
            self.last_error = (proc.stderr or "no BLE output").strip()[:200]
            return []
        if data.get("error"):
            self.last_error = self._friendly(data["error"])
            # may still include partial devices
        now = time.time()
        out = []
        for d in data.get("devices", []):
            cids = d.get("company_ids") or []
            has_apple = APPLE_COMPANY_ID in cids
            name = d.get("name") or ""
            kind, icon = _classify(name, has_apple)
            vendor = ""
            for cid in cids:
                if cid in COMPANY_VENDORS:
                    vendor = COMPANY_VENDORS[cid]; break
            label = name or ("Apple device (AirTag / Find My likely)" if has_apple else "BLE " + d["address"][:8])
            out.append(Device(
                id="ble:" + d["address"], name=label, kind=kind, driver=self.name,
                identifier=d["address"], rssi=d.get("rssi"), vendor=vendor, last_seen=now,
                capabilities=[],
                meta={"icon": icon, "services": d.get("services") or [],
                      "company_ids": [hex(c) for c in cids], "apple": has_apple},
            ))
        return out

    def _friendly(self, msg: str) -> str:
        m = (msg or "").lower()
        if any(k in m for k in ["unauthoriz", "not authorized", "denied", "nsbluetooth", "cbmanagerstateunauthorized"]):
            return ("Bluetooth permission needed: approve the system dialog for this Python, "
                    "or enable it in System Settings → Privacy & Security → Bluetooth. (" + msg[:120] + ")")
        if "poweredoff" in m or "turned off" in m or "powered off" in m:
            return "Bluetooth is turned OFF — enable Bluetooth to scan BLE."
        return msg[:200]

    def send_action(self, device, action, params=None):
        return {"ok": False, "driver": self.name, "error": "observe-only (BLE)"}
