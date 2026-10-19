# RUN16 feedback unit: latest durable handoff

**Status:** the bounded unit is complete; all science source and execution
results in this directory are frozen. Do not repeat the archived M2 runs or the
completed prefix controls just to establish their current status.

## Latest actual work

1. Read immutable original RUN13 gas/full-state code and actual tight snapshots
   from clean Git commit `6405bcba8ec654bf3ab98182be344cd8c3915b97`.
2. Three recorded-state derivative/defect probes: 85 actual native RHS calls,
   no trajectory solves in that first subunit. Its code and `execution01/`
   result remain unchanged after execution.
3. Three new five-dimensional **source-free gas-only prefix IVPs** on
   `z=[0,0.004989333151072248]`: two nominal tolerance settings at max-step
   prefix/4, then one tighter-setting run at prefix/8 because the first pair
   had identical grids. Counts are62+62+122=246 actual native RHS calls.
4. Combined native RHS calls:331. Full transport IVPs:0. Archived M2
   standard/tight reruns:0. Historical complete test suite reruns:0.

The first prefix pair has4accepted steps per run; the halved-step run has8.
At the common five samples, halving the step changed HI by0 in the evaluated
float64 values, temperature by at most3.637978807091713e-12K and a normalized
gas coordinate by at most2.220446049250313e-16.

## New scientific result and limits

The componentwise checkpoint-PCHIP slope at the initial point has the opposite
sign from the original native HI gas RHS. The subsequent short source-free
native calculation quantifies the initial interpolant bias: at the first
photon birth, PCHIP minus native HI relative difference is
`-1.5712776951781748e-6`, and the temperature difference is
`+0.04470254583975475K` using the halved-step reference.

The new native first-birth state has `g_HI=0.9000000534472483` and
`T=9999.925747777985K`. This is a numerically checked five-gas-coordinate
state, **not** a full transport/ledger checkpoint. It has no photon solution
after source activation and supplies no rigorous all-time tube or survivor
error bound. No photons are active within the prefix, so do not convert that
pre-birth gas discrepancy directly into an endpoint-survivor error.

Recorded gas Jacobian norms are about33.6, with infinity logarithmic norms
about0.14 and a charge-exchange mode near-16.74 per normalizedz. These are
point estimates. Native gas thermal feedback acts through chemistry; the
direct gas-temperature column in the depth-rate block is zero for this
prescribed opacity model.

## Next genuinely incomplete calculation

Use [NEXT_NODE_INPUT_CONTRACT.json](NEXT_NODE_INPUT_CONTRACT.json) and
[DERIVATION_AND_NEXT_NODE.md](DERIVATION_AND_NEXT_NODE.md). Construct a
physical five-coordinate gas reference, reconstruct optical depths with
bounded quadrature on the actual threshold/geometry/source partition, and
enclose the full native-plus-photo gas residual over time. Close a comparison
estimate on an admissible tube, including source-forcing error when replacing
the first-cell spectral quadrature by a continuous measure.

The all-time photo-forcing defect must include absorption and heating from the
whole modified first cell. A small endpoint survivor component does not bound
earlier gas heating. The fixed160births/GL8 and47other spectral cells remain
the old comparison setting; their continuum obligations are still open.

The parent owns final RUN16 publication and backups. This subagent has made no
remote writes for this unit. Source/evidence identities are listed in the
execution receipts and `FEEDBACK_DELIVERY_MANIFEST.json`; all original112
files read for these diagnostics were rechecked unchanged.

## Entry points

- [Point-unit Korean report](README_KO.md)
- [New prefix numerical report](SOURCE_FREE_PREFIX_ADDENDUM_KO.md)
- [Point execution receipt](EXECUTION_RECEIPT.json)
- [Prefix execution receipt](PREFIX_EXECUTION_RECEIPT.json)
- [Full point evidence](execution01/RECORDED_STATE_FEEDBACK.json)
- [Latest halved-step prefix evidence](prefix_stephalf_execution01/PREFIX_STEP_HALVING.json)

The original gas executable hash remains
`3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`.
Every numerical driver takes explicit source/binary/evidence paths and writes
only a new output directory. The recorded original runtime paths are provenance;
use the CLI options when executing in a different restored environment.
