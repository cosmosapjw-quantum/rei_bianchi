# REI original IGM owner research loop — 2026-11-15

## Scientific target and frozen inputs

Advance the original `REI-AXBI-GOAL-20261014` abundance goal: homogeneous,
non-tilted, axisymmetric Bianchi I and matched FLRW H/He/electron abundance
histories over mean redshift 20 to 4, with chronological proper-time and gas
temperature curves. The selected model remains
`PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`: fixed physical densities, Plancklike
background, MD14 emissivity, 50,000 K blackbody, escape fraction 0.2, cold
initial temperature 8.098143045 K, primary-only Case A escape. No replacement
by F05 local-OTS chemistry or by the F08 constant-H S0 experiment.

The restored saved histories are ZERO, SHEAR_HALF_PLUS (+0.005),
SHEAR_HALF_MINUS (-0.005), and SHEAR_MINUS (-0.01). Each has 312,238 saved
states. Their full bytes must match their original completed-case hashes.
SHEAR_PLUS (+0.01) is not a completed history. Never infer it from parity.
Original chemistry, thermal state, source, clock, tolerances and failures
are immutable. This loop postprocesses actual saved physical states;
it performs zero new coupled ODE trajectories.

## Concrete outputs and acceptance

1. Owner decisions for the latest BASS, REC, BASS_HE, WU088_HH and bass_cr
   results, stating the source family and the actual consumer action.
2. Six-species abundance tables and chronological figures, normalized as
   both element fractions and Y_i = n_i/(n_H + 4 n_He).
3. Separate comparisons at equal mean scale factor and equal elapsed
   proper time, retaining both reference/candidate coordinates. Quantify
   the exact discrete decomposition into fixed-scale response and clock
   displacement. Elapsed time starts at each model's zbar=20 surface;
   it is not cosmic age or equal proper time since the big bang.
4. First saved-trajectory upward crossings of x_HII=0.1,0.5,0.9, with
   native brackets, paired redshift/time shifts and interpolation-method
   sensitivity. Homogeneous x_HII is not a volume filling fraction.
5. A secondary source-qualified REC Thomson consumer using the actual
   proper electron histories. Its output is the zbar20-to4 interval and
   a conditional receiver at zbar4; the unknown observer tail is null.
   This secondary product cannot substitute for abundance progress.
6. Same-author adversarial verification with a separately implemented
   crossing calculation, background-clock integration, conservation and
   frame/coordinate negative cases. No claim of independent authorship.

Postprocessing agreement is not an error bound on the original evolution.
AX11 time/energy/angle convergence and AX12 source/IC robustness remain
unresolved. No observation, continuum certificate, full family completion,
canonical node completion or production promotion follows from these data.

## Bounded execution and publication

Cloud execution only for this lightweight postprocessing: at most two
full reducer executions (180 s each), one targeted adversarial run (90 s),
and one figure render/repair (60 s each). Stop on source hash, coordinate,
domain, charge, conservation or output-contract failure. Do not reset any
historical solver budget or launch a long trajectory.

Theory R1-R10 and coding C1-C10 run as ten paired checkpoints; each checkpoint
records evidence, a Git commit/publication and an immutable backup archive.
The central DAG is the preserved 88-node authority, 28/88 completed;
working 33/88 is a distinct, non-additive historical view. Original AX
subtasks are reported by ID without manufacturing a new completion count.

Drift test at every checkpoint: does this step recover usable original
physical inputs, produce an abundance/clock/milestone result, validate an
actual new claim, or deliver that result? If not, stop that branch of work.
No subagents; no local-worker modifications; no main merge or force push.
