import unittest, math, csv
from pathlib import Path
import numpy as np
from scipy.constants import h,c,k as k_B
from src.emaa_primary import (parse_radex,raw_crosswalk,bath_rates,radiative_generator,
 stationary,energy_flux,first_v1_quench,compute_atlas,RAW,GL,filehash,HCK,HCJ,EXPECTED_RAW_SHA)

class EmaaPrimaryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=parse_radex()

 def test_source_immutability_and_sections(self):
  self.assertEqual(filehash(RAW),EXPECTED_RAW_SHA)
  self.assertEqual(len(self.d['levels']),52)
  self.assertEqual(len(self.d['radiative']),368)
  self.assertEqual(set(self.d['partners']),{5,7})
  self.assertEqual(len(self.d['partners'][5]['rates']),1326)
  self.assertEqual(len(self.d['partners'][7]['rates']),171)
  self.assertEqual(len(self.d['partners'][7]['temps']),25)

 def test_complete_19_state_collisional_combinatorics(self):
  keys=set(self.d['partners'][7]['rates'])
  self.assertEqual(keys,{(i,j) for i in range(2,20) for j in range(1,i)})
  self.assertEqual(sum(len(x) for x in self.d['partners'][7]['rates'].values()),4275)

 def test_source_witnesses_and_unit(self):
  x=self.d['partners'][7];t=x['temps'].index(105.0)
  self.assertAlmostEqual(x['rates'][(2,1)][t],6.01e-10,places=19)
  self.assertAlmostEqual(HCK,1.4387768775039336,places=14)
  self.assertEqual(len([z for z in self.d['radiative'] if z['up']<=19]),63)

 def test_radiative_frequency_energy_crosscheck(self):
  checks=[]
  for line in self.d['radiative']:
   if line['up']>19:continue
   dl=self.d['levels'][line['up']]['E']-self.d['levels'][line['low']]['E']
   freq=dl*100*c/1e9
   checks.append(abs(freq/line['freq_GHz']-1))
  self.assertLess(max(checks),1e-10)

 def test_gl_source_1560_crosswalk(self):
  rows,valid,extra=raw_crosswalk(self.d)
  self.assertEqual(len(rows),1560)
  self.assertEqual(len(valid),1548)
  self.assertEqual(len(extra),16)
  self.assertEqual(sum(r['crosswalk_status']=='PRINTED_NUMERIC_MATCH' for r in rows),1498)
  self.assertEqual(sum(r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH' for r in rows),50)
  self.assertEqual(sum(r['crosswalk_status']=='SOURCE_DIAGONAL_NOT_A_TRANSITION' for r in rows),10)
  self.assertEqual(sum(r['crosswalk_status']=='SOURCE_PRINTED_UNRELIABLE_EMAA_CANDIDATE' for r in rows),2)

 def test_conspicuous_print_mismatch_not_silent_fixed(self):
  rows,_,_=raw_crosswalk(self.d)
  r=next(r for r in rows if (r['initial_v'],r['initial_J'],r['final_v'],r['final_J'],r['T_K'])==(1,6,0,10,105))
  self.assertAlmostEqual(r['ratio_GL_over_EMAA'],0.1,places=14)
  m=next(r for r in rows if (r['initial_v'],r['initial_J'],r['final_v'],r['final_J'],r['T_K'])==(1,2,0,5,2005))
  self.assertEqual(m['crosswalk_status'],'SOURCE_PRINTED_UNRELIABLE_EMAA_CANDIDATE')
  self.assertEqual(m['GL_source_token'],'1.58(10')
  self.assertAlmostEqual(m['EMAA_rate_cm3_s'],1.58e-10,places=19)

 def test_collisional_generator_and_detailed_balance(self):
  Tg=505.;G=bath_rates(self.d,Tg,1e6)
  self.assertLess(max(abs(G.sum(axis=0))),1e-12)
  lv=self.d['levels'];pi=np.array([lv[i]['g']*math.exp(-HCK*lv[i]['E']/Tg) for i in range(1,20)])
  pi/=pi.sum()
  self.assertLess(max(abs(G@pi)),1e-14)
  self.assertTrue(np.all(G-np.diag(np.diag(G))>=0))

 def test_thermal_equal_baths_lte(self):
  T=105.;n=1e6
  C=bath_rates(self.d,T,n);R,_=radiative_generator(self.d,T)
  p,res=stationary(C+R)
  lv=self.d['levels'];pi=np.array([lv[i]['g']*math.exp(-HCK*lv[i]['E']/T) for i in range(1,20)])
  pi/=pi.sum()
  self.assertLess(max(abs(p-pi)),1e-12)
  self.assertGreaterEqual(min(p),0)
  self.assertLess(abs(energy_flux(self.d,R,p)),1e-33)
  self.assertLess(abs(energy_flux(self.d,C,p)),1e-33)

 def test_positive_mmatrix_cold_and_hot(self):
  for T,n,z in [(5,1,0),(105,1e6,30),(3005,1e9,300),(55,1e3,100)]:
   C=bath_rates(self.d,T,n);R,lines=radiative_generator(self.d,2.7255*(1+z))
   p,res=stationary(C+R)
   self.assertGreaterEqual(min(p),0)
   self.assertLess(res,1e-14)
   Pr=energy_flux(self.d,R,p);Pc=energy_flux(self.d,C,p)
   self.assertLess(abs(Pr+Pc),1e-29)
   # Separate photon sums must agree with the radiative generator energy flow.
   photon=sum(z['delta_E_J']*(z['down_s']*p[z['up']-1]-z['up_s']*p[z['low']-1]) for z in lines)
   self.assertLess(abs(photon-Pr),1e-34)

 def test_source_quench_probability_and_fluence(self):
  cases,branches=first_v1_quench(self.d)
  self.assertEqual(len(cases),175)
  self.assertEqual(len(branches),2100)
  self.assertLess(max(abs(x['total_branch_mass']-1) for x in cases),1e-10)
  self.assertGreater(min(x['p_land_v0_J5to11'] for x in cases),0)
  self.assertTrue(all(x['mean_fluence_cm_minus3_s']>0 for x in cases))

 def test_hybrid_preserves_unprinted_data_and_not_full_gl_model(self):
  _,valid,extra=raw_crosswalk(self.d)
  self.assertEqual(len(extra),16)
  C=bath_rates(self.d,105,1e3)
  C2=bath_rates(self.d,105,1e3,overrides=valid)
  self.assertGreater(float(np.max(np.abs(C-C2))),0)
  self.assertLess(float(np.max(np.abs(C.sum(axis=0)))),1e-15)
  self.assertLess(float(np.max(np.abs(C2.sum(axis=0)))),1e-15)

 def test_source_only_not_chemistry(self):
  G=bath_rates(self.d,105,1e3)+radiative_generator(self.d,84.4905)[0]
  self.assertLess(max(abs(G.sum(axis=0))),1e-15)
  # No chemistry sink: column sums exactly zero within rounding.
  self.assertEqual(G.shape,(19,19))

if __name__=='__main__':unittest.main()
