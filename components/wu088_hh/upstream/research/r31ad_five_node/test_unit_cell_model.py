
import numpy as np, pytest, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"unit_cell_model.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def nodes():
    times=np.arange(5,dtype=float)
    values=[np.array([[t*t+1j*t]]) for t in times]
    derivs=[np.array([[2*t+1j]]) for t in times]
    ks=[np.array([[1+0.5*t+1j*(2-t)]]) for t in times]
    return times,values,derivs,ks

def test_nodes_exact_and_metric_identity():
    t,v,d,k=nodes()
    for j,x in enumerate(t):
        O,dot,Dc,Dr,K,_=m.piecewise_candidate(t,v,d,k,x)
        assert np.allclose(O,v[j],atol=2e-14)
        assert np.allclose(dot,d[j],atol=2e-14)
        assert np.allclose(K,k[j],atol=2e-14)
        assert np.linalg.norm(dot-Dc-Dr.conj().T)<2e-14

def test_c1_at_internal_nodes():
    t,v,d,k=nodes()
    for j in [1,2,3]:
        eps=1e-9
        Ol,dl,*_=m.piecewise_candidate(t,v,d,k,j-eps)
        Or,dr,*_=m.piecewise_candidate(t,v,d,k,j+eps)
        assert np.linalg.norm(Ol-Or)<1e-7
        assert np.linalg.norm(dl-dr)<1e-7

def test_quadratic_O_exact_under_cubic_hermite():
    t,v,d,k=nodes()
    for x in np.linspace(0,4,17):
        O,dot,*_=m.piecewise_candidate(t,v,d,k,float(x))
        assert O[0,0]==pytest.approx(x*x+1j*x,abs=2e-13)
        assert dot[0,0]==pytest.approx(2*x+1j,abs=2e-13)

def test_selection_rule():
    def old(z):
        a=np.array([[0.]])
        return (a,a,a,a,a)
    def new(z):
        a=np.array([[z]])
        b=np.array([[2*z]])
        return (a,a,b,b,a)
    r=m.select_midpoint([.5,1.5,2.5,3.5],old,new)
    assert r["selected_z"]==3.5

def test_bad_inputs():
    t,v,d,k=nodes()
    with pytest.raises(ValueError): m.piecewise_candidate([0,0],v[:2],d[:2],k[:2],0)
    with pytest.raises(ValueError): m.piecewise_candidate(t,v,d,k,-1)
