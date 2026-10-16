# Unit6 T6: delayed hydrogenic 2s reservoir completion

Frozen scope, 2026-10-16: extend the 32 saved statistical-shell mixtures with spontaneous 2s→1s continuum emission. The injection is the existing fixed-n bound-shell distribution, not a recombination coefficient. This is a literature-fit closure of a previously missing physical channel, not an ab-initio spectrum reconstruction. No higher-level coherent two-photon correction, stimulated process, inverse absorption, collision, expansion, or transport is added.

## Source model and normalization

Chluba & Sunyaev (2006), arXiv:astro-ph/0508144, equations (1),(4), supplies the Nussbaumer–Schmutz fit and the pair-counting convention. With y=E/Delta in [0,1], w=y(1-y), define

    g(y)=w[1-(4w)^gamma]+alpha*4^gamma*w^(beta+gamma),
    alpha=0.88, beta=1.53, gamma=0.8.

The source's phi=46.26*g is NOT a normalized probability density. Its decay rate is (A0/2) integral(phi dy), because counting both photons over the full interval counts each decay twice. Keep the shape independent of the adopted lifetime.

Our exact fit normalization follows by integrating powers of y(1-y):

    I=B(2,2)-4^gamma B(2+gamma,2+gamma)
      +alpha*4^gamma B(1+beta+gamma,1+beta+gamma)
      =0.08144613055216544 (double precision evaluation).
    f(y)=g(y)/I; q(y)=2*f(y).

f is the probability density of a uniformly selected photon from a decay and integrates to 1; q is the expected photon number per decay per dy and integrates to 2. Symmetry gives integral(y*f dy)=1/2 and integral(y*q dy)=1. The pair consists of y and 1-y; drawing two independent f samples would violate pairwise energy conservation. If pair sampling is needed, draw one y and set its partner to 1-y. Equivalently the smaller-photon density on [0,1/2] is 2f.

Set f=0 outside [0,1] and f(0)=f(1)=0. Positivity is manifest: 0<=4w<=1 and both terms in g are nonnegative. Near an endpoint g~y, so no artificial infrared cutoff is required for this spontaneous model. The density per energy per decay is q(E/Delta)/Delta, not q(E/Delta).

Schirmer (2016), arXiv:1608.03132, equation (9) and adjacent text, reports roughly 1% fit accuracy over nearly the whole spectral range. This is not a uniform certified endpoint bound, not a claim that our normalization makes the physical spectrum exact, and not the numerical quadrature tolerance. Report the fit as literature approximation with that qualification. No digitized figure is used. The exact 2006 analytic formula and coefficients were read from primary arXiv PDF text, independently corroborated by the 2016 text.

## Species energies and lifetime convention

Read actual R8 transitions.csv and select the unique 2p→1s row per species; its photon_eV is Delta. Do not substitute rounded 10.2, 40.8 or 91.8 eV. Let Delta_inf,H be that row for H_infinite_mass and

    r_mu=Delta/(Z^2*Delta_inf,H).

This is the reduced-mass ratio mu/m_e already encoded in the R8 Coulomb energies; M=0 in that table denotes the infinite-mass model. The species are H_infinite_mass, HeII_infinite_mass, LiIII_infinite_mass, H1, D, T, He3II, He4II. The only LiIII model available is infinite nuclear mass.

Wundt & Jentschura (2009), arXiv:0909.4836, equation (1), gives the nonrelativistic infinite-mass rate A_inf=8.229352 Z^6 s^-1. Freeze

    A=8.229352*r_mu*Z^6 s^-1; tau=1/A.

The r_mu factor is a derived reduced-mass Coulomb approximation, consistent with using the electron-relative-coordinate dipole -e*r. In length gauge, the second-order matrix amplitude scales as r^2/E ~ mu^-3 Z^-4; the integrated two-photon phase-space factor scales as Delta^7 ~ mu^7 Z^14. Their product gives mu Z^6, and leaves the normalized y shape invariant. This is NOT a full recoil treatment. In an exact center-of-mass electric dipole the effective relative charge for a charged ion is e*(M+Z*m_e)/(M+m_e); its fourth power would enter a two-E1 rate. That extra recoil prescription, relativistic corrections, Lamb shifts, finite nuclear size and radiative corrections are not introduced here. Therefore precision isotope lifetimes or full finite-mass ionic rates must not be claimed. The reduced-mass approximation must be present in exported metadata.

Do not substitute the 8.2206 s^-1 value quoted in the cosmological paper without changing the declared rate model: the chosen anchor intentionally follows the nonrelativistic Coulomb calculation. No uncertainty posterior is attached to the quoted digits.

## Saved reservoir and exact conditional time evolution

For each saved row let P=terminal_2s_probability, U_R=terminal_2s_energy_eV, N1=E1_photon_count, U1=E1_energy_eV and U0=initial_excitation_eV. Verify U_R=P*Delta against actual energies. Independently recompute P=sum_l(2l+1)/n^2 * P_terminal_2s(n,l) from cascade.csv. Use the saved mixture P for the emitted spectrum after agreement.

The time origin is completion of the E1 cascade and preparation of its terminal reservoir. It is not the time of original shell injection; the prior cascade time distribution is not saved and is not reconstructed. Conditional on that origin and isolated spontaneous decay,

    R(t)=P*exp(-A*t), D(t)=P*(-expm1(-A*t)), t>=0,
    cumulative dN2/dE=2*D(t)*f(E/Delta)/Delta,
    instantaneous d(dot N2)/dE=2*A*R(t)*f(E/Delta)/Delta,
    N2(t)=2*D(t), U2(t)=Delta*D(t), Uremain(t)=Delta*R(t),
    P_ground(t)=terminal_1s_probability+D(t).

Thus N_total=N1+N2 and U1+U2+Uremain=U0. At infinity N2=2P and U2=P*Delta; ground probability is one. In every finite time row save elapsed_seconds as well as x=A*t. Required x=[0,0.1,1,10]; store infinity as an explicit asymptotic row with elapsed_seconds null, not a JSON nonfinite number. The differential continuum file is the asymptotic yield; finite-time shapes follow by multiplication by 1-exp(-x). Save instantaneous photon and energy rates in time rows as 2AR and Delta*AR.

For future non-impulsive injection S_2s(t), the exact isolated-reservoir solution is R(t)=R(0)e^(-At)+integral_0^t e^[-A(t-s)]S_2s(s)ds. This formula is theory only; no cosmic source history is inferred or implemented in this unit.

## Observable continuum and Li I response

Export both integrated photon count and integrated energy in each continuum bin. Use 128 uniform y bins plus inserted internal boundaries E=5.392,13.6,64.39 eV when inside [0,Delta]; merge exact duplicates. A center-sample times bin width is not an authoritative bin moment. Store E_lo,E_hi,N_bin,U_bin_eV. The full spectrum is existing exact E1 delta lines plus these continuum moments, not two invented monoenergetic photons.

Also integrate photon and energy moments for below-Li [0,5.392], sub-Lyman [5.392,13.6], ionizing-covered [13.6,64.39], and photo-uncovered [64.39,Delta], clipping each interval to [0,Delta]. Empty intervals give exact zero. All boundaries use the existing bridge conventions; 13.6 is a band label, not an isotope-specific threshold.

Use only the actual Verner photo.dat Z=3,N=3 row, verified SHA256 in contract. Its tabulated range is Eth=5.392 to Emax=64.39 eV. The frozen bridge formula is

    x=E/E0-y0; yv=sqrt(x*x+y1*y1)
    sigma=1e-22*sigma0*((x-1)^2+yw^2)*yv^(Pver/2-5.5)
          *(1+sqrt(yv/ya))^(-Pver) m^2,

with E0=3.107, sigma0=62.45, ya=15.01, Pver=4.895, yw=y0=y1=0. Zero below threshold; never evaluate or extrapolate this row above Emax. The source continuum beyond Emax is retained as uncovered photon/energy moments, especially for LiIII.

Let S(E)=2P*f(E/Delta)/Delta be asymptotic photons per injected precursor per eV. Define hypothetical incident flux F_E=J*S(E), with J=1 precursor-equivalent m^-2 s^-1. This convention preserves mixture weights and makes Gamma/J=integral(S*sigma dE) in m^2; H/J=eV_J*integral[S*sigma*(E-Eth)dE] in J m^2; and Abs/J=eV_J*integral(S*sigma*E dE). At the declared unit J, values are also rates per Li I target in s^-1 and J/s. These are conditional response coefficients, not locally inferred radiation from the emission yield. No distance, transfer, isotropic-flux conversion or cosmological source normalization is implicit.

Save responses separately for sub-Lyman and covered-total [Eth,min(Emax,Delta)]. Abs=Eth*eV_J*Gamma+H; use eV_J=1.602176634e-19 exactly. Finite-time fluence responses are the asymptotic coefficients multiplied by 1-exp(-x), if needed; no extra response files are required.

## Bounded implementation and acceptance

One small C99 numerical kernel (shape, beta normalizer, rate, reservoir) with a Python JSON/CSV driver and one focused test file; read original inputs only; write only Unit6 code/tests/results/evidence paths named in JSON. No high-n eigenstates or Coulomb sum reconstruction. Commands must each finish within 30 s, with total numerical run under 30 s. Use Gauss–Legendre quadrature with 64,128,256 nodes on each smooth/clipped integration interval; 256 is final. All three outcomes are retained, comparing 128/256. A single independent SciPy quad evaluation of normalization, the mean-energy moment and each species covered Li response is allowed; do not mirror the implementation in the test. C99 tgamma or lgamma is sufficient for the analytic beta factors; require its normalization to agree with the independent Python reference to 1e-11 relative. No further ladder expansion without controller interpretation.

Tests cover only (i) shape positivity/symmetry/normalization and mean-energy moment, (ii) actual 32-row input/reservoir closure, (iii) finite-time exact closure and limiting values, (iv) Li range handling, positive response and absorption identity. Numerical integral tolerance is 1e-8 relative (absolute floor 1e-14 photons or eV per precursor), comfortably smaller than the literature approximation error. Pure algebraic closures require 1e-11 relative with that floor; probabilities require 1e-12 absolute; analytic shape symmetry 2e-13 absolute. For tiny response coefficients use relative 1e-8 with floors 1e-35 m^2 and 1e-53 J m^2, so an SI absolute tolerance cannot silently accept wrong factors. The analytic beta normalization is an independent reference, not a numerically fitted renormalization. No failed quadrature may be silently rescaled to pass.

PASS permits controller scientific review of this isolated fit-based completion. Any missing input identity, nonpositive spectrum, failure of the finite ladder, or a model change returns one concrete result to controller; it does not create new process gates. Stop after this validation and preserve the raw values.
