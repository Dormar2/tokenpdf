from typing import Tuple
import numpy as np
import cv2
from .image_filter import ImageFilter

class ZoomToROI(ImageFilter, name="zoom"):
    def filter(self, image):
        return image.crop_foreground_roi()

class ForegroundFilter(ImageFilter, name="foreground"):
    def filter(self, image):
        mask = image.foreground.as_array()
        return image.add_mask(mask)
    

