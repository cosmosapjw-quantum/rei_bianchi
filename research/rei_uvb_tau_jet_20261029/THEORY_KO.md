# REI UVB→Thomson-τ: local causal sensitivity-jet theorem

2026-10-29 · DERIVED, NUMERICALLY_CHECKED, NOT physical τ. Parent PR262 HEAD `6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf`. Original DAG working 33/88, central last 28/88, delta 0. No IVP.

## Sources and scope

REI PR262 source: seven H1/D/T/He3/He4 photoionization transitions, frozen ON_refined 17-state populations, Puchwein2019 six moments, common UVB log-amplitude/slope; `B_κ^proper=d B_β^proper` at fixed state, `d=z_mean-3.6`. Actual `results/RESULT.json` Git blob `526773ad659171389466a629e1f127c61ada53cd`, SHA-256 `72db6976ff554663ff11227a016d5421008b26d329a5adad25166a9a9c7f320f`.

BASS PR234 source: `x=ln(a/a_ref)`, positive cumulative `τ_x=K n_e/H`, with K from owner, not manufactured. The **formal compatible proxy** here is `n_e=nHref(x) q^T y(x)`, q the 17-state charge vector. BASS reduced30 electron weights and REI 17-state electron proxy are NOT physically identified. `K,nHref,H` are not numerically bound. Metric signature (-,+,+,+).

## Theorem

On an open source interpolation cell, let `y_x=F(x,y;a)/H(x)`, `τ_x=W(x) q^T y`, `W=K nHref/H`, `a=(β,κ)`, and `z_x=-(1+z)` for the mean redshift. Assume (i) full F is smooth and its only a-dependence is the common photo factor `10^[β+κ(z-3.6)]`; (ii) y(x0), τ(x0), q, K, nHref, H, z(x) are independent of a, so initial tangent v_a(x0)=0; (iii) the baseline is a local solution of that chosen parametric family; (iv) source is evaluated strictly inside a smooth P19 interpolation cell. The previously saved ON_refined history is **not** such a calibrated solution, and supplies only counterfactual frozen-source coefficients.

Let `B_a^t=∂_a F` (proper-time source), `B_a^x=B_a^t/H`, `d=z-3.6`, and

`A=W q^T B_β^x = (K nHref/H²) q^T B_β^t`.

Then

`det D_(β,κ)(τ_xx,τ_xxx)|x0 = A² z_x(x0) = -(1+z_mean(x0)) A²`.

**Proof.** Set v_a=∂_a y. It obeys `v'_a=J v_a+B_a^x`; since v_a(x0)=0, `v'_a(x0)=B_a^x`. From τ_x=W q^T y,

`∂_a τ_xx(x0)=W q^T B_a^x`.

Differentiating again, with `D_x B_a^x` the total derivative along the baseline,

`∂_a τ_xxx(x0)=2W_x q^T B_a^x + W q^T[J B_a^x + D_x B_a^x]`.

Since `B_κ^x=d B_β^x`, `D_x B_κ^x=d_x B_β^x+d D_x B_β^x`, and therefore

`∂_κ τ_xx=d A`, `∂_κ τ_xxx=d ∂_β τ_xxx + d_x A`.

The 2×2 matrix is `[[A,dA],[U,dU+d_x A]]`, where U is unknown, so its determinant is exactly `A² d_x`. QED. All unknown J, W_x and baseline B'_β cancel; U itself is not determined. Local jet rank is 2 if A≠0 and d_x≠0, but practical parameter identifiability from noisy τ or CMB data is NOT established.

## Source-only normalized invariant and conditional bounds

Let `g=q^T B_β^t` (electron/Href/s per dex), `C=K nHref/H²` (unbound). Then

`det/C² = -(1+z) g²`.

For PR260's positive pointwise electron source interval `[r_min,r_max]` under the declared EOS–Jeans box and conditional Gaussian ellipsoid, `g=ln(10) r_e`. Its sharp monotone image is

`|det|/C² ∈ [(1+z)(ln10 r_min)², (1+z)(ln10 r_max)²]`.

All seven conditional joint2-95 lower bounds are positive, so the formal local rank-two property survives this **pointwise** nuisance union. This is not a physical posterior, joint seven-redshift band or τ error radius. At knots, use one-sided derivatives; if K/nHref/H or z depend on a, if initial tangents are nonzero, or if source scaling differs between channels, the determinant theorem need not hold.

## Checks and literature

Wolfram algebra residual 0. Python Fraction 200 exact trials, 100 random full-J cancellation trials, 120-digit mpmath direct analytic toy finite difference, source-locked seven-row tests: Python 15/15 PASS. Independent C++20 7/7 PASS with max relative difference 1.17538e-16. No IVP. Initial 90-digit finite difference failed at 1.10459e-57 versus fixed 1e-65 tolerance; 120 digits resolved roundoff without tolerance relaxation.

Related literature, not proof of this REI-specific lemma: Villaverde et al., *Input-Dependent Structural Identifiability of Nonlinear Systems* (2018), DOI 10.1109/LCSYS.2018.2868608; Puchwein et al., *Consistent modelling of the meta-galactic UV background...* MNRAS 485 (2019), DOI 10.1093/mnras/stz222. Original full chemistry, BASS K, nHref, H, directional redshift, physical norm/radii and calibrated state sensitivity remain unbound. F4 PARTIAL, L4 false, NO_MORE_IVPs.
