# BASS_HE | A/B/C Fermi 78-row physical data × original EXFOR nuclear reported-SIG

A new **actual observed physical-data** addition to BASS_HE PR116: 2015 Fermi-LAT 78-record published Table3 mirror across Galactic foreground scenarios A,B,C (26 bins each), original upstream mirror Git blob 794cb6fcbef243be950613475c4254d6ab3877a4. The mirror complete byte stream was reproduced in a local file and verified against its pinned Git blob; this is not original CDS archive byte verification. The source published uncertainty is **statistics + instrument systematics**, not pure statistical; foreground is separate. From its exact 200–282.8 and 282.8–400 MeV observed bins, combine six actually source-reported EXFOR M0475003 total-SIG points only on 201–359 MeV.

The calculated reported-SIG-weighted gamma-frequency diagnostic (x 10^-38 s^-1 per helium) is:

| foreground model | IGRB flat | IGRB IGRB-PLE | EGB flat | EGB IGRB-PLE *extra hypothesis* |
| --- | ---: | ---: | ---: | ---: |
| A | 2.058528236 | 2.229056993 | 2.887137317 | 3.128608938 |
| B | 2.212214564 | 2.393631184 | 3.148833380 | 3.409676868 |
| C | 1.743559851 | 1.884069870 | 2.586465694 | 2.797979188 |

These rate-like quantities are NOT source-owned sigma_event×photon phase-space, NOT a cosmic-time history, and NOT heat. EGB vs IGRB are alternatives and EGB includes resolved anisotropic sources. The same calculations preserve each value's pair-born kinetic energy weighted diagnostic, positive knot response coefficients, nuclear ERR-S unknown covariance bounds, Fermi BASIC stat+instrument ± conditional and covariance unknown, and FG-model ± shifts. These are recorded in `results/FERMI_ABC_EXFOR_PHYSICAL_DIAGNOSTICS.json` and the CSV.

Additional source-level observation: printed fEGB − fIGRB − fsrc divided by fEGB in 200–282.8,282.8–400 MeV is A [0.19%,0.22%], B [3.32%,4.77%], C [0.43%,2.18%]. This is a **table-field convention consistency diagnostic**, not a physical violation or independent measurement; do not renormalize Fermi's published data to force equality.

Tests (original self-run) target source 78-row Git mirror identity, exact 6-row extraction, 6 original EXFOR source points, units, non-extrapolation, positivity, conservation of moment split and uncertainty taxonomy. Python unittest **20/20 PASS**, compileall PASS. Wolfram computed independent exact-rational flat-case 2.058528236341606861×10^-38 A IGRB, 2.212214563575953940×10^-38 B IGRB, 1.743559851252844478×10^-38 C IGRB and A EGB 2.887137316982167731×10^-38 per He s^-1. Native different-author independent R6/C9 NOT_RUN. Old IVPs, 4501 LP and full production solver NOT_RUN.

**DAG:** Central 28/88, HE physical 14/18, prior observed-gamma 2/4 unchanged, PR114 low-E 3/4 separate sibling; new Fermi A/B/C aux 3/4 scoped, physical delta 0. `kappa=null;R_event=null;heat_rate=null;physical_activation=false;L4=false;production=HOLD`.

Primary publication: Ackermann et al., ApJ 799 (2015) 86 DOI 10.1088/0004-637X/799/1/86; CDS J/ApJ/799/86 ReadMe. Pinned public third-party 78-row mirror: https://github.com/82492749123082/KM3-230213A_UHECR_TA/blob/774174d9faaa5df40b67af5fa42b4191f09d38c6/data/fermi_igrb_1410.3696.csv. Nuclear raw source: https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4.
