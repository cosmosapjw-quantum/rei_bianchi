import csv, hashlib, importlib.util, json, math, unittest
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('wu_bridge',ROOT/'src/bridge.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
R=ROOT/'results'
def records(fn):
 with (R/fn).open(newline='') as f:return list(csv.DictReader(f))

class ActualSourceBridge(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cases=records('BRIDGE_CASES_3528.csv')
  cls.prod=records('BRIDGE_H2_PRODUCTS_35280.csv')
  cls.lines=records('BRIDGE_LINE_PHOTONS_14112.csv')
  cls.roots=records('BRIDGE_RADIATION_BALANCE_504.csv')
  cls.summary=json.loads((R/'SUMMARY.json').read_text())
 def test_original_archive_identities(self):
  self.assertEqual(bridge.sha(bridge.R32_ZIP),bridge.R32_SHA)
  self.assertEqual(bridge.sha(bridge.R33_ZIP),bridge.R33_SHA)
  bridge.lock_inputs()
 def test_full_grid_only_safe_common_t(self):
  self.assertEqual([len(x) for x in (self.cases,self.prod,self.lines,self.roots)],[3528,35280,14112,504])
  self.assertEqual({int(x['Tgas_K']) for x in self.cases},set(bridge.COMMON_T))
  self.assertNotIn(2005,{int(x['Tgas_K']) for x in self.cases})
  keys={(x['Tgas_K'],x['v1_quench_policy'],x['initial_v1_J'],x['v0_spin_policy'],x['n_over_ncrit_J2'],x['CMB_label']) for x in self.cases}
  self.assertEqual(len(keys),3528)
 def test_source_quench_partition(self):
  for x in self.cases:
   w=float(x['quench_enter_J0to4_probability'])
   self.assertTrue(0<w<1)
   self.assertLess(abs(w+float(x['quench_outside_J0to4_probability'])-1),1e-12)
   self.assertLess(abs(w-float(x['selected_reaction_H2_probability_per_initial_v1'])),6e-13)
 def test_first_rad_and_H2_independent_grouping(self):
  sums=defaultdict(lambda:[0.,0.,0.]);d={}
  for x in self.cases:
   key=tuple(x[k] for k in ('Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'))
   d[key]=x
   self.assertLess(abs(float(x['selected_first_radiation_before_reaction_probability'])+float(x['selected_reaction_before_radiation_probability'])-float(x['quench_enter_J0to4_probability'])),6e-13)
  for p in self.prod:
   key=tuple(p[k] for k in ('Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'))
   v=sums[key];v[0]+=float(p['probability_per_initial_v1']);v[1]+=float(p['before_first_radiation_joint']);v[2]+=float(p['at_least_one_radiation_joint'])
  self.assertEqual(len(sums),3528)
  for k,v in sums.items():
   self.assertLess(abs(v[0]-float(d[k]['quench_enter_J0to4_probability'])),6e-13)
   self.assertLess(abs(v[1]+v[2]-v[0]),6e-13)
 def test_two_stage_energy_seam_not_heat(self):
  found_nonzero=False
  for x in self.cases:
   self.assertLess(abs(float(x['conditional_energy_ledger_residual_J'])),3e-32)
   S=float(x['selected_energetic_representation_seam_J'])
   if abs(S)>1e-28:found_nonzero=True
   self.assertLess(abs(float(x['selected_initial_v1_internal_energy_weighted_J']) - sum(float(x[k]) for k in ['selected_quench_proton_bath_gain_R32_J','selected_energetic_representation_seam_J','selected_postquench_proton_bath_gain_R33_J','selected_net_radiation_J_per_initial_v1','selected_prechemistry_HD_rotational_energy_J'])),3e-32)
  self.assertTrue(found_nonzero)
 def test_line_resolved_energy(self):
  d=defaultdict(float)
  for x in self.lines:
   key=tuple(x[k] for k in ('Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'))
   d[key]+=float(x['net_radiation_J_per_initial_v1'])
  for x in self.cases:
   key=tuple(x[k] for k in ('Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'))
   self.assertLess(abs(d[key]-float(x['selected_net_radiation_J_per_initial_v1'])),1e-31)
 def test_root_bracketing_not_global_uniqueness(self):
  self.assertEqual(sum(x['endpoint_sign_change']=='True' for x in self.roots),324)
  for x in self.roots:
   if x['endpoint_sign_change']=='True':
    self.assertGreaterEqual(float(x['z_balance_on_0to300']),0)
    self.assertLessEqual(float(x['z_balance_on_0to300']),300)
    self.assertLess(abs(float(x['root_residual_J_per_initial_v1'])),2e-30)
   else:self.assertEqual(x['z_balance_on_0to300'],'')
 def test_direct_kinetic_matrix_vs_csv_weighted(self):
  a,group,cases,products,lines=bridge.load_inputs()
  r33=bridge.load_r33();parent,_,grid,_=r33.get_parent()
  for T in (55,105,3005):
   j1=0;v1='DB_UPWARD_V1';mode='Eq6-7_spin_effective';ratio=1.;label='z100'
   b=sorted(group[(T,v1,j1)],key=lambda x:int(x['terminal_v0_J']))
   w=[float(x['restricted_probability']) for x in b[:5]]
   direct=bridge.rad_on_mixture(parent,grid,T,mode,ratio,w,100.)
   csv_sum=sum(w[j]*float(cases[(T,mode,ratio,j,label)]['net_radiative_transfer_J']) for j in range(5))
   self.assertLess(abs(direct-csv_sum),1e-30)
 def test_no_fabricated_source_admission(self):
  self.assertEqual(self.summary['emaa_171x25_raw'],'NOT_ACQUIRED')
  self.assertEqual(self.summary['actual_EMAA_comparisons'],0)
  self.assertEqual(self.summary['canonical_DAG'],'34/49_UNCHANGED')
  self.assertEqual(self.summary['R6_distinct_author'],'NOT_RUN')
  self.assertEqual(self.summary['C9_distinct_author'],'NOT_RUN')
  self.assertFalse(self.summary['L4'])
 def test_specific_science_example(self):
  x=self.summary['sample_105K_v1J0_DB_v0spin_ratio1_z100']
  self.assertAlmostEqual(x['quench_enter_J0to4_probability'],0.3587827519512391,places=14)
  self.assertLess(x['selected_net_radiation_J_per_initial_v1'],0.)

if __name__=='__main__':unittest.main()