from typing import Any, Dict

def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges two configuration dictionaries.

    :param base: The base configuration dictionary.
    :param override: The overriding configuration dictionary.
    :return: A unified configuration dictionary.
    """
    merged = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged