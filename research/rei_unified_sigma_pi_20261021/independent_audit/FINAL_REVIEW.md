# Final independent PHYS-MATH-CODE and figure audit

**Decision: `PASS_SCOPED_PRELIMINARY`.** The recovered and completed Lane B component pilot and its z=2 continuations are `COMPLETE_WITH_VERIFIED_RAW`. There are **no unresolved material findings within this explicitly restricted scientific scope**. Final Git publication and final Drive/Dropbox backup verification remain root delivery tasks; this receipt does not claim those later operations have occurred.

Reviewer: `/root/final_audit`, independent nonimplementing Astra reviewer. This closure consolidates the completed source, raw, operational-repair, interpretation and actual-PNG reviews. It performs no new IVP, benchmark or numerical gate replay.

## Scope and actual counts

| Cohort | Verified scope |
|---|---|
| Historical baseline | 91 nominal + 3 refinement histories, z=20→4, preserved |
| Component grid | 175 nominal = 35 exact historical references + 140 new nominal histories |
| New B1 computation | 140 nominal + 3 refinements = 143 IVPs; 35 reference reuses involve no ODE calls |
| Unique histories | 91 + 175 − 35 = 231 nominal; 6 refinement histories; 237 total |
| B2 extension | All 237 full-state tails complete, z=4→2; no old-prefix replay or ODE retry |
| Joined samples | 121 historical samples + 32 appended samples = 153 per history; 36,261 total |

The model is the contracted collisionless, non-tilted LRS Bianchi I system with independent initial matter and radiation quadrupoles. All 40 nominal or 56 refined state coordinates, including geometry and elapsed proper time, are retained at the z=4 join. Only the allowed integration endpoint extends to z=2.

The full spatial Frobenius convention is explicit: `S_F = sqrt(6) s/H`, `Sigma_F = abs(S_F)`, `P_X = sqrt(6) K p_X/H²`, and `Pi_total = abs(P_m + P_r)`, with `K = 8 pi G/c²`, stress in J/m³ and proper-time H in s⁻¹. This distinguishes the signed tensor sum from a sum of component magnitudes. PR198's half-contraction quantities require their explicit sqrt(2) conversion, and that conversion does not make different sources identical IVPs.

Photons and exactly massless neutrinos continue to share the restricted brightness initialization and collisionless evolution. Independent photon/neutrino initial quadrupoles or collision operators are not established here.

## Exact source identity

| Role | SHA256 |
|---|---|
| runner_original_executed | `49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97` |
| runner_repaired_current | `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64` |
| plot_final | `3d7e42a0321caa5189dd566c57b660d162f7099cda000fcc316ea6950475dcad` |
| component_adapter | `36d107b0fee422321e6daef1d43d88f6e93e2751c83331ca971bc01f6db9490d` |
| data_only_receipt_recovery | `a44256bcee0919700da9eb2863c90535c3043cb93683a4d56fb864fcb0be8571` |
| scientific_postprocessing | `a0f21b87bd18c6c3c21245bfc796b501751c067a169b7c0c4c6d51377629b6e0` |

The original runner produced B1's 143 new histories and B2's first 100 saved tails. The repaired runner produced only the 137 previously unlaunched tails. The old runner snapshot, source transition, attempt records and recovery provenance remain preserved. The operational correction changes boolean serialization and bounded execution bookkeeping; it does not change the physical RHS, solver tolerances or initial conditions.

## The 100 recovered tails

These cases contain complete saved tail and joined raw arrays. Their original final RESULT serialization failed because a NumPy boolean was not JSON serializable. The original processes therefore retain `FAILED_WORKER_EXIT` with the recorded supervisor exit value 124. After independent saved-data verification, the corrected receipts use the explicit basis `SAVED_RAW_REVALIDATED_AFTER_SERIALIZATION_FAILURE`. The recovery process exited successfully and made **zero ODE calls**.

The original failed RESULT is retained as `RESULT.serialization_failure.json`; input, attempt, raw/tail hashes and historical charged debit remain intact. Complete endpoint coverage, exact joins, state and diagnostic prefixes, signed normalization, positivity samples and other contracted raw gates were verified from the saved arrays.

Unrecorded solver-success flags, solver messages, function-evaluation counts, worker wall times and peak RSS remain explicitly unavailable. Complete endpoint data are evidence of the saved trajectory; they are not substituted for an observed successful original worker exit. This limitation is preserved in the final verdict and case receipts.

## Numerical and interpretation decisions

The three B1 and six B2 selected refinement controls pass their scoped gates. The data audit checks the exact stored source/config/raw identity, full-state continuation, requested endpoint, dimensions, component sum and norm relations, packet/number properties and contracted 64-node radiation-brightness samples. It does not certify uniform truncation error over a continuous parameter domain or brightness positivity between all angular nodes.

B2's cumulative charged child time is 100.95804054901964 s under its unchanged 120 s envelope, including the original serialization-failure debit. The 137 unlaunched cases ran with at most two workers and a 10 s deadline within the pre-existing 30 s upper bound. No NCP execution, benchmark or measured speedup is claimed.

The separately audited interpretation supports the following finite-grid statements:

- Initially opposite matter/radiation stresses can sum to zero while later generating nonzero signed shear. Initial cancellation is not isotropy.
- In the two selected opposite-component, zero-initial-shear cases, the largest stored absolute shear occurs at z=4.371956272299825; source-evaluated derivatives change sign before the next stored sample at z=4.308095462679229. These are a sampled maximum and a derivative bracket.
- By z=2, the two absolute shears retain approximately 85.25% of their respective stored maxima.
- At the computed `Sigma_F_i = 0.003` section, all 25 signed final shears are positive at z=4, while four are negative at z=2. This count is determined from saved values.
- Finite matter/radiation response secants at initial amplitude ±0.0003 use four computed endpoints. They do not establish a universal response law, exact sign symmetry or continuous interpolation certificate.

## Actual figure verdict

**`PASS_SCOPED_ACTUAL_RENDER_AND_DATA_MAPPING`.** Actual PNG inspection covered the component detail pages and the repaired baseline/history print pages, followed by the final signed-shear joint rendering. Root separately inspected the four main images below. The final versions have readable labels and formulas, no remaining clipping or overlap in the inspected renderings, explicit redshift endpoints and the z=4 join, and clear distinctions between signed components, signed shear and nonnegative norms.

| Main final PNG | SHA256 |
|---|---|
| component_plane_sigma_0.png | `4866ccb403996a6f85e87ca7a4f00b402ee2dbdad17d30c1828daaaecc8caf7b` |
| opposite_component_histories_print.png | `70adc66093e5f7e0058462c6d14491fdd93fdd3c6a58b3d2373468d9e2aba03c` |
| signed_shear_joint_sigma_0p003.png | `69da6951d1defef35bb4b25249bbd3b9cba12ef08ccbc6b0cf999a8947ded449` |
| radiation_baseline_and_controls_print.png | `d00fc046dcea428863304bfe6a9eb4ba62bdfb2d6e9ebf6186f21631e66bffdb` |

The component sections use categorical labels for the actual nonuniform initial values; they do not imply interpolated surfaces. The selected joint figure shares each quantity's color scale across z=4 and z=2, and the opposite-component history panels share symmetric shear limits. Faint colors near zero are not used to infer the four-case sign count.

The seven 7.2-inch detail pages and separate 7.2-inch print editions are suitable for the reviewed approximately 183-mm double-column preliminary presentation. The 28-panel overview remains a navigation view. A 90-mm single-column typography certificate is outside this verdict. The final plot manifest binds PDF companions and plot CSVs; PDF typography was not independently asserted beyond the reviewed generated figure layout.

The completed repairs include the failed/raw plot admission gate, cross-profile debit preservation, SI label, print page separation, title wrapping, shared history limits and the final joint-figure colorbar layout. The bounded 512-entry render cache preserves the verified case/config/hash gate and immutable cached arrays; no performance benchmark claim follows. Generation-time `PENDING_REVIEW` fields in a historical manifest are superseded for scientific admission by this later receipt, without rewriting their snapshot history.

## Prior lane decisions and limits

PR198 retains `PASS_SCOPED_PRELIMINARY`; its 625 + 606 historical trajectories are not added to or identified with this 175-point grid. The recovered original 94-history gate remains closed and was not rerun.

`NATIVE_AGE_TIME_CONVERGENCE = HOLD`, `NONLINEAR_GRACKLE_RESPONSE_BOUND = NOT_ESTABLISHED`, and `PRODUCTION_SCIENTIFIC_ADMISSION = NOT_ISSUED` remain unchanged. The V12 cap of 180 s, debit of 200.39897231891518 s and remaining 100 jobs marked `NOT_AUTHORIZED` are preserved. No result here upgrades general non-LRS/tilted physics, native reionization, observational likelihood or production admission.

## Evidence chain

These are existing completed evidence artifacts; this closure does not rerun their numerical checks.

| Artifact | Decision or role | SHA256 |
|---|---|---|
| CODE_PREREVIEW.json | PASS_SCOPED_CODE_EXECUTION | `e4f06cc6c0439cbbd4b20559331d94624ad5a5047e05b05bbc9355afc42fc671` |
| B1_RAW_AUDIT.json | PASS_SCOPED_NUMERICAL_RAW | `2737322b8f597b2518a074b13b92d5ff26a3fc562c2a1973bbe8d4e1560252bc` |
| B2_RECEIPT_FAILURE_RAW_AUDIT.json | PASS_DATA_ONLY_RECOVERY | `537c00b087e9c302829aef7a3911bd9a34f64c27b78c69f57948d00e2871301b` |
| OPERATIONAL_REPAIR_REVIEW.json | PASS_SCOPED_OPERATIONAL_REPAIR | `fab54746c084eebbf27d1824fd8023c11cdd01a2057e906f7fa6a641e3d4ad36` |
| B2_FINAL_RAW_AUDIT.json | PASS_SCOPED_NUMERICAL_RAW | `7f65d6bfb9c9b97ae84fa4b73421d94ddcf6ddc265fbdc6a3fe7af19f0afde62` |
| D7_INTERPRETATION_REVIEW.json | PASS_SCOPED_DERIVED_AND_NUMERIC_INTERPRETATION | `ba62cf5ce2f3ff864d538b6a9b1c1d14a6cef2c070d2e7f9e462436e55c67a61` |
| ROOT_FIGURE_REVIEW.json | PASS_SCOPED_MAIN_FIGURES | `68a13868715ae6c2b0672c533d010e4191bbbe7882aef003845f6ed133e85f93` |
| UNIFIED_EXECUTION_CONTRACT.md | Identity-bound evidence | `e6e35bf3558e3b27bffa6831416494ef210d1c2a2d3eedd24eb313be4fa91ff5` |
| PHYS_MATH_CONTRACT_REVIEW.json | Identity-bound evidence | `c255f8945791624eed3bf73a83aeb2f9c4d8636ba81836908d88589e4f6ad618` |
| OPERATIONAL_REPAIR_AUTHORIZATION.json | Identity-bound evidence | `bdad798736780bb006518abd2a4f7ceae8934db6253146217ea84a40c42b444c` |
| OPERATIONAL_REPAIR.json | Identity-bound evidence | `5ae967b0380d50657ad749182ccdeebac2bb1c0527a03fd55abba92aef64b493` |
| SERIALIZATION_RECEIPT_RECOVERY.json | Identity-bound evidence | `be880441b30f8897a318b11348b5a2d8f0d4647edb96bd399fa6a56832b8dad1` |
| NEW_SCIENTIFIC_EVIDENCE.json | Identity-bound evidence | `041e593cdf390ff6bca18b88ebf55da9d5a9aa5821e27bb2130a6e6a550117c6` |
| NEW_SCIENTIFIC_RESULTS_KO.md | Identity-bound evidence | `75bd9c94bf3d002df226a2bd041a59a61151e7c2a5f4f56be40dcdaffa7ca290` |
| PLOT_MANIFEST.json | Identity-bound evidence | `8e98a9c53b44cbe08515bf05ce966441c37525c222c07697cdf8c6484c899476` |

## Delivery status and next node

The scoped scientific preliminary gate is closed. **Final Git publication/readback and final create-only Drive/Dropbox upload/full-readback receipts are pending outside that scientific gate.** The next authorized node is D6: controlled additive publication using the expected remote head, followed by final dual backup, publication ACK, integrated status and handoff. No further scientific run is required to publish this scoped pilot.

Machine-readable verdict: `FINAL_REVIEW.json` (SHA256 `9d150941505c8815fefd7d2fbf4cc2d7d97c3a540805745c04a2e2faf51ca0e9`).
