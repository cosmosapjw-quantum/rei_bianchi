---
title: "Reionization microphysics: lightweight reconstruction and executable handoff"
subtitle: "Research update R8 — theory and coding loops"
date: "14 October 2026"
lang: en
geometry: "margin=22mm"
fontsize: 10pt
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
---

# Overview

Research update R8, 14 October 2026 (UTC). This report accompanies native C/C++ kernels, numerical tables, primary-source records, and a local Codex implementation/execution package. It extends the previous R7 synthesis with new theoretical reconstructions and scoped computations. Throughout, the spacetime signature is (-,+,+,+), and c, hbar and k_B are retained. Atomic-unit substitutions inside dimensionless integrals are accompanied by their physical conversion.

## Result and scope

The useful simplification is to compute the microscopic quantities required by an observable, while retaining any correlation or memory that its nonlinear response needs. An isolated hydrogenic E1 cascade is a triangular probability graph; a zero-recoil one-electron daughter is a Coulomb spectral transform; a thermal inverse nuclear reaction is a one-dimensional invariant integral; a prescribed source spectrum can be reduced to photon, energy and cross-section-weighted moments. These reductions yield actual new rates and distributions on the current host. They do not require a parallel many-body calculation.

The scope is the recoverable, physically specified provider inventory. Multi-electron Li continuum states, correlated daughter amplitudes, molecule-specific potential curves, and full coupled Bianchi histories remain distinct calculations. The package identifies the actual code and input still needed for each. A missing physical Hamiltonian/deck is not classified as a long runtime. No graph digitization supplies the new microscopic values.

| New executed component | Quantitative result | Physical scope |
|---|---|---|
| Hydrogenic E1 | 210 levels and 2470 transitions per case through n=20; eight mass/charge cases | Nonrelativistic Coulomb E1, with reduced mass and charged-ion COM dipole |
| Cascade observable reduction | Backward rewards agree with independent forward propagation for every included start | Optically thin spontaneous cascade, with 1s and 2s retained as terminals |
| One-electron daughter | Charge ratio 2 continuum probability 0.026272817 | Sudden zero-recoil Coulomb quench, before physical beta weighting |
| Conditional allowed beta | Four phase-space models: F=1/bare Sommerfeld and infinite/reduced isotope masses; ionization probability about 0.0259033/0.0259209 | Selected ground-channel Q=18600 eV; exchange, full recoil and physical Q determination remain open |
| Direct source folding | 36 Stobbe ionization/heating calculations, plus 21 Planck reference rates | Declared finite-band power law/screen or isotropic Planck field |
| Nuclear capture/inverse | Native threshold expansion, Maxwell capture, inverse Planck rate | Adopted 1999 EFT shape and explicit nonrelativistic/exact-kinematic conventions |
| Astrophysical UVB | 59-node primary Puchwein-v1 table with unit conversion | Named public rate benchmark, not new atomic data |
| Standard recombination IC | Actual stock HYREC-2 native execution and 8000 output rows | Author-default FLRW reference, not an anisotropic history |

The chapters below contain definitions, derivations, numerical construction and validation. They distinguish analytical truncation bounds, floating-point refinement, independent numerical checks, and physical-model uncertainty. Printed reproducibility digits are not observational or theoretical precision estimates.

## Cross-thread changes adopted

HE THEORY16 R10 preserves its source-bound current/clock/bin adapter and specifies receiver binding. HH PHYS29 now evaluates the one-centre Coulomb finite-window thermal rate: at 50000 K the unpolarized value is 2.205624838325349e-12 cm3/s; its finite quadrature and all-roundoff enclosure remains a separate obligation. CR's moving seeded shell supplies a new event-cluster construction and defect bounds. REI OBSERVER15 R7 supplies a finite Gauss32 source-node and observer time certificate. Their exact identities and distinct proof variants are retained in integration/CURRENT_SNAPSHOTS.json.

The new modules do not transplant numbers between these sources. The same electron current, clock, volume, cross-section convention and observer interval must be used at each receiver boundary. Existing CR/RCT/HH production switches are preserved. This report's scoped calculations are ready to consume; production admission and the full 17-state/network history require their named bindings.

## Execution and residual obligations

The C kernels run in milliseconds to a few seconds at the listed small model sizes. High-precision independent checks and source acquisition take longer than the kernels themselves. The package contains actual runtime records instead of projected speedups. Compiler and numerical-library dependencies are listed per module.

The inherited 65 gap list is maintained in GAP_CROSSWALK_R8.json. The new results advance individual sub-obligations; no whole multi-part historical gap is declared closed solely by a hydrogenic or finite-source benchmark. For the expensive lanes, local_codex/ contains the actual recovered WU/ECG code and nuclear observation inputs, algorithms for the remaining providers, a resource-aware runner, and a complete return contract. Execution of those physical campaigns has not occurred in this session.

For legibility, some long decimal entries in the report tables are displayed to eight significant digits. The original module documents and CSV/JSON files retain the full printed values and interval endpoints.

\clearpage

# R8 cross-thread intake and reusable reductions

Read scope: full scientific GitHub documents at the pins in CURRENT_SNAPSHOTS.json, plus the complete Library REI R7 report. Receipts establish delivery identity, not scientific validity. These records supersede the previous readiness table only in the specified rows.

| Family | Actual new result | What remains |
|---|---|---|
| HE THEORY16 R10 | R9 code/input/result preserved and executable resumption checked; current/clock and passive cross-section contract retained | Real receiver binding with one named source; R10 did not compute new microscopic data |
| HH PHYS29 | One-centre Coulomb finite-window thermal rate at 50000 K: singlet 3.0611019e-12, triplet 1.9204658e-12, unpolarized 2.2056248e-12 cm3/s | Finite quadrature and all-roundoff certificate, exchange, two-centre final state, E>2I0 tail, same-channel empirical calibration |
| CR moving cluster | H=(2,4,6)e-15/s seeded angular shell: first contact [11965.71544641560, 11966.01569403099] s; terminal T [101.20671610692, 101.20673069700] K | Seedless continuous angular front; full moving source history not newly solved |
| REI OBSERVER15 R7, latest GitHub publication | Exact-real finite GL32 epsilon=0 residual certificate; saved xe error <4.1257779e-13/H; direct cubic observer consumption | Spectral-continuum, finite-shear, physical-source/calibration and native-receiver extensions |

Two distinct R7 artifacts were actually read. The earlier Library report (SHA-bound archive 10b74244...e26a) uses a weighted gas norm and reports xe<=1.039654397553e-13/H. The subsequently observed GitHub publication at 8bf8e3c18d607334614cfea734f9b10961fbd4d4 uses the unweighted gas norm and archive 3524a7e6...0eaa. They have different code/proof bounds and sizes; no byte or semantic identity is asserted. The latest published source is the externally current snapshot. The following weighted formulas remain explicitly the earlier Library variant's derivation, not coefficients to mix into the published proof.

## Reductions supported by actual new calculations

1. **Remove an angular quadrature analytically.** HH PHYS29 writes the screened Yukawa multipole using I_(l+1/2)(alpha r_min) K_(l+1/2)(alpha r_max)/sqrt(r R), then applies (1-d/dalpha) at alpha=2. This exactly replaces one angle integral in the declared one-centre model. Use scaled Bessel functions and split r=R; it is not exchange or two-centre completion.
2. **Regularize the Coulomb endpoint before quadrature.** x=kappa^2, u_l=sqrt(kappa)F_l(-1/kappa,kappa r)/(kappa r) yields a finite x=0 Bessel limit. Positive partial-wave norms can be accumulated with electron-energy moments in the same pass. The published finite rate is now available: do not repeat PHYS29 merely because the old table called it pending. Analytic omission sum <9.819e-19 cm3/s excludes finite quadrature/roundoff; `global_rate_enclosure=null` remains correct.
3. **Integrate an exactly solvable photon block by characteristics.** On the REI finite baseline, F_m(u)=w_m exp[-sum_a b_am X_a(u)], X_a=int exp(lambda_a u) r_a(u)du. A cubic gas reconstruction needs exponential-polynomial integrals rather than another photon ODE. This requires separable cross sections and the stated absorption-only radiation block. Injection adds a Duhamel integral; scattering/frequency coupling generally breaks independent characteristics.
4. **Separate dissipative transport from nonlinear feedback.** REI's weighted gas norm with diag(1,2,1) has nonpositive weighted column sums; photon loss is also nonamplifying. Thus E'<=a P+d and P'<=b E, with a=.09616,b=.6468 only for that source. The positive 2x2 comparison propagates by cosh/sinh; use stable sinhc/cosh-minus-one evaluations near zero.
5. **Consume the reconstruction that was already certified.** Direct integration of the same cubic supplies P(r=1) in [0.0020224807481693721, 0.0020224807481712630] with no extra linear-interpolation remainder. The ~1.87e6 reduction is an interval-width ratio; it is not a measured CPU acceleration or physical precision gain.
6. **Exploit current-preserving resets only for the observable they preserve.** For U=c u, dx=c k ds, age rate A=q.k>0, D=-u.k, and J=c N u/V+j, u.j=0, C=int[c D N/(V A)-k.j/A] dtheta. Apply sigma_T once, then P=exp(-T_fore)(1-exp(-sigma_T C)). A vanishing direct optical saltation row does not erase post-reset chemistry/work or future response.
7. **Use a seeded shell as an aggregate measure, not a finite ray artifact.** CR proves J_seed=(eta-1)w_min a/(Bcap+a)>w_max-w_min, giving immediate full-shell eligibility. This is an exact sufficient reduction for the declared finite seed. Seedless/grazing cases need a moving angular front; the sufficient condition must not be imposed artificially.

## Integration decision

For the latest published REI variant use e_r=||r-rhat||1, e_F=||F-Fhat||1 with C=.01782339442137827122..., K=.60545256434663311962... in the same 2x2 comparison construction. Its probability at r=1 is [0.00202248074816642495, 0.00202248074817421008]. The shared Hermite centers agree to the printed digits, but that agreement does not identify the separate error proofs or runtime arrays.

Adopt these equations and model-bound numerical records. Do not transplant CR moving radii into HE's unchanged CR53 loader, multiply an old observer response by HH's new rate ratio, or replace missing physical foreground with zero. A separately versioned adapter must bind source state, volume, clocks, currents, constants, reset ownership and observer interval. Latest results are research snapshots, not evidence that native production switches changed.

\clearpage

# Hydrogenic E1 line and cascade provider: R8

Date: 2026-10-14. The native C calculation is **implementation-verified** and
**numerically checked** for the stated nonrelativistic Coulomb model through
`nmax=20`. Final tables are in `n20/`; root-level tables retain the initial
`nmax=12` checkpoint. No R7 bound-free calculation was rerun.

## Physical definition and retained assumptions

This provider treats an isolated, one-electron nucleus of charge `Ze` and mass
`M`, with orbital states `(n,l)` and statistically averaged magnetic substates.
Spin is a spectator. It computes spontaneous electric-dipole emission summed
over photon directions/polarizations and final magnetic substates. The initial
and final electronic wave functions belong to the same Coulomb Hamiltonian.
The outputs apply to H I, hydrogenic He II and hydrogenic Li III. He I, Li I and
Li II require correlated multi-electron wave functions and are outside this
Hamiltonian.

The approximation retains the exact nonrelativistic reduced mass and the
center-of-mass electric dipole of a charged two-body ion. It omits fine and
hyperfine structure, Lamb shifts, nuclear size/polarizability, relativistic
wave functions, emitted-photon translational recoil, and finite-wavelength
multipoles. Therefore `photon_eV` is the nonrelativistic internal energy
difference, before translational recoil. None of the numerical agreement
digits below represents a physical-model error bar.

The cascade is optically thin, with no absorption, stimulated emission,
collisional transitions, external fields or `l` mixing. Both `1s` and `2s` are
terminal states in this E1-only model. The `2s` excitation energy remains in
the atom ledger; no two-photon decay rate or spectral shape is inserted.

## Reduced mass, dipole and scaling

Let `r = r_e-r_N`, `R=(m_e r_e+M r_N)/(M+m_e)`, and

\[
 \mu=\frac{m_eM}{m_e+M},\quad
 a_{\mu Z}=\frac{\hbar}{\mu c\alpha Z},\quad
 \chi_{\mu Z}=\frac12\mu c^2\alpha^2 Z^2,\quad
 E_n=-\frac{\chi_{\mu Z}}{n^2}.
\]

The total electric dipole is

\[
 Ze\mathbf r_N-e\mathbf r_e
 =e(Z-1)\mathbf R-e\frac{M+Zm_e}{M+m_e}\mathbf r.
\]

For an internal transition the center-of-mass term is diagonal in the internal
state and contributes no transition matrix element. Define
`q_eff=e(M+Z m_e)/(M+m_e)`. Its sign disappears in the squared line strength.
For neutral hydrogen `q_eff=e` exactly. For a charged ion, replacing `m_e` by
`mu` while keeping only the electron dipole omits this small center-of-mass
factor. The implemented scaling is

\[
 \omega\propto\mu Z^2,\qquad
 I_{ul}\propto (\mu Z)^{-1},\qquad
 A_{ul}(Z,M)=A_{ul}(1,\infty)
 \frac{\mu}{m_e}Z^4\left(\frac{q_{\rm eff}}e\right)^2.
\]

The line branching probabilities and cascade photon counts are invariant under
this common scaling. Photon energies scale as `mu Z^2`, and lifetimes as the
inverse of the Einstein-A scaling. These statements assume the retained
Coulomb Hamiltonian, not an exact finite-mass QED theory.

## Analytic angular sum and radial quadrature

With `x=r/a_muZ` the dimensionless normalized radial function is

\[
 \mathcal R_{nl}(x)=\frac2{n^2}
 \sqrt{\frac{(n-l-1)!}{(n+l)!}}
 \left(\frac{2x}{n}\right)^l e^{-x/n}
 L_{n-l-1}^{2l+1}\left(\frac{2x}{n}\right).
\]

The length matrix element is

\[
 I_{ul}=a_{\mu Z}\mathcal I_{ul},\qquad
 \mathcal I_{ul}=\int_0^\infty x^3
 \mathcal R_{nl}(x)\mathcal R_{n'l'}(x)\,dx.
\]

Spherical-tensor algebra gives

\[
 \frac{1}{2l+1}\sum_{m,m',q}
 |\langle l'm'|C^{(1)}_q|lm\rangle|^2
 =\frac{\max(l,l')}{2l+1},\qquad l'=l\pm1.
\]

The unpolarized spontaneous coefficient is therefore

\[
 A_{nl\to n'l'}=
 \frac{q_{\rm eff}^2\omega_{ul}^3}{3\pi\epsilon_0\hbar c^3}
 \frac{\max(l,l')}{2l+1}|I_{ul}|^2,
 \quad \omega_{ul}=\frac{\chi_{\mu Z}}{\hbar}
 \left(\frac1{n'^2}-\frac1{n^2}\right).
\]

Only `n'<n` and `|l-l'|=1` occur. States of equal `n` are degenerate in this
Hamiltonian, so their spontaneous rate vanishes as `omega^3`; that does not
describe the small physical `2s-2p` splitting. The prefactor used in C is
`4 alpha omega^3/(3c^2)`, followed by the effective-charge factor, which avoids
introducing a separately rounded `epsilon_0`. Dimensional check:
`omega^3 I^2/c^2` has units `s^-1`.

For each radial integral set `y=(1/n+1/n')x`. The integrand becomes `exp(-y)`
times a polynomial of degree `n+n'+1`. Thus a `q`-point Gauss–Laguerre rule is
algebraically exact when `2q-1 >= n+n'+1`. For all emitted lines through
`n=20`, degree is at most 40; normalization integrals have degree at most 40.
Both the 24- and 48-point rules exceed this degree requirement. Floating-point
roundoff remains and is tested rather than called exact.

The native implementation evaluates Laguerre polynomials by a three-term
recurrence. Golub–Welsch roots are obtained by long-double Jacobi rotations;
weights use

\[
 w_i=\frac{y_i}{(q+1)^2[L_{q+1}(y_i)]^2}.
\]

This analytic weight expression avoids relative-error amplification in tiny
first-component eigenvector weights. An initial eigenvector-weight version
failed a radial normalization check by `2.4e-12` at `n=11,l=0`; it was replaced
before acceptance. The final maximum normalization residual is `1.42e-16`.

## Cascade elimination without a stiff time solver

For every nonterminal state `i`, define

\[
 \Gamma_i=\sum_j A_{ij},\qquad B_{ij}=A_{ij}/\Gamma_i.
\]

The directed graph is acyclic because `n_j<n_i`. Every reward `R` accumulated
from one initial atom obeys

\[
 R_i=\sum_j B_{ij}(r_{ij}+R_j),
\]

with terminal values specified independently. Increasing `n` evaluates all
rewards by back substitution and does not resolve atomic lifetimes in a
cosmological time integrator. The native kernel calculates

* total E1 photon count: `r_ij=1`, terminal reward zero;
* emitted energy: `r_ij=E_i-E_j`, terminal reward zero;
* terminal `2s` probability: zero edge reward, terminal values `(0,1)`;
* Ly-alpha and Balmer-alpha analogue yields: indicator rewards for `2p->1s`
  and any `n=3->n=2` edge;
* individual line yield `Y_i,e`: unit reward for edge `e`, zero otherwise.

The `Lyalpha_yield` and `Halpha_yield` CSV labels refer to hydrogen transitions;
for `Z>1`, they are the corresponding hydrogenic analogues. They are intrinsic
emission yields, not escaping or observed intensities.

The finite-state terminal ledger closes exactly in real arithmetic:

\[
 \sum_e Y_{i,e}\Delta E_e
 +P_{i\to2s}\frac34\chi_{\mu Z}
 =\chi_{\mu Z}\left(1-\frac1{n_i^2}\right).
\]

This is also valid for the initially terminal `2s` state. Adding a sourced
two-photon decay model would transfer that residual into radiation; adding
exactly two photons after eventual isolated `2s` decay is a counting statement,
not a calculation of the two-photon spectrum or time distribution. This
release keeps those quantities null.

For all injection states `n<=20`, downward E1 cascades are complete within the
model: they do not visit `n>20`. The cutoff error concerns unknown capture or
excitation into `n>20`, not loss of a downward edge from a retained state.
Ground-state arrival is not equivalent to net recombination once a real
radiation field can reionize or resonantly reabsorb emitted photons.

## Executed results and independent checks

`n20/RESULT.json`: 210 states, 2470 downward lines for each of eight mass/charge
cases, 19,760 line records, and 6190 native checks. The cases are infinite-mass
`Z=1,2,3` plus physical H, D, T, helium-3 II and helium-4 II. Physical lithium
isotope tables can use the same scaling after a declared nuclear mass is
supplied; this release does not substitute an integer mass number for it.

| Quantity | Computed value |
|---|---:|
| `I_2p,1s/a_muZ` | 1.2902662 |
| analytic radial value | `256/(81 sqrt(6))` |
| H-1 `A_2p,1s` | `6.2649031e+08 s^-1` |
| `B_3p,2s` | `262144/2215269 = 0.11833506` |
| `B_3p,1s` | `0.88166494` |
| `20s` expected E1 photons | 2.0854615 |
| `20s` terminal-2s probability | 0.085583397 |
| `20p` expected E1 photons | 1.2282477 |
| `20p` terminal-2s probability | 0.11767009 |
| circular `(20,19)` E1 photons | 19 |
| circular `(20,19)` H-1 lifetime | `0.00028409556 s` |

There is no Ly-alpha photon from an isolated E1 `3p` cascade: the atom either
emits Ly-beta directly to `1s` or Balmer-alpha to terminal `2s`. A Case-B
recycling prescription changes this result by introducing a different photon
transport problem and must not be silently folded into these branching ratios.

The independent Python verifier expands the radial polynomial with exact
rational coefficients, integrates its monomials using integer factorials,
and evaluates the remaining rational square root at 80 decimal digits.
Thirteen selected low/high-`n` transitions agree within `2.08e-16` relative.
An independent factorial Racah expression verifies the magnetic-substate sum
for eight `(l,l')` pairs through `(19,18)` exactly. No SymPy dependency is
needed. Further native checks include radial normalization, radial
orthogonality, positive A values, selection-rule zeros, exact `Z^4` scaling,
branch normalization, line-yield moments and the residual-energy ledger.

Maximum 24/48-point radial disagreement is `1.90e-14` relative; maximum cascade
energy residual is `2.72e-19` in units of `chi`; maximum line-count sum residual
is `1.13e-17`. These are floating-point diagnostics, not interval enclosures.

Measured final native execution: 0.217 seconds wall time, 0.204 seconds CPU
user time, 0.013 seconds system time, peak RSS 9088 KiB on the current host,
including CSV output. Compilation passed GCC `-Wall -Wextra -Wpedantic -Werror`.
The `resource.json` and independent-check JSON preserve the actual measurements.

## Consumer contract and remaining obligations

`transitions.csv`: state IDs are `(species,n,l)`; `A_s_inverse` is a spontaneous
rate per atom, `photon_eV` is the internal transition energy in eV,
`radial_a_mu_over_Z` is dimensionless, and `branch_probability` is conditional
on spontaneous E1 departure. `cascade.csv` gives one initial atom's expectations.
`line_yields.csv` is species independent under the stated common scaling.
Terminal E1 lifetimes are infinite; they must not be divided into a finite
source term. A network should retain `2s` or attach an explicitly declared
additional decay model.

Given an external bound-free provider `alpha_nl(T)` or excitation source
`S_nl(t)` in atoms per volume per time, line emissivity follows by linear
contraction `dot n_gamma,e = sum_nl S_nl Y_nl,e`, after any needed finite-delay
treatment. The emitted energy and retained `2s` energy use the same injection.
No injection distribution, statistical-`l` assumption, total recombination
coefficient or Case A/B declaration is manufactured from the bound-bound
table. R7's exact 1s bound-free provider can coexist with this provider but does
not supply excited-state injection. Non-E1 channels, optical-depth feedback,
high-`n` injection and multi-electron continua remain separate physical work.

## Primary references and constants

1. NIST, *Atomic Spectroscopy — Spectral Lines*, selection rules and E1
   transition-probability/line-strength relations:
   https://physics.nist.gov/Pubs/AtSpec/node17.html and the accessible equation
   rendering at https://www.nist.gov/pml/atomic-spectroscopy-compendium-basic-ideas-notation-data-and-formulas/atomic-spectroscopy .
2. NIST, *Persistent Lines of Neutral Hydrogen*, Ly-alpha benchmark:
   https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3_a.htm .
3. NIST CODATA 2022 complete constants listing, retrieved 2026-10-14:
   https://physics.nist.gov/cuu/Constants/Table/allascii.txt . The C source pins
   `alpha`, electron/proton/deuteron/triton/helion/alpha-particle masses; `h`,
   `c`, and `e` are exact SI defining constants. `hbar=h/(2pi)`.
4. Wiese & Fuhr, *Accurate Atomic Transition Probabilities for Hydrogen,
   Helium, and Lithium*, J. Phys. Chem. Ref. Data 38 (2009) 565,
   https://doi.org/10.1063/1.3077727 ; NIST public full text:
   https://srd.nist.gov/jpcrdreprint/1.3077727.pdf . This is a benchmark source;
   the present table was generated from the displayed Coulomb formulas.

The radial integral construction, exact finite-state rewards and explicit
center-of-mass dipole derivation above are the calculations implemented here.

\clearpage

# Atomic reduction with observable and time ownership

Evidence: derived; finite cascade implementation checked against independent forward propagation. This is an application of known absorbing-chain and effective-multilevel-atom methods, not a novelty claim. Primary source: Ali-Haimoud & Hirata, PRD82,063521(2010), arXiv:1006.1355v2, Sections IV and Appendices A-C, https://arxiv.org/abs/1006.1355 . The displayed date on the experimental HTML is a conversion artifact; arXiv version metadata fixes 2010.

## A spontaneous cascade is a directed acyclic graph

For a finite nonrelativistic electric-dipole atom with no pumping, collision, line trapping or photoionization during the cascade, every allowed edge i→j has E_i>E_j. Define lambda_i=sum_j A_ij and p_ij=A_ij/lambda_i. Retain ground1s and metastable2s as terminals. A yield w_ij (one photon, its energy, or an indicator of a selected line) satisfies

    v_i=sum_j p_ij(w_ij+v_j).

Starting from low n determines all v in one sweep. Mean time m_i=1/lambda_i+sum_j p_ij m_j. The second moment is

    s_i=2/lambda_i²+2/lambda_i sum_j p_ij m_j+sum_j p_ij s_j.

These follow by conditioning on the exponentially distributed first waiting time, independent of the destination. The joint waiting-time/branch law therefore needs no stiff ODE. Eventual photon yields need neither the event birth time nor a time mesh. Injection in a finite observer bin still needs the delay or a controlled fast-cascade approximation. Markov's inequality gives Pr(T_cascade>Delta)<=min(1,s_i/Delta²). Here T is time to an E1 terminal, not time for metastable2s to reach1s.

Algorithmic cost for one payoff is O(number_of_edges+number_of_states), storage O(states). Computing every individual line payoff can cost O(edges²); use selected observables or batched sparse propagation when the line inventory becomes large. The current finite n20 calculation is sufficiently small to retain the full inventory.

## General interior elimination retains a memory kernel

With column populations, dx/dt=Q x+B y+s and dy/dt=A y+C x+r, Q is transient Metzler. Let all interior paths eventually leave; then -Q is a nonsingular M-matrix and -Q^{-1}>=0. Frozen steady-state elimination gives

    x_*=-Q^{-1}(B y+s),
    A_eff=A-C Q^{-1}B,  r_eff=r-C Q^{-1}s.

For a conserved linear covector w=(w_y,w_x), w_y^T A+w_x^T B=0 and w_y^T C+w_x^T Q=0 imply w_y^T A_eff=0. This uses the full conservation relation; projecting arbitrary untracked binding energy away would not satisfy it. Exact finite-time evolution is instead

    x(t)=exp(Qt)x0+integral_0^t exp(Q(t-u))[B y(u)+s(u)]du.

Thus the exact reduced equation has memory and an initial-layer term. Its transform contains C(zI-Q)^{-1}B, while the static approximation uses -C Q^{-1}B. The derivatives at z=0 encode waiting-time moments. For an absorption kernel K>=0, the elementary |exp(-i omega t)-1|<=|omega|t bounds frequency-domain error by |omega| times its first delay moment. This gives a physically testable criterion for elimination against source variation, not a blanket replacement of dynamics by equilibrium. An E1-dark2s with no extra process makes Q singular if eliminated: retaining it is the constructive resolution used here.

## What moments remove microscopic dimensions

For known per-event joint measure dP, an additive energy or charge payoff needs its expectation, not a Monte Carlo sampling of every joint event. Linear event-to-network maps can therefore use charge probabilities and conditional energy moments directly. If later cross sections depend on electron energy, the relevant integrals are integral sigma(E)v(E)dP(E), not generally sigma(meanE)v(meanE). Spectral line transport requires line-resolved yields, and angular/recoil correlations require the corresponding joint moments or full amplitudes. Our daughter total probabilities and energy moments consequently enter number/heat interfaces; they do not by themselves define all secondary-collision or correlated-Li kernels.

## The moment reduction respects a proper source clock

Use signature(-,+,+,+), x0=ct, u.u=-1, dx=c k ds, q_a=c grad_a(theta), u.q=1. Let D=-u.k and A=q.k>0; source time theta and photon Doppler factor are distinct. The electron number current J^a=c N_e u^a/V+j^a, u.j=0 yields

    C=integral[-k.J/A] dtheta
     =integral[c D N_e/(V A)-k.j/A] dtheta,   B=sigma_T C.

C has units m^-2, B is dimensionless. For a source four-vector S^a=P u^a+F^a with u.F=0, -u.S=P and (g^a_b+u^a u_b)S^b=F^a. This is how per-event energy/momentum moments connect to the macroscopic source. Actual Wolfram/xTensor verifies these contractions. A state reduction or reset that preserves N_e and j at fixed geometry preserves instantaneous Thomson current; subsequent state-dependent rates and work still evolve.

## Reuse of cross-thread exact reductions

HH PHYS29 removes one Yukawa angle integral with modified Bessel functions, then regularizes its Coulomb threshold. REI OBSERVER15 R7 removes its separable absorption-only photon ODE by the characteristic exponential and integrates the existing cubic reconstruction directly. CR seeded angular-cluster closure applies its sufficient finite-seed inequality. See integration/DELTA_AND_REUSE.md for their equations and exact source-specific scope. We adopt these results without re-running their campaigns or transplanting numerical coefficients.

## Verification

cascade_adjoint.py reads the n20 physical transition table and independently forward-propagates probability masses for all starts/species. It checks normalization, selected photon/energy rewards and second-moment positivity. Existing native cascade output supplies a separate implementation. R8 Wolfram scalar checks prove the two-state generic resolvent and nuclear Jacobian identities. These arithmetic checks do not give a bound on omitted high-n population; a physical population provider must supply it.

\clearpage

# Hydrogenic daughter reconstruction from wave functions

This unit computes an actual bound/continuum daughter spectral distribution for a one-electron Coulomb charge quench. It fills a hydrogenic benchmark and supplies a lightweight continuum provider. The result is `derived`, `numerically_checked`, and `implementation_verified` within the nonrelativistic sudden, zero-recoil model. No many-electron correlated daughter distribution is inferred from it.

## Model, units and the physical interface

Let the normalized initial 1s state have inverse radius a>0 and the final Coulomb Hamiltonian have inverse radius b>0:

    psi_i(r) = (a^3/pi)^(1/2) exp(-a r),
    H_f = -(hbar^2/2 mu_f) Laplacian - hbar^2 b/(mu_f r).

The physical definitions are a=mu_i Z_i e^2/(4 pi epsilon_0 hbar^2), b=mu_f Z_f e^2/(4 pi epsilon_0 hbar^2). Introduce rho=b/a, K=hbar^2 a^2/(2 mu_f), y=a r, and x=k/a; k is a continuum wave number, not a momentum. Energies relative to the final electron+nucleus continuum threshold are E_n=-K rho^2/n^2 and E_k=K x^2. Probabilities are dimensionless; continuum density below is per unit x.

The initial benchmark table uses mu_i=mu_f=m_e, infinite nuclear mass. Thus rho=2 is the tritium-like Z_i=1 -> Z_f=2 quench, rho=3/2 is the hydrogenic Z_i=2 -> Z_f=3 quench, rho=3 is an additional Z_i=1 -> Z_f=3 stress test, and rho=1/2 checks a charge decrease. Reduced masses can be substituted without changing the overlap derivation. Section 9 implements that extension and the allowed beta phase-space weighting using CODATA2022 electron/triton and electron/helion mass ratios, while keeping the ground-channel Q value as an explicit selected parameter.

The nuclear transition is treated as instantaneous, the initial electronic wave function is unchanged during it, and the bound electron is propagated by H_f afterwards. Initial orbital angular momentum is zero. At zero recoil only the final l=m=0 channels contribute, so no angular grid or sum over high partial waves is needed. Spin is a spectator in this model.

These overlap weights enter a beta-decay calculation; an actual decay branching distribution additionally weights each electronic state by the available lepton phase space, nuclear matrix element, recoil, exchange and final-state interactions. In particular, the unbounded electronic quench spectrum must be restricted by energy conservation in the physical decay. Brown and Zhai explicitly formulate W_fi=|<f|i>|^2 and Q_f=Q+E_i-E_f, with an energy-dependent upper final-state limit [S1]. This separation is essential for using the result in the nuclear/atomic event ledger.

## Bound-state formula and its derivation

Use the radial convention integral_0^infinity |R_nl|^2 r^2 dr=1. Then

    R_10(a;r)=2 a^(3/2) exp(-a r),
    R_n0(b;r)=2 b^(3/2) n^(-5/2) exp(-b r/n) L_(n-1)^1(2 b r/n).

The Laguerre Laplace integral follows by termwise integration of its finite polynomial:

    integral r^2 exp(-s r) L_(n-1)^1(q r) dr
       = n [2s-(n+1)q] (s-q)^(n-2) / s^(n+2).

Substitution gives

    A_1 = 8 rho^(3/2)/(1+rho)^3,
    A_n = 8 rho^(3/2)(1-rho)n^(5/2)
                (n-rho)^(n-2)/(n+rho)^(n+2),  n>=2,
    P_n = |A_n|^2.

The removable n=rho=2 limit has the polynomial value A_2=-1/2 for rho=2; it must not be evaluated as an undefined logarithm. Equal charges give P_1=1 and P_n=0 for all n>=2. The native implementation handles both cases explicitly and evaluates the general high-n probability through log1p rather than large powers.

Wolfram Language independently integrated the n=1,2,3,4 Laguerre wave functions and the finite-recoil ground-state overlap. Direct 50-digit mpmath radial integration checks n=1,2,3,4,6,10 for all five rho values. These tests use radial wave functions, independently of the C summand formula.

## Controlled high-n tail

For n>rho set C=64 rho^3(1-rho)^2 exp(-4rho). The exact probability can be written

    P_n=C n^(-3) exp(delta_n),
    delta_n = -4n sum_(j>=1) (rho/n)^(2j+1)/(2j+1)
              -4 log(1-rho^2/n^2).

With N+1>rho and D=(N+1)^2-rho^2, elementary positive-series bounds give

    -4rho^3/(3D) <= delta_n <= 4rho^2/D, n>N.

Together with the decreasing-function integral bounds for sum_(n>N) n^(-3),

    C exp[-4rho^3/(3D)]/[2(N+1)^2]
       <= T_N = sum_(n>N) P_n
       <= C exp[4rho^2/D]/(2N^2).

Thus 1-sum_(n<=N)P_n is only an upper bound on the continuum weight. The continuum interval from the bound sum is [1-S_N-T_hi,1-S_N-T_lo]. The analytic bounds control truncation of exact summands. C long-double evaluation is checked against high-precision independent computation; the implementation is not advertised as a directed-rounding certificate.

For rho=2 and N=100000, S_N=0.97372718301410750156 and

    8.58767151085514e-12 <= T_N <= 8.58784328804458e-12.

The tail-bound width is about 1.718e-16. Energy-weighted bound tails satisfy |sum_tail E_n^j P_n| <= [K rho^2/(N+1)^2]^j T_hi, j=1,2.

## Continuum density without a continuum eigenproblem

Choose the attractive regular Coulomb function with eta=-b/k and radial delta(k-k') normalization

    u_k(r)=sqrt(2/pi) F_0(-b/k,k r),
    u_i(r)=2 a^(3/2) r exp(-a r).

Its hypergeometric representation is F_0(eta,z)=C_0(eta) z exp(-iz) 1F1(1-i eta;2;2iz), with

    C_0(-b/k)^2=(2 pi b/k)/(1-exp[-2 pi b/k]).

The overlap is the Laplace transform of r^2 exp[-(a+ik)r] 1F1. The identity

    2F1(A,3;2;z)=(1-z)^(-A-1)[1+(A/2-1)z]

reduces it to an elementary expression. The numerator contains a-b, enforcing exact bound/continuum orthogonality when the charge does not change. The resulting density is

    dP_c/dx = 64 rho (1-rho)^2 x/(1+x^2)^4
              * exp[-4rho atan(x)/x]/(1-exp[-2 pi rho/x]).

It is nonnegative for x>0 and vanishes identically at rho=1. The native code maps x=t/(1-t), 0<t<1, and uses 256 and 512 Gauss-Legendre nodes. expm1 prevents cancellation in the high-energy denominator. Direct mpmath integration of the Coulomb radial wave function validates this density at rho=1,1.5,2 and x=0.3,1,3, including the equal-charge null test.

The zeroth, first and second continuum moments are calculated directly on [0,infinity]. Completeness against the separately computed bound sum and its analytic tail is an independent normalization check. This construction needs no continuum box, pseudostate calibration or parallel eigensolve.

## Computed values

The first and second continuum moments are unconditional: M_j=integral E^j dP_c. The conditional mean energy of an ionized electron is M_1/P_c.

| rho | P_1s | P_2s | P_continuum | M_1/K | M_2/K^2 |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 0 | 0 | 0 |
| 1.5 | 0.884736 | 0.07673604 | 0.023381078 | 0.036588757 | 0.4961318 |
| 2 | 0.70233196 | 0.25 | 0.026272817 | 0.066434444 | 1.5098693 |
| 3 | 0.421875 | 0.56623104 | 0.010381723 | 0.071395182 | 3.9613587 |
| 0.5 | 0.70233196 | 0.04194304 | 0.23351926 | 0.17862065 | 0.95593051 |

For the tritium-like rho=2 case, the converged bound probability is 0.97372718302269525893 and the conditional continuum mean is 2.5286380114760612045 K. Multiply K by its chosen physical value in eV only after fixing reduced masses and constants. These printed digits expose numerical reproducibility of this specified model; they are not a physical uncertainty estimate for tritium decay.

The native C run takes approximately 0.13 CPU seconds on the present host for all five rows, each with 100000 bound levels and both continuum quadratures. Independent 50-digit verification ran in 18.15 seconds and passed 73 assertions. It checks the radial integrals, continuum density, direct/high-precision quadrature agreement, number completeness, and both energy sum rules. Timing is host-specific, not a universal performance guarantee.

## Exact inclusive energy moments and recoil

Because H_f acting on the initial exponential is elementary, the spectral theorem computes the first two full moments without any final-state sum:

    <H_f>/K = 1-2rho,
    <H_f^2>/K^2 = 1-4(1-rho)+8(1-rho)^2,
    Var(H_f)/K^2 = 4(1-rho)^2,
    <H_f-E_1>/K = (rho-1)^2.

The second identity follows from ||H_f psi_i||^2, using <1/r>=a and <1/r^2>=2a^2. It therefore avoids delicate term-by-term second derivatives at the Coulomb cusp. The native bound+continuum moments satisfy these sum rules.

The continuum density has the ultraviolet asymptote dP_c/dx ~ 32(1-rho)^2/(pi x^6). Thus the zeroth through second energy moments are finite, whereas the third and higher raw positive continuum energy moments diverge in this ideal quench model whenever rho!=1. This is a restriction on moment-based reductions of the specified model: extend them using a physical energy cutoff and phase-space kernel, rather than silently requesting undefined higher moments. The high-energy tail and all physical beta-decay corrections remain separate from the small numerical quadrature error.

For a prescribed momentum kick hbar q along a fixed direction, the wave function becomes exp(i q.r) psi_i. At fixed a,b, write zeta=q/a. The ground-state probability is exactly

    P_1(q)=64 (a b)^3 (a+b)^2/[(a+b)^2+q^2]^4
          =P_1(0)[1+q^2/(a+b)^2]^(-4).

The inclusive mean and variance become

    <H_f>/K=1-2rho+zeta^2,
    Var(H_f)/K^2=4(1-rho)^2+4zeta^2/3.

For rho=2 and zeta=0,0.01, 0.1,1, P_1 is respectively 0.70233196159122085, 0.70230074770442958, 0.69921913774036210, 0.4608. The ground overlap was checked by direct spherical-Bessel quadrature. Mapping q to nuclear and atomic recoil momenta requires the same Jacobi mass convention as the event generator; no independent recoil prescription is silently inserted.

The general finite-kick bound channels have

    sum_m P_nlm(q)=(2l+1)|integral r^2 R_nl(b;r) R_10(a;r) j_l(qr) dr|^2.

This gives an explicit local implementation route. This unit does not sum its nonzero-q bound/continuum spectrum to completeness. Actual beta-recoil averaging must retain its correlation with lepton phase space and final excitation energy.

## Observable reduction and what must remain joint

For a prescribed bath and independent daughter propagation, an additive mean response has the form

    E[sum_a F_a(X_a)] = sum_a integral F_a(x_a) dP_a(x_a).

Only one-particle marginals are required; no approximation is involved in this equality. For isotropic zero-recoil injection the birth-direction average is also exact. If a response is affine or quadratic in electronic energy, the matching spectral moments suffice. With instantaneous complete thermalization of an outgoing continuum electron, its number and kinetic-energy injection use P_c and M_1, respectively. Bound excitation is a distinct stored-energy/cascade source and must not be counted as immediate gas heating.

For nonlinear energy-dependent stopping, ionization thresholds or frequency-resolved cascade radiation, the full relevant marginal or a controlled quadrature is retained. An approximation F(E) by a polynomial on a compact interval gives a response error bounded by the sup-norm residual times probability there, plus the separately bounded physical tail. A physical beta-decay kernel requires energy-dependent phase-space weighting before this reduction; raw quench moments cannot replace it.

Marginals do not determine every observable. Two daughter energies with identical Bernoulli(1/2) marginals may be supported on (0,0),(1,1) or on (0,1),(1,0). Both cases have mean total energy 1, but P(E_1+E_2>1) is 1/2 and 0, respectively. Coincidence counts, nonlinear bath response and eventwise conservation therefore need the corresponding joint structure. This example identifies the exact information loss rather than treating all joint calculations as mandatory.

## Source comparison and scoped correction

Frolov [S2] gives finite-N bound sums consistent with the hydrogenic formula used here. Its Table I lists S_1000=0.97372709722987 and S_1700=0.97372715332442. The same displayed text quotes P_bb=0.97372735(10). Our continuum calculation, analytic high-n bound and independent radial checks give 0.97372718302269526; the text's quoted central value differs by approximately 1.67e-7. The finite-N table itself is not contradicted. We adopt the independently reconstructed limit and preserve this discrepancy in provenance.

The continuum density above is independently derived with delta-normalized attractive Coulomb waves. The generalization to arbitrary a=b obeys exact orthogonality. We do not normalize an externally quoted spectral shape to a borrowed total probability, because doing so would conceal a possible normalization or Coulomb-sign error. No conclusion about the validity of every result in [S2] is drawn.

## Executed allowed-beta phase-space extension

The low-cost physical support and phase-space calculation was implemented and run here in `allowed_beta.c`, rather than deferred. Its selected parameter is Q_g=18600 eV, defined as the total kinetic energy available to the beta electron and neutrino when the daughter electron occupies its ground state. This is an illustrative tritium-scale ground-channel value, not a mass-derived isotope Q value. The final electronic excitation energy is Delta_n=K rho^2(1-1/n^2) for bound states and Delta_x=K(rho^2+x^2) in the continuum. Only states with Delta<Q_g contribute.

For a constant allowed nuclear matrix element, zero neutrino mass and no recoil, use the integrated lepton weight

    Phi_F(Q)= integral_0^Q dT [p(T)c] (T+m_e c^2)(Q-T)^2 F(T),
    p(T)c=sqrt[T(T+2m_e c^2)].

Overall weak constants cancel in normalized branching fractions. Two declared choices are executed: F=1, and the point-Sommerfeld factor F=2pi eta/[1-exp(-2pi eta)] with eta=2 alpha (T+m_e c^2)/[p(T)c]. The second is a bare Z_f=2 Coulomb approximation using relativistic kinematics; it does not include screening, finite nuclear size, radiative corrections, beta/atomic-electron exchange, or post-decay electron-electron interactions. The nuclear absolute decay rate is not computed.

The continuum branching probability and moments are

    Z = sum_n P_n Phi(Q_g-Delta_n) + integral dP_c Phi(Q_g-Delta_x),
    P_c(beta)= integral dP_c Phi(Q_g-Delta_x)/Z,
    M_j(beta)= integral (Kx^2)^j dP_c Phi(Q_g-Delta_x)/Z,

where Phi(Q<=0)=0. The physical continuum support is x<sqrt(Q_g/K-rho^2). Beta and neutrino kinetic-energy moments are integrated from the same event measure. The independently summed energy ledger satisfies <T_beta>+<E_nu>+<Delta>=Q_g.

The bound sum uses 100000 levels. Since Phi is increasing in Q, its high-n weighted tail is bracketed by multiplying the analytical probability-tail endpoints by Phi(Q_g-Krho^2) and Phi(Q_g-Delta_(N+1)), respectively. The code uses the bracket midpoint. For rho=2 its normalized-rate bracket width is about 1.7e-16. Tail excitation/beta/neutrino moments use the n=infinity limit, whose omitted excitation variation is bounded by K rho^2 T_hi/(N+1)^2. Quadrature is independently checked with adaptive integration.

| Infinite-mass model | P_continuum | M_1 per decay (eV) | M_2 per decay (eV^2) | Conditional slow-electron mean (eV) | Mean electronic excitation (eV) |
|---|---:|---:|---:|---:|---:|
| Raw unweighted quench | 0.026272817 | K times 0.066434444 | K^2 times 1.5098693 | K times 2.528638 | K |
| Allowed F=1 | 0.025903255 | 0.85824583 | 164.72362 | 33.132741 | 13.480098 |
| Allowed bare Sommerfeld Z=2 | 0.02592081 | 0.86014666 | 166.56022 | 33.183634 | 13.48583 |

For F=1, mean beta/neutrino energies are 6229.30346812155 and 12357.21643411050 eV. For the bare-Coulomb choice they are 5694.48459594246 and 12892.02957386690 eV. The summed energy residual is below 1e-12 eV in all four infinite/reduced-mass model rows. This residual is numerical ledger closure, not physical uncertainty.

The exact CODATA2022 inputs used are m_e c^2=510998.95069 eV, R_infinity h c=13.605693122990 eV, alpha=0.0072973525643, m_e/M_triton=0.0001819200062327 and m_e/M_helion=0.0001819543074649 [S6]. In the reduced-mass runs set mu_i/m_e=1/(1+m_e/M_triton), mu_f/m_e=1/(1+m_e/M_helion), rho=2mu_f/mu_i, and K=(R_infinity h c)(mu_i/m_e)^2/(mu_f/m_e). These calculations are in `allowed_beta_reduced_128.csv` and `allowed_beta_reduced_256.csv`. The selected Q_g remains unchanged across this comparison so that the atomic reduced-mass effect is isolated. Nuclear recoil is a different correction.

Both 128- and 256-node calculations are executed, taking about 1.2 and 2.2 CPU seconds per pair of F choices. Independent SciPy adaptive integration in the direct x and T variables checks the continuum numerator and finite bound sums; 43 added assertions, including finite-q 2p checks, pass in approximately one second. `allowed_beta_verification.json` records exact differences and tolerances. Constants' covariance and the missing physical corrections have not been folded into an uncertainty posterior.

A further finite-recoil bound channel is also evaluated. For a prescribed kick q, the sum over final 2p magnetic substates is

    P_2p(q)=32 a^3 b^5 (a+b/2)^2 q^2 / [(a+b/2)^2+q^2]^6.

For a=1,b=2 this is q^2/(1+q^2/4)^6, giving 0.00009998500131241250, 0.009851303798973779 and 0.262144 at q/a=0.01, 0.1, 1. Direct spherical-Bessel/Laguerre quadrature confirms these numbers. These are specified-kick partial channels, with no claim of complete recoil-averaged branching.

## What local Codex should do next

1. Integrate this provider as a regression benchmark into the daughter module. Re-run `build_and_check.sh`; preserve its model/units fields.
2. Connect the now-executed allowed phase-space and reduced-mass providers. Replace the selected Q_g by a mass/ionic-binding-consistent Q value when that event contract is fixed, and then add recoil and exchange/final-state corrections. The existing small integration does not require HPC.
3. If nonzero recoil matters, implement the displayed spherical-Bessel partial-wave radial integrals, bound and continuum completeness, and recoil averaging. Increase l only until a derived/monitored tail meets the requested observable error.
4. For actual correlated He/Li daughter branching, solve balanced antisymmetric parent and daughter states, form asymptotic exclusive projectors, and evaluate continuum amplitudes. Parallelize independent angular momenta, spin sectors, energies and basis convergence jobs, not duplicated small quadratures.
5. Return channel-resolved spectra, moments, closure/completeness residuals, physical/model errors, convergence grids, exact code/input identities, and measured CPU/RAM scaling. Do not promote the hydrogenic benchmark into a correlated-Li result.

## Sources and execution evidence

- S1. L. S. Brown and C. Zhai, *Atomic effects in tritium beta decay*, Ann. Phys. 249 (1996) 298–361, arXiv:hep-ph/9511209. https://arxiv.org/html/hep-ph/9511209v1 . Primary source read; Eqs. (2)–(5) separate overlap weights from the physical beta spectrum and its support.
- S2. A. M. Frolov, *Spectrum of secondary electrons emitted during the nuclear beta-minus decay of the tritium atom*, arXiv:1512.04721v2. https://arxiv.org/html/1512.04721v2 . Primary source read; finite bound sums are comparison data, continuum and asymptotic normalization independently reconstructed as above.
- S3. NIST DLMF, Chapter 33, Coulomb functions and scattering normalization: https://dlmf.nist.gov/33.2 and https://dlmf.nist.gov/33.22 . Mathematical convention reference.
- S4. J. Arafune and T. Watanabe, *Effect of final-state interactions in tritium beta decay*, Phys. Rev. C 34 (1986) 336. https://doi.org/10.1103/PhysRevC.34.336 . Primary abstract consulted; motivates retaining final-state corrections separately from a sudden benchmark.
- S5. C. Couratin et al., *First Measurement of Pure Electron Shakeoff in the beta Decay of Trapped 6He+ Ions*, Phys. Rev. Lett. 108 (2012) 243201. https://doi.org/10.1103/PhysRevLett.108.243201 . Primary bibliographic/abstract record found; not used as a zero-recoil numerical validation, since experimental recoil and acceptance differ.
- S6. NIST, *2022 CODATA adjustment: Fundamental Physical Constants, Complete Listing*. https://physics.nist.gov/cuu/Constants/Table/allascii.txt . Primary values read on 2026-10-14; the five constants and ratios used in the allowed-beta extension are recorded above.

Files: `daughter_hydrogenic.c`, `verify_daughter.py`, `results.csv`, `verification.json`, `timing.txt`, `wolfram_checks.wl`, `WOLFRAM_RECEIPT.json`, `build_and_check.sh`. Library-wide backup and publication are performed by the parent research unit.

Independent review additionally rederived the n-tail bound and second-moment identity and tested Coulomb radial overlaps at (rho,x)=(0.75, 0.7),(2.5, 0.45),(2.5, 2.3) to relative discrepancies below 6e-41 at 40-digit precision. Evidence is recorded in the parent `review/daughter_independent_radial.json`. The finite-N source comparison is preserved in `source_comparison.json`.

\clearpage

# R8 nuclear microphysics: threshold-regular native capture and inverse rates

## Adopted physics and new result

The physical input is the already reconstructed Chen–Savage (1999) pionless-EFT
np capture model: isovector M1 through NLO and E1 through N3LO. This unit ports
that amplitude to C11, removes its artificial threshold singularity, derives
and executes inverse Planck-spectrum rates, and provides analytic low-temperature
expansions. It does not replace this amplitude by a current global posterior.

The historical thermal input is 334.2 mb at neutron speed 2200 m/s. Fitting the
same counterterm gives L_np = -4.4971393470541 fm², up to floating-point rounding.
The threshold capture coefficient is

    K0 = lim[E→0] σ_np(E) v_rel(E)
       = 7.352401227837007 × 10^(-26) m³/s.

The C result at 6.109701377331961 K is 7.3524011511269414×10^(-26) m³/s.
These are a native implementation and additional inverse-rate calculations of
the adopted physical model, not newly fitted data. Published higher-order
calculations and the 2026 D photodisintegration study are separately identified
in SOURCES.json and in the local execution contract.

The new numerical checks all pass: 54/54 in CHECKS.json. They establish
implementation and quadrature agreement in this declared model. They do not
constitute outward-rounded intervals or certify the EFT truncation error.

## Physical input, units, and frames

The metric convention is (-,+,+,+). External cross sections are m²; capture
coefficients are m³/s; photo-destruction rates are s^(-1). Explicit energy
arguments are in MeV. The kernel keeps c, hbar and k_B in the SI conversion.
The nuclear model uses the paper's equal nucleon rest energy M=938.92 MeV,
binding Q=2.224575 MeV, hbar*c=197.3269804 MeV fm and the inherited scattering
parameters. For the exact kinematic adapter only, the consistent model
deuteron rest energy is Md=2M-Q. These are model masses, not a current AME
mass update. Updating one mass without updating thresholds and the adopted
amplitude is disallowed.

The photon ensemble is isotropic and unpolarized in the target-rest frame
for the stationary-target inverse rate. Nuclear spin degeneracies are
g_n=g_p=2 and g_d=3; g_gamma=2 counts photon polarizations. No excited nuclear
partition functions or hyperfine populations are inferred from these factors.

## Remove the threshold singularity before numerical integration

With p=sqrt(M E)/(hbar*c), the inherited cross section has the form

    σ(E) = A(p²) / p,
    v_rel(E) = 2c sqrt(E/M) = (2c hbar*c/M) p.

Thus K(E)=σ(E)v_rel(E) is analytic in E at zero. The C code evaluates the
product directly and accepts E=0 for K. It rejects E=0 for σ itself, which
really diverges as 1/v in this adopted neutral-capture model. No arbitrary
cross-section cutoff or tiny nonzero replacement energy is required.

The normalized relative Maxwell distribution gives

    <σv>(T) = (2/sqrt(pi)) ∫_0^∞ dx sqrt(x) exp(-x) K(k_B T x).

The change x=y² makes the endpoint smooth:

    <σv>(T) = (4/sqrt(pi)) ∫_0^∞ dy y² exp(-y²) K(k_B T y²).      (N8.1)

The implementation integrates 0≤y≤sqrt(80) with Gauss–Legendre quadrature.
The 64- and 128-node results agree at floating-point roundoff in the reported
grid. An independent adaptive x integral checks a different parameterization.
The thermal domain is 10^(-3)≤T≤10^8 K. Its largest sampled capture energy is
80 k_B T = 0.689387 MeV, below the adopted 1 MeV EFT domain.

The omitted x>80 Maxwell probability is 1.8328665315368073×10^(-34).
This is a probability, not a rate-error bound on unspecified high-energy
cross sections. The finite integral and the model-domain restriction remain
part of each rate's provenance.

## Low-temperature expansion is algebraic

Write K(E)=K0+K1 E+K2 E²/2+... using MeV energy. Formal second-order Taylor
arithmetic applied to the rational EFT expression yields

    K1/K0 = -13.211102286994354 MeV^(-1),
    K2/K0 = 425.88275183062933 MeV^(-2).

Because <x>=3/2 and <x²>=15/4,

    <σv> = K0 [1 + (3/2)(K1/K0) theta
                  + (15/8)(K2/K0) theta² + O(theta³)],             (N8.2)

where theta=k_B T in MeV. This removes quadrature altogether when the
remainder is acceptable. Against direct integration, the quadratic
approximation has relative error 2.7×10^(-14) at 10^4 K, 2.63×10^(-8) at
10^6 K, and 2.54×10^(-5) at 10^7 K. At 10^8 K its error is about 1.98%,
so direct one-dimensional integration is retained there. These differences
are measured approximation errors in the specified amplitude, not universal
error bounds for nuclear physics. Code selection should compare the
asymptotic approximation to a cached direct value for the chosen model.

## Inverse cross sections: spin and photon factors

For distinct incoming particles, time-reversal symmetry of the same matrix
element and two-body phase space give

    σ_gamma_d→np / σ_np→d_gamma
      = (g_n g_p)/(g_d g_gamma) * p_np² / p_gamma²
      = (2/3) p_np² / p_gamma².                                  (N8.3)

The 2/3 is not 4/3: two photon polarizations belong in the incoming-state
average of the inverse cross section. The factor 4/3 reappears in the
thermal statistical-density relation after integration of the photon
phase-space measure. The code checks this distinction explicitly.

For the equal-mass model, set W=2M+E. Exact two-body kinematics are

    p_np² c² = E(4M+E)/4,
    epsilon = [(W-Md)(W+Md)]/(2Md),
    p_gamma c = epsilon Md/W,
    epsilon_th = Q + Q²/(2Md).                                    (N8.4)

The last term is 1.3192293752395967 keV. This is an exact two-body
kinematic adapter applied to a nonrelativistic, equal-nucleon-mass capture
amplitude; it is not a fully relativistic nuclear amplitude.

The threshold-stable inverse is

    E = 2Md delta / [sqrt(4M²+2Md delta)+2M],
    delta = epsilon-epsilon_th.                                  (N8.5)

It avoids subtracting two approximately 1878 MeV numbers to recover a
sub-eV relative energy.

## Planck inverse integral and log-stable implementation

For stationary deuterons in an isotropic photon bath,

    lambda_rest(T_gamma) = c/[pi²(hbar c)³]
       ∫_(epsilon_th)^∞ d epsilon epsilon² σ_gamma(epsilon)
                          /[exp(epsilon/(k_B T_gamma))-1].          (N8.6)

All energies in this expression are joules; the code inserts MEV³ for
MeV integration. Set delta=theta*y² and factor out exp(-epsilon_th/theta).
Then the code returns the pair

    activation = epsilon_th/theta,
    logpref = log(exp(activation)*lambda),
    log(lambda) = logpref - activation.                            (N8.7)

The pair is authoritative at ultralow temperature. Subtracting a number
of order 10^13 from a number of order 10 retains too few digits to recover
the prefactor; therefore log10(lambda) is a display field, not a substitute
for the pair. Zero caused by ordinary exp underflow must never be recorded
as an exact physical zero.

The integrand uses 1/[-expm1(-activation-y²)] and a smooth y endpoint.
An independent calculation uses E as the integration variable and the
identity

    epsilon² (p_np²/p_gamma²) (d epsilon/dE)
      = p_np² (W/Md)³.                                          (N8.8)

Thus the inverse requires one cheap integral, not independent angular
sampling or a multidimensional Monte Carlo calculation.

## Thermal balance: keep the approximation consistent

The separate zero-recoil convention uses epsilon=Q+E and

    σ_gamma^NR = (2/3) M E/(Q+E)² * σ_capture(E).

In the Wien limit it implies the leading nonrelativistic relation

    lambda_NR / <σv> = (4/3)
       [mu k_B T/(2pi hbar²)]^(3/2) exp[-Q/(k_B T)],
    mu c²=M/2.                                                    (N8.9)

The direct NR inverse integral and this independent normalization agree
to about 10^(-14) in log-prefactor on the reported grid. The code retains
the full Planck denominator. The omitted stimulated-capture correction
when comparing with a vacuum capture rate is bounded by
exp(-Q/theta)/[1-exp(-Q/theta)]; Q/theta≥258.151 in this domain, so the
relative correction is below approximately 8×10^(-113).

Equation N8.9 also adopts the leading recoil-free translational-mass
approximation. An exact thermodynamic density ratio instead contains
(m_n m_p/m_d)^(3/2), with relativistic kinetic corrections if required.
Those must be used together with a consistent thermal-target reaction
integral, not selectively inserted into the NR benchmark.

A stationary-target inverse rate is not an equilibrium thermal-target
rate. In particular, combining epsilon_th from N8.4 with the activation
Q of N8.9 fails nonuniformly at low temperature. The ratio of leading
stationary-target to zero-recoil inverse rates is

    (2M/Md)^(3/2) exp[-Q²/(2Md k_B T)].                            (N8.10)

The nominally small recoil shift can dominate a logarithm at low T.
This is a frame/ensemble distinction, not failure of microscopic
reciprocity. A true thermal nuclear equilibrium calculation averages the
target velocities and photon energies consistently. The Maxwell–Boltzmann
thermal-target extension was also executed below; the full Bose moving-target
extension remains specified in LOCAL_CODEX_NUCLEAR.json.

At T_gamma=10^4 K, the model gives log10(lambda_NR/s^-1)=-1121129.6367
and log10(lambda_rest/s^-1)=-1121794.4982. At 10^8 K these are -99.354506
and -99.420156. These are finite-integral, specified-model values, not
universal limits on hard nonthermal photons. A stellar/quasar or other
high-energy component must be integrated over its actual spectrum.

## Network conservation and energy accounting

In the species ordering (n,p,d,gamma), the event vector is
nu=(-1,-1,+1,+1). The baryon vector A=(1,1,2,0) and charge vector
Z=(0,1,1,0) obey A·nu=Z·nu=0. Nuclear particle count decreases by one;
photon count increases by one. The released Q belongs to photon/kinetic
energy and must not also be added as thermal heat when the photon is
explicitly propagated. The inverse consumes that photon. Electronic
charge states and any daughter shake processes require their own
atomic-event records rather than alteration of nuclear Z conservation.

## What was executed and what remains

Executed here: C11 capture, inverse cross sections, finite Planck inverse
integrals, threshold expansion, independent quadratures, conservation,
domain checks. 200 native capture integrations using 64 nodes took about
0.008 s on this host; this timing is not a prediction for a different
machine or an inclusive reaction network.

The higher-order np posterior, nd three-body current, A=3/4 exclusive
continuum amplitudes, Li7 EFT/R-matrix fit, and shared experimental
normalization posterior still require their physical inputs and dedicated
execution. Their expensive wavefunctions may be generated locally once
and consumed as versioned state-resolved response tables. Cheap thermal
averaging and network integration should not be sent to HPC by default.

## Failure and correction record

The initial independent inverse quadrature used an absolute tolerance on
an unnormalized tiny integral; it produced false ~0.14% discrepancies at
the coldest temperatures. FIRST_CHECK_FAILURE.json preserves that result.
The correction divided by the analytic threshold scale before integration.
No physical kernel or acceptance threshold changed. Those 41 new checks
then passed. The later thermal-target check also initially omitted a factor
1/c in its numerical normalization, making its adaptive absolute tolerance
too loose for a 2×10^(-11) comparison. Its record is retained separately;
restoring the dimensionless scale closed the discrepancy. SymPy was absent
in this runtime; formal second-order Taylor
arithmetic supplied the analytic derivatives without adding a dependency.

## Evidence states

* Literature-supported: EFT amplitude order, original thermal fit, published
  higher-order and 2026 update routes.
* Derived: smooth threshold product, inverse kinematic transformation,
  low-T moment expansion, recoil/ensemble distinction, conservation.
* Numerically checked: new rates, asymptotic errors, independent variable
  quadratures and thermal normalization.
* Implementation-verified: C compiler success and 54/54 checks.
* Unresolved/input-dependent: modern nuclear posterior and exclusive
  multibody amplitudes; no associated new physical numbers are invented.

## Thermal-target reduction executed here, without a six-dimensional integral

The invariant Maxwell–Boltzmann reaction-density reduction of Gondolo and
Gelmini supplies an additional useful simplification. For the equal-mass
incoming pair and a cross section specified as a function of invariant s,

    <σ v_Moller> = c/[8 M^4 theta K_2(M/theta)^2]
       ∫_(4M²)^∞ ds σ(s) sqrt(s)(s-4M²) K_1(sqrt(s)/theta).        (N8.11)

Energies are in a common unit; cross sections are SI, so c converts the
dimensionless Moller velocity to m/s. The distributions are classical
Maxwell–Juttner distributions. Fermi blocking and final-state Bose
enhancement are omitted in this particular thermal benchmark. A photon
Maxwell–Boltzmann (Wien) ensemble is used for its matching inverse rate.

Set S_nu(z)=exp(z)sqrt(2z/pi)K_nu(z). The numerical domain satisfies
M/theta≥108956. Then S_nu has a rapidly convergent asymptotic expansion,
implemented through six terms and independently compared with SciPy kve.
After s=(2M+E)², the native integration is again N8.1, with K(E) multiplied by

    F(E,T)=(1+E/(4M)) [(2M+E)/(2M)]^(3/2)
                 S_1((2M+E)/theta)/S_2(M/theta)^2.                 (N8.12)

No exponentially small Bessel values are ever formed. For thermally moving
deuterons, the matching inverse rate has activation Q/theta and prefactor

    lambda_thermal_MB = <σv_Moller> (4/3)
       [(m_n m_p/m_d) k_B T/(2pi hbar²)]^(3/2)
       [S_2(M/theta)^2/S_2(Md/theta)] exp(-Q/theta).                (N8.13)

Here m_n=m_p=M/c² and m_d=Md/c², with unit conversion from MeV. This uses
the consistent mass ratio rather than the leading reduced-mass replacement.
The code independently checks N8.13 by integrating the inverse reaction
density with σ_gamma and dividing by the deuteron equilibrium density:

    exp(Q/theta) lambda_thermal_MB
      = c/[8pi²(hbar c)^3 Md²]
        ∫_0^∞ dE 2[(2M+E)²-Md²]² σ_gamma(E)
        sqrt[Md/(2M+E)] [S_1((2M+E)/theta)/S_2(Md/theta)] exp(-E/theta).
                                                                    (N8.14)

As before, MEV³ converts the all-MeV integration to SI. This check compares
an inverse phase-space integral to a forward integral times a statistical
density ratio, not two copies of the same final expression.

Results are in thermal_target_MB.json. At 10^8 K, capture_Moller is
6.405664345734996×10^(-26) m³/s; its difference from the NR capture average is
-1.99649×10^(-5). The thermal inverse log10 rate is -99.35373125, compared
with -99.42015550 for deuterons fixed at rest. At 10^4 K the difference of
inverse activation energies is enormous in relative rate while both rates
are negligible absolutely. This directly resolves the apparent conflict
between exact stationary-target recoil and the thermal Saha activation.

The model cross section remains the inherited nonrelativistic EFT shape.
These are a verified invariant thermal-averaging adapter and an ensemble
consistency calculation, not a higher-order nuclear amplitude. The full
moving-target Planck occupation/stimulated-emission integral is not claimed
to have been executed. It is unnecessary to offload N8.11 to large hardware;
its reduction and native implementation are complete here.

\clearpage

# Direct Stobbe folding in a prescribed finite spectral band

Reuse the immutable R7 nonrelativistic infinite-mass 1s provider. This new calculation folds it with a common physical intensity, not with a digitized graph or fitted atomic rate. Let E=h nu, chi_Z=Z² chi_H, and J_nu=J_H(E/chi_H)^(-a) exp[-N_H sigma_H(E)] between the target threshold and 200eV. J_H=1e-24 W m^-2 Hz^-1 sr^-1 is the selected illustrative boundary intensity, equivalent to1e-21 erg s^-1 cm^-2 Hz^-1 sr^-1. N_H is a prescribed foreground neutral-hydrogen column. No re-emission or additional absorbers are included.

Substitute x=ln(E/chi_Z). The rates per target are

    Gamma=(4 pi/h) integral J_nu(E) sigma_Z(E) dx [s^-1],
    H=(4 pi/h) integral J_nu(E) sigma_Z(E)(E-chi_Z) dx [J s^-1].

One quadrature accumulates both. The specific intensity, cross section and dnu/nu conversion explain the single1/h; neither an extra c nor another 1/E enters. This uses an isotropic local proper radiation field. The foreground hardens the spectrum because the hydrogenic cross section decreases with energy in this model.

run.py compiles the C code and computes Z1,2,3 ×4 spectral slopes ×3 columns. 64/128/256 orders are refinement checks. Independent SciPy integration uses a separately written cross section and the linear E/chi variable. The two agree to the values in RESULT.json; these are floating-point convergence tests, not directed interval certificates. The finite200eV source cutoff is a model boundary, not an asserted negligible tail of every stellar/quasar spectrum. The output supplies a reusable local radiation response; a redshift history has not been inferred from these illustrative inputs.

Atomic provenance is the copied R7 source and SHA in RESULT.json. Primary physical formula: Kotelnikov & Milstein, Physica Scripta94(2019)055403, Eqs4,5,9 (R7 adopted source). Source history alternatives and actual Puchwein ancillary rates are separately in radiation/.

\clearpage

# R8 radiation sources: theory, candidates, and executed adapters

Access date: 2026-10-14. Scope: stellar/AGN source histories and primordial radiation initial conditions. No cosmological parameter set or source history is adopted on the user's behalf. The executed examples below are either a named public benchmark or explicit parameterized calculations.

## Outcome

Two distinct model modes are ready for use. **Endogenous-source mode** injects escaped stellar/AGN emissivity and solves the project's radiation transport. **Prescribed-background mode** supplies external UVB photoionization/heating rates as a benchmark. A single population's emissivity and its already transported UVB cannot be counted in both modes. These modes can coexist for explicitly disjoint populations or spatial domains with a documented boundary; the current small adapter deliberately supports the simpler exclusive case.

The lightweight native C adapter executes exact finite-band moments for power-law spectra/cross sections, UV luminosity-to-photon conversion, proper/comoving volume conversion, and AB luminosities. It passed **48 tests**, including independent quadrature and narrow-bin limits. Three primary Puchwein ancillary files were downloaded byte-for-byte and hashed. The fiducial 59-node HI/HeI/HeII table adapter passed **181 tests**, including all node conversions and rejection of extrapolation/double-counted source modes.

## Candidate selection and provenance

| Candidate | Verified primary source/version | Appropriate role | Admission conditions |
|---|---|---|---|
| BPASS binary/single stellar populations | [Official BPASS v2.2.1, July 2018](https://www.bpass.auckland.ac.nz/bpass-v2-2/); [v2.2 manual](https://warwick.ac.uk/fac/sci/physics/research/astro/research/catalogues/bpass/v2p2/bpassv2.2_manual_accessible.pdf); Stanway & Eldridge 2018 | Preferred intrinsic SSP spectral library; binary versus single is a controlled alternative | Fix IMF, mass normalization, metallicity, age grid, stellar-only spectrum and escape prescription. The manual normalizes ionizing output to a burst of 10^6 solar masses. Convert to per formed mass before convolution. Do not apply an extra escape fraction to an already escaped spectrum. |
| FSPS | [Author repository](https://github.com/cconroy20/fsps), README version 4.0; Conroy, Gunn & White 2009; Conroy & Gunn 2010 | Fortran alternative for stellar population sensitivity studies | Pin commit and isochrone/atmosphere choices. Disable or separately track nebular reprocessing when the project's transport/cascade owns it. This session inspected docs; it did not build FSPS. |
| Starburst99 | [Official v7.0.1 page](https://massivestars.stsci.edu/starburst99/docs/default.htm); [official PC package](https://www.stsci.edu/science/starburst99/docs/starburst99_pc.htm) | Independent massive-star/rotation alternative | Some index pages still display 7.0.0; pin actual selected archive rather than relying on index text. No package download/build was performed here. |
| UV LF + conditional escaped efficiency | Finkelstein et al. 2019, [DOI 10.3847/1538-4357/ab1ea8](https://doi.org/10.3847/1538-4357/ab1ea8); Choustikov et al., [arXiv:2405.09720v2](https://arxiv.org/abs/2405.09720v2), PHOTONIOn/JADES application | Empirical alternative or normalization constraint on intrinsic SPS source histories | Carry the LF selection, magnitude cutoff, dust convention, and joint f_esc–xi_ion dependence. A field-limited inferred history is not a universal source history. The 2019 extrapolation above observed z is a model assumption. |
| Kulkarni AGN UV LF | [Author repository, tag v3.0](https://github.com/gkulkarni/QLF/tree/v3.0) | Preferred transparent QLF reconstruction candidate; catalog, LF fits, UV emissivity and He reionization routines public | The README identifies 83,488 AGN, z=0–7.5, and tag v3.0 as reproducing the paper. Preserve UV selection, faint cutoff, spectral conversion and obscuration conventions. Python-2-era plotting/MCMC routines require an isolated compatibility adaptation. Do not inherit their hard-coded cosmology. |
| Shen et al. bolometric QLF | [arXiv:2001.02696v2](https://arxiv.org/abs/2001.02696v2), [DOI 10.1093/mnras/staa1381](https://doi.org/10.1093/mnras/staa1381), [author Bitbucket code](https://bitbucket.org/ShenXuejian/quasarlf/src/master/) | Bolometric / obscuration cross-check on the UV-selected AGN model | Paper/code location verified; live Bitbucket content retrieval timed out. Faint-end behavior at high z remains model dependent. A bolometric LF needs SED and unobscured/escaped fractions before use as an ionizing source. |
| Faucher-Giguere 2020 UV/X-ray background | [arXiv:1903.08657v2](https://arxiv.org/abs/1903.08657v2), [DOI 10.1093/mnras/staa302](https://doi.org/10.1093/mnras/staa302), [author data page](https://galaxies.northwestern.edu/uvb-fg20/) | Main external UVB comparison candidate | The author page distinguishes a 2020-10-27 update with a heating-rescaled TREECOOL version. Record original versus rescaled rates. Effective reionization rates are calibrated model inputs; they are not independent raw stellar emissivities. Data page read through Exa; binary table bundle not retrieved here. |
| Puchwein et al. UVB | [arXiv:1801.04931v1](https://arxiv.org/abs/1801.04931v1), published paper [DOI 10.1093/mnras/stz222](https://doi.org/10.1093/mnras/stz222) | **Executed prescribed-rate benchmark**, with fiducial and equivalent-equilibrium alternatives kept distinct | Actual downloaded bytes are **v1 preprint ancillary files**, whose z coverage is 0–15.1. Their identity with later published/reformatted tables is not assumed. Fiducial ionization units s^-1 and heating eV s^-1 follow the ancillary readme. |
| Haardt–Madau 2012 | [arXiv:1105.2039](https://arxiv.org/abs/1105.2039), [DOI 10.1088/0004-637X/746/2/125](https://doi.org/10.1088/0004-637X/746/2/125) | Historical UVB regression and analytic QSO emissivity comparison | Keep its absorber/source assumptions and historical cosmology attached. Do not combine its processed intensity with a second copy of its stellar/QSO emissivity. |
| Consistently reformatted UVB tables | Taira et al. 2025, [arXiv:2505.23544](https://arxiv.org/abs/2505.23544), [DOI 10.3847/2515-5172/adddae](https://doi.org/10.3847/2515-5172/adddae), [Zenodo v1.0.0](https://doi.org/10.5281/zenodo.15367103) | Useful multi-model comparison import path | The source description labels intensities in erg s^-1 cm^-2 versus energy. The transformation code must establish whether these are nu J_nu, 4pi nu J_nu or another convention before using them in rate integrals. No silent inference from a generic 'intensity' label. |
| HYREC-2 | [Author C repository](https://github.com/nanoomlee/HYREC-2), README July 2020; [arXiv:2007.14114v2](https://arxiv.org/abs/2007.14114v2), [DOI 10.1103/PhysRevD.102.083517](https://doi.org/10.1103/PhysRevD.102.083517) | Efficient standard-background recombination IC provider: x_e(z), T_m(z) | Executed the stock SWIFT reference from commit `09e8243d0e08edd3603a94dfbc445ae06cafe139` with its actual input.dat. The native output_xe.dat has z, x_e, T_m; it does not supply the full primordial spectral distribution. This is a conditional FLRW IC/regression reference. |
| CosmoSpec | Chluba & Ali-Haimoud, [arXiv:1510.03877](https://arxiv.org/abs/1510.03877) | Recombination-radiation spectrum beyond a Planck initial field | The paper's effective-conductance factorization is directly relevant to precomputation. Public code availability/build was not established in this session; this is a literature-supported provider candidate, not an executed provider. |

The practical baseline is an explicit **Planck initial photon field + matched recombination x_e,T_m IC + intrinsic BPASS source shape + a supplied LF/SFR history and escaped-efficiency model + one documented AGN LF/SED**. Puchwein-v1 prescribed rates provide an immediately available regression branch. FG20 and published Puchwein tables are comparison targets once their exact versions are acquired. This selects an implementation order, not a best-fit cosmology or a unique astrophysical history.

## Theoretical reduction and source contract

Let epsilon_nu^c be angle-integrated emissivity per rest-frame frequency per present-normalized comoving volume, in erg s^-1 Hz^-1 cMpc^-3. Let a_V=(V_proper/V_comoving,today)^(1/3). The proper source is

    epsilon_nu^p = epsilon_nu^c / [a_V^3 (1 Mpc in cm)^3].

The familiar (1+z)^3 factor requires z=a_V^-1-1. A directional observed redshift in Bianchi spacetime is not automatically this volume redshift. Per-absorber photoionization rates Gamma in s^-1 do not acquire an extra volume factor. If an ODE evolves in a time variable other than local seconds, its clock Jacobian is applied separately.

For an SSP library l_nu(tau,Z) per formed stellar mass,

    epsilon_nu^c(t) = integral dZ integral_0^t d tau
        psi^c(t-tau,Z) l_nu(tau,Z) f_esc(nu,t,tau,Z).

psi has mass/(time comoving volume), l_nu luminosity/(frequency formed mass), and d tau uses the same time unit as psi. A BPASS file per 10^6 solar masses must therefore be divided by 10^6; a file in solar luminosities per Angstrom must first be converted with the file's L_sun convention and d lambda/d nu. Converting L_lambda per Angstrom to per cm requires a factor 10^8 before multiplying by lambda_cm^2/c. A nebular spectrum is separately identified, because its absorbed ionizing energy has already been redistributed.

The empirical photon source can instead be expressed as

    dot n_gamma^c(z) = integral dM Phi(M,z) L_UV(M)
                      <f_esc xi_ion | M,z>.

The conditional product is fundamental: replacing it by <f_esc><xi_ion> discards covariance. L_UV must have the same dust/intrinsic convention as the denominator defining xi_ion. LF distances and volumes were inferred within a source cosmology; adopting them into a different geometry requires a corresponding luminosity/volume reanalysis or an explicitly conditional source model.

**Precomputation:** collapse the frequency dimension once per SSP age, metallicity, escape basis, and photon group. Store photon production q_g, energy u_g, and required reaction-weighted moments. Runtime then performs weighted sums/convolution rather than repeated spectral integrals. Direct convolution of a modest age grid is cheap; FFT convolution is available only for a uniform time grid and time-translation-invariant kernel. Expanding a time-dependent escape fraction in a small fixed spectral basis keeps this reduction useful. Spectral hardening exp[-sum_i N_i sigma_i(nu)] introduces column dependence; either tabulate the required columns or retain frequency bins. A few unattenuated moments alone do not close arbitrary hardened spectra.

**Primary analytic moments executed:** for J_nu=J0 (nu/nu0)^(-alpha), sigma_nu=sigma0 (nu/nu0)^(-s), and x=nu/nu0 in [1,R], define I(q;a,b)=integral_a^b x^(q-1)dx. Then

    Gamma = 4 pi J0 sigma0/h * I(-alpha-s;1,R),
    H = 4 pi J0 sigma0 nu0 * [I(1-alpha-s;1,R)-I(-alpha-s;1,R)],
    dot n_gamma^c = epsilon_nu0^c/h * I(-alpha;1,R),
    n_gamma^p = 4 pi J0/(c h) * I(-alpha;1,R).

H is photoelectron heating per absorber in erg/s. It excludes secondary-electron redistribution, ionization threshold storage, and unrelated heating. The code uses expm1 and a logarithmic-coordinate series to preserve narrow-bin excess energy. At alpha+s>1 and R=infinity, H/Gamma=h nu0/(alpha+s-1), a useful closed-form check. The approximation sigma proportional to nu^-s is declared; the exact Stobbe cross section can replace it via tabulated moments from the atomic lane.

## Initial radiation

In the declared initial observer frame, the simplest CMB IC is f(E)=1/[exp(E/(k_B T_init))-1], per polarization mode, with unpolarized isotropic density matrix. The energy density includes both polarizations. Under collisionless Bianchi propagation the occupation is transported along the actual energy/direction characteristics. An initially Planckian field can have a direction-dependent temperature afterward; imposing one scalar T0(1+z_obs) at every later event would erase the anisotropic transport. HYREC's standard x_e,T_m is a reference IC conditional on its earlier expansion/radiation history. A requested BBN-through-recombination Bianchi history must propagate its own coupled radiation and chemistry to the matching surface. Recombination distortion, nuclear-decay radiation and nonthermal seed populations are separately normalized additions and must be included only once.

## Executed results

For a declared illustrative J0=10^-21 erg s^-1 cm^-2 Hz^-1 sr^-1, alpha=1.5, s=3, sigma0=6.3e-18 cm^2, h nu0=13.6 eV, R=4, the C adapter gives

    Gamma_HI = 2.6499202835113664e-12 s^-1,
    H_HI = 1.6061505550541845e-23 erg s^-1 per HI,
    H/Gamma = 3.7830584288509916 eV.

These are theoretical moments of that explicit radiation/cross-section model, not an inferred astrophysical history. For rho_UV=10^26 erg s^-1 Hz^-1 cMpc^-3, xi_ion=10^25.2 Hz erg^-1, f_esc=0.1, the escaped emissivity is 1.5848931924611113e50 photons s^-1 cMpc^-3. At the explicitly FLRW volume scale a_V=1/7 it is 1.850301429605531e-21 photons s^-1 cm^-3 proper.

The directly downloaded Puchwein-v1 table yields:

| Original z node | Gamma_HI [s^-1] | HI heating [erg s^-1 per HI] | H_HI/Gamma_HI [eV] |
|---|---:|---:|---:|
| 0.00 | 6.06e-14 | 3.6529627e-25 | 3.76237624 |
| 3.02 | 1.02e-12 | 5.9120318e-24 | 3.61764706 |
| 5.81 | 6.09e-13 | 3.6689845e-24 | 3.76026273 |
| 6.14 | 3.11e-15 | 2.9800485e-26 | 5.98070740 |
| 9.99 | 5.66e-17 | 5.7357923e-28 | 6.32508834 |

These are tabulated model inputs converted to CGS, not a fresh microscopic reconstruction. Their sharp change across reionization requires retaining original nodes. The supplied positive log-linear interpolator is an explicit interpolation choice, not a certified continuous reconstruction. The last Compton column is not consumed because its normalization is not established by the short ancillary README.

## Local Codex handoff

1. Acquire only selected BPASS spectral/ionizing products for the fixed IMF and metallicity grid; do not download the full individual stellar-model library by default. The official starter kit advertises 1.5 GB for fiducial outputs and 8.2 GB for all stellar models, making selective acquisition useful. Pin downloaded SHA-256, original units and mass normalization.
2. Precompute source moments in C/Fortran, check photon/energy sums against direct frequency integration, and use reduced source vectors in the cosmological solver. This is principally data preparation and normally should run locally without a large parallel allocation.
3. Refit AGN/galaxy LF posteriors only if the scientific question requires a changed dataset/cosmology. Independent posterior samples, stellar age/metallicity spectra, and independent sightlines are parallel tasks. Do not launch a full population-synthesis evolution grid when a released SSP library suffices.
4. Pin QLF v3.0 and adapt small numeric functions independently of legacy plotting dependencies. Downloaded e912_18_2.npz is retained as candidate evidence only: its `down` values exceed `median` and `up` in sampled inspection, while active rtg2.py/qhe.py instead load e1450_18.npz. Establish generating code and quantile semantics before using cached uncertainty columns. Sorting labels numerically would conceal this provenance problem.
5. The stock HYREC-2 SWIFT IC run has now been executed here (see HYREC_EXECUTION.md); local Codex should reuse its regression output and only rerun for explicitly changed inputs. The substantial task is extending radiative transfer to the requested anisotropic history. CosmoSpec provider availability must be checked before scheduling its execution.
6. Required return: source manifest, selected LF/SFR/escape model, spectrum/group moment tables, proper-volume/clock conventions, source ownership, residual spectral-integration errors, and outputs with interpolation/parameter uncertainty separate from microscopic error.

## Files and checks

- `source_adapter.c`, `test_source_adapter.py`, `SOURCE_ADAPTER_RESULTS.json`: native formulas, build and 48 checks.
- `uvb_table_adapter.py`, `PUBLIC_UVB_RESULTS.json`: version-locked public benchmark and 181 checks.
- `puchwein_v1_*`, `PUBLIC_DATA_RECEIPT.json`: byte-preserved original ancillary tables/readme.
- `qlf_v3_*`, `QLF_DATA_RECEIPT.json`: downloaded author code/cache; **not executed as production source provider**.
- `SEARCH_EVIDENCE.json`: Exa and SciSpace search responses plus inspected official project pages.

No graph digitization was used. The public table import is explicitly distinguished from new theoretical source moments. The documented wrappers are implementation-verified; selecting an astrophysical history and admitting it to the Bianchi network remains an explicit model decision.

Follow-up native execution: HYREC_EXECUTION.md documents the actual stock recombination run, upstream input values, 8,000 output nodes, measured runtime and seven checks.

\clearpage

# Executed HYREC-2 primordial recombination reference

On 2026-10-14, the author repository https://github.com/nanoomlee/HYREC-2 was fetched and its HEAD pinned to **09e8243d0e08edd3603a94dfbc445ae06cafe139**. Both git ls-remote and the GitHub commit response returned this identity. `history.h`, `hydrogen.h`, `history.c`, `hyrec.c`, README and the actual `input.dat` were inspected. In particular the numerical defaults differ from some illustrative comments in input.dat; the actual leading numerical values were used.

The stock **SWIFT** mode was compiled using Ubuntu GCC 13.3.0 with `-O3`, then executed once in an isolated run directory. The precompiled binary in the author's repository was not executed. Compilation took 0.9725 s; execution including writing its 8,000-row history took 0.00980 s on this runtime. These are one-run wall times, not a throughput benchmark or the paper's recurrence timing.

## Exact reference parameters

| Parameter | Actual upstream input |
|---|---:|
| h | 0.6735837 |
| T0 | 2.7255 K |
| Omega_b | 0.04941428 |
| Omega_cb (baryons + CDM) | 0.31242079 |
| Omega_k | 0 |
| w0, wa | -1, 0 |
| Massive neutrinos | 1 species, 0.06 eV |
| N_eff | 3.046 |
| Helium mass fraction | 0.245 |
| alpha and electron-mass ratios | 1, 1 |
| Extra annihilation/decay injection, PBH fraction | 0 |

The provider's number conversion is `fHe=YHe/(1-YHe)/3.97153` and `nH0=11.223846333047e-6*(Omega_b*h*h)*(1-YHe)` cm^-3. Thus fHe=0.08170738009237703 and nH0=1.8998716926411988e-7 cm^-3. The output electron fraction is n_e/n_H, not n_e/n_b and not a helium-normalized fraction.

## Reusable initial values

These are native printed output nodes, with Tgamma=T0(1+z) for this declared FLRW reference.

| z | x_e=n_e/n_H | T_m [K] | T_gamma [K] | n_e [cm^-3] |
|---|---:|---:|---:|---:|
| 1100 | 0.14473827 | 3000.7425457 | 3000.7755 | 36.700298 |
| 200 | 0.0003364307 | 466.28758207 | 547.8255 | 0.00051904864 |
| 100 | 0.00027184599 | 167.61526798 | 275.2755 | 5.3212213e-05 |
| 50 | 0.00023726021 | 50.644524 | 139.0005 | 5.9794291e-06 |
| 30 | 0.00022000333 | 19.79978 | 84.4905 | 1.2451986e-06 |
| 20 | 0.0002092844 | 9.3009842 | 57.2355 | 3.6822987e-07 |

At low redshift this stock calculation continues the no-astrophysical-reionization solution. Consequently those late values describe the selected primordial reference; they are not predictions for the observed reionized universe. The result supplies scalar thermal/electron IC and a separately declared Planck radiation field. It does not resolve a unique 17-species charge distribution or a recombination spectral distortion. Earlier anisotropic evolution, nonthermal radiation, or different BBN composition requires a matched history.

## Execution evidence and reproduction

- `hyrec_reference_run/input.dat`: exact original input, SHA-256 `6353f6586d3cbbdff7579f1c7b9771bb68737a6bf66c8621b29a887dabd7c7f7`.
- `hyrec_reference_run/output_xe.dat`: 8,000 descending integer-z nodes, z=8000 to 1, SHA-256 `1ac2ddad6aa0e3c4080883c71479e2e398669468e4813075ec61bca86b7afc40`.
- `HYREC_09e8243_SOURCE.tar`: exact git archive of the pinned tree, SHA-256 `853b356b233744ed85924d652b7808822201d46453d686ff6c444e9a4b731631`.
- `hyrec_reference_run/RUN_RECEIPT.json`: compiler command, return codes, times and hashes.
- `hyrec_reference_run/HYREC_REFERENCE_RESULTS.json`: parameters, seven executed checks and 11 reference nodes.
- `HYREC_GITHUB_HEAD_RECEIPT.json`: upstream pin metadata.

To reproduce in a fresh directory, extract the source archive, compile the six C files below, and run with the included input.dat in the same directory as its atomic tables:

```sh
cc -O3 hyrectools.c helium.c hydrogen.c history.c energy_injection.c hyrec.c -lm -o hyrec_r8
./hyrec_r8 < input.dat
```

Actual checks passed: 8,000 rows; descending unit z spacing; finite outputs; positive x_e and T_m; x_e below the fully ionized H/He ceiling; initial T_m matches Tgamma; residual late x_e remains below 10^-3 without astrophysical sources. These establish build/execution and basic physical sanity for the reference. They do not replace independent HYREC accuracy tests, and no convergence or broad cosmology scan was run.

The scientific sources remain Lee & Ali-Haimoud, PRD 102, 083517 (2020), https://doi.org/10.1103/PhysRevD.102.083517, and Ali-Haimoud & Hirata, PRD 83, 043513 (2011), https://doi.org/10.1103/PhysRevD.83.043513.

\clearpage

# Symbolic checks, initial radiation and reproducibility

## Wolfram and xAct: executed identities

Wolfram Language 15.0.1 executed seven groups of scalar identities: absorption completeness, the backward mean-time equation, zeroth and first resolvent moments, the photonuclear change of variables, the target-rest threshold, and the inverse spin factor. Every residual simplified to zero. These identities verify the declared formulas; they do not supply missing physical amplitudes.

xAct/xTensor 1.3.0 was actually loaded and used for seven tensor identities. With signature $(-,+,+,+)$, let $u^a u_a=-1$, $k^a k_a=0$, $u^a b_a=u^a j_a=0$, and define

\[
q_a=-u_a+b_a,\qquad D=-u_a k^a,\qquad A=q_a k^a=D+b_a k^a,
\]
\[
J^a=\frac{cN}{V}u^a+j^a,\qquad h^a{}_b=\delta^a{}_b+u^a u_b.
\]

The retained age convention obeys $u^a q_a=1$. The absorption column in the same clock is

\[
\mathcal C=\int\frac{-k_aJ^a}{A}\,d\theta
=\int\left(\frac{cDN}{VA}-\frac{k_a j^a}{A}\right)d\theta.
\]

The Doppler factor $D$ and the age Jacobian $A$ coincide only under the corresponding additional condition. For an energy-momentum source $S^a=P u^a+F^a$ with $u_aF^a=0$, the checked projections give $-u_a S^a=P$ and $h^a{}_b S^b=F^a$. These are algebraic interface identities; they do not solve Einstein, transfer or chemistry equations.

The actual submitted xAct script and observed output are retained. Its unqualified `$Version` printed the xTensor version because of symbol-context shadowing. The scalar call independently establishes the Wolfram version. The replay body uses ``System`$Version``; that metadata-only correction is not represented as a second tensor execution. The xAct archive SHA-256 is `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`.

## Executed Planck reference rates

The reused R7 logarithmic Planck-folding provider was newly evaluated for $Z=1,2,3$ at $z=0,5,10,20,30,100,1000$, giving 21 cases. The explicit reference is $T_\gamma=2.7255(1+z)$ K, consistent with the FIRAS reference of Fixsen (2009), [DOI 10.1088/0004-637X/707/2/916](https://doi.org/10.1088/0004-637X/707/2/916). The 128/256-order refinements agree. Logarithmic output preserves physically tiny rates without reporting a floating-point underflow as an exact zero.

At $z=20$, the model's $\log_{10}(\Gamma/\mathrm{s}^{-1})$ is approximately $-1191.67004$ for H I, $-4785.14896$ for He II and $-10774.93185$ for Li III. These are conditional Planck-only, ground-state hydrogenic rates. They establish neither a stellar ionization history nor the general Bianchi temperature-redshift relation. The stock HYREC reference supplies its matched FLRW $x_e,T_m$ history separately; its density parameters remain attached to its input file.

## Reproduction and interpretation of checks

Native numerical kernels use C11 and libm. Independent verification uses Python 3.12, NumPy 2.3.5, SciPy 1.17.0 and, where needed, mpmath 1.3.0. Each module retains its commands, raw tables, timing and check receipts. `run_lightweight.py --list` prints the executable module registry; it does not launch heavy campaigns. The HYREC source is distributed as a pinned author-source archive with build/run instructions and actual input/output.

The complete source archive also includes the 65-row historical gap crosswalk, cross-thread identities, independent numerical review and publication review, symbolic replay scripts, and local implementation contracts. No numerical convergence test is relabelled as an outward-rounded proof or an uncertainty on the physical Hamiltonian. No complete historical multi-part gap is closed by this bounded update.

\clearpage

# Concrete code shipped with this handoff

This package includes 29 selected byte-identical R6 source/theory/input files (204366 bytes at intake), with original path and SHA256 in `vendor_r6/PROVENANCE.json`. It is not only a launcher. No private raw article PDFs or compiler binaries are included in that intake manifest.

| Available object | Exact package path | Actual readiness |
|---|---|---|
| Native displaced-Gaussian Coulomb donor | `vendor_r6/code/lowt/vendor/r31a/hybrid12_wide_h_v2.cpp`, continuation.hpp | Compiled again in this R8 relocation; four 1–4 electron matrix-element checks passed |
| Few-electron spatial ECG matrix wrapper | `vendor_r6/code/lowt/ecg_matrix.py` | Executable matrix elements; antisymmetric physical-basis optimization still required |
| Molecular input generator | `vendor_r6/code/lowt/generate_molecular_inputs.py` | Actual finite-AO-basis PySCF ROHF/FCI generator with states, BO energies, transition dipoles and overlap links; PySCF absent on this host |
| Low-temperature scattering primitives | `vendor_r6/code/lowt/kernels.py` | Existing propagation/matching/normalization code; needs real molecular inputs |
| Correlated projection/response/cascade operators | `vendor_r6/code/correlated_atomic/operators.py` | Real operators requiring physical matrices; small fixtures are not Li/daughter data |
| Nuclear kernels and donor model | `vendor_r6/code/nuclear/nuclear_kernels.py`, `vendor/r5_be7_kinetics.py` | Existing selected-model kernels retained, not relabeled as new precision posterior |
| Nuclear observation preparation | `vendor_r6/code/nuclear/prepare_external.py` | Executed in R8: 30 recovered tabulated observations and five algorithm contracts written |
| Nuclear observation inputs | `vendor_r6/evidence/nuclear/inputs/BRUNE1994_BRANCH_RESOLVED.csv`, `MUNCH2020_LI7_TABLE3.csv`, `R5_DONOR_BBN.json` | Existing numerical table facts/BBN donor with R6 provenance; missing shared cross-covariance and detector response stay null |
| Prepared nuclear output | `vendor_r6/evidence/nuclear/external/LI7_OBSERVATION_DECK.json`, `EXECUTION_CONTRACT.json` | Real data and explicitly unexecuted fit/response/background tasks |

Rebuild the native donor on the destination platform, from `vendor_r6/`:

```bash
python3 code/lowt/check_native_ecg.py --source code/lowt/vendor/r31a/hybrid12_wide_h_v2.cpp
```

R8's relocated build used g++ and returned exit zero. Maximum reported relative Coulomb difference against the analytic reference was 1.3373831832802231e-16; Hermiticity residuals were zero at the sampled matrices. This is a portability/implementation check of an existing kernel, not a newly converged lithium or molecular potential. The `.so` is platform-specific and should be rebuilt, not treated as an input source.

With PySCF actually installed and recorded, the generator is directly callable. Its arguments select a physical electronic model explicitly; the following is a **finite-basis input-generation pilot**, not a final LiH+ potential:

```bash
python3 code/lowt/generate_molecular_inputs.py --atoms Li H --charge 1 --spin 1 --basis aug-cc-pvdz --rmin 1.5 --rmax 30 --points 8 --roots 2 --threads 1 --max-memory-mb 4000 --output pilot_LiHplus.npz
```

Use this pilot only after checking the molecular charge, spin, symmetry and asymptotic channels of the requested reaction. FCI dimension grows combinatorially. The generator enforces SCF/FCI convergence and spin purity, writes CI/MO data and subspace leakage, and labels remaining channel assignment, finite-mass/HFS and basis/radial convergence. Electronic state tracking across avoided crossings needs the reported overlaps; interpolation must not silently change channel identity. Increase points and basis only after measured wall/RAM. The local Codex task is to review and adapt this real generator, generate the actual physical curves, then bind them to the existing coupled-channel primitives.

`prepare_external.py` has already been executed in the relocated tree; rerun only if observation inputs change. Its nullable response/covariance fields are required missing experimental information, not zero-error assumptions. Current unsupported microscopic jobs in `jobs.json` remain blocked because complete physical decks/executables are not yet bound, while these lower-level kernels/generators are available immediately.

\clearpage

# Reionization R8: local implementation and heavy calculation handoff

Status: **package prepared; local Codex has not executed these calculations**. Start from the R8 report and `integration/CURRENT_SNAPSHOTS.json`. Preserve existing working trees. Read each relevant repository's current AGENTS and actual code before adapting it. The user authorizes this work and external backup/publication; this package does not authorize an unreviewed main merge or change the scientific acceptance scope.

## Reuse first, then select the expensive calculation

R8's native lightweight outputs and tests are the first input; do not rerun the R7 or cross-thread scientific suites by default. Recover complete source archives only where the adapter needs code absent from the read scientific report. Exact archive identities and observed remote entrypoints are in the integration snapshots/reports. The GitHub research entries sometimes publish a substantive report rather than the full executable source. A report URL is not an executable provider.

The current sources are HE R10/PR45, HH PHYS29/PR62, CR moving cluster/PR56 and published REI OBSERVER15 R7 at PR115 commit `8bf8e3c18d607334614cfea734f9b10961fbd4d4`. The earlier Library R7 proof is a separately retained variant, as detailed in integration/DELTA_AND_REUSE.md. Specifically, HH's Coulomb thermal integral is already numerically computed. Its next remaining numerical obligation is finite quadrature/all-roundoff certification; do not regenerate its physical result merely to match an obsolete readiness table. CR's seeded moving result uses a lifted static reference and a new defect bound, so a full moving ODE is a distinct computation. REI's exact-real GL32 baseline now has source-node error; consuming the same cubic avoids a redundant interpolation term.

On the user's 12-core/24-thread, 64-GB workstation, start with two independent single-thread pilots and a total 48-GB scheduling cap. Discover actual CPU/RAM before using these defaults. Do not assume the GPU accelerates Fortran scattering or a dense generalized eigensolver. Cap BLAS/OpenMP separately to avoid nested oversubscription. For each real model, benchmark one small representative block, record wall time and peak memory, then choose workers from measured memory plus headroom. The runner's sampled RSS covers the main process only; MPI aggregate memory needs scheduler/cgroup measurement.

## Execute the prepared runner

```bash
python3 local_codex/run_jobs.py preflight --out local_runs
python3 local_codex/run_jobs.py benchmark --out local_runs --workers 2 --threads 12 --memory-mb 49152
python3 local_codex/run_jobs.py run --out local_runs --workers 2 --threads 12 --memory-mb 49152 --max-seconds 14400
```

Initially preflight returns blocked because actual heavy providers were not supplied. This is the truthful state, not a failed physics calculation. Follow PROVIDER_CONTRACT.md to bind actual executable SHA, source commit and input-file SHA for each job. `run` benchmarks each partition before running it, limits concurrency/threads/declared memory/wall time, writes logs and atomic receipts, and reuses successful matching receipts. The initial `selected_model` partition is a scheduling label, not a scientific input deck. Replace it with real independent symmetry/energy partitions once chosen. A local wrapper may translate this interface into an existing program's native input format, but must not silently invent Hamiltonians, potential curves, external radiation or undocumented defaults.

## Implement remaining providers

### Li bound and continuum: `li_bound` then `li_continuum`

Read BASS_HE and the R7 microscopic-reconstruction chapter. Reuse radial integrals, ECG matrices and symmetry routines actually present, not assumed capabilities. Construct balanced neutral Li and Li+ targets in common isotope/mass conventions. The finite-mass nonrelativistic target Hamiltonian is

H=sum_i[p_i²/(2 mu)-Z e²/(4 pi eps0 r_i)]+sum_i<j[e²/(4 pi eps0 r_ij)+p_i.p_j/M].

Separate L,S,parity blocks and antisymmetrize; solve H c=E S c with explicit overlap conditioning. Retain threshold errors between parent and all daughter targets, not just absolute parent energy. Converge basis scale/count and core/valence balance. A historical 829-configuration target is a reproducibility target only if its actual configuration list is recovered; an independently converged target is a different, scientifically usable reconstruction.

For the continuum, first compute requested response moments using block Lanczos/resolvent or exterior-complex-scaled driven equations if those preserve the chosen observable. Inclusive dipole response alone does not supply exclusive double-ionization or electron-energy/angle distributions. Use a source-specific CCC/R-matrix/close-coupling implementation for those. Construct the Coulomb asymptotics and exchange explicitly. A public method description is not evidence that the native CCC code/deck is available. If source access is missing, mark `missing_provider` and proceed with independent bound-state work.

Parallelize by irreducible symmetry and incident-energy panels; reuse each target factorization and dipole RHS. Accumulate number, energy and response-weighted moments together. Locate resonances adaptively, with a tail and interpolation estimate. Checks: normalized bound states, overlap-spectrum conditioning, threshold convergence, Coulomb normalization, flux/unitarity, positivity, length/velocity gauge comparison at converged basis, shared forward/reverse rates. The full correlated model requires these checks; a gauge difference alone is not a rigorous error bound.

### Molecular low-temperature rates: `molecular_lowT`

Generate or recover charge/symmetry-specific Li–H, Li–He, T/H, T/D potential curves, derivative couplings, asymptotic thresholds, radiative dipoles and hyperfine contacts. These are required physics inputs. Isotope changes enter reduced masses and finite-mass/adiabatic corrections; a universal mass-rescaling factor is insufficient near a pole.

For each J/parity/channel block solve the coupled radial system using renormalized Numerov, log-derivative propagation or an R-matrix method with long-range asymptotic matching. Reuse the common electronic curves. Separate threshold pole searches from thermal convolution. Compute S(E), channel-resolved cross sections, then

k(T)=sqrt(8/(pi mu)) (kB T)^(-3/2) int E sigma(E) exp[-E/(kB T)] dE.

Use x=E/(kB T), split thresholds/resonances, and compute all requested temperatures from a common adaptive energy representation. The Wigner threshold law can guide a bounded extrapolation only after the physical long-range class and absence/location of nearby poles are established. Radiative channels need continuum dipoles and photon energy; an elastic/charge-exchange S matrix does not determine them. Verify radial/domain/energy convergence, unitary open-channel flux in the nonabsorbing case, reciprocity with degeneracies, and bound-plus-continuum normalization. Return actual 1, 6.11, 10 K values only for a converged physical model; retain the full temperature grid used in reionization.

### Correlated daughters: `daughter_correlated`

Use the same parent wavefunction and charge/isotope convention as the bound calculation. Define exclusive asymptotic daughter channels by orthogonal projectors or a controlled POVM; raw overlaps in a nonorthogonal Gram basis are not exclusive probabilities. Construct amplitudes with the nuclear recoil/weak operator and electron correlation, then evolve or project to asymptotic channels. Retain missing norm as unresolved continuum until convergence, rather than renormalize it away.

For additive mean observables in a fixed external bath, compute sufficient one-particle marginals and conditional first moments before attempting the full joint grid. This can remove several dimensions. For coincidence observables, eventwise conservation or nonlinear event feedback, retain the common nuclear/electronic/photon event measure. Use daughter-rest photon energy -u_d.k (with the agreed energy-valued four-momentum convention), not the COM photon energy as the target threshold. Verify total probability including continuum, baryon/charge/energy/momentum event ledgers, projectile recoil conventions and the time/domain plateau of channel projectors. The one-electron sudden/cusp result or independent-electron determinant is a comparison model; neither becomes correlated two-/three-electron data by declaration.

### Precision nuclear response: `nuclear_precision`

Keep the existing np capture result with its actual EFT order and thermal anchor. A precision update requires a Hamiltonian/current scheme, shared low-energy constants and their covariance, detector response and normalization nuisances. Build direct and inverse reactions from the same amplitude and spin/phase-space factors. Do not sample tabulated temperatures independently. For A=3,4 exclusive channels or Li7 near-threshold reactions, obtain the continuum amplitude or fit a specified R-matrix/EFT model to actual data. Parallelize channel/energy solves; compute thermal kernels and uncertainty derivatives cheaply from retained amplitudes. Report theory truncation separately from quadrature and fit error.

### Charge/cascade reduction: `atomic_charge_cascade`

Use block elimination only when the fast block is transient/invertible and its relaxation is short compared with rate/source/expansion variation. For a column generator partitioned slow/fast, Qeff=Qss-Qsf Qff^(-1) Qfs follows a quasisteady approximation; preserve the initial layer or bound it. Solve sparse linear systems rather than form an inverse. Check positivity, exact particle/charge ledgers and whether eliminating radiative states double counts explicit transport. Test the reduced model against a modest full level model on the actual radiation histories. Cold/high-n dissolution and RR/DR branching need physical rates; a hydrogenic 1s kernel cannot supply all multi-electron levels.

### Full BBN to 17-state interface: `bbn17`

The output registry recovered from R7 is [n,H0,H+,D0,D+,T0,T+,He3_0,He3_+,He3_2+,He4_0,He4_+,He4_2+,Li7_0,Li7_+,Li7_2+,Li7_3+], abundance per baryon in the common-rest specialization. Internal Be donors, excited levels, negative ions, molecules, photons and nonthermal particles must be retained where needed; output dimension 17 does not close the internal dynamics.

Carry one finite BBN checkpoint with a,t,Tgamma,Tnu, composition, radiation and covariance into the late solver. Advance the same clock t(a)=tB+int da/(aH). Use one ionic mass ledger: M_q c²=M_0 c²-q m_e c²+sum_{j<q} I_j. Include composition-dependent rest energy once in the background and reaction release once in energy exchange. Baryon conservation uses A^T nu=0, not unweighted Markov column sums. Charge-state transitions of one tagged nucleus may use a conservative generator; nuclear multiplicity-changing events do not generally do so.

Reuse the conditional Be survival result only within its rate/cosmology/no-new-Be assumptions. Extend hyperfine/continuum electron capture and charge-dependent tritium decay where required. Do not renormalize the retained 17-vector to erase excluded nuclei. Use ancestry bounds for excluded channels if they meet the selected observable budget. Propagate a shared parameter sample through nuclear rates, BBN, atomic evolution and reionization; use tangent equations for a smooth low-dimensional response and sample branch/pole/non-Gaussian uncertainties explicitly.

### Full transport and source histories: `full_transport`

First complete a separate baseline H/He calculation using the selected external histories from R8 source research; it need not wait for all trace-species tasks. For the full network, bind stellar/quasar emissivity, escape fraction, spectral normalization, angular measure and initial radiation from named models. Homogeneous isotropic source histories are a controlled baseline, not measured anisotropic Bianchi data. Use conservative spectral transport, distinguish Q_V from Q_M, preserve photon storage and redshift boundary flux, and apply event/source ownership once. Only after binding actual clocks/currents/observer boundaries should the HE/REI adapters consume the source.

## Return exactly what was run

Return model/deck and executable identities; compiler/library versions; per-partition timing, memory, exit status and logs; raw observables and convergence series; retained uncertainty components; source/rate validity domain; failed cases and cause; and the next dependency. Save a checkpoint after each independent block. Distinguish implementation-verified, numerically checked, physically calibrated and unresolved. A prepared job, a passed runner test and a completed physical calculation are three different statuses. Do not claim the original unpublished author arrays have been recovered merely because an independent theoretical reconstruction converged.

The four historical identity gaps G02.11/G06.04/G08.11/G08.12 require original data if exact historical identity is the goal. The independent physics can proceed without that identity, with its own provenance. No amount of heavy execution reconstructs an author's exact unpublished coefficients uniquely from a paper alone.

\clearpage

# R8 independent scientific and code review

Reviewed 2026-10-14. This is an independent agent review of selected physical normalizations and new native kernels, with direct calculations. It is not external scientific peer review, an interval certificate, or a review of the full cosmological production system.

## Scope and outcome

The reviewed hydrogenic E1/cascade, sudden one-electron daughter, nuclear inverse-kinematics, and spectral-moment formulas are internally consistent within their declared approximations. No unresolved normalization defect was found in the selected checks. The physical-model and uncomputed-channel qualifications below are part of that conclusion.

The reviewer executed 24 new checks in `independent_checks.py` and three additional 40-digit Coulomb-wave integrals in `daughter_radial_review.py`. The former compare native tables with independent adaptive radial quadrature, native angular factors with analytic angular factors, the inverse nuclear rate with a direct photon-energy integral, and source rates with integrals in physical frequency. The largest recorded numerical discrepancy was 1.9984e-15. The three new Coulomb points, chosen outside the provider's direct-wave test grid, agree in relative terms to better than 6e-41 at 40-digit working precision. These are numerical comparisons, not rigorous floating-point bounds.

The first attempted daughter integral encountered an environment failure: `mpmath` was not installed on the default Python path. It was resolved using the author's local `daughter/.deps` installation, without changing scientific tolerances or equations.

## Daughter continuum and bound-tail normalization

Let the initial radial state be `u_i(r)=2 a^(3/2) r exp(-a r)`, the final Coulomb strength be `b`, and `rho=b/a>0`. The continuum radial wave `u_k=sqrt(2/pi) F_0(-b/k,kr)` is normalized to `delta(k-k')`. For `x=k/a`, direct integration of this wave with the initial state gives the implemented probability density

\[
 f(x)=\frac{64\rho(1-\rho)^2x}{(1+x^2)^4}
 \frac{\exp[-4\rho\arctan(x)/x]}{1-\exp(-2\pi\rho/x)}.
\]

The independent direct-wave points were `(rho,x)=(0.75, 0.7),(2.5, 0.45),(2.5, 2.3)`. This checks the continuum normalization independently of complementing the bound sum. At `rho=1`, the entire continuum vanishes by orthogonality. Its large-x behavior is `f(x)~32(1-rho)^2/(pi*x^6)`, making the zeroth, first and second energy moments integrable; the third energy moment diverges in the point-Coulomb sudden model. A request for additional energy moments must therefore not extend the loop over moments without examining convergence.

For `n>rho` the exact bound probability can be written

\[
 P_n=C n^{-3}\exp g_n,\quad C=64\rho^3(1-\rho)^2e^{-4\rho},
\]
\[
 g_n=2n\log\frac{1-\rho/n}{1+\rho/n}-4\log(1-\rho^2/n^2)+4\rho.
\]

Using the convergent logarithm series gives

\[
 -\frac{4\rho^3}{3(n^2-\rho^2)}\leq g_n
 \leq\frac{4\rho^2}{n^2-\rho^2}.
\]

Together with `1/[2(N+1)^2] <= sum_(n>N)n^-3 <= 1/(2N^2)`, this yields the implemented finite-n tail bounds for `N+1>rho`. The hard-coded physical test ratios satisfy that condition. Floating-point evaluation is separate from this analytic truncation bound.

With `K=hbar^2 a^2/(2 mu_final)`, applying the final Hamiltonian directly to the initial state gives

\[
 H_f\psi_i=K[-1+2(1-\rho)/(ar)]\psi_i,
\]
\[
 \langle H_f\rangle/K=1-2\rho,\qquad
 \langle H_f^2\rangle/K^2=1-4(1-\rho)+8(1-\rho)^2.
\]

These independently reproduce the two reported spectral sum rules. A finite bound-state tail plus exact continuum is a complete spectral resolution for this one-electron sudden Hamiltonian. Absolute physical beta-decay branching additionally requires the nuclear phase-space weight, recoil, and final-state interactions. Finite-mass use requires consistent `a`, `b`, and final energy unit `K`.

## Hydrogenic E1 angular and mass factors

For nuclear mass `M`, electron mass `m_e`, and relative coordinate `r=r_e-r_N`, the electric dipole is

\[
 \mathbf D=e(Z-1)\mathbf R-e\frac{M+Zm_e}{M+m_e}\mathbf r.
\]

Consequently the internal transition has effective dipole magnitude `e_eff=e(M+Z m_e)/(M+m_e)`. With reduced mass `mu`, frequencies scale as `mu Z^2`, lengths as `1/(mu Z)`, and the spontaneous E1 rates therefore scale as

\[
 A/A_{H,\infty}=(\mu/m_e)Z^4(e_{\rm eff}/e)^2.
\]

The implemented factor agrees. The unpolarized upper-l angular factor is `max(l,l')/(2l+1)` for `|l-l'|=1`. The independent checks extract this factor from output A, frequency, and radial moments for seven transitions. Their radial integrals were recomputed with adaptive infinite-domain quadrature, distinct from the native finite Gauss–Laguerre rule.

The finite cascade includes all allowed downward E1 transitions from each included level, so no upward/high-n completion is needed for a cascade starting in a supplied level at `n<=nmax` in the spontaneous-only model. Population injected into `n>nmax`, continuum recombination, collisions, absorption, and stimulated transitions require additional input. The `2s` state remains a terminal metastable state; mean cascade delay and emitted-energy totals must keep that meaning. Atomic translational photon recoil, fine structure, QED and finite nuclear size are outside the Coulomb energy formula.

## Nuclear inverse rate

For unpolarized distinguishable neutron and proton initial particles, `g_n g_p/(g_d g_gamma)=4/6=2/3`. With equal nucleon masses `M`, deuteron mass `M_d=2M-Q`, and `W=2M+E`, detailed balance gives

\[
 \sigma_{\gamma d}=(2/3)(p^2/k_\gamma^2)\sigma_{np},\quad
 p^2=ME+E^2/4,\quad k_\gamma=\epsilon_\gamma M_d/W.
\]

Here masses and momenta use energy units within the MeV kinematic adapter. The stationary-target threshold is `Q+Q^2/(2M_d)`. At photon energy `epsilon_gamma=threshold+delta`, an independently useful identity is

\[
 p^2=M_d\delta/2,\qquad
 E=\frac{2M_d\delta}{\sqrt{4M^2+2M_d\delta}+2M}.
\]

The reviewer used these identities to integrate `epsilon_gamma^2 sigma_(gamma d)` directly in `u=delta/(k_B T)`, comparing with the native `y=sqrt(u)` quadrature. Four temperatures from `1e-3` to `1e8 K` agree within 3e-10 in log-prefactor (observed errors at machine precision).

The exact two-body kinematics are attached to a historical nonrelativistic equal-mass capture model. This does not supply relativistic amplitude corrections or a modern nuclear posterior. The zero-recoil Saha comparison uses spontaneous capture; Planck versus Wien corrections are exponentially small over the declared domain (`Q/k_B T>=258`), while the native inverse integral retains the Bose denominator. The exact-rest inverse and the zero-recoil thermal equilibrium identity must remain separate output fields. The author confirmed this distinction during review.

## Radiation conventions

For `J_nu=J0(nu/nu0)^(-alpha)` and `sigma=sigma0(nu/nu0)^(-s)`, direct integrals in physical frequency reproduce

\[
 \Gamma=\frac{4\pi J_0\sigma_0}{h}\int_1^R x^{-\alpha-s-1}\,dx,
\]
\[
 \mathcal H=4\pi J_0\sigma_0\nu_0\int_1^R x^{-\alpha-s-1}(x-1)\,dx.
\]

Thus heating has a factor `nu0`, ionization has `1/h`, and the emitted photon rate from a spectral emissivity is `epsilon_nu0/h` times the appropriate dimensionless integral. The checked physical-frequency integrals recover both factors. The volume conversion divides a per-comoving-Mpc^3 source by `(a_V Mpc)^3`; the identifying substitution `a_V=1/(1+z)` is an FLRW scale-factor convention, not an arbitrary Bianchi observed-redshift relation.

The Puchwein adapter reads an explicitly versioned primary table with ionization in `s^-1` and heating in `eV s^-1` per absorber, converting the latter to `erg s^-1`. Its prescribed-rate mode rejects adding a transported copy of the same radiation population. The public homogeneous/isotropic background is an input-model candidate, not an automatically inferred anisotropic source history.

## Remaining adoption obligations

1. Join continuum capture injection to the new bound cascade before claiming total Case A/B recombination. Supply a two-photon provider to propagate terminal 2s to physical ground state.
2. Keep Li multi-electron continuum/correlations and physical daughter multi-particle distributions in their separate provider tasks; the one-electron kernel cannot substitute for them.
3. Preserve historical nuclear amplitude provenance and kinematic convention when importing the new inverse tables.
4. Adopt an explicit source-history model and radiation-population ownership when connecting public UVB tables or emissivity candidates.
5. Carry model errors, interpolation errors, and floating-point/quadrature errors separately; the selected small numerical discrepancies do not estimate omitted physical corrections.

These obligations identify additional physical calculations. They do not reopen the reviewed finite-model normalization checks.

\clearpage

# R8 scoped publication decision

Decision: **PASS for a scoped research draft and reproducibility/handoff release. No current blocking scientific claim, normalization, or provider-readiness inconsistency found in the inspected snapshot.**

This is an independent read-only publication-consistency review, not external peer review, a new numerical certification, or admission of a complete cosmological production model. The existing `review/REVIEW.md` and its executed independent checks were read and reused. This pass did not repeat that scientific suite or start a security/software audit. Requested reviewer model identity is not asserted as observed runtime identity.

## Evidence and consistency judgment

- The n=20 hydrogenic E1 inventory, reduced-mass/COM dipole convention and two terminal states agree across the introduction, theory, result and provider contract. Terminal 2s, finite injection scope, missing continuum capture and missing two-photon propagation preclude total Case A/B claims; these exclusions are explicit.
- The one-electron quench's raw continuum probability and energy moments are separate from the now-executed allowed-beta model. Section 9 and native source use ground-channel Qg=18600 eV as a selected parameter, finite electronic-energy support, common branching normalization and one electronic/beta/neutrino energy ledger. F=1 and bare-Sommerfeld choices are declared approximations. Four infinite/reduced-mass cases and 43 author verification assertions are recorded. No absolute tritium rate, physical Q determination, recoil-complete spectrum, or correlated many-electron distribution is claimed.
- Nuclear stationary-target Planck, recoil-free Saha/Wien comparison and thermally moving Maxwell–Juttner/Wien results are separately identified. The new invariant thermal adapter retains the inherited nonrelativistic equal-mass EFT cross-section shape. The full moving-target Bose calculation and modern nuclear posterior are explicitly unexecuted. Small quadrature errors are not presented as amplitude uncertainty.
- Radiation intensity, emissivity, frequency, proper/comoving volume and heating units agree across the adapters and their explanations. Source-population ownership prevents counting transported UVB and its source emissivity twice. Puchwein-v1 is a versioned external benchmark; HYREC-2 is an actual compiled/executed stock FLRW reference with 8000 rows, not a prepared-only provider or a Bianchi solution.
- Current integration snapshots retain HH's already computed Coulomb rate while keeping finite quadrature/all-roundoff certification open. The two REI R7 variants have separate identities and proof constants. HE closeout and CR seeded-shell results are not promoted into newly solved source histories or changed production switches.
- The 65-item crosswalk keeps whole multi-part physical closure false while recording sub-obligation advances. The introduction and handoff do not turn finite benchmarks into a full 17-state/network result.

## Missing provider versus expensive execution

`local_codex/STATUS.json` reports eight heavy jobs, zero ready and eight blocked. This is supported by its detailed inventory: complete physical executables/decks or coupled implementations are missing, not merely waiting for CPU time. In particular, the actual Li continuum provider/channel deck, antisymmetric optimized Li basis, correlated asymptotic daughter states, precision nuclear scheme/calibration, full plasma rates and coupled background/transport bindings remain obligations.

Real lower-level code does exist: the relocated WU Coulomb donor, spatial ECG matrices, low-temperature propagation primitives, correlated operators, nuclear observation preparation and molecular PySCF input generator. The local runtime lacks PySCF and the physical molecular curves have not been generated. None of these facts establishes a ready converged molecular/Li campaign. Conversely, the new one-dimensional kernels, conditional beta extension, Maxwell–Boltzmann thermal-target reduction and stock HYREC reference are actual local executions and must not be described as missing executables. The handoff preserves this distinction.

## Concrete finding disposition

One transient document contradiction was reported to the parent: daughter section 1 said isotope masses and beta phase space had not been evaluated anywhere in the unit after section 9 had added those conditional calculations. The revised section 1 now limits infinite-mass statements to the initial benchmark and explicitly points to section 9. This minimal claim-scope correction is observed in the inspected snapshot. No formula, numerical result, tolerance or physical acceptance gate was changed to resolve it.

Current blocking findings: **none**. Existing unresolved physics belongs to the declared scope and handoff; it is not a reason to withhold this scoped draft. This decision does not approve an unreviewed main merge or claim the heavy campaigns have run.

## Inspected snapshot

The hashes below identify the actual reviewed text/evidence. Later claim-bearing changes require a bounded delta check; hashes are identity records, not scientific validation.

Review time (UTC): 2026-10-14T02:55:40.043659+00:00

| File | SHA-256 |
|---|---|
| `report/INTRO.md` | `314704e6434f8d5c595f223a0a937dff2cf64245b95a6fca92f9dfaf4ff5bc47` |
| `review/REVIEW.md` | `4b90061f6fffcfa6f62fdf0d2e6559e2562e308202055ea73e61a4b4d5124725` |
| `daughter/THEORY_AND_RESULTS.md` | `00fbdd7ca7c926e17fe537153b6826e08a04971d6b618f03c07dff25a3f52972` |
| `daughter/allowed_beta.c` | `725ac7a464b7770bc54dd2703038e18d62d52dfedbfccd6600a514ef90e038c5` |
| `daughter/allowed_beta_verification.json` | `224521ec9b922de5a481dcfd31d570205f2817bbd29a384b9e0371677b55dd8b` |
| `nuclear/THEORY.md` | `e55f809bdb3f94e9522514c8fc20489938d420382a63f91e6ff8331a6bd9aae0` |
| `nuclear/CHECKS.json` | `8cda233290392e141e636f482af397683f2c084b1a11f5fc28a4687467638eb9` |
| `nuclear/thermal_target_MB.json` | `a89dddc32aed61bd90c927884a7c03aeb7cf5fcc9866376afb628bb38597e7db` |
| `hydrogenic/CONTRACT.json` | `a7a80b699e6c5c842d736da368cdef8549c7a465ad1406afbbc97cde294d93ab` |
| `radiation/SOURCE_CONTRACT.json` | `7466cb84b9ace483819399ff94ceb6f594bf3e397c297805756b4c23f1248469` |
| `radiation/HYREC_EXECUTION.md` | `57d6624b679faf63178b247cd97379b9b23c782d2cc98986d77e24f2d6fcfe8c` |
| `local_codex/STATUS.json` | `65121d34b70e2ffba3ee84820d1bb8a42a6fa4e153e42773ae9ceefa7b86bfdd` |
| `local_codex/LOCAL_CODEX_HANDOFF.md` | `e1beb33e69a5729dfd2263078fa849acf9671f3fcc6cac28077f6af0d7bcef4a` |
| `local_codex/AVAILABLE_CODE_AND_INPUTS.md` | `10e1750caf69755ba327576849e88766ebc86d76a69ee5650db43e286bf0fcb3` |
| `integration/CURRENT_SNAPSHOTS.json` | `d21180dcd2477038e2b665204b797384d17c41b55520c21093ab14ea72e9e71a` |
| `integration/DELTA_AND_REUSE.md` | `fe44873a1c7a28f021e0de12c59e5cfec9afd42c003fe80d84d51e6d09106e87` |
| `GAP_CROSSWALK_R8.json` | `43553d5c6b93239d649ea31a1ee6594a6116943bb8e56e98235b2ee6643539d3` |

## Final report delta review

Decision remains **PASS**, with no new blocking findings. This bounded delta reads the final `report/INTRO.md`, new `report/SYMBOLIC_AND_IC.md`, and their retained symbolic/Planck receipts and replay/registry code. No numerical or symbolic computation was rerun.

The introduction's conditional allowed-beta row correctly describes the four combinations of phase-space approximation and mass convention, selected Qg=18600 eV and unresolved physical corrections. Its UTC date and spacing edits do not alter scientific scope. The symbolic chapter's seven scalar and seven tensor groups match the retained observed outputs; the distinction between actually submitted unqualified `$Version` and the metadata-corrected replay using `System`$Version` is explicit and correct. xTensor 1.3.0 and the archive identity match the receipt. The projection/current formulas preserve the declared metric and clock conventions.

The Planck reference contains exactly 21 tabulated cases at the stated seven redshifts and three hydrogenic charges. The cited z=20 logarithmic rates match the retained table at the displayed rounding, and the retained provider script performs the stated 128/256 comparison. The chapter confines these values to an isotropic FLRW Planck reference and does not claim a Bianchi redshift law, astrophysical reionization, or a complete species history. The lightweight registry's list path only displays its module inventory.

This delta supersedes the earlier INTRO hash only; unchanged reviewed module documents retain the preceding review.

Delta review time (UTC): 2026-10-14T03:00:25.378390+00:00

| File | SHA-256 |
|---|---|
| `report/INTRO.md` | `b083c33bc801932d19e65869ed1e1b91b6693c98bcdb5ce581697b603160a1aa` |
| `report/SYMBOLIC_AND_IC.md` | `8c84396d066e035c877a16c628ece625a9bc3bb7a6eb7a45867e493d01d0ce33` |
| `wolfram/SCALAR_OBSERVED_R8.json` | `2cb06d8e33ab71280f7800d9b2b5afac47d6ce70f85a650b104d3307250071ef` |
| `wolfram/XACT_OBSERVED_R8.json` | `17134c1cf8611975673c5c453743b941f209d67b9ec47b88de9968060ab096a9` |
| `wolfram/XACT_REPLAY_R8_EXECUTED.wl` | `05d1db7bd74171a7e9c3f1590b7afcc8ca4f6da27adf104b773059c060c47fdd` |
| `wolfram/XACT_BODY_R8.wl` | `7785d930441d40adc321da5ac0a0218a56294f2e385430d8387e77389fa8ccdb` |
| `photo/CMB_REFERENCE.json` | `efb1a3cdefc04dca13b758f9fc39b740db7b2df9f997d8434d165b2098b14d06` |
| `photo/CMB_RATES.csv` | `bf5c32dfbf059a503ec5a1aba61d0d5b82172e84dea9ba7c25347cfa3eb05555` |
| `photo/cmb_reference.py` | `76417e3b43235fa0a25e8a00fdcc0ad6f960d64dbf9bfc6054cfca410e303693` |
| `run_lightweight.py` | `9195265a217dcf3e694c9c7eea167b2807ca16f9694f1ed96c6a35fc5cb10123` |

\clearpage

# R8 theory and coding loop closeout

The bounded scientific R8 unit is complete: it contains actual derivations, native calculations, public-source imports, symbolic checks and a local execution package. It does not close the original 65 gaps or complete the full 17-species Bianchi/reionization production calculation. External backup/publication remains a delivery action; its provider/commit receipts must be added before C10 and the overall request are closed.

| Stage | Actual completed work and evidence |
|---|---|
| R1 | Fixed the lightweight-microphysics/source-history scope and explicit conventions using current user authorization. |
| R2 | Read current HE R10, HH PHYS29, moving CR and both distinguishable REI R7 artifacts; surveyed primary source candidates. |
| R3 | Separated physical Hamiltonians, selected parameters, thermal ensembles, units, clocks and evidence states. |
| R4 | Chose Coulomb/angular analytic reductions, transient cascade rewards, continuum moments and stable inverse-rate variables. |
| R5 | Derived E1 mass/dipole factors, daughter overlaps/tail/moments and allowed-beta folding, nuclear inverse/thermal adapters and source reduction formulas. |
| R6 | Independent reviewer normalization checks, exact-rational radial/angular checks, Wolfram and xAct contractions. |
| R7 | Executed the declared microscopic/reference calculations and compared discriminating limits and alternatives. |
| R8 | Adopted results only within their models; retained missing physical providers and the global project obligations. |
| R9 | Mapped equations to concrete C kernels, units, tables and consumer/local handoff contracts. |
| R10 | Preserved the scientific checkpoint and exact resumption dependencies. |
| C1 | Identified current source baselines and the new finite-model computations. |
| C2 | Traced equations through functions, inputs, tables and missing-provider interfaces. |
| C3 | Implemented polynomial radial quadrature, log/expm1 evaluation, endpoint smoothing and acyclic cascade reduction. |
| C4 | Parallelized independent modules here and prepared measured-resource local orchestration. |
| C5 | Built and executed native kernels, public-table adapters and stock HYREC reference. |
| C6 | Passed scoped implementation and error-handling checks, keeping runner fixtures separate from physical calculations. |
| C7 | Checked energy/number closure, orthogonality, angular/spin factors, volume/clock factors and reference limits. |
| C8 | Recorded refinements, independent quadratures, source identities, measured time/memory and remaining model errors. |
| C9 | Completed independent finite-kernel review; subsequent beta/thermal-target additions retain their own explicit checks. |
| C10 | Local package and handoff prepared; external publication acknowledgement pending root delivery. |

## Executed evidence

- Hydrogenic E1: 210 states, 2470 lines per mass/charge case, eight cases and 6190 native checks. An independent exact-rational method checked 13 radial matrix elements and eight angular sums. The E1-dark 2s remains retained.
- Daughter: five zero-recoil sudden Coulomb ratios, continuum and analytic bound tails, 73 checks. Four additional conditional allowed-beta variants use selected Qground=18600 eV, F=1/bare Sommerfeld and infinite/reduced masses; 43 checks. These are explicit physical comparison models, not calibrated absolute tritium branching data.
- Nuclear: native historical Chen-Savage np capture plus stationary-target and Maxwell–Juttner/Wien thermal-target adapters; 54 checks. Exact kinematics do not upgrade the inherited nonrelativistic nuclear amplitude.
- Radiation: 48 native analytic-source tests; a versioned 59-node public UVB table with 181 checks; 36 finite-band Stobbe/screen cases and 21 declared Planck reference cases.
- HYREC-2: source commit `09e8243d0e08edd3603a94dfbc445ae06cafe139` compiled and executed in SWIFT mode; 8000 output rows and seven finite-reference checks. The upstream example cosmology is a reference input, not an adopted project cosmology or a Bianchi/17-species solution.
- Reduction: all retained n20 states receive adjoint photon/energy/terminal and delay moments, compared against independent forward propagation. Wolfram/xAct checks cover the stated scalar/tensor identities.
- Independent review: 24 selected numerical checks plus three additional direct Coulomb-wave integrals. Small arithmetic residuals are not physical uncertainty estimates or outward-rounded certificates.

## Handoff and remaining work

Eight physical local tasks are defined; zero have complete executable/deck bindings. Ten runner fixture checks and four relocated native checks establish orchestration/base-code behavior, not heavy scientific execution. The missing inputs and implementation obligations are named separately for Li bound/continuum, low-temperature molecular scattering, correlated daughter channels, precision nuclear response, atomic charge/cascade, BBN-to-17 and full transport. A baseline H/He integration can proceed independently once its source history and interfaces are selected.

The local record keeps publication prepared rather than verified until actual external receipts are added. Its structural validator checks JSON fields, references and stage statuses only; scientific support resides in the referenced derivations, code and execution evidence.
