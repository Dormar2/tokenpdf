from functools import lru_cache
from re import I
from PIL import Image
from pathlib import Path
from typing import Tuple
import numpy as np
import cv2

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


def find_background(image:np.ndarray, bins:int=64, background_colors:int=3) -> np.ndarray:
    image = np.asarray(image)
    initial_mask = None
    # Convert to grayscale
    if image.ndim == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 4:        
            gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            initial_mask = image[:, :, 3] <= 1
        elif image.shape[2] == 1:
            gray = image
        else:
            raise ValueError("Unsupported number of channels in image")
    else:
        gray = image
    hist = image_hist(gray, bins)
    # Find candidates for the background color
    # by selecting the N most common colors
    N = background_colors
    color_range = np.linspace(0, 255, bins+1).astype(np.uint8)
    background_colors = np.argsort(hist, axis=0)[-N:]
    

    # Now extract only boundary pixels:
    boundary = np.zeros(gray.shape, dtype=bool)
    boundary[[0, -1], :] = True
    boundary[:, [0, -1]] = True
    bpixels = gray[boundary].flatten()
    bhist = image_hist(bpixels, bins)
    
    result_mask = np.zeros(gray.shape, dtype=bool)
    # Only use common colors that are also high-ish in the boundary
    for b in background_colors:
        
        boundary_cover = bhist[b] / bpixels.size 
        if boundary_cover > 1/2:
            g = gray.flatten()

            mask = cv2.inRange(g, color_range[b], color_range[b+1]).astype(bool)
            result_mask |= mask.reshape(gray.shape)
    if initial_mask is not None:
        result_mask |= initial_mask
    return result_mask
    

def find_foreground_roi(image:np.ndarray, hist_bins:int=64, background_colors:int=3) -> Tuple[int, int, int, int]:
    mask = find_background(image, hist_bins, background_colors)
    mask = np.logical_not(mask)
    return mask_to_roi(mask)

def mask_to_roi(mask:np.ndarray) -> Tuple[int, int, int, int]:
    rect = cv2.boundingRect(mask.astype(np.uint8))
    return tuple(rect)

def image_hist(image: np.ndarray, bins: int = 64) -> np.ndarray:
    hist = cv2.calcHist([image], [0], None, [bins], [0, 256])
    return hist

def force_roi_aspect_ratio(roi:Tuple[int,int,int,int], dims:
                           Tuple[int,int]) -> Tuple[int,int,int,int]:

    
    def ao(roi):
        if isinstance(roi, float):
            return roi
        if len(roi) == 2:
            return roi[0] / roi[1]
        return ao(roi[2:])
    goal_ao = ao(dims)

    def to_bounds(roi_):
        rx,ry,rw,rh = roi_
        rx, ry = max(0, rx), max(0, ry)
        return rx, ry, min(dims[0], rx + rw) - rx, min(dims[1], ry + rh) - ry
    def fix_x(roi_):
        rx,ry,rw,rh = roi_
        extra = np.round(rh * goal_ao - rw).astype(int)
        return to_bounds((rx - extra // 2, ry, rw + extra, rh))
    def fix_y(roi_):
        rx,ry,rw,rh = roi_
        extra = np.round(rw / goal_ao - rh).astype(int)
        return to_bounds((rx, ry - extra // 2, rw, rh + extra))
    
    def compare_ao(roi1, roi2):
        ao1 = ao(roi1)
        ao2 = ao(roi2)
        if np.isclose(ao1, ao2, atol=1e-2):
            return 0
        return -1 if ao1 < ao2 else 1 

    #print("Goal AO:", goal_ao)
    #print("Initial AO:", ao(roi), roi)
    if compare_ao(goal_ao, roi) > 0:
        # Need to be wider
        roi = fix_x(roi)
    #print("Fixed X AO:", ao(roi), roi)
    if compare_ao(goal_ao, roi) < 0:
        # Need to be taller
        roi = fix_y(roi)
    #print("Fixed Y AO:", ao(roi), roi)

    # The previous adjustments may have not been enough, so we try reducing instead

    if compare_ao(goal_ao, roi) > 0:
        # Cannot make it wider, make it less tall
        roi = fix_y(roi)
    #print("Fixed Y AO:", ao(roi), roi)  
    if compare_ao(goal_ao, roi) < 0:
        # Cannot make it taller, make it less wide
        roi = fix_x(roi)
    #print("Fixed X AO:", ao(roi), roi)
    return roi
    