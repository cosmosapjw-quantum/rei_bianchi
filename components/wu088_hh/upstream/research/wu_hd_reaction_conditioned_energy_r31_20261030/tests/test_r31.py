import csv
import math
import os
import tempfile
import unittest
from pathlib import Path
import numpy as np
from src import energy_ledger as e

class PhysicalEnergyLedgerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.m=e.restore_parent()
    cls.p=cls.m.load_r29()
    cls.old=cls.p.load_grid()
    cls.new=cls.m.get_grid(cls.old)
    cls.cases,cls.coll,cls.term,cls.ph=e.build_atlas()
    cls.matched=e.matched_density_policy_pairs()
 def test_exact_source_archive(self):
    self.assertEqual(e.file_sha(e.ROOT/'archive'/e.R30_ARCHIVE),e.R30_SHA256)
    self.assertEqual(e.file_sha(e.ROOT/'_r30_restored'/'archive'/'WU_R29_SOURCE_ORIGINAL_20261030.zip'),e.R29_SHA256)
 def test_count_and_scope(self):
    self.assertEqual(tuple(map(len,[self.cases,self.coll,self.term,self.ph])),(210,2100,1050,840))
    self.assertEqual({x['T_K'] for x in self.cases},set(e.restore_parent().load_r29().TEMPS))
 def test_each_case_balance(self):
    self.assertLess(max(abs(x['energy_balance_residual_J']) for x in self.cases),2.1e-34)
 def test_all_reactive_endpoint_probabilities(self):
    for j in range(0,len(self.term),5):
      self.assertAlmostEqual(sum(t['probability_reaction_at_HD_J'] for t in self.term[j:j+5]),1.,places=10)
 def test_R30_photon_emission_energy_parity(self):
    sample=self.cases[0]
    result,*_=e.one_case(self.p,self.old,self.new,sample['T_K'],sample['policy'],sample['n_over_ncrit_J2'],sample['initial_HD_J'])
    r30,*_=self.m.metrics_one(self.p,self.old,self.new,sample['T_K'],sample['policy'],sample['n_over_ncrit_J2'],sample['initial_HD_J'])
    self.assertAlmostEqual(result['integrated_photon_energy_J']/r30['integrated_photon_energy_J_per_initial_HD'],1.,places=13)
 def test_energy_from_matrix_generator_for_all(self):
    for x in self.cases:
      T=x['T_K'];policy=x['policy'];ratio=x['n_over_ncrit_J2'];j=x['initial_HD_J'];n=x['nHplus_cm3']
      G,*_=self.p.assemble(self.new,T,policy,n)
      m=np.linalg.solve(-G,np.eye(5)[:,j]); energy=np.array([self.new.energies_cm1[k]*100*self.p.PLANCK*self.p.SPEED_LIGHT for k in range(5)])
      delta=energy@(-G)@m
      self.assertAlmostEqual(float(delta/energy[-1]),float(x['initial_HD_rotational_energy_J']/energy[-1]),places=12)
 def test_ground_HD_bath_gain_cannot_be_positive(self):
    for x in self.cases:
      if x['initial_HD_J']==0:
        self.assertLessEqual(x['integrated_proton_bath_energy_gain_J'],1e-31)
 def test_signed_thermal_energy_transfer_is_nontrivial(self):
    xs=[x['integrated_proton_bath_energy_gain_J'] for x in self.cases]
    self.assertLess(min(xs),0);self.assertGreater(max(xs),0)
 def test_all_edges_positive_rate_and_energies(self):
    for r in self.coll:
      self.assertGreater(r['source_downward_k_cm3_per_s'],0)
      self.assertGreater(r['detailed_balance_derived_upward_k_cm3_per_s'],0)
      self.assertGreater(r['energy_gap_J'],0)
 def test_detailed_balance_is_source_based(self):
    for r in self.coll:
      T=r['T_K']; hi=r['high_J'];lo=r['low_J']; dE=r['energy_gap_J']
      pred=r['source_downward_k_cm3_per_s']*(2*hi+1)/(2*lo+1)*math.exp(-dE/(self.p.BOLTZMANN*T))
      self.assertAlmostEqual(r['detailed_balance_derived_upward_k_cm3_per_s']/pred,1.,places=14)
 def test_all_emission_ladder(self):
    for r in self.ph:
      self.assertGreater(r['source_A_per_s'],0)
      self.assertGreater(r['emitted_energy_J'],0)
 def test_Ncrit_preserves_R30_parent(self):
    x=next(x for x in self.cases if (x['T_K'],x['policy'],x['n_over_ncrit_J2'],x['initial_HD_J'])==(105,'Eq6-7_spin_effective',1.,2))
    self.assertAlmostEqual(x['nHplus_cm3'],3954.4181821071797,places=9)
 def test_negative_bad_grid_rejected(self):
    with self.assertRaises(ValueError):self.p.assemble(self.new, 105,'Eq6-7_spin_effective',-1.0)
 def test_output_csv_counts(self):
    for file,n in [('R31_ROTATIONAL_ENERGY_210.csv',210),('R31_COLLISION_ENERGY_2100.csv',2100),('R31_TERMINAL_STATE_1050.csv',1050),('R31_PHOTON_ENERGY_840.csv',840)]:
      with (e.ROOT/'results'/file).open() as f:self.assertEqual(sum(1 for _ in csv.DictReader(f)),n)
 def test_matched_density_policy_pair_conservation(self):
    self.assertEqual(len(self.matched),35)
    for r in self.matched:
      self.assertLess(abs(r['matched_energy_difference_residual_J']),1e-30)
      self.assertEqual(r['nHplus_matched_cm3'],self.p.reference_density(self.old,r['T_K'],'Eq6-7_spin_effective'))
 def test_restored_mutable_parent_guard(self):
    file=e.ROOT/'_r30_restored'/'sources'/'REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json'
    before=file.read_bytes()
    try:
      file.write_bytes(before+b'\n# tamper\n')
      with self.assertRaises(e.ImmutableSourceError):e.restore_parent()
    finally:file.write_bytes(before)
    self.assertEqual(e.file_sha(file),self.m.SUNG_SOURCE_SHA)

if __name__=='__main__':unittest.main()
