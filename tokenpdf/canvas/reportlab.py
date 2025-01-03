from typing import Any, Dict, Tuple
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.units import mm
from tokenpdf.utils.image import to_image, join_mask_channel
from contextlib import nullcontext
from collections import namedtuple
from tempfile import NamedTemporaryFile
from .canvas import Canvas, CanvasPage

class ReportLabCanvasPage(CanvasPage):
    def __init__(self, pdf_canvas, width: float, height: float, background: str = None):
        self.pdf_canvas = pdf_canvas
        self.width = width
        self.height = height
        self.background = background
        self.commands = []  # Store commands to execute for this page

        if background:
            self.commands.append(("image", 0, 0, width, height, background))

    def _execute_commands(self):
        """Execute all drawing commands on the canvas."""
        for command in self.commands:
            cmd_type = command[0]
            if cmd_type == "image":
                _, x, y, width, height, image_path, mask = command
                context = nullcontext(namedtuple("context", ["name"])(image_path))
                if mask is not None:
                    # The mask parameter only masks specific colours
                    # we'll use the alpha channel instead
                    image = to_image(image_path)
                    image = join_mask_channel(image, mask, blend=True, allow_resize=True)
                    image_path = image
                    context = NamedTemporaryFile(suffix=".png", delete=False)
                    image.save(context.name)
                with context as img_path:
                    self.pdf_canvas.drawImage(img_path.name, x * mm, (self.height - y - height) * mm, 
                                            width * mm, height * mm, mask='auto')
            elif cmd_type == "text":
                _, x, y, text, font, size = command
                self.pdf_canvas.setFont(font, size)
                self.pdf_canvas.drawString(x * mm, (self.height - y) * mm, text)
            elif cmd_type == "circle":
                _, x, y, radius, stroke, fill = command
                self.pdf_canvas.circle(x * mm, (self.height - y) * mm, radius * mm, 
                                       stroke=int(stroke), fill=int(fill))

    def image(self, x: float, y: float, width: float, height: float, image_path: str, mask: Any = None):
        self.commands.append(("image", x, y, width, height, image_path, mask))

    def text(self, x: float, y: float, text: str, font: str = "Helvetica", size: int = 12):
        self.commands.append(("text", x, y, text, font, size))

    def circle(self, x: float, y: float, radius: float, stroke: bool = True, fill: bool = False):
        self.commands.append(("circle", x, y, radius, stroke, fill))


class ReportLabCanvas(Canvas):
    def __init__(self, config: Dict[str, Any], file_path: str | None = None):
        super().__init__(config, file_path)
        self.pdf = reportlab_canvas.Canvas(config.get("output_file", file_path))
        self.pages = []  # Track pages

    def create_page(self, size: Tuple[float, float], background: str = None) -> CanvasPage:
        page = ReportLabCanvasPage(self.pdf, size[0], size[1], background)
        self.pages.append(page)
        return page

    def save(self):
        """Finalize all pages and save the PDF."""
        for page in self.pages:
            self.pdf.setPageSize((page.width * mm, page.height * mm))
            page._execute_commands()  # Draw all commands for the page
            self.pdf.showPage()  # Finalize the page
        self.pdf.save()
