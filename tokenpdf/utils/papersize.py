""" Drop in replacement for papersize that uses papersizes
    that is MIT and not GPL. """
import papersizes.parse
from papersizes.units import mm
from typing import Tuple
def parse_papersize(st:str) -> Tuple[int, int]:
    ps = papersizes.parse.paper_size(st)
    if ps.is_landscape():
        ps = ps.flip()
    ps = ps.round_to_mm()

    return int(round(ps.width / mm)), int(round(ps.height / mm))