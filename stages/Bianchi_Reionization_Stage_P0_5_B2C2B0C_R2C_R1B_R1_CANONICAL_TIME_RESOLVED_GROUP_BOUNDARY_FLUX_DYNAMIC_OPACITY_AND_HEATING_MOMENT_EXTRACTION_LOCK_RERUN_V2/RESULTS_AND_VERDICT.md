# R1B-R1 results and verdict

## Result

Hypothesis H1 is selected narrowly: all four missing inputs required by R1B are identified sufficiently to authorize a bounded fixed-point-history attempt.

- BDF replay: history 6.100e-13; ledger replay 3.238e-15.
- Global time grid: N=9 rejected; N=17 selected; GL256 1.131e-4; nested 1.131e-4; GL512 1.131e-4.
- Canonical photon ledger: 2.931e-10, below the hard 1e-8 gate but above the 1e-10 engineering target.
- Atomic pairs: 8 supported; all unsupported pairs exact zero; 90-digit independent maximum residual 6.989e-15.
- Dynamic cases: 85 time rows, 340 group cases, 6,120 macro/group cases, 3,916,800 logical node equivalents.
- Moment residuals: q 1.11e-16, opacity 2.53e-16, current 3.76e-16, common flux 2.21e-16.
- Node measure: no negative values and no allocation on zero support.
- State-measure versus inherited shape-prior TV: 0.21588 to 0.67221; no prior is promoted.
- Optical depth: 7.59e-10 to 1.4822. Differential versus finite-cell allocation TV: 1.68e-5 to 9.12e-3.
- Heating: eight supported pairs, bounded hardening coordinate, thermal identity 2.06e-16.

## Scope of the pass

The pass removes the *input-identifiability* blocker. It does not show that the coupled nonautonomous fixed point converges, that thermal refinement closes, or that any node history is production-ready. Absolute global opacity normalization is inherited. The material state provides its unique conditional node/macro distribution only under the four locked axioms.

## Authorization

`R2C_R1B_R2_authorized=true`. Production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB transfer and Bianchi feedback remain false or unstarted.
