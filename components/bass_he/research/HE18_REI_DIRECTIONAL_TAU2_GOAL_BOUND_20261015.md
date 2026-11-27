# BASS_HE to rei_bianchi: conditional directional Thomson quadrupole error budget

Date: 2026-10-15 KST. This is a downstream cold AXBI reuse receipt, **not** a warm HE18 FT03/HM12 source-ODE certificate.

**Canonical code and computed results:** [rei_bianchi directional transfer and sensitivity](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/directional_tau_20261015), commit 5dd89558c290b272716c785094283d3a8d5ca1c8.

All five original 200001-row cold prefix histories have source-epoch SHA256 d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185. BASS_HE warm HE18 16-cell certificates have different temperature, helium and photon-stock conventions. Neither numerical tau nor physics closure is transferred across the models.

For a non-tilted normal-comoving observer at the shared prefix endpoint (mean zbar~10.2693), define the relative, direction-dependent redshift by

\[
1+z_{\rm dir}=\frac{a_o}{a_e}\sqrt{(1-\mu_o^2)\exp[2(b_e-b_o)]+\mu_o^2\exp[-4(b_e-b_o)]}.
\]

This is **not** the line of sight to a present-day CMB observer.

The **derived conditional goal-functional bound** is

\[
|\delta O_{\tau_2}|\leq C_b\,\epsilon_b+C_x\,\epsilon_x.
\]

It assumes frozen exact normal-frame a(t), t(a), nH(t), plus pointwise absolute bounds |delta b| <= epsilon_b and |delta xHII|, |delta xHeII|, |delta xHeIII| <= epsilon_x. The proof uses m=1-2 sup|db/d ln a|>0, the inverse-root bound |delta ln a_e|<=4 epsilon_b/m, and the exact Legendre coefficient (5/2) integral |P2(mu)| dmu = 10/(3 sqrt(3)). The original numerical source constants are not independently certified.

For |q|=0.005 and z_rel=0.75, the stored-source odd directional optical-depth quadrupole is -2.5931564384664e-6. Sensitivities are C_b=0.0975613971785774 and C_x=0.2870530863320277. Sufficient **single-source-only** ceilings for each to contribute no more than 10% are epsilon_b <= 2.65797386410925e-6 and epsilon_x <= 9.033717322471e-7. If both uncertainties coexist, use the summed budget, not both separate limits simultaneously.

**Ubuntu evidence:** 33 parent + 19 directional tests = 52/52 PASS. Manufactured perturbations injected at absolute 1e-6 in real stored histories stayed below the conditional geometry and species-error bounds. All five signed prefixes satisfy n_H*a^3 to maximum relative deviation 3.3306690738754696e-16. Five-source 16384-node chunked longdouble slope analysis equals whole-array vectorized analysis numerically, with interleaved five-run medians 0.08494s vs 0.17557s (approximately 2.07x faster). This is numerical postprocessing, **not** a native Rust solver speedup.

**Double backup:** code/results/test tarball and original parent and geometry numeric caches reside in ~/archives/BASS_HE_REI_TRANSFER_20261015_1445KST/ and ~/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/HE18_REI_TRANSFER_20261015/. Delivery receipt HE18_DIRECTIONAL_GOAL_DELIVERY_RECEIPT.json in both locations records SHA256 identities. Original raw signed history CSVs were not recopied or changed.

Scientific state: **DERIVED / NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED** on frozen cold source surrogates. Native source ODE global error, temperature/opacity closure error, geometry/clock errors and present-day CMB polarization transport remain **UNRESOLVED**. No physical shear-detection claim. Next science gate: independently converged native ZERO and +/-0.005 common-prefix histories with goal-oriented propagation into tau0 and tau2.

References: Fleury, Pitrou & Uzan, Phys. Rev. D 91, 043511 (2015), [DOI](https://doi.org/10.1103/PhysRevD.91.043511). Friedrich et al., MNRAS 421, 2232 (2012), [C2-Ray H/He](https://academic.oup.com/mnras/article/421/3/2232/1077406).
