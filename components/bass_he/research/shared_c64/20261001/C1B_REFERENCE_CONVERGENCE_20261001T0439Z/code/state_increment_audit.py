"""Stable L2 increments from actual radial differences; no fitted/rigorous error bound."""
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from run_centered import load_pair
from evidence_io import atomic_json,sha256
ROOT=Path(__file__).resolve().parents[1]
def distance(a,b):
    q,w=leggauss(max(a.degree,b.degree)+2);mesh=np.unique(np.r_[a.boundaries,b.boundaries]);total=0.
    for lo,hi in zip(mesh[:-1],mesh[1:]):
        jac=(hi-lo)/2;r=lo+jac*(q+1);n=max(len(a.ls),len(b.ls));delta=np.zeros((n,len(r)))
        if lo<a.boundaries[-1]:delta[:len(a.ls)]+=a.radial(r)
        if lo<b.boundaries[-1]:delta[:len(b.ls)]-=b.radial(r)
        total+=np.sum(delta*delta*(w*jac))
    return float(np.sqrt(total))
base=load_pair('B_l96');rows=[]
for tag in ('B_l72','B_l96_h80','B_l96_p5','B_l96_q22','B_l96_tail32'):
    rows.append({'tag':tag,'L2_increment_stable':[distance(a,b) for a,b in zip(base,load_pair(tag))]})
atomic_json(ROOT/'evidence/STATE_INCREMENT_AUDIT.json',{'rows':rows,'method':'direct squared difference with exact piecewise polynomial quadrature; no 2-2overlap cancellation','scope':'discrete state increments, not continuum error certificate','reducer_sha256':sha256(__file__)})
print(rows)
