Publication note: quoted hashes identify archived original bytes; current publication hashes are listed in ../PROVENANCE.json.

# Collisionless FLRW transport: small method comparison

## Conclusion and claim ceiling

A conservative PDE formulation is promising, but ordinary FV or P1 DG does not automatically provide simultaneous photon-number conservation, physical-energy compatibility and positivity. In this diagnostic, unlimited DG preserves both ledgers but becomes unphysical; a standard positivity limiter removes negative density while changing energy. The comoving partial-cell method preserves both ledgers and positivity **for its own declared P0 reconstruction**, whose projection error remains material. This is not a production migration or evidence about H/He chemistry, Bianchi angular transport, or long background histories.

The figure `transport_diagnostics.svg` compares two necessary properties. Read it together with the continuum-accuracy table below: closing a ledger against a method's own initial energy is not a measure of total accuracy against the common analytic pulse.

## Frozen experiment

- Collisionless equation: g_s − g_x = 0, s = ln(a/a0), x = ln(E/13.6 eV), E in [13.6,100] eV, no upper inflow.
- Positive C-infinity pulse supported on x in [0.4,0.9], true N0=1 and U0=26.1803012067007138 eV.
- Same GL8 initial samples per log-spaced panel for all methods. None was renormalized or fed the analytic density during evolution.
- Spatial series n=32,64,128,256 at PDE CFL coefficient 0.075. Independent n=128 time series 0.15,0.075,0.0375. Stock and partial panels have exact characteristic time evolution.
- Exactly nine saved epochs: 0,0.2,0.4,0.5,0.6,0.7,0.8,0.9,1.0. There are 26 cases and 234 rows. No extra solution history was added for the figure or analysis.
- Nout is photon number that crossed the lower face. Eout counts energy **at crossing**. W is independently integrated redshift work. No work or export ledger was defined by subtraction to force closure.

## Continuum accuracy and conservation must be read together

At n=256, with coefficient 0.075 for PDE methods, maxima are over the nine saved epochs. Energy quantities are normalized by the appropriate initial energy as specified in the column. Initial projection error uses the common analytic U0; ledger error uses the method's own pre-limiter U0.

| Method | Initial U error / true U0 | Max Nout error / true N0 | Max 32-bin mass L1 | Max own-U0 ledger defect | Max negative mass |
|---|---:|---:|---:|---:|---:|
| Whole-node stock | 4.1e-16 | 4.50e-4 | 9.51e-4 | 1.90e-15 | 0 |
| Comoving partial P0 | 5.06e-6 | 1.51e-4 | 7.65e-4 | 2.71e-16 | 0 |
| Physical-E P0 FV | 1.01e-5 | 6.08e-2 | 1.20e-1 | 5.79e-3 | 0 |
| Unlimited P1 DG | -1.4e-16 | 1.02e-4 | 4.24e-4 | 5.43e-16 | 2.62e-4 |
| Mean-limited P1 DG | -1.4e-16 before; 4.76e-9 after limiter | 1.11e-5 | 4.72e-4 | 3.95e-6 | 0 |

The partial-cell initial energy bias, 5.06e-6, is comparable to the limited-DG ledger drift, 3.95e-6. Partial cells therefore are **not** established as globally more accurate just because their own-state ledger closes. Limited DG has the smallest sampled outflow error here, while failing exact physical-energy compatibility. Also, the comparison is at equal panel/cell count, not equal degrees of freedom: stock has 8n atomic weights, P0 has n means, and P1 has 2n coefficients.

The number ledger closes for every method (maximum normalized defect 8.89e-16). Stock, partial and unlimited-DG compatible energy defects are at most 1.90e-15. These are algebraic compatibility results, not continuum-accuracy certificates.

## Failures retained

1. **Physical-E P0 FV:** It stays nonnegative but has large spectral diffusion and an energy defect. With interior support its semi-discrete moment follows Udot = −exp(−Delta x) U, rather than −U. Actual face terms were used after threshold contact; the interior formula was not extrapolated across the boundary.
2. **Unlimited P1 DG:** It has substantial undershoot. At n=256,s=0.4, Nout=−1.46726e-5. At s=0.9, N=−1.02045e-4 and U=−1.39414e-3 eV. Excellent ledger closure coexists with signed, unphysical remaining stock and export.
3. **Limited P1 DG:** Endpoint limiting preserves number but changes physical energy. The final n=256 initial limiter change is +1.24693e-7 eV, and subsequent SSP-weighted changes total +1.033257e-4 eV. Initial and stage changes are separately saved. Their agreement with the actual physical-energy defect is within 1.55e-15 normalized. The ledger was never repaired.
4. **Whole-node stock:** Its state is an atomic measure. Continuous-density L1 and density minimum are not applicable; minimum atomic weight is recorded instead. Discontinuous whole-stock exits remain a representation effect even under exact time evolution.

The initially empty-cell unit test explains the DG conflict: upper-face inflow has U/N approaching Eright, outside the nonnegative-linear-density cone [Eleft+DeltaE/3, Eleft+2DeltaE/3]. Smaller time steps cannot remove this representational obstruction.

## Projection versus numerical transport

`PROJECTION_TRANSPORT_SPLIT.json` analytically transports each method's **own fixed initial representation**, solely as a reference, at the same saved epochs. It does not change an evolving numerical state. The signed error identity is checked at every epoch: total outflow error = initial-representation contribution + numerical-transport contribution. Separate maxima need not add. Here numerical transport includes spatial discretization, time stepping and subsequent limiter effects; it is not a pure spatial-error measurement.

At n=256:

| Method | Max initial-representation contribution | Max numerical-transport contribution |
|---|---:|---:|
| Whole-node stock | 4.50e-4 | 2.78e-16 |
| Partial P0 | 1.51e-4 | 3.33e-16 |
| Physical-E P0 FV | 1.65e-4 | 6.06e-2 |
| Unlimited P1 DG | 1.00e-6 | 1.02e-4 |
| Limited P1 DG | 1.00e-6 | 1.15e-5 |

Thus the characteristic methods evolve their respective representations essentially exactly. This does not eliminate their initial continuum approximation errors.

## Refinement and shape limitations

Sampled maximum Nout errors for n=32,64,128,256:

- Stock: 1.31e-2, 7.09e-3, 1.95e-3, 4.50e-4
- Partial P0: 5.25e-3, 2.32e-3, 6.01e-4, 1.51e-4
- FV P0: 2.42e-1, 1.65e-1, 1.03e-1, 6.08e-2
- Unlimited DG: 9.96e-3, 2.50e-3, 7.45e-4, 1.02e-4
- Limited DG: 1.39e-2, 1.13e-3, 1.22e-4, 1.11e-5

At fixed n=128, successive time-refinement differences in Nout have ratios 3.92 (FV), 4.06 (unlimited DG) and 4.06 (limited DG), consistent with second-order temporal behavior in this small test. Error against the continuum need not decrease monotonically with smaller dt because spatial and temporal errors can cancel. Limited-DG energy drift increases from 2.31e-5 to 3.47e-5 as its coefficient falls from 0.15 to 0.0375; it is not merely a time-resolution defect.

Continuous L1 is reported as a **quadrature estimate**, not a certified norm. GL8/GL16 differ by around 0.8% for partial/FV and by up to 1.65% for DG at some epochs because the absolute-value integrand has cusps. The n=256 maximum GL16 estimates are 1.30e-2 (partial), 1.25e-1 (FV), 1.15e-3 (DG), and 6.35e-4 (limited DG). The 32-bin mass L1 is exact for the declared numerical reconstruction, but is coarse-grained and can hide within-bin differences. Stock has no continuous-density L1. No ranking ignores these distinctions.

## Verification, resources and provenance

Nine tests pass. Seven original behavioral tests were observed failing against explicit missing-behavior stubs before implementation; two later characterization tests broadened signed-slope/independent-flux and exact stock-crossing coverage. Initial syntax/linker failures are retained. A single-threaded linker resolved the captured thread-allocation failure under the process memory cap.

An independent reviewer checked the formulas, all 234 rows, stage limiter accounting, source hashes and final replay. An independent standard-library adaptive-Simpson oracle agrees with scalar high-precision outputs to 5.48e-13 absolute. The mpmath 60/80-digit selected-value check agrees to below 1e-50. Supplemental projection-split review is recorded separately.

**Historical resource failure is explicit:** original cross-interval mpmath caches were not initially counted. An instrumented replay reached 4,369 live distinct abscissae, above the 4,096 cap, and stopped. One bounded fix clears caches between integrals. The complete replay peaks at 2,157 sites and produces byte-identical oracle JSON (SHA-256 3bd8fe9a168a7f16f26a224677cdfdcec80d3e61300f0a01fa7ffaeb2018bbe9). This recovers a bounded reference but does not retroactively make the original execution resource-compliant. Both receipts are retained.

The Rust implementation's conservative peak is 2,064 live sites. Actual scalar arrays are separately itemized in `RESOURCE_ACCOUNTING.md`; initialization briefly holds 6,912 doubles. No initial quadrature node in this frozen matrix read as zero strictly inside the pulse support, so recorded omission bounds are zero; the code still counts such omissions and bounds them conservatively without a density floor. This is not an evolving-tail certification.

All numerical executions, including compiles, failed audits and figure generation, are recorded in `BUDGET.json`; final totals are in `RECEIPT.json`. The 120 CPU-second, 180 numerical-wall-second, 512 MiB per-process and 32 MiB output limits were otherwise respected. One numerical process ran at a time. Tiny native timings include diagnostics/output and do not establish production speed.

The checked mathematical design source is `../pde-method-comparison/Bianchi_REI_conservative_transport_design.md`, SHA-256 8b422ccdc9b125eb2132d90926765240d111321e218763b4081d6721db5c463f. Relevant primary literature and the Bianchi scope are cited there. This work neither changes nor validates production source/chemistry/baseline files.
