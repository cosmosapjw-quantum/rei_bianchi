from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT.parent/'he25_proper_birth_20261016/src')]
from native import NativeOwner
from physics import Model
from transport import BirthCell,frozen_duhamel
BIN='/root/HE25_NCP_BIRTH_20261016/build/he25_owner_server'
SHA='22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5'
@pytest.mark.parametrize('q',[-.005,0.,.005])
def test_native_rhs_ledgers_sourcefree_and_k(q):
 from sourcecut import SourceCutModel
 with NativeOwner(BIN,expected_binary_sha256=SHA) as owner:
  b=Model(owner,q=q);m=SourceCutModel(owner,q=q)
  np.testing.assert_array_equal(m.Eref,b.Eref)
  np.testing.assert_array_equal(m.k_perp,b.k_perp)
  np.testing.assert_array_equal(m.k_parallel,b.k_parallel)
  for frac in [0.,.37,1.]:
   t=m.t_end*frac;y=m.initial_state();y[4:4+m.K]=m.scale[4:4+m.K]*.01
   f=m.rhs(t,y);res=m.conservation_rate(t,y,f)
   assert abs(res['number'])<1e-25
   assert abs(res['energy'])<1e-25
  off=SourceCutModel(owner,q=q,source_count=0.)
  t=off.t_end*.37;y=off.initial_state()
  np.testing.assert_array_equal(off.source(t),np.zeros(off.K))
  assert np.all(off.rhs(t,y)[4:4+off.K]==0)

def test_frozen_source_recovers_phi1_in_new_transport_boundary():
 class Frozen:
  def set_interval(self,*args):pass
  def source(self,t):return np.array([2.,3.])
  def geometry(self,t):return np.array([25.,60.]),np.zeros(2),np.zeros(2)
 c=BirthCell(Frozen(),0.,2.)
 lam=np.array([[.2,.3,0.],[.4,.1,.2]])
 s,e,h,w=c.photon_map(np.zeros(2),lam)
 exact,loss=frozen_duhamel(np.zeros(2),np.array([2.,3.]),lam.sum(1),2.)
 np.testing.assert_allclose(s,exact,rtol=1e-15)
 assert abs(e.sum()-loss.sum())<1e-14
 assert np.all(e>=0) and np.all(h>=0) and w==0
