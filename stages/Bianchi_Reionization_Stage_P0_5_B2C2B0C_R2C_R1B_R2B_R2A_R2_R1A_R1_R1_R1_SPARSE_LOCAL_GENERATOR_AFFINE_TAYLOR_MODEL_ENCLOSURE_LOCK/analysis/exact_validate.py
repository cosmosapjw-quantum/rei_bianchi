#!/usr/bin/env python3
"""Exact symbolic validator for the sparse local-generator contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp

NODE_COUNT = 46_080
RANK_PER_SITE = 92_003
EVALUATION_SITE_COUNT = 4
STATE_COORDINATE_COUNT = 4
LOCAL_POLYNOMIAL_GENERATOR_COUNT = 3  # theta_v, theta_f, theta_v theta_f
FLOAT64_BYTES = 8


def validate_exact_contract() -> dict[str, Any]:
    vc, vh, fc, fh, tv, tf, w, z = sp.symbols(
        "vc vh fc fh tv tf w z", finite=True
    )
    v = vc + vh * tv
    f = fc + fh * tf
    ah = sp.expand(v * w + (1 - v) * f * z)
    ah_center = vc * w + (1 - vc) * fc * z
    ah_model = sp.expand(
        ah_center
        + vh * (w - fc * z) * tv
        + fh * (1 - vc) * z * tf
        - vh * fh * z * tv * tf
    )
    branch_residual = sp.simplify(ah - ah_model)

    h_v, h_f, h_vf = sp.symbols("h_v h_f h_vf", finite=True)
    e_v, e_f, e_vf = sp.symbols("e_v e_f e_vf", finite=True)
    h_generators = [sp.Matrix([-x, x, 0, 0, 0]) for x in (h_v, h_f, h_vf)]
    he_generators = [sp.Matrix([0, 0, -x, x, 0]) for x in (e_v, e_f, e_vf)]
    c_h = sp.Matrix([1, 1, 0, 0, 0])
    c_he = sp.Matrix([0, 0, 1, 1, 1])
    h_invariants = [sp.simplify((c_h.T * vector)[0]) for vector in h_generators]
    he_invariants = [sp.simplify((c_he.T * vector)[0]) for vector in he_generators]

    n = sp.symbols("n", integer=True, positive=True)
    h = sp.IndexedBase("h")
    dh = sp.IndexedBase("dh")
    support = sp.symbols("S", nonzero=True)
    d_support = sp.symbols("dS")
    # Algebraic sum of dq_i = dh_i/S - h_i dS/S^2, under sum h_i=S,
    # sum dh_i=dS.  Substitute the identities explicitly to avoid relying on
    # symbolic summation assumptions about IndexedBase objects.
    dq_sum = sp.simplify(d_support / support - support * d_support / support**2)

    storage_bytes = (
        NODE_COUNT
        * EVALUATION_SITE_COUNT
        * STATE_COORDINATE_COUNT
        * LOCAL_POLYNOMIAL_GENERATOR_COUNT
        * FLOAT64_BYTES
    )
    receipt: dict[str, Any] = {
        "classification": "SPARSE_LOCAL_GENERATOR_EXACT_SYMBOLIC_VALIDATION",
        "status": "PASS",
        "branch_bilinear_expansion_residual": str(branch_residual),
        "hydrogen_generator_invariant_residuals": [str(item) for item in h_invariants],
        "helium_generator_invariant_residuals": [str(item) for item in he_invariants],
        "normalized_measure_jvp_sum_residual": str(dq_sum),
        "node_count": NODE_COUNT,
        "evaluation_site_count": EVALUATION_SITE_COUNT,
        "source_safe_rank_lower_bound_per_site": RANK_PER_SITE,
        "source_safe_input_rank_lower_bound": RANK_PER_SITE * EVALUATION_SITE_COUNT,
        "local_polynomial_generator_count_per_site": LOCAL_POLYNOMIAL_GENERATOR_COUNT,
        "state_coordinate_count": STATE_COORDINATE_COUNT,
        "local_polynomial_storage_bytes": storage_bytes,
        "local_polynomial_storage_mib": storage_bytes / 2**20,
    }
    assert branch_residual == 0
    assert all(item == 0 for item in h_invariants)
    assert all(item == 0 for item in he_invariants)
    assert dq_sum == 0
    return receipt


def main() -> None:
    stage = Path(__file__).resolve().parents[1]
    receipt = validate_exact_contract()
    target = stage / "receipts" / "EXACT_SYMBOLIC_VALIDATION.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
