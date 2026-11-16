# T1 ZERO/PLUS owner-consumption contract

Goal: `REI-AXBI-GOAL-20261014`. Consumer: `rei_bianchi` scenario/IC/history and
scientific-admission owner, AX11. Central pin remains
`56dc609ea9b801c88d3364aed3eee140b3a20d46`.

The admitted five-case AX08 family is reused. The first new full-IC wave evolves
only ZERO and PLUS with local target `2.5e-6`, original initial `dln_a=1e-4`,
energy16 / mu8 / background4096, and all original science tolerances. T0 has
local target `1e-5`. These adaptive targets are not fixed-step spacings; their
ratio alone does not specify a convergence order.

## Coordinates and quantities

The metric, source and frame remain the conditional homogeneous non-tilted
axisymmetric Bianchi I H/He Case-A primary-only scenario. The proper clock is
elapsed seconds since each model's zbar20. The endpoint is native a=0.2,
zbar4. No F05/F08 histories or source conventions enter this comparison.

Let X_q^(k)(s) denote one of the five element fractions, electrons per H
nucleus, or gas temperature in kelvin. q is ZERO or PLUS(+0.01), k=0,1 is
T0,T1, and s is either the same scale factor or the same elapsed proper time.
Keep all of the following signed quantities:

    D01_ZERO(s) = X_ZERO^(1)(s) - X_ZERO^(0)(s)
    D01_PLUS(s) = X_PLUS^(1)(s) - X_PLUS^(0)(s)
    Delta_k(s) = X_PLUS^(k)(s) - X_ZERO^(k)(s)
    D01_pair(s) = Delta_1(s) - Delta_0(s)

In real arithmetic D01_pair = D01_PLUS - D01_ZERO. This identity explains why
a small paired change can coexist with a larger common change in both gas
histories. The individual changes must therefore remain visible. Fractions
and xe/H are dimensionless; all temperature differences are kelvin. No shear
gate or photon temperature shift is substituted for these gas differences.

At fixed a, retain the separate proper clocks. At fixed proper time, retain
the separate scale factors/redshifts. A clock change cannot be silently
treated as a change at the same redshift.

## Exact reuse and reduction

`receipts/BASELINE_REUSE.json` binds the existing 1001-row T0 tables. The
fixed-a query is the original uniform-ln(a) grid. Fixed-t uses the exact
existing elapsed-time column, which is not a new uniform-time grid.
`inputs/SAMPLING_GRID.json` pins both. Baseline histories are not rerun or
reconstructed.

The native extractor reads terminated, durably checkpointed T1 segments in
their original order. It checks exact continuation checkpoint identity and
boundary row identity, removes only the repeated first row at a segment
boundary, and preserves all raw files. Any post-checkpoint tail is counted
and excluded explicitly. The scientific sample contains neighboring saved
native rows, not a substitute integration.

Primary interpolation reuses the unchanged owner's `interp` implementation:
linear in ln(a); for fixed time, first invert t -> ln(a), then interpolate X.
`xe_per_H` is formed at each native row before interpolation. Extrapolation is
forbidden apart from the original 8-epsilon endpoint-roundoff allowance.
PCHIP on the local neighboring rows is a T1 interpolation sensitivity only.
It does not qualify the T0 interpolation family or supply an error bound.

All represented history rows are checked for finite physical state, increasing
a/t, element-fraction domain, hydrogen/helium closure, electron charge, and
comoving hydrogen density at the original 1e-12 tolerance. Every saved ledger
batch is checked against its original photon-count, augmented-energy and odd
photon-moment tolerance, and all cumulative values are retained in raw data.
These checks constrain invariants; they do not bound evolution error.

## Decision limits

The original response floors are 1e-7 for element fractions and 0.01 K for
temperature. Charge propagation gives the electron floor
1.243904055128545e-7. Report the fraction of represented, above-floor samples
where the two-level change is smaller than 0.1 times the T1 response, while
calling that quantity a two-level change, not a certified numerical error.

Two levels supply D01. They do not supply D12, observed order, a Richardson
estimate, a continuous supremum, or the full AX11 gate. Full AX11 still
requires the originally scoped baseline plus two refinement levels, separated
dt/dE/dmu evidence and both coordinate modes. No new global theorem is added.
AX12 does not start under this wave.

Native endpoint completion, conservation diagnostics, sampled discrepancies,
interpolation sensitivity, actual cost and scientific admission are separate
fields. A resource-censored history contributes only its represented common
prefix. All previous failures and accumulated historical UNKNOWN cost remain.

Original DAG **10/17**; expansion **28/88**. This contract and its verification
receive no scientific node credit.
