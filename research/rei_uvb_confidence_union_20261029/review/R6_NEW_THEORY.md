# Independent R6 review of the new confidence-union contract

**Verdict: PASS_SCOPED.** The conditional Gaussian coverage theorem, Minkowski-sum support formula, endpoint witnesses, scalar versus joint quantile distinction, and pointwise nested-fit statistic are correct under the stated assumptions. The contract is suitable for bounded implementation. No change to the mathematical model or formulas is required.

This review is by `/root/uvb_code_review`, a different task from the theory author `/root/uvb_theory_review`. The reviewer did not author the derivation. This follow-up read only the two theory artifacts and the original frozen source; no new code, numerical outputs, or phase-two comparisons were read. The reviewer had already inspected original PR257 material during its separately recorded C9 task, so this is independent authorship/reasoning, not a claim of source-blindness. Requested role is scientific review; observed backend model identity is unavailable. No numerical, CAS, scientific Python, or test execution was performed.

Reviewed identities, verified with read-only SHA utilities:

| Object | SHA256 |
|---|---|
| `review/PHASE1_THEORY.md` | `7ecbfb7292c804ee9e9fd5b479f9563ec4b8330a1c2e0710f70cef52d2885061` |
| `review/THEORY_CONTRACT.json` | `0eb1134b7ff1f4554789d391e70ae0d24804f7f0fefe840cfa5f24012e48bcd1` |
| Original frozen source | `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b` |

## Independent derivation checks

**GLS and source sign.** With `B=X^T W X`, `V=B^-1`, `A=V X^T W`, the full-column-rank and SPD hypotheses imply `AX=I`. The response `d-m+theta*v+j` follows the frozen source convention. In the proposed sampling model `d=m+X*a_star-theta_star*v-j_star+epsilon`, evaluating the fit at the true nuisance cancels both negative mean shifts and yields `a_hat(eta_star)=a_star+A*epsilon`. The sign is consistent. The centered residual quadratic completes to `Q_min+(a-a_hat)^T B(a-a_hat)` because the cross term vanishes by the GLS normal equations.

Since C and W are symmetric inverses,

`A C A^T = V X^T W C W X V = V B V = V`.

This is an exact algebraic covariance identity, independent of Gaussianity. Normality is additionally required to turn it into the asserted chi-square pivots. b and kappa have the stated dex and dex-per-redshift units; covariance entries have their paired parameter units, and the Mahalanobis quadratic and q are dimensionless. Redshift is dimensionless, with “per redshift” retained to identify the slope coordinate. Dual directions must be interpreted with the corresponding reciprocal coordinate units when units are carried explicitly.

**Zonotope, union, support and attainment.** Writing each Jeans coordinate as `jc_i+jh_i*q_i` yields `Z=c+G[-1,1]^8` without a rank-eight assumption. Independent coordinate maximization proves `h_Z(s)=s^T c+sum|s^T g_i|`; sign-chosen endpoints attain it. The parameter centers are exactly all of Z, so distributing a common ellipsoid over those centers gives `union_eta(a_hat(eta)+E_q)=Z+E_q`. Compactness gives attained extrema; convexity gives interval projections.

For `delta=V^(1/2)u`, `||u||<=sqrt(q)`, Cauchy-Schwarz gives `s^T delta<=sqrt(q)*||V^(1/2)s||`. For nonzero s and q>0, `delta_s=sqrt(q)*V*s/sqrt(s^T V s)` attains this value and has `delta_s^T V^-1 delta_s=q`. Adding the separately attained Z support witness gives a union support witness. This proves the support and projection formulas without a directional grid or vertex enumeration. q=0 gives Z; s=0 gives zero support; a singleton nuisance set gives one ellipse. These cases are correctly included in the contract. The controller's external CAS report is consistent with the algebra but was neither run nor independently inspected here and is not needed for this proof.

**Coverage and quantiles.** At any fixed allowed true nuisance, `V^-1/2*(a_hat(eta_star)-a_star)` is a standard two-dimensional normal vector under the stated Gaussian model. Its squared norm has chi-square2 law. The true-nuisance ellipsoid with q2 therefore has exactly 95% coverage; it is included in the reported union for every data realization. Consequently the union has coverage at least 95% for every fixed `(a_star,eta_star)`, equivalently the infimum of coverage over that parameter domain is at least 95%. This argument does not require a nuisance prior, a union bound, or multiplicity correction over the allowed nuisance values.

For any one nonzero pre-specified direction s, the normalized scalar error `s^T A epsilon/sqrt(s^T V s)` is standard normal. Its two-sided 95% interval uses `q1=Phi^-1(0.975)^2`; the projection of the true-eta ellipse at q1 is exactly this interval, so projecting the union gives at least 95% scalar coverage. q1 does not provide 95% joint coverage. The q2 identity `chi2_2^-1(0.95)=-2 log(0.05)` is correct. A direction chosen after seeing data is not covered by the q1 pre-specified-direction argument. The q2 full-vector statement already gives simultaneous coverage of all its projections.

The theorem assumes the correct additive affine mean, known fixed C, fixed template/design/responses/bounds, true nuisance inside the declared box, and the specified Gaussian sampling law (or a valid conditional version of that law). Merely observing a covariance matrix, passing an SPD check, or matching earlier GLS calculations establishes none of the empirical Gaussian/model premises. Estimated covariance, template selection, data-dependent bounds and unmodeled mean discrepancy require a separate argument. The text explicitly preserves these distinctions. No empirical goodness-of-fit or physical-source validation is admitted by this R6 verdict.

**Pointwise nested-fit statistic and zero crossing.** Eliminating the intercept gives residual precision `M=W-W1(1^T W1)^-1 1^T W`. Because x is independent of the constant column, `T=x^T Mx>0`. The remaining scalar quadratic has minimizing slope `(x^T Mr)/T`, curvature T, variance `1/T`, and reduction `DeltaQ=kappa_hat^2/Vkk`. Both minimized residual sums must use the same eta. Separately minimizing each model over eta yields a nonnegative nested-profile difference but generally not this pointwise identity.

The continuous affine image of the connected box is the full slope interval [L,U], so squaring that interval gives the stated minimum/maximum range. If zero is interior, convexly interpolate the endpoint nuisance witnesses with upper-witness weight `-L/(U-L)` to attain zero. If an endpoint is zero, use that endpoint directly; if `L=U=0`, any witness suffices. Thus neither a corner-only minimum nor an unguarded division by `U-L` is appropriate in general. The supplied contract's mathematical witness statement allows these cases.

**Statistical sign.** The widened scalar interval excludes zero positively exactly when `L_kappa-sqrt(q1*Vkk)>0`; equality includes zero because the intervals are closed. Replacing q1 with q2 checks exclusion by the projection of the joint union. A positive deterministic L alone is insufficient, as the provided one-point/high-variance counterexample shows. This is a basic conditional inference distinction, not a new universal physical no-go result.

## Coding-contract disposition

The contract requests the right bounded controls: finite dimensions, unmodified full-C Cholesky, whitened design rank, stable solves, AX and ACAT identities, normal equations, quadratic completion, signed source witnesses, oblique support, pointwise nested residual comparisons, zero-crossing synthetic coverage, ellipsoid radius and support attainment, and q/s/fixed-nuisance limits. No scientific repair is required before implementation.

Two implementation interpretations should remain explicit, without changing the frozen theory:

1. The new algebraic residual tolerance `atol=1e-12, rtol=1e-10` governs this new contract. It does not retroactively replace the original source's `atol=1e-13, rtol=1e-11` deterministic regression comparison. Preserve both in their respective checks.
2. Zero-slope range witness construction must branch for a zero endpoint or `L=U=0`, as derived above. Treat exact zero support coefficients by the declared tie rule; do not silently truncate a small nonzero contribution. These are direct implementations of the stated contract, not model changes.

Actual code/test review remains pending and must assess the observed implementation and its raw receipts. This R6 pass authorizes no new budget by itself. Resource reconciliation, unknown overhead, original physical/DAG ceilings and the existing no-IVP boundary remain unchanged. The original C9 review files were left untouched; only this review and its JSON companion were added.
