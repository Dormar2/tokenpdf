from .mapper import Mapper, Image, Tuple, Generator, Sequence, Rectangle, Result
import numpy as np
from .map import Map, MapFragment

class SimpleMapper(Mapper):
    """ Simple mapper, assumes page sizes are all the same """
    def __init__(self, config):
        super().__init__(config)


    def map(self, img: Map,
            page_sizes: Generator[Tuple[float, float], None, None],
            overlap_margin: float = 0,
            verbose: bool = False) -> Result:


        img_size = np.array(img.size_on_page)
        page_size = np.array(next(page_sizes))
        pw,ph = page_size
        
        text_orientation = "p" if pw < ph else "l"
        text_margin = img.config.get("text_margin", 0)
        border_margin = img.config.get("border_margin", 0)
        pborder = np.min(page_size) * border_margin * 2
        pborder = np.array([pborder, pborder])
        tborder = np.array([0, text_margin*ph])
        misc_margin = pborder + tborder
        

        # The misc margin isn't symmetrical, so we don't double it here, but up there
        roi_size = page_size - misc_margin
        roi_size = np.clip(roi_size, 0, img_size)
        placement_N = np.ceil(img_size / roi_size).astype(int)
        nw, nh = placement_N
        placements = []
        page_num = 0
        for i in range(nw):
            for j in range(nh):
                xy_img_start = np.array([i, j]) * roi_size - overlap_margin
                xy_img_start = np.clip(xy_img_start, 0, img_size)
                xy_img_end = xy_img_start + roi_size
                xy_img_end = np.clip(xy_img_end, 0, img_size)
                actual_size_image = xy_img_end - xy_img_start
                actual_size_page = actual_size_image + misc_margin
                img_roi = (*xy_img_start, *actual_size_image)
                page_roi = (0,0, *actual_size_page)
                fragment = img.fragment(img_roi, misc_margin, (i,j))
                placements.append((page_num, fragment, page_roi))
                if (i!=(nw-1)) or (j!=(nh-1)):
                    page_size_next = np.array(next(page_sizes))
                    page_num += 1
                    if not np.allclose(page_size, page_size_next):
                        raise ValueError("SimpleMapper only supports fixed page sizes")
        return placements



                
                
                




        

        
        
        