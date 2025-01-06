

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


