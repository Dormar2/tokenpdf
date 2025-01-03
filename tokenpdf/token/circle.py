
import math
from typing import Tuple
from PIL import Image
import numpy as np
from .token import Token
from tokenpdf.utils.image import get_file_dimensions, dpmm, circle_mask

INCH_IN_MM = 25.4 #TODO more accurate value

class CircleToken(Token):
    """
    Represents circular tokens.
    """

    @classmethod
    def supported_types(cls):
        return {
            "Circle": {
                "radius": None, "border_color": "black", "fill_color": "white",
                "image_url": None, "border_url": None, "keep_aspect_ratio": True,
                "mask": "circle"
            }
        }

    def apply_defaults(self, config, resources):
        config = super().apply_defaults(config, resources)
        if config["image_url"] is not None:
            if config.get("radius") is None:
                dims = get_file_dimensions(resources["image_url"])
                config["radius"] = max(*dims) / (2*dpmm(config))
        else:
            if config.get("radius") is None:
                config["radius"] = INCH_IN_MM / 2
        return config

    def area(self, config, resources) -> Tuple[float, float]:
        radius = config["radius"]
        return 2 * radius, 2 * radius
    
    def _get_mask(self, config, dims):
        mask = config.get("mask")
        max_dim = max(dims)
        if mask == "circle":
            return circle_mask(max_dim // 2)
        else:
            return None

    def draw(self, canvas, config, resources, rect):
        radius = config["radius"]
        x, y, width, height = rect
        canvas.circle(x + width / 2, y + height / 2, radius, stroke=1, fill=1)
        keep_aspect_ratio = config.get("keep_aspect_ratio", True)
        
        if config.get("image_url") is not None:
            oim_width, oim_height = get_file_dimensions(resources["image_url"])
            im_width, im_height = new_dims(radius, (oim_width, oim_height), keep_aspect_ratio)
            mask = self._get_mask(config, (oim_width, oim_height))
            canvas.image(x + width / 2 - im_width / 2, y + height / 2 - im_height / 2, im_width, im_height, resources["image_url"], mask)
        if config.get("border_url") is not None:
            oim_width, oim_height = get_file_dimensions(resources["border_url"])
            im_width, im_height = new_dims(radius, (oim_width, oim_height), keep_aspect_ratio)
            mask = self._get_mask(config, (oim_width, oim_height))
            canvas.image(x + width / 2 - im_width / 2, y + height / 2 - im_height / 2, im_width, im_height, resources["border_url"], mask)
        return rect
    

def new_dims(radius, dims, keep_aspect_ratio):
    d = 2 * radius
    if not keep_aspect_ratio:
        return d, d
    aspect_ratio = dims[0] / dims[1]
    if aspect_ratio > 1:
        return d * aspect_ratio, d
    else:
        return d, d / aspect_ratio
   