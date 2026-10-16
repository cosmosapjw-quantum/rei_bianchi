# Isolated thermal CX coding record

## C1 — Goal and baseline

Implement the frozen R10 contract on the existing snapshot at supplied canonical baseline eb2abcac4f44b7bc4ff532286953fcb4e353c7bb. The snapshot has no Git directory; the controller/publisher owns repository identity and commits. Read AGENTS and physmath CODING_LOOP. Python 3.12.14 stdlib is available; scipy was detected but the runtime will use stdlib only. The requested executor is the lower-tier coding agent; observed model identity is unknown because runtime telemetry is absent.

Inputs and acceptance follow CONTRACT.json and FIXTURES.json. Densities use cm^-3, thermal density eV cm^-3, defect eV, rates cm^3/s and time s. Source Rust exact frozen-rate Riccati results are prior evidence, not new implementation progress. Actual literature Savin fits will be evaluated on synthetic isolated H/D states. No cosmological histories are produced. No code or tests executed in C1.
