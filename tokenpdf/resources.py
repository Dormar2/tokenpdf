import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import requests
import mimetypes
from tokenpdf.utils.config import merge_configs
from tokenpdf.utils.verbose import vprint, vtqdm
import pypdl

class ResourceLoader:
    """
    A class responsible for loading resources, including configuration files.
    """

    def __init__(self):
        self._local_files = []

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Loads a single configuration file in JSON, YAML, or TOML format.

        :param file_path: The path to the configuration file.
        :return: A dictionary representing the configuration.
        :raises ValueError: If the file format is unsupported.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        ext = path.suffix.lower()
        with open(file_path, "r", encoding="utf-8") as f:
            if ext == ".json":
                return json.load(f)
            elif ext in {".yaml", ".yml"}:
                return yaml.safe_load(f)
            elif ext == ".toml":
                return toml.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")

    def load_configs(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Loads multiple configuration files and unifies them.

        :param file_paths: A list of paths to the configuration files.
        :return: A unified dictionary representing the combined configuration.
        """
        unified_config = {}
        for file_path in file_paths:
            single_config = self.load_config(file_path)
            unified_config = merge_configs(unified_config, single_config)
        
        return unified_config

    def load_resources(self, config:Dict[str,Any], verbose=None) -> Dict[str, Any]:
        """
        Load resources specified in the configuration.
        :param config: The configuration dictionary.
        :return: A dictionary of loaded resources.
                Structure is similar to configuration,
                except that paths are replaced with loaded resources.
        """
        if verbose == None:
            verbose = config.get("verbose", False)
        resources = {}
        for key, value in config.items():
            if isinstance(value, dict):
                inner = self.load_resources(value, verbose)
                if inner is not None:
                    resources[key] = inner
            if isinstance(value, list) or isinstance(value, tuple):
                reslist = []
                for item in value:
                    inner = self.load_resources(item, verbose)
                    reslist.append(inner if inner is not None else {})
                if any(reslist):
                    resources[key] = reslist
            elif key == 'url' or key.endswith('_url'):
                resources[key] = self.load_resource(value, verbose)
        return resources

    def load_resource(self, url: str, verbose=False) -> str:
        """
        Saves a local copy of the resource and returns the path.
        :param url: The URL of the resource.
        :return: The local path to the resource.
        """
        # Download the resource from the URL
        print = vprint(verbose)
        print(f"Downloading resource from {url}")
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        self._local_files.append(temp_file.name)
        res = _download(url, temp_file.name, allow_rename=True)
        print(f"Resource saved to {res}")
        return res

    def cleanup(self):
        """
        Cleans up temporary files created during resource loading.
        """
        for file_path in self._local_files:
            if Path(file_path).is_file():
                Path(file_path).unlink()



def _download(url: str, file_path: str, allow_rename: bool = True) -> Path:
    """
    Downloads a file from a URL to a local path.

    :param url: The URL of the file to download.
    :param file_path: The local path to save the downloaded file.
    """
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.HTTPError(f"Failed to download file from {url} - {response.status_code}")
    if allow_rename:
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type, strict=False)
        if extension:
            path = path.with_suffix(extension)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

            





