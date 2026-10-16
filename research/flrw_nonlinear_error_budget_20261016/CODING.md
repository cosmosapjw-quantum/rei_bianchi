# Nonlinear residual diagnostic implementation

## C1 — goal and baseline

The frozen R9/R10 contract maps a supplied four-variable backward-Euler residual/Jacobian packet into frozen native/adaptive scales and reports a binary64 linear correction, conditioning, backward error and thermal projection. The source baseline is commit fdfda0fec423ccb7175552c7dc066be93ce347e1, driver blob 2a16fa8d898588d859eff2c7750a5f8496cadd0c. The local Rust snapshot is stale and is neither imported nor modified. All work stays in this unit. R10 immutable capture released coding.

SOURCE_BINDING_HANDOFF.md is a post-R10 clarification: a future observer changes its producer blob and migrates the diagnostic binding only after a scoped unchanged-equation seam comparison. That future operation is outside this implementation. Existing owner production authorization persists; the current scope respects active SOURCE009 ownership. Actual missing stage telemetry gives HOLD, not a new global execution-permission gate.

Existing NCP/PL cumulative156.5376037069618/300s and deadline1792122617.77407 remain unchanged. New small-fixture time is measured separately; no old oracle or PL suite is rerun.

## C2 — equations, packet and code

`solve_scaled` maps supplied residual/Jacobian and explicit frozen scales to A,b,z,delta and the scaled matrix/linear-system diagnostics. `analyze_stage` constructs native/adaptive chemical scales, verifies supplied same-state/context and current baseline source binding, then evaluates the EOS projection. It never imports or executes the producer. The JSON CLI writes finite results plus measured execution evidence to a fresh directory using atomic durable checkpoint writes. All equation/field paths are recorded in coding_evidence/C2.json.

## C3 — numerical design

The binary64 core uses maximum-absolute partial row pivots in a fixed 4x4 augmented solve/inverse. Only an exactly zero computed pivot is singular; finite ill-conditioning remains a reported diagnostic. Frozen SR and Sy build A and b once, then max vector/row-sum norms give correction, condition estimate and normwise backward error. All arithmetic must remain finite. Thermal exact-map evaluation uses linearDeltaT/(1+dD/D) after corrected-domain validation; invalid corrected states retain the linear diagnostic and null exact map. No state is committed or physical tolerance changed.

## C4 — bounded execution

C5 completes module/CLI/template and tests. C6 checks guards, finite serialization and fresh durable IO. The disjoint C7 harness owner compares new binary64 results with the already completed exact oracle RESULT; no oracle is run again. C8 uses only fixed small conditioning and unequal old/current-energy-scale cases. Each execution has a 30-second outer limit and actual time evidence; no large benchmark or native work is planned. Existing NCP/PL debit and deadline remain separate and unchanged. C9/C10 proceed from captured observed evidence.

## C5 — implemented diagnostic and CLI

The standalone module implements the frozen four-variable scaled core, stage adapter and JSON CLI. It uses exact-zero partial-pivot singular classification, finite arithmetic checks and the frozen EOS map. The adapter validates metadata and accepted-stage residual inequality without acquiring telemetry. The actual packet template deliberately contains null telemetry and is expected to HOLD. Result and measured receipt writes use same-directory temporary files, file flush/fsync, atomic replacement and supported directory fsync. The module is the only runtime code dependency. All new Python sources syntax-parse; C6–C8 executions have not yet run.
