# Final bounded independent review

Decision: **PASS_SCOPED for saved-history scientific results and delivery of the corrected vector figure set; final visual QA PARTIAL.** The ten individual PDF/SVG figures and ten-page PDF bundle may be delivered with the limitations below. A claim that all ten corrected pages have passed final raster inspection, or that the set is fully publication-ready, is not admitted.

This is the finalization of the existing independent review and its one targeted display repair. No new IVP, clock integration, diagnostic calculation, rendering, child review, or retry was performed by this reviewer. Requested reviewer tier: Astra under AGENTS.md; observed runtime model: unknown. Independence is a separate review agent that did not implement the figures, inspecting existing source, results, metadata and images; it is not an independently rerun solver validation.

The frozen physmath-research-loop 1.0.0 contract and its R6/C9 and evidence/reuse policies govern this unit. The available cloud 1.3.0 policy was also read; it does not replace the frozen scientific contract or start a further cycle. Both support reusing unchanged evidence and declaring remaining obligations. AGENTS.md's finite-review and typed-identity policies apply.

## Evidence and admitted science

Read `theory/CLOCK_FIGURE_CONTRACT.md`, `theory/DIAGNOSTIC_CONTRACT.md`, `REPORT_KO.md`, `outputs/DIAGNOSTICS.json`, relevant source in `implementation/diagnostics.py`, both figure source files, `figures/FIGURE_METADATA.json`, `figures/RENDER_PROGRESS.json`, `figures/RASTER_BUDGET.json`, and `outputs/FIGURE_REPAIR_RESULT.json`.

The existing diagnostic execution reports 361 common saved epochs, zero IVP calls and zero new physical samples. The source checks common grids, equal initial stocks, ON scale equality, exact CSV/NPZ population agreement and the saved eta-to-z relation. The plotting conversion is elapsed seconds divided by 31557600000000, with mean redshift from 21 exp(-eta)-1 and inverse ticks from the saved eta/time relation. Early rounded redshift degeneracy is explicitly labeled. The adopted bath remains 300 K; no 8 K trajectory is admitted.

The five recorded abundance groups cover indices 0–16 exactly once, including Li IV. The overview has all 17 ON_refined states with explicit fixed isotope multipliers; the grouped plots use unscaled abundance and three case styles. The source-response array is ON_base minus OFF_base divided by the frozen state scale. It represents the configured source/escape switch. Refinement is the signed ON_base-minus-ON_refined difference divided by that same scale. The recorded maximum 9.475629213e-8 satisfies the unchanged 1e-5 saved-point criterion. This is two-resolution agreement, not a convergence order or a physical error bar.

Conservation uses baryon plus external ledger and heavy charge minus electron ledger, with fast stocks and hidden Li6 included. Saved and recomputed residuals agree exactly in the recorded diagnostics. Maximum baryon and charge residuals, 1.304067965e-12 and 6.536073223e-13, satisfy the original 1.0820350005e-8 threshold. Open-system inventory change is not confused with a residual. The supply/loss interpretation of n and thermal T, sampled 1% sustained times, retained Li I extrema, and the limited knot/minimum inference are supported within the report's saved-sample scope. No new strong no-go, global continuous-time accuracy certificate, anisotropy attribution or self-consistent cosmological prediction is admitted.

## Visual evidence and repair outcome

Directly inspected corrected `figures/preview-01.png`, `preview-02.png` and `preview-03.png`: overview and first two abundance groups. Scientific state labels, case styles, axes, legends and notes are readable at the supplied preview size, without visible label clipping. The overview now discloses multipliers and an eight-decade window; these two grouped views have bounded decade ranges. This closes the observed internal-state-label and excessive-range findings for the directly viewed pages.

Corrected pages 4–10 were **not newly raster-inspected**. Source and metadata support their scientific content, coverage and label changes. The common renderer's layout and the earlier attempt's inspection are useful bounded reuse evidence, but cannot certify every changed final page: groups 3–5 have changed y windows, and all changed labels remain subject to final-page layout checking. The existing source/refinement/conservation numerical arrays and scientific mappings are unchanged by the display repair. No unperformed visual check is marked PASS.

The repair result is `FAILED` because the bounded raster stage exhausted its combined CPU ceiling after vector generation. The progress record explicitly reports all ten vectors and the bundle complete. Three corrected preview files exist; the fourth is incomplete and is not evidence. Named attempt-1 PNGs are stale and must be kept out of the corrected delivery. Their prior inspection is historical evidence only. Delivery of completed vector artifacts is compatible with the raster execution failure, provided the failure and partial visual status remain visible.

## Minimal closeout corrections

1. Point the report to `review/REVIEW.json`, and state that only corrected pages 1–3 received final raster inspection. Do not summarize the failed raster stage as a fully successful repair execution.
2. Record the authorized display amendment beside the original figure contract: fixed isotope multipliers in the overview and bounded y windows omit positive offscale vertices from the rendered geometry. All raw samples remain in saved tables/`plot_data.json`; metadata counts disclose omissions. The original sentence promising all positive samples in vector geometry is superseded for this delivery. No numerical stock was floored, smoothed or replaced.
3. Describe the early-transient panel as resolving n, T I and T II only. It does not recover every offscale early He/Li point in the grouped views.
4. Quarantine stale attempt-1 named PNGs and the incomplete preview from the final delivery; retain the completed corrected vectors, three valid previews and historical attempt records.

These are disclosure/packaging corrections, not a new scientific gate or authorization for further computation. Full final visual QA remains an explicit delivery limitation; any later publication-layout completion would inspect the seven remaining corrected pages within separately available resources. The present positive transition is to preserve and deliver the completed vector set and scoped scientific report, not to rerender or reopen the review loop.

Global status remains working 33/88, central 28/88 and physical-fast 4/7. Local figure completion does not increment the original DAG. Publication/backup acknowledgements are outside this review and must be reported from actual delivery receipts.
