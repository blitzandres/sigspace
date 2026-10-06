"""Offline MAC-prefix -> vendor lookup. No network, no paid API.

data/oui.json is a compact consumer-electronics subset distilled from the free
Wireshark 'manuf' database. You can drop a fuller manuf/oui file next to it later
(data/oui_extra.json, same {PREFIX6: vendor} shape) to enrich the table.
"""
from __future__ import annotations

import json
import os

_TABLE: dict | None = None


def _load() -> dict:
    global _TABLE
    if _TABLE is not None:
        return _TABLE
    t: dict = {}
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    for fn in ("oui.json", "oui_extra.json"):
        p = os.path.join(base, fn)
        try:
            with open(p, encoding="utf-8") as fh:
                t.update({k.upper(): v for k, v in json.load(fh).items()})
        except Exception:
            pass
    _TABLE = t
    return t


def _norm(mac: str) -> str:
    return "".join(c for c in (mac or "") if c in "0123456789abcdefABCDEF").upper()


def is_random(mac: str) -> bool:
    """True for locally-administered / randomized MACs (privacy addresses)."""
    h = _norm(mac)
    if len(h) < 2:
        return False
    try:
        second = int(h[1], 16)
    except ValueError:
        return False
    return bool(second & 0x2)  # locally-administered bit


def vendor_for(mac: str) -> str:
    h = _norm(mac)
    if len(h) < 6:
        return ""
    v = _load().get(h[:6], "")
    if v:
        return v
    if is_random(mac):
        return "(randomized MAC)"
    return ""
