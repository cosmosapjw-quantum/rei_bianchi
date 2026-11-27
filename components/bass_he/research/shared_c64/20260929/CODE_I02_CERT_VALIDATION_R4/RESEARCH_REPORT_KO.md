# BASS_HE CODE-I02 certificate-validation R4 research loop

Date: 2026-09-29 KST
Scope: research/design only. No production source was modified in this loop.

## 0. Fresh authoritative state

Fresh GitHub read at loop start:

- PR #15 HEAD: `ac04d2a9e62120a0da4377ddf92451fde0c44431`
- PR #15 tree: `5697bfb7b2ceae5854499a8132b44e573672df85`
- PR #17 independent-return HEAD: `74c1d701cc341c773d079645c87e19f3d37841e9`
- PR #17 tree: `a67733c98845f9d52da8aa14649f4a46fcacf297`
- independent return path:
  `research/shared_c64/20260929/CODE_I02_HOSTILE_RETURN/20260928T161004Z-i02-independent/RETURN_REPORT.json`

Independent return:

- Critical = 0
- Important = 2
- Minor = 1
- official focused tests = 23/23 PASS
- hostile tests = 54 PASS / 10 FAIL
- `CODE_I02_CLOSED=false`
- `full_certificate_fail_closed=false`
- `PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- production code unchanged

The two Important findings are:

1. nonfinite/negative/string-NaN `max_scaled_matching_error` can satisfy the current one-sided comparison and reach the first anchor;
2. stored binding payload JSON identity can change while Python dict equality remains true, and the validator checks the digest of the expected binding rather than the actual stored payload.

Minor finding: truthy non-boolean `passed` values are admitted.

## 1. Literature-supported checker principle

This loop used SciSpace to retrieve work on self-validating numerical computation and independently checkable certificates.

Relevant principles:

- Rall, *Numerical Computation with Validation* (1988), DOI `10.1007/978-3-0348-6303-2_33`: a numerical result should carry a validity guarantee, or the computation should explicitly report that validation could not be obtained.
- Necula, *Proof-carrying code* (POPL 1997), DOI `10.1145/263699.263712`: the consumer owns the safety policy and validates producer-supplied evidence with a small checker; producer assertions are not themselves the authority.
- Mehlhorn & Schweitzer, *Progress on Certifying Algorithms* (2010), DOI `10.1007/978-3-642-14553-7_1`: a certifying algorithm returns an output plus an easy-to-check witness, separating producer complexity from checker trust.
- Cheung, Gleixner & Steffy, *Verifying Integer Programming Results* (IPCO 2017; arXiv:1611.08832): complex numerical/optimization results can be accompanied by independently checkable certificates verified by a simpler verification tool.

Research implication for BASS_HE:

> A geometry consumer should evaluate a verifier-owned acceptance relation from current endpoint identity and evidence. It should not treat producer-supplied booleans or permissively coerced summary scalars as the source of authority.

This does **not** mean the current certificate must become a formal proof object. It does mean the accepted subset of fields and the trust boundary must be explicit.

## 2. Wolfram-independent checks

Wolfram Language was used as an independent representation/predicate sanity check.

For representation identity:

- `SameQ[1,1.] -> False`
- `Equal[1,1.] -> True`

Thus numerical equality and representation identity are different relations.

For canonical JSON-like payload strings corresponding to integer, boolean and floating representations, SHA-256 digests were all distinct. Therefore a checker that claims payload checksum consistency must hash the **stored canonical payload**, not only a separately reconstructed expected value.

For an explicit acceptance predicate `finite real && 0 <= e <= tolerance`, Wolfram rejected negative, indeterminate and infinite values and accepted zero/small positive controls.

These checks support the two independent findings without relying on Python's comparison semantics as the only argument.

## 3. Additional bounded hostile probes

Using the restored exact `ac04d2a9...` source snapshot and actual repository functions, this loop probed seven additional malformed types not in the returned 64-case matrix.

All seven reached the first anchor:

- `certificate.simple_fold = 'False'`
- `certificate.simple_fold = 1`
- `certificate.simple_fold = np.bool_(True)`
- `pair_membership.tolerance = '<numeric string>'`
- `pair_membership.probe_scale = '<numeric string>'`
- `pair_membership.max_scaled_matching_error = '<numeric string>'`
- `pair_membership.passed = np.bool_(True)`

Evidence: `EXTRA_PROBE.json`.

Classification: this is **additional research evidence**, not a new independent reviewer verdict. It shows that a fix narrowly matching only the ten returned witnesses would leave the admission boundary representation-permissive.

## 4. Threat-model separation

Three different claims must not be conflated.

### L0: stale/malformed payload integrity

Goal: accidental stale copies, type aliases, malformed fields and internally inconsistent stored payloads fail closed before geometry.

This is the minimum CODE-I02 continuation target.

### L1: untrusted external certificate semantic admission

Goal: a caller cannot make geometry accept an arbitrary certificate merely by writing internally consistent fields and recomputing an unkeyed digest.

For L1, verifier-owned policy and semantic recomputation are needed. An unkeyed SHA-256 only establishes consistency/integrity of bytes relative to a digest; it does not establish trusted origin.

### L2: independent physical/spectral truth

Goal: establish the exact physical branch statement independently of the same implementation, potentially with interval/Krawczyk/argument-principle authority.

L2 is outside CODE-I02 repair. Same-code recomputation can protect runtime admission without becoming independent scientific evidence.

## 5. Three repair strategies

### A. Surface hardening only

- strict `passed is True`;
- require finite nonnegative matching error;
- canonical-serialize stored and expected binding and compare bytes;
- check SHA-256 against stored canonical binding;
- strict scalar types.

Pros: tiny change, no new scientific solve.

Cons: a fully fabricated but self-consistent certificate can still pass. `full_certificate_fail_closed` remains ambiguous.

### B. Verifier-owned semantic revalidation with exact-identity cache — recommended

1. Keep strict L0 structural checks.
2. Define policy parameters in verifier code, not as caller authority:
   - policy ID `FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2` owns its allowed tolerance/probe-scale pair.
3. Recompute the current endpoint's `spectral_certificate(...).simple_fold` and pair-membership result under that policy before geometry admission.
4. Cache the recomputation by a verifier-derived exact content identity of
   `(state_a,state_b,R,p,lambda,depth,Z1,Z2,policy)`.
5. Treat stored certificate summary fields as records that must be well-formed and consistent with fresh revalidation, not as the admission authority.
6. Keep diagnostics not used by geometry explicitly non-authoritative.

Representative sandbox timing on one branch:

- `find_exceptional_point`: ~0.724 s
- repeated `_pair_membership_certificate` recomputation: 0.372–0.389 s, mean ~0.380 s

This is **not** a production benchmark. It only shows that one semantic revalidation per exact endpoint is plausible. A content-identity cache avoids paying this per rho/panel action.

Pros:

- closes current F01/F02/F03 at the semantic boundary rather than only their syntax;
- producer-supplied `passed` cannot create authority;
- fabricated matching-error summaries do not create authority;
- stale endpoint/certificate copies still fail closed;
- remains same scientific policy and same physical equations.

Cons:

- slightly broader runtime change;
- requires focused performance/identity tests for the cache;
- same-code revalidation is runtime integrity, not independent scientific proof.

### C. Full proof-object redesign

Store enough witness data for a separate small mathematical checker to verify membership without rerunning continuation.

Pros: strongest long-term architecture.

Cons: new schema, new scientific authority problem, substantially larger scope. Not justified for the current blocker.

## 6. Recommended bounded design

Use Strategy B, but keep the public claim narrow.

### Admission-critical authority

Verifier-owned:

- policy ID;
- policy tolerance;
- policy probe scale;
- exact endpoint identity;
- fresh simple-fold recomputation;
- fresh pair-membership recomputation.

Stored record must additionally satisfy:

- `pair_membership` is dict;
- `passed` is exactly Python `True` after JSON/in-memory normalization contract;
- tolerance/probe scale are numeric values of the declared policy, not strings/bools;
- `max_scaled_matching_error` is finite, nonnegative, and agrees with fresh recomputation;
- `binding` canonical stored bytes exactly equal verifier-reconstructed canonical bytes;
- `binding_sha256 == SHA256(stored_canonical_binding_bytes)`;
- claim/policy ID exact match;
- permutation has the existing accepted structural semantics.

### Non-authoritative diagnostics

`probe_radius`, `probe_R`, `sum_scaled_matching_error`, `scaled_distance_matrix`, `local_sheet_gap`, `iterations`, and descriptive status strings remain diagnostics unless a future claim explicitly promotes them.

Corrupting a non-authoritative diagnostic must not change geometry admission or scientific claim.

### Simple-fold boundary

`contour_geometry` must not use truthiness for `simple_fold`. The stored flag should be strict if retained, but geometry authority should come from the cached fresh spectral revalidation of the current endpoint.

## 7. Acceptance tests for the next implementation node

RED before implementation:

1. Returned witnesses F01/F02/F03 all fail before first anchor.
2. Additional seven representation probes in `EXTRA_PROBE.json` fail before first anchor.
3. A payload with modified tolerance/probe scale **and recomputed stored digest** still fails because policy parameters are verifier-owned.
4. A payload with `passed=True`, small fabricated error and internally recomputed payload hashes cannot admit a deliberately wrong advertised pair; fresh membership revalidation must reject it.
5. Valid original, JSON roundtrip and accepted NumPy integer endpoint identity still admit.
6. Reversed valid permutation remains accepted if permutation continues to be non-authoritative/permutation-invariant.
7. Revalidation cache key changes for one-ULP endpoint changes and policy changes; repeated exact identity executes semantic revalidation once per process/cache instance.
8. No Eq.(55), Eq.(50), Eq.(54), Nmax or continuum code is touched.

Verification hierarchy after GREEN:

- focused certificate tests;
- existing PR #15 focused suite;
- affected geometry tests;
- full repository suite once because runtime admission logic changed;
- no 56-action replay or worker sweep unless a scientific/numerical dependency changes or the independent reviewer explicitly requires it.

## 8. Gate

Current status after this research loop:

- `CODE_I02_CLOSED = false`
- `full_certificate_fail_closed = false`
- `scientific_PROMOTE = HOLD`
- `Eq55_next_node_authorized = false`
- `Eq55 = NOT_RUN`
- production physics = unchanged
- implementation of R4 design = NOT_RUN in this loop
- next required node = bounded certificate-admission implementation + fresh independent rereview

