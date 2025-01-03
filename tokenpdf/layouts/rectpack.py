from typing import Any, Dict, Generator, List, Tuple
from itertools import product
import rectpack
from .layout import KnownPagesLayout, BestLayout
import math
from collections import defaultdict


PACKING_BIN_NAMES = {n:getattr(rectpack.PackingBin, n) for n in rectpack.PackingBin}
PACKING_ALGO_NAMES = {
    name: getattr(rectpack, name) for name in dir(rectpack) 
    if (
        name.startswith("Guillotine") or
        name.startswith("MaxRects") or
        name.startswith("Skyline")
    )
}
PACKING_SORT_NAMES = {
    name[5:] : getattr(rectpack, name) for name in dir(rectpack) 
    if name.startswith("SORT_")
}

# Lowercase versions of the names to allow case-insensitive matching
PACKING_BIN_NAMES_L = {name.lower():name for name in PACKING_BIN_NAMES}
PACKING_ALGO_NAMES_L = {name.lower():name for name in PACKING_ALGO_NAMES}
PACKING_SORT_NAMES_L = {name.lower():name for name in PACKING_SORT_NAMES}



class RectPackLayout(KnownPagesLayout):
    """
    Uses the various packing algorithms from the rectpack library to arrange tokens on pages.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the layout with the given configuration.
        :param config: Dictionary of configuration options for the layout.
        """
        super().__init__(config)
        self.config = config
        self.bin_algo_name = self.config.get("bin_algo", "BFF")
        self.bin_algo = PACKING_BIN_NAMES[PACKING_BIN_NAMES_L[self.bin_algo_name.lower()]]
        self.pack_algo_name = self.config.get("pack_algo", "GuillotineBssfSas")
        self.pack_algo = PACKING_ALGO_NAMES[PACKING_ALGO_NAMES_L[self.pack_algo_name.lower()]]
        self.sort_algo_name = self.config.get("sort_algo", "AREA")
        self.sort_algo = PACKING_SORT_NAMES[PACKING_SORT_NAMES_L[self.sort_algo_name.lower()]]
        self.rotation = self.config.get("rotation", True)

    def __str__(self)->str:
        return f"RP({int(self.bin_algo)}, {self.pack_algo_name}, {self.sort_algo_name}, {int(self.rotation)})"
    
    def arrange_on_pages(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: List[Tuple[float, float]],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """
        Arranges tokens on pages based on their sizes and page constraints.
        :param token_sizes: A list of tuples representing token widths and heights in mm.
        :param page_sizes: A list of tuples representing page widths and heights in mm.
        :param verbose: Whether to print progress information.
        :return: A list of pages, where each page is a list of tuples containing the token index
            and the placement rectangle (x, y, width, height)
        """
        # Create a new packer
        packer = rectpack.newPacker(
            mode=rectpack.PackingMode.Offline,
            bin_algo = self.bin_algo,
            pack_algo = self.pack_algo,
            sort_algo = self.sort_algo,
            rotation = self.rotation,
        )

        # Add the pages to the packer
        for page_width, page_height in page_sizes:
            packer.add_bin(int(math.floor(page_width)), int(math.floor(page_height)))
        # Add the tokens to the packer
        for i, (width, height) in enumerate(token_sizes):
            packer.add_rect(width, height, rid=i)
        # Pack the tokens onto the page
        packer.pack()
        # Get the placement rectangles
        placement = packer.rect_list()
        # Convert the placement rectangles to the format expected by the caller
        pages = defaultdict(list)
        for bid, x, y, width, height, rid in placement:
            pages[int(bid)].append((int(rid), x, y, width, height))
        return [pages.get(i, [])
                for i in range(len(page_sizes))]


def make_rectpack_layouts(bin_algo:str|None|List[str]|Tuple[str] = None,
                          pack_algo:str|None|List[str]|Tuple[str] = None,
                          sort_algo:str|None|List[str]|Tuple[str] = None,
                          rotation:bool | None = None) -> Generator[RectPackLayout, None, None]:
    """
    Factory function to create a RectPackLayout with the given configuration.
    :param bin_algo: The bin packing algorithm to use.
    :param pack_algo: The packing algorithm to use.
    :param sort_algo: The sorting algorithm to use.
    :param rotation: Whether to allow rotation of tokens.
    :return: A RectPackLayout instance.
    """
    def to_combination_list(value, options_dict):
        options = list(options_dict.keys())
        if isinstance(value, str) and value.lower() != "all":
            return [value]
        elif isinstance(value, list) or isinstance(value, tuple):
            return value
        return options
        

    bin_algos = to_combination_list(bin_algo, PACKING_BIN_NAMES_L)
    pack_algos = to_combination_list(pack_algo, PACKING_ALGO_NAMES_L)
    sort_algos = to_combination_list(sort_algo, PACKING_SORT_NAMES_L)
    rotations = [rotation] if rotation is not None else [True, False]
    for bin_algo, pack_algo, sort_algo, rotation in product(bin_algos, pack_algos, sort_algos, rotations):
        yield RectPackLayout({
            "bin_algo": bin_algo,
            "pack_algo": pack_algo,
            "sort_algo": sort_algo,
            "rotation": rotation
        })

def make_constrainted_rectpack_layouts(config: Dict[str, Any]) -> Generator[RectPackLayout, None, None]:
    """
    Factory function to create a RectPackLayout with all possible configurations
    other than constrained in the given config.
    """
    # Make kw with only relevant keys
    kw = {k:config.get(k) for k in ["bin_algo", "pack_algo", "sort_algo", "rotation"]}
    kw = {k:v for k,v in kw.items() if v is not None}
    yield from make_rectpack_layouts(**kw)

def make_constrainted_best_layout(config: Dict[str, Any]) -> BestLayout:
    """
    Factory function to create a BestLayout with all possible configurations
    other than constrained in the given config.
    """
    return BestLayout(config, make_constrainted_rectpack_layouts(config))

def make_default_rectpack_layouts(rotation:bool=True) -> Generator[RectPackLayout, None, None]:
    """
    Factory function to create a RectPackLayout with reccommended configurations
    Currently, uses GuillotineBssfSas, MaxRectsBssf, SkylineMwf for in-bin packing, 
    AREA for sorting,
    and all possible bin-packing algorithms.
    """
    config = {
        "pack_algo": ["GuillotineBssfSas", "MaxRectsBssf", "SkylineMwf"],
        "sort_algo": "AREA",
        "rotation": rotation
    }
    yield from make_constrainted_rectpack_layouts(config)
    
def make_default_best_layout(config) -> BestLayout:
    """
    Factory function to create a BestLayout with reccommended configurations
    Currently, uses GuillotineBssfSas, MaxRectsBssf, SkylineMwf for in-bin packing, 
    AREA for sorting,
    and all possible bin-packing algorithms.
    """
    rotation = config.get("rotation", True)
    return BestLayout(config,make_default_rectpack_layouts(rotation=rotation))