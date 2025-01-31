
from typing import Tuple
import numpy as np
from .token import Token
from tokenpdf.utils.image import get_file_dimensions, complete_size
from tokenpdf.utils.geometry import n_sided_polygon
class SideStandToken(Token, name="stand_sides"):
    """ A new version of the standing token that supports
        more options and uses relative drawing """
    
    @classmethod
    def supported_types(cls):
        """ """
        return {
            "stand_sides": {
                "width": None, "height": None, "border_color": "black", "fill_color": "white",
                "image_url": None, "border_url": None, "keep_aspect_ratio": True,
                "rect_border_thickness": 1,
                "rect_border_style": "dot-dash",
                "sides": 4,
            }
        }
    
    def apply_defaults(self, config, resources):
        config = super().apply_defaults(config, resources)
        width, height = config.get("width"), config.get("height")
        width, height = complete_size(width, -1, *resources[config["image_url"]].dims, keep_aspect_ratio=config.get("keep_aspect_ratio", True))
        config["width"], config["height"] = width, height
        return config
    
    def area(self, config, resources) -> Tuple[float, float]:
        n = config.get("sides", 4)
        bsize = np.zeros(2)
        if n < 3:
            bsize = self._thin_token_base_area(config, resources)
        bw, bh = bsize
        ssize = self._standing_area(config, resources)
        sw, sh = ssize
        w = n*sw
        h = sh+bh
        return np.array([w, h])
    
    def _standing_area(self, config, resources) -> Tuple[float, float]:
        return np.array([config["width"], config["height"]])
    
    def _thin_token_base_area(self, config, resources) -> Tuple[float, float]:
        w = config.get("width", 0)
        return np.array([w, w/2])
    
    def draw(self, view, config, resources):
        n = config.get("sides", 4)
        smargin = config.get("standing_margin", 0) * config.get("width", 0)
        hbox_views = view.hbox(n, spacing=smargin, return_spacing=True)
        image_views = hbox_views[::2]
        spacing_views = hbox_views[1::2]
        for sv in spacing_views:
            self._draw_spacing(config, sv)
        img = self._load_image(resources, config["image_url"])
        for iv in image_views:
            self._draw_image(img, config, resources, iv)
        if n <= 2:
            for iv in image_views:
                self._draw_lower_margin(config, iv)
        super().draw(view, config, resources)


    def _draw_lower_margin(self, config, view):
        b = view.size[0] 
        margin = config.get("standing_margin", 0) * b
        y = view.size[1] - b/2
        xy0 = np.array([margin, y])
        xy1 = np.array([view.size[0] - margin, y])
        view.line(*xy0, *xy1,
                         color = config.get("rect_border_color", "black"),
                         thickness = config.get("rect_border_thickness", 1),
                         style = config.get("rect_border_style", "solid"))
        
    def _load_image(self, resources, url):
        return resources[url]
    
    def _draw_image(self, img, config, resources, view):
        n = config.get("sides", 4)
        vs = np.array(view.size)
        standing_size = vs
        if n<=2:
            standing_size -= [0, vs[0]/2]
        m = np.min(vs)*config.get("standing_margin", 0)
        x = y = m
        w,h = standing_size - 2*m
        
        view.image(x,y,w,h,img)
        

    def _draw_spacing(self, config, view):
        vw, vh = view.size
        midw = vw/2
        h_start = vw/2
        h_end = vh - h_start
        view.line(midw, h_start, midw, h_end,
                         color = config.get("rect_border_color", "black"),
                         thickness = config.get("rect_border_thickness", 1),
                         style = config.get("rect_border_style", "solid"))
    
        
        
class TopStandToken(Token, name=["stand_tops", "standing"]):
    @classmethod
    def supported_types(cls):
        """ """
        types = {
            "stand_tops": {
                "width": None, "height": None, "border_color": "black", "fill_color": "white",
                "image_url": None, "border_url": None, "keep_aspect_ratio": True,
                "rect_border_thickness": 1,
                "rect_border_style": "dot-dash",
                "sides": 4,
                "fold_lines": False
            }
        }
        types["standing"] = dict(types["stand_tops"], sides=2)
        return types
    
    def apply_defaults(self, config, resources):
        config = super().apply_defaults(config, resources)
        width, height = config.get("width"), config.get("height")
        width, height = complete_size(width, -1, *resources[config["image_url"]].dims, keep_aspect_ratio=config.get("keep_aspect_ratio", True))
        config["width"], config["height"] = width, height
        return config
    
    def area(self, config, resources) -> Tuple[float, float]:
        n = config.get("sides", 4)
        inner, outer = self.construct_segments(config["width"], config["height"], n)
        all_points = np.concatenate([inner, outer], axis=0)
        all_points -= np.min(all_points, axis=0)
        w,h = np.max(all_points, axis=0)
        return w,h
    
    def draw(self, view, config, resources):
        n = config.get("sides", 4)
        # Figure out the shrinkage factor
        orig_size = self.area(config, resources)
        factor = np.array(view.size) / orig_size
        # Reconstruct the inner and outer polygons from the new size
        nw, nh = factor * np.array([config["width"], config["height"]])
        
        inner, outer = self.construct_segments(nw, nh, n)
        # Align all points to the origin of the view (0,0)
        all_points = np.concatenate([inner, outer], axis=0)
        mallp = np.min(all_points, axis=0)
        inner-=mallp
        outer-=mallp

        linekw = {
            "color": config.get("rect_border_color", "black"),
            "thickness": config.get("rect_border_thickness", 1),
            "style": config.get("rect_border_style", "solid")
        }

        # Attach an image on each side of the polygon, and draw edges of inner and outer polygons
        for i in range(n):
            # Points are in counter-clockwise order
            top_right_corner = inner[i] 
            top_left_corner = inner[(i+1)%n]
            tlx, tly = top_right_corner - top_left_corner
            angle = np.arctan2(tly, tlx)
            rview = view.view(*top_left_corner, nw, nh, angle=angle)
            mview = rview.margin_view(config.get("standing_margin", 0), regular=True)
            img = self._load_image(config, resources, config["image_url"])
            
            mview.image(0,0, None, None, img)
            # Draw the bounding rect of each image
            #rview.line(0,0, nw, 0, **linekw)
            #rview.line(0, nh, nw, nh, **linekw)
            rview.rect(0,0,nw,nh, **linekw)

            # Complete the outter polygon
            # (The last line swe cannot do through the rviews, so use the raw points)
            if n>2:
                # n <= 2 handling below
                op0 = outer[(2*i + 1) % (2*n)]
                op1 = outer[(2*i + 2) % (2*n)]
                view.line(*op0, *op1, **linekw)
        if n<=2:
            # We only want to draw the extra margins we added
            rects = np.reshape(outer, (-1, 2, 2))
            for rect in rects:
                p0, p1 = rect
                w,h = p1 - p0
                view.rect(*p0, w, h, **linekw)



    def _load_image(self, config, resources, url):
        return self.get_image(resources, url, config=config)



    def construct_segments(self, w,h, n):
        inner = self.construct_inner_segments(w,h,n)
        outer = self.construct_outer_segments(w,h,n)
        return inner, outer

    def construct_inner_segments(self, w,h,n):
        return n_sided_polygon(n, w)

    def construct_outer_segments(self, w,h,n):
        points = self.construct_inner_segments(w,h,n)
        # Always have at least two points
        if n<=2:
            # Special case, add margin to the bottoms of the two images as extra points
            # The points above will still be used to calculate the polygon edges.
            m = w/2
            p0 = np.min(points, axis=0) if len(points) else np.array([0,0])
            p1 = p0 + [w,0]
            # Below the bottom image
            rect1 = p0 + [0,h], p1 + [0,m+h]
            outer_poly_points = rect1
            if n == 2:
                # Add a second margin rect above the second image
                rect2 = p0 - [0,m+h], p1 - [0,h]
                outer_poly_points = np.concatenate([rect1, rect2], axis=0)
            return outer_poly_points
        




        # lay the images on each side of the polygon
        outer_poly_points = []
        for i in range(n):
            p0,p1 = points[i], points[(i+1)%n]
            
            # Get the x,y of the normal to p0->p1 
            normal = np.array([p1[1]-p0[1], p0[0]-p1[0]])
            normal /= np.linalg.norm(normal)
            outer_poly_points.extend([p0 + h*normal, p1 + h*normal])
        
        return np.array(outer_poly_points)
    
        
    
