# Run state

- Phase: optimization runtime implemented; frozen independent review passed.
- Calculation started: no.
- Full first interval executed here: no.
- Science result: none.
- Output classification: `CANDIDATE_UNSEALED_LOCAL_EXECUTION`.
- Pre-calculation lock commit: `bf2aa2e92b1b21bbc145613b014d7c6923a77471`.
- Validation: 49 unit tests pass; one initial real three-lane endpoint matched
  all sealed values and endpoint arrays exactly; parallel/serial hashes
  matched. A clean-commit endpoint rerun remains before handoff.
- Performance: 16.984 s parallel versus 46.153 s serial (2.72x) for the same
  three-lane endpoint in this environment.
- Next: finalize the manifest, commit the runtime, rerun only one endpoint for
  final parity/package proof, then push. The user subsequently runs the complete
  calculation locally and pushes a compact candidate result branch.
