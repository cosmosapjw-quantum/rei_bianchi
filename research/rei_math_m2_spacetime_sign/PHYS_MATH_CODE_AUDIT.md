# PHYS-MATH-CODE audit — second sequential review pass

Performed after the PHYS-MATH pass on implementation
fee018efd2f1d91e2ef859c0ee91874c0437bb62. This is the implementing assistant's
separate code/evidence review, not a claim of independent human/agent review.

## Executed evidence

RED commit 21a11ce82b4d71fe8be86efc32aaf6490b7c48cc was actually executed:
10 intended M2_IMPLEMENTATION_ABSENT assertion failures, zero errors/skips.
The implementation commit changed exactly two paths: the new module and RED
receipt. The ten tests and work-unit acceptance contract were not weakened.

GREEN run 33914082531 / job 101157086098 checked out the exact push SHA,
not a synthetic merge. All ten frozen tests passed. The standalone report
then regenerated the exact residuals, mutation table and plots successfully.
The workflow also checked base ancestry, allowed-path closure, git diff
whitespace, and no changes to M1/src/rust/stages/handoff paths.

## Equation-to-code checks

`derive`: M1 Koszul connection -> independently extended 4D connection ->
connection derivatives/commutator curvature -> Ricci -> Einstein -> projections.
Gauss/Codazzi candidates are residual comparators, not oracle replacements.

`coordinate_witness`: differentiate a coordinate metric first; compare to the
ONF result only afterward. It shares symbolic variable labels but not the ONF
connection implementation or candidate constraint formulas.

`class_b_report`: substitute the chart into the directly derived projection.
`mutation_records`: compare six mutated candidate channels to that projection.
`write_report`: emit exact strings, preserve true zeros, apply the log floor
only to plotted numbers. Deterministic fixtures use no RNG or tolerances.

## Findings and narrowed claims

No implementation repair was needed for the frozen tests. The old formula
claim is corrected in the new research note, not in BASS production files.

P1 full closeout incomplete: the generated images have not been visually
opened in this session. Logs/CSV establish numerical signatures, not visual
legibility. Do not claim the mandatory visual audit is complete.

P1 owner validation not supplied: an independent BASS-native xTensor bridge
and owner acceptance are required before consuming this as common authority.

P2 reproducibility limit: SymPy/mpmath/matplotlib are pinned; plotting
transitive dependencies and the hosted OS are not a production-toolchain lock.
Artifact hashes bind the produced bytes; they do not promise byte-identical
future rendering or admit the Rust/MPFR host.

P2 harness boundary: the standalone report's aggregate PASS covers its stated
residual groups; the full frozen test gate is the required source of the
scaling, counterexample and mutation-coverage results. Consumers must retain
both test-result.json and M2_SIGN_REPORT.json, not only the report status.

Complexity is bounded by fixed 3D/4D component loops and symbolic polynomial
simplification, not advertised as a production performance result. No host,
Section-0, lease, attempt, native worker or provider surface is imported.
