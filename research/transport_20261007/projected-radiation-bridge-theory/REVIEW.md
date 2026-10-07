# Independent read-only design review

2026-10-07 UTC. Verdict: **DESIGN-QUALIFIED**, conditional on the explicit evidence gates in the proposal. This is not an implementation, numerical acceptance, or midpoint acceptance.

## Archived original reviewed artifact identities

The following SHA-256 values identify the corrected archived originals inspected in this review, not the relocated publication bytes. Later substantive scientific edits require renewed review.

- BRIDGE_DESIGN.md: `ec9dc580636aec47936dec230749061bb0bae8fa5a2e468feae22822b12a051a`
- TAIL_DIAGNOSTIC.md: `4c6404c3b928108bc6b7dff11b5bf0f665bc1c5aea343e3b65d1610e26d0ed15`
- TEST_FIRST_AND_RESOURCES.md: `b6cea01d47d352f0a9d8a1b907aa2ba0afd61e1f875a8df45d78df45df847eab`

## Material corrections incorporated

1. **Replay cost is distinct from projected-lane cost.** Resource section 3 now accounts for fresh-node historical traversal, optional reuse across Newton trials only for fixed nodes/accepted prior paths, and the possible quadratic-in-history cost. Shared gas-path descriptors save storage without eliminating characteristic evaluations.
2. **Replay requires historical spectral topology.** Bridge section 8.B and resource section 3 now require transformed source/threshold/staging edges from all retained descriptors, or an independently certified adaptive alternative. The projected current-transaction bound C<=P+10 is explicitly unavailable for the replay reference; its actual C_ref and oracle nodes must be counted.
3. **Projection isolation uses the same numerical source/rate history.** Bridge section 8.B now requires identical event-local frozen q_s/lambda approximations, paths, anchors and time partitions. A continuously varying source or changed rate quadrature belongs to the separate physical-reference comparison, not this projection-error estimate.
4. The tail diagnostic now conditions the claim that spectral weighting further reduces amplitude on a geometric weight 0<w<1, rather than positivity alone.

## Scientific checks and source evidence

- **Moment rule and source ownership:** Bridge section 4 reproduces the initial-measure rule in `../../../docs/research_program/igm_next_nodes_20261007/boundary-design/INITIAL_MOMENT_QUADRATURE_OPTION.md`: n_J and m_J are formed before owner evaluation, the unit-initial/zero-source transaction receives weight n_J, and the zero-initial/source transaction uses geometric eta weights. The displayed ordinary/front restriction formulas and antiderivatives are algebraically consistent. Post-budget normalization is excluded. Kernel-carried energy determines endpoint M, with the conversion and next-start discrepancy measured rather than repaired.
- **Closure and support:** Bridge sections 3 and 5 correctly retain the interior (1-y) right-front taper implemented by `../continuous-boundary-prototype-v2/src/primitives.rs`, `closure_stats` and `density_value`. A left split child cannot acquire an artificial zero at an interior cut. The initially empty source's fixed lower edge has a zero exact trace, and the proposed ordinary approximation there is explicitly a tested shape error. The beta bracket and width/coordinate restrictions agree with `reconstruct` and `../continuous-boundary-prototype-v2/ARITHMETIC_ADMISSION.json`; refinement or merging does not automatically establish admission.
- **Tails:** Bridge section 6 correctly distinguishes the exponential segment's -lambda*h logarithmic attenuation from the baseline BE -log1p(dt*opacity) in `../../../rust/rei_microphysics/src/igm_continuous.rs:493-515`. The 1e-20 photon/H and 1e-30 erg/H cumulative caps agree with that source at lines 548-549. Shared-scale N/M is explicitly new, separately tested state; V2's `Inventory::LogTail` tag does not implement its transport. Dimensional bounds, finite-log versus empty provenance, source restart, species owners, and tail-only export are required rather than assumed.
- **Physical diagnostic:** The unchanged manufactured configuration, FLRW background formulas, Verner HI fit, and saved first-interval reference endpoint support the diagnostic's setup. The inspected sources are `../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg`, the immutable background/atomic files under `../../../rust/rei_microphysics/src/`, and `../short-hhe-coupling/results/reference_tighter.csv`. The source-off witness is a frozen-coefficient plausibility calculation; it is correctly not promoted to a coupled four-interval trajectory. The reviewer did not independently recompute its printed scalar table.
- **Gas and error separation:** Bridge sections 2, 7 and 8 preserve the shared A/B gas increments and midpoint qualifications in `../short-hhe-midpoint-theory/METHOD_DERIVATION.md`, sections 2-3 and 6-7. Fixed projection epochs with unprojected substeps are distinguished from every-step total-method refinement. The old 2e-4 reference is not reused as an 8e-4 endpoint oracle, and zero outflow over four base intervals is not claimed as a boundary-export test.
- **Resources:** The proposed counts 3192, 3132 and 6264 are consistent with the stated simple current-transaction geometry. All remain conditional candidates; actual fragments, simultaneous trial/closure/oracle data and historical replay are additional accounting requirements. The old solver's 16-iteration and 12-line-search caps are visible in `../short-hhe-coupling/src/coupled.rs:179-220` and do not imply only four radiation evaluations per step. No measured runtime feasibility is claimed.

## Claim ceiling and unresolved gates

No additional mathematical/design defect was identified within this bounded review. Tail primitives and their error enclosures, stable closure restrictions, actual narrow/steep-wake admission, nonlinear coupled acceptance, reference-pair tightening, observation-schedule invariance, and the specified resource envelope still require their stated evidence. Midpoint acceptance remains external. A later nonzero-boundary experiment and all long histories remain separately gated.

This review supplied source and algebraic inspection, without a new solver run, experiment, compilation, candidate implementation, or numerical history.
