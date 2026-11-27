"""Independent defining-series and output audit of the new PHYS72 bound code.

This does not run the implementation's test suite or any old science campaign.
It compares against inverse-minus-finite-polynomial identities, rather than
copying the implementation's closed tail expression.
"""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "implementation" / "bounds.py"
SPEC = importlib.util.spec_from_file_location("phys72_independent_subject", SOURCE)
b = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = b
SPEC.loader.exec_module(b)


def run():
    # Constants reconstructed from the fixed physical theorem, not imported
    # from the subject module. All arithmetic comparisons remain exact.
    delta = Q(3, 10**23)
    c = Q(253, 1000)
    q = c * 27**2 * delta
    prefactor = Q(77)**2 * delta / 2
    checks = []

    def check(name, result):
        if not result:
            raise AssertionError(name)
        checks.append({"name": name, "result": "PASS_SCOPED"})

    check("constant_q_from_physical_parameters", b.Q_UPPER == q)
    check("strict_positive_root_witness", 27*c*c-Q(20, 7)*c-1 == Q(37701, 7000000))

    for label, lam in [("zero", Q(0)), ("one", Q(1)),
                       ("half_radius", 1/(2*q)), ("three_quarter_radius", 3/(4*q))]:
        # Scalar model S=q, B_-^*B_+=prefactor has a known exact inverse.
        inverse_response = prefactor * lam / (1-lam*q)
        polynomial = Q(0)
        term = prefactor * lam
        for n in range(1, 8):
            polynomial += term
            if n in (1, 3, 7):
                actual = b.born_remainder_bound(n, lam)
                check(f"inverse_minus_polynomial_{label}_N{n}",
                      actual.remainder_upper == inverse_response-polynomial)
            term *= lam*q

    for label, lam in [("critical", 1/q), ("above", 2/q)]:
        result = b.born_remainder_bound(3, lam).as_dict()
        check(f"strict_critical_guard_{label}",
              result["status"] == "SUFFICIENT_CONDITION_NOT_MET"
              and result["remainder_upper"] is None
              and "does not decide" in result["interpretation"])

    radius_display = Q(Decimal(b.rational_record(1/q)["upper_decimal"]))
    check("upward_radius_display_is_not_used_for_admission",
          radius_display >= 1/q and
          b.born_remainder_bound(3, radius_display).remainder_upper is None)

    old_limit = sys.get_int_max_str_digits()
    large = Q(10**5200+17, 10**10500+31)
    large_record = b.rational_record(large)
    recovered = Q(Decimal(large_record["numerator"]))/Q(Decimal(large_record["denominator"]))
    check("large_rational_record_preserves_exact_value_and_limit",
          recovered == large and sys.get_int_max_str_digits() == old_limit)
    check("large_rational_display_is_outward",
          Q(Decimal(large_record["upper_decimal"])) >= large)

    # Angular growth is explicitly unbounded; the selected external product
    # is a different object. Compare the exact difference at a very large j.
    j = 10**8
    check("angular_weight_unbounded_affine_difference",
          b.c_j(j+1)-b.c_j(j) == Q(800, 189))
    check("finite_external_product_only",
          b.c_j(20)*b.c_j(21) == 5929 and b.c_j(j)**2 > 5929)

    # The code's same-space defect estimate is checked through exact residual
    # inversion in the scalar extremal model, with nontrivial contraction.
    lam, rho = Q(3, 4)/q, Q(7, 13)
    rec = b.defect_bound(rho, lam)["error_upper"]
    actual = Q(Decimal(rec["numerator"]))/Q(Decimal(rec["denominator"]))
    check("defect_same_space_inverse", (1-lam*q)*actual == rho)

    return {
        "schema": "PHYS72_INDEPENDENT_EXACT_CODE_AUDIT_V1",
        "status": "PASS_SCOPED",
        "scope": "PHYS72 exact sufficient-bound implementation only",
        "source": {"path": str(SOURCE.relative_to(ROOT)),
                   "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
        "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "checks": checks,
        "checks_count": len(checks),
        "legacy_suites_replayed": 0,
        "physical_integrations": 0,
        "Coulomb_function_evaluations": 0,
        "HH_R10": "OFF",
    }


if __name__ == "__main__":
    result = run()
    payload = json.dumps(result, indent=2)+"\n"
    if len(sys.argv) == 2:
        with Path(sys.argv[1]).open("x", encoding="utf-8") as output:
            output.write(payload)
    else:
        print(payload, end="")
