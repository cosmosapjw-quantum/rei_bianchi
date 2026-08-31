# Independent PHYS-MATH audit

Date: 2026-08-31

Recovery classification: `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`

Verdict:
`PASS_BOUNDED_GENERIC_FIXTURE_ONLY / BLOCKED_PRODUCTION_AND_SCIENTIFIC_CLAIM`

## Frozen question

Does this branch provide a mathematically sound, outward-rounded generic
interval certificate substrate for the declared linear, tangent, and mixed
implicit systems, without presenting that substrate as the missing physical
four-site operator or a canonical interval?

## Findings

1. The non-code derivation and native implementation agree on
   \(A Z_a=b_a-A_aZ\) and
   \(A Z_{ab}=b_{ab}-A_{ab}Z-A_aZ_b-A_bZ_a\). The tangent path does not use a
   midpoint-only inverse as an enclosure.
2. The Rust kernel implements MPFR RNDD/RNDU interval primitives, rejects a
   zero-containing divisor before division, and accepts an implicit block only
   after strict full-interval Krawczyk self-inclusion. Binary64 export is also
   rejected if it collapses the proved strict margins.
3. The public H/He derivatives, normalized-measure Hessian, MPRK conservation
   identities, Alexander SDIRK2 order condition, same-parent composition, and
   difference-first remainder were statically consistent in the supplied
   formula contract.
4. The supplied non-code ZIP and markdown are byte-bound in `INPUT_LOCK.json`.
   The Wolfram receipt is source-hash-bound and explicitly limited to exact
   symbolic identities; it was not replayed on this executor.
5. No mathematical under-enclosure was found in the bounded generic kernel.

## Fresh evidence

| Gate | Result |
|---|---|
| Non-code formula contract | 9/9 pass |
| Repo-relative non-code manifest | 7/7 pass |
| Native Rust suite | 11/11 pass |
| Independent exact oracle | 96 families, 6,144 corner systems pass |
| Joint request and Python/Rust bridge | 28/28 pass (12 joint + 16 bridge) |

The audited Rust source is SHA-256
`c4dd1f21200faab60e239e96b56d1eb3d2691c47dc3d3a4991af7565ce0a9d51`;
the exact-oracle source is
`83a77d2bc56261caaf4c5d07475b4eb97430de142a658aaa14b6d58b696ee497`;
the deterministic native artifact is
`a563eec77de3e0bfa55df454b4ec4cfdc317a1feb4cf2074385719ebdcca32ef`.

## Evidence boundary

- `P0 / BLOCKED`: no real Rust ABI recomputes all four physical sites,
  including outer thermal/owner self-inclusion.
- `P0 / BLOCKED`: no admitted node-38382 endpoint/full-field/owner/reduction
  authority and no independently verified predecessor replay ABI.
- `P0 / NOT_RUN`: the 46,080-by-three canonical pilot is excluded.
- `P2 / NOT_RUN`: Wolfram/xAct, SageMath, Singular, Lean/mathlib, and Rocq were
  unavailable on this executor. Lean workspace/toolchain/dependency pins are
  also absent.
- `P2 / PARTIAL`: the 3-by-3 formal fixture verifies supplied Krawczyk-image
  margins; it does not independently derive the supplied \(K_3\).

The literature cross-check supports the generic validated-integrator and MPRK
methods but does not supply this repository's physical four-site certificate.
Accordingly the only admissible terminal state is
`STOP_INVALID / NO_PASS_FIRST_CANONICAL_INTERVAL`; no performance,
publication, or scientific-pass claim is admitted.
