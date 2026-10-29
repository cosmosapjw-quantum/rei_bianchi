import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.integrate import cumulative_simpson, cumulative_trapezoid

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('energy_atlas',ROOT/'code/energy_atlas.py')
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)

class TestSourceEnergy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary,cls.epoch,cls.events,cls.spec,cls.arr=p.compute()
    def test_01_original_source_identity(self):
        self.assertEqual(self.summary['source']['donor_archive_sha256'],p.DONOR_SHA)
        self.assertEqual(self.summary['source']['trajectory_sha256'],p.TRAJ_SHA)
        self.assertEqual(self.summary['source']['network_sha256'],'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80')
    def test_02_bad_hash_fails(self):
        with patch.object(p,'DONOR_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'DONOR_ZIP_SHA_MISMATCH'):
                with __import__('tempfile').TemporaryDirectory() as td:
                    p.source_owner(Path(td))
    def test_03_expected_epoch_count(self):self.assertEqual(len(self.epoch),193)
    def test_04_expected_species_count(self):self.assertEqual(len(self.events),193*13)
    def test_05_expected_energy_bin_count(self):self.assertEqual(len(self.spec),193*71)
    def test_06_gamma_source_mirror(self):self.assertLess(self.summary['identities']['max_abs_native']['source_gamma_s'],1e-24)
    def test_07_native_absorbed(self):self.assertLess(self.summary['identities']['max_relative_native']['abs'],2e-14)
    def test_08_native_primary(self):self.assertLess(self.summary['identities']['max_relative_native']['primary'],2e-14)
    def test_09_native_core(self):self.assertLess(self.summary['identities']['max_relative_native']['core'],2e-14)
    def test_10_native_li_1s_counts(self):self.assertLess(self.summary['identities']['max_abs_native']['inner_count_m3_s'],1e-30)
    def test_11_physical_nonnegative_absorption(self):self.assertGreaterEqual(min(r['absorbed_eV_per_baryon_s'] for r in self.events),0.)
    def test_12_physical_nonnegative_ion(self):self.assertGreaterEqual(min(r['ion_threshold_eV_per_baryon_s'] for r in self.events),0.)
    def test_13_physical_nonnegative_core(self):self.assertGreaterEqual(min(r['unresolved_core_eV_per_baryon_s'] for r in self.events),0.)
    def test_14_site_branch_equality(self):
        for r in self.events:
            a=r['absorbed_eV_per_baryon_s'];b=r['ion_threshold_eV_per_baryon_s'];c=r['primary_electron_eV_per_baryon_s'];d=r['unresolved_core_eV_per_baryon_s']
            self.assertLessEqual(abs(a-b-c-d),2e-14*max(a,b,c,d,1e-75))
    def test_15_epoch_branch_equality(self):
        for r in self.epoch:
            a=r['absorption_eV_per_baryon_s'];b=r['ionization_threshold_eV_per_baryon_s'];c=r['primary_electron_eV_per_baryon_s'];d=r['unresolved_core_eV_per_baryon_s']
            self.assertLessEqual(abs(a-b-c-d),2e-14*max(a,1e-75))
    def test_16_spectral_branch_equality(self):
        for r in self.spec:
            a=r['absorption_W_m3'];b=r['ionization_threshold_W_m3'];c=r['primary_electron_W_m3'];d=r['unresolved_core_W_m3']
            self.assertLessEqual(abs(a-b-c-d),2e-14*max(a,1e-85))
    def test_17_site_records_epoch_aggregation(self):
        for t in (0,1,64,128,192):
            sub=self.events[t*13:(t+1)*13]
            self.assertAlmostEqual(sum(r['absorbed_eV_per_baryon_s'] for r in sub)/self.epoch[t]['absorption_eV_per_baryon_s'],1.,places=13)
    def test_18_spectral_records_epoch_aggregation(self):
        for t in (1,71,192):
            spec=self.spec[t*71:(t+1)*71]
            a=sum(r['absorption_W_m3'] for r in spec)
            b=self.epoch[t]['absorption_eV_per_baryon_s']*self.epoch[t]['nb_m3']*p.EV_J
            self.assertAlmostEqual(a/b,1.,places=13)
    def test_19_Li_isotopes_only_core(self):
        nonli=[r for r in self.events if r['source_index'] not in (13,17)]
        self.assertTrue(all(r['Li_1s_event_per_baryon_s']==0. for r in nonli))
        self.assertTrue(all(r['unresolved_core_eV_per_baryon_s']==0. for r in nonli))
    def test_20_Li_core_energy_per_event(self):
        for r in self.events:
            if r['Li_1s_event_per_baryon_s']>0:
                self.assertAlmostEqual(r['unresolved_core_eV_per_baryon_s']/r['Li_1s_event_per_baryon_s'],p.LI_CORE_E,places=12)
    def test_21_core_is_nonzero_but_tiny_globally(self):
        exposures=self.summary['exposures']
        self.assertGreater(exposures['core_eV'],0)
        self.assertLess(exposures['core_eV']/exposures['abs_eV'],1e-9)
    def test_22_sampled_grid_exposure(self):
        x=self.arr['x'];H=self.arr['H_s'];a=self.arr['total_abs_eV']
        oracle=float(cumulative_simpson(a/H,x=x,initial=0)[-1]);self.assertAlmostEqual(oracle,self.summary['exposures']['abs_eV'],places=11)
    def test_23_separate_integration_quadratures(self):
        x=self.arr['x'];H=self.arr['H_s'];a=self.arr['total_abs_eV'];t=float(cumulative_trapezoid(a/H,x=x,initial=0)[-1]);self.assertGreater(t,0)
    def test_24_photo_event_exposure_reused(self):
        self.assertAlmostEqual(self.summary['exposures']['events'],4.986531593057092,places=11)
    def test_25_photon_flux_nonnegative(self):self.assertGreaterEqual(min(r['photon_flux_m2_s'] for r in self.spec),0)
    def test_26_no_evolving_photon_source(self):self.assertFalse(self.summary['holds']['radiation_photon_evolution'])
    def test_27_no_unsourced_heating_promotion(self):self.assertFalse(self.summary['holds']['photo_energy_is_gas_heat'])
    def test_28_no_ivp(self):self.assertEqual(self.summary['counts']['new_IVPs'],0)
    def test_29_holds_dag(self):
        h=self.summary['holds'];self.assertEqual((h['working_DAG'],h['central_DAG'],h['physical_fast'],h['F4'],h['L4_ready']),('33/88','28/88','4/7','PARTIAL',False))
    def test_30_actual_species_indices(self):self.assertEqual(self.arr['site_indices'].tolist(),[1,3,5,7,8,10,11,13,14,15,17,18,19])
    def test_31_source_photon_bins(self):self.assertEqual(self.arr['photon_energy_eV'].shape,(71,))
    def test_32_no_zero_temperature(self):self.assertTrue(np.all(self.arr['temperature_K']>0))
    def test_33_no_zero_H(self):self.assertTrue(np.all(self.arr['H_s']>0))
    def test_34_helium_heating_not_assumed(self):self.assertFalse(self.summary['holds']['secondary_photoelectron_energy_deposition'])
    def test_35_monotone_original_x(self):self.assertTrue(np.all(np.diff(self.arr['x'])>0))
    def test_36_bin_energy_threshold(self):
        self.assertGreater(float(self.arr['photon_energy_eV'].min()),5.0)
        self.assertLess(float(self.arr['photon_energy_eV'].max()),200.)
    def test_37_sharp_Li_core_source_identity(self):
        self.assertAlmostEqual(self.summary['exposures']['core_eV']/self.summary['exposures']['inner_events'],p.LI_CORE_E,places=11)
    def test_38_ion_energy_lower_than_abs(self):self.assertGreater(self.summary['exposures']['abs_eV'],self.summary['exposures']['ion_eV'])
    def test_39_primary_energy_fraction(self):self.assertTrue(all(0<r['primary_fraction_of_abs']<1 for r in self.epoch[1:]))
    def test_40_li_photo_edges_positive(self):self.assertTrue(all(r['threshold_eV']>0 for r in self.events))

if __name__=='__main__':unittest.main()
