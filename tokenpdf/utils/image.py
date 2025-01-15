from functools import lru_cache
from re import I
from PIL import Image
from pathlib import Path
from typing import Tuple, Generator
import numpy as np
from tempfile import NamedTemporaryFile
from contextlib import contextmanager


@lru_cache(maxsize=None)
def get_file_dimensions(file_path: str | Image.Image) -> Tuple[int, int]:
    """
    Get the dimensions of an image file.
    :param file_path: The path to the image file.
    :return: A tuple of the width and height of the image.
    """
    if isinstance(file_path, Image.Image):
        return file_path.size
    with Image.open(file_path) as image:
        return image.size

def complete_size(width, height, image_width, image_height, keep_aspect_ratio:bool=False) -> Tuple[float, float]:
    """
    Complete the size of an object based on the image dimensions.
    :param width: The width of the object. (None or -1 to indicate auto)
    :param height: The height of the object. (None or -1 to indicate auto)
    :param image_width: The width of the image.
    :param image_height: The height of the image.
    :param keep_aspect_ratio: If True, keep the aspect ratio of the image.
    """
    no_width = width is None or width < 0
    no_height = height is None or height < 0
    if no_width and no_height:
        return image_width, image_height
    
    aspect_ratio = image_width / image_height
    if keep_aspect_ratio and not (no_width or no_height):
        if width / height > aspect_ratio:
            return width, width / aspect_ratio
        return height * aspect_ratio, height

    if no_width:
        return aspect_ratio * height, height
    return width, width / aspect_ratio
    

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

  

def TemporaryCropImageFile(image : Image.Image | Path | str,
                           roi: Tuple[int, int, int, int], 
                           delete: bool = True, suffix: str = ".png", **kw) -> NamedTemporaryFile:
    """Temporary file for cropped images."""
    if isinstance(image, Path) or isinstance(image, str):
        image = Image.open(image)
    roi = np.array(roi)
    roi_pil = (*roi[:2],*(roi[:2]+roi[2:]))
    cropped = image.crop(roi_pil)
    return TemporaryFilepathForImage(cropped, delete=delete, suffix=suffix, **kw)

@contextmanager
def TemporaryFilepathForImage(image : Image.Image | Path | str, delete: bool = True, suffix: str = ".png", **kw) -> Generator[NamedTemporaryFile, None, None]:
    """Temporary file for images."""
    if isinstance(image, Path) or isinstance(image, str):
        image = Image.open(image)
    with NamedTemporaryFile(suffix=suffix, delete=delete, delete_on_close=True) as tmp:
        tmp.close()
        image.save(tmp.name, **kw)
        yield tmp


def add_grid(img : Image.Image, grid: Tuple[int,int], color: str = "black") -> Image.Image:
    """
    Add a grid to an image.
    :param img: The image to add the grid to.
    :param grid: The grid size as a tuple of (width, height).
    :param color: The color of the grid.
    :return: The image with the grid added.
    """
    grid = np.round(np.array(grid)).astype(int)
    img = img.convert("RGBA")
    grid = np.array(grid)
    width, height = img.size
    x = np.linspace(0, width, grid[0]+1)
    y = np.linspace(0, height, grid[1]+1)
    cell_size = (x[1]-x[0], y[1]-y[0])
    line_thickness = max(1, int(min(cell_size) / 50))
    for i in range(grid[0]+1):
        for j in range(grid[1]+1):
            x0 = int(x[i])
            y0 = int(y[j])
            x1 = int(x[i] + cell_size[0])
            y1 = int(y[j] + cell_size[1])
            img.paste(color, (x0, y0, x1, y0+line_thickness))
            img.paste(color, (x0, y0, x0+line_thickness, y1))
    return img