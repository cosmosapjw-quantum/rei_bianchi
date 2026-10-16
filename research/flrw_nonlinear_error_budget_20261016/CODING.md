# Nonlinear residual diagnostic implementation

## C1 — goal and baseline

The frozen R9/R10 contract maps a supplied four-variable backward-Euler residual/Jacobian packet into frozen native/adaptive scales and reports a binary64 linear correction, conditioning, backward error and thermal projection. The source baseline is commit fdfda0fec423ccb7175552c7dc066be93ce347e1, driver blob 2a16fa8d898588d859eff2c7750a5f8496cadd0c. The local Rust snapshot is stale and is neither imported nor modified. All work stays in this unit. R10 immutable capture released coding.

SOURCE_BINDING_HANDOFF.md is a post-R10 clarification: a future observer changes its producer blob and migrates the diagnostic binding only after a scoped unchanged-equation seam comparison. That future operation is outside this implementation. Existing owner production authorization persists; the current scope respects active SOURCE009 ownership. Actual missing stage telemetry gives HOLD, not a new global execution-permission gate.

Existing NCP/PL cumulative156.5376037069618/300s and deadline1792122617.77407 remain unchanged. New small-fixture time is measured separately; no old oracle or PL suite is rerun.

## C2 — equations, packet and code

`solve_scaled` maps supplied residual/Jacobian and explicit frozen scales to A,b,z,delta and the scaled matrix/linear-system diagnostics. `analyze_stage` constructs native/adaptive chemical scales, verifies supplied same-state/context and current baseline source binding, then evaluates the EOS projection. It never imports or executes the producer. The JSON CLI writes finite results plus measured execution evidence to a fresh directory using atomic durable checkpoint writes. All equation/field paths are recorded in coding_evidence/C2.json.
