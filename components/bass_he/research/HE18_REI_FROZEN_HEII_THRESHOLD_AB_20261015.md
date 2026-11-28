# BASS_HE / HE18 downstream cold rei_bianchi frozen HeII threshold A/B research, 2026-10-15

**Authority:** This is a read-only cross-repository receipt. Warm HE18 P01 FT03/HM12 16-cell certified source data and cold rei_bianchi Plancklike_MD14_BB50K are not physically interchangeable. No warm tau, helium fraction, temperature or photo-rate is transplanted.

Canonical rei_bianchi implementation and source-scoped results:
https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/frozen_collision_ab_20261015

Verified research commit: da99c26013af3c60e3e7558fe44aeecd0ce99639. Original live owner HEAD remains 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

## Actual native Rust A/B

Controlled frozen-gas H/He composition with normal-frame proper density scaling, q=-0.005,0,+0.005, absorber eta=0,1e-6,1e-5, energy bins 5/20/32/33 and source subdivisions 1/32/256. This gives 108 matched source conditions and 216 individual transport records.

- A: original Driver::geometry_map fixed-energy two-node projection each half-step, followed by original AtomicProvider Verner cross sections at exact canonical grid-node energies, HHeModel threshold binding, and stable exponential photon absorption.
- B: original CovariantPhoton conserved spatial momentum, exact local photon energy, and original absorb_frozen_gas exponential H/He species partition at the same midpoint and proper time.
- All 216 rows have photon number, binding+heating+redshift+boundary energy and atomic species event ledgers closed to maximum normalized residual <2e-15. Using grid-node sigma(E_i) eliminates the separate one-ULP false-negative threshold classification caused by a same-frame momentum roundtrip.

**Threshold ghost:** Original Verner HeII photoionization is zero for exact E<54.42 eV and positive at 54.42 eV. An initially 54.42 eV photon redshifts below this threshold, yet fixed-grid two-neighbor projection places a positive weight at the 54.42 eV node. For q=0, eta=1e-5, 256 steps, this produces projected 0.00246475583249896 absorbed HeII photons per injected photon, versus zero for the exact-covariant arm. Injecting 1e-10 photons per H gives 2.46475583249896e-13 artificial HeII events per H in this hypothetical frozen-gas test.

At this same control, the energy transferred to binding ledger is 0.277566641328993 eV per injected photon (projected) versus 0.143466406870282 eV (covariant); heating 0.299579659468956 versus 0.299883127280840 eV. Both satisfy ledgers, illustrating that ledger closure does not by itself imply correct threshold reaction accounting.

Physical nuances: AtomicProvider's opacity switch 54.42 eV and HHeModel binding threshold 54.41776 eV are distinct original source constants and both were preserved. Absorber neutral fractions are deliberately imposed, not cosmologically evolved; this experiment does not predict the native xHII, xHeIII, gas temperature or full EoR optical depth. Original frozen native binary full source epoch differs from the independently linked rlib epoch, though 12 selected atomic/geometry/transport Rust function bodies match exactly. The optional reference frozen absorber is not claimed to be identical to native production BE chemistry.

## Verification, performance, backups

Ubuntu test suites: 33 parent + 19 directional + 28 native + 19 frozen H/He Python + 5 original-crate-linked Rust = 104 passing tests. All 216 final formatted-binary physics output rows agree exactly with the canonical uncached and signature-cached serial/parallel results, excluding wall-time diagnostic columns.

Source-scoped wall times: uncached canonical serial 45.30 s, Verner-cache serial 44.56 s, Verner-cache two-worker 41.64 s, final rustfmt compiled two-worker 42.29 s. Speedups ~1.07-1.09x are modest single-sample A/B throughput changes, not production solver speedups.

Final code+evidence manifest is published to rei_bianchi branch; independent code archive: HE18_FROZEN_HHE_AB_CODE_da99c260_20261015.tar.gz, SHA256 ce9589ddcef273ac8afc5b4efe5418c68224cdd96040cd60f85b130643081a65. Original Rust artifacts+CSV archive: HE18_FROZEN_HHE_AB_RAW_da99c260_20261015.tar.gz, SHA256 600d2189fb4af88a8f2a0b10ffe1e5cd7e314cfa8754071d1e6a35dd929b3d54.

Both archives are present and byte-hash matched in ~/archives/ and Dropbox/BASS_DERIVATION_DOSSIERS_20260912/HE18_REI_TRANSFER_20261015. Next source-scoped DAG HHE_AB5: independently update HII, HeII, HeIII and gas thermal energy with conserved photon-number/binding/heat/nuclear ledgers under both photon lanes before any proposal to replace the original production solver. Scientific admission remains source-specific IMPLEMENTATION_VERIFIED, production EoR global error HOLD.

Relevant literature: Friedrich et al. (2012), MNRAS 421, 2232, https://academic.oup.com/mnras/article/421/3/2232/1077406 ; Norman et al. (2015), ApJS 216:16, https://doi.org/10.1088/0067-0049/216/1/16 ; Fleury, Pitrou & Uzan (2015), Phys. Rev. D 91, 043511, https://doi.org/10.1103/PhysRevD.91.043511 .