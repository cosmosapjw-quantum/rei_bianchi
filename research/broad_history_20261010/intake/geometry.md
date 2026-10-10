# BASS / REC fresh source intake — 2026-10-10

Read-only GitHub metadata plus freshly cloned source inspection. No remote/source mutation, numerical rerun, merge, gate promotion, or reinterpretation of old receipts. Exact inspected file identities are in `geometry_source_manifest.json`; complete cloned branch inventories are in `bass_intake_refs.json` and `rec_intake_refs.json`; raw PR metadata is in `geometry_github_metadata.json`.

## Fresh pins and new result

| Repository / lane | Exact remote head | Finding |
|---|---|---|
| BASS PR136 `research/rei-pr96-bass-snapshot-readback-20261010` | `220d765f1df3803e6d4e3e3ad92d31ff421165ec` | Unchanged; open; 17 warm snapshots read back, no new history |
| BASS PR135 snapshot receiver | `45f31b8edd644b49e4ea06f10d0190eb664737c7` | Legacy REI state to proper-SI electron state |
| BASS PR134 axisymmetric observables | `8216c5c6ebe2719c32a4082096ac9d7341d50c62` | Fixed-time slab and supplied endpoint validation |
| BASS PR132 host branch | `e57064934bb176b08d2072aa537e5f71a430ae5e` | Separate modern HHe/FT03 visibility and clock bridge |
| BASS PR133 native gain branch | `548c9f71304d4dd0b6df3565e2d25229429f64d3` | Separate zero-tilt frozen-frame gain research; not default coupled history |
| BASS CR-PHYS01 sync | `62633b3b6c158d0697f57b8999eefeb1a71c24d9` | Exactly two documentation paths; no microphysics delta against PR136 |
| REC PR81 `forward/rust-he-sources-20260922` | `d74fc9e78d1cf707eef2d16fe771b4d8eb72cd7f` | Unchanged; open draft; PR body contains historical superseded status and later REC-PB02/SYNC02/SYNC03 returns |
| REC PR82 `research/p02b-flrw-endpoint-20261010` | `b1213b09cab2c8d30678ae29a948ab7ad92d030f` | **New** source-pinned archival HyRec conditional FLRW endpoint, created 2026-10-10 11:41 UTC |
| REC CR-PHYS01 sync | `da579e70d9fabf91ea77c60c3ffa40de55a2ccdb` | Exactly two documentation paths; no scientific operator changes |

Latest public GitHub branch inventory was cloned rather than inferred from default branches. BASS has 219 remote refs, REC has 100 (including origin/HEAD). PR136 and PR81 comment tools returned no top-level comments; their PR bodies and source documents contain the posted returns. No new direct recipient-chat ACK is established.

## Actual source already available

| Source | Executable function / state | Reuse and limits |
|---|---|---|
| BASS136 `_rustcore/src/microphysics/visibility.rs` | `ElectronState::new`, `scattering_rate_per_normal_second` | Proper SI charge closure and q=cσT n_e D. D applied once. Chemistry/geometry external. |
| Same | `integrate_visibility` | Backward piecewise-constant τ, survival, stable interval mass, supplied observer tail. No need to rewrite optical-depth primitive. |
| Same | `compare_opacity` | Same-clock L1 opacity transfer into survival/mass error bounds; not continuum history error or peak-location certification. |
| BASS136 `axisym_observables.rs` | `fixed_time_optical_depth` | Integrates cσT n_e over externally supplied proper-time cells and clipped bounds. Unknown tail remains `None`. |
| Same | `DirectionalRedshiftEndpoint`, `validate_common_observer_pair` | Only validates supplied Eo/Ee=1/(1+z), direction normalization and identical observer time. Does **not** compute/invert z. |
| BASS136 `rei.rs` | `electron_state_from_rei` | Full helium simplex and one cm^-3→m^-3 conversion. Legacy state snapshots only. |
| BASS132 `rei_visibility.rs` | `electron_state_from_hhe`, `electron_state_from_ft03`, `integrate_rei_visibility` | Actual typed HHe/FT03 density conversion and cell schedule→existing visibility. A density-valid state is not an atomic-rate domain admission. |
| BASS132 `visibility_clock.rs` | `integrate_clock_visibility` | Explicit normal seconds, conformal seconds, conformal metres. Factors 1,a,a/c; no extra density dilution. Cells/rate freezing remain external. |
| BASS136 `_rustcore/src/ode/charts.rs` and `solve.rs` | ClassA normalized RHS and BDF `integrate` | Bianchi I algebra exists as N_i=0; axisymmetry can use Sigma_minus=0. This is a constant gamma-law background chart, not the requested full cosmological material inventory or physical clock reconstruction. |
| BASS136 `_rustcore/src/rays/geodesic.rs` | `photon_rhs`, `trace_ray_diag` | Native photon RHS exists. `trace_ray_diag` deliberately mirrors **forward Euler**, gamma-law matter, sampled history (~400 records), no chemistry. A reusable algebraic reference, not ready long-redshift coupled driver. |
| REC81 `src/full_bianchi_hyrec/background/evolution_provider.py` | `BianchiReviewBianchiIIProvider` | **Only orthogonal Bianchi II is provider-validated.** All non-II families fail closed; Bianchi I cannot be silently sent through this provider. |
| REC81 `rust/rec_microphysics/src/hydrogen_peebles.rs` | retained event RHS, frozen-escape QSS, `peebles_rhs`, `hyrec2_one_temperature_source` | Existing source-bound pure-H point API. Not a full cosmological history, general Bianchi RT, or selected-He consumer replacement. |

### Branch compatibility is a real integration task

At BASS136 the actual Cargo pins are REC `d3cc6e0120061f113d28e7a3a55a2e3dd561e81e` and REI `1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8`. The modern BASS132 branch pins REI `41e4592aa494b48929dcd23fc8504c169a98a908` with the same REC pin. It contains `rei_visibility.rs` and `visibility_clock.rs` absent from PR136, while PR136 contains `axisym_observables.rs` absent from PR132. Combining these lanes requires explicit source/dependency composition, not an assumption that the newest PR contains all previous science.

The actual PR136 return confirms 17 snapshots, zero material velocity, six-column input readback and two equal orthogonal Thomson rates. It explicitly says no chemistry/background calls, no CR injection, interpolation, τ/visibility/observer-tail integration. Its successful CI did not rerun the 17-snapshot science receiver. That evidence should be retained, not repeatedly rerun as a substitute for history work.

## REC82 source and numerical return

The new C driver allocates the original HyRec arrays, invokes `read_rates`, `read_twog_params`, `rec_get_cosmoparam`, and **`rec_build_history`**, then calls original `rec_interp1d` at ln(a)=-log(1+5.807). The driver actually validates all native history nodes before exporting only the endpoint and four interpolation-support nodes. Original source archive SHA-256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`; input.dat SHA-256: `f8073ba70197378e156a6723e229ff47cc9f0d8be0121f1fce82aff6c64abcbc`.

| Quantity at z=5.807 | Baseline DLNA=8.49e-5 | Refined DLNA=4.245e-5 |
|---|---:|---:|
| xe=ne/nH | 0.0001860196684866345 | 0.0001860195581797334 |
| Tm (K) | 1.0120602409998003 | 1.0120600999382203 |
| ne (m^-3) | 0.010998414136317698 | 0.010998407614421436 |

Common nH=59.12500665007869 m^-3, nHe=4.701224649342645 m^-3, H=2.086105637709873e-17 s^-1, Tgamma=18.569496 K. Cosmology is original archival input: T0=2.728 K, obh2=.021976, omh2=.13, odeh2=.343, okh2=0, Y=.24, Nnueff=3.04, w0=-1, wa=0. It must not be silently substituted for a different cosmology.

Posted receipts contain two actual successful native C runs (0.470 and 0.971 wall seconds), not fresh execution by this intake. Relative xe/ne difference is 5.93e-7, Tm difference 1.39e-7. This is one step-halving comparison, not convergence-order/global-error evidence. INDEPENDENT_REVIEW.json says PASS_SCOPED; the report opening still says pre-independent-review, a stale prose line superseded by the source-bound review file. Helium assignment is explicitly neutral-after-original-HyRec-cutoff, not resolved tiny residual helium populations.

Crucial consequence: a cold archival recombination endpoint now exists. Its ~1 K state remains outside the currently noted 100 K CR packet and warm FT03 closure; no floor/temperature substitution is justified. REI/Bianchi IC adoption, cold atomic/thermal provider and photon/source IC remain HOLD in the posted result.

## Posted CR synchronization

Both two-file sync returns bind CR24 scientific source `0522fac6dcaf1874974e2a59979aef88408a81e6` and REI102 scientific receiver `2fd4c5bd8a9cd5ada7718c179294c73dc6c0a1da`. They describe a nonzero physical component under stated 1–4 MeV channel / FS10 xi=.01 terminal-yield assumptions. BASS return explicitly requires a new actual REI CR history and new source identity before its receiver; old CR-off warm17 evidence cannot authenticate CR-on history. REC return requires a shared chemical-energy convention and says the current 100 K packet is not warm FT03 or a full recombination/reionization history. Delay, composition, omitted losses and state dependence remain component extensions, not closed history gates.

## Science-first implementation consequence (derived here)

For the homogeneous, non-tilted axisymmetric metric with transverse a_perp and longitudinal a_parallel, use a_bar=(a_perp^2 a_parallel)^(1/3), and label volume redshift separately from directional observed redshift. The conserved spatial covectors give exactly

`1+z_obs(t,mu_o)=sqrt((1-mu_o^2)*(a_perp,o/a_perp(t))^2 + mu_o^2*(a_parallel,o/a_parallel(t))^2)`.

This permits robust scalar endpoint inversion on monotone ray-energy intervals without upgrading the legacy Euler ray routine. It also gives a direct independent target for `photon_rhs`.

At common proper-time endpoints, non-tilted homogeneous Thomson depth is **direction independent**:

`tau(t,t_o)=integral_t^t_o c*sigma_T*ne(t') dt'`.

Directional tau at a common observed z arises through direction-dependent emission time, not an extra Doppler factor when beta=0. A long-redshift deliverable must therefore contain actual evolving `a_perp,a_parallel,H,shear,n_H,n_He,x_HII,x_HeII,x_HeIII,T_m` and photon/source histories plus an observer endpoint/tail decision. A manufactured n_e curve or the 17 warm snapshots cannot close this task.

Priority sequence: (1) choose and bind a physical cosmological background/initial state and valid providers over its full trajectory; (2) run the actual coupled material/photon history over a meaningful volume-redshift interval with one substantive refinement; (3) hand actual densities/clock to existing BASS integral; (4) solve directional endpoint inversion and compare tau at fixed observed redshift. Only the compatibility checks made necessary by that composition need new focused tests. Do not replace steps 1–2 with further repeated unit/frame probes.

All scientific conclusions above distinguish directly inspected executable source, inherited posted results, and newly derived geometry. No end-to-end physical history PASS is asserted.
