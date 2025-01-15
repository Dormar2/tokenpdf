from typing import Tuple, Dict, Any
from pathlib import Path
from PIL import Image
import numpy as np
from tokenpdf.utils.image import TemporaryFilepathForImage, get_file_dimensions
import logging 
class CanvasPage:
    """Base class for a single page in a canvas."""

    def __init__(self, canvas: "Canvas"):
        """Initializes a new page in the canvas.

        Args:
            canvas: The parent canvas.
        """
        self.canvas = canvas
        self.optimize_images_quality = canvas.config.get("optimize_image_quality", 0)
        self.optimize_images_for_dpmm = canvas.config.get(
                                    "optimize_images_for_dpmm", 
                                    canvas.config.get("optimize_images_for_dpi", 0) / 25.4)
        self.pil_save_kw = {"optimize": True,
                            "format": "PNG"}
        if self.optimize_images_quality:
            self.pil_save_kw["quality"] = self.optimize_images_quality
    
    
    def image(self, x: float, y: float, width: float, height: float, image_path: str, mask: Any = None,
              flip: Tuple[bool, bool] = (False, False), rotate: float = 0):
        """Draws an image on the page, possibly with image optimization.

        Args:
            x: X-coordinate in mm.
            y: Y-coordinate in mm.
            width: Width of the image in mm.
            height: Height of the image in mm.
            image_path: Path to the image file.
            mask: Optional mask for the image.
            flip: Tuple of (horizontal, vertical) flip flags.
            rotate: Rotation angle in radians.
        """
        goaldpmm = self.optimize_images_for_dpmm
        optquality = self.optimize_images_quality
        if not optquality and not goaldpmm:
            return self._image(x, y, width, height, image_path, mask, flip, rotate)
        scale = 1.0
        if goaldpmm:
            iw, ih = get_file_dimensions(image_path)
            if (iw < ih) != (width < height):
                iw, ih = ih, iw
            cur_dpmm = np.array([iw, ih]) / np.array([width, height])
            cur_dpmm = max(cur_dpmm)
            if cur_dpmm > goaldpmm:
                scale = goaldpmm / cur_dpmm
        image = image_path if isinstance(image_path, Image.Image) else Image.open(image_path)
        if scale != 1.0:
            image = image.resize((int(round(image.width * scale)), int(round(image.height * scale))), Image.LANCZOS)
        new_mask = mask
        if scale!=1.0 and mask is not None:
            new_mask = mask.resize((int(round(mask.width * scale)), int(round(mask.height * scale))), Image.LANCZOS)
        with TemporaryFilepathForImage(image, delete=False, suffix=".png", **self.pil_save_kw) as tmp:
            self.canvas.add_cleanup(tmp.name)
            self._image(x, y, width, height, tmp.name, new_mask, flip, rotate)

        

    
    def _image(self, x: float, y: float, width: float, height: float, image_path: str, mask: Any = None,
               flip: Tuple[bool, bool] = (False, False), rotate: float = 0):
        """Draws an image on the page.

        Args:
            x: X-coordinate in mm.
            y: Y-coordinate in mm.
            width: Width of the image in mm.
            height: Height of the image in mm.
            image_path: Path to the image file.
            mask: Optional mask for the image.
            flip: Tuple of (horizontal, vertical) flip flags.
            rotate: Rotation angle in radians.
        """
        pass

    
    def text(self, x: float, y: float, text: str, font: str = "Helvetica", size: int = 12, rotate: float = 0):
        """Draws text on the page.

        Args:
            x: X-coordinate in mm.
            y: Y-coordinate in mm.
            text: The text content to draw.
            font: Font name.
            size: Font size in points.
            rotate: Rotation angle in radians.
        """
        pass

    
    def circle(self, x: float, y: float, radius: float, stroke: bool = True, fill: bool = False):
        """Draws a circle on the page.

        Args:
            x: X-coordinate of the center in mm.
            y: Y-coordinate of the center in mm.
            radius: Radius of the circle in mm.
            stroke: Whether to stroke the circle.
            fill: Whether to fill the circle.
        """
        pass

    
    def line(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int] = (0, 0, 0),
             thickness: float = 1, style: str = "solid"):
        """Draws a line on the page.

        Args:
            x1: X-coordinate of the starting point in mm.
            y1: Y-coordinate of the starting point in mm.
            x2: X-coordinate of the ending point in mm.
            y2: Y-coordinate of the ending point in mm.
        """
        pass

    
    def rect(self, x: float, y: float, width: float, height: float, stroke: int = 1, fill: int = 0,
                color: Tuple[int, int, int] = (0, 0, 0), style: str = "solid"):
        """Draws a rectangle on the page.

        Args:
            x: X-coordinate of the top-left corner in mm.
            y: Y-coordinate of the top-left corner in mm.
            width: Width of the rectangle in mm.
            height: Height of the rectangle in mm.
            stroke: Whether to stroke the rectangle.
            fill: Whether to fill the rectangle.
        """
        pass


class Canvas:
    """Baseclass for a canvas to manage multiple pages."""

    def __init__(self, config: Dict[str, Any], file_path: str | None = None):
        """Initializes the canvas with a given configuration and output file path.

        Args:
            config: Dictionary of configuration options for the canvas.
            file_path: Path to the output file.
        """
        self.config = config
        self.file_path = file_path if file_path else config["output_file"]
        self.files_cleanup = []

    
    def create_page(self, size: Tuple[float, float], background: str = None) -> CanvasPage:
        """Creates a new page in the canvas.

        Args:
            size: Tuple of (width, height) in mm.
            background: Optional path to a background image.

        Returns:
            An instance of CanvasPage.
        """
        pass

    
    def save(self, verbose: bool = False):
        """Finalizes and saves the canvas to the output file."""
        pass

    def add_cleanup(self, file_path: str):
        """Adds a file to the cleanup list.

        Args:
            file_path: Path to the file to cleanup.
        """
        self.files_cleanup.append(Path(file_path))

    def cleanup(self):
        """Cleans up all temporary files."""
        for file_path in self.files_cleanup:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logging.warning(f"Failed to cleanup file {file_path}: {e}")
