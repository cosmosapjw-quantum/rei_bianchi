# F4 source-common theory: bounded Li II 2E1 causal photoionization on frozen REI H/He thermochemistry

**Selected bounded cycle:** R1–R10 + C1–C10, one science unit. Baseline PR295 `eb0fbebd3779dfa208bace2785e5e0b3e957ab96`; disjoint PR294 `43b8064a2e3122f9d3787f2a08f94b6b614b422a` used as immutable input without merging. Metric (-,+,+,+), c and k_B retained, proper seconds, energy eV and erg, atomic Y_i=n_i/n_b, x=ln(a/a_ini). No new IVP, transport or source-owner mutation.

## Original primary literature and identity

Ferrett et al., Phys. Rev. A **36**, 3172–3183 (1987), DOI `10.1103/PhysRevA.36.3172`: the directly measured ratios R31,R32 (only overlapping 80–92.5 eV) constrain `1s2s ^3S`, n=2 nontriplet **sum**, and n=3. They do NOT directly measure separate `1s2s ^1S` vs `1s2p ^3P`. Langer et al., Phys. Rev. A **43**, 1652–1655 (1991), DOI `10.1103/PhysRevA.43.1652`: resolved term structure exists as figures, but previous manual figure digitization is EXPLORATORY and excluded. Drake, Victor & Dalgarno, Phys. Rev. **180**, 25–32 (1969), DOI `10.1103/PhysRev.180.25` supplies the Li II 2E1 spectral-shape source for PR287/294.

Furlanetto & Stoever, *MNRAS* **404**, 1869–1878 (2010), DOI `10.1111/j.1365-2966.2010.16401.x` model secondary electron heat/ionization/excitation for H/He and electron energies >10 eV; **no source-owned deposition table is imported in this cycle**. Grackle 3.4.1 documentation `https://grackle.readthedocs.io/en/grackle-3.4.1/` describes the H/He photo-chemistry/cooling family, while actual PR295 source ownership is a Python translation of repo-pinned REI Rust, not an assertion that external Grackle alone certifies the implementation.

## 1. Conditional source and causal point mapping

Let `j=0...191` be saved-BASS redshift intervals, with original proper duration `Δt_j>0`. PR294 supplies the **upper** conditional first-flight 2E1 photon absorption events per original baryon `N_{jH},N_{jHeI},N_{jHeII},N_{jLi}` and energy `Ekin_j` eV per baryon. They are all conditional on (i) assigning the entire unseparated Ferrett n2 remainder to singlet, (ii) 1σ rectangular lab-error envelope not representing a joint confidence region, (iii) native BASS K-shell event denominator equated with experimental n2+n3 subspace and the same natural-Li fractions applied to Li6 and Li7, (iv) frozen isotropic-mean PR287 first-flight transport.

Define `r_{js}=N_{js}/Δt_j` in baryon^-1 s^-1, and `h_j=n_Href/n_b` (dimensionless) from original PR295 saved BASS H abundances. The **formal external injection** to the 5 species `Y5=(Y_HI,Y_HII,Y_HeI,Y_HeII,Y_HeIII)` is

```
ΔF5_j = (-r_H, +r_H, -r_HeI, r_HeI-r_HeII, +r_HeII).
A_H=(1,1,0,0,0), A_He=(0,0,1,1,1), q=(0,1,0,1,2).
A_H·ΔF5=A_He·ΔF5=0, q·ΔF5=r_H+r_HeI+r_HeII.
```

`LiI` absorption is recorded separately, never inserted into HHe F5. Per Href electron source `e_j=(q·ΔF5)/h_j` in Href^-1 s^-1. The actual REI17 photo-rate Jacobian is **not** `∂F/∂Y` of this frozen prescribed source: the photon histories are nonlocal functionals of absorber states and the original REI17 closure is unavailable. This is an evaluated conditional photo-port, NOT a new REI17 native F/J, chemistry evolution or additive modification of original BASS photon gamma.

## 2. Source-native energy and thermal EOS envelope

The BASS original HHe thresholds are chi_B=(13.6,24.59,54.42) eV; the PR295 source-translated REI HHe thresholds are chi_R=(13.598434599702,24.587389011,54.41776) eV. The HHe **source-owner defect** per baryon is precisely

```
ΔE_binding,j = (N_H,N_HeI,N_HeII)_j · (chi_R-chi_B).
```

Keep it signed instead of silently claiming identical absorbed-photon operators. The parent energy includes LiI binding and is not equated to the HHe-only binding sum.

On frozen left-endpoint BASS backgrounds `T_j,n_Href,j,n_He,j,n_e,HHe,j`, let `eta_j=(n_Href+n_He+n_e,HHe)/n_Href` and `Cv_Href=(3/2) k_B eta_j` [erg / Href / K]. The maximum available **primary photoelectron** kinetic power per Href is conservatively

```
Q_primary,j^upper = Ekin_j (1.602176634e-12 erg/eV)/(Δt_j h_j),
ΔTdot_heat_coeff,j = Q_primary,j^upper/Cv_Href,j,
ΔTdot_electron_loading,j = -T_j e_j/eta_j.
```

Note `Ekin_j` includes the negligible LiI primary electron energy: it therefore safely **overestimates** the energy available to HHe for heating. No heat-deposition efficiency or secondary electron transport is defined by these equations. At fixed maximal-source event counts, a unit-efficiency diagnostic coefficient is `ΔTdot_heat_coeff + ΔTdot_electron_loading`, not an integrated ΔT.

## 3. New energy-limited secondary-ionization envelope (derived)

If secondary electron collisions draw no further external energy and partition Ekin among heat, excitation, escape and additional H/He collisional ionizations, each extra H/He ionization costs at least chi_HI^REI=13.598434599702 eV. Hence the nonnegative energy cone

```
0 <= N_secondary,HHe,j <= Ekin_j/chi_HI^REI.
0 <= E_heat,j <= Ekin_j - chi_HI^REI N_secondary,HHe,j.
```

The RHS is a relaxed energy-only ceiling: no prediction of the secondary species partition, discrete-event attainability, background density or Monte Carlo yield. If actual singlet source is below the PR294 envelope, all absolute budgets decrease accordingly. For the maximal PR294 source, no-deposition or secondary models imply an absolute conservative **point RHS** bracket

```
 -T_j [e_j + Ekin_j/(chi_HI^REI Δt_j h_j)]/eta_j
    <= ΔTdot_j <= Ekin_j * erg_per_eV /(Δt_j h_j Cv_Href,j).
```

This deliberately weak envelope is valid for nonnegative heat fraction and nonnegative secondary ion counts with no independent energy source. It does **not** include radiative hydrodynamics, recombination feedback, Compton, or the unknown secondary photon transport. PR295 already includes original BASS HHe photo gamma, so adding this source to native F/J requires proving the LiII 2E1 line photons are not already represented; we do not perform that insertion.

## 4. Source identity, results and decision

Inspect `results/RESULT.json` for numerical output, `results/LI2E1_HHE_CAUSAL_SOURCE_192.csv` for all 192 real saved intervals, and `results/PLOT01–06*.png` for actual scientific figures. All source-owner assumptions and negative controls are explicit in the pre-registered objective and audit.

**Admission:** source-scoped *derived* chemical stoichiometry, thermal RHS coefficients, threshold mismatch and energy-only secondary-ionization upper. **Not admitted:** genuine source-common REI17/BASS21 F/J, secondary deposition, observed temperature, CMB optical depth, anisotropic radiation transfer, production. Working DAG 33/88, central 28/88, F4-fast 4/7, canonical physical delta 0. New auxiliary work unit 1/1 scoped; production HOLD.
