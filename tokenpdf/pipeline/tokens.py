
from tokenpdf.token import make_token
from tokenpdf.utils.verbose import vtqdm

class TokenMaker:
    """Handles token object generation from configuration."""
    def __init__(self, config, loader):
        self.config = config
        self.loader = loader
        self.verbose = config.get("verbose", False)
        self.tqdm = vtqdm(self.verbose)

    def make_tokens(self):
        tokens_data = self.loader.generate_tokens(self.config)
        return [make_token(token_config, self.loader)
                for token_config in self.tqdm(tokens_data, desc="Loading tokens")]