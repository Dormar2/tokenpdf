from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from tokenpdf.utils.config import merge_configs


class Token(ABC):
    """Abstract base class for tokens.
    Defines the interface for all token types.

    Args:

    Returns:

    """

    TOKEN_REGISTRY = None

    @classmethod
    @abstractmethod
    def supported_types(cls) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary mapping supported types to their expected configuration values
        and default values. Example: @see SideStandToken.supported_types()

        Args:

        Returns:

        """
        pass

    def apply_defaults(self, config: Dict[str, Any], resources: Dict[str, Any]) -> Dict[str, Any]:
        """Applies default values to the configuration dictionary after loading resources

        Args:
          config: The configuration dictionary for the token instance.
          resources: The resources loaded for the token instance (e.g.
        fonts, images).
          config: Dict[str: 
          Any]: 
          resources: Dict[str: 

        Returns:

        """
        return config

    @abstractmethod
    def area(self, config, resources) -> Tuple[float, float]:
        """Calculates the required area in real-world units (mm)
        Should be based on the configuration of the token instance.

        Args:
          config: The configuration dictionary for the token instance.
          resources: The resources loaded for the token instance (e.g.
        fonts, images).

        Returns:

        """
        pass

    def draw(self, view, config, resources):
        """Draws the token on the specified canvas view

        Args:
          view: The canvas view to draw the token on. The view provides sizing as well.
          config: The configuration dictionary for the token instance.
          resources: Resources loaded for the token instance (e.g. fonts, images).

        Returns:

        """
        if config.get("rect_border_thickness") is not None:
            rect=(0,0,*view.size)
            view.rect(*rect, thickness=config.get("rect_border_thickness", None),
                        fill=0, color=config.get("rect_border_color", None),
                        style=config.get("rect_border_style", None))
                        


    # Registry new subclasses
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Token.TOKEN_REGISTRY is not None:
            Token.TOKEN_REGISTRY.register(cls)


class TokenRegistry:
    """A class responsible for managing token types."""

    def __init__(self):
        self._token_types = {}

    def register(self, cls):
        """Registers a token class.

        Args:
          cls: The token class to register.

        Returns:

        """
        supported_types = cls.supported_types()
        for token_type, config in supported_types.items():
            ttype = token_type.lower()
            if ttype in self._token_types:
                raise ValueError(f"Token type '{ttype}' already registered.")
            self._token_types[ttype] = (cls, config)
    
    def make(self, config, resources) -> Tuple[Token, Dict[str, Any], Dict[str, Any]]:
        """Creates a new token instance of the specified type.

        Args:
          config: The configuration dictionary for the token instance.
          resources: The resources loaded for the token instance (e.g.
        fonts, images).

        Returns:
          : A new token instance.

        """
        token_type = config.get("type", "Circle").lower()
        if token_type not in self._token_types:
            raise ValueError(f"Unsupported token type: {token_type}")
        cls, default_config = self._token_types[token_type]
        merged_config = merge_configs(default_config, config)
        token = cls()
        config = token.apply_defaults(merged_config, resources)
        return token, config

Token.TOKEN_REGISTRY = TokenRegistry()