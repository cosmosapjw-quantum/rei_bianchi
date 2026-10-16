---
title: "R9: Correlated Microphysics for the Reionization Network"
subtitle: "Actual NCP execution, constructive numerical repairs, and the remaining physical closure"
author: "Reionization research project"
date: "15 October 2026"
geometry: "margin=23mm"
fontsize: "10pt"
colorlinks: true
toc: true
---

# Scope and status

We continue the eight-task programme by computing new atomic and molecular quantities on the actual 64-core NCP host. The purpose of this iteration is to replace missing microscopic inputs with explicit calculations where the present Hamiltonians suffice, and to identify the additional operators and boundary conditions required elsewhere. We do not identify completion of a finite calculation with completion of the cosmological model.

The execution host is \texttt{s1a0e5abed09}, with 64 logical CPUs and approximately 125 GiB of physical memory. At the largest declared allocation, four workers use 12 threads and 24 GiB of address-space allowance each. The aggregate allocation is bounded by 48 threads and 96 GiB, leaving capacity outside this campaign. The actual numerical environment is Python 3.12.3, PySCF 2.14.0, NumPy 2.5.4, and SciPy 1.18.1. These versions were measured on NCP; they are not inferred from local installations.

The latest repository intake includes rei_bianchi PR150 at commit \nolinkurl{54dd5352672127e77970eb06f3dda027f2aee275}, BASS_HE PR64 at \nolinkurl{b0af50b052862320896085fac70250f51c077944}, WU088_HH PR89 at \nolinkurl{6db2b278aeed8c938098a92fb874e5b996d68e2e}, and bass_cr PR71 at \nolinkurl{ff23e118a72d268bb44f24a35a0eb053a80bb2c8}. The earlier R8 reproducibility archive was restored and its SHA256 verified before reuse. The present work is additive and is published in PR151.

The accompanying numerical appendix contains the final execution index and measured convergence series. Raw CI vectors, orbital transformations, density matrices, residuals, inputs, source identities, and logs are retained in the backup archives. The report should be read together with those records.

# What the latest repositories supply

The current rei_bianchi branch already supplies a conditional deuterium atomic provider, the Savin charge-exchange fits, and a conservative covariant-energy transport implementation. Its native isotope registry has 13 states. It is not yet a complete 17-state cosmological network. We retain the distinction between an available standalone provider and its activation in the common network, equation of state, radiation field, and cosmological evolution.

The BASS_HE saved P01 calculations and one-electron two-centre constructions provide useful numerical experience, but they do not supply a correlated three-electron Li wavefunction. The current WU088_HH result supplies a finite-collar boundary construction; a physical outgoing scattering trace and the resulting cross sections remain separate. The bass_cr energy-degradation cascade is likewise distinct from a bound-level atomic cascade. We therefore reuse established inputs and verified numerical ideas without relabelling these earlier objects as missing many-electron data.

The R8 native C neutron-proton kernel and the physical hydrogenic transition and line-yield tables are reused directly. The new atomic calculations use PySCF integral and full-CI routines. No historical unpublished Li coefficients are claimed to have been recovered. We have produced independent, reproducible wavefunctions for explicitly specified finite Hamiltonians.

# Atomic bound states and the choice of approximation

We use atomic units and the clamped, point-nucleus, nonrelativistic Coulomb Hamiltonian
\[
H=\sum_i\left[-\frac12\nabla_i^2-\sum_A\frac{Z_A}{|\mathbf r_i-\mathbf R_A|}\right]
+\sum_{i<j}\frac{1}{r_{ij}}.
\]
All electrons are correlated in the retained Gaussian orbital space. There is no effective core potential, frozen core, density fitting, or isotope-dependent modification of this Hamiltonian. Nuclear repulsion is added for the molecular Born-Oppenheimer energy.

For a chosen orbital space, full CI solves
\[
H_{\rm FCI}C=EC,\qquad C^\dagger C=1.
\]
We check the residual of the original Hamiltonian, even when an auxiliary spin penalty is used to select the desired state. The state is accepted only after normalization, orbital-metric, one-particle trace, spin, convergence, and residual checks. The principal residual threshold is \(10^{-7}\,E_h\); the two-electron runs also record the tighter \(10^{-9}\,E_h\) target.

Li, Li\(^{+}\), and He are computed in cc-pVDZ, cc-pVTZ, and cc-pVQZ spaces. Diffuse Li/Li\(^{+}\) calculations and core-valence basis extensions are added to expose separate basis deficiencies. Correlating every electron in a valence-optimized basis does not make that basis complete for core correlation.

The ionization energy is formed only from matched spaces,
\[
I_{\rm Li}^{(B)}=E_{\rm Li^+}^{(B)}-E_{\rm Li}^{(B)}.
\]
The cc-pVXZ series gives \(0.1964137691\), \(0.1967155315\), and \(0.1973396187\,E_h\) at D, T, and Q. The T-to-Q change exceeds the selected \(10^{-4}\,E_h\) target. This is a measured basis sensitivity, not a rigorous complete-basis error estimate. The core-valence extension is consequently a physical convergence calculation, rather than another replay of the same numerical test.

Finite nuclear mass, mass polarization, recoil, relativistic and QED corrections, finite nuclear size, and hyperfine structure remain absent. An isotope label alone does not restore these terms.

# Correlated daughter projections

## A common Hilbert space

For a sudden change in nuclear charge, the electronic amplitudes are
\[
A_f=\langle\Psi_f|\Psi_i\rangle,\qquad P_f=|A_f|^2.
\]
Both states must be represented in the same one-particle space and determinant convention if their CI coefficients are dotted directly. We diagonalize the AO overlap once,
\[
S=UsU^\dagger,\qquad X=U_{\rm ret}s_{\rm ret}^{-1/2},
\]
and transform the parent and daughter Hamiltonians with the same \(X\). The default retained-space criterion is \(s_j>10^{-10}s_{\max}\); selected repeats use \(10^{-9}s_{\max}\).

For the daughter ground state,
\[
q=C_i-A_0C_{f0},\qquad
P_0+\|q\|^2=1,\qquad C_{f0}^\dagger q=0.
\]
The complement contains both bound excitation and ionization. It is not an ionization probability. We also compute the daughter-Hamiltonian mean, second moment, and variance by direct Hamiltonian action.

The original common Li-only contracted basis gave He-to-Li\(^{+}\) ground probabilities of approximately 0.467282 at aug-DZ and 0.716703 at aug-TZ. Independent calculations reproduced the low-basis energies; the discrepancy was not a coefficient-ordering bug. The Li contractions poorly represented the He parent. We retained this failed convergence series and replaced the imbalanced common space with a union of the He and Li AO shells. The union values are 0.7086742709 and 0.7089407396 at aug-DZ and aug-TZ. The retained Q-space calculation gives 0.7086682802. Its T-to-Q change still exceeds the selected probability target; the numerical appendix records the overlap truncation.

For the three-electron Li-to-Be\(^{+}\) quench, the common Li+Be union gives 0.5759197782 at cc-DZ and 0.5756492553 at aug-DZ. This channel is relevant to the electronic sudden approximation for beta-minus decay of Li isotopes, subject to the stated omissions. It is not a full recoil- and phase-space-weighted decay distribution.

## Constructive removal of the 64-orbital restriction

The first large two-electron calculation encountered a PySCF creation/destruction-index restriction. This is an implementation limitation of the selected spin route, not a physical obstruction.

For a singlet, write the two-electron coefficient matrix as \(C=C^T\). In a real orthonormal orbital basis, the exact finite-space action is
\[
(HC)_{pq}=(hC+Ch^T)_{pq}
+\sum_{rs}(pr|qs)C_{rs}.
\]
We pack the symmetric matrix in orthonormal coordinates, using a factor \(\sqrt{2}\) for off-diagonal elements, and solve the resulting matrix-free symmetric eigenproblem. This retains the full singlet FCI space. The density matrix and spin diagnostic are
\[
\gamma=CC^\dagger+C^TC^*,\qquad
\langle S^2\rangle=1-\operatorname{Re}\langle C,C^T\rangle.
\]
Random-vector Hamiltonian actions, energies, and projection probabilities were compared with the native small-basis FCI implementation before using this route above 63 orbitals.

For three electrons, the ordinary Hamiltonian and density-matrix kernels support occupation lists above the bitstring limit. The unsupported spin-penalty route is removed, with Davidson iteration in the fixed \((N_\alpha,N_\beta)=(2,1)\) sector and no pspace shortcut. The resulting spin is checked independently through spin-resolved density matrices. Only a state satisfying \(\langle S^2\rangle=3/4\) within the frozen tolerance is admitted as the doublet. No orbitals are discarded to make the code run.

## Electron capture remains a different calculation

The dominant BBN mass-7 inventory may be stored as \(^{7}\mathrm{Be}\), whose later electron capture is not described by the beta-minus overlap above. In a spin-independent point-contact approximation, a conditional electronic amplitude instead has the form
\[
A_{f\sigma}^{\rm EC}
=\langle \Psi_{f,N-1}|\hat\psi_\sigma(0)|\Psi_{i,N}\rangle.
\]
The annihilation operator changes electron number. Its inclusive strength is related to the contact density, whereas an absolute capture rate also needs nuclear matrix elements, neutrino phase space, ionic-state populations, and the appropriate bound or continuum capture model. Hyperfine and spin correlations may modify the selected approximation.

One can implement this next calculation by evaluating orbital values at the nucleus, applying signed annihilation maps to the CI tensor, and projecting the resulting \((N-1)\)-electron vectors onto daughter eigenstates in a common basis. Density-matrix contact sums provide an independent closure test. The present beta-minus probabilities must not be substituted for these electron-capture amplitudes.

# Finite-basis response and physical continuum data

The Li response calculation begins from the projected dipole operator,
\[
D_a=P\sum_i r_{i,a}P,\qquad
b_a=(D_a-\langle D_a\rangle)C_0,\qquad K=H-E_0.
\]
We calculate
\[
m_k=\sum_a\langle b_a|K^k|b_a\rangle,\quad k=0,1,2,
\]
directly, and compare them with Lanczos moments. The chains use explicit reorthogonalization and lengths 32, 64, and 128. For positive Ritz weights \(w_j\), the reported broadened response is
\[
S_\eta(\omega)=\sum_j
\frac{w_j\eta}{\pi[(\omega-\omega_j)^2+\eta^2]},
\]
with \(\eta=0.02,0.01,0.005\,E_h\). Finite-window Lorentzian weight is treated analytically; the plotted interval is not assumed to contain the entire norm.

The diagnostic \((2/3)m_1\) approaches the nonrelativistic Thomas-Reiche-Kuhn electron count in a complete space. The aug-DZ and aug-TZ results are about 1.11126 and 1.65647, respectively, both substantially below three. The internal moment and Gram-matrix checks can pass while the physical space remains incomplete. Likewise, convergence of a broadened Krylov response does not establish the outgoing-wave normalization of the continuum.

A physical Li photoionization or recombination provider still requires energy-normalized channels, exchange, correct thresholds and Coulomb boundary conditions, with a controlled R-matrix, close-coupling, exterior-complex-scaled, or equivalent construction. The finite Gaussian Ritz states are retained as pseudostates. No exclusive cross section is inferred from them in this iteration.

# Molecular curves and the route to low-temperature rates

We calculate neutral LiH \(X\,{}^1\Sigma^+\) with four electrons and neutral LiHe \(X\,{}^2\Sigma^+\) with five electrons. The nuclei lie at \(\pm R/2\), with \(R\) in Bohr. All selected ground-state curves include electronic and nuclear contributions to the permanent dipole.

At each geometry, the counterpoise potential is
\[
V_{\rm CP}(R)=E_{AB}^{AB}(R)-E_A^{AB}(R)-E_B^{AB}(R),
\]
where a superscript denotes the orbital basis and the absent partner is a zero-charge ghost. The uncorrected potential,
\[
V_{\rm raw}=E_{AB}^{AB}-E_A^A-E_B^B,
\]
is retained separately. The fragment electron numbers and spins are explicit.

The mandatory coarse grid comprises 12 LiH geometries in each of cc-DZ and aug-DZ, and 10 LiHe geometries in cc-DZ. Selected LiH TZ and LiHe aug-DZ points then examine basis errors near the chemically relevant and weak-binding regions.

For LiH at \(R=3a_0\), the counterpoise potential changes from \(-0.0825685768\,E_h\) in cc-DZ to \(-0.0861078210\,E_h\) in aug-DZ and \(-0.0899521868\,E_h\) in cc-TZ. These changes exceed the selected tolerance. For LiHe at \(R=11.5a_0\), cc-DZ gives \(+5.5109086\times10^{-6}\,E_h\), whereas aug-DZ gives \(-3.7928598\times10^{-6}\,E_h\). A shallow physical well cannot be established by inspecting the uncorrected attraction alone.

Two distant LiH geometries initially failed their SCF initializer. Full CI depends on the complete orthonormal orbital span, not on convergence of an auxiliary SCF reference. We therefore retained complete orthonormal trial orbitals, or constructed a canonical overlap basis within each symmetry block, and imposed the same final FCI gates. Both distant geometries were recovered. Their earlier failures remain in the archive.

A reaction rate needs more than a ground-state curve. For channel potentials and couplings \(V_{\alpha\beta}(R)\), one solves the radial coupled-channel equation with asymptotic channel thresholds, reduced nuclear masses, and outgoing or standing-wave boundary conditions. After obtaining a cross section,
\[
k(T)=\sqrt{\frac{8}{\pi\mu}}\,(k_BT)^{-3/2}
\int_0^\infty E\,\sigma(E)e^{-E/k_BT}\,dE.
\]
Radiative association additionally needs transition dipoles and the relevant bound and continuum nuclear wavefunctions. Charge transfer needs the coupled ionic and covalent channels. Near-threshold resonances and scattering lengths are especially sensitive to the long-range potential. The new BO curves are actual inputs to this programme, not completed low-temperature rates.

# Nuclear calibration sensitivity

We reuse the historical Chen-Savage neutron-proton capture kernel implemented in native C. The new calculation varies the selected thermal cross-section anchor by \(\pm1\%\): 330.858, 334.2, and 337.542 mb. The corresponding fitted parameter values are approximately \(-4.67553285\), \(-4.49713935\), and \(-4.31874585\,\mathrm{fm}^2\), with
\[
\frac{dL}{d\sigma_{\rm anchor}}
=0.0533792642\,\mathrm{fm}^2/\mathrm{mb}.
\]
This derivative follows from the affine calibration model. It is not a new parameter covariance.

The thermal integrations use 10 temperatures from \(10^{-3}\) to \(10^8\) K and four quadrature resolutions. The largest measured 64-to-256 difference is \(1.33\times10^{-15}\) in relative terms. This agreement concerns numerical integration of the inherited model and its declared energy domain. It says nothing about neglected effective-field-theory orders, current experimental normalization uncertainties, or correlations among nuclear parameters.

The next precision calculation must specify the joint data likelihood and its covariance, propagate the model truncation uncertainty, and distinguish calibration data from validation data. Repeating a thermal integral at higher resolution cannot replace those inputs.

# E1 cascade spectra and residual excitation

The hydrogenic line-yield tables contain physical transition energies and branching probabilities. We form a declared statistical shell mixture
\[
p_{nl}=\frac{2l+1}{n^2},
\]
and propagate it through the E1 network. This is an explicit injection model for a diagnostic calculation; it is not a computed recombination population.

The photon number and emitted energy are obtained from the actual line yields. For the H1 statistical \(n=12\) mixture, the E1 photon yield is 7.52035012269 and the emitted E1 energy is 13.41984882082 eV per initial atom. The residual \(2s\) probability is 0.00823690917714, carrying a separately retained 0.0840058928695 eV of excitation.

The E1 model terminates in both \(1s\) and \(2s\). A \(2s\) two-photon continuum must be added before calling this a complete radiative cascade. State-resolved recombination injection, collisional redistribution, ionic abundances, and escape or reabsorption then determine the cosmological photon source. An arbitrary carrier energy must not convert a bolometric energy packet into a claimed physical photon number.

# BBN inventory and the 17-state interface

Let \(Y_A=n_A/n_b\) be the nuclear abundance per baryon and \(x_{Aq}\) a charge fraction. The ionic map is
\[
y_{Aq}=Y_Ax_{Aq},\qquad
\sum_qx_{Aq}=1,\qquad
x_e=\sum_{Aq}q\,y_{Aq}.
\]
The 17-state inventory comprises neutron, H/D/T neutral and singly ionized states, three charge states for each of He3 and He4, and four charge states for Li7. Nuclear abundance and ionic charge are independent inputs.

We retain omitted nuclei in an explicit residual inventory, preserving their baryon and nuclear-charge contributions. The R5 donor has full baryon sum 1.0000000000016263; its mapped 17-state contribution is 0.9999999973520841, leaving \(2.6495419403\times10^{-9}\) outside the selected inventory. In particular, the donor's Be7 contribution is not silently converted into Li7 or removed by renormalization.

The present charge map is conditional. It does not evolve the donor through recombination and radioactive conversion to the selected redshift. The current HYREC donor has its own helium convention; a differing He/H normalization cannot be silently imported into a new isotope split. The implementation preserves these distinctions instead of manufacturing missing abundances.

To activate the full network, the common solver must own all charge-state populations, free electrons, thermal particle counts, ionization binding energy, and nuclear conversion terms. The existing standalone D provider is a useful component of that integration, not proof that the integration has been executed.

# Source spectra and transport coupling

The existing selected stellar source is a 50000 K blackbody shape normalized on 13.6--100 eV. LiI also responds below the H ionization edge. We introduce a separate, explicitly conditional spectral extension, preserving the original normalization.

Write the photon spectrum per unit reference photon flux as
\[
\phi(E)=\frac{E^2/[\exp(E/k_BT_\star)-1]}
{\int_{13.6}^{100}E'^2/[\exp(E'/k_BT_\star)-1]\,dE'}.
\]
For the source-backed Verner LiI fit, only its declared 5.392--64.39 eV domain is used:
\[
\Gamma_{\rm LiI}=F_{\rm ref}\int\phi(E)\sigma_{\rm LiI}(E)\,dE,
\]
\[
\mathcal H_{\rm LiI}=F_{\rm ref}\int
\phi(E)\sigma_{\rm LiI}(E)(E-\chi_{\rm LiI})\,dE.
\]
The energy unit is converted to joules in the heating integral. For \(F_{\rm ref}=1\) photon \(\mathrm{m}^{-2}\mathrm{s}^{-1}\), the sub-Lyman and fully covered rates are \(1.9547821482\times10^{-22}\) and \(2.5453130729\times10^{-22}\,\mathrm{s}^{-1}\). The sub-Lyman band supplies about 76.8% of this covered photoionization response. The source extension is therefore consequential for Li, but it remains a declared source model.

The actual Verner table bytes were acquired and matched to the frozen repository SHA256. The LiI fit was not extrapolated above its upper limit. Inner-shell channels, branching, collisionally induced ionization, dielectronic recombination, charge exchange, and kinetic recombination-cooling moments remain separate providers.

For the existing D point equations, define photoionization, collisional ionization, recombination, and net charge exchange as \(P,C,R,X\). With a common threshold convention,
\[
\dot n_{\mathrm D^+}=P+C-R+X,\qquad
\dot n_{\mathrm H^+}=-X,\qquad
\dot n_e=P+C-R.
\]
The thermal, chemical, and escaping-radiation terms satisfy
\[
Q_{\rm th}+Q_{\rm chem}+Q_{\rm esc}
=\chi_{\rm D}P+\mathcal H_{\rm D}.
\]
We independently evaluated the algebra with Wolfram and obtained the expected energy identity and zero charge-exchange electron residual. This is a local bookkeeping check, not a new FLRW or Bianchi trajectory.

The current transport-owner campaign is preserved. This microphysics campaign does not relaunch an owner-stopped run or claim that source moments solve the transport equation. Coupling the new providers, refining energy and angular grids, comparing actual temperature and charge histories, and establishing the final reionization trajectory remain necessary.

# Research-loop record and acceptance

The theory loop proceeded through the following concrete stages: recover and pin inputs; classify the eight missing physical objects; select Hamiltonians and charge conventions; derive projections and energy maps; identify basis and boundary assumptions; calculate new quantities; diagnose basis imbalance and backend restrictions; construct equivalent finite-space repairs; review results independently; and preserve the next executable dependencies.

The coding loop froze inputs before implementation, built versioned workers, ran small numerical comparisons, installed the NCP environment, measured thread scaling, executed the actual grids, retained first failures, applied focused repairs, audited full receipts and raw arrays, and published reproducible work units. The 4/8/12-thread Hamiltonian-action medians were approximately 1.3753/0.7318/0.5228 s, with action differences below \(9\times10^{-16}\). We selected 12 threads per production worker from this measurement.

Implementation correctness, convergence in a finite model, basis completeness, and physical closure are reported separately. None is replaced by a single global success flag. The first unit's 56 receipts contained 53 successful solves and three preserved failures; later units add their repaired and extended calculations. The independent first-unit audit verified all 53 saved NPZ hashes and the original-H, norm, trace, spin, projection, and counterpoise identities. The full execution index records subsequent results.

The source revisions are immutable. Earlier incorrect or inadequate numerical attempts remain inspectable. Files from unrelated repository work and the existing desktop checkout branch are preserved. Backup hashes are verified against both remote destinations.

# Remaining programme

The bounded work performed here advances all eight tasks, but the physical completion conditions differ:

| Task | New result in this loop | Remaining physical requirement |
|:--|:--|:--|
| Li bound states | All-electron FCI energies, CI/RDMs, matched ionization series and core-valence extension | Accepted basis error, finite-mass/relativistic corrections where needed |
| Li continuum | Projected moments and broadened Lanczos response | Energy-normalized outgoing Coulomb channels and exclusive cross sections |
| Low-temperature molecular rates | Counterpoise LiH/LiHe curves and dipoles | Channel couplings, long-range convergence and nuclear scattering/radiative calculation |
| Correlated daughters | Common-basis 2e/3e projections, complements and energy moments | Excited/continuum resolution, recoil/phase-space weights; separate electron-capture operator |
| Nuclear precision | Native-kernel calibration sensitivity and thermal convergence | Current data likelihood, correlated parameter/truncation uncertainties |
| Atomic charge cascades | Physical E1 mixture line spectra and residual excitation ledger | Recombination injection, two-photon channels, charge-changing and collisional processes |
| BBN to 17 states | Conservative inventory and conditional ionic map | Be7 conversion, charge-history evolution, common electron/EOS integration |
| Full transport | Conditional Li source-band response and provider interfaces | Coupled isotope/radiation evolution and cosmological refinement |

The next calculation should be selected from these physical dependencies, using the new wavefunctions and curves as inputs. Numerical failure of a particular initialization or backend does not constitute a physical no-go result; the successful repairs in this loop demonstrate why the distinction matters.

# Primary references and reproducibility entry points

1. PySCF full-CI documentation and source: \url{https://pyscf.org/user/ci.html}, \url{https://pyscf.org/_modules/pyscf/fci/direct_spin1.html}, and \url{https://pyscf.org/_modules/pyscf/fci/cistring.html}.
2. Correlated electronic final-state calculations: \url{https://arxiv.org/abs/1001.0120} and \url{https://arxiv.org/abs/1305.5696}. These motivate methods; no graph values were digitized into the present results.
3. Verner photoionization table: \url{https://www.pa.uky.edu/~verner/dima/photo/photo.dat}; SHA256 \nolinkurl{a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389}.
4. Lithium ionization in the primordial radiation field: \url{https://arxiv.org/abs/astro-ph/0507106}.
5. LiHe basis studies: \url{https://doi.org/10.1007/s004600050118} and \url{https://jupiter.chem.uoa.gr/pchem/pubs/pdf/JPCA_104(2000)408.pdf}.
6. Current integration branch: \url{https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150}.
7. This research package: \url{https://github.com/cosmosapjw-quantum/rei_bianchi/pull/151}.

The repository package contains the exact contracts, versioned drivers, tests, source intake, review records, compact results, archive identifiers, and remote hash checks. The raw archives additionally contain the computed CI/RDM arrays and complete execution logs.

# Numerical appendix: actual NCP snapshot

These tables are generated from actual saved receipts. Counts refer to attempts, including diagnostic repeats and preserved failures, rather than distinct physical systems. A successful finite-model calculation does not establish complete-basis convergence.

| Run | Receipts | Accepted solves | Other attempts |
|:--|--:|--:|--:|
| conditioning repair v7 | 2 | 2 | 0 |
| extension v4 | 19 | 18 | 1 |
| final basis v7 | 3 | 2 | 1 |
| molecular v1 | 34 | 32 | 2 |
| pilot v1 | 5 | 5 | 0 |
| production v1 | 17 | 16 | 1 |
| qz conditioning v7 | 1 | 0 | 1 |
| response v4 | 2 | 2 | 0 |

## Atomic energies

| Case | Energy (Hartree) | Residual (Hartree) |
|:--|--:|--:|
| atomic Li core DZ | -7.466025164462 | 1.39e-08 |
| atomic Li core TZ | -7.474251419701 | 1.71e-08 |
| atomic Li plus core DZ | -7.269191736123 | 1.58e-11 |
| atomic Li plus core TZ | -7.276559599089 | 5.78e-11 |
| atomic Li core QZ final | -7.476372869917 | 8.2e-09 |
| atomic Li plus core QZ final | -7.278331078483 | 3.62e-12 |
| pilot atomic Li aug-cc-pvtz | -7.446157917192 | 1.6e-08 |
| atom He cc-pvdz | -2.887594831091 | 8.76e-10 |
| atom He cc-pvqz | -2.902410877946 | 3.34e-08 |
| atom He cc-pvtz | -2.900232169009 | 3.85e-09 |
| atom Li aug-cc-pvdz | -7.432659338287 | 1.79e-08 |
| atom Li aug-cc-pvtz | -7.446157917192 | 1.6e-08 |
| atom Li cc-pvdz | -7.432637514965 | 4.5e-09 |
| atom Li cc-pvqz | -7.449832450866 | 2.13e-08 |
| atom Li cc-pvtz | -7.446068921286 | 3.17e-08 |
| atom Liplus aug-cc-pvdz | -7.236230821920 | 5.47e-09 |
| atom Liplus aug-cc-pvtz | -7.249419294409 | 4.55e-08 |
| atom Liplus cc-pvdz | -7.236223745851 | 2.56e-09 |
| atom Liplus cc-pvqz | -7.252492832143 | 3.47e-09 |
| atom Liplus cc-pvtz | -7.249353389769 | 3.6e-08 |

The matched core-valence T and Q ionization energies are 0.197691820613 and 0.198041791435 Hartree. The change, 0.000349970822 Hartree, exceeds the frozen $10^{-4}$ Hartree criterion. The bound-state basis target remains unmet.

## Shared-space daughter projections

| Case | Ground probability | AO / retained rank |
|:--|--:|--:|
| quench He Li union aug QZ cond1e 6 | 0.708668280218 | 126 / 124 |
| quench He Li union aug QZ cond1e 7 | 0.708668280218 | 126 / 124 |
| quench He Li union aug DZ | 0.708674270938 | 32 / 32 |
| quench He Li union aug DZ cutoff1e 9 | 0.708674270938 | 32 / 32 |
| quench He Li union aug TZ | 0.708940739563 | 69 / 69 |
| quench Li Be union DZ | 0.575919778231 | 28 / 28 |
| quench Li Be union DZ cutoff1e 9 | 0.575919778231 | 28 / 28 |
| quench Li Be union aug DZ | 0.575649255288 | 46 / 46 |

The untruncated He+Li aug-Q union had 126 retained directions and failed the orbital-metric and original-H residual gates. The bounded repair used relative overlap cutoffs $10^{-7}$ and $10^{-6}$ and eigensolver tolerance $10^{-13}$. Both cutoffs retained the same 124-dimensional space from 126 AOs. Both gave $P_0=0.7086682802176386$, parent energy $-2.90273212428737\,E_h$, and daughter energy $-7.27709543375322\,E_h$. Their largest metric defect was $6.58\times10^{-11}$ and largest residual $8.91\times10^{-12}\,E_h$.

Identical probabilities show reproducibility in the same retained space. They do not establish convergence to the discarded two directions. The T-to-Q probability change is $2.72459345\times10^{-4}$, above the selected $10^{-4}$ criterion. The failed 126-direction attempts remain archived separately.

## Projected response

| Basis | TRK diagnostic | Largest 64-to-128 difference | Wall time (s) |
|:--|--:|--:|--:|
| aug-cc-pvdz | 1.111259136696 | 5.94e-15 | 9.553 |
| aug-cc-pvtz | 1.656474429247 | 5.82e-15 | 485.179 |

The internal Krylov criterion is satisfied at the declared broadenings. The TRK deficit and missing outgoing-wave provider prevent physical continuum closure.

## Rust execution on NCP

The NCP installation reports \texttt{rustc 1.99.0 (b940084d7 2026-09-28)} and \texttt{cargo 1.99.0 (5f94df478 2026-08-27)}. We staged the native microphysics crate and its compile-time contract inputs from the same pinned PR150 commit. The locked, offline library check succeeded. The explicit \texttt{deuterium\_atomic} integration-test target ran eight tests: all eight passed.

An earlier library-only test filter selected zero tests and is retained in the logs but is not counted. Initial incomplete staging omitted compile-time contract files; staging them from the same commit resolved the build failure. No scientific implementation was changed for the build.

This establishes the native Rust toolchain and verifies the existing standalone D provider on the target host. It does not activate the 17-state solver. A next native implementation can consume the versioned microscopic tables through the existing isotope, charge and energy conventions, while expensive wavefunction construction remains a separately validated producer.

## Acceptance and continuation

The independent reviews and machine-readable convergence records accompany this report. All eight programme completion flags remain open for the physical reasons stated in the main text. This iteration supplies new finite-model calculations, executable source code, raw states, and explicit next dependencies.


At this snapshot, the large three-electron Li+Be aug-TZ attempt is still running under frozen wall-time and memory limits. Completed DZ/aug-DZ projections and the independently completed 84-orbital Li core-Q solve remain available. No result for the running attempt is inferred.
