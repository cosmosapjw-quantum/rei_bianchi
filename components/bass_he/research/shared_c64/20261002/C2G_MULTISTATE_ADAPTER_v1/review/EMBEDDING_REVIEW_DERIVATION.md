# Independent check of the proposed common embedding

This note checks the adapter construction proposed for C2g. It is a derivation, not numerical evidence, and does not certify the pointwise Coulomb operator or continuum spectrum.

For fixed charge-center coordinates O, a finite-element coefficient vector c maps to sampled physical values E c. With normalized azimuthal modes exp(i m phi)/sqrt(2 pi), all sampled states share physical weights W = diag(r^2 w_r w_eta w_phi). All r nodes lie strictly inside positive radial intervals.

Use the union of every represented radial mesh. Each radial u_l is a degree-p polynomial on each resulting cell, and the r^-1 factors in the wavefunction cancel r^2 in W. Thus radial Gauss-Legendre order at least p+1 integrates each u_l u_k product exactly in exact arithmetic. For equal m, normalized associated-Legendre products are polynomials of degree at most l+k, so eta order at least lmax+1 is sufficient. Uniform distinct azimuth nodes with n_phi >= 2 mmax+1 integrate exp(i (m-n) phi) exactly for every represented mode pair. Different m sectors therefore vanish independently of their non-polynomial eta cross-products. It follows that E^dagger W E = M for each represented finite sector, with zero cross-sector blocks.

For a real symmetric weak Hamiltonian H and positive definite mass M, define on the common sampled Hilbert space

H_emb = E M^-1 H M^-1 E^dagger W.

Then H_emb is self-adjoint in the W inner product. On the embedded FEM span, H_emb E c = E M^-1 H c, and

(E C)^dagger W H_emb (E C) = C^dagger H C.

Therefore a measured C^dagger H C may be supplied as the actual selected projected operator for this explicitly declared finite weak-form embedding. It is not a pointwise PDE evaluation. The extension above acts as zero on the W-orthogonal complement of the represented FEM span; that artificial complement is another reason not to infer full-space spectral isolation from a sampled guard gap.

For the registered real, spinless, static axial Hamiltonian, m=+1 and m=-1 sectors may use the same real meridional eigenfunction multiplied by conjugate azimuthal phases. Their degeneracy and conjugacy are exact by construction, so parity measurements do not independently validate the omitted sector physics. This reconstruction must be disabled if magnetic, spin, rotating-frame, or other symmetry-breaking terms enter.

Changing R changes the two nuclear positions while O remains the common coordinate origin. Changing the numerical origin without an explicit physical translation is inadmissible. A common box and grid are necessary here; two directed overlaps on different grids are not a substitute for one shared metric.
