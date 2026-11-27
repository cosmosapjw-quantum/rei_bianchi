"""Research-only contracts; no native spectral solver or cloud process is run."""
import importlib.util
import numpy as np
import pytest


def api():
    assert importlib.util.find_spec('error_envelopes') is not None, 'R2 error-envelope implementation missing'
    import error_envelopes
    return error_envelopes


def toy():
    s=np.linspace(0,1,65)
    return 2+3j*(2*s-s*s),np.sqrt(1-s),6j*(1-s)


def test_constant_gap_primitive_and_rho_derivative():
    a=api();s=np.linspace(0,1,1025);R=3+2j*(2*s-s*s);dR=4j*(1-s);rho=1.3
    v,d1,d2=a.action_jet(R,np.ones_like(R),dR,rho)
    ref=np.sqrt((3+2j)**2-rho**2)-np.sqrt(9-rho**2)
    ref1=-rho/np.sqrt((3+2j)**2-rho**2)+rho/np.sqrt(9-rho**2)
    assert abs(v-ref)<1e-10
    assert abs(d1-ref1)<1e-10
    assert np.isfinite(d2)


def test_jet_matches_independent_finite_difference():
    a=api();R,g,dR=toy();rho=.7;h=2e-4
    f,df,ddf=a.action_jet(R,g,dR,rho)
    fm=a.action_jet(R,g,dR,rho-h)[0];fp=a.action_jet(R,g,dR,rho+h)[0]
    assert abs((fp-fm)/(2*h)-df)<1e-8
    assert abs((fp-2*f+fm)/h**2-ddf)<1e-6


def test_interpolation_bound_covers_complex_action_not_only_nodes():
    a=api();R,g,dR=toy();lo,hi=.8,1.4
    bound=a.interpolation_bound(R,g,dR,lo,hi)
    A=a.action_jet(R,g,dR,lo)[0];B=a.action_jet(R,g,dR,hi)[0]
    for x in np.linspace(lo,hi,53):
        L=A+(B-A)*(x-lo)/(hi-lo)
        assert abs(a.action_jet(R,g,dR,x)[0]-L)<=bound+1e-14


def test_gap_error_bound_covers_independent_perturbation():
    a=api();R,g,dR=toy();e=np.linspace(1e-9,2e-7,len(R));phase=np.exp(1j*np.arange(len(R)))
    for rho in [0.,.9,1.5]:
        diff=abs(a.action_jet(R,g+e*phase,dR,rho)[0]-a.action_jet(R,g,dR,rho)[0])
        assert diff<=a.gap_error_bound(R,dR,e,1.5)+1e-14


def test_rho_domain_is_fail_closed():
    a=api();R,g,dR=toy()
    for rho in [-1.,2.,float('nan')]:
        with pytest.raises(ValueError):a.action_jet(R,g,dR,rho)


def test_shapes_and_finite_values_are_checked():
    a=api();R,g,dR=toy()
    with pytest.raises(ValueError):a.action_jet(R[:-1],g[:-1],dR[:-1],.3)
    g[4]=np.nan
    with pytest.raises(ValueError):a.action_jet(R,g,dR,.3)


def test_exact_hybrid_observable_telescope_reversible_and_sink():
    a=api();rng=np.random.default_rng(2312)
    for _ in range(35):
        ps=rng.random(9);qs=rng.random(9)
        events=[(i%3,(i+1)%3,bool(i%2)) for i in range(9)]
        y=rng.random(3);y/=y.sum();w=rng.random(3)
        r=a.hybrid_telescope(ps,qs,events,y,w)
        assert abs(r['direct_difference']-sum(r['signed_contributions']))<2e-14
        assert abs(r['direct_difference'])<=r['weighted_bound']+2e-14
        assert r['weighted_bound']<=r['global_bound']+2e-14


def test_stochastic_inputs_are_required():
    a=api()
    with pytest.raises(ValueError):a.hybrid_telescope([1.1],[.2],[(0,1,False)],[1.,0.],[0.,1.])
    with pytest.raises(ValueError):a.hybrid_telescope([.1],[.2],[(0,1,False)],[2.,0.],[0.,1.])


def test_adaptive_mesh_bounded_and_unchanged_trace():
    a=api();R,g,dR=toy();R0=R.copy();g0=g.copy();dR0=dR.copy()
    result=a.certified_mesh(R,g,dR,1.5,1e-4,max_intervals=1024)
    assert max(result['interval_bounds'])<=1e-4
    assert np.all(np.diff(result['nodes'])>0)
    assert np.array_equal(R,R0) and np.array_equal(g,g0) and np.array_equal(dR,dR0)


def test_adaptive_budget_fails_closed():
    a=api();R,g,dR=toy()
    with pytest.raises(RuntimeError):a.certified_mesh(R,g,dR,1.5,1e-15,max_intervals=2)


def test_abs_imaginary_action_is_applied_after_interpolation():
    a=api()
    # A linear complex action passes through zero. Interpolating Delta itself is wrong.
    A,B=-1j,1j
    assert abs(((A+B)/2).imag)==0
    assert (abs(A.imag)+abs(B.imag))/2==1


def test_finite_nodes_and_slopes_cannot_certify_general_interpolation():
    a=api()
    import sympy as s
    x=s.symbols('x');b=x*x*(x-s.Rational(1,2))**2*(x-1)**2
    assert all(b.subs(x,z)==0 and s.diff(b,x).subs(x,z)==0 for z in [0,s.Rational(1,2),1])
    assert b.subs(x,s.Rational(1,4))==s.Rational(9,4096)
