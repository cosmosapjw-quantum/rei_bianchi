# PHYS-MATH-CODE audit: exceptional momentum compatibility

## Review sequence

Software-contract review performed after the primary PHYS-MATH pass and after reading the completed exact-head Actions job log. It is a separate review pass by the same assistant, not an independent external agent. No repair was required after these reviews.

Verdict: PASS_RESEARCH_IMPLEMENTATION_AND_EXECUTED_REGRESSION, with visual and owner integration gates open.

## Source-to-result chain

1. RED commit `1dce17ccfc522de02647c9a3f02d85955abba9ad` contains the contract and ten frozen tests, but no implementation. Decoded run `33932323043`, job `101213295258`, showed exactly ten implementation-absent assertion failures and no errors/skips.
2. GREEN commit `4bdd2c77255e33ea209b1eec9ecbc28aeaca9f5c` adds only the bounded research implementation, derivation, RED receipt, and progress checkpoint. Frozen test/contract/workflow bytes are not weakened.
3. Both workflow and Python import recheck the actual donor Git blob `bd8c7a639628b7d44b1aaca16cd4f5a466245cda`. The workflow binds exact head/base tree and rejects changes outside this work unit, including any M1/M2/production/runtime changes.
4. L comes from the Jacobian of R_02,R_03 with respect to Sigma12,Sigma13. The candidate matrix lives only in tests; the donor computes four-dimensional curvature before projection.
5. Test IDs are matched exactly against the contract, not admitted by count alone. All ten tests passed without skips.
6. The mpmath sweep uses lu_solve on an explicit numerical matrix and compares against the separately stated exact rational solution at 80 digits. It is numerical corroboration, not a second symbolic derivation of the geometry.
7. JSON, CSV, source ZIP, PNG/SVG, head/tree records and SHA256SUMS were generated; all nine artifact content files passed checksums in the job log. Archive digest is recorded in EXECUTION_RECEIPT.json.

## Adversarial findings and retained limits

- Same-input self-comparison is avoided at the geometric entry: the target L is independently checked against the pinned Ricci result. Algebraic projector certificates then test nontrivial polynomial residuals off the exceptional surface.
- Nonzero q catches the old momentum sign; zero-flux constraints alone would not be a sufficient sign oracle.
- Free-shear and N22=0 fixtures prevent dropping the exceptional sector or introducing an incomplete chart division.
- Near-singular tests do not introduce pseudoinverse projection or an epsilon-based physical branch switch. The module is a research report generator, not a public matter-input admission API.
- P,Q need not be orthogonal. Silently replacing an incompatible physical q by Pq remains forbidden.
- The optional plot uses ordinary float conversion only after the 80-digit numerical checks. This does not provide arbitrary-precision rendered axes.
- Plot files were generated and checksummed, but the current session cannot directly render the downloaded artifact. Visual correctness, overlap and reduced-print readability remain PENDING_DIRECT_IMAGE_INSPECTION. Source/caption inspection is not substituted for that review.
- The workflow pins the principal symbolic versions but not all transitive plotting dependencies. Exact numeric claims bind this executed environment; byte-identical regeneration of PNG/ZIP is not asserted.
- Generated Actions artifacts have finite retention. Persistent source and normalized execution descriptors are committed; no promise of indefinite hosted artifact retention is made.

## Deferred, not repaired by this work

BASS-owner native tensor projection and slot adapter; full constraint propagation; matter EOS and positivity; time integration; H1B1 signed package census and host reconstruction; Section-0; first canonical interval and provider export.

No BASS source, production src/rust/stages/handoff, original runtime lock or attempt ref was changed. Symbolic Actions execution is not the one-attempt production native runtime.
