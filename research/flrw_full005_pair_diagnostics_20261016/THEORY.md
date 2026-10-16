# Continuous piecewise-linear FULL005 pair diagnostics

## R1 — research position and contract

The task is to compute the full-overlap maximum absolute difference and integrated L1, L2 and RMS differences of the continuous piecewise-linear reconstructions of two saved adaptive histories in the coordinate `L = ln(a)`. The diagnostic acts on the existing validated history arrays; it does not alter a saved state or the solver. Completion requires the formulas, an independent symbolic or rational check, a discriminating narrow-peak example, a bounded implementation contract and integration into the FULL_PAIR postprocessor.

The inspected reader is `research/flrw_full005_postprocess_20261015/vendor/compare_histories.py`. `load_case` supplies `array('d')` sequences under `case['series']`. `L` is the stored binary64 `math.log(a)` value. Every row has already passed finite-value, strict coordinate/time ordering, H/He fraction, inventory, abundance/history, baryon and charge checks. The comparison observables are every series key except `L` and `time_s`: `xe`, the nine `FIELDS` entries, and the six baryon-normalized species abundances. The FULL_PAIR reader enforces the same represented endpoints, from `a=1/21` to `a=1/5`, and proper time starts at zero at zbar20.

`postprocess_flrw.run` currently calls `reader.compare`, which reports 1001 regularly spaced ln(a) samples. The vendor reader also contains an optional `exact_reconstruction_summaries` path using `reconstruction_support.reconstruction_norm`, an O(n+m) Fraction-arithmetic union-knot supremum with equal endpoints. This existing result is reused as the exact reference for small fixtures. The new work adds analytic integrated diagnostics and a bounded-memory binary64 sweep to the actual FULL_PAIR caller. Union-knot extrema are prior project knowledge, not a new mathematical claim.

The claim concerns saved-history reconstructions and has no continuum-solver error or convergence threshold attached. FULL005 source identity, single energy ownership, H/He normalizations, all-row validation, actual-gas-temperature chronology, elapsed proper-time convention, saved milestone definitions and the source005 admission boundary are preserved. The native solver and source006 experiments are outside this change.

The NCP postprocessor import failure and recovered package are separate environment/execution evidence owned by the controller. Their repair or full-data reduction is not required for this light mathematical and implementation unit.

R1 completion: the representation, integration coordinate, admissible changes and completion evidence are fixed. R2 must map the prior reconstruction helper and selected primary literature; R6/R7 require actual independent and discriminating evidence before scientific adoption.

## R2 — evidence and reuse

The baseline caller SHA256 is `b396a5b439a5cc3e305ab6663ac8d6d46424b747c13a84da4fe3d89ac468b5fc`; the vendor reader is `ba5441981f4dd37607648a14c4edd3663f57c061413c28713d6e37dd2f5b72ed`; `reconstruction_support.py` is `98eb05a8a13d2c613b53fa2bc6c5bc5117eb40bbb25f717da5ffab40e9531808`. These identities were computed from actual local bytes in the baseline snapshot supplied by the controller at remote commit `4e2f0682fb605c6aa940bd756d9869e67b6ded0b`.

The existing support helper converts stored binary64 numbers to exact Fractions, merges both knot sequences and evaluates their PL difference at every union knot. Its equal-endpoint contract and endpoint-maximum argument are reused. Its `_points` conversion materializes O(n+m) rational data; using it as a small-fixture oracle avoids that cost for the large completed histories. The new float sweep retains the loaded arrays and O(k) auxiliary state for k observables. The prior `POSTPROCESS_REVIEW.json` explicitly characterizes the existing caller output as 1001 sampled ln(a) differences and crossings.

Selected literature was retrieved by the controller on 2026-10-16 using Exa and SciSpace. Primary method support is the official SciPy [`PPoly.integrate`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PPoly.integrate.html) reference and [piecewise-polynomial tutorial](https://docs.scipy.org/doc/scipy/tutorial/interpolate/splines_and_polynomials.html): a piecewise polynomial has a local power-basis representation and admits a definite integral over a stated interval. Here the difference is linear on each merged segment and its square is quadratic, so explicit integration suffices without importing SciPy. These sources support the computational representation; R5 supplies the actual formulas and proof.

SciSpace supplied two contextual leads: Agocs, Hobson and Handley, *Dense output for highly oscillatory numerical solutions*, [arXiv:2007.05013](https://arxiv.org/abs/2007.05013), and Calvo, Higham and Montijano, *Global error estimation with adaptive explicit Runge–Kutta methods*, [DOI:10.1093/imanum/16.1.47](https://doi.org/10.1093/imanum/16.1.47). The former concerns method-specific dense output, whereas this unit fixes linear reconstruction of saved states; the latter concerns global-error estimation, whereas this unit computes pair-reconstruction differences. Neither paper is used as a proof of the PL norm formulas or as evidence of FULL005 global accuracy. Their role is contextual scope alignment.

The theorem will be derived from affine interpolation and elementary integration. No unresolved literature lemma enters the derivation. Wolfram symbolic output and the independent small-fixture probe belong to R6/R7 and remain separate evidence from source retrieval.

## R3 — quantified claims and assumptions

Forward execution context supplied by the controller during R3: concurrent commit `5e0becf8709215e7ec8cc482c933663b045c47f9` preserved completed FULL005 postprocessing and its scoped independent review. The full render took 87.98996 s and the Yi extension 12.6463 s, producing nine plots; the cumulative postprocessing debit is 103.79374452296179 s. These completed outputs are reused. The earlier NumPy import failure is historical and needs no new environment repair or render replay in this unit. The three baseline code files above are unchanged. SOURCE007 work belongs to another active thread. Any future diagnostic of compressed public display tables must be labeled as a compressed-display reconstruction; this contract targets the complete validated accepted-row arrays.

Let two finite data sets `(r_i,R_i)` and `(c_j,C_j)` have at least two rows each, strictly increasing finite coordinates and finite real values. Each value defines its unique continuous piecewise-affine interpolant on its represented closed interval. In the mathematical statement, stored binary64 values are regarded as exact real numbers; implementing the formulas in binary64 adds ordinary arithmetic rounding.

Define `A=max(r_0,c_0)`, `B=min(r_last,c_last)`, and require `A<B`. The overlap interval is reported explicitly. Let `K` be the sorted unique union of both sets of knots strictly inside `(A,B)`, together with `A,B`. Equality here means equality of stored coordinate values: nearby distinct knots are retained. The FULL_PAIR caller has equal endpoints by the existing reader contract, so its overlap is the whole represented z20-to-z4 history. Partial overlap is supported by the generic helper and is labeled with both input domains and the returned overlap; extrapolation is absent.

For each observable define `d(L)=C_PL(L)-R_PL(L)`. The requested quantities, all integrated with the dimensionless measure `dL=d ln(a)`, are:

* `sup_abs = max_[A,B] |d|`, with the earliest maximizing coordinate in K and its signed difference;
* `l1_integral = integral_A^B |d| dL` and `mean_abs = l1_integral/(B-A)`;
* `l2_squared_integral = integral_A^B d^2 dL`, `l2_norm = sqrt(l2_squared_integral)`, and `rms = sqrt(l2_squared_integral/(B-A))`;
* signed differences at A and B, for continuity with existing endpoint reporting.

Fractions, `xe` and baryon abundances have unit one; `ne_cm3` has cm^-3, `Tgas_K` has K, and `U0_eV_per_H`,`U2_eV_per_H` have eV per H. L1, L2, RMS, mean absolute difference and supremum retain the observable's unit because L is dimensionless; the squared integral has its squared unit. Time-weighted norms would have a different measure and are outside this contract. Tgas itself need not be monotone: it is an observable reconstructed in L and is never used to reorder saved states.

The proof target is: for every pair satisfying these assumptions, the union-knot formulas in R5 calculate these reconstruction functionals in exact arithmetic, with O(n+m) knot visits per fixed observable set. The binary64 implementation will report analytic reconstruction diagnostics and explicitly identify its arithmetic, rather than claiming exact dyadic values. Input validation, physical invariants and full-source identity remain responsibilities of the existing caller/reader, while the generic helper also rejects malformed numeric arrays.
