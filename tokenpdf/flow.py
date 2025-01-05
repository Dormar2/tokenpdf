import papersize
from .resources import ResourceLoader
from .token import make_token
from .canvas import make_canvas
from .layouts import make_layout
from .utils.verbose import vtqdm, vprint


def make(*config_paths, output_file=None, verbose=None):
    config, resources, loader = _load(*config_paths)
    if verbose is not None:
        config['verbose'] = verbose
    if output_file is not None:
        config['output_file'] = output_file
    elif 'output_file' not in config:
        config['output_file'] = config.get('output', 'output.pdf')
    tokens = _make_tokens(config, loader)
    layout = _make_layout(config)
    canvas = _make_canvas(config, loader)
    return tokens, layout, canvas, config, resources, loader

def place_tokens(tokens, layout, canvas, config, resources, loader):
    verbose = config.get("verbose", False)
    tqdm = vtqdm(verbose)
    print = vprint(verbose)
    sizes = [token.area(token_cfg, loader) for token, token_cfg in tqdm(tokens)]
    print("Arranging tokens in pages")
    pages = layout.arrange(sizes, _gen(_page_size(config)), verbose=verbose)
    canvas_pages = _make_pages(canvas, pages, config)
    for placement_page, canvas_page in zip(tqdm(pages, desc="Drawing pages"),
                                            canvas_pages):
        for tindex, x, y, width, height in tqdm(placement_page, desc="Drawing tokens", leave=False):
            token, t_cfg = tokens[tindex]
            token.draw(canvas_page, t_cfg, loader, (x, y, width, height))

def run(*config_paths, output_file=None, verbose=None):
    tokens, layout, canvas, config, resources, loader = make(*config_paths, output_file=output_file, verbose=verbose)
    
    print = vprint(config.get("verbose", False))
    print(f"Placing {len(tokens)} tokens")
    place_tokens(tokens, layout, canvas, config, resources, loader)
    print(f"Saving output to {output_file}")
    canvas.save()
    print("Done, cleaning up...")
    loader.cleanup()

def _make_tokens(config, loader):
    verbose = config.get("verbose", False)
    tqdm = vtqdm(verbose)
    tokens_data = loader.generate_tokens(config)
    
    return [make_token(token_config, loader)
                for token_config in 
                    tqdm(tokens_data, desc="Loading tokens")]

def _make_layout(config):
    vprint(config.get("verbose", False))("Making layout")
    return make_layout(config)

def _make_canvas(config, resources):
    vprint(config.get("verbose", False))("Making canvas")
    return make_canvas(config)


def _make_pages(canvas, pages, config):
    page_size = _page_size(config)
    # For now, all pages are the same size
    return [canvas.create_page(page_size) for _ in pages]

def _page_size(config):
    page_type = config.get('page_size', 'A4')
    page_size = papersize.parse_papersize(page_type, "mm")
    return [float(x) for x in page_size]

def _load(*config_paths):
    rl = ResourceLoader()
    
    config = rl.load_configs(config_paths)
    verbose = config.get("verbose", False)
    print = vprint(verbose)
    print(f"Loaded configuration from", *config_paths)
    print("Loading resources...")
    resources = rl.load_resources(config)
    return config, resources, rl

def _gen(value):
    while True:
        yield value

if __name__ == "__main__":
    import sys
    args=sys.argv[1:]
    run(*(args if len(args) > 0 else ["example.toml"]))