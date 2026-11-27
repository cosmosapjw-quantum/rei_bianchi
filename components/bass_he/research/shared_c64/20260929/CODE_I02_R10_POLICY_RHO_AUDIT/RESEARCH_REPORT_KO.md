# BASS_HE R10 policy synthesis after ARSENY author-code audit

## 0. Decision summary

R9 changed the normalization problem qualitatively. The distributed ARSENY Version 1
source inserts

\[
P=\exp[-2\Delta/v]
\]

directly into the hidden-crossing matrix updates on both traversals. This agrees with
CPC Eq.(55) and the advanced-adiabatic literature, and conflicts with the printed
factor-one Eq.(52) matrix probability.

At the same time, the distributed source builds a grid of impact-parameter-dependent
\(\Delta(\rho)\) values but SECTION exponentiates only `CMES(1)` for every impact
parameter. This is a second, logically independent source/code discrepancy.

R10 therefore separates normalization selection from author implementation reproduction.

## 1. Updated epistemic status

### Established from source / author code

- CPC Eq.(52): factor-one elementary transition probability in Eq.(51).
- CPC Eq.(55): factor-two Q-series single-pass probability.
- CPC Eq.(56): Stückelberg action is impact-parameter dependent.
- Distributed ARSENY SECTION: factor two is used directly in both matrix traversals.
- Distributed ARSENY SECTION: the first stored Delta sample is reused for each `RO`.
- The distributed author source does not implement either the linear or squared-gap
  Eq.(43) approximation.

### Literature-supported

Advanced-adiabatic/hidden-crossing literature treats the branch-point action and
transition probability as impact-parameter dependent. Grozdanov-Solov'ev 2014
explicitly parameterizes branch-point evolution by \(\omega=\rho v\), and
Janev-Pop-Jordanov-Solov'ev 1997 explicitly studies impact-parameter-dependent
transition probabilities. Richter-Solov'ev 1993 supports factor-two branch-point
probability.

### Derived

For
\[
P(\rho)=\exp[-2\Delta(\rho)/v],
\]
using a frozen value \(\Delta_0=\Delta(0)\) gives
\[
\frac{P_{\rm frozen}(\rho)}{P(\rho)}
=\exp\!\left[-\frac{2(\Delta_0-\Delta(\rho))}{v}\right],
\qquad
\frac{\partial\ln P}{\partial\Delta}=-\frac{2}{v}.
\]

Thus the effect is exponentially amplified at low velocity. Its sign cannot be fixed
without the actual \(\Delta(\rho)\) profile.

For one isolated branch with support \(R_b\), if
\(\Delta_{\min}\le\Delta(\rho)\le\Delta_{\max}\),
\[
\pi R_b^2 e^{-2\Delta_{\max}/v}
\le
2\pi\int_0^{R_b}e^{-2\Delta(\rho)/v}\rho\,d\rho
\le
\pi R_b^2 e^{-2\Delta_{\min}/v}.
\]
This is not the full Eq.(50) multibranch cross section.

## 2. Policy synthesis

### Factor-two lane

The factor-two lane is now the primary research interpretation because it is
supported simultaneously by:

1. printed CPC Eq.(55);
2. the distributed author matrix code;
3. upstream advanced-adiabatic theory;
4. the modulus-square complex-action derivation.

This does not authorize a production default change.

### Eq.(52)-literal lane

The factor-one lane should be retained as a source-compatibility/control lane. It
remains useful for reproducing literal Eq.(52), documenting the paper/code conflict,
and sensitivity comparisons. It is no longer the strongest scientific candidate
solely because it appears in Eq.(52).

### Author Appendix-A benchmark

R9's `CMES(1)` finding changes how benchmark agreement should be interpreted.
Appendix-A numbers are outputs of the distributed author implementation, which appears
to use factor two but frozen \(\Delta(0)\) inside each branch support.

Therefore agreement with Appendix A measures implementation reproduction, not by
itself validation of the physically intended \(\rho\)-dependent Eq.(56) calculation.

This does not invalidate prior comparisons; it changes their claim ceiling.

## 3. Why no production change yet

A policy change now would mix two different changes:

- factor one -> factor two;
- author-like frozen Delta -> clean-room rho-dependent Delta.

They must be separated experimentally.

Existing DR8 evidence supplies a validated rho-dependent surrogate framework and shows
that the factor-two lane is more sensitive to low-energy model systematics. It did
not include an author-frozen-\(\Delta(0)\) comparison. Therefore R9 finding I2 cannot
be back-attributed to prior residuals without a new bounded diagnostic.

## 4. Canonical next experiment

Run three Nmax=3 research lanes under otherwise identical settings:

1. **F2-RHO:** factor two with current \(\Delta(\rho)\);
2. **F2-FROZEN:** factor two with \(\Delta(0)\) fixed inside each branch support,
   emulating the R9 static author data flow;
3. **F1-RHO:** literal Eq.(52) factor-one with current \(\Delta(\rho)\), as a
   source-compatibility control.

Use only the scoped five branches and energies 0.5 and 5 keV/u. Reuse validated DR8
surrogate/integration artifacts when provenance permits.

Required outputs:
- branchwise \(\Delta(\rho)/\Delta(0)\) profiles;
- branchwise F2-FROZEN / F2-RHO probability ratios;
- scoped indexed/shell observables for all three lanes;
- Appendix-A discrepancy metrics labeled
  `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`;
- F2-RHO vs F2-FROZEN as the measured impact of R9 finding I2.

If F2-FROZEN reproduces Appendix A materially better, it supports the `CMES(1)`
static interpretation and quantifies the author-code artifact, but does not make
F2-FROZEN physically preferred.

If F2-RHO remains closer, another implementation difference dominates.

## 5. Claim gate after R10

- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `factor2_research_lane=PRIMARY_CANDIDATE`
- `eq52_literal_lane=SOURCE_COMPATIBILITY_CONTROL`
- `author_appendix_benchmark=IMPLEMENTATION_BENCHMARK_NOT_PHYSICAL_GOLD`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`
- `production_default_change=NOT_AUTHORIZED`

The next node is bounded numerical research, not production Eq.(55).
