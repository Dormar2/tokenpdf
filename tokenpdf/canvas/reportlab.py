from multiprocessing import context
from typing import Any, Dict, Tuple
from pathlib import Path
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.units import mm
from tokenpdf.utils.image import to_image, join_mask_channel
from contextlib import nullcontext
from collections import namedtuple
from tempfile import NamedTemporaryFile
from PIL import Image, ImageColor
from tokenpdf.utils.verbose import vprint, vtqdm
from tokenpdf.image import TokenImage
from .canvas import Canvas, CanvasPage
import contextlib
import numpy as np

class ReportLabCanvasPage(CanvasPage):
    """ """
    def __init__(self, canvas, width: float, height: float, background: str = None):
        super().__init__(canvas, (width, height))
        self.pdf_canvas = canvas.pdf
        self.width = width
        self.height = height
        self.background = background
        self.commands = []  # Store commands to execute for this page
        self.lastLineDash = None
        if background:
            self.commands.append(("image", 0, 0, width, height, background))

    def _execute_commands(self, verbose: bool = False):
        """Execute all drawing commands on the canvas.

        Args:
          verbose: bool:  (Default value = False)

        Returns:

        """
        tqdm = vtqdm(verbose)
        for command in tqdm(self.commands, desc="Executing Page Commands", leave=False):
            cmd_type = command[0]
            if cmd_type == "image":
                _, x, y, width, height, image, flip, angle = command
                rotate = -angle # Reportlab rotates clockwise
                
                with apply_image_filters(image, flip) as fimage:
                    bltagaim = reportlab_translation_for_rotation(self.height, height, (x, y), rotate)
                    # Now we can rotate around this point
                    with self._translation(*bltagaim), self._rotation(rotate):
                        image_param = fimage.image
                        if image_param.mode == "RGBA":
                            # Reportlab supports alpha channels, but they don't seem
                            # to work unless passed as a file path
                            image_param = fimage.path
                        self.pdf_canvas.drawImage(fimage.path, 0, 0, 
                                                    width * mm, height * mm, mask='auto')
            elif cmd_type == "text":
                _, x, y, text, font, size, rotate = command
                self.pdf_canvas.setFont(font, size)
                with self._rotation(rotate, (x, y)) as ((xr, yr),):
                    self.pdf_canvas.drawString(xr * mm, (self.height - yr) * mm, text)
            elif cmd_type == "circle":
                _, x, y, radius, stroke, fill = command
                self.pdf_canvas.circle(x * mm, (self.height - y) * mm, radius * mm, 
                                       stroke=int(stroke), fill=int(fill))
            elif cmd_type == "line":
                _, x1, y1, x2, y2, color, thickness, style = command
                with self._stroke_color(color), self._stroke_thickness(thickness), self._stroke_style(style):
                    self.pdf_canvas.line(x1 * mm, (self.height - y1) * mm, x2 * mm, (self.height - y2) * mm)
                
            elif cmd_type == "rect":
                _, x, y, width, height, thickness, fill, color, style, angle = command
                # Rect command needs the bottom left corner
                blx, bly = rotation_matrix(angle) @ np.array([0, height]) + np.array([x, y])
                #angle =  angle - np.pi/2
                angle *= -1 # Reportlab rotates clockwise
                bltagaim = blx,self.height-bly
                #bltagaim = reportlab_translation_for_rotation(self.height, height, (blx, #bly), angle)
                with self._stroke_color(color), self._stroke_style(style), \
                        self._translation(*bltagaim), self._rotation(angle):
                    self.pdf_canvas.rect(0,0, width * mm, height * mm, 
                                        stroke=thickness, fill=fill)
                

    def _image(self, x: float, y: float, width: float, height: float, image:TokenImage, 
              flip: Tuple[bool, bool] = (False, False), rotate: float = 0):
        """

        Args:
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
        self.commands.append(("image", x, y, width, height, image, flip, rotate))

    def text(self, x: float, y: float, text: str, font: str = "Helvetica", size: int = 12, rotate: float = 0):
        """

        Args:
          x: float: 
          y: float: 
          text: str: 
          font: str:  (Default value = "Helvetica")
          size: int:  (Default value = 12)
          rotate: float:  (Default value = 0)

        Returns:

        """
        self.commands.append(("text", x, y, text, font, size, rotate))

    def circle(self, x: float, y: float, radius: float, stroke: bool = True, fill: bool = False):
        """

        Args:
          x: float: 
          y: float: 
          radius: float: 
          stroke: bool:  (Default value = True)
          fill: bool:  (Default value = False)

        Returns:

        """
        self.commands.append(("circle", x, y, radius, stroke, fill))

    def line(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int] = (0, 0, 0), 
             thickness: float = 1, style: str = "solid"):
        """

        Args:
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
        self.commands.append(("line", x1, y1, x2, y2, color, thickness, style))
    
    def rect(self, x: float, y: float, width: float, height: float, thickness: int = 1, fill: int = 0,
            color: Tuple[int, int, int] = (0, 0, 0), style: str = "solid", angle: float = 0):
        """

        Args:
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
        self.commands.append(("rect", x, y, width, height, thickness, fill, color, style, angle))

    @contextlib.contextmanager
    def _stroke_color(self, color: Tuple[int, int, int] | str | None) -> contextlib.contextmanager:
        """Set the stroke color for the context.

        Args:
          color: Tuple[int: 
          int: 
          int] | str | None: 

        Returns:

        """
        if color is None:
            yield
            return
        if isinstance(color, str):
            color = ImageColor.getrgb(color)
        orig_color = self.pdf_canvas._strokeColorObj
        self.pdf_canvas.setStrokeColorRGB(*[c / 255 for c in color])
        yield
        self.pdf_canvas.setStrokeColorRGB(*orig_color)
    
    @contextlib.contextmanager
    def _stroke_style(self, style: str | None) -> contextlib.contextmanager:
        """Set the stroke style for the context.

        Args:
          style: str | None: 

        Returns:

        """
        if style is None:
            yield
            return
        #orig_style = self.pdf_canvas._lineDash
        orig_style = self.lastLineDash # Unfortunately, the original line style is not accessible
        pattern = []
        for s in style.split("-"):
            if s.lower() == "dot":
                pattern.extend([1, 2])
            elif s.lower() == "dash":
                pattern.extend([3, 2])
            elif s.lower() == "solid":
                pattern.extend([1, 0])
            else:
                try:
                    pattern.append(int(s))
                except ValueError:
                    raise ValueError(f"Invalid line style: {style}")
        self.pdf_canvas.setDash(pattern)
        self.lastLineDash = pattern
        yield
        if orig_style is not None:
            self.pdf_canvas.setDash(orig_style)

    @contextlib.contextmanager
    def _stroke_thickness(self, thickness: float | None) -> contextlib.contextmanager:
        """Set the stroke thickness for the context.

        Args:
          thickness: float | None: 

        Returns:

        """
        if thickness is None:
            yield
            return
        orig_thickness = self.pdf_canvas._lineWidth
        self.pdf_canvas.setLineWidth(thickness)
        yield
        self.pdf_canvas.setLineWidth(orig_thickness)
    @contextlib.contextmanager
    def _rotation(self, angle: float, *args) -> contextlib.contextmanager:
        """Rotate the canvas for the context.

        Args:
          angle: float: 
          *args: 

        Returns:

        """
        if angle == 0:
            yield args
            return
        self.pdf_canvas.saveState()
        # Reportlab rotates around the origin, which is at the bottom left
        self.pdf_canvas.rotate(angle*180/np.pi)
        yield args
        self.pdf_canvas.restoreState()
            

    @contextlib.contextmanager
    def _translation(self, x: float, y: float) -> contextlib.contextmanager:
        """Translate the canvas for the context.

        Args:
          x: float: 
          y: float: 

        Returns:

        """
        self.pdf_canvas.saveState()
        self.pdf_canvas.translate(x * mm, y * mm)
        yield
        self.pdf_canvas.restoreState()
class ReportLabCanvas(Canvas):
    """ """
    def __init__(self, config: Dict[str, Any], file_path: str | None = None):
        super().__init__(config, file_path)
        self.pdf = reportlab_canvas.Canvas(config.get("output_file", file_path))
        self.pages = []  # Track pages

    def create_page(self, size: Tuple[float, float], background: str = None) -> CanvasPage:
        """

        Args:
          size: Tuple[float: 
          float]: 
          background: str:  (Default value = None)

        Returns:

        """
        page = ReportLabCanvasPage(self, size[0], size[1], background)
        self.pages.append(page)
        return page

    def save(self, verbose: bool = False):
        """Finalize all pages and save the PDF.

        Args:
          verbose: bool:  (Default value = False)

        Returns:

        """
        
        tqdm = vtqdm(verbose)
        for page in tqdm(self.pages, desc="Saving pages"):
            self.pdf.setPageSize((page.width * mm, page.height * mm))
            page._execute_commands(verbose=verbose)  # Draw all commands for the page
            self.pdf.showPage()  # Finalize the page
        self.pdf.save()



def apply_image_filters(image:TokenImage, flip: Tuple[bool, bool] = (False, False), 
                        rotate: float = 0) -> TokenImage:
    """Apply filters to an image.

    Args:
      flip: A tuple of booleans indicating whether to flip the image
    horizontally and vertically.
      rotate: The angle to rotate the image.

    Returns:
      : The image with the filters applied.

    """
    
    if not image.masked and flip == (False, False) and rotate == 0:
        # null context with a name attribute for the image path
        return image

    # The mask parameter in reportlab only masks specific colours
    # we'll use the alpha channel instead
    image = image.join_mask(blend=True, allow_resize=True)
    

    image = image.flip(flip)
    if rotate:
        image = image.rotate(rotate * 180 / np.pi, expand=True)
    
    return image


def reportlab_translation_for_rotation(page_height, object_height, top_left, angle):
    """ This function calculates the translation needed before a reportlab-rotation 
        (which rotates around the bottom left) 
        that would have the same results as rotating around the top left,
        while respecting the reportlab coordinate system. """
    # Reportlab rotates around the origin, which is at the bottom left
    # So we need to find the bottom left corner of where we want to paint.
    # If we rotate, we need to find the bottom left corner of the rotated image
    # So rotate (0,h) by the angle around (0,0) and then translate by (x,y)
    x,y = top_left
    bl = np.array([0, object_height])
    M = rotation_matrix(angle)
    bltag = bl @ M + np.array([x, y])
    # Now invert y due to reportlab's coordinate system
    bltagaim = np.array([bltag[0], page_height - bltag[1]])
    return bltagaim

def rotation_matrix(angle):
    """ """
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])