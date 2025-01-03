from .layout import Layout
from .greedy import GreedyLayout


def make_layout(config: dict) -> Layout:
    """
    Factory function to create a layout object based on the given configuration.
    :param config: The configuration dictionary for the layout.
    :return: A layout object.
    """
    layout_type = config.get("layout", "greedy")
    if layout_type in ["greedy", ""]:
        return GreedyLayout(config)
    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")

__all__ = ["make_layout", "Layout", "GreedyLayout"]