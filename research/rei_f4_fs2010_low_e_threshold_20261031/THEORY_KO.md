# REI F4: Li II 2E1 최초 광흡수의 저에너지 전자 문턱별 분해

## Authority and scope
- Parent: `cosmosapjw-quantum/rei_bianchi`, Draft PR #297, `0f41c8f0d3ddc7f8af67765f09cd37ae885768bf`.
- Read-only sibling: PR #296 native Rust H/He point RHS, `b89069aae6866d58f63822d072f98cf424ec5370`; independent branch, **not merged**.
- Science owners: original BASS21 `cc602e209e7deeb511ab2a1f3b2268d55206c43c`, frozen PR287 causal photon kernel and PR294 singlet upper. Parent PR297 original source is byte-locked in private ZIP.
- Inputs from user original PDFs (private): Ferrett et al. *Phys. Rev. A* **36**, 3172–3183 (1987), DOI 10.1103/PhysRevA.36.3172, especially Tables II–IV; Langer et al., *Phys. Rev. A* **43**, 1652–1655 (1991), DOI 10.1103/PhysRevA.43.1652, especially Figs. 2–3; Furlanetto & Stoever, *MNRAS* **404**, 1869–1878 (2010), DOI 10.1111/j.1365-2966.2010.16401.x, especially §§2,7 and Table 1.

## Definition and derivation

Let `x=ln a`, `k` be emitted singlet 2E1 epoch, `j` an arrival interval, and `E0_p ∈ {y E_line,(1-y) E_line}` for a 2E1 pair. The original PR287 effective-mean background fixes `E(u)=E_start exp(-u)` with `u=x-x_j`, photoabsorber state population `Y_i`, and constant subinterval optical hazard `λ=c n_b Y⋅σ(E_mid)/H` in units of `dln a` (metric signature `(-,+,+,+)`; `c` kept). `χ_i` is the original BASS21 threshold **for that absorber state** (not the REI Grackle binding-energy owner).

At the beginning of substep, surviving photon fraction `S`, per-target hazard share `p_i=(n_b Y_i σ_i)/Σ_m(n_b Y_m σ_m)`, width `d`, and emitted line energy `E_start` define the exact *within this frozen-hazard substep* cumulative absorption and electron kinetic energy:

\[
N_i[a,b]=S p_i e^{-\lambda a}(1-e^{-\lambda(b-a)}),
\]
\[
K_i[a,b]=S p_i E_{\rm start}\frac{\lambda}{1+\lambda}
 e^{-(1+\lambda)a}(1-e^{-(1+\lambda)(b-a)})-\chi_i N_i[a,b].
\]

For a photoelectron threshold `T_e`, the kinetic condition `E_start exp(-u)-χ_i < T_e` holds for `u > ln(E_start/(χ_i+T_e))`. Set
`u_* = clamp(ln(E_start/(χ_i+T_e)),0,d)`. Then `N_<T=N_i[u_*,d]`, `K_<T=K_i[u_*,d]`. All categories are disjoint under the original quadrature, and telescoping interval sums recover original PR287 count and kinetic energy exactly up to roundoff. Both 2E1 photons must be included using the original paired weights `w_y`, not twice the one-photon mean.

The measured-window source weights for emission epoch `k` are **not re-estimated**: take `P_k = PR294.measuredwindow_2E1_emitted_pairs_rectangle_upper`, and sum `Σ_k P_k N_{i,kj}` for each arrival `j`. This is a conditional *upper-envelope* operator. Ferrett's directly measured `R31, R32` do not fix pure `1S` positively, and `σ_K^(BASS)` has not been proven equivalent to the laboratory `σ(n2)+σ(n3)` denominator. Langer Fig. 3 is separated but untabulated and its digitization remains exploratory, not used to invent the source normalization.

### Furlanetto–Stoever physical partition

Furlanetto & Stoever (2010), §2, treat **sub-10.2 eV** electrons as depositing all their remaining energy as thermal energy in a prescribed static primordial plasma. Their Monte Carlo high-energy input covers 10–9900 eV with ionization-dependent fractions and cascade tracking. The 3 keV Table 1 does not describe these few-tens-eV photoelectrons. We therefore admit only the local model assignment `f_heat(E_e<10.2eV)=1`, subject to the paper's energy-loss/instantaneity approximations; no empirical `f_heat(E_e≥10.2eV)` is asserted. The Furlanetto–Stoever tabulated 2D data and C interpolator are *not available* in this execution.

Define `Q_<10.2 = Σ_p,i,k,j P_k ∫_{E_e<10.2} E_e dN`. If we compute only a subset `K` of source epochs, then positivity gives a source-conservative bracket (at the fixed original PR287 quadrature):

\[
Q^{K}_{<10.2}\leq Q^{\mathrm{all}}_{<10.2}
\leq Q^{K}_{<10.2}+E_{\mathrm{primary}}^{\mathrm{all}}-E_{\mathrm{primary}}^K.
\]

The second term is read from the **immutable PR297 total energy** and independently checked against recomputed PR287 total energy for the selected epochs. This is a conditional-model bound, not a bound on real kinetic thermalization in arbitrary Bianchi I gas.

For H I secondary collisional ionizations, each costs at least `χ_HI^REI=13.598434599702 eV`. The old continuous bound `E_total/χ_HI` ignores the discrete per-electron threshold. A stronger bound is

\[
N_{\mathrm{sec,HI}}\leq\sum_{k,p,i,j}P_k\left\lfloor\frac{E_{e,kpij}}{\chi_{\rm HI}}\right\rfloor,
\]

with the floor integrated **before** averaging. The selected kernel records the `n=1..3` threshold indicators per photoelectron. For H/He original photon absorbers, `E_e ≤ E_line-χ_HI ≈47.324 eV <4χ_HI` and only these three suffice. For rare Li I absorptions, `E_e` can reach `E_line−5.39 ≈55.533 eV`; therefore a *fourth* H secondary ionization is kinematically allowed and must not be silently discarded. We add the strictly conservative selected Li I primary count for this fourth term. For the uncomputed source, add `min(E_miss/χ_HI,4N_miss)`.

**Critical counterexample:** H/He-absorbed Li II 2E1 photons cannot directly yield an electron above the He II collisional ionization threshold of ~54.418 eV. However rare **Li I absorber** photoelectrons can; the selected 30-epoch original source yields a positive tiny tail. It would be false to set the all-absorber He II secondary channel to zero.

## Source shape, conservation, numerical scope

The PR287 redshifted first-flight calculation uses the effective isotropic mean `a(t)` with frozen saved `H, n_b, Y_i`, a 16-point 2E1 spectral quadrature and four substeps in `ln a`. This is not the full Bianchi directional transport. No new IVP is solved, and the new source is **not added** to native REI17/BASS chemistry. Energy conservation, paired-photon counting and per-category photon/kinetic-energy sums are checked directly against the immutable 18,528-row PR287 kernel.

One representative emission epoch `k=71` gave a relative change in the low-energy threshold-weighted source of `+0.00677914` for quadrature order `16→24` (substeps fixed at 4), and `-0.00036731` for substeps `4→8` (order fixed at 16). This is an explicit *numerical sensitivity*, not an interval-certified continuous-model truncation bound. Full order/substep convergence for 193 epochs is not asserted.

## Model status

`WORKING=33/88`, `CENTRAL=28/88`, `F4_FAST=4/7`, `CANONICAL_DELTA=0`; new `AUXILIARY=1/1_SCOPED`. `F4=PARTIAL`, `L4_ready=false`, `PRODUCTION=HOLD`, `NO_MORE_IVPS`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`. Same-author hostile checks only, distinct-author R6/C9 NOT_RUN, native subagent NOT_RUN.
