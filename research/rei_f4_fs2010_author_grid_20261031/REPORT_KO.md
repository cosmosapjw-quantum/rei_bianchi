# REI F4 | 원저자 FS2010 2D grid × BASS193 full-source conditional response (2026-10-31)

## Science status and actual source

Date: 2026-10-31. Frozen original REI/BASS source: PR #302 HEAD `3a213db3b1fed40e0348e724579e8d73653f3634`, PR #303 HEAD `f593534869989aa7cb08fd8df47699bc33c46ed7`. PR #301 remains separate (read-only) at `9bf503648823353bce8458e4f7aca19092cea7c2`. The 18,528 emission-arrival kernel, 192 first-generation photoelectron arrival rows, 192 saved H/He heat-capacity clock rows, and PR #303 192 source-chemistry compatibility rows are byte-locked, with exact source hashes in `results/RESULTS.json` and `evidence/SOURCE_LOCK.json`. No new IVP or production source mutation. The source is a Ferrett-max conditional Li II singlet source, NOT a measured positive lower bound on cosmological Li II 2E1 abundance.

The user-supplied author source `elec_interp.tar` SHA256 is `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101`. It contains 14 original numerical files × 258 E_e nodes = 3612 grid states, plus Furlanetto-Stoever C interpolator and X-ray example. Energy table from 10 to 9937.21 eV; x_i tabulated in [1e-4,0.999]. Author code defines f_heat,f_ion,f_exc, n_Lya, nion_HI, nion_HeI, nion_HeII, with n_Lya and nion as **number per initial electron**, not energy fractions. One table header for `log_xi_-4.0.dat` says HeII=0.001 instead of the x_i=1e-4 implied by filename/author C array. Whether this is metadata typo or reflects a source-generation inconsistency cannot be resolved from this archive alone; original bytes retained.

Furlanetto, S.R. & Stoever, S.J. (2010), *Secondary ionization and heating by fast electrons*, MNRAS 404, 1869–1878, DOI `10.1111/j.1365-2966.2010.16401.x`, model approximates primordial low-density static gas with HII fraction x_i, HeII=x_i, HeIII=0 and terminal E_e<10.2 eV thermal assignment. The full grid must **not** be described as verified for BASS193 real multi-ion chemistry, dynamic ionized fractions or cosmological gas heating.

## Derivation and calculation

At arrival bin j, absorber s, sub-band b, the immutable previous physical kernel contains the primary photoelectron count N_sb and kinetic energy M_sb=integral_b E_e dN_sb (eV per original baryon). The source is *not* added to other REI/HHe photon source terms. For a **hypothetical** FS x_i=xHII(t) projection, let x range over the saved xHII start/end values; exact piecewise-bilinear extrema on [E_b,min,E_b,max]×[x_start,x_end] supply f_sb,min and f_sb,max. Then

sum_sb M_sb f_sb,min ≤ Q_heat_FS ≤ sum_sb M_sb f_sb,max.

Identical marginal bounds hold for f_ion and f_exc using M_sb; for n_Lya,nion_species using N_sb. For E_e<10.2 eV, original author's terminal classification gives f_heat=1, other channels 0. Bounds are mathematical consequences of the tabulated linear-interpolant rectangles and immutable band count/energy moments, NOT estimates of model accuracy or the actual species-aware cascade. At fixed per-band mean Ebar=M/N, we separately report an `M1_moment_closure` surrogate evaluation, not a resolved intra-band electron distribution. `f_ion + f_heat + f_exc` differs from unity by at most 3.9e-5 in raw source tables, compatible with tabulation/Monte Carlo rounding; neither independent min nor max channels should be summed as simultaneously achievable states.

The 192 original arrival bins cover 18,528 original causal emission-arrival pairs and four absorbers×five E bands, yielding 3,840 new conditional deposition rows and 192 new interval response rows, plus 63 raw-grid evaluation samples. The 18,528 source kernel was independently reaggregated and recovered the 192 original first-electron kinetic totals with |difference| <1e-24 eV/b.

## Numerically checked outcomes

- Complete first-generation primary kinetic energy: `6.749242464433259e-11 eV/b`, unaltered from PR #302.
- Sub-10.2eV terminal assignment: `8.581099847924098e-12 eV/b`, unaltered.
- Exactly **87/192** arrival intervals keep both xHII endpoints within the original table's x_i range; they represent **99.2164244283%** of the original primary kinetic energy. **105/192** outside-domain intervals, representing `5.288541522292482e-13 eV/b`, were not forcibly clamped.
- For the 87 valid-x intervals only, with the one-parameter FS projected chemistry, heat-energy marginal range: `[6.654809992906246e-11,6.688386662957416e-11] eV/b`; mean-energy collocation proxy `6.68180175704177e-11 eV/b`. Fractions relative to valid-source energy are `[0.993795573324605,0.998809742940177]` and proxy `0.997826386487220`.
- Corresponding marginal FS-model ionization energy `[1.8458404052294534e-14,1.7262525428837274e-13] eV/b`, excitation `[5.837853941812256e-14,2.468451508703595e-13] eV/b`, and Ly-alpha photon count `[3.1694710511079836e-15,2.976460362969971e-14] / baryon`. These marginal intervals are not joint-conservation solutions.
- With unmodeled >0.999-x intervals treated solely by 0≤f≤1 and retaining their subthreshold terminal heat, a conservative all-source bookkeeping interval is `[6.659668493554143e-11,6.74127207818034e-11] eV/b`; this wide conditional interval does **not** cure the helium state mismatch.
- No BASS193 interval exactly satisfies the FS single-x_i chemistry assumption at both saved endpoints (`FS_chemical_exact_at_both_saved_endpoints=0/192`), so **actual BASS gas heating/ionization remains unresolved**. Frozen `K/s` or integrated K values in the CSV are capacities/source-coefficient exposures, NOT evolving temperatures.

## Test and numerical evidence

- `python -m unittest -q code/test_physics.py`: 31/31 targeted tests PASS.
- Safe C copied from original `elec_interp.c` with only bounded `fscanf` labels (the source's literal `char label[]=" "` is too small for arbitrary `%s`), compiled as shared library, 200 points × five exposed routines gave worst normalized discrepancy <4e-7 versus Python. This is **modified safe-C reference parity**, not a claim of verified memory safety for unmodified original C.
- Original source table column sum closure max `3.9e-5`; original energy grid and 14 ionized fractions checked. Original source archive and all four PR302/303 CSVs SHA locked; no C/FS interpolation extrapolation was silently applied to 105 outside-domain bins.
- Same-author adversarial review focused on primary threshold, high-E-band coverage, marginal vs simultaneous interval claims, xHeIII/electron denominator, C source buffer and the -4 input metadata discrepancy. No independent distinct-author R6/C9 review has been performed.

## DAG verdict and actual next action

`WORKING_DAG=33/88`, `CENTRAL_DAG=28/88`, `PHYSICAL_FAST=4/7`, `CANONICAL_DELTA=0`; this is ONE new external-source-conditioned auxiliary result, not a completed REI17 F/J or standalone new canonical DAG node. `F4=PARTIAL`, `L4_READY=false`, `PRODUCTION=HOLD`, `NO_MORE_IVPS=true`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `NO_BUDGET_RESET=true`, `AUTO_NEXT_NODE=false`.

Next scoped research: import the 13-species REI isotope-number owner and original BASS21 21-component network, resolve neutron weak Jacobian and full 21-vector source ownership with nHref/nb, K, electron bath and thermal Cv, and either build a valid species-resolved electron-loss operator or quantify deviation from FS single-xi assumptions. Full energy-dependent Li I singlet/triplet branching from Ferrett et al. (1987) PRA 36 3172, DOI 10.1103/PhysRevA.36.3172 and Langer et al. (1991) PRA 43 1652, DOI 10.1103/PhysRevA.43.1652 remains unresolved; proper state-resolved digitized cross-section/branching tables would help. Native REI17 production photon source replacement, true coupled F/J, and any temperature/history/CMB claims remain HOLD.
