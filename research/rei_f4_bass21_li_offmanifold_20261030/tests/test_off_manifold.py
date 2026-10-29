import sys,unittest,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import off_manifold as m

class OffManifoldTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.net,cls.cases=m.load()
  cls.gamma=cls.net.isotope_inventory['Li6']/cls.net.isotope_inventory['Li7']
  cls.P,cls.E,cls.D,cls.T,cls.Tinv=m.maps(cls.gamma)
 def test_01_source_members_and_schema(self):
  self.assertEqual(len(self.cases),5)
  self.assertEqual(tuple(self.net.names[:7]),('n','H1I','H1II','DI','DII','TI','TII'))
 def test_02_invertible_transport(self):
  np.testing.assert_array_equal(self.T@self.Tinv,np.eye(21))
  np.testing.assert_array_equal(self.P@self.E,np.eye(17))
 def test_03_saved_original_native_f_and_j(self):
  import io,zipfile
  with zipfile.ZipFile(m.SRC/'VIGILODE_PR118_SOURCE_IMMUTABLE.zip') as z:
   with np.load(io.BytesIO(z.read('new_physics/results/ACTUAL_SOURCE_J_F_AT_ENDPOINTS.npz'))) as a:
    for i,case in enumerate(self.cases):
     self.assertEqual(str(a['case_id'][i]),case['id'])
     ev=self.net.evaluate(np.array(case['Y'],float),case['T_K'],case['uv'],case['nb_m3'])
     np.testing.assert_allclose(ev['dY_dt'],a['F_proper_s'][i],rtol=1e-12,atol=1e-32)
     np.testing.assert_allclose(ev['jac'],a['J_proper_s'][i],rtol=1e-12,atol=1e-30)
 def test_04_actual_source_electron_and_isotope(self):
  for case in self.cases:
   y=np.array(case['Y'],float)
   self.assertLess(abs(self.net.A@y-1),1e-12)
   self.assertLess(abs(case['ne_m3']-case['nb_m3']*self.net.q@y),1e-11)
   self.assertTrue(np.all(y>=0))
 def test_05_exact_lift_f_j(self):
  for case in self.cases:
   y=self.P@np.array(case['Y'])
   Ey=self.E@y
   ev=self.net.evaluate(Ey,case['T_K'],case['uv'],case['nb_m3'])
   np.testing.assert_allclose(ev['dY_dt'],self.E@(self.P@ev['dY_dt']),rtol=1e-12,atol=1e-27)
   np.testing.assert_allclose(ev['jac']@self.E,self.E@self.P@ev['jac']@self.E,rtol=1e-12,atol=2e-24)
 def test_06_full_block_source_j(self):
  for case in self.cases:
   y=self.P@np.array(case['Y']); ey=self.E@y
   ev=self.net.evaluate(ey,case['T_K'],case['uv'],case['nb_m3'])
   JJ=self.T@ev['jac']@self.Tinv
   self.assertLess(np.max(abs(JJ[17:,:17])),5e-24)
   rates=self.net.rates(case['T_K'],case['uv'])
   MM=rates['G0'][np.ix_(m.LI6,m.LI6)]+ev['ne']*rates['Gne'][np.ix_(m.LI6,m.LI6)]
   np.testing.assert_allclose(JJ[17:,17:],MM,rtol=2e-12,atol=1e-23)
   RHS=case['nb_m3']*np.outer(self.P@rates['Gne']@self.E@y,m.CHARGES)
   np.testing.assert_allclose(JJ[:17,17:],RHS,rtol=2e-12,atol=1e-25)
 def test_07_markov_contraction(self):
  for case in self.cases:
   Y=np.array(case['Y'],float);ev=self.net.evaluate(Y,case['T_K'],case['uv'],case['nb_m3'])
   r=self.net.rates(case['T_K'],case['uv'])
   M=r['G0'][np.ix_(m.LI6,m.LI6)]+ev['ne']*r['Gne'][np.ix_(m.LI6,m.LI6)]
   off=M.copy();np.fill_diagonal(off,0)
   self.assertGreaterEqual(np.min(off),0)
   self.assertLess(np.max(abs(M.sum(axis=0))),1e-25)
   self.assertLess(abs(np.max(np.diag(M)+np.sum(abs(off),axis=0))),1e-25)
 def test_07b_frozen_original_li_gap(self):
  for case in self.cases:
   d=m.evaluate_case(self.net,case)
   spectrum=np.array(d['L_static_eigenvalues_per_s'])
   self.assertEqual(len(spectrum),4)
   self.assertTrue(np.all(spectrum[:3]<-1e-18))
   self.assertLess(abs(spectrum[-1]),1e-26)
   self.assertGreater(d['L_static_relaxation_years'],1e6)
   self.assertLess(d['L_static_relaxation_years'],2e7)
   self.assertLess(d['L_detailed_balance_max_abs_per_s'],1e-27)
 def test_08_off_manifold_exact_identities(self):
  for case in self.cases:
   x=m.evaluate_case(self.net,case)
   self.assertLess(x['retained_source_defect_max_abs'],1e-24)
   self.assertLess(x['delta_source_defect_max_abs'],1e-24)
   self.assertLess(x['upper_block_diff_max_abs'],1e-23)
   self.assertLess(x['lowerleft_block_max_abs'],1e-24)
   self.assertLess(x['lowerright_block_max_abs'],1e-23)
 def test_09_retained_forcing_bound(self):
  for case in self.cases:
   x=m.evaluate_case(self.net,case)
   self.assertLessEqual(x['retained_forcing_l1_per_s'],x['retained_forcing_l1_upper_per_s']*(1+1e-12)+1e-35)
 def test_10_pointwise_tau_delta_not_history(self):
  for case in self.cases:
   r=m.evaluate_case(self.net,case)
   self.assertLessEqual(abs(r['pointwise_tau_x_gap_stable']),r['pointwise_tau_x_gap_bound']*(1+1e-12))
   self.assertLess(r['pointwise_tau_x_fp_cancellation_abs'],3e-17)
 def test_11_zero_defect_theorem_analytic(self):
  case=self.cases[0];y=self.P@np.array(case['Y']);Y=self.E@y
  rr=case.copy();rr['Y']=Y.tolist();vals=m.evaluate_case(self.net,rr)
  self.assertLess(vals['Li6_scaled_defect_l1'],1e-12)
  self.assertLess(vals['delta_source_defect_max_abs'],1e-24)
 def test_12_counterexample_li_isotope_rate_split(self):
  case=self.cases[0];y=self.P@np.array(case['Y']);Ey=self.E@y
  # Move 5% of the actual source inventory between Li6 charge +3 and +2.
  # This respects physical positivity and fixed Li6 total.
  nu6=self.net.isotope_inventory['Li6']
  delta=np.array([0.,0.,0.05*nu6,-0.05*nu6])
  Y=Ey.copy();Y[m.LI6]+=delta
  rr=case.copy();rr['Y']=Y.tolist();x=m.evaluate_case(self.net,rr)
  self.assertGreater(x['delta_l1'],0)
  self.assertGreater(x['retained_forcing_l1_per_s'],1e-35)
  self.assertLess(abs(x['Li6_scaled_defect_l1']-0.1),1e-12)
  self.assertLess(x['pointwise_tau_x_gap_stable'],0)
  # the physical upper-bound formula applies regardless of the sign of delta
  self.assertLessEqual(x['retained_forcing_l1_per_s'],x['retained_forcing_l1_upper_per_s']*(1+1e-12))

if __name__=='__main__':unittest.main()
