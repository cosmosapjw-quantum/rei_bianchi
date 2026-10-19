# RUN16: fixed-gas survivor sensitivity and the coupled feedback obligation

## Result and scope

For the unchanged positive source measure, native prescribed geometry, and a
**fixed** H-only retained energy core, the sub-H survivor is a decreasing,
convex functional of the neutral-H path. Its first derivative has an explicit
positive time kernel. A signed finite path change has an exactly nonnegative
Taylor remainder with computable nodewise bounds. These give a new diagnostic
of *where* gas-path uncertainty matters and whether a signed first-order
prediction explains the observed path change.

The existing RUN15 `compare_gas_paths.py` bounds two specified cubic
interpolants by a scalar relative epsilon. `compare_gas_pairs.py` applies that
comparison to specified finite trajectories. The transferred enclosure JSONs
use epsilon in global H-opacity extrema. Those results are reused; they did
not compute the signed functional derivative, its localized weights, or its
finite convex remainder. Those are the new RUN16 contributions proposed here.

This note provides the derivation and coding contract. The root agent owns
the new numerical implementation and actual numerical results. No original
source or result file is modified by this note.

## 1. Fixed measure, geometry and units

Use the original finite 160 births and GL8 exact scalar reflection quotient
(640 rays), with the first-cell source measure from the actual RUN15 postloss
source. For ray r let

\[
d\mu_r(E)=\frac{C_r g(E)}{Z}\,dE,\qquad
g(E)=\frac{E^2}{e^{E/(k_BT_*)}-1},\quad T_*=50000\,\mathrm K.
\]

Here `C_r` is the original first-cell comoving photon count and `Z` the fixed
first-cell normalization. The energy interval `I_r` is fixed before varying
the gas path. It includes the geometric terminal H-fit preimage and, for the
two subobservables, the separate terminal H-binding preimage. These endpoints
depend on geometry, not neutral-H density.

**Implementation detail that affects the derivative:** RUN15 initially chooses
its numerical core cutoff through a neutral-H lower bound. For RUN16, freeze
the baseline core intervals, source nodes/weights and H-crossing times for
all comparisons. Differentiating a density-dependent integration endpoint
would add a boundary term. A new tail estimate can be computed for the fixed
cutoff without changing that cutoff.

Let `z=(X-X0)/DeltaX`, `DeltaX=0.0004`, and define the fixed nonnegative kernel

\[
k_{rE}(z)=\frac{c\,\Delta X}{H(z)}
 \sigma_H(E R_r(z))\,
 \mathbf1_{z_{b,r}\le z\le z_{H,rE}}.
\]

It has units of volume; proper neutral-H density `n(z)` has units `m^-3`.
Consequently

\[
A_{rE}[n]=\int_0^1 k_{rE}(z)n(z)\,dz=\tau_{rE}[n]
\]

is dimensionless. In code, the argument is the archived dimensionless
comoving coordinate `Y_HI`, with

\[
n(z)=n_{H,0}e^{-3\Delta Xz}Y_{HI}(z).
\]

Multiplying `k` by this fixed density factor gives the code's linear operator
on `Y_HI`. Relative perturbations of `Y_HI` and `n` agree pointwise. The core
is born below the unchanged D gate, and the previously checked positive
native redshift rate keeps D inactive there. H binding, H fit and D gate
remain `13.598434599702`, `13.6`, and `13.602134599702 eV`, respectively.

For either binding subbin or their union, define

\[
S[n]=\sum_r\int_{I_r}e^{-A_{rE}[n]}\,d\mu_r(E).
\tag{1}
\]

The source measure is finite, and the native kernel has uniformly bounded
integral on this compact retained domain. These facts justify the exchanges
of differentiation and integration below for bounded gas paths. The formulas
also hold for the finite positive quadrature sum, with integrals replaced by
sums. An identity for that finite sum does not certify its continuum
quadrature error.

## 2. Derivative, positive kernel and convexity

Write `tau=A[n]` and `x=A[h]`. Direct differentiation of (1) gives

\[
DS[n]h=-\sum_r\int_{I_r}e^{-\tau_{rE}}A_{rE}[h]d\mu_r,
\tag{2}
\]

\[
D^2S[n](h,j)=\sum_r\int_{I_r}e^{-\tau_{rE}}
                       A_{rE}[h]A_{rE}[j]d\mu_r.
\tag{3}
\]

In particular, `D^2S[n](h,h)>=0`. Convexity need not be strict: a direction
with `A[h]=0` on the measured rays/energies has zero second variation.
Positivity of `A` also gives `DS[n]h<=0` for `h>=0`.

Fubini's theorem rewrites (2) as

\[
DS[n]h=-\int_0^1K_n(z)h(z)\,dz,\qquad
K_n(z)=\sum_r\int_{I_r}e^{-\tau_{rE}}k_{rE}(z)d\mu_r\ge0.
\tag{4}
\]

The weight is the **final** survivor, not the instantaneous photon population.
The same result follows from the scalar photon adjoint: its backward survival
factor multiplied by the forward population equals the final population.
This supplies an independent interpretation of the sign and time weighting.

For `h=n*rho`, define a dimensionless relative-response kernel and elasticity

\[
\eta_n(z)=\frac{n(z)K_n(z)}{S[n]},\qquad
\kappa_1=\int_0^1\eta_n(z)dz
=\frac{\sum_r\int e^{-\tau}\tau\,d\mu_r}{S[n]}.
\tag{5}
\]

Then `DS[n](n*rho)/S[n]=-integral(eta_n*rho)`. A uniform multiplicative
perturbation is therefore controlled to first order by the survivor-weighted
mean optical depth, not by the largest optical depth of all retained photons.
The value of `kappa_1` must be computed from the actual data. On a common time
partition `J_l`, record positive weights

\[
W_l=\frac{\sum_r\int e^{-\tau}A_{rE}[n\mathbf1_{J_l}]d\mu_r}{S[n]},
\qquad W_l\ge0,\qquad\sum_lW_l=\kappa_1.
\tag{6}
\]

These weights localize which portions of the gas path matter to each
observable. A gas discrepancy's maximum need not occur where `eta_n` is large.

## 3. Signed finite change and an explicit remainder

For any bounded signed `h` with physically nonnegative `n+h`,

\[
S[n+h]-S[n]=DS[n]h+\mathcal R[n,h],
\]

\[
\mathcal R[n,h]=\sum_r\int e^{-\tau}
       [e^{-x}-1+x]d\mu_r\ge0.
\tag{7}
\]

The exact scalar identity

\[
e^{-x}-1+x=x^2\int_0^1(1-s)e^{-sx}ds
\tag{8}
\]

proves positivity for either sign of `x`, including the continuous value zero
at `x=0`. Since `exp(-s*x)` lies between `exp(-max(x,0))` and
`exp(max(-x,0))`, it also proves

\[
\frac12\sum_r\int e^{-\tau-x_+}x^2d\mu_r
\le\mathcal R[n,h]\le
\frac12\sum_r\int e^{-\tau+(-x)_+}x^2d\mu_r.
\tag{9}
\]

Thus, if `d=sup|A[h]|`, a coarser bound is
`R <= exp(d)*sum(exp(-tau)*x^2*dmu)/2 <= S[n]*exp(d)*d^2/2`.
The signed prediction in (2) retains cancellation between time intervals;
an absolute epsilon envelope intentionally discards that cancellation.

For small `x`, evaluate the finite change using `expm1(-x)`. Evaluate the
remainder with a stable `x^2*(1/2-x/6+x^2/24-...)` representation or (8);
`expm1(-x)+x` still suffers cancellation when `x` is tiny. Record the series
truncation treatment or quadrature for (8), and do not silently clamp negative
roundoff into an asserted exact positivity certificate.

## 4. Conditional gas-path envelopes

If `n_minus<=n_star<=n_plus` pointwise, positivity of `A` gives the exact
functional order

\[
S[n_+]\le S[n_*]\le S[n_-].\tag{10}
\]

For `|h|<=epsilon*n`, `0<=epsilon<1`, this becomes

\[
\sum_r\int e^{-(1+\epsilon)\tau}d\mu_r
\le S[n+h]\le
\sum_r\int e^{-(1-\epsilon)\tau}d\mu_r.
\tag{11}
\]

It can be evaluated from the existing baseline optical depths without a new
IVP. For an absolute nonuniform envelope `|h|<=a`, replace `epsilon*tau` by
`A[a]`. In addition, (9) gives

\[
0\le\mathcal R[n,h]\le\frac{\epsilon^2}{2}
 \sum_r\int \tau^2e^{-(1-\epsilon)\tau}d\mu_r.
\tag{12}
\]

This converts a supplied path envelope into a goal-specific nonlinear error
budget. It does not establish the supplied envelope against the true ODE.

Keep the inherited tail separate. On the frozen core support, recompute the
tail upper bound using a valid H-density lower bound (for a relative family,
at least the factor `1-epsilon`). If `0<=T_i<=U_i` are the two omitted tails,
then the full observable change lies in
`[DeltaS_core-U_0, DeltaS_core+U_1]`, in addition to any core numerical error.
The core Taylor remainder alone is not the Taylor remainder of an uncomputed
full-tail functional.

## 5. A new computable checkpoint-preserving family

On every interval `[a,b]` of the union of the actual tight13 and standard18
knots, put `u=(z-a)/(b-a)` and `bump(z)=16*u^2*(1-u)^2`. The piecewise bump
and its first derivative vanish at every union knot. Hence

\[
n_\epsilon(z)=n_0(z)[1+\epsilon\,bump(z)]
\tag{13}
\]

is a positive C1 prescribed-HI family for suitable epsilon and agrees with
the baseline at every archived knot. Equations (2), (7), (9), and (11) can
quantify its observable effect now. This is a transparent conditional path
family, not an asserted solution of the chemical ODE. Varying only HI is an
argument of the optical-response functional; full gas conservation/rate
consistency is a separate condition. The construction is not presented as a
strong no-go theorem or a bound on the actual interpolation error.

## 6. Constructive closure of the full coupled error obligation

The full gas system is not a prescribed coefficient. After eliminating the
linear photon equations along a given gas path, write its integral equation
as `g=T_mu[g]`, where the nonlinear Volterra map contains the native atomic
rates and the entire spectral photoresponse. For a reconstructed path `gbar`
and a finite source quadrature `Q`, define

\[
r_\mu=gbar-\mathcal T_\mu[gbar]
=(gbar-\mathcal T_Q[gbar])+
  (\mathcal T_Q[gbar]-\mathcal T_\mu[gbar]).
\tag{14}
\]

The two terms separate reconstruction/ODE defect from source-quadrature
defect **at the same reconstructed path**. With a verified positive gas and
temperature tube, suppose the native rates and photon memory imply

\[
\|\mathcal T_\mu[g_1](t)-\mathcal T_\mu[g_2](t)\|
\le\int_0^t L(t,s)\|g_1(s)-g_2(s)\|ds,
\quad L\ge0.
\]

Then the actual error satisfies

\[
e(t)\le\|r_\mu(t)\|+\int_0^tL(t,s)e(s)ds.\tag{15}
\]

For example, if `L(t,s)<=M` and `||r_mu||<=R0` on the finite interval,
Gronwall gives `e(t)<=R0*exp(M*t)`. A bounded Volterra kernel has a finite-time
resolvent with factorial control of iterated integrals; a strict global
contraction constant below one is not a prerequisite. Tighter time-dependent,
component-scaled or one-sided estimates can improve an otherwise loose bound.

What remains to make (15) numerical is concrete: a tube in the native rate
domain; a between-knot defect enclosure; an entire-source spectral defect;
and bounds on the native atomic Jacobian plus the photon-memory response in
that tube. This core survivor kernel alone supplies none of those whole-system
constants. Once a resulting HI path envelope is available, (10)--(12) transfer
it to this particular observable. Einstein/geometry feedback is a separate
remaining DAG obligation and is not included in this prescribed-geometry map.

An alternative goal-weighted route uses an adjoint and the same residual,
with a controlled nonlinear remainder. Cao--Petzold (2004), sections 2.1 and
2.3, makes explicit the residual sensitivity and the nonlinear remainder that
must be retained. Ranocha--Giesselmann, arXiv:2307.12677, section 2.1,
Lemma 2.1, gives a residual-based ODE bound under a one-sided Lipschitz
condition and a sufficiently regular reconstruction. These support a
constructive next step; they do not provide this project's missing constants.

## 7. Coding and evidence contract

Compute now: baseline positive quadrature optical depths; moment elasticities;
the signed tight13-to-standard18 perturbation on one frozen support/time
partition; the direct change, linear prediction, positive remainder and
nodewise bounds; positive interval weights and their sum; and selected
checkpoint-preserving C1 perturbations. Retain the two binding observables.

Use actual input/source hashes and one fixed normalization. Check the shared
support and unchanged crossings. Compare direct and kernel contractions and
the convex remainder within declared arithmetic tolerances. Keep the existing
RUN15 scalar/vector optical-depth discrepancy in the inherited uncertainty
record; exact finite-sum identities do not remove it. Do not rerun old native
trajectories.

| Claim | Status in this derivation unit |
|---|---|
| Fixed-core derivative, convexity, positive kernel | DERIVED |
| Signed finite remainder and conditional envelope | DERIVED |
| Nonlinear residual/Volterra implication given its assumptions | DERIVED |
| Adjoint/residual methodology in primary papers | LITERATURE_SUPPORTED |
| RUN16 numerical sensitivities and bump effects | Root implementation/results, not executed by this theory agent |
| True IVP HI envelope, whole-source defect and feedback constants | UNRESOLVED |
| Coupled spectral continuum bound | UNRESOLVED |

The existing `P4-S4C-SPECTRAL-EDGE-SUPPORT` node remains selected. No original
45-node/26-node DAG obligation is removed or replaced. This unit supplies the
next constructive equations and diagnostic, not a new gate.

## Primary references actually retrieved

1. Y. Cao and L. Petzold, *A Posteriori Error Estimation and Global Error
   Control for Ordinary Differential Equations by the Adjoint Method*,
   SIAM Journal on Scientific Computing 26(2), 359--374 (2004),
   DOI: [10.1137/S1064827503420969](https://doi.org/10.1137/S1064827503420969).
   [Author-hosted full text](https://people.cs.vt.edu/~ycao/publication/siam_42096.pdf).
   Actual read: sections 2.1 and 2.3, equations 6--8 and 15--18. SciSpace's
   index dated the record 2005; the primary paper prints 2004 and an electronic
   publication date of 22 December 2004. The primary year is used here.
2. H. Ranocha and J. Giesselmann, *Stability of step size control based on a
   posteriori error estimates*, [arXiv:2307.12677](https://arxiv.org/abs/2307.12677),
   [author preprint](https://arxiv.org/pdf/2307.12677).
   Actual read: section 2.1, equations 2.7--2.9, Lemma 2.1 and proof. Its
   role here is residual-plus-stability control, not the paper's separate
   analysis of step-size-controller stability.

SciSpace was actually searched with a natural-language question about
adjoint ODE observable-error estimates, residual representations and stability
factors. Exa located the first primary PDF, and both primary PDFs were then
opened with the research web tool. Exact discovery queries and selected IDs
are in `LITERATURE_RETRIEVAL_RECEIPT.json`.
