"""Exact PHYS72 scalar bounds for the actual outgoing Coulomb exterior problem.

The theorem and its assumptions live in the sibling theory documents.  This
module evaluates their sufficient conditions; it does not sample a radial or
angular operator, integrate a Born coefficient, or substitute a finite-L norm.

Atomic coordinates are retained: B=27 a0, k=7/(10 a0), E=49/200 Hartree,
V=2(1+1/d) exp(-2d), d=|x-0.7 zhat|, A0=2 h_C-k^2, and Z=+u'(B)u(B)^-1.
All numerical decisions below use Fraction.  Decimal is only an outward display.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


B = Fraction(27)
K = Fraction(7, 10)
ENERGY = Fraction(49, 200)
ETA_COULOMB = Fraction(-10, 7)
SHIFT = Fraction(7, 10)
DELTA = Fraction(3, 10**23)
C_RESOLVENT_UPPER = Fraction(253, 1000)
V_WEIGHTED_UPPER = B**2 * DELTA
Q_UPPER = C_RESOLVENT_UPPER * V_WEIGHTED_UPPER
GAMMA_EXTERNAL = Fraction(5929)
POISSON_SANDWICH_NORM_SQUARED_UPPER = DELTA / 2
ENTRY_PREFACTOR = GAMMA_EXTERNAL * POISSON_SANDWICH_NORM_SQUARED_UPPER
FROZEN_NPZ_SHA256 = (
    "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
)
D3_CERTIFICATE_SHA256 = (
    "f75d082e1966dd61a326c37b6ff14e8f330e010341a59a88eb4ca8d4734e6173"
)
MAX_SEARCH_TERMS = 10000


def exact_nonnegative(value: Fraction | int | str, name: str) -> Fraction:
    """Parse exact input, rejecting bool/float and non-finite/negative values."""
    if isinstance(value, bool) or not isinstance(value, (Fraction, int, str)):
        raise TypeError(f"{name} must be Fraction, int, or an exact rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite rational") from exc
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def c_j(j: int) -> Fraction:
    """PHYS69/71 channel weight for every nonnegative j, without truncation.

    H_C has ||g||_HC^2 = sum_jm C_j^2 |g_jm|^2.  C_j grows linearly
    beyond 28.  Gamma_external=77^2 controls the chosen external entry;
    it is not a uniform-in-j propagator or angular multiplier norm.
    """
    if isinstance(j, bool) or not isinstance(j, int) or j < 0:
        raise ValueError("j must be a nonnegative integer")
    return Fraction(77) if j <= 28 else Fraction(800 * (j + 1), 189)


def resolvent_quadratic_witness(c: Fraction | int | str = C_RESOLVENT_UPPER) -> Fraction:
    """Nonnegative value proves c >= (10+sqrt(1423))/189 for c>=0."""
    c = exact_nonnegative(c, "c")
    return B * c * c - 2 * c / K - 1


def upward_decimal(value: Fraction | int | str, digits: int = 40) -> str:
    """Return a scientific decimal >= the exact nonnegative value.

    Decimal(int) is exact even when the active precision is smaller.  Thus the
    sole arithmetic rounding is the directed division under ROUND_CEILING.
    """
    value = exact_nonnegative(value, "value")
    positive_integer(digits, "digits")
    with localcontext() as ctx:
        ctx.prec = digits
        ctx.rounding = ROUND_CEILING
        result = Decimal(value.numerator) / Decimal(value.denominator)
    return format(result, "E")


def rational_record(value: Fraction | int | str, digits: int = 40) -> dict[str, str]:
    value = exact_nonnegative(value, "value")
    return {
        # Decimal(int) and its fixed-point formatting are exact.  This also
        # supports bounded high-order searches whose integers exceed Python's
        # configurable int-to-string digit limit, without changing that limit.
        "numerator": format(Decimal(value.numerator), "f"),
        "denominator": format(Decimal(value.denominator), "f"),
        "upper_decimal": upward_decimal(value, digits),
        "display_rounding": "ROUND_CEILING",
    }


@dataclass(frozen=True)
class RemainderBound:
    """Exact scalar theorem evaluation for the fixed (21,20),m=0 entry."""

    terms: int
    lambda_abs: Fraction
    contraction_upper: Fraction
    remainder_upper: Fraction | None
    status: str

    def as_dict(self, digits: int = 40) -> dict[str, Any]:
        return {
            "status": self.status,
            "terms_retained": self.terms,
            "first_omitted_power": self.terms + 1,
            "lambda_abs": rational_record(self.lambda_abs, digits),
            "contraction_upper": rational_record(self.contraction_upper, digits),
            "entry": {"ell": 21, "p": 20, "m": 0},
            "remainder_upper": (
                rational_record(self.remainder_upper, digits)
                if self.remainder_upper is not None
                else None
            ),
            "remainder_unit": "a0^-1",
            "criterion": "abs(lambda)*q_upper < 1",
            "interpretation": (
                "All-angular, all-radial DtN entry tail after N Born terms."
                if self.remainder_upper is not None
                else "This sufficient bound does not decide convergence or divergence."
            ),
        }


def born_remainder_bound(
    terms: int = 3, lambda_abs: Fraction | int | str = Fraction(1)
) -> RemainderBound:
    """Bound sum_(n>N) lambda^n D_n, N>=1, in the original fixed entry.

    ||sqrt(V) R0^+ sqrt(V)|| <= q and the weighted Coulomb Poisson
    estimate give Gamma_ext delta/2 * |lambda|^(N+1) q^N /(1-|lambda|q).
    N=3 is precisely the order>=4 remainder.  The condition is sufficient;
    no decision about actual divergence follows when it is not met.
    """
    positive_integer(terms, "terms")
    lam = exact_nonnegative(lambda_abs, "lambda_abs")
    contraction = lam * Q_UPPER
    if contraction >= 1:
        return RemainderBound(
            terms, lam, contraction, None, "SUFFICIENT_CONDITION_NOT_MET"
        )
    remainder = ENTRY_PREFACTOR * lam * contraction**terms / (1 - contraction)
    return RemainderBound(terms, lam, contraction, remainder, "SUFFICIENT_CONDITION_MET")


def minimum_terms(
    budget: Fraction | int | str,
    lambda_abs: Fraction | int | str = Fraction(1),
    max_terms: int = 256,
) -> dict[str, Any]:
    """Find the smallest N>=1 whose certified scalar tail meets a budget.

    The exact recurrence is monotone when its sufficient condition holds.
    A finite search exhaustion reports only that this search did not certify
    the requested budget; it is not a lower bound on the true error.
    """
    budget = exact_nonnegative(budget, "budget")
    positive_integer(max_terms, "max_terms")
    if max_terms > MAX_SEARCH_TERMS:
        raise ValueError(f"max_terms must not exceed {MAX_SEARCH_TERMS}")
    first = born_remainder_bound(1, lambda_abs)
    common: dict[str, Any] = {
        "budget": rational_record(budget),
        "budget_unit": "a0^-1",
        "max_terms": max_terms,
        "minimum_terms": None,
        "minimum_over": "positive integers N>=1",
    }
    if first.remainder_upper is None:
        return {
            **common,
            "status": "SUFFICIENT_CONDITION_NOT_MET",
            "last_bound": first.as_dict(),
        }
    if budget == 0 and first.lambda_abs > 0:
        return {
            **common,
            "status": "ZERO_BUDGET_NO_FINITE_CERTIFIED_TERM_COUNT",
            "last_bound": first.as_dict(),
            "interpretation": "The positive geometric upper bound never equals zero.",
        }
    current = first.remainder_upper
    for n in range(1, max_terms + 1):
        if current <= budget:
            return {
                **common,
                "status": "BUDGET_CERTIFIED",
                "minimum_terms": n,
                "bound": RemainderBound(
                    n, first.lambda_abs, first.contraction_upper,
                    current, "SUFFICIENT_CONDITION_MET",
                ).as_dict(),
            }
        if n < max_terms:
            current *= first.contraction_upper
    return {
        **common,
        "status": "TERM_SEARCH_LIMIT_REACHED",
        "last_bound": RemainderBound(
            max_terms, first.lambda_abs, first.contraction_upper,
            current, "SUFFICIENT_CONDITION_MET",
        ).as_dict(),
        "interpretation": "The sufficient upper bound remains above budget in this finite search.",
    }


def defect_bound(
    residual_norm_upper: Fraction | int | str,
    lambda_abs: Fraction | int | str = Fraction(1),
) -> dict[str, Any]:
    """Birman--Schwinger solution-space error from an actual residual bound.

    For (I-lambda S)z=b and residual b-(I-lambda S)z_tilde with norm <=rho,
    ||z-z_tilde|| <= rho/(1-|lambda|q).  No DtN trace conversion is inferred.
    The caller must supply a certified residual upper bound in the same space.
    """
    rho = exact_nonnegative(residual_norm_upper, "residual_norm_upper")
    contraction = exact_nonnegative(lambda_abs, "lambda_abs") * Q_UPPER
    common = {
        "residual_norm_upper": rational_record(rho),
        "contraction_upper": rational_record(contraction),
        "norm_space": "Birman-Schwinger L2(dr dOmega), z=sqrt(V)u",
        "error_unit": "same as supplied residual norm",
    }
    if contraction >= 1:
        return {**common, "status": "SUFFICIENT_CONDITION_NOT_MET", "error_upper": None}
    return {
        **common,
        "status": "SUFFICIENT_CONDITION_MET",
        "error_upper": rational_record(rho / (1 - contraction)),
    }


def verify_file_identity(path: str | Path, expected_sha256: str) -> dict[str, Any]:
    """Read-only byte identity check; identity alone makes no scientific claim."""
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(c not in "0123456789abcdef" for c in expected_sha256)
    ):
        raise ValueError("expected_sha256 must be 64 lowercase hexadecimal characters")
    path = Path(path)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
            size += len(block)
    actual = digest.hexdigest()
    return {
        "path": str(path.resolve()),
        "size_bytes": size,
        "expected_sha256": expected_sha256,
        "actual_sha256": actual,
        "status": "MATCH" if actual == expected_sha256 else "MISMATCH",
    }


def report(
    terms: int = 3,
    lambda_abs: Fraction | int | str = Fraction(1),
    budget: Fraction | int | str | None = None,
    max_terms: int = 256,
) -> dict[str, Any]:
    witness = resolvent_quadratic_witness()
    if witness < 0:
        raise ArithmeticError("The fixed rational resolvent bound failed its exact witness")
    result: dict[str, Any] = {
        "schema": "PHYS72_EXACT_WEIGHTED_BORN_BOUND_V1",
        "calculation": "exact rational evaluation of proved sufficient inequalities",
        "scope": "actual outgoing Dirichlet Coulomb exterior; all j and all r>=27",
        "model": {
            "coordinates": "atomic",
            "B_a0": "27",
            "k_a0_inverse": "7/10",
            "E_Hartree": "49/200",
            "shift_a0": "7/10",
            "A0": "2*h_C-k^2",
            "screened_multiplier": "V=2*(1+1/d)*exp(-2*d); d=abs(x-0.7*zhat)",
            "outgoing": "H_plus=G+i*F_C",
            "DtN_sign": "Z=+u_prime*u_inverse",
            "eta_C": "-10/7",
            "source_eta": "F*y",
            "source_xi": "F*y-phi",
        },
        "constants": {
            "delta": rational_record(DELTA),
            "resolvent_norm_upper": rational_record(C_RESOLVENT_UPPER),
            "resolvent_quadratic_witness": rational_record(witness),
            "weighted_multiplier_upper": rational_record(V_WEIGHTED_UPPER),
            "q_upper": rational_record(Q_UPPER),
            "sufficient_abs_lambda_open_radius": rational_record(1 / Q_UPPER),
            "external_entry_factor": rational_record(GAMMA_EXTERNAL),
            "weighted_Poisson_norm_squared_upper": rational_record(
                POISSON_SANDWICH_NORM_SQUARED_UPPER
            ),
        },
        "radius_membership_rule": (
            "Use the exact rational radius or abs(lambda)*q_upper<1; "
            "the upward decimal radius is a display and cannot enlarge the open disk."
        ),
        "angular_space": {
            "definition": "||g||_HC^2=sum_(j,m) C_j^2*abs(g_jm)^2",
            "C_j": "77 if 0<=j<=28; 800*(j+1)/189 if j>=29",
            "all_j": True,
            "finite_L_Gamma_replacement": False,
            "entry_vs_operator": "5929=C_21*C_20; it is not sup_j C_j^2",
        },
        "remainder": born_remainder_bound(terms, lambda_abs).as_dict(),
        "provenance": {
            "theorem_source": "research/hh_phys72_20261020/theory/",
            "angular_weight_source": "research/hh_phys71_20261020/theory/ANGULAR_D3.md",
            "frozen_npz_expected_sha256": FROZEN_NPZ_SHA256,
            "D3_certificate_expected_sha256": D3_CERTIFICATE_SHA256,
            "original_source_driven_xi": "separate unresolved obligation",
            "inherits_PHYS63": "qualitative actual all-angular LAP/Poisson/DtN",
            "inherits_PHYS69": "completed D2 coefficient",
            "inherits_PHYS71": "completed D3 coefficient; no integration replay",
        },
        "scientific_integrations": 0,
        "HH_R10": "OFF",
    }
    if budget is not None:
        result["term_budget"] = minimum_terms(budget, lambda_abs, max_terms)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", type=int, default=3)
    parser.add_argument("--lambda-abs", default="1", help="Exact rational absolute lambda")
    parser.add_argument("--budget", help="Optional nonnegative a0^-1 exact rational budget")
    parser.add_argument("--max-terms", type=int, default=256)
    parser.add_argument("--residual-norm", help="Optional certified Birman-Schwinger residual norm")
    parser.add_argument("--frozen-npz", type=Path)
    parser.add_argument("--d3-certificate", type=Path)
    parser.add_argument("--output", type=Path, help="Create-only JSON output; default stdout")
    args = parser.parse_args(argv)
    try:
        result = report(args.terms, args.lambda_abs, args.budget, args.max_terms)
        if args.residual_norm is not None:
            result["defect"] = defect_bound(args.residual_norm, args.lambda_abs)
        identities = []
        for path, expected in (
            (args.frozen_npz, FROZEN_NPZ_SHA256),
            (args.d3_certificate, D3_CERTIFICATE_SHA256),
        ):
            if path is not None:
                identities.append(verify_file_identity(path, expected))
        result["input_identity_checks"] = identities
        result["input_identity_status"] = (
            "MATCH" if identities and all(x["status"] == "MATCH" for x in identities)
            else "MISMATCH" if identities
            else "NOT_REQUESTED"
        )
        if result["input_identity_status"] == "MISMATCH":
            result["adoption_status"] = "BLOCKED_INPUT_IDENTITY_MISMATCH"
        else:
            result["adoption_status"] = "BOUND_EVALUATED_WITH_STATED_PROVENANCE"
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output is None:
            print(encoded, end="")
        else:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        return 2 if result["input_identity_status"] == "MISMATCH" else 0
    except (ValueError, TypeError, OSError, ArithmeticError) as exc:
        parser.exit(2, f"PHYS72 input/output error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
