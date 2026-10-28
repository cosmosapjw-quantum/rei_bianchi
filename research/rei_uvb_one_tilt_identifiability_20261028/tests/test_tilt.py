import sys,unittest,math,json
from pathlib import Path
from decimal import Decimal
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from tilt_gls import fit
from reference_decimal import fit as reference
BB=json.loads((ROOT/'input'/'BB13.json').read_text());CAL=json.loads((ROOT/'input'/'CALIBRATION_RESULT.json').read_text())
Z=BB['z'];D=BB['values'];M=CAL['template_log10_Gamma12'];C=BB['statistical_covariance_dex2']
A=fit(Z,D,M,C)
class TiltTests(unittest.TestCase):
 def test_frozen_x(self):self.assertEqual(A['x'],[v-3.6 for v in Z])
 def test_source_known_beta(self):self.assertAlmostEqual(A['beta0'],CAL['statistical_only']['beta_log10_amplitude'],places=11)
 def test_source_known_chi2(self):self.assertAlmostEqual(A['Q0'],19.381736839571925,places=10)
 def test_info_SPD(self):self.assertGreater(A['det_information'],0)
 def test_cov_symmetric(self):self.assertEqual(A['covariance'][0][1],A['covariance'][1][0])
 def test_cov_positive(self):self.assertGreater(A['covariance'][0][0],0);self.assertGreater(A['covariance'][1][1],0)
 def test_nested_Q(self):self.assertGreaterEqual(A['DeltaQ'],-1e-12)
 def test_delta_identity(self):self.assertAlmostEqual(A['DeltaQ'],A['delta_from_slope_identity'],places=10)
 def test_degrees_freedom(self):self.assertEqual((A['dof0'],A['dof2']),(6,5))
 def test_conditional_model(self):self.assertEqual(A['fixed_EOS_theta'],0)
 def test_amplitude_shift_invariance(self):
  x=fit(Z,[v+.125 for v in D],M,C)
  self.assertAlmostEqual(x['Q2'],A['Q2'],places=9);self.assertAlmostEqual(x['kappa'],A['kappa'],places=11)
  self.assertAlmostEqual(x['beta'],A['beta']+.125,places=11)
 def test_template_shift_invariance(self):
  x=fit(Z,D,[v+.25 for v in M],C)
  self.assertAlmostEqual(x['kappa'],A['kappa'],places=11);self.assertAlmostEqual(x['Q2'],A['Q2'],places=9)
 def test_joint_permutation(self):
  idx=[6,2,0,4,1,5,3];cc=[[C[i][j] for j in idx] for i in idx]
  x=fit([Z[i] for i in idx],[D[i] for i in idx],[M[i] for i in idx],cc)
  self.assertAlmostEqual(x['Q2'],A['Q2'],places=9);self.assertAlmostEqual(x['kappa'],A['kappa'],places=10)
 def test_diagonal_wrong_covariance_detectable(self):
  cv=[[C[i][j] if i==j else 0 for j in range(7)] for i in range(7)]
  x=fit(Z,D,M,cv);self.assertGreater(abs(x['Q2']-A['Q2']),1e-2)
 def test_decimal_reference(self):
  b=reference(Z,D,M,C); self.assertLess(abs(float(b['beta'])-A['beta']),1e-12)
  self.assertLess(abs(float(b['kappa'])-A['kappa']),1e-12)
  self.assertLess(abs(float(b['Q2'])-A['Q2']),1e-10)
  self.assertLess(abs(float(b['DeltaQ'])-A['DeltaQ']),1e-10)
 def test_synthetic_zero_slope(self):
  z=Z;m=[0.0]*7;d=[.3]*7;x=fit(z,d,m,C)
  self.assertLess(abs(x['kappa']),1e-12);self.assertLess(x['Q2'],1e-20)
 def test_synthetic_exact_slope(self):
  m=[0.0]*7;d=[.3-.1*(v-3.6) for v in Z];x=fit(Z,d,m,C)
  self.assertAlmostEqual(x['kappa'],-.1,places=11);self.assertLess(x['Q2'],1e-20)
 def test_invalid_bad_shape(self):
  with self.assertRaises(ValueError):fit(Z[:-1],D,M,C)
 def test_invalid_nonsymmetric(self):
  c=deepcopy(C);c[0][1]*=2
  with self.assertRaises(ValueError):fit(Z,D,M,c)
 def test_invalid_nonSPD(self):
  c=[[0.0]*7 for _ in range(7)]
  with self.assertRaises(ValueError):fit(Z,D,M,c)
 def test_invalid_duplicate_redshift(self):
  z=Z.copy();z[4]=z[3]
  with self.assertRaises(ValueError):fit(z,D,M,C)
 def test_invalid_nan(self):
  d=D.copy();d[3]=float('nan')
  with self.assertRaises(ValueError):fit(Z,d,M,C)
 def test_invalid_other_anchor(self):
  with self.assertRaises(ValueError):fit(Z,D,M,C,z0=3.7)
 def test_no_data_drop(self):self.assertEqual(len(A['residual2']),7)
if __name__=='__main__':unittest.main(verbosity=2)
