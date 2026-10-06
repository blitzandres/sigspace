#!/usr/bin/env python3
"""device-reach — full-capacity passive discovery + local control for SIGSPACE.

REACH is the brain: it listens on every passive source macOS allows (BLE, mDNS/
Bonjour, SSDP/UPnP, Google Cast, LAN ping+ARP sweep, Wi-Fi) and surfaces EVERYTHING
in range — even devices with no controllable actions, which appear as observe-only
"reached" nodes.

SAFE BY DEFAULT:
- Passive discovery is READ-ONLY and always runs, even while DISARMED.
- Sending a control ACTION to a real device requires ARM (POST /api/arm {"confirm":true}).
- Binds to 127.0.0.1 only. Idle-exits after 1h with no requests.
"""

from __future__ import annotations

import os
import threading
import time as time_mod
from concurrent.futures import ThreadPoolExecutor, wait

from flask import Flask, jsonify, request

from drivers import DRIVERS, SOURCES, SIM_DRIVER
from drivers.base import ALL_CAPS, category_for

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5070"))
IDLE_SECONDS = int(os.environ.get("IDLE_SECONDS", "3600"))
ALLOW_SIM = os.environ.get("ALLOW_SIM", "1") != "0"
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "45"))
SCAN_TIMEOUT = int(os.environ.get("SCAN_TIMEOUT", "24"))

app = Flask(__name__)
_lock = threading.Lock()
_scan_lock = threading.Lock()
_by_id: dict = {}
_snapshot: list = []
_scan_errors: dict = {}
_sources_active: list = []
_last_scan = 0.0
_last_hit = time_mod.time()
_armed = os.environ.get("REACH_ARMED", "0") == "1"
_driver_map = {d.name: d for d in DRIVERS}

_GENERIC_PREFIX = ("Host ", "BLE ", "Gateway ", "MediaRenderer ", "UPnP ", "Wi-Fi: ")


def touch():
    global _last_hit
    _last_hit = time_mod.time()


# ---------------- merge / de-dupe ----------------

def _generic(name: str, host: str = "") -> bool:
    if not name:
        return True
    if host and name == host:
        return True
    return name.startswith(_GENERIC_PREFIX)


def _combine(a, b):
    if b.driver not in a.sources:
        a.sources.append(b.driver)
    # prefer a more specific kind (media/phone/tag) over generic host/node
    _RANK = {"tv": 5, "media": 5, "speaker": 5, "phone": 5, "wearable": 5,
             "headphones": 5, "tag": 5, "beacon": 4, "printer": 4,
             "host": 2, "node": 2, "unknown": 1}
    if not a.capabilities and _RANK.get(b.kind, 0) > _RANK.get(a.kind, 0):
        a.kind = b.kind
        if (b.meta or {}).get("icon"):
            a.meta = a.meta or {}
            a.meta["icon"] = b.meta["icon"]
    if not a.capabilities and b.capabilities:
        a.capabilities = list(b.capabilities)
        a.driver = b.driver
        a.id = b.id
        a.state = b.state or a.state
        a.kind = b.kind or a.kind
        if (b.meta or {}).get("icon"):
            (a.meta or {}).setdefault("icon", b.meta["icon"])
    elif b.capabilities:
        for c in b.capabilities:
            if c not in a.capabilities:
                a.capabilities.append(c)
    if a.rssi is None and b.rssi is not None:
        a.rssi = b.rssi
    if not a.vendor and b.vendor:
        a.vendor = b.vendor
    if not a.identifier and b.identifier:
        a.identifier = b.identifier
    if not a.host and b.host:
        a.host = b.host
    if _generic(a.name, a.host) and not _generic(b.name, b.host):
        a.name = b.name
    am, bm = (a.meta or {}), (b.meta or {})
    for k, v in bm.items():
        if k == "services" and isinstance(v, list):
            cur = am.setdefault("services", [])
            for s in v:
                if s not in cur:
                    cur.append(s)
        else:
            am.setdefault(k, v)
    a.meta = am
    a.last_seen = max(a.last_seen or 0, b.last_seen or 0)


def _merge(devices: list) -> list:
    result, index = [], {}
    for d in devices:
        keys = []
        if d.identifier:
            keys.append("k:" + d.identifier.upper())
        if d.host:
            keys.append("h:" + d.host)
        hit = None
        for k in keys:
            if k in index:
                hit = index[k]
                break
        if hit is None:
            if not d.sources:
                d.sources = [d.driver]
            result.append(d)
            for k in keys:
                index[k] = d
        else:
            _combine(hit, d)
            for k in keys:
                index.setdefault(k, hit)
    return result


# ---------------- scanning ----------------

def _collect_one(src):
    try:
        devs = src.discover()
        return src.name, devs, (getattr(src, "last_error", "") or "")
    except Exception as e:
        return src.name, [], str(e)[:200]


def run_scan():
    """Run every source concurrently, merge, and publish a fresh snapshot."""
    global _by_id, _snapshot, _scan_errors, _sources_active, _last_scan
    if not _scan_lock.acquire(blocking=False):
        return False
    try:
        ex = ThreadPoolExecutor(max_workers=max(1, len(SOURCES)))
        futs = {ex.submit(_collect_one, s): s for s in SOURCES}
        done, notdone = wait(futs, timeout=SCAN_TIMEOUT)
        all_devs, errors, active = [], {}, []
        for f in done:
            nm, devs, err = f.result()
            if devs:
                active.append(nm)
            if err:
                errors[nm] = err
            all_devs.extend(devs)
        for f in notdone:
            errors[futs[f].name] = "timed out (>%ss)" % SCAN_TIMEOUT
        ex.shutdown(wait=False, cancel_futures=True)

        merged = _merge(all_devs)
        now = time_mod.time()
        for d in merged:
            if not d.last_seen:
                d.last_seen = now
        if not merged and ALLOW_SIM:
            merged = SIM_DRIVER.discover()
            for d in merged:
                d.last_seen = now
                if not d.sources:
                    d.sources = [d.driver]
        snap = [d.to_dict() for d in merged]
        with _lock:
            _by_id = {d.id: d for d in merged}
            _snapshot = snap
            _scan_errors = errors
            _sources_active = active
            _last_scan = now
        return True
    finally:
        _scan_lock.release()


def _kick_scan():
    if not _scan_lock.locked():
        threading.Thread(target=run_scan, daemon=True).start()


def refresher():
    run_scan()
    while True:
        time_mod.sleep(REFRESH_SECONDS)
        if time_mod.time() - _last_hit <= IDLE_SECONDS:
            run_scan()


def _counts():
    cats, controllable = {}, 0
    for d in _snapshot:
        cats[d.get("category", "Other")] = cats.get(d.get("category", "Other"), 0) + 1
        if d.get("capabilities"):
            controllable += 1
    return cats, controllable


# ---------------- HTTP ----------------

@app.after_request
def cors(resp):
    touch()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


@app.route("/")
def panel():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panel.html")
    try:
        with open(p, encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception:
        return jsonify({"status": "ok", "service": "device-reach", "note": "panel.html missing"}), 200


@app.route("/healthz")
def health():
    cats, controllable = _counts()
    return jsonify({
        "status": "ok", "service": "device-reach", "armed": _armed,
        "drivers": [d.name for d in DRIVERS], "actions": ALL_CAPS,
        "devices": len(_snapshot), "controllable": controllable,
        "sources_active": _sources_active, "categories": cats,
    })


@app.route("/api/status")
def status():
    cats, controllable = _counts()
    return jsonify({
        "armed": _armed,
        "drivers": [d.name for d in DRIVERS],
        "sources": [s.name for s in SOURCES],
        "sources_active": _sources_active,
        "actions": ALL_CAPS,
        "devices": len(_snapshot),
        "controllable": controllable,
        "categories": cats,
        "scan_errors": _scan_errors,
        "scanning": _scan_lock.locked(),
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
    return jsonify({"ok": True, "armed": True, "devices": _snapshot})


@app.route("/api/disarm", methods=["POST", "OPTIONS"])
def disarm():
    if request.method == "OPTIONS":
        return ("", 204)
    global _armed
    _armed = False
    return jsonify({"ok": True, "armed": False, "devices": _snapshot})


@app.route("/api/devices")
def devices():
    if time_mod.time() - _last_scan > REFRESH_SECONDS:
        _kick_scan()
    return jsonify({"devices": _snapshot, "armed": _armed, "scanning": _scan_lock.locked(),
                    "sources_active": _sources_active, "scan_errors": _scan_errors,
                    "scanned_at": _last_scan})


@app.route("/api/rescan", methods=["POST", "OPTIONS"])
def rescan():
    if request.method == "OPTIONS":
        return ("", 204)
    _kick_scan()
    return jsonify({"devices": _snapshot, "armed": _armed, "scanning": True,
                    "scanned_at": _last_scan})


def _run_action(device_id: str, action: str, params: dict):
    with _lock:
        device = _by_id.get(device_id)
    if not device:
        return {"ok": False, "error": "device not found / not in reach"}, 404
    if not getattr(device, "in_reach", True):
        return {"ok": False, "error": "device not in reach"}, 403
    caps = device.capabilities or []
    if not caps:
        return {"ok": False, "error": "observe-only device — no control actions",
                "observe_only": True}, 400
    is_sim = device.driver == "simulated"
    if not is_sim and not _armed:
        return {"ok": False, "error": "device-reach is DISARMED — arm it to control real devices",
                "armed": False}, 423
    if action not in caps:
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
    print("Passive discovery is always on (read-only). Control actions require ARM.", flush=True)
    threading.Thread(target=idle_watch, daemon=True).start()
    threading.Thread(target=refresher, daemon=True).start()
    app.run(host=HOST, port=PORT, threaded=True)
