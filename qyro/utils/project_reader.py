import json
import pathlib
from typing import Any
from . import EngineError


def _read_project_settings() -> dict:
    """
    Reads and validates the 'base.json' file from the project settings.

    Returns:
        dict: The parsed content of base.json.

    Raises:
        EngineError: If the file is not found, cannot be read, or is invalid.
    """
    try:
        settings_path = pathlib.Path('src/build/settings/base.json')
        with settings_path.open('r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise EngineError("Project configuration file 'base.json' not found. "
                          "Are you in the project's root directory?") from None
    except json.JSONDecodeError:
        raise EngineError(
            "Invalid format in 'base.json'. Please check the file for syntax errors.") from None
    except Exception as e:
        raise EngineError(
            f"An unexpected error occurred while reading 'base.json': {e}") from None


def get_project_settings(key: str) -> Any:
    """
    Returns a specific setting from the project's base.json file.

    Args:
        key (str): The setting key to retrieve.

    Returns:
        Any: The value of the setting.

    Raises:
        EngineError: If the key is not found.
    """
    settings = _read_project_settings()
    if key not in settings:
        raise EngineError(f"Setting '{key}' not found in 'base.json'.")
    return settings[key]
