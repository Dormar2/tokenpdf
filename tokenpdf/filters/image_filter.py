from tokenpdf.utils.verbose import vprint
from typing import Sequence, Dict

class ImageFilterRegistry:
    def __init__(self):
        self.filters = {}

    def register(self, name, filter_cls):
        self.filters[name] = filter_cls

    def get(self, name):
        return self.filters.get(name)
    
    def __getitem__(self, name):
        return self.get(name)
    
    def __contains__(self, name):
        return name in self.filters
    
main_image_filter_registry = ImageFilterRegistry()

class ImageFilter:
    IMAGE_FILTER_REGISTRY = main_image_filter_registry

    def __init__(self, config, loader):
        self.config = config
        self.loader = loader
        self.verbose = config.get("verbose", False)
        self.print = vprint(self.verbose)

    def filter(self, image):
        raise NotImplementedError("Subclasses must implement this method")


    @classmethod
    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name is None:
            name = cls.__name__
        ImageFilter.IMAGE_FILTER_REGISTRY.register(name, cls)

def apply_imagefilters(image, filters:Sequence[str]|Dict[str, Dict], loader):
    if isinstance(filters, tuple|list):
        filters = {f: {} for f in filters}
    for name, config in filters.items():
        filter_cls = ImageFilter.IMAGE_FILTER_REGISTRY.get(name)
        if filter_cls is None:
            raise ValueError(f"Unknown filter: {name}")
        filter = filter_cls(config, loader)
        image = filter.filter(image)
    return image