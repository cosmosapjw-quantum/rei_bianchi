# New postloss fixed-gas optical response

This work unit is newly implemented after the workspace-loss incident. It is
not the lost RUN15 enclosure source and does not restore the missing native
RUN15 trajectory arrays. No native IVP is executed by these files.

## Source and physical scope

The explicit `--source-root` is the original `run13/recovered` directory at the
restored repository. Every used archive input is checked against that
directory's actual `SHA256SUMS.txt`; the manifest's own SHA is recorded. The
original `RetardedModel`, `sigma_native_formula`, geometry table and atomic
source files are read from that directory. The new vector geometry evaluation
is checked against the original scalar geometry and ray energy expressions.

The source retains the original first-cell count for each of 160 birth samples
and GL8 direction pairs. The exact reflection quotient contains 640 rays. For
each ray, let `C_r` be its archived comoving first-cell photon count and let

\[
g(E)=\frac{E^2}{\exp(E/k_BT_*)-1},\quad T_*=50000\,\mathrm K,\qquad
Z=\int_{13.6}^{14.112863291954785}g(E)\,dE.
\]

The continuous source measure for this diagnostic is `C_r g(E)dE/Z`. The
operation order for `k_B T_*` is read from the owner source. GL64 and GL96
normalizations are compared. No new cohort packet or other 47-cell source
values are written. This continuous first-cell reference is conditional on
the original finite births, angular quadrature and original cell counts.

The archived **tight** history supplies 12 saved gas checkpoints plus the
initial state: **13 knots**. The archived **standard** history supplies 17
saved checkpoints plus the initial state: **18 knots**. These define different
PCHIP paths. Comparing their responses combines checkpoint placement and
finite solver effects; it is not a comparison of ODE tolerances on one common
gas interpolation grid. The true gas path between checkpoints is not bounded.

## Optical depth and threshold partition

The original prescribed BASS121 `SIGNED_MINUS` geometry gives

\[
E(X)=R(X;X_b,\mu)E_b,
\quad q=-\frac{d\ln E}{dX}
=1+b_X(3w-1),\quad 0\leq w\leq1.
\]

Here `w` is the parallel directional energy fraction. The extrema of the
original quadratic `b_X` on each intersecting Hermite interval give a positive
global `q` lower bound. An endpoint ratio alone is not used as a monotonicity
proof. `H=exp(cubic)` has its extrema determined from the log-H cubic.

With `z=(X-X0)/(X1-X0)`, the retained core optical depth is

\[
\tau_H(E_b)=\int_{z_b}^{z_H}
 \frac{c\,\Delta X}{H(z)}\,n_{H,0}Y_{HI}(z)e^{-3\Delta X z}
 \sigma_H(E_bR(z))\,dz.
\]

This keeps the proper-density dilution and `dX/H` proper-time factor. The
crossing `z_H` solves `E_b R(z_H)=13.6 eV`. Time quadrature is split at both gas
PCHIP knots and geometry Hermite knots, then uses positive Gauss-Legendre
nodes on each resulting panel. Four independent scalar native-geometry plus
adaptive-quadrature checks compare optical depths with the vector procedure.

The source observable has endpoint upper birth-energy limit
`U_r=13.6/R_r(1)`. It is separately partitioned at
`13.598434599702/R_r(1)` to measure the part below H binding and the part between
H binding and H fit. This is an observable partition. The H absorption fit
edge remains **13.6 eV**. The separate D gate remains **13.602134599702 eV** and
uses the original threshold-gated H-equality approximation.

## Positive omitted-tail estimate

In the core, every birth energy is below the D gate and decreases, so D opacity
vanishes exactly under the unchanged archived gate. The whole sub-H interval
can extend beyond D at birth; that part is handled by a positive tail estimate.
The change of variable from `X` to instantaneous energy gives

\[
\tau_H(E_b)=\int_{13.6}^{E_b}
 \frac{c\,n_{HI}(X(E))}{H(X(E))q(X(E))}\frac{\sigma_H(E)}{E}\,dE.
\]

On the actual small support, `sigma_H(E)/E` decreases. This follows directly
from the archived H Verner algebra: with `x=E/E0>1` and exponent `p`,

\[
\frac{d\ln(\sigma_H/E)}{d\ln E}
=\frac{2x}{x-1}+\frac p2-6.5
-\frac p2\frac{\sqrt{x/y_a}}{1+\sqrt{x/y_a}}<0.
\]

The code checks a negative upper bound obtained by dropping the last,
nonpositive term. It obtains PCHIP neutral-H extrema at cubic stationary
points and uses the largest allowed dilution. Thus, conditional on the
explicit polynomial-extrema ranges,

\[
\Lambda_{\min}=
\frac{c\,n_{HI,\min}}{H_{\max}q_{\max}}
\frac{\sigma_H(U_{\max})}{U_{\max}}>0,
\qquad \tau_H(E_b)\geq\Lambda_{\min}(E_b-13.6).
\]

The retained core ends at the smaller of `U_r` and
`13.6 + 32/Lambda_min`. The code requires the latter to be below D. Energy
panels use optical-depth coordinates `0,2,6,14,30,32` and the binding observable
cut, with GL6, GL8 or GL12 on each panel.

Because `g` decreases on this cell and D opacity is nonnegative, a tail energy
interval `[a,b]` contributes a nonnegative amount bounded above by

\[
\frac{C_r}{Z}g(13.6)
\frac{e^{-\Lambda_{\min}(a-13.6)}
      [-\operatorname{expm1}(-\Lambda_{\min}(b-a))]}{\Lambda_{\min}}.
\]

This is accumulated separately for the two binding subcomponents and their
sum. It includes possible D-active tail energies conservatively. It is not
added as if it were a measured survivor correction. The numerical core and
tail upper bound are separate output fields.

The extrema implementation uses binary64 polynomial roots plus an explicit
`2e-11` padding. It does not use directed rounding. The analytic inequalities
are **DERIVED conditionally**; the reported floating values are
**NUMERICALLY_CHECKED**. The tail upper bound does not enclose numerical core
quadrature error, interpolation error against the true IVP, or nonlinear
opacity feedback.

## Executed checks and finite comparisons

Actual results are recorded in the JSON and test receipt when executed. The
planned settings are tight13 `(energy,time)=(6,16),(8,16),(12,16),(12,24)` and
standard18 `(12,24)`. Finite differences do not establish a continuum order or
a Richardson error bound. PCHIP is piecewise cubic with limited smoothness;
neither global high derivatives of the response nor nonlinear feedback bounds
are supplied by these finite samples.

Portable commands from this directory:

```bash
python -m unittest -v test_postloss_fixed_gas_optical_response.py
python postloss_fixed_gas_optical_response.py \
  --source-root /ABSOLUTE/RESTORED/run13/recovered \
  --output /ABSOLUTE/NEW_OUTPUT/FIXED_GAS_OPTICAL_RESPONSE.json
```

The output path must not already exist. The receipt includes exact arguments,
execution environment, all read input hashes, source hash, actual numerical
checks and finite results. Native IVP calls remain zero.

## Existing DAG continuation

`P4-S4C-SPECTRAL-EDGE-SUPPORT` remains incomplete. This unit isolates a finite
prescribed-gas continuous-energy response and its binding-bin classification;
the next unresolved work is control of the actual coupled gas path and
nonlinear spectral feedback, together with a trustworthy spectral error
enclosure. It does not change the original 45-node or 26-node DAG. Continuous
spectral refinement, angular and birth-time continua, whole donor domain,
full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, and Li/Be plus
nuclear T1-T8 remain obligations.
