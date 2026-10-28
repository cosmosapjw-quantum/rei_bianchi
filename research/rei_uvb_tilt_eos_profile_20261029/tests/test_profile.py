import sys,unittest,math,json,copy
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'src'))
from profile import fit
from reference_decimal import fit as dfit
BB=json.loads((P/'input/BB13.json').read_text());CAL=json.loads((P/'input/CALIBRATION_RESULT.json').read_text());ONE=json.loads((P/'input/ONE_TILT_RESULT.json').read_text())
z=BB['z'];obs=BB['values'];model=CAL['template_log10_Gamma12'];C=BB['statistical_covariance_dex2'];v=BB['slope_nuisance']['response_dex'];R=fit(z,obs,model,C,v)
class Tests(unittest.TestCase):
 def close(self,a,b):self.assertTrue(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12),f'{a!r} vs {b!r}')
 def test_grid(self):self.assertEqual(R['input_z'],[2.4,2.8,3.2,3.6,4,4.4,4.75])
 def test_theta0_parent_beta(self):self.close(R['beta_theta0'],ONE['beta'])
 def test_theta0_parent_kappa(self):self.close(R['kappa_theta0'],ONE['kappa'])
 def test_theta0_parent_Q2(self):self.close(R['theta0']['Q2'],ONE['Q2'])
 def test_theta0_parent_Q0(self):self.close(R['theta0']['Q0'],CAL['statistical_only']['residual_chi2'])
 def test_theta1_parent_amplitude_profile(self):self.close(R['theta_plus']['Q0'],CAL['EOS_box_profile']['residual_chi2'])
 def test_convex_profile(self):self.assertGreater(R['Q2_quadratic_coefficients'][2],0)
 def test_outside_unconstrained_diagnostic(self):self.assertGreater(R['unconstrained_theta_diagnostic'],1)
 def test_clipped_profile(self):self.assertEqual(R['bounded_theta_star'],1)
 def test_numerical_Q_quadratic_each(self):
  for point in R['profile_points']:self.close(point['Q2'],point['Q2_quadratic'])
 def test_affine_beta_at_endpoints(self):self.close((R['theta_plus']['beta']+R['theta_minus']['beta'])/2,R['beta_theta0'])
 def test_affine_kappa_at_endpoints(self):self.close((R['theta_plus']['kappa']+R['theta_minus']['kappa'])/2,R['kappa_theta0'])
 def test_slope_decreases_with_theta(self):self.assertLess(R['kappa_dtheta'],0)
 def test_profile_max_min_from_endpoints(self):
  self.assertEqual(R['kappa_box'],[R['theta_plus']['kappa'],R['theta_minus']['kappa']])
 def test_profile_residuals_nonnegative(self):
  for p in R['profile_points']:self.assertGreater(p['Q2'],-1e-12)
 def test_nested_delta_nonnegative(self):
  for p in R['profile_points']:self.assertGreaterEqual(p['DeltaQ'],-1e-10)
 def test_nested_delta_identity(self):
  for p in R['profile_points']:self.close(p['DeltaQ'],p['DeltaQ_identity'])
 def test_conditional_covariance_positive(self):self.assertGreater(R['conditional_covariance'][1][1],0)
 def test_conditional_covariance_symmetric(self):self.assertEqual(R['conditional_covariance'][0][1],R['conditional_covariance'][1][0])
 def test_collinearity_in_box(self):self.assertLess(abs(R['projected_EOS_vs_tilt_correlation']),1)
 def test_collinearity_nontrivial(self):self.assertGreater(abs(R['projected_EOS_vs_tilt_correlation']),0.5)
 def test_full_covariance_not_diagonal(self):
  cd=[[a if i==j else 0.0 for j,a in enumerate(row)] for i,row in enumerate(C)]
  q=fit(z,obs,model,cd,v);self.assertGreater(abs(q['theta0']['Q2']-R['theta0']['Q2']),0.1)
 def test_decimal_independent_theta0(self):
  d=dfit(z,obs,model,C,v)
  for a,b in [(R['beta_theta0'],d['beta0']),(R['kappa_theta0'],d['kappa0']),
              (R['beta_dtheta'],d['betader']),(R['kappa_dtheta'],d['kappader']),
              (R['bounded_theta_star'],d['theta_star'])]:self.close(a,float(b))
 def test_decimal_independent_covariance(self):
  d=dfit(z,obs,model,C,v)
  for i in range(2):
   for j in range(2):self.close(R['conditional_covariance'][i][j],float(d['cov'][i][j]))
 def test_common_shift_beta_only(self):
  q=fit(z,[a+.125 for a in obs],model,C,v)
  self.close(q['beta_theta0'],R['beta_theta0']+.125)
  self.close(q['kappa_theta0'],R['kappa_theta0']);self.close(q['theta0']['Q2'],R['theta0']['Q2'])
 def test_joint_permutation(self):
  idx=[6,2,0,4,1,5,3];cc=[[C[i][j] for j in idx] for i in idx]
  q=fit([z[i] for i in idx],[obs[i] for i in idx],[model[i] for i in idx],cc,[v[i] for i in idx])
  self.close(q['kappa_theta0'],R['kappa_theta0']);self.close(q['bounded_theta_star'],R['bounded_theta_star']);self.close(q['best_profile']['Q2'],R['best_profile']['Q2'])
 def test_invalid_missing_data(self):
  with self.assertRaises(ValueError):fit(z[:-1],obs,model,C,v)
 def test_invalid_duplicate_redshift(self):
  zz=z.copy();zz[1]=zz[0]
  with self.assertRaises(ValueError):fit(zz,obs,model,C,v)
 def test_invalid_nonsymmetric_C(self):
  cc=copy.deepcopy(C);cc[0][1]*=2
  with self.assertRaises(ValueError):fit(z,obs,model,cc,v)
 def test_invalid_non_SPD(self):
  cc=[[0.0]*7 for i in range(7)]
  with self.assertRaises(ValueError):fit(z,obs,model,cc,v)
 def test_invalid_nonfinite(self):
  vv=v.copy();vv[2]=float('nan')
  with self.assertRaises(ValueError):fit(z,obs,model,C,vv)
 def test_zero_source_response_refusal(self):
  with self.assertRaises(ValueError):fit(z,obs,model,C,[0.0]*7)
if __name__=='__main__':unittest.main(verbosity=2)
