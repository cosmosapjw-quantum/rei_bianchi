# Independent review: V14 frozen reconstruction diagnostic

Review date: 2026-10-19 UTC. Reviewer: separate scientific-review subagent.

## Verdict and scope

**PASS_SCOPED** for the conditional local-defect derivation, its mapping to the existing native photon transport, and the new frozen-gas diagnostic. The source is an additive diagnostic that calls the native public reconstruction and exponential-attenuation paths. Its actual saved outputs show a broad-spectrum local defect approaching order two in step size and finite-horizon self-differences approaching order one. The delta control closes to floating-point accuracy.

This establishes the reconstruction mechanism in the prescribed frozen problem. Its quantitative contribution to the previously completed 84 coupled cosmological histories remains **unresolved**. In particular, this review does not attribute all of their temperature error to reconstruction, or promote source-on second order, uniform stiff accuracy, Case B, full EoR, or signed Bianchi claims.

The reviewer read the native and diagnostic source, build/run logs, execution receipt, and both CSVs, and recomputed the reported differences from the saved CSV. The reviewer did not rerun the binary, alter native source, rerun the old campaign, or create additional toy problems.

## Inputs and identity

Paths below are relative to `/workspace/scratch/6af5e9e6c737/v14_work/` unless stated otherwise.

| Input | SHA256 |
|---|---|
| `native_baseline/rust/rei_microphysics/src/axbi_driver.rs` | `fd5b040bceb2134dc92c09f4bf49e6b04be2e8115f553c19fe989f472f32c01d` |
| `native_baseline/rust/rei_microphysics/src/axbi_covariant_transport.rs` | `79b4d0972db8ed65ba64e71edc7530e46274ce8299197295bf24c800f86dbee9` |
| `native_baseline/rust/rei_microphysics/src/axbi_q_closure.rs` | `8c114090f11e5220659860e0ac4d9f03537b219d8384827e2bf8702d5d276c26` |
| `native_baseline/rust/rei_microphysics/examples/v14_projection_diagnostic.rs` | `868a4f8e28acebce0f1d78ff62f0adaf6a5d411c6896ea0b528afb8a16a0085f` |
| `projection_diagnostic.csv` | `ca4b20024bd2f8adfac5995ffeebfecd0c56f47d7cbe89d38f874a909402dc3e` |
| `projection_diagnostic.csv.cells.csv` | `3e9af61a432d40e743901c5000611a00788b3766b90840df4806a56466737b6b` |

The diagnostic source and two CSV byte hashes match `projection_execution.json`. That receipt records rustc 1.94.1, `cargo build --offline --locked --release --example v14_projection_diagnostic --jobs 2`, build exit 0, execution start `2026-10-19T05:34:54.390328+00:00`, and run exit 0. The build log contains the successful release build and `build_exit=0`; stderr contains eight completed cell/spectrum blocks and the final `COMPLETE diagnostic` marker.

## Mathematical review

For one occupied reference-energy cell, let the stored moments be

\[
M=(N,U_q),\qquad A f=\left(\int f(q)\,dq,\int qf(q)\,dq\right).
\]

Here \(N\) is photons per total H, \(U_q\) is reference-energy eV per total H, and \(q\) has units eV. Freeze the geometry, absorber densities, and support interval. The ray energy is \(E(q)=r q\), with fixed positive dimensionless \(r\), and

\[
(Lf)(q)=-\kappa(q)f(q),\qquad
\kappa(q)=c\sum_{j\in\{\mathrm{HI,HeI,HeII}\}}n_j\sigma_j(rq).
\]

The code uses \(c\) in cm/s, \(n_j\) in cm\(^{-3}\), cross sections in cm\(^{2}\), and physical stage duration \(h\) in seconds. Thus \(h\kappa\) is dimensionless. The same construction applies to the code's finite quadrature measure when its node locations/base quadrature branch are fixed.

Let \(R(M)\) denote the positive reconstruction with \(AR(M)=M\). On an interior smooth reconstruction branch, assume \(R\) is twice continuously differentiable locally and \(L\) is bounded on the represented support. Set

\[
\Phi_h(M)=A e^{hL}R(M),\qquad F(M)=ALR(M),\qquad G(M)=AL^2R(M).
\]

Expansion gives

\[
\Phi_h(M)=M+hF+\frac{h^2}{2}G+O(h^3),
\]

and, with the reconstruction repeated between the two half steps,

\[
\Phi_{h/2}(\Phi_{h/2}(M))
=M+hF+\frac{h^2}{4}\{G+F'(M)F(M)\}+O(h^3).
\]

Consequently,

\[
\boxed{\Phi_h-\Phi_{h/2}\circ\Phi_{h/2}
=\frac{h^2}{4}B(M)+O(h^3)},\qquad
B=AL^2R-F'F=AL\{I-R'(M)A\}LR.
\]

The final equality uses fixed \(L\), so \(F'=ALR'\). Differentiating \(AR(M)=M\) yields \(AR'=I\), and \(P=R'A\) is a tangent projection: \(P^2=P\). The component \(\{I-P\}LR\) has zero retained moments but influences the next moment derivative after multiplication by \(L\).

The exact solution of the closed moment ODE \(\dot M=F(M)\) instead has second term \(h^2F'F/2\). A nonzero \(B\) therefore gives a local error of order \(h^2\) for this particular projected map relative to that closed ODE. Under the usual local smoothness/stability conditions, this is the mechanism for first-order temporal error over a fixed interval. A single frozen-spectrum kinetic evolution \(Ae^{TL}R(M_0)\) is a different reference from the solution of the repeatedly closed moment ODE; the two references must retain separate labels.

### Sign check for the exponential family

On a fixed quadrature branch the code's final tilted weights have the form

\[
r_i=N\frac{b_i e^{\lambda q_i}}{\sum_k b_k e^{\lambda q_k}},
\qquad \mu=U_q/N,\qquad V=\operatorname{Var}(q)>0,
\]

where the positive \(b_i\) and \(q_i\) are fixed. Define expectations using \(r_i/N\), and

\[
\kappa_\perp=\kappa-\langle\kappa\rangle
-\frac{\operatorname{Cov}(q,\kappa)}{V}(q-\mu).
\]

Differentiation of the normalized exponential family gives

\[
R'\delta M=r\left[\frac{\delta N}{N}
+\frac{q-\mu}{V}\frac{\delta U_q-\mu\delta N}{N}\right].
\]

Hence \((I-P)LR=-r\kappa_\perp\) and

\[
B_N=N\langle\kappa\kappa_\perp\rangle
=N\langle\kappa_\perp^2\rangle\ge0.
\]

The native CSV deliberately uses **halves minus full**. Its predicted small-step number defect is therefore

\[
\Delta N_{\mathrm{CSV}}
=-\frac{h^2}{4}N\langle\kappa_\perp^2\rangle+O(h^3).
\]

The observed negative broad-spectrum number differences agree with that sign. No corresponding fixed sign is implied for energy, individual species events, or heat. A delta distribution is a separate zero-variance branch and attenuates as a single scalar exponential. For the smooth exponential family an affine opacity \(\kappa(q)=a+bq\) also preserves the family and gives exact semigroup closure in exact arithmetic. The physical cross-section diagnostic measures the actual nonlinear-opacity case rather than assuming a nonzero coefficient from its name.

The Taylor statements require small \(h\|L\|\); their remainder constants do not establish a uniform stiff result. Finite arithmetic replaces \(AR=I\) by the actual checked moment-fit tolerance. Endpoint collapse, complete extinction, support changes, and quadrature branch changes require separate treatment.

### Literature correspondence

Gorban, Karlin, Öttinger, and Tatarinova, *Physical Review E* **63**, 066124 (2001), DOI [10.1103/PhysRevE.63.066124](https://doi.org/10.1103/PhysRevE.63.066124), Eq. (8), gives the corresponding first correction to the macroscopic vector field. With microscopic field \(J=Lf\), moments \(A\), and reconstruction \(f^*=R(M)\), its correction is \(B/2\). The reviewer opened the [primary paper mirror](https://icm.krasn.ru/ftp/articles/2001/2088gorban_PREEhr101.pdf) and checked Eq. (8). The algebraic correspondence is used here; no entropy theorem from that paper is transferred to the absorbing photon/gas subsystem. The general projection lemma is not claimed as novel.

## Source mapping and frozen diagnostic contract

`axbi_driver.rs::chemical_stage` clones the old state, prepares photon quadrature once before Newton iterations, and passes the immutable `PreparedAbsorption` into the residual context. `evaluate_source_clocks` changes trial absorber densities using the selected gas clock, including midpoint gas, while retaining that prepared spectrum. At acceptance the output photon moments replace the old moments. The next chemical stage prepares a new reconstruction from those accepted moments.

`axbi_covariant_transport.rs::prepare_legacy_serial` / `prepare_cell` call `cell_quadrature` from each cell's number, reference energy, and support envelope. The resulting nodes retain \(q_i\), number weights, physical-energy cross sections, and excess energies. `PreparedAbsorption::evaluate_with_rule` multiplies each node weight by `exp(-dt_s*c*opacity)` in exponential mode and sums the survivors back into the two moments. The integrated mean attenuation is used for the same absorption event, binding, and excess-heat owners. These operations realize the proposed projected map, up to the documented numerical quadrature/roundoff.

The new diagnostic calls exactly those public methods. It initializes the MD14 source distribution once, fixes geometry at \(a=1/21\), fixes \([n_{\mathrm{HI}},n_{\mathrm{HeI}},n_{\mathrm{HeII}}]\) from fractions \((0.075,0.12,0.03)\), and performs no further injection, geometry evolution, gas update, Newton solve, or adaptive acceptance. The reference opacity is the actual native total opacity at 20 eV. Pair experiments compare one duration \(\theta/\kappa_{20}\) against two duration-\(\theta/(2\kappa_{20})\) stages, rebuilding the reconstruction between stages. Frozen histories keep total duration \(1/\kappa_{20}\) while varying the number of stages.

The delta control uses a single 60 eV reference-ray delta with the same initial total photon number as the broad state. All frozen rays have \(r=1\) at this isotropic reference geometry, so the reported reference-energy L1 and physical-energy inventory have the intended common energy scale here. Temperature is not an input to this fixed-opacity transport diagnostic.

There is no cached-template composition mistake: each half-step prepares from the previous result state. Calling the same prepared object's evaluation twice without updating/repreparing the state would not represent two successive stages, but the diagnostic does not do that.

## Recomputed output checks

The main CSV contains **62 diagnostic rows**: 24 broad pair comparisons, 24 delta pair comparisons, seven broad refinement rows, and seven delta refinement rows. The cell sidecar contains 13,312 rows. These counts are neither new cosmological histories nor the previous manufactured 76-problem suite.

From the last pair \(\theta=0.05,0.025\), the reviewer recomputed local L1 slopes \(\log_2(D(0.05)/D(0.025))\):

| Energy cells | Number L1 slope | Reference-energy L1 slope |
|---:|---:|---:|
| 8 | 1.9196576082 | 1.9110312479 |
| 16 | 1.9425978724 | 1.9551579999 |
| 32 | 1.9680288475 | 1.9720901686 |
| 64 | 1.9737222874 | 1.9744674831 |

Every broad pair has negative signed total number `result-base`, as predicted by the convention above. At 16 cells the two smallest signed differences are \(-4.0765896984\times10^{-14}\)/H and \(-1.0605148974\times10^{-14}\)/H. These differences are well separated from the saved ledger and moment-fit residuals.

For the 16-cell broad frozen histories, \(p=\log_2|(Q_{16}-Q_{32})/(Q_{32}-Q_{64})|\), computed from `result_Q`, is:

| Quantity | Observed self-difference order |
|---|---:|
| Number | 1.0092408929 |
| Energy | 1.0073594067 |
| HI absorption | 0.9451900214 |
| HeI absorption | 0.9931821766 |
| HeII absorption | 0.9987316763 |
| Binding | 1.0009081238 |
| Heat | 0.9798425730 |

These are finite-refinement self-differences. The fixed `base` outcome is one full frozen kinetic attenuation and is not labeled as an exact closed-moment-ODE reference. Subtracting it cancels in successive differences, but its absolute separation from a refined history must not be called the latter's temporal error.

Independent reductions of all saved rows give:

- Delta pair relative number L1 maximum: \(1.5396438568\times10^{-16}\).
- Delta pair relative energy L1 maximum: \(1.6422867806\times10^{-16}\). A combined rounded bound for both is \(1.65\times10^{-16}\).
- Absolute number ledger maximum: \(7.4446255130\times10^{-23}\)/H.
- Absolute energy ledger maximum: \(4.7380905487\times10^{-21}\) eV/H.
- Maximum reconstruction count/energy relative defects: \(2.2123947568\times10^{-16}\) and \(4.1996091450\times10^{-16}\).
- Tail-bound and asymptotic-mean diagnostic columns are zero throughout these runs.
- Minimum photon number is zero because empty cells are retained; native validation accepts every occupied state. Minimum broad occupied normalized support slack is 0.0052123209943.

The pair reports have constant total prepared-node count at each spectral resolution: 640, 832, 1,280, and 2,432. This and the interior support/tail diagnostics are consistent with the regular branch used in the derivation. Total node counts do not uniquely identify per-cell node positions or rule out compensating per-cell panel changes. Per-node fingerprints and a direct numerical evaluation of \(N\langle\kappa_\perp^2\rangle\) were not recorded. Therefore the output supports the predicted scaling and sign; it does not constitute coefficient-by-coefficient verification of the discrete covariance formula.

## Coupled-campaign interpretation and remaining decision

The diagnostic removes gas-solver tolerance, source-birth timing, changing geometry, and source evolution while retaining the native reconstruction and attenuation path. The first-order frozen refinement therefore demonstrates a concrete spectral-reconstruction limitation of this map. It is sufficient to invalidate the unqualified assertion that exact per-node exponential attenuation automatically makes the represented broad photon moments second order.

The original V14 sweep's `source_off` modes start with the driver's empty photon state and inject no photons. Their gas convergence does not directly test the broad-spectrum projection mechanism. Conversely, the source-on temperature history involves state-dependent opacity, source additions that can alter support envelopes, geometry, and several thermal channels. The present frozen diagnostic alone does not establish which contribution dominates those histories. No other definite native source defect was found in the inspected source, and no core change is requested solely on the basis of this review.

For the original coupled interpretation, use the already-saved event/heat/channel differences and any explicitly selected new coupled diagnostic to separate contributions. Keep the operator target explicit: accurate integration of the chosen closed moment ODE, or persistent spectral evolution of an initialized reconstruction. Positive conservation residuals and a change of temporal scheme are evaluated against that declared target. Source-on second order and the other held claims retain their existing status until the corresponding evidence is obtained.


## Dated addendum — final report and wrapper replay, 2026-10-19 UTC

The same separate scientific-review subagent completed a bounded consistency review of `delivery/RESEARCH_CONTINUATION_KO.md` and the saved wrapper replay receipts. This addendum preserves all earlier review text and its original scope. No additional simulations, searches, or general audit were performed for this addendum.

Reviewed file identities:

| File relative to `v14_work/` | SHA256 |
|---|---|
| `delivery/RESEARCH_CONTINUATION_KO.md` | `74b72a02ade9f24114e85fca515e560779e6d448363129e94fbedf6849a4343e` |
| `delivery/evidence/WRAPPER_VERIFICATION.json` | `cd4047e9a0fd53269ae9824e72074915adb984d1b1b807927e5efaced7a99c65` |
| `delivery/evidence/wrapper_replay/EXECUTION.json` | `7dd2758512efcad9155fba174bea0f720538ecbe201e94c42cad192f06be78fc` |

One concrete notation issue was reported and corrected before this acknowledgment: the single-history balance now uses \(\delta_t(w+B)\), with \(\delta_t\) explicitly distinguished from the coarse-minus-fine \(\Delta\). The event and heat terms in that balance are cumulative quantities on one history. The listed initial broad photon number and energy are now expressly labeled as the 16-cell initial values.

The final report retains the \(h^2/4\) full-minus-two-halves coefficient and the opposite sign for the CSV's halves-minus-full number defect. It distinguishes the frozen transport suboperator from the coupled photon–chemistry–thermal map, and it does not infer a quantitative causal contribution to the old coupled temperature error from the frozen result alone. The fixed-node/smooth-branch qualification and the distinction between a one-shot kinetic attenuation reference and a closed-moment-ODE reference remain explicit.

The wrapper execution receipt records a fresh-placement replay from `2026-10-19T05:46:18.389808+00:00` to `2026-10-19T05:46:30.913330+00:00`. Restore, build, diagnostic, and analysis each exited 0; the recorded build and diagnostic durations are 9.256738101 s and 0.101428768 s. Its diagnostic source SHA256 is `868a4f8e28acebce0f1d78ff62f0adaf6a5d411c6896ea0b528afb8a16a0085f`, matching the first diagnostic. The saved verification receipt records original/replay byte equality for both CSVs, with the same hashes listed earlier in this review and the same 62 summary rows and 13,312 cell rows. This is a replay of the same diagnostic matrix, not additional unique research cases or cosmological histories. These receipts are execution evidence supplied for review; this reviewer did not rerun the wrapper or binary.

The report correctly treats the previous NCP 84 histories and 36 native tests as inherited completed evidence, separately from this sandbox diagnostic and its wrapper replay. It also distinguishes the later evidence-publication commit from an established runtime checkout SHA; native byte identities and the frozen source anchor support the source comparison without inventing a runtime Git identity. Source-on second order, uniform stiff accuracy, Case B, full EoR, and signed Bianchi remain held. No consensus between independent model families is asserted.

**Final-report consistency verdict: PASS_SCOPED after the stated notation correction.** This acknowledgment neither enlarges the scientific scope of the original review nor certifies a future publication or provider backup that had not yet occurred when the review was written.
