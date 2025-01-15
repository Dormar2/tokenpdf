from multiprocessing import context
from typing import Any, Dict, Tuple
from pathlib import Path
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.units import mm
from tokenpdf.utils.image import to_image, join_mask_channel
from contextlib import nullcontext
from collections import namedtuple
from tempfile import NamedTemporaryFile
from .canvas import Canvas, CanvasPage
from PIL import Image, ImageColor
from tokenpdf.utils.verbose import vprint, vtqdm
import contextlib
import numpy as np

class ReportLabCanvasPage(CanvasPage):
    def __init__(self, canvas, width: float, height: float, background: str = None):
        super().__init__(canvas)
        self.pdf_canvas = canvas.pdf
        self.width = width
        self.height = height
        self.background = background
        self.commands = []  # Store commands to execute for this page
        self.lastLineDash = None
        if background:
            self.commands.append(("image", 0, 0, width, height, background))

    def _execute_commands(self, verbose: bool = False):
        """Execute all drawing commands on the canvas."""
        tqdm = vtqdm(verbose)
        for command in tqdm(self.commands, desc="Executing Page Commands", leave=False):
            cmd_type = command[0]
            if cmd_type == "image":
                _, x, y, width, height, image_path, mask, flip, rotate = command
                
                with apply_image_filters(image_path, mask, flip, rotate, **self.pil_save_kw) as img_path:
                    self.canvas.add_cleanup(img_path.name)
                    self.pdf_canvas.drawImage(img_path.name, x * mm, (self.height - y - height) * mm, 
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
                _, x, y, width, height, stroke, fill, color, style = command
                with self._stroke_color(color), self._stroke_style(style):
                    self.pdf_canvas.rect(x * mm, (self.height - y - height) * mm, width * mm, height * mm, 
                                        stroke=stroke, fill=fill)
                

    def _image(self, x: float, y: float, width: float, height: float, image_path: str, mask: Any = None,
              flip: Tuple[bool, bool] = (False, False), rotate: float = 0):
        self.commands.append(("image", x, y, width, height, image_path, mask, flip, rotate))

    def text(self, x: float, y: float, text: str, font: str = "Helvetica", size: int = 12, rotate: float = 0):
        self.commands.append(("text", x, y, text, font, size, rotate))

    def circle(self, x: float, y: float, radius: float, stroke: bool = True, fill: bool = False):
        self.commands.append(("circle", x, y, radius, stroke, fill))

    def line(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int] = (0, 0, 0), 
             thickness: float = 1, style: str = "solid"):
        self.commands.append(("line", x1, y1, x2, y2, color, thickness, style))
    
    def rect(self, x: float, y: float, width: float, height: float, stroke: int = 1, fill: int = 0,
            color: Tuple[int, int, int] = (0, 0, 0), style: str = "solid"):
        self.commands.append(("rect", x, y, width, height, stroke, fill, color, style))

    @contextlib.contextmanager
    def _stroke_color(self, color: Tuple[int, int, int] | str | None) -> contextlib.contextmanager:
        """Set the stroke color for the context."""
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
        """Set the stroke style for the context."""
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
        """Set the stroke thickness for the context."""
        if thickness is None:
            yield
            return
        orig_thickness = self.pdf_canvas._lineWidth
        self.pdf_canvas.setLineWidth(thickness)
        yield
        self.pdf_canvas.setLineWidth(orig_thickness)
    @contextlib.contextmanager
    def _rotation(self, angle: float, *args) -> contextlib.contextmanager:
        """Rotate the canvas for the context."""
        if angle == 0:
            yield args
            return
        self.pdf_canvas.rotate(angle)
        # args is a sequence of x,y pairs, we need to find out where they went
        # after the rotation
        new_args = []
        for x, y in args:
            x, y = x * np.cos(angle) - y * np.sin(angle), x * np.sin(angle) + y * np.cos(angle)
            new_args.append((x, y))
        yield new_args
        self.pdf_canvas.rotate(-angle)


class ReportLabCanvas(Canvas):
    def __init__(self, config: Dict[str, Any], file_path: str | None = None):
        super().__init__(config, file_path)
        self.pdf = reportlab_canvas.Canvas(config.get("output_file", file_path))
        self.pages = []  # Track pages

    def create_page(self, size: Tuple[float, float], background: str = None) -> CanvasPage:
        page = ReportLabCanvasPage(self, size[0], size[1], background)
        self.pages.append(page)
        return page

    def save(self, verbose: bool = False):
        """Finalize all pages and save the PDF."""
        
        tqdm = vtqdm(verbose)
        for page in tqdm(self.pages, desc="Saving pages"):
            self.pdf.setPageSize((page.width * mm, page.height * mm))
            page._execute_commands(verbose=verbose)  # Draw all commands for the page
            self.pdf.showPage()  # Finalize the page
        self.pdf.save()



def apply_image_filters(image_path, mask=None, flip: Tuple[bool, bool] = (False, False), 
                        rotate: float = 0, **kw) -> NamedTemporaryFile:
    """
    Apply filters to an image.
    :param mask: The mask to apply to the image.
    :param flip: A tuple of booleans indicating whether to flip the image horizontally and vertically.
    :param rotate: The angle to rotate the image.
    :return: A context to hold the file on disk
    """
    
    if mask is None and flip == (False, False) and rotate == 0:
        # null context with a name attribute for the image path
        return nullcontext(namedtuple("context", ["name"])(image_path))
    image = to_image(image_path)
    if mask is not None:
        # The mask parameter only masks specific colours
        # we'll use the alpha channel instead
        image = join_mask_channel(image, mask, blend=True, allow_resize=True)
    

    if flip[0]:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if flip[1]:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    if rotate:
        image = image.rotate(rotate * 180 / np.pi, expand=True)
    
    context = NamedTemporaryFile(suffix=".png", delete=False)
    
    path = Path(context.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    #context.close()  # Close the file so that the image can be saved to it
    image.save(path, **kw)
    return context


