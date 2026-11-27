# E13C9: signed second-Volterra correction with two independent resolutions

Status: **DERIVED; candidate-design assistance, not independent numerical admission**.
Author role: `e13c9_volterra_theory`. This task performed source inspection and direct
derivation only. It did not execute captured paths, the previous full batch, or a
new manufactured control. No restored evidence was changed.

## 1. Scope and exact available interfaces

The target is the same captured OFF finite problem: fixed gas interpolation,
captured source switch and masks, captured binary64 constants realified exactly,
unchanged weights, and signed energy seams. No continuum, gas-feedback, production,
or receiver claim follows from this numerical method.

Source root, abbreviated `R7` below:

`../RESTORED_E13C8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`

Evidence root, abbreviated `R8` below:

`../RESTORED_E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1`

Read sources:

- `R8/analysis/RESIDUAL/RESIDUAL_AND_NEXT_METHOD_KO.md`, especially sections 2–3.
- `R8/review/THEORY_PROPOSAL_REVIEW.json`: previous finite Volterra identities
  accepted only as derived proposals, with numerical implementation absent.
- `R7/code/vendor/local_enclosure.py`: `Coefficients`, `integrands`.
- `R7/code/vendor/directed_interval.py`: `IV`, `Jet2`, `response_j`.
- `R7/code/vendor/path_enclosure.py`: local quadrature, frozen outputs/gains,
  remainder, segment assembly, and seam rules.
- `R7/code/off_path_worker.py`: input semantic checks and unchanged-kernel pins.

`Coefficients(control)(Jet2.variable(cell))` evaluates `E, q, lambdas` and their
first and second derivatives with respect to **normalized** `x∈[0,1]`. `Jet2.d2`
is the actual second derivative, not the second Taylor coefficient. `IV` uses
directed arithmetic; `response_j(rate, width)` implements the continuous
zero-rate branch and accepts interval widths. Its rate argument is an `IV`.

For the present implementation, use `N_base` for the already computed local
first-variation quadrature and coefficient absolute-integral bounds, and
`M_second` for the new prefix and signed correction computation. These are
distinct numerical resolutions.

Reusing `local.signed` and `local.bounds` is valid only after matching their
actual bytes, captured input identity, scientific kernel identity, and precision.
Both quantities are independent of incoming correction center `c` and radius
`η`. In contrast, each segment must recompute

\[
S=|c_{new}|+\eta_{new}+B_r
\]

from its newly propagated carry. A saved old `S` is not interchangeable with it.

## 2. Prefix equation in the implementation coordinate

Write physical segment coordinate `t=h x`, `x∈[0,1]`, and let

\[
a=h\Lambda_f,\quad
r(x)=q(x)-q_f-\Delta\Lambda(x)P_f(x),\qquad
Y(x)=\delta_1(hx).
\]

Then

\[
Y'(x)=h r(x)-aY(x),\qquad Y(0)=c.
\]

Only the incoming **center** initializes the prefix. Incoming uncertainty `η`
is retained separately in the final analytic remainder. The interval width of a
computed prefix is numerical enclosure width; it does not stand for `η`.

The first-variation function still uses the same frozen stock

\[
P_f(hx)=f_0 e^{-a x}+q_f J(\Lambda_f,hx),\qquad
J(\ell,z)=\int_0^z e^{-\ell u}\,du.
\]

All coefficients and their derivatives are evaluated on the existing captured
branch, including event-adjacent segments. Do not retest the mask from endpoint
energy or clamp an endpoint to a branch threshold.

## 3. Stable O(M_second) endpoint recurrence

Set `Δ=1/M_second`, cell `[x_j,x_{j+1}]`, midpoint `m_j`. Suppose directed interval
`Y_j` contains the exact `Y(x_j)`. The exact recurrence is

\[
Y(x_{j+1})=e^{-a\Delta}Y(x_j)
 +h\int_{x_j}^{x_{j+1}}e^{-a(x_{j+1}-v)}r(v)\,dv.
\]

Define `f_j(v)=exp[-a(x_{j+1}−v)]r(v)`. Since `a` is constant,

\[
f_j''(v)=e^{-a(x_{j+1}-v)}
 [r''(v)+2ar'(v)+a^2r(v)].
\]

The existing whole-cell `Jet2` evaluation bounds all three values on the right.
Obtain `M2_j ≥ sup_cell |f_j''|` by ordinary directed interval expression
composition. Let `R_j` be an outward upper bound of `h Δ³ M2_j / 24`. Then

\[
Y_{j+1}=e^{-a\Delta}Y_j
 +h\Delta e^{-a\Delta/2}r(m_j)+[-R_j,R_j]
\]

contains the exact next endpoint. Induction starts with `Y_0=[c,c]`.
The exponential never grows, so this avoids a global integrating factor
`exp(a x)` and the associated large-`a` amplification.

**Coordinate warning:** derivatives above are with respect to `x`. The midpoint
radius is `h Δ³ M2_j/24`; do not multiply by an additional `h²` after obtaining
`r′,r″` from the normalized-coordinate `Jet2`.

This recurrence uses one whole-cell coefficient/derivative call and one
midpoint coefficient call per new cell. It is O(M_second) and can stream with
constant working memory aside from the evidence the owner elects to retain.

## 4. Enclose the whole causal prefix in each cell

For any `z=x−x_j∈[0,Δ]`, variation of constants gives

\[
Y(x_j+z)=e^{-az}Y(x_j)
 +h\int_0^z e^{-a(z-u)}r(x_j+u)\,du.
\]

Let `R_cell` be the interval value of `r` on the whole cell. Because the kernel
is nonnegative, the following is a simultaneous enclosure for every such `x`:

\[
U_j=\exp(-a[0,\Delta])Y_j
      +hJ(a,[0,\Delta])R_{cell}.
\]

The product drops correlations and can be conservative, but inclusion follows
directly. No positivity of `Y_j` or of `r` is needed. The zero-rate branch has
`J(0,[0,Δ])=[0,Δ]`. Negative `ΔΛ` is permitted as long as the original actual
opacity nonnegativity premise remains valid.

`U_j` must use the **left** endpoint enclosure before it is overwritten by
`Y_{j+1}`. A terminal prefix enclosure by itself cannot replace all `U_j`.

## 5. Signed correction kernels and rectangle enclosure

Use the original terminal kernels at the current physical point `t=hx`:

\[
W=e^{-\Lambda_f(h-t)},\quad K_0=J(\Lambda_f,h-t),\quad
K_E=E(t)J(\Lambda_f+1,h-t).
\]

The signed kernels to multiply by `δ1` are:

| Output | `k(t)` in second correction `∫ k(t)δ1(t) dt` |
|---|---|
| P1 | `−W ΔΛ` |
| P1_energy_eV | `E(h) k_P1` |
| Z_eV | `−K_E ΔΛ` |
| QN, QE_eV | exactly zero |
| A_i | `Δλ_i − λ_fi K_0 ΔΛ` |
| B_i_eV | `E Δλ_i − λ_fi K_E ΔΛ` |
| H_i_eV | `(E−χ_i)Δλ_i − λ_fi(K_E−χ_i K_0)ΔΛ` |

For a whole-cell interval enclosure `K_{k,j}` of the appropriate signed kernel,

\[
C_k=\sum_j h\Delta K_{k,j}U_j
\]

contains the exact signed second correction. Every term and sum uses directed
interval arithmetic. This is a rectangle **range** enclosure, not a midpoint
estimate with an omitted error bar. Its width generally decreases only to first
order with `M_second`, whereas the causal endpoint recurrence has a midpoint
truncation enclosure. Do not label the whole method as a new global second-order
quadrature solely because the Volterra expansion has two terms.

The cheap rectangle enclosure is appropriate for the bounded prototype: its
uncertainty is multiplied by the small coefficient-defect kernels, whereas the
already certified first-variation midpoint radii remain unchanged. Whether it
is sufficiently narrow must be measured on the actual representative paths.

For exact functions, `k_A,total=−k_P1`; also
`k_P1_energy+k_B,total+k_Z=0`, and
`k_H,i−k_B,i+χ_i k_A,i=0`. Interval evaluation should preserve inclusion of zero
in these ledger combinations, not force centers to satisfy them through an
intersection or clamp. For reported totals retain the original species-sum
semantics; a separately enclosed total kernel is not a silent replacement.

## 6. Final segment assembly and carry

Let `F1_k` be the reused `local.signed[k]`, `G_k` the existing frozen gain, and
`R_rep,k = frozen[k]−captured[k]` the unchanged representation correction.
The numerical enclosure before the analytic tail is

\[
B_k=F1_k+G_k[c,c]+C_k+R_{rep,k}.
\]

Use this expression, **not** the coarse new prefix endpoint, for the final
first-plus-second photon candidate. The new prefix endpoint is auxiliary to
the small signed correction. Replacing `F1_P1+G_P1 c` by `Y_M` would discard the
finer baseline first-variation quadrature.

Choose a representable center of `B_k`, account outwardly for its radius and
centering, and add

\[
R_{tail,k}=(|G_k|+T_k)\eta+T_k D S,
\quad D\ge\int_0^h|\Delta\Lambda|,\quad
S=|c|+\eta+B_r.
\]

For photon, `G=F(h)`, `T=H_h`; for redshift `T=H_E`; for individual moments use
the unchanged effective/triangle `T` bounds. For QN and QE both `G,T` vanish.
The identity is finite and does not require `D<1`. `H_h` is a terminal kernel
bound and must not replace the whole-operator bound `D`.

Numerical prefix uncertainty is already present in `C_k`; it must not be
silently erased. Conversely there is no need to add it a second time as a
separate physical incoming uncertainty. Compute new outgoing photon center and
radius, then use the original exact captured photon stitch and signed `ΔE·P`
seam procedure. Never erase or duplicate the energy anchor.

## 7. Independent manufactured-control suggestions

These are proposals for independent implementation, not executed results.
Separate the scalar prefix/correction algebra from the project coefficient
class so its oracle cannot inherit the same coefficient translation error.

1. **Zero opacity / polynomial forcing; coordinate and sign check.** Set
   `Λ_f=0`, `P_f=0`, `ΔΛ=d≥0`, physical forcing `r(t)=1+t+t²`, and center `c`.
   Then
   `δ1(t)=c+t+t²/2+t³/3` and
   `C_P=−d[c h+h²/2+h³/6+h⁴/12]` exactly.
   A rational `h` other than 1 detects incorrect `h` scaling. With a single
   species and unit weight, `C_A=−C_P`. Test every prefix boundary against the
   exact polynomial, not only the final correction.

2. **Constant opacity / closed exponential reference.** With `Λ_f=L≥0`,
   constant `ΔΛ=d`, and constant `r=R`,
   `δ1(t)=c exp(−Lt)+R J(L,t)`, while
   `δ(t)=(c+e)exp[−(L+d)t]+R J(L+d,t)`.
   Require `L+d≥0`. This checks the signed correction and analytic tail for
   positive and negative allowed `d`, including a finite case with `D≥1`.

3. **Signed cancellation without absolute-value substitution.** Set `r=0`,
   `ΔΛ(t)=d(2t/h−1)`, `Λ_f≥|d|`, and nonzero center `c`. Then
   `δ1=c exp(−Λ_f t)` and `C_P=0` exactly because the signed integrated opacity
   defect is zero, although the absolute-kernel bound is positive. The exact
   endpoint defect also equals `(c+e)exp(−Λ_f h)`. The second correction need not
   vanish at intermediate prefixes or for every weighted moment.

4. **Incoming uncertainty cannot disappear.** Choose constant `P_f=1`,
   `q_f=Λ_f`, actual `q=Λ_f+d`, actual `Λ=Λ_f+d≥0`, `c=0`, and `0<η<1`.
   Then `r=0`, `δ1=0`, and every signed correction is zero, but exact solutions
   with `e=±η` have `δ=e exp[−(Λ_f+d)t]`. Both must be enclosed after the analytic
   incoming tail is added. This admits positive actual photon stock and tests
   the uncertainty term independently of the prefix's own numerical width.

5. **Species cancellation with nonzero individual moments.** Set
   `Δλ_1=+d`, `Δλ_2=−d`, `ΔΛ=0`, and frozen rates large enough that both actual
   rates stay nonnegative. With nonzero `δ1`, photon second correction is zero,
   but unit-weight species corrections are
   `C_A1=+d∫δ1`, `C_A2=−d∫δ1`, generally nonzero. This detects the invalid shortcut
   that kills every species correction when total opacity defect is zero.

6. **Exact-zero invariant.** With `f0=qf=q=c=η=0`, `δ1` and every new correction
   vanish even if nonnegative opacities vary. This is a manufactured algebraic
   test; the already adopted 95 zero paths need not be recomputed.

The owner's representative captured-path tests then address byte/input parity,
fixed branch behavior, incoming carry, signed seams, raw overlap/nesting, and
measured time. These test different risks from the manufactured formulas.

## 8. What to conclude if the remaining width is dominated by midpoint bounds

Increasing `M_second` changes only the new prefix/rectangle enclosure. It does
not shrink the inherited `N_base` first-variation midpoint radius. Thus a small
M32→M128 improvement after a larger first-plus-second improvement can be an
expected result, not evidence for higher precision or a full batch rerun.

If new rectangle width remains materially important, an available O(M_second)
refinement is to enclose `Y` at each cell midpoint and build
`Jet2(U_j, h r_cell−a U_j, h r'_cell−a(h r_cell−a U_j))`.
Multiplying by a `Jet2` for `k` then bounds `(kY)''` for a validated midpoint
correction. One simple midpoint enclosure is

\[
Y(m_j)\in e^{-a\Delta/2}Y_j+hJ(a,\Delta/2)r(m_j)
 +[-hM_{1,j}\Delta^2/8,\ hM_{1,j}\Delta^2/8],
\]

where `M1_j≥sup_cell |r′|`; this follows by integrating the mean-value bound
against the nonnegative exponential kernel. This is an optional mathematical
design, not a claim that it was implemented or benchmarked.

If instead the unchanged first-variation midpoint radius dominates, further
second-correction refinement has little demonstrated value. The next numerical
choice would need an accuracy objective and a bounded comparison of targeted
first-variation quadrature improvements (resolution or a separately derived
higher-order rule). The present `Jet2` supplies only second derivatives; it
does not justify a fourth-order Simpson/Gauss remainder. Do not extrapolate
the whole width by `D`, by `M_second^-2`, or by an unmeasured NCP speedup.

Physical/continuum/production/receiver remain **HOLD**. The preceding full
finite E13C8 admission is unchanged by this design note.
