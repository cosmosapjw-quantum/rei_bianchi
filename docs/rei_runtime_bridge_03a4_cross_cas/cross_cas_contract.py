#!/usr/bin/env python3
"""Methodology-only cross-CAS checks for the REI 03A4 execution order.

This module proves properties of a declared finite chain.  It has no GitHub
write surface, attempt-state surface, production import, or scientific-authority
effect.  The canonical target-host preflight remains a separate executable node.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence


NODES = (
    "IndependentAudit",
    "TargetHostStaticPreflight",
    "FreshProtectionReadback",
    "GlobalLease",
    "LocalLease",
    "DispatchIntent",
    "NativeWorker",
    "RuntimeResultAudit",
    "FirstIntervalEligibility",
    "ProviderReview",
)
EDGES = tuple(zip(NODES[:-1], NODES[1:]))
EXTERNAL_FIXTURES = {
    "octave": "octave_verify.m",
    "sage": "sage_verify.py",
    "singular": "singular_verify.sing",
    "lean_mathlib": "lean/REI03A4.lean",
}
PR54_HEAD = "9ecaa45d4794b2c7f2a430acff4e3ac7f213a2fc"
PR54_TREE = "db334db438c59f20ebd8c9b289e00c9f3ede27cc"
INDEPENDENT_AUDIT_SHA256 = (
    "7438d027d306308628a87d9d546506c31f39db4523c9cf151091b98e99af856c"
)
AUDITED_PROTECTION_SHA256 = (
    "ca1b13ddd7dc9d124bcfd484aedd94016a761c36c5b32a243e54746ee644914a"
)


class CrossCasContractError(RuntimeError):
    """Typed failure for the non-authoritative finite-chain checks."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def is_exact_adjacent_chain(edges: Sequence[tuple[str, str]]) -> bool:
    return tuple(edges) == EDGES


def has_prelease_native_bypass(edges: Sequence[tuple[str, str]]) -> bool:
    """Detect any direct NativeWorker predecessor other than DispatchIntent."""

    return any(
        target == "NativeWorker" and source != "DispatchIntent"
        for source, target in edges
    )


def verify_sympy_exact() -> dict[str, bool]:
    import sympy as sp
    from sympy.logic.inference import satisfiable

    size = len(NODES)
    matrix = sp.zeros(size)
    for index in range(size - 1):
        matrix[index, index + 1] = 1

    symbol = sp.Symbol("lambda")
    expected_reachability = sp.zeros(size)
    for row in range(size):
        for column in range(row + 1, size):
            expected_reachability[row, column] = 1
    reachability = sp.zeros(size)
    for power in range(1, size):
        reachability += matrix**power

    propositions = sp.symbols(f"g0:{size}", boolean=True)
    predecessor_contract = sp.And(
        *(
            sp.Implies(propositions[index + 1], propositions[index])
            for index in range(size - 1)
        )
    )
    provider_requires_all = all(
        satisfiable(
            sp.And(
                predecessor_contract,
                propositions[-1],
                sp.Not(propositions[index]),
            )
        )
        is False
        for index in range(size - 1)
    )
    native_requires_prelease_chain = all(
        satisfiable(
            sp.And(
                predecessor_contract,
                propositions[NODES.index("NativeWorker")],
                sp.Not(propositions[index]),
            )
        )
        is False
        for index in range(NODES.index("NativeWorker"))
    )

    return {
        "exact_adjacent_edges": is_exact_adjacent_chain(EDGES),
        "no_direct_prelease_native_bypass": not has_prelease_native_bypass(
            EDGES
        ),
        "strictly_upper_triangular": matrix.is_upper is True
        and all(matrix[index, index] == 0 for index in range(size)),
        "nilpotent_at_chain_length": matrix**size == sp.zeros(size),
        "maximal_chain_witness_unique": sum(
            1 for value in matrix ** (size - 1) if value != 0
        )
        == 1,
        "characteristic_polynomial_lambda_power_n": sp.expand(
            matrix.charpoly(symbol).as_expr()
        )
        == symbol**size,
        "transitive_reachability_is_total_order": reachability
        == expected_reachability,
        "provider_requires_every_predecessor": provider_requires_all,
        "native_requires_every_prelease_predecessor": (
            native_requires_prelease_chain
        ),
    }


def verify_mpmath_numeric() -> dict[str, Any]:
    import mpmath as mp

    mp.mp.dps = 100
    size = len(NODES)
    matrix = mp.matrix(size, size)
    for index in range(size - 1):
        matrix[index, index + 1] = mp.mpf(1)
    terminal = matrix**size
    maximal = matrix ** (size - 1)
    terminal_norm = mp.fsum(
        abs(terminal[row, column])
        for row in range(size)
        for column in range(size)
    )
    maximal_nonzero = sum(
        1
        for row in range(size)
        for column in range(size)
        if maximal[row, column] != 0
    )
    return {
        "precision_decimal_digits": mp.mp.dps,
        "a_power_n_norm": str(terminal_norm),
        "a_power_n_minus_1_nonzero": maximal_nonzero,
        "authority_effect": "NONE",
    }


def build_receipt(
    *,
    sympy_result: Mapping[str, Any],
    mpmath_result: Mapping[str, Any],
    external_axes: Mapping[str, str],
) -> dict[str, Any]:
    if set(external_axes) != set(EXTERNAL_FIXTURES):
        raise CrossCasContractError("EXTERNAL_AXIS_SET_MISMATCH")
    if not sympy_result or not all(value is True for value in sympy_result.values()):
        raise CrossCasContractError("SYMPY_CHAIN_CONTRACT_FAILED")
    if (
        mpmath_result.get("precision_decimal_digits") != 100
        or mpmath_result.get("a_power_n_norm") != "0.0"
        or mpmath_result.get("a_power_n_minus_1_nonzero") != 1
        or mpmath_result.get("authority_effect") != "NONE"
    ):
        raise CrossCasContractError("MPMATH_CHAIN_CONTRACT_FAILED")
    return {
        "schema": "rei-runtime-03a4-cross-cas-ordering/v1",
        "status": "PASS_SYMPY_MPMATH_CHAIN_CONTRACT",
        "canonical_parent": {"commit": PR54_HEAD, "tree": PR54_TREE},
        "input_evidence": {
            "independent_audit_receipt_sha256": INDEPENDENT_AUDIT_SHA256,
            "audited_protection_receipt_sha256": AUDITED_PROTECTION_SHA256,
            "evidence_role": "HISTORICAL_AND_METHOD_BOUND_NOT_TIMELESS_AUTHORITY",
        },
        "nodes": list(NODES),
        "edges": [list(edge) for edge in EDGES],
        "sympy": dict(sympy_result),
        "mpmath": dict(mpmath_result),
        "external_axes": dict(external_axes),
        "authority_effect": "NONE",
        "mutation_effect": "NONE",
        "global_attempt_ref": "ABSENT_REQUIRED",
        "local_lease": "NOT_CREATED",
        "native_runtime": "NOT_RUN",
        "first_canonical_interval": "NO_PASS",
        "provider_export": "NOT_AUTHORIZED",
        "next_canonical_node": "TARGET_HOST_STATIC_PREFLIGHT",
    }


def write_o_excl(path: Path, value: Mapping[str, Any]) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise CrossCasContractError("OUTPUT_PATH_INVALID")
    parent = candidate.parent.resolve(strict=True)
    target = parent / candidate.name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(target, flags, 0o600)
    except OSError as exc:
        raise CrossCasContractError("OUTPUT_PATH_UNAVAILABLE") from exc
    payload = canonical_bytes(dict(value)) + b"\n"
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            target.unlink()
        except OSError:
            pass
        raise
    return target.resolve(strict=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    options = parser.parse_args(argv)

    sympy_result = verify_sympy_exact()
    mpmath_result = verify_mpmath_numeric()
    receipt = build_receipt(
        sympy_result=sympy_result,
        mpmath_result=mpmath_result,
        external_axes={
            key: "DECLARED_SEPARATE_CI_AXIS"
            for key in EXTERNAL_FIXTURES
        },
    )
    if options.output is not None:
        path = write_o_excl(options.output, receipt)
        receipt = dict(receipt)
        receipt["output"] = str(path)
    if options.self_test or options.output is not None:
        print(json.dumps(receipt, sort_keys=True))
        return 0
    parser.error("one of --self-test or --output is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
