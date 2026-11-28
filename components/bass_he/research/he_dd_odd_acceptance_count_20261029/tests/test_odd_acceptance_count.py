import unittest, sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from odd_acceptance_count import (rat,reweight_outer,odd_leakage_envelope,
                                  marked_event_moments,poisson_cross_covariance,physics_gate)
D2=F('12834742575893748070725/3378807374235230161')
K0=F('153.0767609')
class TestExact(unittest.TestCase):
 def test_rational_accepts_only_exact(self):
  self.assertEqual(rat('0.5'),F(1,2))
  for x in [0.1,True,False,{},None]:
   with self.assertRaises(TypeError):rat(x)
 def test_pr111_reweight_identity(self):self.assertEqual(reweight_outer('0.2','0.4',1),(F(1,5),F(2,5)))
 def test_bad_envelope(self):
  for args in [(0,1,0),(-1,1,1),(1,0,1),(0,2,1)]:
   with self.assertRaises(ValueError):reweight_outer(*args)
 def test_eta_is_delta_at_symmetric_band(self):
  a=odd_leakage_envelope(F(1,4),F(3,4),F(21,19),D2)
  self.assertEqual(a['eta'],F(1,20))
 def test_explicit_exchange_even_response(self):
  a=odd_leakage_envelope(F(1,4),F(1,2),F(21,19),D2,exchange_even_response=True)
  self.assertEqual(a['eta'],0)
  self.assertEqual(a['m2_upper'],0)
  self.assertEqual(a['conditional_var_lower_MeV2'],D2*a['bq_lower'])
 def test_even_flag_nonboolean_rejected(self):
  with self.assertRaises(TypeError):odd_leakage_envelope(0,1,2,D2,exchange_even_response='yes')
 def test_zero_odd_symmetry(self):
  x=odd_leakage_envelope(F(1,4),F(1,3),1,D2)
  self.assertEqual(x['m2_upper'],0)
  self.assertEqual(x['conditional_var_lower_MeV2'],D2/4)
 def test_rigorous_nonnegativity(self):
  for d in [F(0),D2]:
   e=odd_leakage_envelope(F(0),F(1),F(21,19),d)
   self.assertGreaterEqual(e['conditional_var_lower_MeV2'],0)
   self.assertGreaterEqual(e['conditional_var_upper_MeV2'],e['conditional_var_lower_MeV2'])
 def test_single_event_perfect_anticorrelation(self):
  z=marked_event_moments(15,3,F(1,4),F(1,2),1,0)
  self.assertEqual(z['covariance'].xx,-z['covariance'].xy)
  self.assertEqual(z['covariance'].xx,z['covariance'].yy)
  self.assertEqual(z['pair_total_variance'],0)
 def test_poisson_cancellation(self):
  m,b,lam=F(1,4),F(1,2),F(10)
  z=marked_event_moments(15,3,m,b,lam,lam)
  self.assertEqual(z['covariance'].xy,poisson_cross_covariance(15,9,b,lam))
 def test_fixed_count_negative_cross(self):
  z=marked_event_moments(15,3,F(1,4),F(1,2),3,0)
  self.assertLess(z['covariance'].xy,0)
 def test_common_contrast_cov(self):
  z=marked_event_moments(15,3,F(1,4),F(1,2),F(10),F(10))
  self.assertEqual(z['sum_difference_covariance'],F(4)*F(10)*F(15)*F(3)/4)
  self.assertGreater(z['sum_difference_covariance'],0)
 def test_unphysical_moments_rejected(self):
  for m,b in [(1,0),(F(1,2),F(1,8))]:
   with self.assertRaises(ValueError):marked_event_moments(15,3,m,b,1,0)
 def test_integral_event_count_moment_floor(self):
  with self.assertRaises(ValueError):marked_event_moments(15,3,0,F(1,2),F(1,2),F(0))
  z=marked_event_moments(15,3,0,F(1,2),F(1,2),F(1,4))
  self.assertEqual(z['pair_total_variance'],4*F(1,4)*15*15)
 def test_impossible_daughter_negative_energy(self):
  with self.assertRaises(ValueError):marked_event_moments(2,3,0,F(1,2),1,1)
  with self.assertRaises(ValueError):poisson_cross_covariance(2,9,F(1,2),1)
 def test_psd_covariance(self):
  for m in [F(-1,4),F(0),F(1,4)]:
   for b in [F(1,4),F(1,2)]:
    for lam,nu in [(1,0),(F(1,2),F(1,4)),(1,1),(2,4)]:
     z=marked_event_moments(15,3,m,b,lam,nu)
     c=z['covariance']
     self.assertGreaterEqual(c.xx,0)
     self.assertGreaterEqual(c.yy,0)
     self.assertGreaterEqual(c.xx*c.yy-c.xy*c.xy,0)
 def test_two_point_leakage_sharp(self):
  for rr in [F(1),F(3,2),F(5)]:
   mu=F(3,4)
   qp,qm=rr,F(1)
   m=mu*(qp-qm)/(qp+qm)
   b=mu*mu
   eta=(rr-1)/(rr+1)
   self.assertEqual(m*m,eta*eta*b)
 def test_none_is_not_zero_rate(self):
  g=physics_gate();self.assertIsNone(g['R_event']);self.assertFalse(g['physical_activation']);self.assertEqual(g['production'],'HOLD')
 def test_discrete_even_distribution_exhaustive(self):
  # Paired x in {1/4,1/2,3/4,1}, arbitrary positive rational q+,q-.
  for xnum in range(1,5):
   x=F(xnum,4)
   for p in range(1,6):
    for q in range(1,6):
     qp,qm=F(p),F(q)
     den=qp+qm
     m=x*(qp-qm)/den
     b=x*x
     r=max(qp,qm)/min(qp,qm)
     eta=(r-1)/(r+1)
     self.assertLessEqual(m*m,eta*eta*b)
     self.assertLessEqual((1-eta*eta)*b,b-m*m)
 def test_discrete_mixture_rigorous(self):
  for weight_num in range(1,5):
   p=F(weight_num,5)
   for q1p in [1,2,5]:
    for q1m in [1,2,5]:
     for q2p in [1,2,5]:
      for q2m in [1,2,5]:
       w=[p/2,p/2,(1-p)/2,(1-p)/2]
       x=[F(1,4),-F(1,4),F(3,4),-F(3,4)]
       q=list(map(F,[q1p,q1m,q2p,q2m]))
       den=sum(a*b for a,b in zip(w,q))
       m=sum(a*b*c for a,b,c in zip(w,q,x))/den
       bq=sum(a*b*c*c for a,b,c in zip(w,q,x))/den
       base=sum(a*c*c for a,c in zip(w,x))
       rr=max(q)/min(q)
       v=odd_leakage_envelope(base,base,rr,D2)
       self.assertTrue(v['bq_lower']<=bq<=v['bq_upper'])
       self.assertLessEqual(m*m,v['eta']*v['eta']*bq)
       self.assertTrue(v['conditional_var_lower_MeV2']<=D2*(bq-m*m)<=v['conditional_var_upper_MeV2'])
if __name__=='__main__': unittest.main(verbosity=2)
