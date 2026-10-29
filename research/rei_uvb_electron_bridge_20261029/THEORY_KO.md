# REI UVB photo-event electron observable bridge (2026-10-29)

**Work unit:** `REI_UVB_ELECTRON_BRIDGE_20261029` · Parent REI PR263 `f52ecdb11b3f7e43fdf1fbc19d9feff38fe56927`; REI PR262 `6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf`; BASS PR234 `c74317ce5df34c442514eccf8a1e87494657393d`.

Status `DERIVED + EXACT_ALGEBRA_CHECK + SOURCE_ONLY_NUMERIC_CHECK`, **not a physical BASS 17→30 projection**, not the user-requested distinct-author R6/C9. Original REI DAG working **33/88**, central **28/88**, physical delta **0**; F4 PARTIAL, L4_ready false; NO_MORE_IVPs.

## Assumptions and authority

REI `y∈R_+^17` is ionic/heavy population per reference H, charge row `q` from PR262 `source17.py`; 7 ordered photo events are H1^0→H1+, D^0→D+, T^0→T+, He3^0→+, He3+→2+, He4^0→+, He4+→2+. Here only seven selected frozen `ON_refined` states are used. BASS 6 charged coordinates are `(H+,He+,He2+,Li+,Li2+,Li3+)`, with isotope weights `wH=sH1+sD`, `wHe=sHe3+sHe4`, `wLi=sLi6+sLi7` from PR234. The owner binary64 isotope scales must be exactified individually before adding for represented-real interpretation. Physical numerical values are **not imported**. Assume `ρ(x)=nHref(x)/nb(x)>0`, with positive weights and compatible coordinate units. Time variable `x=ln(a/a_ref)`; `z_x=−(1+z)` only for mean redshift, not observed direction-dependent z.

Puchwein 2019 Table D1 supplies fiducial *non-equilibrium* rates, D2 different equivalent-equilibrium rates. Applying HI rate to H1,D,T and HeI/HeII rate to He3,He4, and imposing common `10^[β+κ(z−3.6)]` is a **REI model assumption**, not a published universal isotope theorem.

## Theorem 1: exact algebraic charge complement

For `rho>0` and positive `w`, define a six-by-seventeen linear map `M` by

```
z_H+      = rho*(y_H1+ + y_D+)/wH
z_He+     = rho*(y_He3+ + y_He4+)/wHe
z_He2+    = rho*(y_He3++ + y_He4++)/wHe
z_Li(j)+  = rho*y_Li7(j)+/wLi,  j=1,2,3
```

and `e_B=(wH,wHe,2wHe,wLi,2wLi,3wLi)`. Direct multiplication yields

`e_B M = rho (q_17^T − e_T+^T)`.

Thus the single extra observable coordinate `t=rho*y_T+` gives

`e_B M y + t = rho q_17^T y` **for every y**. Multiplication by physical `nb` would give `nb(e_B My+t)=nHref qy`, conditional on actually binding these densities. The missing row has rank one. Without an extra T-sensitive coordinate, any two states differing only in T neutral↔T+ partition with the same total T have the same six reduced coordinates, but different electron charge. This proves necessity of T-sensitive information for *this fixed M*, not a universal no-reduction theorem.

Let `S∈Z^{17×7}` have `−1` at each source, `+1` at its ionic daughter. Then `q S=1_7^T`, and

`e_B M S − rho q S = (0,0,−rho,0,0,0,0)`.

The unique mismatch of these seven **photo-only event electron** columns is T0→T+. For source event rates `lambda_j>=0` with a common `Gamma_HI` for H1,D,T, the missing event flux is `lambda_T=Gamma_HI*y_T0`, all per Href/s. This is not the total chemical electron budget: Li6, fast n/T pools, beta/CR/nuclear/escape and recombination are outside S.

### Necessary but insufficient source/dynamics compatibility

`z=My` and BASS reduced RHS `f_B` would require

`M_x y + M F_REI(x,y;a)/H_REI(x) = f_B(x,My;a)`

at compatible states and clocks, with appropriate electron/charge bookkeeping and branch/source identity. This commutation has NOT been demonstrated. `M_x` generally contains `rho_x`. A source electron equality alone does not imply H/He/Li simplex admissibility, isotope conservation, closed chemical 6D equations or any ODE solution mapping. For this six-state map, source-independent **necessary** inequalities are `0<=z_H+<=T_H`, `0<=z_He+ + z_He2+<=T_He`, `0<=z_Li+ + z_Li2+ + z_Li3+<=T_Li`; actual totals are unbound.

## Theorem 2: source-only twojet defect

At an artificial *source-consistent local restart* with parameter-independent IC and geometry, let `F` be smooth, `B_kappa=d B_beta` where `d=z_mean−3.6` and `d_x=−(1+z_mean)`. For **any parameter-independent smooth covector** `c(x)`, consider `tau_x=c(x)y(x)`, `y_x=F(x,y;a)/H(x)`, with `v_a(x0)=0`. Then

`A=c B_beta^x`,
`∂_beta tau_xxx=U=2 c_x B_beta^x+c(J B_beta^x + D_x B_beta^x)`,
`D_(beta,kappa)(tau_xx,tau_xxx)=[[A,dA],[U,dU+d_x A]]`,

and `det = d_x A^2`. Hence the **entire full chemical Jacobian and covector time derivative** cancel from the determinant. This extends the PR263 scalar time-prefactor statement to parameter-independent **time-varying charge projection** covectors, but not parameter-dependent `M`, `K`, density, clock or IC.

Take the source-only unprojected covector proportional to `q_17` and the six-coordinate projected covector proportional to `q_17−e_T+`; normalize by the same hypothetical `C=K nHref/H²>0`. Let `g=ln(10)Σ_j lambda_j`, `g_T=ln(10)lambda_T`, `epsilon=g_T/g=lambda_T/Σ lambda_j`. For `g>0`,

`D_REI=−(1+z_mean)g²`, `D_projected=−(1+z_mean)(g−g_T)²`,

`D_projected/D_REI=(1−epsilon)²`, and `0<=1−D_projected/D_REI=2epsilon−epsilon²`.

Since H/D/T share positive `Gamma_HI` and He photo rates are nonnegative,

`0<=epsilon<=epsilon_upper := y_T0/(y_H1_0+y_D_0+y_T_0)`.

This inequality survives the **same common positive log-UVB factor** for all seven events. It does not survive arbitrary relative rate perturbations. Each saved epoch is a separate pointwise conditional statement, not an all-redshift simultaneous likelihood/credible band.

Seven saved-state *numeric transcript* (not original CSV byte copy) yields max `epsilon_upper=1.20052873728269005×10^-16`, hence max source-only relative determinant distortion `2.40105747456537996×10^-16`; the latter is close to float64 machine precision and is computed with Fraction/Decimal85 before rounding. This **does not bound absolute electron density, full chemistry, time-integrated optical depth, or practical CMB inference**. In particular,

`D_x(nHref y_T+) = (nHref)_x y_T+ + nHref (y_T+)_x`;

only the photo contribution to `(y_T+)_x` is supplied. A tiny photo source ratio says nothing universal about the density-dilution term, other reaction fluxes, long-time amplification, or BASS model fidelity.

## Symbolic and computational validation

Python new 24/24 unit cases PASS after a first two-case test-input parsing failure; C++20 independent long-double 7/7 bound comparison PASS with max relative 1.17536e−19; Wolfram second corrected call exact `{0, 17-vector with only -rho at T+, 7-vector with only -rho at T event}`. First Wolfram call had malformed iterator and produced spurious Li terms; it was repaired without changing theory/acceptance. Python Decimal85 numeric source-only rows 7/7, exact Fraction stoichiometry and runtime refusals. No IVP. Two saved-only figures, with seven individual points and no interpolating time curve, were inspected visually.

Independence caveat: Wolfram and the standalone C++ numerical oracle are different calculation methods, **not different-author scientific reviewers**. R6/C9 distinct-author status remains NOT_RUN.

## Literature and limits

- Puchwein et al. (2019), MNRAS 485, 47–68, DOI 10.1093/mnras/stz222, fiducial vs equivalent-equilibrium UVB tables.
- Ovchinnikov et al. (2021), *Bioinformatics* 37, 1732–1738, DOI 10.1093/bioinformatics/btab010, exact constrained lumping; its kinetic closure requirements do not automatically hold for the current REI–BASS 6D map.
- Eilertsen et al. (2026), arXiv:2606.28895, exact lumping under generic versus critical parameter regimes. Motivation only, **not a new no-go admitted for the present physical solver**.

**Boundary:** This paper-ready algebraic lemma is a source-only exploratory result. BASS and REI state spaces, electron pool/charge carriers, clock, `K/nHref/nb/H`, Jacobian, full chemistry and directional redshift remain physically unbound. Original DAG and budget unchanged.
