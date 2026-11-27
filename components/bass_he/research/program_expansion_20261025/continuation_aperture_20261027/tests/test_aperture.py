"""New conditional controls only; no historical suite or kernel imports."""
from decimal import Decimal
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.aperture import (AngularMap, BernsteinDensity, ContractError, FULL,
    IntegralBounds, SetBounds, StoppedDirectionError, UnsupportedMeasureError,
    aperture_integral, difference, intersection, length, normalize, pair_response,
    rational, reflection, union)
from scripts.build_saved_payload import SOURCE_SHA256, build_payload, save_payload


class ApertureTests(unittest.TestCase):
    def setUp(self):
        self.uniform = BernsteinDensity([Q(1, 2)])
        self.folded = AngularMap(1, Q(5, 4))

    def enclosed(self, result, value):
        self.assertLessEqual(result.lower, value)
        self.assertLessEqual(value, result.upper)

    def test_01_exact_scalar_model(self):
        self.assertEqual(rational('1/10'), Q(1, 10))
        self.assertEqual(rational('0.125'), Q(1, 8))
        self.assertEqual(rational(0.1), Q.from_float(0.1))
        self.assertNotEqual(rational(0.1), Q(1, 10))

    def test_02_scalar_invalid_policy(self):
        for value in (True, False, float('inf'), float('-inf'), float('nan'),
                      'NaN', '1/0', Decimal('0.5'), None, complex(1)):
            with self.subTest(value=repr(value)), self.assertRaises(ContractError):
                rational(value)

    def test_03_parameter_and_delta_domain(self):
        for gamma, a in ((0, 0), (10**6 + 1, 0), (1, -1), (1, 10**6 + 1), (True, 0)):
            with self.assertRaises(ContractError):
                AngularMap(gamma, a)
        for delta in (0, Q(1, 2**81), 2, True):
            with self.assertRaises(ContractError):
                self.folded.preimage((0, 1), delta)
        for window in ((1, 0), (-2, 0), (0,), None):
            with self.assertRaises(ContractError):
                self.folded.preimage(window, Q(1, 256))

    def test_04_atoms_rejected_and_stopped_direction(self):
        with self.assertRaises(UnsupportedMeasureError):
            AngularMap(1, 1, kappa=0)
        with self.assertRaises(UnsupportedMeasureError):
            AngularMap(1, 1, measure_kind='ATOM')
        with self.assertRaises(StoppedDirectionError):
            AngularMap(1, 1).compare(-1, 0)

    def test_05_identity_predicate(self):
        angular = AngularMap(1, 0)
        for mu, nu in ((Q(-3, 4), Q(-1, 2)), (0, 0), (Q(4, 5), Q(3, 5)), (-1, -1), (1, 1)):
            self.assertEqual(angular.compare(mu, nu), (mu > nu) - (mu < nu))

    def test_06_original_sign_filter(self):
        angular = AngularMap(1, Q(1, 2))
        self.assertEqual(angular.compare(Q(-3, 4), Q(1, 2)), -1)
        self.assertEqual(angular.compare(Q(-3, 4), Q(-1, 2)), 1)
        self.assertEqual(angular.compare(Q(-3, 4), Q(-1, 4)), -1)
        self.assertEqual(angular.compare(Q(-1, 2), 0), 0)
        self.assertEqual(angular.compare(-1, 1), -1)

    def test_07_exact_fold_and_singleton(self):
        self.assertEqual(self.folded.compare(Q(-4, 5), Q(3, 5)), 0)
        result = self.folded.preimage((Q(3, 5), Q(3, 5)), Q(1, 256))
        self.assertEqual(result.sets, SetBounds((), ()))

    def test_08_full_support_and_endpoints(self):
        for angular in (AngularMap(1, 0), AngularMap(2, Q(1, 3)), self.folded):
            result = angular.preimage((-1, 1), Q(1, 256))
            self.assertEqual(result.sets.inner, FULL)
            self.assertEqual(result.sets.outer, FULL)
        self.assertEqual(self.folded.compare(-1, 1), 0)
        self.assertEqual(self.folded.compare(1, 1), 0)

    def test_09_stopped_auxiliary_boundary_only(self):
        angular = AngularMap(2, 1)
        zero = angular.preimage((-1, 0), Q(1, 256))
        full = angular.preimage((0, 1), Q(1, 256))
        self.assertEqual(zero.sets.outer, ())
        self.assertEqual(full.sets.inner, FULL)
        with self.assertRaises(StoppedDirectionError):
            angular.compare(-1, Q(1, 2))

    def test_10_outside_support(self):
        for window in ((-1, 0), (Q(1, 5), Q(1, 2))):
            result = self.folded.preimage(window, Q(1, 256))
            self.assertEqual(result.sets.outer, ())

    def test_11_branch_bracket_and_uncertainty_length(self):
        delta = Q(1, 2**16)
        result = self.folded.preimage((Q(13, 20), Q(4, 5)), delta)
        self.assertEqual(len(result.root_brackets), 4)
        self.assertTrue(all(hi - lo <= delta for lo, hi in result.root_brackets))
        self.assertLessEqual(result.uncertainty_length, 4 * delta)
        self.assertFalse(difference(result.sets.inner, result.sets.outer))

    def test_12_identity_preimage_exact(self):
        result = AngularMap(1, 0).preimage((Q(-1, 2), Q(3, 4)), Q(1, 2**16))
        self.assertEqual(result.sets.inner, ((Q(-1, 2), Q(3, 4)),))
        self.assertEqual(result.sets.inner, result.sets.outer)

    def test_13_fold_mass_independent_algebraic_value(self):
        mass = aperture_integral(self.folded, self.uniform, (Q(3, 5), Q(4, 5)), delta=Q(1, 2**24))['integral']
        self.assertGreater(mass.lower, 0)
        self.assertLessEqual(mass.lower**2, Q(7, 25))
        self.assertLessEqual(Q(7, 25), mass.upper**2)

    def test_14_fold_complement_mass(self):
        low = aperture_integral(self.folded, self.uniform, (Q(3, 5), Q(4, 5)), delta=Q(1, 2**16))['integral']
        high = aperture_integral(self.folded, self.uniform, (Q(4, 5), 1), delta=Q(1, 2**16))['integral']
        self.enclosed(low.added(high), Q(1))
        self.assertLessEqual((1 - high.upper)**2, Q(7, 25))
        self.assertLessEqual(Q(7, 25), (1 - high.lower)**2)

    def test_15_near_fold_mass_and_no_fake_density(self):
        narrow = aperture_integral(self.folded, self.uniform, (Q(3, 5), Q(3, 5) + Q(1, 1024)), delta=Q(1, 2**24))['integral']
        wide = aperture_integral(self.folded, self.uniform, (Q(3, 5), Q(3, 5) + Q(1, 256)), delta=Q(1, 2**24))['integral']
        self.assertGreater(narrow.lower, 0)
        self.assertLess(narrow.upper, wide.lower)
        self.assertLess(wide.upper, 1)

    def test_16_normalized_interval_union(self):
        self.assertEqual(normalize(((0, 0), (Q(1, 2), 1), (-1, 0), (0, Q(3, 4)))), FULL)
        with self.assertRaises(ContractError):
            normalize(((1, -1),))
        with self.assertRaises(ContractError):
            normalize(((-2, 0),))

    def test_17_set_intersection_and_reflection(self):
        a = ((Q(-3, 4), Q(1, 4)),)
        b = ((0, Q(3, 4)),)
        self.assertEqual(intersection(a, b), ((Q(0), Q(1, 4)),))
        self.assertEqual(reflection(reflection(a)), normalize(a))
        self.assertEqual(reflection(intersection(a, b)), intersection(reflection(a), reflection(b)))
        self.assertEqual(reflection(union(a, b)), union(reflection(a), reflection(b)))

    def test_18_difference_partition_and_contacts(self):
        a, b = ((Q(-3, 4), Q(3, 4)),), ((Q(-1, 4), Q(1, 4)),)
        self.assertEqual(length(difference(a, b)), 1)
        self.assertEqual(union(difference(a, b), intersection(a, b)), normalize(a))
        self.assertEqual(intersection(((-1, 0),), ((0, 1),)), ())

    def test_19_enclosure_boolean_difference(self):
        a = SetBounds(((Q(-1, 2), Q(1, 2)),), FULL)
        b = SetBounds(((Q(-1, 4), Q(1, 4)),), ((Q(-1, 2), Q(1, 2)),))
        result = a.difference(b)
        self.assertFalse(difference(result.inner, result.outer))
        self.assertEqual(result.outer, ((Q(-1), Q(-1, 4)), (Q(1, 4), Q(1))))
        with self.assertRaises(ContractError):
            SetBounds(FULL, ())

    def test_20_constant_and_partition_of_unity(self):
        self.assertEqual(self.uniform.sigma, 1)
        self.assertEqual(self.uniform.integral(), 1)
        density = BernsteinDensity([Q(1, 2)] * 9)
        for mu in (-1, Q(-1, 3), 0, Q(7, 8), 1):
            self.assertEqual(density.value(mu), Q(1, 2))
        self.assertEqual(density.integral(), 1)

    def test_21_individual_basis_integrals(self):
        for k in range(9):
            coefficients = [0] * 9
            coefficients[k] = 1
            density = BernsteinDensity(coefficients)
            self.assertEqual(density.integral(), Q(2, 9))
            # Independent beta first moment: E[mu]=2(k+1)/(n+2)-1.
            self.assertEqual(density.integral(w0=0, w1=1), Q(2, 9) * (Q(k + 1, 5) - 1))

    def test_22_manufactured_parabolic_density(self):
        density = BernsteinDensity([0, Q(3, 2), 0])
        for mu in (-1, Q(-1, 3), 0, Q(3, 4), 1):
            self.assertEqual(density.value(mu), Q(3, 4) * (1 - mu**2))
        self.assertEqual(density.integral(), 1)
        self.assertEqual(density.integral(w0=0, w1=1), 0)
        self.assertEqual(density.integral(((0, 1),)), Q(1, 2))

    def test_23_positive_coefficient_policy(self):
        density = BernsteinDensity([0, 1, 3, 2, 0])
        for mu in (Q(k, 8) for k in range(-8, 9)):
            self.assertGreaterEqual(density.value(mu), 0)
            self.assertLessEqual(density.value(mu), density.maximum)
        for coefficients in ([], [0] * 10, [-1], [True]):
            with self.assertRaises(ContractError):
                BernsteinDensity(coefficients)

    def test_24_event_symmetry_boundary(self):
        asymmetric = BernsteinDensity([0, 1])
        result = aperture_integral(AngularMap(1, 0), asymmetric, (0, 1), delta=Q(1, 256))
        self.enclosed(result['integral'], Q(3, 4))
        with self.assertRaises(ContractError):
            pair_response(AngularMap(1, 0), asymmetric, (0, 1), (-1, 0))

    def test_25_signed_linear_weight_root_split(self):
        sets = SetBounds(((Q(-1, 4), Q(1, 4)),), ((Q(-1, 2), Q(1, 2)),))
        result = self.uniform.bounds(sets, 0, 1)
        self.assertEqual(result.lower, Q(-3, 64))
        self.assertEqual(result.upper, Q(3, 64))
        self.assertEqual(result.width, Q(3, 32))
        self.assertLessEqual(result.width, result.width_bound)
        self.assertEqual(self.uniform.bounds(sets, 0, -1), result)
        shifted = self.uniform.bounds(sets, Q(1, 8), 1)
        self.assertLessEqual(shifted.width, shifted.width_bound)

    def test_26_zero_density_short_circuit(self):
        density = BernsteinDensity([0, 0, 0])
        result = aperture_integral(self.folded, density, (Q(3, 5), Q(4, 5)))
        self.assertIsNone(result['preimage'])
        self.assertEqual(result['integral'].width, 0)
        pair = pair_response(self.folded, density, (-1, 0), (0, 1))
        self.assertIsNone(pair['preimage_a'])
        self.assertEqual(pair['coincidence'].upper, 0)
        with self.assertRaises(ContractError):
            aperture_integral(self.folded, density, (1, -1))

    def test_27_correlated_count_counterexample(self):
        result = pair_response(AngularMap(1, 0), self.uniform, (Q(1, 2), 1), (-1, Q(-1, 2)))
        for key in ('coincidence', 'hit_a', 'hit_b', 'inclusive_a', 'inclusive_b'):
            self.assertEqual(result[key].lower, Q(1, 2))
            self.assertEqual(result[key].upper, Q(1, 2))
        self.assertEqual(result['coincidence_daughters'].lower, 1)
        self.assertNotEqual(result['coincidence'].lower, result['hit_a'].lower * result['hit_b'].lower)

    def test_28_inclusive_count_and_detector_overlap(self):
        result = pair_response(AngularMap(1, 0), self.uniform, (-1, 1), (0, 0))
        self.assertEqual(result['hit_a'].lower, 1)
        self.assertEqual(result['inclusive_a'].lower, 2)
        self.assertEqual(result['coincidence'].upper, 0)
        with self.assertRaises(ContractError):
            pair_response(AngularMap(1, 0), self.uniform, (-1, Q(1, 2)), (0, 1))

    def test_29_exchange_and_shared_energy_integrand(self):
        args = (self.folded, self.uniform, (Q(3, 5), Q(4, 5)), (Q(4, 5), 1))
        result = pair_response(*args, delta=Q(1, 2**16), energy0=3, energy1=2)
        swapped = pair_response(args[0], args[1], args[3], args[2], delta=Q(1, 2**16), energy0=3, energy1=2)
        self.assertEqual(result['coincidence'], swapped['coincidence'])
        self.assertEqual(result['pair_energy_MeV'], result['coincidence'].scaled(6))
        separate = result['selected_plus_energy_MeV'].added(result['selected_minus_energy_MeV'])
        direct = result['pair_energy_MeV']
        self.assertLessEqual(separate.lower, direct.lower)
        self.assertGreaterEqual(separate.upper, direct.upper)

    def test_30_boolean_event_partition_and_error_ceiling(self):
        delta = Q(1, 2**16)
        result = pair_response(self.folded, self.uniform, (Q(3, 5), Q(4, 5)), (Q(4, 5), 1), delta=delta)
        y, ha, hb = result['coincidence'], result['hit_a'], result['hit_b']
        self.assertLessEqual(y.lower, min(ha.upper, hb.upper))
        for key in ('coincidence', 'hit_a', 'hit_b'):
            self.assertLessEqual(result[key].uncertainty_length, 16 * delta)
            self.assertLessEqual(result[key].width, 16 * self.uniform.maximum * delta)
        inner, outer = result['coincidence_sets'].inner, result['coincidence_sets'].outer
        self.assertEqual(union(inner, difference(FULL, inner)), FULL)
        self.assertEqual(intersection(inner, difference(FULL, outer)), ())
        self.assertLessEqual(16 * self.uniform.maximum * self.uniform.default_delta(), self.uniform.sigma / 2**40)

    def test_31_convergence_8_16_24_40(self):
        previous = None
        for bits in (8, 16, 24, 40):
            result = aperture_integral(self.folded, self.uniform, (Q(3, 5), Q(4, 5)), delta=Q(1, 2**bits))
            mass, sets = result['integral'], result['preimage'].sets
            self.assertLessEqual(mass.lower**2, Q(7, 25))
            self.assertLessEqual(Q(7, 25), mass.upper**2)
            if previous:
                prior_mass, prior_sets = previous
                self.assertGreaterEqual(mass.lower, prior_mass.lower)
                self.assertLessEqual(mass.upper, prior_mass.upper)
                self.assertLess(mass.width, prior_mass.width)
                self.assertFalse(difference(prior_sets.inner, sets.inner))
                self.assertFalse(difference(sets.outer, prior_sets.outer))
            previous = mass, sets

    def test_32_native_parameters_and_new_saved_payload(self):
        source = ROOT / 'sources/ANGULAR06_SAVED_PLOT_DATA.json'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), SOURCE_SHA256)
        payload = build_payload()
        self.assertEqual(len(payload['native_parameters']), 12)
        self.assertFalse(payload['empirical_DCS_used'])
        self.assertFalse(payload['old_scientific_kernels_called'])
        self.assertEqual(payload['source_columns_used'], ['source_row', 'gamma', 'a'])
        for row in payload['native_parameters']:
            for name in ('coincidence', 'hit_a', 'hit_b', 'inclusive_a', 'inclusive_b'):
                value = row[name]
                self.assertLessEqual(Q(value['lower']['rational']), Q(value['upper']['rational']))
                self.assertGreaterEqual(Q(value['lower']['rational']), 0)
            self.assertLessEqual(Q(row['coincidence']['upper']['rational']), 1)
        path = save_payload(payload)
        self.assertEqual(json.loads(path.read_text()), payload)


if __name__ == '__main__':
    unittest.main(verbosity=2)
