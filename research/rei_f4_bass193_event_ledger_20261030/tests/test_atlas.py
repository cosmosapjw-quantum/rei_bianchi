import csv, hashlib, importlib.util, json, math, sys, unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atlas',ROOT/'code'/'build_atlas.py')
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class TestNative193Atlas(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a,_=m.saved()
  cls.net=m.src.new_native_network()
  cls.ret,cls.epochs,cls.events,cls.p19=m.generate(write=False)
  cls.names=[str(x) for x in cls.a['diagnostic_names']]
  cls.d={s:cls.a['diagnostics'][:,k] for k,s in enumerate(cls.names)}
 def test_01_original_193_trajectory_byte_sha(self):
  self.assertEqual(m.sha(m.DONOR/'original/trajectory.npz'),m.SOURCE_SHA256)
 def test_02_original_VigilODE121_archive_byte_sha(self):
  self.assertEqual(m.sha(ROOT/'VIGILODE_BASS21_SAVED193_SOURCE_REPLAY_20261030_FULL.zip'),m.PR121_ZIP_SHA256)
 def test_03_history_cardinalities(self):
  self.assertEqual((len(self.epochs),len(self.events),len(self.p19)),(193,6755,104))
 def test_04_true_event_count(self):
  e=m.owner_events(self.net)
  self.assertEqual([sum(ev.kind==x for ev in e) for x in ('photo','rr','dr','weak')],[13,13,6,3])
 def test_05_no_new_IVP(self): self.assertEqual(self.ret['counts']['new_IVP'],0)
 def test_06_positive_event_rates(self): self.assertGreaterEqual(min(float(x['rate_per_baryon_s']) for x in self.events),0.)
 def test_07_eventwise_FJ_matches_native_source_13_snapshots(self):
  for idx in [0,1,10,25,48,67,96,119,128,144,160,181,192]:
   y=self.a['Y'][idx].copy(order='C')
   t=self.d['T_K'][idx]; uv=self.d['uv_scale'][idx];nb=self.d['nb_m3'][idx]
   r=self.net.rates(t,uv);v=self.net.evaluate(y,t,uv,nb)
   F,J,w,ne=m.evaluate_event_F_J(self.net,y,r,nb)
   self.assertLessEqual(np.max(abs(F-v['dY_dt']))/max(np.max(abs(v['dY_dt'])),1e-100),2e-12)
   self.assertLessEqual(np.max(abs(J-v['jac']))/max(np.max(abs(v['jac'])),1e-100),2e-12)
   self.assertEqual(ne,v['ne'])
 def test_08_max_validation_is_scoped(self):
  self.assertLessEqual(self.ret['validation']['native_event_F_scaled_max'],2e-12)
  self.assertLessEqual(self.ret['validation']['native_event_J_scaled_max'],2e-12)
 def test_09_baryon_invariant(self):
  for idx in (0,30,70,145,192):
   y=self.a['Y'][idx].copy(order='C');r=self.net.rates(self.d['T_K'][idx],self.d['uv_scale'][idx]);F,J,_,_=m.evaluate_event_F_J(self.net,y,r,self.d['nb_m3'][idx]);
   self.assertLess(abs(self.net.A@F),1e-27)
 def test_10_photo_source_charge_positive(self):
  self.assertGreater(sum(float(r['rate_per_baryon_s']) for r in self.events if r['channel']=='photo'),0)
 def test_11_all_event_charge_signs(self):
  for r in self.events:
   want= -1 if r['channel'] in ('rr','dr') else +1
   self.assertEqual(int(r['charge_delta']),want)
 def test_12_proper_time_H(self): self.assertTrue(all(float(r['H_s'])>0 for r in self.epochs))
 def test_13_source_stored_ne(self):
  self.assertTrue(all(math.isclose(float(row['ne_m3']),float(self.d['ne_m3'][i]),rel_tol=1e-14) for i,row in enumerate(self.epochs)))
 def test_14_weak_zero_only_due_original_trajectory(self):
  self.assertEqual(self.ret['path_exposure_simpson_per_baryon']['weak'],0)
 def test_15_lithium_source_equality_roundoff(self):
  self.assertLess(self.ret['validation']['max_Li_l1_rel_nu6'],1e-12)
 def test_16_no_negative_lithium_spectral_gap(self): self.assertGreaterEqual(self.ret['local_spectral_gap_min_s'],0)
 def test_17_spectral_gap_193_rows_not_time_global_proof(self):
  self.assertGreater(self.ret['local_spectral_gap_max_s'],self.ret['local_spectral_gap_min_s'])
 def test_18_photo_193_exposure_matches_original_replay_scope(self):
  original=json.loads((m.DONOR/'replay/results/SUMMARY.json').read_text())
  self.assertAlmostEqual(self.ret['path_exposure_simpson_per_baryon']['photo'],original['chemistry']['proper_photo_event_exposure_per_baryon'],delta=2e-13)
 def test_19_recomb_exposure(self):
  original=json.loads((m.DONOR/'replay/results/SUMMARY.json').read_text())
  self.assertAlmostEqual(self.ret['path_exposure_simpson_per_baryon']['rr'],original['chemistry']['proper_RR_event_exposure_per_baryon'],delta=2e-13)
 def test_20_dr_exposure(self):
  self.assertGreater(self.ret['path_exposure_simpson_per_baryon']['dr'],0)
  self.assertLess(self.ret['path_exposure_simpson_per_baryon']['dr'],1e-14)
 def test_21_original_source_energy_positive(self):
  self.assertTrue(all(float(r['absorbed_W_m3'])>=0 for r in self.epochs))
 def test_22_no_false_thermal_heat(self): self.assertNotIn('heating',self.ret['path_exposure_definition'])
 def test_23_p19_valid_epoch_only(self):
  self.assertTrue(all(2.4<=float(r['z'])<=4.75 for r in self.p19))
 def test_24_p19_no_li_source(self):
  self.assertTrue(all('P19' in r['tag'] for r in self.p19))
 def test_25_p19_two_variants_52_each(self):
  from collections import Counter
  self.assertEqual(sorted(Counter(r['tag'] for r in self.p19).values()),[52,52])
 def test_26_p19_electron_charge_reconciliation(self):
  for r in self.p19:
   self.assertLessEqual(abs(float(r['charge_identity_residual'])),1e-28)
 def test_27_p19_baryon_reconciliation(self):
  for r in self.p19:
   self.assertLessEqual(abs(float(r['baryon_identity_residual'])),1e-28)
 def test_28_p19_one_sample_nonzero_defect(self):
  self.assertGreater(max(abs(float(r['source_difference_electrons_per_baryon_s'])) for r in self.p19),0)
 def test_29_no_P19_as_REI_physical_history(self):
  self.assertIn('NOT a P19 history',self.ret['counterfactual_claim'])
 def test_30_frozen_DAG(self): self.assertEqual(self.ret['canonical_dag']['central'],'28/88')
 def test_31_reject_source_digest_negative(self):
  old=m.SOURCE_SHA256
  try:
   m.SOURCE_SHA256='0'*64
   with self.assertRaisesRegex(ValueError,'SAVED_TRAJECTORY_SHA_INVALID'):m.saved()
  finally:m.SOURCE_SHA256=old
 def test_32_mathematical_stoich_reconstruction(self):
  for e in m.owner_events(self.net):
   self.assertEqual(int(self.net.A[e.target]-self.net.A[e.source]),0)
 def test_33_derivative_general_Y_off_manifold(self):
  y=self.a['Y'][128].copy();y[13]+=5e-17; y[14]-=5e-17 # native Li6 source perturbation
  r=self.net.rates(self.d['T_K'][128],self.d['uv_scale'][128]);nb=self.d['nb_m3'][128]
  F,J,_,_=m.evaluate_event_F_J(self.net,y,r,nb)
  n=self.net.evaluate(y,self.d['T_K'][128],self.d['uv_scale'][128],nb)
  self.assertLess(np.max(abs(F-n['dY_dt'])),1e-27)
  self.assertLess(np.max(abs(J-n['jac']))/np.max(abs(n['jac'])),1e-12)
 def test_34_output_is_not_full_REI_bridge(self): self.assertEqual(self.ret['full_physical_F4'],'PARTIAL')
 def test_35_r6_c9_not_mislabeled(self):
  self.assertEqual((self.ret['independent_R6'],self.ret['independent_C9']),('NOT_RUN','NOT_RUN'))
 def test_36_no_source_extrapolation(self):
  with self.assertRaises(ValueError):m.src.p19_nominal_gamma(6.0)

if __name__=='__main__':unittest.main()
