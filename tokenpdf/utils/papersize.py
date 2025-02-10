""" Drop in replacement for papersize that uses papersizes
    that is MIT and not GPL. """
import papersizes.parse
import papersizes.units
from typing import Tuple
def parse_papersize(st:str, unitname:str="mm") -> Tuple[int, int]:
    ps = papersizes.parse.paper_size(st)
    if ps.is_landscape():
        ps = ps.flip()
    unit = getattr(papersizes.units, unitname, None)
    if unit is None:
        raise ValueError(f"Unknown unit: {unitname}")
    
    

    return int(round(ps.width / unit)), int(round(ps.height / unit))