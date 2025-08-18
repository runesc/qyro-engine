
from qyro_engine.utils.platform import linux_based, ubuntu_based, arch_based, fedora_based, _get_platform_name
from typing import Dict, Any, List


def get_config_path(working_directory: str) -> Dict[str, str]:
    """
    Receives a working directory and returns a dictionary containing that path.
    """
    return {"project_dir": working_directory}


def generate_core_profiles() -> List[str]:
    """
    Generates a list of base profiles, always including 'base', 'secret', and the platform name.
    If the platform is Linux, it adds a specific profile for the distribution.
    """
    base_profiles = ['base', 'secret', _get_platform_name().lower()]

    if linux_based():
        if ubuntu_based():
            base_profiles.append('ubuntu')
        elif arch_based():
            base_profiles.append('arch')
        elif fedora_based():
            base_profiles.append('fedora')

    return base_profiles


def extract_public_settings(configuration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filters public settings from a settings dictionary, taking only the keys
    listed in settings['public_settings'].
    """
    public_items = configuration_data.get('public_settings', [])
    public_settings = {
        key: value for key, value in configuration_data.items() if key in public_items
    }
    return public_settings
