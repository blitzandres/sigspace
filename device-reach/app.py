#!/usr/bin/env python3
"""device-reach — local device discovery + control for SIGSPACE.

SAFE BY DEFAULT: the server starts DISARMED. While disarmed it shows only the
simulated field and refuses every real action with HTTP 423. Arm it explicitly
(POST /api/arm {"confirm": true}, or start with REACH_ARMED=1) before it will
discover or command real hardware on your LAN. Simulated devices always work so
the UI and the website preview behave the same with nothing connected.
"""

from __future__ import annotations

import os
import threading
time_mod = __import__("time")
from flask import Flask, jsonify, request

from drivers import DRIVERS
from drivers.base import ALL_CAPS

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5070"))
IDLE_SECONDS = int(os.environ.get("IDLE_SECONDS", "3600"))
ALLOW_SIM = os.environ.get("ALLOW_SIM", "1") != "0"

app = Flask(__name__)
_lock = threading.Lock()
_devices: dict = {}
_last_scan = 0.0
_last_hit = time_mod.time()
_armed = os.environ.get("REACH_ARMED", "0") == "1"
_driver_map = {d.name: d for d in DRIVERS}


def touch():
    global _last_hit
    _last_hit = time_mod.time()


def _sim_only() -> list:
    sim = _driver_map.get("simulated")
    return sim.discover() if sim else []


def scan(force: bool = False):
    """Disarmed -> simulated field only (no LAN traffic). Armed -> real discovery."""
    global _devices, _last_scan
    now = time_mod.time()
    with _lock:
        if not force and _devices and now - _last_scan < 20:
            return [d.to_dict() for d in _devices.values()]
        armed = _armed
    if not armed:
        found = _sim_only()
    else:
        found = []
        for drv in DRIVERS:
            if drv.name == "simulated":
                continue
            try:
                found.extend(drv.discover())
            except Exception:
                continue
        if not found and ALLOW_SIM:
            found.extend(_sim_only())
    with _lock:
        _devices = {d.id: d for d in found}
        _last_scan = now
        return [d.to_dict() for d in _devices.values()]


def _get_device(device_id: str):
    with _lock:
        device = _devices.get(device_id)
    if not device:
        scan(force=False)
        with _lock:
            device = _devices.get(device_id)
    return device


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
        "armed": _armed,
        "drivers": [d.name for d in DRIVERS],
        "actions": ALL_CAPS,
        "devices": len(_devices),
    })


@app.route("/api/status")
def status():
    return jsonify({
        "armed": _armed,
        "drivers": [d.name for d in DRIVERS],
        "actions": ALL_CAPS,
        "devices": len(_devices),
        "idle_seconds": IDLE_SECONDS,
        "scanned_at": _last_scan,
    })


@app.route("/api/arm", methods=["POST", "OPTIONS"])
def arm():
    if request.method == "OPTIONS":
        return ("", 204)
    body = request.get_json(silent=True) or {}
    if not body.get("confirm"):
        return jsonify({"ok": False, "error": "confirm:true required to arm real control"}), 400
    global _armed
    _armed = True
    devices = scan(force=True)
    return jsonify({"ok": True, "armed": True, "devices": devices})


@app.route("/api/disarm", methods=["POST", "OPTIONS"])
def disarm():
    if request.method == "OPTIONS":
        return ("", 204)
    global _armed
    _armed = False
    devices = scan(force=True)
    return jsonify({"ok": True, "armed": False, "devices": devices})


@app.route("/api/devices")
def devices():
    return jsonify({"devices": scan(force=False), "armed": _armed, "scanned_at": _last_scan})


@app.route("/api/rescan", methods=["POST", "OPTIONS"])
def rescan():
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify({"devices": scan(force=True), "armed": _armed, "scanned_at": _last_scan})


def _run_action(device_id: str, action: str, params: dict):
    device = _get_device(device_id)
    if not device:
        return {"ok": False, "error": "device not found / not in reach"}, 404
    if not getattr(device, "in_reach", True):
        return {"ok": False, "error": "device not in reach"}, 403
    is_sim = device.driver == "simulated"
    # Real hardware requires the server to be armed. Simulated is always safe.
    if not is_sim and not _armed:
        return {"ok": False, "error": "device-reach is DISARMED — arm it to control real devices",
                "armed": False}, 423
    caps = device.capabilities or []
    if caps and action not in caps:
        return {"ok": False, "error": f"'{action}' not supported by this device",
                "capabilities": caps}, 400
    drv = _driver_map.get(device.driver)
    if not drv:
        return {"ok": False, "error": "unknown driver"}, 400
    result = drv.send_action(device, action, params)
    result.setdefault("id", device.id)
    result.setdefault("name", device.name)
    result["action"] = result.get("action", action)
    return result, (200 if result.get("ok") else 502)


@app.route("/api/action", methods=["POST", "OPTIONS"])
def action():
    if request.method == "OPTIONS":
        return ("", 204)
    body = request.get_json(silent=True) or {}
    device_id = body.get("id") or body.get("device_id")
    act = body.get("action")
    params = body.get("params") or {}
    if not device_id or not act:
        return jsonify({"ok": False, "error": "id and action required"}), 400
    result, code = _run_action(device_id, act, params)
    return jsonify(result), code


@app.route("/api/poweroff", methods=["POST", "OPTIONS"])
def poweroff():
    if request.method == "OPTIONS":
        return ("", 204)
    body = request.get_json(silent=True) or {}
    device_id = body.get("id") or body.get("device_id")
    if not device_id:
        return jsonify({"ok": False, "error": "id required"}), 400
    result, code = _run_action(device_id, "power_off", {})
    return jsonify(result), code


def idle_watch():
    while True:
        time_mod.sleep(15)
        if time_mod.time() - _last_hit > IDLE_SECONDS:
            print(f"device-reach idle {IDLE_SECONDS}s — exiting")
            os._exit(0)


if __name__ == "__main__":
    print(f"device-reach on http://{HOST}:{PORT}/  idle={IDLE_SECONDS}s  armed={_armed}", flush=True)
    if not _armed:
        print("DISARMED: showing simulated field only. POST /api/arm {\"confirm\":true} to control real devices.", flush=True)
    threading.Thread(target=idle_watch, daemon=True).start()
    threading.Thread(target=lambda: scan(force=True), daemon=True).start()
    app.run(host=HOST, port=PORT, threaded=True)
