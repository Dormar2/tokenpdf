from functools import lru_cache
from re import I
from PIL import Image
from pathlib import Path
from typing import Tuple
import numpy as np


def get_file_dimensions(file_path: str | Image.Image) -> Tuple[int, int]:
    """Get the dimensions of an image file.
       Uses an LRU cache on specific files paths, so if the state of the file changes
        (detected using modification time), the cache for that file is invalidated.

    Args:
      file_path: The path to the image file.
      file_path: str | Image.Image: 

    Returns:
      : A tuple of the width and height of the image.

    """
    @lru_cache(maxsize=None)
    def _get_file_dimensions(file_path_: Path, version: int) -> Tuple[int, int]:
        """ Gets the dimensions with a dummy version number to invalidate the cache
        when necessary."""
        with Image.open(file_path_) as image:
            return image.size, file_path_.stat().st_mtime
        
    if isinstance(file_path, Image.Image):
        return file_path.size
    file_path = Path(file_path)
    result = None
    version = 0
    file_m_time = file_path.stat().st_mtime
    # Get the most updated version of the result
    while True:
        result, last_mtime = _get_file_dimensions(file_path, version)
        if last_mtime >= file_m_time:
            break
        version += 1
    return result
    

def complete_size(width, height, image_width, image_height, keep_aspect_ratio:bool=False) -> Tuple[float, float]:
    """Complete the size of an object based on the image dimensions.

    Args:
      width: The width of the object. (None or -1 to indicate auto)
      height: The height of the object. (None or -1 to indicate auto)
      image_width: The width of the image.
      image_height: The height of the image.
      keep_aspect_ratio: If True, keep the aspect ratio of the image.
      keep_aspect_ratio:bool:  (Default value = False)


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
    """Calculate the dots per millimeter (dpmm) based on the configuration.

    Args:
      config: The configuration dictionary.
      default:float:  (Default value = 300/25.4), equivalent to 300 dpi.

    Returns:
      : The calculated dpmm value.

    """
    return config.get("dpmm", config.get("dpi", default*25.4)/25.4)


def to_float_np_image(arr:np.ndarray) -> np.ndarray:
    """Convert an array to float32 and normalize the values from [0, 255] to [0, 1].
    Arrays of type float are assumed to be already normalized.

    Args:
      arr:np.ndarray: Array to convert.

    Returns:
        : A normalized float32 array.
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
    """Convert an array to uint8 and scale the values from [0, 1] to [0, 255] if necessary.
    Arrays of type uint8 are assumed to be already scaled to [0, 255].
    Arrays of type float are assumed to be normalized to [0, 1].

    Args:
      arr:np.ndarray: Array to convert (see description).

    Returns:
        : A uint8 array.

    """
    if arr.dtype == np.uint8:
        return arr
    return (to_float_np_image(arr) * 255).astype(np.uint8)

def join_mask_channel(image: Image.Image, mask: np.ndarray,
                      blend:bool = False, allow_resize:bool = False) -> Image.Image:
    """Join the mask as an alpha channel to the image.

    Args:
      image: The image to add the mask to.
      mask: The mask as a boolean array.
      blend: If True and image has an alpha channel, blend the mask
    with the alpha channel (by multiplying the alpha values).
      image: Image.Image: 
      allow_resize:bool:  If True, resize the mask to the image size if necessary.

    Returns:
      : The image with the mask as an alpha channel (or blended into the alpha channel).

    """
    if image.mode == "RGBA" and blend:
        image_alpha = np.array(image)[:, :, 3]
        mask_alpha = to_float_np_image(np.array(mask))
        if allow_resize and mask_alpha.shape != image_alpha.shape:
            mask_alpha = np.asarray(Image.fromarray(to_uint8_np_image(mask_alpha)).resize(image.size, Image.NEAREST))
        mask = image_alpha * mask_alpha
    
    mask = to_uint8_np_image(np.array(mask))
     
    mask_image = Image.fromarray(mask)
    if allow_resize and mask_image.size != image.size:
        mask_image = mask_image.resize(image.size, Image.NEAREST)
    image.putalpha(mask_image)
    return image

def circle_mask(radius):
    """
    Creates a circular boolean mask of size (2*radius, 2*radius), as a PIL image.

    Args:
      radius: The radius of the circle, in pixels.

    Returns:
        : The mask as a uint8 PIL image (0 for False, 255 for True).

    """
    x = np.linspace(-radius, radius, np.round(2 * radius).astype(int))
    y = np.linspace(-radius, radius, np.round(2 * radius).astype(int))
    X, Y = np.meshgrid(x, y)
    mask = X**2 + Y**2 <= radius**2
    return to_image(mask)

def to_image(obj: Image.Image | Path | str | np.ndarray) -> Image.Image:
    """
    Convert an object to a PIL image.

    Args:
      obj: Image.Image: A PIL image object, returned as is.
      obj: Path | str: A path to an image file, opened with PIL.
      obj: np.ndarray: A numpy array, converted to a PIL image. Must be uint8, bool, or float32 (assumed normalized)

    Returns:
        : The PIL image.

    """
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


def add_grid(img : Image.Image, grid: Tuple[int,int], color: str = "black",
             thickness: int | None = None) -> Image.Image:
    """Add a grid to an image with the color and thickness specified.

    Args:
      img: The image to add the grid to.
      grid: The grid size as a tuple of (width, height).
      color: The color of the grid lines (Default value = "black").      
      thickness: int | None: The thickness of the grid lines. If None, it is automatically calculated based on the cell size.

    Returns:
      : The image with the grid added.

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