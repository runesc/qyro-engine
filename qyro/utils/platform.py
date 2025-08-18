import sys
import platform
import os
from typing import Any
from functools import lru_cache

class EngineError(Exception):
    pass


@lru_cache(maxsize=1)
def _get_platform_name() -> str:
    """
    Determines and returns the name of the current platform.
    Caches automatically using lru_cache.
    """
    try:
        return sys.platform
    except Exception as e:
        raise EngineError(f"Failed to determine platform name: {e}") from e


@lru_cache(maxsize=1)
def _get_linux_distribution() -> Any:
    """
    Determines and returns the name of the Linux distribution.
    Caches automatically using lru_cache.
    """
    if _get_platform_name() == "linux":
        try:
            os_info = platform.freedesktop_os_release()
            return os_info.get("ID", "").lower()
        except (IOError, FileNotFoundError):
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"').lower()
            except (IOError, FileNotFoundError):
                return None
    return None


def windows_based() -> bool:
    return _get_platform_name().startswith("win")


def mac_based() -> bool:
    return _get_platform_name() == "darwin"


def linux_based() -> bool:
    return _get_platform_name() == "linux"


def ubuntu_based() -> bool:
    distribution = _get_linux_distribution()
    return distribution in ("ubuntu", "linuxmint", "Pop!_os")


def arch_based() -> bool:
    return _get_linux_distribution() == "arch"


def fedora_based() -> bool:
    return _get_linux_distribution() == "fedora"


def gnome_based() -> bool:
    return "gnome" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()


def kde_based() -> bool:
    return "kde" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
