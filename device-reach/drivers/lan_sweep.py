from __future__ import annotations

import ipaddress
import re
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from .base import Device
from . import oui

ARP_RE = re.compile(r"\(([\d.]+)\)\s+at\s+([0-9a-fA-F:]+)")
COMPUTER_HINT = ("macbook", "imac", "mac-mini", "macmini", "mac mini", "-air", "-mbp", "mbp",
                 "pc", "laptop", "desktop", "openwrt", "router", "gateway", "nas", "synology")
PHONE_HINT = ("iphone", "android", "pixel", "galaxy", "oneplus", "phone")


def _pad_mac(mac: str) -> str:
    parts = mac.split(":")
    if len(parts) == 6:
        try:
            return ":".join(f"{int(p, 16):02X}" for p in parts)
        except ValueError:
            return mac.upper()
    return mac.upper()


def _is_mcast_mac(mac: str) -> bool:
    first = mac.split(":")[0]
    try:
        return bool(int(first, 16) & 0x01)  # multicast/broadcast LSB of first octet
    except ValueError:
        return False


def _classify(name: str, is_gw: bool):
    n = (name or "").lower()
    if any(h in n for h in PHONE_HINT):
        return "phone", "📱"
    if is_gw:
        return "host", "🌐"
    if any(h in n for h in COMPUTER_HINT):
        return "host", "🖥️"
    return "host", "🖥️"


class LanSweepDriver:
    name = "lan"

    def __init__(self):
        self.last_error = ""

    def _subnets(self) -> list[str]:
        nets = set()
        try:
            out = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=4).stdout
        except Exception:
            out = ""
        for m in re.finditer(r"inet (\d+\.\d+\.\d+\.\d+) netmask (0x[0-9a-fA-F]+)", out):
            ip, mask = m.group(1), m.group(2)
            if ip.startswith("127."):
                continue
            try:
                if int(mask, 16) >= 0xFFFFFF00:
                    nets.add(".".join(ip.split(".")[:3]))
            except Exception:
                continue
        if not nets:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]; s.close()
                if not ip.startswith("127."):
                    nets.add(".".join(ip.split(".")[:3]))
            except Exception:
                pass
        return list(nets)

    def _ping(self, ip: str):
        try:
            subprocess.run(["ping", "-c", "1", "-t", "1", ip], capture_output=True, timeout=2)
        except Exception:
            pass

    def discover(self) -> list[Device]:
        self.last_error = ""
        subnets = self._subnets()
        if not subnets:
            self.last_error = "no local IPv4 subnet detected"
            return []
        targets = []
        for base in subnets:
            targets += [f"{base}.{i}" for i in range(1, 255)]
        try:
            with ThreadPoolExecutor(max_workers=96) as ex:
                list(ex.map(self._ping, targets, timeout=9))
        except Exception:
            pass
        try:
            arp = subprocess.run(["arp", "-a", "-n"], capture_output=True, text=True, timeout=5).stdout
        except Exception as e:
            self.last_error = "arp failed: " + str(e)
            arp = ""
        now = time.time()
        seen = {}
        socket.setdefaulttimeout(0.4)
        for line in arp.splitlines():
            m = ARP_RE.search(line)
            if not m or "incomplete" in line.lower():
                continue
            ip, mac = m.group(1), m.group(2)
            # drop multicast / broadcast noise
            if ip.endswith(".255"):
                continue
            try:
                ipa = ipaddress.ip_address(ip)
                if ipa.is_multicast or ipa.is_reserved or ipa.is_unspecified:
                    continue
            except ValueError:
                continue
            if _is_mcast_mac(mac):
                continue
            mac_n = _pad_mac(mac)
            if mac_n in seen:
                continue
            vendor = oui.vendor_for(mac_n)
            host = ""
            try:
                host = socket.gethostbyaddr(ip)[0].split(".")[0]
            except Exception:
                host = ""
            is_gw = ip.split(".")[-1] in ("1", "254")
            nm = host or ((vendor + " device") if vendor and vendor != "(randomized MAC)" else None) \
                 or ("Gateway " + ip if is_gw else "Host " + ip)
            kind, icon = _classify(host or nm, is_gw)
            seen[mac_n] = Device(
                id="lan:" + mac_n, name=nm, kind=kind, driver=self.name,
                host=ip, identifier=mac_n, vendor=vendor, last_seen=now, capabilities=[],
                meta={"icon": icon, "mac": mac_n, "gateway": is_gw, "hostname": host},
            )
        return list(seen.values())

    def send_action(self, device, action, params=None):
        return {"ok": False, "driver": self.name, "error": "observe-only (LAN host)"}
