#!/usr/bin/env python3
"""Generic homogeneous three-curvature oracle in the locked Bianchi convention.

The calculation starts from the non-coordinate orthonormal-frame commutator,
uses the Koszul formula, constructs the curvature tensor, and reduces candidate
formula residuals modulo the Jacobi ideal n^{ab} a_b = 0.

This is a formula/research oracle.  It has no runtime-attempt authority.
"""

from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import sympy as sp


CONVENTIONS = {
    "metric_signature": "(-,+,+,+)",
    "spatial_orientation": "epsilon_123=+1",
    "commutator": "[e_a,e_b]=C^c_ab e_c",
    "structure": "C^c_ab=epsilon_abd n^(dc)+a_a delta^c_b-a_b delta^c_a",
    "curvature": "R(X,Y)Z=nabla_X nabla_Y Z-nabla_Y nabla_X Z-nabla_[X,Y] Z",
    "c": "explicit",
}


def _epsilon(i: int, j: int, k: int) -> sp.Expr:
    return sp.LeviCivita(i, j, k)


def _zero_matrix() -> list[list[str]]:
    return [["0"] * 3 for _ in range(3)]


def _canonical(expr: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(sp.expand(expr))))


def _symbols() -> dict[str, Any]:
    a0, a1, a2 = sp.symbols("a0 a1 a2", real=True)
    n00, n11, n22, n01, n02, n12 = sp.symbols(
        "n00 n11 n22 n01 n02 n12", real=True
    )
    s00, s11, s01, s02, s12 = sp.symbols(
        "s00 s11 s01 s02 s12", real=True
    )
    a = sp.Matrix([a0, a1, a2])
    n = sp.Matrix(
        [
            [n00, n01, n02],
            [n01, n11, n12],
            [n02, n12, n22],
        ]
    )
    sigma = sp.Matrix(
        [
            [s00, s01, s02],
            [s01, s11, s12],
            [s02, s12, -s00 - s11],
        ]
    )
    polynomial_variables = (
        a0,
        a1,
        a2,
        n00,
        n11,
        n22,
        n01,
        n02,
        n12,
    )
    return {
        "a": a,
        "n": n,
        "sigma": sigma,
        "polynomial_variables": polynomial_variables,
    }


def _structure_constants(a: sp.Matrix, n: sp.Matrix) -> list[list[list[sp.Expr]]]:
    # C[k][i][j] is C^k_{ij} in [e_i,e_j]=C^k_{ij} e_k.
    return [
        [
            [
                sp.expand(
                    sum(_epsilon(i, j, d) * n[d, k] for d in range(3))
                    + a[i] * sp.KroneckerDelta(k, j)
                    - a[j] * sp.KroneckerDelta(k, i)
                )
                for j in range(3)
            ]
            for i in range(3)
        ]
        for k in range(3)
    ]


def _connection(C: list[list[list[sp.Expr]]]) -> list[list[list[sp.Expr]]]:
    # Gamma[k][j][i] is defined by nabla_{e_i} e_j=Gamma^k_{j i} e_k.
    # Koszul: 2 Gamma^k_{j i}=C^k_{ij}-C^i_{jk}+C^j_{ki}.
    return [
        [
            [
                sp.expand(
                    (C[k][i][j] - C[i][j][k] + C[j][k][i]) / 2
                )
                for i in range(3)
            ]
            for j in range(3)
        ]
        for k in range(3)
    ]


def _ricci_from_connection(
    C: list[list[list[sp.Expr]]],
    gamma: list[list[list[sp.Expr]]],
) -> sp.Matrix:
    # R^l_{k i j} are components of R(e_i,e_j)e_k.
    def riemann(l: int, k: int, i: int, j: int) -> sp.Expr:
        return sp.expand(
            sum(
                gamma[m][k][j] * gamma[l][m][i]
                - gamma[m][k][i] * gamma[l][m][j]
                - C[m][i][j] * gamma[l][k][m]
                for m in range(3)
            )
        )

    # Ric_{k j}=R^i_{k i j}.
    return sp.Matrix(
        3,
        3,
        lambda k, j: sp.expand(sum(riemann(i, k, i, j) for i in range(3))),
    )


def _candidate_ricci(a: sp.Matrix, n: sp.Matrix) -> sp.Matrix:
    n_trace = sp.trace(n)
    n_sq = sp.trace(n * n)
    a_sq = (a.T * a)[0]
    isotropic = -2 * a_sq - n_sq + sp.Rational(1, 2) * n_trace**2

    def epsilon_cross(i: int, j: int) -> sp.Expr:
        # -2 epsilon_{cd(i} n_{j)}^c a^d
        first = sum(
            _epsilon(c, d, i) * n[j, c] * a[d]
            for c in range(3)
            for d in range(3)
        )
        second = sum(
            _epsilon(c, d, j) * n[i, c] * a[d]
            for c in range(3)
            for d in range(3)
        )
        return -first - second

    return sp.Matrix(
        3,
        3,
        lambda i, j: sp.expand(
            2 * sum(n[i, c] * n[j, c] for c in range(3))
            - n_trace * n[i, j]
            + epsilon_cross(i, j)
            + isotropic * sp.KroneckerDelta(i, j)
        ),
    )


def _candidate_scalar(a: sp.Matrix, n: sp.Matrix) -> sp.Expr:
    return sp.expand(
        -6 * (a.T * a)[0]
        - sp.trace(n * n)
        + sp.Rational(1, 2) * sp.trace(n) ** 2
    )


def _jacobi_groebner(a: sp.Matrix, n: sp.Matrix, variables: tuple[sp.Symbol, ...]):
    constraints = [sp.expand(sum(n[i, j] * a[j] for j in range(3))) for i in range(3)]
    return sp.groebner(constraints, *variables, order="grevlex"), constraints


def _reduce_mod_jacobi(expr: sp.Expr, basis: sp.GroebnerBasis) -> sp.Expr:
    _quotients, remainder = basis.reduce(sp.Poly(sp.expand(expr), *basis.gens).as_expr())
    return sp.factor(remainder)


def _divergence_from_connection(
    gamma: list[list[list[sp.Expr]]], sigma: sp.Matrix
) -> sp.Matrix:
    # D_b sigma^{a b}; homogeneous frame components have zero ordinary derivative.
    return sp.Matrix(
        3,
        1,
        lambda a, _unused: sp.expand(
            sum(
                gamma[a][c][b] * sigma[c, b]
                + gamma[b][c][b] * sigma[a, c]
                for b in range(3)
                for c in range(3)
            )
        ),
    )


def _candidate_divergence(a: sp.Matrix, n: sp.Matrix, sigma: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        3,
        1,
        lambda i, _unused: sp.expand(
            -3 * sum(a[b] * sigma[i, b] for b in range(3))
            - sum(
                _epsilon(i, b, c) * n[b, d] * sigma[c, d]
                for b in range(3)
                for c in range(3)
                for d in range(3)
            )
        ),
    )


@lru_cache(maxsize=1)
def _derived_objects() -> dict[str, Any]:
    data = _symbols()
    a: sp.Matrix = data["a"]
    n: sp.Matrix = data["n"]
    sigma: sp.Matrix = data["sigma"]
    C = _structure_constants(a, n)
    gamma = _connection(C)
    ricci = _ricci_from_connection(C, gamma)
    scalar = sp.expand(sp.trace(ricci))
    candidate_ricci = _candidate_ricci(a, n)
    candidate_scalar = _candidate_scalar(a, n)
    basis, jacobi = _jacobi_groebner(a, n, data["polynomial_variables"])
    divergence = _divergence_from_connection(gamma, sigma)
    candidate_divergence = _candidate_divergence(a, n, sigma)
    return {
        **data,
        "C": C,
        "gamma": gamma,
        "ricci": ricci,
        "scalar": scalar,
        "candidate_ricci": candidate_ricci,
        "candidate_scalar": candidate_scalar,
        "basis": basis,
        "jacobi": jacobi,
        "divergence": divergence,
        "candidate_divergence": candidate_divergence,
    }


@lru_cache(maxsize=1)
def run_symbolic_audit() -> dict[str, Any]:
    data = _derived_objects()
    ricci_residuals = [
        [
            _reduce_mod_jacobi(
                data["ricci"][i, j] - data["candidate_ricci"][i, j],
                data["basis"],
            )
            for j in range(3)
        ]
        for i in range(3)
    ]
    scalar_residual = _reduce_mod_jacobi(
        data["scalar"] - data["candidate_scalar"], data["basis"]
    )
    codazzi_residuals = [
        sp.factor(data["divergence"][i, 0] - data["candidate_divergence"][i, 0])
        for i in range(3)
    ]
    return {
        "schema": "rei-math-m1-generic-spatial-curvature-audit/v1",
        "conventions": CONVENTIONS,
        "jacobi_generators": [_canonical(expr) for expr in data["jacobi"]],
        "ricci_residuals_mod_jacobi": [
            [_canonical(expr) for expr in row] for row in ricci_residuals
        ],
        "scalar_residual_mod_jacobi": _canonical(scalar_residual),
        "codazzi_divergence_residuals": [
            _canonical(expr) for expr in codazzi_residuals
        ],
        "candidate_ricci_scalar": _canonical(data["candidate_scalar"]),
        "authority_effect": "FORMULA_RESEARCH_ONLY",
        "einstein_momentum_constraint_sign": "DEFERRED_PENDING_SPACETIME_CONVENTION_RECONCILIATION",
        "native_runtime": "NOT_RUN",
    }


def _substitute_matrix(matrix: sp.Matrix, substitutions: dict[sp.Symbol, sp.Expr]) -> list[list[str]]:
    return [
        [_canonical(matrix[i, j].subs(substitutions)) for j in range(3)]
        for i in range(3)
    ]


@lru_cache(maxsize=1)
def sentinel_report() -> dict[str, Any]:
    data = _derived_objects()
    a: sp.Matrix = data["a"]
    n: sp.Matrix = data["n"]
    ricci: sp.Matrix = data["ricci"]
    scalar: sp.Expr = data["scalar"]
    A, N = sp.symbols("A N", real=True)
    variables = list(a) + [n[0, 0], n[1, 1], n[2, 2], n[0, 1], n[0, 2], n[1, 2]]
    zero = {symbol: sp.Integer(0) for symbol in variables}
    v = dict(zero)
    v[a[0]] = A
    ix = dict(zero)
    ix[n[0, 0]] = N
    ix[n[1, 1]] = N
    ix[n[2, 2]] = N

    def record(subs: dict[sp.Symbol, sp.Expr]) -> dict[str, Any]:
        return {
            "ricci": _substitute_matrix(ricci, subs),
            "scalar": _canonical(scalar.subs(subs)),
        }

    return {"I": record(zero), "V": record(v), "IX": record(ix)}


def main() -> int:
    report = {
        "symbolic_audit": run_symbolic_audit(),
        "sentinels": sentinel_report(),
    }
    print(json.dumps(report, sort_keys=True, indent=2))
    all_zero = (
        report["symbolic_audit"]["ricci_residuals_mod_jacobi"] == _zero_matrix()
        and report["symbolic_audit"]["scalar_residual_mod_jacobi"] == "0"
        and report["symbolic_audit"]["codazzi_divergence_residuals"] == ["0", "0", "0"]
    )
    return 0 if all_zero else 1


if __name__ == "__main__":
    raise SystemExit(main())
