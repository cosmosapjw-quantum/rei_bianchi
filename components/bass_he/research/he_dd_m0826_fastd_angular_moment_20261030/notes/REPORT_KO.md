# HE-DD source-only fast-deuteron angular-moment atlas: 결과 보고

2026-10-30 | PR122 immutable parent `6d105cd89bc8f47f00560ec07d6e41574bed1c38`.

- Actual original inputs: EXFOR M0826003 angular DA nine [30,50] MeV **CURVE** bins, original-byte SHA/Git locked. M0011 raw preserved as crosswalk, but its already-published 14 total+7 E2 data and sigmaK are NOT new.
- New derived physics: sharp low-energy 2nd angular-moment interval, not a within-bin constant fit; 27 conditional deuteron pair kinetic-energy supports at three reference photon energies and exact pair energy conservation.
- Conditional central `<cos²θ>∈[0.203489633794599,0.441697674860268]`; flat-within-bin reference `0.310838714890014`; unknown-covariance ERR-S rectangular what-if `[0.122578897542818,0.533030715995283]`, NOT CI.
- At Eγ=40 MeV **calculation coordinate** (not monochromatic experiment), physical kinetic variance `[0.6874128458,1.4921087133] MeV²`. At 30 and 50 MeV: `[0.1469340513,0.3189372728]` and `[1.7330553306,3.7617960958] MeV²`.
- Science tests: Python 16/16, compileall, reproducible JSON, source-tamper negative test; Wolfram independent numerical moment and K-variance parity.
- Rice 1998 TUNL PhD identified, 198 scanned pages, but scanned numeric tables not retrievable in this execution; Rice 2000 absolute 6 angles×2 energy bins established from original abstract, numeric data and detector efficiency remain `BLOCKED_INPUT`. No guesses.
- Canonical DAG Central 28/88, HE Physical 14/18 unchanged. New source-only micro 2/2 complete, 0 new measured experiments, 27 **derived** records. R6 and C9 independent different-author reviews `NOT_RUN` in absence of native host delegation. No IVP, LP or production reruns.
- Do not infer physical cosmological deuteron injection, deposition or heating: `kappa=null; R_event=null; heat_rate=null; D_fast_pool=null; L4=false; production=HOLD`.

Original references: Arkatov et al. (1972, YF16 p12 / transl. SNP16 p6) EXFOR M0826@IAEA-NDS/exfor_master 939a14d7bba1ddce51975cb5e8711ce96b3b0871; Arkatov et al. (1978) M0011; Rice et al. Phys Rev C61 064612 (2000), DOI 10.1103/PhysRevC.61.064612; TUNL Rice_1998.pdf. Reused PR114 E2 source atlas and PR122 M0826 event consistency.
