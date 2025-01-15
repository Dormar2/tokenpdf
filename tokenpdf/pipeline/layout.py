from tokenpdf.layouts import make_layout
from tokenpdf.maps import make_mapper
from tokenpdf.utils.verbose import vprint

class LayoutManager:
    """Handles layout creation.
       Currently just a pass-through to the layout module.

    Args:

    Returns:

    """
    def __init__(self, config, verbose):
        self.verbose = verbose
        self.print = vprint(verbose)
        self.config = config
    
    def make_layout(self):
        """ """
        print = self.print
        print("Creating layout and mapper...")
        return make_layout(self.config), make_mapper(self.config)

