# Shared physics for sandbox kernels

The current tagged PhysMath skill is 1.3.0. This invocation explicitly selects a cross-repository intake, DAG, bounded theory/construction, implementation and verification, followed by publication and continuation instructions. It does not claim completion of the whole reionization project.

## Source and density conventions

The supplied Reionization_Standalone_Dossier(4).pdf, sections 1.2–1.3 and 2.2, was read from Library libfile_933a25043be08191a50ed1d64bfc81e9. Its 17-state vector is n,H0,H+,D0,D+,T0,T+,3He0,3He+,3He2+,4He0,4He+,4He2+,7Li0,7Li+,7Li2+,7Li3+. Electrons and radiation are separate. Current 21-state and 18-family research packages are extensions with their own explicit maps, not interchangeable vector sizes. Retained isotope abundances cannot be renormalized to one when excluded ancestry is nonzero.

For common-rest-frame abundances Y_i=n_i/n_B and reaction rates R_r per proper volume per proper second,
dY_i/dt = sum_r nu_ir R_r/n_B,
sum_i A_i nu_ir=0.
The isotope network conserves baryon number, not the unweighted number of nuclei. Tagged-charge Markov generators instead conserve the number of the tagged nucleus. Nuclear beta events must have one owner in a coupled network.

For nonrelativistic gas with common temperature, thermal energy u=(3/2)n_th k_B T. The local reaction contribution is
Tdot_react = 2 Q_th/(3 n_th k_B) - T R_th/n_th.
For an untilted homogeneous gas, add -2 H T; for a tilted material congruence use its proper clock and expansion, not this shortcut. Q_th excludes changes already assigned to binding/excitation or a retained nonthermal reservoir. Atomic population change and thermal/photon energy change must use the same reaction count.

## Conservative source components

For a photoionization event of threshold I, photon energy E>=I:
(delta binding,delta kinetic,delta photon)=(I,E-I,-E).
For recombination with captured kinetic energy K>=0:
(-I,-K,I+K).
Both sum to zero before quadrature. This is an event-energy identity; it does not supply cross sections, captured-electron distributions or anisotropic radiation moments. The actual Wolfram evaluator checked these sums and the variable-particle-number temperature derivative.

For a prescribed isotropic blackbody bath in the nonrelativistic Thomson limit,
Q_C=4 sigma_T a_R k_B n_e T_gamma^4 (T_gamma-T)/(m_e c),
where Q_C is energy per proper volume per proper second. For frozen particle number, its temperature relaxation is
Gamma_C=8 sigma_T a_R T_gamma^4/(3 m_e c) (n_e/n_th).
It is zero at T=T_gamma or n_e=0, and its sign heats colder gas. A saved-trajectory integral of omitted Q_C measures an omission along that trajectory, not a newly solved coupled thermal history.

## Exact coordinate reduction and solver metric

On an invariant affine subspace y=b+Pz, with selector R satisfying RP=I and F(b+Pz) in range(P), the reduced system is zdot=R F(b+Pz). Its Jacobian is J_z=R J_y P. This is an exact restriction for the specified invariant initial conditions, not a blanket isotope-lumping theorem. H/He/Li normalization eliminates one fraction per elemental block. Dynamic species production or isotope-dependent rates can invalidate the earlier invariant subspace and must be examined before reuse.

A reduced-coordinate adaptive integrator must preserve the intended physical error metric. For full-state scales s_i>0 and full dimension n, use sqrt(sum_i[((P e_z)_i/s_i)^2]/n). Removing variables and simply applying diagonal tolerances in the reduced coordinates changes this gate: an eliminated neutral error is minus the sum of its charged errors. This is the concrete reason for the VigilODE client-side lifted-error kernel. No solver core or production-speed claim follows from this adapter.

## Quadrupole transport functional

For elastic scattering against stationary heavy targets and a small Grad quadrupole, define sigma_2(v)=integral(1-P_2(cos theta)) dsigma. With v_T=sqrt(2k_B T/m), the quadrupole relaxation functional is
nu_pi=n_target v_T/Gamma(7/2) * integral_0^infinity x^3 exp(-x) sigma_2(v_T sqrt(x)) dx.
For sigma_2(v)=sigma_0(v/v_0)^r, r>-8:
nu_pi=n_target v_T sigma_0(v_T/v_0)^r Gamma(4+r/2)/Gamma(7/2).
Wolfram returned the constant-cross-section coefficient 16/(5sqrt(pi)), and its ratio to the ordinary Maxwellian event-frequency coefficient 2/sqrt(pi) is 8/5. Event frequency therefore does not by itself determine pressure relaxation. Finite-mass mixtures and empirical transport rates require their own collision operator/input.

## External theory reused

Exa retrieved and read the primary preprints https://arxiv.org/html/2411.14242 and https://arxiv.org/abs/2606.28895. Their exact-lumping criterion concerns Jacobian-invariant reduction spaces; approximate lumping introduces a separate controlled error problem. This supports explicit separation of exact invariant restriction from approximations. No code from these papers was copied. SciSpace returned Mao et al., The electron energy loss rate due to radiative recombination, DOI10.1051/0004-6361/201629708; the REC lane's pinned primary input remains the authority for its existing hybrid moment model. Search output alone is not source admission.

