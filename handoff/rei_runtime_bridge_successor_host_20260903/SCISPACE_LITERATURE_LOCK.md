# SciSpace methodology lock

This handoff uses literature only for reproducibility and provenance methodology.

Admitted roles:

- Ivie and Thain, *PRUNE: A Preserving Run Environment for Reproducible Scientific Computing*: tightly couple a task to a declared environment and preserve an immutable derived-data lineage.
- Santana-Perez et al., *A Semantic-Based Approach to Attain Reproducibility of Computational Environments in Scientific Workflows*: an equivalent successor environment may be described and re-provisioned through explicit semantic resource descriptions rather than by pretending that it is the original machine.
- Oliveira et al., *Supporting Long-term Reproducible Software Execution*: preserving binaries alone is not the same as preserving a reproducible execution process.
- Pimentel et al., *Tracking and Analyzing the Evolution of Provenance from Scripts*: attempt and execution evolution should remain queryable rather than overwritten.

Project interpretation:

1. the unavailable historical raw receipt is not reconstructed;
2. the successor host produces a new receipt with exact field equality to the project lock;
3. the global attempt reservation precedes the host-local lease;
4. the first native outcome is append-only and cannot be retried.

These papers do not own REI source bytes, toolchain hashes, Formula IDs, attempt counts, or scientific claims.
