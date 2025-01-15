from typing import List, Tuple, Generator
from .layout import Layout

from tokenpdf.utils.verbose import vprint, vtqdm

class GreedyLayout(Layout):
    """Greedy layout algorithm for arranging tokens on pages."""

    def arrange(
        self, 
        token_sizes: List[Tuple[float, float]], 
        page_sizes: Generator[Tuple[float, float], None, None],
        verbose: bool = False
    ) -> List[List[Tuple[int, float, float, float, float]]]:
        """Implements a greedy algorithm for arranging tokens on pages."""
        if not page_sizes:
            raise ValueError("At least one page size must be provided.")

        
        pages = []  # List of pages to be returned
        
        current_page = []  
        x, y = 0, 0  
        page_width, page_height = next(page_sizes)
        max_row_height = 0  
        tqdm = vtqdm(verbose)
        for i, (token_width, token_height) in enumerate(tqdm(token_sizes,
                                                                desc="Arranging tokens")):
            # If the token doesn't fit in the current row, move to the next row
            if x + token_width > page_width:
                x = 0
                y += max_row_height
                max_row_height = 0

            # If the token doesn't fit on the current page, create a new page
            if y + token_height > page_height:
                pages.append(current_page)
                current_page = []
                x, y = 0, 0
                max_row_height = 0
                page_width, page_height = next(page_sizes)

            # Add the token to the current page
            current_page.append((i, x, y, token_width, token_height))
            x += token_width
            max_row_height = max(max_row_height, token_height)

        # Add the last page if it has any tokens
        if current_page:
            pages.append(current_page)

        return pages
