# REI F4 physical-fast: original BASS193 chemistry F/J × conditional causal electron/thermal clock bridge

**2026-10-30; one bounded source-data auxiliary unit.** Parent chemistry: immutable REI PR278; first-flight radiation: PR287; rate-family cross-owner: PR276; Li6 static F/J: PR281; experimental Li1s branching: PR292. Original BASS AtomicNetwork owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. This analysis runs original BASS21 code with pinned 193 saved states; it does **not** solve a new ODE, evaluate a native REI17 Rust F/J, or modify an original PR. Isolation from the 2026-10-30 concurrent sibling PRs is intentional.

## Direct theoretical derivation (derived + CAS checked)

Baryon-counting conventions: original BASS21 `Y_i` is **number of ions/nuclei per baryon**, positive and normalized `A^T Y=1`, `q_i` is ionic charge, `n_b` in m^-3. Metric (-,+,+,+) and cosmic-proper-time `t` (seconds). The original reaction operator has `G0(T,UV)`, decay operator `D` and electron-collision/rec. generator `Gne(T)` (matrix rates in s^-1 or m^3/s in consistent owner units). At fixed T,UV,nb:

```
ne = nb*(q·Y)
F21(Y,T,UV,nb) = [G0(T,UV) + D + ne*Gne(T)] Y
J21 = G0 + D + ne*Gne + nb*(Gne Y)*q^T
```

The 17-state restriction excludes four BASS Li6 states, but it is **not** equivalent to native REI17. If the source generator does not directly move nuclei between this Li6 block and the retained 17 block, and all cross-block terms occur through ne, then

```
ΔF17 = nb*(q_Li6·Y_Li6)*(Gne_17,17 Y17)
J(17,Li6) = nb*(Gne_17,17 Y17) q_Li6^T, rank≤1
```

Proved symbolically for a general quadratic charge-coupled F with Wolfram residual matrix exactly zero; numerical maximum F17 residual 1.51e−31 /b/s, J17 residual 1.53e−28 s^-1 (includes independent frozen PR276 HHe parity). Maximum original Li6 omission in ne/nb: 2.2586209868e−14; largest 17x4 cross Jacobian max 3.0596290097e−15 s^-1.

## Thermal and clock port: explicit conditional rate, NOT physical gas temperature

Original BASS x=ln(a/a_ini), dx/dt=H. Crucially each causal arrival is integrated on saved **Δt_i = t_(i+1)−t_i**, rather than assigning local x/H as an identical clock. Causal first-flight event count ΔN_ion and primary kinetic ΔE_kin per original baryon are original PR287 values (baryon^-1 and eV/baryon). Local diagnostic rates:

```
S_e^(conditional)(i) = ΔN_ion(i)/Δt_i          [baryon^-1 s^-1]
Q_kin^(conditional)(i) = ΔE_kin(i)/Δt_i        [eV baryon^-1 s^-1]
N_thermal = Σ_j Y_j + q·Y                       [number/baryon]
Cv,b = 3*k_B*N_thermal/2                       [eV baryon^-1 K^-1]
Θ_kin(i, ε=1) = Q_kin(i)/Cv,b                  [K/s]
```

`Θ_kin` assumes all primary electron kinetic energy is deposited as heat instantly, **for plotting coefficients only**. The electron-loading term `−T*S_e/N_thermal` is also a diagnostic only if injected primary electrons thermalize in the same ideal monatomic electron+baryon fluid. A physical temperature evolution further needs the cross-source consistent primary+secondary electron spectrum, deposition fractions ε(E,x_e), energy escape/line channels, chemical potential, recombination/ionization energy, thermal cooling, and correct Bianchi shear/K and density reference. **Do not add these ports to F21** because original photoevents already contribute there; this would double-count ionization. No CMB τ, true gas heat or full radiation transfer is inferred.

## Actual computed data on source-owned histories

- Source-locked input archives: PR278 BASS193 ZIP SHA `df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db`, PR276 cross-bath SHA `58815601324ade9871077236dccee25cbbfe126141ee9af3d7da9ed9ffdb56f2`, PR287 causal SHA `cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef`. Native original trajectory SHA `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`.
- Original BASS21 193 states, 4053 F components and 85113 J matrix cells; 193 stored electron/thermal/UV/background source rows; causal arrival electron and photon energy on 192 original proper-time bins; 7 separately owned REI17 clock snapshots. `NO_NEW_IVP`.
- Baryon normalization max `|A^T F|=4.55e−32/b/s`, max `|A^T J|=2.12e−24/s`; nb*a^3 relative span 2.19e−16 and saved ne from q·Y max relative residual 3.56e−16.
- Four independent numerical directional finite differences of native analytic Jacobian: relative residual ≤2.66e−16 (source-preserving local test, not a distinct-author blind review).
- Source BASS21 electron rate `∫ q·F dx/H=0.877305447227` per baryon vs observed saved 0.877305456813, difference approximately 9.59e−9 due finite archived sampling. The difference is **not** a physical additional electron source.
- The conditional PR287 photon-pair first-flight cumulative absorptions = 5.183362629197418e−11/b; summed primary photoelectron kinetic energy = 7.997916399993969e−10 eV/b; binding energy 9.585049280055294e−10 eV/b. Max interval Q_kin = 2.9613366273550195e−25 eV/b/s. Max heat-equivalent operator Θ_kin at ε=1 is 1.6640507797144296e−21 K/s. Numerical sum of Θ_kin*Δt = 4.443963036e−6 K **only a source-port integral**, not ΔT of physical gas.
- Seven REI saved history points differ from BASS interpolated proper elapsed time at matched z by ~0.21–0.45%; their initial conditions and background owners are not shown identical. **No claim of a clock bug nor correct shared clock**.
- Five actual source-backed figures: electron chemical sources, causal absorbed primary/binding energy ports, thermal operator equivalents, Li6 Jacobian cross block, REI/BASS separate clock comparison.

## One bounded same-author hostile audit and retained blockers

1. **Source mixing:** PR276's REI Grackle H/He was Python translated from original Rust; native Rust REI17 F/J not actually run. Correct interpretation is BASS21 source and REI-vs-BASS HHe static comparison, **not common physical F/J closure**.
2. **Input light cone:** PR287 emitted hypothetical all-singlet LiII photons through fixed isotropic FLRW-proxy opacity. The BASS background anisotropy `b` and H are real saved, but no directional Bianchi photon transport, angular time shear, or K is bound.
3. **Thermal closure:** observed `primary_e` is initial kinetic energy, not secondary-deposited heat. ε=1 heat equivalent overestimates potential heating and is not an error bar; energy partition/escape unknown.
4. **Source double counting:** the original chemistry already contains photoionization. The post-processed causal photon channel cannot be inserted as a second chemical source without a calibrated replacement operator and source subtraction.
5. **Clock semantics:** the 7 REI saved history points do not establish common H,nHref/nb, initial conditions or matter content; clock differences do not identify code defects.
6. **REI17 and independent author:** no full REI17 native Rust solver or distinct-author R6/C9 execution. Own hostile review is one same-author review only.

Inferred admission: auxiliary data bridge **1/1 scoped complete**, main Working **33/88**, Central **28/88**, physical fast **4/7**, canonical delta **0**, `F4=PARTIAL`, `L4_ready=false`, `PRODUCTION=HOLD`, `NO_MORE_IVPS=true`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `NO_BUDGET_RESET=true`, `AUTO_NEXT_NODE=false`. No proof of physical F4 closure.

## Literature and missing exact sources

- Drake, Victor, Dalgarno (1969), *Phys. Rev.* **180**, 25–32, Table II p29, DOI 10.1103/PhysRev.180.25; now 21/21 direct visual verified in siblings PR290/291. Source one shape.
- Ferrett et al. (1987), *Phys. Rev. A* **36**, 3172–3183, Table II/III direct ratios, DOI 10.1103/PhysRevA.36.3172; PR292 directly-source-weighted n2/n3. Need full-energy state-resolved singlet 1S vs adjacent 3P and instrument response.
- Langer et al. (1991), *Phys. Rev. A* **43**, 1652–1655, DOI 10.1103/PhysRevA.43.1652, Fig3 and Fig4 measured state-specific branching curves but not machine-tabulated in currently held original. Request author data or properly image-digitize with explicit errors, not handwritten exact values.
- L. Vo Ky et al. (1998), *Phys. Rev. A* **57**, 1045, DOI 10.1103/PhysRevA.57.1045 (R-matrix source over 130 eV with partial cross sections). Need source complete table/alternative dataset and original covariance.
- S. R. Furlanetto & S. J. Stoever (2010), *MNRAS* **404**, 1869–1878, DOI 10.1111/j.1365-2966.2010.16401.x: electronic tables of fast-electron heating/ionization/excitation fractions depend on E,x_e, valid primordial H/He set. Exact electron-spectrum kernel and applicability to Li isotopes remain to be qualified; no fraction has been imported.
- CHIANTI `continuum/heseq_2photon.dat` original Z3 data, official NASA mirrors; raw bytes not acquired; source 1969 Drake spectral shape and Drake1986 A rates not equal without normalization.