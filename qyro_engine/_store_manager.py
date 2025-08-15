import copy
from typing import Any, Tuple

class RuntimeState:
    """
    Manages the global state of the application.

    This class provides a modular and testable way to handle
    application-wide state attributes.
    """
    def __init__(self):
        """
        Initializes the state attributes to None.
        """
        self._platform_name: Any = None
        self._linux_distribution: Any = None
        self._AppEngine: Any = None

    def set_platform_name(self, name: Any) -> None:
        """
        Sets the platform name.
        """
        self._platform_name = name

    def get_platform_name(self) -> Any:
        """
        Gets the platform name.
        """
        return self._platform_name

    def set_linux_distribution(self, distribution: Any) -> None:
        """
        Sets the Linux distribution.
        """
        self._linux_distribution = distribution

    def get_linux_distribution(self) -> Any:
        """
        Gets the Linux distribution.
        """
        return self._linux_distribution

    def set_AppEngine(self, context: Any) -> None:
        """
        Sets the AppEngine.
        """
        self._AppEngine = context

    def get_AppEngine(self) -> Any:
        """
        Gets the AppEngine.
        """
        return self._AppEngine

    def get_state_copy(self) -> Tuple[Any, Any, Any]:
        """
        Returns a deep copy of all state attributes as a tuple.
        """
        return (
            copy.deepcopy(self._platform_name),
            copy.deepcopy(self._linux_distribution),
            copy.deepcopy(self._AppEngine)
        )

    def restore_state(self, platform_name: Any, linux_distribution: Any, AppEngine: Any) -> None:
        """
        Restores the state from provided deep copies.
        """
        self._platform_name = copy.deepcopy(platform_name)
        self._linux_distribution = copy.deepcopy(linux_distribution)
        self._AppEngine = copy.deepcopy(AppEngine)


# Singleton instance for global use
QYRO_RUNTIME_STATE = RuntimeState()