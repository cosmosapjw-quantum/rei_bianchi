# HE36 independent derivation: incoming reactive loss moments

Author: independent theory agent `/root/he_latest_synthesis`. This is a direct derivation, not a claim that an empirical atomic or nuclear source has been calibrated. It is a candidate component for workflow1.0.0 / approval0.2. No earlier solver, trajectory, renderer or benchmark is executed here.

## 1. Definitions and the conditional kinetic model

Use a local orthonormal frame with signature (-+++), proper time, masses in kg, number densities in m^-3 and pressure tensors in Pa. Write θ=k_B T. Neither ℏ nor c enters the classical collision integral itself; its domain requires thermal and bulk speeds ≪c. A rate kernel K(E)≥0 has units m³/s and is held fixed as T varies. For a two-body process it is g σ(g) expressed in relative energy E=μg²/2, where μ=m_A m_B/(m_A+m_B). The kernel may be an admitted total reactive cross section; it supplies only the frequency of removal of each incoming parent. Product differential moments, radiation/recoil and final-state branching are independent inputs.

At common bulk velocity zero and common temperature T, incoming species are independent Maxwellians plus small STF first variations:

\[
f_s(\boldsymbol v)=f_{Ms}(\boldsymbol v)
\left[1+\frac{m_s}{2n_s\theta^2}\pi_{s,ij}v_i v_j\right]+O(\pi^2),
\qquad P_s=n_s\theta I+\pi_s,\quad\operatorname{tr}\pi_s=0.
\]

This equation denotes a linear response / Grad first variation. A nonzero traceless quadratic Grad polynomial is negative in some sufficiently large velocity direction. It is therefore not an everywhere-positive finite-anisotropy PDF. The same first variation follows from a positive anisotropic Gaussian family near its isotropic point. None of the results below supplies a global positive nonlinear closure.

## 2. Maxwellian energy-moment ladder

The relative Maxwellian energy probability is

\[
d\mathbb P_T(E)=\frac{2}{\sqrt\pi}\frac{E^{1/2}}{\theta^{3/2}}e^{-E/\theta}\,dE.
\]

Define M_j(T)=⟨E^j K(E)⟩, α=M_0, β=M_1 and γ=M_2. Under differentiation under the integral, with the kernel and its domain fixed,

\[
T\partial_T M_j=\frac{M_{j+1}}{\theta}-\frac32M_j.
\]

Consequently

\[
\boxed{\beta=\theta\left(T\alpha'+\frac32\alpha\right)},
\qquad
\boxed{\gamma=\theta^2\left(T^2\alpha''+5T\alpha'+\frac{15}{4}\alpha\right)}.
\tag{1}
\]

The second derivative is an ordinary derivative with respect to T, not a derivative with respect to log T. Equivalently, with D=T∂_T,
β=θ(D+3/2)α and γ=θ²(D+5/2)(D+3/2)α. The extra +1 comes from differentiating θ in the first identity.

If K depends explicitly on T (screening, population-dependent internal structure, phenomenological interpolation changes), then Eq. (1) acquires kernel-derivative terms. Even the first relation becomes β=θ[Tα′+3α/2−T⟨∂_T K⟩]. A fitted α(T) does not remove that obligation. Likewise, differentiating a fit twice is an algebraic closure prescription until its relation to a microscopic nonnegative kernel and error is established. Small rate-fit error alone does not bound derivative or second-moment error.

For nonnegative K and finite moments,

\[
\alpha,\beta,\gamma\ge0,\qquad \alpha\gamma\ge\beta^2.
\tag{2}
\]

For α=0 all retained moments vanish. For α>0 the last relation is Cauchy–Schwarz for the positive measure K d𝓟. These are necessary moment-consistency gates, not a sufficient proof that an arbitrary fitted triple comes from one microscopic cross section across a whole temperature interval. Signed DR fit summands must not be treated as separate positive physical channels or clipped to pass these conditions.

## 3. Stationary isotropic bath: direct angular projection

First take a parent of mass m and a stationary bath n_t, with E=mv²/2 and loss operator C[f]=−n_t K(E)f. The angular identities are

\[
\langle\hat v_i\hat v_j\rangle_\Omega=\delta_{ij}/3,
\qquad
\langle\hat v_i\hat v_j\hat v_k\hat v_l\rangle_\Omega
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}+\delta_{il}\delta_{jk}}{15}.
\]

The traceless variation contributes zero to scalar number and kinetic-energy integrals. Since v⁴=4E²/m², contraction of the fourth angular tensor with π gives twice π. Thus

\[
R_n=-nn_t\alpha,\qquad Q=\frac12\operatorname{tr}\mathcal S^{\rm kin}=-nn_t\beta,
\]
\[
\mathcal S^{\rm kin}=-n_t\left[\frac23n\beta I+\kappa_2\pi\right],
\qquad
\boxed{J=-n_t\kappa_2\pi},\qquad
\kappa_2=\frac{4\gamma}{15\theta^2}
=\alpha+\frac43T\alpha'+\frac4{15}T^2\alpha''.
\tag{3}
\]

κ₂ has the units of a rate coefficient m³/s; ν_loss=n_tκ₂ is s^-1. This is an instantaneous loss projection of the selected incoming distribution. A reaction event coefficient α is generally different from κ₂. The net reactive J also includes product birth and outgoing surviving-particle terms.

For constant K, β=(3/2)θα and γ=(15/4)θ²α, so κ₂=α and the full tensor is removed in proportion to P. For K∝E^s with s>−3/2, α∝T^s and κ₂/α=4(s+3/2)(s+5/2)/15. The integrability condition is imposed on α; moments of higher order then exist for the exponentially decaying Maxwell weight in this power-law example.

## 4. Finite masses: center-of-mass derivation

Let M=m_A+m_B, a=m_A/M, b=m_B/M, μ=abM, a+b=1. Set V=a v+b w and g=v−w, so v=V+b g and w=V−a g. Under the common-T isotropic reference, V and g are independent Gaussians, with ⟨V_iV_j⟩=(θ/M)δ_ij and ⟨g_i g_j⟩=(θ/μ)δ_ij. The rate kernel depends on g only.

Write t=θ/M. For any STF tensor Z, direct independent Gaussian and angular contraction gives

\[
\langle vv\,K\,(Z:vv)\rangle_{\rm STF}
=\left(2t^2\alpha+\frac{8b^2t\beta}{3\mu}
+\frac{8b^4\gamma}{15\mu^2}\right) Z,
\]
\[
\langle vv\,K\,(Z:ww)\rangle_{\rm STF}
=\left(2t^2\alpha-\frac{8ab t\beta}{3\mu}
+\frac{8a^2b^2\gamma}{15\mu^2}\right) Z.
\tag{4}
\]

Terms proportional to tr Z vanish. The mixed Vg terms produce the middle coefficients; dropping them would give a wrong finite-mass coupling.

Multiplying Eq. (4) by the masses, density product and each Grad normalization yields, with κ₁=2β/(3θ), κ₂=4γ/(15θ²),

\[
A=a^2\alpha+2ab\kappa_1+b^2\kappa_2,\quad
B=b^2\alpha+2ab\kappa_1+a^2\kappa_2,\quad
C=ab(\alpha-2\kappa_1+\kappa_2),
\]
\[
\boxed{\begin{pmatrix}J_A\\J_B\end{pmatrix}
=-\begin{pmatrix}n_B A&n_A C\\n_B C&n_A B\end{pmatrix}
\begin{pmatrix}\pi_A\\\pi_B\end{pmatrix}.}
\tag{5}
\]

Each independent STF component obeys this same 2×2 instantaneous block. In LRS, π_s=q_s diag(−1,−1,2), Eq. (5) applies to (q_A,q_B). Scalar parent sources are

\[
R_A=R_B=-n_A n_B\alpha,
\]
\[
\boxed{Q_A=-n_A n_B[(3/2)a\theta\alpha+b\beta]},\qquad
\boxed{Q_B=-n_A n_B[(3/2)b\theta\alpha+a\beta]}.
\tag{6}
\]

The sum is −n_A n_B[(3/2)θα+β]. It is the kinetic energy of both **removed parents**, including their center-of-mass energy. It is not the net RR/CI/nuclear cooling law. For a capture product, its birth motion typically retains center-of-mass energy, and the radiation/daughter/recoil moments determine the remainder. Those moments must be provided and added before claiming net Q or J.

The limit m_B/m_A→∞ gives a→0,b→1: J_A→−n_Bκ₂π_A, recovering Eq. (3), while the complementary parent retains its own removal term. A stationary cold target is a different reference from the common-T finite-mass family for its own target moments; only the projectile projection is identified in this limit.

## 5. Dissipation and the sign of cross coupling

Let L be the negative matrix in Eq. (5) and W=diag(1/n_A,1/n_B). WL is symmetric. Its determinant is positive because

\[
AB-C^2=(a+b)^2\left[(a-b)^2\alpha\kappa_2
+2ab\kappa_1(\alpha+\kappa_2)\right].
\tag{7}
\]

For positive masses/densities and a nonzero nonnegative integrable kernel with support at positive energy, α,κ₁,κ₂>0. Hence WL is negative definite. The frozen-state quadratic form π_A:π_A/n_A+π_B:π_B/n_B decreases under this instantaneous linear block. This statement holds with the coefficients/densities frozen; it is not a global entropy or finite-step positivity theorem for a reacting and thermally evolving mixture.

C can have either sign. Its radial integrand is proportional to 1−4x/3+4x²/15, with roots (5±√10)/2. Nonnegative kernels concentrated between these roots give negative C. For the physical-shaped family K∝E^s,

\[
\frac{C}{ab\alpha}=\frac4{15}s(s-1).
\tag{8}
\]

For constant cross section K∝g (s=1/2), C=−abα/15. With equal masses and densities n, A=B=79α/60 and C=−α/60; the positive loss eigenvalues are 13nα/10 and 4nα/3. Negative off-diagonal C does not violate weighted dissipation. One cannot infer species-by-species monotonic decay of signed anisotropy from the whole-block result.

## 6. Positive counterexample: equal number/heat rates, different STF source

Freeze a reference temperature T₀, θ₀=k_B T₀, and K₀>0. Define two temperature-independent microscopic functions

\[
K_1(E)=K_0,\qquad K_2(E)=\frac{2K_0}{5}\left(\frac E{\theta_0}-\frac52\right)^2\ge0.
\tag{9}
\]

The appearance of T₀ sets a fixed energy scale; it is not varied when differentiating α(T). At T=T₀, the Maxwell moments ⟨x^r⟩=(3/2)_r give

| Quantity | K₁ | K₂ |
|---|---:|---:|
| α/K₀ | 1 | 1 |
| β/(θ₀K₀) | 3/2 | 3/2 |
| γ/(θ₀²K₀) | 15/4 | 27/4 |
| κ₂/K₀ | 1 | 9/5 |

Thus a scalar number rate and captured-energy moment at one T do not determine the STF sink. Their common first derivative α′(T₀)=0 is also insufficient; second derivatives differ. Explicitly α₁(T)=K₀ and α₂(T)=K₀[(3/2)(T/T₀)²−3T/T₀+5/2], so α₂″(T₀)=3K₀/T₀².

For equal finite masses, K₁ gives A=B=K₀,C=0. K₂ gives A=B=6K₀/5,C=K₀/5. At equal n the eigenvalues change from (nK₀,nK₀) to (nK₀,7nK₀/5), despite identical scalar parent number and kinetic-energy sinks. This is a bounded counterexample to one proposed identification, not a strong no-go theorem against determining moments when a full microscopic kernel or exact α(T) transform is available.

## 7. Source assembly, particle counts and frame guard

For a complete event with stoichiometric changes ΔN_s, total proper-volume event rate ℛ and supplied kinetic increments ΔK_s and STF increments ΔΠ_s, the source adapter forms R_part=ℛΣ_s ΔN_s, Q=ℛΣ_s ΔK_s and J=ℛΣ_s ΔΠ_s. Photons, neutrinos and escaping components have separately declared reservoirs rather than being silently included in the thermal particle count. Baryon conservation is mass-number weighted; nuclear reactions need not preserve the count of heavy particles. Atomic ionization/recombination can change the free-electron count with fixed nuclei; nucleus-changing processes cannot use R_part=R_e without the heavy-particle term.

One source ledger must own kinetic, ionic/rest-mass reference, radiation and nuclear release energies exactly once. A β-based donor RR net cooling formula and the parent-removal Q in Eq. (6) are different quantities. Adding both would double count removed kinetic energy. An unspecified birth moment remains unknown, including when the incident radiation is isotropic.

The present derivation uses the common rest frame. In a general reactive drifting species with mass m_s fixed per species, number source R_n, momentum source F and raw second moment source R₂, central pressure source is

\[
C_s=R_{2,s}-u_sF_s^T-F_su_s^T+m_s R_{n,s}u_su_s^T.
\tag{10}
\]

The last term vanishes in a fixed-density elastic problem or at u_s=0. HE35's elastic centralization formula cannot be used for a drifting birth/death source while omitting this number-source term.

## 8. Reuse and limits

The established HE33 definition Q=tr S_kin/2 and J=S_kin−(2Q/3)I is retained. HE35 finite-mass elastic gain/loss is a distinct operator; this unit supplies incoming reactive loss only. THERM donor Maxwellian first-energy moment supplies β under its own kernel/fit conditions; it does not independently validate γ or product tensor moments. Matched D PI/RR source moments, CI outgoing electrons, CX species transfer, nuclear daughter distributions and stopping remain their respective provider dependencies.

The algebraic checks in CHECKS.json use standard-library exact rational arithmetic. An attempted optional SymPy check encountered ModuleNotFoundError before any science execution; that environment failure is retained separately and did not change the derivation. No old scientific execution was repeated.
