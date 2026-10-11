# C11 pinned-provider endpoint trace contract

Status: explicit one-sided **value** trace is implemented and locally checked. Conversion of a rounded moment state into an endpoint distribution and an endpoint Jacobian remain unimplemented and fail closed. Existing C10 bytes and admission guards are unchanged.

## Source-owned definition

The primary authority is `rust/rei_microphysics/src/atomic_provider.rs`, `AtomicProvider::cross_section`, called by the hash-pinned N1 native `SIGMA` protocol. This source uses the Verner outer-shell fit and the strict branch `E < E_th -> 0`; at equality it evaluates the active fit. It rejects energies above 50000 eV. The wrapper also requires a positive energy. Source and binary hashes are in `endpoint_trace.py` and `STATUS.json`; this derivation is source based and needs no new literature model or provider substitution.

For species s,

\[
\sigma_s(E)=\begin{cases}0,&E<E_{t,s},\\f_s(E),&E\ge E_{t,s},\end{cases}\quad
f_s(E)=10^{-18}\sigma_{0,s}[(x-1)^2+y_w^2]\,y^{p/2-5.5}(1+\sqrt{y/y_a})^{-p},
\]
\[
x=E/E_0-y_0,\quad y=\sqrt{x^2+y_1^2}.
\]

All fitted factors are continuous and finite on each active domain. Native `SIGMA(E_t)` is therefore the actual evaluation of the right trace. The left trace is exactly the source-defined zero branch. Native values of the other two species are retained, with their own threshold sides.

| Native energy | Left trace | Right trace |
|---|---|---|
| Exact species threshold 13.60, 24.59 or 54.42 eV | Zero for that species | Actual native `SIGMA(E_t)` value |
| Smooth point strictly inside (0, 50000) | Actual native value | Actual native value |
| 50000 eV provider maximum | Actual native value | Outside provider domain; reject |
| Nonpositive or above-cap energy | Reject | Reject |

`native_trace(opacity, energy_ev, side)` returns an immutable `NativeValueTrace`. It calls the existing native binary at the **unchanged declared binary64 energy**, with no adjacent-float, extrapolation, threshold nudge, or duplicated fit implementation. Source SHA checks make the zero/continuity reasoning fail closed if the controlling source changes. For lower weak support limits use the right trace; for upper weak support limits use the left trace, only after the caller establishes the physical endpoint identity.

## Why a trace value does not admit a rounded endpoint

A power-law closure with an exact lower mean has the mathematical weak limit `N delta(q-a)`; an exact upper mean has `N delta(q-b)`. Its opacity limits are `K0 = N c sigma_side(R q*)` and `KE = R q* K0`. These are value limits, not an interior covariance Jacobian. The map from two moments to a delta at the cone boundary has no Jacobian supplied by this work.

A binary64 expression `(U/N)/R == a` does **not** establish that the physical moment was exactly at the endpoint. It may erase a small positive `Q-aN`. Similarly `float(R*q) == E_t` does not prove exact physical threshold coincidence. Before using a trace in a production moment operation, the caller must retain the exact endpoint/side provenance or authoritative low moment components. If that information is missing, reject the state. This adapter deliberately accepts only an explicitly identified energy; it does not take a `CellSpectrum`, rewrite a mean, erase a low component, bypass the old coordinate indicator, or create a seed.

The following are separate and remain unpromoted:

1. Inverting a compensated interior moment while retaining its low part.
2. Controlling moment/quadrature errors and the direct and ABI photoheat components.
3. Proving a support endpoint is an exact physical weak limit rather than roundoff.
4. Providing an endpoint Jacobian or a restart law for such a distribution.

## Provider-specific coordinate sensitivity

A useful mathematical bound concerns only the **smooth active value**; it is not a quadrature certificate or a reason to drop reconstruction guards. Set `A=(x-1)^2+y_w^2` and `s=sqrt(y/y_a)`. Differentiation gives

\[
{d\log f\over d\log E}={E\over E_0}\left[
{2(x-1)\over A}+(p/2-5.5){x\over y^2}-{p\over2}{x\over y^2}{s\over1+s}\right].
\]

For HI and HeII, `y=x=E/E0>1` and the absolute-value bound is

\[
L_\sigma\le {2E_t\over E_t-E_0}+5.5<7.566.
\]

For HeI the source parameters have `x>1`, `y_w>0`, `y_1>0`. Using
`2u/(u^2+y_w^2) <= 1/y_w`, `x/(x^2+y_1^2) <= 1/(2 y_1)` and `s/(1+s)<1` gives

\[
L_\sigma\le2+{1+y_0\over y_w}+5.5\left(1+{y_0\over2y_1}\right)<8.779.
\]

Thus 8.8 is a conservative common bound for same-branch energy-coordinate sensitivity over each active threshold to 50000 eV. For two same-branch energies, relative fit variation is bounded by `expm1(8.8*abs(log(E2/E1)))` in exact arithmetic. This does not bound native floating transcendental evaluation error. A crossing of a threshold has a finite jump and is outside this bound.

For direct heat kernel `(E-chi_s)*sigma_s(E)`, chemical chi remains distinct from sigma thresholds, and

\[
L_{\mathrm{heat},s}\le L_{\sigma,s}+{E\over E-\chi_s}
\le L_{\sigma,s}+{E_{t,s}\over E_{t,s}-\chi_s}.
\]

A common conservative bound is 24304. The small difference must still have its own error scale, and direct and ABI difference heat must agree under the frozen 1e-7 local criterion. This derivative bound does not certify subtraction error in `KE-chi*K0`, moment reconstruction, or cumulative energy conservation.

## Time-control integration

For a continuous cell distribution, moving a sigma threshold through its support changes the integrated rate continuously. The threshold is a spatial/energy quadrature split at every evaluation; it is not automatically a hard step boundary. Active-support or source-band branch changes and source interpolation knots can remain the caller's declared time events. A physical delta crossing a threshold can jump; that endpoint distribution is not admitted here. Occupied support above 50000 eV is always rejected.

A production attempt can retain explicit endpoint failure as a stop condition while evolving verified strict-interior states. This lane does not give a production GO. If a changed run actually reaches a rounded endpoint, a threshold-equal quadrature node without side provenance, or above-band support, preserve the first rejected candidate and checkpoint the last accepted boundary. Do not move the node or time to evade rejection.

## New evidence only

Five new trace-semantics tests passed, covering all three threshold sides, native cap-side refusal, invalid inputs, non-native-provider refusal, and value-only metadata. They make eight actual native calls and zero gas RHS calls. The missing-module RED and first integration-path failure are retained; the final test run passed after correcting only the new module search path. No C3, old native suite, old opacity, old source scan, C10 coupled family, or old checkpoint test was rerun.

These tests establish the new adapter's branch behavior under the actual pinned binary. They are not a new independent accuracy validation of the Verner fit, a physical endpoint-closure test, or a full-history reionization result.
