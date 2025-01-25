from typing import Tuple, Dict, Any, Sequence
from pathlib import Path
from PIL import Image
import numpy as np
from tokenpdf.utils.image import TemporaryFilepathForImage, get_file_dimensions
import logging 
import cv2



class CanvasPage:
    """Base class for a single page in a canvas."""

    def __init__(self, canvas: "Canvas", size: Tuple[float, float]):
        """Initializes a new page in the canvas.

        Args:
            canvas: The parent canvas.
        """
        self._page_size = size
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
          x: float: 
          y: float: 
          width: float: 
          height: float: 
          image_path: str: 
          mask: Any:  (Default value = None)
          flip: Tuple[bool: 
          bool]:  (Default value = (False)
          False): 
          rotate: float:  (Default value = 0)

        Returns:

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
          x: float: 
          y: float: 
          width: float: 
          height: float: 
          image_path: str: 
          mask: Any:  (Default value = None)
          flip: Tuple[bool: 
          bool]:  (Default value = (False)
          False): 
          rotate: float:  (Default value = 0)

        Returns:

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
          x: float: 
          y: float: 
          text: str: 
          font: str:  (Default value = "Helvetica")
          size: int:  (Default value = 12)
          rotate: float:  (Default value = 0)

        Returns:

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
          x: float: 
          y: float: 
          radius: float: 
          stroke: bool:  (Default value = True)
          fill: bool:  (Default value = False)

        Returns:

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
          x1: float: 
          y1: float: 
          x2: float: 
          y2: float: 
          color: Tuple[int: 
          int: 
          int]:  (Default value = (0)
          0: 
          0): 
          thickness: float:  (Default value = 1)
          style: str:  (Default value = "solid")

        Returns:

        """
        pass

    
    def rect(self, x: float, y: float, width: float, height: float, thickness: int = 1, fill: int = 0,
                color: Tuple[int, int, int] = (0, 0, 0), style: str = "solid", rotate: float = 0):
        """Draws a rectangle on the page.

        Args:
          x: X-coordinate of the top-left corner in mm.
          y: Y-coordinate of the top-left corner in mm.
          width: Width of the rectangle in mm.
          height: Height of the rectangle in mm.
          thickness: The thickness the rectangle.
          fill: Whether to fill the rectangle.
          x: float: 
          y: float: 
          width: float: 
          height: float: 
          stroke: int:  (Default value = 1)
          fill: int:  (Default value = 0)
          color: Tuple[int: 
          int: 
          int]:  (Default value = (0)
          0: 
          0): 
          style: str:  (Default value = "solid")

        Returns:

        """
        pass


    def view(self, x: float, y: float, width: float, height: float, angle:float=0) -> "CanvasPageView":
        """Creates a view of a part of the page.
            Elements can be drawn relative to the returned view.

        Args:
          x: X-coordinate of the top-left corner in mm.
          y: Y-coordinate of the top-left corner in mm.
          width: Width of the view in mm.
          height: Height of the view in mm.
          angle: Rotation angle in radians. (Default = 0)

        Returns:
          : An instance of CanvasPageView.

        """
        return CanvasPageView(self, (x, y, width, height), angle)

    def hbox(self, n:int = None, weights : Sequence[float] = None, spacing: float = 0, sizing:Tuple[float,float] = None, return_spacing:bool=False) -> Sequence["CanvasPageView"]:
        """Creates a horizontal box layout that covers the entire page (or view)
            n or weights must be provided.

        Args:
          n: Number of elements in the layout. (Default = None)
          weights: List of weights for each element. (Default = None)
          spacing: Spacing between elements, in mm. (Default = 0)
          sizing: If provided, the width and height of the layout. (Default = None)

        Returns:
          : An instance of CanvasHBox.

        """
        w,h = self._page_size if sizing is None else sizing
        if weights is None:
            if n is None:
                raise ValueError("Either n or weights must be provided")
            weights = [1] * n
        else:
            n = len(weights)
        if n != len(weights):
            raise ValueError("Length of weights must match n")
        spacing_weight = spacing / w
        total_weight = sum(weights) + spacing_weight * (n - 1)
        if return_spacing:
            n_total = n + (n-1)
            all_weights = np.zeros(n_total)
            all_weights[::2] = weights
            all_weights[1::2] = spacing_weight
            return self.hbox(n_total, all_weights, 0, (w,h), return_spacing=False)
        widths = [w * weight / total_weight for weight in weights]
        start_x = np.cumsum([0] + widths[:-1])
        views = [
            self.view(x, 0, width, h)
            for x, width in zip(start_x, widths)
        ]
        return views
    
    def vbox(self, n:int = None, weights : Sequence[float] = None, spacing: float = 0, sizing:Tuple[float,float] = None, return_spacing:bool = False) -> Sequence["CanvasPageView"]:
        """Creates a vertical box layout that covers the entire page (or view)
            See `hbox` for details. """
        sizing = (self._page_size if sizing is None else sizing)[::-1]
        return [view.T for view in self.hbox(n, weights, spacing, sizing, return_spacing=return_spacing)]

    
    def as_view(self) -> "CanvasPageView":
        """Returns a view of the entire page."""
        return self.view(0, 0, *self._page_size)
    
    def margin_view(self, ratio:float, regular:bool=True) -> "CanvasPageView":
        """Returns a view of the page with a margin.

        Args:
          ratio: The ratio of the margin to the page size.
          regular: If True, the margin is the same on all sides.

        Returns:
          : An instance of CanvasPageView.

        """
        return self.as_view().margin_view(ratio, regular)



class CanvasPageView(CanvasPage):
    def __init__(self, page, view_rect: Tuple[float, float, float, float], angle:float = 0):
        self.page = page
        self.view_rect = view_rect
        self.angle = angle
    
    @property
    def size(self) -> Tuple[float, float]:
        return np.array(self.view_rect[2:])

    def image(self, x, y, width, height, image_path, mask = None, flip = (False, False), rotate = 0):
        if width is None:
            width = self.size[0]
        if height is None:
            height = self.size[1]
        x, y = self._transform(x, y)
        self.page.image(x, y, width, height, image_path, mask, flip, rotate + self.angle)
    
    def text(self, x, y, text, font = "Helvetica", size = 12, rotate = 0):
        x, y = self._transform(x, y)
        self.page.text(x, y, text, font, size, rotate)
    
    def circle(self, x, y, radius, stroke = True, fill = False):
        x, y = self._transform(x, y)
        self.page.circle(x, y, radius, stroke, fill)
    
    def line(self, x1, y1, x2, y2, color = (0, 0, 0), thickness = 1, style = "solid"):
        x1, y1 = self._transform(x1, y1)
        x2, y2 = self._transform(x2, y2)
        self.page.line(x1, y1, x2, y2, color, thickness, style)
    
    def rect(self, x, y, width, height, thickness = 1, fill = 0, color = (0, 0, 0), style = "solid", rotate:float=0):
        x, y = self._transform(x, y)
        self.page.rect(x, y, width, height, thickness, fill, color, style, rotate + self.angle)
    
    def _transform(self, x, y, rotation_only = False, translation_only = False):
        M = self._affine_matrix()
        if rotation_only:
            return np.dot(M, [x, y, 0])[:2]
        if translation_only:
            return M[:2, 2]+[x, y]
        return np.dot(M, [x, y, 1])[:2]
    
    def _transform_inv(self, x, y):
        M = np.linalg.inv(self._affine_matrix())
        return np.dot(M, [x, y, 1])[:2]
    
    def resize(self, width, height):
        return self.page.view(*self.view_rect[:2], width, height, self.angle)
    
    def translate(self, dx, dy):
        drx, dry = self._transform(dx, dy, rotation_only=True)
        return self.page.view(
            drx + self.view_rect[0],
            dry + self.view_rect[1],
            *self.view_rect[2:], self.angle
        )
    
    def rotate(self, angle):
        return self.page.view(*self.view_rect, self.angle + angle)

    
    def _affine_matrix(self):
        x0, y0, _, _ = self.view_rect
        translation = np.array([
            [1, 0, x0],
            [0, 1, y0],
            [0, 0, 1]
        ])
        if not self.angle:
            return translation
        # We want rotation by angle clockwise around the origin,
        # from the x-axis to the y-axis.
        # Note that y-axis is inverted because we work in image coordinates.
        # So positive x (right) to positive y (down) means clockwise rotation.
        rotation = np.array([
            [np.cos(self.angle), -np.sin(self.angle), 0],
            [np.sin(self.angle), np.cos(self.angle), 0],
            [0, 0, 1]
        ])
        return np.dot(translation, rotation)

    
    @property
    def T(self) -> "CanvasPageView":
        """ Returns a transposed view of the current view. """
        x0, y0, w, h = self.view_rect
        return self.page.view(y0, x0, h, w, self.angle)

    def view(self, x, y, width, height, angle: float = 0) -> "CanvasPageView":
        x0, y0 = self._transform(x, y)
        return self.page.view(x0, y0, width, height, self.angle + angle)
    
    def relative_view(self, view: "CanvasPageView") -> "CanvasPageView":
        x0, y0 = self._transform(*view.view_rect[:2])
        return self.page.view(x0, y0, *view.size, self.angle + view.angle)
    
    def hbox(self, n:int = None, weights : Sequence[float] = None, spacing: float = 0, sizing:Tuple[float,float] = None, return_spacing:bool=False) -> Sequence["CanvasPageView"]:
        """ See `CanvasPage.hbox` """
        sizing = (self.view_rect[2], self.view_rect[3]) if sizing is None else sizing
        return [
            self.relative_view(view)
            for view in self.page.hbox(n, weights, spacing, sizing, return_spacing=return_spacing)
        ]
    
    def vbox(self, n:int = None, weights : Sequence[float] = None, spacing: float = 0, sizing:Tuple[float,float] = None, return_spacing:bool=False) -> Sequence["CanvasPageView"]:
        """ See `CanvasPage.vbox` """
        sizing = (self.view_rect[2], self.view_rect[3]) if sizing is None else sizing
        return [
            self.relative_view(view)
            for view in self.page.vbox(n, weights, spacing, sizing, return_spacing=return_spacing)
        ]
    
    def margin_view(self, ratio:float, regular:bool=True):
        ratio = np.clip(ratio, 0, 1)
        if regular:
            margin = np.min(self.size) * ratio
            margin = np.array([margin, margin])
        else:
            margin = np.array(self.size) * ratio
        return self.translate(*margin).resize(*(self.size - 2*margin))

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
          size: Tuple[float: 
          float]: 
          background: str:  (Default value = None)

        Returns:
          : An instance of CanvasPage.

        """
        pass

    
    def save(self, verbose: bool = False):
        """Finalizes and saves the canvas to the output file.

        Args:
          verbose: bool:  (Default value = False)

        Returns:

        """
        pass

    def add_cleanup(self, file_path: str):
        """Adds a file to the cleanup list.

        Args:
          file_path: Path to the file to cleanup.
          file_path: str: 

        Returns:

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
