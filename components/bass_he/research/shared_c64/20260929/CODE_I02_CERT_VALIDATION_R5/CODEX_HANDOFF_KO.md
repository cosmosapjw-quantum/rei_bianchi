# BASS_HE CODE-I02 R5 consolidated Codex handoff

Run without prior conversation context. Implement only the bounded CODE-I02 semantic-admission repair. R5 adds an exact-cache identity constraint; the interval/Krawczyk L2 research is explicitly non-scope.

## 0. Fresh identity gate

Repository: cosmosapjw-quantum/BASS_HE

Fresh-read before editing:
- PR15 branch: audit11/dr11h-certificate-binding
- expected HEAD: ac04d2a9e62120a0da4377ddf92451fde0c44431
- expected tree: 5697bfb7b2ceae5854499a8132b44e573672df85
- PR17 research branch: research/shared-c64-crossrepo-20260928
- pre-R5 basis was a0b81a2cd65f223798fc26d6e62b69117f3e6c30 / tree 0e68846bb35965714d67d637708384c18b266b8a

Read root AGENTS.md, then:
- research/shared_c64/20260929/CODE_I02_HOSTILE_RETURN/20260928T161004Z-i02-independent/RETURN_REPORT.json
- .../ATTACK_MATRIX.json
- research/shared_c64/20260929/CODE_I02_CERT_VALIDATION_R4/
- research/shared_c64/20260929/CODE_I02_CERT_VALIDATION_R5/

If PR15 changed, do not reset/force. Read new commits and reconcile; stop if another implementation already overlaps this repair materially. Use a new detached worktree. Never clean/reset/delete an existing user worktree.

## 1. Governing independent findings

Independent return:
- Critical 0
- Important 2
- Minor 1
- official focused 23/23 PASS
- hostile 54 PASS / 10 FAIL
- CODE_I02_CLOSED=false
- full_certificate_fail_closed=false
- PROMOTE=HOLD
- Eq55_next_node_authorized=false

F01 Important: nonfinite/negative/string-NaN max_scaled_matching_error may reach first anchor.
F02 Important: stored binding JSON identity may change while Python dict equality remains true; validator hashes reconstructed expected binding rather than stored canonical bytes.
F03 Minor: truthy non-boolean passed is admitted.

R4 research also reproduced truthy/nonboolean simple_fold, numeric-string tolerance/probe/error, and np.bool_ aliases reaching first anchor.

## 2. R5 cache warning

Do NOT key semantic-admission memoization by a raw nested Python tuple, including functools.lru_cache(typed=True) on a tuple argument.

Observed:
- (1,0,0) == (1.0,0,0) == (True,0,0)
- same tuple hash in the observed interpreter
- typed lru_cache treated the three nested tuples as one key.

Use deterministic canonical bytes/digest as the key.

Existing src/bass_he/geometry.py is the reference pattern:
- deterministic _canonical(...)
- allow_nan=False
- SHA256 content addressing
- EvidenceCache validates key and payload hashes
- caller must include transitive source identity in key.

For this repair, prefer a small in-process canonical-key cache unless persistent reuse is clearly needed. If persistent, include exact verifier/scientific source revision.

## 3. Required admission architecture

The verifier, not the producer payload, owns authority.

1. Verifier-owned policy
   - policy ID FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2
   - tolerance and probe scale are code-owned policy values
   - payload fields may record but never relax them.

2. Canonical stored binding
   - deterministic canonical JSON bytes, no NaN
   - stored canonical binding bytes == verifier-reconstructed bytes
   - binding_sha256 == SHA256(stored canonical binding bytes)
   - never rely on Python dict numeric equality.

3. Strict scalar types
   - reject bool/string aliases where constructor emits numeric values
   - matching error finite and nonnegative.

4. Producer passed is not authority
   - stored representation strict if retained
   - actual admission derives from fresh semantic revalidation.

5. Fresh current-endpoint semantics before first anchor
   - recompute spectral_certificate(...).simple_fold
   - recompute pair membership via the existing _pair_membership_certificate
   - require both to pass.

6. Exact-content cache
   canonical key must include at least:
   state_a,state_b,R,p,lambda,depth,Z1,Z2,policy-id,policy parameters,verifier revision.
   - one-ULP endpoint changes miss
   - state/depth/policy/verifier revision changes miss
   - caller digest is never cache authority.

7. Stored record consistency
   - stored matching error agrees with fresh recomputation under exact/hex or another explicitly justified deterministic identity rule
   - reversed valid permutation remains accepted if permutation stays diagnostic/permutation-invariant.

8. Diagnostics remain diagnostics
   do not silently promote probe_radius, probe_R, distance matrix, local sheet gap, etc. into new scientific gates.

9. Simple-fold boundary
   no truthiness of stored certificate.simple_fold. Geometry authority comes from fresh cached spectral revalidation.

## 4. TDD RED contract

Write tests before production edits and observe real behavior failures.

Independent-return cases:
- matching error NaN
- -Infinity
- negative finite
- string nan
- stored binding state bool
- stored binding state float
- stored binding depth float
- passed='False'
- passed='0'
- passed=1

R4 extensions:
- truthy/nonbool simple_fold
- numeric-string tolerance/probe/matching-error
- passed=np.bool_(True)

Semantic attacks:
- change tolerance/probe scale and recompute all local stored hashes: still reject because policy is verifier-owned
- fabricate internally consistent passed=True + small error + valid local digests for a wrong advertised pair: fresh semantic revalidation must reject before anchor.

Valid controls:
- untouched constructor result
- JSON roundtrip
- supported NumPy integer endpoint identity
- reversed valid permutation if non-authoritative/permutation-invariant.

Cache tests:
- repeated exact endpoint performs one semantic revalidation per cache instance
- one-ULP R/p/lambda/Z1/Z2 changes miss
- state/depth/policy/verifier revision changes miss
- raw nested tuple equality aliases do not alias canonical cache key
- caller-provided stale digest cannot obtain cached admission.

Record RED command, exit code, actual failing cases/count. Collection errors do not count as RED.

## 5. GREEN and fresh verification

Implement the smallest code satisfying the contract.

Then run:
1. new R5 focused tests
2. existing tests/test_dr11h_certificate_binding.py
3. affected geometry/spectral tests
4. full repository pytest once
5. compileall
6. git diff --check

Measure:
- cold semantic validation
- repeated exact endpoint cached validation
- one-ULP cache miss.

Do not claim PASS from historical receipts.

## 6. Explicit non-scope

Do NOT change or run:
- finite-CF physical equations
- branch list
- physical tolerance values
- Eq.(52)/(55) exponent convention
- Eq.(55)
- production Eq.(50)/(54)
- Nmax/channel semantics
- continuum ionization
- common-contour production path
- 56-action replay
- worker sweep
- R1/R2 replay
- bass_cr / HH work.

If any heavy replay seems newly affected, stop and explain the dependency before running it.

## 7. Future L2 note, research only

Do not implement this in CODE-I02.

R5 identifies the current augmented fold system
H(p,lambda,R)=(F1,F2,det DzF)
as a future interval/Krawczyk target after realification to R^6.

Wolfram verified in adapted rank-one fold coordinates:
det(DH)=-a^2 alpha beta,
so nonsingularity of the augmented zero encodes standard transversality and fold-curvature nondegeneracy.

Future blockers:
- interval exclusion of every continued-fraction chart pole
- rigorous second derivatives/AD for D H
- separate validated continuation / named-state membership certificate.

## 8. Publication / backup

- non-force push only
- no merge
- no reset/clean/stash/delete user branches/worktrees
- append evidence under a new timestamped namespace
- report final PR15 commit/tree and changed files/blobs.

Create-only backup new durable artifacts to the existing BASS_HE Google Drive folder and Dropbox /BASS_DERIVATION_DOSSIERS_20260912/. Record ACK/object ID/size/checksum and distinguish upload verification from restore verification.

## 9. Return contract

Do not self-certify independent scientific closure.

Return:
- exact source/final HEAD and tree
- RED evidence
- GREEN focused/full results
- cache-key representation and source-identity policy
- cold/cached/miss timings
- remaining findings
- what was NOT run
- backup state
- a self-contained prompt for a separate independent rereview.

Keep:
- CODE_I02_CLOSED=false
- scientific_PROMOTE=HOLD
- Eq55_next_node_authorized=false
- Eq55=NOT_RUN

Only the subsequent independent rereview may change those fields.
