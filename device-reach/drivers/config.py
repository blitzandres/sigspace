"""Shared loader for user-defined reach nodes (http / wol / mqtt).

Config is OPTIONAL. Copy reach_nodes.example.json to reach_nodes.json and edit.
Nothing here reaches the network on import; drivers only act on explicit requests.
"""
from __future__ import annotations

import json
import os

_CACHE: dict | None = None


def load() -> dict:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    path = os.environ.get("REACH_CONFIG") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reach_nodes.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            _CACHE = json.load(fh) or {}
    except Exception:
        _CACHE = {}
    return _CACHE
