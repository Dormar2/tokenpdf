
from tokenpdf import maps
from tokenpdf.token import make_token
from tokenpdf.utils.verbose import vtqdm

class TokenMaker:
    """Handles token object generation and map loading from configuration."""
    def __init__(self, config, loader):
        self.config = config
        self.loader = loader
        self.verbose = config.get("verbose", False)
        self.tqdm = vtqdm(self.verbose)

    def make_tokens(self):
        # Make tokens from config
        tokens_data = self.loader.generate_tokens(self.config)
        tokens = [make_token(token_config, self.loader)
                for token_config in self.tqdm(tokens_data, desc="Loading tokens")]
        return tokens
    
    def make_maps(self):
        maps_data = self.loader.generate_maps(self.config)
        return maps_data