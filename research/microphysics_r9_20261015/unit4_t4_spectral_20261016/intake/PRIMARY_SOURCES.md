# Primary sources for the next finite-space calculation

Accessed 2026-10-16 KST. Two targeted Exa searches returned five candidates each; selected primary pages were opened directly. SciSpace returned ten candidates, including duplicate records; these were discovery aids, not independent scientific validation.

1. PySCF developers, `pyscf.fci.direct_spin1`, https://pyscf.org/_modules/pyscf/fci/direct_spin1.html . The official implementation uses `absorb_h1e(..., fac=0.5)` before `contract_2e` for the complete electronic Hamiltonian action. The input tensor to `contract_2e` is not directly the bare electron-repulsion tensor. The repository's frozen V6 `raw_action` already implements this convention and an occupation-list link-table route at orbital rank >=64. The new runner must reuse that route and the pinned installed PySCF environment; this live documentation is explanatory rather than a replacement source lock.

2. G. H. Golub and G. Meurant, *Matrices, moments and quadrature*, author-hosted manuscript https://gerard-meurant.fr/mmq_1993.pdf and Stanford copy https://stanford.edu/class/cme335/sccm93-07.pdf . The spectral measure of a symmetric matrix and starting vector connects Lanczos projection to Gaussian quadrature. Quadrature nodes come from the projected matrix and weights from the first eigenvector components. This supports a finite spectral diagnostic; it supplies no physical identification of continuum channels.

3. Wolfram Language symbolic calculation is retained in `WOLFRAM_MOMENT_CHECK.json`. It checks exact-ground conditional-moment algebra and numerical evaluation of recorded decimal inputs. Finite residual corrections are derived separately in the T4 contract. High-precision arithmetic on stored decimals does not establish extra physical precision.
