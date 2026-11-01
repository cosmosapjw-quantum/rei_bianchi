# REI IGM original 26-event tick160: four-site source-coupled stage physics and low-rank implicit derivative

## Scope, owner, immutable conditions

Based on source-owned [PR #332](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/332), exact HEAD \`2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a\`, which includes the original 26-event REI model and three neutral-species / four photon-group Jacobian. Original accepted tick160 source archive SHA256 \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\`, state array SHA256 \`cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01\`. Original 46,080 physical cells, 3 lanes sharing identical numeric parent. First canonical interval remains blocked at [160,161], 160/131072 ticks accepted and original full-X independent-box logT error \`2.1245050576368385e-4\` above locked \`2e-4\` gate; width limit \`2e-3\`. No source owner change, clipping, tolerance relaxation, new full IVP, production or merge.

## Exact source derivative (derived from source-owner equations, not a new approximation)

For photon group \(g\), original global neutral species \(s\in\{\mathrm{HI},\mathrm{HeI},\mathrm{HeII}\}\), and node \(i\), let \(n_{is}\) be species **particle counts**, \(S_s=\sum_i n_{is}\), \(C_{sg}\ge0\) the original cross section/owner-normalized coefficient (including H/He normalization and \(Y_{\rm He}\)), \(E_g\ge0\) the original externally owned subgrid opacity, and \(J_g\) the original photon current (particles/s). The original photon source site evaluates

\[
D_g=E_g+\sum_t C_{tg} S_t,\qquad
r_{isg}=\frac{J_g C_{sg} n_{is}}{D_g}.
\]

At fixed forcing \(J_g,C_{sg},E_g\), all derivatives within a smooth active support branch satisfy

\[
\frac{\partial r_{isg}}{\partial n_{jt}}
=\underbrace{\delta_{ij}\delta_{st}\frac{J_g C_{sg}}{D_g}}_{\text{on-node direct}}
-\underbrace{r_{isg}\frac{C_{tg}}{D_g}}_{\text{shared-denominator feedback}}.
\]

Summing \(g\) preserves the same three global moments in the off-node part, so the **nonlocal Jacobian of each source evaluation site** factors through three moment coordinates, regardless of the 46,080-node spatial dimension. This statement does NOT imply that the complete nonlinear multi-stage map or its full/half difference is rank three. At a fixed node-local numerator, the derivative with respect to the LOG of the global species moment is

\[
\left.\partial_{\ln S_t} r_{isg}\right|_{n_{is}\,\mathrm{fixed}}
=-r_{isg}p_{tg},\qquad p_{tg}=\frac{C_{tg} S_t}{D_g}.
\]

This is a denominator-only counterfactual sensitivity, not the total derivative from a realizable globally rescaled parent state. Original primary photoheating at each site is \(Q^{\rm photo}_i=\sum_{g,s}r_{isg}\epsilon_{sg} \mathrm{eV}_{\rm erg}\). Thus its exact denominator-only source response is \(-\sum_{g,s}r_{isg}\epsilon_{sg} \mathrm{eV}_{\rm erg}\,p_{tg}\). Nucleus, photon, source energy units must not be mixed.

## New constructive implicit-stage Jacobian form

Let \(z\) collect local population/thermal stage unknowns for one implicit source-evaluation stage and \(M(z)\in\mathbb R^3\) its three shared neutral sums. Introduce an independent moment argument \(\mu\) and write \(R_{\rm loc}(z,x,\mu,\theta)=0\) with \(\mu=M(z)\). If the source-owned stage equations have no other cross-cell terms when \(\mu\) is held fixed, the exact Jacobian on any fixed smooth/table branch takes the form

\[
R_z = A+B V^\top,\quad
A=\partial_z R_{\rm loc}|_{\mu},\quad
B=\partial_\mu R_{\rm loc},\quad
V^\top=M_z.
\]

\(A\) has local node blocks. By the Woodbury identity, if \(A\) and the Schur complement \(K=I_3+V^\top A^{-1}B\) are nonsingular,

\[
(R_z)^{-1}
=A^{-1}-A^{-1}B K^{-1}V^\top A^{-1}.
\]

Multiple independently evaluated stage source sites may require an extended shared moment vector \(\mu\in\mathbb R^{3k}\), including four original event-box sites in EACH original MPRK/SDIRK map. This does NOT prove that the combined map Jacobian has rank \(3k\) without a complete derivation of every cross-site/implicit-root dependency. It shows an exact conditional computational decomposition for its source-coupled residual.

For shared physical source parameters \(\theta\), the full-vs-two-half defect is \(D_h(x,\theta)=F_h(x,\theta)-G_{h/2}(G_{h/2}(x,\theta),\theta)\). Where the implicit roots are smooth and unique,

\[
D_xD_h
=D_xF_h-(D_xG_2)(D_xG_1),\qquad
D_\theta D_h
=D_\theta F_h-(D_xG_2)D_\theta G_1-D_\theta G_2.
\]

The source/forcing \(\theta\) must be shared across full and both halves. For each implicit stage \(R(z;x,\theta)=0\), \(\partial_q z=-(\partial_z R)^{-1}(\partial_q R)\). The stage-level Schur decomposition is therefore a constructive route to calculating a correlated \(J_D\); however its **complete interval remainder on original \(X\times\Theta\)**, including table events and thermochemical root dependence, remains UNPROVED.

## Scientific experiment

A read-only wrapper observes the original \`event_box\` during **actual** original source-owned full, first-half and second-half runs from one source-locked, nuclei-conserving tick160 point parent. Each map has four physical source evaluation sites: parent, predictor, implicit gamma-stage and final stage. Later outer-root iterations overwrite gamma/final records with the final original source evaluation. For all twelve genuine sites, the experiment evaluates the original **46,080-cell** photon-source absorption, original source primary photoheating, the exact three shared-neutral denominator-only source derivatives, and four photon-group source fractions. It checks membership in the original source interval operator and original photon conservation. It produces **552,960 spatial-cell×source-site model records plus 48 source-group records** if all three original steps certify. This is genuinely new source-conditioned **within-step** physical data, not a rerun of PR332's static tick160 input/source atlas.

The original source code and blocked parent archive remain unmodified. The single point parent and passive stage instrumentation are deliberately nonauthoritative for the all-X acceptance; the original status stays 28/88 REPORTED, working 33/88, physical fast 4/7, canonical delta zero. No claim about Bianchi LoS/CMB measurement or source-time global thermal closure.

## Adversarial pre-commit risks

1. Source denominator-only derivatives omit the correlated local-numerator term under actual parent perturbations. Never treat them as a total Jacobian.
2. A nucleus-conserving representative is inside the marginal source enclosure; actual cross-site correlation of the accepted solution need not allow every such representative.
3. Positivity and exact operator inclusion are necessary but not sufficient for a source-correlated all-X MPRK/SDIRK defect certificate. A narrow point gap cannot replace the historical full-box gate.
4. Differentiating through original implicit stage roots requires nonsingular Jacobian and a fixed table-event/branch certificate. This has NOT been verified across the entire frozen parent set.
5. The three original lanes are not three independent 46,080-cell observational datasets. This unit runs one declared lane, uses the original source runtime and keeps that limitation explicit.
6. Native subagent and independent-author referee are NOT_RUN. Wolfram symbolic and synthetic Schur tests are same-project mathematical controls only.

## Operational completion and next physics

R5 theory and C5 source-owned experiment produce the physical output and tests for this bounded unit, not a new canonical node. 20-stage source/R/C ledger records inherit valid stages and identify exactly newly executed ones; all metadata and numerical claims require actual GitHub CI result and binary readback. Next if success: *derive and enclose the whole original nonlinear implicit-stage \(D_h(X,\Theta)\) Jacobian and second-order remainder*, then one unchanged-gate [160,161] targeted retry. If it fails, preserve the source-conditioned failure and use independent B2D/geometry-consumer science, never blind loop or gate inflation.
