#!/usr/bin/env python3
"""Small, synthetic algebra checks for an HE29 candidate linear-solve adapter.

This file does not execute the HE29 RHS, native integrator, historical suites,
or a physical thermochemistry experiment. Gas dimension is four.

For J = [[-K,U],[V,G]], a = gamma*h >= 0:
    D = I + a*K
    S = I - a*G - a*a*V*D^-1*U
    du = solve(S, bu + a*V*D^-1*bq)
    dq = D^-1*(bq + a*U*du).

Related primary source: Brown & Woodward (2001), SISC 23(2), 499-516,
doi:10.1137/S106482750037295X, section 5.2.
The source studies radiation diffusion preconditioning. The present arrowhead
specialization is direct block algebra, not reuse of its performance claims.
"""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np


GAS_DIM = 4
RESIDUAL_LIMIT = 5e-13
SOLUTION_DIFF_LIMIT = 2e-10
RCOND_MIN = 1e-12


class SchurContractError(ValueError):
    """Input dimension, domain, or finite-value contract was violated."""


class SchurNumericalError(ArithmeticError):
    """A finite candidate system fails the declared conditioning boundary."""


def arrowhead_solve(kappa, upper, lower, gas, rhs, a, rcond_min=RCOND_MIN):
    """Solve a dimensionless stage matrix without forming its full dense form."""
    kappa, upper, lower, gas, rhs = (
        np.asarray(x, dtype=np.float64) for x in (kappa, upper, lower, gas, rhs)
    )
    if kappa.ndim != 1 or kappa.size == 0:
        raise SchurContractError("kappa must be a nonempty vector")
    n = kappa.size
    if (upper.shape, lower.shape, gas.shape, rhs.shape) != (
        (n, GAS_DIM), (GAS_DIM, n), (GAS_DIM, GAS_DIM), (n + GAS_DIM,)
    ):
        raise SchurContractError("expected photon N and gas 4 block shapes")
    if not np.isfinite(a) or a < 0:
        raise SchurContractError("a = gamma*h must be finite and nonnegative")
    if not np.isfinite(rcond_min) or not 0 < rcond_min < 1:
        raise SchurContractError("rcond_min must lie in (0,1)")
    if not all(np.all(np.isfinite(x)) for x in (kappa, upper, lower, gas, rhs)):
        raise SchurContractError("nonfinite block input")
    if np.any(kappa < 0):
        raise SchurContractError("negative absorption")
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            diagonal = 1.0 + a * kappa
            inv_upper = upper / diagonal[:, None]
            inv_rhs = rhs[:n] / diagonal
            schur = np.eye(GAS_DIM) - a * gas - a * a * (lower @ inv_upper)
            reduced_rhs = rhs[n:] + a * (lower @ inv_rhs)
    except FloatingPointError as exc:
        raise SchurNumericalError("nonfinite Schur assembly") from exc
    if not np.all(np.isfinite(schur)) or not np.all(np.isfinite(reduced_rhs)):
        raise SchurNumericalError("nonfinite Schur assembly")
    condition = float(np.linalg.cond(schur, p=2))
    rcond = 0.0 if not np.isfinite(condition) else 1.0 / condition
    if rcond < rcond_min:
        raise SchurNumericalError("ill-conditioned Schur complement")
    try:
        du = np.linalg.solve(schur, reduced_rhs)
    except np.linalg.LinAlgError as exc:
        raise SchurNumericalError("singular Schur complement") from exc
    dq = (rhs[:n] + a * upper @ du) / diagonal
    answer = np.concatenate((dq, du))
    if not np.all(np.isfinite(answer)):
        raise SchurNumericalError("nonfinite reconstructed stage")
    return answer, rcond


def manufactured_blocks(rng, n, near_zero=False):
    """Differentiate a positive finite-donor absorption fixture analytically.

qdot = source - k(u)*q; udot = source_gas - R*u + B*(k(u)*q)
k_j(u) = k0_j*exp(sum_l H_jl*u_l).
All states and time are dimensionless. This is a synthetic algebra fixture,
with no claim to the source rates, invariants, or units of HE29.
    """
    q = np.exp(rng.uniform(-7.0, 1.0, size=n))
    u = rng.uniform(0.05, 0.8, size=GAS_DIM)
    sensitivity = rng.uniform(0.0, 0.07, size=(n, GAS_DIM))
    k0 = np.full(n, 1e-280) if near_zero else np.exp(rng.uniform(-12, 8, size=n))
    kappa = k0 * np.exp(sensitivity @ u)
    deposition = rng.uniform(0.0, 0.2 / max(n, 1), size=(GAS_DIM, n))
    decay = np.diag([0.2, 0.35, 0.5, 0.7])
    upper = -(kappa * q)[:, None] * sensitivity
    lower = deposition * kappa[None, :]
    gas = -decay + deposition @ ((kappa * q)[:, None] * sensitivity)
    return kappa, upper, lower, gas


def full_stage_matrix(kappa, upper, lower, gas, a):
    """Independent dense construction: form J, then I-aJ."""
    jacobian = np.block([[-np.diag(kappa), upper], [lower, gas]])
    return np.eye(jacobian.shape[0]) - a * jacobian


def backward_error(matrix, x, rhs):
    denominator = np.linalg.norm(matrix, ord=np.inf) * np.linalg.norm(x, ord=np.inf)
    denominator += np.linalg.norm(rhs, ord=np.inf)
    numerator = np.linalg.norm(matrix @ x - rhs, ord=np.inf)
    return float(numerator / denominator) if denominator else float(numerator)


def check_case(rng, n, a, near_zero=False):
    blocks = manufactured_blocks(rng, n, near_zero)
    rhs = rng.normal(size=n + GAS_DIM)
    actual, rcond = arrowhead_solve(*blocks, rhs, a)
    matrix = full_stage_matrix(*blocks, a)
    expected = np.linalg.solve(matrix, rhs)
    error = backward_error(matrix, actual, rhs)
    difference = float(np.linalg.norm(actual - expected, ord=np.inf) /
                       max(1.0, np.linalg.norm(expected, ord=np.inf)))
    # Since sensitivity and deposition are nonnegative in this fixture,
    # the upper stage block is nonnegative and lower stage block nonpositive.
    if not np.all(matrix[:n, n:] >= 0) or not np.all(matrix[n:, :n] <= 0):
        raise AssertionError("stage off-diagonal sign convention")
    if error > RESIDUAL_LIMIT or difference > SOLUTION_DIFF_LIMIT:
        raise AssertionError((n, a, error, difference))
    return {"donors": n, "gas": GAS_DIM, "a": a, "near_zero_absorption": near_zero,
            "backward_error_inf": error, "scaled_solution_difference_inf": difference,
            "schur_rcond_2": rcond}


def expect_rejection(name, fn, exception):
    try:
        fn()
    except exception as exc:
        return {"name": name, "expected": exception.__name__, "message": str(exc)}
    raise AssertionError(name + " was not rejected")


def run_checks():
    rng = np.random.default_rng(20261019)
    cases = [check_case(rng, n, a) for n in (1, 4, 32, 129)
             for a in (0.0, 1e-8, 1e-3, 1.0, 10.0)]
    cases.extend(check_case(rng, n, 10.0, True) for n in (1, 32, 129))
    n = 7
    k = np.zeros(n)
    upper, lower = np.zeros((n, 4)), np.zeros((4, n))
    gas, rhs = -np.diag([0.2, 0.3, 0.4, 0.5]), rng.normal(size=n + 4)
    a = 3.0
    x, _ = arrowhead_solve(k, upper, lower, gas, rhs, a)
    diagonal_expected = rhs / np.r_[np.ones(n), 1 + a * np.array([0.2, 0.3, 0.4, 0.5])]
    np.testing.assert_allclose(x, diagonal_expected, rtol=0, atol=2e-15)
    rejections = [
        expect_rejection("dimension", lambda: arrowhead_solve(
            k, np.zeros((n, 3)), lower, gas, rhs, a), SchurContractError),
        expect_rejection("negative_absorption", lambda: arrowhead_solve(
            -np.ones(n), upper, lower, gas, rhs, a), SchurContractError),
        expect_rejection("negative_stage_factor", lambda: arrowhead_solve(
            k, upper, lower, gas, rhs, -1.0), SchurContractError),
        expect_rejection("nonfinite_input", lambda: arrowhead_solve(
            np.full(n, np.nan), upper, lower, gas, rhs, a), SchurContractError),
        expect_rejection("ill_conditioned", lambda: arrowhead_solve(
            k, upper, lower, np.diag([0, 0, 0, 1 - 1e-15]), rhs, 1.0),
            SchurNumericalError),
        expect_rejection("singular", lambda: arrowhead_solve(
            k, upper, lower, np.eye(4), rhs, 1.0), SchurNumericalError),
    ]
    # A deliberate sign mutation must be detectable on a coupled case.
    blocks = manufactured_blocks(rng, 11)
    b = rng.normal(size=15)
    correct_matrix = full_stage_matrix(*blocks, 1.0)
    wrong, _ = arrowhead_solve(blocks[0], -blocks[1], blocks[2], blocks[3], b, 1.0)
    mutation_residual = backward_error(correct_matrix, wrong, b)
    if mutation_residual <= 100 * RESIDUAL_LIMIT:
        raise AssertionError("wrong-sign mutation was not detected")
    return {
        "status": "PASS_SYNTHETIC_SCHUR_ALGEBRA",
        "evidence_class": "numerically_checked",
        "scope": "dimensionless manufactured finite-donor absorption; four gas variables",
        "native_he29_runs": 0,
        "historical_suites_rerun": 0,
        "positivity_guarantee_claimed": False,
        "physical_result_claimed": False,
        "thresholds": {"backward_error_inf": RESIDUAL_LIMIT,
                       "scaled_solution_difference_inf": SOLUTION_DIFF_LIMIT,
                       "schur_rcond_min": RCOND_MIN},
        "seed": 20261019,
        "dense_comparison_cases": cases,
        "dense_comparison_count": len(cases),
        "zero_absorption_zero_coupling_check": "PASS",
        "rejections": rejections,
        "wrong_sign_mutation_backward_error": mutation_residual,
        "max_backward_error_inf": max(c["backward_error_inf"] for c in cases),
        "max_scaled_solution_difference_inf": max(c["scaled_solution_difference_inf"] for c in cases),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "platform": platform.platform()},
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_checks()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in (
        "status", "dense_comparison_count", "max_backward_error_inf",
        "max_scaled_solution_difference_inf", "wrong_sign_mutation_backward_error")}))


if __name__ == "__main__":
    main()
