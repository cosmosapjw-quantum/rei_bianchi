# Independent C10 handoff review

Decision: **PASS for packaging and NCP inspect/collect**. This is implementation and handoff admission, not a scientific success declaration. Current NCP runtime and terminal outcome remain **unknown**.

Reviewed the frozen contract, original V6 source behavior, recovery code, fixture tests and their actual command receipt, Korean Codex prompt and execution guide. The review used one pass and one bounded repair pass. It executed no physics or remote commands. Reviewer and implementer are separate agents; actual runtime model identities are not exposed.

The final recorded suite passed **17/17 tests**, exit 0, in 0.785 seconds. Help and restored historical snapshot inspection also returned 0. The restored snapshot classified `stale`; this only describes the archived local evidence. Fixtures do not establish NCP execution or scientific validity.

Four concrete recovery defects were repaired and their regressions passed:

- Broken ZIP/schema validation now records failure and preserves original corrupted NPZ evidence.
- Stable duplicate terminal NPZs are retained when no matching process is active; conflict remains unaccepted.
- Exact V6 supervisors without optional `--only` are detected from driver, contract and target output/case evidence.
- The original driver's parent `run_manifest.json` is collected.

The receipt gates preserve separate input-byte and parsed-case identities, frozen source and contract identity, original solver gates, and independent NPZ invariants. Inspection/collection cannot launch or kill jobs. Live or unavailable states cannot become accepted results, and evidence copying detects source mutations. Driver exit 0 is not treated as solver success. The mandatory receipt `input_sha256` is appropriate for the historically observed `run` supervisor; an initial concern based only on its child `launch.json` was withdrawn after reviewing supervisor finalization.

The prompt preserves the original 12-thread, 24-GiB, one-worker, 7200-second bounded attempt budget and aggregate/headroom guards. New execution requires an observed diagnosis and separate attempt identity. The independent PR150 full005 campaign remains untouched. The final package test command uses `handoff/tests`; its actual staged-layout execution also passed 17/17 tests (exit 0, 0.655 seconds), as recorded in `PACKAGE_LAYOUT_TEST.json`. All eight physical closure flags remain open.

No blocking findings remain within this bounded review. **Next action:** assemble and publish the complete portable package, then run NCP `inspect` and `collect` through the user's existing local environment. Final bundle assembly and actual provider acknowledgements are controller responsibilities; this review does not certify uploads that have not occurred. Use actual NCP receipt/data before admitting its finite-model result.
