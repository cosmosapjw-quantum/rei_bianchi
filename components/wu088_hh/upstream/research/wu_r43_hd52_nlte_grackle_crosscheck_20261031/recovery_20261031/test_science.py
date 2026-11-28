"""Source and physics acceptance for the R43 EMAA/Grackle reconstructed archive.
Same-author mathematical/implementation checks; not a distinct-author R6 or C9.
"""
import csv,json,math,unittest
from pathlib import Path
import numpy as np
from mpmath import mp
from scipy.constants import h,c,k as KB
from generate import ROOT,sha,load_data,GRID_H,GRID_HP,GRID_Z,GRID_Z_JOINT,coll_matrix,radio_matrix,equilibrium,grackle_low,grackle_lte,RAW_HASH,PARSER_HASH

def read_csv(name):
 with (ROOT/'results'/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
class R43RecoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=load_data(); cls.cases=read_csv('R43_CASES_324.csv');cls.lte=read_csv('R43_GRACKLE_REFERENCE_15.csv')
  cls.s=json.loads((ROOT/'results/SUMMARY.json').read_text())
 def test_01_source_sha(self):
  self.assertEqual(sha(ROOT/'source_private/HD.Rovibration.805a7aa5.radex'),RAW_HASH)
  self.assertEqual(sha(ROOT/'source_private/emaa_primary.py'),PARSER_HASH)
 def test_02_source_52_levels(self):self.assertEqual(len(self.d['levels']),52)
 def test_03_source_368_lines(self):self.assertEqual(len(self.d['radiative']),368)
 def test_04_H1326_pairs(self):self.assertEqual(len(self.d['partners'][5]['rates']),1326)
 def test_05_Hp171_pairs(self):self.assertEqual(len(self.d['partners'][7]['rates']),171)
 def test_06_H_only_original_T_nodes(self):self.assertEqual(len(self.d['partners'][5]['temps']),15)
 def test_07_proton_only_original_T_nodes(self):self.assertEqual(len(self.d['partners'][7]['temps']),25)
 def test_08_exact_common_T(self):self.assertEqual(sorted(set(self.d['partners'][5]['temps'])&set(self.d['partners'][7]['temps'])),[5.])
 def test_09_324_physical_cases(self):self.assertEqual(len(self.cases),324)
 def test_10_16848_level_population_rows(self):self.assertEqual(len(read_csv('R43_POPULATIONS_16848.csv')),16848)
 def test_11_119232_source_photon_rows(self):self.assertEqual(len(read_csv('R43_SIGNED_PHOTONS_119232.csv')),119232)
 def test_12_15_Grackle_comparator_rows(self):self.assertEqual(len(self.lte),15)
 def test_13_no_unjustified_high_level_proton_collisions(self):
  K=coll_matrix(self.d,7,5.,1e3)
  self.assertEqual(float(np.max(abs(K[19:,:]))),0.)
  self.assertEqual(float(np.max(abs(K[:,19:]))),0.)
 def test_14_generator_column_mass(self):
  for K in [coll_matrix(self.d,5,70.,1e4),coll_matrix(self.d,7,5.,1e3),radio_matrix(self.d,84.4905)[0]]:
   self.assertLess(np.max(abs(K.sum(axis=0))),1e-12)
 def test_15_original_rate_detailed_balance(self):
  for T in (70.,100.,3000.):
   K=coll_matrix(self.d,5,T,1.)
   for up,lo in ((2,1),(52,34),(19,11),(40,15)):
    g=self.d['levels']; expected=g[up]['g']/g[lo]['g']*math.exp(-(g[up]['E']-g[lo]['E'])*__import__('generate').owner.HCK/T)
    down=K[lo-1,up-1]
    if down>0:self.assertLess(abs(K[up-1,lo-1]-down*expected)/down,2e-12)
 def test_16_all_probability_cases_normalized(self):
  rows=read_csv('R43_POPULATIONS_16848.csv');s={}
  for r in rows:
   key=(r['T_gas_K'],r['n_H_cm_minus3'],r['n_Hplus_cm_minus3'],r['z_boundary'])
   v=float(r['p_HD_level']);self.assertGreaterEqual(v,0);s[key]=s.get(key,0.)+v
  self.assertEqual(len(s),324);self.assertLess(max(abs(x-1) for x in s.values()),2e-13)
 def test_17_energy_balance(self):
  for x in self.cases:
   L=float(x['net_photon_J_s_per_HD']);C=float(x['collisional_H_heating_of_HD_J_s'])+float(x['collisional_Hplus_heating_of_HD_J_s']);
   self.assertLess(abs(L-C)/max(abs(L),abs(C),1e-60),5e-7)
 def test_18_photon_flux_integral(self):
  rows=read_csv('R43_SIGNED_PHOTONS_119232.csv');integ={}
  for r in rows:
   k=(r['T_gas_K'],r['n_H_cm_minus3'],r['n_Hplus_cm_minus3'],r['z_boundary']);integ[k]=integ.get(k,0.)+float(r['net_radiative_energy_J_s_per_HD'])
  self.assertEqual(len(integ),324)
  for x in self.cases:
   k=(x['T_gas_K'],x['n_H_cm_minus3'],x['n_Hplus_cm_minus3'],x['z_boundary']);L=float(x['net_photon_J_s_per_HD'])
   self.assertLess(abs(integ[k]-L)/max(abs(L),1e-40),2e-11)
 def test_19_70K_OFF_cools(self):
  r=next(x for x in self.cases if float(x['T_gas_K'])==70 and float(x['n_H_cm_minus3'])==1e4 and x['z_boundary']=='OFF' and float(x['n_Hplus_cm_minus3'])==0)
  self.assertAlmostEqual(float(r['net_photon_J_s_per_HD']),2.8901144843322e-29,delta=5e-40)
 def test_20_70K_z30_heats(self):
  r=next(x for x in self.cases if float(x['T_gas_K'])==70 and float(x['n_H_cm_minus3'])==1e4 and x['z_boundary']=='30' and float(x['n_Hplus_cm_minus3'])==0)
  self.assertAlmostEqual(float(r['net_photon_J_s_per_HD']),-1.4935503559987723e-29,delta=5e-39)
 def test_21_100K_z30_cools(self):
  r=next(x for x in self.cases if float(x['T_gas_K'])==100 and float(x['n_H_cm_minus3'])==1e4 and x['z_boundary']=='30' and float(x['n_Hplus_cm_minus3'])==0)
  self.assertAlmostEqual(float(r['net_photon_J_s_per_HD']),1.93081506923182e-29,delta=1e-38)
 def test_22_EMAA_Grackle70_ratio(self):
  x=next(r for r in self.lte if float(r['T_gas_K'])==70)
  self.assertAlmostEqual(float(x['ratio_EMAA_over_Grackle_HDlow']),1.0073969277995367,places=11)
 def test_23_EMAA_Grackle100_ratio(self):
  x=next(r for r in self.lte if float(r['T_gas_K'])==100)
  self.assertAlmostEqual(float(x['ratio_EMAA_over_Grackle_HDlow']),0.9367276170439331,places=11)
 def test_24_no_joint_collider_off_5K(self):
  self.assertTrue(all(float(r['T_gas_K'])==5 for r in self.cases if float(r['n_Hplus_cm_minus3'])>0))
 def test_25_exact_Tg_Trad_zero(self):
  # Fixed radiation equal to collision bath; source detailed balance enforces zero flux.
  x,p,_=equilibrium(self.d,100.,1e4,0.,100.)
  self.assertLess(abs(float(x['net_photon_J_s_per_HD'])),1e-36)
 def test_26_mpmath80_52level_stationary(self):
  # Independent 80-digit algebra using same source-locked matrix entries.
  mp.dps=80;T=70.;n=1e4;Trad=2.7255*(1+30)
  K=coll_matrix(self.d,5,T,n)+radio_matrix(self.d,Trad)[0];scale=np.max(abs(K))
  A=mp.matrix([[mp.mpf(str(K[i,j]/scale)) for j in range(52)] for i in range(52)])
  for j in range(52):A[0,j]=mp.mpf('1')
  rhs=mp.matrix([int(i==0) for i in range(52)])
  sol=mp.lu_solve(A,rhs);pp=np.asarray([float(sol[i]) for i in range(52)]);pp=np.maximum(pp,0);pp/=pp.sum()
  d,p,_=equilibrium(self.d,T,n,0.,'30');self.assertLess(np.max(abs(pp-p)),3e-12)
 def test_27_scope_and_dag(self):
  self.assertEqual(self.s['canonical_DAG'],'34/49_UNCHANGED');self.assertEqual(self.s['production'],'HOLD')
  self.assertEqual(self.s['R6_distinct_author'],'NOT_RUN');self.assertEqual(self.s['C9_distinct_author'],'NOT_RUN')
if __name__=='__main__':unittest.main(verbosity=2)
