# Isolated thermal CX coding record

## C1 — Goal and baseline

Implement the frozen R10 contract on the existing snapshot at supplied canonical baseline eb2abcac4f44b7bc4ff532286953fcb4e353c7bb. The snapshot has no Git directory; the controller/publisher owns repository identity and commits. Read AGENTS and physmath CODING_LOOP. Python 3.12.14 stdlib is available; scipy was detected but the runtime will use stdlib only. The requested executor is the lower-tier coding agent; observed model identity is unknown because runtime telemetry is absent.

Inputs and acceptance follow CONTRACT.json and FIXTURES.json. Densities use cm^-3, thermal density eV cm^-3, defect eV, rates cm^3/s and time s. Source Rust exact frozen-rate Riccati results are prior evidence, not new implementation progress. Actual literature Savin fits will be evaluated on synthetic isolated H/D states. No cosmological histories are produced. No code or tests executed in C1.

## C2 — Equation to data and code

`State`, `Defect`, `RateProvider` and `Controls` will be immutable dataclasses. `integrate` reconstructs all species and thermal density from the original state and normalized extent. The pure H/D particle inventory includes ne=hp+dp exactly once. Savin2002 uses retained cm^3/s coefficients and closed 2.7–200000 K domain. No production module is imported or changed. `verify_thermal_cx.py` will read cached independent Decimal expectations, rather than rerunning the probe. Mapping details are in coding_evidence/C2.json. No scientific run in C2.

## C3 — Numerical design

Use the frozen adaptive SSP Heun RK2 step-doubling map. Both Euler states are interval checked; the accepted result is two halfsteps. Every RHS call is charged, including provider failures. The scalar state retains physical positivity and the provider domain by checked stages and convex updates. Counters, finite caps and partial statuses expose incomplete work. Provider approaches return the actual interior state and reached time. The local error estimate is a heuristic; neither global error nor arbitrary stiffness is certified. Cached independent exact manufactured flow and fixed-step refinement discriminate the changed thermal-feedback seam. No run in C3.

## C4 — Execution and resource plan

C5 writes the runtime and bounded verification harness. C6 runs new manufactured and changed-seam controls. C7 runs three Savin default/tight pairs and fixed Heun N=16/32/64. C8 audits saved evidence and environment without replay. C9 obtains a fresh independent review. C10 reports measured results and exact resume commands. Scientific verification cumulative wall time is capped at30 s, with one thread, zero builds/native/old suites/external reference runs. Each stage waits for immutable-capture ACK. Substantive failure evidence is preserved for root/Astra interpretation. No run in C4.

## C5 — Implementation

Completed thermal_cx.py and verify_thermal_cx.py. The module exposes immutable state/defect/provider/control records, reduction, guarded Heun map, adaptive integration and Savin JSON CLI. It preserves the last accepted state on incomplete return; initial invalid inputs have typed INVALID_INPUT records. Every attempted RHS is charged before provider evaluation. Tests read cached Decimal references and cover the new thermal seam. No tests or scientific import executed before this stage capture.

## C6 — Implementation verification

Actual command `timeout30s python3 verify_thermal_cx.py --stage C6` completed with exit0. Seven manufactured cases and17 changed-seam controls passed, including signed negative defect, reverse feedback, lambda-zero flow, both provider events, dt0/empty/no-D/zero-rate paths, invalid input, charged provider failures and work caps. The SI-equivalent field conversion passed. Independent Decimal expectations were read from the cached probe; the probe was not replayed. All saved invariant/amplitude checks passed. Actual test wall 0.051000459 s, CPU 0.050998123 s. Detailed outputs and exact command are in C6_results.json/C6_execution.json; event time differences are diagnostics.
