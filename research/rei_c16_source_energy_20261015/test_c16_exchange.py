#!/usr/bin/env python3
"""C16 physical exchange source and actual C15 feedback regression gates."""
from __future__ import annotations
import dataclasses
import math
from pathlib import Path
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from c16_exchange import (
    WorkAuditor,Config,NativeStellarSource,Scenario,ROOT,
    formula_energies, perH_source_balance, flux_reconstruction,
    EV_CM3_TO_PA,START,STOP)
from c15_coupled import Coupled

class OriginalC15ActualConservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=NativeStellarSource.load(Scenario(ROOT),
                       ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
        cls.control=WorkAuditor(Config(nstep=16),cls.source,order=8).run()
        cls.pos=WorkAuditor(Config(legacy_q_for_locked_source=.005,nstep=16),cls.source).run()
    def test_original_C13_native_source_and_scoped_boltzmann(self):
        self.assertEqual(self.source.source_id,"MD14_Z002_FESC_BB50K_13P6_100_V1")
        self.assertEqual(len(self.control["history"]),17)
        self.assertTrue(self.control["numerical"]["coalescence"])
        self.assertLess(self.control["numerical"]["max_photo_energy_ledger_error_eV_perH"],3e-11)
    def test_five_external_UV_CaseA_thermo_binding_reservoir_ledger(self):
        for z in (self.control,self.pos):
            c=z["C16_scoped_open_Q_energy_audit"]
            self.assertLess(c["max_open_source_energy_ledger_abs_eV_perH"],1e-12)
            self.assertGreater(c["actual_stellar_energy_emitted_eV_perH"],.19)
            self.assertGreater(c["actual_CaseA_escaped_energy_eV_perH"],.001)
            self.assertGreater(c["signed_external_net_eV_perH"],.18)
            self.assertGreater(c["observed_ionizing_UV_energy_end_eV_perH"],0)
            self.assertEqual(c["external_Q_is_gravitationally_owned_by_stellar_plus_escaped_radiation"],
                             "NOT_IMPLEMENTED")
    def test_independent_gauss8_shear_pressure_plus_adiabatic_gas_work(self):
        for z in (self.control,self.pos):
            c=z["C16_scoped_open_Q_energy_audit"]
            self.assertEqual(c["number_accepted_source_halfsteps"],32)
            self.assertLess(c["max_independent_GL_photon_pressure_shear_work_error_eV_perH"],2e-14)
            self.assertLess(c["max_independent_GL_pressure_shear_work_error_eV_perH"],2e-13)
            self.assertLess(abs(c["actual_cumulative_pressure_work_eV_perH"]-
                  z["endpoint"]["geometry_work_eV_perH"]),1e-12)
    def test_positive_non_tilt_reflection_has_zero_baryon_momentum_recoil(self):
        for z in (self.control,self.pos):
            c=z["C16_scoped_open_Q_energy_audit"]
            p=c["angular_axis_reflection_source_momentum_dipole"]
            self.assertLess(p["max_ratio_uv_energy_flux_to_energy"],2e-13)
            self.assertLess(p["max_BASS_PSTF_gamma_nu_dipole"],2e-15)
            self.assertEqual(len(c["independent_momentum_checks"]),16)
    def test_dipolar_source_rejected_not_fake_non_tilt_zero_transfer(self):
        # Adversarial positive but asymmetric stellar weights: new mode should
        # require baryon/Einstein recoil, not borrow reflection cancellation.
        w=self.source.weights.copy()
        w*=1+0.03*self.source.mu
        w/=w.sum()
        bad=dataclasses.replace(self.source,weights=w)
        with self.assertRaisesRegex(ValueError,"PHOTON_DIPOLE"):
            WorkAuditor(Config(nstep=8),bad)
    def test_true_c15_source_outcomes_identical_by_adding_only_audit(self):
        cc=Coupled(Config(nstep=16),self.source).run()
        zz=self.control
        for k in ("a","b","Sigma","x_HII","x_HeII","x_HeIII","Tgas_K",
                  "Pi_Einstein_shear_Pa","photon_U_eV_perH","thomson_tau"):
            self.assertEqual(cc["endpoint"][k],zz["endpoint"][k],k)
        self.assertEqual(cc["numerical"]["max_photo_energy_ledger_error_eV_perH"],
                         zz["numerical"]["max_photo_energy_ledger_error_eV_perH"])
    def test_Gauss4_8_16_actual_source_pressure_work_refinement(self):
        q=.005
        r=[]
        for order in (4,8,16):
            z=WorkAuditor(Config(nstep=8,legacy_q_for_locked_source=q),
                          self.source,order=order).run()
            r.append((z["endpoint"]["Sigma"],z["C16_scoped_open_Q_energy_audit"]["max_independent_GL_pressure_shear_work_error_eV_perH"]))
        self.assertEqual(r[0][0],r[1][0])
        self.assertEqual(r[1][0],r[2][0])
        self.assertLess(max(p for _,p in r),3e-12)
    def test_open_energy_source_power_dimensions_real_data(self):
        x=self.control["C16_scoped_open_Q_energy_audit"]["explicit_source_exchange_flux"]
        self.assertEqual(len(x),16)
        self.assertTrue(all(v["dt_s"]>0 and v["external_power_J_m3_s"]>0 for v in x))
        self.assertTrue(all(np.isfinite(v["open_external_Q_over_H_rho_rad"]) for v in x))
        self.assertTrue(all(0<v["open_net_external_energy_in_eV_perH"]<.03 for v in x))
    def test_schema_protects_full_covariant_admission(self):
        s=self.control["C16_scoped_open_Q_energy_audit"]
        self.assertEqual(s["scientific_admission"],"NOT_ISSUED")
        self.assertEqual(self.control["physical_gap"]["scientific_admission"],"NOT_ISSUED")
        self.assertIn("NOT_CLOSED",self.control["physical_gap"]["global_einstein_source_conservation"])

if __name__=="__main__":
    unittest.main(verbosity=2)
