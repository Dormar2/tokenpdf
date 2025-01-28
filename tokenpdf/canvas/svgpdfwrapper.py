import sys
from .canvas import ConvertCanvasWrapper

from svglib.svglib import svg2rlg
from .reportlab import ReportLabCanvas, ReportLabCanvasPage
from reportlab.graphics.renderPDF import draw as draw_on_pdf_canvas
from reportlab.lib.units import mm
import io
class SVGPDFWrapper(ConvertCanvasWrapper):
    def __init__(self, subcanvas, config, file_path=None):
        super().__init__(subcanvas, config, file_path)
        

    def convert(self, result, verbose: bool = False, return_result: bool = False):
        rl_canvas = ReportLabCanvas(self.config.copy())

        for svg in result:
            page = rl_canvas.create_page(self.config['page_size'])
            
            filelike = io.StringIO(svg)
            drawing = svg2rlg(filelike)
            drawing.renderScale = 2
            draw_on_pdf_canvas(drawing, page.pdf_canvas, 0, 0)
        rl_canvas.pdf.save()

