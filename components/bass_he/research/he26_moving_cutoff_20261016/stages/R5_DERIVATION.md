# HE26 R5: exact moving H/He photoionization cutoff and positive source quadrature

**Scope:** source-only theorem and fixed-grid quadrature construction, not a verified HE25 native microphysics update. Parent BASS_HE HE25 PR72 exact head `eb4952af1f3d9ca99aad300ddf6db6f2b2fe1233`. Original HE25 `src/physics.py` Git blob `32a0de3aaca054544597ded826ce87d4f608cbae`; exact HE21 Verner/BB50K source SHA256 `3df86063f12e238ec41219343a016b3a5086d18ce973015c335ec8118d9a5b66`.

For HE25 non-tilted LRS Bianchi I, signature `(-,+,+,+)`, let `x=ln(a/a_b)`, `nu` be reference covariant-momentum direction cosine and `P` its reference energy (eV). Set `A=exp[-2(1+q)x]`, `B=exp[-2(1-2q)x]`, `G=sqrt[A+(B-A)nu²]`. Then `E=P*G`, `mu=nu*sqrt(B)/G`; the **exact** Jacobian is `J=|d(E,mu)/d(P,nu)|=sqrt(B)*A/G²=exp(-3x)/G²`. Wolfram symbolic Jacobian difference and cutoff-equation substitution both vanish identically.

At any time x, for source support `[13.6,100]eV` and Verner fit thresholds `chi_i=(13.6,24.59,54.42)eV`, clip each old fixed `P∈[L,R]` cell at `P_cut=chi_i/G` plus endpoints `13.6/G,100/G`. Each new support-valid child `[l,h]` has true positive `N=∫[l,h] J*shape(PG)dP`, `U=∫ J*shape(PG)*PG dP`, and independent source-driven photoevent `∫ J*shape(PG)*sigma_i(PG)dP` and photoheat `∫ J*shape(PG)*sigma_i(PG)*(PG-I_i)dP` moments. The physical binding energy `I_i` differs from the Verner fit cutoff. The child centroid lies in `[lG,hG]`; cut parts sum to the original full source integral by partition, not by inventing spectra from arbitrary parent N/U.

For a fixed `P` shell the exact angular cutoff satisfies `nu_cut²=[(chi_i/P)²-A]/(B-A)`; retain ±sqrt only if `0<nu_cut²<1`. For `B=A` no internal angular cut exists. At `B>A`, active directions are `|nu|>=nu_cut`; at `B<A`, active directions are `|nu|<=nu_cut`. Break angular integration exactly before Gauss quadrature.

Independent reference integrates in physical birth `(E,mu)`, yielding source number/mean, HI/HeI/HeII Verner cross-section and photoheat kernels **independent of x or signed q** for isotropic emission. This invariance applies only to newly born source moments at frozen absorber conditions, not evolved photons, anisotropic stress or nonlinear chemistry.

HE25's original `Model.__init__` uses `parts=1` when fixed-endpoint cut panels have `hi/lo<=1.01`, independent of `m`; a moving threshold can traverse that under-resolved panel. The default four-node mask may yield a bias that survives increasing regular m. `Model.source` additionally normalizes raw emitted photons, hiding raw-number quadrature bias while leaving source energy/photoevent/photoheat kernel biases. New HE26 donor fixes source quadrature in isolation; transport/radiation/Gas native numerical acceptance remains HOLD until integrated and revalidated.

Primary method context: Mirocha et al. (2012), [Optimized Multi-Frequency Spectra](https://arxiv.org/abs/1204.1944), and Friedrich et al. (2012), [C2-Ray H/He multifrequency](https://doi.org/10.1111/j.1365-2966.2012.20449.x). This theorem/diagnostic is a new source-scoped construction, not a quotation of literature results.

**DAG milestone R5:** R2 PASS/source read; R5 DERIVED; C5 implementation in sandbox; C6/C7/C8 pending executed evidence; C10 pending. `native_subagent: NOT_RUN` (no callable native delegation tools).
