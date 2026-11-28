# BASS_HE observed MeV photon field × EXFOR DD physical-data bridge
Date 2026-10-30 KST. Parent BASS_HE Draft PR115 HEAD b271023c9fe6a9c87cd96cc2561c7d1f7bf8e0ed. PR114 low-E E2 75-row original-source data is an independent read-only sibling, not automatically merged.

## Scientific new input
Primary Fermi LAT Ackermann et al. (2015) ApJ 799:86 Table3, DOI 10.1088/0004-637X/799/1/86, Galactic foreground model A: IGRB bin integrated intensity 200–280MeV 1.1±0.3e-6, 280–400MeV 6.7±2.0e-7; EGB corresponding 1.5±0.3e-6 and 9.7±2.0e-7 photons cm^-2 s^-1 sr^-1. Foreground systematic ± separately retained (model A). These are measured BIN-integrated intensities; source data JSON is curated transcription with SHA256 lock, NOT a bitwise copy of the original Fermi machine-readable publication. Source EXFOR M0475003 six original reported SIG points from IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871: E=201,225,253,285,320,359 MeV, source raw Git blob c49433293921dbb012d7f1b0387745732a598efa; NO measured SIG330.

## Derived conditional same-observer gamma diagnostic
A=4π * 1e-33 cm²/nb. Fermi model-A best-fit within-bin g(E) ∝ (E/100 MeV)^(-2.32)*exp(-E/279000MeV), renormalized to EACH measured bin-integrated intensity separately. Cross section linear between EXFOR published SIG coordinates; truncate to overlap 201–359MeV, no extrapolation. Observer-local isotropic photon field and He-rest coincidence assumed, not cosmologically established.
Gamma_reported_like^IGRB=2.329295763535772e-38 s^-1 per helium; Gamma_reported_like^EGB=3.215557459578155e-38 s^-1 per helium. The corresponding pair kinetic weights are 5.156962719683174e-36 and 7.144818531152085e-36 MeV s^-1 per helium, NOT heat rates. Full 2-bin isotropic number densities 7.419291377708954e-16 and 1.0353474408441307e-15 cm^-3. EGB and IGRB are alternatives, DO NOT SUM. Model countercheck flat within-bin: 2.1520599518476934e-38 (IGRB), 2.9680631181773316e-38 (EGB) s^-1 per helium, matching Wolfram exact rational piecewise integral. Rate-like shape sensitivity ~8.24% IGRB, not a certified interpolation uncertainty.

## Executed evidence and governance
Tested local Python3.13 SciPy 12/12 unittest PASS, compileall PASS. Independent vectorized trapezoid over 300001 points per bin matched SciPy integral within 2e-8 relative; Wolfram flat weighted exact symbolic result matches. No original IVPs, old 4501 LP or full production solver. Source data and code published as exact local-byte-matching Git blobs after explicit terminal-LF repair, not confused with original Fermi raw paper bytes.
Native distinct-author R6/C9 NOT_RUN. EXFOR measured event convention, calibration, Fermi photon phase-space at arbitrary redshift and He frame, physical D stopping/deposition/heat capacity unresolved. kappa, R_event, heat_rate NULL. physical_activation false, L4 false, production HOLD.
Original Central 28/88 HE physical 14/18 unchanged, original measured-data 2/2 scoped, PR114 lowE 3/4 scoped sibling unchanged. New auxiliary gamma-data→reported-rate diagnostic DAG D1 exact source-transcribed two Fermi bands COMPLETE_SCOPED, D2 source-weighted reported-sigma numerical diagnostic COMPLETE_SCOPED, D3 source-owned z,x,He-rest gamma phase-space OPEN, D4 source-owned sigma_event and fast-D heat deposition OPEN => auxiliary 2/4; physical_delta 0.

## References
Fermi primary: https://doi.org/10.1088/0004-637X/799/1/86
Fermi open-access Table3: https://openaccess.inaf.it/bitstreams/c1cdedfe-0b59-4462-a8d9-ed930eeec2db/download
EXFOR raw: https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4
BASS_HE frozen parent: https://github.com/cosmosapjw-quantum/BASS_HE/pull/115
BASS_HE sibling data: https://github.com/cosmosapjw-quantum/BASS_HE/pull/114
