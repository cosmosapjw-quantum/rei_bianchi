# Static collinear Coulomb exterior-sector bound

This is a derivation in the present bounded work unit, not an assertion of novelty or independent review. Assume a spinless scalar electron, T=-Delta/2 in atomic units, static nonnegative charges Zi on one z axis, Q=sum Zi>0, and no magnetic, rotational, ETF or time-dependent additional operator. Nuclear repulsion is omitted.

For one center and a fixed m, use spherical partial waves l>=|m|. Translation of the center along the z axis commutes with Lz. The reduced radial operator is

h_l = -(1/2)d^2/dr^2 + l(l+1)/(2r^2) - Q/r.

Put D_l=d/dr-(l+1)/r+Q/(l+1). On a dense quadratic-form core with vanishing endpoint terms,

<u,h_l u> + Q^2/[2(l+1)^2] ||u||^2 = (1/2)||D_l u||^2 >= 0.

Equivalently, h_l+Q^2/[2(l+1)^2]=D_l^dagger D_l/2. Hardy and Cauchy-Schwarz give integral |psi|^2/r <= 2||gradient psi||||psi||; the Coulomb form is controlled and the inequality extends by Friedrichs form closure. Hence T-Q/ri >= -Q^2/[2(|m|+1)^2] in the same fixed-m Hilbert space for every axial center i.

With wi=Zi/Q, the exact operator decomposition is H=sum_i wi(T-Q/ri), wi>=0 and sum wi=1. Therefore

H|_m >= -Q^2/[2(|m|+1)^2],
H|_(direct-sum |m|>=M) >= -Q^2/[2(M+1)^2].

For ZA=1,ZB=2,M=2 this is -1/2 E_A for every R. At R=0 the state with l=|m| and u proportional to r^(|m|+1) exp(-Qr/(|m|+1)) saturates the bound, so a universally stronger constant cannot be asserted over a domain including R=0. H1_0 functions on a same-axis Dirichlet ball inherit the inequality under zero-extension to full space. This form-domain observation is not implementation of cross-box embeddings.

The result covers infinitely many high-m sectors directly; it is not an extrapolation from calculated m2 roots. It does not certify the selected approximate Ritz energies, omitted roots in m0/|m|1, the full-H gap, finite-R atomic correlations, or collision observables. To deduce a target/exterior distance one separately needs a certified target spectral upper enclosure e_plus<-1/2; the available ordinary-quadrature Ritz maximum is not such an enclosure. The reported 0.1807548935849548 and 0.1728107014160001 E_A margins are nominal arithmetic only.

## General-m common-Hilbert embedding

Use the inherited no-Condon-Shortley chart

A_lm(eta)=(-1)^m sqrt[(2l+1)/2 * (l-m)!/(l+m)!] P_l^m(eta), m>=0,
psi_(+/-m)=G_m exp(+/-i m phi)/sqrt(2*pi), psi_-m=conjugate(psi_+m).

SciPy lpmv includes the Condon-Shortley phase, hence its cancellation here. For a fixed |m|, A_lm A_km is a polynomial of degree l+k: (1-eta^2)^m times two polynomials. Gauss-Legendre order n_eta>=lmax+1 integrates the finite mass exactly. Cross-signed-m products vanish on a uniform Fourier rule with n_phi>=2*mmax+1. Radial union cells with n_r>=pmax+1 then give E^dagger W E=M for the same-origin/same-box FEM span. This is an L2 finite-mass isometry, not a PDE residual or unbounded-observable certificate. Actual root archives and conjugate partners are preserved; added m>=2 records are guards, not relabeled selected roots.

Primary convention references checked 2026-10-02: https://dlmf.nist.gov/14.30 and https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.lpmv.html . The analytic bound above is derived here; convention references are not substituted for a source of numerical results.
