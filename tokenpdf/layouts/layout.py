from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Generator

class Layout(ABC):
    """
    Abstract base class for layouts.
    Defines the interface for all layout algorithms.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the layout with the given configuration.
        :param config: Dictionary of configuration options for the layout.
        """
        self.config = config

    @abstractmethod
    def arrange(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """
        Arranges tokens on pages based on their sizes and page constraints.
        :param token_sizes: A list of tuples representing token widths and heights in mm.
        :param page_sizes: A generator of tuples representing page widths and heights in mm.
        :param verbose: Whether to print progress information.
        :return: A list of pages, where each page is a list of tuples containing the token index
            and the placement rectangle (x, y, width, height)
        """
        pass
