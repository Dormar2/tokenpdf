from PIL import Image
from pathlib import Path
from typing import Tuple
import numpy as np

def get_file_dimensions(file_path: str) -> Tuple[float, float]:
    """
    Get the dimensions of an image file.
    :param file_path: The path to the image file.
    :return: A tuple of the width and height of the image.
    """
    with Image.open(file_path) as image:
        return image.size


def dpmm(config: dict, default:float = 300/25.4) -> float:
    """
    Calculate the dots per millimeter (dpmm) based on the configuration.
    :param config: The configuration dictionary.
    :return: The calculated dpmm value.
    """
    return config.get("dpmm", config.get("dpi", default*25.4)/25.4)


def to_float_np_image(arr:np.ndarray) -> np.ndarray:
    """
    Convert an array to float32 and normalize the values to the range [0, 1].
    Arrays of type float are assumed to be already normalized.
    """
    if arr.dtype == bool:
        return arr.astype(np.float32)
    elif arr.dtype == np.uint8:
        return arr.astype(np.float32) / 255
    elif arr.dtype in (np.float32, np.float64):
        return arr
    else:
        raise ValueError(f"Unsupported array type: {arr.dtype}")

def to_uint8_np_image(arr:np.ndarray) -> np.ndarray:
    """
    Convert an array to uint8 and scale the values to the range [0, 255].
    Arrays of type uint8 and float are assumed to be normalized.
    """
    if arr.dtype == np.uint8:
        return arr
    return (to_float_np_image(arr) * 255).astype(np.uint8)

def join_mask_channel(image: Image.Image, mask: np.ndarray,
                      blend:bool = False, allow_resize:bool = False) -> Image.Image:
    """
    Join the mask as an alpha channel to the image.
    :param image: The image to add the mask to.
    :param mask: The mask as a boolean array.
    :param blend: If True and image has an alpha channel, blend the mask with the alpha channel.
    :return: The image with the mask as an alpha channel.
    """
    if image.mode == "RGBA" and blend:
        image_alpha = np.array(image)[:, :, 3]
        mask_alpha = to_float_np_image(np.array(mask))
        mask = image_alpha * mask_alpha
    
    mask = to_uint8_np_image(np.array(mask))
     
    mask_image = Image.fromarray(mask)
    if allow_resize and mask_image.size != image.size:
        mask_image = mask_image.resize(image.size, Image.NEAREST)
    image.putalpha(mask_image)
    return image

def circle_mask(radius):
    x = np.linspace(-radius, radius, np.round(2 * radius).astype(int))
    y = np.linspace(-radius, radius, np.round(2 * radius).astype(int))
    X, Y = np.meshgrid(x, y)
    mask = X**2 + Y**2 <= radius**2
    return to_image(mask)

def to_image(obj):
    if isinstance(obj, Image.Image):
        return obj
    elif isinstance(obj, str) or isinstance(obj, Path):
        return Image.open(obj)
    elif isinstance(obj, np.ndarray):
        if obj.dtype == bool:
            obj = obj.astype(np.uint8) * 255
        return Image.fromarray(obj)
    else:
        raise ValueError("Unsupported object type for conversion to image.")