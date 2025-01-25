from .token import Token, TokenRegistry
from .circle import CircleToken
from .standing import StandingToken
from .stand import SideStandToken
Registry = Token.TOKEN_REGISTRY

def make_token(config, resources):
    """

    Args:
      config: 
      resources: 

    Returns:

    """
    return Registry.make(config, resources)

__all__ = ["Token", "TokenRegistry", "StandingToken", "CircleToken", "Registry", "make_token"]