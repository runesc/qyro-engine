from .frozen import app_is_frozen
import importlib.util

def module_exists(module_name: str) -> bool:
    """
    Checks if a Python module is available for import.

    Args:
        module_name (str): The name of the module to check.

    Returns:
        bool: True if the module is found, False otherwise.
    """
    module_spec = importlib.util.find_spec(module_name)
    return module_spec is not None