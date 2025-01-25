
import math
from typing import Tuple
from PIL import Image
import numpy as np
from .token import Token
from tokenpdf.utils.image import get_file_dimensions, dpmm, circle_mask

INCH_IN_MM = 25.4 #TODO more accurate value

class CircleToken(Token):
    """Represents circular tokens."""

    @classmethod
    def supported_types(cls):
        """ """
        return {
            "Circle": {
                "radius": None, "border_color": "black", "fill_color": "white",
                "image_url": None, "border_url": None, "keep_aspect_ratio": True,
                "mask": "circle"
            }
        }

    def apply_defaults(self, config, resources):
        """

        Args:
          config: 
          resources: 

        Returns:

        """
        config = super().apply_defaults(config, resources)
        if config["image_url"] is not None:
            if config.get("radius") is None:
                dims = resources[config["image_url"]].dims
                config["radius"] = max(*dims) / (2*dpmm(config))
        else:
            if config.get("radius") is None:
                config["radius"] = INCH_IN_MM / 2
        return config

    def area(self, config, resources) -> Tuple[float, float]:
        """

        Args:
          config: 
          resources: 

        Returns:

        """
        radius = config["radius"]
        return 2 * radius, 2 * radius
    
    def _get_mask(self, config, dims):
        """

        Args:
          config: 
          dims: 

        Returns:

        """
        mask = config.get("mask")
        max_dim = max(dims)
        if mask == "circle":
            return circle_mask(max_dim // 2)
        else:
            return None

    def draw(self, view, config, resources):
        """

        Args:
          canvas: 
          config: 
          resources: 
          rect: 

        Returns:

        """
        super().draw(view, config, resources)
        radius = config["radius"]
        width, height = view.size
        view.circle(width / 2, height / 2, radius, stroke=1, fill=1)
        keep_aspect_ratio = config.get("keep_aspect_ratio", True)
        
        if config.get("image_url") is not None:
            image = resources[config["image_url"]]
            oim_width, oim_height = image.dims
            im_width, im_height = new_dims(radius, (oim_width, oim_height), keep_aspect_ratio)
            mask = self._get_mask(config, (oim_width, oim_height))
            image = image.add_mask(mask)
            view.image(width / 2 - im_width / 2, height / 2 - im_height / 2, im_width, im_height, image)
        if config.get("border_url") is not None:
            border_image = resources[config["border_url"]]
            oim_width, oim_height = border_image.dims
            im_width, im_height = new_dims(radius, (oim_width, oim_height), keep_aspect_ratio)
            mask = self._get_mask(config, (oim_width, oim_height))
            border_image = border_image.add_mask(mask)
            view.image(width / 2 - im_width / 2, height / 2 - im_height / 2, im_width, im_height, border_image)
        
    

def new_dims(radius, dims, keep_aspect_ratio):
    """

    Args:
      radius: 
      dims: 
      keep_aspect_ratio: 

    Returns:

    """
    d = 2 * radius
    if not keep_aspect_ratio:
        return d, d
    aspect_ratio = dims[0] / dims[1]
    if aspect_ratio > 1:
        return d, d / aspect_ratio
    else:
        return d * aspect_ratio, d
   