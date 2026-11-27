import copy
import csv
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
import zipfile
import numpy as np
from scipy.integrate import solve_ivp
from src.native_atlas import (check_pdf,extract_source,verify_source,parse_printed,expand_csv,moment_at,analyze,
  SourceContractError,TEMPS,FINAL)
from src.finite_species import (coefficients,run_experiment,step,two_order_study)
BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE/'sources/GL2022_CSIC_supplement.pdf'
OLD=BASE/'parent_R25/sources/GL2022_NATIVE_PRODUCT_GRID_R25.json'
R25_SHA='c00daeb40ae385f776c727a770ece0a3faee577496bcb621ae066294e94efca1'

class SourceAtlas(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=extract_source(SOURCE)
  cls.m=analyze(cls.r)
 def test_sha_pdf(self):check_pdf(SOURCE)
 def test_700(self):self.assertEqual(self.m['cell_count'],700)
 def test_coverage(self):self.assertEqual(self.r['shape'],[10,7,10])
 def test_counts(self):self.assertEqual(self.m['positive_cells']+self.m['printed_zero_unqualified'],700)
 def test_total_printed(self):self.assertEqual(self.m['positive_cells'],678)
 def test_printed_zero_count(self):self.assertEqual(self.m['printed_zero_unqualified'],22)
 def test_suspect_count(self):self.assertEqual(self.m['source_suspect_nonzero'],21)
 def test_j5_duplicate(self):self.assertEqual(self.r['tokens_jprime_j_T'][0][5],self.r['tokens_jprime_j_T'][1][5])
 def test_2505_anomaly(self):self.assertEqual(self.r['tokens_jprime_j_T'][7][3][8],'6.72(16)')
 def test_2019_units(self):self.assertEqual(parse_printed('1.15(10)'),Decimal('1.15E-10'))
 def test_zero_not_true_zero(self):self.assertIsNone(parse_printed('0.00(00)'));self.assertIsNone(parse_printed('.000(00)'))
 def test_bad_token(self):
  for x in ('NaN','1.1(-10)','1.1(100)','-1.1(10)','1.10e-10'):
   with self.subTest(x=x),self.assertRaises(SourceContractError):parse_printed(x)
 def test_r25_original_exact(self):
  self.assertEqual(self.r['r25_subset_sha256'],'f1b8e438a0117688e2497af1434227a42c8c158bab9f810b536b3ad2c36e4174')
  r25=json.loads(OLD.read_text())
  self.assertEqual(r25['tokens_by_product_J'],[[self.r['tokens_jprime_j_T'][jp][2][ti] for ti in range(10)] for jp in range(10)])
 def test_105_R25_anchor(self):self.assertEqual(self.r['tokens_jprime_j_T'][1][2][2],'1.15(10)')
 def test_source_record_sha_reject(self):
  bad=copy.deepcopy(self.r);bad['tokens_jprime_j_T'][0][0][0]='3.11(22)'
  with self.assertRaises(SourceContractError):verify_source(bad)
 def test_digest_reforged_negative(self):
  bad=copy.deepcopy(self.r);bad['tokens_jprime_j_T'][0][0][0]='3.11(22)'
  bad['token_sha256']=hashlib.sha256(json.dumps(bad['tokens_jprime_j_T'],ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
  with self.assertRaises(SourceContractError):verify_source(bad)
 def test_table11_mutation_reject(self):
  bad=copy.deepcopy(self.r);bad['table11_thermal_nominal_tokens'][0]='2.47(20)'
  with self.assertRaises(SourceContractError):verify_source(bad)
 def test_source_gate_reject(self):
  for key,value in [('physical_Q','-4e-21'),('PES_native_threshold','1'),('owner_ACK',True),('source_uncertainty',0),('production','ISSUED'),('L4',True)]:
   with self.subTest(key=key):
    bad=copy.deepcopy(self.r);bad[key]=value
    with self.assertRaises(SourceContractError):verify_source(bad)
 def test_refuses_unpublished_T(self):
  with self.assertRaises(SourceContractError):moment_at(self.r,100,2,False)
 def test_table11_last(self):self.assertEqual(self.m['original_table11_cm3_s'][-1],'7.22E-10')
 def test_thermal_not_reconstructed(self):self.assertIn('NOT_QUALIFIED',self.m['thermal_Table11_reconstruction'])
 def test_odd_parity_source(self):
  for T in (105,255):
   a=moment_at(self.r,T,2,False);b=moment_at(self.r,T,2,True)
   self.assertNotEqual(a['positive_sum_cm3_s'],b['positive_sum_cm3_s'])
   source=self.r['tokens_jprime_j_T'];idx=TEMPS.index(T)
   with localcontext() as ctx:
    ctx.prec=64
    spin_direct=sum((parse_printed(source[jp][2][idx])*(Decimal('0.75') if jp%2 else Decimal('0.25')) for jp in FINAL),Decimal(0))
    self.assertEqual(Decimal(b['positive_sum_cm3_s']),spin_direct)
 def test_flagged_rows(self):
  self.assertNotEqual(moment_at(self.r,105,5,False)['source_status'],'PASS_PRINTED_COMPLETE')
  self.assertNotEqual(moment_at(self.r,2505,3,False)['source_status'],'PASS_PRINTED_COMPLETE')
  self.assertNotEqual(moment_at(self.r,15,2,False)['source_status'],'PASS_PRINTED_COMPLETE')
 def test_completeness_105(self):
  self.assertEqual(moment_at(self.r,105,4,True)['source_status'],'PASS_PRINTED_COMPLETE')
 def test_700_csv_no_missing(self):
  rows=expand_csv(self.r)
  self.assertEqual(len(rows),700)
  self.assertEqual(sum(v['published_rate_cm3_s']=='' for v in rows),22)
 def test_wrong_pdf(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'wrong.pdf';p.write_bytes(SOURCE.read_bytes()[:-1]+b'0')
   with self.assertRaises(SourceContractError):check_pdf(p)

class Chemistry(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.r=extract_source(SOURCE)
 def test_policies(self):
  for spin in (False,True):
   q,K=coefficients(self.r,105,(2,4),spin)
   self.assertEqual(len(q),2)
   self.assertTrue(all(len(row)==10 for row in q))
   self.assertAlmostEqual(sum(q[0]),K[0],delta=1e-29)
 def test_censored_rejected(self):
  with self.assertRaises(SourceContractError):coefficients(self.r,15,(2,4),False)
 def test_duplicate_rejected(self):
  with self.assertRaises(SourceContractError):coefficients(self.r,255,(5,),False)
 def test_exponent_rejected(self):
  with self.assertRaises(SourceContractError):coefficients(self.r,2505,(3,),False)
 def test_unavailable_initial(self):
  with self.assertRaises(SourceContractError):coefficients(self.r,105,(8,),False)
 def test_no_proton_reserve(self):
  with self.assertRaises(ValueError):run_experiment(self.r,schedule=((105,5e9),),spin=False,proton_initial_m3=1e5)
 def test_conservation_both_order(self):
  for spin in (False,True):
   for t in (((105,5e9),(255,5e9)),((255,5e9),(105,5e9))):
    r=run_experiment(self.r,schedule=t,spin=spin)
    self.assertLess(r['max_conservation_abs_m3'],1e-6)
    self.assertIsNone(r['physical_Q'])
    self.assertEqual(r['canonical_DAG'],'34/49_UNCHANGED')
 def test_single_segment_compatibility(self):
  for spin in (False,True):
   a=run_experiment(self.r,schedule=((105,7.5e9),),spin=spin)
   b=run_experiment(self.r,schedule=((105,2.5e9),(105,5e9)),spin=spin)
   self.assertAlmostEqual(a['total_extent_m3'],b['total_extent_m3'],delta=2e-5)
 def test_order_noncommutation(self):
  for spin in (False,True):
   r=two_order_study(self.r,spin)
   self.assertGreater(abs(r['delta_forward_minus_reverse_extent_m3']),1000)
   self.assertEqual(r['production'],'NOT_ISSUED')
 def test_positive_and_0time(self):
  r=run_experiment(self.r,schedule=((105,1e-6),),spin=False)
  self.assertGreater(r['total_extent_m3'],0)
  self.assertLess(r['total_extent_m3'],1e-5)
 def test_detailed_balance_not_issued(self):
  r=two_order_study(self.r,True)
  self.assertIsNone(r['physical_Q']);self.assertIsNone(r['owner_ACK'])
 def test_against_independent_ivp(self):
  for spin in (False,True):
   for schedule in (((105,5e9),(255,5e9)),((255,5e9),(105,5e9))):
    predicted=run_experiment(self.r,schedule=schedule,spin=spin)
    # y = [p,y2,y4,d,z0..z9]. Direct physical ODE integration.
    y=np.array([1.3e6,6e5,4e5,0.]+[0.]*10)
    for T,dt in schedule:
     q,K=coefficients(self.r,T,(2,4),spin);q=np.array(q);K=np.array(K)
     def rhs(t,v):
      p,a,b,d,*z=v
      flux=p*np.array([a,b])*K
      dz=p*np.array([a,b])@q
      return np.array([-sum(flux),-flux[0],-flux[1],sum(flux),*dz])
     sol=solve_ivp(rhs,(0,float(dt)),y,method='DOP853',rtol=1e-12,atol=1e-7)
     self.assertTrue(sol.success)
     y=sol.y[:,-1]
    measured=[y[0],y[1],y[2],y[3],*y[4:]]
    expect=[predicted['final_proton_m3'],predicted['final_HD_J_m3']['2'],predicted['final_HD_J_m3']['4'],predicted['final_Dplus_m3'],*predicted['final_H2_Jprime_m3']]
    self.assertLess(max(abs(x-x0) for x,x0 in zip(measured,expect)),2e-4)

if __name__=='__main__':unittest.main()
