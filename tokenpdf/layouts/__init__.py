from .layout import Layout, BestLayout, LayoutImpossibleError
from .greedy import GreedyLayout
from .rectpack import RectPackLayout, make_default_best_layout, make_constrainted_best_layout



def make_layout(config: dict) -> Layout:
    """Factory function to create a layout object based on the given configuration.

    Args:
      config: The configuration dictionary for the layout.
      config: dict: 

    Returns:
      : A layout object.

    """
    layout_type = str(config.get("layout", "rectpack_best")).lower()
    if layout_type in ["greedy", ""]:
        return GreedyLayout(config)
    elif layout_type.startswith("rectpack") or layout_type.startswith("rpack"):
        if layout_type.endswith("best"):
            return make_default_best_layout(config)
        cbest = make_constrainted_best_layout(config)
        if len(cbest.layouts) == 1:
            # Only one layout, return it directly
            return cbest.layouts[0]
        return cbest
    elif layout_type == 'all':
        layouts = [
            make_layout(dict(config, layout="greedy")),
            make_layout(dict(config, layout="rectpack_best"))
        ]
        return BestLayout(config, layouts)
    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")

__all__ = ["make_layout", "Layout", "GreedyLayout", "RectPackLayout", "BestLayout", "LayoutImpossibleError"]