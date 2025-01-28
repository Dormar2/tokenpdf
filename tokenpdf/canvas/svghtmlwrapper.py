
import xml.etree.ElementTree as ET
from .canvas import Canvas, CanvasPage, ConvertCanvasWrapper

class SvgHTMLWrapper(ConvertCanvasWrapper):
    def __init__(self, subcanvas, config, file_path = None):
        super().__init__(subcanvas, config, file_path)
        # Make sure the subcanvas shares images between pages to
        # minimize output size
        self.subcanvas.config = self.subcanvas.config.copy()
        self.subcanvas.config['share_images_between_pages'] = True

    
    def convert(self, result, verbose:bool = False, return_result:bool = False):
        divs = [
            f'<div style="page-break-after: always;">{self.svg_tag_outerhtml(svg)}</div>\n'
            for svg in result
        ]

        html = f"""
        <!DOCTYPE html>
        <html>
        <body> {''.join(divs)} </body> </html> """
        if return_result:
            return html
        if self.format.lower() == 'html':
            with open(self.file_path, 'w') as f:
                f.write(html)
        else:
            raise ValueError(f"Unsupported output format: {self.format}")
           

    def svg_tag_outerhtml(self, svg_text):
        # Unfortunate, but using xml.etree.ElementTree
        # Adds a lot of unneeded xml namespace attributes
        # that screw up the SVG rendering in the html
        # So just return svg element
        index = svg_text.find("<svg")
        return svg_text[index:]

    def cleanup(self):
        self.subcanvas.cleanup()
        super().cleanup()

    @ConvertCanvasWrapper.converted_name.getter
    def converted_name(self):
        return "html"



        