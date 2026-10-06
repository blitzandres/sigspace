from .samsung import SamsungDriver
from .roku import RokuDriver
from .lg_webos import LgWebosDriver
from .upnp_av import UpnpDriver
from .cast import CastDriver
from .http_node import HttpNodeDriver
from .wol import WolDriver
from .ssdp_generic import SsdpGenericDriver
from .simulated import SimulatedDriver

# Order matters only for display; app.py keeps a name->driver map for dispatch.
DRIVERS = [
    SamsungDriver(),      # Samsung Tizen TVs (prioritised for Andrés)
    RokuDriver(),         # Roku TVs / players (ECP)
    LgWebosDriver(),      # LG webOS TVs (SSAP)
    CastDriver(),         # Google Cast (optional: pychromecast)
    UpnpDriver(),         # UPnP/DLNA media renderers (AVTransport)
    HttpNodeDriver(),     # user-defined generic HTTP control nodes
    WolDriver(),          # Wake-on-LAN power-on nodes
    SsdpGenericDriver(),  # read-only visibility of any UPnP device
    SimulatedDriver(),    # safe demo field (always available)
]

__all__ = ["DRIVERS"]
