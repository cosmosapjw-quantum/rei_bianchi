"""Independent manufactured and native-byte checks for HM12 intake.

Run: python -m unittest discover -s research/physical_provider_20261010 -p test_hm12_data.py -v
The Gaussian-quadrature reference reads raw native rows independently; it shares
the declared PWL interpolation, but not the analytic moment implementation.
These are intake/interpolation checks, not validation of HM12's physical model.
"""

import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from hm12_data import (C_CM_S, EV_ERG, H_ERG_S, HC_EV_ANGSTROM, MPC_CM,
                       HM12Table, load_hm12)


def manufactured(energies, values, kind="uvb"):
    energies = np.array(energies, dtype=float)
    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = np.stack([values, 2.0 * values], axis=1)
    return HM12Table(kind, np.array([0.0, 2.0]), HC_EV_ANGSTROM / energies[::-1], values[::-1])


class ManufacturedChecks(unittest.TestCase):
    def test_native_values_and_bilinear_positive_interpolation(self):
        table = manufactured([1, 2, 8], [0, 2, 4])
        np.testing.assert_allclose(table.values([1, 2, 8], 0), [0, 2, 4], rtol=1e-15, atol=0)
        self.assertAlmostEqual(table.values(math.sqrt(2), 1), 1.5)
        self.assertAlmostEqual(table.values(4, 1), 4.5)
        self.assertEqual(table.values(1, 1), 0.0)

    def test_duplicate_jump_is_not_averaged(self):
        table = manufactured([1, 2, 2, 4], [1, 2, 7, 9])
        self.assertEqual(table.values(2, 0), 7)
        self.assertEqual(table.values(2, 0, side="left"), 2)
        self.assertAlmostEqual(table.values(math.sqrt(2), 0), 1.5)
        self.assertAlmostEqual(table.values(math.sqrt(8), 0), 8.0)
        self.assertAlmostEqual(table.moment(1, 4, 0), 9.5 * math.log(2), places=13)
        self.assertAlmostEqual(sum(table.group_moments([1, 2, 4], 0)), table.moment(1, 4, 0), places=13)

    def test_analytic_constant_moments_and_narrow_intervals(self):
        table = manufactured([1, 2, 10], [3, 3, 3])
        for lo, hi in ((1.3, 8.7), (2, 2 * (1 + 1e-8))):
            for power in (0, 1e-9, 1, -3, 5):
                expected = (3 * math.log(hi / lo) if power == 0 else
                            3 * (lo / 2.5) ** power * math.expm1(power * math.log(hi / lo)) / power)
                got = table.moment(lo, hi, 0, power=power, reference_eV=2.5)
                self.assertAlmostEqual(got / expected, 1.0, places=12)

    def test_linear_ordinate_exact_primitive(self):
        table = manufactured([1, math.e, math.e ** 2], [2, 5, 8])
        # F=2+3x, x=ln E, integral F exp(x) dx = exp(x)(3x-1).
        expected = math.exp(1.7) * (3 * 1.7 - 1) - math.exp(.2) * (3 * .2 - 1)
        self.assertAlmostEqual(table.moment(math.exp(.2), math.exp(1.7), 0, power=1) / expected, 1, places=13)

    def test_photon_units_and_ic_source_firewall(self):
        uvb = manufactured([1, 2], [1, 1])
        source = manufactured([1, 2], [1, 1], "emissivity")
        self.assertAlmostEqual(uvb.photon_number_log(1.5, 0) * C_CM_S * H_ERG_S / (4 * math.pi), 1)
        self.assertAlmostEqual(source.photon_emission_log(1.5, 2) * MPC_CM ** 3 * H_ERG_S / 27, 2)
        self.assertAlmostEqual(uvb.moment(1, 2, 0, power=1, proper_photons=True) * EV_ERG,
                               4 * math.pi * EV_ERG / (C_CM_S * H_ERG_S), delta=1e-15)
        with self.assertRaises(ValueError):
            uvb.photon_emission_log(1.5, 0)
        with self.assertRaises(ValueError):
            source.photon_number_log(1.5, 0)

    def test_extrapolation_invalid_inputs_and_read_only_data(self):
        table = manufactured([1, 2, 4], [1, 2, 3])
        for energy, z in ((.9, 1), (4.1, 1), (2, -.1), (2, 2.1), (math.nan, 1), (2, math.nan)):
            with self.assertRaises(ValueError):
                table.values(energy, z)
        with self.assertRaises(ValueError):
            table.moment(2, 1, 0)
        with self.assertRaises(ValueError):
            table.group_moments([1, 3, 2], 0)
        with self.assertRaises(ValueError):
            table.spectra[0, 0] = 3
        with self.assertRaises(ValueError):
            manufactured([1, 2], [1, -1])

    def test_read_refuses_corruption_and_wrong_unit_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.out"
            path.write_text("# ergs/s/cm^2/Hz/sr\n0 2\n1 2 3\n2 3 4\n")
            with self.assertRaises(ValueError):
                HM12Table.read(path, "uvb", expected_sha256="0" * 64)
            with self.assertRaises(ValueError):
                HM12Table.read(path, "emissivity")
            path.write_text("# ergs/s/cm^2/Hz/sr\n0 2\n1 2 junk\n2 3 4\n")
            with self.assertRaisesRegex(ValueError, "Invalid numeric field"):
                HM12Table.read(path, "uvb")


class NativeSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = load_hm12()

    def test_actual_shape_hashes_zeros_and_distinct_grids(self):
        uvb, source = self.tables["uvb"], self.tables["emissivity"]
        self.assertEqual(uvb.spectra.shape, (575, 60))
        self.assertEqual(source.spectra.shape, (378, 60))
        self.assertEqual(uvb.source_sha256, "a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc")
        self.assertEqual(source.source_sha256, "88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b")
        self.assertEqual(uvb.provenance()["zero_ordinates"], 712)
        self.assertEqual(uvb.provenance()["unequal_duplicate_pairs"], 19)
        self.assertEqual(source.provenance()["unequal_duplicate_pairs"], 0)
        self.assertGreater(uvb.energies_eV[-1], source.energies_eV[-1])

    def test_raw_native_nodes_preserved_one_sided(self):
        for table in self.tables.values():
            energies = table.energies_eV
            unique, first, counts = np.unique(energies, return_index=True, return_counts=True)
            for iz in (0, 37, 59):
                np.testing.assert_array_equal(table.values(unique, table.redshifts[iz], side="left"),
                                              table.spectra[::-1, iz][first])
                np.testing.assert_array_equal(table.values(unique, table.redshifts[iz], side="right"),
                                              table.spectra[::-1, iz][first + counts - 1])

    def test_actual_moments_against_independent_gaussian_quadrature(self):
        gx, gw = np.polynomial.legendre.leggauss(32)
        source_dir = Path(__file__).parent / "sources"
        for kind, name in (("uvb", "UVB.out"), ("emissivity", "emissivity.out")):
            # Deliberately independent parser and interpolation path.
            raw_rows = [list(map(float, line.split())) for line in (source_dir / name).read_text().splitlines()
                        if line.strip() and not line.lstrip().startswith("#")]
            zraw, matrix = np.array(raw_rows[0]), np.array(raw_rows[1:])
            energy = HC_EV_ANGSTROM / matrix[::-1, 0]
            redshift = 6.0
            iz = np.flatnonzero(zraw <= redshift)[-1]
            tz = (redshift - zraw[iz]) / (zraw[iz + 1] - zraw[iz])
            profile = matrix[::-1, iz + 1] * (1 - tz) + matrix[::-1, iz + 2] * tz
            for power in (0.0, 1.0, -3.0):
                reference_terms = []
                for i in range(len(energy) - 1):
                    left, right = max(13.6, energy[i]), min(500.0, energy[i + 1])
                    if left >= right:
                        continue
                    xa, xb = math.log(left), math.log(right)
                    points = (xa + xb) / 2 + (xb - xa) / 2 * gx
                    t = (points - math.log(energy[i])) / math.log(energy[i + 1] / energy[i])
                    sampled = profile[i] + t * (profile[i + 1] - profile[i])
                    reference_terms.append((xb - xa) / 2 * np.dot(gw, sampled * np.exp(power * (points - math.log(13.6)))))
                reference = math.fsum(reference_terms)
                actual = self.tables[kind].moment(13.6, 500, redshift, power=power, reference_eV=13.6)
                self.assertAlmostEqual(actual / reference, 1, places=12)
                groups = self.tables[kind].group_moments([13.6, 24.6, 54.4, 500], redshift,
                                                        power=power, reference_eV=13.6)
                self.assertAlmostEqual(sum(groups) / actual, 1, places=12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
