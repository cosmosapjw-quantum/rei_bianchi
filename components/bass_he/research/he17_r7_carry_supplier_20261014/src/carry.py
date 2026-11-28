"""Positive comparison step. Exact rational arithmetic; no scientific producer."""
from fractions import Fraction as Q

def advance(eg, memory, forcing, inverse, width):
    if width < 0 or not (len(eg)==len(memory)==len(forcing)==len(inverse)):
        raise ValueError("CARRY_DIMENSION_OR_WIDTH")
    b=[x+width*m+y for x,m,y in zip(eg,memory,forcing)]
    return [sum((v*w for v,w in zip(row,b)),Q(0)) for row in inverse]
