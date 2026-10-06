from __future__ import annotations

import time

from .base import Device

try:
    from zeroconf import Zeroconf, ServiceBrowser
except Exception:  # pragma: no cover
    Zeroconf = None
    ServiceBrowser = None

TYPES = [
    "_airplay._tcp.local.", "_raop._tcp.local.", "_googlecast._tcp.local.",
    "_spotify-connect._tcp.local.", "_hap._tcp.local.", "_homekit._tcp.local.",
    "_companion-link._tcp.local.", "_apple-mobdev2._tcp.local.",
    "_ipp._tcp.local.", "_ipps._tcp.local.", "_printer._tcp.local.", "_pdl-datastream._tcp.local.",
    "_sonos._tcp.local.", "_sleep-proxy._udp.local.",
    "_device-info._tcp.local.", "_smb._tcp.local.", "_ssh._tcp.local.",
    "_http._tcp.local.", "_amzn-wplay._tcp.local.",
    "_mediaremotetv._tcp.local.", "_touch-able._tcp.local.",
]

# service base -> (kind, icon), in priority order (first match wins for a host)
PRIORITY = [
    ("googlecast", "media", "🎬"), ("amzn-wplay", "media", "📺"),
    ("mediaremotetv", "media", "📺"), ("airplay", "media", "📺"),
    ("sonos", "media", "🔊"), ("raop", "speaker", "🔊"), ("spotify-connect", "media", "🎵"),
    ("companion-link", "phone", "📱"), ("apple-mobdev2", "phone", "📱"), ("touch-able", "phone", "📱"),
    ("hap", "node", "🏠"), ("homekit", "node", "🏠"),
    ("ipps", "printer", "🖨️"), ("ipp", "printer", "🖨️"), ("printer", "printer", "🖨️"), ("pdl-datastream", "printer", "🖨️"),
    ("smb", "host", "🖥️"), ("ssh", "host", "🖥️"), ("sleep-proxy", "host", "🖥️"),
]
COMPUTER_HINT = ("macbook", "imac", "mac mini", "mac-mini", "air", "mbp", "pc", "laptop", "desktop", "nas")
PHONE_HINT = ("iphone", "ipad", "android", "pixel", "galaxy", "phone")


class _Listener:
    def __init__(self, zc):
        self.zc = zc
        self.items = {}

    def _store(self, type_, name):
        try:
            info = self.zc.get_service_info(type_, name, timeout=1500)
        except Exception:
            info = None
        if info:
            self.items[(type_, name)] = info

    def add_service(self, zc, type_, name):
        self._store(type_, name)

    def update_service(self, zc, type_, name):
        self._store(type_, name)

    def remove_service(self, zc, type_, name):
        pass


class MdnsDriver:
    name = "mdns"

    def __init__(self):
        self.last_error = ""

    def _classify(self, name, services):
        n = (name or "").lower()
        if any(h in n for h in PHONE_HINT):
            return "phone", "📱"
        if any(h in n for h in COMPUTER_HINT):
            return "host", "🖥️"
        for base, kind, icon in PRIORITY:
            if base in services:
                return kind, icon
        return "node", "📡"

    def discover(self) -> list[Device]:
        self.last_error = ""
        if Zeroconf is None:
            self.last_error = "zeroconf not installed"
            return []
        zc = None
        try:
            zc = Zeroconf()
            listener = _Listener(zc)
            _ = [ServiceBrowser(zc, t, listener) for t in TYPES]
            time.sleep(4.5)
        except Exception as e:
            self.last_error = str(e)[:200]
            if zc:
                try: zc.close()
                except Exception: pass
            return []
        now = time.time()
        hosts: dict = {}
        for (type_, name), info in listener.items.items():
            base = type_.split(".")[0].lstrip("_")
            addrs = []
            try:
                addrs = [a for a in info.parsed_addresses() if ":" not in a]
            except Exception:
                pass
            host = addrs[0] if addrs else (info.server or "").rstrip(".")
            if not host:
                continue
            props = {}
            try:
                for k, v in (info.properties or {}).items():
                    try:
                        props[k.decode()] = v.decode() if isinstance(v, bytes) else v
                    except Exception:
                        pass
            except Exception:
                pass
            friendly = props.get("fn") or props.get("n") or (info.server or name).split(".")[0].replace("-", " ")
            model = props.get("md") or props.get("model") or props.get("am") or ""
            h = hosts.setdefault(host, {"services": set(), "name": friendly, "model": model})
            h["services"].add(base)
            if model and not h["model"]:
                h["model"] = model
            # prefer a human friendly name over a bare hostname
            if friendly and (len(friendly) > len(h["name"]) or " " in friendly):
                h["name"] = friendly
        out = []
        for host, h in hosts.items():
            services = h["services"]
            kind, icon = self._classify(h["name"], services)
            out.append(Device(
                id="mdns:" + host, name=h["name"] or host, kind=kind, driver=self.name,
                host=host, identifier=host, last_seen=now, capabilities=[],
                meta={"icon": icon, "services": sorted(services), "model": h["model"]},
            ))
        try:
            zc.close()
        except Exception:
            pass
        return out

    def send_action(self, device, action, params=None):
        return {"ok": False, "driver": self.name, "error": "observe-only (mDNS)"}
