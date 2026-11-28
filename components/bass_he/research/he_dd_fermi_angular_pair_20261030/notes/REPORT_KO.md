# BASS_HE | EXFOR measured DA × Fermi photon sky angular injection atlas | actual research report

**Date:** 2026-10-30 KST. **Source parent:** BASS_HE Draft PR118 `d92e94290977d4f0bb59ea16c8219d52a295bd99`. This is new derived physical model-data, not 168 new lab measurements.

**Inputs:** original byte-verifiable EXFOR M0475 3349 bytes, DA 12×[213,258,330 MeV; 46,61,73,87 deg], original Fermi 78row public mirror 15975 bytes, with exact 200–282.8/282.8–400 MeV bins. All 6 original source-reported total-SIG observations are reused only as provenance checks, never substituted for measured DA.

**New outputs:** 12 source-exact measured-coordinate + daughter kinematic entries, 168 conditional cross-products (144 IGRB/EGB × two spectral assumptions over 3 FG models, plus 24 single shared high-lat `fsrc` products). Each output includes original `DA/ERR-S`, separately modeled Fermi energy density, source-specific Fermi BASIC/FG uncertainty scales, pair `K±`, `theta_lab_±`, `p_±c`, daughter marginal variance, and the energy-weighted *born* angular response (not heat). Original Fermi basic error is statistical+instrumental, not pure statistical. `fsrc` is not three independent measurements and is not an independent additive component to EGB.

**Representative numerical source-linked results (330 MeV, 46 deg, published DA=0.14±0.03 nb/sr):**
`K+=195.89049798808395 MeV;K-=110.26302381191605 MeV;Ksum=306.1535218 MeV`; marginal variance `1833.0160834475744 MeV²`. FG-A IGRB flat `D_rep=9.982330240587364e-42 s^-1 MeV^-1 sr_CM^-1 per He`; high-lat source flat `2.9887652843124764e-42` under separate sky-mask hypothesis. At measured 213 MeV, 46° DA=0.22±0.04 nb/sr, `K+=116.8998711540382`, `K−=72.2536506459618 MeV`. At 258 MeV, 46°, DA=.08±.03 nb/sr, `K+=146.84133303089088`, `K−=87.31218876910912 MeV`.

**Validation:** Python 26/26 targeted PASS, compileall PASS, full source raw+Git hashes matched, unit/numerical conservation and exchange checks for 12 coordinates, Wolfram independent reported flat numerical and exact pair-sum checks. Actual CI, distinct-author independent R6/C9 and original full historical production suite are NOT_RUN.

**Limits:** source-reported DA counting convention not reclassified as event. Gamma differential shape at point energies is modeled, not directly Fermi measured. EGB all-sky isotropy and high-lat `fsrc` local uniformity are hypotheses. Fermi present-day Earth-observer spectrum does not establish arbitrary redshift gamma history or D_fast heat deposition. Central28/88, HE14/18 unchanged; local ANGULAR_SOURCE_DAG=2/3_SCOPED; physical_delta=0, L4=false, production HOLD.

**Next:** independent original Arends/Rice detector and event/inclusive normalization plus actual He-rest high-energy radiation phase-space followed by D_fast slowing, secondary energy and escape/deposition, heat capacity; stop before production. Fermi raw CDS original byte authentication remains open. No merge, no force push, no old IVPs or 4501-node LP.
