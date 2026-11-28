# BASS_HE CODE-I02 R6 independent rereview handoff

이 prompt는 새 독립 context에서 실행한다. 구현자/Codex의 GREEN 보고를 독립 판정으로 재사용하지 않는다. 대상 코드는 수정하지 않는다.

## 0. Fresh identity gate

Repository:
`cosmosapjw-quantum/BASS_HE`

Fresh-read PR #15:

- branch: `audit11/dr11h-certificate-binding`
- expected current HEAD:
  `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`
- expected current tree:
  `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`

Important provenance distinction:

- pre-R5 baseline:
  `ac04d2a9e62120a0da4377ddf92451fde0c44431`
  / tree `5697bfb7b2ceae5854499a8132b44e573672df85`
- final source/test commit:
  `8bf9ce27a39be06d2487fffd40c2b97a2cdb3e1a`
  / tree `54c522773944ca00d3eee0b91952ffce5ecd413a`
- current HEAD `b8b2fe47...` is one commit after `8bf9ce2` and adds only the final backup receipt.

Expected current blobs:
- `src/bass_he/spectral.py`
  `c41dc2bfacff6140fc130a787a856eae389a23b4`
- `tests/test_code_i02_r5_admission.py`
  `d62681d71cd96d1dc11dc849315f44060d73e2c6`

Read root `AGENTS.md` first.

If HEAD/tree/source blobs differ, do not review a guessed revision. Fresh-read the changes and reconcile before proceeding.

Use a new detached checkout/worktree. Do not reset/clean/stash/delete user worktrees.

## 1. Evidence to read, but not trust as verdict

Prior independent hostile return on PR #17:

`research/shared_c64/20260929/CODE_I02_HOSTILE_RETURN/20260928T161004Z-i02-independent/`

Read:
- `RETURN_REPORT.json`
- `ATTACK_MATRIX.json`

R5 implementation evidence on PR #15:

`research/shared_c64/20260929/CODE_I02_R5_IMPLEMENTATION_20260929T015933Z/`

Read:
- `RED_GREEN_EVIDENCE.json`
- backup receipts
- implementer rereview prompt

R6 research evidence on PR #17:

`research/shared_c64/20260929/CODE_I02_R6_POST_IMPLEMENTATION_RESEARCH/`

The implementer reports 57 focused PASS, 189 full PASS, compileall/diff-check PASS. Treat these as provenance only until independently reproduced where needed.

## 2. Original findings that must be attacked

Prior independent reviewer found:

- Critical 0
- Important F01: NaN/-Inf/negative/string matching errors admitted
- Important F02: stored binding JSON identity/digest mismatch admitted
- Minor F03: truthy non-boolean `passed`
- `CODE_I02_CLOSED=false`
- `PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`

R4 research also found truthy/nonboolean `simple_fold`, numeric-string policy/error fields, and NumPy-bool aliases reaching the first anchor.

Independently verify that all relevant cases now fail before `bound_pair`.

## 3. Inspect the new semantic authority boundary

Confirm from source, not comments alone:

1. stored binding is compared through canonical bytes, not Python numeric equality;
2. stored SHA256 authenticates the stored canonical binding bytes;
3. policy tolerance/probe scale are verifier-owned at admission;
4. malformed/nonfinite scalar aliases fail closed;
5. stored `passed` and `simple_fold` cannot create authority by truthiness;
6. fresh `spectral_certificate` and fresh advertised-pair membership are recomputed before the first anchor;
7. a fully self-consistent fabricated wrong advertised pair cannot reach the anchor;
8. altered caller policy plus recomputed local digest cannot relax verifier policy.

## 4. Cache hostile review

The cache must not reintroduce the old identity bug.

Attack:

- nested `int` / `float` / `bool` aliases;
- NumPy integer valid controls;
- extended precision scalars;
- one-ULP changes in R/p/lambda/Z1/Z2;
- state/depth changes;
- policy/revision changes;
- stale caller digest;
- attempts to inject an alternate caller-owned cache or policy.

Confirm repeated exact identity revalidates once while a changed exact identity misses.

Because the cache is process-local, distinguish:
- current runtime safety;
- hypothetical persistent-cache source identity.

Do not demand persistent-cache machinery that the implementation does not use.

## 5. R6 portability question: exact stored matching-error equality

The current validator additionally requires exact IEEE hex equality between stored and freshly recomputed `max_scaled_matching_error`.

Independently decide the contract.

### If the certificate is environment-bound

Exact equality can be acceptable, but state explicitly:
- which environment identity is part of validity;
- whether restore on a different supported host is expected to fail closed.

### If the certificate is intended to be portable across supported hosts

Test portability if two supported numerical environments are readily available. Do not launch a heavy cloud replay.

A minimal test is enough:
1. generate one ordinary certificate under environment A;
2. serialize/restore it;
3. validate it under environment B with the same scientific source/policy;
4. record stored error, fresh error, hex/ULP difference, and pass/fail.

If no second environment is available, classify portability as unresolved rather than inventing a verdict.

Relevant R6 theorem:

[
E(D)=\min(\max(d_{00},d_{11}),\max(d_{01},d_{10}))
]

is 1-Lipschitz in (|D|_infty). This supports interval/enclosure semantics, but it does not prove current cross-host error bounds.

Do not treat failure of exact hex equality as false scientific admission. It is a possible false-rejection/portability issue.

## 6. R6 policy-SSOT question

Source currently has both:

- constants `PAIR_MEMBERSHIP_TOLERANCE=5e-6`,
  `PAIR_MEMBERSHIP_PROBE_SCALE=1e-4`;
- literal defaults `tolerance=5e-6`, `probe_scale=1e-4`
  in `_pair_membership_certificate`.

`find_exceptional_point` uses the function defaults.

The values agree now. Determine whether this is:

- no finding for current closure;
- Minor maintenance/SSOT finding;
- or a material closure issue because the stated policy ownership contract requires one source of truth.

Do not manufacture a current mismatch that does not exist.

## 7. Bounded fresh tests

Run fresh:

- `tests/test_code_i02_r5_admission.py`;
- `tests/test_dr11h_certificate_binding.py`;
- any additional bounded hostile tests needed for findings above.

Run the full suite only if your review framework requires it or your added probe changes test code in an isolated review worktree. Do not infer correctness from the implementer's 189-pass receipt.

Record commands, versions, counts, exit codes, and target source hashes before/after.

## 8. Explicit non-scope

Do NOT run or modify:

- Eq.(55);
- production Eq.(50)/(54);
- 56-action replay;
- worker sweep;
- R1/R2;
- bass_cr;
- HH;
- interval/Krawczyk L2;
- branch list or physical tolerances.

No production-code edits in the independent review context.

## 9. Decision contract

Return separately:

- Critical findings + evidence
- Important findings + evidence
- Minor / portability / maintenance notes
- focused test results
- first-anchor hostile attack matrix
- cache identity verdict
- portability verdict:
  `PORTABLE_PASS / ENVIRONMENT_BOUND_BY_CONTRACT / UNRESOLVED / FAIL`
- policy-SSOT verdict
- `CODE_I02_CLOSED: true/false`
- `full_certificate_fail_closed: true/false`
- `scientific_PROMOTE: PASS/HOLD`
- `Eq55_next_node_authorized: true/false`

Eq55 can be authorized only if the actual independent review returns:
- Critical = 0
- Important = 0
- CODE_I02_CLOSED = true
- scientific_PROMOTE = PASS
- Eq55_next_node_authorized = true

A portability-only false-rejection issue need not automatically become an Important scientific-admission finding; classify it according to the actual declared contract and impact.

Publish a separate immutable review artifact and preserve all failures.

## 10. Claim ceiling

Even if CODE-I02 closes, this does not establish:

- Eq.(52)/(55) exponent convention;
- production P_rot;
- Eq.(50)/(54) physical result;
- Nmax convergence;
- continuum ionization;
- L2 interval fold proof;
- common-contour lifted homotopy.

Those remain separate gates.
