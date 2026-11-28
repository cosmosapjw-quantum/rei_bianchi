import math
import numpy as np
import pytest

from bass_he.coherent_topology import (
    janev97_eq14_2ppi_probability,
    janev97_eq15_2psigma_coherent_probability,
    janev97_eq15_2psigma_phase_average,
)
from bass_he.transport import apply_eq50
from arseny_reimpl.eq50_scoped import ordered_scoped_branches, branch_state_indices
from arseny_reimpl.state_index import state_index


def _events():
    out=[]
    for b in ordered_scoped_branches():
        i,j=branch_state_indices(b)
        out.append((i-1,j-1,b.state_b[0]==3))
    return out


def _prot(r):
    dim=state_index(3,2,2)
    P=np.eye(dim)
    s=state_index(2,1,0)-1
    p=state_index(2,1,1)-1
    P[s,s]=1-r;P[p,s]=r
    P[s,p]=r;P[p,p]=1-r
    return P[None,:,:]


def _pvec(vals):
    return np.array([[vals[b.name] for b in ordered_scoped_branches()]],float)


def test_eq15_uniform_relative_phase_average_matches_closed_form():
    x,w=np.polynomial.legendre.leggauss(64)
    phases=(x+1)*math.pi
    for vals in [(0.02,0.1,0.3,0.4),(0.4,0.2,0.7,0.8),(0.8,0.9,0.05,0.15)]:
        p12,p23,pS,prot=vals
        avg=sum(wi*janev97_eq15_2psigma_coherent_probability(p12,p23,pS,prot,phi)
                for wi,phi in zip(w,phases))/2
        assert avg == pytest.approx(janev97_eq15_2psigma_phase_average(p12,p23,pS,prot),
                                    rel=2e-14,abs=2e-14)


def test_eq15_phase_average_equals_current_sparse_eq50_inverse_channel():
    rng=np.random.default_rng(20260927)
    branches=ordered_scoped_branches()
    dim=state_index(3,2,2);initial=np.zeros((dim,1));initial[0,0]=1
    final=state_index(2,1,0)-1
    for _ in range(250):
        vals={b.name:float(rng.uniform()) for b in branches};r=float(rng.uniform())
        got=apply_eq50(_pvec(vals),_events(),_prot(r),initial)[0,final,0]
        want=janev97_eq15_2psigma_phase_average(vals['Q12'],vals['Q23'],vals['S23'],r)
        assert got == pytest.approx(want,rel=3e-14,abs=3e-14)
        vals2=dict(vals);vals2['Qother']=float(rng.uniform());vals2['Qm1']=float(rng.uniform())
        got2=apply_eq50(_pvec(vals2),_events(),_prot(r),initial)[0,final,0]
        assert got2 == pytest.approx(got,rel=0,abs=3e-15)


def test_eq14_forward_2ppi_probability_equals_current_sparse_eq50_topology():
    rng=np.random.default_rng(20260928);branches=ordered_scoped_branches()
    dim=state_index(3,2,2);initial=np.zeros((dim,1))
    initial[state_index(2,1,0)-1,0]=1
    final=state_index(2,1,1)-1
    for _ in range(250):
        vals={b.name:float(rng.uniform()) for b in branches};r=float(rng.uniform())
        got=apply_eq50(_pvec(vals),_events(),_prot(r),initial)[0,final,0]
        want=janev97_eq14_2ppi_probability(vals['Q23'],vals['Q12'],vals['S23'],vals['Qm1'],r)
        assert got == pytest.approx(want,rel=3e-14,abs=3e-14)
        vals2=dict(vals);vals2['Qother']=float(rng.uniform())
        got2=apply_eq50(_pvec(vals2),_events(),_prot(r),initial)[0,final,0]
        assert got2 == pytest.approx(got,rel=0,abs=3e-15)


def test_source_formula_inputs_are_strict():
    with pytest.raises(ValueError):janev97_eq15_2psigma_phase_average(-0.1,0.2,0.3,0.4)
    with pytest.raises(ValueError):janev97_eq14_2ppi_probability(0.2,0.3,0.4,0.5,1.1)
    with pytest.raises(ValueError):janev97_eq15_2psigma_coherent_probability(0.2,0.3,0.4,0.5,float('nan'))
