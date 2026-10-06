# Control drivers — can discover AND send actions to real hardware.
from .samsung import SamsungDriver
from .roku import RokuDriver
from .lg_webos import LgWebosDriver
from .cast import CastDriver
from .upnp_av import UpnpDriver
from .http_node import HttpNodeDriver
from .wol import WolDriver
# Passive collectors — observe-only (read-only), always safe even while disarmed.
from .ssdp_generic import SsdpGenericDriver
from .mdns_scan import MdnsDriver
from .ble_scan import BleScanDriver
from .lan_sweep import LanSweepDriver
from .wifi_scan import WifiDriver
from .simulated import SimulatedDriver

CONTROL_DRIVERS = [
    SamsungDriver(), RokuDriver(), LgWebosDriver(), CastDriver(),
    UpnpDriver(), HttpNodeDriver(), WolDriver(),
]
PASSIVE_COLLECTORS = [
    SsdpGenericDriver(), MdnsDriver(), BleScanDriver(), LanSweepDriver(), WifiDriver(),
]
SIM_DRIVER = SimulatedDriver()

# Everything that discovers (control first so merges prefer controllable entries).
SOURCES = CONTROL_DRIVERS + PASSIVE_COLLECTORS
# Full set for name->driver dispatch and the /healthz drivers list.
DRIVERS = SOURCES + [SIM_DRIVER]

__all__ = ["DRIVERS", "SOURCES", "CONTROL_DRIVERS", "PASSIVE_COLLECTORS", "SIM_DRIVER"]
