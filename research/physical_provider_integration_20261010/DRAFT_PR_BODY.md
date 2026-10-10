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
- one fixed `0..1e11 s`, 2904-node, 17-epoch interval: numerical compatibility `SCOPED_PASS`; max state relative difference `4.56e-13`

The initial byte-exact array comparison is retained as FAIL because the integrated host used NumPy 2.4.2 while PR96 recorded 2.3.5. PR96's numerical targets pass. No 11-history rerun or parameter scan was performed.

## Claim ceiling

This is a conditional warm H/He HM12 lane. CR/RCT/HH are OFF. It is not a cold primordial-IGM/REC IC result, a low-energy cosmic-ray deposition result, production `PhysicalHistory`, or global EoR admission. Production source remains fail-closed. PR95 still retains `64*EPSILON`, naive summation, and a relative mutable REC path; those are not selected physical policies.

Remote PR94/95 CI failures are inherited formatting failures with tests skipped; targeted local results above are not a whole-CI PASS.

