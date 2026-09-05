# REI M2 owner-native execution handoff — 2026-09-05

Task layers: review, document, execution handoff.

## Before this work

The preceding conversation treated exceptional transverse-momentum algebra and the native owner calibration as unfinished. A fresh read of the repositories found material changes: REI PR #65 already executed the exceptional-algebra research node; BASS PR #130 already supplies the native xCoba launcher, but explicitly has no observed execution. Do not repeat either implementation.

## Exact source snapshot

| Role | Repository / PR | Commit | Tree |
|---|---|---|---|
| Independent M2 sign oracle | rei_bianchi #64 | 3f2f876b219d5c435cfd5d0dc70236a1edc1fd96 | 87a30c114b00a987beefc34d757a0eb736dc54ba |
| Exceptional compatibility oracle and parent of this handoff | rei_bianchi #65 | 7d2fe29d46e3aab4a649c3679ae028e82ef0796c | 08970b6b35bc749b37be9db6b9aaa6a2848fe06e |
| Typed owner reference | bass #129 | ac01009dec8678d9f1b8af10fb915b871e2358fd | ef10fb3199645e3962fce3ad322e5a23d5971e2f |
| Prepared native owner calibration | bass #130 | 477371143f15ef2625a7de21a5d178b09ffc1c32 | fe4c9f9b6deae0bf072dd553cd046c0a4a7801e3 |

BASS remains the common geometry owner. REI remains an independent oracle and the owner of its reionization/runtime outputs. Reading and executing the existing BASS diagnostic is not permission to edit BASS production or authority files.

## Fresh observations versus inherited execution

The PR #65 closeout comment 5548041894 reports final exact-source run 33932820559, job 101214764766, at commit 7d2fe29d46e3aab4a649c3679ae028e82ef0796c. In this session the workflow-job step endpoint was read: checkout, source binding, frozen tests, algebra/numerical sweep and artifact upload actually completed successfully. Test counts and residual magnitudes below are the recorded prior-run results, not a new rerun in this session:

- ten frozen tests, no failures/errors/skips;
- 26 exact-zero certificate entries;
- both N22=0 exceptional charts covered;
- nine 80-digit mpmath samples, reported maximum comparison/residual 6.33211791714577e-72 against 1e-60;
- artifact 9959145017, ZIP digest 607c8dc15a88b318aef29fc7fd45eb9de24ce03f12a5480d61d920bb30959157.

BASS #130 is PREPARED_UNEXECUTED. Its PR body and all four new diagnostic files were read. Its discussion had no native execution receipt when checked. No test or native PASS is inferred from those sources.

## Execution capability in the publishing session

One container process probe and one independent Python probe returned ClientError before process start. Wolfram Context and a minimal kernel/package-locator evaluation both returned MCP SSE HTTP 404 before any kernel result. No fresh SymPy, mpmath, Octave, Sage, Singular, Lean or xAct computation was obtained. The same failed execution routes were not repeatedly retried.

GitHub and Atlassian read/write actions were available after current tool discovery. Earlier claims that all writes were unavailable are session-specific, not permanent facts. This handoff is a documentation publication, not a new scientific execution certificate.

## PHYS-MATH review

Keep signature (-,+,+,+), epsilon_123=+1, tau=c*t, positive K_ab=h_a^c h_b^d nabla_c n_d, q_a=-h_a^c T_cd n^d, and kappa_G=8*pi*G/c^4.

For C_a=D^b K_ab-D_a K, the independent reference target is M_a=-C_a-kappa_G*q_a. A view adapter must transform all-lower curvature and the Ricci contraction together; physical Ricci must not be negated merely because the all-lower representation changes.

The native target metric is

    ds^2=-d tau^2+exp(2 H1 tau) dx^2
         +exp(2 H2 tau-2 a0 x) dy^2
         +exp(2 H3 tau-2 a0 x) dz^2.

Coordinates have length dimension; H1,H2,H3,a0 have L^-1. Its normal is unit and future-directed. The sentinel a0=H1=1/ell, H2=H3=0, tau=x=0, ell>0 is off shell: it is a sign diagnostic, not a cosmological solution. The source's old-momentum discrepancy target is +4/ell^2. The native producer must calculate curvature before making this comparison; that number is not permission to assign a result.

The new REI exceptional oracle uses L with det L=0, trace L=-6A, A!=0. Cayley-Hamilton gives L^2=-6A L, hence P=-L/(6A), Q=I-P are complementary oblique projectors. Q q_perp=0 and Sigma_perp=kappa_G*q_perp/(6A)+Q w are consistent with the prior Moore-Penrose description: for compatible q, any difference of particular solutions lies in ker L. The oblique projectors are not generally orthogonal. These pointwise statements do not prove constraint propagation, matter admissibility, finite-tilt dynamics or background evolution.

## PHYS-MATH-CODE review

The existing native launcher and Wolfram source were inspected, not executed.

- `calibrate.wls` loads only the pinned activation helper, not the full BASS initializer. It calls xTensor/xCoba DefMetric, MetricInBasis, MetricCompute, ComponentArray and ToValues.
- Native Riemann/Ricci feed the native Einstein projection. The comparison path separately differentiates the coordinate metric to Christoffel and curvature, then constructs spatial K, curvature and divergence.
- `run_native.py` requests a new output outside the checkout, checks source cleanliness and input hashes before/after, writes a checkpoint, records logs, handles timeout/process-group termination, and publishes a process receipt.
- Admission requires exit zero, no timeout, all twelve exact named checks, no recorded computation messages, correct stage/status and archive identity, and unchanged clean source.
- The launcher records source HEAD/tree; it does not itself compare them with the exact PR #130 constants. The receiving operator must perform that comparison before launch and repeat it when evaluating the receipt. This is an operator precondition, not a new production patch.
- `native_xact_evaluated=true` alone is not PASS. Missing components, native messages, nonzero residuals, unavailable kernel or absent receipt remain failures/blocks.
- No source defect is declared fixed by this review. Syntax/API/runtime behaviour is still unexecuted.

The generic Bianchi-V checks are useful native calibration, not a proof for every Bianchi family, arbitrary lapse/shift, the exceptional VI branch, the complete abstract H/M/T/S bridge, or constraint propagation.

## Visual boundary

REI #64 and #65 generated PNG/SVG and exact data, but direct image/reduced-print inspection remains open. This session could not render the artifacts. Do not call an image audit complete from a filename, checksum or plotting exit code. Exact-zero markers and positive display floors must remain distinct.

## Method references actually used

SciSpace returned van Elst and Uggla's orthonormal-frame work (DOI 10.1088/0264-9381/14/9/021) and other 1+3 references. The arXiv abstract at https://arxiv.org/abs/gr-qc/9603026 supports the subject/method scope; no new equation-level native result is attributed to the abstract.

Official xAct documentation distinguishes abstract xTensor computations and xCoba basis/component computations: https://xact.es/xCoba/ and https://xact.es/index.html . Documentation is a method/API reference, not a result for this checkout. All external method references have authority_effect=NONE.

## After this work / next single node

Execute the already prepared BASS #130 calibration once on a genuinely usable Wolfram/xAct runtime, with exact source identity and a fresh external output directory. Preserve the first outcome. Do not generate another replacement solver or use an unrelated CAS to label the native xAct lane PASS.

The complete receiving-thread prompt is NEXT_THREAD_PROMPT_KO.md. It separates BASS diagnostic execution from REI-only publication and from the irreversible REI Rust/MPFR lane.

## Claim ceiling

This handoff makes no new native, algebra-runtime, visual, provider or scientific-admission claim. No BASS source, runtime lock, host package, attempt ref, lease, controller, worker, first interval, ready or merge change is included.

- M2/M2A research: prior bounded execution evidence retained.
- Owner-native calibration: PREPARED_UNEXECUTED, pending actual run.
- Visual review: pending.
- Constraint propagation: not proved.
- H1B1 host package census: separate, not run here.
- First interval: NO_PASS_FIRST_CANONICAL_INTERVAL.
- Provider export: NOT_AUTHORIZED.

Progress is the exact-source executable handoff and durable current-state reconciliation, not a reworded claim that the native computation succeeded.
