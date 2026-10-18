# PR171 resource-stop and native-mesh review

**Disposition:** `PASS_SCOPED_RESOURCE_AND_SOURCE_REVIEW; EXECUTION_HOLD`  
**Scientific admission:** `NOT_ISSUED`  
**Review scope:** read-only interpretation of the existing PR171 age64 reference terminal and its native mesh binding. No solver, test, build, postprocessor, or new physics run was performed.

## Source and receiver identity

The frozen source is native base `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, published supplier `57533355976fe10e574d01d338dcc0e9ab9d22a5`, and launch checkout `6465ec502ee23af85cedc5cb73fbccc3254f02d4`. `SOURCE_BINDING.json` records exact matches for all eight native base blobs and hashes the retained `positive_native`, `positive_solver.py`, `positive_native.rs`, `matrix_owner.rs`, and `positive_accessor.rs` payloads. No source edits were made for the run.

The receiver was the warm analytic MD14/BB50k plus Grackle Case-A setup: q=0, 8000 K, initial fractions `[0.01, 0.01, 0.001]`, birth panels 64, angular count 8, source subdivisions 8, and transport cells 16. This lineage is not established as equivalent to BASS009/010.

## Terminal classification

The age64 reference command reached its fixed 600-second command wall cap and was terminated at 600.128026917 seconds (0.128026917-second sampling/termination overrun), exit `-9`, stop `WALL_CAP`. It preserved 35 accepted-prefix states through 53.90625% of the requested interval; no endpoint was completed. The controller recorded 32 provider trial rejections, zero controller retries, and stopped the packet at the first failure. The three remaining commands were not started.

This is a resource-terminated incomplete run, not a completed numerical endpoint or a demonstrated terminal solver error. The 32 rejected provider trials are real internal trial failures and remain preserved; because no endpoint exists, endpoint comparisons are `NOT_EVALUABLE`. Sampled process-tree CPU was 584.49 seconds; wait4 parent CPU excludes the provider child and must not be reported as total tree CPU. Runtime speedup and full-interval ETA remain unknown.

The packet grants one fixed 1800-second allocation with a stop-on-first-resource/domain/binding/RHS failure rule. That stop rule was triggered. The unused aggregate remainder does not authorize continuing the queued commands, relaunching age64, or resetting the deadline. The existing packet is spent for execution purposes; a future solver start requires a new frozen packet and explicit owner approval.

## Static native mesh finding

In the frozen `matrix_owner.rs`, `common_mesh` forms the shared mesh from only the supplied `birth_levels` (lines 299–323). `trial_impl` requires every requested birth midpoint to occur bit-exactly in that mesh and otherwise returns `COHORT_MESH_DOMAIN` (lines 377–391). The frozen native matrix driver constructs its common mesh from levels `[8, 16, 32]`, then supplies requested `birth_count` to the trial (positive_native.rs lines 628–638); the age64 native command would request 64. The existing mesh therefore does not guarantee the required age64 midpoint support.

This is a static source limitation, not an observed age64 native runtime failure: `age64_native` was never launched. Comparing the partial age64 reference prefix with existing native age8/16/32 results would also mix birth-age refinement with different clock meshes and cannot establish matched age convergence.

## Preserved research boundaries

Completed R1–R10/C1–C10 and PR177/178 evidence remain reused; no completed tests or scientific runs were repeated. The Li6/Li7 coefficient contract remains explicit `ElementalElectronicEquality` opt-in, not isotope-resolved coefficients. Single-owner energy accounting and durable-checkpoint requirements remain unchanged. No result was promoted to physical convergence, full reionization, isotope history, or production admission.

## Next dependency

`PR171_RESOURCE_STOP_REVIEW_001` is complete. The next executable solver node is `HOLD_NEW_FROZEN_PACKET_AND_OWNER_APPROVAL`: freeze a new source/receiver-matched packet that either constructs an age64-capable common mesh or limits itself to a distinct reference-only question, then obtain explicit owner approval before any new solver start. Preserve this run's wall cost, saved rejection records, and deadline; do not resume or reset the old allocation.
