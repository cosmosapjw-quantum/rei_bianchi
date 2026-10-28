"""Boundary of a planar zonotope: c+sum_i[-g_i,g_i].
Sort oriented nonzero generators; parallel rays may yield redundant vertices.
Return a closed polygon with 2*N+1 points, no global numerical state.
"""
from math import atan2, pi

def boundary(center, generators):
    c0, c1 = map(float, center)
    oriented = []
    for gx, gy in generators:
        gx, gy = float(gx), float(gy)
        if gx == 0 and gy == 0:
            continue
        if gy < 0 or (gy == 0 and gx < 0):
            gx, gy = -gx, -gy
        oriented.append((atan2(gy,gx),gx,gy))
    oriented.sort()
    x = c0 - sum(a for _, a, _ in oriented)
    y = c1 - sum(b for _, _, b in oriented)
    points=[(x,y)]
    for _, a, b in oriented:
        x, y = x + 2*a, y + 2*b
        points.append((x,y))
    for _, a, b in oriented:
        x, y = x - 2*a, y - 2*b
        points.append((x,y))
    return points
