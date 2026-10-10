## Scope

Integrates four reviewed source lines without rewriting their ancestry:

- PR96 conditional warm HM12/Bianchi-I physical-provider research (`528bb69a...`)
- PR94 positive-energy/zero-temperature underflow guard (`2ee78d59...`)
- PR95 current-field selected-He closure recomputation (`73bd78d0...`)
- PR98 production `SourceBoundConditional` route (`c168e578...`), merged as a sibling while preserving PR94/95

The historical PR96 commit and source manifest are not rewritten. Original PR98 changed sealed `RESEARCH_DAG.json` and marked P01 complete without sufficient source-to-binary proof. This integration restores that sealed file byte-for-byte to the PR96 manifest value and P01 `ready`; PR98's original commit/report remain preserved in Git as non-authoritative producer evidence. This branch adds an integration report, machine validation, one bounded identical-input compatibility run, and a precise Codex handoff.

## Validation

- historical PR96 commit `528bb69a...`: 87/87 payload hashes PASS, including NPZ datasets
- original PR98 commit `c168e578...`: 86/87 because sealed `RESEARCH_DAG.json` became `7a6ecb...`
- current integrated tree after corrective restoration: all 87 PR96-manifest-listed payloads pass; `RESEARCH_DAG.json` is again manifest value `012f742...`. PR98-added files are outside that historical manifest and are bound by the Git evidence commit and integration checksum set instead.
- HM12 intake: 10 passed
- merged native conditional consumer: 6 passed
- PR94 axisym coupling: 5 passed
- PR95 adapter: 4 passed
- merged PR98 Rust conditional: 8 passed
- merged PR98 Python boundary: 5 passed
- post-merge contract/coupling: 6 + 5 passed
- saved outputs from one fixed `0..1e11 s`, 2904-node, 17-epoch interval: new same-input compatibility checks using PR96's pre-existing targets `SCOPED_PASS`; max state relative difference `4.56e-13`

The initial byte-exact array comparison is retained as FAIL with roundoff-scale deviations. The observed environments differ in Python (3.12.14 to 3.12.3) and NumPy (2.3.5 to 2.4.2), while SciPy 1.17.0 is unchanged; causation was not isolated. Corrected saved-data checks restore PR96's per-epoch pressure scaling and field threshold, and explicitly pass exact saved time/mu/weight identity, finite/positive state, ionic fraction and temperature domains. No new solver run, 11-history rerun or parameter scan was performed for the correction.

## Claim ceiling

This is a conditional warm H/He HM12 lane. CR/RCT/HH are OFF. It is not a cold primordial-IGM/REC IC result, a low-energy cosmic-ray deposition result, production `PhysicalHistory`, or global EoR admission. Production source remains fail-closed. PR95 still retains `64*EPSILON`, naive summation, and a relative mutable REC path; those are not selected physical policies.

Remote PR94/95 and integration PR97 CI failures are inherited formatting failures with tests skipped; targeted local results above are not a whole-CI PASS.

PR98 producer JSON/NPZ raw bytes were recovered locally and match its reported SHA-256 values. The matching 3,288,066-byte Dropbox recovery archive (`9a82f25e...`, provider ID `BSpOijBcT10AAAAAAD3sHQ`) was independently statically inspected by the parent worker and contains both outputs, resolving artifact availability. It lacks the production binary, clean-build transcript and P01 command/stdout/stderr receipt, so execution remains uncertified. The Python entrypoint accepts an arbitrary `--binary`, records source/binary hashes only after integration, and Rust `BIND` verifies identity strings rather than files/build provenance. Future execution is explicitly blocked pending a clean source-pinned build receipt and prelaunch executable/source hash check. No new solver run was performed while integrating PR98.

Fresh PR99/`d6ad8b73...` diffuse-screen results are not merged or adopted. Its finite-grid cap is only a frozen diagnostic, and its validation-recorded `screen_diffuse.py` hash does not match the committed blob. It remains HOLD pending run-source identity resolution; this integration did not rerun it.

