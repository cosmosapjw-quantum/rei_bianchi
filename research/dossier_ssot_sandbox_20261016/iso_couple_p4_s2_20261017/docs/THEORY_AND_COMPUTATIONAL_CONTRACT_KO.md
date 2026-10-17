# REI ISO-COUPLE P4/S2: 양의 출생-광학깊이 시간 적분, 실제 Rust owner 결합

2026-10-17 KST. 연구단위 `ISO-COUPLE-P4/S2`. 원본 PR150 / P3 코드는 불변이며 S2는 별도 opt-in Rust 구현이다. 본문은 **수학적 유도**, **계산 실험**, **코드 검증**, **과학적 허가**를 구분한다.

## (R5) 물리 문제와 정확한 frozen-coefficient 해

Proper time `t` [s], reference-comoving photon count `N` [ph m^-3], source `j` [ph m^-3 s^-1], absorber rate `kappa_i` [s^-1], `kappa=sum_i kappa_i`. 4 species HI, HeI, HeII, DI; photo cross-sections from the original Rust `AtomicProvider` Verner fit and the `DAtomicProvider` threshold-gated hydrogen approximation. Homogeneous diagonal Bianchi-I, signature `(-,+,+,+)`; photons follow the original Killing momenta. Standard source `AxbiSource` MD14/BB50k 13.6..100 eV, support `4<=z<=20`. Stage-local midpoint `j`, `kappa_i` frozen. No frequency/angular continuum or fully physical Einstein geometry claim.

Each step `Delta t>0`, tau=kappa Delta t>=0. An old photon cohort is fully present at the beginning and gets `Nold*exp(-tau)` at the end. New photons created uniformly inside the step with total positive count `B=j Delta t` solve

`Nbirth,1 = Integral_0^Delta t j exp[-kappa(Delta t-s)] ds = B phi(tau)`;
`phi(tau)=(1-exp(-tau))/tau`, `phi(0)=1`.

Total absorption for channel i is

`A_i=[kappa_i/kappa] * {Nold [1-exp(-tau)] + B [1-phi(tau)]}`;
if kappa=0, `A_i=0`. Positivity follows from `0<=phi<=1`, `kappa_i>=0`, and `B,Nold>=0`. Exact number identity:

`Nold,1 + Nbirth,1 + Sum_i A_i = Nold + B`.

For physical photon energy `E` in eV, one absorption contributes thermal `A_i (E-chi_i)` and chemical binding `A_i chi_i`; the two sum to `A_i E` before conversion by exact `1.602176634e-19 J/eV`. The original P3 owner executes this balance after B -> events with one D `d_atomic_rhs` source check. RR/DR, CX and free-free/CMB remain exclusively owned by P2 `full_network::step` with `use_photo=false`, so no duplicate photo reaction.

The P3 old birth exposure `B exp(-tau)` gives a signed difference

`Nbirth,P3 - Nbirth,exact = B [ exp(-tau) - phi(tau)] = -B tau/2 + B tau^2/3 + O(tau^3)`.

Because `B=O(dt)` and `tau=O(dt)`, the *source exposure* local difference is `O(dt^2)` and the global error after `T/dt` steps generally `O(dt)`. Replacing it with the exact frozen slab removes this term, **not** the splitting, opacity-update, temporal birth geometry or spectral/angle errors.

Numerically use `old_absorbed=-expm1(-tau)`; for `0<tau<1e-3` use

`new_absorbed = tau/2 - tau^2/6 + tau^3/24 - tau^4/120 + tau^5/720 - tau^6/5040`.

Set `new_surviving=1-new_absorbed` to avoid cancellation. Nonfinite/negative tau rejected; no clipping and no arbitrary spectral extrapolation. Extremely small tau absorption underflow is harmless and the number ledger still remains nonnegative. For constant positive tau large, `phi -> 1/tau` and old photon survival vanishes.

## (R7/C5-C8) Native implementation and frozen-gas control

The new `src/positive_birth_clock.rs::PositiveBirthClockBridge::advance` uses original `AxbiSource::new(n_H0,fesc,16,8)` and `SourceAgeBridge`, 384 preserved P3 positive cells per birth; original `positive_age.rs` is untouched. Prior cohorts use full exp(-tau). Exactly new cohorts created this time step use `phi(tau)`. All gas and photon changes are transactional: method clones the initial `AgeHistory`, checks original D photo RHS source, nonnegative nuclei, T within 2.7..2e5 K, chemical/thermal and whole-step energy accounting, commits accepted state only on `Ok`.

**Proof scope caution:** The implementation stores the newborn as an effective midpoint-geometry cohort rather than resolving the full birth-time measure. For time-dependent E(t), kappa(E,t), j(t), this *is not* an exact continuous retarded source-age transport. The gas/photo updates remain Lie-split with generally first-order error, even though frozen slab source exposure is exact. In dynamic Bianchi geometry, the interaction time distribution and photon energy work are approximate. The electron, species, gas density and sigma owners are not altered.

Test 1 (genuinely independent analytic control): static geometry and *frozen* original proper gas compositions, true original 48 energy-cell moments and 8 GL directions, Verner & H-equality D cross sections, fixed j and kappa for all steps. At T=8e10 s, `N=2,4,8,16,32,64,128`, corrected photon survival matches closed-form positive Duhamel solution within `1.674e-16` in relative error. P3 first-order full-exposure has 34.343% survivor error at N8, 5.019% at N64, and 2.536% at N128. Both methods are photon-number conservative within `<1e-14` in this oracle. This is **not** the evolving-gas result.

Test 2 (source-native coupled bounded history): same original 13-state H/He/D mixture & Savin thermal CX, Grackle Case A gas, physical source MD14/BB50k, transparent prescribed FLRW/BI+/- background with H=1.2e-16/s, shear +/-0.06H, T=8e10 s; 4 cases x 4 step grids x two representations = 32 numerical Rust runs. For FLRW N64, P4 survivor count is +5.2840% vs frozen P3, total absorbed count -0.8877%, HI event -0.8792%, HeI -0.9286%, HeII -1.2245%, DI -1.0071%. Temperature difference -3.944e-5 K. Original P3 code reproduced at max normalized difference 4.455e-16 compared with its frozen 32-row input. Maximum completed photon inventory relative residual 1.420e-15, total-step energy residual 6.944e-16.

**Scientific countercheck:** FLRW native N16/32/64 survivor observed order: P3 `p=0.9020`, P4 `p=0.9961`, not 2. Correct claim: exact (frozen) birth-clock + source-native coupling, **not full second-order gas/transport solver**. The flux integrated outside 13.6..100 eV and D energy threshold remains manufactured P3 `chi_D=chi_H+0.0037eV` versus real atomic source not fitted.

## Source conventions and known distinct thresholds

Original `HHeModel::controlled_fixture()` binding chi_H=13.598434599702 eV, chi_HeI=24.587389011 eV, chi_HeII=54.41776 eV. Original Verner fit photo thresholds are 13.60, 24.59, 54.42 eV. P3 manufactured isotope chi_D=13.602134599702 eV; H equality sigma_D(E)=sigma_HI(E) only for E>=chi_D. Do not conflate BINDING and PHOTO_CROSS_SECTION gates. Source spectral segments use [13.6,24.59,54.42,100] eV. D edge within first source H bin is not yet adapted in current native crate.

## (R8/C10) Status and next DAG gate

- Derived: Exact constant-step Duhamel formula, positivity, channel conservation.
- Numerically checked / implementation-verified: Rust original P3 68/68, new 7/7, native full 75/75, 32 coupled rows, seven frozen-gas oracle rows, static bounds and original owner blob 12/12.
- Unresolved: P4/S3 source-history birth-time/energy quadrature, threshold-resolved D spectral owner, full angular/timestep independent convergence, BASS on-shell Einstein background, actual original PR171 native source-age H2 acceptance, FLRW-CONV and BI-SIGNED. Preserve HOLD for full ISO-COUPLE and EoR.
- Status: `ISO-COUPLE-P4/S2 PASS_SCOPED_POSITIVE_BIRTH_CLOCK_NATIVE_REFERENCE`. `ISO-COUPLE-P4` remains `PARTIAL`; `FULL_EOR HOLD`.
- Next unit: P4/S3 positive retarded birth-time quadrature under varying cross sections and Bianchi redshift, adaptive threshold-aware spectrum; separate time/angle/spectral axes and on-shell BASS geometry after source identity intake. No full NCP FULL005 rerun authorized in this unit.

## Literature used for methodological context (not proof of this new code)

- Abel, Norman & Madau, 1999, *Photon Conserving Radiative Transfer around Point Sources in Multi-dimensional Numerical Cosmology*, [arXiv:astro-ph/9812151](https://arxiv.org/abs/astro-ph/9812151). Photon-number conservation as core radiation-transfer property. This paper does **not** supply this precise new time-distributed emission identity.
- Mackey, 2012, *Accuracy and efficiency of raytracing photoionisation algorithms*, [A&A](https://www.aanda.org/articles/aa/full_html/2012/03/aa17984-11/aa17984-11.html). Non-equilibrium photoionisation time accuracy and first/second-order algorithm trade-offs.
- Verner et al., 1996, *Atomic data for astrophysics II*, DOI [10.1086/177435](https://doi.org/10.1086/177435). Actual source cross-section parametric form imported unchanged from PR150.
- Original source owner PR150 and P3 12 Git blobs, `inputs/P3_OWNER_SOURCE_IDENTITY.json`, not inferred from current general literature.
