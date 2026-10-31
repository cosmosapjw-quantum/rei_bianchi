# REI F4 Physical Fast: BASS193 Li II 2E1 causal photon-source memory

2026-10-31. One original-source frozen-background constructive theory+coding science unit; no IVP, no native REI17 full F/J replacement. Original source parent PR305 SHA `27b00a2e6bb0d96bcbdad8bc0520c8cc61c32126`; read-only sibling PR304 `ee0a488a4eef93cf316c01395604db0be4d7ad00`. BASS native atomic source owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. Original BASS21 193×21 Y source SHA `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`. Original PR302 18528-row full first-flight kernel SHA `d7ca818ce55835f8c38408e4c575f42d6529d6e225aab346fad76709b4354538`; FS2010 UCLA raw TAR SHA `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101`.

## Actual source-linked physical construction

Use original physical 2E1 singlet conditional emission Q_k pairs/original baryon, k=0,...,192. Each pair makes two photons with complementary energies E_gamma=y E_2E1 and (1-y) E_2E1, E_2E1=60.922559447552 eV. The photon transport/first-photoabsorption operator was previously computed on frozen BASS193 state history (T,nb,opacity,H,redshift). Define source-independent per-pair first-absorption transfer K_{jks} for arriving in interval j at absorber class s from emission k. Original source records give every k<=j<192, 18528 potential links. For frozen opacity/background only:

    N_{j,s} = sum_{k<=j} K_{jks} Q_k,
    K_{jks} >= 0, sum_{j>=k,s} K_{jks} <= 2,
    N_j = sum_s N_{j,s},
    R_k(z=2) = 2 Q_k - sum_{j>=k,s} N_{j,s,k} >= 0.

Then exactly in the discrete original source model, sum_j N_j + sum_k R_k = 2 sum_k Q_k. R counts photons not first absorbed **by z=2**, not photons ultimately escaping to infinity or an energy reservoir. Original final emission Q_192 has no subsequent interval and is retained fully in R. Proper time is the original BASS elapsed_s, Δt_j=t_(j+1)-t_j; the source-normalized electron creation rate from the *modelled one-electron-per-first-photoionization* is N_j/dt_j [baryon^-1 s^-1] or N_j/(rho_j dt_j) [Href^-1 s^-1] where rho=nHref/nb. The latter is a diagnostic source port only: it is NOT added to any existing BASS/REI photon photoionization operator; the final LiI Auger/multielectron yield is unresolved.

For emission and absorption clocks the within-cell event time is not available in the preceding aggregated kernel, hence only the exact interval bracket t_j - t_k <= delta t_event <= t_(j+1)-t_k is reported; midpoint age is NOT an exact delay. No local Markovian J was inferred from this causal operator: the frozen-kernel derivative with respect to emissions is K, but the chemical-state functional derivative additionally depends on historical opacity variations. It requires independent photon state or causal Volterra-memory treatment. An arbitrary instantaneous 21×21 J would not represent its historical response.

## Computed values on original source

- Conditional original injected 2E1 pairs: 2.544374180157812e-12 /baryon; 2Q=5.088748360315624e-12 emitted photons/baryon.
- First absorbed up to z=2: 4.374110632809564e-12 photons/baryon, with first-generation kinetic energy 6.749242464433259e-11 eV/baryon. Not absorbed by z=2: 7.1463772750606e-13 photons/baryon (14.043487256692258% of emitted photons).
- H I: 2.678569652103253e-12, He I: 1.6028839907664316e-12, He II: 9.265669938712474e-14, Li I: 2.905527545664037e-19 first absorption events/baryon. These are original first-flight event categories, not uniquely H1 vs D vs T or He3 vs He4 isotope-resolved F states.
- Source contribution from emission k<arrival j: 0.00592205805631089 of all first absorption events, 0.008901664954473112 of primary electron kinetic energy. This is exact in the inherited 16-point spectral quadrature/four substep original discretization.
- 103/192 arrival intervals have >50% delayed origin, but together account for only 0.003684925004268388 of all first-absorption events. Thus small **integrated** local-in-time truncation error does not certify pointwise/local chemical source accuracy.
- Event-count-weighted lag has only a rigorous within-bin bracket 5.556707409480696e5 to 8.812095227143338e6 years; energy-weighted bracket 5.025081049512809e5 to 8.740957030125812e6 years. These are broad interval bounds, not a measured mean lifetime or photon mean free path.
- Maximum first-generation point-source rate = 1.623053027425852e-27 per original baryon per proper second at arrival index 71 (z roughly 9.23 to 9.12); not an increment to the actual BASS F of an evolved solution.
- Original BASS21 weak Jacobian J[H1II,n]=1/878.4 s^-1 is preserved untouched. Charge/baryon source counts are scalar class moments, with no assumed isotope partition or missing native REI17 F/J owner.

## Conditional FS2010 original-grid thermal-memory result

For explicitly artificial one-parameter projection x_i=xHII with x_i in original FS2010 [10^-4,0.999] only (87/192 arrival intervals), use actual FS2010 table's piecewise-bilinear model with initial photoelectron energy moments per original PR302 category. For unknown energy distribution in band b, fheat,min(E,x_i), fheat,max(E,x_i) are the exact extrema of this fixed piecewise-bilinear interpolation in the rectangular band × saved xHII-start/end, so E-weighted bounds are valid **only for this projected table model**. Its extra photon-memory support is 2.4255125090344433e-13 to 2.425689707500973e-13 eV/baryon, comprising a rigorously enclosed fractional range 0.3626453779156885% to 0.3645017228270467% of the same 87-bin projected total model heating. Original PR305 87-bin heat bound independently reproduced exactly to <2e-22 eV/baryon: 6.654809992906245e-11 to 6.688386662957417e-11 eV/baryon.

**DO NOT** promote this to native BASS heating: original BASS HII/HeII/HeIII chemical fractions do not inhabit the FS2010 single-x_i helium manifold in any 192 bins. Beyond x_i author table limits, FS heat is not extrapolated. No evolved gas temperature, no full hybrid REI17 F/J, no CMB tau, no optical-depth or observational likelihood.

## Evidence and current DAG

Source input exact SHA guards; 30 targeted Python source/physics/adversarial tests with no tolerance relaxation; finite 4×4 Wolfram symbolic causal transfer budget reduces identically to zero. Independent native subagent unavailable, distinct-author R6/C9 NOT_RUN; one bounded same-author hostile check. 5 real scientific PNG/SVG figure pairs. Original old source archives unchanged. Test/readback and remote delivery identities in finalized manifest and delivery receipt.

WORKING=33/88; CENTRAL=28/88; PHYSICAL_FAST=4/7; CANONICAL_PHYSICAL_DELTA=0; AUXILIARY=1/1_SOURCE_SCOPED. F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; NO_MORE_IVPS=true; NO_MERGE=true; NO_FORCE_PUSH=true; NO_BUDGET_RESET=true; AUTO_NEXT_NODE=false.

Next authorized candidate: identify actually native isotope-complete REI17 F/J and full reaction owner, properly split photon first-flight source into isotope-resolved stoichiometric channels without double count, with common electron bath, neutron weak J, original rho,H,K,proper clock, IC and actual species-aware energy deposition. Only a valid new common-source physics test may advance central DAG.

Primary references: G.W.F. Drake, G.A. Victor, A. Dalgarno (1969), Phys Rev 180,25, DOI 10.1103/PhysRev.180.25; S.R. Furlanetto, S.J. Stoever (2010), MNRAS 404,1869–1878 DOI 10.1111/j.1365-2966.2010.16401.x; C.M. Hirata, E.R. Switzer (2008), Phys Rev D 77,083007 DOI 10.1103/PhysRevD.77.083007. Native-operator numeric outputs derive exclusively from immutable BASS/REI first-party sources, not these papers.
