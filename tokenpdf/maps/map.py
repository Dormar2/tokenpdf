from pydoc import text
import numpy as np
from tokenpdf.utils.image import TemporaryCropImageFile, add_grid, complete_size
from tokenpdf.token import Token
from PIL import Image


        


class MapFragment(Token):
    def __init__(self, map, rect, misc_margin, system, section=None):
        self.map = map
        self.rect = rect
        self.system = system
        self.section = section
        if misc_margin is None:
            self.text_margin = np.array([0,0])
            self.border_margin = np.array([0,0])
        else:
            border_margin_r = np.min(misc_margin)
            text_margin_r = np.max(misc_margin) - border_margin_r            
            self.text_margin = np.array([0, text_margin_r])
            self.border_margin = np.array([border_margin_r, border_margin_r])
        self.misc_margin = self.text_margin + self.border_margin
        
        


    @staticmethod
    def supported_types():
        return {
            "map_fragment": {
                "image_url": None, "grid": None, "dpi": 120, "overlap_margin": 0
            }
        }
    @property
    def width(self):
        return self.rect[2] + self.misc_margin[0]
    
    @property
    def height(self):
        return self.rect[3] + self.misc_margin[1]
    
    @property
    def text(self)->str:
        return f"{self.map.name}: {self.section[0]},{self.section[1]}" if self.section is not None else self.map.name
    
    def area(self, config, resources):
        return self.width, self.height
    
    def draw(self, canvas, config, resources, rect):
        factor2 = np.array([*self.map.factor, *self.map.factor])
        rect_in_image = np.array(self.rect)/factor2
        
        x,y,w,h = rect
        rotated = (self.width < self.height) != (w < h)
        misc_margin = self.misc_margin if not rotated else self.misc_margin[::-1]
        border_margin = self.border_margin if not rotated else self.border_margin[::-1]
        text_margin = self.text_margin if not rotated else self.text_margin[::-1]
        wp, hp = np.array([w,h]) - misc_margin
        xp, yp = np.array([x,y]) + border_margin / 2


        with TemporaryCropImageFile(self.map.img, rect_in_image, delete = False) as cropped:    
            canvas.image(xp, yp, wp, hp, cropped.name, mask = None, rotate = np.pi/2 * int(rotated))
        font_size = 12
        if text_margin[1] != 0:
            # Write it on the bottom
            xpt = xp
            ypt = y + h - text_margin[1]/2
            canvas.text(xpt, ypt, self.text, size = font_size)
        if text_margin[0] != 0:
            # Write it on the right
            xpt = x + w - text_margin[0]/2
            ypt = yp
            canvas.text(xpt, ypt, self.text, rotate = np.pi/2, size = font_size)
            
        
        

class Map:
    def __init__(self, config, loader, system):
        self.config = config
        self.name = config.get("name", "Map")
        self.system = system
        self.loader = loader
        res = config
        self.img = Image.open(loader[config["image_url"]])        
        self.dims = np.array(self.img.size)
        if "width" in res or "height" in res:
            width = res.get("width", -1)
            height = res.get("height", -1)
            self.width, self.height = complete_size(width, height, self.dims)
        else:
            if "grid" in res:
                size_in_cells = np.array(res["grid"])
            else:            
                size_in_cells = np.array(self.dims) / res.get("dpi", 120)
            self.width, self.height = system.cells_to_page(size_in_cells)
        img_in_page_size = np.array([self.width, self.height])
        self.factor = img_in_page_size / self.dims
        self.system = system

        grid_color = res.get("grid_color")
        add_grid_ = res.get("add_grid", grid_color is not None)
        if add_grid_:
            grid_color = grid_color if grid_color is not None else "black"
            self.img = add_grid(self.img, self.size_in_cells, grid_color)
    @property
    def size_on_page(self):
        return self.width, self.height
    
    @property
    def size_in_cells(self):
        return self.system.page_to_cells([self.width, self.height])
    
    @property
    def overlap_margin(self):
        return self.system.cells_to_page(self.config.get("overlap_margin", 0))
    
    def fragment(self, rect, misc_margin = np.array([0,0]), section=None) -> MapFragment:
        return MapFragment(self, rect, misc_margin, self.system, section)

        

    
    
    