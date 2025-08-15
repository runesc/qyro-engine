import collections
import copy
from typing import Dict, List, Tuple


class ProjectState:
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

    def get_state_copy(self) -> Tuple[Dict, List, Dict]:
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


QYRO_INTERNAL_STATE = ProjectState()
