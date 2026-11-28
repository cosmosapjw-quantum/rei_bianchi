from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ArsenyInput:
    Z1: float
    Z2: float
    Zin: float
    n: int
    l: int
    Jmax: int
    Nmax: int
    DMP: float
    KEYPC: int
    energies_keV_per_amu: tuple[float,...]

def _numbers(line: str):
    line=line.split("!")[0].replace(","," ")
    return [x for x in line.split() if x]

def parse_arseny_input(text: str) -> ArsenyInput:
    lines=[ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 6:
        raise ValueError("input too short")
    a=_numbers(lines[0]); b=_numbers(lines[1]); c=_numbers(lines[2])
    d=_numbers(lines[3]); e=_numbers(lines[4])
    Z1,Z2=map(float,a[:2])
    Zin=float(b[0]); n=int(b[1]); l=int(b[2]); Jmax=int(b[3])
    Nmax=int(c[0]); DMP=float(c[1])
    KEYPC=int(d[0]); NE=int(e[0])
    if len(lines) < 5+NE:
        raise ValueError("energy list shorter than NE")
    energies=tuple(float(_numbers(lines[5+i])[0]) for i in range(NE))
    if Z2 < Z1:
        raise ValueError("paper contract requires Z2 >= Z1")
    return ArsenyInput(Z1,Z2,Zin,n,l,Jmax,Nmax,DMP,KEYPC,energies)
