from functools import partial
from tqdm import tqdm
from typing import Protocol


class PrintCallable(Protocol):
    """ Protocol for a print-like callable.
      Used to type hint functions that return
      print-like functions."""
    __call__ = print
  
class TqdmCallable(Protocol):
    """ Protocol for a tqdm-like callable. """
    __call__ = tqdm.__init__

def vprint(verbose) -> PrintCallable:
    """Returns a print wrapper that only prints if verbose is True.

    Example:
    >>> print = vprint(verbose)
    >>> print("Hello, world!")
    
    """
    if verbose:
        return print
    return lambda *args, **kwargs: None

def vtqdm(verbose) -> TqdmCallable:
    """Returns a tqdm wrapper that is a no-op if verbose is False.

    Args:
      verbose: 

    Returns:

    """
    return partial(tqdm, disable=not verbose)


