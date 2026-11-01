# REI F05 original Rust restoration and native physical data (2026-11-01)

## Source authority
Isolated PR356 parent: cc1929982948265f6d0b0f699353b3170ccd1792.
Original Rust crate: rust/rei_microphysics at historical commit d234243a79e4e8e611aaf4ac61949c5ef9111468.
117/117 historical Git blobs verified byte-identical; 6 required historical contract/template files recovered by exact Git object, with no original source overwrite.
Current original 26-event F05 kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644 remains unmodified.
Original source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.
Accepted tick160 parent SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.
Real nonauthoritative tick161 46080x27 CSV.gz SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d.

## Rust physical science, not just a source copy
Historical Rust IgmGasState::from_temperature and IgmGasState::eos are invoked on EACH of 46,080 actual original physical cells in the new additive Rust example f05_original46k_rust_eos.rs.
Mapping: Ne=NH*xHII + NHe*(xHeII + 2*xHeIII); U=(3/2)*kB*T*(NH+NHe+Ne). Original historical kB=1.380649e-16 erg/K.
For homogeneous IDEAL GAS EOS only, use normalized nH=1 and nHe=NHe/NH, then multiply by actual NH count. This does not set the original proper density to 1 cm^-3; NEVER use the normalized source for density-dependent rates or opacity.
Native original-source electron total = 5.96030682267282542e66; gas thermal energy U = 3.37202732430408246e55 erg.
Owner source electron enclosure = [5.96030664684742926e66, 5.96030699849822158e66]. Owner source gas energy enclosure = [3.37202414425589284e55, 3.37203050435370671e55] erg.
Exact per-cell original source interval strict misses: electron 0/46080; gas energy 0/46080. Integrated original signed delta-Ne interval = [-1.56613314196649239e60,-1.55349711801073923e60].
Native T range = 2096.66931752347682..66261.7300247082458 K. Original owner source metadata and global totals independently crosschecked by read-only audit.
These are real source-conditioned preview data. Official original tick161 is NOT ACCEPTED.

## Execution evidence and failure classification
Historical Rust offline locked full suite: 262 tests PASS across 42 groups; new Rust original46k example: 4 tests PASS; new rustfmt check PASS; actual 46080-cell native Rust CLI exit=0 with parseable JSON.
First Rust build failed because 3 historical compile-time source contracts were absent (input/provenance), then recovered without bypass. One old test missed 3 binding templates; exact historical byte restoration resolved it.
An invented 1e-10 midpoint equality diagnostic falsely rejected 1206 cells. All 46080 native EOS points were inside ORIGINAL source intervals; the false gate was removed while the 1206 midpoint discrepancies remain visible as non-gating data. No original scientific tolerance changed.
Historical Rust EOS and direct independent algebra agree at machine roundoff. Source SHA, row count, ordering, finite state, fractions, per-cell interval inclusion and real source totals are checked; original 14 physical time-map ledgers NOT_RUN in Rust.
No Rust time-integrator speedup or original 26-event map parity is claimed. Earlier VigilODE PR183's Python thermal-root speedup is a Python-only source shadow, not native Rust performance.

## Same-author adversarial review and drift watchdog
BLOCK production: historic Rust engine has been restored and one native F05 output evaluated, but the present original 26-event H/He/OTS/thermal MPRK22(1)+Alexander SDIRK2 time map with all 14 ledgers, clock/events and V1/V2 owner protocol has NOT been migrated.
BLOCK source consistency: one normalized ideal EOS algebra must never be passed to density-dependent rates; original photon HeII subnormal trace remains unresolved for f64.
BLOCK continuum: no formal MPFI/MPFR proof; no post-tick160 continuous-time global original history. Original independent-output logT upper 2.1245050576368385e-4 still exceeds 2e-4, and original official tick160/131072 remains accepted only.
Next directly productive unit: bind current ORIGINAL photon-group forcing and original 26-event stage clocks into recovered Rust microphysics, reusing VigilODE RODAS/Radau where mathematically source-compatible; compare full/half/half H/He/thermal states, 14 ledgers and fallback under frozen gates. No more unrelated photon atlases.

## Official DAG (not inflated by a successful auxiliary Rust port)
REI central 28/88; working 33/88; Physical Fast 4/7. VigilODE official 7/23, successor 0/12. Canonical delta 0. Draft/HOLD; no default change, merge, force-push, tolerance relaxation or automatic tick162.
Subagent: NOT_RUN (not present). Hostile review: same author. Durable backup and GitHub ACK reported separately.
