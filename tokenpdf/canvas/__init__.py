from .canvas import Canvas, CanvasPage, CanvasPageView, CanvasRegistry
from pathlib import Path


@Canvas.factory("rl", "reportlab")
def make_reportlab_canvas(config, **kw):
    from .reportlab import ReportLabCanvas
    return ReportLabCanvas(config)

@Canvas.factory("svgwrite")
def make_svgwrite_canvas(config, **kw):
    from .svgwrite import SvgwriteCanvas
    return SvgwriteCanvas(config)

@Canvas.factory("svg2html")
def make_svg2html_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for svg2html")
    from .svghtmlwrapper import SvgHTMLWrapper
    return SvgHTMLWrapper(inner, config)

@Canvas.factory("html2pdf")
def make_html2pdf_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for html2pdf")
    from .htmlpdfwrapper import HTMLPDFWrapper
    return HTMLPDFWrapper(inner, config)

@Canvas.factory("svg2pdf(rl)")
def make_svg2pdf_canvas(config, inner, **kw):
    if inner is None:
        raise ValueError("Inner canvas required for svg2pdf")
    from .svgpdfwrapper import SVGPDFWrapper
    return SVGPDFWrapper(inner, config)

@Canvas.factory("svg2pdf(re)")
def make_svg2pdf_resvg_canvas(config, inner, **kw):
    from .resvgconverter import ResvgConvert
    return ResvgConvert(inner, config)

@Canvas.factory("svg2pdf(r)")
def make_svg2pdf_resvg_canvas(config, inner, **kw):
    from .rsvgconverter import RsvgConvert
    return RsvgConvert(inner, config, many_to_one=True)

FORMAT_CHAIN = {
    'pdf': 'svg',
    'html': 'svg',
    'svg': 'svgwrite',
    'svg2pdf': 'svg2pdf(r)'
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
    if "canvas" not in config and of not in format_specifiers:
            raise ValueError(f"Unsupported output format: {of}")
    canvasname = config.get("canvas", of)
    config["output_format"] = of
    canvas = _make_canvas(canvasname, format_specifiers, config)
    config["canvas"] = canvas.name
    print(f"Using canvas: {canvas.name}")
    return canvas

def _make_canvas(format, format_specifiers, config, inner=None):
    if callable(format):
        return format(config, inner=inner)
    print(format)
    registry = CanvasRegistry.get_registry()
    if format not in format_specifiers and format not in registry:
        raise ValueError(f"Unsupported canvas format: {format}")
    
    from_ = format_specifiers[format] if format in format_specifiers else registry[format]
    
    
    canvas = _make_canvas(from_, format_specifiers, config, inner=inner)
    if isinstance(from_, str):
        converter = f'{from_}2{format}'
        if converter in format_specifiers:
            canvas = _make_canvas(converter, format_specifiers, config, canvas)
    return canvas
    

    
    
    
        

__all__ = ["make_canvas", "Canvas", "CanvasPage", "CanvasPageView"]