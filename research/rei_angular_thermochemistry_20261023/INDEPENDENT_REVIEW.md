# Independent math-to-code and result review — ANGTHERM01

Date: 2026-10-23. Reviewer: Astra lane `/root/rei_latest_survey`.
The reviewer did not author the theory, implementation or execution code.
Protocol: intrinsic physmath-research-loop 1.0.0, approved v0.2.

## Verdict

**PASS for the stated finite, conditional trace-system result.** The code
implements the reviewed equations, the independent unfolded M4 event oracle
agrees with the reduced optical-depth model within every frozen comparison
limit, and all ten completed configurations pass the applicable trajectory
gates. The ten configurations comprise the original nine and the
controller-authorized matched mean-redshift case in `MATCHED_MEAN_CONTROL.md`.
No further IVP, physics repair, timing repetition or parameter sweep is
requested by this review.

This admission covers the source-preserving C22A event/thermal closure on
the two prescribed saved backgrounds, the exact eligible isotope/angular
quotient, and the observed finite numerical results. It does not establish
an angular-continuum error bound, empirical capture-heat accuracy,
self-consistent Einstein feedback or a cosmological reionization prediction.
Observed timing differences are not admitted as a fixed-tolerance,
equal-error or universal speedup.

The earlier independent derivation remains in `MATH_REVIEW.md`. Its two
frozen input hashes are unchanged. The explicit constant addendum and the
matched mean-redshift addendum were also read. This review inspected
`code/angular_model.py`, `code/run_cases.py`, `code/bounded_run.py`,
`code/algebra_checks.py`, `code/analyze_results.py`, the active atomic and
capture-energy source files, the finite pre-IVP report, preserved failures,
all ten final raw NPZs and their metadata, and the actual six corrected PNGs.
Read-only array comparisons and source hashes were independently evaluated;
no scientific solver was invoked by the reviewer.

## 1. Mathematical equations are implemented consistently

### Geometry, measure and work

`geometry()` evaluates the exact fixed-covariant-momentum map with
`expm1/log1p`. Packet counts retain their integrated initial momentum-space
weights. No additional current-angle Jacobian is applied.

`Background.fields()` returns the derivative of the same Hermite `b`
interpolant used for the directional map. The RHS, Jacobian and reported
`bprime` therefore implement the effective proper shear `s_eff=H*bprime`.
There is no separately interpolated shear substituted in a work term.
`Wshear'=2*bprime*sum(E*g*P2)` retains the signed moment. The Frobenius and
tensor-contraction checks use the full `sqrt(6)` convention and independently
assembled photon vectors. Mean and shear work are separate evolved ledgers.

The continuous Hermite-interval extrema check bounds the redshift factor
away from zero for every direction and both shear signs: the grid044 lower
bound is `0.5101020514433645`. Grid022 retains its nonzero saved anisotropy.
Threshold roots use the exact adopted geometry. Only cross-section sampling
is displaced to the correct one-sided interval at an endpoint; energy,
direction and work remain evaluated at the actual eta.

### Events, thermal state and analytic Jacobian

The reduced population equations use the exact element totals, the six
adjacent electronic channels and cross sections converted from Mb to cm².
Every absorption and recombination event supplies the population, photon,
thermal, escape and count rows consistently. The code evolves thermal
energy, reconstructs `T=U/[1.5*k_B*(N_nuc+v)]`, and includes both electron
response and temperature response in the recombination Jacobian. The
particle-count contribution to temperature is consequently present once.
The derivative of the capture-energy factor is analytic and has the correct
sign and factor of `1/(4*T)`.

The optical-coordinate coefficient is formed directly as
`exp(log(c*n/H)+logsigma+logg0-tau)`. Populations are multiplied afterwards,
allowing signed solver trial populations without clipping. Crucially, the
photo Jacobian's optical-depth columns use `-photo`, and the population
columns use the directly scaled coefficient. They do not reconstruct an
underflowed raw photon count first. Structural zero photons use `-inf`
initial log count and produce exact zero absorption without `log(0)`.

The full oracle independently loops over every original isotope edge and
every direct photon packet. It does not call the reduced event RHS or obtain
its derivatives by lifting reduced output. It uses a numerical Jacobian,
21 scaled populations and 192 direct packets at M4. Immutable fit data,
constitutive thermal functions and geometry are shared, as disclosed.
This is an implementation oracle, not an independent empirical atomic model.

### Exact quotient and source-domain check

The code rejects mismatched isotope initial fractions, retains all nine
electronic fractions, and lifts zero neutron/tritium stocks as exact zero.
The unfolded directions have the specified reflected signs and four
azimuths. The independent tensor check and three interior RHS comparisons
test the finite angular/isotope lift. The odd-angular control remains
unfolded and exposes the flux discarded by a symmetric reconstruction.

The prior HeI-domain question is **resolved**. The provider parses
`rrfit.f`'s `RNEW(2,2)` coefficients
`[9.356e-10, 0.7892, 4.266e-2, 4.677e6]`, which match **HeI b**, not HeI a.
The vendored `rr_description.txt` documents the b row over
`3<T<1e10 K`. Thus the adopted `3..1e9 K` computational restriction does
not silently select the narrower a row. All recorded accepted and reporting
temperatures are strictly inside either interval. This resolves provenance,
not the separate conditional accuracy of a heat moment inferred from a fit.

All 34 manifest-listed copied objects independently matched their SHA256
identities. The active provider's own immutable source checks are consistent
with that audit. The new code imports the fit provider, not the old donor's
prescribed-temperature or beta-event RHS.

## 2. Focused algebra evidence and raw trajectory admission

The existing `checks_pre_ivp.json` was inspected with its generating code;
it was not rerun. Its ten finite checks all passed. Relevant discriminants
are:

| Check | Observed maximum or result |
| --- | ---: |
| Full/reduced RHS disagreement, three interior states | `6.62797e-15` in the documented scaled norm |
| Centered-FD Jacobian component residual | `1.38614e-5`, below `2e-5` |
| Jacobian infinity-norm relative residual | `2.98415e-11` |
| Local differential conservation cancellation | `3.18542e-15` |
| Omitted-shear-work residual | `2.03050e-8` to `9.02168e-6`, resolved above cancellation |
| Full/folded pressure tensor absolute disagreement | `1.77636e-15` |
| Actual directly scaled coefficient after raw-count underflow | 79 positive coefficients; maximum `1.705273e-318` |
| Unequal isotope / odd angular controls | Rejected / explicitly kept unfolded |

All final NPZs contain 201 common reporting times from zero to `ln(7)`,
accepted-node arrays and support boundaries. The reviewer recomputed the
comparison maxima from the arrays and also checked the accepted-state
temperature and population ranges. The original first three case JSONs
reported sample-only temperature ranges; the accepted-node maxima are
larger, as now separately recorded by the analysis. No acceptance failure
is hidden by that distinction.

Across the ten configurations, the recorded/recomputed extrema are:

| Quantity | Observed bound | Frozen limit or interpretation |
| --- | ---: | --- |
| Normalized energy-ledger residual | `2.539543e-11` | `2e-8` |
| Normalized charge residual | `4.697264e-15` | `2e-9` |
| Normalized photon-number residual | `3.176159e-11` | `2e-9` |
| Relative nonzero isotope-block residual | `2.846031e-15` | `2e-9` |
| Smallest primary fraction at accepted/reporting nodes | `-1.306005e-22` | At least `-1e-10`; no clipping |
| Temperature, accepted and reporting nodes | `6.122457710..13803.039705 K` | Inside the adopted fit domain |
| Primary lifted n/T stocks | Exactly zero | Structural invariant face |
| Full-oracle zero-face scaled magnitude | `1.789984e-30` | Authorized summary bound `64 eps=1.421085e-14` |
| Full-oracle minimum reporting photon count | `-2.159477e-21` | Recorded raw direct-count roundoff; no positivity theorem asserted |

Energy, charge and photon normalization use fixed initial physical scales;
element totals normalize nonzero isotope blocks individually. These are not
residuals divided by an arbitrarily inflated denominator. The zero-UV case
has exactly zero photon count, absorption and radiation work. The opposite
shear sign reverses the sign of Q while both signed shear-work integrals
can remain negative, as the product `bprime*Q` requires. Neither a sum of
absolute moments nor a sign-forced work term has been introduced.

### Independent M4 agreement

| Observable / metric | Nominal versus full oracle | Nominal versus tight | Gate |
| --- | ---: | ---: | ---: |
| Scaled population / fraction maximum absolute error | `8.16732e-11` | `8.00320e-11` | `2e-7` |
| Temperature maximum relative error | `1.86960e-9` | `1.73715e-9` | `2e-6` |
| Electron/Href maximum absolute error | `4.56376e-11` | `4.90520e-11` | `2e-7` |
| Photon/Href maximum absolute error | `3.88578e-16` | `0` at stored samples | `2e-8` |
| UV-energy maximum absolute error, eV/Href | `1.77636e-14` | `0` at stored samples | `2e-6` |
| Q maximum absolute error, eV/Href | `3.31469e-16` | `0` at stored samples | `2e-6` |
| Largest energy-ledger component difference, eV/Href | `6.84165e-10` | `7.42822e-10` | `2e-6` |
| Thomson-depth maximum absolute error | `8.68219e-12` | `8.43664e-12` | `2e-7` |

The explicit full-oracle isotope fraction disagreement is at most
`1.66533e-16`; its eight copies within each packet group differ by at most
`2.69809e-24` at the reporting times. These support the finite quotient.
The comparison numbers measure implementation agreement at the saved
times, not absolute error against an exact continuum solution.

## 3. Matched mean-redshift control and the resolved trace-Li signal

Case10 uses `Reduced(M=4,tight=True,sign=0)` on **the same grid044 H and n**
as case3. Their stored H, n and reporting-time arrays are bit-identical.
`bprime` and `Wshear` are exactly zero in case10; its maximum `|Q|` is
`5.71032e-16 eV/Href`, consistent with finite arithmetic in isotropic
quadrature. Its energy residual is `2.14151e-13`. No event law, atomic
coefficient, density or solver tolerance changed.

This addresses the H-history confounding in grid044 versus grid022. The
matched directional/mean contrast is a comparison of two physical trace
closures, not a reference error that should satisfy the oracle-agreement
limits. Both use the frozen tight settings.

Bulk temperature and electron changes are very small in this constructed
inventory: maximum `|Delta T|=8.43584e-8 K`, maximum relative temperature
difference `4.98147e-11`, and maximum electron/Href difference
`2.41136e-11`. No resolved bulk thermal angular-convergence order is inferred
from such small differences. Radiation geometry is clearly distinguished:
maximum `|Delta Q|=0.04030697 eV/Href`, final directional
`Wshear=-0.00915341273 eV/Href`, and final mean-work difference
`0.00652399419 eV/Href`.

There is also a substantial **trace-species fraction** effect that a
bulk-electron plot alone conceals. The maximum LiI/LiII fraction difference
is `0.04899986856` at `eta=0.7297163059`. At that sample,
LiI is `0.00156001484` in the directional system and `0.05055988340` in
the matched mean-redshift system. Final LiI fractions are `0.3256059802`
and `0.3587027785`, respectively. H fractions differ by at most
`6.27985e-12`, and He fractions by at most `4.58916e-13`.

The source-threshold mechanism is directly visible in saved crossing
metadata. The 10 eV cohort crosses the 5.392 eV LiI threshold at directional
etas `0.488914070`, `0.604430735`, `0.698847600`, and `0.726724388`, versus
the common mean-redshift eta `0.617668719`. Surviving transverse cohorts
therefore retain ionizing support later. Because the total Li stock is only
`5.0001e-10/Href`, a roughly 0.049 fraction change contributes only about
`2.45e-11/Href` to the electron count. This explains how the trace-ionization
effect can be visible while the bulk quantities nearly coincide.

This interpretation remains conditional on the finite source inventory,
the adopted ground-state Li rates and the prescribed geometry. It is not
an observational lithium prediction.

## 4. Angular refinement has observable-dependent limits

All three directional refinement runs use the same tight integration
settings. Independent differences from existing arrays are:

| Observable | M4 to M8 maximum absolute difference | M8 to M16 maximum absolute difference |
| --- | ---: | ---: |
| T, K | `3.41720e-8` | `3.77161e-8` |
| Electron/Href | `1.32588e-12` | `1.08458e-12` |
| UV energy, eV/Href | `5.31729e-7` | `4.61720e-11` |
| Q, eV/Href | `9.02967e-6` | `1.48928e-9` |
| Shear work, eV/Href | `1.06587e-6` | `8.37544e-11` |
| Thomson depth | `2.23797e-13` | `1.95250e-13` |
| Li fractions | `9.97743e-5` | `4.64160e-5` |

The radiation energy/stress/work differences decrease strongly over these
three finite quadratures. The small T/electron/depth differences do not
establish a resolved angular order. Reported log2 ratios are descriptive
successive-difference ratios, not demonstrated asymptotic orders.

Li fractions converge more slowly around directional threshold crossings.
The `4.64160e-5` M8-to-M16 Li difference must remain separate from the
`2e-7` M4 full/reduced implementation gate; it does not satisfy that gate as
an angular-continuum error assertion. The M16 directional Li contrast with
the matched mean model is still `0.04912182803`, so the observed finite
trace-Li effect persists, with an explicit angular-resolution qualification.
No additional refinement is required for admission of the stated finite
system, and no continuum error certificate is claimed.

## 5. Reporting repairs preserved the scientific evidence

**Empty reporting mask.** The first invocation solved a short support
interval containing no common reporting sample, then failed while asking
the dense-output object to evaluate an empty array. The repair skips that
empty output evaluation. The resumed result preserves, bit for bit, all
363 accepted states and all 39 populated reporting columns in the saved
checkpoint at `eta=0.3720455828589731`.

The failed invocation's metadata counted 365 attempted accepted nodes,
whereas the persisted checkpoint contains 363. Two terminal unpersisted
nodes were consequently recomputed during the authorized continuation.
The precise statement is **no persisted interval was replayed**; the
failed-attempt cost is retained. This distinction does not invalidate the
resumed numerical result. The zero-IVP empty/nonempty-mask regression and
original failure artifacts remain available.

**Full-oracle exact-zero summary assertion.** The full oracle completed
all 1073 accepted nodes before an exact postprocessing equality rejected
an approximately `1.79e-30` scaled neutron excursion. Its neutron RHS is
identically zero, the initial n/T face is zero, and the preflight invariance
check confirms zero n/T derivatives on that face. Tritium remained exactly
zero. The controller-authorized numerical summary bound is `64 eps`;
the primary lift still enforces exact structural zeros.

The oracle's final accepted-time array, accepted-state array and all 201
reporting states are bit-identical to the preserved pre-repair arrays.
No state was clipped, projected or overwritten to pass the bound, and no
oracle IVP was replayed. The subsequent NumPy-boolean JSON serialization
failure was fixed by scalar conversion only. Its failed process and cost
also remain recorded. These are scoped reporting repairs, not changes to
the physical equations or a relaxed trajectory-accuracy target.

## 6. Costs, resource bounds and plot inspection

| Configuration | State size | Accepted nodes | rtol | Observed case wall time, s |
| --- | ---: | ---: | ---: | ---: |
| grid044 M4 nominal | 41 | 639 | `2e-9` | 6.7305 |
| grid022 M4 nominal | 41 | 476 | `2e-9` | 3.8011 |
| grid044 M4 tight | 41 | 1782 | `2e-11` | 12.6096 |
| grid044 M4 full direct oracle | 221 | 1073 | `2e-10` | 46.4569 |
| grid044 reversed b, M4 nominal | 41 | 642 | `2e-9` | 6.7851 |
| grid044 zero UV, M4 nominal | 41 | 209 | `2e-9` | 3.9219 |
| grid044 ionized IC, M4 nominal | 41 | 1097 | `2e-9` | 19.6315 |
| grid044 M8 tight | 65 | 2030 | `2e-11` | 18.2590 |
| grid044 M16 tight | 113 | 2410 | `2e-11` | 26.5662 |
| grid044 M4 matched mean, tight | 41 | 1422 | `2e-11` | 5.8902 |

Case timers include case-level setup/raw saves and are not whole-pipeline
timers. The nominal resumed case includes its failed-attempt case time.
Whole-child and plotting records are separately retained in
`results/execution_budget.json`. At the reviewed budget snapshot, cumulative
charged CPU/wall were `217.943352/230.352828 s`, including conservative
preflight and recorded postprocessing charges, below `300/420 s`.
Later documentation-only processing has no scientific IVP implication;
the final ledger remains the authority for any later recorded charge.

M4 nominal versus full direct uses rtol `2e-9` versus `2e-10`, different
component atols, and different native coordinates/error norms. Even a
common rtol would not make optical-depth and direct-count error weights
identical. Reported solver counters are observations: nominal M4 has
`nfev/njev/nlu=4968/132/578`, while the full oracle has
`8145/152/628`. These are solver-reported counters, not a claim that every
numerical-Jacobian evaluation has identical cost. The valid performance
statement is smaller state dimension and these observed costs alongside
the physical-observable agreement above. No matched repeated timing pair
or equal-error optimization frontier was measured.

All six actual figures were opened and inspected. The initial conservation
and agreement panels had compressed axes caused by long tick labels and
legends. Their saved-data-only layout correction now gives readable axes,
compact scientific scales, visible zero handling and external legends.
The corrected evolution, signed-stress/work, conservation, agreement,
angular-refinement and size/cost figures identify the conditional
prescribed-background scope and normalization. The cost figure explicitly
states the differing tolerances and native error norms. The tiny M8-to-M16
radiation differences are below the visual scale of some linear panels;
their raw maxima are retained in the numerical tables.

## 7. Review identity and closure

Core reviewed code identities:

| File | SHA256 |
| --- | --- |
| `code/angular_model.py` | `8fcbf90b821706fa01b84fa43bb80fd89f7fca71a2b3115ab69ffbb99d2fa1bb` |
| `code/run_cases.py` | `6c0b3b333d57ee06f28fd08cada43ef6970f9efd2ebea88299dffa40a7e98fdc` |
| `code/bounded_run.py` | `ad6338e0d9e027b65de4901d4cad17e32d2b3288d22da9e6a993bf01fbd8c945` |
| `code/algebra_checks.py` | `3865c71b73bf2b89a0bc194e09faa9de99b386337ab55c39beee03581bc9bfab` |
| `checks_pre_ivp.json` | `14eaca6f16df689a1ad8b2b3768a9cb5f4a0ebbe6ac8350c472f1ba4e9b2aa39` |
| `MATCHED_MEAN_CONTROL.md` | `b8f4355dbd8cea7cce2633fa75cd1e93255a077a1b3d24d087b3e44362780cc8` |

The decisive raw comparison identities are:

| NPZ under `results/` | SHA256 |
| --- | --- |
| `grid044_M4_nominal.npz` | `ac035e9bdc6427dd66cbc3a39db92769ffc23f2ae8de7a2c1200b83fb9f20619` |
| `grid044_M4_oracle.npz` | `775372cece8b694e1ca0c3ac6c59b11c99d01accc5ebb2c6e5ecb7ab37c2add1` |
| `grid044_M4_tight.npz` | `6a1adec0bda0285ccaf55ee5f2e39a1e7fcedd981fe607a6a85783e53406910c` |
| `grid044_M8_tight.npz` | `d9669ace7d0a9f71cf4faf918502ca1b698788e9f6f7df4a7d6832894a550c52` |
| `grid044_M16_tight.npz` | `87196e8ff76689820c827e0f277ac00fc435df74e53c8c29c05e4d7fbd0399e8` |
| `grid044_M4_mean_tight.npz` | `fe89cfbec148fb8ae13684bdcdee6a6fbfe38ea86f5448349eeaff6048d36d2a` |

There are no unresolved blocking mathematical or implementation findings
for this finite unit. The source-domain question, numerical-zero reporting
guard, saved-state continuation and plot readability issues are closed.
The remaining restrictions are scientific claim boundaries stated above,
especially trace-Li angular accuracy, conditional VF heat, prescribed
background feedback and unequal-error-norm timing comparisons. Publication
and checkpoint decisions belong to the controller.
