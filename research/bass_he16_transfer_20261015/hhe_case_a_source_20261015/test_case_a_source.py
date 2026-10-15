"""Measured source-linked Grackle Case-A reionization microphysics experiments."""
import json
import unittest
from pathlib import Path
from analyze_case_a import (read,parity,analyze,check_row,F_HE,N0,CHI)

HERE=Path(__file__).resolve().parent
RES=HERE/"results"
def get(rows,q=0.,eta=0.,idx=32,n=128,arm="PROJECTED"):
    return rows[(q,eta,idx,n)][arm]

class OriginalNativeCaseATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read(RES/"CASE_A_SERIAL.csv")
        cls.analysis=analyze(RES/"CASE_A_SERIAL.csv",RES/"CASE_A_PARALLEL.csv")
        cls.half=read(RES/"CASE_A_HALF_MICRO.csv")
        cls.source=json.loads((HERE/"SOURCE_RATE_SURFACE_IDENTITY.json").read_text())

    def test_all_54_paired_source_cases_are_present(self):
        self.assertEqual(len(self.data),54)
        self.assertEqual(self.analysis["physical_cases"],54)
        self.assertEqual(self.analysis["individual_lanes"],108)

    def test_parallel_and_serial_source_physics_byte_identical(self):
        self.assertTrue(parity(RES/"CASE_A_SERIAL.csv",RES/"CASE_A_PARALLEL.csv"))

    def test_half_micro_stencil_same_physics_configurations(self):
        self.assertEqual(self.data.keys(),self.half.keys())
        for key in self.data:
            for arm in self.data[key]:
                for field in ("q_ref","eta_initial","energy_index","substeps","transport","initial_energy_eV"):
                    self.assertEqual(self.data[key][arm][field],self.half[key][arm][field])

    def test_all_108_source_ledgers_close_with_boundary(self):
        for pair in self.data.values():
            for row in pair.values():
                e=check_row(row)
                self.assertLess(e["charge_source_abs"],1e-13)
                self.assertLess(e["atomic_binding_residual_eV_per_H"],3e-12)
                self.assertLess(e["native_micro_energy_residual_eV_per_H"],3e-12)
                self.assertLess(e["thermal_energy_residual_eV_per_H"],3e-14)
                self.assertIsNotNone(e["optional_full_energy_residual_eV_per_H"])
                self.assertLess(e["optional_full_energy_residual_eV_per_H"],3e-12)

    def test_low_temperature_recombination_event_is_active(self):
        for q in (-.005,0.,.005):
            for arm in ("PROJECTED","COVARIANT"):
                row=get(self.data,q,0.,32,1,arm)
                self.assertGreater(float(row["RR_HII_per_H"]),0.)
                self.assertGreater(float(row["RR_HeIII_per_H"]),0.)
                self.assertEqual(float(row["DR_HeII_per_H"]),0.)
                self.assertLess(float(row["x_HeIII_final"]),1.)

    def test_one_step_zero_initial_HeII_has_no_photo_HeII_events(self):
        a=get(self.data,n=1)
        b=get(self.data,n=1,arm="COVARIANT")
        self.assertEqual(float(a["HeII_absorbed_fraction"]),0.)
        self.assertEqual(float(b["HeII_absorbed_fraction"]),0.)
        self.assertEqual(a["x_HeIII_final"],b["x_HeIII_final"])

    def test_recombination_creates_heii_ghost_photon_reactions_at_substeps(self):
        for q in (-.005,0.,.005):
            for eta in (0.,1e-5):
                for n in (16,128):
                    a=get(self.data,q,eta,32,n)
                    b=get(self.data,q,eta,32,n,"COVARIANT")
                    self.assertGreater(float(a["HeII_absorbed_fraction"]),.6)
                    self.assertEqual(float(b["HeII_absorbed_fraction"]),0.)
                    self.assertLess(float(a["x_HeIII_final"])-float(b["x_HeIII_final"]),-3e-5)

    def test_subthreshold_hi_packet_cannot_ionize_heii(self):
        for q in (-.005,0.,.005):
            for n in (16,128):
                self.assertEqual(float(get(self.data,q,0.,5,n)["HeII_absorbed_fraction"]),0.)
                self.assertEqual(float(get(self.data,q,0.,5,n,"COVARIANT")["HeII_absorbed_fraction"]),0.)

    def test_true_above_threshold_heii_is_positive_in_both(self):
        for q in (-.005,0.,.005):
            for n in (16,128):
                self.assertGreater(float(get(self.data,q,1e-5,33,n)["HeII_absorbed_fraction"]),0.)
                self.assertGreater(float(get(self.data,q,1e-5,33,n,"COVARIANT")["HeII_absorbed_fraction"]),0.)

    def test_initial_eta_zero_does_not_require_helium_as_absorber_forever(self):
        # Original Case-A source builds HeII by recombination. Starting eta=0
        # does not create an always-transparent gas. This is intentional.
        row=get(self.data,0.,0.,32,128)
        self.assertGreater(float(row["micro_substeps"]),100)
        self.assertGreater(float(row["RR_HeIII_per_H"]),0.025)
        self.assertGreater(float(row["HeII_absorbed_fraction"]),0.5)

    def test_micro_refinement_keeps_ghost_signal(self):
        for q in (-.005,0.,.005):
            for eta in (0.,1e-5):
                a=get(self.data,q,eta,32,128)
                b=get(self.data,q,eta,32,128,"COVARIANT")
                c=get(self.half,q,eta,32,128)
                d=get(self.half,q,eta,32,128,"COVARIANT")
                v=float(a["x_HeIII_final"])-float(b["x_HeIII_final"])
                w=float(c["x_HeIII_final"])-float(d["x_HeIII_final"])
                self.assertGreater(abs(w),4e-5)
                self.assertLess(abs(v-w)/abs(w),1e-4)
                self.assertGreater(int(c["micro_substeps"]),int(a["micro_substeps"]))

    def test_recombination_thermal_cooling_and_cmb_source_present(self):
        for arm in ("PROJECTED","COVARIANT"):
            r=get(self.data,0.,0.,32,128,arm)
            self.assertLess(float(r["micro_thermal_eV_per_H"]),0.)
            self.assertLess(float(r["micro_binding_eV_per_H"]),0.)
            self.assertGreater(float(r["micro_escape_eV_per_H"]),0.)
            self.assertGreater(float(r["micro_cmb_to_gas_eV_per_H"]),0.)

    def test_native_rate_functions_exactly_bound_between_source_epochs(self):
        self.assertEqual(self.source["source_function_count"],7)
        self.assertTrue(self.source["all_seven_tested_function_bodies_equal"])
        self.assertFalse(self.source["full_source_epochs_identical"])
        surfaces={x["function"] for x in self.source["function_surfaces"]}
        for s in ("pub fn igm_rates(","pub fn igm_point_rhs(","pub fn rates(self","pub fn point("):
            self.assertIn(s,surfaces)

if __name__=="__main__":unittest.main()
