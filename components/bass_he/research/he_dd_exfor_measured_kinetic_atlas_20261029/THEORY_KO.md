# HE-DD M0475: measured-coordinate kinetic-energy-weighted data
2026-10-29. Parent BASS_HE Draft PR112 HEAD a03c1eee365c9b796fef137b81a4347ad44008d1. Source-only, add-only. Exact original EXFOR M0475 bytes=3349, SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f and Git blob c49433293921dbb012d7f1b0387745732a598efa, IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4; both byte digests independently matched in the current runtime. Source records tagged bremsstrahlung, liquid helium, 2-arm coincidence TOF scintillators, and ERR-S statistical-only.

## Measured-data identity
M0475002: 12 original DATA-CM [nb/sr], energies E_gamma 213,258,330 MeV × CM angles 46,61,73,87 degrees. M0475003: 6 original SIG [nb], energies 201,225,253,285,320,359 MeV. The energy sets are disjoint; 330 MeV SIG is not measured by this source. Detector efficiency, photon polarization, azimuthal acceptance, and event vs inclusive D normalization remain unresolved; two-arm COINC is not a normalization identity. Arends 1976 DOI 10.1016/0370-2693(76)90671-7 full methods not independently obtained; Silverman 1984 inverse Td376 MeV corresponds approximately to E_gamma213.1255MeV, not 330MeV.

## Exact two-body derivation
Metric (-,+,+,+), retain c by treating frozen parent PR104 M=M_alpha c²=3727.3794118 MeV and m=m_d c²=1875.61294500 MeV as rest-energy numbers. Let Q=2m−M=23.84647820MeV. Real-photon lab threshold E_thr=((2m)²−M²)/(2M)=Q+Q²/(2M)=23.922758940396704688...MeV. The difference Q vs E_thr is recoil, not a conflict with earlier PHOTON05.
At alpha-target rest incident E_gamma above threshold: s=M²+2ME_gamma, q*=sqrt(s/4−m²), beta_CM=E_gamma/(M+E_gamma), gamma_CM=(M+E_gamma)/sqrt(s), mu=cos(theta_CM).
K±=(M+E_gamma)/2−m ±(E_gamma/sqrt(s))q*mu;
p_z± c=E_gamma/2 ± gamma_CM q*mu;
p_perp± c=±q*sqrt(1−mu²) (opposite azimuth).
Exactly K++K−=E_gamma−Q and (m+K±)²−[(p_z± c)²+(p_perp± c)²]=m². The ± pair is an arbitrary CM label, not measured arm identity.

At each MEASURED DA coordinate define A_K(E,theta)=DATA-CM(E,theta)*(E−Q) [nb MeV/sr] and A_K_ERR=ERR-S*(E−Q); at each MEASURED SIG energy define S_K(E)=SIG_reported(E)*(E−Q) [nb MeV] and S_K_ERR=ERR-S*(E−Q). Masses frozen: these products are rational-exact. The mapping needs no unknown global angular law or unmeasured-energy interpolation. It is a reported cross-section weighted by generated kinetic energy, neither a physically calibrated event rate nor deposited heat. Preserve unknown counting factor kappa=null and separate cross-row covariance unknown.

Numeric source products: SIG S_K at 201:426.939987538±56.689126976, 225:259.488043122±46.265310014, 253:210.821240056±45.83070436, 285:271.599662672±52.23070436, 320:180.653648298±47.384563488, 359:184.33443699±50.27302827 nb MeV. At E330 DA angular rows 46,61,73,87 source-reconstructed daughter K± pairs MeV respectively (195.890497988,110.263023812), (182.956932941,123.196588859), (171.096446303,135.057075497), (156.302372173,149.851149627), and DA weighted pair energy 42.861493052,48.984563488,21.430746526,58.169169142 nbMeV/sr.

## Evidence and withheld physics
Python3.13.5 new targeted 23/23 PASS, source bytes SHA256/Git blob exact, compileall PASS. Independent C++ Boost 100-digit decoder checks original 12+6 rows and max daughter mass-shell residual 5.5856e-103 MeV²; Wolfram independently verifies threshold, K330/46 and both mass shells. Three source-data plots generated/inspected. Native distinct nonauthor R6/C9 NOT_RUN. No legacy IVP/full suite/4501-node LP replay.
Original Central DAG28/88, HE14/18 and physical delta0 unchanged; new data-product DAG has D1 source byte identity and D2 verified measured-coordinate transform. Event/inclusive normalization and actual 330MeV sigma_event, MeV photon phase-space, helium proper target state, D_fast stopping/deposition/C_V unavailable. kappa=null,R_event=null,heat_rate=null,physical_activation=false,L4=false,production=HOLD.