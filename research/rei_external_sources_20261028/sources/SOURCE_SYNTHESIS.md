# External photon, particle and isotope sources: R2–R3 synthesis

2026-10-28. This source lane supplies usable constitutive forms and identifies their calibration domains. It does not compute a new global trajectory. `SKILL_CONTEXT_USED.json` records PhysMath Research Loop 1.3.0, selected R2–R3 and integrated policy context. Selected SciSpace and Exa were both actually used; compact retrieved evidence is preserved alongside this file.

## 1. Six-source intake and status

| Source | Formula/data location | Admitted reuse |
|---|---|---|
| Zier et al., Lumina, [MNRAS stag1469](https://academic.oup.com/mnras/article/552/4/stag1469/8971942), published 26 October 2026 | Sections 3.2–3.4; equations 10, 15–17; Table 1; Data Availability | Stellar/AGN/ISM source construction, finite photon bands, source-dependent opacity weighting. Calibration belongs to Lumina. |
| Haardt & Madau 2012, [arXiv:1105.2039](https://arxiv.org/pdf/1105.2039) | Section 2 equations 1–4; section 6 equations 37–38; section 8 equations 51–54 | Proper-emissivity radiation transport, absorber opacity, historical fitted AGN/SFR shapes. |
| Puchwein et al. 2019, [arXiv:1801.04931](https://arxiv.org/abs/1801.04931) | Abstract and listed ancillary `rates_fiducial.txt`, `rates_eq-eq.txt`, `TREECOOL`, `readme.txt` | Existing rate-table option; physical non-equilibrium rates and equivalent-equilibrium rates must not be confused. This lane located but did not download/validate table bytes. |
| Strong & Moskalenko 1998, [author full text](https://ar5iv.labs.arxiv.org/html/astro-ph/9807150), DOI 10.1086/306470 | Appendix A equation A.1 and secondary-source paragraph; Appendix C.1 losses | Transport/source/loss architecture. Galactic B/C/Be calibration is not an intergalactic neutron/tritium calibration. |
| Depta, Hufnagel & Schmidt-Hoberg 2021, [ACROPOLIS](https://export.arxiv.org/pdf/2011.06518) | Section 2.1 equation 2.3, Section 2.2 and Table 1 | Photonuclear thresholds and energy-resolved production/cascade architecture; no imported BSM injection amplitude. |
| Strumia & Vissani 2003, [arXiv:astro-ph/0302055](https://arxiv.org/pdf/astro-ph/0302055) | Sections 2–3; equations 17–18, 25 | Inverse-beta threshold and cross-section convolution; requires an actual antineutrino distribution. |

The original requested Lumina article was readable through Exa. Its data statement promises full public data in 2028 and points to [the project website](https://www.lumina-simulation.com) for some figure data. The website was readable, but no numerical figure data were retrieved or validated here. A guessed `/data` route returned `CRAWL_NOT_FOUND`; this does not establish absence of data. No author contact was made. A separate web-open fallback failed while Exa retrieval succeeded.

## 2. Photon source and absorption contract

Let J_nu be energy specific intensity [energy time^-1 area^-1 frequency^-1 sr^-1], epsilon_nu proper-volume emissivity [energy time^-1 volume^-1 frequency^-1], and kappa_nu absorption per proper length. HM12 equations 1–4 give

    (partial_t - H nu partial_nu) J_nu + 3 H J_nu
        = -c kappa_nu J_nu + c epsilon_nu/(4 pi),
    J_nu0(z0) = c/(4 pi) integral_z0^infinity dz/[H(z)(1+z)]
        [(1+z0)/(1+z)]^3 epsilon_nu(z) exp[-tau_eff],
    nu = nu0 (1+z)/(1+z0),
    tau_eff = integral dz dN_HI f(N_HI,z) [1-exp(-tau_cloud)],
    tau_cloud = N_HI sigma_HI + N_HeI sigma_HeI + N_HeII sigma_HeII.

A homogeneous local closure instead uses kappa_nu=sum_i n_i sigma_i. The cloud-distribution closure and local homogeneous opacity are alternatives at the chosen averaging scale. Do not apply their attenuation factors twice. Converting a comoving luminosity density to epsilon_nu multiplies by (1+z)^3 once.

Direct event bookkeeping from this intensity convention gives

    Gamma_i = 4 pi integral_nu_i^infinity J_nu sigma_i(nu)/(h nu) dnu,
    r_photo,i = Y_i Gamma_i                         [events/baryon/proper s],
    H_primary = sum_i n_i 4 pi integral J_nu sigma_i/(h nu)
                       (h nu-chi_i) dnu.

The last expression is primary photoelectron excess power, not automatically thermal heating: nonthermal electron excitation, secondary ionization, radiation and heat require an energy-partition closure. Absorption removes one photon per event; emitted recombination/decay photons need an explicit escaping or transported owner. Prescribed J_nu already includes its source history: adding its underlying epsilon_nu as a second forcing double counts it.

Useful emissivity inputs:

- Stellar population: epsilon_nu,com(t)=f_esc(nu,t) integral_0^t dtau SFRD(t-tau) l_nu[tau,Z(t-tau)]. This is the HM12 equation 51 construction generalized in frequency. Lumina section 3.2.1 uses BPASS v2.2.1 binary age/metallicity tables and cumulative photon-yield differences. Its f_esc=0.18 is a simulation calibration, not a measured universal constant.
- A reusable historical AGN shape is HM12 equation 37: epsilon_912,com=10^24.6 (1+z)^4.68 exp(-0.28z)/[exp(1.77z)+26.3] erg s^-1 Mpc^-3 Hz^-1. The stated fit comparison is 1<z<5. Equation 38 has L_nu proportional to nu^-0.44 above 1300 Angstrom and nu^-1.57 below. HM12 explicitly treats X-rays separately; do not extend this UV slope arbitrarily to MeV energies.
- Lumina section 3.2.2 uses L_bol=epsilon_rad(1-epsilon_f,high) Mdot_BH c^2 and equation 15 L_observed/L_bol=0.3[L_bol/(10^46 erg/s)]^0.07, with a composite AGN SED and no additional source-level escape factor. Missing BH population/accretion history leaves the amplitude uncalibrated here.
- Lumina equations 16–17 prescribe an ISM energy-luminosity shape g(E)=1 below 240 eV and (E/240 eV)^-3 above, normalized over 13.6–2000 eV to 3.3e40 erg/s per Msun/yr. Correct dimensional use is L_E=L_band g(E)/integral_band g(E)dE; number emission is L_E/E. HMXB SEDs and metallicity-dependent luminosity/SFR require their external tabulations, not this ISM formula.

Lumina Table 1 provides spectral-bin-averaged cross sections and excess energies for 13.6–24.59, 24.59–54.42, 54.42–100, 100–200, 200–500, and 500–2000 eV. They are weighted by named source SEDs. They cannot be used as spectrum-independent atomic cross sections. Its switch at z=4.75 and neglected secondary ionizations are declared simulation choices. None of those photon bands reaches the nuclear thresholds below.

## 3. Energetic n/T production, slowing, thermal handoff and escape

Adopt a physical differential fast-particle density N_i(E,t), with E kinetic energy per particle. The following spatially averaged equation is a direct reduced continuity construction, using the transport/loss architecture of Strong–Moskalenko Appendix A:

    partial_t N_i + 3H N_i + partial_E[dotE_i N_i]
        = Q_i(E,t) - [lambda_i/gamma_i + k_dest,i(E,t)
                     + tau_esc,i^-1(E,t)] N_i,
    dotE_i = -b_coll,i(E,t) - H p_i v_i,
    k_dest,i = sum_a n_a v_i sigma_dest,ia,
    Q_i(E,t) = sum_(projectile p,target a) n_a integral dEp
        N_p(Ep,t) v_p(Ep) d sigma_(pa -> i+...)(Ep,E)/dE.

The daughter-inclusive differential cross section includes multiplicity. Use either N_p v_p or 4 pi j_p for an isotropic differential intensity j_p, not both. A per-nucleon input spectrum requires the energy Jacobian before insertion. The H p v energy-loss term assumes isotropic FRW momentum redshift; an anisotropic Bianchi calculation must retain directional transport or explicitly adopt an angular closure. Strong–Moskalenko's spatial diffusion and convection are replaced here only by a declared phenomenological escape time. Neutrons can escape ballistically; charged tritons need a magnetic transport model.

For a chosen thermal/fast boundary E_th with downward energy flux, the number entering the thermal inventory is

    S_i,thermal = [-dotE_i(E_th) N_i(E_th)] / n_B.

This boundary must be included as a loss of the fast component and a gain of the thermal one. Treating all energetic production as thermal instantaneously is an optional closure, not a stopping calculation. Catastrophic nuclear channels produce daughter source kernels as well as parent losses. Slowing time integral dE/b, decay hazard integral lambda/gamma dt, and escape hazard determine the surviving thermal handoff.

Baryon/charge-allowed examples include p+He4 -> p+He3+n and p+He4 -> 2p+T. Their amplitudes are **missing** without projectile intensity, target state and energy-dependent yield data. The preserved CR113 0.1–10 eV atomic-electron marginal is not such a provider. No n/T production cross-section calibration was newly installed.

ACROPOLIS Table 1 supplies thresholds: D(gamma,n)p 2.22 MeV; T(gamma,n)D 6.26 MeV; He4(gamma,p)T 19.81 MeV; He4(gamma,n)He3 20.58 MeV; Li7(gamma,alpha)T 2.47 MeV. For isotropic photon number density n_gamma(E), r_(a,gamma)=Y_a integral c n_gamma(E) sigma(E)dE. A 5–60 eV or 13.6–2000 eV finite spectrum therefore has exactly zero support for these channels; extending the spectrum introduces new required input.

## 4. Reuse decay/capture inputs; distinguish weak channels

The frozen recovered source remains authoritative: neutron mean lifetime 878.4 s, tritium half-life 12.312 years with 365.24219878 days/year; lambda_n=0.001138433515482696 s^-1 and lambda_T=1.784030041121361e-9 s^-1. Thermal 2200 m/s captures use p(n,gamma)D 0.3326 b, D(n,gamma)T 0.000519 b, He3(n,p)T 5328 b, and Li6 absorption 940 b as its stated dominant-branch approximation. Their 1/v continuation and bare, instantaneously thermalized nuclei remain conditional. Do not replace 5328 with 5327 or import a different year convention. DD constants S_DDp=50.8 and S_DDn=51.0 keV b are retained, not refitted.

For thermal survival, k_n=lambda_n+sum_a n_a<sigma v>_na+tau_esc^-1, and P_survival(t,t0)=exp[-integral k_n dt]. Replace lambda by lambda/gamma for energetic propagation. Creation and disappearance act together; a lifetime alone is not a population prediction.

- Beta-minus: n -> p+e-+anti-nu_e and T -> He3+e-+anti-nu_e. The frozen nuclear source owns these events; omit the duplicate atomic decay matrix. Ionic daughter branching and bound-state decay corrections are not supplied by isotope-total lifetimes.
- Antineutrino inverse beta: anti-nu_e+p -> n+e+, threshold E_thr=[(m_n+m_e)^2-m_p^2]c^2/(2m_p), approximately 1.806 MeV. Rate per proton is integral differential_flux(E) sigma_IBD(E)dE (or c integral n_nubar sigma). Strumia–Vissani equations 17–18 define the convolution; equation 25 supplies a convenient MeV-range approximation. Their exact kinematics should be retained near threshold. No antineutrino amplitude is available here.
- Free-proton electron capture: p+e- -> n+nu_e has stationary-proton threshold K_thr=[m_n^2-m_p^2-m_e^2]c^2/(2m_p)-m_e c^2, approximately 0.783 MeV. This formula is a direct two-body invariant derivation. It is not antineutrino inverse beta and needs its own energetic electron bath and cross section. Nuclear bound-electron capture also needs isotope/Q/occupancy-specific data; this free-proton threshold cannot be applied to it.
- The exact time reverse of three-body beta decay is a three-body absorption process. Drawing a reversed arrow does not generate any of the above two-body rates.

## 5. Injected isotope and charge-state accounting

The following are direct number/charge continuity identities, not new literature calibration. Index an ion by (A,Z,q), where q is the positive ionic charge. An isotope-total source S_(A,Z) [proper volume^-1 time^-1] can populate ionic states only after supplying P(q|A,Z,E,t), sum_q P=1. Without P, report isotope totals and leave TI/TII unresolved. A fully stripped injection is a declared limiting model, not a measured branch distribution.

If sources add/remove baryons, define S_B=sum_i A_i(S_i,in-S_i,out) and evolve

    dot n_B + 3H n_B = S_B,
    dot Y_i = [R_i + S_i,in - S_i,out - Y_i S_B]/n_B.

Here R_i is the internal reaction number source and sum_i A_i R_i=0. At fixed prescribed n_B, every physical matter injection instead requires a compensating reservoir/outflow or an explicitly tracer-only interpretation. The normalization term cannot be silently omitted while claiming a closed sum A_iY_i=1.

Net charge added by ions is e sum q_i S_i; local neutrality requires the corresponding free-electron/positron or boundary-current ledger. For bare beta-minus decay, the nuclear charge rise of one is balanced by one electron; for an ion with spectators/shake-off, daughter charge and released electrons must be accounted together. Available Q plus absorbed incident energy is allocated once among daughter kinetic energy, leptons, neutrinos, photons, ionization/excitation and heat. Electron number production is not identical to immediate thermal ionization; Q is not identical to heat.

## 6. Concrete use classification

**Existing calibrated/evaluated inputs:** frozen nuclear lifetimes/captures and their exact original conventions; historical UVB/AGN model fits only within their cited domains. No new empirical n/T source data.

**Reusable shapes:** proper-volume radiative transfer, stellar-age convolution, finite Lumina photon bands and source spectra, differential cosmic-ray production, slowing/escape and weak flux convolution.

**Placeholder amplitudes if used next:** arbitrary nonnegative A_star(t), A_AGN(t), A_CR(t), or injected isotope S_i(t). Give units, normalization and support; label them phenomenological. A nonzero response to them tests model behavior, not a physical cosmological abundance.

**Missing inputs for physical coupling:** actual stellar/BH/CR histories, nonthermal nuclear yield kernels and transport, isotope charge branches, ionic weak rates/endpoints, energy deposition, compensating matter/charge flow and source radiation feedback. These omissions do not prevent a bounded parameterized source-response calculation. They prevent promoting it to a calibrated global prediction.
