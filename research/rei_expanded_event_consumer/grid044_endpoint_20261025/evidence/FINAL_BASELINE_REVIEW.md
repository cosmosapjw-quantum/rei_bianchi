# Independent final review: saved-state binding, normalization, scopes and resources

Reviewer: `/root/rei_baseline_intake`. Unit: REI-GRID044-ENDPOINT-BINDING-01. Date: 2026-10-25. The reviewer did not author or implement the consumer. Source and raw evidence were read directly; the PNG was viewed through `view_image`. No scientific suite, provider quadrature, ODE, donor history, old83, fresh83 or NCP run was performed by this review.

## Decision

**PASS_SCOPED_SAVED_STATE_NORMALIZATION_AND_CALLBACK_BINDING.** The actual saved GRID044 endpoint, selected frozen continua, normalization transformation and finite callback checks support the stated instantaneous photo-only counterfactual result. No scientific correction or rerun is required by this review. A metadata deliverable remains for root before publication: the frozen output list names SCENARIO.json, but the reviewed tree does not yet contain it. The necessary scenario values are already in the frozen contract, actual-state binding and source configuration; create that small machine-readable summary or explicitly map its equivalent existing records. This does not change the physics or verification result.

The earlier row-scale ambiguity is resolved. The final tests use absolute contributing-event scales for sources, row maxima of analytic coefficients for the Jacobian, signed-sector absolute sums for energy, and exact zero-row checks. None uses an arbitrary unit denominator that would hide tiny trace-rate errors.

## Reviewed source identity

The final consumer.py, test_consumer.py, render_sources.py, write_rust_client.py and run_bounded.py bytes match PREEXEC_CODE_SNAPSHOT.json. Exact reviewed artifact hashes are in BASELINE_FINAL_EVIDENCE.json. Main scientific source hashes:

- consumer.py: e84cba47f39c1557c0a4c22a7a635b692f22488f9054cda5f66c723101bd3051
- test_consumer.py: af4962769fbd5da97881815d8aef093599f9e62d7d1fc0564fcfd34acb278fc9
- results.json: 0e943294ed12f3cd4493bd2d9be0139f887ed6aace0e7ebc007d5c25cc8337cd
- RESOURCE_RECEIPT.json: 73a24d0529b4ed6cd518a71dcfe99ab1fbe31afa8813e94b8b008cd73ef229a1
- viewed PNG: bc6f2376ebe371325a47dcfbb1f3e3a8d2b4f3a38388c082d7847e3278fdc331

This is a source-bound independent review of the new consumer. Supplier-module identity and microscopic event-ledger review are covered independently by the supplier reviewer; no inherited native suite was replayed.

## Baseline mapping and physical interpretation

Direct comparison of the original NPZ `atomic_abundance_per_Href[:, -1]`, its own atomic_state_labels, ACTUAL_STATE_BINDING.json and results.json gives exact equality after the recorded Li7-before-Li6 → Li6-before-Li7 permutation. All21 populations are preserved, including exact n,T_0,T_1 zeros and positive trace Li values. The code does not use the isotope-conditional `atomic_scaled` field as an absolute abundance. The explicit He4 sum check distinguishes these possible misbindings.

The selected epoch eta=ln7, a≈1/3 and z≈2 matches the opacity-response endpoint. The maximum reported coherence discrepancy is4.440892098500626e-16, below the frozen1e-14 requirement. r=5.151254745827818 m^-3 is the saved normalization, with n_ref0=r*a^3=0.19078721280843758 m^-3 for a_today=1 and the declared coordinate volume. Its bookkeeping number remains independent of the actual hydrogen/baryon counts. Donor temperature14994.847774798709K is explicitly retained as background context; no thermal rate or RR fit is evaluated.

The actual endpoint came from the earlier donor history, while the stellar and external_IGM continua are separately prescribed. No new trajectory under those continua is asserted. Old donor photo rates, RR rates and UV fluxes are copied only as context; the active rates are the immutable stored2x6x3 continuum moments. Source inspection finds no call to source production/oracle/quadrature or any integration driver.

## Formula-to-implementation review

normalize_source_directional implements F=(S-xR)/r and dF=(dS-Rdx-xdR)/r-Fdr/r with finite data and positive-reference checks. The actual fixed-comoving abundance derivative uses R=dR=dr=0 and consumes physical S=r*f, avoiding a second division of the already normalized REC output.

Independent complex-step derivatives of a separately written nonlinear manufactured quotient system check the full changing-reference tangent. A separate fixed-comoving a variation checks r_a=-3r/a. The manufactured controls are explicitly separated from actual astrophysical source data. The omitted quotient term produces absolute error0.03812178499999999, and the omitted density-denominator derivative produces row-scaled error0.2024793964639783; both are resolved by the retained terms.

The existing REC response is called on the actual21 abundance vector and two unit source amplitudes. Its output25 and Jacobian25x23 remain source-response objects. The first21 rows form the material ODE source; the electron-number and three energy rows are diagnostics/receiver inputs. A full photon/thermal/geometry derivative is not inferred. Tests compare all23 columns at the actual point, including source-template columns and zero rows.

Observed source comparison WU/REC=1.924856455018995e-16; actual-point Jacobian complex-step difference=1.488667807882561e-16; changing-reference tangent=2.147543150575634e-16; fixed-comoving a tangent=8.367371580054058e-17. Source energy checks retain independent K and are not made circular by defining K through subtraction.

## Callback and whole-program gates

The Rust client computes A*x from physical coefficients generated through WU incidence and saved REC Gamma. It writes every21x21 Jacobian entry. Its actual-state and positive-supported mathematical-point comparisons agree with the independent REC calculation in saved output. The all-zero and positive-supported points are callback-envelope controls, not new fixed-inventory physical scenarios. The point time-domain admits the frozen epoch only; centered time stencils and outside-point times are rejected. The component box is explicitly separate from isotope-simplex and full physical domain certification.

The deliberately finite wrong Jacobian passes the gateway but differs by0.5 in the independent row-scaled comparison. This directly preserves the distinction between callback admission and Jacobian accuracy. Gateway reuse does not replace the native norm or repeat D1–D5. The witness is transparently a caller assertion; native floating-point environment certification and trajectory error control remain open.

Recorded flags are new_IVPs=0, new_opacity_integrals=0, historical_test_replays=0, new83_runs=0 and NCP_runs=0. L4_ready=false, global_physical_completion=null and thermal_heating_J_m3_s=null. HE input contains number/kinetic moments only, BASS input contains prescribed geometry/signed stocks only, and neither creates missing stopping/angular measure/feedback. These claim boundaries agree with the actual computation.

## Resource and historical evidence preservation

Six recorded process invocations were inspected. Three new scientific stages are the Python changed-contract suite, compiled Rust callback execution and saved-output comparison. Their exact sums are2.900492 CPU s and2.940682361000654 wall s, under30/120. Infrastructure sums are14.682127000000001 CPU s and14.797034617000463 wall s, under60/180. They include the original failed compiler probe, its single-thread linker repair and the successful client build. The failure remains recorded with exit1 and its raw logs; it is not recategorized as a scientific failure or removed from cumulative cost.

The Python32 and Rust9 saved checks are distinct stage records. They are not added to the existing GRID04418, old831 or bootstrap historical test counts. The run paths contain only the new unit and scratch compiler. Existing historical budgets are not rewritten or transferred; wrapper/inspection/remote overhead is explicitly unmeasured, not zero. The frozen old-budget figures documented in the baseline intake continue to apply to their own lineages.

## Direct figure review

Viewed figures/GRID044_ACTUAL_ENDPOINT_SOURCES.png. The top panel displays13 isotope charge events with stellar/external IGM contributions and proper-second/reference-number units. The exact T source zero is labeled without a floor; Li6/Li7 trace contributions remain visible across the logarithmic scale. The middle panel keeps signed radiation loss, binding gain and primary kinetic gain separate; it does not label primary kinetic energy as heat. The lower panel identifies its physical binding residuals and manufactured quotient-omission control, with the mutation's absolute units stated explicitly. The title states instantaneous photo-only counterfactual scope and no new trajectory/feedback. Figure and recorded CSV are consistent with the claim.

## Finding disposition and next action

P1 pre-execution tiny-rate scaling ambiguity: CLOSED by the explicit denominator definitions and retained raw scales. No numerical rerun required.

P3 delivery output SCENARIO.json: OPEN_METADATA_ONLY at the reviewed tree; root can close by serializing already frozen inputs/gates, with no source algorithm change or scientific replay. This is the sole remaining output-contract action identified by this review. Then root may adopt the scoped result, update the central DAG additively, and proceed to expected-SHA publication and the requested source/dual backups. Full-network/L4 remain separate.
