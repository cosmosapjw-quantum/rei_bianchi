# Bianchi I initial shear, physical stresses and population response

2026-10-28. Selected R2/R3/R5/R7: analytical construction and bounded algebraic checks only. Requested authority Astra; actual runtime identity unobserved. Existing AGENTS.md and unchanged physmath-research-loop1.3.0 policies were read/reused. The completed PR248 pilot and its closures remain unchanged. No new background or chemistry IVP is selected.

## 1. Frame, units and exact gravitational system

Use signature(-,+,+,+), proper seconds t, metric ds²=−c²dt²+h_ij(t)dx^i dx^j, a=(det h)^(1/6), H=dot a/a. The normal congruence is geodesic, irrotational and non-tilted. Tensor components below are measured in its nonrotating Fermi-propagated orthonormal triad; the dot on them is the corresponding projected proper-time derivative, not an ordinary derivative of coordinate covariant components. A constant initial spatial coordinate transformation can set h_ij(t0)=a0²δij. It cannot remove physical shear or a relative stress eigenframe orientation.

Let σ_ij be symmetric tracefree, in s^-1, σ²=σ:σ/2, κ=8πG/c², ρ_A energy density J/m³ (includes rest energy), p_A,π_Aij pressures in J/m³, and Q_A energy transfer J/(m³s). Λ has units m^-2. With zero total normal-frame energy flux and Bianchi I spatial curvature0:

    3H² = κρ + Λc² + σ²,
    dot H = −H² −(2/3)σ² −κ(ρ+3p)/6 + Λc²/3,
    dot σ_ij + 3Hσ_ij = κ Σ_A π_Aij,
    dot ρ_A + 3H(ρ_A+p_A) + σ:π_A = Q_A.

Here ρ=Σρ_A and p=Σp_A. The equivalent constrained equation is dot H=−κ(ρ+p)/2−σ². Summing components cancels internal Q_A. A genuinely closed Einstein system requires ΣQ_A=0 after all reservoir components are included. For externally forced prescribed backgrounds, excluded reservoirs can supply a nonzero sum; those equations are then bookkeeping on a prescribed geometry and do not establish a self-consistent Einstein solution.

Derivation: subtract the trace from the mixed spatial Einstein evolution equation (intrinsic spatial Ricci=0) to obtain the STF shear equation. The normal-normal Einstein equation gives the Hamiltonian constraint. Contract each component stress-energy conservation equation with the normal to obtain the pressure/shear work term with the displayed plus sign on its left. The Raychaudhuri equation gives the second line. Define C=3H²−κρ−Λc²−σ²; direct differentiation gives dot C=−2HC for ΣQ=0, since dot σ²=−6Hσ²+κσ:π. Hence initially satisfied constraint remains satisfied. This algebraic identity was actually checked in Wolfram.

General σ and π need not commute. They cannot be diagonalized simultaneously by one rotation, nor may their evolving eigenframes be held fixed without a justified symmetry. The full tensor equation above carries relative orientation. A diagonal/LRS restriction is an explicit submodel, not a generic Bianchi I assertion. Net momentum flux must obey the momentum constraint; the even distributions below provide each component zero flux. Tilted components with canceling total flux require additional momentum evolution and are not silently added here.

## 2. Positive-distribution initial stress, including cold/warm matter

For a nonnegative, even-in-momentum phase density f_A(p), include the same positive phase-space measure dν in every moment:

    E(p)=sqrt(m²c⁴+p²c²),
    ρ=∫E f dν,  P_ij=∫(c²p_i p_j/E)f dν,
    p=Tr(P)/3,  π=P−pI.

This ensures positive-semidefinite P, 0≤3p≤ρ and therefore π eigenvalues≥−p. Photon m=0 gives3p=ρ exactly. Matter stress is bounded by kinetic pressure, not freely chosen at order its rest-mass energy. Pressureless dust has π=0; anisotropic stress assigned to truly cold dust is inconsistent. Collisionless warm matter may have π≠0, but its magnitude scales with velocity dispersion. A thermal baryon stress is a distinct proposed theoretical extension with its own velocity/closure; it does not modify the pilot's isotropic baryon bath.

A constructive generic initial ansatz is f(p,n)=f0(p)[1+A_ij n_i n_j], A symmetric tracefree. It is nonnegative exactly when λ_min(A)≥−1. It has zero dipole and unchanged monopole. Angular integration gives

    π_rad=(2ρ_rad/15)A_rad,
    π_massive=(2p_massive/5)A_massive.

Different components may use different rotated tensors A=R diag(a1,a2,−a1−a2)Rᵀ. Thus tracefree amplitude, positive-distribution domain and relative orientation are exposed without fabricating a kinetic closure. The smooth quadrupole family is a useful subset of all physical stress distributions, not an exhaustive parameterization. Initial moments alone do not determine future collisionless moments; f or a justified closure is still needed for a future IVP.

For the axisymmetric subset write D=diag(−1,−1,2), A=(q/2)RDRᵀ, −1≤q≤2. Then f=f0[1+qP2(n·e)], π_rad=ρq RDRᵀ/15 and π_m=pq RDRᵀ/5. For a mono-speed massive shell, w=p/ρ=v²/(3c²); a narrow smooth radial distribution can replace the shell. This family yields ⟨P2⟩=q/5 and ⟨μ²⟩=(5+2q)/15, checked in Wolfram. For fixed q, equal energy densities and a nonrelativistic component, its stress is reduced relative to radiation by3w.

## 3. Constraint-consistent shear parameters and inherited sign

Choose positive initial component densities, Λ, and a dimensionless STF tensor S=σ/H. Let Ωσ=Tr(S²)/6<1, assuming κρ+Λc²>0. Set

    H0=sqrt[(κρ0+Λc²)/(3(1−Ωσ0))],  σ0=H0 S0.

This holds matter/radiation energy densities fixed while varying shear and satisfies the constraint exactly. Holding H,ρ and an arbitrary changed σ simultaneously is inconsistent. A sign-paired shear S→−S keeps H0 fixed because Ωσ is quadratic. Initial chemistry adds its actual rest/thermal contribution to the chosen matter inventory only once; abundance fractions alone do not fix the total cosmological matter or radiation density.

The existing source is LRS:

    ds²=−c²dt²+a²e^(−2b)(dx²+dy²)+a²e^(4b)dz²,
    σ=sD,  s=dot b,  S=s/H,  Ωσ=S²,
    ||σ||F/H=sqrt(6)|S|.

Do not replace this Frobenius normalization by historical sqrt(3)|s|/H. Initial b0 can be set0 as a coordinate normalization; s0 cannot.

The actually recovered grid044 donor has b0=0, s0/H0=0.24494897427831772, H0=1.2206975634162752e-16s^-1 and s0=2.990086160628583e-17s^-1. Thus Ωσ0=(s0/H0)²≈0.06 and ||σ||F/H≈0.6. This is a substantial anisotropy stress-test, not a near-FLRW or observationally calibrated initial state. The small-shear formulas below describe separate analytical controls and are not retrofitted as controlled perturbation theory for that existing donor. The three distinguishable quantities are σ²=3s², ||σ||F²=6s², and Ωσ=s²/H².

For a stress axis tilted by θ relative to the shear axis, the signed radiation work is

    σ:π_rad = (2/5)sρ_rad q_rad P2(cosθ).

Aligned positive s,q gives positive work: the component loses more energy than isotropic expansion alone. Opposite sign or sufficiently transverse alignment reverses the shear-work contribution. θ=arccos(1/sqrt3) makes the instantaneous contraction0 despite nonzero stress and shear. A sum of stress norms loses this physical cancellation and must not replace Σπ as a tensor.

## 4. Exact free and conditional forced response

For π=0, σ(t)=σ0(a0/a)^3 exactly and σ²∝a^-6. This statement is for the physical orthonormal tensor; coordinate covariant components contain scale-factor factors. On a weak-shear fixed dominant FLRW background H=H0 x^-p, x=a/a0, the normalized shear scales σ/H∝x^(p−3). Radiation p=2 givesx^-1; pressureless matter p=3/2 givesx^-3/2; deSitter p=0 givesx^-3. The power laws for normalized shear are conditional small-shear backgrounds; exact free shear may itself change H when dynamically important.

For a specified tensor stress history, integrating factor gives

    σ(t)=x^-3[σ0+κ∫t0^t x(u)^3 π(u)du].

This is an exact identity along a self-consistent solution, or a forced response on an explicitly prescribed a,π. At first order about FLRW, one may use the unperturbed a and selected first-order stress. With H=H0x^-p and π=π0x^-m in fixed Fermi-frame orientation:

    σ(x)=x^-3[σ0+(κπ0/H0)F_(3+p−m)(x)],
    F_n(x)=(x^n−1)/n,  F_0(x)=ln x.

This closed formula is the current executable benchmark, not a new IVP. Fixed radiation-like stress m=4 gives a sustained normalized leading response in the radiation background and a slowerx^-1 normalized tail in matter background. Nonrelativistic collisionless kinetic stress scales approximatelym=5 on an isotropic background (number∝a^-3, velocities∝a^-1); its matter-era forcing integral converges and leaves a free-likex^-3 shear tail. These are imposed power-law responses. A self-consistent collisionless angular distribution may change stress orientation/amplitude and may partially oppose shear. No unconditional monotonic shear or isotope-response theorem follows.

Barrow–Maartens' primary study discusses slower, including logarithmic, anisotropy decay with dynamically coupled tracefree stresses. Its coupled asymptotics must not be transplanted onto the constant-quadrupole forced formula above. We use that source as evidence that free-shear extrapolation is insufficient, not as a replacement closure.

## 5. Angular radiation versus scalar ionization

Spatial translation invariance conserves photon covariant momenta. In the inherited LRS metric, with initial b0=0,

    E=E0 x^-1 sqrt[(1−μ0²)e^(2b)+μ0²e^(−4b)],
    μ=μ0e^(−2b)/sqrt[(1−μ0²)e^(2b)+μ0²e^(−4b)],
    dot E/E=−H−σ_ij n_i n_j=−H−2sP2(μ).

Thus positive s redshifts axial rays faster and transverse rays slower at fixed mean a. Wolfram gives ∂_b(E x/E0)|0=1−3μ0²=−2P2. Photon packet counts per conserved reference nucleus have no second angular Jacobian when pushed forward. Spectrum and direction evolve; counts do not acquire an invented angular weight.

For isotropic unpolarized targets at rest, a local scalar photo-rate depends on the spectral angular monopole: Γ=∫σ(E)F_E(Ω)dEdΩ. A pure angular quadrupole with fixed monopole leaves that instantaneous rate unchanged. Shear subsequently changes angle-dependent energies and thresholds, feeding the monopole. For smooth spectra away from non-differentiable thresholds, an initially isotropic field has vanishing first-order monopole shift because ⟨P2⟩=0. Define g0(E)dE as angular-integrated photon number per conserved Href in the reference spectrum; its angular measure is [1+qP2(μ)]dΩ/(4π), with q constant across this illustrative spectrum. At fixed mean expansion and reference density, the leading small-b perturbation is δΓ=−(2bq/5)c nHref∫g0(E)Eσ'(E)dE. With c in cm/s, nHref in cm^-3, σ in cm² and E in eV, δΓ has units s^-1. For declining σ above threshold this factor can have the opposite sign to loss of photons crossing below the threshold. Narrow photon bins at a threshold invalidate the smooth Taylor inference and can produce leading nonanalytic effects.

Consequently more initial shear does not imply uniformly more/less ionization, n production, T production or LiIV. Recombination depends on n_e and T, photon nuclear channels have different thresholds, and elapsed proper time changes when H changes. A conditional chemical tangent on a known background is δdot y=J_y δy+J_TδT+J_eδn_e+J_ΓδΓ, with initial δy independently specified; this equation is a future response contract, not an executed result here. Anisotropic matter affects chemistry gravitationally through H/σ and, only if physically specified, through collision/source channels. Matter quadrupole is not itself an atomic photoionization flux.

## 6. Small paired analytical sensitivity matrix

The seven rows below compare geometry/stress formulas, with the same explicit density normalization and chemistry held fixed. They are not seven newly authorized cosmological trajectories. Set ε=1e-3, q*=0.05, w_m=1e-6 as illustrative diagnostic values, not observationally inferred parameters. Use radiation- and matter-dominated benchmark H power laws separately. Initial orientation is aligned except for the separate analytic θ work scan.

| Row | S=s/H | q_rad | q_m | Purpose |
|---|---:|---:|---:|---|
| B0 | 0 | 0 | 0 | Isotropic algebraic control |
| S+ | +ε | 0 | 0 | Free positive shear |
| S− | −ε | 0 | 0 | Sign-paired free shear |
| R+ | 0 | +q* | 0 | Positive radiation quadrupole forcing |
| R− | 0 | −q* | 0 | Sign-paired radiation forcing |
| M+ | 0 | 0 | +q* | Finite-pressure matter forcing |
| M− | 0 | 0 | −q* | Sign-paired matter forcing |

Output functions at x=1,2,7 only: F_n, free/forced shear response normalized by its initial/shear-source coefficient, constraint residual, angular moment identities and signed-work at θ=0,π/2,arccos(1/sqrt3). For source amplitudes use normalized κπ0/H0² as independent reported coefficients or leave symbolic; do not infer an unprovided Ωγ/Ωm from the chemistry CSV. Verify zero-source and zero-shear limits, ±pair antisymmetry of linear forced response, radiative stress trace, matter3w suppression, and constraint closure. Full nonlinear future runs require a chosen distribution/closure and new explicit IVP authority; none is started now.

For a compact tensor serialization use(xx,yy,zz,xy,xz,yz), or full3×3 arrays. Contractions must count off-diagonal terms twice in the compact form. Symmetry and tracefree conditions are checked, not silently projected. Roundoff-size residuals use relative1e-12 and absolute1e-14 in normalized benchmark variables.

## 7. Evidence, limits and budget advice

Primary lookup actually used Exa and then opened author pages: Barrow–Maartens, Phys.Rev.D59,043502 (1999), https://arxiv.org/abs/astro-ph/9808268 ; Caceres–Castaneda–Tejeiro, https://arxiv.org/abs/1003.3491 . Exa supplied primary-text abstract/conclusion excerpts; direct HTML full-text retrieval failed, so no unobserved equation numbers are claimed. The tensor equations and identities here are directly derived; the second source flags the physical-versus-coordinate shear derivative distinction. Existing ANGTHERM01 THEORY.md supplies the inherited metric, moment convention and geometry map. IC/recombination primary sourcing is the separate IC investigator's responsibility.

Actual Wolfram outputs: angular normalization1; longitudinal pressure moment(5+2q)/15; quadrupole momentq/5; directional linear derivative1−3μ². A second exact CAS check returned0 for dot C+2HC. These are same-construction algebra checks, not independent review or an evolved solution.

Main620 is a3.333...% temporary increase over original600 and is within the existing less-than50% owner policy. A new at-most4CPU-second non-IVP formula suite plus1tail reserve is a legitimate new scientific bounded job on the same cumulative main ledger:604.395912+5=609.395912<620. It does not reset/transfer planning or presentation balances, consume a closed reservation, or revive the closed three-IVP exception. Root should record the new scientific scope, exact command, estimated versus actual costs, UNKNOWN_NOT_ZERO overhead, and restore600 afterward. No new plot or IVP is required to close this analytical unit.

This construction contributes to REI-L0 signed STF work and clarifies prospective REI-L3 baryon-stress, L4 live-H/shear and L5 initial-data interfaces. It does not itself close those original physical DAG nodes or change33/88. Newly completed local analytical subobligations may be reported explicitly after bounded checks and one independent review; no invented global completion count.
