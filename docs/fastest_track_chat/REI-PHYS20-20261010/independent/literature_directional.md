# REI-PHYS20 — primary-source note and scope challenges

Independent source-support subtask, 2026-10-10. Inherited model label: GPT-6 Astra, from host developer metadata. Research harness core and model-routing document read. Harness ZIP SHA supplied by owner: `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`. This is source research and diagnostic derivation, not a decision review or a repo audit.

## Primary sources inspected

Page numbers below refer to the indicated arXiv PDF pages (one-based), not publisher pagination. Source relations distinguish directly supported identities from project derivations.

### S1 — exact Bianchi-I geodesics

Pierre Fleury, Cyril Pitrou, Jean-Philippe Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D **91**, 043511 (2015), DOI [10.1103/PhysRevD.91.043511](https://doi.org/10.1103/PhysRevD.91.043511); [arXiv:1410.8473v3](https://arxiv.org/abs/1410.8473v3), [PDF](https://arxiv.org/pdf/1410.8473v3).

Inspected portions: PDF p.2, Eqs.(2.1)–(2.5); p.4, Eqs.(4.1)–(4.5) and surrounding argument; p.9, Eqs.(7.20)–(7.23). Retrieval references: `turn1view0`, `turn2view1`, `turn7view2`; screenshot request `turn6view0`.

**supports:** spatial translation Killing fields conserve covariant wave-vector components `k_i`, whereas contravariant components evolve, Eq.(4.1). Equations (4.2)–(4.3) give `omega = a^{-1} sqrt(sum_i exp(-2 beta_i) k_i^2)`. Equations (2.1)–(2.3) define `a_i=a exp(beta_i)`, `sum beta_i=0`. Equations (7.20),(7.23) exhibit first-order energy anisotropy `-sum beta_i k_i^2` in observer-normalized coordinates.

**limits:** their `d` is the direction of observation, opposite propagation. Paper units absorb `c`; for covariant photon momentum `q_i=hbar k_i`, restore `E=c sqrt(sum q_i^2/a_i^2)`. These are free-geodesic identities between interactions. The paper does not directly supply the atomic heating cancellation theorem or the momentum-angle Jacobian used below.

### S2 — exact spectral and integrated Liouville multipoles

Roy Maartens, Tim Gebbie, George F. R. Ellis, *Cosmic microwave background anisotropies: Nonlinear dynamics*, Phys. Rev. D **59**, 083506 (1999), DOI [10.1103/PhysRevD.59.083506](https://doi.org/10.1103/PhysRevD.59.083506); [arXiv:astro-ph/9808163v2](https://arxiv.org/abs/astro-ph/9808163v2), [PDF](https://arxiv.org/pdf/astro-ph/9808163v2).

Inspected portions: conventions p.3; pp.13–14, Eqs.(69)–(73) and scope paragraphs; p.15, Eq.(86). Retrieval references: `turn2view0`, `turn7view0`, `turn3view2`; screenshot request `turn6view1`.

**supports:** Eq.(69) gives exact photon energy change. Eq.(70) is the energy-resolved Liouville hierarchy; its homogeneous geodesic-observer monopole is

`b_0/E = dot(F_0) - H E partial_E F_0 - (2/15) sigma^{ab} E^{-2} partial_E(E^3 F_ab)`.

Equation (72) gives the brightness monopole, with shear coupled to the quadrupole as `(2/15) sigma^{ab} Pi_ab`. The paragraph following Eq.(71) explicitly allows any collision multipoles. Equation (86) is the photon energy balance with the stated Thomson approximation.

**limits:** the exact Liouville part and approximate Thomson kernel must be distinguished. These statements do not independently validate a chosen atomic collision closure. A shear-times-quadrupole contribution is second order only when both quantities are first-order perturbations about an isotropic baseline. Nonperturbative radiation anisotropy changes that counting. Source units set `c=8 pi G=k_B=1`.

### S3 — first-order Bianchi radiation anisotropy

Andrew Pontzen, Anthony Challinor, *Bianchi model CMB polarization and its implications for CMB anomalies*, MNRAS **380**, 1387–1398 (2007), DOI [10.1111/j.1365-2966.2007.12221.x](https://doi.org/10.1111/j.1365-2966.2007.12221.x); [arXiv:0706.2075](https://arxiv.org/abs/0706.2075), [PDF](https://arxiv.org/pdf/0706.2075).

Inspected portions: PDF p.4, Eqs.(21)–(25); p.5, Eqs.(34)–(38) and distribution definition; pp.6–7, Eqs.(43),(55). Retrieval references: `turn4view0`, `turn5view0`, `turn5view1`, `turn7view1`; screenshot request `turn6view2`.

**supports:** Eq.(22) states the exact comoving energy law `epsilon'=-epsilon exp(alpha) p^i p^j sigma_ij`. Section 4 defines the phase-space distribution and its Liouville derivative. Eq.(43) explicitly identifies the first-order gravitational temperature source as a pure quadrupole. Equation (55) shows the linear Thomson temperature monopole collision term vanishes.

**limits:** the CMB Boltzmann hierarchy is linearized around FRW and uses an achromatic Thomson kernel. It cannot be reused as a nonperturbative ionization/heating calculation, nor as proof that finite shear produces no scalar response.

## Diagnostic derivations (our work, not quotations from these sources)

### Covariant momentum versus physical angular measure

Let `A=diag(a_1,a_2,a_3)`, `q=|q_i|`, `n_q=q_i/q`, `S=|A^{-1}n_q|`. The physical tetrad momentum is `p=A^{-1}q`, so `E=c q S` and `n_phys=A^{-1}n_q/S`. The radial-linear map gives

`dOmega_phys = det(A)^{-1} S^{-3} dOmega_q`.

For `a_i=a exp(beta_i)`, `sum beta_i=0`, put `r=|exp(-beta)n_q|`; then `S=r/a` and the angular Jacobian is `r^{-3}`. However,

`d^3p = det(A)^{-1} d^3q = a^{-3} q^2 dq dOmega_q`.

Therefore a full integral in conserved covariant momentum already contains the complete volume Jacobian; multiplying it by the separate angular Jacobian again is incorrect. The variable and measure of the transported array (`f`, spectral density, group count, etc.) must be identified before inserting any Jacobian.

For a physically isotropic emission event at `s`, use `D_i=a_i(s)/a_i(t)`, `n_s` its physical emission direction. Then `E_t/E_s=|D n_s|` and `dOmega_t=det(D)|D n_s|^{-3}dOmega_s`. Here the perturbative anisotropy is `Delta beta_i=beta_i(t)-beta_i(s)`.

### First-order scalar cancellation: precise scope

Write `Delta beta=lambda B`, with `tr B=0`. In an isotropic angular average,

`<n_i n_j>=delta_ij/3`, hence `<B_ij n_i n_j>=0`.

Given an isotropic initial photon distribution, isotropic physical source at every emission time, scalar absorption/response coefficients in the non-tilted gas frame, the same mean-scale-factor/gas baseline, and a differentiable transfer-and-response functional, its first variation is an angular contraction of a trace-free tensor history. Its angular mean vanishes. Spectrally, the same conclusion follows by perturbative order counting in S2 Eq.(70). This is a derived local cancellation theorem. It is not a data set, an atomic closure validation, or a proof of small finite-amplitude corrections.

An initially anisotropic source or photon bath independent of `lambda` supplies another tensor: `B_ij <n_i n_j>_source` need not vanish. If the source anisotropy itself is O(lambda), the mixed term is O(lambda^2), which must be stated rather than treating every anisotropic source as an O(lambda) violation.

### Threshold counterexample to an unconditional quadratic claim

Take physically isotropic monochromatic emission such that the isotropic reference arrival energy is exactly `E_th`. Let `Delta beta=(b,-b,0)`. At arrival,

`E/E_th = 1 - b(n_x^2-n_y^2) + O(b^2)`.

For an ideal excess-energy response `W(E)=(E-E_th)_+`, the angular mean obeys

`<W(E)> = (2/(3 pi)) E_th |b| + O(b^2)`.

Proof: `<|n_x^2-n_y^2|>=<sin^2(theta)><|cos(2 phi)|>=4/(3 pi)`; the positive and negative regions contribute equally at leading order. The cusp violates differentiability at `b=0`; trace-free geometry alone does not guarantee an O(b^2) scalar response. A discontinuous ionization threshold acting on a delta line can be still more singular.

For a smooth continuum spectrum, integrating the threshold correctly preserves first-order cancellation, including moving-boundary terms. Narrow lines require the anisotropic energy shift to be small compared with the spectral regularization scale for a uniform Taylor argument. Energy nodes exactly at thresholds can mimic a delta-line singularity; a grid test must distinguish this from continuum physics.

### Angular quadrature and history checks

For normalized weights, first-order cancellation for arbitrary STF tensors requires `sum w n_i n_j=delta_ij/3`; `sum w=1` and antipodal symmetry are insufficient. The leading second-order coefficient additionally requires the isotropic fourth moment

`sum w n_i n_j n_k n_l=(delta_ij delta_kl+delta_ik delta_jl+delta_il delta_jk)/15`.

For `r=|exp(-beta)n|` and trace-free diagonal beta,

`<r> = 1 + (4/15) tr(beta^2) + O(|beta|^3)`.

With `beta=(b,-b,0)`, the continuum is `1+(8/15)b^2+...`; six coordinate-axis nodes give `(exp(b)+exp(-b)+1)/3=1+b^2/3+...`. Thus this grid passes linear cancellation but underestimates the leading scalar coefficient by 37.5 percent.

Control smallness over the source/absorption memory interval using integrated shear, `Delta beta_i=integral_s^t sigma_i(t') dt'` in the fixed diagonal proper-time frame. A small instantaneous `sigma/H` or vanishing present shear does not alone bound the stored directional redshift. Different source times require their own physical-isotropy map.

## Status

Source identities and indicated equation/page portions were read through web retrieval on 2026-10-10. Algebraic statements in the diagnostic section are `derived`; no numerical experiment or implementation execution is claimed here. This note provides source support and scope challenges only. Final promotion belongs to a separate decision reviewer.
