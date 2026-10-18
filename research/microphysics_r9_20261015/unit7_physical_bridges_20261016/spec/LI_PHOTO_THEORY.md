# Unit7 lane A: complete the Li I smooth direct-photoionization response

Frozen 2026-10-16. Requested theory authority: Astra; observed runtime identity: UNKNOWN. The construction extends the actual Unit6 32-mixture **two-photon continuum** response to its full support, including LiIII's 91.83842857919419 eV endpoint. Old files are immutable. This is a provider-prescribed smooth direct-ionization model, not a resonance-resolved or charge-yield calculation. Source yields remain conditional incident spectral shapes; no physical H(t), NCP, transport or source luminosity is introduced.

## Source-derived shell selection

Use the original author's `phfit2.f`, Version 2 dated March 25, 1996, as the branch authority. Its source lines 35–67 select PH2 (1996) below the innermost occupied-core threshold and PH1 (1995) above it. For Z=N=3, NTOT(3)=2, NINN(3)=1 and L(1)=L(2)=0. Therefore there are only 1s and 2s partial cross sections. Let Bv=5.392 eV and Bk=64.39 eV.

* E<Bv: both partials vanish.
* Bv<=E<Bk: sigma_2s uses PH2(3,3); sigma_1s=0.
* E>=Bk: sigma_2s uses PH1(3,3,2) and sigma_1s uses PH1(3,3,1).
* sigma_total=sigma_1s+sigma_2s; no occupancy multiplier is applied. The partial fits already represent their ground-state subshell cross sections.

The exact edge belongs to the upper branch, following `e.ge.einn` and the strict below-threshold return. The former Unit6 Emax=64.39 restriction was correct for its isolated 1996 row. It is not the upper validity limit of the combined provider model. In particular **do not continue PH2 above Bk and add PH1(1s)**; that is a different prescription. Do not shift Bk to a different experimental edge or smooth the jump.

For PH1, with t=E/E0 and orbital l,

    sigma_Mb = sigma0 * [(t-1)^2+yw^2]
               * t^(P/2-l-5.5) * [1+sqrt(t/ya)]^(-P).

For PH2, x=E/E0-y0 and v=sqrt(x^2+y1^2),

    sigma_Mb = sigma0 * [(x-1)^2+yw^2]
               * v^(P/2-5.5) * [1+sqrt(v/ya)]^(-P).

Use 1 Mb=1e-22 m^2. Values are read from the downloaded provider bytes and crosschecked with the independent tabulation and old photo.dat:

| Branch | B (eV) | E0 (eV) | sigma0 (Mb) | ya | P | yw | y0 | y1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PH2 2s below edge | 5.392 | 3.107 | 62.45 | 15.01 | 4.895 | 0 | 0 | 0 |
| PH1 2s above edge | 5.392 | 3.466 | 47.74 | 20.35 | 4.423 | 0 | — | — |
| PH1 1s | 64.39 | 27.40 | 156.4 | 33.82 | 1.490 | 0 | — | — |

Only the continuum domain through max(actual Delta) is admitted here. The provider's much wider advertised range is unnecessary for this calculation.

## Deliberate discontinuity

Independent 50-decimal formula evaluation gives the following edge limits in Mb:

    sigma_total(Bk-) = sigma_2s_PH2(Bk) = 0.05189110135229765269415408
    sigma_2s(Bk+) = 0.05099580193561292466846986
    sigma_1s(Bk+) = 3.460013037136730675720974
    sigma_total(Bk+)/sigma_total(Bk-) = 67.66109694291315901525.

The dominant total step is the new K-shell channel; the outer-shell prescription also changes by about -1.725%. These are facts of the chosen fit, not precise predictions of the real near-edge spectrum. Export both one-sided limits, the exact-edge branch and shell changes. Split every numerical integral at Bk. Quadrature nodes must not straddle this jump as a single smooth interval. The measure-zero choice at the edge does not change continuum integrals, but is tested separately.

## Actual source and response construction

Read the original Unit6 local input copies and its saved response CSV. Reconstruct the source from each actual saved mixture P=terminal_2s_probability and actual transitions' unique 2p->1s energy Delta:

    w=y(1-y), g(y)=w[1-(4w)^0.8]+0.88*4^0.8*w^2.33,
    I=0.08144613055216544, f(y)=g(y)/I,
    S(E)=2P*f(E/Delta)/Delta on [0,Delta], zero outside.

This is precisely the prior normalized literature fit; do not fit the tabulated spectrum or renormalize numerical integrals. The prior fit accuracy and infinite-mass LiIII limitation remain. The 32 rows are eight saved species times n=3,5,10,12. Reuse Unit6's independently checked reservoirs; verify actual P*Delta against saved reservoir energy and recover total photon/energy moments. This lane changes opacity, not the source or source time evolution.

Take the same hypothetical incident normalization F_E=J*S(E), J=1 precursor-equivalent m^-2 s^-1. For shell a with threshold Ba define, for each band,

    G_a = integral S(E)*sigma_a(E) dE                         [m^2],
    W_a = eV_J*integral S(E)*sigma_a(E)*E dE                  [J m^2],
    K_a = eV_J*integral S(E)*sigma_a(E)*(E-Ba) dE             [J m^2],
    Q_a = eV_J*Ba*G_a                                       [J m^2].

G is the direct absorption-event coefficient (also primary-electron count within this direct single-electron model). K is the primary photoelectron kinetic-energy coefficient, not a thermal heating rate. Q is the shell-threshold/configuration-energy bookkeeping coefficient. For each shell W_a=K_a+Q_a; sum shells to form totals. At unit J the same numbers give events/s and J/s per target in the stated hypothetical illumination. Do not infer flux from precursor yield alone.

A useful decomposition separates the ground-state Li I ionization cost and core excitation:

    Q_total = eV_J*Bv*G_total + X_core,
    X_core = eV_J*(Bk-Bv)*G_1s,
    W_total = K_total + eV_J*Bv*G_total + X_core.

Export X_core explicitly. If the legacy valence subtraction is evaluated as L=W_total-eV_J*Bv*G_total, then L=K_total+X_core. Above the edge, calling L primary kinetic energy would overcount it by 58.998 eV per 1s event. The decomposition is within this shell model, not a resolved final-state spectrum.

Required disjoint bands are sub_Lyman=[Bv,13.6], upper_old=[13.6,Bk], extension=[Bk,Delta], each clipped to source support. Also export covered_total=[Bv,min(Bk,Delta)] and full_total=[Bv,Delta]. Empty bands are exact zero. Save all three quadrature levels for each mixture, shell (1s,2s,total) and band. Export source photon/energy in the extension, fraction of full response arising in the extension, fractional increase over the old covered response, shell contribution fractions and cross-section-weighted mean absorbed energy wherever denominators are positive (otherwise null, never NaN).

Reproduce old authoritative sub_Lyman and covered_total Gamma/H/Abs for every row: new G_total agrees with old Gamma, new K_total with old H, new W_total with old Abs. In these old bands only 2s contributes except the measure-zero endpoint. Species with Delta<Bk must have zero extension and unchanged full response. For LiIII the extension is positive and the former uncovered source band is fully assigned within this fit model. No E1 line-response expansion is requested in this lane.

## Physical interpretation boundary

The 1996 near-threshold fit is smoothed over resonances, and the high-energy partials are an independent-particle HDS fit. Neither table nor phfit2 specifies resonance structure, shake channels, fluorescence branching, Auger yields, final charge fractions, electron thermalization or secondary ionizations. Consequently the code exports direct absorption and the above energy bookkeeping; it must not infer a LiII/LiIII branching fraction or convert all shell energy to heat. In particular do not assign an Auger yield of one to Li's K channel simply by analogy with heavier atoms. A future relaxation calculation needs appropriate Li final-state data and energetics. No uniform physical percent error is certified for the near-edge extension by our numerical convergence.

## Bounded implementation and tests

Implement a compact C99 kernel with Python driver, or an equally small stdlib Python implementation, reconstructing the Li rows from the supplied source data and provider branch. Pure Python is permitted to reuse the already validated Unit6 numerical helper for Gauss–Legendre nodes. Preserve source bytes and record hashes in outputs. No old file is modified. Source reconstruction output records actual parsed PH1/PH2 rows, their comparison with table1.dat/photo.dat, and the effective branch rules.

Use 64,128,256 Gauss–Legendre nodes per smooth clipped interval; final=256, compare128/256. Split at Bv,13.6,Bk,Delta. Required tolerance is 1e-8 relative with response floors 1e-35 m^2 and 1e-53 J m^2; source moments floor1e-14. Shell/energy algebraic closures require1e-11 relative using those floors. Direct kernel-vs-independent Decimal/log-form references require1e-11 relative, absolute floor1e-30 Mb; exact-zero and branch selection tests use exact expected zero.

If gfortran is available, compile the unmodified public phfit2 source as a separate oracle, preserving native REAL precision. Test shell1/2 and unoccupied shell3 on a grid including 5.391,5.392,5.393,13.6,40,64.389,64.39,64.391,80,Delta. Compare1e-5 relative (floor1e-7 Mb), appropriate to the source's single precision. Pass the same float32-rounded energies to the port when comparing oracle branches; evaluate the double-precision exact mathematical boundaries separately. If no compiler is available, report `public_Fortran_execution: NOT_RUN_compiler_unavailable`, retain the original source and use a direct source-derived port plus independent 50-decimal formula checks and explicit branch truth-table tests. Do not describe fallback as executed Fortran. No compiler installation or package change is needed.

The independent check also integrates each species' three full-response quantities using a distinct quadrature route (existing SciPy if available; otherwise adaptive Simpson on each smooth band with endpoint handling and adequate error estimates). Evaluate this once per species with P=1 and scale for mixtures, avoiding32 redundant integrations. It must compare event, absorbed-energy and primary-kinetic integrals, not just a point cross section. All numerical commands<=30s and combined numerical run<=30s, threads1. Finite quadrature ladder; no automatic expansion. Stop after one implementation/validation pass; return a concrete failure for authority interpretation, allowing at most one specifically authorized repair. PASS advances to independent Astra review and scoped admission of this smooth conditional response only.
