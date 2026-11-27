# BASS_HE | HE-DD source-gated physical transport bridge | 2026-10-30

## Frozen sources and epistemic status

Parent PR113 HEAD `da989b83bb37ee4256a1a80ba9400dfe48559084`; parent PR112 HEAD `a03c1eee365c9b796fef137b81a4347ad44008d1`. Immutable IAEA EXFOR M0475.x4 source: IAEA-NDS/exfor_master @ `939a14d7bba1ddce51975cb5e8711ce96b3b0871`, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`, 3349 bytes. PR113 exact compact atlas Git blob `293cb5d6937cf6c84584cb8d6f0a37336f50535f`. Original source is 12 DA rows (E_gamma=213,258,330 MeV; theta_CM=46,61,73,87 degrees) and 6 reported SIG rows (201,225,253,285,320,359 MeV). No measured 330 MeV total SIG. Source ERR-S are pointwise statistical errors only.

Original Arends et al. Phys. Lett. B 62 (1976) 411-412, DOI:10.1016/0370-2693(76)90671-7, article metadata and EXFOR experiment description inspected, but paywalled full original methods NOT acquired. Silverman et al. Phys. Rev. C 29 (1984) 35, DOI:10.1103/PhysRevC.29.35, abstract verified: inverse d+d -> alpha+gamma measured at incident T_d=376 MeV, theta_gamma(CM)=73 and 91 degrees, comparison with Arends ratio 2.0±0.9 and 1.7±0.9 (large uncertainties). These data do NOT establish detector efficiency, polarization corrections, or 330 MeV sigma_event.

## Derived statistical model, NOT a measured new datum

Linear interpolation of reported EXFOR SIG on E=[320,359] MeV:

    sigma_reported^lin(330)=29/39 * (0.61 nb) + 10/39 * (0.55 nb)
                              =773/1300 nb = 0.594615384615... nb.

Let e_320=0.16 nb and e_359=0.15 nb denote EXFOR ERR-S. With unknown correlation rho,

    Var_stat(sigma^lin)= (29/39 e_320)^2 + (10/39 e_359)^2
                         + 2 rho (29/39 e_320)(10/39 e_359).

Conditional independent-point SD = 0.125036746735... nb; allowing any rho ∈ [-1,1], SD interval [157/1950,307/1950] nb, i.e. [0.0805128205,0.1574358974] nb. Statistical correlations are not measured here; those are covariance-dependent bounds, not a confidence interval for the true 330 MeV cross section.

For an assumed C^2 underlying sigma_reported(E) on [320,359] MeV, Lagrange interpolation remainder:

    sigma_true(330)-sigma^lin(330) = sigma''(xi)/2*(330-320)*(330-359)
                                  = -145 MeV^2 * sigma''(xi), xi in (320,359).

An externally justified curvature bound M_2 [nb/MeV^2] would imply |model bias|≤145 MeV^2 M_2. No such bound established; the interpolation-model systematic is UNKNOWN. The source's finite energy-bin response and detector systematic are also unresolved. This is source-conditional SIG_reported only, NOT SIG_event, not an independently measured 330 MeV datum, and not a viable cross-section closure for production.

Multiplying this model estimate by the exact pair-born energy K_pair=330-Q=306.1535218 MeV gives the *model diagnostic* 182.043594116... nb MeV, NOT heat, NOT energy injection rate.

## Exclusive event measure and daughter push-forward

Metric (-,+,+,+); M=M_alpha c^2=3727.3794118 MeV; m=m_d c^2=1875.61294500 MeV; Q=2m-M=23.8464782 MeV. A photon impinging on resting He has s=M²+2ME, q*=sqrt(s/4-m²), and E_thr=Q+Q²/(2M). For one event choose one of the two back-to-back CM directions Omega_* and take only a representative hemisphere H (except measure-zero boundary). Daughter momenta in the He proper frame are

    p_±^0 c=(M+E)/2 ± (E/sqrt(s)) q* mu
    (p_± c)_parallel=E/2 ± ((M+E)/sqrt(s)) q* mu
    (p_± c)_perp= ±q* sqrt(1-mu²) (cos(phi), sin(phi)).

Here p^0 c means relativistic particle energy in MeV. The unordered identical-D event contributes the distributional kernel

    J_D(p|E,Omega_*)=delta^3(p-p_+)+delta^3(p-p_-).

Consequently ∫d³p J_D=2; ∫d³p K(p) J_D=E-Q; ∫d³p p J_D=k_gamma; and both daughters are on-shell. The hemisphere H prevents counting the same event twice, while both daughters still enter the injection. If an inclusive-D cross section uses the full sphere, its integral equals 2 sigma_event only when the same experiment's calibrated definitions correspond to the constructed inclusive measure. The EXFOR SIG/DA normalization relative to this event measure must be source-locked first; do NOT set kappa=1 or 2 by inspection.

## Proper-frame event source, transport and heat, conditional theory only

Let n_gamma^(alpha)(E,Omega;x) [cm^-3 MeV^-1 sr^-1] be actual energetic-photon number density in the target-alpha proper frame (energy E=-p_gamma.u_alpha). If gamma polarization enters the differential event cross section, write its state as P_gamma(E,Omega;x). For physical source-qualified d sigma_event/dOmega_* [cm²/sr] on the representative H,

    S_D(x,p)=n_alpha c ∫dE dOmega n_gamma^(alpha)(E,Omega;x)
              ∫_H dOmega_* (d sigma_event/dOmega_*)(E,Omega_*,P_gamma)
              [delta³(p-p_+)+delta³(p-p_-)].

The resulting number and born-kinetic-energy rates are

    dot n_D|born = 2 R_event,
    qdot_D,kin|born = n_alpha c ∫dE dOmega n_gamma^(alpha) sigma_event(E,Omega,P_gamma) (E-Q).

For unpolarized isotropic photons only, n_gamma(E)=∫dOmega n_gamma(E,Omega), so R_event=n_alpha c∫dE n_gamma(E) sigma_event(E). Units: R_event [cm^-3 s^-1], qdot_D,kin [MeV cm^-3 s^-1]. The collision operator in Bianchi requires the local tetrad, target rest-frame distribution, angular dependence and expansion/shear transport, not an unqualified homogeneous isotropic photon replacement. UV background photons are not a substitute for a real ∼330 MeV photon population.

For nonthermal D distribution F_D(t,x,p) [cm^-3 (MeV/c)^-3], the necessary kinetic equation is

    partial_t F_D + div_x(dot x F_D) + div_p(dot p F_D)
       = S_D + C_redist[F_D; background] - C_react[F_D; background].

Stopping/ionization, Coulomb transfer, nuclear redistribution, expansion/redshifting, escape, and the energy of secondary particles must be separately accounted for. Define b_heat(p) [MeV/s] as *actual heat credited from a D* after solving secondary energy deposition, not simply minus total D kinetic-energy loss; then qdot_heat = ∫d³p b_heat(p) F_D plus properly traced secondary channels. Born kinetic energy is neither instantaneous thermal heat nor guaranteed fully deposited heat. For fixed-composition nonrelativistic ideal gas C_V=(3/2)n_tot k_B [MeV cm^-3 K^-1]; with ionization or changing species use the actual derivative C_V=(partial u_th/partial T)_{composition,volume} and chemical/ionization energy ledger. The temperature equation also contains -p_th Θ and other cooling/source terms.

## Validation and admission

New bounded Python 8/8 targeted tests and compileall PASS, including every original measured DA coordinate for two azimuths; verify daughter_count=2, four-momentum and each mass shell to specified 80-digit numerical accuracy, source-byte-mismatch rejection, and uncertainty algebra. Wolfram independent algebra verified 330 interpolation, covariance extrema and exact energy/longitudinal-momentum cancellation. New work does not perform original IVP, 4501-node LP or full production suite. Distinct-author R6 and C9 NOT_RUN (no native subagent tool). The actual PR113 atlas is source-locked by Git blob at runtime; the local targeted tests use exact cited EXFOR tabular coordinates but did not execute the end-to-end source-atlas loader because container access to the GitHub raw bytes was unavailable. No runtime event-rate or D transport model is activated.

Preserved: Central 28/88; HE 14/18; measured 2/2 scoped; physical_delta=0. kappa=null; R_event=null; heat_rate=null; physical_activation=false; L4=false; production=HOLD. Next physical step is authenticated original Arends/Silverman detector calibration and event counting, target-proper MeV photon phase space, and a validated named D stopping/redistribution + deposition kernel with heat capacity.

References:
- Exact EXFOR: https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4
- Arends original DOI: https://doi.org/10.1016/0370-2693(76)90671-7
- Silverman original DOI: https://doi.org/10.1103/PhysRevC.29.35
- EXFOR interpretation: https://www-nds.iaea.org/nrdc/nrdc_doc/iaea-nds-0208-202505.pdf
- Cosmic-ray plasma and neutral-gas stopping example (not calibrated D kernel): https://academic.oup.com/mnras/article/469/1/416/3098184
