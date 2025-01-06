
from typing import Tuple
from .token import Token
from tokenpdf.utils.image import get_file_dimensions, complete_size
import numpy as np

class StandingToken(Token):

    @classmethod
    def supported_types(cls):
        return {
            "standing": {
                "width": None, "height": None, "border_color": "black", "fill_color": "white",
                "image_url": None, "border_url": None, "keep_aspect_ratio": True,
                "rect_border_thickness": 1,
                "rect_border_style": "dot-dash"
            }
        }
    
    def apply_defaults(self, config, resources):
        config = super().apply_defaults(config, resources)
        width, height = config.get("width"), config.get("height")
        width, height = complete_size(width, height, *get_file_dimensions(resources[config["image_url"]]), keep_aspect_ratio=config.get("keep_aspect_ratio", True))
        config["width"], config["height"] = width, height
        return config

        

    def area(self, config, resources) -> Tuple[float, float]:
        sarea = self._standing_area(config, resources)
        barea = self._base_area(config, resources, sarea)
        w = sarea[0]
        h = (sarea[1] + barea[1])*2
        return np.array([w, h])


    def _base_area(self, config, resources, standing_area) -> Tuple[float, float]:
        base = standing_area[0]
        return np.array([base, base/2])

    def _standing_area(self, config, resources) -> Tuple[float, float]:
        return np.array([config["width"], config["height"]])
    
    def draw(self, canvas, config, resources, rect):
        super().draw(canvas, config, resources, rect)
        x, y, width, height = rect
        xy = np.array([x, y])
        

        aw, ah = self.area(config, resources)
        sw, sh = self._standing_area(config, resources)
        bw, bh = self._base_area(config, resources, (sw, sh))
        b = max(bw, bh)
        smargin = config.get("standing_margin", 0) * np.array([b,b])
        rotated = False
        if (aw < ah) != (width < height):
            rotated = True
            sw, sh = sh, sw
            bw, bh = bh, bw
        sw_small, sh_small = sw - 2*smargin[0], sh - 2*smargin[1]
        
        if not rotated:
            # Vertical fold
            # Top, upside down
            pic1 = (*(xy + smargin + [0,bh]), sw_small, sh_small)
            pic1_transformation = {"flip": (False, True), "rotate": 0}
            # Bottom, right side up
            pic2 = (*(xy + [0, bh + sh] + smargin), sw_small, sh_small)
            pic2_transformation = {"flip": (False, False), "rotate": 0}
            # Fold lines
            fold1 = (x + smargin[0], y + bh, x+sw - smargin[0], y + bh)
            fold2 = (x + smargin[0], y + bh + sh, x+sw - smargin[0], y + bh + sh)
            fold3 = (x + smargin[0], y + bh + 2*sh, x+sw - smargin[0], y + bh + 2*sh)
        else:
            # Horizontal fold
            # Left, rotated anticlockwise
            pic1 = (*(xy + smargin + [bw, 0]), sw_small, sh_small)
            pic1_transformation = {"flip": (True, False), "rotate": np.pi/2}
            # Right, rotated clockwise
            pic2 = (*(xy + [bw + sw, 0] + smargin), sw_small, sh_small)
            pic2_transformation = {"flip": (False, False), "rotate": -np.pi/2}

            # Fold lines
            fold1 = (x + bw, y + smargin[1], x + bw, y + sh - smargin[1])
            fold2 = (x + bw + sw, y + smargin[1], x + bw + sw, y + sh - smargin[1])
            fold3 = (x + bw + 2*sw, y + smargin[1], x + bw + 2*sw, y + sh - smargin[1])
        canvas.image(*pic1, resources[config["image_url"]], **pic1_transformation)
        canvas.image(*pic2, resources[config["image_url"]], **pic2_transformation)

        canvas.line(*fold1)
        canvas.line(*fold2)
        canvas.line(*fold3)


        

    