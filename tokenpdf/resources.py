import itertools
from pathlib import Path
from typing import Dict, Any, List, Sequence
import numpy as np
from tokenpdf.utils.config import merge_configs
from tokenpdf.utils.image import get_file_dimensions, complete_size
from tokenpdf.utils.verbose import vprint, vtqdm
from tokenpdf.utils.io import download_file
from tokenpdf.systems import registry as system_registry
from tokenpdf.maps import Map
from .image import TokenImage
import tokenpdf.utils.config as config

class ResourceLoader:
    """A class responsible for loading resources, including configuration files."""
    CROSS_PRODUCT_KEYS = ["page_size"]
    def __init__(self):
        self._local_files = []
        self._cfg = {}
        self._resources = {}
        self._systems = system_registry

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """Loads a single configuration file in JSON, YAML, or TOML format.

        Args:
          file_path: The path to the configuration file.
          file_path: str: 

        Returns:
          : A dictionary representing the configuration.

        Raises:
          ValueError: If the file format is unsupported
          FileNotFoundError: If the file does not exist

        """
        c = config.load_with_imports(file_path)
        self._cfg = c
        return c

    def load_configs(self, file_paths: List[str]) -> Dict[str, Any] | Sequence[Dict[str, Any]]:
        """Loads multiple configuration files and unifies them.
            Possibly generates multiple "configuration tasks"
            if some specific keys have multiple values.

        Args:
          file_paths: A list of paths to the configuration files.
          file_paths: List[str]: 

        Returns:
          : A unified dictionary representing the combined
          configuration.

        """
        unified_config = {}
        for file_path in file_paths:
            single_config = self.load_config(file_path)
            unified_config = merge_configs(unified_config, single_config)
        if file_paths:
            unified_config["__config_files"] = file_paths
        self._cfg = unified_config
        # Generate multiple configuration tasks if needed
        uc = unified_config
        cross_product_values ={
            k: (uc.get(k) if isinstance(uc.get(k), list|tuple) else [uc.get(k)])
            for k in self.CROSS_PRODUCT_KEYS
        }
        products = list(itertools.product(*cross_product_values.values()))
        print(products, cross_product_values)
        if len(products) == 1:
            return unified_config
        elif not products:
            raise ValueError("No configuration tasks generated")
        else:
            
            config_tasks = [
                dict(unified_config, **dict(zip(cross_product_values.keys(), p)))
                for p in products
            ]
            return config_tasks
    
    def generate_tokens(self, config: Dict[str, Any] = None, verbose=None) -> Dict[str, Any]:
        """Generates token specifications based on the configuration.

        Args:
          config: The configuration dictionary.
          config: Dict[str: 
          Any]:  (Default value = None)
          verbose:  (Default value = None)

        Returns:
          : A dictionary of generated tokens.

        """
        config = config if config is not None else self._cfg
        if config is None:
            return []
        if verbose == None:
            verbose = config.get("verbose", False)
        seed = config.get("seed", None)
        rng = np.random.RandomState(seed)
        if "system_url" in config:
            system = self._systems.load_system(config["system_url"])
        else:
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
    
    def generate_maps(self, config: Dict[str, Any] = None, verbose=None) -> Dict[str, Any]:
        """Generates map specifications based on the configuration.

        Args:
          config: The configuration dictionary.
          config: Dict[str: 
          Any]:  (Default value = None)
          verbose:  (Default value = None)

        Returns:
          : A dictionary of generated maps.

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
        print("Generating map specifications")
        maps = []
        gmap = config.get("map", {}).copy()
        for map in config.get("maps", {}).values():
            res = merge_configs(gmap, map)
           
            
            maps.append(Map(res, self, system))
        print(f"Generated {len(maps)} maps")
        return maps

            
            

            
        

    @property
    def resources(self):
        """ """
        if self._resources is None:
            self.load_resources()
        return self._resources

    def load_resources(self, config:Dict[str,Any] = None, verbose=None) -> Dict[str, Any]:
        """Load resources specified in the configuration.

        Args:
          config: The configuration dictionary.
          config:Dict[str: 
          Any]:  (Default value = None)
          verbose:  (Default value = None)

        Returns:
          : A dictionary of loaded resources. Structure is similar to
          configuration, except that paths are replaced with loaded
          resources.

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
    
    def load_resource(self, url: str, verbose=False) -> TokenImage:
        """Saves a local copy of the resource (if needed) and returns the path.

        Args:
          url: The URL of the resource.
          url: str: 
          verbose:  (Default value = False)

        Returns:
          : The local path to the resource.

        """
        config_files = self._cfg.get("__config_files", [])
        optimize_images_quality = self._cfg.get("optimize_image_quality", 0)
        pil_save_kw = {"optimize": True,
                            "format": "PNG"}
        if optimize_images_quality:
            pil_save_kw["quality"] = optimize_images_quality


        # Check if the URL is actually a local file
        if url.lower().startswith("file://"):
            path_or_url = find_local_path(Path(url[7:]), config_files, verbose)
        elif (any(url.lower().startswith(s) for s in [".", "/", "~"])
            or url.lower()[1:3] == ":\\"):
            path_or_url = find_local_path(Path(url), config_files, verbose)
        else:
            path_or_url = url
        # Download the resource from the URL
        return TokenImage(path_or_url, None, default_suffix=".png", **pil_save_kw)
    
    def cleanup(self):
        """Cleans up temporary files created during resource loading."""
        for file_path in self._local_files:
            if Path(file_path).is_file():
                Path(file_path).unlink()



def _download(url: str, file_path: str, 
              config_files: List[str] = (),
              allow_rename: bool = True,
              verbose:bool = False) -> str:
    """Downloads a file from a URL to a local path.

    Args:
      url: The URL of the file to download.
      file_path: The local path to save the downloaded file.
      url: str: 
      file_path: str: 
      config_files: List[str]:  (Default value = ())
      allow_rename: bool:  (Default value = True)
      verbose:bool:  (Default value = False)

    Returns:

    """
    

    return download_file(url, file_path, allow_rename)

            




def random_ratio(mu, sigma, rng):
    """Generates a random ratio, log-normally distributed around a mean.

    Args:
      mu: The mean of the distribution.
      sigma: The standard deviation of the distribution.
      rng: The random number generator.

    Returns:
      : A random ratio.

    """
    return rng.lognormal(np.log(mu), sigma)


def find_local_path(path:Path, config_files:List[str], verbose:bool = False) -> Path:
    """Finds a local path based on a configuration file.

    Args:
      path: The path to find.
      config_files: The list of configuration files.
      path:Path: 
      config_files:List[str]: 
      verbose:bool:  (Default value = False)

    Returns:
      : The local path to the file.

    """
    print = vprint(verbose)
    print(f"Looking for local path {path}")
    if path.is_absolute():
        print(f"Using absolute path {path}")
        return path
    for config_file in config_files:
        config_path = Path(config_file).parent
        local_path = config_path / path
        print(f"Trying {local_path}")
        if local_path.is_file():
            print(f"Found! At {local_path}")
            return local_path
    raise FileNotFoundError(f"File {path} not found in any configuration directory")        


def make_n(d, n):
    """

    Args:
      d: 
      n: 

    Returns:

    """
    return [d.copy() for _ in range(n)]