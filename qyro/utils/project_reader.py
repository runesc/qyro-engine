import json
import pathlib
from qyro.store import QYRO_INTERNAL_STATE
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


def get_project_settings(key: str= None) -> dict:
    """
    Returns a specific setting from the project's base.json file.

    Args:
        key (str): The setting key to retrieve.

    Returns:
        Any: The value of the setting.

    Raises:
        EngineError: If the key is not found.
    """
    if key is None:
        return _read_project_settings()

    settings = _read_project_settings()
    if key not in settings:
        raise EngineError(f"Setting '{key}' not found in 'base.json'.")
    return settings[key]

def _find_and_store_settings():
    """
    Finds the project settings file and stores its content and project path
    in the global state.
    """
    current = pathlib.Path.cwd()
    project_dir = None

    while current != current.parent:
        potential_file = current / "src" / "build" / "settings" / "base.json"
        if potential_file.exists():
            project_dir = current
            break
        current = current.parent

    if not project_dir:
        raise EngineError("Cannot determine project directory. Make sure you ran 'init' first.")

    try:
        with open(project_dir / "src" / "build" / "settings" / "base.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            for k, v in config.items():
                QYRO_INTERNAL_STATE.set_config(k, v)

        QYRO_INTERNAL_STATE.set_config("project_dir", str(project_dir))

    except (IOError, json.JSONDecodeError) as e:
        raise EngineError(f"Failed to load project settings: {e}") from e


def _validate_project_structure():
    """
    Verifies that the project directory and its 'src' folder exist.

    Returns:
        pathlib.Path: The path to the project's root directory.
    """
    project_dir = QYRO_INTERNAL_STATE.get_config("project_dir")
    if not project_dir:
        raise EngineError("Project directory is not set. Run 'init' first.")

    src_path = pathlib.Path(project_dir) / "src"
    if not src_path.exists():
        raise EngineError(
            f"Could not find the 'src/' directory in: [bold]{project_dir}[/bold]"
        )
    return project_dir
