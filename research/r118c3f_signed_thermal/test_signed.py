import numpy as np
from signed import SignedKompaneets
def test_exact_planck_and_tiny_transfer():
 s=SignedKompaneets(np.geomspace(1e-5,40,1025));z=np.zeros(len(s.x))
 q,du=s.advance(z,1.,1e-5,8);assert np.array_equal(q,z) and du==0
 q,du=s.advance(z,.3,1e-20,1)
 assert du<0 and np.any(q!=0) and abs(q.sum())<1e-12*np.sum(abs(q))
 assert abs(du/(s.x@q)-1)<1e-12
 assert abs(du/(4e-20*(1-1/.3)*np.pi**4/15)-1)<.03
def test_large_against_absolute():
 import sys
 from pathlib import Path
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c3e_nonlinear_compton'))
 from nonlinear import Kompaneets
 s=SignedKompaneets(np.geomspace(.001,30,65));o=Kompaneets(s.edges);d=.1*s.c*s.f0
 q,du=s.advance(d,.5,.001,256);a=o.advance(d+s.c*s.f0,.5,.001,256)
 assert np.sum(abs(q+s.c*s.f0-a))/np.sum(a)<1e-11
 assert abs(q.sum()-d.sum())<1e-12
