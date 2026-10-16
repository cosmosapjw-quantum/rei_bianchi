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

SciSpace supplied two contextual leads: Agocs, Hobson, Handley and Lasenby, *Dense output for highly oscillatory numerical solutions*, [arXiv:2007.05013](https://arxiv.org/abs/2007.05013), and Calvo, Higham and Montijano, *Global error estimation with adaptive explicit Runge–Kutta methods*, [DOI:10.1093/imanum/16.1.47](https://doi.org/10.1093/imanum/16.1.47). The controller fetched the arXiv primary abstract and corrected the omitted fourth author in the discovery result. The OUP primary-page retrieval timed out, so the Calvo paper remains a discovery-only lead and contributes no premise. The former concerns method-specific dense output, whereas this unit fixes linear reconstruction of saved states; the latter title identifies a distinct global-error-estimation problem. Neither paper is used as a proof of the PL norm formulas or as evidence of FULL005 global accuracy.

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

## R4 — candidate representations and discriminating example

Three representations were compared against the same saved-PL target:

| Candidate | Information and cost | Decision |
|---|---|---|
| Existing 1001 uniform ln(a) evaluations | Historical sampled maximum and milestone reporting; repeated binary searches; a fixed grid can miss an adaptive-knot peak | Preserve for continuity; add full-overlap diagnostic |
| Existing exact Fraction union supremum | Exact result for stored dyadic inputs and equal endpoints; rational conversion stores both histories; no integrated norms | Reuse as small-fixture independent oracle |
| Streaming merged knots with analytic integrals | Visits every affine segment once; evaluates endpoints for the supremum and two segment integrals; binary64 implementation with O(k) auxiliary state | Select for FULL_PAIR extension |

The discriminating synthetic example is a zero reference on `[0,1]` and a triangular candidate with knots `(0,0)`, `(2001/4000,0)`, `(1001/2000,1)`, `(2003/4000,0)`, `(1,0)`. Its positive support `(0.50025,0.50075)` lies strictly between consecutive samples `500/1000` and `501/1000`. Thus all 1001 uniform samples are zero, while the PL maximum is one. The triangle base is `1/2000`; its exact L1 integral is `1/4000` and squared integral is `1/6000`. R5 derives those values from the general formulas; R7 executes the example independently.

An affine change from `[0,1]` to the physical ln(a) interval places the same example between adjacent regular ln(a) samples, preserves its maximum and multiplies each integral by the interval length. It is therefore a representation-level explanation of the information missing from fixed sampling. It is not an observed FULL005 discrepancy. The selected diagnostic resolves the full saved-PL question without choosing a finer arbitrary sample count.

Watchdog finding closed: an additional abstract function-space formalism would add no implementation obligation here. The useful structure is precisely the union partition, affine endpoint values and elementary integrals; each maps directly to a loop accumulator.

## R5 — constructive derivation and algorithm

Write consecutive union knots as `u<v`, with `h=v-u`, and let `p=d(u)`, `q=d(v)`. No reference or candidate knot lies inside this interval, so both interpolants, and hence their difference, are affine there. With `t=(L-u)/h`,

`d(L)=(1-t)p+tq`, `0<=t<=1`.

The triangle inequality gives `|d(L)| <= (1-t)|p|+t|q| <= max(|p|,|q|)`. Endpoints belong to the closed interval, so the maximum is exactly the larger endpoint magnitude. Applying this to every segment proves that the global supremum is attained at a union knot. Visiting knots in increasing order and replacing the witness only on a strictly larger magnitude returns the earliest maximizing knot, including a flat maximum.

Integrating the square directly gives

`I2(u,v)=h integral_0^1 [p+(q-p)t]^2 dt = h (p^2+p q+q^2)/3`.

An equivalent nonnegative form is `h [p^2+q^2+(p+q)^2]/6`. For the absolute integral there are two cases. If p and q have the same sign or either is zero, the affine function retains that sign and

`I1(u,v)=h (|p|+|q|)/2`.

If signs are opposite, put `a=|p|`, `b=|q|`. The unique zero divides the interval in the length ratio a:b, at `t0=a/(a+b)`. The two triangular areas give

`I1(u,v)=h [a*t0+b*(1-t0)]/2 = h (a^2+b^2)/(2(a+b))`.

Both expressions agree at p=0 or q=0; the identically-zero segment uses the same-sign formula and never divides by zero. Summing I1 and I2 over the union partition proves the R3 definitions. The triangle example has two nonzero segments of width 1/4000 with endpoint pairs (0,1),(1,0), giving total I1=1/4000 and I2=1/6000.

Useful exact consistency relations follow immediately: all metrics are nonnegative; `mean_abs <= rms <= sup_abs`; `I2_total <= sup_abs*I1_total`; swapping the two histories preserves all norms and reverses signed values. Inserting redundant knots on either affine reconstruction leaves every integral and the supremum unchanged. These are implementation checks, not new physical acceptance criteria.

The algorithm first validates each coordinate array and selected observable arrays. Set A,B as above; initialize one bracket pointer per history at A. Evaluate both histories at A, recording initial differences and maxima. At each iteration choose the minimum of B and the next unconsumed knot of each history. Evaluate all k observables there by convex interpolation in the current brackets; update maxima and analytic integrals from the previous endpoint. Advance each pointer whose next knot equals the chosen endpoint; coincident knots advance both. Stop at B, recording final differences. A pointer advances at most its input length, and each merged segment is processed once: O(k(n+m)) work. The sweep stores two bracket indices, coordinates, prior differences and per-observable accumulators/witnesses: O(k) auxiliary storage. No sorted union array, Fraction copy or list of all segment contributions is needed.

For floating-point implementation use exact coordinate equality for merges, exact source values at their own knots, and convex interpolation weights in [0,1]. Avoid an unconditional `q-p` interpolation when the endpoint values are large. Determine opposite signs by comparisons, not by multiplying p*q. Integrals may use scaled endpoint values and streaming compensated summation; the implementation must reject nonfinite arithmetic or results rather than write NaN/Infinity. Squared norms can overflow the representable range even when input values are finite; a typed diagnostic failure is acceptable for that explicit arithmetic domain. These representability checks add no data clipping or tolerance to the physical invariants. Production outputs identify binary64 arithmetic and do not contain an invented arithmetic error bound.

R5 establishes the exact-arithmetic theorem and bounded-memory algorithm. Independent symbolic checks and actual fixture outcomes are still recorded in R6/R7 before adoption.
