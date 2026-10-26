# H1 electric-dipole angular source: conditional construction

Evidence state: derived; exact polynomial angular moments checked with Wolfram.
This closes a conditional angular-map lemma, not a canonical full-provider node.

## Definition and assumptions

Use metric (-,+,+,+), the local orthonormal observer tetrad, stationary ground-state
H1, a nonrelativistic outgoing electron, and the electric-dipole, heavy-ion limit.
Let k be the unit incident photon direction. Its normalized transverse coherency
matrix rho is Hermitian, positive semidefinite, tr(rho)=1 and rho k=0. It describes
polarization and transforms as a spatial tensor under a rotation of the tetrad.
It is not inferred from the scalar photon energy marginal.

For a 1s initial state, rotational covariance and the electric-dipole selection
rule give the amplitude C(E) epsilon.u for electron direction u. The common radial
factor cancels when conditioning on an absorption event. Therefore

    P(u | rho) = 3/(4 pi) u_i Re(rho_ij) u_j,
    integral_S2 P dOmega = 1.

Positivity follows from rho >= 0. Using the second and fourth spherical moments,

    integral u_i u_j dOmega = 4 pi delta_ij / 3,
    integral u_i u_j u_l u_m dOmega
      = 4 pi (delta_ij delta_lm + delta_il delta_jm + delta_im delta_jl)/15,

one obtains

    <u_i> = 0,
    <u_i u_j> = (delta_ij + 2 Re(rho_ij))/5,
    <u_<i u_j>> = (2/5)(Re(rho_ij) - delta_ij/3).

For unpolarized incident photons rho=(I-kk)/2,

    P(u | k) = 3/(8 pi) [1-(u.k)^2],
    <u_i u_j> = (2 delta_ij-k_i k_j)/5,
    <P2(u.k)> = -1/5.

The second-moment eigenvalues are (2/5,2/5,1/5), all positive. The isotropic
photon-direction mixture gives I/3. Thus angular marginalization is not the
same operation as assuming an isotropic photoelectron distribution per event.

## Joint source and physical observables

For the absorption-event measure dW(Egamma,k,rho), define

    dQ(E,u) = integral delta(E-Egamma+chi) P(u|rho) dW dE dOmega,
    chi = 13.6 eV in the inherited H1 source convention.

Its energy marginal equals the already admitted primary source. At each event,
electron momentum magnitude is sqrt(2 m_e E), and kinetic stress injection is

    d(dot P_ij) = 2 E <u_i u_j> dW,
    d(dot pi_ij) = (4 E/5)(Re(rho_ij)-delta_ij/3) dW.

Here E must be in joules and dW in m^-3 s^-1 for stress injection in
J m^-3 s^-1. The trace is 2 E dW, independent of polarization. For an
unpolarized beam d(dot pi_ij)=-(2 E/5)(k_i k_j-delta_ij/3)dW.
These are kinetic stress sources, not thermal heat. Integrating over angle
preserves the number source and the original photon/binding/kinetic energy ledger.

## Symmetry, invariants, and observables

- Symmetry/gauge: rho and the moment tensor rotate together under tetrad rotations;
  polarization-basis changes leave the coherency tensor and P invariant. The
  source number convention is inherited unchanged.
- Invariants: probability normalization, positivity, zero dipole in the E1
  approximation, trace 2E per event, and unchanged event ownership.
- Observable connection: the signed STF kinetic stress can feed a BASS stress
  equation once the same-source angular inventory and recoil convention are
  supplied. No numerical anisotropic stress is claimed from the energy-only file.

## Validity and remaining physical input

The E1 result omits nondipole forward/backward asymmetry and finite-mass recoil.
The ion's momentum transfer and recoil energy must be included before admitting
a finite-mass four-force law; zero electron mean momentum alone does not balance
the incident photon momentum. No error radius for this approximation is assigned.

The PR233 atom file retains birth and observer energies but does not retain each
birth time/direction/polarization. Neither the full joint measure nor its stress
can be reconstructed uniquely from that energy marginal. The original forward
integrand has the needed direction variable; a future authorized emission can
preserve it without changing the photon model. This is an input-retention task,
not a new arbitrary isotropic closure.

The scalar CDF remains a finite-quadrature diagnostic. This angular lemma supplies
no continuum-CDF error bound and requires no rerun of the saved quadrature.

## Check and source scope

Wolfram's first full trigonometric tensor integration reached its 5-second limit.
The diagnosed cost was redundant symbolic azimuthal integration. The repaired
check integrates the exact polynomial mu marginal after using azimuthal symmetry:
normalization 1, first moment 0, longitudinal moment 1/5, transverse moment 2/5,
quadrupole -1/5, with all five exact residuals zero. Both tool outcomes are retained.

S. H. Lin, Canadian Journal of Physics (1968), DOI 10.1139/p68-639, is a contextual
primary reference on anisotropic hydrogen photoionization. Only its abstract was
retrieved; it is not claimed as a verified equation source for these coefficients.
The coefficients above follow from the displayed amplitude and spherical moments.

No new strong no-go, numerical cross section, runtime activation, or canonical
node completion is claimed by this conditional construction.
