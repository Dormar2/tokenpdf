from contextlib import contextmanager
from pathlib import Path
from typing import Tuple, Generator

class ResettableGenerator:
    """
    A generator that can be reset to its initial state,
    saves all values it has generated so far.
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
        next_val = next(self.gen)
        self.history.append(next_val)
        return next_val
            
    def reset(self):
        self.available = self.history[::-1].copy()



def consume(generator, n):
    """ Consume up to n items from a generator and return them in a list.
        If no items are left, raises StopIteration. """
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
    """
    A context manager that renames a file when entering and renames it back when exiting.
    Useful for "inplace" processing of a file, while making sure that if the processing fails,
    the original file is not lost.
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
        self._disable = True
        if self.delete_on_cancel and self.to.exists():
            self.to.unlink()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._disable:
            return False
        self.to.rename(self.path)
        return False
    
rename = Rename