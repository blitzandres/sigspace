from .samsung import SamsungDriver
from .roku import RokuDriver
from .lg_webos import LgWebosDriver
from .upnp_av import UpnpDriver
from .simulated import SimulatedDriver

DRIVERS = [
    SamsungDriver(),
    RokuDriver(),
    LgWebosDriver(),
    UpnpDriver(),
    SimulatedDriver(),
]

__all__ = ["DRIVERS"]
