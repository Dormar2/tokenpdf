from contextlib import contextmanager
from pathlib import Path
from typing import Tuple, Generator
import inspect

class ResettableGenerator:
    """A generator that can be reset to its initial state,
    saves all values it has generated so far.

    Args:

    Returns:

    """
    def __init__(self, gen, reset_on_stop=True):
        self.gen = gen
        self.history = []
        self.available = []
        self.reset_on_stop = reset_on_stop
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.available:
            return self.available.pop()
        else:
            try:
                return self._consume()
            except StopIteration:
                if self.reset_on_stop:
                    self.reset()
                else:
                    raise
            
    def _consume(self):
        """ """
        next_val = next(self.gen)
        self.history.append(next_val)
        return next_val
            
    def reset(self):
        """ """
        self.available = self.history[::-1].copy()

@contextmanager
def set_attr(obj, **kwargs):
    was = {key:getattr(obj, key, None) for key in kwargs if hasattr(obj, key)}
    for key, value in kwargs.items():
        setattr(obj, key, value)
    try:
        yield obj
    finally:
        for key, value in kwargs.items():
            if key in was:
                setattr(obj, key, was[key])
            else:
                delattr(obj, key)

def consume(generator, n):
    """Consume up to n items from a generator and return them in a list.
       If no items are left, raises StopIteration.

    Args:
      generator: 
      n: 

    Returns:

    """
    res = [None] * n
    length = 0
    for i in range(n):
        try:
            res[i] = next(generator)
            length = i + 1
        except StopIteration:
            if i == 0:
                raise
            break
    return res[:length]



class Rename:
    """A context manager that renames a file when entering and renames it back when exiting.

    Useful for "inplace" processing of a file, while making sure that if the processing fails,
    the original file is not lost.

    Args:
        path (str): The original file path.
        to (str): The new file path.
        delete_on_cancel (bool): If True, the new file will be deleted if cancel() is called.

    Examples:
        .. code-block:: python

            with Rename("file.txt", "file.txt.tmp"):
                process_file("file.txt.tmp")
                # If process_file fails, the original file is still intact.

            with Rename("file.txt", "file.txt.tmp", delete_on_cancel=True) as r:
                process_file("file.txt.tmp")
                # process_file succeeded, the original file is now "file.txt.tmp"
                # it is safe to delete the new file.
                r.cancel()

            with Rename("file.txt", "file.txt.tmp") as r:
                process_file("file.txt.tmp")
                r.cancel() # Cancel the renaming, leaving the original file intact as "file.txt.tmp"
        
    """
    def __init__(self, path : Path, to : Path, delete_on_cancel=False):
        self.path = path
        self.to = to
        self._disable = False
        self.delete_on_cancel = delete_on_cancel
    
    def __enter__(self):
        self.path.rename(self.to)
        return self
    
    def cancel(self):
        """ 
        Disables the renaming-back of the file at __exit__.
        If delete_on_cancel is True, the new file is deleted here.
        """
        self._disable = True
        if self.delete_on_cancel and self.to.exists():
            self.to.unlink()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._disable:
            return False
        self.to.rename(self.path)
        return False
    
rename = Rename


def parent_class_leading_to(cls, parent_cls):
    """ Returns the direct parent of the cls that is a subclass of parent_cls."""
    if not issubclass(cls, parent_cls):
        raise ValueError(f"{cls} is not a subclass of {parent_cls}")
    for c in inspect.getmro(cls):
        if c is cls:
            continue
        if issubclass(c, parent_cls):
            return c
    raise RuntimeError(f"Parent class {parent_cls} not found in {cls} inheritance chain.")