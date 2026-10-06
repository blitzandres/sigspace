#!/usr/bin/env python3
"""Standalone BLE scan worker. Run as a subprocess so macOS CoreBluetooth runs on
this process's main thread and the Bluetooth permission binds to this python
executable. Prints one JSON line: {"error": "...", "devices": [...]}.
"""
import asyncio
import json
import sys


async def _scan(timeout):
    from bleak import BleakScanner
    return await BleakScanner.discover(timeout=timeout, return_adv=True)


async def main():
    timeout = float(sys.argv[1]) if len(sys.argv) > 1 else 7.0
    try:
        import bleak  # noqa: F401
    except Exception as e:
        print(json.dumps({"error": "bleak not installed: " + str(e), "devices": []}))
        return
    try:
        results = await asyncio.wait_for(_scan(timeout), timeout=timeout + 4)
    except asyncio.TimeoutError:
        print(json.dumps({"error": ("Bluetooth authorization required — the scan never "
              "started (CoreBluetooth stayed unauthorized). Approve the Bluetooth prompt "
              "for this app, or enable it in System Settings > Privacy & Security > "
              "Bluetooth."), "devices": []}))
        return
    except Exception as e:
        print(json.dumps({"error": str(e), "devices": []}))
        return
    out = []
    for addr, pair in results.items():
        try:
            bd, adv = pair
        except Exception:
            bd, adv = pair, None
        name, rssi, mfg, services = "", None, {}, []
        if adv is not None:
            name = (adv.local_name or getattr(bd, "name", "") or "")
            rssi = adv.rssi
            mfg = adv.manufacturer_data or {}
            services = list(adv.service_uuids or [])
        else:
            name = getattr(bd, "name", "") or ""
        out.append({
            "address": str(addr),
            "name": (name or "").strip(),
            "rssi": rssi,
            "company_ids": [int(k) for k in mfg.keys()],
            "services": [str(s) for s in services],
        })
    print(json.dumps({"error": "", "devices": out}))


asyncio.run(main())
