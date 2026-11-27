# CODE-I02 Important finding repair report

Date: 2026-09-28.

## Status

The first independent rereview returned HOLD with one Important finding: lossy integer canonicalization in the endpoint identity binding. The finding is repaired on PR #15, but CODE-I02 is not self-certified closed. A second independent rereview is required.

Repaired PR #15 HEAD:
`ac04d2a9e62120a0da4377ddf92451fde0c44431`

Tree:
`5697bfb7b2ceae5854499a8132b44e573672df85`

Original reviewed target:
`af3ed44ce3cc1023aa8a1370ab2981aa76760869`

## Finding reproduced

The previous canonicalizer used:

- `[int(x) for x in state_a]`
- `[int(x) for x in state_b]`
- `int(depth)`

Therefore distinct endpoint payloads could share the same canonical binding. The isolated reproducer confirmed acceptance by the old validator for:

- state_a: 1 -> 1.5
- state_a: 1 -> True
- state_a: 1 -> 1.0
- state_b: 2 -> 2.5
- state_b: 2 -> 2.0
- depth: 64 -> 64.5
- depth: 64 -> 64.0

Depth 64 -> True did not alias because int(True)=1, so it changed the binding hash; the repaired code rejects it by type anyway.

## Repair

`spectral.py` now validates discrete identity before canonical conversion.

- state labels must be tuple/list length 3;
- each state component must satisfy `numbers.Integral`;
- Python bool and NumPy bool are rejected explicitly;
- depth must satisfy the same non-boolean Integral contract;
- NumPy integer subclasses remain accepted and canonicalize to the same JSON integer semantic identity;
- validator converts malformed/non-integral current endpoint identity to the existing fail-closed binding-mismatch error.

The reviewer-noted boolean permutation alias was also closed. The permutation must now be a length-two list of non-boolean Integral values equal to the set/order-independent content [0,1].

No exponent convention, physical probability, numerical tolerance, geometry algorithm, or pair-membership policy changed.

## Test-first commit chain

1. `e226c60c3ac40f032b67cfc1bbe6dfe6f1009ab3`
   added lossy endpoint identity attacks before the implementation fix.

2. `f5f9f3a7eff2230e4cfcef77d9b42eed90b0b9be`
   implemented strict integer identity validation.

3. `ad25da7aed556ce0edd1a416ba6aa0eda8c2f8aa`
   expanded attacks for state_a, tolerance, probe scale, corrupt/missing hash, and boolean permutation.

4. `ac04d2a9e62120a0da4377ddf92451fde0c44431`
   closed the boolean permutation alias.

## Verification

AUTHORING-SIDE ISOLATED LOGIC CHECK:
- pytest 18/18 PASS;
- old lossy aliases explicitly reproduced;
- repaired aliases rejected;
- NumPy Integral semantic identity accepted;
- tolerance/probe-scale/hash attacks rejected;
- boolean permutation rejected.

This is not the repository scientific suite.

Repository clone in the ChatGPT container was blocked by DNS resolution to github.com, so the exact repository focused pytest was not executed here. The first independent-review host separately reported NumPy and pytest unavailable. A dependency-complete host must execute `tests/test_dr11h_certificate_binding.py` at the repaired exact HEAD before independent closure.

GitHub combined status currently exposes no CI status for the repaired HEAD.

## Gate

Current:
- Critical = unresolved pending rereview, not promoted from prior zero.
- Important finding repair = IMPLEMENTED, independent confirmation pending.
- CODE_I02_CLOSED = false.
- stale_certificate_reuse_blocked = PENDING_INDEPENDENT_CONFIRMATION.
- scientific_PROMOTE = HOLD.
- Eq55_next_node_authorized = false.
- Eq55 = NOT_RUN.

A self-contained repaired rereview handoff is stored beside this report.
