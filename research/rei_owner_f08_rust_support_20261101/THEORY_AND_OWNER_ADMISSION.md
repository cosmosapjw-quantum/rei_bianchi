# REI physical fast | F08 original photon spectral support: owner R7 and Rust companion

Date: 2026-11-01 (Asia/Seoul). Scope: **one original-source, 128-direction first-step negative-physics witness**; no native coupled IVP or canonical node approval.

## Immutable authority and live owner intake

- REI source owner [PR #358](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/358) frozen base HEAD `5ba12e8c7f66315024f5d71dcc5fb168310b0865`. F08 original [REI #349](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/349) and [BASS #315](https://github.com/cosmosapjw-quantum/bass/pull/315) + BASS_HE #145 remain source-conditional. BASS #315 upstream magnitude-test CI FAILED; this status is retained.
- New sibling original-source counterexample [BASS #321](https://github.com/cosmosapjw-quantum/bass/pull/321) (fixed-input original photon remap and actual checkpoint): source snapshot `paired_runtime.rs` SHA256 `b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7` byte-verified against recovered original Rust.
- Separate F05 owner [REI #357](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/357) already accepted BASS_HE #146 H/He ionization storage and REC #190 native electron Thomson area for **source-conditional derived data only**. Do not re-import those outcomes or confuse F05 He/H=0.079 with F08 S0 He/H=0.083.
- Original F08 S0: birth E0=13.7 eV; first native dt=6.25e8 s; fixed H_i=(1.01,0.99,1)e-14 s^-1; initial N0=0.05 photons per H; original 8x16 directional qhat and fixed energy pair [13.675,13.7] eV. Prescribed diagonal Bianchi I ds²=-c²dt²+sum_i a_i(t)² dx_i², no tilt or Einstein-solved background.

## R7 physical discrimination: exact finite-support counterexample

For an original photon with conserved comoving ray direction q_i and exponential a_i(t)=exp(H_i t), E/E0 = r(q,t)=[sum_i q_i² exp(-2 H_i t)]^{1/2}.
For H_i>0, the *physical* support of initially monochromatic photons at finite t lies in [E0 exp(-H_max t),E0 exp(-H_min t)]. In particular first-step physical continuous minimum is 13.699913519022955 eV, strictly above the fixed grid's lower node 13.675 eV. The 8x16 original ray grid minimum is 13.699913596561121 eV.

Original native `hat` remapping instead assigns positive weight at the lower fixed energy:
`w_minus(q)=(E0-E(q,t))/(E0-E_minus)` and `w_plus=1-w_minus`. These satisfy `w_minus+w_plus=1` and `w_minus E_minus+w_plus E0=E(q,t)`, but introduce `Var_grid(E)=(E-E_minus)(E0-E)>0` where the exact monochromatic characteristic has zero conditional spectral variance. This is **not** a general prohibition on finite-volume photon transport; it is an exact counterexample for the original first-step fixed-node hat allocation.

Define A(q)=sum_i q_i² H_i and B(q)=sum_i q_i² H_i². Wolfram verified
`1-r=A dt-[B-A²/2]dt²+O(dt³)`.
Therefore `N_ghost=N0(E0/DeltaE){<A>_q dt-[<B>_q-<A²>_q/2]dt²+O(dt³)}`. Under a genuinely isotropic angular average `<A>=H_mean`; for this **specific original 8x16 grid** this leading equality also holds because its x/y symmetry cancels H_x-H_y while H_z=H_mean. This is NOT asserted for arbitrary anisotropic quadrature/grid.

## Independently reproduced original first-step physical records

An independent Rust offline Cargo project computes all **128 original qhat rays** and their *off-grid physical* energy, with the old hat ghost weight recorded **diagnostically only**. Rust-generated original-model CSV source data:
- 128 records, every actual characteristic above 13.675 eV (zero true sub-support rays).
- Discrete actual E_min=13.699913596561121 eV, E_max=13.699915153974095 eV.
- Original remap's below-support artificial deposit `sum N0/128*w_minus = 0.00017124946478631471 photons/H`. BASS #321 reports `0.00017124946478640907 photons/H`; absolute agreement `9.44e-17 photons/H`.
- 4/4 offline Rust companion unit tests PASS; rustfmt --check PASS (rustc/cargo 1.99.0). CSV SHA256 `330c91e9920fd7e13c373dbc0c48aa526eb5a7e00e559e3b72ba3762ffeb7343`.
- Historical recovered `rust/rei_microphysics` was separately compiled in an isolated copy with three byte-identical AXBI contract inputs and passed selected 19/19 integration tests (radiation_conservation 4, bianchi_i 6, igm_foundation 9). Its `cargo test --lib` ran 0 tests and is *build-only* evidence. The original Rust owner crate is NOT yet restored on production/main.
- Separate private worktree for F05 native-Rust restoration is concurrently owned by another workstream; do not touch it, overwrite its untracked original Rust source, or claim that this companion is the official native F05 kernel.

## Project-owner science admission / adversarial review

**Decision:** ACCEPT BASS #321 for *source-authentic F08 spectral-transport defect evidence and design guidance*, and accept the new 128-ray Rust first-step verification as **SCOPED_NUMERICALLY_CHECKED_IMPLEMENTATION_VERIFIED** (not production). The literal off-grid characteristic is the minimal physics-preserving candidate for transport, pending coupling to original native opacity, photoelectric absorption, H/He/OTS thermochemistry, thermal energy and photon ledgers.

**Do not admit:** BASS #321's observed ~23.4276% final below-support tally as solely explaining the separately reported -6.13% continuum-characteristic photon-count mismatch; no coupled original F08 photon solver replay performed here. No source-mismatched F05/F08 chemistry splice, full polarized Boltzmann equation, CMB likelihood, or Einstein-constrained Bianchi evolution. No F05 original tick161 acceptance or F09 provider repair. BASS #315 strict CI FAIL is not waived.

**Same-author hostile self-review:** Rechecked exact original qhat normalization and initial 0.05/H normalization; distinguished continuous-direction minimum from finite 128-grid minimum; verified two-node mean-energy conservation does **not** imply support conservation; verified 8x16 symmetry condition for H_mean expansion; ruled out using an off-grid *one-step characteristic* as evidence of a complete remapping/chemistry replacement. Native subagent and distinct-author blind reviewer NOT_RUN.

**Drift watchdog:** Actual original Rust source bug reproduced, physical 128-ray data emitted and a Rust alternative implemented. No duplicated photoheat atlas, no metadata-only gate, no change in canonical accepted physical states. **DAG at this R7 stage: REI Central 28/88; Working 33/88 nonadditive; Physical Fast 4/7; canonical delta 0.** Original accepted F05 160/131072, V2 tick161 shadow-only, F09 blocked, production HOLD.
