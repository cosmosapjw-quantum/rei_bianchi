"""Focused new representation controls; old suites are not imported."""
import unittest
from fractions import Fraction as Q
from atomic_storage import (CHI, ENERGY, FINE, SOURCE_PIN, SOURCE_SHA256, SOURCE_BLOB,
                            coarse_mapping, energy_lift, right_proper,
                            linearization, rational, source_guard)
from atomic_storage import endpoint_split, conditional_abundance, conditional_abundance_jvp

MATCH = (('H1I', 1), ('H1II', 2))


class AtomicStorageTests(unittest.TestCase):
    def coarse(self, values):
        return coarse_mapping(tuple(Q(value) for value in values), fine_order=FINE, native_mapping=MATCH)

    def test_lya_internal_storage_and_photon(self):
        result = self.coarse((1, 0, -1, 0))
        self.assertEqual((result.neutral, result.ion, result.thermal_electrons), (Q(0),) * 3)
        energies = (Q(0), Q(-7), Q(0), Q(0), Q(7))
        lift = energy_lift(energies, Q(0), chi=CHI, energy_order=ENERGY)
        self.assertEqual((lift.hidden_atomic_storage, lift.source_sum), (Q(-7), Q(0)))

    def test_recombination_has_thermal_not_fast_electrons(self):
        result = self.coarse((0, 0, 1, -1))
        self.assertEqual((result.neutral, result.ion, result.thermal_electrons, result.fast_zeta),
                         (Q(1), Q(-1), Q(-1), Q(0)))

    def test_linear_coarse_and_baryon_residual(self):
        a, b = (Q(2), Q(-3), Q(5), Q(-4)), (Q(1, 3), Q(2, 3), Q(-1), Q(0))
        combined = self.coarse(tuple(2 * x - y for x, y in zip(a, b)))
        first, second = self.coarse(a), self.coarse(b)
        self.assertEqual(combined.neutral, 2 * first.neutral - second.neutral)
        self.assertEqual(combined.baryon_residual, sum((2 * x - y for x, y in zip(a, b)), Q(0)))

    def test_hidden_convention_and_excited_storage(self):
        values = (Q(2), Q(11), Q(3), Q(-5), Q(7))
        first = energy_lift(values, Q(2), chi=Q(3), energy_order=ENERGY)
        second = energy_lift(values, Q(2), chi=Q(4), energy_order=ENERGY)
        self.assertEqual((first.hidden_atomic_storage, second.hidden_atomic_storage), (Q(5), Q(3)))
        self.assertEqual(first.mapped_sum, second.source_sum)
        self.assertEqual(first.direct_source, values)

    def test_nonzero_residual_is_not_clipped(self):
        tiny = Q(1, 10 ** 70)
        result = self.coarse((Q(1), Q(0), tiny, Q(-1)))
        self.assertEqual(result.baryon_residual, tiny)
        energies = (Q(0), tiny, Q(0), Q(0), Q(0))
        self.assertEqual(energy_lift(energies, Q(0), chi=CHI, energy_order=ENERGY).source_sum, tiny)

    def test_right_proper_volume(self):
        self.assertEqual(right_proper((Q(3), Q(-6)), Q(3, 2)), (Q(2), Q(-4)))

    def test_directional_derivative(self):
        coarse, hidden = linearization((Q(1), Q(2), Q(-4), Q(5)), Q(7),
                                       chi=Q(3), dchi=Q(2), continuum=Q(11))
        self.assertEqual(coarse, (Q(-1), Q(5), Q(5)))
        self.assertEqual(hidden, Q(-30))

    def test_exact_numeric_types(self):
        for bad in (True, 1, 1.0, None):
            with self.assertRaises(TypeError):
                rational(bad)
        self.assertEqual(rational('1.602176634e-19'), Q('1.602176634e-19'))
        with self.assertRaises(TypeError):
            coarse_mapping((Q(0), Q(0), Q(0), 0), fine_order=FINE, native_mapping=MATCH)

    def test_dimension_order_and_h1_owner_guards(self):
        with self.assertRaises(ValueError):
            coarse_mapping((Q(0),) * 3, fine_order=FINE, native_mapping=MATCH)
        with self.assertRaises(ValueError):
            coarse_mapping((Q(0),) * 4, fine_order=tuple(reversed(FINE)), native_mapping=MATCH)
        with self.assertRaises(ValueError):
            coarse_mapping((Q(0),) * 4, fine_order=FINE, native_mapping=(('H1I', 2), ('H1II', 1)))
        with self.assertRaises(ValueError):
            energy_lift((Q(0),) * 5, Q(0), chi=CHI, energy_order=tuple(reversed(ENERGY)))

    def test_volume_and_threshold_guards(self):
        for ratio in (Q(0), Q(-1)):
            with self.assertRaises(ValueError):
                right_proper((Q(1),), ratio)
        with self.assertRaises(TypeError):
            right_proper((Q(1),), 1)
        with self.assertRaises(ValueError):
            energy_lift((Q(0),) * 5, Q(0), chi=Q(0), energy_order=ENERGY)

    def test_source_identity_guard(self):
        args = dict(source_pin=SOURCE_PIN, sha256=SOURCE_SHA256, git_blob=SOURCE_BLOB, byte_count=3554206)
        source_guard(**args)
        for field in args:
            altered = dict(args)
            altered[field] = 'wrong'
            with self.assertRaises(ValueError):
                source_guard(**altered)

    def test_immutable_result_and_declared_target_chi(self):
        result = self.coarse((0, 0, 0, 0))
        with self.assertRaises(AttributeError):
            result.neutral = Q(1)
        self.assertEqual(CHI, Q('13.6') * Q('1.602176634e-19'))

    def test_proper_endpoint_volume_and_saved_residual_split(self):
        initial = (Q(2), Q(0), Q(0), Q(2))
        final = (Q(6), Q(0), Q(0), Q(6))
        events = (Q(3), Q(0), Q(0), Q(3))
        actual, event, volume, residual = endpoint_split(initial, final, events, Q(2))
        self.assertEqual(actual, (Q(1),) * 3)
        self.assertEqual(event, (Q(3, 2),) * 3)
        self.assertEqual(volume, (Q(-1),) * 3)
        self.assertEqual(residual, (Q(1, 2),) * 3)
        self.assertEqual(actual, tuple(a + b + c for a, b, c in zip(event, volume, residual)))

    def test_both_b_and_volume_jvp_all_directions_nonzero(self):
        initial, final = (Q(2), Q(0), Q(0), Q(2)), (Q(6), Q(0), Q(0), Q(6))
        d_initial, d_final = (Q(3), Q(0), Q(0), Q(3)), (Q(5), Q(0), Q(0), Q(5))
        self.assertEqual(conditional_abundance(initial, final, ratio=Q(2), b_a=Q(3), b_b=Q(4)),
                         (Q(1, 12),) * 3)
        result = conditional_abundance_jvp(initial, final, d_initial, d_final,
                                           ratio=Q(2), b_a=Q(3), b_b=Q(4),
                                           d_ratio=Q(1), d_b_a=Q(2), d_b_b=Q(3))
        self.assertEqual(result, (Q(-125, 144),) * 3)


if __name__ == '__main__':
    unittest.main()
