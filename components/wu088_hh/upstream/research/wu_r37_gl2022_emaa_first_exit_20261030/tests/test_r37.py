import unittest, csv, hashlib, sys, math
from pathlib import Path
import numpy as np
import mpmath as mp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_r37 import *

class R37SourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=verify_inputs()
  cls.data=parse_radex(RAW)

 def test_original_pdf_and_emaa_byte_hashes(self):
  self.assertEqual(sha(RAW),EXPECTED['EMAA'])
  self.assertEqual(sha(SRC/'214302_1_online.pdf'),EXPECTED['GL_MAIN'])
  self.assertEqual(sha(SRC/'084307_1_online.pdf'),EXPECTED['VELILLA_MAIN'])

 def test_source_domain_and_excluded_suspect_points(self):
  self.assertEqual(len(T_GRID),8)
  self.assertNotIn(15,T_GRID)
  self.assertNotIn(2505,T_GRID)
  self.assertTrue(set(T_GRID).issubset(self.a['temperature_nodes_K']))
  self.assertEqual(self.a['shape'],[10,7,10])

 def test_invalid_source_tokens_not_approximated_as_zero(self):
  for token in ('.000(00)','', '1.8(10', 'missing'):
   with self.assertRaises(ValueError):parse_token(token)
  self.assertEqual(parse_token('4.43(13)'),4.43e-13)

 def test_spinweights_eq6_eq7(self):
  a=self.a;T=105
  W=source_reaction(self.data,a,T,'eq6_7_spin_weighted')
  R=source_reaction(self.data,a,T,'unweighted_source_counterfactual')
  np.testing.assert_allclose(W[::2]/R[::2],0.25,rtol=0,atol=6e-16)
  np.testing.assert_allclose(W[1::2]/R[1::2],0.75,rtol=0,atol=6e-16)

 def test_all52_radiative_censor_not_collisional_rate_completion(self):
  R=radex_all52(self.data,2.7255*301)
  self.assertEqual(R.shape,(52,52))
  self.assertGreater(float(np.sum(R[5:,:5])),0)
  self.assertLess(np.max(np.abs(R.sum(axis=0))),1e-12)

 def test_source_Mmatrix_positive_and_censor_conservation(self):
  cases, products,G,M=solve_case(self.data,self.a,105,1e3,300,'eq6_7_spin_weighted')
  self.assertTrue(np.all(M>=0))
  self.assertTrue(np.all(G-np.diag(G.diagonal())>=0))
  self.assertLess(max(x['max_probability_defect'] for x in cases),3e-15)
  for i in range(5):
   x=cases[i]
   self.assertAlmostEqual(x['P_H2_before_first_exit']+x['P_collision_exit_first']+x['P_radiative_exit_first'],1.0,places=14)
   self.assertAlmostEqual(x['P_radiative_exit_v0_highJ']+x['P_radiative_exit_vib_or_higher'],x['P_radiative_exit_first'],places=14)
   self.assertAlmostEqual(x['P_collision_exit_v0_highJ']+x['P_collision_exit_v1'],x['P_collision_exit_first'],places=14)

 def test_blackbody_off_has_no_radiative_first_exit(self):
  cases,_,_,_=solve_case(self.data,self.a,105,1e3,'OFF','eq6_7_spin_weighted')
  self.assertTrue(all(x['P_radiative_exit_first']==0.0 for x in cases))
  self.assertTrue(all(x['P_H2_before_first_exit']>0 for x in cases))

 def test_radiation_boundary_makes_difference_not_astro_history(self):
  x,_,_,_=solve_case(self.data,self.a,105,1e3,300,'eq6_7_spin_weighted')
  self.assertGreater(x[2]['P_radiative_exit_first'],0.5)
  self.assertLess(x[2]['P_H2_before_first_exit'],0.5)

 def test_spin_policy_chemical_absorption_monotonic(self):
  for T,n,z in [(55,.01,30),(105,1e3,300),(1505,1e6,0),(3005,1e3,100)]:
   eff,_,_,_=solve_case(self.data,self.a,T,n,z,'eq6_7_spin_weighted')
   raw,_,_,_=solve_case(self.data,self.a,T,n,z,'unweighted_source_counterfactual')
   self.assertTrue(all(e['P_H2_before_first_exit']<=r['P_H2_before_first_exit']+1e-12 for e,r in zip(eff,raw)))

 def test_paper_partial_hybrid_not_full_reaction(self):
  rows=paper_eq5_partial(self.data,self.a)
  self.assertEqual(len(rows),8)
  self.assertTrue(all(0<x['partial_fraction_of_printed_total']<=1.001 for x in rows))
  self.assertLess(rows[-1]['partial_fraction_of_printed_total'],rows[0]['partial_fraction_of_printed_total'])

 def test_off_source_temperature_prohibited(self):
  with self.assertRaises(ValueError):source_reaction(self.data,self.a,205,'eq6_7_spin_weighted')

 def test_independent_embedded_jump_chain(self):
  # Independent first-step recursion in arbitrary precision; no residence-time inverse.
  T,n,z,pol=105,1e3,300,'eq6_7_spin_weighted'
  q=n*source_reaction(self.data,self.a,T,pol)
  C=bath_rates(self.data,T,n); R=radex_all52(self.data,2.7255*(1+z))
  outC=np.sum(C[5:,:5],axis=0);outR=np.sum(R[5:,:5],axis=0)
  off=C[:5,:5]+R[:5,:5];np.fill_diagonal(off,0)
  with mp.workdps(65):
   H=[sum(mp.mpf(repr(float(off[i,j]))) for i in range(5) if i!=j)+mp.mpf(repr(float(outC[j])))+mp.mpf(repr(float(outR[j])))+sum(mp.mpf(repr(float(q[k,j]))) for k in range(10)) for j in range(5)]
   P=mp.matrix(5,5);absorb=mp.matrix(12,5)
   for j in range(5):
    for i in range(5):P[i,j]=mp.mpf(repr(float(off[i,j])))/H[j] if i!=j else 0
    for k in range(10):absorb[k,j]=mp.mpf(repr(float(q[k,j])))/H[j]
    absorb[10,j]=mp.mpf(repr(float(outC[j])))/H[j]
    absorb[11,j]=mp.mpf(repr(float(outR[j])))/H[j]
   branches=absorb*mp.inverse(mp.eye(5)-P)
   src,_pr,_,_=solve_case(self.data,self.a,T,n,z,pol)
   for j in range(5):
    self.assertLess(abs(float(sum(branches[k,j] for k in range(10)))-src[j]['P_H2_before_first_exit']),1e-14)
    self.assertLess(abs(float(branches[10,j])-src[j]['P_collision_exit_first']),1e-14)
    self.assertLess(abs(float(branches[11,j])-src[j]['P_radiative_exit_first']),1e-14)

if __name__=='__main__': unittest.main()
