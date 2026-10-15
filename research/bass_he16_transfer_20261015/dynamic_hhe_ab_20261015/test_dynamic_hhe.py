"""Regression and falsification controls for minimal dynamic H/He A/B output."""
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from analyze_dynamic import (load,analyze,check_gas,parity,
                             F_HE,T0,N0,KB_EV_PER_K)

ROOT=Path(__file__).resolve().parent
R=ROOT/"results"
Q=(-.005,0.,.005)


def case(all_rows,q,eta,index,steps):
    return all_rows[(q,eta,index,steps)]


class TestDynamicHHe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load(R/"FINAL_SERIAL.csv")
        cls.result=analyze(R/"FINAL_SERIAL.csv",R/"FINAL_PARALLEL2.csv")

    def test_81_matched_cases_and_162_photon_lanes(self):
        self.assertEqual(len(self.data),81)
        self.assertEqual(self.result["cases"],81)
        self.assertEqual(self.result["lane_records"],162)

    def test_serial_parallel_physics_fields_identical(self):
        self.assertTrue(parity(R/"FINAL_SERIAL.csv",R/"FINAL_PARALLEL2.csv"))

    def test_photo_only_gas_census_every_lane(self):
        for x in self.data.values():
            for row in x.values():
                self.assertTrue(check_gas(row))

    def test_zero_opacity_keeps_gas_fractions(self):
        for q in Q:
            for idx in (5,32,33):
                for n in (1,16,128):
                    for arm,row in case(self.data,q,0,idx,n).items():
                        self.assertEqual(float(row["x_HII_final"]),1.)
                        self.assertEqual(float(row["x_HeII_final"]),0.)
                        self.assertEqual(float(row["x_HeIII_final"]),1.)
                        self.assertEqual(float(row["gas_deposited_photoheat_eV_per_H"]),0.)

    def test_transparent_temperature_matches_adiabatic_exact_solution(self):
        expected=T0*(20.8/21.)**2
        for arm,row in case(self.data,0.,0,32,128).items():
            self.assertLess(abs(float(row["Tgas_final_K"])-expected),2e-12)

    def test_subthreshold_dynamic_helium_ab(self):
        for q in Q:
            for eta in (1e-5,1e-4):
                a=case(self.data,q,eta,32,128)["PROJECTED"]
                b=case(self.data,q,eta,32,128)["COVARIANT"]
                self.assertGreater(float(a["HeII_absorbed_fraction"]),.002)
                self.assertEqual(float(b["HeII_absorbed_fraction"]),0.)
                self.assertGreater(float(a["x_HeIII_final"])-float(b["x_HeIII_final"]),1e-8)

    def test_signed_refinement_persistence(self):
        for n in (1,16,128):
            arms=case(self.data,0.,1e-5,32,n)
            a=arms["PROJECTED"];b=arms["COVARIANT"]
            self.assertGreater(float(a["HeII_absorbed_fraction"]),.002)
            self.assertEqual(float(b["HeII_absorbed_fraction"]),0.)

    def test_heii_true_above_threshold_control(self):
        for q in Q:
            for n in (1,16,128):
                for r in case(self.data,q,1e-5,33,n).values():
                    self.assertGreater(float(r["HeII_absorbed_fraction"]),0.)

    def test_hi_only_subthreshold_Heii_negative_control(self):
        for q in Q:
            for eta in (0,1e-5,1e-4):
                for r in case(self.data,q,eta,5,128).values():
                    self.assertEqual(float(r["HeII_absorbed_fraction"]),0.)

    def test_helium_nuclei_inventory(self):
        for r in (row for arms in self.data.values() for row in arms.values()):
            y=float(r["x_HeII_final"]);z=float(r["x_HeIII_final"])
            self.assertGreaterEqual(1-y-z,-1e-12)
            he_sum=F_HE*(1-y-z)+F_HE*y+F_HE*z
            self.assertLess(abs(he_sum-F_HE),1e-15)

    def test_each_heii_event_creates_one_HeIII_and_one_electron(self):
        for q in Q:
            for eta in (1e-5,1e-4):
                for n in (1,16,128):
                    for r in case(self.data,q,eta,32,n).values():
                        events=float(r["HeII_absorbed_fraction"])*N0
                        heIII_gain=(float(r["x_HeIII_final"])-(1-eta))*F_HE
                        self.assertLess(abs(events-heIII_gain),5e-16)

    def test_all_thermal_and_photon_ledgers_are_closed(self):
        max_photon_n=0;max_photon_e=0;max_gas_u=0;max_charge=0
        for arms in self.data.values():
            for row in arms.values():
                max_photon_n=max(max_photon_n,abs(float(row["photon_number_residual_relative"])))
                max_photon_e=max(max_photon_e,abs(float(row["photon_energy_residual_relative"])))
                max_gas_u=max(max_gas_u,abs(float(row["gas_thermal_residual_eV_per_H"])))
                max_charge=max(max_charge,abs(float(row["gas_max_charge_residual"])))
        self.assertLess(max_photon_n,3e-15)
        self.assertLess(max_photon_e,3e-15)
        self.assertLess(max_gas_u,5e-18)
        self.assertLess(max_charge,4e-16)

    def test_gas_ionization_failure_on_incomplete_source(self):
        with TemporaryDirectory() as tmp:
            output=Path(tmp)/"short.csv"
            lines=(R/"FINAL_SERIAL.csv").read_text().splitlines()
            output.write_text("\n".join(lines[:-1])+"\n")
            with self.assertRaises(ValueError):
                load(output)

    def test_sample_is_non_authoritative(self):
        self.assertIn("PHOTO_ONLY",self.result["status"])
        self.assertEqual(self.result["scientific_admission"],"HOLD_FULL_EOR_NATIVE")


    def test_source_manifest_source_epoch_and_mode(self):
        m=json.loads((ROOT/"DELIVERY_EVIDENCE_MANIFEST.json").read_text())
        self.assertEqual(m["n_physical_cases"],81)
        self.assertEqual(m["n_photon_transport_records"],162)
        self.assertFalse(m["full_compiled_source_epochs_identical"])
        self.assertEqual(m["test_passed_atomic_transport_source_function_count"],12)
        self.assertEqual(m["gas_ode_photoionization_only"],True)
        self.assertEqual(m["original_full_eor_native_replayed"],False)

    def test_all_committed_source_inputs_match_sha256_manifest(self):
        import hashlib
        m=json.loads((ROOT/"DELIVERY_EVIDENCE_MANIFEST.json").read_text())
        for row in m["files"]:
            f=ROOT/row["relative_path"]
            self.assertTrue(f.is_file())
            self.assertEqual(f.stat().st_size,row["bytes"])
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),row["sha256"])


if __name__=="__main__":unittest.main()
