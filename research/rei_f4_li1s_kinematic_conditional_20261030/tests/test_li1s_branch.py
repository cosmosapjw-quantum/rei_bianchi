"""Regression tests for frozen BASS Li I K-shell kinematic science data."""
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_simpson

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('li1s_branch',ROOT/'code/li1s_branch.py')
li=importlib.util.module_from_spec(spec)
sys.modules['li1s_branch']=li
spec.loader.exec_module(li)

class FrozenLiKinematics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=li.physics()
        cls.r=cls.d['result']
        cls.e=cls.r['source_exposures_per_baryon']

    def test_01_source_original_sha(self):
        self.assertEqual(li.digest(li.ORIGINAL.read_bytes()),li.ORIGINAL_SHA)

    def test_02_native_grid_counts(self):
        self.assertEqual(self.r['counts']['epochs'],193)
        self.assertEqual(self.r['counts']['original_photon_bins'],71)
        self.assertEqual(self.r['counts']['active_Li1s_bins'],22)
        self.assertEqual(self.r['counts']['bin_rows'],193*2*22)
        self.assertEqual(self.r['counts']['hhe_potential_rows'],193*3)

    def test_03_reproduces_PR277_events(self):
        self.assertAlmostEqual(self.e['events'],3.4426556153037163e-11,delta=2e-23)
        self.assertLessEqual(self.r['derived']['max_relative_Li1s_event_vs_PR277'],2e-14)

    def test_04_reproduces_PR277_core_energy(self):
        self.assertAlmostEqual(self.e['BASS_core_eV'],2.0310979599168846e-9,delta=1e-20)

    def test_05_NIST_atomic_threshold_ordering(self):
        self.assertTrue(li.BASS_K_EDGE_EV < li.E_LI_TRIPLET_EDGE<li.E_LI_SINGLET_EDGE<li.E_DOUBLE_EV)
        self.assertTrue(li.E_TRIPLET_EV<li.I_LIPLUS_EV)
        self.assertTrue(li.E_SINGLET_EV<li.I_LIPLUS_EV)

    def test_06_source_first_bin_triplet_only(self):
        self.assertLess(li.E_LI_TRIPLET_EDGE,self.r['derived']['first_Li_active_bin_energy_eV'])
        self.assertLess(self.r['derived']['first_Li_active_bin_energy_eV'],li.E_LI_SINGLET_EDGE)
        self.assertEqual(self.r['derived']['triplet_only_bins'],1)
        self.assertGreater(self.e['triplet_only_events'],0)

    def test_07_no_fictitious_Auger(self):
        self.assertFalse(self.r['derived']['field_free_Auger_allowed_from_1s2s_singlet_or_triplet'])
        self.assertEqual(self.r['derived']['singlet_and_triplet_branch_probabilities'],'UNBOUND')

    def test_08_K_energy_bin_by_bin(self):
        for r in self.d['bins']:
            e=r['photon_eV']
            self.assertGreaterEqual(r['primary_electron_eV_min'],-1e-13)
            self.assertLessEqual(r['primary_electron_eV_min'],r['primary_electron_eV_max']+1e-14)
            self.assertAlmostEqual(e,li.I_LI_EV+r['conditional_excitation_eV_min']+r['primary_electron_eV_max'],delta=2e-12)
            self.assertAlmostEqual(e,li.I_LI_EV+r['conditional_excitation_eV_max']+r['primary_electron_eV_min'],delta=2e-12)

    def test_09_exposure_conservation_bounds(self):
        a=self.e['absorbed_eV'];i=self.e['NIST_valence_ion_eV']
        self.assertTrue(np.isclose(a,i+self.e['NIST_excitation_min_eV']+self.e['NIST_primary_max_eV'],rtol=1e-13))
        self.assertTrue(np.isclose(a,i+self.e['NIST_excitation_max_eV']+self.e['NIST_primary_min_eV'],rtol=1e-13))

    def test_10_no_assigned_double_yield(self):
        self.assertGreater(self.e['single_K_events_above_double_threshold'],0)
        self.assertEqual(self.r['derived']['direct_double_photoionization_partial_sigma'],'NOT_SOURCE_QUALIFIED')
        self.assertTrue(all(not b['double_photoionization_rate_known'] for b in self.d['bins']))

    def test_11_no_thermalization_assumed(self):
        self.assertEqual(self.r['derived']['secondary_electron_thermal_deposition_kernel'],'NOT_SOURCE_QUALIFIED')
        self.assertEqual(self.r['derived']['REI_IgmPhotoInput_heat'],'UNBOUND')
        self.assertTrue(all(not h['REI_thermal_port_valid'] for h in self.d['hhe']))

    def test_12_HHe_rates_native_at_same_source(self):
        self.assertLess(self.r['derived']['max_abs_HHe_gamma_per_absorber_s'],1e-22)
        self.assertEqual(len(set(h['source_species'] for h in self.d['hhe'])),3)

    def test_13_nonnegative_extreme_values(self):
        self.assertTrue(all(float(r['source_events_per_baryon_s'])>=0 for r in self.d['bins']))
        self.assertGreater(self.e['NIST_excitation_min_eV'],self.e['BASS_core_eV'])
        self.assertGreater(self.e['NIST_excitation_max_eV'],self.e['NIST_excitation_min_eV'])

    def test_14_no_IVP_or_promotion(self):
        self.assertEqual(self.r['counts']['new_IVPs'],0)
        self.assertTrue(self.r['holds']['NO_MORE_IVPs'])
        self.assertEqual(self.r['holds']['PRODUCTION'],'HOLD')
        self.assertFalse(self.r['holds']['L4_ready'])
        self.assertEqual(self.r['holds']['canonical_physical_delta'],0)

    def test_15_source_neg_control(self):
        original=li.ORIGINAL_SHA
        try:
            li.ORIGINAL_SHA='0'*64
            with self.assertRaisesRegex(ValueError,'PR277_ZIP_SHA_MISMATCH'):
                li.load_source()
        finally:
            li.ORIGINAL_SHA=original

    def test_16_original_NIST_energy_factor(self):
        self.assertAlmostEqual(li.CM1_TO_EV,1.2398419843320026e-4,places=15)
        self.assertAlmostEqual(li.E_TRIPLET_EV,59.02072367315768,places=9)
        self.assertAlmostEqual(li.E_SINGLET_EV,60.922559447552,places=9)

    def test_17_saved_clock_sample_count(self):
        xx=np.array([v['x'] for v in self.d['epochs']]);h=np.array([v['H_s'] for v in self.d['epochs']]);r=np.array([v['source_Li1s_events_per_baryon_s'] for v in self.d['epochs']]);
        self.assertTrue(np.all(np.diff(xx)>0))
        self.assertAlmostEqual(float(cumulative_simpson(r/h,x=xx,initial=0)[-1]),self.e['events'],delta=1e-23)

if __name__ == '__main__':unittest.main()
