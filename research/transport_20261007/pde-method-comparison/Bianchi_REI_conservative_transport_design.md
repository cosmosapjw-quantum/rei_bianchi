# Conservative energy and angular transport for Bianchi reionization

## Purpose and recommendation

An energy–angle PDE is a natural formulation for homogeneous Bianchi reionization. Conservative finite-volume (FV) and discontinuous Galerkin (DG) methods can replace whole-node threshold export with resolved energy-face fluxes. The decisive requirements are simultaneous control of photon number, the physical energy moment, positivity and chemistry exchange. Merely selecting a method called FEM or DG does not establish these properties.

The immediate comparison should retain the current FLRW characteristic solver, add a comoving partial-cell candidate, and use simple fixed-energy FV and DG schemes as **diagnostic baselines**. A production candidate needs an explicit moment-compatible, realizability-aware design. The first angular extension should use prescribed, non-tilted Bianchi I geometry before attempting dynamical Einstein–radiation coupling.

This is a mathematical design and reference note. It reports no newly implemented solver or executed benchmark.

## 1 Physical variables and conservative equation

Assume metric signature \((-+++ )\), observer proper time \(t\), a homogeneous non-tilted Bianchi I background, and a nonrotating orthonormal frame. Write the photon momentum as \(p=E(e_0+n^ae_a)\), with \(n_an^a=1\). The dimensional shear \(\sigma_{ab}\) is symmetric and tracefree. Define

\[
q(n)=\sigma_{ab}n^an^b,\qquad
x=\ln(E/E_\star),\qquad
v_x=-H-q,\qquad
v_\Omega=-(I-nn^{\mathsf T})\sigma n.
\]

Here \(H\) is the mean expansion rate. The equations \(\dot E=E v_x\) and \(\dot n=v_\Omega\) follow from null geodesic transport. Conserved covariant spatial momenta provide an exact diagonal Bianchi I solution; see [Fleury, Pitrou and Uzan, Section IV](https://www2.iap.fr/users/pitrou/publi/PhysRevD.91.043511.pdf).

Let \(f\) be scalar photon occupation, \(A\) its constant phase-space normalization, and \(n_H\) the conserved hydrogen-nucleus density, so \(\dot n_H=-3Hn_H\). The number density measure is \(A E^2 f\,dE\,d\Omega\). Thus

\[
g=\frac{A E^3f}{n_H},\qquad
g\,dx\,d\Omega=\text{photon number per H nucleus}.
\]

If \(Df=Q_f\), where \(Q_f\) is the collision rate per proper time, then

\[
D\ln(E^3/n_H)=-3q.
\]

On the unit sphere,

\[
\nabla_{S^2}q=2(I-nn^{\mathsf T})\sigma n,
\quad \Delta_{S^2}q=-6q,
\quad \operatorname{div}_{S^2}v_\Omega=3q.
\]

The two shear factors cancel, giving

\[
\boxed{\partial_t g+\partial_x(v_xg)
+\operatorname{div}_{S^2}(v_\Omega g)=S_g},
\qquad S_g=\frac{AE^3Q_f}{n_H}.
\]

There is no additional shear source. If the starting Boltzmann equation uses affine parameter, \(df/d\lambda=C[f]\), then \(Q_f=C[f]/E\) in the stated \(c=1\) frame. This normalization must not be confused with emissivity already expressed per H nucleus and proper second.

For photoabsorption, a useful source decomposition is

\[
S_g=S_{\rm em}-\sum_\alpha \kappa_\alpha(E)g+S_{\rm sc},
\qquad \kappa_\alpha=c\,n_\alpha\,\sigma_\alpha(E).
\]

The conservative formulation and the distinction between number conservation and energy-momentum compatibility are consistent with [Cardall, Endeve and Mezzacappa](https://arxiv.org/html/1305.0037v2). The specialized equations above are derived here for the stated Bianchi I assumptions.

## 2 Number and energy moments

Integrate over the full sphere and a fixed physical-energy interval \([x_L,x_R]\). Define

\[
N=\int g\,dx\,d\Omega,\qquad
U=\int E g\,dx\,d\Omega,\qquad
\Pi_{ab}=\int E(n_an_b-\delta_{ab}/3)g\,dx\,d\Omega.
\]

With brackets denoting the upper endpoint minus the lower endpoint,

\[
\dot N=\int S_g\,dx\,d\Omega
-\int [v_xg]_{x_L}^{x_R}\,d\Omega,
\]

\[
\boxed{\dot U+HU+\sigma_{ab}\Pi_{ab}
=\int E S_g\,dx\,d\Omega
-\int [E v_xg]_{x_L}^{x_R}\,d\Omega.}
\]

Consequently, proper radiation density \(u=n_HU\) and anisotropic stress \(\pi_{ab}=n_H\Pi_{ab}\) satisfy

\[
\dot u+4Hu+\sigma_{ab}\pi_{ab}
=n_H\int E S_g\,dx\,d\Omega
-n_H\int [E v_xg]_{x_L}^{x_R}\,d\Omega.
\]

At a lower threshold with \(v_x<0\), the boundary removes photons and crossing energy \(E_L\) per photon. In a more strongly anisotropic background, \(H+q\) can change sign by direction. Boundary conditions must then admit the appropriate inflow, and geometric energy exchange is signed rather than necessarily a positive redshift loss.

The time coordinate \(s=\ln a\) is convenient on a monotone expanding branch. Divide proper-time velocities and rates by \(H\) exactly once. This parameterization requires \(H>0\); proper time remains suitable through \(H=0\).

## 3 What the inspected REI and BASS sources establish

The continuous/adaptive IGM path is currently energy-only. In the inspected REI source, `igm_continuous.rs` stores fixed characteristic coordinates \(\eta\), quadrature weights and counts, with

\[
E=\exp(\eta-s)
\]

when energy is numerically measured in the code's eV unit. It splits time steps at node/support events and exports the entire surviving node count at its HI crossing. These are characteristic quadrature nodes, not angular PDE cells.

The same repository separately contains exact diagonal Bianchi I rays and positive packet deposition into energy–\(\mu\)–\(\phi\) bins. `bianchi_i.rs` implements the direction/energy map, its solid-angle Jacobian and the corresponding derivatives. `angular_photons.rs` implements packet measures and bin deposition. Their existence does not establish an integrated angular FV/DG reionization solver or full REI–BASS coupling.

`igm_photo.rs` assigns shared per-packet/per-absorber photon-loss, ionization and heating owners; `igm_step.rs` checks their number and material-energy exchanges. `igm_source.rs` specifies escaping photons/H/proper-second, with no extra \(a^3\) conversion. These contracts should survive a transport redesign.

The atomic provider distinguishes cross-section support cutoffs from binding energies. Its inspected Verner cutoffs are 13.60, 24.59 and 54.42 eV for HI, HeI and HeII. Aligning energy faces should use the provider support convention; heating and binding bookkeeping should retain their existing owner rather than silently identifying the two energy conventions.

BASS `bianchi/conventions.py` declares signature \((-+++)\), and `bianchi/rays/geodesics.py` uses dimensional proper-time \(H,\sigma,N,A,R\). Its equations reduce to those above when the Bianchi I curvature variables and frame rotation vanish. Hubble-normalized BASS quantities must be explicitly converted before being supplied to the proper-time transport equation.

Source anchors: REI `igm_continuous.rs` lines 29–46, 204–246, 309–342, 419–490; `igm_photo.rs` lines 81–148; `igm_step.rs` lines 286–324; `atomic_provider.rs` lines 104–110; `bianchi_i.rs` lines 185–233. BASS checkout `3192b72d546df8d23084d161ceccd5f97c9627b9`: `bianchi/conventions.py` lines 263–269 and `bianchi/rays/geodesics.py` lines 4–16, 27–37. These describe inspected snapshots, not a claim about an uninspected later branch.

## 4 Three spectral candidates

### Comoving panels with partial-cell integration

In FLRW, \(\eta=x+s\) is constant along collisionless characteristics. Let \(G(s,\eta)=g(s,\eta-s)\), and let a panel span \([\eta_L,\eta_R]\). Its active part above a physical threshold is bounded by \(\eta_{\rm th}(s)=x_{\rm th}+s\). A reconstructed panel distribution gives

\[
N_{\rm active}=\int_{\max(\eta_L,\eta_{\rm th})}^{\eta_R}G\,d\eta,
\quad
U_{\rm active}=E_\star e^{-s}
\int_{\max(\eta_L,\eta_{\rm th})}^{\eta_R}e^\eta G\,d\eta,
\]

with zero contribution when the lower bound reaches the upper bound. The derivative of the moving integration limit supplies the threshold flux. The same partial-panel reconstruction must define number, energy, source support, opacity and heat integrals. Existing node weights alone do not specify a unique positive continuous reconstruction.

This is a smaller FLRW change than introducing spectral advection and may address whole-node crossing artifacts directly. It still requires spectral convergence and positivity checks. In Bianchi I, \(\dot\eta=-q\), so scalar comoving energy no longer eliminates transport, and angular drift remains.

### Fixed physical-energy FV

Fixed threshold-aligned faces make boundary crossing an explicit flux. A number-only, piecewise-constant FV method is a useful positive baseline, but generally does not satisfy the exact physical energy-redshift identity at finite resolution.

For example, a standard upwind discretization in uniformly spaced \(x\), with compact support away from the boundaries, gives

\[
\dot N_i=\frac{H}{\Delta x}(N_{i+1}-N_i).
\]

For energy weights proportional to \(e^{x_i}\), including exact mean-energy weights of constant-\(g\) cells, its energy moment obeys

\[
\dot U_h=-H\frac{1-e^{-\Delta x}}{\Delta x}\,U_h,
\]

rather than \(-HU_h\). Number conservation therefore does not establish physical energy compatibility. Additional energy moments, compatible fluxes or another designed representation are needed if that identity is to hold discretely. Until then, this method should be labeled a diagnostic baseline.

### DG with a physically meaningful energy test

Ordinary polynomial DG in \(x\) contains the number test 1, but generally not the energy weight \(E_\star e^x\). An enriched test space or an explicitly moment-compatible construction is required.

An alternative is physical-energy DG on logarithmically spaced faces. Set

\[
h=g/E,\qquad
\partial_t h+\partial_E[-E(H+q)h]
+\operatorname{div}_{S^2}(v_\Omega h)=S_g/E.
\]

For polynomial degree \(p\geq1\), both 1 and \(E\) belong to the test space. They yield the desired semidiscrete moment identities when numerical face fluxes, volume quadrature, geometry and collision exchange are compatible. This is an advantage of the weak formulation, not an automatic positivity or fully discrete conservation guarantee.

## 5 Why a conventional DG limiter is insufficient

For a linear, nonnegative density \(h\) on \([E_L,E_R]\), write \(\Delta E=E_R-E_L\). Nonnegative endpoint values imply the restricted moment cone

\[
\boxed{\frac{U}{N}\in
[E_L+\Delta E/3,\ E_L+2\Delta E/3].}
\]

An initially empty cell receiving infinitesimal inflow from its upper face has incoming \(U/N\to E_R\). That pair lies outside this cone. No everywhere-nonnegative P1 density in the cell can preserve both newly received moments. Reducing the step size does not remove this representation obstruction.

A usual cell-mean-preserving slope limiter preserves \(N\), while changing the slope and therefore \(U\). A correct pre-limiter weak energy identity is consequently insufficient. Unmodified P1 DG with such limiting is another diagnostic baseline, not a demonstrated simultaneous solution.

Possible remedies require an explicit design and proof or tests: a positive representation with sufficient moment support, conservative subcell/characteristic treatment of partial support, or conservative redistribution with an identified physical approximation and convergence study. Redistribution changes the numerical state and must be distinguished from changing a bookkeeping term to hide a defect. In particular, assigning geometric work from the energy residual would conceal the failure rather than verify the equation.

[Endeve et al.](https://arxiv.org/abs/1410.7431) provide bound-preserving DG conditions for curvilinear phase-space advection, including CFL and geometric-identity requirements. Their fermionic upper bound \(f\leq1\) is not a photon-occupation bound. [Laiu et al.](https://arxiv.org/abs/2309.04429) explicitly analyze number/energy compatibility and realizability in DG–IMEX radiation transport. Their two-moment \(\mathcal O(v/c)\) model is methodological guidance, not a ready-made full-angle Bianchi solver.

## 6 Shared discrete contracts

- Compute each interior numerical face flux once and apply opposite signs to neighboring cells.
- Use the correct spherical measure and conormal flux. For \(\mu=\cos\theta\), \(d\Omega=d\mu\,d\phi\); poles and periodic azimuth still require consistent treatment.
- Make discrete geometry and quadrature consistent with the shear compression identity. Test the angular Jacobian and isotropic limit, rather than assuming Euclidean angular differencing is adequate.
- Use one set of absorbed events for radiation loss, ionization, heat and binding-energy gain, at matching quadrature points and temporal stages.
- Keep explicit transport CFL and implicit collision positivity separate. Nonlinear chemistry must retain physical ionization fractions and positive thermal energy.
- Verify geometric work from \(HU+\sigma:\Pi\) and crossing energy from the actual face flux. Do not infer either from a residual chosen to close the ledger.
- Refine time, energy and angle independently. Report limiter frequency, moment changes introduced by limiting, and any conservative redistribution.

The frequency-advection/implicit-collision organization has precedent in [CASTRO multigroup radiation hydrodynamics](https://arxiv.org/abs/1207.3845), but that paper uses flux-limited diffusion and an \(\mathcal O(v/c)\) model. [thornado](https://github.com/endeve/thornado) is an implementation reference for high-order radiation methods; its existence does not establish drop-in compatibility with REI.

## 7 Minimal comparison benchmark

### FLRW collisionless transport and threshold flux

With \(s=\ln(a/a_0)\), the exact equation is

\[
\partial_s g-\partial_xg=0,\qquad g(s,x)=g_0(x+s).
\]

Choose a smooth positive finite spectral pulse, no upper-boundary inflow, and a lower physical threshold. For angularly integrated \(g\),

\[
N_{\rm out}'=g(x_L,s),\quad
E_{\rm out}'=E_Lg(x_L,s),\quad
U'=-U-E_Lg(x_L,s).
\]

Check independently

\[
N+N_{\rm out}=N_0,\qquad
U+E_{\rm out}+\int_0^s U(\xi)\,d\xi=U_0.
\]

Compare the current whole-node characteristic scheme, reconstructed comoving partial panels, number-only FV, and a specifically documented DG candidate. Report spectral profile error, count/energy balance defects, cumulative threshold flux error, minimum density and computational cost. Include an initially empty cell with upper-face inflow to expose the P1 obstruction. Do not replace failed energy checks with residual-defined redshift work.

### Prescribed diagonal Bianchi I transport

For \(ds^2=-dt^2+\sum_i a_i(t)^2(dx^i)^2\), define

\[
r_i=\frac{a_i(t_0)}{a_i(t)},\qquad
P=\prod_i r_i,\qquad
R(n_0)=\sqrt{\sum_i r_i^2n_{0i}^2}.
\]

The exact characteristic solution is

\[
E=E_0R,\quad n_i=\frac{r_i n_{0i}}R,\quad
d\Omega=\frac{P}{R^3}d\Omega_0,\quad
g=\frac{R^3}{P}g_0.
\]

Use a smooth even angular distribution, \(g(n)=g(-n)\), and check the full number/energy identities, \(\Pi_{ab}\), angular redistribution and the isotropic limit. Prescribed scale factors are a kinematic benchmark, not an Einstein-equation solution claim. First choose expansion along all principal axes; sign-changing energy drift is a later boundary-condition test.

Finally add controlled absorption/emission with shared event owners, then live H/He chemistry. Full dynamical coupling must include radiation stress and satisfy the total momentum constraint. Tilt, polarization and other Bianchi types require their additional frame, scattering and geometric terms; none is supplied merely by adding an angular grid.
