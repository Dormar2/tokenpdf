from .canvas import Canvas, CanvasPage, CanvasPageView
from pathlib import Path
def make_canvas(config):
    """Factory function to create a canvas based on the configuration.

    Args:
      config: Dictionary of configuration options for the canvas.

    Returns:
      : A new canvas instance.

    """
    TYPE_DEFAULTS = {'pdf':'reportlab', '':'reportlab'}
    if "output_format" not in config and "canvas" not in config:
        config["output_format"] = Path(config["output_file"]).suffix[1:]
    if "canvas" not in config:
        of = config["output_format"]
        if of not in TYPE_DEFAULTS:
            raise ValueError(f"Unsupported output format: {of}")
        config["canvas"] = TYPE_DEFAULTS[of]
    if config["canvas"] in ["reportlab",'rl']:
        from .reportlab import ReportLabCanvas
        return ReportLabCanvas(config)
    raise ValueError(f"Unsupported canvas type: {config['canvas']}")
        

__all__ = ["make_canvas", "Canvas", "CanvasPage", "CanvasPageView"]