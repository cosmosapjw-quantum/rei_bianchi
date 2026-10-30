import csv,importlib.util,json,pathlib,sys,tempfile,unittest,zipfile
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import build_physics as ph

class SourceThermalTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows,cls.events,cls.matrices,cls.info=ph.calculate()
  cls.z=np.array([r['z'] for r in cls.rows]);cls.H=np.array([r['H_s'] for r in cls.rows]);cls.j=cls.matrices['J5'];cls.F=cls.matrices['F5']
 def test_01_input_source_is_exact(self):
  self.assertEqual(ph.sha(ph.SRC.read_bytes()),ph.SHA_293)
 def test_02_193_579_physical_rows(self):
  self.assertEqual((len(self.rows),len(self.events)),(193,579))
 def test_03_rei_f_j_shapes(self):
  self.assertEqual(self.F.shape,(193,5));self.assertEqual(self.j.shape,(193,5,5));self.assertEqual(self.matrices['J5x21_common'].shape,(193,5,21))
 def test_04_rates_positive(self):
  for e in self.events:
   for k in ['source_BASS_native_photo_gamma_s','REI_Grackle_CI_cm3_s','REI_Grackle_RR_cm3_s','REI_point_photoevents_per_Href_s','REI_point_rr_events_per_Href_s']:
    self.assertGreaterEqual(e[k],0,k)
 def test_05_fraction_domain(self):
  for row in self.rows:
   self.assertGreaterEqual(row['HII_fraction'],0)
   self.assertLessEqual(row['HII_fraction'],1)
   self.assertGreaterEqual(row['HeII_fraction'],0)
   self.assertLessEqual(row['HeII_fraction']+row['HeIII_fraction'],1.00000000000001)
 def test_06_nhref_conversion(self):
  r=np.array([x['nHref_over_nb'] for x in self.rows]);self.assertTrue(np.allclose(r,.7549543987593133,rtol=4e-15))
 def test_07_ne_all_ge_reduced(self):
  self.assertTrue(all(r['ne_all_BASS_cm3']>=r['ne_HHe_cm3']-2e-14 for r in self.rows))
 def test_08_frozen_source_grackle_F_original_parity(self):
  self.assertLess(self.info['max_REI_Rust_source_translated_F_vs_PR276_residual_per_baryon_s'],3e-24)
 def test_09_frozen_source_grackle_J_original_parity(self):
  self.assertLess(self.info['max_REI_Rust_source_translated_J_vs_PR276_residual_s'],2e-22)
 def test_10_BASS_photo_owner_exact(self):
  self.assertLess(self.info['max_BASS_photo_event_reconstruction_abs_baryon_s'],2e-24)
 def test_11_charge_event_continuity(self):
  q=np.array([0,1,0,1,2.]);b=np.array([r['nb_m3']/1e6 for r in self.rows]);dne=np.array([r['REI_HHe_dNe_cm3_s'] for r in self.rows]);
  self.assertLess(np.max(abs(self.F@q*b-dne)),2e-30)
 def test_12_rei_hhe_F_stoich(self):
  self.assertLess(np.max(abs(self.F.sum(axis=1))),2e-21)
  self.assertLess(np.max(abs(self.F@np.array([1,1,0,0,0]))),2e-21)
  self.assertLess(np.max(abs(self.F@np.array([0,0,1,1,1]))),2e-21)
 def test_13_J_conservation(self):
  self.assertLess(np.max(abs(self.j.sum(axis=1))),2e-20)
 def test_14_energy_ledger_exact(self):
  self.assertLess(self.info['max_rust_thermal_energy_identity_abs_erg_cm3_s'],3e-38)
 def test_15_thermal_temperature_decomposition(self):
  for r in self.rows:
   expected=r['REI_HHe_Tdot_thermal_K_s']+r['REI_HHe_Tdot_expansion_K_s']+r['REI_HHe_Tdot_electron_loading_K_s']
   self.assertAlmostEqual(expected,r['REI_HHe_Tdot_point_K_s'],delta=3e-25)
 def test_16_k_trace_sign_convention(self):
  for r in self.rows:
   self.assertAlmostEqual(2*r['K_perp_proxy_s']+r['K_parallel_proxy_s'],-3*r['H_s'],delta=5e-29)
   self.assertAlmostEqual(r['K_perp_proxy_s']+r['H_s'],r['b_dot_proxy_s'],delta=5e-29)
   self.assertAlmostEqual(r['K_parallel_proxy_s']+r['H_s'],-2*r['b_dot_proxy_s'],delta=5e-29)
 def test_17_eos_capacity(self):
  for r in self.rows:
   expected=1.5*ph.KB_ERG*(r['nHref_cm3']+r['nHe4_cm3']+r['ne_HHe_cm3'])/r['nHref_cm3']
   self.assertAlmostEqual(expected,r['REI_HHe_Cv_erg_per_Href_per_K'],delta=1e-30)
 def test_18_cmb_sign(self):
  for r in self.rows:
   cmb=r['REI_HHe_cmb_exchange_erg_per_Href_s']; dt=r['T_CMB_external_K']-r['T_BASS_saved_K'];self.assertGreaterEqual(cmb*dt,0)
 def test_19_cmb_zero_at_equal_temperature(self):
  arr=np.ones(3);coeff=np.array([1e-15,1e-20,1e-20,1e-12,1e-12,1e-12,0.]);T=ph.T_CMB0*3
  v=ph.point_thermal(T,2.,1e-18,1.,.2,.1,np.array([.9,.18,.1]),np.array([.1,.02,.1]),arr,np.zeros(3),coeff)
  self.assertEqual(v['cmb'],0.)
 def test_20_no_double_count_contract(self):
  self.assertTrue(all(r['source_status']=='BASS_NATIVE_PHOTO_REPLACEMENT_NOT_ADDITIVE' for r in self.rows))
 def test_21_K_not_owner(self):
  self.assertTrue(all(r['K_status']=='AXBI_CONVENTION_GRADIENT_PROXY_NOT_OWNER_CERTIFIED' for r in self.rows))
 def test_22_raw_data_numerical_finite(self):
  for r in self.rows:
   for k,v in r.items():
    if type(v)==float:self.assertTrue(np.isfinite(v),k)
 def test_23_rei_FJ_difference_is_real(self):
  v=np.array([r['REI_HHe_common_electron_pool_F_difference_max_per_baryon_s'] for r in self.rows]);self.assertGreater(v.max(),0)
 def test_24_grackle_low_T_floor_preserved(self):
  v=[r['Grackle_low_T_CI_floor_active'] for r in self.rows];self.assertTrue(any(v));self.assertTrue(not all(v))
 def test_25_k_metric_sign_counterexample(self):
  # Previous wrong sign Kperp=-H-bdot must fail the actual REI source convention at nonzero bdot.
  r=self.rows[90];wrong=-r['H_s']-r['b_dot_proxy_s'];self.assertGreater(abs(wrong-r['K_perp_proxy_s']),1e-23)
 def test_26_source_identity_reject_corruption(self):
  with tempfile.TemporaryDirectory() as d:
   orig=ph.SRC;bad=pathlib.Path(d)/'corrupt.zip';bad.write_bytes(ph.SRC.read_bytes()+b'bad')
   try:
    ph.SRC=bad
    with self.assertRaisesRegex(ValueError,'PARENT_SHA'):ph.load()
   finally:ph.SRC=orig
 def test_27_jacobian_directional_finite_difference(self):
  net,s,rei,g,m,old,pr=ph.load()
  y=s['Y'];z=s['z'];d={str(n):s['diagnostics'][:,i] for i,n in enumerate(s['diagnostic_names'])}
  U=np.array([1,2,10,11,12]);q5=np.array([0.,1.,0.,1.,2.])
  for k in [0,48,100,170,192]:
   x=y[k,U];nb=float(d['nb_m3'][k]);coeff=g(float(d['T_K'][k]))[0]
   M=m(coeff*1e-6);G=net._Gphoto[np.ix_(U,U)]*d['uv_scale'][k]
   def f(v):return G@v+nb*(q5@v)*(M@v)
   h=1e-7;v=np.array([.2,-.1,.05,-.03,.02]);jv=(f(x+h*v)-f(x-h*v))/(2*h)
   expected=self.j[k]@v
   self.assertLess(np.linalg.norm(jv-expected)/(max(np.linalg.norm(expected),1e-70)),2e-7)
 def test_28_jacobian_cross_other_charge(self):
  net,s,rei,g,m,old,pr=ph.load()
  U=np.array([1,2,10,11,12]);q=np.asarray(net.q,float);remain=np.array([i for i in range(21) if i not in U]);
  for k in [0,90,192]:
   J=self.matrices['J5x21_common'][k][:,remain]
   # All off-H/He derivative columns arise from one shared electron pool vector q_other.
   for a in range(len(remain)):
    for b in range(a+1,len(remain)):
     self.assertLess(np.max(abs(J[:,a]*q[remain[b]]-J[:,b]*q[remain[a]])),1e-23)
 def test_29_rei_source_is_not_native(self):
  self.assertTrue(self.info['not_native_rei_rust_execution']);self.assertTrue(self.info['not_native_REI17_full_FJ'])
 def test_30_canonical_no_promotion(self):
  self.assertEqual(self.info['DAG']['central'],'28/88');self.assertEqual(self.info['DAG']['physical_fast'],'4/7')
  self.assertEqual(self.info['DAG']['canonical_delta'],0)
 def test_31_cross_owner_threshold_energy_defect_exact(self):
  for r in self.rows:
   d=r['REI_HHe_photo_input_erg_per_Href_s']-r['BASS_native_HHe_absorbed_input_erg_per_Href_s']
   p=r['REI_BASS_ionization_threshold_source_defect_erg_per_Href_s']
   self.assertAlmostEqual(d,p,delta=3e-37)
 def test_32_nonzero_source_threshold_mismatch(self):
  a=np.array([r['REI_BASS_ionization_threshold_source_defect_erg_per_Href_s'] for r in self.rows]);self.assertGreater(np.max(abs(a)),1e-31)
 def test_33_source_energy_owner_explicit_hold(self):
  self.assertTrue(all(r['energy_owner_status']=='BASS_ROUNDED_CHI_VS_REI_FINE_CHI_EXPLICIT_DEFECT' for r in self.rows))
 def test_34_source_K_proxy_direction(self):
  r=self.rows[90]
  self.assertAlmostEqual((r['K_parallel_proxy_s']-r['K_perp_proxy_s'])/(3*r['H_s']),-r['b_dot_proxy_s']/r['H_s'],delta=1e-15)
 def test_35_thermal_erg_per_h_reference_to_ev_units(self):
  r=self.rows[100];v=r['REI_HHe_primary_heat_erg_per_Href_s'];self.assertGreater(v,0)
  self.assertGreater(v/ph.EV_ERG,0)
if __name__=='__main__':unittest.main(verbosity=2)
