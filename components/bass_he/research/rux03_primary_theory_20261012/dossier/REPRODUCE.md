# Reproduce the theory checks

The mathematical proofs are in `../derivations/`. Three exact Wolfram Language
inputs corroborate the indicated algebraic transitions:

1. `../evidence/shared_provider_exact.wl`: 19 identity groups.
2. `../derivations/PHOTON_EXACT_CHECK.wl`: 19 identity groups.
3. `../evidence/temperature_witness_exact.wl`: 9 identity groups.

Each file is a complete, stateless Wolfram Language input. Evaluate its entire
contents in a Wolfram kernel, or pass the complete contents as `code` to the
Wolfram Language evaluator. The original requested time constraints were 45,
30 and 30 seconds respectively. These inputs use exact symbols, rational
coefficients, differentiation and `Together`; no candidate binary, sampled
rate table or ODE run is required.

The raw outputs are preserved in `WOLFRAM_RAW_RESULT.json`,
`WOLFRAM_PHOTON_RAW_RESULT.json` and `WOLFRAM_TEMPERATURE_WITNESS_RAW.json` in
the corresponding directories. The root outputs encode a JSON string in the
tool's text result; their decoded summaries are also preserved. The photon
output's named checks are mapped verbatim in `SYMBOLIC_CHECK.json`. Every
recorded group is True. Sign/domain conclusions additionally use the explicit
inequality proofs in the two derivations.

The initial `check_photon_elimination.py` attempted a SymPy implementation.
It stopped at import because SymPy was absent. Its file and
`SYMPY_ENVIRONMENT_FAILURE.json` preserve that observation; it is not the
successful execution path for this unit. The available Wolfram evaluator was
used to finish the algebra checks without installing another package.

To revisit the source correspondence, use the exact receiver commit and file
hashes in `../source_map/CURRENT_SOURCE.json`. The source map contains pinned
repository links. The prior native/interval results retain their original
EVENT_BRIDGE_02 provenance and are not counted as new executions here.

The candidate science freeze records the reviewed file identities. The final
evidence archive manifest records all packaged payload identities. Verify
those hashes before interpreting a packet as the reviewed result.
