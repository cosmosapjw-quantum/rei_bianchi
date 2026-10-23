# ANGTHERM01: directional reionization thermochemistry on prescribed Bianchi backgrounds

**Scientific status: PASS for the conditional finite system.** See SCIENTIFIC_DECISION.md and the independently authored INDEPENDENT_REVIEW.md. The implementation, ten completed raw trajectories, seven figures and source inputs are bundled here. Final publication and backup facts are recorded separately in FINAL_DELIVERY.json.

## Start here

| Purpose | File |
|---|---|
| Korean result, physical interpretation and limits | REPORT_KO.md |
| Mathematical definitions, units, equations and exact reductions | THEORY.md |
| Frozen experiment and tolerances | EXECUTION_CONTRACT.md, MATCHED_MEAN_CONTROL.md |
| Independent theory and implementation review | MATH_REVIEW.md, INDEPENDENT_REVIEW.md |
| Actual numeric tables and costs | RESULTS_OBSERVED.md, FINAL_RUN_RECEIPT.json |
| Safe preparation, inspection and separate reproduction recipe | REPRODUCE.md |
| Research stages and global remaining dependencies | LOOP_PROGRESS.md, DAG.json |
| Copyable next-thread instructions | HANDOFF_KO.md |
| Source survey and immutable copies | inputs/source_indexes/, inputs/COPY_MANIFEST.json |

## Implementation

The main implementation is code/angular_model.py. It imports the unmodified bundled atomic fit provider, evaluates exact fixed-covariant-momentum photon drift, evolves nine electronic fractions and 6M optical depths with eight independent ledgers, and supplies an analytic Jacobian. The separate full event oracle retains 21 isotope populations and 48M direct photon packets. At M4 the dimensions are 41 and 221. Eligibility conditions and physical approximations are explicit in THEORY.md.

code/run_cases.py saves per-case raw NPZ histories, every accepted node, threshold-segment checkpoints, configuration and diagnostics. code/bounded_run.py records this session's finite resource budget and historical recovery commands. It is intentionally not a generic queue that reruns completed work. The source-preserving preparation command, from this unit directory, is:

    sh run_fresh.sh --prepare-only

That command checks 34 copied objects and executes zero IVPs. For a clean reproduction in a separate temporary copy, use REPRODUCE.md. The actual run environment was Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8 with one BLAS thread. No donor IVP, external service or compiled atomic library is required to execute the supplied model.

## Results to distinguish

The source-preserving full/reduced comparison and the angular-continuum question are different. The M4 population disagreement is at most 8.17e-11, while the observed M8/M16 lithium-fraction difference is 4.64e-5. The same-background directional/mean-redshift lithium signal is about 0.049. It is a fraction of lithium, whose total abundance is only 5.0001e-10/Href. The plotted bulk temperature/electron differences remain small.

figures/07_lithium_threshold.png displays that chemical signal and its angular-refinement qualification. figures/02_stress_work.png displays the signed radiation stress and work. The remaining figures show evolution, conservation, finite-system agreement, angular diagnostics and observed costs.

The ten trajectories consume ten completed cases plus one conservatively charged interrupted attempt. Final cumulative scientific/postprocessing accounting is CPU 224.778756 s of 300 s and wall 238.352717 s of 420 s. This includes failures, conservative check charges and figure work, not network delivery time. Unequal native norms and tolerances preclude a universal or equal-error timing-speedup claim.

## Provenance and publication

This unit adds to cosmosapjw-quantum/rei_bianchi PR221. The former scientific base is 73c5e00cac26b4efc782446975bd6b6762555997. Existing PR222 work remains a separate valid branch. The prepared source/theory checkpoint was published at 00303ab27c33a7afa0cec61679af78ef72e3f4aa and backed up separately. The full source census is retained in that prepared archive; the relevant sources and manifests required for this unit are bundled here.

Vendor attribution and licenses remain beside their original sources. TRAPHIC and C2-Ray are primary methodological references; their full solvers were not imported. Reuse does not transfer their physical validation to this prescribed finite inventory.

The final ZIP is the complete executable snapshot, including binary background histories, raw NPZ results and PNG figures. The Git publication is the reviewable text source, theory, input provenance and result metadata; binary histories and figures are supplied in the companion ZIP. A Git text-only copy therefore needs that companion archive before the 34-file prepare check or a fresh trajectory can run. The archive itself contains every required file and needs no download during execution.

This delivery route was chosen after a 262,312-byte binary Git create_blob request returned no receipt before interruption. No successful binary upload is inferred. Actual Git path coverage and the complete archive member count are recorded in FINAL_DELIVERY.json. The delivery receipt is necessarily created after the ZIP and is supplied as a small sidecar and an additive Git metadata commit; the archive cannot contain its own final hash.
