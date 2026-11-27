import unittest,sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mixed_family import *

def initial():return ToyState(Jet.constant(Q(1,4)),Jet.constant(Q(1,10)))
def corners():
 c=CornerIdentity('a'*64,'b'*64,'c'*64,'d'*64,Q(0),Q(1,16),Q(1),Q(1,5),'full')
 return {'LS':c,'L0':replace(c,source=Q(0)),'0S':replace(c,lam=Q(0)),'00':replace(c,lam=Q(0),source=Q(0))}

def direct_corner(old,h,lam,source):
 # Independent monotone root bracketing, not Krawczyk or derivative arithmetic.
 # 80 fixed cuts chosen before evaluating signs/mixed response; never fitted.
 def bracket(xprev,pprev):
  n=pprev+h*source
  def r(x):return x-xprev-h*((1-x)*n/(1+h*(1-x))+lam*Q(1,10)*(1-x)**2)
  lo,hi=xprev,Q(1)
  assert r(lo)<=0<=r(hi)
  for _ in range(80):
   mid=(lo+hi)/2
   if r(mid)>0:hi=mid
   else:lo=mid
  return Box(lo,hi)
 lower=bracket(old[0].lo,old[1].lo);upper=bracket(old[0].hi,old[1].hi)
 x=Box(lower.lo,upper.hi);n=old[1]+h*source;p=n/(1+h*(1-x))
 return x,p

def direct_mixed(scheme):
 vals={}
 for name,c in corners().items():
  state=(asbox(Q(1,4)),asbox(Q(1,10)))
  for h in ([c.duration]if scheme=='full'else[c.duration/2,c.duration/2]):state=direct_corner(state,h,c.lam,c.source)
  vals[name]=state[0]
 return vals['LS']-vals['L0']-vals['0S']+vals['00'],vals

class MixedFamilyTests(unittest.TestCase):
 def test_corner_contract(self):self.assertTrue(validate_four_corners(corners()))
 def test_all_shared_identity_mutations_rejected(self):
  for field,value in [('initial_state_sha256','e'*64),('theta_sha256','e'*64),('source_law_sha256','e'*64),('birth_measure_sha256','e'*64),('clock',Q(1)),('duration',Q(1,32)),('scheme','twohalf'),('source',Q(1))]:
   c=corners();c['L0']=replace(c['L0'],**{field:value})
   with self.assertRaises(Unresolved):validate_four_corners(c)
 def test_missing_and_forged_native_certificate_rejected(self):
  with self.assertRaisesRegex(Unresolved,'AUTHORIZATION'):native_mixed_response(corners())
  with self.assertRaisesRegex(Unresolved,'TRUSTED_NATIVE'):native_mixed_response(corners(),{'certified':True},{'approved':True})
 def test_correlated_common_errors_cancel(self):
  huge=Box(Q(-10**30),Q(10**30));c={(0,0):huge,(1,0):huge,(0,1):huge,(1,1):asbox(Q(-3)),(2,1):asbox(Q(1))}
  self.assertEqual(correlated_polynomial_difference(c,Q(2),Q(5)),asbox(Q(-10)))
 def test_full_chain_jacobian_includes_photon_elimination(self):
  h=Q(1,16);m=ToyModel();x=Jet.variable(Q(1,4),0);lam=Jet.variable(Q(1),1);s=Jet.variable(Q(1,5),2);old=initial();r=residual(x,old,lam,s,h,m);n=old.photons.value+h*s.value
  self.assertEqual(r.gradient[0],full_chain_M(x.value,n,lam.value,h,m))
  # Holding eliminated P fixed omits its x chain; it produces a different M.
  den=1+h*(1-Q(1,4));fixed_photon_M=1+h*(Q(1,10)+h*Q(1,5))/den+2*h*Q(1,10)*(1-Q(1,4))
  self.assertNotEqual(r.gradient[0],asbox(fixed_photon_M))
 def test_whole_discrete_family_encloses_independent_corners(self):
  for scheme in ['full','twohalf']:
   out=synthetic_family(initial(),Box(Q(0),Q(1)),Box(Q(0),Q(1,5)),Q(1,16),scheme);mixed,vals=direct_mixed(scheme)
   self.assertTrue(out['mixed_interval'].contains(mixed));self.assertFalse(out['native_certified'])
   for cert in out['certificates']:
    self.assertLess(Q(cert['scaled_contraction']),1);self.assertFalse(cert['native_trusted'])
 def test_zero_future_birth_preserves_old_photon_stock(self):
  zero=synthetic_family(initial(),Box(Q(0),Q(1)),asbox(0),Q(1,16),'full')
  self.assertEqual(zero['mixed_interval'],Z)
  self.assertGreater(zero['state'].photons.value.lo,0)
  self.assertGreater(zero['state'].x.value.lo,Q(1,4))
 def test_second_half_carries_gas_and_photon_derivatives(self):
  box=Box(Q(0),Q(1));sb=Box(Q(0),Q(1,5));first,_=synthetic_stage_family(initial(),box,sb,Q(1,32));second,_=synthetic_stage_family(first,box,sb,Q(1,32));reset=ToyState(Jet.constant(first.x.value),Jet.constant(first.photons.value));wrong,_=synthetic_stage_family(reset,box,sb,Q(1,32))
  self.assertNotEqual(second.x.gradient,wrong.x.gradient);self.assertNotEqual(second.photons.hessian,wrong.photons.hessian)
 def test_implicit_parameter_derivative_equations_contain_zero(self):
  old=initial();out,_=synthetic_stage_family(old,Box(Q(0),Q(1)),Box(Q(0),Q(1,5)),Q(1,16));r=residual(out.x,old,Jet.variable(Box(Q(0),Q(1)),1),Jet.variable(Box(Q(0),Q(1,5)),2),Q(1,16),ToyModel())
  for i in [1,2]:self.assertTrue(r.gradient[i].contains(Z))
  self.assertTrue(r.hessian[1][2].contains(Z))
 def test_float_and_large_synthetic_step_refused(self):
  with self.assertRaises(Unresolved):asbox(0.5)
  with self.assertRaises(Unresolved):synthetic_family(initial(),asbox(1),asbox(1),Q(1),'full')
if __name__=='__main__':unittest.main()
