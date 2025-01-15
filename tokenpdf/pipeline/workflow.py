from .tokens import TokenMaker
from .canvas import CanvasManager
from .layout import LayoutManager
from .post import FilePostProcess
from tokenpdf.resources import ResourceLoader
from tokenpdf.utils.verbose import vtqdm, vprint

class WorkflowManager:
    """Coordinates the overall workflow for generating RPG token PDFs."""

    def __init__(self, *config_paths, output_file=None, verbose=None):
        self.loader = ResourceLoader()
        
        self.config = self.loader.load_configs(config_paths)
        self.verbose = verbose if verbose is not None else self.config.get("verbose", False)
        self.print = vprint(self.verbose)
        
        if output_file:
            self.config['output_file'] = output_file
        elif 'output_file' not in self.config:
            self.config['output_file'] = self.config.get('output', 'output.pdf')
        self.layout = LayoutManager(self.config, self.verbose)
        self.tokens = TokenMaker(self.config, self.loader)
        self.canvas = CanvasManager(self.config, self.loader, self.verbose)

    def run(self):
        """Executes the complete flow for token generation."""

        print = self.print
        print("Starting workflow...")
        print("Loading resources...")
        self.loader.load_resources()
        print(f"Loaded {len(self.loader.resources)} resources")
        
        print("Creating layout...")
        layout, mapper = self.layout.make_layout()
        print("Generating token objects...")
        maps = self.tokens.make_maps()
        tokens = self.tokens.make_tokens()
        print(f"Generated {len(tokens)} token objects")

        print(f"Placing {len(tokens)} tokens")
        self.canvas.place_tokens(tokens, layout, maps, mapper)

        print(f"Saving output to {self.config['output_file']}")
        self.canvas.save()
        print(f"Post-processing {self.config['output_file']}")
        FilePostProcess.process(self.config['output_file'], self.config, self.loader)
        print("Done, cleaning up...")
        self.loader.cleanup()
