from .canvas import Canvas, CanvasPage, CanvasPageView
from pathlib import Path



def make_reportlab_canvas(config, **kw):
    from .reportlab import ReportLabCanvas
    return ReportLabCanvas(config)

def make_svgwrite_canvas(config, **kw):
    from .svgwrite import SvgwriteCanvas
    return SvgwriteCanvas(config)

def make_svg2html_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for svg2html")
    from .svghtmlwrapper import SvgHTMLWrapper
    return SvgHTMLWrapper(inner, config)

def make_html2pdf_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for html2pdf")
    from .htmlpdfwrapper import HTMLPDFWrapper
    return HTMLPDFWrapper(inner, config)


def make_svg2pdf_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for svg2pdf")
    from .svgpdfwrapper import SVGPDFWrapper
    return SVGPDFWrapper(inner, config)

FORMAT_CHAIN = {
    'pdf': 'html',
    'html': 'svg',
    'svg': 'svgwrite',
    'svg2html': make_svg2html_canvas,
    'html2pdf': make_html2pdf_canvas,
    'svg2pdf': make_svg2pdf_canvas,
    'reportlab': make_reportlab_canvas,
    'svgwrite': make_svgwrite_canvas,
    'rl': make_reportlab_canvas,
}

def make_canvas(config):
    """Factory function to create a canvas based on the configuration.

    Args:
      config: Dictionary of configuration options for the canvas.

    Returns:
      : A new canvas instance.

    """
    
    of = config.get("output_format", Path(config["output_file"]).suffix[1:] )
    
    format_specifiers = FORMAT_CHAIN.copy()
    format_specifiers.update(config.get("canvas_formats", {}))
    if "canvas" not in config:
        if of not in FORMAT_CHAIN and of not in format_specifiers:
            raise ValueError(f"Unsupported output format: {of}")
    canvasname = config.get("canvas", of)
    config["output_format"] = of
    canvas = _make_canvas(canvasname, format_specifiers, config)
    config["canvas"] = canvas.name
    return canvas

def _make_canvas(format, format_specifiers, config, inner=None):
    if callable(format):
        return format(config, inner=inner)
    
    if format not in format_specifiers:
        raise ValueError(f"Unsupported canvas format: {format}")
    
    from_ = format_specifiers[format]
    
    
    canvas = _make_canvas(from_, format_specifiers, config, inner=inner)
    if isinstance(from_, str):
        converter = f'{from_}2{format}'
        if converter in format_specifiers:
            canvas = _make_canvas(converter, format_specifiers, config, canvas)
    return canvas
    

    
    
    
        

__all__ = ["make_canvas", "Canvas", "CanvasPage", "CanvasPageView"]