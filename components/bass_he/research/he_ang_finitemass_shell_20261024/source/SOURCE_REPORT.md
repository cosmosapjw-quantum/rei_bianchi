# HEANG next3 primary-source intake (2026-10-24)

## Scope and decisive input

Read-only source intake for parent R2/R4, not independent review or scientific execution. No numerical physics, fitting, quadrature, simulation, remote solver, remote mutations, or new scope/budget freeze was performed.

**Constructive input A:** Kadyrov et al. (2009) supplies explicit arbitrary-finite-mass three-body Jacobi mechanics and energy shell. The root can derive and implement a bounded exact finite-mass shell/Jacobian substrate with this source binding. This is an advance to recoil kinematics; it does not supply or admit an outgoing-electron amplitude/event law.

**Constructive input B (alternative/future):** Attaourti et al. supplies an analytic Coulomb-Born direct-channel construction through its wavefunctions, interaction, and Nordsieck integral. An apparent internal discrepancy in preprint Eq18 requires using the defining overlap Eq16 and independent derivation, not copying Eq18. Exchange, final electron-electron distortion and finite mass remain absent. No candidate is selected or budgeted by this report.

PR98 TDCS413D results, prior DDCS20/CCC/Hex scopes and old exclusions remain reused without rerun. The parent full physical-source gate remains SOURCE_INPUT_PENDING.

## A. Arbitrary finite-mass primary foundation

A. S. Kadyrov, I. Bray, A. M. Mukhamedzhanov, A. T. Stelbovics, *Surface-integral formulation of scattering theory*, Annals of Physics **324**, 1516–1546 (2009).
DOI: https://doi.org/10.1016/j.aop.2009.02.003
Author-hosted published PDF: https://atom.curtin.edu.au/igor/atomlab/sdarticle.pdf
Published PDF first page: received 8 January 2009, accepted 5 February 2009, online 10 March 2009.
Retrieved 2026-10-24; 448174 bytes; SHA256:
c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165

### Exact selected source content, visually verified

Journal pp1527–1528 = PDF pp12–13, §3.1. Private page renders:
private/kadyrov_selected-12.png and private/kadyrov_selected-13.png.
The Greek rho coordinate must not be confused with conjugate q momentum in OCR text.

For arrangement alpha, the pair is beta,gamma. Relative coordinate/momentum are r_alpha,k_alpha; coordinate of particle alpha relative to pair center of mass is rho_alpha, with conjugate momentum q_alpha. Source reduced masses:
\[
\mu_\alpha=\frac{m_\beta m_\gamma}{m_\beta+m_\gamma},\qquad
M_\alpha=\frac{m_\alpha(m_\beta+m_\gamma)}
 {m_\alpha+m_\beta+m_\gamma}.
\]

Eq72:
\[
\mathbf r_\beta=-\frac{\mu_\alpha}{m_\gamma}\mathbf r_\alpha
-\epsilon_{\beta\alpha}\boldsymbol\rho_\alpha,\qquad
\boldsymbol\rho_\beta=\epsilon_{\beta\alpha}\frac{\mu_\beta}{M_\alpha}
 \mathbf r_\alpha-\frac{\mu_\beta}{m_\gamma}\boldsymbol\rho_\alpha.
\]
Eq73:
\[
\mathbf k_\beta=-\frac{\mu_\beta}{m_\gamma}\mathbf k_\alpha
-\epsilon_{\beta\alpha}\frac{\mu_\alpha}{M_\beta}\mathbf q_\alpha,\qquad
\mathbf q_\beta=\epsilon_{\beta\alpha}\mathbf k_\alpha
-\frac{\mu_\alpha}{m_\gamma}\mathbf q_\alpha.
\]
Source defines epsilon_betaalpha=-epsilon_alphabeta, epsilon_aa=0, with its cyclic sign convention. Preserve orientation explicitly when specializing; do not infer signs from garbled extracted text.

Eq74–76 define a mass-scaled hyperradius and hyperangle, with an arbitrary auxiliary mass mu that is not a new physical mass:
\[
R^2=(\mu_\alpha/\mu)r_\alpha^2+(M_\alpha/\mu)\rho_\alpha^2,\qquad
\varphi_\alpha=\arctan[\sqrt{\mu_\alpha/M_\alpha}\,r_\alpha/\rho_\alpha].
\]

Eq78 and following Hamiltonian definition:
\[
(E-H)\Psi_{\alpha n}^{+}=0,\qquad
H_0=-\frac{\Delta_{\mathbf r_\alpha}}{2\mu_\alpha}
-\frac{\Delta_{\boldsymbol\rho_\alpha}}{2M_\alpha},\quad H=H_0+V.
\]
The source permits short-range pair potentials and an optional three-body interaction. For pure Coulomb specialization take those additions zero. Eq79:
\[
V_\alpha^C(r_\alpha)=\frac{z_\beta z_\gamma}{r_\alpha}.
\]
**The energy equation is unnumbered immediately after Eq79**, not Eq79 itself:
\[
E=E_{\alpha n}+\frac{q_{\alpha n}^2}{2M_\alpha}
=\frac{k_\alpha^2}{2\mu_\alpha}+\frac{q_\alpha^2}{2M_\alpha}.
\]
Eq81 initial channel separates into relative cluster wave times pair bound state. Eq82:
\[
\left[\frac{1}{2\mu_\alpha}\Delta_{\mathbf r_\alpha}
 -V_\alpha(r_\alpha)+E_{\alpha n}\right]\phi_{\alpha n}=0.
\]
Eq83–84 asymptotic cluster Coulomb phase uses
\(\bar\eta_\alpha=z_\alpha(z_\beta+z_\gamma)M_\alpha\).
Neutral e+H initial cluster has zero monopole Coulomb phase under the H specialization. This is not a statement that all projectile-target interaction vanishes.

### Mapping to BASS_HE (derived specialization; not printed H-specific equations)

Choose alpha=incident electron, beta=bound electron, gamma=proton; masses (1,1,M), charges(-1,-1,+1), in electron atomic units.
Then \(\mu_\alpha=M/(M+1)\), \(M_\alpha=(M+1)/(M+2)\).
Hydrogen ground-state binding \(E_{\alpha,1s}=-\mu_\alpha/2\) follows by solving the two-body Coulomb problem defined in Eq79/82. It is a derived specialization.
The source E is internal/center-of-mass energy, not the incident electron's laboratory kinetic energy. Lab-to-COM mapping, laboratory outgoing momenta and recoil, admissible shell roots, root multiplicities, coarea/Jacobian factors, endpoint treatment, exchange-label/count policy, and infinite-M limit require explicit root derivation and review.

**Not supplied here:** a lab detector TDCS normalization, an e-H numerical T-matrix/event dataset, a Born approximation, spin trace, a physical identical-electron count factor, measured uncertainties, or an empirical recoil law. Kinematics alone cannot give their values.

The same authors' *Coulomb Breakup Problem*, PRL101,230405(2008), DOI10.1103/PhysRevLett.101.230405 is corroborating primary:
https://atom.curtin.edu.au/igor/PhysRevLett_101_230405.pdf
109547bytes; SHA25681035ed94f82a0fbf65154fb1868ad0fd13175f9baebbbe9e2aa2b75dd1a1011.
Its page2 gives arbitrary masses/Jacobi construction. The longer 2009 article is the selected equation authority.
Neither retrieved published PDF has a redistribution license established here; keep full bytes/pages private.

## B. Analytic direct Coulomb-Born alternative

Y. Attaourti, S. Taj, B. Manaut, published title *Semirelativistic model for ionization of atomic hydrogen by electron impact*, Phys.Rev.A71,062705,17June2005, DOI https://doi.org/10.1103/PhysRevA.71.062705.
Publisher metadata: https://journals.aps.org/pra/abstract/10.1103/PhysRevA.71.062705
Actual equation authority acquired: author preprint *Exact semi-relativistic model ...*, arXiv:physics/0411013v2 [physics.atom-ph],2November2004:
https://arxiv.org/pdf/physics/0411013
326595bytes; SHA256b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1.
Published PDF access returned403; no equation equivalence to published version asserted.

### Source definition and limited physical contract

Preprint p2 Eq1 explicitly omits exchange. Eq2 uses \(V_d=1/r_{12}-1/r_1\). Incoming/scattered projectile plane waves; bound Darwin H1s; ejected electron Sommerfeld–Maue Coulomb continuum. Atomic units hbar=me=e=1. Fixed proton coordinates/no recoil kinetic term. Ejected B and scattered f are distinct model roles; no unordered identical-electron event measure is established. Swapping those different distortion roles is not automatically a source-derived exchange amplitude.

Eq8 gives outgoing ket continuum Coulomb factor
\(e^{\pi\eta_B/2}\Gamma(1+i\eta_B)e^{i\mathbf p_B\cdot\mathbf r}
{}_1F_1(-i\eta_B,1,-i[p_Br+\mathbf p_B\cdot\mathbf r])\),
plus the stated semi-relativistic correction. Eq9 \(\eta_B=E_B/(c^2p_B)\), so NR limit is1/p_B. The bra in Eq13/15 has conjugate Gamma(1−iη) and hypergeometric parameter+iη.
Eq13 energy delta is \(E_f+E_B-E_i-\epsilon_b=0\), with no finite-mass term.
Eq15 uses \(H_1(\Delta-p_B)-H_1(-p_B)\), \(\Delta=p_i-p_f\).
Eq16 defines H1 with the bound wavefunction, no extra1/r.

### Source Eq19 (p4), checked visually

\[
I(\lambda;\mathbf q,\mathbf p)=
\int d^3r\,e^{i\mathbf q\cdot\mathbf r}\frac{e^{-\lambda r}}r
{}_1F_1(i\eta,1,i[pr+\mathbf p\cdot\mathbf r])
=\frac{4\pi}{q^2+\lambda^2}
\exp\left[i\eta\log\frac{q^2+\lambda^2}
 {q^2+\lambda^2+2\mathbf q\cdot\mathbf p-2i\lambda p}\right].
\]
A hydrogen1s overlap without1/r is obtained by \(-\partial_\lambda I/\sqrt\pi\) atlambda1 in the NR limit. That derivative, branch policy, closed rational reduction, orthogonality atq=−p, and normalization are **derivation obligations**, not formulae quoted as source Eq18.

**Source discrepancy:** Eq18 literally includes \(e^{-r}/r\), while Eq16 combined with Eq5/6 gives the upper-component bound factor \(e^{-r}/\sqrt\pi\). Confirmed in private/attaourti_p4.png; it is not OCR-only. Do not silently repair or call the journal corrected.

Eq26 averages both incident and target spins (1/2 each) and sums outgoing spins. Eq27 gives semi-relativistic TDCS in \(dE_Bd\Omega_Bd\Omega_f\), with source spinor-dependent amplitude conventions. A standalone correctly normalized NR scalar T/f should be independently derived from those wave normalizations; don't copy the semi-relativistic prefactor onto a newly normalized scalar amplitude.
Source comparison includes250eV incident/5eV ejected/3degree scattered asymmetric geometry. It states higher-order Eikonal-Born calculations are more accurate there. Figures are not new numerical grids; no digitization performed. No global error band or full-domain adequacy established.

## Fresh discovery/access coverage and provider accounting

Fresh SciSpace semantic search and fresh Exa search/fetch were actually executed this turn. Literal results are preserved privately in RAW_PROVIDER_RESULTS.json; metadata followup in METADATA_SEARCH.json. All billed/API costs remain UNKNOWN_NOT_ZERO, not zero.
SciSpace proposed Kadyrov2004 PRA70,062703 among leads; Murdoch fulltext URL timed out throughExa and returned503 throughpublicread. This is access gap, not source absence.
Exa fulltext fetch of MPG3c.paper.pdf and CORE229141039 timed out. A single separate read-only MPG download returned403. No bypass, repeat search loop or solver execution followed.
The two Curtin author-hosted PDFs and arXiv preprint were actually downloaded/extracted. DOWNLOAD_RECEIPT.json, PRIMARY_HASHES.json, PUBLISHED_VERSION_ACCESS.json retain receipts.
Attachment archive name inventories only:18-literatures.zip has7 cosmology/kinetic/fluid books;19-papers.zip has8 generically named papers. No relevant e-H namedfile; generic file contents were not inspected, and no absence claim extends to those contents.
Earlier CCC/Hex scan failures, Buicaerratum access gap, omitted Weigoldcells and old budget unknowns are preserved; no replay/upgrade.
This finite targeted search did not acquire a new full-support numerical spin/exchange/recoil-consistent electron-H event provider. That is a bounded intake result, not a universal no-go or claim no such source exists.

## Handoff

Root may construct the new finite-mass shell/Jacobian mathematics using source A, or a direct Coulomb-Born analytic kernel using source B with discrepancy handling. Neither choice admits a physical full HEANG provider by itself. No independent verification/physical claim is asserted by this source intake.

