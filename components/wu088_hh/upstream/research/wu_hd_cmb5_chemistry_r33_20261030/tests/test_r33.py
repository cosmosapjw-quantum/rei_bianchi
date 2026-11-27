import csv,hashlib,io,json,math,unittest,zipfile
from pathlib import Path
import numpy as np
from src import cmb5 as m

class R33Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parent,cls.old,cls.grid,cls.centers=m.get_parent()
  cls.out=m.ROOT/'results'
  with zipfile.ZipFile(m.ROOT/'archive'/m.PARENT_ZIP_NAME) as z:
   r31=z.read('archive/WU_R31_SOURCE_ORIGINAL_20261030.zip')
  with zipfile.ZipFile(io.BytesIO(r31)) as z:
   r30=z.read('archive/WU_R30_SOURCE_ORIGINAL_20261030.zip')
  with zipfile.ZipFile(io.BytesIO(r30)) as z:
   cls.r30cases=list(csv.DictReader(io.StringIO(z.read('results/R30_CASES_210.csv').decode())))
   cls.r30products=list(csv.DictReader(io.StringIO(z.read('results/R30_RESTRICTED_H2_JOINT_2100.csv').decode())))

 def test_original_parent_byte(self):
  self.assertTrue(m.verify_sources());self.assertEqual(m.hashfile(m.ROOT/'archive'/m.PARENT_ZIP_NAME),m.PARENT_SHA)
 def test_original_source_exact(self):
  for key,sha in m.SOURCE_HASH.items():self.assertEqual(m.hashfile(m.ROOT/'sources'/key),sha)
 def test_original_source_tamper_rejected(self):
  other=(m.ROOT/'sources/GL2022_700_SOURCE.json').read_bytes()
  self.assertNotEqual(hashlib.sha256(other+b' ').hexdigest(),m.SOURCE_HASH['GL2022_700_SOURCE.json'])
 def test_physical_grid(self):
  self.assertEqual(len(self.grid.q),350);self.assertEqual(len(self.grid.down),70)
  self.assertEqual(list(self.centers),[89.22792,177.84141,265.24055,350.85401])
 def test_gas_collision_detailed_balance(self):
  p=self.parent;T=105;pol='raw_SQM'; n=p.reference_density(self.grid,T,pol)
  G,G0,C,chem,r=m.assemble(p,self.grid,T,pol,n,0)
  Ep=np.array([self.grid.energies_cm1[k]*m.CMJ for k in range(5)])
  w=np.array([(2*j+1)*math.exp(-Ep[j]/(m.KB*T)) for j in range(5)]);w/=w.sum()
  self.assertLess(np.linalg.norm(C@w,np.inf),1e-18)
 def test_radiation_LTE_and_occupations(self):
  for T in [5,50,300,1000]:
   Ep=np.array([self.grid.energies_cm1[k]*m.CMJ for k in range(5)])
   w=np.array([(2*j+1)*math.exp(-Ep[j]/(m.KB*T)) for j in range(5)]);w/=w.sum()
   R=np.zeros((5,5))
   for j in range(1,5):
    q=m.photon_occupation(self.centers[j-1],T)
    down=self.grid.A[j]*(1+q)
    up=self.grid.A[j]*(2*j+1)/(2*j-1)*q
    R[j-1,j]+=down;R[j,j]-=down
    R[j,j-1]+=up;R[j-1,j-1]-=up
   self.assertLess(np.linalg.norm(R@w,np.inf),2e-17)
 def test_zero_radiation_limit(self):
  self.assertEqual(m.photon_occupation(89.22792,0),0)
  G,G0,C,chem,rad=m.assemble(self.parent,self.grid,105,'raw_SQM',3954.41,0)
  for j,c,sp,st,ab,occ in rad:self.assertEqual((st,ab,occ),(0.,0.,0.))
 def test_cold_and_hot_cmb_sign(self):
  vals=[m.evaluate(self.parent,self.grid,self.centers,105,'Eq6-7_spin_effective',1.,2,lab,z)[0] for lab,z in zip(m.LABELS,m.REDSHIFTS)]
  self.assertGreater(vals[0]['net_radiative_transfer_J'],0)
  self.assertLess(vals[-1]['net_radiative_transfer_J'],0)
  self.assertGreater(vals[-1]['CMB_absorptions_per_initial'],vals[0]['CMB_absorptions_per_initial'])
 def test_full_generator_nonnegative_and_mass(self):
  for T in m.TEMPS:
   for p in m.MODES:
    for z in [None,0,30,300]:
     G,G0,C,R,lines=m.assemble(self.parent,self.grid,T,p,self.parent.reference_density(self.grid,T,p),0 if z is None else m.T0*(1+z))
     self.assertLess(np.max(np.abs(G.sum(axis=0)+R.sum(axis=0))),1e-17)
     self.assertTrue(np.all(np.linalg.eigvals(G).real <0))
 def test_first_radiation_or_reaction(self):
  r,lines,br=m.evaluate(self.parent,self.grid,self.centers,105,'Eq6-7_spin_effective',1.,2,'z100',100)
  self.assertAlmostEqual(r['prob_any_radiative_interaction_before_reaction']+r['prob_reaction_before_any_radiation'],1.,places=12)
  self.assertAlmostEqual(sum(x['probability_all'] for x in br),1.,places=12)
  self.assertAlmostEqual(sum(x['joint_no_radiation'] for x in br),r['prob_reaction_before_any_radiation'],places=12)
 def test_energy_identity(self):
  for j in range(5):
   r,_,_=m.evaluate(self.parent,self.grid,self.centers,55,'raw_SQM',.1,j,'z300',300)
   self.assertLess(abs(r['energy_balance_residual_J']),3e-32)
 def test_r30_exact_OFF_baseline_all_210(self):
  for old in self.r30cases:
   T=int(old['T_K']);pol=old['policy'];ratio=float(old['n_over_ncrit_J2']); j=int(old['initial_J'])
   cur,lines,br=m.evaluate(self.parent,self.grid,self.centers,T,pol,ratio,j,'OFF',None)
   self.assertTrue(math.isclose(cur['spont_emissions_per_initial'],float(old['expected_photons']),rel_tol=1e-11,abs_tol=1e-11))
   self.assertTrue(math.isclose(cur['mean_reaction_wait_s'],float(old['lifetime_to_restricted_exchange_s']),rel_tol=2e-13))
   self.assertTrue(math.isclose(cur['net_radiative_transfer_J'],float(old['integrated_photon_energy_J_per_initial_HD']),rel_tol=1e-11))
 def test_r30_product_replay_all_2100(self):
  orig={(int(x['T_K']),x['policy'],float(x['n_over_ncrit_J2']),int(x['initial_J']),int(x['H2_final_Jprime'])):float(x['probability_restricted_product_Jprime']) for x in self.r30products}
  for T in m.TEMPS:
   for p in m.MODES:
    for ratio in m.RATIOS:
     for j in m.LEVELS:
      _,_,b=m.evaluate(self.parent,self.grid,self.centers,T,p,ratio,j,'OFF',None)
      for row in b:self.assertTrue(math.isclose(row['probability_all'],orig[(T,p,ratio,j,row['H2_final_Jprime'])],rel_tol=1e-11,abs_tol=1e-12))
 def test_atlas_counts_and_source(self):
  for n,rows in [('R33_CMB_CASES_1470.csv',1470),('R33_CMB_LINES_5880.csv',5880),('R33_H2_PRODUCTS_14700.csv',14700),('R33_FIXED_DENSITY_POLICY_735.csv',735)]:
   with (self.out/n).open(newline='') as f:self.assertEqual(sum(1 for _ in csv.DictReader(f)),rows)
 def test_radiation_balance_redshift_roots(self):
  with (self.out/'R33_RADIATIVE_BALANCE_Z_210.csv').open(newline='') as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),210)
  self.assertEqual(sum(x['zero_crossing_in_0_300']=='True' for x in r),163)
  for x in r:
   if x['zero_crossing_in_0_300']=='True':
    self.assertGreater(float(x['z_radiative_balance']),0)
    self.assertLess(float(x['z_radiative_balance']),300)
    self.assertLess(abs(float(x['Rnet_root_residual_J'])),1e-28)
 def test_rad_no_source_repair(self):
  self.assertEqual(m.TEMPS,(55,105,255,505,1005,2005,3005))
  self.assertEqual(m.REDSHIFTS,(None,0,5,10,30,100,300))
 def test_no_production_or_assumed_Q(self):
  x=json.loads((self.out/'SUMMARY.json').read_text())
  self.assertIsNone(x['physical_Q']);self.assertFalse(x['EMAA_raw_acquired']);self.assertEqual(x['canonical_DAG'],'34/49_UNCHANGED')

if __name__=='__main__':unittest.main()
