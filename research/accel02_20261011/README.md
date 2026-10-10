# REI-ACCEL02 — C07R interruption recovery

The missing 256-energy native run has now been recovered by actual execution over **z = 15.9 → 4**. Previously completed RUN002 and the 128-energy runs were not rerun. The 128→256 comparison **fails the unchanged spectral target**: the largest normalized difference is 0.1401807633 for ΓHeI, against 0.001. Native evolution, conservation, and spectral convergence are separate results.

| Node | Current state | Exact scope |
|---|---|---|
| N1 | DONE_SCOPED | Pinned source and cold Case-A H/He/thermal native provider |
| N2_TIME | DONE_SCOPED | Published 128×2 same-grid time refinement and conservation |
| N2_SPECTRAL | FAIL / repair ready | Actual 128×2 versus recovered 256×2 whole-interval comparison |
| N2_GAS_003 | Directly measured | All accepted gas/finite/photon checks pass in recovered 003; original 002 all-accepted gas remains NOT_MEASURED |
| N3 | HOLD | New anisotropic paired history awaits numerical admission |
| N4 | DONE_SCOPED | BASS PR140 adoption of the two original reduced histories; no new native H/He receiver run |

Recovered EVENT_COUPLED003 uses 256×2 nodes, r=0, rtol=1e-11. It completed in 629.20 s with maximum energy/initial-energy residual 6.6493278602e-11 and photon-number/initial-H residual 5.5014857431e-10. Both satisfy the frozen 1e-9 bounds at the measured segment endpoints and saved output epochs. This does not establish a continuous-time bound or a separate same-grid temporal comparison for 256 nodes.

## Read first

- `REPORT_KO.md`: actual recovery, results, physical limitations, and next research action.
- `NEXT_DAG.json`: machine-readable state and dependency graph.
- `RESUME_PROMPT_KO.md`: self-contained next-session/local Codex prompt.
- `n2/evidence/EVENT_SPECTRAL_COMPARISON_RECOVERED.json`: both 65-epoch and 129-epoch comparisons, each normalized on its own selected epochs.
- `review/recovery/SPECTRAL_DECISION.json`: independent decision for recovered outputs; old reviews are preserved.
- `recovery/QUADRATURE_NEXT_STEP.md` and `.json`: concrete conservative quadrature candidates; no claim that the root cause is already proved.
- `figures/NATIVE_SPECTRAL_RECOVERED_128_256.png`: solid 128/dashed 256 conditional diagnostic, not a converged scientific prediction.

## Immediate next action

Q0 source/IC attribution is independently accepted within its scope, without ODE calls; read `recovery/Q0_SOURCE_ATTRIBUTION.md/.json` and its bounded independent review. It directly finds source quadrature error (256-grid reference-volume number 5.08064%, energy 3.96376% against the declared interpolation) and nonmonotone initial-UVB discretization error. The 256-grid initial full-number difference of +17.3215% is overwhelmingly in sub-HI 10–13.6 eV photons, not a 17.3% ionizing-photon or heating error. These do not apportion the complete evolved error. Select one bounded fixed-q composite-Gauss candidate with immutable positive weights and predetermined initial-UVB/source/threshold trajectory knots. Do not rerun Q0 merely to recover its metrics. Apply it consistently inside the actual RHS. It is not exact moving-threshold alignment. A moving q/weight substitution into the current packet equations is forbidden without the corresponding remap/weight derivatives; a genuine two-moment fixed-cell scheme is a larger alternative, documented separately. Do not patch only reported Γ, heat, or counters, or launch unbounded uniform grid doubling.

In parallel, a validated checkpoint-resume CLI, saved-state source profiling, and a new native-history BASS schema can proceed. Current `RESTART.npz` is evidence, not an implemented resume interface.

## Scope and recovery

Conditional IC at z15.9: T20 K, xHII=2e-4, neutral He. Pinned HM12 UVB is initial-only; evolving emissivity is evaluated in the RHS within 10–50,000 eV. The closure is homogeneous primary-only Case A with imported Grackle RR/CI/DR/CE/ff and a prescribed isotropic CMB bath. CR, RCT, secondary cascades, diffuse recombination transport, and stress backreaction are not included. Ionic fraction is not filling factor Q; mean-scale-factor redshift is not directional observed redshift.

The scratch loss is classified as RUNTIME_INTERRUPTION_RECOVERY. C06 archive and native binary were restored and identity checked; missing local-only 003 evidence and transcript-only claims were not inherited. C07R2 is an overlay containing this research tree, raw arrays, exact as-run sources, provider tables, and the verified binary. It still requires the published Git repository; it is not a standalone full-repository bundle. Read `recovery/C07R*_BACKUP_RECEIPT.json` and final publication receipts for exact objects and upload status. UPLOAD_VERIFIED does not imply RESTORE_VERIFIED.

Campaign path `20261011` is the Korean-date identifier. Actual execution timestamps are in UTC (2026-10-10 for this recovery). Preserve first failures, contracts, and original atomic/CR/RCT lanes. No RUN002 replay, relaxed budgets, negative clipping, owner-branch force update, or automatic merge.
