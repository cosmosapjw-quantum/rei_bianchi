"""Source-specific 192-interval quantitative and adversarial checks."""
from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('cross_source',ROOT/'code'/'build_joint.py')
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class CrossSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result,cls.summary=MOD.compute()
        cls.h=MOD.verified_read('PR298_HYBRID_FJ_THERMAL_193.csv')
        cls.t=MOD.verified_read('PR299_FROZEN_SOURCE_TANGENCY_193.csv')
        cls.p=MOD.verified_read('PR297_ALL_EPOCH_CAUSAL_ARRIVAL_192.csv')
        cls.s=MOD.verified_read('PR300_FS2010_SELECTED_ARRIVAL_192.csv')
    def test_01_four_verified_real_source_csv(self):
        self.assertEqual([len(self.h),len(self.t),len(self.p),len(self.s)],[193,193,192,192])
        self.assertEqual(len(MOD.SOURCE_LOCK),4)
    def test_02_actual_same_redshift_grid(self):
        np.testing.assert_allclose(self.h.z,self.t.z,rtol=0,atol=1e-12)
        np.testing.assert_allclose(self.h.z.iloc[:-1],self.p.z_high,rtol=0,atol=1e-12)
        np.testing.assert_allclose(self.p.z_high,self.s.z_high,rtol=0,atol=1e-12)
        np.testing.assert_allclose(self.p.z_low,self.s.z_low,rtol=0,atol=1e-12)
    def test_03_exact_archived_proper_time_agreement(self):
        dt=self.p.proper_interval_s.to_numpy()
        dt_h=np.diff(self.h.elapsed_s.to_numpy())
        self.assertLess(np.max(abs(dt_h-dt)/dt),1.3e-14)
        self.assertTrue(np.all(dt>0))
    def test_04_midpoint_quadrature_is_not_exact_clock_identity(self):
        defect=np.abs(self.result.clock_midpoint_Hdt_dx_minus_1.to_numpy())
        self.assertGreater(defect.max(),1e-7)
        self.assertLess(defect.max(),4e-5)
    def test_05_unselected_energy_is_nonnegative_with_frozen_kernel(self):
        unselected=self.p.conditional_all_species_primary_e_eV_per_b.to_numpy()-self.s.total_primary_e_eV_per_b.to_numpy()
        self.assertGreaterEqual(unselected.min(),-1e-28)
        self.assertAlmostEqual(unselected.sum(),3.345307698030213e-13,delta=2e-25)
    def test_06_first_generation_upper_is_not_total_heat_upper(self):
        low=self.result.conditional_terminal_selected_low_e_eV_per_b.to_numpy()
        narrow=self.result.conditional_terminal_low_e_upper_eV_per_b.to_numpy()
        total=self.result.conditional_total_primary_energy_all_eV_per_b.to_numpy()
        self.assertTrue(np.all(low>=0) and np.all(narrow>=low-1e-30) and np.all(total>=narrow-1e-30))
        self.assertGreater((total-narrow).sum(),0)
        self.assertAlmostEqual(total.sum(),6.749242464433259e-11,delta=4e-23)
    def test_07_original_selected_subthreshold_energy(self):
        e=self.s.FS_low_e_heat_kinematic_eV_per_b.to_numpy()
        self.assertAlmostEqual(e.sum(),8.54068904110878e-12,delta=1e-24)
        np.testing.assert_allclose(e,self.result.conditional_terminal_selected_low_e_eV_per_b,atol=0,rtol=0)
    def test_08_heat_units_using_independent_per_baryon_cv(self):
        i=int(np.argmax(self.result.terminal_Tdot_upper_K_s.to_numpy()))
        e=self.result.conditional_terminal_low_e_upper_eV_per_b.iloc[i]
        cv=self.result.Cv_BASS21_per_baryon_erg_per_K.iloc[i]
        dt=self.result.proper_interval_s.iloc[i]
        self.assertAlmostEqual(e*MOD.EV_ERG/cv/dt,self.result.terminal_Tdot_upper_K_s.iloc[i],delta=1e-36)
    def test_09_temperature_source_is_not_an_evolved_state(self):
        self.assertEqual(self.summary['source_assumptions']['no_new_ivps'],True)
        self.assertEqual(self.summary['admission']['Production'],'HOLD')
        self.assertEqual(self.summary['admission']['native_REI17'],'NOT_RUN')
    def test_10_source_kinematics_and_primary_counts(self):
        parent=self.p[['directwindow_LiII_2E1_HI_counts_upper_per_b','directwindow_LiII_2E1_HeI_counts_upper_per_b','directwindow_LiII_2E1_HeII_counts_upper_per_b']].sum(axis=1).to_numpy()
        out=self.result.conditional_HHe_primary_electrons_per_b.to_numpy()
        self.assertLess(np.max(np.abs(parent-out)),1e-23)
    def test_11_hybrid_source_is_not_duplicate_photon_source(self):
        self.assertGreater(abs(self.summary['electron_counts']['PR299_signed_hybrid_source_electron_exposure_per_b']),1e-4)
        self.assertLess(self.summary['electron_counts']['primary_plus_secondary_upper_per_b'],1e-10)
        self.assertLess(self.summary['electron_counts']['max_ratio_to_PR299_frozen_signed_electron_exposure'],1e-9)
    def test_12_secondary_count_is_a_ceiling_not_measured_yield(self):
        s=self.result.conditional_discrete_H_secondary_selected_upper_per_b.to_numpy()
        b=self.result.conditional_H_secondary_all_upper_per_b.to_numpy()
        self.assertTrue(np.all(s>=0) and np.all(b>=s))
        self.assertIn('NOT admitted',self.summary['source_assumptions']['source_ownership'])
    def test_13_thermal_loading_sign_and_hypothetical_definition(self):
        assert np.all(self.result.hypothetical_instant_electron_loading_Tdot_K_s<=0)
        self.assertGreater(self.summary['thermal']['max_terminal_heat_rate_K_s'],0)
        self.assertLess(self.summary['thermal']['frozen_electron_loading_exposure_K'],0)
    def test_14_integrated_source_exposure_not_actual_temperature(self):
        dt=self.result.proper_interval_s.to_numpy()
        hi=self.result.terminal_Tdot_upper_K_s.to_numpy()
        broad=self.result.conditional_all_primary_to_heat_Tdot_ceiling_K_s.to_numpy()
        self.assertAlmostEqual(np.dot(dt,hi),self.summary['thermal']['frozen_terminal_upper_Tdot_exposure_K'],delta=1e-20)
        self.assertGreater(np.dot(dt,broad),np.dot(dt,hi))
        self.assertTrue(np.all(broad>=hi))
    def test_15_tampered_source_file_rejected(self):
        original=MOD.SRC
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); name='PR297_ALL_EPOCH_CAUSAL_ARRIVAL_192.csv'
            data=(original/name).read_bytes()
            (t/name).write_bytes(data+b'\nFAKE_UNAUTHORIZED_ROW\n')
            try:
                MOD.SRC=t
                with self.assertRaisesRegex(AssertionError,'SOURCE SHA mismatch'):
                    MOD.verified_read(name)
            finally:
                MOD.SRC=original
    def test_16_incompatible_clock_negative_control(self):
        dt=self.p.proper_interval_s.to_numpy().copy()
        modified=dt.copy();modified[37]*=1.001
        true_dt=np.diff(self.h.elapsed_s.to_numpy())
        self.assertGreater(np.max(np.abs(modified-true_dt)/dt),1e-3-1e-12)
    def test_17_dimensionless_energy_partition(self):
        sm=self.summary['energies']; broad=sm['PR297_all_primary_kin_eV_per_b']
        self.assertGreater(broad,sm['FS_all_low_upper_eV_per_b'])
        self.assertAlmostEqual(sm['FS_selected_high_e_eV_per_b']+sm['FS_selected_low_kin_eV_per_b']+sm['FS_unselected_primary_e_upper_eV_per_b'],broad,delta=1e-24)
    def test_18_weak_jacobian_result_is_preserved_as_parent_not_overwritten(self):
        # No new F/J source or neutron column is manufactured here. Read-only PR298/299 source.
        self.assertGreater(self.h.weak_beta_s.min(),0)
        self.assertAlmostEqual(self.h.weak_beta_s.iloc[0],1/878.4,delta=1e-15)
        self.assertEqual(self.summary['source_prs']['hybrid'],298)
    def test_19_no_overinterpretation_of_thermal_endpoints(self):
        self.assertIn('future cascade deliberately outside',self.summary['source_assumptions']['thermalization'])
        self.assertIn('FIRST-GENERATION',self.summary['source_assumptions']['upper_scope'])
        self.assertEqual(len(self.result),192)

if __name__=='__main__': unittest.main(verbosity=2)