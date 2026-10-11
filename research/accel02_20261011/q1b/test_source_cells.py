"""New cell source fixtures: no physical ODE or legacy reference replay."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'physical_provider_20261010'))
from hm12_data import HM12Table, HC_EV_ANGSTROM
from source_cells import table_cell_moments
from grid_cells import build_grid


def manufactured(energies, values):
    energies = np.asarray(energies, float)
    values = np.asarray(values, float)
    return HM12Table('emissivity', np.array([0., 2.]),
                     HC_EV_ANGSTROM / energies[::-1],
                     np.column_stack([values[::-1], values[::-1]]))


class SourceTests(unittest.TestCase):
    def test_constant_and_R_factors(self):
        table = manufactured([1., 100.], [3., 3.])
        got = table_cell_moments(table, 1., [4., 8.], [.5, .8], [.4, .6], (1., 100.))
        fac = table.proper_photon_factor(1.)
        for a, (R, w) in enumerate(zip([.5, .8], [.4, .6])):
            expected_N = w / R**3 * 3. * math.log(2.) * fac
            expected_U = w / R**3 * 3. * (8.*R-4.*R) * fac
            self.assertAlmostEqual(got['N'][a, 0]/expected_N, 1., delta=2e-14)
            self.assertAlmostEqual(got['U_eV'][a, 0]/expected_U, 1., delta=2e-14)
            self.assertEqual(got['Q_eV'][a, 0], got['U_eV'][a, 0]/R)

    def test_linear_log_ordinate(self):
        table = manufactured([1., math.e**2], [2., 8.])  # f=2+3 ln(E)
        lo, hi = math.exp(.2), math.exp(1.7)
        got = table_cell_moments(table, 1., [lo, hi], [1.], [1.], (1., math.e**2))
        fac = table.proper_photon_factor(1.)
        n = 2.*1.5 + 1.5*(1.7**2-.2**2)
        u = hi*(3.*1.7-1.) - lo*(3.*.2-1.)
        self.assertAlmostEqual(got['N'][0, 0]/(n*fac), 1., delta=2e-14)
        self.assertAlmostEqual(got['U_eV'][0, 0]/(u*fac), 1., delta=2e-14)

    def test_jump_has_zero_measure_and_one_sided_pieces(self):
        table = manufactured([1., 2., 2., 4.], [1., 1., 3., 3.])
        got = table_cell_moments(table, 1., [1., 1.5, 3., 4.], [1.], [1.], (1., 4.))
        fac = table.proper_photon_factor(1.)
        self.assertAlmostEqual(got['N'].sum()/(4.*math.log(2.)*fac), 1., delta=2e-14)
        self.assertAlmostEqual(got['U_eV'].sum()/(7.*fac), 1., delta=2e-14)

    def test_empty_and_partial_entry(self):
        table = manufactured([1., 100.], [2., 2.])
        got = table_cell_moments(table, 1., [20., 40., 60., 80.], [1.], [1.], (10., 50.))
        fac = table.proper_photon_factor(1.)
        self.assertEqual(got['N'][0, 2], 0.)
        self.assertEqual(got['U_eV'][0, 2], 0.)
        self.assertAlmostEqual(got['N'][0, 1]/(2.*math.log(1.25)*fac), 1., delta=2e-14)
        self.assertTrue(40. < got['Q_eV'][0, 1]/got['N'][0, 1] < 50.)
        boundary = table_cell_moments(table, 1., [50., 80.], [1.], [1.], (10., 50.))
        self.assertEqual(boundary['N'][0, 0], 0.)

    def test_invalid_input_rejected_without_clipping(self):
        table = manufactured([1., 100.], [1., 1.])
        for edges, R, w in [([2., 1.], [1.], [1.]), ([1., 2.], [0.], [1.]),
                            ([1., 2.], [1.], [-1.]), ([1., 2.], [float('nan')], [1.])]:
            with self.assertRaises(ValueError):
                table_cell_moments(table, 1., edges, R, w, (1., 100.))

    def test_fixed_nested_grid_and_distinct_features(self):
        uvb = manufactured([1., 12., 12., 54.37903440052643, 54.37903440052643, 200000.],
                           [1., 1., 2., 2., 3., 3.])
        coarse = build_grid(uvb, 169000., 1)
        fine = build_grid(uvb, 169000., 2)
        self.assertEqual(len(fine['q_edges_eV'])-1, 2*(len(coarse['q_edges_eV'])-1))
        self.assertEqual(fine['q_edges_eV'][::2], coarse['q_edges_eV'])
        self.assertIn(54.37903440052643, coarse['q_edges_eV'])
        self.assertIn(54.42, coarse['q_edges_eV'])
        self.assertEqual(sum(coarse['angular_weights']), 1.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
