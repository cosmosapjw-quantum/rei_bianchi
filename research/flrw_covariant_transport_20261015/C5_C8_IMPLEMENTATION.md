# C5–C8 native covariant implementation: observed return

Baseline is PR150 (`8aa6cd081f218e3a4ff6180a547c790df234a073`). The new
`axbi_covariant_transport` module stores four fixed-length ray-major arrays:
number/H, reference energy/H, populated support lower endpoint and upper
endpoint. Geometry changes the ray energy scale and direction without moving
these stored cells. Inert redshifted photons remain in the inventory.

C5 source deposition integrates positive GL8 subcells of each original frozen
source cell, intersected with the mapped reference grid. The current angular
Jacobian enters once, followed by the existing normalized local-isotropic
weight. Source ledgers contain the number and actual energy injected by this
quadrature. Both physical source cutoffs and every selected signed-shear case
at z4 fit inside the default reference domain [13.6,512] eV.

C6 reconstruction uses the bounded exponential two-moment closure, splits at
the actual fit cutoffs divided by the ray scale, and fits positive discrete
weights to the stored number and first moment before Newton. Fit cutoffs remain
distinct from binding thresholds. Each Newton trial uses the same cached nodes
for backward-Euler survivors, Gamma, heat and event diagnostics. Its caller
retains the coupled gas RHS as the event owner. No centroid cross section or
second frozen-gas absorption update is present.

C7 support is an envelope of actual populated source intervals. It is retained
through reconstruction and absorption rather than contracted to quadrature
node extrema or expanded to whole bins. True support deltas use one actual
energy. Near-endpoint broad supports use the exponential endpoint-distance
coordinate; the explicitly bounded tail beyond48 is recorded in cache
diagnostics, and positive moment fitting still satisfies the frozen64/128-eps
checks. Exact endpoint equality at the resolution of represented N/U forces an
endpoint delta; no tolerance-based broad-support delta fallback is used.

C8 proper stage time continues to use the direct finite log1p/GL8 interval
increment integrated in PR150. That background implementation was unchanged
by this unit, and its earlier targeted results were reused rather than rerun.

## First failure and authorized repair

The first new core run compiled successfully and passed6 of7 tests. The
near-endpoint output state failed its support admissibility check because
ordinary independent N/U sums rounded U/N below the retained support. Root
authorized one targeted repair: compensated outgoing count plus a compensated
first moment centered about the nearer support endpoint. Primary admissibility
compares U with lo*N and hi*N, and near-endpoint reconstruction uses a centered
mean. This changed numerical accumulation without changing a physical
tolerance or clipping a moment. The dependent rerun passed all7 tests,
including near-low and near-high endpoint absorption and subsequent prepare.

Exact commands, first failure and rerun are preserved in
`raw/covariant_transport_tests*`. The first run took6.641s including compilation;
the repaired run took11.032s including compilation and0.17s for tests. The
additional signed-family source assertions were covered by the controller's
1.104s targeted source-support test, recorded in
`raw/core_signed_source_support_test.*`. No historical28-test campaign ran.

## Bounded diagnostic and NCP preparation

The controller-authorized read-only checkpoint diagnostic reproduced exactly
three full-versus-two-half comparisons from q128 checkpoint12000. It used
9 tentative steps,63 RHS evaluations and0.769s including example compilation.
For h,h/2,h/4 the normalized photon-number errors were respectively
3.963479149419194e-6,1.0722307640564845e-6,2.794455764758477e-7.
The measured component maximum agreed with the native error metric. Gas,
thermal, per-cell, source, event and first-HI-straddling-cell Gamma/heat values
are preserved in `raw/q128_step_diagnostic_001/diagnostic.json`. This reports
measurements; physical interpretation and further repair decisions belong to
the controller review.

The allowlisted67-member source archive was staged to the fresh NCP task
`/root/REI_FLRW_COVARIANT_20261015_001`. All staged source hashes passed. A fresh
offline NCP release build succeeded in5.827s with a4-worker build allocation
and8GiB address-space limit. The staged compiled-source identity equals the
local pilot identity. Receipts are in `raw/ncp_stage_build_receipt.json`.
Scientific NCP launches remain zero at this return; no full-history admission
or completion is asserted. The prepared full launch controls preserve the
two-case, single-native-thread,8GiB/case,4GiB/case and cumulative12h contract.

The executor was the assigned implementation worker. Its runtime model name
was not exposed; no requested model label is presented as an observed identity.
