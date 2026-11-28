import csv,hashlib,io,json,math,unittest,zipfile
from pathlib import Path
import numpy as np
from src import quench as m

class R32Physics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows,cls.e0,cls.e1=m.load_sources()

 def test_01_immutable_original_sources(self):
  for typ,path in [('R31','archive/WU_R31_SOURCE_ORIGINAL_20261030.zip'),('GL','sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv'),('PDF','sources/GL2022_CSIC_supplement.pdf')]:
   self.assertEqual(m.filehash(m.ROOT/path),m.SOURCE_SHA[typ])
  z=zipfile.ZipFile(m.ROOT/'archive/WU_R31_SOURCE_ORIGINAL_20261030.zip')
  self.assertIsNone(z.testzip())
  self.assertEqual(hashlib.sha256(z.read('archive/WU_R30_SOURCE_ORIGINAL_20261030.zip')).hexdigest(),'d1aa63fedb6527d6aab59df447f1f2b4aa557fab98789b962464a2b86bb5bf16')

 def test_02_original_source_census_and_2005_block(self):
  self.assertEqual(len(self.rows),890)
  self.assertEqual(sum(r['final_v']=='0' for r in self.rows),680)
  self.assertEqual(sum(r['final_v']=='1' for r in self.rows),210)
  self.assertEqual(sum(r['status']=='SOURCE_PRINTED_VALID' for r in self.rows),889)
  self.assertEqual(len(m.QUALIFIED_T),9)
  with self.assertRaises(m.SourceError):m.build_generator(self.rows,2005,self.e1,m.MODES[0])

 def test_03_2011_v2_source_energy_state_map(self):
  self.assertAlmostEqual(self.e0[1],89.227932,places=6)
  self.assertAlmostEqual(self.e1[0],3632.160743,places=6)
  self.assertAlmostEqual(self.e1[-1],5384.374907,places=6)
  self.assertTrue(np.all(np.diff(self.e1)>0))

 def test_04_original_cells_9T_complete(self):
  for T in m.QUALIFIED_T:
   y=[r for r in self.rows if int(r['T_K'])==T]
   self.assertEqual(len(y),89)
   self.assertEqual(len([r for r in y if r['final_v']=='0']),68)
   self.assertEqual(len([r for r in y if r['final_v']=='1']),21)
   self.assertTrue(all(r['status']=='SOURCE_PRINTED_VALID' for r in y))

 def test_05_generator_source_faithfulness(self):
  h,q,downs,ups,sinks=m.build_generator(self.rows,105,self.e1,m.MODES[0]);self.assertEqual(len(downs),21);self.assertEqual(len(ups),21);self.assertEqual(len(sinks),68)
  self.assertLess(np.max(np.abs(h.sum(axis=0)+q.sum(axis=0))),1e-22)
  self.assertTrue(np.all(q.sum(axis=0)>0))

 def test_06_upward_detailed_balance(self):
  T=105
  h,q,downs,ups,sinks=m.build_generator(self.rows,T,self.e1,m.MODES[0]); up={(i,j):x for i,j,x in ups}
  for i,j,k in downs:
   self.assertAlmostEqual(up[j,i]/k,((2*i+1)/(2*j+1))*math.exp(-m.CM_TO_J*(self.e1[i]-self.e1[j])/(m.KB*T)),places=13)

 def test_07_counterfactual_no_source_upward(self):
  h,q,d,u,s=m.build_generator(self.rows,105,self.e1,m.MODES[1]);self.assertEqual(len(u),0);self.assertEqual(len(d),21)
  self.assertAlmostEqual(h[6,0],0.,places=16)

 def test_08_fundamental_probability_and_fluence(self):
  for T in m.QUALIFIED_T:
   for mode in m.MODES:
    h,q,*_=m.build_generator(self.rows,T,self.e1,mode)
    for j in range(7):
     x=m.case_solve(h,q,self.e0,self.e1,j)
     self.assertGreater(x['fluence'],0)
     self.assertAlmostEqual(sum(x['p']),1,places=11)
     self.assertTrue(np.all(x['p']>=0))

 def test_09_energy_balance_all_126(self):
  res=[]
  for T in m.QUALIFIED_T:
   for mode in m.MODES:
    h,q,*_=m.build_generator(self.rows,T,self.e1,mode)
    for j in range(7):
     x=m.case_solve(h,q,self.e0,self.e1,j)
     res.append(abs(x['residual']))
  self.assertEqual(len(res),126)
  self.assertLess(max(res),1e-32)

 def test_10_no_2005_case_or_zero_imputation(self):
  path=m.ROOT/'results/ATLAS_QUENCH_126.csv'
  with path.open() as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),126)
  self.assertTrue(all(int(x['T_K'])!=2005 for x in r))
  self.assertEqual(set(x['mode'] for x in r),set(m.MODES))

 def test_11_native_105K_physics_not_mocked(self):
  h,q,*_=m.build_generator(self.rows,105,self.e1,m.MODES[0]);x=m.case_solve(h,q,self.e0,self.e1,0)
  self.assertAlmostEqual(x['k_eff']/1e-9,1.449128031791665,places=10)
  self.assertAlmostEqual(x['bath']/1.602176634e-19,0.25047204504258347,places=11)

 def test_12_nontrivial_upward_policy_effect(self):
  x=[]
  for mode in m.MODES:
   h,q,*_=m.build_generator(self.rows,3005,self.e1,mode)
   x.append(m.case_solve(h,q,self.e0,self.e1,0))
  self.assertLess(x[0]['k_eff']/x[1]['k_eff'],0.97)
  self.assertGreater(x[0]['k_eff']/x[1]['k_eff'],0.95)

 def test_13_source_spectral_provenance_not_upgrade(self):
  x=json.loads((m.ROOT/'sources/CDMS2011V2_RENDERED_V0V1_LEVELS.json').read_text())
  self.assertIsNone(x['original_2011_raw_bytes_sha256'])
  self.assertTrue(x['not_use_as_observed_uncertainty'])

 def test_14_model_not_full_rates(self):
  x=json.loads((m.ROOT/'results/SUMMARY.json').read_text())
  self.assertFalse(x['full_gas_heating'])
  self.assertIsNone(x['EMAA_raw_171x25'])
  self.assertEqual(x['new_canonical_DAG_nodes'],0)
  self.assertEqual(x['production'],'NOT_ISSUED')

if __name__=='__main__':unittest.main()
