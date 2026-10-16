# Unit 7 lane B: physical early-epoch Be7 kinetics

Authority identity: requested Astra; observed runtime identity UNKNOWN. This freezes a model and its executable numerical contract, not a product-code change. No existing runner or NCP changes are authorized. The unmodified Unit 6 donor is the immutable input; numerical outputs are compared numerically, never by hashes.

## Model and source interpretation

Khatri–Sunyaev, arXiv:1009.3932v2, equations 5–9, supplies total radiative recombination, blackbody photoionization, and statistical-hyperfine hydrogenic capture. Ground-state recombination is retained because the trace species does not appreciably modify the radiation bath. Adopt their approximate 106.4-day half-life and fit coefficients; this is not an ab initio atomic or nuclear rate calculation.

Use only Be4+ ↔ Be3+ → Li3+. The lithium state counts the bare daughter immediately following bound capture, not its subsequent atomic history. Continuum capture, second-electron recombination, nonthermal radiation, heat deposition and late recombination/reionization are outside this model. H and He are fully ionized across the computed z=100000 to 10000 window; Tmatter=Tgamma=T0(1+z). Charge spectators are frozen in the bath. The source's parameter set is not adopted: the primary run uses the actual donor's cosmology and abundances. No plot digitization is permitted.

Let B be the donor Be7 abundance per baryon and (a,b,F) its normalized surviving bare, surviving one-electron, and decayed fractions. Initially (1,0,0). The pre-existing direct Li7 abundance is kept separately. Define r=ne alpha, beta the photoionization rate, and lambda=ln(2)/(106.4*86400 s). In physical time:

    a_dot = -r a + beta b
    b_dot = r a - (beta+lambda)b
    F_dot = lambda b

The generator is Metzler and has zero column sums after adding the absorbing daughter. Therefore all populations stay nonnegative and a+b+F=1. This supplies the physical history within the explicitly frozen early-epoch model; it does not complete all nuclear or ionic evolution of the donor.

## Rate and cosmology definitions

Use Z=4, t=T/(1e4 K Z^2), alpha=1e-13 Z*5.596*t^(-0.6038)/(1+0.3436*t^0.4479) cm^3/s. Define S(T)=(2*pi*me*kB*T/h_planck^2)^(3/2)*exp(-chi/(kB*T)) in m^-3, converted to cm^-3 by division by 1e6. Then beta=alpha*S_cm3 in s^-1, with no additional degeneracy factor. chi=217.7 eV is a deliberately rounded hydrogenic binding-energy model. NIST ASD's Be3+ ground-state threshold near 217.7186 eV supports this rounding; its extra digits are not treated as a measured isotope-specific Be7 input.

The adopted fit is evaluated over T=27257.7255..272552.7255 K (scaled T/Z^2 about 1704..17035 K); the start comparison extends to 545102.7255 K. The paper applies this fit at the conversion epoch. We claim neither a global accuracy certificate nor a high-temperature asymptote: Verner–Ferland explicitly identifies the old fit's incorrect high-temperature asymptote. The donor-to-start tail bound below cancels alpha and does not extend that fit to the BBN endpoint. Numerical tolerances measure solution error within this rate model, not atomic-model uncertainty.

Constants and units are fixed in the JSON contract. In particular h_planck=2*pi*hbar; c and kB are explicit SI values, energies use 1 eV=e joule, day=86400 s, and Mpc is explicit. The dimensionless cosmological h is distinct from h_planck.

    H0 = 100 h km/s/Mpc; h=0.7
    Omega_m = (0.02205+0.12495)/h^2
    rho_gamma_mass = pi^2 (kB*T0)^4/(15 hbar^3 c^5)
    Omega_gamma = 8*pi*G*rho_gamma_mass/(3 H0^2)
    Omega_r = Omega_gamma*[1+(7/8)*(4/11)^(4/3)*Neff]
    Omega_Lambda = 1-Omega_m-Omega_r
    H(z)=H0*sqrt(Omega_r*(1+z)^4+Omega_m*(1+z)^3+Omega_Lambda)

Neff=3.0439772985579183 and T0=2.7255 K. Neutrinos are treated as relativistic for this high-redshift expansion history. No neutrino mass claim at z=0 follows from this parametrization. nb(z)=2.47920954940649e-7*(1+z)^3 cm^-3. Ye=sum_i Zi Yi is computed from every donor species, with n:0,p:1 and H,He,Li,Be,B,C,N,O,F,Ne,Na charges 1..11; do not substitute a helium-only fit or normalize the donor. ne=nb Ye is the prescribed bath used in r. The trace electron ledger below is separate. Frozen tritium and other minor spectators are part of this bath approximation.

## Why the initial bare donor can be started at z=100000

The donor endpoint is zd=4257756.520289892. Put x=1+z, A=chi/(kB*T0), and R(z)=ne/S(T)=K*x^(3/2)*exp(A/x). Its only interior stationary point is a minimum, so M=max(R(zstart),R(zd)) bounds it throughout the omitted interval. Since b_dot<=r-(beta+lambda)b and r/(beta+lambda)<=R, the interval [0,M] is invariant for b starting from zero. Consequently

    F_omitted <= lambda*M*Delta_t_rad
    Delta_t_rad = [xstart^-2-xd^-2]/(2*H0*sqrt(Omega_r)).

This uses H>=H0 sqrt(Omega_r) x^2, hence is a conservative time bound. It depends on detailed balance in an ionized thermal bath, not on extrapolation of the recombination fit. The initial omitted b is bounded by M as well. Require F_omitted+M<1e-7 and execute the independent zstart=200000 comparison. The latter is a numerical initialization test; the analytic bound links the initial condition to the actual donor. Do not set the physical omitted tail identically to zero or infer that the donor endpoint time equals the integrated cosmic age in this simplified cosmology.

## Stable solution without resolving the ionization timescale

Use u=ln[(1+zstart)/(1+z)], so du/dt=H and d/dz=-1/[(1+z)H] d/dt. On each uniform u interval freeze rates and H at its midpoint; dt_eff=Delta_u/H_mid. This exponential midpoint discretization solves the frozen two-state system exactly. The two positive decay rates are

    L=r+beta+lambda
    D=sqrt((r-beta-lambda)^2+4*r*beta)
    ks=2*r*lambda/(L+D), kf=(L+D)/2.

Computing ks by the product relation prevents subtractive cancellation. Write es=exp(-ks*dt_eff), ef=exp(-kf*dt_eff), J=es*(-expm1(-D*dt_eff)). The nonnegative propagator entries are

    E00=[(beta+lambda-ks)*es+(r-ks)*ef]/D
    E01=beta*J/D
    E10=r*J/D
    E11=[(r-ks)*es+(beta+lambda-ks)*ef]/D.

For the fixed physical inputs D>0; no near-degenerate branch is needed in the production physical interval. A generic utility that accepts D=0 must implement its analytic limit or reject outside-contract fixtures. Do not expand a large hyperbolic cosine or form exp(+kf dt).

Accumulate F with an independent positive decay reward rather than subtracting nearly equal 1-a-b. With I(k)=-expm1(-k dt_eff)/k, continuous at k=0,

    Delta_F=lambda/D * {r*a*[I(ks)-I(kf)]
                  +b*[(r-ks)*I(ks)+(beta+lambda-ks)*I(kf)]}.

Use old a,b in the reward, then apply E. All reward terms are nonnegative. Tiny residuals are reported without clipping or normalization. The surviving fraction at the final redshift remains the computed a+b even when F rounds to unity.

An independent SciPy Radau integration in u of (a,b,F), with an analytic Jacobian, supplies the reference. It must not use the exponential propagator internally. rtol=1e-9, atol=1e-12; dense output is evaluated on the production grid. Use a 30-second cumulative numerical budget, with a reported 60-second ceiling only if a measured reference startup/solve warrants it; stop an unbounded stiff integration and return evidence rather than hiding it. No optional parameter scan is required.

## Competing ionization and capture; quantified reduction

A newly formed Be3+ ion has probability lambda/(beta+lambda) of decaying before photoionization when rates are frozen. Therefore the hazard on a bare ion is r*lambda/(beta+lambda), not r alone. For S=a+b and s=b/S,

    S_dot=-lambda*s*S
    s_dot=r-(r+beta+lambda)*s+lambda*s^2.

The stable instantaneous root is sstar=2*r/(L+D)=ks/lambda. Adiabatically setting s=sstar gives S_QSS=exp[-integral(ks/H)du], F_QSS=1-S_QSS, and b_QSS=sstar*S_QSS. This is a comparison approximation; the full two-state solution is primary. Also report the simpler algebraic closure s0=r/L, obtained by neglecting b_dot in the S,b equations, and its integrated F0. Evaluate both integrals by cumulative trapezoid on the production grid. Require max|F_QSS-F_full|<=1e-3 and report the observed maxima for both reductions; the simpler closure has no independent acceptance gate. Report ratios beta/lambda, r/H, and D/H near z10,z50,z90 so the accuracy has a physical interpretation.

## Physical electron and nuclear ledger

For abundances per baryon, Delta free electrons=-B*(b+F), bound electrons=B*b, Delta nuclear charge=-B*F, and Delta ionic charge=-B*(b+F), all relative to the initially bare Be inventory. The recombination-minus-ionization count equals B*(b+F); bound capture consumes one bound electron, produces Li3+ and one neutrino, and does not itself change free electrons. Thus total electron loss=-B*F, electron-plus-neutrino lepton count is unchanged, and Delta ionic charge-Delta free electrons=0. Heavy-nucleus number B and mass-seven baryons 7B are conserved. Nuclear proton number is not conserved. The prescribed rate bath ne remains fixed to the frozen background even though this explicit trace ledger changes; its fractional effect is bounded by B/Ye and must be reported. This is a controlled trace-bath approximation, not an exactly self-consistent plasma closure.

## Outputs and acceptance

Production uses N=32768 equal-u intervals and zstart=100000,zend=10000. A N=16384 run supplies convergence evidence. Output descending z with columns z,u,x_Be4,x_Be3,x_Li3,Fdecay,dF_dz,p_z. x_Li3=Fdecay. dF_dz=-lambda*b/[(1+z)H]. p_z=-dF_dz/(F_end-F_start) is the conditional redshift density in the computed window; it is not the absolute yield. Lane C must use raw Fdecay for conservative counts and raw dF_dz for a differential spectrum. Preserve B, direct donor Li, nb0 and nBe0=nb0*B in metadata.

Define z10,z50,z90 by F(zq)=q, where q=.1,.5,.9 of the initial Be population. z10>z50>z90. Use monotone linear interpolation, report if any target is not reached. Never redefine quantiles silently as conditional ones. Numerical trapezoid normalization of p_z is diagnostic: midpoint-frozen endpoint b has a small grid-phase error even when cumulative F is more accurate.

Frozen acceptance: min(a,b,F)>=-1e-12; max|a+b+F-1|<=5e-11; F monotone within 1e-12; grid convergence max absolute F error<=5e-6 and b error<=5e-6; Radau max F error<=1e-5 and b error<=1e-5; z quantile differences<=2 redshift units for refinement and reference; |integral p_z dz-1|<=2e-3; QSS bound above; start-test max F difference<=1e-7 after interpolation at common z (use the reference dense output for start test if coarse-grid interpolation would dominate). Final a+b<=1e-8 is the early-window completion criterion; any larger value is reported, not overwritten. Stoichiometric donor-relative ledger residual<=1e-12 with absolute floor1e-25, using separate signed delta arrays rather than subtraction of rounded backgrounds. A failed tolerance goes back to authority once with raw evidence; it does not authorize changing physics or tolerances.

No paper-like comparison is mandatory. If performed, it is separately labeled with its complete helium/radiation assumptions and cannot be called exact paper reproduction. PASS authorizes independent scientific review of this scoped history and the downstream spectrum calculation, not native evolution, exact recombination physics, gas heating, or reionization completion.
