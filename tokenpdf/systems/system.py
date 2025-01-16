from typing import Dict, Tuple
from pathlib import Path
import numpy as np
import tokenpdf.utils.config as config

class RPGSystem:
    """ """
    def __init__(self, config):
        self.config = config
        self.name : str = config["name"]
        self.token_sizes : Dict[str, np.ndarray] = {}
        for k,v in config["token_sizes"].items():
            self.token_sizes[k.lower()] = np.array(v)
        self.cell_size_in_mm = np.array(config["cell_size"]["mm"])
        self.cell_size_in_world_coords = np.array(config["cell_size"]["world"])
        self.world_coords_unit : str = config["cell_size"]["unit"]

    def token_size(self, name) -> np.ndarray:
        """

        Args:
          name: 

        Returns:

        """
        name = name.lower()
        sz = self.world_to_page(self.token_sizes[name])
        if isinstance(sz, float) or isinstance(sz, int) or len(sz) == 1:
            sz = [float(sz), float(sz)]
        return np.array(sz)
    
    def world_to_cells(self, world_coords) -> np.ndarray:
        """

        Args:
          world_coords: 

        Returns:

        """
        wc = np.array(world_coords)
        return (wc / self.cell_size_in_world_coords)
    
    def cells_to_world(self, cell_coords) -> np.ndarray:
        """

        Args:
          cell_coords: 

        Returns:

        """
        cc = np.array(cell_coords)
        return (cc * self.cell_size_in_world_coords)
    
        
    def page_to_cells(self, page_coords) -> np.ndarray:
        """

        Args:
          page_coords: 

        Returns:

        """
        pc = np.array(page_coords)
        return (pc / self.cell_size_in_mm)

    def cells_to_page(self, cell_coords) -> np.ndarray:
        """

        Args:
          cell_coords: 

        Returns:

        """
        cc = np.array(cell_coords)
        return (cc * self.cell_size_in_mm)

    def world_to_page(self, world_coords) -> np.ndarray:
        """

        Args:
          world_coords: 

        Returns:

        """
        return self.cells_to_page(self.world_to_cells(world_coords))

    def page_to_world(self, page_coords) -> np.ndarray:
        """

        Args:
          page_coords: 

        Returns:

        """
        return self.cells_to_world(self.page_to_cells(page_coords))    
        
        
        

class RPGSystemRegistry:
    """ """
    def __init__(self):
        self.systems = {}
        self._load_defaults()
    
    def add_system(self, system):
        """

        Args:
          system: 

        Returns:

        """
        self.systems[system.name] = system
        return system

    def load_system(self, path:Path) -> RPGSystem:
        if not path.exists():
            raise FileNotFoundError(f"System file {path} not found.")
        if not config.format_supported(path):
            raise ValueError(f"Unsupported file format for system file {path}")
        return self.add_system(RPGSystem(config.load_any(path)))
    
    def get_system(self, name):
        """

        Args:
          name: 

        Returns:

        """
        return self.systems[name]
    
    def __getitem__(self, name):
        return self.get_system(name)
    
    def __setitem__(self, _, system):
        self.add_system(system)
    
    def __contains__(self, name):
        return name in self.systems

    def __iter__(self):
        return iter(self.systems.values())
    
    def __len__(self):
        return len(self.systems)
    
    def __str__(self):
        return f"RPGSystemRegistry({self.systems})"
    
    def __repr__(self):
        return str(self)
    
    def __bool__(self):
        return bool(self.systems)
    
    def __nonzero__(self):
        return self.__bool__()
    
    def _load_defaults(self):
        """ """
        data_folder = config.get_data_folder() / "systems"
        for files in data_folder.rglob("*.*"):
            if config.format_supported(files):
                self.load_system(files)


