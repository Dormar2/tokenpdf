
import numpy as np

from tokenpdf.canvas import make_canvas
from tokenpdf.utils.verbose import vprint, vtqdm
from tokenpdf.utils.papersize import parse_papersize

class CanvasManager:
    """Manages canvas creation and token and map placement."""

    def __init__(self, config, loader, verbose):
        self.verbose = verbose
        self.print = vprint(verbose)
        self.tqdm = vtqdm(verbose)
        self.loader = loader
        self.canvas = make_canvas(config)
        self.config = config
        self.page_size, self.margin, self.page_size_margin, self.margin_r = self._calculate_page_size()

    def place_tokens(self, tokens, layout, maps, mapper):
        """Places tokens on the canvas.

        Args:
          tokens: 
          layout: 
          maps: 
          mapper: 

        Returns:

        """
        # add map tokens
        tokens = tokens.copy()
        tokens.extend(self.make_map_tokens(maps, mapper))
        verbose = self.verbose
        tqdm = vtqdm(verbose)
        print = vprint(verbose)
        sizes = [token.area(token_cfg, self.loader) for token, token_cfg in tqdm(tokens)]
        sizesm = [self._add_margin(size, token_cfg) for size, (_, token_cfg) in zip(sizes, tokens)]
        sizes_with_margins = [size for size, *_ in sizesm]
        token_margins = [(r, regular) for _, r, regular in sizesm]

        print("Arranging tokens in pages")
        print(f"Page size: {self.page_size_margin}")
        #print(f"Token sizes: {sizes_with_margins}")
        pages = layout.arrange(sizes_with_margins, self._gen_page_size(), verbose=verbose)
        canvas_pages = self._make_pages(pages)
        for placement_page, canvas_page in zip(tqdm(pages, desc="Drawing token pages"),
                                                canvas_pages):
            page_view = canvas_page.margin_view(self.margin_r, regular=True)
            for tindex, x, y, width, height in tqdm(placement_page, desc="Drawing tokens", leave=False):
                
                
                orig_size = sizes[tindex]
                r, regular_margins = token_margins[tindex]
                rotated = not same_aspect_ratio((width, height), orig_size)
                
                if rotated:
                    # When rotated, the top left corner is shifted to the right by "height"
                    # And the whole thing is rotated around that by 90 degrees
                    # (actually adding width, because that's the original height)
                    view = page_view.view(x + width, y, height, width, angle=np.pi/2)
                else:
                    view = page_view.view(x,y, width, height)
                    
                mview = view.margin_view(r, regular=regular_margins)
                token, t_cfg = tokens[tindex]
                token.draw(mview, t_cfg, self.loader)
    
    def make_map_tokens(self, maps, mapper):
        """Places maps on the canvas.

        Args:
          maps: 
          mapper: 

        Returns:

        """
        verbose = self.verbose
        tqdm = vtqdm(verbose)
        print = vprint(verbose)
        fragments = []
        page_gen = self._gen_page_size()
        for map in tqdm(maps, desc="Making map fragments"):
            in_page_size = map.size_on_page
            overlap_margin = map.overlap_margin
            #placements = mapper.map(in_page_size, page_gen, overlap_margin, verbose=verbose)
            placements = mapper.map(map, page_gen, overlap_margin, verbose=verbose)
            # Ignore the placements themselves, just use 
            # the fragments. The mapper returned a possible
            # placement, so we know it can be placed.
            #num_pages = max(p for p, *_ in placements) + 1
            fragments.extend([(f, f.map.config) for _, f, _ in placements])
            
            #pages = self._make_pages(range(num_pages))
            
            #for page_num, img_roi, page_roi in placements:
            #    page = pages[page_num]
            #    page_roi_with_margins = (*(page_roi[:2] + self.margin), *page_roi[2:])
            #    map.draw(page, page_roi_with_margins, img_roi)
        return fragments    
            


    def save(self):
        """Saves the canvas to a file."""
        self.canvas.save(verbose=self.verbose)
        self.canvas.cleanup()

    def _calculate_page_size(self):
        """ """
        config = self.config
        page_type = config.get('page_size', 'A4')
        page_size = np.array([float(m) for m in parse_papersize(page_type, "mm")])
        if config.get("orientation", "portrait").lower() in ["landscape", "l"]:
            page_size = page_size[::-1]
        margin_ratio = np.clip(config.get("page_margin", config.get("margin", 0)), 0, 1)
        margin = page_size * margin_ratio
        page_size_margin = page_size - 2 * margin
        return page_size, margin, page_size_margin, margin_ratio


    def _gen_page_size(self):
        """Generates pages (page sizes) as needed.
           Currently a constant stream of the same size

        Args:

        Returns:

        """
        while True:
            yield self.page_size_margin

                
    def _make_pages(self, pages):
        """

        Args:
          pages: 

        Returns:

        """
        return [self.canvas.create_page(self.page_size) for _ in pages]
    
    def _add_margin(self, size, token_cfg):
        """

        Args:
          size: 
          token_cfg: 

        Returns:

        """
        regular = token_cfg.get("regular_margin", True)
        r = np.clip(token_cfg.get("margin", 0), 0, 1)
        margin =  r * (np.array(size) if not regular else np.min(size))
        return size + 2 * margin, r, regular
  

def same_aspect_ratio(size1, size2):
    """ Tests if the two (w,h) pairs have the same aspect ratio."""
    if size1[1] == 0 or size2[1] == 0:
        return size2[1] == 0 and size1[1] == 0
    def same_ao(s1,s2):
        return np.isclose(s1[0] / s1[1], s2[0] / s2[1], rtol=1e-2, atol=1e-2)
    
    # Try normally, and floored
    return (same_ao(size1, size2) or
            same_ao((int(size1[0]), int(size1[1])), (int(size2[0]), int(size2[1]))))