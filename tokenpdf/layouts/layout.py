from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Generator

from tokenpdf.utils.general import ResettableGenerator, consume
from tokenpdf.utils.graph import largest_connected_component

class Layout(ABC):
    """Abstract base class for layouts.
    Defines the interface for all layout algorithms.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initializes the layout with the given configuration.

        Args:
            config: Dictionary of configuration options for the layout.
        """
        self.config = config

    @abstractmethod
    def arrange(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Arranges tokens on pages based on their sizes and page constraints.

        Args:
            token_sizes: A list of tuples representing token widths and
                heights in mm.
            page_sizes: A generator of tuples representing page widths
                and heights in mm.
            verbose: Whether to print progress information.

        Returns:
            A list of pages, where each page is a list of tuples
            containing the token index and the placement rectangle (x,
            y, width, height)
        """
        pass

    def sort_output(self, output: List[List[Tuple[int, float, float, float, float]]]) -> List[List[Tuple[int, float, float, float, float]]]:
        """Sorts the pages of the output to resemble the order of the tokens as best we can"""
        # We'll use lexicographic order the token sequences in each page
        def _page_key(page):
            return sorted([t[0] for t in page])
            
        return sorted(output, key=_page_key)

    def __str__(self):
        return self.__class__.__name__

class LayoutImpossibleError(Exception):
    """Exception raised when a single page layout algorithm is unable to arrange the given tokens on the given page."""
    pass



class KnownPagesLayout(Layout):
    """A subclassable layout that arranges tokens on a generator of page sizes,
    using an overrided function that arranges tokens on a concrete list of page sizes.
    Uses an iterative "double pages number" approach to find the best number of pages.
    """
    def arrange(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Arranges tokens on pages based on their sizes and page constraints.

        Args:
            token_sizes: A list of tuples representing token widths and
                heights in mm.
            page_sizes: A generator of tuples representing page widths
                and heights in mm.
            verbose: Whether to print progress information.

        Returns:
            A list of pages, where each page is a list of tuples
            containing the token index and the placement rectangle (x,
            y, width, height)
        """
        pages = [next(page_sizes)]
        while len(pages) <= len(token_sizes): # Safety check
            try:
                if verbose:
                    print(f"Trying {len(pages)} pages")
                result = self.arrange_on_pages(token_sizes, pages, verbose)
                # Remove unneeded pages
                while not result[-1]:
                    result.pop()
                return self.sort_output(result)
            except LayoutImpossibleError as e:
                try:
                    # Try to add new pages
                    pages.extend(consume(page_sizes, max(1,min(len(pages), len(token_sizes) - len(pages)))))
                except StopIteration:
                    # Can't even add a single page
                    raise e
        
        raise LayoutImpossibleError("Not enough pages to arrange all tokens")
    
    @abstractmethod
    def arrange_on_pages(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: List[Tuple[float, float]],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Arranges tokens on pages based on their sizes and page constraints.
        Raises LayoutImpossibleError if the tokens can't be arranged on the given pages.

        Args:
            token_sizes: A list of tuples representing token widths and
                heights in mm.
            page_sizes: A list of tuples representing page widths and
                heights in mm.
            verbose: Whether to print progress information.

        Returns:
            A list of pages, where each page is a list of tuples
            containing the token index and the placement rectangle (x,
            y, width, height)
        """
        pass


class BestLayout(Layout):
    """Runs multiple Layout and chooses the best result"""

    def __init__(self, config: Dict[str, Any], layouts: List[Layout]):
        """Initializes the layout with the given configuration.

        Args:
            config: Dictionary of configuration options for the layout.
            layouts: List of layouts to run
        """
        super().__init__(config)
        
        # Just to "cut the middle-man", if there are any BestLayouts in the layouts list
        # we will just merge them into this one
        layoutr = []
        for layout in layouts:
            if isinstance(layout, BestLayout):
                layoutr.extend(layout.layouts)
            else:
                layoutr.append(layout)
        self.layouts = layoutr

    def arrange(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Arranges tokens on pages based on their sizes and page constraints.

        Args:
            token_sizes: A list of tuples representing token widths and
                heights in mm.
            page_sizes: A generator of tuples representing page widths
                and heights in mm.
            verbose: Whether to print progress information.

        Returns:
            A list of pages, where each page is a list of tuples
            containing the token index and the placement rectangle (x,
            y, width, height)
        """
        if not token_sizes:
            return []
        page_sizes = ResettableGenerator(page_sizes)
        best_result = None
        best_layout = None
        layouts = self.layouts.copy()
        for layout in layouts:
            try:
                page_sizes.reset()
                result = layout.arrange(token_sizes, page_sizes, verbose)
                
                best_result, best_layout = self._compare_results(best_result, result, best_layout, layout)
            except LayoutImpossibleError:
                if verbose:
                    print(f"Layout {layout.__class__.__name__} failed")
        if best_result is None:
            raise LayoutImpossibleError("No layout succeeded")
        return best_result
    
    def _compare_results(
        self, 
        result1: List[List[Tuple[int, float, float, float, float]]], 
        result2: List[List[Tuple[int, float, float, float, float]]],
        layout1: Layout, layout2: Layout
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Compares two results and returns the best one.

        Args:
            result1: The first result.
            result2: The second result.

        Returns:
            The best result.
        """
        if result1 is None:
            print(f"{layout1} failed, using {layout2}")
            return result2, layout2
        if result2 is None:
            print(f"{layout2} failed, using {layout1}")
            return result1, layout1
        if len(result1) < len(result2):
            print(f"{layout2} has more more pages ({len(result2)}), using {layout1} ({len(result1)})")
            return result1, layout1
        elif len(result1) > len(result2):
            print(f"{layout2} has less pages ({len(result2)}), using it")
            return result2, layout2
        # Same number of pages, compare by total contiguous area
        result1area = _largest_contiguous_areas(result1)
        result2area = _largest_contiguous_areas(result2)
        if result1area > result2area:
            print(f"{layout1} has the same page count ({len(result1)}) but more contiguous area ({result1area}) than {layout2} ({result2area}), using it")
            return result1, layout1
        elif result1area < result2area:
            print(f"{layout2} has the same page count ({len(result2)}) but more contiguous area ({result2area}) than {layout1} ({result1area}), using it")
            return result2, layout2
        print(f"{layout1},{layout2}: Equivalent ({len(result1)}), ({result1area}), using {layout1}")
        return result1, layout1

    
def _largest_contiguous_areas(result: List[List[Tuple[int, float, float, float, float]]]) -> float:
    """Returns the largest contiguous area in the result.
    Sums per-page contiguous areas.
    """
    EPS = 1e-4
    def _overlap(r1, r2):
        *_, x1, y1, w1, h1 = r1
        *_, x2, y2, w2, h2 = r2
        return (
            x1 + w1 >= x2 + EPS and x2 + w2 >= x1 + EPS and
            y1 + h1 >= y2 + EPS and y2 + h2 >= y1 + EPS
        )
    ccs = [
        (page, largest_connected_component(range(len(page)), lambda i, j: _overlap(page[i], page[j])))
        for page in result
    ]
    return sum(
        sum(page[i][-2] * page[i][-1] for i in cc)
        for page, cc in ccs
    )




    
