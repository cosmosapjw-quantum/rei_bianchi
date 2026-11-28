"""Bounded physics/API unit tests; no ODE, benchmark, or PHYS78 replay.

Independent oracles use 72-digit Decimal arithmetic and literals transcribed
from Voronov1997 cfit.dat and Savin2002 Eq6/Table2.  Source text acquisition
and its limitations are recorded in theory/SOURCE_EVIDENCE_EXTRACTED.json.
The test count is the number of unique unittest methods, not subtest probes.
Running this file writes append-preserving machine receipts next to it.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source'))
import numpy as np
import collisional as c

D = Decimal
KB = 1.380649e-23 / 1.602176634e-19
PRIMARY_CI = (
    ('13.6', '0', '2.91e-8', '.2320', '.39', '1', '20'),
    ('24.6', '0', '1.75e-8', '.1800', '.35', '1', '20'),
    ('54.4', '1', '2.05e-9', '.2650', '.25', '3', '20'),
    ('5.4', '0', '1.39e-7', '.4380', '.41', '1', '20'),
    ('75.6', '1', '2.01e-9', '.2090', '.23', '4', '20'),
    ('122.4', '1', '9.60e-10', '.5820', '.17', '5', '20'),
)
# Independent finite-slot contract, including a spectator neutron.
NAMES = (
    'H1_I', 'H1_II', 'D_I', 'D_II', 'T_I', 'T_II',
    'He3_I', 'He3_II', 'He3_III', 'He4_I', 'He4_II', 'He4_III',
    'Li6_I', 'Li6_II', 'Li6_III', 'Li6_IV',
    'Li7_I', 'Li7_II', 'Li7_III', 'Li7_IV', 'n',
)
IX = {name: i for i, name in enumerate(NAMES)}
CHARGES = np.array([0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2,
                    0, 1, 2, 3, 0, 1, 2, 3, 0], dtype=np.int64)
ISOTOPES = ('H1', 'D', 'T', 'He3', 'He4', 'Li6', 'Li7', 'n')


def ci_decimal(row, temperature):
    """Direct primary formula, not the implementation's logarithmic form."""
    with localcontext() as ctx:
        ctx.prec = 72
        de, p, a, x, power, _, _ = map(D, PRIMARY_CI[row])
        kb = D('1.380649e-23') / D('1.602176634e-19')
        u = de / (kb * D(str(temperature)))
        return a * (1 + p * u.sqrt()) * (power * u.ln()).exp() * (-u).exp() / (x + u)


def d_raw_decimal(temperature):
    with localcontext() as ctx:
        ctx.prec = 72
        t = D(str(temperature))
        forward = (D('2e-10') * (D('.402') * t.ln()).exp()
                   * (-D('37.1') / t).exp()
                   - D('3.31e-17') * (D('1.48') * t.ln()).exp())
        reverse = (D('2.06e-10') * (D('.396') * t.ln()).exp()
                   * (-D('33') / t).exp()
                   + D('2.03e-9') * (D('-.332') * t.ln()).exp())
        return forward, reverse


def state(**entries):
    y = np.zeros(len(NAMES))
    for name, value in entries.items():
        y[IX[name]] = value
    return y


def mixed_state():
    return state(H1_I=.61, H1_II=.39, D_I=1.4e-5, D_II=1.06e-5,
                 T_I=1e-8, T_II=2e-8, He3_I=7e-6, He3_II=3e-6,
                 He3_III=7.4e-7, He4_I=.052, He4_II=.02, He4_III=.01,
                 Li6_I=1e-9, Li6_II=2e-10, Li6_III=3e-11, Li6_IV=4e-12,
                 Li7_I=5e-9, Li7_II=4e-10, Li7_III=2e-11, Li7_IV=1e-12,
                 n=3e-8)


class PhysicsTestCase(unittest.TestCase):
    def assertRelative(self, actual, expected, tolerance=5e-14):
        expected = float(expected)
        self.assertTrue(math.isfinite(actual))
        self.assertNotEqual(expected, 0.)
        self.assertLessEqual(abs(actual - expected) / abs(expected), tolerance,
                             msg=f'actual={actual!r}, expected={expected!r}')


class PrimaryRateTests(PhysicsTestCase):
    def test_ci_six_rows_against_72_digit_primary_formula(self):
        for row in range(6):
            with self.subTest(row=row):
                self.assertRelative(c.ci_rate(row, 100000.), ci_decimal(row, 100000.))

    def test_observed_temperature_has_only_neutral_ci_domain(self):
        actual = c.ci_domain_mask(np.array([255., 25370.7, 100000., math.nan]))
        expected = np.array([[False] * 6,
                             [True, True, False, True, False, False],
                             [True] * 6, [False] * 6])
        np.testing.assert_array_equal(actual, expected)
        for row in (0, 1, 3):
            with self.subTest(row=row):
                self.assertRelative(c.ci_rate(row, 25370.7), ci_decimal(row, 25370.7))

    def test_ci_author_domain_units_and_inclusive_endpoints(self):
        for row, primary in enumerate(PRIMARY_CI):
            minimum = float(primary[5]) / KB
            maximum = 1000 * float(primary[6]) / KB
            with self.subTest(row=row):
                self.assertEqual(c.CI_MIN_K[row], minimum)
                self.assertEqual(c.CI_MAX_K[row], maximum)
                self.assertGreater(c.ci_rate(row, minimum), 0.)
                self.assertGreater(c.ci_rate(row, maximum), 0.)
                for outside in (np.nextafter(minimum, 0.), np.nextafter(maximum, math.inf)):
                    with self.assertRaises(c.RateDomainError):
                        c.ci_rate(row, outside)

    def test_ci_row_identity_rejects_bool_fractional_and_unknown(self):
        for row in (True, False, -1, 6, .0, .5, '0', None):
            with self.subTest(row=repr(row)), self.assertRaises(ValueError):
                c.ci_rate(row, 100000.)
        self.assertRelative(c.ci_rate(np.int64(0), 100000.), ci_decimal(0, 100000.))

    def test_nonpositive_and_nonfinite_rate_temperatures_are_rejected(self):
        for temperature in (0., -1., math.nan, math.inf, -math.inf):
            with self.subTest(temperature=repr(temperature)):
                with self.assertRaises(c.RateDomainError):
                    c.ci_rate(0, temperature)
                with self.assertRaises(c.RateDomainError):
                    c.d_cx_rates(temperature)

    def test_savin_raw_pair_against_72_digit_table2_formula(self):
        for temperature in (255., 10000., 25370.7):
            actual = c.d_cx_rates(temperature, closure='raw_fit')
            expected = d_raw_decimal(temperature)
            for direction in (0, 1):
                with self.subTest(T=temperature, direction=direction):
                    self.assertRelative(actual[direction], expected[direction])

    def test_derived_d_forward_is_distinct_from_source_forward(self):
        temperature = 10000.
        forward, reverse = c.d_cx_rates(temperature, closure='detailed_balance')
        raw_forward, raw_reverse = c.d_cx_rates(temperature, closure='raw_fit')
        self.assertEqual(reverse, raw_reverse)
        with localcontext() as ctx:
            ctx.prec = 72
            boltzmann = (-D(43) / D(str(temperature))).exp()
            expected_forward = d_raw_decimal(temperature)[1] * boltzmann
        self.assertRelative(forward, expected_forward)
        self.assertLess(forward / reverse, 1.)
        self.assertGreater(raw_forward / raw_reverse, 1.)
        self.assertGreater(abs(raw_forward / forward - 1.), .01)
        for closure in ('raw_fit', 'detailed_balance'):
            result = c.CollisionNetwork(ci_rows=(), d_cx=True,
                                        d_cx_closure=closure).rhs(temperature, 1., mixed_state())
            self.assertEqual(result.diagnostics['d_cx_closure'], closure)
            if closure == 'raw_fit':
                self.assertNotIn('DB43K', result.diagnostics['model'])

    def test_d_fit_domain_and_closure_name_are_explicit(self):
        for temperature in (2.7, 200000.):
            self.assertTrue(all(value > 0. for value in c.d_cx_rates(temperature)))
        for temperature in (np.nextafter(2.7, 0.), np.nextafter(200000., math.inf)):
            with self.subTest(T=temperature), self.assertRaises(c.RateDomainError):
                c.d_cx_rates(temperature)
        with self.assertRaises(ValueError):
            c.d_cx_rates(300., closure='unspecified')


class StoichiometryTests(PhysicsTestCase):
    def test_each_event_conserves_isotopes_and_total_charge(self):
        self.assertEqual(tuple(c.atomic.SPECIES_NAMES), NAMES)
        network = c.CollisionNetwork(ci_rows=tuple(range(6)), d_cx=True)
        self.assertEqual(network.stoichiometry.shape, (21, 15))
        self.assertEqual(len(set(network.event_names)), 15)
        expected_ci = ['CI:' + name for name in NAMES
                       if name != 'n' and CHARGES[IX[name]] <
                       (1 if name.split('_')[0] in ('H1', 'D', 'T')
                        else 2 if name.startswith('He') else 3)]
        self.assertEqual(list(network.event_names[:13]), expected_ci)
        for j, name in enumerate(network.event_names):
            column = network.stoichiometry[:, j]
            with self.subTest(event=name):
                for isotope in ISOTOPES:
                    positions = [i for i, species in enumerate(NAMES)
                                 if species.split('_')[0] == isotope]
                    self.assertEqual(sum(int(column[i]) for i in positions), 0)
                emitted_electrons = 1 if name.startswith('CI:') else 0
                self.assertEqual(int(CHARGES @ column) - emitted_electrons, 0)
                self.assertEqual(network.delta_electron[j], emitted_electrons)
        np.testing.assert_array_equal(network.stoichiometry[IX['n']], np.zeros(15))

    def test_dcx_direction_is_endothermic_forward_and_exothermic_reverse(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        expected = state(D_I=-1, H1_II=-1, D_II=1, H1_I=1)
        np.testing.assert_array_equal(network.stoichiometry[:, 0], expected)
        np.testing.assert_array_equal(network.stoichiometry[:, 1], -expected)
        self.assertAlmostEqual(network.delta_binding_eV[0], 43. * KB, delta=5e-15)
        self.assertEqual(network.delta_binding_eV[1], -network.delta_binding_eV[0])
        forward = network.rhs(255., .1, state(D_I=2.46e-5, H1_II=1.))
        reverse = network.rhs(255., .1, state(D_II=2.46e-5, H1_I=1.))
        self.assertGreater(forward.event_per_H_s[0], 0.)
        self.assertEqual(forward.event_per_H_s[1], 0.)
        self.assertLess(forward.heat_eV_per_H_s, 0.)
        self.assertGreater(reverse.heat_eV_per_H_s, 0.)
        self.assertEqual(forward.d_electron_per_H_dt, 0.)
        self.assertEqual(reverse.d_electron_per_H_dt, 0.)

    def test_chemical_ledger_uses_pinned_potentials_and_d_defect(self):
        expected = np.array([0., 13.6, 0., 13.6 + 43. * KB, 0., 13.6,
                             0., 24.59, 79.01, 0., 24.59, 79.01,
                             0., 5.392, 81.032, 203.532,
                             0., 5.392, 81.032, 203.532, 0.])
        np.testing.assert_allclose(c.ionic_potential_eV(), expected, rtol=3e-16, atol=0.)
        self.assertNotEqual(expected[IX['He4_II']], float(PRIMARY_CI[1][0]))
        self.assertNotEqual(expected[IX['Li7_II']], float(PRIMARY_CI[3][0]))

    def test_subnetwork_selection_is_explicit_and_configuration_validated(self):
        network = c.CollisionNetwork(ci_rows=(0, 1, 3), d_cx=False)
        self.assertEqual(set(network.event_names),
                         {'CI:H1_I', 'CI:D_I', 'CI:T_I', 'CI:He3_I',
                          'CI:He4_I', 'CI:Li6_I', 'CI:Li7_I'})
        for rows in ((0, 0), (6,), (-1,), (True,), (.0,)):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                c.CollisionNetwork(ci_rows=rows, d_cx=False)
        with self.assertRaises(ValueError):
            c.CollisionNetwork(ci_rows=(), d_cx=1)
        with self.assertRaises(ValueError):
            c.CollisionNetwork(ci_rows=(), d_cx=True, d_cx_closure='unknown')

    def test_zero_electrons_do_not_bypass_the_requested_rate_domain(self):
        network = c.CollisionNetwork(ci_rows=(0,), d_cx=False)
        neutral = state(H1_I=1.)
        with self.assertRaises(c.RateDomainError):
            network.rhs(255., 1., neutral)
        allowed = network.rhs(20000., 1., neutral)
        np.testing.assert_array_equal(allowed.event_per_H_s, np.zeros(3))
        self.assertEqual(allowed.heat_eV_per_H_s, 0.)

    def test_full_cosmological_admission_remains_explicitly_refused(self):
        with self.assertRaises(c.UnresolvedClosureError) as caught:
            c.require_full_cosmological_admission()
        for obligation in ('low_temperature_CI', 'He_Li_CX', 'D_PI_RR', 'z20_initial_charge'):
            self.assertIn(obligation, str(caught.exception))
        result = c.CollisionNetwork(ci_rows=(), d_cx=True).rhs(300., 1., mixed_state())
        self.assertEqual(result.diagnostics['full_cosmological_admission'], 'NOT_ISSUED')


class LocalDynamicsTests(PhysicsTestCase):
    def test_ci_event_units_and_density_scaling_use_derived_electrons(self):
        network = c.CollisionNetwork(ci_rows=(0,), d_cx=False)
        y = state(H1_I=.7, H1_II=.3)
        result = network.rhs(20000., 2.5, y)
        expected = D('2.5') * D('.7') * D('.3') * ci_decimal(0, 20000.)
        self.assertRelative(result.event_per_H_s[0], expected)
        self.assertRelative(result.d_electron_per_H_dt, expected)
        self.assertEqual(result.electron_abundance_per_H, .3)
        denser = network.rhs(20000., 10., y)
        np.testing.assert_allclose(denser.event_per_H_s, 4. * result.event_per_H_s,
                                   rtol=2e-15, atol=0.)
        self.assertRelative(denser.heat_eV_per_H_s, 4. * result.heat_eV_per_H_s)

    def test_dcx_flux_has_no_electron_catalyst_and_preserves_particle_count(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        y = state(H1_I=.6, H1_II=.4, D_I=1.5e-5, D_II=9.6e-6)
        result = network.rhs(255., 2., y)
        altered = y.copy()
        altered[IX['Li7_IV']] = .01  # inert spectator changes charge-derived ne
        spectator = network.rhs(255., 2., altered)
        np.testing.assert_array_equal(spectator.event_per_H_s, result.event_per_H_s)
        self.assertNotEqual(spectator.electron_abundance_per_H, result.electron_abundance_per_H)
        self.assertEqual(result.d_electron_per_H_dt, 0.)
        self.assertEqual(math.fsum(result.d_species_per_H_dt), 0.)

    def test_temperature_derivative_obeys_full_ideal_gas_chain_rule(self):
        network = c.CollisionNetwork(ci_rows=tuple(range(6)), d_cx=True)
        y = mixed_state()
        temperature, density, hubble = 100000., 1.7, 2e-11
        result = network.rhs(temperature, density, y, H_per_s=hubble)
        particles = math.fsum(y) + float(CHARGES @ y)
        thermal = 1.5 * KB * temperature * particles
        energy_derivative = -2. * hubble * thermal + result.heat_eV_per_H_s
        particle_derivative = (math.fsum(result.d_species_per_H_dt)
                               + float(CHARGES @ result.d_species_per_H_dt))
        derived = ((energy_derivative - 1.5 * KB * temperature * particle_derivative)
                   / (1.5 * KB * particles))
        self.assertRelative(result.temperature_derivative_K_per_s, derived)
        without_particle_term = energy_derivative / (1.5 * KB * particles)
        self.assertGreater(result.d_electron_per_H_dt, 0.)
        self.assertGreater(abs(derived - without_particle_term), 1e-4 * abs(derived))

    def test_empty_operator_adiabatic_term_and_thermal_inverse(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=False)
        y = mixed_state()
        result = network.rhs(700., .01, y, H_per_s=3e-16)
        self.assertEqual(result.event_per_H_s.size, 0)
        np.testing.assert_array_equal(result.d_species_per_H_dt, np.zeros(21))
        self.assertEqual(result.heat_eV_per_H_s, 0.)
        self.assertRelative(result.temperature_derivative_K_per_s, -2. * 3e-16 * 700.)
        energy = network.thermal_energy(700., y)
        self.assertRelative(network.temperature(energy, y), 700., tolerance=2e-15)

    def test_event_energy_and_direct_state_use_distinct_conditioning_scales(self):
        # One API diagnostic case; C9 owns the separate F2 conditioning grid.
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        y = state(H1_I=.75, H1_II=.25, D_I=6.15e-6, D_II=1.845e-5)
        result = network.rhs(700., .003, y)
        with localcontext() as ctx:
            ctx.prec = 72
            eps_h = D.from_float(13.6)
            eps_d = D.from_float(13.6 + 43. * KB)
            defect = eps_d - eps_h
            f, r = map(lambda value: D.from_float(float(value)), result.event_per_H_s)
            event_oracle = defect * (f - r)
            direct_oracle = (eps_h * D.from_float(float(result.d_species_per_H_dt[IX['H1_II']]))
                             + eps_d * D.from_float(float(result.d_species_per_H_dt[IX['D_II']])))
            constituent_oracle = (abs(eps_h * D.from_float(float(result.d_species_per_H_dt[IX['H1_II']])))
                                  + abs(eps_d * D.from_float(float(result.d_species_per_H_dt[IX['D_II']]))))
            event_scale = float(abs(defect * f) + abs(defect * r))
        self.assertLessEqual(abs(result.binding_derivative_eV_per_H_s - float(event_oracle)),
                             5e-15 * event_scale)
        self.assertLessEqual(abs(result.energy_ledger_residual_eV_per_H_s), 2e-13 * event_scale)
        self.assertRelative(result.heat_eV_per_H_s, -float(event_oracle))
        diagnostics = result.diagnostics
        direct = diagnostics['binding_derivative_direct_state_eV_per_H_s']
        constituent = diagnostics['binding_derivative_constituent_energy_scale_eV_per_H_s']
        self.assertRelative(constituent, float(constituent_oracle), tolerance=2e-15)
        self.assertLessEqual(abs(direct - float(direct_oracle)), 8 * np.finfo(float).eps * constituent)
        self.assertEqual(diagnostics['binding_derivative_direct_minus_event_eV_per_H_s'],
                         direct - result.binding_derivative_eV_per_H_s)


class ValidationAndOwnershipTests(PhysicsTestCase):
    def test_invalid_species_are_rejected_without_clipping(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        for bad_value in (-1e-250, math.nan, math.inf):
            y = mixed_state()
            y[IX['n']] = bad_value
            before = y.copy()
            with self.subTest(value=repr(bad_value)):
                for operation in (lambda: network.rhs(300., 1., y),
                                  lambda: network.thermal_energy(300., y),
                                  lambda: network.temperature(1., y)):
                    with self.assertRaises(ValueError):
                        operation()
                np.testing.assert_array_equal(y, before)
        for invalid in (np.zeros(20), np.zeros(22), np.zeros((21, 1)), np.zeros(21)):
            with self.subTest(shape=invalid.shape), self.assertRaises(ValueError):
                network.rhs(300., 1., invalid)

    def test_density_hubble_and_thermal_energy_input_validation(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        y = mixed_state()
        for density in (0., -1., math.nan, math.inf):
            with self.subTest(density=repr(density)), self.assertRaises(ValueError):
                network.rhs(300., density, y)
        for hubble in (math.nan, math.inf, -math.inf):
            with self.subTest(H=repr(hubble)), self.assertRaises(ValueError):
                network.rhs(300., 1., y, H_per_s=hubble)
        for energy in (0., -1., math.nan, math.inf):
            with self.subTest(energy=repr(energy)), self.assertRaises(ValueError):
                network.temperature(energy, y)

    def test_rhs_preserves_input_without_hidden_renormalization(self):
        network = c.CollisionNetwork(ci_rows=(), d_cx=True)
        y = mixed_state()
        y[IX['H1_I']], y[IX['H1_II']] = 2.5, 1.5
        before = y.copy()
        result = network.rhs(300., .1, y)
        np.testing.assert_array_equal(y, before)
        self.assertEqual(result.electron_abundance_per_H, float(CHARGES @ before))
        self.assertEqual(result.diagnostics['species_projection'], 'NONE')
        self.assertEqual(result.diagnostics['escaping_photon_energy'], 0.)

    def test_network_and_rhs_ledger_arrays_are_irreversibly_readonly(self):
        network = c.CollisionNetwork(ci_rows=(0,), d_cx=True)
        result = network.rhs(20000., 1., mixed_state())
        arrays = {'stoichiometry': network.stoichiometry,
                  'binding': network.binding_eV,
                  'delta_binding': network.delta_binding_eV,
                  'delta_electron': network.delta_electron,
                  'ionic_potential_return': c.ionic_potential_eV(),
                  'd_species_return': result.d_species_per_H_dt,
                  'event_return': result.event_per_H_s}
        for name, array in arrays.items():
            with self.subTest(array=name):
                self.assertFalse(array.flags.writeable)
                with self.assertRaises(ValueError):
                    array.setflags(write=True)
                with self.assertRaises(ValueError):
                    array.flat[0] = 1
        with self.assertRaises(FrozenInstanceError):
            result.heat_eV_per_H_s = 0.

    def test_detached_rate_values_do_not_alias_network_state(self):
        network = c.CollisionNetwork(ci_rows=(0,), d_cx=True)
        original = network.rate_coefficients(20000.)
        expected = original.copy()
        original[:] = 0.
        np.testing.assert_array_equal(network.rate_coefficients(20000.), expected)
        self.assertTrue(np.all(expected > 0.))


class ReceiptResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.current = None

    def startTest(self, test):
        super().startTest(test)
        self.current = {'name': test.id(), 'status': 'RUNNING', 'issues': []}
        self.records.append(self.current)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.current['status'] = 'PASS'

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.current['status'] = 'FAIL'
        self.current['issues'].append(self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.current['status'] = 'ERROR'
        self.current['issues'].append(self._exc_info_to_string(err, test))

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.current['status'] = 'FAIL' if issubclass(err[0], test.failureException) else 'ERROR'
            self.current['issues'].append({'subtest': str(subtest),
                                           'traceback': self._exc_info_to_string(err, test)})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.current['status'] = 'SKIP'
        self.current['issues'].append(reason)


def source_identity():
    names = ['source/collisional.py', 'source/phys78_bridge.py',
             'vendor/PHYS78_PROVENANCE.json', 'vendor/phys78/source/atomic_network.py',
             'vendor/phys78/vendor/atomic/photo.dat', 'vendor/phys78/vendor/atomic/rec_table1.dat',
             'theory/SOURCE_EVIDENCE_EXTRACTED.json', 'verification/test_collisional.py']
    result = {}
    for name in names:
        data = (ROOT / name).read_bytes()
        result[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return result


def run_and_record():
    started = datetime.now(timezone.utc).isoformat()
    before = source_identity()
    wall, cpu = time.perf_counter(), time.process_time()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, resultclass=ReceiptResult).run(suite)
    elapsed_wall, elapsed_cpu = time.perf_counter() - wall, time.process_time() - cpu
    after = source_identity()
    names = [record['name'] for record in result.records]
    success = result.wasSuccessful() and before == after and len(names) == len(set(names))
    directory = ROOT / 'verification'
    attempt_number = 1
    while (directory / f'LIGHT_TEST_ATTEMPT_{attempt_number:03d}.json').exists():
        attempt_number += 1
    receipt = {'schema': 'PHYS79_LIGHT_UNITTEST_RECEIPT_V1',
               'attempt': attempt_number, 'started_utc': started,
               'completed_utc': datetime.now(timezone.utc).isoformat(),
               'status': 'PASS' if success else 'FAIL',
               'unique_test_method_count': len(set(names)), 'tests_run': result.testsRun,
               'passed_count': sum(record['status'] == 'PASS' for record in result.records),
               'failed_or_error_count': sum(record['status'] in ('FAIL', 'ERROR') for record in result.records),
               'skipped_count': len(result.skipped), 'counting_policy': 'Unique unittest methods; subtests are not separately counted.',
               'test_results': result.records,
               'source_identity_before': before, 'source_identity_after': after,
               'source_identity_unchanged_during_run': before == after,
               'oracle': '72-digit Decimal primary-source formulas and independent physical slot/energy/charge contract',
               'python': platform.python_version(), 'numpy': np.__version__,
               'wall_seconds': elapsed_wall, 'cpu_seconds': elapsed_cpu,
               'ode_executions': 0, 'existing_identity_reruns': 0, 'benchmarks': 0,
               'source_mutations': 0, 'production_admission': 'NOT_ISSUED',
               'scope': 'Bounded source/kernel/API checks. C9 owns the separate F1/F2 targeted diagnostic grid; no cosmological admission.'}
    attempt_path = directory / f'LIGHT_TEST_ATTEMPT_{attempt_number:03d}.json'
    with attempt_path.open('x') as handle:
        json.dump(receipt, handle, indent=2, allow_nan=False)
        handle.write('\n')
    attempts = []
    for path in sorted(directory.glob('LIGHT_TEST_ATTEMPT_*.json')):
        data = path.read_bytes()
        prior = json.loads(data)
        attempts.append({'path': path.name, 'sha256': hashlib.sha256(data).hexdigest(),
                         'status': prior['status'], 'tests_run': prior['tests_run']})
    latest = dict(receipt)
    latest['preserved_attempts'] = attempts
    (directory / 'LIGHT_TEST_RECEIPT.json').write_text(json.dumps(latest, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': receipt['status'], 'unique_tests': len(set(names)),
                      'passed': receipt['passed_count'], 'attempt': attempt_number,
                      'receipt': 'verification/LIGHT_TEST_RECEIPT.json'}))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(run_and_record())
