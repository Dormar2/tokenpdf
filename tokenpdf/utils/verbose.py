from functools import partial
from tqdm import tqdm
from typing import Callable

def vprint(verbose) -> Callable:
    """Returns a print wrapper that only prints if verbose is True.

    Args:
      verbose: 

    Returns:

    """
    if verbose:
        return print
    return lambda *args, **kwargs: None

def vtqdm(verbose) -> Callable:
    """Returns a tqdm wrapper that is a no-op if verbose is False.

    Args:
      verbose: 

    Returns:

    """
    return partial(tqdm, disable=not verbose)