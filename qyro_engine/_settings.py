import json
from pathlib import Path
from typing import Any, Union, List, Dict

def load_json_configs(paths: List[Union[str, Path]], defaults: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Load multiple JSON files, merge their contents, and expand placeholders.
    """
    merged_settings = dict(defaults) if defaults else {}

    for path in paths:
        path_obj = Path(path)
        if not path_obj.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged_settings = deep_combine(merged_settings, data)

    # Recursively expand placeholders
    merged_settings = resolve_placeholders(merged_settings, merged_settings)
    return merged_settings


def resolve_placeholders(obj: Any, context: Dict[str, Any]) -> Any:
    """
    Replace placeholders like ${key} in strings, lists, and dictionaries.
    """
    if isinstance(obj, str):
        for k, v in context.items():
            obj = obj.replace(f"${{{k}}}", str(v))
        return obj
    elif isinstance(obj, list):
        return [resolve_placeholders(item, context) for item in obj]
    elif isinstance(obj, dict):
        return {key: resolve_placeholders(val, context) for key, val in obj.items()}
    return obj


def deep_combine(source: Any, override: Any) -> Any:
    """
    Recursively merge two data structures (dict or list).
    """
    if type(source) != type(override):
        raise TypeError(f"Cannot merge {type(source).__name__} with {type(override).__name__}")

    if isinstance(source, list):
        return source + override

    if isinstance(source, dict):
        combined = dict(source)
        for key, val in override.items():
            combined[key] = deep_combine(source[key], val) if key in source else val
        return combined

    # For primitive types, override the source value
    return override
