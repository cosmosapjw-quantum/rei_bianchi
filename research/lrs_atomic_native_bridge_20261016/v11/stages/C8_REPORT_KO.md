# V11 C8: collisional and thermal microphysics clocks

## Executed reference conditions

- Native owner: PR150 frozen `6ea2b1b4b3875c9163cafc45efe720afded43fc4`; new code is independent Python port; actual native Rust V11 NOT_RUN.
- Reference: independent continuous SciPy Radau RHS with original Grackle Case-A owner rate coefficients, total-H normalization and native FLRW cosmology/EOS.
- Actual 144 rows = 3 cases × 8 clock modes × N=8,16,32,64,128,256; per-case process timed to avoid sandbox timeout. First one-pass 144-case attempt exceeded runtime; incomplete first attempt not counted; unchanged physics regenerated in three bounded runs.
- Initial state `(HII,HeII,HeIII)=(.075,.12,.03)`, `T0=15000 K`, source/photon=0, `a0=1/21`.
- Original frozen C-Grackle 96 temperatures ×17 original coefficients: maximum relative difference `2.8410045294244635e-14`.

## Quantitative C8 results (N=128)

|case|BE T error K|CE-only-mid error K|all-mid error K|CE error reduction|last p_BE|last p_CE|last p_all-mid|
|---|---:|---:|---:|---:|---:|---:|---:|
|D1_X1E4|0.021696993|0.000643681784|9.28734153e-07|97.033%|0.99977|0.99889|1.99851|
|D5_X1E5|0.005401554|0.000134405867|1.18012395e-07|97.512%|0.99988|0.99932|1.99960|
|V10_D1_X1E5|0.0002322904|6.90758679e-06|8.8584784e-10|97.026%|0.99998|0.99991|1.87250|

## Owner-matched evidence

Prior native V10 source-free N128 T = 14988.761135230299 K; Python V11 BE temperature minus native = 4.314642865211e-09 K. This is a single endpoint numeric comparison, not original Rust V11 execution.
Maximum discrete energy ledger residual across 144 rows = 4.4408920985e-15 eV/H. Conserved under each clock method by construction; it is not an order proof.

## Scientific interpretation and hold

CE HI instantaneous cooling initially dominates the source-free thermal sink and moving CE to midpoint reduces measured absolute temperature error ~97% in all three tested conditions. BE full, CE-only-mid and thermal-only-mid have observed global order close to one. Fully coupled state midpoint is second order in the nonstiff conditions; finest very-short-interval order at Xend=1e-5 approaches numerical-reference/roundoff limits.
This is strong evidence that CE endpoint evaluation is a principal source of source-free temporal error in the *matched Python port*. Native original Driver at PR150 must still be run with opt-in CE clock to assign causal native error. No photon source/opacity, GL2 age, or full EoR completion can be inferred.

Sources: `src/ci_thermal_clock.py`, `tests/test_ci_thermal_clock.py`, `run_clock_matrix.py`, `merge_study.py`, `evidence/C8_MATRIX_144.*`, `C8_SUMMARY.json` and three case-specific stdout logs.
