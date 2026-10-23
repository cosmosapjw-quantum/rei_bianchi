# Independent mathematical review — ANGTHERM01

Date: 2026-10-23. Reviewer: Astra research-review lane
`/root/rei_latest_survey`. This reviewer did not author the theory or
implementation. Authority: the intrinsic physmath-research-loop 1.0.0,
approved v0.2 research protocol and the controller's bounded review request.

## Decision and reviewed scope

**PASS for the mathematical contract, under its stated source, symmetry,
initial-data and validity-domain assumptions.** No blocking algebraic defect
was found. This decision permits implementation and the frozen finite
experiment; it does **not** admit implementation correctness, numerical
results, empirical atomic accuracy or a self-consistent cosmological model.

Only the two requested frozen documents were inspected for this review:

| Document | Bytes | SHA256 |
| --- | ---: | --- |
| `THEORY.md` | 13895 | `7140ababd9f5e7cd9915d97154c436ba62239c4266ac6bb3ff644a8a5c77b12e` |
| `EXECUTION_CONTRACT.md` | 9232 | `e0239480a8d6e26cba9faa32948d69c272a5e3e85ed49f9a06f7f05275c4ddf7` |

The algebra below was checked independently by direct differentiation and
eventwise cancellation. The controller's reported Wolfram identities are
consistent with this derivation but were not used as a substitute for it.
No scientific IVP, donor rerun, implementation edit or remote write was
performed by this review.

The controller separately communicated the source-bound constants
`sigma_T=6.6524587051e-25 cm^2` from C13 `THOMSON_CGS`,
`c=29979245800 cm/s`, and
`k_B=1.380649e-23/1.602176634e-19 eV/K` from C22A. These clarify provenance
without changing the derivation. This addendum is not present in the two
file byte sequences identified above and should retain its own revision
identity when recorded.

## 1. Directional characteristics and fixed-momentum measure

Let `D^2=(1-mu0^2)e^(2b)+mu0^2 e^(-4b)` and
`mu=mu0 e^(-2b)/D`. The transverse and longitudinal contributions divided
by `D^2` are `1-mu^2` and `mu^2`, respectively. Therefore

\[
\frac{D'}D=b'[(1-\mu^2)-2\mu^2]=b'(1-3\mu^2),
\]

\[
\frac{E'}E=-1+b'(1-3\mu^2)=-1-2b'P_2(\mu),\qquad
\mu'=-3b'\mu(1-\mu^2).
\]

Both identities have the stated signs. They follow from the exact map and
require no discretized directional ODE. The constant subtraction of the
initial `b` is a spatial coordinate normalization when initial momenta and
initial physical directions are defined in that normalized frame.

The spatial metric determinant is `a^6`; the factors containing `b` cancel.
Thus physical volume is proportional to `a^3`. The fixed covariant-momentum
measure `2 f(q)d^3q/[(2 pi hbar)^3 a^3]` and the conserved reference-nucleus
density have the same volume dilution. A fixed momentum cell has constant
photon number per Href in collisionless propagation. Applying an additional
current-angle Jacobian to its already integrated count would double count
the push-forward. The frozen packet convention is correct.

## 2. Radiation tensor, sign and work normalization

For an azimuthally symmetric packet collection,
`Pzz=sum(E g mu^2)=(U_gamma+2Q)/3`, and each transverse pressure is
`(U_gamma-Q)/3`. Subtracting the trace gives

\[
\pi=\operatorname{diag}(-Q/3,-Q/3,2Q/3).
\]

Consequently

\[
\sigma:\pi=2sQ,\quad \|\sigma\|_F^2=6s^2,\quad
\|\pi\|_F^2=2Q^2/3.
\]

These are per-Href stress moments until multiplied by `n_Href` and the
chosen energy-unit conversion. The distinction from a historical
`sqrt(3)|s|/H` display convention is explicit. Signed `Q`, rather than its
absolute value, must enter the shear work. The contraction can have either
sign.

Using the single-photon energy identity gives

\[
U_\gamma'=-U_\gamma-2b'Q
\]

in the absence of absorption. Multiplication by `n_Href`, whose logarithmic
derivative is `-3`, gives the stated physical-radiation equation with mean
expansion coefficient four. Thus the ledger choices
`W_mean'=U_gamma` and `W_shear'=2b'Q` have the correct normalization.

For the prescribed interpolant, the effective proper shear in an interior
evaluation is **`s_eff=H_interp*b_interp'`**. Every new contraction, norm and
work diagnostic must use that same derivative; separately interpolating
the saved proper-shear samples and substituting them in a work diagnostic
would define a different model. This is an implementation consequence of
the already frozen interpolation rule, not an additional physical input.

## 3. Common temperature and the event ledger

Each photoionization event changes electron count by `+1`, consumes one
photon and increases binding energy by `chi`. It deposits `E-chi` into the
gas. Each radiative recombination reverses the electron/binding change,
removes mean captured kinetic energy `K` from the gas and records
`chi+K` in the cumulative escaped-energy ledger. Combining these changes
with the photon and gas expansion terms cancels each event separately:

\[
\bigl(U+I+U_\gamma+E_{\rm esc}+W_{\rm gas}
 +W_{\rm mean}+W_{\rm shear}\bigr)'=0.
\]

The charge/count identities also cancel eventwise:
`(v+C_RR-C_abs)'=0` and `(sum g+C_abs)'=0`. These statements do not depend
on the eventual numerical trajectory. Integrating their reservoirs with
their own right-hand sides makes them useful numerical diagnostics;
reconstructing reservoirs from the identity would remove that test.

The factor `n_Href/H` in recombination and `c n_Href/H` in absorption is
dimensionally correct for events per Href per eta. For an isotropic ideal
nonrelativistic mixture, pressure work per Href is
`3(N_nuc+v)k_B T=2U`, so the gas term is `U'=-2U+event heat`.
There is no traceless gas stress under this closure.

The common-temperature relation is an explicit constitutive assumption:
photoelectron excess energy is assigned to the common thermal pool, and
all included particles share its temperature. Since
`T=U/[C_T(N_nuc+v)]`, the derivative contains the particle-count term
`-T v'/(N_nuc+v)`. Evolving `U` and reconstructing `T` as specified includes
it automatically. Adding the same term again to the energy equation would
be incorrect. The stated derivatives `T_U` and `T_f` are correct.

`E_esc` is accumulated energy at emission. It is not the present energy of
an escaped, subsequently redshifted photon distribution. The explicit
ledger interpretation therefore closes the accounting without silently
introducing a new gravitating or transported radiation component.

## 4. VF capture-energy closure

For the frozen VF functional form, logarithmic differentiation yields

\[
D_\alpha=-\frac12-rac{(1-b_v)r_0}{2(1+r_0)}
                   -\frac{(1+b_v)r_1}{2(1+r_1)}.
\]

Therefore `3/2+D_alpha` is exactly the positive rational expression in
`THEORY.md`. For finite positive temperature, positive fit temperature
scales and `-1<=b_v<=1`, the resulting `K` is positive.

For a temperature-independent microscopic capture kernel, a Maxwellian
rate has the form `alpha=C T^(-3/2) integral[epsilon sigma(epsilon)
exp(-epsilon/(k_B T)) d epsilon]`. Differentiating this integral gives
`K/(k_B T)=3/2+d ln(alpha)/d ln(T)`. Applying that identity to an adopted
fit is the stated conditional constitutive closure. A good number-rate
fit alone does not establish accuracy of its derivative or energy moment.
The theory correctly keeps those claims separate.

The numerical temperature-domain gate must ultimately match the **active
source rows**. An earlier inventory of a different donor registry listed
an HeI-a fit interval of `3..1e6 K`, whereas this contract writes the general
`3..1e9 K` interval. The present review has not read the new vendored row
selection and does not establish that the same narrower row is active.
This is a bounded source-applicability check for the implementation review:
inspect the actual selected rows and apply their common domain if it is
narrower. It is not an algebra defect or evidence that any planned case
leaves its valid range.

## 5. Exact isotope and angular quotients

For two eligible isotopes in the same electronic element, their fraction
difference satisfies `delta'=M_g(T,g,n_e) delta` along a full-system
solution. Equal initial fractions give the unique solution `delta=0`,
including when the shared coefficient matrix depends on the nonlinear
collective state. Equivalently, lifting a reduced solution gives the same
electron density, opacity and thermal state and satisfies the full
equations. This uses the adopted equality of electronic rates and energy
increments and the exact individual isotope totals. The stated sums
`Y_H=1.000025`, `Y_He=.08201`, `Y_Li=5.0001e-10` are correct.

Zero-total species must be kept as invariant zero blocks rather than
dividing by their total. Unequal isotope initial fractions do not meet the
hypothesis. Retaining all nine fractions also avoids defining a neutral
fraction by a cancelling subtraction. The theorem is an invariant
finite-system quotient under the stated assumptions, not an unrestricted
claim about physical isotopes.

For each angular group, the eight members have the same energy and radial
cross sections at every eta. Thus they have a common extinction
coefficient, and their sum satisfies `G'=-kappa G` exactly. The equal
member-count ratios remain invariant. Four uniformly spaced azimuths
cancel off-diagonal moments and give equal transverse diagonal moments;
the reflected partners cancel odd directional moments. The folded scalar
count and the diagonal stress therefore equal the explicitly unfolded
finite system exactly. This proof does not establish angular-continuum
accuracy. Its symmetry restrictions and unequal-data controls are
appropriate and explicit.

The two quotients are compatible: both preserve the same total opacity,
electron density, common thermal state and event energies. The documented
state dimensions are correct: `21+48M+8` versus `9+6M+8`, or 221 versus 41
at `M=4`.

## 6. Optical depth and analytic Jacobian

For positive initial group inventory, integrating
`G'=-kappa G` gives `G=G0 exp(-tau)` and `tau'=kappa`. This is an exact
coordinate change. At fixed gas state it removes the direct `-kappa`
diagonal from the photon equation, but does not establish that the coupled
gas/photon system is nonstiff. Structural zero groups require no logarithm.

The direct coefficient should be evaluated as

\[
c_{ej}=\exp\{\log(c n_{\rm Href}/H)+\log\sigma_e+\ell_j\},
\qquad A_{ej}=c_{ej}y_l,
\]

with physical zero cross sections handled before taking a logarithm. The
signed trial population is multiplied afterwards. This preserves a
representable scaled event coefficient when its separately exponentiated
raw photon count would underflow.

The same representation must be retained in the Jacobian:
`partial A/partial tau_j=-c_ej*y_l` and
`partial A/partial y_l=c_ej` before any isotope-coordinate factors. A
Jacobian that first reconstructs a vanishing `G` would contradict the
direct-scaled RHS in precisely the intended representation control. The
frozen differential formulas imply the correct implementation.

The recombination differential, the common-temperature chain rule and the
analytic differentiation of `K` are correct. Centered finite differences
at fixed eta away from support boundaries test state derivatives without
differentiating a threshold discontinuity.

## 7. Background domain and finite acceptance

Using `b` and the derivative of the same cubic Hermite interpolant makes
the geometry and work identities mutually consistent. Positive `H` from
the exponential of the interpolated `log H` and
`n_Href=n_Href(0)exp(-3 eta)` complete a specified trace-background model.
Those conventions do not supply an error bound for the original Einstein
solution, which the theory correctly excludes.

Monotone redshift on a ray requires
`1+b'(3mu^2-1)>0`. A convenient sufficient bound for every direction is

\[
-\tfrac12 < b'(\eta) < 1.
\]

For each Hermite interval, `b'` is quadratic, so its endpoints and any
interior vertex provide a finite direct check of this sufficient bound.
The sign-reversed control must also satisfy its own check; `|b'|<1/2`
suffices for both signs. Failure of the sufficient bound alone is not a
proof of nonmonotonicity for the particular finite rays, which can instead
be checked directly. All adopted fits' support thresholds and the LiI
provider switch must be included in the frozen segmentation. One-sided
provider evaluation at a discontinuity is compatible with keeping actual
geometry and work evaluated at the true endpoint.

The separately assembled full per-isotope/per-packet event model is an
independent implementation oracle for the quotient. Sharing immutable
atomic data, geometry and the Radau integrator does not make it an
independent validation of the physical atomic fits or the cosmological
background. The analytic geometry controls, local identities, Jacobian
check, full/reduced comparison and tighter-tolerance run address distinct
implementation risks. The contract states these boundaries accurately.

The fixed comparison limits, count of IVPs, resource caps and stop rule
form a finite acceptance decision. Agreement on 201 samples and measured
M4/8/16 differences do not by themselves certify continuum-time or
angular-continuum error; the admitted claim remains the explicitly tested
finite system if angular refinement is unresolved. Conservation residuals
must retain the promised fixed, physically meaningful normalization and
raw maxima.

## Required next review, without expanding the experiment

No theory repair or additional trajectory is requested by this review.
The subsequent independent math-code/results review should inspect the
actual diff, donor/source identities, the active fit validity intervals,
`s_eff=H b'` consistency, directly scaled RHS **and** Jacobian columns,
non-quotient control admission, raw finite acceptance metrics and the
actual plots. These are implementation checks within the existing frozen
contract. This reviewer remains available for that review and has not
authored the implementation.
