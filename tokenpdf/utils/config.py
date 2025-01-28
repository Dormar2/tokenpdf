from typing import Any, Dict
from pathlib import Path
import json
import toml
import yaml
import configparser
from contextlib import contextmanager

def merge_configs(base: Dict[str, Any], override: Dict[str, Any], *overrides) -> Dict[str, Any]:
    """Merges two or more configuration dictionaries.
    Does not modify the original dictionaries.
    Merge is done recursively for nested dictionaries.
    Lists are NOT merged, the override list replaces the base list.

    Args:
      base: The base configuration dictionary.
      override: The dictionary to merge into the base.
      *overrides: Additional dictionaries to merge.

    Returns:
      : A unified configuration dictionary.

    """
    if overrides:
        return merge_configs(merge_configs(base, override), *overrides)
    merged = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged

def format_supported(path: Path | str) -> bool:
    """
    If the file format is supported for loading configuration files.
    Check is based on file suffix and not content.
    Currently supported: JSON, TOML, YAML, INI (ConfigParser).
    """
    suffix = Path(path).suffix.lower()
    return suffix in [".json", ".toml", ".yaml", ".yml", ".ini", ".cfg"]

def load_any(path: Path | str) -> Dict[str, Any]:
    """Loads a configuration in various formats.
    Supported: JSON, TOML, YAML, INI (ConfigParser).

    Args:
      path: The path to the configuration file.

    Returns:
      : A dictionary of configuration options.

    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    if path.suffix.lower() == ".json":
        with path.open() as f:
            return json.load(f)
    if path.suffix.lower() == ".toml":
        return toml.load(path)
    if path.suffix.lower() in [".yaml", ".yml"]:
        with path.open() as f:
            return yaml.safe_load(f)
    if path.suffix.lower() in [".ini", ".cfg"]:
        parser = configparser.ConfigParser()
        parser.read(path)
        return {s: dict(parser.items(s)) for s in parser.sections()}
    raise ValueError(f"Unsupported configuration file format: {path.suffix}")

def load_with_imports(path: Path | str) -> Dict[str, Any]:
    """Loads a configuration file with support for importing other configuration files.
    Supported file Formats: JSON, TOML, YAML, INI (ConfigParser).
    
    Syntax for importing is one of the following:
    - As a key name, use "@import: <any text>" as key and a file path as the value.
        This will result in merging the imported file into the parent dictionary.
        The <any text> is ignored, and can be used to describe the import.
    - As a value, use any key name, and "@import: <file path>" as the value.
        This will replace the value with the imported file.
    
    References files can be in different formats.
    The paths are assumed relative to the configuration file being loaded, unless they are absolute.
    To use paths relative to cwd, have the path start with "./".
    
    Note: In toml, this can be acheived by using quoted keys, e.g. "@import: this is a description" = "path/to/file.json"

    Args:
      path: Path | str: 

    Returns:

    """
    path = Path(path)

    def get_path(p : Path) -> Path:
        if p.is_absolute():
            return p
        if p.parts[0] == ".":
            return Path.cwd() / p
        return path.parent / p
    
    base = load_any(path)

    def _load_with_imports(current: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively load a configuration dictionary with support for imports.

        """
        if isinstance(current, dict):
            new_dict = {}
            for k,v in current.items():
                if k.startswith("@import:"):
                    if isinstance(v, str):
                        new_dict = merge_configs(new_dict, load_with_imports(get_path(v)))
                    else:
                        raise ValueError(f"Invalid import value: {k}:{v}")
                elif isinstance(v, str) and v.startswith("@import:"):
                    rpath = Path(v.split(":",1)[-1].strip())
                    new_dict[k] = load_with_imports(get_path(rpath))
                else:
                    new_dict[k] = _load_with_imports(v)
            return new_dict
        if isinstance(current, list) or isinstance(current, tuple):
            return [_load_with_imports(v) for v in current]
        return current
    return _load_with_imports(base)
            
                    
def get_data_folder() -> Path:
    """Returns the path to the package data folder."""
    return Path(__file__).parent.parent / "data"

    

@contextmanager
def config_change(cfg, **kw):
    orig_values = {k:cfg.get(k) for k in kw.keys() if k in cfg}
    
    cfg.update(kw)
    yield
    for k in kw:
        if k in orig_values:
            cfg[k] = orig_values[k]
        else:
            del cfg[k]