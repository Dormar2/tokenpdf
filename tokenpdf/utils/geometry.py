from typing import Sequence
import numpy as np

def n_sided_polygon(n, side_length, center=None):
    """Return the coordinates of the vertices of a regular n-sided polygon with side_length.
        The points are returned in counter-clockwise order.
    Args:
        n: Number of sides of the polygon
        side_length: Length of each side
        center: If None, the center is chosen such that the polygon touches the x and y axes.
                If a tuple, the center of the polygon is set to this tuple.
    """
    if n==1:
        return np.array([[0.0,0.0]])
    elif n==0:
        return np.array([])
    
    phase = 0#np.pi/4
    t = np.linspace(phase, 2*np.pi+phase, n, endpoint=False)
    x = np.cos(t)
    y = np.sin(t)
    points = np.array([x,y]).T
    cur_side_length= np.linalg.norm(points[0] - points[1])
    points *= side_length / cur_side_length
    
    
    if center is None:
        points -= np.min(points, axis=0)
    else:
        points_center = (np.max(x)/2, np.max(y)/2)
        points += center - points_center
    return points


def stroke_dash_array(style:str) -> Sequence[int]:
    pattern = []
    for s in style.split("-"):
        if s.lower() == "dot":
            pattern.extend([1, 2])
        elif s.lower() == "dash":
            pattern.extend([3, 2])
        elif s.lower() == "solid":
            pattern.extend([1, 0])
        elif s.isnumeric():
            pattern.append(int(s))
        else:
            try:
                pattern.append(int(s))
            except ValueError:
                raise ValueError(f"Invalid line style: {style}")
    return pattern