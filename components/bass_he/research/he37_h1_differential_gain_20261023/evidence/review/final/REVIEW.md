# HE37 independent follow-up review

Date: 2026-10-23. Contract: workflow1.0.0 / approval0.2. This is a read-only review of the documentary corrections, saved diagnostic and figure, and the newly implemented H1 net-source bridge. No author file was edited. No subagent was used for this follow-up.

## Verdict

**The two previous documentary findings are closed. The new bridge, saved diagnostic, performance interpretation, and final plot are confirmed within the declared source-model scope. No new material defect was established.** The bridge's actual energy owner and number census are now reviewed; they were explicitly outside the first review.

The physical scope remains ground-H1 Le–Cambier Eq.85 with assumed isotropic outgoing directions, a stationary heavy target, common bulk frame, and an infinitesimal electron Grad STF variation. The temperature source additionally requires the explicit all-retained, common-T thermal interpretation. Neither the code nor its saved evidence establishes a calibrated angular law, finite-mass reaction kernel, finite-amplitude distribution closure, or total-gas species-stress partition.

The principal exact identities reviewed are:

| Object | SHA256 |
|---|---|
| Corrected public derivation | `40935086d1682e7eec94df391f4bfc2edbbbfc73d85a77f68453dbd59c9d7372` |
| Unchanged LC provider | `9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16` |
| Net-source implementation | `34147e2a6b7644b5509189037e26d6f9f469bd618588fb2266c7225027d8e379` |
| Net-source verifier | `006746338b7c4a57e5a75012d2c5ffc525fca10fcd4bd960c25735d9334d0975` |
| Net-source saved RESULT | `35530b3ef188253c2863cc5fa0b3889c0c260625c436a21bf4603767aeccf92d` |
| Diagnostic script | `fb995a03c819f97ef59a00282de82b46f083dda2feb40deda3b0e6c08f0cdcd0` |
| Diagnostic CSV | `7e6103b1f2a2aca36608e5d2fa99b94d3494ecb52f98377ae2e0b4b29e9ed745` |
| Final diagnostic PNG | `13643f1caff1714ed828f8b4650af27b95d4314c4e2d827094c7a4bd8d470099` |

## 1. Documentary disposition

**R1: closed.** The public companion `components/lc_provider/INPUT_COERCION_CLARIFICATION.md` states the actual NumPy coercion behavior: scalar/all-Boolean inputs are rejected, while mixed Boolean/numeric sequences are coerced before validation. It explicitly limits the prior broad wording and identifies the actual saved 24 rejection cases. The provider and verifier remain byte-identical to the original executed objects. This is the documentation remedy proposed in the original review, so no kernel replay is needed.

**R2: closed.** `evidence/docfix/DERIVATION_before.md` is byte-identical to the original reviewed derivation. The corrected public derivation differs only by the two-line paper-title replacement. Its equations, assumptions, and other wording are unchanged. Both old and new hashes match `evidence/docfix/CORRECTION.json`. Preserving the original mathematical-check evidence and recording the new document identity is the appropriate disposition; changing a title does not require a mathematical re-execution.

The recorded failed string-matching edit attempt made no scientific change and is separately preserved. It does not alter either closure decision. [Evidence: public `CORRECTION.json`, exact old/new text comparison, companion coercion document; `SAVED_PAYLOAD_OBSERVATIONS.json`, documentary disposition.]

## 2. Net-source physics, ownership, and normalization

### One coherent event and energy ledger

The bridge uses HE32's `Y_i=n_i/n_b` ordering with H0 at index 1 and H+ at index 2. It rejects nonzero populations in the other 19 slots and requires `Y_H+Y_p=1` within the inherited roundoff tolerance, without renormalizing. Thus `n_e=n_b Y_p`, `n_H=n_b Y_H`, and the event rate is

\[
r=n_e n_H\alpha=n_b^2\alpha Y_HY_p.
\]

The effective unary event is H0→H+ with the **current** coefficient `n_e α`. This reproduces the desired physical event rate through the unchanged REI event algebra. It does not treat H+ as a fabricated catalyst or double the event count. The mass-number and charge arrays match the pinned HE36 convention. [Evidence: `net_source.py` lines 8–18, 41–75, 147–179; unchanged donor `ResolvedEvent`; donor provenance byte comparisons.]

The resulting sources are correctly

\[
R_H=-r,\quad R_p=R_e=R_{\rm part}=r,\quad R_{\rm nucleus}=0,
\qquad Q=-Ir.
\]

The actual event ledger assigns `dI=+I`, `dEth=−I`, and zero to the remaining reservoirs, using the same source-native `I_J`. The ionization reference at the H+ slot checks that potential change against the stoichiometry. `attach_event_tensor` checks the per-event and volumetric tensor traces against this heat owner. The returned `Q` and `reservoir_sources_W_m3['dEth']` are two views of the same quantity, with explicit documentation that they must not be added. The potential owner is therefore present in the code, not merely in the derivation. [Evidence: `net_source.py` lines 171–192, 204–215; donor energy validation and `event_bridge.py` trace/owner checks.]

### Frame and electron STF

The per-event tensor is

\[
C_{\rm event}=-\frac{2I}{3}\mathbf1-
\frac{\kappa_2}{\alpha}\frac{\pi_e}{n_e},
\]

so the common-bulk central source is

\[
S=\frac{2Q}{3}\mathbf1+J,
\qquad J=-n_H\kappa_2\pi_e.
\]

The code passes the explicit common-bulk central frame, net-thermal-tensor scope, and J/event unit labels to the unchanged bridge. `electron_pi_Pa` is named and documented as electron pressure STF. It is neither clipped nor projected into a different tensor. The normalized input magnitude is only a diagnostic for an infinitesimal variation, not a certificate for a positive finite Grad distribution. [Evidence: `net_source.py` lines 123–154, 181–203; README contract and equation map; saved rotation control.]

The heavy parent-to-daughter kinetic-pressure transfer cancels in the summed retained source at the admitted leading recoil-free order. That permits the stated net `S` at this order; it does not identify `π_e` with total gas `π_b`. A future gas evolution still needs the species-stress partition and thermalization closure described as deferred dependencies.

### Thermal particle census

The code requires both all-retained-thermal and neutral-21-state census labels. For the admitted pure-H state it uses `n_part=n_b(Y_H+2Y_p)`. Its reaction-only temperature result

\[
\dot T=-\frac{r}{n_{\rm part}}\left(T+\frac{2I}{3k_B}\right)
\]

is the correct chain rule for `U_th=(3/2)n_part k_B T`, with particle creation counted once. It does not add the capacity term to the heat ledger. The saved separate donor thermal-RHS comparison agrees for its stated control. This is an instantaneous conditional common-T result; no trajectory or thermalization proof is asserted. [Evidence: `net_source.py` lines 160–170, 204–215; `thermal_and_immutability` saved group.]

## 3. Jacobians and zero boundaries

The donor row Jacobian fixes its current effective unary coefficient and therefore fixes `n_e`. The code retains that row under `event_row_frozen_ne` with an explicit scope string. It separately supplies the physical **abundance-source** Jacobian at fixed T and n_b. For the two H columns this is

\[
J_Y=n_b\alpha
\begin{pmatrix}
-Y_p&-Y_H\\
Y_p&Y_H
\end{pmatrix}.
\]

The missing electron-density derivative is correctly restored in its second column. This is a 21×21 ambient polynomial extension with only the H0/H+ block active. On the normalized pure-H manifold, setting `Y_p=x` gives the tangent derivative `dF_p/dx=n_b α(1−2x)`. Neither matrix is presented as the Jacobian of temperature, pressure, all 21 physical species, or a full network. [Evidence: `net_source.py` lines 47–48, 132–134, 155–159; saved `physical_jacobian` controls.]

Known zero states are handled before dividing by `n_e` or constructing a positive event. At zero electron density and at zero target density the source vanishes, but the respective nonzero activation derivatives are retained. At vacuum the abundance derivative is also zero and temperature evolution is returned as undefined (`None`), rather than interpreting empty-space temperature as a dynamical quantity. Nonzero electron stress at zero electron density is rejected. These behaviors are physically and mathematically consistent with the admitted polynomial source. [Evidence: `net_source.py` lines 147–170; `zero_states` saved group.]

The saved finite-difference checks stay on the admissible normalized manifold. Their maximum recorded relative discrepancy is `2.9017643843332053e−10` against the declared `3e−9` gate. Their same-form algebra checks alone would be insufficient evidence of the density derivative, but the independent differentiation above and the separate finite differences confirm the actual formula.

## 4. Tiny STF and representability

The code deliberately returns `J` from the direct STF expression while retaining the donor-owned full `S`. This is appropriate because an extremely small diagonal STF can round away when added to a much larger isotropic diagonal. The comparison to the donor projection is scaled to the full source, rather than divided by a vanishing STF. No trace repair or clipping is introduced.

One new, narrowly scoped control resolved this concrete cancellation risk. With `π_e=diag(10^−200,−10^−200,0) Pa`, T=20000 K, n_b=10^6 m^−3, and `(Y_H,Y_p)=(0.7,0.3)`, the returned STF is

\[
J=\operatorname{diag}(-1.684966749100594,\;1.684966749100594,\;0)
\times10^{-210}\ {\rm Pa/s}.
\]

The donor projection of rounded `S` is zero for this control; `S` has diagonal entries about `−2.86527×10^−24 Pa/s`. The direct returned STF agrees with an 80-digit Decimal multiplication of the exact binary64 inputs to relative error `2.220446049250313e−16`. Therefore the suspected loss in the **returned** J is rejected. Consumers must use that returned J when the small STF is the quantity of interest, rather than reconstructing it from an isotropic-dominated rounded S. This behavior is already documented by the author. [Evidence: `check_tiny_stf.py`, `TINY_STF_OBSERVATION.json`; source hash pinned before import.]

The inherited scaled multiplication helpers reject nonzero underflow/overflow rather than changing it into a physical zero. The saved bridge receipt contains both rejection cases. This is a fail-closed representability policy, not a promise that all finite input magnitudes can produce every requested per-event and volumetric output in binary64.

## 5. Saved diagnostic and tail proof

All 129 CSV rows exactly match the JSON rows and the saved temperature grid. The reused CCC CSV is byte-identical to the HE36 diagnostic payload; the old kernel is not imported by the new diagnostic. The endpoint/center summaries and ratio range match the saved rows. The LC/CCC comparison remains a comparison of different source kernels, thresholds, and energy support, not a calibrated error estimate. [Evidence: `run_diagnostic.py`; `SAVED_PAYLOAD_OBSERVATIONS.json`.]

The independent numerical lane uses the original `σ(E)v(E)` Maxwell energy measure with `t=(E−I)/θ`. Its raw integrand construction and positive GL weights are correct. The actual planned refinement was GL64→GL96, stopping at the first passing order. The recorded maximum relative discrepancies are `9.138023671084738e−12` and `2.2426505097428162e−14`, respectively, against `3e−12`; GL128 was not executed.

The omitted t>64 tail is correctly separated from GL discretization. For `x=I/θ`, the scaled moment integrands are `t(x+t)^(j−1)e^−t`. For α, bounding `t/(x+t)≤1` and using `F(x)≥1/(x+2)` gives `(x+2)e^−L`. The β, γ, and δ bounds follow from the exact polynomial exponential tails of t, t², and t³. The denominators are respectively `1`, `x+2`, and `x²+4x+6`. Thus the formulas in the README and `tail_bounds` are valid positive relative bounds for this model. The saved maximum is `4.617226718601215e−24`. It does not bound omitted real cross-section physics or the CCC table tail.

## 6. Performance claims and execution counts

The measured workloads are the same source, the same 129 temperatures, and the same four SI moments. Only GL nodes/weights are prepared outside the timed calls. T-dependent energy, cross section, and weights are rebuilt during each raw-GL call; the analytic lane retains its validation/immutable-result overhead. The separate node-setup timings are disclosed.

The saved source loops and receipt agree on two warmup batches per lane and five alternating paired trials with 64 batches per lane per trial: **320 timed batches per lane**. Including the primary diagnostic and resolution calls, there are 323 analytic batches and 324 GL batches in that experiment. Saved times reproduce the median paired GL/analytic ratio **4.4825080029195785**, the observed range **3.892765018690632–8.538838605855716**, and the ratio of median times **4.41035830843409**. These are distinct statistics and are labeled correctly.

The host, thread settings, wall time, and RSS are recorded. The report appropriately limits the conclusion to this local reference-kernel comparison. It does not claim an IVP, network, native-Fortran, or production throughput speedup. No new timing run was performed by this review.

## 7. Actual figure inspection

I opened the final PNG with `view_image`, without rendering it again. All four panels, axes, units, legends, the source/approximation subtitle, and both footer lines are visible. The corrected footer is separated from the bottom x-axis labels; the panel (b) annotation does not cross the curve. The native/CCC rate comparison, positive cooling magnitude, returned two-electron energy, and angular envelope agree with the saved columns and renderer mapping.

The angular envelope is explicitly described as a set of positive recoil-free models at fixed LC cross section, not measured H1 uncertainty. The electron-STF and infinitesimal-heavy-target assumptions appear on the figure. I found no material labeling, clipping, or scientific-interpretation problem. The render receipt binds the actual inspected PNG, SVG, renderer, and CSV; both preserved render attempts used the same scientific CSV. The second render's changes are confined to layout/annotation placement and attempt metadata.

## 8. Evidence binding, scope, and final state

The diagnostic manifest verifies **22/22** payloads; the bridge manifest verifies **13/13**. The bridge START fields are retained in RESULT, all **nine** receipt code hashes match current files, and the seven recorded test groups match the current verifier's group definitions. All four vendored source files match their declared donor bytes. All 13 public bridge copies match the reviewed scratch package. The review does not infer a fresh execution from this readback.

The bridge's seven saved groups all passed. Their maximum scalar normalized defect is `5.995204332975845e−15`; the rotation/direct-STF group reports `1.1102230246251565e−16`; 25 input/scope rejection cases and two representability cases are recorded. These results apply to the exact hashes above. They are finite numerical checks, not a uniform error proof or physical calibration.

New review execution comprised **one targeted bridge call**, which performs one provider temperature evaluation, and a standard-library-only saved-payload audit. No completed suite, diagnostic, IVP, benchmark, or render was replayed. The actual final PNG was inspected once. `FINAL_HASH_READBACK.json` rechecks the reviewed files at completion. `REVIEW.json` contains per-claim confirmed/rejected/inconclusive judgments and the prior-finding dispositions.

Remaining scientific dependencies are unchanged: calibrated angular distributions if replacing isotropy; finite-mass target motion/recoil; thermalization and species-stress partition; additional atomic/isotope/nuclear channels; and coupled population/temperature/stress/background/metric evolution. They are explicit limits of this completed component, not new defects discovered by the follow-up.
