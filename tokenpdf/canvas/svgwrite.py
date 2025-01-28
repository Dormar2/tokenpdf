import array
from uuid import uuid4
from cv2 import transform
from svgwrite import Drawing
from .canvas import Canvas, CanvasPage
from tokenpdf.utils.geometry import stroke_dash_array
from tokenpdf.utils.verbose import vtqdm
import numpy as np
import hashlib

class SvgwriteCanvasPage(CanvasPage):
    def __init__(self, canvas, width, height, background = None):
        super().__init__(canvas, (width, height))
        self.dwg = Drawing(
                           viewBox=array_arg(0, 0, width, height))
        
        self.images = {}
        self.share_images_between_pages = self.canvas.config.get("share_images_between_pages", False)

    def _find_image(self, md5):
        if not self.share_images_between_pages:
            return self.images.get(md5)
        for page in self.canvas.pages:
            if md5 in page.images:
                return page.images[md5]
        return None

    def _image(self, x, y, width, height, image, flip = (False, False), rotate = 0):
        if image.masked:
            image = image.join_mask()
        mdata = image.mime_with_data
        md5 = hashlib.md5(mdata.encode()).hexdigest()
        data = self._find_image(md5)
        if data is None:
            id_ = uuid4().hex[:8]
            img = self.dwg.image(mdata, size=image.dims)
            symbol = self.dwg.symbol(id=id_)
            symbol.add(img)
            self.dwg.add(symbol)
            self.images[md5] = {"id": id_, "dims": image.dims}
            data = self.images[md5]
                                       
        
        id_, dims = data["id"], data["dims"]
        
        scale_x, scale_y = np.array([width, height]) / np.array(dims)
        flip_x, flip_y = (-1 if flip[0] else 1, -1 if flip[1] else 1)
        tscale_x, tscale_y = scale_x * flip_x, scale_y * flip_y


        group = self.dwg.g(**transform(x, y, rotate, tscale_x, tscale_y))
        group.add(self.dwg.use(f"#{id_}"))
        self.dwg.add(group)

    def line(self, x1, y1, x2, y2, color:str = "black", thickness = 1, style = "solid"):
        self.dwg.add(self.dwg.line((x1, y1), (x2, y2), stroke=color, stroke_width=thickness/2, **stroke_array(style)))
    
    def rect(self, x, y, width, height, thickness = 1, fill = 0, color:str = "black", style = "solid", rotate = 0):
        kw = {}
        if fill:
            kw["fill"] = color
        else:
            kw["fill-opacity"] = 0
        self.dwg.add(self.dwg.rect(size=(float(width), float(height)), stroke=color, stroke_width=thickness/2, **stroke_array(style), **transform(x, y, rotate), **kw))
        
    def circle(self, x, y, radius, stroke = True, fill = False):
        kw = {}
        if fill:
            kw["fill"] = "black"
        else:
            kw["fill-opacity"] = 0
        self.dwg.add(self.dwg.circle(center=(x, y), r=radius, stroke_width=stroke/2, **kw))

    def text(self, x, y, text, font = "Helvetica", size = 12, rotate = 0):
        ms = min(self._page_size)
        font_size = size * ms / 1000
        self.dwg.add(self.dwg.text(text, font_family=font, font_size=font_size, **transform(x, y, rotate)))
            
        
        



class SvgwriteCanvas(Canvas):
    def __init__(self, config, file_path = None):
        super().__init__(config, file_path)
        self.pages = []

    def create_page(self, size, background = None) -> SvgwriteCanvasPage:
        page = SvgwriteCanvasPage(self, *size, background)
        self.pages.append(page)
        return page
    
    
    def save(self, verbose:bool = False, return_result:bool = False):
        tqdm = vtqdm(verbose)
        results = []
        for i, page in enumerate(tqdm(self.pages, desc="Saving pages")):
            if return_result:
                results.append(page.dwg.tostring())
            else:
                page.dwg.saveas(f"{self.file_path}_{i}.svg", pretty=True)
        self.pages = []
        if return_result:
            return results
        
    @Canvas.name.getter
    def name(self):
        return "svg(svgwrite)"



def stroke_array(style) -> dict:
    return {
        'stroke_dasharray':  array_arg(*stroke_dash_array(style))
    }


def transform(x,y,angle=0,scale_x=1.0, scale_y=1.0)-> dict:
    telements = [f"translate({x},{y})"]
    if angle:
        telements.append(f"rotate({angle*180/np.pi})")
    if scale_x != 1.0 or scale_y != 1.0:
        telements.append(f"scale({scale_x},{scale_y})")
    return {"transform": ' '.join(telements)}


def array_arg(*seq)->str:
    return ' '.join(str(i) for i in seq)