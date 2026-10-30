"""Targeted physical and implementation checks for immutable BASS193 radiative capacity."""
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('radiative',ROOT/'code/radiative_atlas.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RadiativeCapacity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=mod.compute()
        cls.result=cls.data['result']
        cls.r=cls.result['saved_trajectory_exposures_per_baryon']

    def test_01_source_hash_immutable(self):
        self.assertEqual(mod.sha256_bytes(mod.ORIGINAL.read_bytes()),mod.ORIGINAL_SHA)

    def test_02_nested_pr277_source(self):
        b,e,o=mod.read_source()
        self.assertEqual(o['source']['BASS_owner_commit'],mod.SOURCE_OWNER)

    def test_03_actual_193_saved_epochs(self):
        self.assertEqual(len(self.data['epochs']),193)

    def test_04_actual_8492_active_bin_rows(self):
        self.assertEqual(len(self.data['bins']),8492)

    def test_05_expected_two_isotopes(self):
        self.assertEqual(set(x['isotope'] for x in self.data['bins']),{'Li6I','Li7I'})

    def test_06_primordial_HeII_threshold_order(self):
        self.assertGreater(mod.E_TRIPLET_EV,mod.THRESHOLDS_EV['He_II'])
        self.assertLess(mod.E_SINGLET_EV,2*mod.THRESHOLDS_EV['He_II'])
        self.assertGreater(mod.E_SINGLET_EV,2*mod.THRESHOLDS_EV['He_I'])

    def test_07_triplet_single_M1_photon(self):
        for t in mod.THRESHOLDS_EV.values():
            self.assertEqual(mod.allowed_event_bounds(True,t),(1,1))

    def test_08_singlet_two_photon_HI_capacity(self):
        self.assertEqual(mod.allowed_event_bounds(False,mod.THRESHOLDS_EV['H_I']),(1,2))

    def test_09_singlet_two_photon_HeI_capacity(self):
        self.assertEqual(mod.allowed_event_bounds(False,mod.THRESHOLDS_EV['He_I']),(1,2))

    def test_10_singlet_two_photon_HeII_capacity(self):
        self.assertEqual(mod.allowed_event_bounds(False,mod.THRESHOLDS_EV['He_II']),(0,1))

    def test_11_two_photon_support_extrema_sampled(self):
        for chi in mod.THRESHOLDS_EV.values():
            lo,hi=mod.two_photon_count_bounds(mod.E_SINGLET_EV,chi)
            nn=[int(y>chi)+int(mod.E_SINGLET_EV-y>chi)
                for y in np.linspace(0,mod.E_SINGLET_EV,10001)]
            self.assertEqual(min(nn),lo)
            self.assertEqual(max(nn),hi)

    def test_12_parent_original_BASS_events_reused(self):
        self.assertAlmostEqual(self.r['K_events']/3.4426556153037163e-11,1.,places=13)

    def test_13_forced_triplet_events_identical_to_parent(self):
        self.assertAlmostEqual(self.r['triplet_forced_events']/4.27548054648883e-12,1.,places=13)

    def test_14_HeII_min_equals_forced_triplet(self):
        self.assertAlmostEqual(self.r['potential_He_II_photons_min']/self.r['triplet_forced_events'],1.,places=13)

    def test_15_HeII_max_equals_total_single_K_events(self):
        self.assertAlmostEqual(self.r['potential_He_II_photons_max']/self.r['K_events'],1.,places=13)

    def test_16_HI_HeI_max_identical(self):
        self.assertAlmostEqual(self.r['potential_H_I_photons_max']/self.r['potential_He_I_photons_max'],1.,places=13)

    def test_17_energy_ledger_lower(self):
        rhs=self.r['source_li_valence_ion_eV']+self.r['vacuum_total_radiative_energy_min_eV']+self.r['conditional_photoelectron_kinetic_max_eV']
        self.assertAlmostEqual(rhs/self.r['source_absorption_eV'],1.,places=13)

    def test_18_energy_ledger_upper(self):
        rhs=self.r['source_li_valence_ion_eV']+self.r['vacuum_total_radiative_energy_max_eV']+self.r['conditional_photoelectron_kinetic_min_eV']
        self.assertAlmostEqual(rhs/self.r['source_absorption_eV'],1.,places=13)

    def test_19_observed_singlet_lifetime_and_A(self):
        a=self.result['measured_radiative_lifetimes']['LiII_singlet_2E1']
        self.assertEqual(a['tau_s'],503e-6)
        self.assertAlmostEqual(a['A_per_s']*a['tau_s'],1.,places=14)

    def test_20_observed_triplet_lifetime_and_A(self):
        a=self.result['measured_radiative_lifetimes']['LiII_triplet_M1']
        self.assertEqual(a['tau_s'],52.2)
        self.assertAlmostEqual(a['A_per_s']*a['tau_s'],1.,places=14)

    def test_21_small_H_tau_only_frozen_epoch_diagnostic(self):
        self.assertLess(self.result['measured_radiative_lifetimes']['LiII_triplet_M1']['max_H_tau'],1e-12)

    def test_22_every_epoch_baryon_source_positive(self):
        self.assertTrue(all(v['K_events_per_baryon_s']>=0 for v in self.data['epochs']))

    def test_23_no_spin_branch_probability_fabricated(self):
        self.assertEqual(self.result['scientific_scope']['actual_singlet_triplet_branch_probabilities'],'UNBOUND')

    def test_24_thermal_port_is_not_bound(self):
        self.assertEqual(self.result['scientific_scope']['REI_IgmPhotoInput_heat_erg_per_absorber_s'],'UNBOUND')
        self.assertTrue(all(v['photo_thermal_heat_source']=='UNBOUND' for v in self.data['bins']))

    def test_25_no_new_ivs_and_no_canonical_promotion(self):
        self.assertEqual(self.result['counts']['new_IVPs'],0)
        self.assertEqual(self.result['progress']['canonical_physical_delta'],0)

    def test_26_source_sha_negative_control(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip'
            p.write_bytes(mod.ORIGINAL.read_bytes()[:1024])
            with patch.object(mod,'ORIGINAL',p):
                with self.assertRaisesRegex(ValueError,'PR279_ARCHIVE_BYTE_IDENTITY_FAIL'):
                    mod.read_source()

    def test_27_Li1s_isotope_kinematic_origin(self):
        self.assertEqual(self.result['counts']['active_bins_per_isotope'],22)
        self.assertEqual(self.result['counts']['threshold_potential_cells'],25476)

    def test_28_HeII_two_photon_endpoint_support(self):
        e=mod.E_SINGLET_EV-mod.THRESHOLDS_EV['He_II']
        self.assertGreater(e,6.5)
        self.assertLess(e,6.6)

if __name__=='__main__':
    unittest.main(verbosity=2)
