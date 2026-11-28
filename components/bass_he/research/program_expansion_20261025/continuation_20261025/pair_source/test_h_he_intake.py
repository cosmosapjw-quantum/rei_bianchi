"""Source-contract and exact-identity tests only; no physical fit evaluation."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h_he_intake import (load_h_he_fit_input, relative_temperature,
                         conditional_h_he_moments, KINDS)


class HHeIntakeContracts(unittest.TestCase):
    def test_exact_source_and_two_inherited_rows(self):
        p = load_h_he_fit_input()
        self.assertEqual(set(p["fit_rows"]), set(KINDS))
        inherited = [k for k, v in p["fit_rows"].items()
                     if v["admission"] == "INHERITED_SCOPED_TRANSPORT_RESULT_REUSED"]
        self.assertEqual(set(inherited), {"Q11", "Q22"})
        self.assertFalse(p["differential_cross_section_supplied"])
        self.assertFalse(p["physical_provider_admitted"])

    def test_temperature_domain_endpoints(self):
        for t in (50.0, 50000.0):
            self.assertEqual(relative_temperature(t, t, 1.0, 4.0), t)
        for t in (49.0, 50001.0, float("nan"), float("inf"), True, -1.0):
            with self.assertRaises(ValueError):
                relative_temperature(t, t, 1.0, 4.0)

    def test_reduced_temperature_and_interchange(self):
        # Synthetic exact rational controls, not a source-evaluation grid.
        self.assertEqual(relative_temperature(100.0, 200.0, 1.0, 4.0), 120.0)
        self.assertEqual(relative_temperature(200.0, 100.0, 4.0, 1.0), 120.0)

    def _arguments(self):
        # Unit-test numbers and Q11 have no physical supplier admission.
        return dict(T_H_K=100.0, T_He_K=100.0, n_H_m3=1.0, n_He_m3=1.0,
                    mass_H_kg=1.0, mass_He_kg=4.0, q11_m2=1.0,
                    q11_temperature_K=100.0, q11_value_evidence="synthetic-test",
                    mass_binding_evidence="synthetic-test")

    def test_equilibrium_and_vacuum_exact_zero(self):
        p = conditional_h_he_moments(**self._arguments())
        self.assertEqual(p.heat_a_W_m3, 0.0)
        self.assertEqual(p.heat_b_W_m3, 0.0)
        self.assertFalse(p.physical_provider_admitted)
        args = self._arguments()
        args["n_H_m3"] = 0.0
        q = conditional_h_he_moments(**args)
        self.assertEqual(q.thermal_conductance_W_m3_K, 0.0)
        self.assertEqual(q.linear_drag_kg_m3_s, 0.0)

    def test_negative_inputs_and_wrong_source_temperature_rejected(self):
        for field, value in (("n_H_m3", -1.0), ("mass_He_kg", 0.0),
                             ("q11_m2", -1.0), ("q11_temperature_K", 101.0),
                             ("q11_value_evidence", ""),
                             ("mass_binding_evidence", "")):
            args = self._arguments()
            args[field] = value
            with self.assertRaises(ValueError, msg=field):
                conditional_h_he_moments(**args)


if __name__ == "__main__":
    unittest.main()

