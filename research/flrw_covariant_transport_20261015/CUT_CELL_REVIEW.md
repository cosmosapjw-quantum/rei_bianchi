# Independent cut-cell review

**PASS_SCOPED_CUT_CELL_IMPLEMENTATION_AND_FRESH_SHORT_PILOT.** The changed implementation may be published, and a fresh finite short pilot may run on the actual NCP under the existing contract. Full-history launch remains pending the completed, reviewed pilot/refinement screen.

Reviewed base: `a71052cec02c48c08d6823e00331fab1db654a76`. Requested reviewer model: `gpt-6-astra`, high reasoning; runtime identity not independently observed. This review changed no source/git state and ran no numerical jobs or tests. Previous22 checks were reused, not repeated. Final reviewed hashes are in the JSON companion and match the worker receipts.

## Diagnosis and measured control

The retained baseline q128 pilot reached its20,000 accepted-step cap near z19.973432 without completing z20→19.8. Its original full-launch gate therefore remains pending. The actual h,h/2,h/4 diagnostic identifies HI-straddling cell0 across eight rays as about95% of the photon discrepancy, with order approximately1.9 and much smaller gas errors. This supports a closure/splitting error coefficient; it does not justify weakening the local target.

The candidate uses a common initial partition of the preserved12000-step state and performs9 tentative solves/63 RHS calls. At h, the original total-cell metric is2.648206423745888e-7 and the stronger separated-pool metric is2.648206423744218e-7. Both satisfy the preselected bound7.926958298838388e-7. The total discrepancy is about14.97 times smaller than the retained baseline; h/2 and h/4 give7.185016608031656e-8 and1.8747217064445134e-8. Positive domains and augmented photon/energy ledgers pass. The tiny rounding difference between strong and total metrics does not affect this decision.

This is a local discrepancy-reduction result, not a measured runtime speedup or a global accuracy proof. The checkpoint was explicitly used as an experimental initial state, not resumed as a changed production history.

## Production seam

`inactive_hi_split` defaults false. Activation rejects nonzero q_ref, and backward geometry is rejected. Expanding q0 FLRW gives monotonically decreasing photon energy, so photons below the current H/He minimum fit cutoff cannot reactivate. Future lower-threshold processes or blueshifting geometries are outside this admission.

The existing positive closure is restricted at actual13.60eV, preserving count/reference-energy moments under the frozen internal tolerances. Equality deltas remain active. Four active arrays and two passive arrays retain q-cell/ray indexing. The centered transactional passive merge preserves realizability without clipping. The operation restricts the declared closure; it does not infer unknown true child spectra.

Only active photons enter the unchanged source/BE/Newton chemistry interface. Total photon count, physical energy, continued redshift work and radiation moments include both pools. Transfer does not create absorption or boundary outflow. The adaptive norm sums absolute active and passive differences separately in each cell, using the original total photon denominators/floors. The cancellation-negative-control test confirms that equal total moments cannot hide opposite pool errors.

CheckpointV4 serializes all six arrays and rejectsV3. Exact outer source/config identity binds the variant. Output retains25 history and12 spectrum columns, with total moments and explicitly conservative passive-support envelopes. Four pool VALUE ledger rows distinguish active/passive count/energy. Gamma uses active photons; radiation stress includes both pools.

All physical/controller tolerances are retained: local1e-5, strict<2e-4, Newton1e-11, step/cumulative ledgers1e-10/1e-8, parity1e-12 and existing provider domains. No clipping, threshold change or duplicate photo-event owner was introduced.

## Actual test evidence and decision

The three original partition tests pass; a new passive-merge test passes. The seven new driver tests pass across two preserved attempts. The first attempt passed six and failed the output test because substring `active_photon` also matched `inactive_photon`. The bounded repair compares the exact CSV ledger-name field. Production source did not change for that repair. The corrected output test and new merge test pass in a focused invocation; already passing tests were skipped. This is11 distinct new passing tests, not a replay of the earlier22.

No unresolved defect was found in the changed seam. Publish this scoped unit and proceed to the fresh finite NCP q128 pilot, then the frozen energy/time/angular controls after q128 completes. A capped or incomplete pilot is not a successful screen. Full z20→4 admission requires the actual completed screen and subsequent review; no full-history result is claimed here.
