from functools import lru_cache
from qyro.utils.platform import mac_based, windows_based, linux_based, _get_linux_distribution
from qyro._exceptions import EngineError

FREEZER_MAP = {
    "mac": ("qyro.pipelines.mac", "build_for_mac"),
    "windows": ("qyro.pipelines.windows", "build_for_windows"),
    "ubuntu": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "linuxmint": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "Pop!_os": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "arch": ("qyro.pipelines.arch", "build_for_arch"),
    "fedora": ("qyro.pipelines.fedora", "build_for_fedora"),
    "linux": ("qyro.pipelines.linux", "build_for_linux"),
}

@lru_cache(maxsize=1)
def get_freezer():
    """
    Returns a tuple (os_key, module_name, func_name)
    for the current platform/distro.
    """
    if mac_based():
        return "mac", *FREEZER_MAP["mac"]

    if windows_based():
        return "windows", *FREEZER_MAP["windows"]

    if linux_based():
        distro = _get_linux_distribution()
        if distro in FREEZER_MAP:
            return distro, *FREEZER_MAP[distro]
        return "linux", *FREEZER_MAP["linux"]

    raise EngineError("Unsupported OS")