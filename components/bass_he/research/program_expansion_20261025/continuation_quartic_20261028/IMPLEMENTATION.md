# QUARTIC12 implementation and bounded execution handoff

This unit implements the root's frozen full nonnegative even-quartic contract. It imports unchanged EXFOR11 definitions and reuses only the exact parser, inherited geometry and exact matrix inverse. It never invokes predecessor campaigns or suites. Preparation performs compile-only syntax checking; scientific imports, controls, actual cases, and plots wait for the actual S05 publication pin and explicit root GO after fresh intake.

## Equation-to-code map

`src/quartic_aperture.py` stores signed coefficients of `q(mu^2)=b0+b1*mu^2+b2*mu^4`, full integrals `(2,2/3,2/5)`, the fixed proven box `B=160`, and normalization floor `49/4800000`. `angle_row` derives exact cosine, square/fourth-power intervals and independent outward 2^-60 rounding, midpoint and fixed box-wide perturbation epsilon. `system` applies all four sensitivity windows with outer/inner offsets, all three signed box constraints and Dfloor, then either nodal/cell Bernstein positivity or the endpoint-exact two-parameter cone. Exact duplicate rows retain the tighter RHS, with counts recorded.

`enumerate_shared` attempts every active-constraint combination and calls the unchanged exact inverse. It shares inverse work across each identical matrix's energy RHS; endpoint-zero inner and outer share the same matrix too. Each RHS independently checks every inequality and deduplicates feasible vertices. It records active subsets, singular subsets, actual inverse calls, invertible subsets, RHS candidates, feasible subsets and unique vertices. The saved inverse-call count includes singular attempts, distinguished from invertible matrices.

`moments` integrates nonnegative monomials over the inherited coincidence inner/outer interval unions and exact strip widths. `signed_numerator` reverses each moment endpoint when its coefficient is negative. The lower numerator is concave and the upper numerator convex. For `b=sum lambda_v v`, the denominator weights `lambda_v D(v)/D(b)` sum to one. Jensen therefore bounds the lower ratio below by the corresponding weighted vertex lower ratios and the upper ratio above by weighted vertex upper ratios. Minimizing/maximizing the vertex envelopes gives the outer certificate. Inner vertices provide the specific minimum-upper and maximum-lower witnesses used in brackets, without asserting an attained-range equality.

`quadratic_minimum` classifies each inner vertex by endpoint values and the interior stationary value when applicable. A deterministic witness prefers a negative old folded Bernstein coordinate if available, then exact lexicographic order. Its exact minimum, coefficients, old coordinates, normalization and observed-angle enclosures are saved. Previous degree-four results are read unchanged from saved EXFOR11 JSON with its hash, without recomputation.

## Controls and independent reader

Seven new control methods cover signed row perturbations, B/Dfloor proofs, true positivity versus cell controls and the endpoint cone, nested meshes and signed known polytopes, manufactured rational geometry/moments, concave/convex denominator weighting, and source/type/physical boundaries. The saved reader independently recomputes exact scalar checks from JSON; it is not a second optimizer. It checks vertex inequalities, box/Dfloor, inner exact quadratic positivity and data windows, inner-outer inclusion, all stored objective extrema/witnesses, FULL, deterministic witness old coordinates, and nested finite-mesh vertex inclusions.

## One bounded primary campaign

`validate_once.py` runs all new controls and the twelve unique actual cases in one invocation, preserves exact data, then independently reads saved certificates. `PARTIAL_PROGRESS.json` is atomically replaced after geometry and completed polytope groups/configurations. A terminated process retains the latest completed checkpoint; no failure triggers an automatic retry. Named-test reserve runs only named controls and never silently repeats the actual campaign. A diagnosed science-case repair requires a separate root-authorized affected-case selector.

Before GO root writes the actual S05 pin with `source_commit`, `source_sha256` (all new Python files and current contract, plus exactly five inherited source files), `input_sha256` (official source), and `prior_saved_sha256` (unchanged EXFOR11 saved JSON). The partial mirror uses actual publication identity and exact manifests rather than claiming a local Git commit.

```
python -B scripts/measure_execution.py --mode validate --source-commit ACTUAL_S05_COMMIT --pin ABSOLUTE_PIN --source ABSOLUTE_M0475 --prior-saved ABSOLUTE_EXFOR11_SAVED_JSON --output ABSOLUTE_NEW_INITIAL_DIR --receipt ABSOLUTE_RESOURCE_RECEIPT
```

The whole science cap is CPU120s/wall300s/AS768MiB/threads1, with one initial campaign and only one diagnosed root-authorized targeted reserve within the same cumulative cap. `measure_execution.py` measures the complete runner subprocess lifetime and waited descendants; outer orchestration is reported separately. Raw stdout/stderr, start manifest and resource receipts are create-only.

## Saved-only plot

`plot_saved.py` imports only saved JSON/Fraction/plotting code. It does no optimization, geometry, fitting, polynomial evaluation, or science-module import. The plot distinguishes outer physical enclosures from inner attained-witness bounds and shows the independent twelve cases. Plot cap CPU10s/wall30s/AS768MiB/threads1; root reads the actual image. No previous plot is regenerated.

Requested coding executor is gpt-6.1-sol; observed runtime model identity is unexposed and remains null. Root owns scientific interpretation and admission.

An outer raw envelope wholly outside [0,1] is retained as `raw_outer_ratio_range`, with `physical_range=null`, status `EMPTY_PHYSICAL_INTERSECTION` and a scoped reason. Such a result with any inner witness is a validation contradiction and raises an error. It does not supply a global physical no-go.
