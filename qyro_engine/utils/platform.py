import sys
import platform
import os
from typing import Any

from qyro_engine._store_manager import QYRO_RUNTIME_STATE
from qyro_engine.exceptions import EngineError

def _get_platform_name() -> str:
    """
    Determines and returns the name of the current platform.
    Caches the result in the global state.
    """
    if QYRO_RUNTIME_STATE.get_platform_name() is None:
        try:
            name = sys.platform
            QYRO_RUNTIME_STATE.set_platform_name(name)
        except Exception as e:
            raise EngineError(f"No se pudo determinar la plataforma del sistema: {e}")
    return QYRO_RUNTIME_STATE.get_platform_name()

def _get_linux_distribution() -> Any:
    """
    Determines and returns the name of the Linux distribution.
    Caches the result in the global state.
    """
    if QYRO_RUNTIME_STATE.get_linux_distribution() is None:
        distribution_name = None
        if _get_platform_name() == 'linux':
            try:
                # Use platform.freedesktop_os_release() for a more robust check on newer systems.
                os_info = platform.freedesktop_os_release()
                distribution_name = os_info.get('ID', '').lower()
            except (IOError, FileNotFoundError):
                # Fallback in case of older systems or errors.
                # Note: platform.dist() is deprecated, so we use os-release file if available.
                try:
                    with open('/etc/os-release', 'r') as f:
                        for line in f:
                            if line.startswith('ID='):
                                distribution_name = line.split('=')[1].strip().strip('"').lower()
                                break
                except (IOError, FileNotFoundError):
                    pass # Couldn't determine distribution
        QYRO_RUNTIME_STATE.set_linux_distribution(distribution_name)
    return QYRO_RUNTIME_STATE.get_linux_distribution()

def windows_based() -> bool:
    """
    Checks if the current platform is Windows.
    """
    return _get_platform_name().startswith('win')

def mac_based() -> bool:
    """
    Checks if the current platform is macOS.
    """
    return _get_platform_name() == 'darwin'

def linux_based() -> bool:
    """
    Checks if the current platform is Linux.
    """
    return _get_platform_name() == 'linux'

def ubuntu_based() -> bool:
    """
    Checks if the Linux distribution is Ubuntu or a derivative.
    """
    distribution = _get_linux_distribution()

    # Please only add tested distributions here
    return distribution in ('ubuntu', 'linuxmint', 'Pop!_OS')

def arch_based() -> bool:
    """
    Checks if the Linux distribution is Arch.
    """
    return _get_linux_distribution() == 'arch'

def fedora_based() -> bool:
    """
    Checks if the Linux distribution is Fedora.
    """
    return _get_linux_distribution() == 'fedora'

def gnome_based() -> bool:
    """
    Checks if the desktop environment is GNOME-based.
    
    This is a simplified check based on environment variables.
    """
    return 'gnome' in os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

def kde_based() -> bool:
    """
    Checks if the desktop environment is KDE-based.
    
    This is a simplified check based on environment variables.
    """
    return 'kde' in os.environ.get('XDG_CURRENT_DESKTOP', '').lower()