# REI F4 | Direct Ferrett singlet upper -> source-owned BASS193 frozen causal 2E1
2026-10-30 | Parent PR293 SHA `fd9385f131f93dae2868bbb50b6a542f09dd870b`

## Original scientific identity and model
- Source BASS owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`; PR292 SHA `8219c0be13093d64da1b50e75854260975bc4384`.
- Original conditional causal kernel is nested PR287 from the private PR293 master. 193 saved epochs, 18,528 original causal emission/arrival pair rows, 2 lithium isotopes, 3 actually measured native energies (81.85233848, 86.70882056, 91.85344858 eV).
- Primary source Ferrett et al., *Phys. Rev. A* **36**, 3172 (1987), DOI 10.1103/PhysRevA.36.3172. Use only DIRECT Table II R31 and Table III R32 on 80–92.5 eV, NOT model-derived Table IV numerators with assumed Rp.
- Define `r=R31=σ(3S)/[σ(1S)+σ(1P)+σ(3P)]` and `t=R32=σ(n3)/σ(n2)`. Within **n2+n3 residual core subset**, `f3S=r/((1+r)*(1+t))`, `fn2_rest=1/((1+r)*(1+t))`, `fn3=t/(1+t)`. Their sum is 1. Actual pure singlet `0<=f1S<=fn2_rest`; there is no justified positive lower bound.
- Original native BASS `K_native` event source cross section is **NOT** established identical to the measured `n2+n3` laboratory denominator. `alpha(E)=sigma_exp(n2+n3)/sigma_BASS(K_native)` remains UNBOUND; `alpha=1` here is a consciously **conditional** source projection, NOT physical closure.
- Within native measured window only, per saved `x=ln(a/a_ini)` emission node `k`, `B_k=(Simpson_weight_k/H_k)*K_rate_k*f1S_k` in emitted 2E1 photon pairs/baryon; preserve `0<=B_k<=B_k_upper`.
- Original PR287 nonnegative frozen 2E1 kernel `K^X_jk` sends emitted pair at `k` into first-flight absorption, primary photoelectron, binding, cosmological redshift, survivor at arrival interval `j`. New source-weighted results `N^X_j=sum_{k<=j} B_k*K^X_jk`. This is **not** a new photon IVP or true REI17 chemistry source; positivity gives componentwise upper only for these selected modeled photons.
- Separate M1 triplet *vacuum radiation capacity* does not propagate through the original 2E1 kernel. Current primary kinetic energy != actual deposited gas heat; `epsilon=1` instantaneous `Q/Cv` is diagnostic only, no thermal evolution.

## New additional exploratory state resolution, NOT admitted
Langer et al., *Phys. Rev. A* **43**,1652 (1991), DOI 10.1103/PhysRevA.43.1652 Fig3 measured three ratios. We manually read 30 graph markers at 320 dpi, without publisher machine data, calibrated covariance or instrument response. Define `A=sigma3S/sigma1S`, `B=sigma1P/sigma1S`, `C=sigma3P/sigma3S`. Using Ferrett direct `f3S` and `f_rest`, exploratory `f3P=C*f3S`, `f1S=(f_rest-C*f3S)/(1+B)`, `f1P=B*f1S` provided `r*C<=1`; this yields identity `A_expected=r*(1+B)/(1-r*C)`. Cross-paper A consistency is NOT guaranteed; do not impose numerical Langer values as physical data input without measured covariances and a response map.

## Immutable progress and release gates
WORKING 33/88, CENTRAL 28/88, F4_FAST 4/7, canonical physical delta 0. New self-contained auxiliary source-scoped node 1/1 only; F4=PARTIAL; L4_ready=false; PRODUCTION=HOLD; NO_MERGE; NO_FORCE_PUSH; NO_MORE_IVPS; AUTO_NEXT_NODE=false. Independent distinct-author R6/C9=NOT_RUN. Source PDFs and full original ZIPs are private and not uploaded to GitHub.
