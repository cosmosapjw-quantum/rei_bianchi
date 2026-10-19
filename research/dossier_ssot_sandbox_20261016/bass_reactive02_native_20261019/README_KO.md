# BASS-REACTIVE-02: long-span separated controls, 2026-10-19

The original91-file reactive1 solver is unchanged. Four readable Rust overlay files add a controlled experiment, scalar birth-time oracle and4tests. Copy overlay contents into a fresh reconstructed reactive1 crate from sibling bass_reactive01_published_20261019. The resulting95-file crate is exactly the one tested in this stage. The full ZIP contains that complete crate, original donor data, Python driver/analysis/tests, all scientific CSV/logs and full Korean report. No arbitrary source replacement, no PR192 lineage substitution, no production merge.

## Reproduce native examples

With user-supplied Rust1.94.1, in the complete crate:

cargo test --release --offline --locked --all-targets
cargo clippy --offline --locked --all-targets -- -D warnings
cargo run --release --offline --locked --example bass_long -- SIGNED_MINUS 121 64 0 8e13 false false 4 4
cargo run --release --offline --locked --example birth_slab_oracle

CLI: case grid nsteps t0 duration spectral_split frozen_H_s birth_GL opacity_m. Spectral switch does NOT silently select birth order. A frozen comparison uses the same donor start H,s but holds them constant thereafter. Original regression composition,T0=10000K,Ddefect.0037eV,CMBbath20K,sourceMD14/BB50k,fesc.2,GL8angles and tightCXrtol1e-12 are retained. These are not observational EoR IC or two-way Einstein coupling.

## Executed result

Rust183/183 (prior179+new4), Python6/6, strictClippy and newRustfmt pass. Source91files unchanged. Initial4controls tests failed against a fixed stub, then passed. Main plan13cases:11completed624steps; n128_g4 stopped109/128 at host timeout, n64_split stopped54/64 after28s. Partial cases excluded from all final pairs. Three pilot histories are separately recorded; the8e13pilot duplicates n32_g2 numerically and is not an additional independent main result.

At duration8e13s (1000x prior), N64 with original spectrum and opacity4, changing birthGL2->GL4 changes survivor9.0920352574e-12->8.7234944944e-10 per reference-comoving m3, factor95.94655. Max photon inventory residual over completed cases1.12079471e-14, energy6.95947871e-16. Conservation alone misses this resolution effect. N32/64/128 birthGL2 temperature differences suggest p2.0472, but photon/DI/HeII differences do not establish convergence; no global2ndorder claim.

At fixed N64/birthGL4, opacity4->8 survivor relative change4.02122e-10, while changing donor121->481 gives1.2688e-12. At N32/birthGL4, original mean->Dedge splitGL3 changes survivor+1.209641% and DI-.0308615%. At N64/birthGL4, frozen-start geometry->actualBASS gives deltaT+1.104259877K and survivor-.0973683%; these are paired finite-resolution values, not certified continuum geometry effects. Signed q2 remains sensitive to birth/time resolution and is not a CMB a20.

## Direct diagnostic derivation

For constant source j and opacity kappa over h, new survivor is jh phi(tau), phi=(1-exp(-tau))/tau,tau=kappa h. Interior positive Gauss birth quadrature gives jh Q=sum_l jh w_l exp[-tau(1-u_l)]. With delta=min(1-u_l)>0, Q/phi<=tau exp(-delta tau)/(1-exp(-tau))->0 at large tau. This is a fixed-node stiff-limit issue, not a no-go for other integrators. GL2 small-tau defect Q-phi=-tau^4/4320+tau^5/8640+O(tau^6). Conserving absorbed=source-survivor does not certify survivor accuracy.

Wolfram identities/series and separate clean limit call were executed. Native20scalar rows compared to independent NumPyGL/analytic phi with max absolute difference1.11e-16. At tau100 survivor deficits are GL2 .9999999668, GL4 .98321268. These scalar errors are NOT measured absolute errors of the evolving gas runs. Mackey2012 DOI10.1051/0004-6361/201117984 supplies general optical-depth/timestep context, not proof of this new code.

Fresh directory: all183tests/build rerun; selected n32_g4 and n64_frozen (96steps) reproduced all scientific CSV fields exactly with wall_s excluded. Scalar20rows byte-identical. All11histories were NOT rerun. Independent photon-work difference/source energy max3.53524238e-5 is distinct from the small conservation ledger and remains visible.

## Preservation and next gate

FULL ZIP1743500bytes/174members/173payload hashes; SHA256ca3c909802e2d198f14ea218434108a7ea345135e2aee29f437ee95c8d1722a9.
Drive: https://drive.google.com/file/d/1iMk4oFR5eV2oiovOg7FcfwXSGCyD6VPS/view?usp=drivesdk
Dropbox: /bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_REACTIVE02_20261019_ca3c9098_FULL.zip ;id:BSpOijBcT10AAAAAAD_Png.

Status SCOPED_LONG_SPAN_DIAGNOSIS_COMPLETE; RADIATION_CONVERGENCE_UNRESOLVED. FullP4 PARTIAL;SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. Next concrete correction is stiff-aware positive Duhamel/phi birth quadrature or birth subdivision, retaining species/thermal/geometric ledgers. Existing S10 adaptive control has NOT been run over this long interval and is not presumed to solve it automatically. Native subagent NOT_RUN_UNAVAILABLE; all new execution sandbox only.
