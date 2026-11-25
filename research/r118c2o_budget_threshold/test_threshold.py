import numpy as np
from threshold_transport import Cell,split,combine,T
def test_delta_threshold_equality():
    c=Cell(2.,2*T,T,T)
    lo,hi=split(c,T)
    assert lo is None and hi==c
def test_split_conserves_moments_and_support():
    c=Cell(2.,120.,50.,70.)
    lo,hi=split(c,54.42)
    assert lo.hi<=54.42 and hi.lo>=54.42
    assert abs(lo.n+hi.n-c.n)<1e-13 and abs(lo.u+hi.u-c.u)<1e-11
    merged=combine([lo,hi])
    assert abs(merged.u-c.u)<1e-11
def test_monotone_crossing():
    c=Cell(2.,120.,50.,70.)
    a,b=split(c,54.42);lo,hi=split(b,62.)
    m=combine([a,lo])
    assert m.n>a.n and hi.n<b.n and abs(m.n+hi.n-c.n)<1e-13
