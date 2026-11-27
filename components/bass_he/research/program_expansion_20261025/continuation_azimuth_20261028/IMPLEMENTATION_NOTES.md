# AZIMUTH09 implementation preparation

## Identity and scope

The new unit imports `../continuation_kinematic_20261028/src/kinematic.py` by an exact relative file path and uses its `PhysicalAngularMap`, `BernsteinDensity`, `SetBounds` and integration implementation unchanged. The inherited base is local `b3ac835c3fa0b1aa09606ab6e8cfdc08699bab25`, remote `e56573a5961623c49428f6f8d566fb13edf8a6b9`, exact tree `0bc4f06d711fd30e8d7d71e2dc2d69ec2bf2e363`. No old suite or plot is executed by this unit.

The API requires explicit `UNIFORM_DECLARED`. It accepts exact rational-turn `(start,width)` arcs, up to 8 patches per detector and 8 distinct active polar windows. Empty arcs and singleton polar windows still undergo input validation. Canonical inherited interval union handles overlapping or contacting polar intervals. Sector endpoint splitting, including all halfturn endpoints, makes membership constant inside each exact strip. The strip midpoint selects this constant mask; it is not quadrature of the polar law. Each distinct active polar window calls the inherited preimage solver once. The minus direction uses the reflected preimage of the same physical map, not a negated lab polar cosine.

All reported event and count bounds use `Fraction`. Boolean events carry actual uncertainty area and the Bernstein-maximum area bound; the global `10 N B delta` is checked separately. Inclusive and assignment counts sum component bounds. Energy and daughter-count widths scale explicitly. Conditional ratios distinguish certified positive denominators, exactly zero denominators and unresolved denominators. No automatic empirical normalization, flux, thermal, deposition or species binding is supplied.

## Planned verification and stored evidence

`tests/test_azimuth.py` defines 22 new test methods. Independent exact grid-cell enumeration supports full polar and analytic forward/backward polar windows for the manufactured model. Its expected values use neither the production preimage nor integration implementation. Additional direct Lorentz momentum checks cover fold and stopped cases. The inherited API comparison uses the same explicit manual delta and calls only that affected response, without importing or running any old test suite.

`validate_once.py` writes exact fraction bounds and separate display floats, 17 rotation rows, four explicit counterfactual diagnostic controls, default/manual-delta rows, three native-energy finite-sector rows, per-test timings, operation counts and strip sets in the same single run. These controls are analytic counterfactual diagnostics, not a separate mutated-implementation campaign. Native rest-energy source bytes are checked against the inherited NIST SHA256. Manufactured rho is explicitly not empirical DCS.

`plot_saved.py` reads only this saved JSON. The 2x2 figure displays the triangular rotation oracle, diagnostic controls, native finite-sector measures and actual versus area-based widths. It imports no scientific modules. The runner uses a workspace MPLCONFIGDIR seeded with the prior font cache by copying that cache; no prior plot is rerun or modified. PNG and SVG are generated once.

## Execution boundary

The runner and outer measurement scripts are adapted from the repaired prior runner. Validation has CPU 12 s, wall 40 s and AS 512 MiB; saved-only plotting has CPU 8 s, wall 20 s and AS 512 MiB. Threads are fixed at 1. Every status call uses per-command Git preload/index options. The pinned source must equal current HEAD and the tracked working tree must be clean. The inner receipt records source commit, tree and source hashes. The outer receipt measures the complete runner subprocess, its waited descendants and final inner receipts, with outer orchestration CPU reported separately. Final external receipt serialization and the outer interpreter startup/shutdown are outside that explicitly stated boundary.

At preparation, science validation and plot executions are **0**. Controller authorization of the immutable source pin and exact command is required before either runs. A separate syntax check does not certify scientific output. Requested executor identity and observed runtime identity must be recorded separately; this code does not claim to observe its model runtime.

## Preparation-only inspection after session recovery

The executor requested by the controller is `gpt-6.1-sol`; the observed runtime model identity is `UNAVAILABLE` because no execution telemetry exposes it. The requested identity is not asserted as an observed runtime identity.

A nonexecuting AST syntax check parsed all six unit Python files plus the existing preparation helper. JSON parsing accepted the four unit metadata files, `node --check` accepted the publication helper, and static AST enumeration found 22 `test_` methods. These are syntax and structure observations only; no scientific module was imported and no suite or plot was run.

The six explicitly selected public survey summaries were copied into `preflight/` and the precontract review into `review/`, preserving each source byte. No raw provider directory, private owner data, or PDF was copied. The workspace Matplotlib configuration already contains `fontlist-v390.json`. Read-only host observations before execution were 9 logical CPUs/affinity CPUs, cgroup CPU quota `1600000/200000` (8 CPU equivalents), cgroup memory maximum 8589934592 bytes, and cpuset `0-8`; the prescribed execution remains one thread with the frozen process address-space cap.
