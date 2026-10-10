import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from characteristics import exponential_step, geometry_nodes


def test_constant_coefficients_source_has_correct_residence_time():
    for x in (0., 1e-12, 1e-5, 1., 100., 1e6):
        n0, source, dt = np.array([.3]), np.array([.7]), 2.
        k = np.array([[.2, .3, .5]]) * x/dt
        out = exponential_step(n0, source, k, dt)
        # Independent high-precision scalar formula, not implementation phi helpers.
        from decimal import Decimal, localcontext
        with localcontext() as context:
            context.prec=60
            xx = Decimal(str(x))
            want = Decimal('.3') * (-xx).exp()
            want += Decimal('1.4') * ((1-(-xx).exp())/xx if x else 1)
        assert np.allclose(out['number'], float(want), rtol=3e-13, atol=0)
        residual = out['number'] + out['absorbed_by_species'].sum(1) - n0 - source*dt
        assert np.max(abs(residual))/(n0+source*dt) < 1e-12
        assert (out['number'] >= 0).all()
        assert (out['absorbed_by_species'] >= 0).all()
        if x:
            ratios=out['absorbed_by_species'][0]/out['absorbed_by_species'].sum()
            assert np.allclose(ratios, [.2,.3,.5], rtol=1e-14)


def test_fixed_covector_keeps_threshold_activity_without_remapping():
    q=np.array([13.7, 25., 60.]); mu=np.array([0.,.3,1.])
    a={'a_rel':1.2,'b':.02}; b={'a_rel':1.5,'b':.03}
    ea,ma,_=geometry_nodes(q,mu,a)
    eb,mb,_=geometry_nodes(q,mu,b)
    direct=q*np.sqrt((1-mu**2)*np.exp(2*b['b'])+mu**2*np.exp(-4*b['b']))/b['a_rel']
    assert np.allclose(eb,direct,rtol=1e-14)
    # Transport A->B using the actual intermediate covector, never hat weights.
    ap=a['a_rel']*np.exp(-a['b']); az=a['a_rel']*np.exp(2*a['b'])
    bp=b['a_rel']*np.exp(-b['b']); bz=b['a_rel']*np.exp(2*b['b'])
    chained=ea*np.sqrt((1-ma**2)*(ap/bp)**2+ma**2*(az/bz)**2)
    assert np.allclose(eb,chained,rtol=1e-13)
    assert np.array_equal(eb>=13.60,direct>=13.60)


def test_rejects_bad_domains_without_clipping():
    for n,s,k,dt in [([-1.],[1.],[[1.,0.,0.]],1.),([1.],[-1.],[[1.,0.,0.]],1.),
                      ([1.],[1.],[[-1.,0.,0.]],1.),([1.],[1.],[[1.,0.,0.]],-1.)]:
        with pytest.raises(ValueError): exponential_step(np.array(n),np.array(s),np.array(k),dt)
