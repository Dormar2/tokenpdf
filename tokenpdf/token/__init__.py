from .token import Token, TokenRegistry
from .circle import CircleToken
from .standing import StandingToken

Registry = Token.TOKEN_REGISTRY

def make_token(config, resources):
    return Registry.make(config, resources)

__all__ = ["Token", "TokenRegistry", "StandingToken", "CircleToken", "Registry", "make_token"]