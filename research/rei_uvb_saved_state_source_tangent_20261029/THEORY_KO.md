# REI UVB photo-source to frozen 17-state chemical tangent

2026-10-29 | `REI_UVB_SAVED17_SOURCE_TANGENT_20261029` | Derived + numerically checked + implementation-verified **scoped**. Native different-author R6/C9 `NOT_RUN`.

## 1. Original model, domain and provenance

- Owner source `rei_bianchi` PR248/251: `research/rei_external_sources_20261028/implementation/model.py` Git blob `1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc`, `FAMILIES`/`photo_atom_{family}_{q}` event transitions. This is a *typed extraction* of its 17 heavy-state topology, not a raw-byte copy of the entire source file.
- Saved `ON_refined` 361-epoch source CSV Git blob `189c2d903e25c18bee49e0ab6add3ba1d1805e93`. Seven selected rows from this original were compared by 17-significant-digit canonical numeric representation, FNV-1a64 `174743cb945f8bfe`, length 3059. This is **numerical content identity of 7 rows**, not byte identity to the original full CSV.
- Parent PR261 `8a3107a6477a648ad87a4db2a52240c1bea4cc42` supplies pinned BB13 input SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b` and Puchwein 13-row projection SHA256 `dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff`, with P19 parent Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`.
- Only saved `z_mean` in `[2.4,4.75]` is evaluated; `z=4.7574357` is excluded and the next lower saved point `4.7016901` is used. This is a normal-frame **mean-redshift** argument, not a direction-dependent observed redshift.
- `ON_refined` 17-state population is a **prescribed-bath trajectory under a different, uncalibrated source**. Every calculation below holds that saved state fixed while inserting the P19 conditional source. It is NOT the response of a self-consistent REI evolution to changing the UVB.

## 2. Definition and stoichiometry

Let `y in R_+^17` be the original populations per H reference, with labels `(n,H1_0,H1_1,D_0,D_1,T_0,T_1,He3_0,He3_1,He3_2,He4_0,He4_1,He4_2,Li7_0,Li7_1,Li7_2,Li7_3)`. The seven photoionization transitions are

1. `H1_0 -> H1_1`, `D_0 -> D_1`, `T_0 -> T_1` using P19 `Gamma_HI` and original 13.6 eV threshold;
2. `He3_0 -> He3_1`, `He4_0 -> He4_1` using P19 `Gamma_HeI`, threshold 24.6 eV;
3. `He3_1 -> He3_2`, `He4_1 -> He4_2` using P19 `Gamma_HeII`, threshold 54.4 eV.

The H/D/T and He3/He4 rate equalities are **explicit old-model approximations**, not separate empirical isotope calibrations. Li7, hidden Li6, nuclear/CR, recombination, fast stocks and old donor radiation remain untouched.

Let `S in Z^(17x7)` have one `-1` at each event's source and `+1` at its destination. Let `E in {0,1}^(7x17)` select source populations and `P in {0,1}^(7x6)` select the three ionization-rate columns of the six moments `R_6=(Gamma_HI,heat_HI,Gamma_HeI,heat_HeI,Gamma_HeII,heat_HeII)`. Define `lambda=diag(E y) P R_6`. Then the **photo-only** generator is

    F_UVB(y,z,a) = S diag(E y) P R_6(z,a).

At fixed `z` and `a`, the exact partial derivatives are

    J_y^UVB = S diag(P R_6) E       (17x17)
    J_R^UVB = S diag(E y) P         (17x6).

The P19/BB13 conditional common scaling `R_6(z,a)=R_6^P19(z) 10^(t(z)^T a)` with `a=(beta,kappa)`, `t(z)=(1,z-3.6)` yields

    B_a^UVB := D_a F_UVB = J_R^UVB D_a R_6
             = (ln 10) F_UVB t(z)^T.    (17x2)

**Rank theorem:** At each fixed redshift, `rank(B_a)<=1`. If two saved redshifts differ and both corresponding `F_UVB` are nonzero, the vertically stacked two-epoch matrix has rank 2. Proof: if a two-vector lies in the kernel, `t(z_i)^T v=0` for both distinct `z_i`; these two rows are independent. This is structural identifiability of the *source forcing*, not observational Fisher information or dynamical parameter identifiability.

## 3. Conservation, electron source and positivity

With the original first-17 baryon weights `A17=(1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7)` and charge weights `Q17=(0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3)`, exact integer identities give

    A17^T S = 0,  1^T S=0,  Q17^T S=1_7^T.

Hence photoionization preserves heavy nuclei and total heavy-state count, but produces one free electron per event. The instantaneous source of free electrons *per Href* is

    e_dot_UVB = Q17^T F_UVB = sum_k lambda_k >=0,
    D_a e_dot_UVB = (ln 10) e_dot_UVB t(z)^T.

The photo-only `J_y` is Metzler with zero column sums, so its unweighted 1-norm logarithmic norm is exactly `mu_1(J_y)=0` and its homogeneous positive evolution is 1-norm nonexpansive. For the **photo-only** variational equation `v'=J_y v+B_a delta_a` (with all other chemistry frozen),

    ||v(t)||_1 <= ||v(t0)||_1 + integral_(t0)^t ||B_a(s) delta_a||_1 ds.

This is an analytical conditional bound, not a physical whole-system error radius. Adding recombination, nuclear events, external injections, density feedback, or geometry changes the Jacobian and requires a new lognorm.

## 4. Energy ownership and nonlinear nuisance envelopes

For each event k, retain the old-model threshold `I_k` and the corresponding P19 per-target photoheating moment `h_k` (eV/target/s):

    E_ion_dot = sum_k I_k lambda_k,
    E_excess_dot = sum_k y_source,k h_k,
    E_abs_dot = E_ion_dot + E_excess_dot.

All three are eV/Href/s. The P19 excess photoheating is an **energy port**: it cannot be silently added to the old pilot `heat` or `fast_electron` ledger without a specified deposition/thermalization rule. `E_abs` is the sum, not an additional energy injection. At fixed y, their `D_a` are the same `ln10 * value * t` structure.

The PR260 joint nuisance set `U_q=Z+E_q` gives the exact pointwise support of `t^T a`:

    L(z)=t^T c - ||G^T t||_1 - sqrt(q t^T V t),
    U(z)=t^T c + ||G^T t||_1 + sqrt(q t^T V t).

Since `e_dot^P19(y,z)` and `E_excess^P19(y,z)` are nonnegative for frozen y, their sharp conditional pointwise envelopes are `[g 10^L,g 10^U]`. `q=0` is the deterministic EOS/Jeans outer box; `q=5.991464547...` is the 95% **two-parameter** Gaussian ellipse union, conditional on the known-C Gaussian fixed-template assumptions. Different redshifts share the same nuisance vector; pointwise extrema cannot be chosen independently. These are NOT posterior intervals for actual `n_e(t)`.

## 5. Interface to Thomson tau and what remains unbound

BASS PR234 has `d tau_T/dx=K n_e/H`, `x=ln(a/a_ref)`. The exact chain-rule tangent is

    D_a(d tau_T/dx) = K/H D_a n_e - K n_e/H^2 D_a H

if K is held fixed. Our `D_a e_dot_UVB` is **not** `D_a n_e`; the latter requires a source-accepted full variational initial/boundary-value evolution, density `nHref(x)`, electron feedback, other chemistry, `D_a H`, the physical K binding and time/observational-redshift transport. In the actual old pilot, `electron_per_Href` was itself a prescribed bath field. Do not substitute the source event rate for that field. BASS reduced30 and REI 17-state populations are distinct state spaces; no unproved 17->30 projection is admitted.

Physical F4 PARTIAL, L4 false, actual temperature/native25/physical radii null. NO_MORE_IVPs; original working33/88, central28/88, delta0.

## References and source hierarchy

- Original REI source `model.py` Git blob `1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc`; saved ON_refined CSV blob `189c2d903e25c18bee49e0ab6add3ba1d1805e93`.
- REI PR261 https://github.com/cosmosapjw-quantum/rei_bianchi/pull/261 and PR260 https://github.com/cosmosapjw-quantum/rei_bianchi/pull/260.
- BASS tau PR234 https://github.com/cosmosapjw-quantum/bass/pull/234 and VigilODE chemical6 PR103 https://github.com/cosmosapjw-quantum/vigilode/pull/103.
- Puchwein et al. (2019), MNRAS 485, 47–68, DOI https://doi.org/10.1093/mnras/stz222. Original fiducial homogeneous UVB and equivalent-equilibrium tables are different products.
- Leong et al. (2023), MNRAS, DOI https://doi.org/10.1093/mnras/stac3828, H/He rate equations and photon transport caveats.
