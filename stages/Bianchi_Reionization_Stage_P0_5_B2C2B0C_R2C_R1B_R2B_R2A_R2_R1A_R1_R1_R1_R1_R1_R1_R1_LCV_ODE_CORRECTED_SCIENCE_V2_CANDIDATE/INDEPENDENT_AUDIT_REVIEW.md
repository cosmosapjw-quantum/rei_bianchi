# INDEPENDENT EXTERNAL-AUDIT REVIEW

Reviewer role: fresh non-editing reviewer  
Review verdict: `PARTIALLY_CONFIRMED`  
Promotion decision reviewed: `HOLD / FORBIDDEN` — supported  
Review preimage report SHA-256:
`26fd6a56fc0dcaab157a6abd63a3906905a5cc42c4d6a362805c5f027c2affa7`  
Review preimage additive-manifest SHA-256:
`ba71b4860328d9535ec5709d084176ed72c749264154ae61ff769dc4e5a7f6b0`

The candidate provides useful, locally checked shadow primitives, but it does
not establish an active corrected ODE trajectory or scientific result.

Path abbreviation below: `N=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_R1_LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE`.

## Material findings

### Medium — exact resource ceilings are post-computation checks

The “bounded exact algebra” claim overstates resource enforcement. Decimal
parsing occurs before checking the 16,384-bit ceiling, and integer
exponentiation computes `a.lo**exponent` and `a.hi**exponent` before checking
result size. Very long decimal exponents or huge integer powers can consume
unbounded CPU/memory before returning `EXACT_RESOURCE_LIMIT`.

Evidence: `N/analysis/verified_backend.py:125-134`,
`N/analysis/verified_backend.py:239-255`; compare the bounded-algebra claim at
`N/CLAIM_LEDGER.md:10-11` and `N/FINAL_ODE_INTEGRATION_AUDIT.md:21-24`.

### Medium — escaped descendants can outlive the capture wall

The capture runner is not a complete hard wall against escaped descendants. It
kills only the original process group. After `killed=True`, the selector loop
has no second deadline and waits until inherited pipes close. A forked
grandchild that starts a new session can escape `killpg`, retain stdout/stderr,
and prevent capture termination.

Evidence: `N/tools/capture_audit_run.py:227-231`,
`N/tools/capture_audit_run.py:321-353`; bounded-recorder description at
`N/FINAL_ODE_INTEGRATION_AUDIT.md:155-162`. D-07 already retains complete
process/resource budgets, so this reinforces `HOLD`.

### Medium — run manifests do not bind recorder source preimages

Per-run manifests bind the child executable, argv, environment, Git
HEAD/tree/status digest and streams, but no hash of `capture_audit_run.py`. N is
untracked and absent from the recorded Git tree. The report states that capture
code changed during repair-closeout, so runs 001--003 cannot be
cryptographically tied to a specific recorder source preimage. The raw streams
remain directly inspectable and correctly hashed.

Evidence: manifest construction at `N/tools/capture_audit_run.py:374-434`;
repair history at `N/VALIDATION_LEDGER.md:80-87`.

### Medium — atomic opacity is not a complete physical-domain predicate

`atomic_opacity_per_h` can return `PhysicsStatus.OK` for an impossible
inventory, such as `N_HeII=80` with declared total `N_He=79`. It checks
negativity and the total He/H ratio but never checks absorber counts against
the corresponding total inventory. Independent probe result: status `OK`,
HeII abundance `2/25`. This does not falsify the per-H algebra, but the helper
cannot serve as a complete physical-domain predicate; D-02 remains necessary.

Evidence: `N/analysis/corrected_physics.py:128-146`.

### Low — independent oracle ignores redundant fields and may raise

The independent oracle correctly recomputes determinant, residual, digest and
enclosures and imports no candidate arithmetic. However, it ignores
`certificate.dimension` and `certificate.residual_exact_zero`; certificates
with `dimension=999` or `residual_exact_zero=False` still passed. Malformed
enclosure fields can raise `TypeError` instead of returning a failed verdict.

Evidence: `N/validation/independent_exact_oracle.py:116-160`. The mathematical
witnesses themselves remained correct.

### Low — run-002 narrative count

Run 002's raw stream says `Ran 38 tests`, while the report says “37 displayed
passing tests.” The run remains a preserved failure either way.

Evidence: `N/audit_runs/002_successor_focused/stderr.bin:20`,
`N/FINAL_ODE_INTEGRATION_AUDIT.md:250-252`.

## Confirmed evidence

- Exact preimages remained unchanged after review:
  - report SHA-256
    `26fd6a56fc0dcaab157a6abd63a3906905a5cc42c4d6a362805c5f027c2affa7`;
  - `ADDITIVE_SHA256SUMS.txt`
    `ba71b4860328d9535ec5709d084176ed72c749264154ae61ff769dc4e5a7f6b0`;
  - HEAD `111b6ace750e36e218df7fc9626c6bad2ec19971`;
  - tree `2f541ee051f0844bdeed88fd2dcba2a0c54ab035`;
  - predecessor manifest
    `df5dfb2d27ff844127a686af8c9343305376b711c8caba0aba37aff86b9dc2b2`.
- The additive manifest contains 68 entries and all 68 hashes passed. Before
  this review file was added, the candidate had 69 files; the sole unbound file
  was the additive manifest itself.
- All ten run sidecars, canonical JSON bytes, raw stream hashes/sizes,
  durations, return codes and termination values matched
  `AUDIT_RUN_INDEX.json`. Runs 001--003 remained exit-1 failures; runs 004--010
  were preserved as recorded.
- `PREDECESSOR_SHA256SUMS.txt` exactly covered all 1,012 HEAD blobs across the
  eight declared predecessor roots: no missing/extra paths, no symlinks and
  1,012/1,012 current hashes matched.
- Each 32-item table inspected contained IDs 1--32 exactly once. All 22
  enumerated R3/R4 evidence-file hashes matched `FOUR_LOOP_PROVENANCE.md`.
- N has zero tracked entries; `git grep` at HEAD found no N name or module
  imports. The active driver explicitly binds the predecessor C-stage kernel.
- Independent numerical probes passed:
  - 20,006 rational-to-binary64 enclosure checks;
  - 15,000 interval-algebra outward exports;
  - 2,000 exact binary64 sums;
  - 900 random nonsingular 1x1--3x3 systems checked against independent Cramer
    determinants/solutions;
  - 5,000 per-H opacity formula cases and 5,000 direct-share partitions;
  - 63 admission mutations and 300 valid FSM state/action cases.
- A distinct ambient-environment read-only predecessor probe reproduced the
  signed-sum exclusion, both false point certificates, double-He factor,
  nonabsorbing terminal behavior and incomplete admission. Exact command:

  `PYTHONDONTWRITEBYTECODE=1 python3 -B N/tools/predecessor_red_probe.py | jq ...`

  This was not the exact failed run-001 command/environment. None of the frozen
  failed commands 001--003 was rerun.
- Runs 007/008 have byte-identical 2,824-byte output with SHA-256
  `e353ab05f9158e319f69d3251a890ee29ca587fbcf194654a74f1c7ccac13b1b`.

## Unverifiable historical statements

- Current inspection confirms the original checkout is at the bound HEAD with
  no tracked diff and exactly two named untracked bundles. Filesystem state
  cannot independently prove that those bundles were never opened or every
  intermediate custody instant was unchanged.
- The mutable `/tmp` R3/R4 roots and their current hashes were verified, but
  creation timestamps, author identity and continuous immutability are not
  independently authenticated.
- External literature/source-refresh claims were not re-fetched; they are not
  load-bearing for this source-based verdict.

## Residual claim ceiling

Supported: additive, untracked shadow implementation; exact rational finite
algebra on exercised inputs; outward binary64 export; exact point certificates
up to dimension three with independent mathematical replay;
convention-qualified per-H opacity/direct shares; typed admission/FSM behavior;
locally captured diagnostic receipts.

Not supported: a general interval/Krawczyk or transcendental backend, complete
physical-domain validation, continuous/global/QoI/event error control,
conservative hybrid restart, corrected independent BDF/reference trajectory,
exact pinned-runtime parity, active routing, package/security closure,
production history, endpoint authority, performance claims, or publication
science.
