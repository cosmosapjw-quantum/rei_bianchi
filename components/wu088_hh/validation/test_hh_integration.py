"""Independent source, physics and conditioning checks of the merged D/H entry."""

import csv
import hashlib
import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np
from scipy.integrate import solve_ivp

from rei_bianchi.microphysics.hh import charge_exchange_source, savin_rates, trace_step


COMPONENT = Path(__file__).resolve().parents[1]
R51 = COMPONENT / "upstream/research/wu_r51_rei_f05_savin_charge_exchange_20261101"
TABLE = R51 / "sources/SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestMergedSource(unittest.TestCase):
    def test_unchanged_historical_reference(self):
        self.assertEqual(
            hashlib.sha256(TABLE.read_bytes()).hexdigest(),
            "ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8",
        )
        reference = load_module("legacy_r51", R51 / "r51_savin_f05.py")
        with TABLE.open() as stream:
            table = [
                (
                    float(r["T_K"]),
                    float(r["k_forward_cm3_s"]),
                    float(r["k_reverse_cm3_s"]),
                )
                for r in csv.DictReader(stream)
            ]
        for row in table[1:]:
            self.assertEqual(savin_rates(row[0]), row[1:])
        for t in np.geomspace(2.7, 2e5, 301):
            expect = tuple(reference.interp_published(table, t, j) for j in (1, 2))
            np.testing.assert_allclose(savin_rates(t), expect, rtol=8e-15, atol=0)

    def test_extent_energy_and_nuclei(self):
        for densities, sgn in [
            ((0.0, 1.0, 1.0, 0.0), 1),
            ((1.0, 0.0, 0.0, 1.0), -1),
            ((0.0, 0.0, 0.0, 0.0), 0),
        ]:
            d = charge_exchange_source(100.0, *densities)
            self.assertEqual(int(np.sign(d.net_events_cm3_s)), sgn)
            self.assertEqual(d.hi_rate_cm3_s + d.hii_rate_cm3_s, 0.0)
            self.assertEqual(d.di_rate_cm3_s + d.dii_rate_cm3_s, 0.0)
            self.assertEqual(d.dii_rate_cm3_s + d.hii_rate_cm3_s, d.electron_rate_cm3_s)
            self.assertEqual(d.photon_rate_cm3_s, 0.0)
            self.assertEqual(d.gas_power_erg_cm3_s + d.binding_power_erg_cm3_s, 0.0)
            self.assertEqual(int(np.sign(d.gas_power_erg_cm3_s)), -sgn)

    def test_invalid_input_and_saturated_step(self):
        for t in (1.0, 2.69, 2e5 + 1, float("nan")):
            with self.assertRaises(ValueError):
                savin_rates(t)
        for t, n1, n2, n3, n4 in [
            (10.0, -1.0, 0.0, 1.0, 0.0),
            (10.0, 1.0, math.inf, 0.0, 1.0),
        ]:
            with self.assertRaises(ValueError):
                charge_exchange_source(t, n1, n2, n3, n4)
        self.assertEqual(trace_step(0.712, 1e15, 7000.0, 0.0, 0.8), 0.712)
        self.assertEqual(trace_step(0.712, 0.0, 7000.0, 0.1, 0.8), 0.712)
        kf, kr = savin_rates(2.7)
        x = 1e-17
        target = kf * x / (kf * x + kr * (1 - x))
        self.assertEqual(trace_step(1.0, 1e24, 2.7, 1.0, x), target)

    def test_optical_solution_against_native_radau(self):
        model = load_module(
            "tracer_reconstruction", COMPONENT / "analysis/trace_original_axbi.py"
        )
        t = np.array([0.0, 0.8, 1.0])
        a = np.array([0.7, 5.0, 0.22])
        b = np.array([1.8, 0.9, 25.0])
        y, _ = model.propagate_optical(t, a, b, 0.77, 16)
        y0 = 0.77
        for j in range(2):
            dt = t[j + 1] - t[j]

            def rhs(s, state):
                u = (s - t[j]) / dt
                ca = a[j] * (1 - u) + a[j + 1] * u
                cb = b[j] * (1 - u) + b[j + 1] * u
                return ca - (ca + cb) * state

            result = solve_ivp(
                rhs, (t[j], t[j + 1]), [y0], method="Radau", rtol=8e-13, atol=1e-14
            )
            self.assertTrue(result.success)
            y0 = result.y[0, -1]
            self.assertLess(abs(y[j + 1] - y0), 3e-12)


if __name__ == "__main__":
    unittest.main()
