import os
import sys
from typing import Dict, Any, List
from qyro_engine.utils.platform import mac_based

# Dictionary injected at runtime by a packaging script or PyInstaller hook
BUILD_SETTINGS: Dict[str, Any] = {}

def get_frozen_resource_dirs() -> List[str]:
    """
    Returns a list of paths where the application's resources are located.

    This function adapts the resource path for both development and
    packaged environments (e.g., PyInstaller). On macOS, it looks for the
    'Resources' folder relative to the executable.

    Returns:
        List[str]: A list of absolute paths to resource directories.
    """
    if getattr(sys, 'frozen', False) and mac_based():
        return [os.path.join(sys._MEIPASS, '..', 'Resources')]
    elif getattr(sys, 'frozen', False):
        return [sys._MEIPASS]
    else:
        return [os.path.dirname(os.path.abspath(__file__))]

def load_frozen_build_settings() -> Dict[str, Any]:
    """
    Returns the build configuration loaded at runtime.

    This dictionary is typically populated by a packaging script and contains
    metadata or relevant settings for the application's build.

    Returns:
        Dict[str, Any]: The global BUILD_SETTINGS dictionary.
    """
    return BUILD_SETTINGS
