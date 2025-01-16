from .tokens import TokenMaker
from .canvas import CanvasManager
from .layout import LayoutManager
from .post import FilePostProcess
from tokenpdf.resources import ResourceLoader
from tokenpdf.utils.verbose import vtqdm, vprint

class WorkflowManager:
    """Coordinates the overall workflow for generating RPG token PDFs."""
    NAMED_VARIABLES = {'ps':'page_size'}
    def __init__(self, *config_paths, output_file=None, verbose=None):
        self.loader = ResourceLoader()
        
        self.config_tasks = self.loader.load_configs(config_paths)
        if isinstance(self.config_tasks, dict):
            self.config_tasks = [self.config_tasks]
        self.config = self.config_tasks[0]
        self.verbose = verbose if verbose is not None else self.config.get("verbose", False)
        self.print = vprint(self.verbose)
        self.requested_output_file = output_file


    def _generate_output_path(self):
        if self.requested_output_file:
            self.config['output_file'] = self.requested_output_file
        elif 'output_file' not in self.config:
            self.config['output_file'] = self.config.get('output', 'output.pdf')
        for n, fn in self.NAMED_VARIABLES.items():
            if '{' + n + '}' in self.config['output_file']:
                self.config['output_file'] = self.config['output_file'].format(**{n: self.config[fn]})
        
        

    def reset(self):
        self._generate_output_path()
        self.layout = LayoutManager(self.config, self.verbose)
        self.tokens = TokenMaker(self.config, self.loader)
        self.canvas = CanvasManager(self.config, self.loader, self.verbose)

    def run(self):
        """Executes the complete flow for token generation
        Possibly multiple times if multiple configuration tasks are present."""
        for config in self.config_tasks:
            self.config = config.copy()
            self.loader._cfg = self.config
            self.reset()
            self._run_one()

    def _run_one(self):
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
