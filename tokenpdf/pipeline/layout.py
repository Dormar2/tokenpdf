from tokenpdf.layouts import make_layout
from tokenpdf.utils.verbose import vprint

class LayoutManager:
    """Handles layout creation.
       Currently just a pass-through to the layout module.
    """
    def __init__(self, config, verbose):
        self.verbose = verbose
        self.print = vprint(verbose)
        self.config = config
    
    def make_layout(self):
        print = self.print
        print("Creating layout...")
        return make_layout(self.config)
