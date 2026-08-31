from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
import unittest


STAGE = Path(__file__).resolve().parents[1]
RESEARCH = STAGE / "research" / "noncode_math_20260831"


def solve2(matrix: tuple[tuple[Q, Q], tuple[Q, Q]], rhs: tuple[Q, Q]) -> tuple[Q, Q]:
    (a, b), (c, d) = matrix
    det = a * d - b * c
    if det == 0:
        raise ZeroDivisionError("singular exact fixture")
    x = (d * rhs[0] - b * rhs[1]) / det
    y = (-c * rhs[0] + a * rhs[1]) / det
    return x, y


class NoncodeFormulaContractTests(unittest.TestCase):
    def test_local_manifest_and_external_member_bytes_are_closed(self) -> None:
        seen: set[str] = set()
        for line in (RESEARCH / "MANIFEST.sha256").read_text(encoding="ascii").splitlines():
            digest, name = line.split("  ", 1)
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertNotIn(name, seen)
            seen.add(name)
            raw = (RESEARCH / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
        self.assertEqual(len(seen), 7)

    def test_external_wolfram_receipt_does_not_promote_numerical_status(self) -> None:
        receipt = json.loads((RESEARCH / "WOLFRAM_VERIFICATION_RECEIPT.json").read_bytes())
        intake = json.loads((RESEARCH / "INTAKE.json").read_bytes())
        self.assertTrue(receipt["all_pass"])
        self.assertEqual(len(receipt["checks"]), 18)
        self.assertIn("not an all-node interval certificate", receipt["qualification"])
        self.assertEqual(intake["executor_replay"]["wolfram_18_checks"], "NOT_RUN_TOOL_NOT_ON_PATH")
        self.assertEqual(intake["scientific_status"], "NO_PASS_FIRST_CANONICAL_INTERVAL")

    def test_public_helium_difference_identities_are_exact(self) -> None:
        values = (Q(0), Q(1, 7), Q(2, 3), Q(1))
        for qh, qf, rh, rf in itertools.product(values, repeat=4):
            qb, rb = (qh + qf) / 2, (rh + rf) / 2
            dq, dr = qh - qf, rh - rf
            self.assertEqual(qh * rh - qf * rf, qb * dr + rb * dq)
            self.assertEqual(
                qh * (1 - rh) - qf * (1 - rf),
                (1 - rb) * dq - qb * dr,
            )

    def test_ots_photon_identity_is_exact(self) -> None:
        ell, m = Q(57, 40), Q(737, 1000)
        values = (Q(0), Q(1, 4), Q(3, 5), Q(1))
        for v, f, y, z in itertools.product(values, repeat=4):
            w = (ell - m) + m * y
            ah = v * w + (1 - v) * f * z
            ahe = v * m * (1 - y) + (1 - v) * f * (1 - z)
            self.assertEqual(ah + ahe + v * (2 - ell) + (1 - v) * (1 - f), 1 + v)

    def test_normalized_measure_first_and_second_variations_sum_to_zero(self) -> None:
        h = (Q(2), Q(3), Q(5))
        u = (Q(1), Q(-2), Q(4))
        v = (Q(-3), Q(1), Q(2))
        total = sum(h)
        du = sum(u)
        dv = sum(v)
        first = tuple(u[i] / total - h[i] * du / total**2 for i in range(3))
        second = tuple(
            -(u[i] * dv + v[i] * du) / total**2
            + 2 * h[i] * du * dv / total**3
            for i in range(3)
        )
        self.assertEqual(sum(first), 0)
        self.assertEqual(sum(second), 0)

    def test_implicit_tangent_requires_delta_a(self) -> None:
        matrix = ((Q(2), Q(1)), (Q(1), Q(3)))
        z = solve2(matrix, (Q(1), Q(2)))
        delta_a = ((Q(1), Q(0)), (Q(0), Q(-1)))
        delta_b = (Q(1), Q(-1))
        rhs = (
            delta_b[0] - delta_a[0][0] * z[0] - delta_a[0][1] * z[1],
            delta_b[1] - delta_a[1][0] * z[0] - delta_a[1][1] * z[1],
        )
        self.assertEqual(z, (Q(1, 5), Q(3, 5)))
        self.assertEqual(solve2(matrix, rhs), (Q(14, 25), Q(-8, 25)))
        self.assertEqual(solve2(matrix, delta_b), (Q(4, 5), Q(-3, 5)))
        self.assertNotEqual(solve2(matrix, rhs), solve2(matrix, delta_b))

    def test_mixed_rhs_uses_all_three_matrix_products(self) -> None:
        matrix = ((Q(2), Q(-1)), (Q(-1), Q(1)))
        full_rhs = (Q(-7), Q(3))
        products = ((Q(1), Q(2)), (Q(11), Q(7)), (Q(8), Q(5)))
        self.assertEqual((Q(13) - sum(p[0] for p in products), Q(17) - sum(p[1] for p in products)), full_rhs)
        self.assertEqual(solve2(matrix, full_rhs), (Q(-4), Q(-1)))
        self.assertEqual(
            [solve2(matrix, (full_rhs[0] + p[0], full_rhs[1] + p[1])) for p in products],
            [(Q(-1), Q(4)), (Q(14), Q(24)), (Q(9), Q(17))],
        )

    def test_two_by_two_krawczyk_corner_hull_is_strict(self) -> None:
        c = ((Q(2, 3), Q(1, 3)), (Q(1, 3), Q(2, 3)))
        w = (Q(-3, 4), Q(-3, 8))
        box = ((Q(-9, 4), Q(3, 4)), (Q(-9, 8), Q(3, 8)))
        values: tuple[list[Q], list[Q]] = ([], [])
        for a, rhs0, x0, x1 in itertools.product(
            (Q(3, 2), Q(5, 2)), (Q(-3, 2), Q(-3, 4)), box[0], box[1]
        ):
            matrix = ((a, Q(-1)), (Q(-1), Q(2)))
            residual = (matrix[0][0] * w[0] + matrix[0][1] * w[1] - rhs0,
                        matrix[1][0] * w[0] + matrix[1][1] * w[1])
            correction = (c[0][0] * residual[0] + c[0][1] * residual[1],
                          c[1][0] * residual[0] + c[1][1] * residual[1])
            ca = tuple(tuple(sum(c[i][k] * matrix[k][j] for k in range(2)) for j in range(2)) for i in range(2))
            dx = (x0 - w[0], x1 - w[1])
            image = tuple(
                w[i] - correction[i] + sum(((Q(1) if i == j else Q(0)) - ca[i][j]) * dx[j] for j in range(2))
                for i in range(2)
            )
            values[0].append(image[0])
            values[1].append(image[1])
        hull = ((min(values[0]), max(values[0])), (min(values[1]), max(values[1])))
        self.assertEqual(hull, ((Q(-7, 4), Q(1, 4)), (Q(-7, 8), Q(1, 8))))
        self.assertEqual((hull[0][0] - box[0][0], box[0][1] - hull[0][1]), (Q(1, 2), Q(1, 2)))
        self.assertEqual((hull[1][0] - box[1][0], box[1][1] - hull[1][1]), (Q(1, 4), Q(1, 4)))

    def test_mprk_columns_are_conservative_with_unit_dominance_margin(self) -> None:
        p = ((Q(0), Q(2), Q(3)), (Q(5), Q(0), Q(7)), (Q(11), Q(13), Q(0)))
        d = (Q(17), Q(19), Q(23))
        h = Q(5, 7)
        g = [[Q(0) for _ in range(3)] for _ in range(3)]
        for source in range(3):
            for destination in range(3):
                if destination != source:
                    g[destination][source] = p[destination][source] / d[source]
            g[source][source] = -sum(g[destination][source] for destination in range(3) if destination != source)
        a = [[(Q(1) if i == j else Q(0)) - h * g[i][j] for j in range(3)] for i in range(3)]
        for source in range(3):
            self.assertEqual(sum(g[destination][source] for destination in range(3)), 0)
            self.assertEqual(sum(a[destination][source] for destination in range(3)), 1)
            self.assertEqual(a[source][source] - sum(abs(a[destination][source]) for destination in range(3) if destination != source), 1)


if __name__ == "__main__":
    unittest.main()
