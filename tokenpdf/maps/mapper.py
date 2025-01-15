
import abc
from re import M
from PIL import Image
from typing import Tuple, Generator, Sequence
from tokenpdf.layouts import LayoutImpossibleError
from tokenpdf.utils.general import consume
from .map import Map, MapFragment

Rectangle = Tuple[float, float, float, float]
# Returns the page, and the map fragment, and its placement on the page
Result = Sequence[Tuple[int, MapFragment, Rectangle]]


class Mapper(abc.ABC):
    
    def __init__(self, config):
        self.config = config
        self.verbose = config.get("verbose", False)
    
    @abc.abstractmethod
    def map(self, map: Map, page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False) -> Result:
        pass

class KnownPagesMapper(Mapper):
    """
    Maps a map to a set of known page sizes,
    similar to the KnownPagesLayout layout.
    """
    
    def __init__(self, config, loader):
        super().__init__(config, loader)
    
    def map(self, map: Map, page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False) -> Result:
        pages = [next(page_sizes)]
        while True:
            try:
                result = self.map_on_pages(map, pages, verbose)
                return result
            except LayoutImpossibleError as e:
                try:
                    # Try to add new pages
                    pages.extend(consume(page_sizes, len(pages)))
                except StopIteration:
                    raise e

        
        
    @abc.abstractmethod 
    def map_on_pages(self, map: Image, page_sizes: Sequence[Tuple[float, float]], verbose: bool = False) -> Result:
        """
        Maps a map to a set of known page sizes.
        """
        pass
    