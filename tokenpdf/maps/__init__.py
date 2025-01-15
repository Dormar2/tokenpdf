from .simple import SimpleMapper
from .mapper import Rectangle, Result, KnownPagesMapper, Mapper
from .map import Map

def make_mapper(config):
    mapper_type = str(config.get("mapper", "simple")).lower()
    if mapper_type == "simple":
        return SimpleMapper(config)
    else:
        raise ValueError(f"Unsupported mapper type: {mapper_type}")
    
__all__ = ["make_mapper", "Rectangle", "Result", "KnownPagesMapper", "Mapper", "Map"]

