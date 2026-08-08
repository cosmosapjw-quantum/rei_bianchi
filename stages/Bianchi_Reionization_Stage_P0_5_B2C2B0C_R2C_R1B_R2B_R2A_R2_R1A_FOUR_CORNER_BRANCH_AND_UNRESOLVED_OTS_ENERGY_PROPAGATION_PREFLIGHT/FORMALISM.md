# Four-corner branch and unresolved-OTS propagation formalism

## 1. Scope and conventions

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B` remain explicit. The background is homogeneous. This stage changes no Bianchi geometry equation, owner law, MPRK22(1) coefficient, Alexander-SDIRK2 coefficient, material-state definition, or photon/energy ownership equation.

The node state is

\[
Y_i=(N_{\rm HI},N_{\rm HII},N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII},U)_i,
\]

with

\[
N_{\rm HI}+N_{\rm HII}=N_H,
\qquad
N_{\rm HeI}+N_{\rm HeII}+N_{\rm HeIII}=N_{\rm He}.
\]

## 2. Branch policies

The He III cascade coefficients are

\[
A_H=v[(\ell-m)+my]+(1-v)fz,
\]

\[
A_{\rm HeI}=vm(1-y)+(1-v)f(1-z),
\]

where `ell=57/40`, `m=737/1000`, `0<=y,z<=1`, and `f in [0.1,1]`.

For each node:

- below `10^4 K`, strict policies use `v=0` and `v=1`;
- inside the Hummer--Seaton table, strict policies use the two bracketing table values;
- named log-linear policies are auditors only;
- `T>10^5 K` is a branch-domain failure.

With `f=0.1` and `f=1`, this gives four strict policies and four adapter auditors per shape lane.

## 3. Instantaneous multi-affine theorem

For fixed state-dependent `y,z`, each branch coefficient is affine in `v` for fixed `f` and affine in `f` for fixed `v`:

\[
\partial_v^2 A_s=0,
\qquad
\partial_f^2 A_s=0.
\]

Hence on a fixed rectangle `[v_-,v_+] x [f_-,f_+]`, the instantaneous coefficient is the bilinear interpolation of the four corner values with nonnegative weights. Its instantaneous minimum and maximum are therefore attained at corners.

This theorem does not automatically extend to the nonlinear flow map

\[
\Phi_{\Delta t}: (Y_0,v(\cdot),f(\cdot))\mapsto Y(\Delta t),
\]

because the rates, table cell, thermal state, and owner distribution evolve.

## 4. Event-resolved material and energy update

The locked 26-event graph supplies nonnegative production--destruction fluxes to MPRK22(1). Exact He II Ly-alpha excess energy enters resolved heat once. Unidentified two-photon and free-bound first moments remain in `E_OTS_unres`; escaped Ly-alpha enters `E_escape`.

For each event,

\[
\Delta E_\gamma+\Delta E_{\rm chem}+\Delta U_{\rm res}
+\Delta E_{\rm OTS}^{\rm unres}+\Delta E_{\rm escape}=0.
\]

No unidentified energy is set to zero and no unresolved energy is injected into the resolved thermal state.

## 5. Numerical gate

For every policy, one full step and two half steps are evaluated at partition 2048. The blockwise error is measured in

\[
x_{\rm HII},\quad x_{\rm HeII},\quad x_{\rm HeIII},\quad \ln T,
\]

and must satisfy

\[
\epsilon_{\rm local}<2\times10^{-4}.
\]

The strict-corner state width has a separate source-model threshold

\[
\max \operatorname{width}(x_s),\ \max\operatorname{width}(\ln T)<2\times10^{-3}.
\]

## 6. Missing continuous-family certificate

Let `theta` denote all admissible branch choices. A load-bearing certificate must enclose the differential inclusion

\[
\dot Y\in\{F(t,Y,\theta):\theta\in\Theta(t,Y)\}.
\]

Corner calculations alone are sufficient only if a suitable monotonicity cone is proved or a validated interval/Taylor-model integrator encloses the entire set. Neither result is inherited from the instantaneous multi-affine identity. This is the sole remaining blocker identified by the stage.

## 7. Units and dimensions

- event rates and source rates: `s^-1` after normalization or particles `cm^-3 s^-1` before normalization;
- number ledgers: particles `cm^-3` or locked comoving density units;
- energy rates: `erg s^-1` per locked parcel measure;
- integrated energies: `erg` in the same parcel convention;
- `x_s`, `v`, `f`, and local-error fractions: dimensionless;
- `ln T` width: dimensionless.
