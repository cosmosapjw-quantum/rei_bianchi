"""Focused algebra/source/energy controls; this module does not integrate ODEs."""
from decimal import Decimal, localcontext
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"source"))
import atomic_network as a


class AtomicNetworkTests(unittest.TestCase):
    def setUp(self):
        self.net = a.prepare_network()

    def mixed_state(self):
        y = a.neutral_abundances()
        # All charge stages have positive populations; isotope totals retained.
        for iso in a.ISOTOPES[:-1]:
            indices = [i for i, s in enumerate(a.SPECIES) if s.isotope == iso]
            total = y[indices].sum()
            y[indices] = total*np.arange(1, len(indices)+1)/sum(range(1, len(indices)+1))
        return y

    def test_registry_has_21_nuclear_slots_and_derived_electron(self):
        self.assertEqual(a.N_SPECIES, 21)
        self.assertEqual(len(self.net.lower), 13)
        self.assertEqual(a.SPECIES_NAMES[-1], "n")
        self.assertNotIn("electron", a.SPECIES_NAMES)
        self.assertEqual(a.SPECIES[a.SPECIES_INDEX["Li7_IV"]].charge, 3)
        self.assertEqual(a.DEFAULT_INVENTORY["T"], 0)
        self.assertEqual(a.DEFAULT_INVENTORY["n"], 0)
        self.assertAlmostEqual(self.net.binding_eV[a.SPECIES_INDEX["Li7_IV"]], 203.532)
        neutral = a.neutral_abundances()
        self.assertAlmostEqual(4*a.DEFAULT_INVENTORY["He4"]/(a.MASS_NUMBER@neutral),
                               a.DEFAULT_HE4_MASS_FRACTION, delta=1e-16)

    def test_exact_original_tables_bind_all_embedded_coefficients(self):
        self.assertEqual(a.verify_author_tables(a.DEFAULT_TABLE_DIRECTORY), dict(a.SOURCE_SHA256))
        a._verify_original_coefficients(a.DEFAULT_TABLE_DIRECTORY)

    def test_stoichiometry_preserves_each_isotope_and_nucleons(self):
        np.testing.assert_array_equal(a.ISOTOPE_SUM @ self.net.stoichiometry, 0)
        np.testing.assert_array_equal(a.MASS_NUMBER @ self.net.stoichiometry, 0)
        np.testing.assert_array_equal(a.CHARGE @ self.net.stoichiometry, np.ones(13))
        np.testing.assert_allclose(self.net.binding_eV @ self.net.stoichiometry,
                                   self.net.threshold_eV, rtol=0, atol=3e-14)

    def test_prepared_arrays_cannot_be_mutated(self):
        for arr in (self.net.photon_energy_eV, self.net.photo_cross_section_cm2,
                    self.net.rr_coefficients, self.net.stoichiometry):
            with self.assertRaises(ValueError):
                arr.flags.writeable = True

    def test_photo_rate_independent_decimal_anchor_and_units(self):
        # Independent direct powers, original HI coefficient row, Mb -> cm^2.
        with localcontext() as ctx:
            ctx.prec = 60
            D = Decimal
            x = D("18")/D("0.4298")
            p = D("2.963")
            expected = (D("54750")*(x-1)**2*x**(p/2-D("5.5"))
                        *(1+(x/D("32.88")).sqrt())**(-p)*D("1e-18"))
        row = np.flatnonzero(self.net.lower == a.SPECIES_INDEX["H1_I"])[0]
        self.assertAlmostEqual(self.net.photo_cross_section_cm2[row, 0]/float(expected), 1., delta=1e-14)
        self.assertAlmostEqual(self.net.photo_rate_per_photon_cm3_s[row, 0]
                               / (float(expected)*a.C_CM_S), 1., delta=1e-14)
        # Source thresholds retain physically absent high-ion photo channels.
        for name in ("Li6_II", "Li6_III", "Li7_II", "Li7_III"):
            j = np.flatnonzero(self.net.lower == a.SPECIES_INDEX[name])[0]
            np.testing.assert_array_equal(self.net.photo_cross_section_cm2[j], 0.)

    def test_rr_independent_decimal_anchor_and_capture_label(self):
        alpha, _, _ = self.net.rr_rates(10000.)
        with localcontext() as ctx:
            ctx.prec = 60
            D = Decimal
            s0 = (D(10000)/D("107.7")).sqrt()
            s1 = (D(10000)/D("11770000")).sqrt()
            expected = D("1.036e-11")/(s0*(1+s0)**D("0.612")*(1+s1)**D("1.388"))
        j = np.flatnonzero(self.net.lower == a.SPECIES_INDEX["Li7_I"])[0]
        self.assertEqual(self.net.upper[j], a.SPECIES_INDEX["Li7_II"])
        self.assertAlmostEqual(alpha[j]/float(expected), 1., delta=1e-14)

    def test_rr_capture_energy_matches_temperature_derivative(self):
        for t in (3., 7., 1e4, 1e7, 1e9):
            alpha, capture, slope = self.net.rr_rates(t)
            np.testing.assert_allclose(capture/(a.KB_EV_K*t), 1.5+slope, rtol=4e-13, atol=1e-16)
            self.assertTrue(np.all(capture > 0))
            self.assertTrue(np.all(capture < a.KB_EV_K*t))
            if 3 < t < 1e9:
                h = 1e-4
                plus = self.net.rr_rates(t*np.exp(h))[0]
                minus = self.net.rr_rates(t*np.exp(-h))[0]
                np.testing.assert_allclose((np.log(plus)-np.log(minus))/(2*h), slope,
                                           rtol=1e-8, atol=2e-10)

    def test_event_energy_and_number_ledgers_in_mixed_state(self):
        y = self.mixed_state()
        result = self.net.rhs(8000., .002, y, [.0001, .0002, .00005])
        scale = result.photo_absorbed_eV_per_H_s+result.rr_escape_eV_per_H_s
        self.assertLessEqual(abs(result.energy_ledger_residual_eV_per_H_s), 2e-15*scale)
        np.testing.assert_allclose(a.ISOTOPE_SUM @ result.dsdt, 0,
                                   rtol=0, atol=2e-16*max(abs(result.dsdt)))
        np.testing.assert_allclose(result.photon_absorption_cm3_s,
                                   .002*result.photon_absorption_per_H_s, rtol=0, atol=0)
        self.assertEqual(result.electron_density_cm3, .002*(a.CHARGE @ y))
        self.assertEqual(result.d_electron_per_H_dt, a.CHARGE @ result.dsdt)
        self.assertEqual(result.diagnostics["state_projection"], "NONE")

    def test_positivity_generator_on_every_coordinate_boundary(self):
        photons = np.array([.0001, .0002, .0003])
        # For a nonnegative state with one zero coordinate, that derivative
        # must be nonnegative (quasipositivity of the number-reaction vector).
        for zero in range(a.N_SPECIES):
            y = np.linspace(.001, .021, a.N_SPECIES)
            y[zero] = 0
            result = self.net.rhs(4000., .002, y, photons)
            self.assertGreaterEqual(result.dsdt[zero], 0., a.SPECIES_NAMES[zero])

    def test_neutral_dark_limit_and_pure_rr_energy_sign(self):
        y = a.neutral_abundances()
        result = self.net.rhs(10., .001, y, [0., 0., 0.])
        np.testing.assert_array_equal(result.dsdt, 0)
        self.assertEqual(result.heat_eV_per_H_s, 0)
        y[a.SPECIES_INDEX["H1_I"]] = 0
        y[a.SPECIES_INDEX["H1_II"]] = 1
        result = self.net.rhs(10., .001, y, [0., 0., 0.])
        self.assertGreater(result.dsdt[a.SPECIES_INDEX["H1_I"]], 0)
        self.assertLess(result.heat_eV_per_H_s, 0)
        self.assertGreater(result.rr_escape_eV_per_H_s, 0)

    def test_invalid_domains_and_negative_states_fail_without_projection(self):
        for energies in ([18., 30., 64.390001], [0.], [float("nan")], []):
            with self.assertRaises(ValueError):
                a.prepare_network(energies)
        for t in (0., 2.9999, 1e9+1, float("nan")):
            with self.assertRaises(ValueError):
                self.net.rr_rates(t)
        y = a.neutral_abundances()
        y[3] = -1e-30
        with self.assertRaisesRegex(ValueError, "NEGATIVE_NO_CLIPPING"):
            self.net.rhs(100., .001, y, [0., 0., 0.])
        with self.assertRaises(ValueError):
            self.net.rhs(100., .001, a.neutral_abundances(), [0., -1e-30, 0.])
        with self.assertRaisesRegex(ValueError, "EMAX_EXCEEDED"):
            self.net.with_photon_energies([18., 30., 65.])

    def test_dynamic_photon_energy_recomputes_rates_and_heat(self):
        changed = self.net.with_photon_energies([12., 25., 59.])
        np.testing.assert_array_equal(self.net.photon_energy_eV, [18., 30., 60.])
        h = np.flatnonzero(changed.lower == a.SPECIES_INDEX["H1_I"])[0]
        self.assertEqual(changed.photo_cross_section_cm2[h, 0], 0.)
        result = a.rhs(100., .001, a.neutral_abundances(), [.01, .02, .01],
                       photon_energy_eV=[12., 25., 59.], prepared=self.net)
        self.assertLess(abs(result.energy_ledger_residual_eV_per_H_s),
                        2e-15*result.photo_absorbed_eV_per_H_s)

    def test_solver_extension_is_bounded_raw_and_not_state_projection(self):
        y = self.mixed_state()
        li = a.SPECIES_INDEX["Li7_IV"]
        y[li] = -1e-11*a.DEFAULT_INVENTORY["Li7"]
        before = y.copy()
        with self.assertRaises(ValueError):
            self.net.rhs(100., .001, y, [0., 0., 0.])
        result = self.net.rhs(100., .001, y, [0., 0., 0.], allow_solver_extension=True)
        np.testing.assert_array_equal(y, before)
        self.assertTrue(result.diagnostics["solver_extension"])
        self.assertEqual(result.diagnostics["negative_stage_coordinates"], 1)
        # Raw polynomial extension: a negative parent produces a negative RR
        # flux, rather than a silently clipped zero. It is not physical data.
        channel = np.flatnonzero(self.net.upper == li)[0]
        self.assertLess(result.rr_event_per_H_s[channel], 0)
        y[li] = -1e-7*a.DEFAULT_INVENTORY["Li7"]
        with self.assertRaisesRegex(ValueError, "BOUND_EXCEEDED"):
            self.net.rhs(100., .001, y, [0., 0., 0.], allow_solver_extension=True)

    def test_sparse_jacobian_includes_electron_feedback(self):
        s = self.net.species_jacobian_sparsity
        self.assertTrue(s[a.SPECIES_INDEX["H1_I"], a.SPECIES_INDEX["Li7_IV"]])
        self.assertFalse(s[a.SPECIES_INDEX["H1_I"], a.SPECIES_INDEX["Li7_I"]])
        self.assertFalse(np.any(s[a.SPECIES_INDEX["n"]]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
