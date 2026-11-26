import numpy as np
from nonlinear import Kompaneets
def test_equilibrium_and_number_entropy():
 o=Kompaneets(np.geomspace(1e-3,30,65))
 for t in (.5,1.,2.):
    n=o.equilibrium(t,.2)
    assert np.max(abs(o.advance(n,t,.01,8)-n))<1e-12
    n=o.equilibrium(1.,.2)
    q=o.advance(n,t,.01,16)
    assert np.min(q)>=0 and abs(q.sum()-n.sum())<1e-12
    assert o.entropy(q,t)<=o.entropy(n,t)+1e-12
def test_zero_donor():
 o=Kompaneets(np.geomspace(.1,5.,17));n=np.zeros(16);n[8]=1.
 q=o.advance(n,1.,.03,4);assert min(q)>=0 and abs(q.sum()-1.)<1e-13
