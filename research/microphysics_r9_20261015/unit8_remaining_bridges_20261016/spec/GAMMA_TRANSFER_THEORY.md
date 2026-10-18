# Unit 8 lane C: nuclear gamma first scattering

The admitted Unit7 source emits 477600 eV photons on the 0.104 excited-state branch. This unit computes their first Compton collision in the same cosmology, including photon redshift before that collision and the exact cold-electron Klein–Nishina redistribution. It produces an electron kinetic-energy source and a remaining-photon source. Later electron thermalization and repeated photon scattering are the next transport dependencies.

Authority requested: Astra; observed runtime identity: UNKNOWN. Parent approved this scope, a z=10000 endpoint, and a cumulative numerical allowance of 30 s. No product code is changed.

## Frozen inputs and constants

Use Unit7 `evidence/be_kinetics_history.csv`, `BE_KINETICS_RESULT.json`, and `DECAY_SPECTRUM_RESULT.json` at the identities in the JSON contract. The positive source measure is raw dF, not the normalized PDF. N_gamma,comoving=nb0*YBe7*0.104*DeltaF. Retain the actual finite DeltaF and direct-Li exclusion.

Use H(z)=H0 sqrt(Omega_r(1+z)^4+Omega_m(1+z)^3+Omega_Lambda) and ne(z)=nb0*Ye*(1+z)^3 from Unit7 metadata. Its values are H0=2.2685455026110557e-18 s^-1, Omega_r=8.53585043761982e-5, Omega_m=0.3000000000000001, Omega_Lambda=0.6999146414956238, nb0=2.47920954940649e-7 cm^-3, Ye=0.8765521883879055. T=2.7255(1+z) K is a diagnostic of the electron bath.

Freeze c=29979245800 cm/s (exact), kB=1.380649e-23 J/K and eV=1.602176634e-19 J (exact), and the CODATA 2022 recommended central values mec2=510998.95069 eV and re=2.8179403205e-13 cm. Set sigmaT=8*pi*re^2/3 consistently; compare the published rounded 6.6524587051e-25 cm^2. The measured electron constants have uncertainty and are not declared exact.

## Differential kernel and independent moments

For x=E/(mec2), mu=cos(theta), and r=Eout/E=[1+x(1-mu)]^-1,

`d sigma/d mu = pi*re^2*r^2*[r+1/r-(1-mu^2)]`, -1<=mu<=1.

This is the unpolarized free stationary-electron kernel. Define sigma0=integral d sigma, sigma1=integral(1-r)d sigma, and sigma2=integral(1-r)^2 d sigma. The collision rate is Gamma0=ne*c*sigma0; the fractional photon-energy-loss rate at fixed E is Gamma1=ne*c*sigma1. Their dimensionless comparisons to expansion are Gamma0/H and Gamma1/H. Mean electron kinetic energy per collision is E*sigma1/sigma0, and the variance is E^2*[sigma2/sigma0-(sigma1/sigma0)^2]. Mean remaining photon energy is E minus the mean electron kinetic energy.

Independently change variable to r on [1/(1+2x),1]. With mu=1-(1/r-1)/x,

`d sigma/d r = pi*re^2/x*[r+1/r-(1-mu^2)]`.

The recoil energy K=E(1-r) has probability density `(d sigma/d r)/(E*sigma0)`. Its support is 0<=K<=E*2x/(1+2x). Integrate number and K moments within each recoil bin; assign outgoing photon energy by E*bin_probability-bin_K_moment, not a midpoint approximation. Every bin then preserves K+Eout=E times its probability. This histogram is the reusable first-collision electron/photon redistribution handoff.

The analytic total cross section provides a third check:

`sigma0=(3*sigmaT/4)*{(1+x)/x^3*[2*x*(1+x)/(1+2*x)-log1p(2*x)] + log1p(2*x)/(2*x) - (1+3*x)/(1+2*x)^2}`.

Use angular quadrature as the primary low-x evaluator, since the closed formula cancels small terms. For the fractional loss use `1-r=x*(1-mu)/(1+x*(1-mu))` to avoid cancellation. Thomson limits are sigma0/sigmaT=1-2x+O(x^2), sigma1/(sigmaT*x)->1, and sigma2/(sigmaT*x^2)->7/5. The last follows from the Thomson average of (1-mu)^2, where <mu>=0 and <mu^2>=2/5. The high-x total tends to (3*sigmaT/(8*x))*(ln(2*x)+1/2).

## Cosmological first-collision distribution

For a photon emitted at z_s with E0=477600 eV, use u=ln[(1+z_s)/(1+z)]>=0. Before its first collision E(u)=E0*exp(-u), z(u)=(1+z_s)*exp(-u)-1. The cumulative optical depth is

`tau(u)=integral_0^u A(v)dv`, with `A(u)=ne(z(u))*c*sigma0(E(u))/H(z(u))`.

The no-collision probability is S(u)=exp(-tau(u)); the first-collision probability is exp(-tau)*d tau. The endpoint u_end=ln[(1+z_s)/10001] supplies tau_end, collision probability -expm1(-tau_end), and remaining no-collision probability. A gamma does not free stream merely because its source is a trace species: this probability depends on the ordinary electron bath.

Avoid under-resolving the short initial mean free path on a uniform cosmological-redshift grid. Integrate the inverse trajectory `du/dtau=1/A(u)`, u(0)=0, and evaluate first-collision averages against exp(-tau)d tau. Compute the independent total tau_end directly by quadrature in u. Use tau_stop=min(tau_end,40); the probability beyond tau=40 is at most exp(-40), and omitted first-collision energy is bounded by E0*exp(-40). If a source node reaches z=10000 before tau=40, stop it at tau_end instead of extending the bath.

For each source epoch, accumulate:

1. C_K=integral_0^tau_stop exp(-tau)*E(tau)*sigma1(E)/sigma0(E) d tau.
2. C_gamma=integral exp(-tau)*E(tau)*[1-sigma1(E)/sigma0(E)] d tau + exp(-tau_stop)*E(tau_stop).
3. C_redshift=integral exp(-tau)*[E0-E(tau)] d tau + exp(-tau_stop)*[E0-E(tau_stop)].

Thus C_K+C_gamma+C_redshift=E0. The unresolved survival term is a carried photon state at tau_stop, not falsely assigned electron energy. If tau_stop=tau_end it is the actual unscattered endpoint state; if tau_stop=40 the remaining error is explicitly bounded. C_gamma consists of photon energy *at first scattering* (and the survival state), not a spectrum transported to a common late epoch. C_redshift is cosmological photon energy loss before first scattering. The ledger is consequently well-defined without pretending to solve later transport.

Report median and 5%,95% first-collision u or z from tau=-ln(1-p), when tau_end admits them; use conditional-on-collision values otherwise. The exact conditional optical-depth quantile is tau_p=-log1p[-p*(-expm1(-tau_end))]. Include source-epoch z10,z50,z90 from Unit7. Numerically check the inverse trajectory by recovering tau(u(tau)) with an independent u quadrature at representative optical depths.

## Actual source weighting and tables

Integrate any C(z_s) against the raw cumulative decay measure. A bounded scheme uses equal-F midpoint quadrature with n=128 and 256 source nodes: F_k=F_start+(k+1/2)*DeltaF/n and raw weight DeltaF/n. Invert the existing monotone piecewise-linear F(z), preserving plateau handling. The physical amplitude remains N0*0.104*DeltaF. This quadrature is not a reset of DeltaF to one. Record convergence of source-weighted energy yields and typical optical depths; if its prescribed tolerance fails, report the discrepancy before changing the contract.

Provide a 257-point log energy table from 1 keV to 1 MeV plus the exact 477.6 keV row: sigma0, sigma1, sigma2, mean K, mean Eout, variance. Provide the normalized 477.6 keV recoil kernel in 256 equal K bins with bin moments. Provide donor-history rate/H and thermal diagnostics at every native history row. Provide a 256-node source-weighted first-collision table, and JSON integrated yields per source gamma, per initial Be7 donor, per cosmic baryon, and per present comoving volume. All these emission-frame transfer units must remain distinct from a present photon energy density.

The first-collision K yield is a rigorous lower bound on cumulative gross photon-to-electron kinetic transfer *within the cold-electron downscattering model*, since later collision contributions are nonnegative. It is not a lower bound on net deposited heat in a finite-temperature plasma. Quote the omitted tau tail and source quadrature error separately.

## Physical validity and next transport algorithm

The bath is fully ionized as inherited from Unit7 and used only at z>=10000. Compute theta_e=kBT/(mec2), sqrt(3*theta_e), and 4*kBT/E at the actual source quantiles and before first collisions. These diagnose the stationary-electron approximation; a numerical integration tolerance is not a thermal/model error bound. At the dominant emission epoch the source gamma is much harder than the electron thermal scale. The low-energy part of the reusable cross-section table is a cold-kernel reference, not an admission of accurate near-thermal cooling. Bound-electron XCOM attenuation and Geant4's empirical per-atom cross-section fit are different targets and are not substituted for ne*sigma0.

Prepared next algorithm: evolve comoving photon number per energy with conservative redshift advection and the gain/loss operator `ne*c*[integral_E^infty n(Ein)*d sigma(Ein->E)/dE dEin - sigma0(E)*n(E)]`. Reuse bin-integrated KN redistribution with its electron-K handoff, and check photon number conservation and photon-loss/electron-gain energy closure at each collision step. Near E~kBT, replace the stationary-electron kernel by a finite-temperature detailed-balance operator; couple energetic electrons to Coulomb/ionization/inverse-Compton cooling before reporting heat. The source-weighted first-collision table supplies concrete initial conditions for that calculation. This unit does not run this multiple-scattering calculation or invent a deposition efficiency.

## Verification and stopping

Use 64-point angular Gauss–Legendre primary quadrature, 128-point refinement, and independent adaptive r-integration at 1,10,100,477.6,1000 keV. Compare sigma0 to its closed form on that domain. Require moment agreement <=1e-9 relative and closed-form sigma0 agreement <=1e-8. Test the three low-x limits at x=1e-6 within 1e-5 relative, and the high-x asymptotic at x=1e6 within 2e-5. Kernel bin count and energy closure must be <=1e-10 relative. First-collision probability and energy ledger closure must be <=1e-8; inverse-tau consistency <=1e-7. Source quadrature refinement must change weighted energy yields by <=3e-4 relative and weighted mean first-collision u by <=1e-3. Record solver/quadrature settings, raw residuals, and total numerical wall time <=30 s. PASS advances to independent scientific review; a substantive violation returns for one targeted diagnosis/repair. No new no-go theorem is asserted.
