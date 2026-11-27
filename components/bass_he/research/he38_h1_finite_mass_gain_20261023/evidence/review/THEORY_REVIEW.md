# HE38 R6 independent theory review

**Verdict: PASS_SCOPED.** Reviewer `/root/he38_independent_review` is separate from the source, derivation and implementation authors. The finite-mass H1 source-coordinate construction is mathematically consistent under the declared common-temperature/common-bulk, infinitesimal independent e/H STF model. There is no unresolved theoretical correction required for the stated unit.

Workflow **1.0.0**, approval **0.2**. Reviewed contract: `research/he38_h1_finite_mass_gain_20261023/CONTRACT.json`. The derivation reviewed is `/tmp/he38_gain_theory/DERIVATION.md`, SHA256 `eebf5d8c1398d66b226966af9a24a5cab11eeb98eabeba90b2862cba967f67c1`. Read source records and the corresponding sections of the existing Le–Cambier PDF text; no literature corpus or old suite was replayed.

## Independent analytic checks

1. **Jacobi coordinates and event invariants.** Starting from the three output velocities in derivation Eq.2, their mass-weighted sum is $LV$. The coefficients of both internal Jacobi velocities vanish in that sum. Their kinetic quadratic form has coefficients $\mu$ and $\mu_t$, with vanishing mixed term because $mc=Md$. Together with the declared Jacobi energy partition this gives outgoing minus incoming kinetic energy $-I$, independently of $V$ and the two angular directions. The number changes conserve nuclei and charge and satisfy $m-h+M=0$ in the specified Newtonian mass convention.

2. **Species gain and independent total tensor.** Angular averages use $\langle g_a g_a\rangle=|g_a|^2\mathbf1/3$ and $\langle g_1g_2\rangle=0$ only in the original source Jacobi coordinates. This gives derivation Eqs.7–8. Summing those gains and subtracting both incoming tensors independently gives $B_{\rm net}=2(E-I)\mathbf1/3-\mu g_0g_0$, whose half-trace is $-I$. Thus the total scalar heat is fixed without reliance on the detailed energy-sharing mean, while the species heat split retains that dependence.

3. **Transfer compression.** In the weighted radial measure $C_\mu(E-I)e^{-E/\theta}dE/E$, multiplication by the conditional mean $IE\log(E/I)/(E-I)$ cancels the rational factors. Integration by parts gives $\Lambda=C_\mu I\theta E_1(I/\theta)$. The recurrence for $E_2$ then gives $\Lambda=\beta-\theta\alpha$, $U_1=\theta\alpha$, and $U_2=\beta-(I+\theta)\alpha$. These equalities depend on the selected cross section and transfer law together; the derivation does not promote them to arbitrary CI kernels.

4. **Positive remainder and conditioning.** Direct differentiation of $F(x)=\int_0^\infty t(x+t)^{-1}e^{-t}dt$ yields $H=-xF'=x\int_0^\infty t(x+t)^{-2}e^{-t}dt>0$. The ratio $H/F$ is a weighted mean of $x/(x+t)$, so $0<U_2<\theta\alpha$. This establishes the stated mean-energy bounds without a numerical extrapolation. The production species formulas avoid subtracting $U_2$; the small combined heavy heat also has a direct expression.

5. **STF map.** At the common-T reference, $V$ and $g_0$ are independent Gaussians. The Grad coefficient $m_s/(2n_s\theta^2)$ has the normalization needed to reproduce the input pressure STF. In the gain, the sole anisotropic contraction is the fourth Gaussian moment of $V$: its STF part is $2(\theta/L)^2\alpha\pi_s$. The mixed terms are odd and the remaining contractions are proportional to $\operatorname{tr}\pi_s=0$. This yields the gain weights in Eq.22. Adding the already-derived incoming coefficients yields Eq.24 and the sum $J_{\rm total}=-\kappa_2(n_H\zeta\pi_e+n_e\eta\pi_H)$. The direct total-event tensor gives the same weights independently.

6. **Scalar heat and temperature.** Combining the COM gain energy, $U_1,U_2$, and the incoming removal energies gives all three Eq.18 expressions. Their coefficient sums reduce to $-I\alpha$. The all-retained particle count rises by one per event, so differentiating $3n_{\rm part}k_BT/2$ gives the stated reaction temperature term. The explicit common thermal inventory is essential to this last conversion.

7. **Mass limit and dimensions.** The radial prefactor changes by $\zeta^{-1/2}$, while the electron-only total STF coefficient additionally contains $\zeta$. The resulting rate and STF ratios are therefore $1/\sqrt\zeta$ and $\sqrt\zeta$, respectively. This is consistent with the heavy-mass limit. All species heat and pressure/STF sources have units Pa/s, and the transfer variable is a Jacobi relative energy; its lab-energy reinterpretation at finite mass would change the model.

## Primary-source and claim alignment

The existing Le–Cambier text, SHA256 `34f495db1eefa34bdf1104117f8546b2a539ccc2b3f4ba303365d2c673cc18e5`, was read at Eq.2–7, Eq.39–48, §III.E and Eq.85. It supports the mass convention, original coordinates, relative-energy variable, and stated differential law. Adopting its uniform angular law before taking the heavy-mass limit is correctly identified as the explicit finite-mass model choice.

The printed Eq.48 sign is locally inconsistent with Eq.2c and the loss/gain conventions in Eq.39–47 in the reviewed version. A direct event argument establishes $-I r$. The source record appropriately limits its statement to the local discrepancy in this version; this review does not assert that an erratum or another published version has been checked.

The source record separates this conditional construction from a measured H1 full-angle differential provider. It also leaves unequal temperatures, drift, finite anisotropy, total-gas stress closure and coupled dynamics as explicit later dependencies. These distinctions match the equations actually derived.

## Evidence and review boundary

The author’s exact-rational/Wick and 65-digit transfer receipts were inspected and reused with their file identity. They were not rerun. The present independent review supplies the analytic checks above and the separate bounded interface probes recorded in `PROBE_RESULT.json`. Root’s new raw numerical contraction, diagnostic and figure are separate evidence and are not claimed as completed by this review.

The unit makes a constructive exact-moment extension within its model, rather than a strong no-go claim. NG1–NG7 are therefore not an admission path for any new impossibility statement here. No missing angular table is treated as proof of nonexistence. The added definitions directly enter the conservation, heat and STF formulas; the formalism has a concrete computational contribution through elimination of an extra sharing integral.

