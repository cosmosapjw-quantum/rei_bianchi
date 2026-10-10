## Scope

Integrates three independently reviewed sibling lines without rewriting their ancestry:

- PR96 conditional warm HM12/Bianchi-I physical-provider research (`528bb69a...`)
- PR94 positive-energy/zero-temperature underflow guard (`2ee78d59...`)
- PR95 current-field selected-He closure recomputation (`73bd78d0...`)

The original PR96 evidence bytes and source manifest are unchanged. This branch adds an integration report, machine validation, one bounded identical-input compatibility run, and a precise Codex handoff.

## Validation

- PR96 manifest: 87/87 payload hashes PASS, including NPZ datasets
- HM12 intake: 10 passed
- merged native conditional consumer: 6 passed
- PR94 axisym coupling: 5 passed
- PR95 adapter: 4 passed
- saved outputs from one fixed `0..1e11 s`, 2904-node, 17-epoch interval: new same-input compatibility checks using PR96's pre-existing targets `SCOPED_PASS`; max state relative difference `4.56e-13`

The initial byte-exact array comparison is retained as FAIL with roundoff-scale deviations. The observed environments differ in Python (3.12.14 to 3.12.3) and NumPy (2.3.5 to 2.4.2), while SciPy 1.17.0 is unchanged; causation was not isolated. Corrected saved-data checks restore PR96's per-epoch pressure scaling and field threshold, and explicitly pass exact saved time/mu/weight identity, finite/positive state, ionic fraction and temperature domains. No new solver run, 11-history rerun or parameter scan was performed for the correction.

## Claim ceiling

This is a conditional warm H/He HM12 lane. CR/RCT/HH are OFF. It is not a cold primordial-IGM/REC IC result, a low-energy cosmic-ray deposition result, production `PhysicalHistory`, or global EoR admission. Production source remains fail-closed. PR95 still retains `64*EPSILON`, naive summation, and a relative mutable REC path; those are not selected physical policies.

Remote PR94/95 and integration PR97 CI failures are inherited formatting failures with tests skipped; targeted local results above are not a whole-CI PASS.

