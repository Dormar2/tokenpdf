from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class CanvasPage(ABC):
    """
    Interface for a single page in a canvas.
    """

    @abstractmethod
    def image(self, x: float, y: float, width: float, height: float, image_path: str):
        """
        Draws an image on the page.
        :param x: X-coordinate in mm.
        :param y: Y-coordinate in mm.
        :param width: Width of the image in mm.
        :param height: Height of the image in mm.
        :param image_path: Path to the image file.
        """
        pass

    @abstractmethod
    def text(self, x: float, y: float, text: str, font: str = "Helvetica", size: int = 12):
        """
        Draws text on the page.
        :param x: X-coordinate in mm.
        :param y: Y-coordinate in mm.
        :param text: The text content to draw.
        :param font: Font name.
        :param size: Font size in points.
        """
        pass

    @abstractmethod
    def circle(self, x: float, y: float, radius: float, stroke: bool = True, fill: bool = False):
        """
        Draws a circle on the page.
        :param x: X-coordinate of the center in mm.
        :param y: Y-coordinate of the center in mm.
        :param radius: Radius of the circle in mm.
        :param stroke: Whether to stroke the circle.
        :param fill: Whether to fill the circle.
        """
        pass


class Canvas(ABC):
    """
    Interface for a canvas to manage multiple pages.
    """

    def __init__(self, config: Dict[str, Any], file_path: str | None = None):
        """
        Initializes the canvas with a given configuration and output file path.
        :param config: Dictionary of configuration options for the canvas.
        :param file_path: Path to the output file.
        """
        self.config = config
        self.file_path = file_path if file_path else config["output_file"]

    @abstractmethod
    def create_page(self, size: Tuple[float, float], background: str = None) -> CanvasPage:
        """
        Creates a new page in the canvas.
        :param size: Tuple of (width, height) in mm.
        :param background: Optional path to a background image.
        :return: An instance of CanvasPage.
        """
        pass

    @abstractmethod
    def save(self):
        """
        Finalizes and saves the canvas to the output file.
        """
        pass
