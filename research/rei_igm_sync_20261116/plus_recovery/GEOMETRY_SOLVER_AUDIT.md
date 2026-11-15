# Original AXBI geometry and solver contribution audit

Observed on 2026-11-15 UTC (2026-11-16 KST). The original target is the conditional, non-tilted, density-fixed H/He IGM abundance family over mean redshift 20→4. A reproduced plot, a native derivative, a Krawczyk root, or a new metadata contract does not by itself complete an abundance-response claim. Current primary owner: rei_bianchi PR374, `research/rei-axbi-owner-consumption-20261115`, `df72fb686a41c3f047bca1a92df8946482948f82`.

| Repository / branch | Exact reviewed head | Actual contribution | Original AXBI claim ceiling |
|---|---|---|---|
| BASS PR315 `research/bass-rei-f08-source-matched-sachs-20261101` | `eb146d198d2363869d441572466afc6c81b62e7b` | Source-matched prescribed-metric Sachs optics; own-flux magnitude comparator repaired | Geometry/optics support; no abundance completion |
| BASS PR331 `research/bass-rei-f08-native-root-bridge-20261102` | `ea19c11ee3412b9fcbc8d3d07ec7c7eefcf7ddbf` | F08 native photon/gas root bridge | Separate constant-H source family; not an AXBI trajectory donor |
| BASS PR334 `research/bass-typeii-clock-interface-20261115-r1` | `7ad4e4b1cf841e0a974715bcece739ec06b38014` | Tilted reaction/expansion clock separation and high-z HYREC scalar reservoir | Separate Type-II support; neither original non-tilted IGM IC nor prerequisite |
| VigilODE PR183 `research/vigilode-rei-igm-photon-fusion-20261101` | `6844c8fe18361f3c2243ee2db95bbf3d68a6ce7b` | Source-native F05 point H/He, nonphoto and thermal RHS, 46,080 cells | Point RHS implementation; no complete AXBI IVP or AX11 empirical convergence |
| rei_bianchi PR374 | `df72fb686a41c3f047bca1a92df8946482948f82` | Four recovered complete original histories; fifth +0.01 incomplete at intake | Original trajectory, abundance comparisons and scientific claims remain owned here |

BASS remains the geometry, frame, characteristic transport and proper-clock owner. VigilODE remains a numerical execution/support contributor whose work must connect to a named original AXBI error or measured runtime bottleneck. Neither repo may replace the selected source law, species closure, background, IC, or numerical claim standard. Their canonical completion counters do not increase from this audit.

## The actual missing-case blocker

The original SHEAR_PLUS execution reached its 200,000 accepted-step cap at `a=0.08873654701704167`, then one resource-only continuation reached durable checkpoint 240,480 at `a=0.107527522059568434`, `zbar=8.299944617397738`. The saved continuation CSV contains 47 later accepted rows, but no terminal RETURN or execution-wrapper identity. The last observer receipt classified `LIVE_WORKERS_OR_CHILDREN_HOLD`; it does not establish the solver's terminal cause. Raw stdout/stderr/time logs are empty. This is an interrupted execution/accounting problem, not evidence of a physical no-go.

Original and continuation CSVs were recovered byte-for-byte. Their duplicate boundary matches in every column. Removing exactly one duplicate and retaining only checkpoint-supported rows yields 240,481 rows from zbar20 to 8.299944617397738. `Sigma=s/H` is exact in the saved decimal values, and the prescribed H and signed-s identities agree within 4.44e-16 and 3.33e-16 relative error. The first local xHII=0.1 crossing is bracketed at zbar[10.248063100947423,10.248027950805152], with linear crossing 10.248037304661773. Neither xHII=0.5 nor .9 was reached in this prefix. These are saved-history checks, not convergence or detection claims.

The previous current worktree changed the driver, background, reaction adapter and thermal files relative to the compiled old trajectory. Rebuilding there would silently change physics. The embedded `source_identity.txt` contains the complete 17-file original identity corpus; all 17 SHA256 values match historical execution receipts. Full Git base `44af42ba60a44a3e9ee23288b766c025c4e0de11` supplies the rest of the crate. An isolated source reconstruction plus a resource-only new wrapper actually compiled and passed the native checkpoint preflight. This removes the concrete rebuild/continuation blocker without a new thermal or transport derivation.

## Current bounded execution

The root coordinator allocated one new continuation with 90,000 accepted steps, 360,000 attempts, 3,000,000 RHS evaluations, 2,700 seconds wall/CPU, one core, 2 GiB address space and 2 GiB output. The old continuation's unknown actual terminal cost remains UNKNOWN and its full 10,800-second reservation is charged conservatively. This is an explicit new allocation, not unspent old headroom. Physical checkpoint counters are unchanged; the 47 orphan rows are preserved separately and will not be used as a resume state or counted twice in the history.

Native build: Rust 1.99.0, Cargo 1.99.0, `cargo build --release --manifest-path rust/rei_microphysics/Cargo.toml --locked --example axbi_plus_recovery_002`, exit0 in 2.10655 seconds. Binary SHA256 `c16932bdd7a9fdb86c20d9ea3d8b08f897663874e1f1b6e35ea39fa3f2db3263`. Native preflight passed at 2026-11-15T15:39:27Z. The root launched the one allowed process at 15:39:48Z. At 15:40:22Z checkpoint241980 had advanced by1,500 accepted steps in32.8431 seconds. The terminal receipt, not this early observation, decides completion.

`plus_recovery/ALLOCATION.json`, `BUILD_RECEIPT.json`, `PREFLIGHT_RECEIPT.json`, the native wrapper, launcher and independent review preserve the exact execution contract. No automatic retry is permitted. A completed fifth baseline still does not complete AX11 or AX12.

## AX11 must remain the original empirical question

The authoritative `FULL_CAMPAIGN_EXECUTION_CONTRACT.json` at `fa20d75e344a28c833a47cbca82315ccbbdf6882` requires baseline plus two refinements, with common physical IC at zbar20. Initial matrix: time targets1e-5/2.5e-6/6.25e-7 for q0,+.01; energy subdivisions16/32/64 for q0,+.01; angles8/16/32 for q+.01,-.01. Twelve new full histories are staged after the baseline family and measured costs are available. This is not the F05 continuum theorem or an interval-root obligation. It does not require high-z HYREC, a full observer tail, total optical depth, CMB sky or a spatial filling factor.

Compare 1,001 common ln(a) points plus actual milestone brackets. Preserve D01 and D12. Richardson estimates require observed order/ratio support; otherwise report a variation envelope without a continuum guarantee. Do not transfer positive-shear errors to negative or half-amplitude cases. Resolve a response only when its supported paired empirical uncertainty is at most0.1|Delta| above the fraction floor1e-7 or temperature floor0.01K. Local target alone cannot establish a full-history error.

A checkpoint immediately before an actual abundance-response peak can support a finite local sensitivity diagnostic with the exact same complete state and photon stocks. It cannot become a refined full-history IC, and coarse-grid interpolation onto a finer spectrum cannot certify the earlier evolution error. The first complete +0.01 run should locate the response peak and its predecessor checkpoint. If the full refinement budget is unaffordable, report the precisely scoped diagnostic and keep AX11 unresolved; do not silently weaken or expand its claim gate.

## Why the critical path stalled, and the correction

The original missing fifth trajectory was left interrupted while adjacent F05, F08 and Type-II work accumulated. Those results are useful within their own sources but cannot close the selected abundance problem. The full saved source corpus and reusable checkpoint were present but not consumed. Support counters, proof strength, process reviews and plots therefore became proxies for progress. The observed worker-handoff failure was also never reduced to its minimal reproducible execution state.

The correction is concrete: preserve all old evidence and costs; recover the exact source; run one finite continuation; compose and analyze the actual five-case family; then spend the next numerical budget on the specific abundance response that limits AX11. Every new support PR must name the original AXBI output and the exact remaining claim gate it changes. New geometry frameworks, generic solver optimization, high-z recombination and plot-only work are paused on this track unless that dependency is demonstrated. A fresh native event, derivative, code path, root certificate or metadata file is not counted as a completed original science node.

Audit coverage is bounded to the retrieved current PR/branch states, the actual remote original run directories, recoverable Dropbox titles/bytes and the authoritative original campaign contract. No claim is made that an unavailable hidden conversation or every deleted external backup was inspected.
