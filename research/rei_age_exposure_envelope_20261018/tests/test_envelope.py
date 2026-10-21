import math
import pytest
import age_envelope as ae

def test_constant_scalar_number_and_exposure():
    got = ae.enclosure((1.,1.),(2.,2.),[(3.,3.),(0.,0.),(0.,0.)],.5,(20.,20.))
    assert got is not None, 'missing positive photon/exposure enclosure'
    expected = math.exp(-1.5)+2*(-math.expm1(-1.5))/3
    assert got.n[0] == pytest.approx(expected,rel=3e-15)
    assert got.n[1] == pytest.approx(expected,rel=3e-15)
    assert got.absorbed[0][0] == pytest.approx(2-expected,rel=5e-15)

@pytest.mark.parametrize('tau',[0.,1e-14,1e-8,.001,.01,1.,10.,1000.])
def test_stable_phi_functions_against_high_precision(tau):
    import mpmath as mp
    with mp.workdps(70):
        t=mp.mpf(tau)
        f=mp.mpf(1) if t==0 else -mp.expm1(-t)/t
        g=mp.mpf('.5') if t==0 else (1-f)/t
    assert ae.phi1(tau)==pytest.approx(float(f),rel=3e-14,abs=0)
    assert ae.phi2(tau)==pytest.approx(float(g),rel=3e-14,abs=0)

@pytest.mark.parametrize('k',[0.,1e-12,1.,1e6])
def test_number_conservation_and_exposure(k):
    n,j,h=3e-5,7e-5,.3
    end,expo=ae.constant_flow(n,j,k,h)
    assert end>=0 and expo>=0
    assert end+k*expo==pytest.approx(n+j*h,rel=8e-15)

@pytest.mark.parametrize('bad',[-1.,float('nan'),float('inf')])
def test_invalid_optical_depth_rejected(bad):
    with pytest.raises(ValueError):ae.phi1(bad)
    with pytest.raises(ValueError):ae.phi2(bad)

def test_zero_species_and_zero_photons():
    e=ae.enclosure((0,0),(0,0),[(0,0)]*3,.2,(0,100))
    assert e.n==(0,0) and e.heat==(0,0) and e.absorbed==((0,0),)*3

def test_different_fit_and_binding_are_not_merged():
    # At the allowed fit edge the excess energy is small but nonzero.
    e=ae.enclosure((1,1),(0,0),[(0,0),(1,1),(0,0)],1,(24.59,24.59))
    assert e.heat[0]>0
    assert e.absorbed_energy[0]==pytest.approx(e.heat[0]+e.binding[0],rel=5e-15)

def test_unsplit_active_threshold_rejected():
    with pytest.raises(ValueError,match='THRESHOLD_EVENT_UNSPLIT'):
        ae.enclosure((1,1),(0,0),[(0,0),(1,2),(0,0)],.5,(24.58,25))

def test_inconsistent_active_below_fit_rejected():
    with pytest.raises(ValueError,match='ACTIVE_RATE_BELOW_FIT'):
        ae.enclosure((1,1),(0,0),[(0,0),(0,0),(1,1)],.5,(10,30))

@pytest.mark.parametrize('q',[-.1,0.,.1])
def test_lrs_box_contains_exact_signed_rays(q):
    import numpy as np
    xa,xb=.02,.12
    ba,bb=sorted((q*xa,q*xb))
    for mu in (-1.,-.37,0.,.81,1.):
        lo,hi=ae.lrs_energy_bounds(80,mu,0,(xa,xb),0,(ba,bb))
        for x in np.linspace(xa,xb,101):
            value=80*math.exp(-x)*math.sqrt((1-mu*mu)*math.exp(2*q*x)+mu*mu*math.exp(-4*q*x))
            assert lo-2e-14<=value<=hi+2e-14

def test_observer_before_birth_rejected():
    with pytest.raises(ValueError):ae.lrs_energy_bounds(80,0,0,(-.1,.1),0,(0,.01))

def test_enclosure_initial_and_coefficient_monotonicity():
    small=ae.enclosure((.1,.1),(.2,.2),[(1,1),(2,2),(0,0)],.1,(80,80))
    wide=ae.enclosure((.09,.11),(.19,.21),[(.9,1.1),(1.9,2.1),(0,0)],.1,(79,81))
    assert wide.n[0]<=small.n[0]<=wide.n[1]
    for s,w in zip(small.absorbed,wide.absorbed):assert w[0]<=s[0]<=w[1]
    assert wide.heat[0]<=small.heat[0]<=wide.heat[1]

@pytest.mark.parametrize('star',[.73,.985])
def test_independent_piecewise_radau_inside_exposure_bounds(star):
    from run_study import reference,evaluate
    truth,calls=reference(star)
    assert calls>0
    for n in (8,32,128):
        for split in (False,True):
            r=evaluate(n,star,split)
            assert r['n'][0]-2e-15<=truth[0]<=r['n'][1]+2e-15
            for bounds,t in zip(r['absorbed'],truth[1:]):assert bounds[0]-2e-15<=t<=bounds[1]+2e-15
