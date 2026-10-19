# Native VigilODE Radau continuation: equations and scope

Scientific owner: `/root` (Astra), 2026-10-19. This is the independent LRS V14 continuation, separate from production v3/rux and the BASS/age-reference lanes. `CONTRACT.md` specifies the finite numerical experiment. The two independent reviews and actual command receipts are separate evidence.

## 1. What is being integrated

The chemical substep integrates the **existing native reconstructed photon-moment system and four gas variables together**. Geometry, moment support, and affine scales are frozen within that substep; the positive quadrature closure is reconstructed from the current moments on **every** RHS call and finite-difference perturbation. Source jumps occur at the existing physical GL2 birth endpoints, between chemical segments. This does not substitute a frozen initial radiation field for the coupled system.

The solver is the actual public `radau_step` from VigilODE commit `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, using its 3-stage Radau IIA tableau, modified Newton implementation, work counters, and faer-backed pivoted LU. Its returned stage increments solve `K_i = h f(Y_i)`, with `Y_i = y_0 + sum_j A_ij K_j`. They are not the stage displacements themselves. A real finite-difference Jacobian is provided. The generic ODE API is not being treated as a continuous-error certificate.

The base native source is the prior SSPRK2 publication `339dab4336d1fcfd38106640ee9bf7056dabcfd8`, reached through PR198 HEAD `fa9615a565a10a770eb1768d8f10cd503b0e1336`. The original 152 files and the full original covariant-transport prefix are preserved; the new public derivative API is one child module with an appended hook. Default/adaptive/checkpoint, MD14, Verner, Grackle, and EOS ownership stays in the existing code.

## 2. Photon and gas units

Let `n_l` be photons per total H at a native quadrature node, `q_l` its reference energy, and `epsilon_l = r_ray q_l` its proper energy. Only in isotropic geometry is `r_ray = a_ref/a`. Angular weights are already in `n_l`. With species order HI, HeI, HeII,

\[
\kappa_{\ell s}=c\,n_{{\rm abs},s}\sigma_s(\epsilon_\ell),\qquad
P_s=\sum_\ell\kappa_{\ell s}n_\ell,
\]
\[
\dot N_c=-\sum_{\ell\in c,s}\kappa_{\ell s}n_\ell,\qquad
\dot U_c^{\rm ref}=-\sum_{\ell\in c,s}q_\ell\kappa_{\ell s}n_\ell.
\]

The provider receives absorber-normalized photo rates `Gamma_s = c n_H sum_l sigma_s n_l`, and excess-energy heating in erg/absorber/s. The independent node sum yields events/H/s and eV/H/s. The native thermal state is erg/H, so its derivative is divided by `ev_erg` once; volume event rates and cooling rates are divided by `n_H` and `n_H ev_erg`, respectively.

Binding uses native ionization energies `(13.598434599702, 24.587389011, 54.41776)` eV. The rounded Verner fit partition boundaries are not replacements for these constants.

Set `Y = n_He/n_H = 0.2454/[4(1-0.2454)] = 1227/15092`. For raw photoionization, collisional ionization, radiative recombination, and HeII dielectronic recombination events `(P,C,R,D)`, all per H, define `v_s = P_s+C_s-R_s`. Then

\[
\Delta x=v_H,\qquad Y\Delta y=v_{HeI}-D-v_{HeII},\qquad Y\Delta z=v_{HeII},
\]
\[
e=x+Y(y+2z),\qquad \Delta e=\sum_s v_s-D,
\]
\[
B=\chi_H x+Y[\chi_{HeI}y+(\chi_{HeI}+\chi_{HeII})z],\quad
\Delta B=\chi\!\cdot\!v-\chi_{HeI}D.
\]

These equations also apply to instantaneous rates. Let `Q_rad` be CE plus RR kinetic cooling plus DR kinetic cooling plus FF. The unchanged provider gives

\[
\dot w=Q_{\rm photoheat}-\chi\!\cdot\!C-Q_{\rm rad}+Q_{\rm CMB},
\qquad
\dot E_{\rm escape}=Q_{\rm rad}+\chi\!\cdot\!R+\chi_{HeI}D.
\]

CMB is signed, positive into gas. CI transfers thermal energy into binding; capture binding and RR/DR kinetic cooling remain separate. In a chemical segment the provider receives mean expansion rate zero. The existing geometry maps already account for thermal and photon work. Hence

\[
\Delta(w+B)+E_{\rm escape}+W_{\rm gas}-E_{\rm CMB}
=Q_{\rm photoheat}+P_{\rm binding},
\]
\[
\Delta(E_\gamma+w+B)+E_{\rm escape}+W_{\rm gas}+W_\gamma-E_{\rm CMB}
=E_{\rm source}
\]

for a complete split interval, with source and work measured by the native birth and geometry operations. At fixed geometry, photon absorption supplies `-dot E_gamma = Q_photoheat + chi.P`. These are accounting identities, not time-accuracy proofs. Independent Wolfram and rational-coefficient checks returned zero event coefficients; they are algebra checks, not new manufactured histories.

## 3. Affine coordinates and what conservation actually implies

For each occupied nonzero-width photon cell, freeze `S>0`, lower support `q_L`, and width `dq>0`, and use

\[
u=N/S,\qquad v=(U^{\rm ref}-q_LN)/(\Delta q S),\qquad 0\le v\le u.
\]

The offset derivative is summed directly with `(q_l-q_L)` node weights. It is not recovered by subtracting two large forward-Euler updates or two large energy derivatives. Point support needs only number; exactly empty cells can be omitted during a source-free segment because their derivative is exactly zero. Each segment after a source birth constructs a fresh occupied set, support layout, and scales.

Write the physical decoder as `Z=Z_*+D theta` and a linear physical invariant plus its event ledger as `I=L Z+J`, `dot J=g`. Define

\[
\rho=\theta_1-\theta_0-\sum_i b_iK_i,\quad
r_i=K_i-hf(\Theta_i),\quad
\eta_i=L\mathcal D f(\Theta_i)+g_i.
\]

If event ledgers are accumulated from the actual reconstructed Radau stages with the **same** accepted `h` and weights `b_i`, then

\[
\boxed{\Delta I=L\mathcal D\rho+\sum_i b_iL\mathcal D r_i+h\sum_i b_i\eta_i.}
\]

The implementation reports all three terms and the remaining binary64 decoder/accumulation mismatch. A small library WRMS is insufficient: the maximum scaled component stage residual and returned-endpoint closure are independently recomputed. The six linear audits cover photon number, HII, helium charge states, electron number, and total photon+thermal+binding energy. The subsequent raw analysis must also rebuild the separate event/binding/thermal/escape/source/work accounts; a supplied zero `energy_residual` is not accepted as proof.

The passive ledger variables need not increase the dense Newton dimension because they do not feed back into the physical RHS. Shared-stage quadrature is exactly the corresponding augmented Runge–Kutta update. Native calls used by finite differences and stage replay are counted, including failed attempts. A failed candidate cannot commit state or accumulated physical ledgers.

## 4. Stability is insufficient for native stage admissibility

For scalar absorption `y'=-k y`, `tau=h k`, the actual Radau tableau gives

\[
R(-\tau)=\frac{3(20-8\tau+\tau^2)}{60+36\tau+9\tau^2+\tau^3},
\]
\[
\frac{Y_2}{y_0}=\frac{6[50+(10-5\sqrt6)\tau+(1-\sqrt6)\tau^2]}
{5(60+36\tau+9\tau^2+\tau^3)}.
\]

The endpoint is positive and below its initial value for positive tau, but the second stage becomes negative for `tau>5.14892565376694...`. At tau=10 the stages are approximately `(0.319356963,-0.060736273,0.051724138)y_0`. This is an exact scalar tableau counterexample to unconditional stage positivity, not a universal nonlinear CFL boundary or a new native cosmological case.

The pinned Newton code aborts on a trial callback domain error. Therefore an observed failure may arise from intrinsically inadmissible converged stages or from a Newton path leaving the domain; the two causes must be distinguished. Finite-difference one-sided fallback is allowed only for an explicitly invalid perturbation. Nonfinite derivatives, preparation/provider faults, and budget failures remain fatal. A valid one-sided direction does not always exist at a simultaneous abundance/EOS boundary.

## 5. Accuracy and cost questions to resolve with the finite runs

Radau IIA3 has formal order five on a sufficiently smooth, regular fixed-geometry ODE solved accurately. This is not a fifth-order claim for the geometry/birth composition, the general nonlinear native system, or a uniformly stiff family. The native moment closure and physical domain must be examined in the actual finite runs.

The preregistered bounded matrix is 7 fixed-geometry and 12 chronological GL2 histories: Radau N=2,4,8,16 and SSPRK2 N=8,16,32 for the seeded fixed problem, then Radau/SSPRK2 N=4,8,16 for both source-on and seeded source-disabled GL2 at Delta ln a=1e-6. The first N=4 gate is replayed after the concrete FD classification repair and exact source freezing; the replay is the same unique setting. The intended per-case budget was 200,000 native RHS calls and 30 seconds, with a 180-second total incremental native wall limit. Actual enforcement is 200,000 RHS for both methods, an internal 30-second clock for Radau, and external process timeout at most 40 seconds; SSPRK has no internal wall check. The final portable runner also caps process timeout by the remaining total budget. Every observed case was below two native seconds, so no measured case reached these limits. Failures remain failures and are not silently subcycled.

Finest Radau can be used only as an empirical discrete-system comparison when its own refinement supports that use. Report self differences, cross-method absolute differences, signed CMB and channel magnitudes, and the cancellation floor for small HeIII changes. Compare RHS counts including FD/replay, LU/Newton counts, solver wall, and process wall as distinct scopes. No speedup is inferred merely from selecting faer or an implicit method.

## 6. References and retained evidence

- `vigilode_intake/VIGILODE_NATIVE_API_AND_RUST_PACKAGES.md`: exact source/API and official Rust-package investigation; full source/cache identities in its receipts.
- `theory/WOLFRAM_CHECK.wl`, `theory/WOLFRAM_RAW.json`: root exact event/tableau calculations and raw tool outcome.
- `theory/SCISPACE_DISCOVERY.json`: literature discovery only; no imported abstract is used as a proof of this implementation.
- `theory_review/INDEPENDENT_THEORY_REVIEW.md` and companions: independent native units, event algebra, stage residual and positivity derivations, with 11 actually read source hashes.
- `c9_code/`: fresh independent implementation/receipt review and concrete FD error-classification finding.

Neither this derivation nor the small matrix admits source-on overall second order, uniform stiff accuracy, Case B, full EoR, or signed Bianchi without their own evidence. The prior 76 manufactured problems and Python57 checks are not counted again.
