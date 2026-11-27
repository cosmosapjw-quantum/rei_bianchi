import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cascade_bridge import SourceShape
import numpy as np
from pi0_physics import B_2G
class Tests(unittest.TestCase):
 def test_source_count(self):
  for energy in (206,216,229,241):
   q=SourceShape.from_exfor(energy)
   self.assertAlmostEqual(sum(q.weights),1,places=13)
   self.assertEqual(len(q.mu),len(q.weights))
 def test_physical_gamma_energies(self):
  q=SourceShape.from_exfor(216)
  self.assertTrue(np.all(q.lows>0))
  self.assertTrue(np.all(q.highs<216))
  self.assertTrue(np.all(q.highs>q.lows))
 def test_conservative_projection(self):
  q=SourceShape.from_exfor(229)
  for n in (30,60,120):
   eg=np.geomspace(1.5,max(q.highs)*1.000000001,n)
   f,ww=q.project_source(eg)
   self.assertAlmostEqual(float(np.dot(ww,f)),2*B_2G,places=12)
   self.assertTrue(np.all(f>=0))
 def test_analytic_photon_source_energy(self):
  q=SourceShape.from_exfor(206)
  self.assertAlmostEqual(q.exact_moments()['energy'],B_2G*np.dot(q.weights,q.epi),places=12)
if __name__=='__main__': unittest.main()

class PhysicsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cascade_bridge import run_fixed_epoch
        cls.result, cls.spectrum, cls.injected, cls.source = run_fixed_epoch(216.,1e5,48,photon_only_check=True)

    def test_source_analytic_moments(self):
        source=self.source
        self.assertLess(abs(self.result['source_grid_energy_relerr']),5e-4)
        self.assertAlmostEqual(self.result['pion_count_injected'],2*B_2G,places=12)

    def test_species_positivity(self):
        self.assertTrue(np.isfinite(self.spectrum).all())
        self.assertGreaterEqual(float(self.spectrum[1:].min()),0.)

    def test_below_cut_derived_split(self):
        r=self.result
        self.assertAlmostEqual(r['D_born_below150_per_pi0']+r['D_born_above150_per_pi0'],r['D_born_per_pi0_conditional'],places=12)
        self.assertGreater(r['fraction_D_born_below150'],0.95)

    def test_target_density_and_positive_response(self):
        r=self.result
        self.assertGreater(r['D_born_per_pi0_conditional'],0.)
        self.assertGreater(r['D_destroy_per_pi0'],0.)
        self.assertLess(r['D_destroy_per_pi0'],r['D_born_per_pi0_conditional'])
        self.assertLess(r['Be7_destroy_per_pi0'],r['D_destroy_per_pi0'])

    def test_electron_feedback_is_not_hard_coded(self):
        r=self.result
        self.assertGreater(r['electron_spectrum_max'],0.)
        self.assertGreater(r['positron_spectrum_max'],0.)
        self.assertGreater(r['D_born_coupled_over_photon_only'],1.)

    def test_primary_gamma_scaling(self):
        r=self.result
        self.assertAlmostEqual(r['D_born_per_primary_gamma_first_pi0_then_cascade'],r['pi0_parent_P_first']*r['D_born_per_pi0_conditional'],places=15)

    def test_photon_source_energy_ledger(self):
        r=self.result
        self.assertGreater(self.source.exact_moments()['mean_pion_energy'],0.)
        self.assertLess(self.source.exact_moments()['mean_pion_energy'],216)
        self.assertAlmostEqual(self.source.exact_moments()['energy'],B_2G*self.source.exact_moments()['mean_pion_energy'],places=12)
