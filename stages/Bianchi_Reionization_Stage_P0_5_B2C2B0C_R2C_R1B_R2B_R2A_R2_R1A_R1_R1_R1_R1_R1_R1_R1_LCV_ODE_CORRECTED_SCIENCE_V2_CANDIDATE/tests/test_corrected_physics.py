from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))

import corrected_physics as cp
import verified_backend as vb


def _ratio(numerator: int, denominator: int = 1) -> vb.ExactScalar:
    result = vb.exact_scalar_from_ratio(numerator, denominator)
    if result.status is not vb.NumericStatus.OK:
        raise AssertionError(result)
    return result.value


class CorrectedPhysicsTests(unittest.TestCase):
    def test_pure_heii_has_exactly_one_per_h_helium_factor(self) -> None:
        yhe = vb.exact_scalar_from_decimal_text("0.079").value
        result = cp.atomic_opacity_per_h(
            absorber_counts=(_ratio(0), _ratio(0), yhe),
            hydrogen_nuclei_total=_ratio(1),
            sigma_cm2=(_ratio(0), _ratio(0), _ratio(1)),
            geometric_scale=_ratio(1),
            helium_nuclei_total=yhe,
            declared_yhe=yhe,
        )
        self.assertEqual(result.status, cp.PhysicsStatus.OK)
        self.assertEqual(result.raw_exact, (Fraction(0), Fraction(0), Fraction(79, 1000)))
        self.assertNotEqual(result.raw_exact[2], Fraction(79, 1000) ** 2)

    def test_pure_absorber_and_mixed_shares_are_direct_and_exact(self) -> None:
        pure = cp.direct_opacity_partition(
            owner_names=("HI", "HeI", "HeII"),
            raw_opacity=(_ratio(0), _ratio(0), _ratio(9)),
        )
        self.assertEqual(pure.status, cp.PhysicsStatus.OK)
        self.assertEqual(pure.shares_exact, (Fraction(0), Fraction(0), Fraction(1)))

        mixed = cp.direct_opacity_partition(
            owner_names=("HI", "HeI", "HeII"),
            raw_opacity=(_ratio(2), _ratio(3), _ratio(5)),
        )
        self.assertEqual(mixed.shares_exact, (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)))
        self.assertEqual(sum(mixed.shares_exact), Fraction(1))
        self.assertTrue(all(value >= 0 for value in mixed.shares_exact))

    def test_share_partition_is_invariant_under_common_scale(self) -> None:
        first = cp.direct_opacity_partition(
            owner_names=("a", "b", "c"),
            raw_opacity=(_ratio(2), _ratio(3), _ratio(5)),
        )
        scaled = cp.direct_opacity_partition(
            owner_names=("a", "b", "c"),
            raw_opacity=(_ratio(14), _ratio(21), _ratio(35)),
        )
        self.assertEqual(first.shares_exact, scaled.shares_exact)

    def test_share_partition_is_owner_permutation_equivariant(self) -> None:
        first = cp.direct_opacity_partition(
            owner_names=("a", "b", "c"),
            raw_opacity=(_ratio(2), _ratio(3), _ratio(5)),
        )
        permuted = cp.direct_opacity_partition(
            owner_names=("c", "a", "b"),
            raw_opacity=(_ratio(5), _ratio(2), _ratio(3)),
        )
        self.assertEqual(permuted.shares_exact, (first.shares_exact[2], first.shares_exact[0], first.shares_exact[1]))

    def test_zero_opacity_vacuum_and_inconsistent_current_are_distinct(self) -> None:
        vacuum = cp.direct_opacity_partition(
            owner_names=("HI", "HeI", "HeII"),
            raw_opacity=(_ratio(0), _ratio(0), _ratio(0)),
            authoritative_current=_ratio(0),
        )
        self.assertEqual(vacuum.status, cp.PhysicsStatus.ZERO_OPACITY_VACUUM)
        self.assertIsNone(vacuum.shares_exact)

        inconsistent = cp.direct_opacity_partition(
            owner_names=("HI", "HeI", "HeII"),
            raw_opacity=(_ratio(0), _ratio(0), _ratio(0)),
            authoritative_current=_ratio(1),
        )
        self.assertEqual(
            inconsistent.status,
            cp.PhysicsStatus.NONZERO_CURRENT_WITH_ZERO_OPACITY,
        )
        self.assertIsNone(inconsistent.shares_exact)

    def test_hydrogen_reference_vacuum_negative_population_and_yhe_mismatch_are_typed(self) -> None:
        common = dict(
            sigma_cm2=(_ratio(1), _ratio(1), _ratio(1)),
            geometric_scale=_ratio(1),
        )
        vacuum = cp.atomic_opacity_per_h(
            absorber_counts=(_ratio(0), _ratio(0), _ratio(0)),
            hydrogen_nuclei_total=_ratio(0),
            **common,
        )
        self.assertEqual(vacuum.status, cp.PhysicsStatus.HYDROGEN_REFERENCE_VACUUM)

        negative = cp.atomic_opacity_per_h(
            absorber_counts=(_ratio(-1), _ratio(0), _ratio(0)),
            hydrogen_nuclei_total=_ratio(1),
            **common,
        )
        self.assertEqual(negative.status, cp.PhysicsStatus.NEGATIVE_POPULATION)

        yhe = vb.exact_scalar_from_decimal_text("0.079").value
        mismatch = cp.atomic_opacity_per_h(
            absorber_counts=(_ratio(1), _ratio(0), _ratio(0)),
            hydrogen_nuclei_total=_ratio(1),
            helium_nuclei_total=_ratio(1, 10),
            declared_yhe=yhe,
            **common,
        )
        self.assertEqual(mismatch.status, cp.PhysicsStatus.ABUNDANCE_CONVENTION_MISMATCH)

    def test_nonfinite_raw_float_differs_from_finite_untagged_float(self) -> None:
        nonfinite = cp.atomic_opacity_per_h(
            absorber_counts=(float("nan"), _ratio(0), _ratio(0)),
            hydrogen_nuclei_total=_ratio(1),
            sigma_cm2=(_ratio(1), _ratio(1), _ratio(1)),
            geometric_scale=_ratio(1),
        )
        self.assertEqual(nonfinite.status, cp.PhysicsStatus.NONFINITE_INPUT)

        finite_untagged = cp.direct_opacity_partition(
            owner_names=("HI",),
            raw_opacity=(1.0,),
        )
        self.assertEqual(
            finite_untagged.status,
            cp.PhysicsStatus.AMBIGUOUS_NUMERIC_PROVENANCE,
        )

        infinite = cp.direct_opacity_partition(
            owner_names=("HI",),
            raw_opacity=(float("inf"),),
        )
        self.assertEqual(infinite.status, cp.PhysicsStatus.NONFINITE_INPUT)

    def test_trace_opacity_is_retained_exactly_across_binary64_underflow(self) -> None:
        trace = _ratio(1, 1 << 1075)
        result = cp.atomic_opacity_per_h(
            absorber_counts=(trace, _ratio(0), _ratio(0)),
            hydrogen_nuclei_total=_ratio(1),
            sigma_cm2=(_ratio(1), _ratio(0), _ratio(0)),
            geometric_scale=_ratio(1),
        )
        self.assertEqual(result.status, cp.PhysicsStatus.OK)
        self.assertEqual(result.raw_exact[0], Fraction(1, 1 << 1075))
        self.assertEqual(result.raw_binary64[0].lo, 0.0)
        self.assertEqual(result.raw_binary64[0].hi, float.fromhex("0x0.0000000000001p-1022"))


if __name__ == "__main__":
    unittest.main()
