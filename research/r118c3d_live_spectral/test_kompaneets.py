import numpy as np
from kompaneets import LinearKompaneets
def test_number_entropy():
 o=LinearKompaneets(np.geomspace(.01,10.,65))
 x=o.x;n=o.cap*(.01*np.sin(x))
 q=o.advance(n,1.)
 assert abs(q.sum()-n.sum())<1e-13
 assert o.energy_norm(q)<o.energy_norm(n)
 assert np.max(abs(o.advance(o.cap,1.)-o.cap))<1e-13
 assert np.max(abs(o.direct(n)-o.matrix@n))<1e-12
