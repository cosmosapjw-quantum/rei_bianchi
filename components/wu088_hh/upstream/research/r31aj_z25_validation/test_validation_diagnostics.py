import hashlib
import importlib.util
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

m = load(HERE / "validation_diagnostics.py", "diag")
epath = HERE.parent / "r31ad_five_node" / "unit_cell_model.py"
e = load(epath, "pinned_engine")


def test_midpoint_formula_matches_pinned_engine():
    rng = np.random.default_rng(31025)
    arrays = [rng.normal(size=(4,2)) + 1j*rng.normal(size=(4,2)) for _ in range(6)]
    o0,o1,d0,d1,k0,k1 = arrays
    got = m.midpoint_values(o0,o1,d0,d1,k0,k1,2.2358772390338113)
    expected = e.piecewise_candidate([0.,2.2358772390338113],[o0,o1],[d0,d1],[k0,k1],2.2358772390338113/2)
    for a,b in zip(got,expected[:5]):
        assert np.allclose(a,b,rtol=0,atol=3e-15)


def test_margin_enclosure_and_missing_source_bound():
    r = m.margin_bounds([.1,.2],[.5,.6],[.02,.03])
    assert r['lower'] == pytest.approx([.36,.34])
    assert r['upper'] == pytest.approx([.44,.46])
    assert r['conditional_pareto_support']
    assert m.margin_bounds([.1,.2],[.5,.6],None)['source_accuracy_certified'] is False
    assert m.margin_bounds([.1,.2],[.5,.6],None)['lower'] is None


def test_margin_factor_two_is_sharp():
    eps=.125
    g,a,r0,r1=2.,-2.,0.,eps
    d0=abs(g-r0)-abs(a-r0)
    d1=abs(g-r1)-abs(a-r1)
    assert abs(d1-d0)==2*eps
    r=m.margin_bounds([2.,2.],[2.,2.],[eps,eps])
    assert r['lower']==[-2*eps,-2*eps]
    assert not r['conditional_pareto_support']


def test_reference_perturbations_random_matrix_norms():
    rng=np.random.default_rng(3151)
    for _ in range(40):
        a,g,r0,q=[rng.normal(size=(3,2))+1j*rng.normal(size=(3,2)) for _ in range(4)]
        pert=q/np.linalg.norm(q,2)*.05
        ea=np.linalg.norm(a-r0,2); eg=np.linalg.norm(g-r0,2)
        delta_star=np.linalg.norm(g-r0-pert,2)-np.linalg.norm(a-r0-pert,2)
        lohi=m.margin_bounds([ea,ea],[eg,eg],[.05,.05])
        assert lohi['lower'][0]-1e-13<=delta_star<=lohi['upper'][0]+1e-13


def test_block_uncertainty_mapping():
    assert m.block_error_bounds(.1,.3)==pytest.approx([.2,.3])


def test_strict_radius_is_sufficient_not_source_bound():
    r=m.strict_common_radius([.06617406868623811,.06827426878354666],[.2504316158571644,.26534506458633733])
    assert r==pytest.approx(.092128773535463145)
    assert m.strict_common_radius([1.,1.],[0.,0.]) is None


def test_pareto_tolerance_boundary():
    assert not m.margin_bounds([0.,0.],[1e-10,1e-10],[0.,0.])['conditional_pareto_support']
    assert m.margin_bounds([0.,0.],[2e-10,1e-10],[0.,0.])['conditional_pareto_support']


@pytest.mark.parametrize('bad',[-1.,float('nan'),float('inf'),True,'0.1'])
def test_invalid_uncertainty(bad):
    with pytest.raises(ValueError):
        m.margin_bounds([0.,0.],[1.,1.],[bad,0.])


def test_canonicalization_disallows_float_ambiguity():
    assert m.canonical_scope_bytes({'b':True,'a':'0.0000000001'})==b'{"a":"0.0000000001","b":true}'
    for value in [1e-10,float('nan')]:
        with pytest.raises(ValueError):m.canonical_scope_bytes({'a':value})


def test_canonicalization_ascii_only():
    with pytest.raises(ValueError):m.canonical_scope_bytes({'a':'한글'})


def test_pinned_engine_identity():
    assert hashlib.sha256(epath.read_bytes()).hexdigest()=='ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0'


def test_central_cell_is_unchanged_by_exterior_refinement():
    rng=np.random.default_rng(3181)
    coarse=[0.,1.,2.,3.,4.]; fine=[0.,.5,1.,2.,3.,3.5,4.]
    def arrays(n):return [rng.normal(size=(4,2))+1j*rng.normal(size=(4,2)) for _ in range(n)]
    cv,cd,ck=arrays(5),arrays(5),arrays(5)
    fv,fd,fk=arrays(7),arrays(7),arrays(7)
    for x,y in [(cv,fv),(cd,fd),(ck,fk)]:
        y[3]=x[2].copy();y[4]=x[3].copy()
    for t in np.linspace(2.,3.,31,endpoint=False):
        c=e.piecewise_candidate(coarse,cv,cd,ck,t)
        f=e.piecewise_candidate(fine,fv,fd,fk,t)
        for a,b in zip(c[:5],f[:5]):assert np.array_equal(a,b)


def test_metric_identity_does_not_bound_connection_error():
    c=np.array([[1+1j],[2-1j]]); b=np.array([[3-2j],[-1+2j]])
    perturb=np.array([[1000+2000j],[-3000+4000j]])
    dot=c+b
    assert np.array_equal(dot-((c+perturb)+(b-perturb)),np.zeros_like(dot))
    assert np.allclose(((c+perturb)-(b-perturb))/2-(c-b)/2,perturb)
    assert np.linalg.norm(perturb,2)>5000


def test_separation_alone_does_not_force_a_winner():
    a=np.array([[1e6,0.],[0.,0.]])
    g=-a; truth=(a+g)/2
    assert np.linalg.norm(a-g,2)==2e6
    assert np.linalg.norm(a-truth,2)==np.linalg.norm(g-truth,2)
