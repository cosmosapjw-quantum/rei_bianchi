# Actual-endpoint warm electron coefficients and native H secondary energy operator

This unit resolves two parts of the recurring stopping-provider blocker: the existing CR warm-electron operator is now bound analytically to the saved endpoint, and the NIST hydrogen BED differential cross section supplies a positive, independently usable secondary-energy law. It does not deliver a cascade, a deposition fraction, or activation in the old 13.6 eV chemical ledger. These are component results within `HE-EXP-STOPPING` / `CR_N4_STOPPING_KERNEL`; `HE-CLOSURE` remains partial. The already admitted `REI-EXP-EVENT-CONSUMER` source is reused without replay.

## Fixed physical input and inherited evidence

The immutable H1 source from PR233 has 307200 atoms with electron kinetic energies 0.011132743029032 to 134.47572072132542 eV. Its primary energy convention is photon energy minus 13.6 eV. The saved endpoint gives T=14994.847774798709 K, free charge-derived electron density 5.996197830412253 m^-3 and reference density 5.151254745827818 m^-3. Neutral H1 abundance is 1.561568161163724e-5 per reference; the physical neutral density is their product. No source atom was scanned or source history replayed in this unit.

CR59 already implements the warm Maxwellian operator; CR99/C23D already admitted finite chains at T0=10000 K, ne0=140000 m^-3 and prescribed lnLambda=20. Reusing their mathematics is evidence reuse, not a new derivation claim. Their selected sources, finite upper boundaries and first-entry measurements are different from the present endpoint. HE PR102 still supplies no fully admitted physical stopping provider.

## Warm electron-electron component

Select a stationary Maxwellian perturbative bath in the source's normal tetrad, using the saved gas temperature and pre-existing free electron density. This is an explicit bath closure, not an inference that the actual distribution was measured Maxwellian. Retain lnLambda=20 as a prescribed leading-log model; screening is not newly determined.

Let theta=k_B T/eV_J, x=E/theta, and

\[
F(x)=\operatorname{erf}\sqrt{x}-\frac{2\sqrt{x}e^{-x}}{\sqrt\pi},\quad
\Gamma=\frac{4\pi n_e[e^2/(4\pi\epsilon_0)]^2\ln\Lambda}{m_e^2},\quad
b_0(E)=\frac{m_e\Gamma}{\mathrm{eV}_J\sqrt{2\mathrm{eV}_J E/m_e}}.
\]

The backward energy generator is L phi=A phi'+D phi'', with

\[
D=\theta b_0 F(x),\qquad
A=b_0\left[\frac{4\sqrt{x}e^{-x}}{\sqrt\pi}-\operatorname{erf}\sqrt{x}\right].
\]

Here A has units eV/s, D has units eV^2/s and Var(dE)=2D dt. The number density N(E), rather than the flux-weighted literature variable, has current

\[
j=AN-(DN)'=-D\left[N'+\left(\theta^{-1}-(2E)^{-1}\right)N\right].
\]

Consequently N_M proportional to sqrt(E) exp(-E/theta) has zero current. This equation also fixes the drift/diffusion convention and guards against converting a friction force directly into an energy drift. D is positive for E>0. At the actual endpoint theta=1.2921560049057651 eV. A crosses zero near 1.2662862505493653 eV; at E=.011 eV it is +9.068498165521886e-10 eV/s. A cold-drag model has the opposite sign there and is a discriminating negative control.

For T1=a T0 and beta=(ne1 lnLambda1)/(ne0 lnLambda0) a^(-3/2),

\[
A_1(aE)=\beta a A_0(E),\quad D_1(aE)=\beta a^2 D_0(E).
\]

The density pushforward N1(E)=a^(-1)N0(E/a) conjugates the generators with time multiplier beta. Correspondingly scaled finite grids inherit Q1=beta Q0 and unchanged dimensionless equilibrium weights. This closes an exact parameter-binding lemma. Here a=1.4994847774798709 and beta=2.3325707502987591e-5. The old R80 upper boundary maps to 103.37248039246121 eV, below the actual source maximum. Therefore old chain source-weighted first-entry statistics cannot simply be reused, even with the correct time scaling.

The conditional plasma has very small classical coupling (3.26e-9), degeneracy (1.35e-27) and theta/(m_e c^2) (2.53e-6), and a large electron Debye-sphere population (1.03e12). These calculations support a dilute nonrelativistic weak-coupling model. They do not prove the bath closure, give a rigorous leading-log error bound or establish a chosen Coulomb logarithm from screening. Energy-space scalar coefficients require no assertion that the injected distribution is isotropic; momentum and angular transport remain separate.

For an actual kinetic evolution the bath energy owner must receive minus the SAME collisional kinetic moment. On a finite interval,

\[
\frac{d}{dt}\int E N\,dE=-[Ej]+\int AN\,dE-[DN].
\]

The boundary terms cannot be discarded merely because the number current reflects. In a discrete implementation use the actual generator's energy row. Adding a separate integral of b0 N as heat would double count and omit thermal diffusion. This coefficient query unit computes neither that moment nor heat.

## Native NIST H BED secondary kernel

The source is the NIST Electron-Impact Ionization Cross Section Database, introductory equations 3 and 4, H differential query, and Kim & Rudd (1994), DOI 10.1103/PhysRevA.50.3954. The actual T=30 eV returned table and T=100 eV/W=0 witness are preserved. Both report the 0.955 normalization. The fit values are B=U=13.6057 eV, N=1, Ni=.4343, n=1, a0=.52918 Angstrom and R=13.6057 eV. The separately printed Q=.5668 is not used by this differential formula.

Put t=E/B, w=W/B, a=1+w, b=t-w, y=1/a, S=4 pi a0^2 and

\[
p(y)=-.02247280y^2+1.177455y^3-.4626461y^4+.08906479y^5.
\]

The following is the NIST expression rewritten algebraically for positivity:

\[
k(E,W)=\frac{.955S}{B(t+2)}\left[(2-N_i)\frac{a^2+b^2-ab}{a^2b^2}+\frac{\ln t}{a}p(y)\right].
\]

k is d sigma/dW in Angstrom^2/eV; multiply by 1e-20 for m^2/eV. The selected domain is B<=E<=150 eV and 0<=W<=(E-B)/2. W denotes the slower outgoing electron. The faster partner is E-B-W. There is no extra factor two when integrating this half range to obtain the event cross section. At E=B the interval has zero width, hence zero total rate even though the differential endpoint value need not vanish. The model uses a stationary heavy ground-state target with neglected recoil; moving-target convolution has not been admitted.

The rewrite uses a+b=t+1. Its first numerator is positive. Also y is in [2B/(150+B),1], and p(y)/y^2 is at least c2+(c3+c4)*2B/(150+B)=.0964164006908072>0. Thus k>=0 over the declared rectangle with triangular support. This is a useful certified operator property, not a numerical sampling claim.

The energy-only branching operator, for a test function phi, is

\[
L_{\rm H}\phi(E)=n_{\rm HI}v(E)\int_0^{(E-B)/2} k(E,W)
[\phi(W)+\phi(E-B-W)-\phi(E)]\,dW.
\]

Its event has net electron count +1, H I count -1, H II count +1, and exact charge balance. For phi(E)=E the electron kinetic change is -B per event, balanced by +B in the native ionization ledger. No thermal fraction has been introduced. This supplies an actual secondary redistribution law and paired energy accounting; the present implementation evaluates the differential kernel and individual event identities without quadrature or an evolution.

BED is an approximate collision model. Its energy sharing convention is not a fully resolved two-electron angular/spin state. The original paper's near-threshold behavior does not provide exact Wannier-threshold accuracy. General total-cross-section performance quoted by the database does not give a pointwise SDCS confidence interval or covariance. The native data's displayed constants are rounded: strict agreement with an independent Wolfram evaluation of those displayed constants uses 2e-12 relative; agreement with the native printed table uses 5e-5 relative. The latter accommodates parameter and display rounding and is not a physical model uncertainty.

## Convention obstruction and next actual dependency

The old primary/chemical threshold is 13.6 eV, native BED uses 13.6057 eV, and the NIST atom page separately lists physical ionization energy 13.5984 eV. They must not be silently identified. Passing the native operator into the old binding ledger leaves a per-event .0057 eV gap. A common zero-of-energy gauge cannot remove an energy DIFFERENCE across an ionization event. Independent native paired results are valid; direct old-network activation must reject until a coherent source/potential convention is selected and remapped. No artificial offset reservoir has been introduced.

The same source offers actual 1s->2p excitation data (BE-scaled rows beginning at 11 eV, with alternatives), retained as intake only. NIST lists a 10.1988 eV excitation gap whereas WU's admitted finite-native model uses 10.20435 eV. A selected excitation model needs a matched energy convention and interpolation/domain/error contract, rather than a reused thermal rate coefficient masquerading as a tagged fast-electron hazard. Other populated target species, recoil/elastic channels, the closure boundary, and coupled source/cascade evolution remain explicit dependencies.

The smallest next action is coherent H native energy-convention binding, then a bounded operator/source contraction with newly allocated remaining authority. This unit neither scans the existing source nor starts a new cascade. The 10 CPU-second source lineage has planning use 9.689830337 seconds before the bounded combined tests; no budget reset or transfer occurs.

## Symmetries, invariants and observables

The Maxwell bath is rotationally invariant, so its energy marginal closes for test-particle collisions without imposing isotropy on the source. Temperature dilation is a similarity between models, not a physical gauge freedom. The slower/faster labels avoid duplicate outgoing pairs; they do not supply differential angular correlations. Conserved number/charge/baryon and paired kinetic-plus-binding energy are event invariants. Measurable model outputs here are A(E), D(E), k(E,W) and the endpoint-specific drift sign; deposition, residence-time distribution, irreversible assimilation, secondary yield and heat are uncomputed observables.

## R1-R10 and canonical position

| Stage | Concrete result | Whole-DAG position |
|---|---|---|
| R1 | Fixed saved source/T/ne/frame and current HE/CR heads | Reuses completed source leaf; selects stopping descendant |
| R2 | CR59/99 reuse audit, SciSpace and Exa intake, official NIST response | Existing stopping parents remain partial |
| R3 | Maxwell bath, prescribed logarithm and native target domains stated | Separates component model from full HE closure |
| R4 | Exact density/time dilation and positive BED rewrite derived | Closes analytic component obligations |
| R5 | Six Wolfram algebra residuals zero; numeric anchors obtained | Independent symbolic/numeric evidence, no local evolution |
| R6 | Warm drift, Maxwell invariant, paired energy/count identities | Physical meaning checked before implementation |
| R7 | Native binding gap, finite old-chain upper support and unknown channels exposed | No false promotion of parents |
| R8 | Frozen equations, inputs, tests and cap in IMPLEMENTATION_CONTRACT.json | Routine implementation assigned to implementation26 |
| R9 | Root reviews bounded combined stdlib tests and resource evidence | Runtime outcome belongs to root test artifact |
| R10 | Source/contract/derivation handed off with exact remaining dependencies | No canonical denominator or parent-completion increment asserted |

Raw Wolfram output records a symbol-warning in the first call and returns all six residuals as zero with resolved numerical outputs; it is preserved without concealment. No local scientific runtime was used by the theory worker. Implementation acceptance is determined by the separately executed combined test result, not by this document.
