"""Eventwise refinement without changing the supplied emission realization."""
from __future__ import annotations
import math
from collections.abc import Sequence

class MeshError(ValueError):
    pass

def refine_all_cells(mesh: Sequence[float]) -> list[float]:
    """Insert one representable interior midpoint into EVERY original cell."""
    if len(mesh)<2 or any(isinstance(x,bool) or not math.isfinite(x) for x in mesh):
        raise MeshError('INVALID_FINITE_EVENT_MESH')
    if any(b<=a for a,b in zip(mesh,mesh[1:])):
        raise MeshError('NONINCREASING_EVENT_MESH')
    out=[mesh[0]]
    for a,b in zip(mesh,mesh[1:]):
        m=(a+b)/2
        if not a<m<b:
            raise MeshError('NO_REPRESENTABLE_INTERIOR_MIDPOINT')
        out.extend((m,b))
    return out
