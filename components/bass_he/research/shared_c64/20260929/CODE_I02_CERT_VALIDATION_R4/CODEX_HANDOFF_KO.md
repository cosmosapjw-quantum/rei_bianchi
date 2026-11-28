# BASS_HE CODE-I02 R4 certificate-admission repair handoff

이 prompt는 이전 대화 없이 실행한다. 목적은 CODE-I02의 독립 hostile rereview에서 확인된 certificate admission 결함을 **정확히 한정된 범위에서 수정하고 검증**하는 것이다. Eq.(55)나 production physics를 열지 않는다.

## 0. Fresh identity gate

Repository:
`cosmosapjw-quantum/BASS_HE`

먼저 fresh-read:

- PR #15 head branch `audit11/dr11h-certificate-binding`
- expected current HEAD `ac04d2a9e62120a0da4377ddf92451fde0c44431`
- expected tree `5697bfb7b2ceae5854499a8132b44e573672df85`

Independent return evidence:

- PR #17 return publication HEAD `74c1d701cc341c773d079645c87e19f3d37841e9`
- tree `a67733c98845f9d52da8aa14649f4a46fcacf297`
- `research/shared_c64/20260929/CODE_I02_HOSTILE_RETURN/20260928T161004Z-i02-independent/RETURN_REPORT.json`
- `.../ATTACK_MATRIX.json`

Research design evidence is on the research branch under:
`research/shared_c64/20260929/CODE_I02_CERT_VALIDATION_R4/`

Read root `AGENTS.md` before any edit.

If PR #15 HEAD/tree changed, do not reset/force. Read the new commits, reconcile append-only, and stop if they overlap this repair materially.

Use a new isolated detached checkout/worktree. Do not clean/reset/delete an existing user worktree.

## 1. Independent return that must be preserved

The independent reviewer returned:

- Critical = 0
- Important = 2
- Minor = 1
- official focused tests = 23/23 PASS
- hostile = 54 PASS / 10 FAIL
- `CODE_I02_CLOSED=false`
- `full_certificate_fail_closed=false`
- `PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`

Important F01:
`max_scaled_matching_error` accepts NaN, -Infinity, negative finite and string `nan`, reaching the first anchor.

Important F02:
stored binding JSON payload may change integer identity to bool/float while Python dict equality remains true; validator hashes reconstructed expected binding instead of validating the digest of the stored canonical payload.

Minor F03:
truthy non-boolean `passed` values are admitted.

Do not downgrade or erase these findings merely because previous focused tests passed.

## 2. Additional research probes

The research thread additionally reproduced, on the same exact source, first-anchor admission for:

- `certificate.simple_fold='False'`
- `certificate.simple_fold=1`
- `certificate.simple_fold=np.bool_(True)`
- numeric-string `pair_membership.tolerance`
- numeric-string `pair_membership.probe_scale`
- numeric-string `max_scaled_matching_error`
- `pair_membership.passed=np.bool_(True)`

These are research-thread probes, not an independent decision. Reproduce the relevant cases in RED tests before fixing them.

## 3. Design contract

The repair must distinguish three layers:

- stale/malformed payload integrity;
- runtime semantic admission of an externally restored/dict endpoint;
- independent physical truth.

This node addresses the first two only. Same-code semantic revalidation is not independent physical evidence.

### Required architecture

Do not let producer-supplied `passed`, matching-error summaries, or self-declared tolerance create geometry authority.

Implement a small verifier-owned admission path with these properties:

1. **Policy authority is code-owned.**
   `FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2` must resolve to the allowed membership tolerance and probe scale used by the current production/research policy. A payload may record them but may not relax them by changing its own fields/digest.

2. **Stored binding canonical identity is checked as bytes, not Python numeric equality.**
   Construct canonical JSON bytes with deterministic key ordering/separators and no NaN. Require:
   - stored canonical binding bytes == verifier-reconstructed canonical binding bytes;
   - stored `binding_sha256` == SHA256(stored canonical binding bytes).
   Do not only hash the reconstructed expected object.

3. **Admission scalars are strict and finite.**
   Reject bools, strings and nonfinite values where the constructor emits numeric scalars. `max_scaled_matching_error` must be finite and nonnegative.

4. **`passed` is not authority.**
   Its stored representation must be strict if retained, but actual admission must derive from fresh semantic revalidation of the current endpoint.

5. **Fresh current-endpoint semantic revalidation.**
   Before the first geometry anchor, recompute:
   - current endpoint simple-fold status using the existing spectral policy;
   - pair membership using the existing `_pair_membership_certificate` numerical policy.
   Require both to pass.

6. **Content-identity cache, not rounded cache.**
   Avoid repeating the ~same membership revalidation for every rho/panel call. Cache the semantic admission result by an exact verifier-derived identity containing at least:
   `(state_a,state_b,R,p,lambda,depth,Z1,Z2,policy-id,policy parameters)`.
   One-ULP endpoint changes must miss the cache. No user-supplied digest alone may be the cache authority.

7. **Stored admission record consistency.**
   Require stored `max_scaled_matching_error` to agree with the fresh recomputation under an exact/hex float identity rule or another explicitly justified deterministic rule. Keep permutation behavior permutation-invariant; reversed valid permutation must remain admitted unless you explicitly change the scientific policy, which is not authorized.

8. **Diagnostics stay diagnostics.**
   Fields not consumed by geometry and not needed for the admission relation should be documented as non-authoritative rather than silently promoted into new claim gates.

9. **Strict simple-fold gate.**
   Do not use truthiness of stored `certificate.simple_fold`. Geometry authority comes from fresh cached spectral revalidation; malformed stored flags must not create admission.

### Forbidden scope

Do NOT change:

- finite-CF equations;
- branch list;
- physical tolerance values;
- Eq.(52)/(55) exponent convention;
- Eq.(55) probability;
- production Eq.(50)/Eq.(54);
- Nmax/channel semantics;
- continuum ionization;
- common-contour research;
- cloud worker policy.

If implementing the design requires changing any of those, stop and return to the research thread.

## 4. TDD contract

### RED first

Add focused regression tests before production edits. At minimum:

A. exact returned hostile failures:
- matching error NaN
- -Infinity
- negative finite
- string `nan`
- stored binding state bool
- stored binding state float
- stored binding depth float
- `passed='False'`
- `passed='0'`
- `passed=1`

B. research-loop extensions:
- truthy/nonbool `simple_fold`
- numeric-string tolerance/probe/matching-error
- `np.bool_(True)` passed

C. stronger semantic attacks:
- alter tolerance/probe scale and recompute all local stored hashes; must still fail because policy is verifier-owned;
- fabricate internally consistent `passed=True`/small error payload for a wrong advertised pair; fresh semantic revalidation must reject before anchor.

D. valid controls:
- untouched constructor result;
- JSON roundtrip;
- supported NumPy integer endpoint identity;
- reversed valid permutation if permutation remains diagnostic/permutation-invariant.

E. cache contract:
- repeated exact endpoint uses one semantic revalidation;
- one-ULP change in R/p/lambda/Z1/Z2 misses;
- state/depth/policy change misses;
- cached admission cannot be obtained from a caller-provided stale digest alone.

Record the RED command and actual failing cases/count. A collection error is not a valid RED if it does not exercise the intended behavior.

### GREEN

Make the smallest implementation satisfying the design. Avoid unrelated refactors.

## 5. Verification after GREEN

Run fresh, dependency-complete checks and record exact commands/counts:

1. new R4 focused tests;
2. `tests/test_dr11h_certificate_binding.py`;
3. affected geometry/spectral tests;
4. full repository pytest once, because runtime admission code changed;
5. compileall;
6. `git diff --check`.

Do not claim PASS from historical counts.

Do NOT rerun:

- resume-004;
- 56-action geometry replay;
- 15-arm worker sweep;
- R1/R2 common-contour analysis;
- bass_cr/HH work;
- Eq.(55);

unless a newly changed scientific/numerical dependency makes one of them genuinely affected. If you believe such a replay became necessary, stop and explain the dependency before executing it.

## 6. Performance check

The research sandbox measured one representative pair-membership recomputation at roughly 0.37–0.39 s. Treat this only as a feasibility hint, not a benchmark.

Measure on your host:

- cold semantic validation per endpoint;
- repeated exact endpoint with cache;
- cache miss on one-ULP endpoint change.

Do not optimize beyond the measured need.

## 7. Publication

Mutation policy:

- non-force push only;
- no merge;
- no reset/clean/stash/delete of user branches/worktrees;
- keep execution checkout identity distinct from publication branch;
- append evidence under a new timestamped namespace.

If you advance PR #15, report exact final commit/tree and changed file list.

Publish machine-readable evidence containing:

- source and final commit/tree;
- RED/GREEN commands and exit codes;
- actual test counts;
- cache-performance measurements;
- changed files/blobs;
- what was NOT run;
- claim ceiling.

## 8. Backup

For new durable artifacts, create-only backup to the existing BASS_HE Google Drive folder and Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/`.

Record provider ACK/object ID/size/checksum where available. Distinguish upload verification from restore verification. Do not duplicate already verified archives.

## 9. Return decision

Do not self-certify scientific independence. Return:

- implementation status;
- exact final HEAD/tree;
- RED result;
- GREEN focused/full test results;
- semantic revalidation/caching behavior;
- remaining findings;
- backup state;
- a new self-contained prompt for **separate independent rereview**.

Keep gate closed in this implementation context:

- `CODE_I02_CLOSED=false`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`

Only the subsequent separate independent rereview may change those decision fields.
