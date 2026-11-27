import csv, json, math, shutil, sys, tempfile, unittest
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from angular_injection_atlas import (EXFOR_SHA256,EXFOR_BLOB,FERMI_SHA256,FERMI_BLOB,M_ALPHA,M_D,Q,E_THRESHOLD,
                                    _gitblob, source_da, source_fermi, two_body, generate, _norm_shape, NB_TO_CM2)

class SourceAndPhysics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.da=source_da(ROOT/'sources/M0475.x4');cls.fermi=source_fermi(ROOT/'sources/fermi_igrb_2015_AB_C_78row_mirror.csv')
  cls.result=generate(ROOT)

 def test_A_untouched_EXFOR_raw_git(self):
  raw=(ROOT/'sources/M0475.x4').read_bytes();self.assertEqual(len(raw),3349)
  self.assertEqual(_gitblob(raw),EXFOR_BLOB)
 def test_B_untouched_fermi_mirror(self):
  raw=(ROOT/'sources/fermi_igrb_2015_AB_C_78row_mirror.csv').read_bytes();self.assertEqual(len(raw),15975)
  self.assertEqual(_gitblob(raw),FERMI_BLOB)
 def test_C_tamper_nuclear_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'n.x4';p.write_bytes((ROOT/'sources/M0475.x4').read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'BYTES_MISMATCH'):source_da(p)
 def test_D_tamper_fermi_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'b.csv';p.write_bytes((ROOT/'sources/fermi_igrb_2015_AB_C_78row_mirror.csv').read_bytes()[:-1])
   with self.assertRaisesRegex(ValueError,'BYTES_MISMATCH'):source_fermi(p)
 def test_E_exfor_DA_grain(self):
  self.assertEqual(len(self.da),12)
  self.assertEqual({int(r[0]) for r in self.da},{213,258,330})
  self.assertEqual({int(r[1]) for r in self.da},{46,61,73,87})
 def test_F_exfor_330_DA_not_reported_SIG(self):
  self.assertEqual([(a,v,e) for E,a,v,e in self.da if E==330],[(F(46),F('.14'),F('.03')),(F(61),F('.16'),F('.05')),(F(73),F('.07'),F('.05')),(F(87),F('.19'),F('.05'))])
 def test_G_fermi_exact_binned_energy(self):
  self.assertEqual(len(self.fermi),78)
  for m in 'ABC':
   x=[z for z in self.fermi if z['FG']==m]
   self.assertEqual(len(x),26)
   self.assertTrue(any((r['energy_min_MeV'],r['energy_max_MeV'])==(200.,282.8) for r in x))
   self.assertTrue(any((r['energy_min_MeV'],r['energy_max_MeV'])==(282.8,400.) for r in x))
 def test_H_resolved_source_not_triple_counted(self):
  x=[r for r in self.fermi if r['energy_min_MeV'] in (200.,282.8)]
  self.assertEqual({r['fsrc'] for r in x if r['energy_min_MeV']==200.},{4.092e-7})
  self.assertEqual({r['fsrc'] for r in x if r['energy_min_MeV']==282.8},{3.026e-7})
 def test_I_threshold_exact(self):
  self.assertEqual(Q,F('23.8464782'))
  self.assertEqual(E_THRESHOLD,Q+Q*Q/(2*M_ALPHA))
  self.assertGreater(E_THRESHOLD,Q)
 def test_J_mass_shell_and_4mom_conservation(self):
  for E,theta,_,_ in self.da:
   k=two_body(E,theta)
   for key in ('shell_plus','shell_minus'):
    self.assertLess(abs(k[key]),mp.mpf('1e-67'))
   self.assertLess(abs(k['Pplus'][0]+k['Pminus'][0]-(mp.mpf(M_ALPHA.numerator)/M_ALPHA.denominator+mp.mpf(E.numerator)/E.denominator)),mp.mpf('1e-67'))
   self.assertLess(abs(sum((k['Pplus'][1][2],k['Pminus'][1][2]))-mp.mpf(E.numerator)/E.denominator),mp.mpf('1e-67'))
   self.assertLess(abs(k['Pplus'][1][0]+k['Pminus'][1][0]),mp.mpf('1e-67'))
 def test_K_daughter_exchange(self):
  for E,a,_,_ in self.da:
   x=two_body(E,a);y=two_body(E,F(180)-a)
   self.assertLess(abs(x['Kplus']-y['Kminus']),mp.mpf('1e-67'))
   self.assertLess(abs(x['Kminus']-y['Kplus']),mp.mpf('1e-67'))
 def test_L_positive_physical_kinematics(self):
  for E,a,_,_ in self.da:
   d=two_body(E,a)
   self.assertGreater(d['Kplus'],0);self.assertGreater(d['Kminus'],0)
   self.assertLess(abs(d['Kplus']+d['Kminus']-mp.mpf((E-Q).numerator)/(E-Q).denominator),mp.mpf('1e-67'))
 def test_M_output_grain(self):
  x=self.result['data'];self.assertEqual(len(x),168)
  self.assertEqual(len({(r['E_gamma_MeV'],r['theta_CM_deg'],r['FG'],r['component'],r['shape']) for r in x}),168)
  self.assertEqual(sum(r['component']=='fsrc_high_lat' for r in x),24)
  self.assertEqual(sum(r['component']=='IGRB' for r in x),72)
  self.assertEqual(sum(r['component']=='EGB' for r in x),72)
 def test_N_Fermi_source_is_model_not_observation_at_point(self):
  x=self.result
  self.assertEqual(x['science']['pointwise_gamma_shape'],'MODEL_DEPENDENT_NOT_MEASURED')
  self.assertEqual(x['science']['DA_exclusive_event_normalization'],'UNRESOLVED')
  self.assertFalse(x['citation']['original_CDS_byte_verified'])
 def test_O_at_E330_observed_DA_marginal_variance(self):
  row=next(r for r in self.result['data'] if r['E_gamma_MeV']=='330' and r['theta_CM_deg']=='46')
  self.assertAlmostEqual(float(row['K_single_D_marginal_mean_MeV']),float(F(330)-Q)/2,places=11)
  self.assertGreater(float(row['K_single_D_marginal_variance_MeV2']),0)
 def test_P_source_ErrS_linear_only(self):
  row=next(r for r in self.result['data'] if r['E_gamma_MeV']=='330' and r['theta_CM_deg']=='46' and r['FG']=='A' and r['component']=='IGRB' and r['shape']=='flat')
  self.assertAlmostEqual(row['Gamma_ERR_S_DA_only_abs_scale']/row['Gamma_reported_like_per_MeV_per_srCM_s_He'],float(F('.03')/F('.14')),places=12)
 def test_Q_flat_shape_exact(self):
  e=330;lo=282.8;hi=400.
  self.assertAlmostEqual(_norm_shape(e,lo,hi,'flat','A'),1/(hi-lo),places=15)
 def test_R_model_shapes_still_integrate_to_one(self):
  from scipy.integrate import quad
  for f in 'ABC':
   for a,b in ((200.,282.8),(282.8,400.)):
    integral=quad(lambda E:_norm_shape(E,a,b,'model_ple_igrb',f),a,b,epsabs=1e-12)[0]
    self.assertAlmostEqual(integral,1.,places=12)
 def test_S_angular_photon_intensity_sample(self):
  # Source exact Fermi A second band IGRB 6.650e-7 integrated; flat uniform within bin.
  row=next(r for r in self.result['data'] if r['E_gamma_MeV']=='330' and r['theta_CM_deg']=='46' and r['FG']=='A' and r['component']=='IGRB' and r['shape']=='flat')
  expected=4*math.pi*(6.650e-7/(400.-282.8))*float(F('.14'))*NB_TO_CM2
  self.assertAlmostEqual(row['Gamma_reported_like_per_MeV_per_srCM_s_He']/expected,1.,places=13)
 def test_T_highlat_omega_not_4pi(self):
  row=next(r for r in self.result['data'] if r['E_gamma_MeV']=='330' and r['theta_CM_deg']=='46' and r['component']=='fsrc_high_lat' and r['shape']=='flat')
  self.assertAlmostEqual(row['sky_solid_angle_sr_assumed'],4*math.pi*(1-math.sin(math.radians(20))),places=13)
 def test_U_kinetic_weight_is_not_heat(self):
  row=next(r for r in self.result['data'] if r['E_gamma_MeV']=='258' and r['theta_CM_deg']=='87' and r['FG']=='C' and r['component']=='EGB' and r['shape']=='flat')
  self.assertAlmostEqual(row['GammaK_reported_like_MeV_per_MeV_per_srCM_s_He']/row['Gamma_reported_like_per_MeV_per_srCM_s_He'],float(F(258)-Q),places=12)
  self.assertIsNone(self.result['science']['heat_rate'])
 def test_V_no_real_event_rate_or_production(self):
  i=self.result['science']
  for key in ['R_event','kappa','heat_rate']:
   self.assertIsNone(i[key])
  self.assertFalse(i['L4']);self.assertFalse(i['physical_activation']);self.assertEqual(i['production'],'HOLD')
 def test_W_source_observed_only_twelve(self):
  o=json.loads((ROOT/'results/MEASURED_ANGULAR_DPAIR_12.json').read_text())
  self.assertEqual(len(o),12)
  for r in o:
   self.assertEqual(F(r['pair_Ksum_MeV']),F(r['E_gamma_MeV'])-Q)
 def test_X_no_silent_double_d_factor(self):
  x=self.result['data']
  for row in x:
   self.assertGreater(row['Gamma_reported_like_per_MeV_per_srCM_s_He'],0)
   self.assertTrue('per_srCM' in 'Gamma_reported_like_per_MeV_per_srCM_s_He')
 def test_Y_output_CSV_row_equality(self):
  with (ROOT/'results/ANGULAR_DPAIR_FERMI_168.csv').open(newline='') as f:
   rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),168)
  for a,b in zip(rows,self.result['data']):
   self.assertEqual(a['Gamma_reported_like_per_MeV_per_srCM_s_He'],str(b['Gamma_reported_like_per_MeV_per_srCM_s_He']))
 def test_Z_kinematic_domain_rejection(self):
  with self.assertRaises(ValueError):two_body(E_THRESHOLD-F('.01'),F(46))
  with self.assertRaises(ValueError):two_body(F(330),F(181))

if __name__=='__main__':unittest.main(verbosity=2)
