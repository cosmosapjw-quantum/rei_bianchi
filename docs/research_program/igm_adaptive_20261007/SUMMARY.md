# Adaptive continuous-source H/He IGM checkpoint

Date: 2026-10-07 UTC. Independent decision: **ACCEPT SCOPED**.

This checkpoint adds an opt-in first-order backward-Euler step-doubling driver with private trial rollback, an actual two-half-step accepted state, cancellation-aware radiation/ledger controls, and detached observation solves. The existing fixed-step driver remains the default and its checked outputs are byte-identical.

## Accepted experiment

The manufactured homogeneous FLRW fixture spans z=12 to 11.5, with 32 threshold-band panels per segment (512 fixed nodes), relative tolerance 1e-6, absolute-scale multiplier 1000, maximum delta ln(a) 0.0002, minimum retry width 1e-12, and explicitly enabled guarded-research policy. See the [runner guide](../../igm_adaptive_v1.md) for the invocation and failure semantics.

- All 37 protected fields and both unchanged global number/energy budgets pass on regular21, dense81, and offphase61 schedules against same-grid 512-node and refined 1024-node independent Radau histories.
- Worst allowance ratio: 0.9811165189523667, offphase Gamma_HeII against the refined reference. This is a narrow empirical spectral margin.
- Every schedule pair has 21 common epochs with 41 required columns equal by float64 bits. Primary state, final count/log spectrum, and primary diagnostics are identical.
- Independent verification: 249 Rust tests and 32 Python tests, including executable CLI checks. An independently built release executable has the same SHA256.
- Primary work: 52,176 accepted macros, 104,336 accepted primitive transactions, 157,889 attempted transactions, 464 LTE rejections, and one physical rejection. Sixteen adjacent-f64 exceptions are separately counted, guarded, and explicitly unestimated. Maximum guard ratio: 0.0004192599413256698.

## Evidence index

- [Independent acceptance](INDEPENDENT_ACCEPTANCE.json), [results](RESULTS.json), and [field-level comparisons](FIELD_SUMMARY.csv)
- [Unchanged criteria and reference identities](VALIDATION_CRITERIA.json), [program/source identity](SOURCE_IDENTITY.json), and [run receipts](RUN_RECEIPTS.json)
- [Output invariance](OUTPUT_INVARIANCE.json) and [checked fixed-path invariance](FIXED_PATH_INVARIANCE.json)
- [Retained negative results](NEGATIVE_RESULTS.json)
- Exact candidate inputs and histories: [regular21](cases/regular21), [dense81](cases/dense81), [offphase61](cases/offphase61)
- [All 16 explicit microstep records and accepted diagnostics](cases/dense81/status.json); [common final primary state](cases/dense81/primary_state.csv); [common final count/log spectrum](cases/dense81/nodes_final.csv)
- [Evidence checksums](ARTIFACT_SHA256.json)

The histories contain additional numeric diagnostic columns. A retained last-error value is not a current estimate when primary_last_error_measured=0. Original field allowances and number/energy ledgers determine scientific acceptance, not these diagnostic columns.

## Failures and qualifications

The unscaled profile fails at the minimum-step/physical-ledger floor near source onset. Strict mode rejects an unsplittable hard boundary. The absolute-scale-100 run was stopped for cost and remains incomplete. Completed absolute-scale 10000 and 3000 runs fail the original field criteria; the completed same-grid ladder is 2.151044676 → 1.542357131 → 0.914122262. The loosest level used an earlier captured producer and is identified accordingly. The original pulsed-source accuracy failure remains unchanged.

Acceptance uses the original field-specific absolute-plus-relative allowances and is not a uniform 0.1% relative-error statement. The ladder shows empirical reduction only, without a universal tolerance scaling law. Same-grid temporal/splitting error and spectral error remain separate. Exact offphase61 references are archived retight histories; a new tight/retight pair at exactly those 61 epochs was not generated. New dense81 tightening and common-epoch checks are recorded. Finite EOS/electron decomposition is endpoint algebra rather than a variational propagator or cumulative CMB-error attribution.

Local estimates, guarded motion and conservation do not prove a global or continuum error bound. No all-step LTE, production-readiness, observed/full-EoR, Bianchi-coupling, adaptive-spectrum, restart, arbitrary-state theorem, or speedup claim is made. Reported timing is shared-load context only.

## Repository status and rollback

Incremental parent: 865c16bac2d22ac30f8192f69cae9c64ed50e3b8. Seven implementation/documentation paths are updated; unrelated repository paths are preserved. This is a draft-PR research checkpoint, with no merge or release. Prior-head CI failed at cargo fmt on 12 unchanged legacy paths and skipped the subsequent test step. Exact new-head CI must be reported separately; local tests are not a green-CI claim.

Rollback is a revert of this additive checkpoint commit, or simply continuing to use the unchanged fixed-step driver. There are no dependency changes, migrations, or external runtime-state changes.
