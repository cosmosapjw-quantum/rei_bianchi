import importlib.util, pathlib, unittest, numpy as np
from scipy.integrate import simpson,cumulative_simpson
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'code/primary_spin.py'
spec=importlib.util.spec_from_file_location('atomic_spin',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourcePhysics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lab,cls.meas,cls.epochs,cls.all,cls.summary=m.compute()
 def test_imm_source_sha(self):
  self.assertEqual(m.h(m.BASS),m.SHA['PR280']);self.assertEqual(m.h(m.CASUAL),m.SHA['PR287'])
 def test_original_scanned_and_langer_hash(self):
  for k,n in m.PDFS.items():self.assertEqual(m.h(m.ROOT/'source'/n),m.SHA[k])
 def test_negative_original_scanned_hash(self):
  before=m.SHA['drake_original']
  try:
   m.SHA['drake_original']='0'*64
   with self.assertRaises(AssertionError):m.verify_sources()
  finally:m.SHA['drake_original']=before
 def test_original_1969_21_points(self):
  self.assertEqual(len(m.DR1969),21)
  self.assertEqual(m.DR1969[0],0)
  self.assertEqual(m.DR1969[10],4540)
  self.assertEqual(m.DR1969[-1],5420)
  self.assertAlmostEqual(float(np.trapezoid(m.DR1969,m.DR_Y)),1945.475,9)
 def test_1987_lab_original_rows(self):
  self.assertEqual(len(self.lab),13)
  a=next(r for r in self.lab if r['energy_eV']==85)
  self.assertEqual((a['sigma_n2_Mb'],a['sigma_n3_Mb'],a['sigma_1s2s_3S_Mb'],a['sigma_unresolved_1S_plus_3P_Mb']),(1.58,.30,.99,.53))
 def test_1987_limit_n3_unreported(self):
  self.assertIsNone(self.lab[0]['sigma_n3_Mb']);self.assertIsNone(self.lab[1]['sigma_n3_Mb'])
  self.assertIsNone(m.interp_rows(75.35,self.lab)['sigma_n3_Mb'])
 def test_no_extrapolation(self):
  for v in (65.632,68.854,72.940,99.01,194.318):self.assertIsNone(m.interp_rows(v,self.lab))
 def test_channels_exclusive_positive(self):
  for r in self.lab:
   self.assertGreater(r['sigma_1s2p_1P_residual_Mb'],-1e-12)
   self.assertAlmostEqual(r['sigma_1s2s_3S_Mb']+r['sigma_unresolved_1S_plus_3P_Mb']+r['sigma_1s2p_1P_residual_Mb'],r['sigma_n2_Mb'],12)
 def test_triplet_is_not_zero(self):
  for r in self.lab:self.assertGreater(r['triplet_3S_fraction_within_n2'],0.5)
 def test_unknown_singlet_untouched(self):
  for r in self.lab:
   self.assertLess(r['singlet_1S_fraction_max_within_n2'],1-r['triplet_3S_fraction_within_n2']+1e-13)
   self.assertIn('unresolved',r['warning'])
 def test_total_subspace_requires_80eV(self):
  self.assertIsNone(m.interp_rows(77.559188961682,self.lab)['f3S_n2n3'])
  self.assertGreater(m.interp_rows(81.852338482804,self.lab)['f3S_n2n3'],0.4)
 def test_epoch_193_bin_8492_and_window_2316(self):
  self.assertEqual(len(self.epochs),193);self.assertEqual(len(self.meas),2316);self.assertEqual(len(self.all),8492)
 def test_six_bin_each_epoch_two_isotopes(self):
  for i in (0,1,53,130,192):
   rows=[r for r in self.meas if r['epoch']==i]
   self.assertEqual((len(rows),len({r['photon_eV'] for r in rows}),len({r['isotope'] for r in rows})),(12,6,2))
 def test_all_source_energy_owner_identities(self):
  a=self.summary['integrated_conditional'];self.assertAlmostEqual(a['K_all']/3.442655615303716e-11,1,11)
  self.assertLess(a['K_75_99'],a['K_all']);self.assertLess(a['K_80_99'],a['K_75_99'])
 def test_source_subspace_nonnegative(self):
  a=self.summary['integrated_conditional'];self.assertGreater(a['triplet3S_n2n3'],0)
  self.assertLess(a['triplet3S_n2n3']+a['singlet1S_upper_n2n3'],a['K_80_99'])
 def test_m1_radiative_competing_branch(self):
  self.assertGreater(m.BR_M1,0.9999)
  self.assertLess(m.BR_M1,1)
 def test_energy_binding_discrepancy_not_erased(self):
  f=self.summary['Ferrett1987'];self.assertGreater(f['NIST_BASS_source_eV']-f['mainline_1S_bind_1987_eV'],.16)
  self.assertLess(abs(f['NIST_BASS_source_eV']-f['mainline_1S_bind_1991_eV']),.01)
 def test_provenance_full_but_no_actual_electron_source(self):
  a=self.summary['admission'];self.assertEqual(a['real_singlet_production'],'UNRESOLVED_1S_PLUS_3P')
  self.assertEqual(a['K_scaled_partial_emission'],'CONDITIONAL_ON_K_SUBSPACE_OWNER_UNVERIFIED')
 def test_no_ivp_or_dag_promotion(self):
  d=self.summary['DAG'];self.assertEqual((d['working'],d['central'],d['physical_fast'],d['canonical_delta'],d['new_IVPs']),('33/88','28/88','4/7',0,0))
  self.assertNotIn('solve_ivp(',p.read_text())
 def test_integrated_source_nonnegative_each_epoch(self):
  for e in self.epochs:
   self.assertGreaterEqual(e['K_all_per_baryon_s'],0)
   self.assertLessEqual(e['K_75_99_per_baryon_s'],e['K_all_per_baryon_s']*1.00000000000001)
 def test_quadrature_reproduction(self):
  x=np.array([r['x'] for r in self.epochs]);H=np.array([r['H_s'] for r in self.epochs]);K=np.array([r['K_75_99_per_baryon_s'] for r in self.epochs]);
  a=simpson(K/H,x=x);b=cumulative_simpson(K/H,x=x,initial=0)[-1]
  self.assertLess(abs(a-b),max(1e-26,1e-12*abs(a)))
if __name__=='__main__':unittest.main()
