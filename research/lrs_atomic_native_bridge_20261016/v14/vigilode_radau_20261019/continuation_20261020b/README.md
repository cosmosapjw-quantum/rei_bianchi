# Borrowed-cell iterator experiment: final tested candidate v2

Use `--native-eval cell-borrowed` to select this opt-in evaluation path. Legacy remains default and `cell-cache` remains available. The normal runner supports `prepare_and_run.py --all --native-eval cell-borrowed --output-root FRESH_OUTPUT` with the same immutable input, offline-cache and toolchain arguments as before.

The additive module shares one original native_rates arithmetic body over an Iterator<Item=&AbsorptionNode>. PreparedAbsorption uses its owned node slice. The borrowed view retains state/cache references and at most one changed PreparedCell; it preserves original increasing cell/node order, cache validation and diagnostics folds. No original native baseline byte, hook, solver, provider, pin, FD rule, tolerance, default or ledger policy changes.

Version1 used external `for node in nodes`; the one authorized performance iteration changed only that outer traversal to `nodes.for_each`, with identical sequential closure body. Version1 source/binary/raw remain preserved. Both versions passed the focused native suite, all nineteen existing fixture replays, legacy/cache continuity controls, and every measured physical/work-count comparison. This is a replay of existing fixtures, not nineteen new physical histories.

The named cached_prepared_state_clones and cached_prepared_node_clones count only explicit clones during cached PreparedAbsorption construction, excluding coordinate decoding, once-per-Jacobian base cloning and all other allocation/copy work. Borrowed mode removes these counted operations; this is not a memory-footprint, zero-allocation or bandwidth claim.

Five same-binary CPU0 profile-off paired repetitions per setting did not establish overall acceleration. The reported ratio is cache wall divided by borrowed wall; a ratio below1 means borrowed was slower.

| Version and traversal | Fixed median paired native ratio | Birth median paired native ratio | Disabled median paired native ratio |
|---|---:|---:|---:|
| v1 external-for |0.760292589|1.030525822|0.979692101|
| v2 for_each |0.932205715|0.980651463|0.879170577|

The corresponding v2 median paired process-wall ratios were0.999236805,0.876616602 and0.940713637. All individual samples, dispersion and attribution profiles remain preserved; the timing evidence for each version is reported separately. Root selected v2 as the final explicit experimental cell-borrowed path for reproduction only. No acceleration admission was issued; use the existing cell-cache path for performance. No further variants or runs follow this selection. Root retains scientific admission; no new NCP execution or production scientific admission is asserted.

The included evidence scripts retain exact task-specific workspace paths used to generate their receipts; the normal runner and case CLI provide the portable execution path.
