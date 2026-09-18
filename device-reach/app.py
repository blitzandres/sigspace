#!/usr/bin/env python3
"""device-reach — local TV/device discovery + power-off for SIGSPACE."""

from __future__ import annotations

import os
import threading
time_mod = __import__("time")
from flask import Flask, jsonify, request

from drivers import DRIVERS

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5070"))
IDLE_SECONDS = int(os.environ.get("IDLE_SECONDS", "3600"))
ALLOW_SIM = os.environ.get("ALLOW_SIM", "1") != "0"

app = Flask(__name__)
_lock = threading.Lock()
_devices = {}
_last_scan = 0.0
_last_hit = time_mod.time()
_driver_map = {d.name: d for d in DRIVERS}


def touch():
    global _last_hit
    _last_hit = time_mod.time()


def scan(force: bool = False):
    global _devices, _last_scan
    now = time_mod.time()
    with _lock:
        if not force and _devices and now - _last_scan < 20:
            return [d.to_dict() for d in _devices.values()]
        found = []
        for drv in DRIVERS:
            if drv.name == "simulated":
                continue
            try:
                found.extend(drv.discover())
            except Exception:
                continue
        if not found and ALLOW_SIM:
            found.extend(_driver_map["simulated"].discover())
        _devices = {d.id: d for d in found}
        _last_scan = now
        return [d.to_dict() for d in _devices.values()]


@app.after_request
def cors(resp):
    touch()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "service": "device-reach",
        "drivers": [d.name for d in DRIVERS],
        "devices": len(_devices),
    })


@app.route("/api/devices")
def devices():
    return jsonify({"devices": scan(force=False), "scanned_at": _last_scan})


@app.route("/api/rescan", methods=["POST", "OPTIONS"])
def rescan():
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify({"devices": scan(force=True), "scanned_at": _last_scan})


@app.route("/api/poweroff", methods=["POST", "OPTIONS"])
def poweroff():
    if request.method == "OPTIONS":
        return ("", 204)
    body = request.get_json(silent=True) or {}
    device_id = body.get("id") or body.get("device_id")
    if not device_id:
        return jsonify({"ok": False, "error": "id required"}), 400
    scan(force=False)
    with _lock:
        device = _devices.get(device_id)
    if not device:
        return jsonify({"ok": False, "error": "device not found / not in reach"}), 404
    if not getattr(device, "in_reach", True):
        return jsonify({"ok": False, "error": "device not in reach"}), 403
    if not getattr(device, "can_power_off", True):
        return jsonify({"ok": False, "error": "power-off not supported"}), 400
    drv = _driver_map.get(device.driver)
    if not drv:
        return jsonify({"ok": False, "error": "unknown driver"}), 400
    result = drv.power_off(device)
    result["id"] = device.id
    result["name"] = device.name
    return jsonify(result), (200 if result.get("ok") else 502)


def idle_watch():
    while True:
        time_mod.sleep(15)
        if time_mod.time() - _last_hit > IDLE_SECONDS:
            print(f"device-reach idle {IDLE_SECONDS}s — exiting")
            os._exit(0)


if __name__ == "__main__":
    import sys
    print(f"device-reach on http://{HOST}:{PORT}/  idle={IDLE_SECONDS}s", flush=True)
    threading.Thread(target=idle_watch, daemon=True).start()
    threading.Thread(target=lambda: scan(force=True), daemon=True).start()
    app.run(host=HOST, port=PORT, threaded=True)
