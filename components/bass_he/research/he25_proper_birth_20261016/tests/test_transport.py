import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from physics import Model,frozen_duhamel
from native import NativeOwner
BIN='/root/HE25_NCP_BIRTH_20261016/build/he25_owner_server'

def test_frozen_opacity_phi1():
    tau=np.array([0.,1e-10,.2,5.,200.])
    surviving,absorbed=frozen_duhamel(np.zeros(5),np.ones(5),tau,1.)
    expected=np.array([1.,-np.expm1(-1e-10)/1e-10,-np.expm1(-.2)/.2,-np.expm1(-5)/5,-np.expm1(-200)/200])
    np.testing.assert_allclose(surviving,expected,rtol=2e-15,atol=0)
    np.testing.assert_allclose(surviving+absorbed,1.,atol=2e-16)
    assert np.all(surviving>=0) and np.all(absorbed>=0)

@pytest.mark.parametrize('q',[-.005,0.,.005])
def test_source_clock_killing_and_energy_identity(q):
    with NativeOwner(BIN) as owner:
        model=Model(owner,m=4,angles=4,q=q)
        for t in [0.,model.t_end*.37,model.t_end]:
            x=model.x(t);E,mu,dEdt=model.geometry(t)
            assert abs(sum(model.source(t))/(model.H(t)*model.source_per_x)-1)<2e-14
            assert np.all(model.source(t)>=0)
            assert np.all(model.source(t)[(E<13.6)|(E>100.)]==0.)
            assert np.max(abs(mu))<1 and np.all(dEdt<0)
        ta=model.t_end*.2;tb=model.t_end*.8
        Ea,mua,_=model.geometry(ta);Eb,_,_=model.geometry(tb)
        dx=model.x(tb)-model.x(ta)
        from he21_photo import redshift_vector
        np.testing.assert_allclose(Eb/Ea,redshift_vector(dx,mua,q),rtol=8e-15)
        y=model.initial_state();y[4:4+model.K]=model.scale[4:4+model.K]*.01
        f=model.rhs(ta,y);r=model.conservation_rate(ta,y,f)
        assert abs(r['number'])<1e-25
        assert abs(r['energy'])<1e-25

def test_duhamel_cell_frozen_phi1_and_positive_events():
    from transport import BirthCell
    class Frozen:
        K=2
        def set_interval(self,a,b):pass
        def source(self,t):return np.array([1.,2.])
        def geometry(self,t):return np.array([30.,80.]),np.zeros(2),np.zeros(2)
    c=BirthCell(Frozen(),0.,1.)
    lam=np.array([[.2,.1,0.],[100.,50.,20.]])
    survive,events,heats,work=c.photon_map(np.array([.4,.3]),lam)
    expected,_=frozen_duhamel(np.array([.4,.3]),np.array([1.,2.]),lam.sum(axis=1),1.)
    np.testing.assert_array_equal(survive,expected)
    assert abs(sum(survive)+sum(events)-3.7)<1e-14
    assert np.all(heats>=0) and work==0

def test_geometry_clock_and_sourcefree_limit():
    from scipy.integrate import quad
    from transport import solve_transport
    from physics import Hubble
    with NativeOwner(BIN) as owner:
        m=Model(owner,m=4,angles=4,q=0.,source_count=0.)
        for f in [.1,.5,.9]:
            t=f*m.t_end
            independent=quad(lambda x:1/Hubble(x),0,m.x(t),epsabs=.0001,epsrel=3e-14)[0]
            assert abs(independent-t)<3e-13*m.t_end
        r=solve_transport(m,n=16)
        assert r['photon_number']==0 and r['ledger']['birth_n']==0
        assert abs(r['energy_defect_ev'])<3e-12
        assert r['ledger']['work_p']==0 and r['gas_positive']
