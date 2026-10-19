# BR05 continuation handoff

## Completed bounded unit

`BR05_NATIVE_BIRTH_MONITOR_AND_R_PAIR = COMPLETE_VERIFIED_SCOPED_MONITOR_AND_CONTROL`.

Parent PR203 scientific lineage is pinned at final parent HEAD `a8e550846745fc89e79e84ad32567e3fb556c175`. The new scientific source commit, final receipt commit, ZIP SHA-256 and provider/raw-restore identities are recorded in the separately issued publication receipt. Read that receipt and recheck current remote HEAD before continuing. Do not infer its values from a branch name.

Read `docs/REPORT_KO.md`, `evidence/SCIENCE_RESULTS.json`, `evidence/VERIFICATION.json`, `contracts/DAG_PROGRESS.json`, `contracts/SOURCE_IDENTITY.json`, `contracts/PARENT_INPUT_SHA256.json`, `evidence/FAILURE_LEDGER.json`, and `evidence/runtime/NATIVE_ARTIFACT_READBACK_FINAL.json` first. `contracts/PROJECT_POLICY_INPUTS.json` preserves the four user project policy files actually used in this unit.

The source is add-only: 125 parent inputs are byte-identical and eight new Rust/build inputs add an opt-in observational birth monitor. The photon source, twelve physical owners, CX half-flows, and four-corner controller are unchanged. Monitor OFF directly delegates to the parent path. A monitor record marked accepted refers to a successful local fixed-step transaction, not a new outer adaptive acceptance filter.

## Exact new native execution

One `SIGNED_MINUS` native history at `T=8e12 s`, `Nt=16`, birth refinement `r=8` ran 16/16 steps and completed in 41.91796186300053 seconds under the actual one-run wrapper. The argument vector is `SIGNED_MINUS 121 16 0 8e12 false false 2 4 1e-12 8 <monitor-output>`. The absolute CX tolerance was `1e-14` as serialized by the driver.

The final ordinary history is `evidence/native/ap_n16_r8.csv`, SHA-256 `8fe55425a8b406fb6ce09f2a8defd7d27f5439908e82df62e46cb759c256880d`. Its receipt is `evidence/native/ap_n16_r8.json`. Six raw monitor CSVs retain 314,624 birth and final cohort rows, 768 rules, 19,664 panels and 6,144 templates. Cohort/template/rule/node/panel identity, birth time and geometry, Killing vector, spectrum/direction labels, weights, energy and age are retained. Represented zero weights remain in the output. The new long native history recorded zero threshold crossings; it does not establish threshold-crossing accuracy.

The final surviving photon count is `1.00386973104496329e-8` reference-comoving m^-3. The mean age is approximately `1.51113853498e10 s`. Exact Decimal values and all 15 observable comparisons are in the independent pair CSV/JSON outputs. Five comparison histories are reused, not newly executed.

The mixed time/birth difference for `(Nt=16,32) x (r=4,8)` is `2.96732631e-17` in photon count, `20836.57083140278 s` in mean age, `7.7354158350578039e15 s^2` in second age moment, and `3.052254082468e-13` in the q2 diagnostic. These are respectively 0.0960384, 0.0775058, 0.0856057 and 0.0828189 of the absolute mixed differences for r=2 to 4. This is one contracted rectangle, not a universal order or nonlinear absolute-error result.

## Verified scope and remaining numerical issues

Actual full regression: 233 Rust tests, strict all-target Clippy, scoped rustfmt; independent Python tests 9/9. Independent Decimal90/96 analyses cover every actual rule/panel and every birth/final row; source-shape certificates sample one template per rule while mass/raw moments cover all templates. Wolfram checks and primary-source receipts are under `evidence/theory`. Code-audit author overlap is explicitly disclosed; root, theory and runtime verification paths are separate. Three actual corrupt-data mutations were detected. Four final figures at 90 mm and 182 mm were directly viewed and passed 44 data/layout checks after the C9 review.

A fresh directory and fresh build target restored all 133 inputs, passed the new 9 tests and strict Clippy, rebuilt the release driver, and reproduced a small Nt1/r1/T1e9s fixture. Its 53 non-timing history fields and six monitor CSVs match exactly; an independent Python audit passes. This was not another longspan run. Full ZIP cloud raw restoration has a separate publication gate and receipt.

The full native number, total-energy and species-sum ledger residuals are approximately `2.67e-14`, `3.74e-16` and `2.55e-16`. The original independent photon geometry-work comparison is approximately `2.435e-6` under its separately defined normalization; tiny total-energy closure does not certify photon-work quadrature accuracy.

The frozen-reference kernel mass defect is at most `2.85e-17` for actual stored nodes in the Decimal audit. Native source-plus-clock and transport changes relative to that comparator are each about `8e-5`; they are not the evolving gas solution's absolute errors. A maximum physical clock defect of `4.8828125e-4 s` and a finite source-amplitude ratio change are explicitly measured.

Open P2: source-weight division can underflow before the existing downstream underflow flags on extreme inputs; no such case occurs in this actual native dataset. Very small old-reference panels can have poor local relative mass despite tiny absolute mass; retain those rows. The orphan 13-row running snapshot is preserved under `evidence/runtime/orphan_snapshot` with unknown origin and is not another accepted native history. The prior BR04 metadata recovery exception remains disclosed. Prior `Cx(WorkLimit)` is a work-budget termination, not absence of a physical solution.

## Next bounded node

`BR06_FROZEN_NATIVE_GAS_VARIABLE_GEOMETRY_BIRTH_REFERENCE`.

Begin with the actual recorded native step 1 rate-gas, source labels and BASS geometry. Freeze the declared gas owner state while preserving time-varying Killing energies, birth geometry, source normalization, competitive opacity and threshold crossings. Construct an independent positive birth-time/absorption reference; compare r4/r8 while separately refining path-opacity integration. The next unit should resolve the measured source/transport/reference gap before changing any controller. No new longspan nonlinear history is needed by default for this bounded node.

Continue with `physmath-research-loop`, actual sandbox implementation and independent checks. Preserve the production branch, old PRs and source identities. Publish a separate add-only Draft PR and the same full archive to Drive and Dropbox, distinguishing upload acknowledgement, provider hashes and raw restoration.

`LONGSPAN_SOLUTION = NOT_ADMITTED_JOINT_TIME_AGE_CONVERGENCE_INCOMPLETE`; `ISO-COUPLE-P4 = PARTIAL`; `SA-01/02`, `FLRW-CONV`, `BI-SIGNED`, and `FULL_EOR` remain on HOLD. Two-way Einstein feedback remains unimplemented. Future universal order, nonlinear response bounds and full time/age/spectrum/angle convergence require separate evidence.

## Reproduction

Use the verified Rust/Cargo 1.94.1 with rustfmt/Clippy and Python 3.12 environment. The full ZIP contains all five generated data files omitted from GitHub according to `contracts/GITHUB_DATA_OMISSIONS.json`. Run `bash RUN_STAGE.sh verify` before `test`, `light`, or `analyze`. The `native` mode is an explicit separate execution into a fresh output directory, never an automatic recovery retry.
