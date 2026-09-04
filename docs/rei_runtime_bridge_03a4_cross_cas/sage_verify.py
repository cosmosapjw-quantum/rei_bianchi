#!/usr/bin/env sage -python
"""SageMath polynomial-ideal proof of the REI 03A4 predecessor chain."""

from __future__ import annotations

import json
from sage.all import PolynomialRing, QQ, matrix


N = 10
R = PolynomialRing(QQ, names=tuple(f"g{i}" for i in range(N)), order="lex")
g = R.gens()

# Boolean points and the adjacent implication constraints
# g_(i+1) -> g_i, encoded as g_(i+1) * (1 - g_i) = 0.
relations = [value * (value - 1) for value in g]
relations.extend(g[index + 1] * (1 - g[index]) for index in range(N - 1))
base = R.ideal(relations)

provider_implications = []
for index in range(N - 1):
    counterexample = base + R.ideal([g[-1] - 1, g[index]])
    provider_implications.append(counterexample.reduce(R.one()) == 0)

native_index = 6
native_implications = []
for index in range(native_index):
    counterexample = base + R.ideal([g[native_index] - 1, g[index]])
    native_implications.append(counterexample.reduce(R.one()) == 0)

A = matrix(QQ, N, N)
for index in range(N - 1):
    A[index, index + 1] = 1

assert A**N == matrix(QQ, N, N)
assert sum(1 for value in A ** (N - 1) if value != 0) == 1
assert all(provider_implications)
assert all(native_implications)

print(
    json.dumps(
        {
            "status": "PASS_SAGEMATH_BOOLEAN_IDEAL_AND_MATRIX_WITNESS",
            "polynomial_ring": "QQ[g0,...,g9]",
            "boolean_relations": N,
            "adjacent_implication_relations": N - 1,
            "provider_predecessors_proved": sum(provider_implications),
            "native_predecessors_proved": sum(native_implications),
            "matrix_nilpotence_index_upper_bound": N,
            "maximal_chain_witness_nonzero": 1,
            "authority_effect": "NONE",
            "native_runtime": "NOT_RUN",
        },
        sort_keys=True,
    )
)
