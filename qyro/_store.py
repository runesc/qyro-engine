import collections
import copy
from typing import Dict, List, Tuple


class _Store:
    """
    A class to manage the global state of the project in a modular way.
    """

    def __init__(self):
        self._configuration = {}
        self._loaded_profiles = []
        self._available_commands = collections.OrderedDict()

    def set_config(self, key: str, value: any):
        self._configuration[key] = value

    def get_config(self, key: str, default: any = None) -> any:
        return self._configuration.get(key, default)

    def add_command(self, name: str, command: any):
        self._available_commands[name] = command

    def get_state(self) -> Tuple[Dict, List, Dict]:
        """Returns a deep copy of the current project state."""
        return (
            copy.deepcopy(self._configuration),
            copy.deepcopy(self._loaded_profiles),
            copy.deepcopy(self._available_commands)
        )

    def restore_state(self, configuration: Dict, loaded_profiles: List, commands: Dict):
        """Restores the project state from a previous copy."""
        self._configuration.clear()
        self._configuration.update(configuration)

        self._loaded_profiles.clear()
        self._loaded_profiles.extend(loaded_profiles)

        self._available_commands.clear()
        self._available_commands.update(commands)

    def mount_profile(self, profile_name: str) -> bool:
        """
        Loads a profile by name, updating the configuration and loaded profiles.
        """
        if profile_name not in self._loaded_profiles:
            self._loaded_profiles.append(profile_name)
            return True
        return False

    def umount_profile(self, profile_name: str) -> bool:
        """
        Unloads a profile by name, updating the configuration and loaded profiles.
        """
        if profile_name in self._loaded_profiles:
            self._loaded_profiles.remove(profile_name)
            return True
        return False

    def is_profile_loaded(self, profile_name: str) -> bool:
        """
        Checks if a profile is currently loaded.
        """
        return profile_name in self._loaded_profiles


QYRO_INTERNAL_STATE = _Store()
