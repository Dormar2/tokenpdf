from pathlib import Path
from typing import Dict, Any, List
import tempfile
import requests
import mimetypes
import numpy as np
from tokenpdf.utils.config import merge_configs
from tokenpdf.utils.verbose import vprint, vtqdm
from tokenpdf.systems import registry as system_registry
import tokenpdf.utils.config as config

class ResourceLoader:
    """
    A class responsible for loading resources, including configuration files.
    """

    def __init__(self):
        self._local_files = []
        self._cfg = None
        self._resources = {}
        self._systems = system_registry

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Loads a single configuration file in JSON, YAML, or TOML format.

        :param file_path: The path to the configuration file.
        :return: A dictionary representing the configuration.
        :raises ValueError: If the file format is unsupported
        :raises FileNotFoundError: If the file does not exist
        """
        c = config.load_with_imports(file_path)
        self._cfg = c
        return c

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
        if file_paths:
            unified_config["__config_files"] = file_paths
        self._cfg = unified_config
        return unified_config
    
    def generate_tokens(self, config: Dict[str, Any] = None, verbose=None) -> Dict[str, Any]:
        """
        Generates token specifications based on the configuration.
        :param config: The configuration dictionary.
        :return: A dictionary of generated tokens.
        """
        config = config if config is not None else self._cfg
        if config is None:
            return []
        if verbose == None:
            verbose = config.get("verbose", False)
        seed = config.get("seed", None)
        rng = np.random.RandomState(seed)
        system = self._systems.get_system(config.get("system", "D&D 5e"))
        print = vprint(verbose)
        print("Generating token specifications")
        tokens = []
        gtoken = config.get("token", {}).copy()
        monsters = config.get("monsters", {})
        for mid, monster in monsters.items():
            for token in monster.get("tokens", []):
                
                res = merge_configs(gtoken, monster, token)
                res["monster"] = mid
                count = token.get("count", 1)
                tokens.extend(make_n(res, count))

        for token in config.get("tokens", []):
            monster = {}
            if "monster" in token:
                if token["monster"] not in monsters:
                    raise ValueError(f"Monster {token['monster']} not found")
                monster = monsters.get(token["monster"], {})
            res = merge_configs(gtoken, monster, token)
            count = res.get("count", 1)
            tokens.extend(make_n(res, count))
        
        # Apply system-specific token sizes
        for token in tokens:
            if "size" not in token:
                continue
            size = system.token_size(token["size"])
            if isinstance(size, float) or isinstance(size, int):
                size = [size, size]
            size = np.array(size)
            token["width"] = size[0]
            token["height"] = size[1]
            token["radius"] = (size[0] + size[1]) / 4

        # Apply token-instance-specific scaling
        for token in tokens:
            scale = token.get("scale", 1)
            scale_rho = token.get("scale_rho", 0)
            if scale_rho != 0:
                scale = random_ratio(scale, scale_rho, rng)
            if scale != 1:
                token["width"] *= scale
                token["height"] *= scale
                token["radius"] *= scale
        
        # Apply random images
        for token in tokens:
            if "images_url" in token:
                token["image_url"] = rng.choice(token["images_url"])
        print(f"Generated {len(tokens)} tokens")


        return tokens

    @property
    def resources(self):
        if self._resources is None:
            self.load_resources()
        return self._resources

    def load_resources(self, config:Dict[str,Any] = None, verbose=None) -> Dict[str, Any]:
        """
        Load resources specified in the configuration.
        :param config: The configuration dictionary.
        :return: A dictionary of loaded resources.
                Structure is similar to configuration,
                except that paths are replaced with loaded resources.
        """
        config = config if config is not None else self._cfg
        if config is None:
            return {}
        if verbose == None:
            verbose = config.get("verbose", False)
        resources = {} if self._resources is None else self._resources
        
        if not isinstance(config, dict):
            return {}
        for key, value in config.items():
            if isinstance(value, dict):
                inner = self.load_resources(value, verbose)
                if inner is not None:
                    resources.update(inner)
            if isinstance(value, list) or isinstance(value, tuple):
                if key == 'url' or key.endswith('_url'):
                    for item in value:
                        if item not in resources:
                            resources[item] = self.load_resource(item, verbose)
                else:
                    for item in value:
                        inner = self.load_resources(item, verbose)
                        if inner is not None:
                            resources.update(inner)
            elif key == 'url' or key.endswith('_url'):
                if value not in resources:
                    resources[value] = self.load_resource(value, verbose)
        self._resources = resources
        return resources
    
    def __getitem__(self, key):
        return self._resources[key]
    
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
        res = _download(url, temp_file.name, 
                        self._cfg.get("__config_files", []),
                        allow_rename=True)
        print(f"Resource saved to {res}")
        return res

    def cleanup(self):
        """
        Cleans up temporary files created during resource loading.
        """
        for file_path in self._local_files:
            if Path(file_path).is_file():
                Path(file_path).unlink()



def _download(url: str, file_path: str, 
              config_files: List[str] = (),
              allow_rename: bool = True) -> Path:
    """
    Downloads a file from a URL to a local path.

    :param url: The URL of the file to download.
    :param file_path: The local path to save the downloaded file.
    """
    # Check if the URL is a local file
    if url.lower().startswith("file://"):
        return find_local_path(Path(url[7:]), config_files)
    elif (any(url.lower().startswith(s) for s in [".", "/", "~"])
          or url.lower()[1:3] == ":\\"):
        return find_local_path(Path(url), config_files)
    

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

            




def random_ratio(mu, sigma, rng):
    """
    Generates a random ratio, log-normally distributed around a mean.
    :param mu: The mean of the distribution.
    :param sigma: The standard deviation of the distribution.
    :param rng: The random number generator.
    :return: A random ratio.
    """
    return rng.lognormal(np.log(mu), sigma)


def find_local_path(path:Path, config_files:List[str]) -> Path:
    """
    Finds a local path based on a configuration file.
    :param path: The path to find.
    :param config_files: The list of configuration files.
    :return: The local path to the file.
    """
    if path.is_absolute():
        return path
    for config_file in config_files:
        config_path = Path(config_file).parent
        local_path = config_path / path
        if local_path.is_file():
            return local_path
    raise FileNotFoundError(f"File {path} not found in any configuration directory")        


def make_n(d, n):
    return [d.copy() for _ in range(n)]