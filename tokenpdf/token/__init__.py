from .token import Token
from .circle import CircleToken

from .stand import SideStandToken, TopStandToken


def make_token(config, resources):
    """

    Args:
      config: 
      resources: 

    Returns:

    """
    return Token.make(config, resources)

__all__ = ["Token", "CircleToken", "Registry", "make_token", "SideStandToken", "TopStandToken"]