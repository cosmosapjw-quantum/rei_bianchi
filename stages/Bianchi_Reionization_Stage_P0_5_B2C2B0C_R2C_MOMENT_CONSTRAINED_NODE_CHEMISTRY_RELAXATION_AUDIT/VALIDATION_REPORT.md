# R2C validation report

## Executed checks

- stage unit tests: `16 passed`
- independent output/ledger validator: `PASS`
- exact symbolic/90-digit fallback: `PASS`
- input logical-output reassembly and SHA-256: `PASS`
- 90 case keys and 1,620 macro keys unique: `PASS`
- case pass equals conjunction of 18 macro certificates: `PASS`
- 2,363 violation rows equal the expanded certificate multiset: `PASS`
- feasible-case flag equals convergence flag in all 90 cases: `PASS`
- successful substep KKT, capacity, column, current-Gamma and nuclei gates:
  `PASS`
- 450 structural-zero rows are literal exact zeros: `PASS`
- clipping-used flags: all `false`

The machine-readable independent receipt is
`receipts/independent_stage_validation.json`.

## Wolfram status

`wolfram_r2c_exact_semigroup_validation.wl` is the canonical Wolfram script.
No native Wolfram kernel was exposed in this runtime, so no native-Wolfram
success claim is made. `tests/exact_symbolic_fallback.py` independently checks
the same identities with SymPy and 90-digit Decimal arithmetic.

## Special-function status

The R2C operator uses exponentials only; no Bessel, hypergeometric, elliptic,
gamma, or zeta evaluation enters the locked equations. The high-precision
special-function plugin was unavailable and no surrogate special-function
value was introduced. Decimal exponential arithmetic supplies the relevant
high-precision fallback.
