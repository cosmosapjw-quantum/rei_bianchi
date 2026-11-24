# REC + REI electron history for the BASS native sky (R110)

`rust/rei_microphysics/src/bass_ionization.rs` and the example
`bass_ionization` write a BASS `--ionization` table (`eta  xe_per_H`, with
η=ln[(1+z_emit)/(1+z)]) with one owner per redshift interval:

| Interval | Owner |
|---|---|
| z > 20 | REC/HYREC table (BASS `research/r109_native_sky/hyrec_1100/hyrec_xe.tsv`) |
| 4 ≤ z ≤ 20 | native AX08 REI case (`zbar`, `xe_per_H` of `five_case_abundances.csv.gz`) |
| 0 ≤ z < 4 | donor-matched continuation to 1+2f_He at z=0 (htt_base R107 `DonorMatchedContinuation`, z_HeII=3.5, Δz=0.5) |

The x_e difference at z=20 is reported, not smoothed. The z<4 shape remains a
conditional placeholder until sources, SEDs and absorbers are supplied.

```bash
cd rust/rei_microphysics
cargo test --release --lib bass_ionization
cargo build --release --example bass_ionization
gzip -dc ../../research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz > /tmp/ax08.csv
target/release/examples/bass_ionization BASS/research/r109_native_sky/hyrec_1100/hyrec_xe.tsv \
  /tmp/ax08.csv ZERO > merged_ZERO.tsv 2> report.json
```

Cloud receipt (case ZERO): 2,481 knots (1,080 REC, 1,001 REI, 400
continuation), HYREC−REI jump at z=20 of 1.03×10⁻⁵ (5% of x_e), final x_e
1.16260270 = 1+2f_He; table SHA-256
`62e4fa35bef2c1b53eec56c097ec28e35c78b9958064808de5bab10663f1caf4`
(`ZERO_REPORT.json`). With BASS R110 (VII_h demonstration, SDIRK2, Lie
congruence, Ω_Λ, 1,400 steps) the bare depth from z=1100 to 0 is 1.17818
versus 1.12444 without reionization (Δτ=0.0537); TT at ℓ≥3 drops by ≈e^{−2Δτ}
and EE at ℓ=3 rises by 60% in that template. These are synthetic templates,
not a calibrated reionization history.
