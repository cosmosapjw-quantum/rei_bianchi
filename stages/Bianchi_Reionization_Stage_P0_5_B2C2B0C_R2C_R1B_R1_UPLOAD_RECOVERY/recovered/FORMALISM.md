# R2C-R1B-R1 canonical RT input-extraction formalism

## 1. Scope and conventions

This stage extracts and locks the inputs required by a later photon-conserving nonautonomous RT–chemistry fixed point. It does **not** integrate or promote a production node chemistry history.

The metric convention is \((- + + +)\), \(\epsilon_{123}=+1\), and \(c\), \(\hbar\), and \(k_B\) remain explicit. Photon groups are

\[
G_1=[13.6,24.59),\quad G_{2a}=[24.59,39.5],\quad
G_{2b}=(39.5,54.42),\quad G_3=[54.42,100]\;{\rm eV}.
\]

Species support is exact:

- H I: \(G_1,G_{2a},G_{2b},G_3\);
- He I: \(G_{2a},G_{2b},G_3\);
- He II: \(G_3\);
- every below-threshold contribution is exactly zero.

## 2. Canonical time-resolved global forcing

R1B showed that endpoint values plus one interval integral do not identify an interior forcing. R1B-R1 therefore does not interpolate endpoints. It reopens the canonical B2C2A-R1 BDF dense solution and samples the already solved trajectory at nine predeclared Chebyshev–Lobatto nodes in each of the ten reduced-DAE substeps,

\[
\xi_k=\frac{1-\cos(k\pi/8)}{2},\qquad k=0,\ldots,8.
\]

The extracted variables include all four photon groups and the direct group-boundary transport information present in the dense solution. A shape-preserving PCHIP representation is used only as an adapter to evaluate the existing dense solution at the locked nodes. It is not an added dynamical ansatz. A Simpson-versus-dense quadrature audit checks that the locked representation preserves the canonical interval measures.

## 3. State-derived opacity measure

For node \(i\), macro state \(m\), group \(g\), and time \(t\), define the nonnegative absorption measure

\[
 h_{img}(t)=w_i L_i\sum_{s\in\{\mathrm{HI,HeI,HeII}\}}
 n_{s,i}(t)\,\bar\sigma_{s g},
\]

where \(w_i\) and \(L_i\) are inherited fixed node measure/column factors and \(\bar\sigma_{sg}\) is the group-averaged Verner photoionization cross section under the locked within-group photon-number spectrum. This stage never defines opacity by \(\kappa=J/\Phi\), never changes cloud mass to match opacity, and never clips a node.

When node-resolved helium states are absent, the canonical dense global \(x_{\rm HeII}(t)\) and \(x_{\rm HeIII}(t)\) histories are disintegrated over the already fixed node mass measure. Hydrogen ionization is not used as a helium proxy.

## 4. Conditional uniqueness of the macro-to-node disintegration

Let \(\kappa_{mg}(t)\) and \(J_{mg}(t)\) be inherited independent macro moments. R1B-R1 imposes four predeclared conditions within each macro/group/time slice:

1. nonnegative node opacity and current;
2. locality: zero absorption measure receives zero allocation;
3. one incident group flux \(\Phi_{mg}=J_{mg}/\kappa_{mg}\) across the unresolved macro state;
4. absolute continuity with a common Radon–Nikodym derivative relative to \(h_{img}\).

These conditions give the unique allocation

\[
 \kappa_{img}=\kappa_{mg}\frac{h_{img}}{\sum_j h_{jmg}},\qquad
 J_{img}=J_{mg}\frac{h_{img}}{\sum_j h_{jmg}}
 =\Phi_{mg}\kappa_{img}.
\]

The uniqueness claim is conditional on the four stated physical conditions; it is not a theorem that arbitrary unresolved radiation fields have a unique disintegration. All three inherited shape lanes remain separate systematic lanes. No lane is selected after seeing the result.

## 5. Atomic and spectral moments

For the locked photon-number spectrum \(n_E\propto E^{-2.5}\),

\[
 \bar\sigma_{sg}=
 \frac{\int_{G_g\cap[E_{{\rm th},s},\infty)} dE\,E^{-2.5}\sigma_s(E)}
 {\int_{G_g\cap[E_{{\rm th},s},\infty)} dE\,E^{-2.5}},
\]

and the optically thin absorbed excess-energy moment is

\[
 \bar\epsilon^{\rm thin}_{sg}=
 \frac{\int dE\,E^{-2.5}\sigma_s(E)(E-E_{{\rm th},s})}
 {\int dE\,E^{-2.5}\sigma_s(E)}.
\]

The optical-depth-dependent moment replaces \(\sigma_s(E)\) by the absorbed fraction \(1-e^{-\tau_{sg}\sigma_s(E)/\sigma_{\rm ref}}\). Thin and thick limits are retained as hard envelopes.

## 6. Thermal forcing lock

The canonical B2C2A-R1 dense thermal history is used to select the otherwise underidentified hardening coordinate. If group-resolved heating is present, each group moment is calibrated directly. Otherwise one shared, predeclared hardening coordinate is solved at each locked time from the total dense thermal forcing. The monotonic branch is selected before examining node histories; a root outside the thin–thick envelope is a fail-closed condition.

Photon-number and energy ledgers remain distinct. The later fixed-point stage must assign photoheating, atomic cooling, expansion work, and mass-transfer work exactly once.

## 7. What has and has not been resolved

Resolved here:

- canonical interior global forcing from the original BDF dense trajectory;
- all-four-group boundary/absorption forcing on locked time nodes;
- a state-derived, moment-preserving dynamic opacity **shape**;
- a conditional unique macro-to-node Radon–Nikodym disintegration;
- optical-depth-dependent group heating moments calibrated to the dense thermal history;
- exact species thresholds and structural zeros.

Not yet performed:

- photon-conserving nonautonomous RT–chemistry fixed-point iteration;
- production node history promotion;
- unresolved subtraction, front/\(Q_M\), source/\(f_{\rm esc}\) calibration;
- primordial-recombination adapter or surrogate;
- CAMB transfer or Bianchi feedback.
