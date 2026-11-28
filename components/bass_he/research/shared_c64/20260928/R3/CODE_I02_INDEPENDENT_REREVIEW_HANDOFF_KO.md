# BASS_HE CODE-I02 repaired focused independent rereview handoff

이 문서는 첫 독립 재검토의 Important finding을 수정한 뒤의 두 번째 독립 판정용 handoff다. 이전 대화 없이 시작한다. 구현자/ChatGPT 연구 스레드/첫 reviewer의 결론을 새 독립 판정으로 재사용하지 않는다.

## 1. Exact repaired target

Repository: cosmosapjw-quantum/BASS_HE

Review PR: #15, DR11H: bind pair-membership certificate to endpoint identity

Repaired exact HEAD:
ac04d2a9e62120a0da4377ddf92451fde0c44431

Repaired tree:
5697bfb7b2ceae5854499a8132b44e573672df85

Original reviewed implementation:
af3ed44ce3cc1023aa8a1370ab2981aa76760869

Base:
ac09160bae74f051e5e2e17d8a1cde4084576c16

Fresh-read PR #15 before any review. If HEAD/tree differ, do not silently switch revisions.

Supporting runtime evidence only:
PR #16 head 2c3812e390b91b89da1de30988b3933646b79f30
resume-004 execution commit/tree:
6ddc4ff821ab5d1397fbd08493dd3954a89750f1
e80a9218d9d275546132110605da35160a878bb0

Do not rerun resume-004, the old 56-action scientific replay, or the worker sweep unless a newly affected scientific dependency specifically requires it.

## 2. First independent rereview result

The first independent reviewer returned:

- Critical findings = 0
- Important findings = 1
- CODE_I02_CLOSED = false
- stale_certificate_reuse_blocked = false
- intact_7_branch_geometry_supported = true, limited to prior PR #16 runtime evidence
- PROMOTE = HOLD
- Eq55_next_node_authorized = false

Important finding:
`_pair_membership_binding()` canonicalized state labels and CF depth through lossy `int()`. Endpoint mutations such as state_a 1 -> 1.5 or True, state_b 2 -> 2.5, and depth 64 -> 64.5 could collapse onto the original binding representation and hash, allowing validation to pass before geometry.

The reviewer also noted boolean permutation acceptance as a minor strictness issue.

## 3. Append-only repair history

Exactly four commits were added to PR #15 after the reviewed target.

1. e226c60c3ac40f032b67cfc1bbe6dfe6f1009ab3
   test: reproduce lossy integer identity aliasing

2. f5f9f3a7eff2230e4cfcef77d9b42eed90b0b9be
   fix: reject lossy integer certificate identities

3. ad25da7aed556ce0edd1a416ba6aa0eda8c2f8aa
   test: expand CODE-I02 stale identity attacks

4. ac04d2a9e62120a0da4377ddf92451fde0c44431
   fix: reject boolean permutation aliases

No force push, merge, physics tolerance change, pair-membership policy change, geometry-algorithm change, or Eq.(55) work was performed.

## 4. Intended repair semantics

The repaired identity canonicalizer accepts only actual Integral state labels and CF depth and rejects bool/NumPy bool before converting to the JSON integer representation. NumPy integer subclasses are intentionally accepted as the same discrete semantic identity.

The validator catches malformed/non-integral current endpoint identity and converts it to the existing fail-closed error:

`pair membership certificate binding mismatch`

The permutation certificate field now requires a length-two list of non-boolean Integral values whose integer set is exactly [0,1].

The SHA256 remains an unkeyed self-consistency binding. This repair does not claim authenticity against a jointly fabricated endpoint + certificate + recomputed hash.

## 5. Required fresh focused tests

On a dependency-complete checkout of the exact repaired HEAD, run at minimum:

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    python -m pytest -q -p no:cacheprovider \
      tests/test_dr11h_certificate_binding.py

Record actual collected/passed/failed counts. Do not substitute expected counts.

The test file now covers:
- ordinary stale state_a/state_b/R/p/lambda/depth/Z1/Z2 mutations;
- lossy aliases state_a 1.5/True/1.0, state_b 2.5/2.0, depth 64.5/64.0/True;
- tolerance-only and probe_scale-only mutations;
- corrupt/missing binding hash;
- stale policy;
- boolean permutation alias.

If the host lacks NumPy/pytest/project dependencies, classify as ENVIRONMENT_BLOCKED and do not claim PASS.

ChatGPT authoring-side evidence:
an isolated exact-logic reproducer, not the repository suite, ran 18/18 PASS after the fix. It also reproduced seven lossy aliases accepted by the old canonicalizer. This is supporting implementation logic evidence only.

## 6. Independent inspection requirements

A. Confirm the new strict type gate occurs before lossy canonicalization and before geometry/anchor work.

B. Confirm valid ordinary integer endpoint identity still passes.

C. Check that accepting NumPy Integral values is semantically harmless and does not reintroduce aliasing.

D. Re-run or independently construct the specific stale attacks named above.

E. Trace downstream use of certificate diagnostics. Distinguish unused diagnostics from identity/provenance-critical fields.

F. Keep the authenticity claim ceiling explicit: unkeyed SHA256 proves payload consistency, not trusted origin.

G. Use PR #16 only as supporting evidence that the previously admitted seven branches had intact runtime geometry. It is not the independent decision for the repaired code.

## 7. Decision contract

Return separately:

- Critical findings: integer + details
- Important findings: integer + details
- Minor or claim-scope notes
- focused_tests: PASS/FAIL/BLOCKED with command and counts
- CODE_I02_CLOSED: true/false
- stale_certificate_reuse_blocked: true/false
- intact_7_branch_geometry_supported: true/false
- PROMOTE: PASS/HOLD
- Eq55_next_node_authorized: true/false

Eq.(55) may be opened only if all are simultaneously true:
- Critical findings = 0
- Important findings = 0
- focused tests sufficient for the repaired dependency are PASS
- PROMOTE = PASS
- Eq55_next_node_authorized = true

If a new scientific assumption, tolerance, certificate policy, or structural redesign is required, preserve evidence and return to the research thread. Do not repair substantive design inside the independent-review context.

## 8. Claim ceiling

Even a PASS closes only CODE-I02.

Still separate/open:
- Eq.(52)/(55) exponent convention
- production P_rot
- new production Eq.(50)/(54)
- full Nmax convergence
- continuum-ionization authority
- common-contour lifted same-sheet homotopy
