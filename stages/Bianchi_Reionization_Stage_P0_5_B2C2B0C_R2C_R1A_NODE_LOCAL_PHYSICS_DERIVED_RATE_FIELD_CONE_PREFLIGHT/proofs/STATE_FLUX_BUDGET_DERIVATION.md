# R2C-R1A state–flux–budget derivation

## Conventions and dimensions

Metric and tetrad conventions are inherited but do not enter this homogeneous
local chemistry proof.  No natural-unit convention is used.

- `M=N_HI+N_HII`, `N=N_HI`, `I=N_HII`: H nuclei per comoving Mpc^3.
- `U=(3/2) k_B M T`: erg per comoving Mpc^3.
- `J_g`: absorbed photons, equivalently primary H photoionization events, per
  second per comoving Mpc^3.
- `Gamma_g`: photoionization rate per neutral H atom, s^-1.
- `alpha_B n_e` and `beta_HI n_e`: recombination and collisional-ionization
  rates, s^-1.
- `S_+`, `S_-`: H-nucleus inflow and outflow, s^-1 cMpc^-3.

Thus every term in `dot N` and `dot I` has units s^-1 cMpc^-3.

## 1. Minimal H chemistry generator

Let

\[
 u(t)=\sum_g\Gamma_g(t)+\beta_{\rm HI}[T(t)]n_e(t)\ge0,
 \qquad
 r(t)=\alpha_B[T(t)]n_e(t)\ge0.
\]

For fixed mass and without transfer,

\[
 \frac{d}{dt}
 \begin{pmatrix}N\\I\end{pmatrix}
 =
 \underbrace{
 \begin{pmatrix}-u&r\\u&-r\end{pmatrix}}_{A(t)}
 \begin{pmatrix}N\\I\end{pmatrix}.
\]

`A` is Metzler: both off-diagonal entries are nonnegative.  Its column sums
vanish, so `d(N+I)/dt=0`.  At the boundary `N=0`, `dot N=rI>=0`; at the
boundary `I=0`, `dot I=uN>=0`.  Hence the nonnegative orthant is forward
invariant and `0<=I<=M` follows from H-nucleus conservation.

For constant `u,r`,

\[
 x(t)=x_{\rm eq}+[x(0)-x_{\rm eq}]e^{-(u+r)t},
 \qquad x_{\rm eq}=\frac{u}{u+r}\in[0,1].
\]

This is the physical exponential relaxation used by C2-Ray: the *ionization
fraction* relaxes under reaction rates.  It does not imply that every derived
flux or interval budget is an independently relaxing state.

## 2. Transfer terms preserve the cone

For nonnegative inflow/outflow rates and incoming ionized fraction
`0<=x_in<=1`, write

\[
 s_{\rm in}=S_+
 \begin{pmatrix}1-x_{\rm in}\\x_{\rm in}\end{pmatrix},
 \qquad \lambda_{\rm out}=S_-/M\ge0.
\]

Then

\[
 \dot y=[A(t)-\lambda_{\rm out}(t)\mathbf1]y+s_{\rm in}(t),
 \qquad y=(N,I)^T.
\]

The off-diagonal entries remain nonnegative and the source is nonnegative;
therefore positivity is preserved.  Summing the two equations gives

\[
 \dot M=S_+-S_-.
\]

## 3. Photon current is an algebraic RT flux

Photon conservation gives

\[
 J_g(t)=\Gamma_g(t)N(t)\ge0,
\]

or, in a finite photon-conserving cell, the corresponding time-averaged
relation between absorbed photon count, time-averaged neutral population and
time-averaged photoionization rate.  `J_g` is therefore a reaction flux coupled
to the radiation field, not a material reservoir with its own scalar
relaxation equilibrium.

The locked current-Gamma representation `J_g=Phi_g kappa_g` is an equivalent
algebraic closure at each inherited endpoint.

## 4. The old cycling quantity is an interval budget, not a state

The inherited gate defined

\[
 C_{\Delta t}=\frac{N_{\rm HI,start}}{\Delta t}+\bar R_{\rm rec}.
\]

It has rate units, but depends explicitly on the chosen interval.  At fixed
physical state and recombination rate, refinement `Delta t -> Delta t/q`
gives

\[
 C_{\Delta t/q}=q\frac{N_{\rm HI,start}}{\Delta t}+\bar R_{\rm rec},
\]

so

\[
 C_{\Delta t/q}-C_{\Delta t}=(q-1)\frac{N_{\rm HI,start}}{\Delta t}.
\]

Unless the neutral inventory vanishes, `C` is not refinement invariant and
cannot be an autonomous state coordinate.  The quantity with invariant
meaning is the integrated budget

\[
 B_{\Delta t}=\Delta t\,C_{\Delta t}
 =N_{\rm HI,start}+\Delta t\,\bar R_{\rm rec}.
\]

It is a necessary whole-interval photon-count bound under the assumptions of
the original gate.  It is not a pointwise node state and must not be evolved
independently of `N` and `I`.

## 5. Exact cumulative photon ledger

With group-summed primary photoionization current `J=sum_g J_g`, collisional
ionization `Q_coll=beta n_e N`, recombination `R_rec=alpha_B n_e I`, and
neutral transfer components

\[
 S_{N,+}=(1-x_{\rm in})S_+,
 \qquad S_{N,-}=(1-x)S_-,
\]

the neutral equation is

\[
 \dot N=-J-Q_{\rm coll}+R_{\rm rec}+S_{N,+}-S_{N,-}.
\]

Therefore the photon count over `[t_0,t_1]` obeys

\[
 \boxed{
 \int_{t_0}^{t_1}J\,dt
 =N(t_0)-N(t_1)
 -\int Q_{\rm coll}dt
 +\int R_{\rm rec}dt
 +\int S_{N,+}dt
 -\int S_{N,-}dt .}
\]

This cumulative identity, together with nonnegative group currents and the H
reaction generator, replaces the artificial pointwise cone
`J_G1+J_G2a<=C(t)`.

## 6. Why the 497 R2C-R1 Farkas certificates are not physical no-go theorems

The common-equilibrium surrogate used

\[
 y_1=y_{\rm eq}+(y_0-y_{\rm eq})e^{-k\Delta t},
\]

so

\[
 y_{\rm eq}=y_0+\frac{y_1-y_0}{1-e^{-k\Delta t}}.
\]

For finite positive `k Delta t`, the multiplier
`1/(1-e^{-k Delta t})` is greater than one.  The inferred equilibrium is an
*extrapolation beyond the target endpoint*, not a point on the endpoint
segment.  It can leave a convex physical cone even when both endpoints and a
positive path between them are admissible.

- 491 certificates involve `C` or independently relaxed `J_g`; those
  coordinates are not independent material states.
- The remaining six mass-cap certificates occur although both mass endpoints
  lie below the locked cap.  Their straight convex segment also lies below the
  cap; only the extrapolated common equilibrium violates it.

Consequently the certificates validly reject the common-equilibrium
surrogate, but they do not establish that the inherited endpoints lack a
physical photon-conserving history.

## 7. Scope boundary

This derivation removes the *structural Farkas blocker*.  It does not identify
the interior radiation forcing or certify a production temperature history.
The next bounded task must determine a nonautonomous photon-conserving
`Gamma_g(t)`/flux history, close the cumulative ledger at every macro and
substep, and retain a separate thermal accuracy gate.
