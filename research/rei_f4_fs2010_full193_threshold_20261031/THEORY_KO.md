# REI F4 | Furlanetto–Stoever 저에너지 terminal response의 전체 BASS193 원본 source

## Authority, scope and claim

- Repository: `cosmosapjw-quantum/rei_bianchi`, immutable parent Draft PR #300 HEAD `0e9024f92682bc3b7a0080cc86855cbddca8b0d9`.
- Original BASS21 owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`; nested frozen PR287→PR294→PR297 first-flight. Read-only siblings PR #296, #298, #299 remain unmerged.
- Reference papers in the private source archive: T. A. Ferrett et al., *Phys. Rev. A* **36**, 3172 (1987), DOI `10.1103/PhysRevA.36.3172`, Tables II–IV; B. Langer et al., *Phys. Rev. A* **43**, 1652 (1991), DOI `10.1103/PhysRevA.43.1652`, Fig. 3; S. R. Furlanetto and S. J. Stoever, *MNRAS* **404**, 1869 (2010), DOI `10.1111/j.1365-2966.2010.16401.x`, §§2,7, p.1876 Table 1.
- Frozen BASS193 chemical/radiation background, metric signature (-,+,+,+), c explicitly in `λ=c n_b Yσ/H`; no new IVP, no production injection, no full directional Bianchi photon transport.

## Exact substep derivation within original fixed-hazard approximation

For emitted Li II singlet 2E1 epoch k and arrival ln(a) cell j, the two correlated photon energies are (y E_line,(1-y) E_line), integrated with original paired 16-point spectral weights. Within a PR287 substep of width `d=Δ ln(a)/4`, take original frozen hazard `λ>0`, target share `p_i≥0`, survivor `S≥0`, initial photon energy E0, absorber ionization threshold χ_i. Redshifted energy at u is E(u)=E0 exp(-u).

The expected first absorption count and produced primary-electron kinetic energy are

    N_i[a,b]=S p_i (exp(-λ a)−exp(-λ b))
    K_i[a,b]=S p_i [E0 λ/(λ+1)(exp(-(λ+1)a)−exp(-(λ+1)b)) − χ_i (exp(-λ a)−exp(-λ b))].

These follow by directly integrating the differential first-flight hazard S p_i λ exp(-λ u) du and multiplied kinetic energy E0 exp(-u)−χ_i. The electron-energy cut E_e<T corresponds to u>ln(E0/(χ_i+T)), clipped into the substep. Five disjoint electron-energy ranges are `<10.2`, `[10.2,13.598434599702)`, `[13.598434599702,24.587389011)`, `[24.587389011,54.41776)`, `≥54.41776` eV. Bin differences telescope exactly to the original first-absorption N_i and K_i. Wolfram symbolic partition/derivative checks were 4 exact zeros.

The first threshold is the Furlanetto–Stoever 2010 **model terminal heating convention**. Their actual continuous plasma model assumes eventual loss of sub-10.2eV electron energy to heat. This is not an independently measured instantaneous thermalization rate in very tenuous anisotropic gas, and it is **not a positive lower bound on actual Li II 2E1 radiation** because the source itself is conditional upper based on Ferrett laboratory channel ratios.

## Full 193-source reconstruction

The original PR300 computed 30 emission epochs capturing 99.4806418% of potential singlet source and bounded the rest. We independently evaluated the remaining 162 active emission epochs (14 immutable chunk datasets), added the 30 verified parent epochs, and reinstated the original first epoch k=0's exactly zero-emission plane (192 zero rows). Last emission epoch k=192 has a tiny nonzero conditional emitted source but no later first-flight arrival interval on the fixed saved history. Result: all 193 sources accounted for, all 18,528 original emission–arrival index pairs and all 192 arrival intervals represented. Never confuse source emission coverage with effective first-absorption events.

- Full conditional photoelectron kinetic budget: 6.749242464433259e-11 eV per original baryon.
- FS-model terminal <10.2eV kinetic energy: 8.581099847924098e-12 eV/baryon, fraction 0.12714167394554643. This closes the previous top30 [0.12654292813,0.13149949580] bracket **within original 16-point/4-substep discretization**.
- H I, He I, He II and Li I photon counts reproduce original parent kernel; full totals relative error `≤4.44e-16` vs PR297 by independent source sums.
- Previous per-photoelectron relaxed bound N_secondary ≤ E_total/χ_HI = 4.963249567403269e-12 per baryon; new full-source energy-threshold count bound 2.943495108593608e-12 per baryon. The rare Li I possible fourth H secondary is preserved with a *conservative* Li I-event addendum 2.905527545664037e-19/baryon; this is not the exact fourth-collision yield. No external electron heating is added.

## Frozen thermal/EOS coefficient

Reuse PR297 source-specific HHe proper intervals Δτ_j, nHref/nb_j and Cv_j without modifying any native source:

    Qdot_terminal,j = (Eterminal,j [eV/baryon]) * (1.602176634e-12 erg/eV)
                       /((nHref/nb)_j * Δτ_j) [erg/Href/s]
    Tdot_terminal_coefficient,j=Qdot_terminal,j/Cv_j [K/s].

For the conditional maximum source, integrated Σ_j Qdot_j Δτ_j=1.8210951142160422e-23 erg/Href; maximum point coefficient=1.770297769640156e-23 K/s. These are static coefficients on the prescribed saved background, **not actual ΔT, evolved gas energy, secondary cascade deposition, or completed native REI17 source replacement**. Electron-loading and photo/UV source double counting remain separate. Native original H/He thermal input is not overwritten.

## Critical unresolved physical source ownership

1. Ferrett's lab n=2+n=3 denominator is not proven the same as original BASS K photoevent operator, including Li6/Li7 isotopes. Hence all amplitudes remain CONDITIONAL MAX-SINGLET only, true lower singlet zero.
2. Langer Fig.3 resolves neutral-Li 1s 1S/3P but has no supplied full channel covariance or original numeric marker list. Do not promote exploratory digitization to exact data.
3. Full Furlanetto–Stoever E_e×x_i deposition tables and C interpolator have been located on the official group page at `https://cosmicdawn.astro.ucla.edu/codes_and_tools.html`, direct download `https://cosmicdawn.astro.ucla.edu/elec_interp.tar`, but download failed in this execution environment. Their Table 1 is 3-keV only; do not apply to few-tens-eV photoelectrons.
4. Frozen original BASS193 source and REI17 full chemistry and H/K/clock share no validated same-IC 17-state dynamical trajectory. PR296/298/299 sibling inputs remain independent. No production.
5. Original 16-point spectral quadrature and 4 substeps have known representative sensitivity ~0.68% to quadrature order; this new exact **finite-grid** result is not an error certification for continuum transport.

## Validation and DAG

Independent whole-kernel code test checks 18,528 emission–arrival indices and unweighted-by-source parent cross sections after correct source weighting, two-photon normalization, energy closure, source positivity, zero-first epoch and endpoint handling, HHe normalization and source boundaries. Tests 16/16 PASS. This is one bounded research unit with same-author adversarial review, **not** genuine distinct-author R6/C9.

Working DAG 33/88; Central 28/88; F4-fast 4/7; canonical physical delta 0; new auxiliary 1/1_SCOPED. F4 PARTIAL; L4_ready false; production HOLD; no merge/force-push, no automatic next node.
