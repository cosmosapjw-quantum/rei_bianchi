# C10 implementation and execution facts

## Source scope

The frozen native driver prefix SHA-256 remains `fd5b040bceb2134dc92c09f4bf49e6b04be2e8115f553c19fe989f472f32c01d`; the original physical-birth file remains `3de9ca2dc4a442cb6d4d7fa6eaeb0f993ffc634d6ffdeb2b9410faec38fee0fa`. Existing transport owner prefix is `79b4d0972db8ed65ba64e71edc7530e46274ce8299197295bf24c800f86dbee9`. Additive child modules and appended hooks supply the new behavior. Default, adaptive, checkpoint, rate, source normalization and EOS bodies are unchanged.

Contract A implements native-node forward Euler with actual two-stage CFL rejection, reconstruction at each SSPRK stage, conservative event/heat/binding weights, endpoint anchored moments and exact identity branches. Contract B explicitly selects common gas midpoint opacity and microphysics, uses one absorption RHS addition, original serial four-variable Newton and chronological source births, and commits physical state only after complete success. The scalar attenuation enum is explicitly ignored only by the named new SSPRK APIs. No automatic subcycling is present.

## One observed clock defect and bounded repair

The first coupled execution used `ln(end/begin)` on nearby binary64 endpoints. Independent review found concrete cancellation; this was not a conclusion about Newton tolerance alone. Original source/results/receipts are preserved in `execution_coupled_pre_clock` and `native_files_pre_clock`. The sole repaired calculation uses `ln1p((end-begin)/begin)`. The accepted gas-solve dt is carried in the new report and reused by an additive accepted-segment constructor; the original V14 constructor is untouched. Diagnostic macro dx uses the same stable relative form. Source weights, rates, ICs, closure, tolerance 1e-15 and refinement levels are unchanged.

The actual worst pre-clock segment was source GL2 N512, step386, segment2. Independent review confirmed all 5,952 repaired birth-segment dt values are bit-identical to the native stable formula. The exact-binary64 endpoint/same-native-H accumulated sourceGL2 N512 discrepancy changed from about +112.286124136 seconds to -4.88281e-7 seconds. An earlier +112.28144-second estimate used CSV decimal strings and is preserved as a distinct approximation. The same-native-H versus decimal-physical-H contribution is separately identified, not conflated with the repaired ratio cancellation.

## Actual bounded execution

Seven transport tests and seven coupled tests pass: 14 unique targeted tests. One added regression uses the actual worst segment and checks stable-log accuracy plus bit identity of accepted solve/report dt. No historical tests or matrices were rerun. Stage A has 52 transport summary rows; adding diagnostic columns replayed the same cases. Coupled execution has 16 unique histories: six fixed-geometry evolving-gas histories, five source GL2 histories and five seeded DisabledGauss2 histories. The repaired campaign repeats those same 16 cases once; it does not create 32 unique histories. Repaired fixed geometry completed in 3.53 seconds and births in 37.59 seconds; all exits zero under unchanged CPU2/time caps. The fixed-geometry numeric rows are bit-identical across the repair except wall time.

Actual post-clock raw audit maxima include full energy about 2.93e-14 eV/H and stage optical depth about 0.4652814346. The largest accepted nonlinear residual is about 9.97713e-16 at the existing configured 1e-15. Finest sourceGL2 successive-difference exponents are w=2.03401 and T=2.02319 after repair. Source-on HeIII differences remain near the numeric floor and irregular. Scientific admission and claim boundaries belong to the root research report and independent review; a zero exit is not an order proof.

## Restoration and runner verification

Normal Python source files `restore_ssprk2_native.py` and `run_ssprk2_native.py` reconstruct through the existing V12/V13/V14 chain, verify exact old prefixes and all final Rust/package source hashes, append hooks once, and preserve command/stdout/stderr/exit/timing records. The runner supports jobs1..2, prepare-only, and transport/fixed/birth/all modes. Actual compiler versions are recorded without a sandbox-version downgrade requirement. Host/platform/UTC are recorded without inferring NCP from a hostname. Delivery-session NCP status is explicitly historical context, not a claim about a future runner execution.

Actual wrapper checks: Python compile, CLI help, fresh restoration and prepare-only compiler metadata, and an intentionally absent compiler returning127 with a failed-stage receipt. The wrapper did not replay a native scientific matrix during verification. Its build/tests/run modes are handoff code, separate from the independently executed native evidence.

The four-panel PNG/PDF plot uses only actual raw CSV points with hash-linked `PLOT_DATA.json`; slope2/3 lines are guides, not fits. No new scientific execution was used to create it. New NCP execution during this delivery session is NOT_RUN because the specified local key was absent and the remote connector paused calls at monthly usage. No SSH probe/retry was attempted.
