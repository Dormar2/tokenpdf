from .system import RPGSystem, RPGSystemRegistry

registry = RPGSystemRegistry()

__all__ = ["RPGSystem", "RPGSystemRegistry", "registry"]