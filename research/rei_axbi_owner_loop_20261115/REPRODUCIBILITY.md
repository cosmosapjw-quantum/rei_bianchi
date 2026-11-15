# R8/C8 — reproduction and preserved execution evidence

All science inputs are original saved history bytes listed in
`INPUT_MANIFEST.json`. The source-full archive contains `private_inputs/`
with four complete histories and `loop/` with code/results through R7/C7.
Later small stage archives carry final report/decision/handoff updates.
No private full history is committed to the public repository.

The successful run used Python 3.12.14, NumPy 2.3.5, pandas 2.2.3 and
SciPy 1.17.0. Additional audit/plot package versions are recorded in
`REPRODUCIBILITY_MANIFEST.json`. No dependency change was made to an
original producer or user-computer runtime.

With this directory as cwd and a fresh output directory:

```sh
python3 -O physics_consumer.py --inputs /path/to/private_inputs --output /path/to/fresh_results
python3 audit_consumer.py --inputs /path/to/private_inputs
python3 -O method_checks.py
python3 plot_results.py
```

The audit and plotting scripts compare/render this release's `results/`
directory. A new reducer output should first be compared to the released
science files before replacing that directory. The reducer intentionally
refuses to overwrite an existing output directory. It validates complete
source hashes and requires all four declared cases. On the recorded
environment, CSV formatting and gzip mtime are deterministic; no cross-
platform byte identity or second successful full replay was demonstrated.

`results/SUMMARY.json` pins the successful consumer source SHA-256 and
the six generated table hashes. `REPRODUCIBILITY_MANIFEST.json` adds all
science/figure artifact hashes. Runtime logs are not expected to be byte
identical across re-executions. All uncertainty fields remain part of the
output contract; identical bytes cannot promote an unconverged trajectory.

## Measured attempts and bounds

The fixed allowance was two reducer attempts of at most 180 s, one scalar
audit of at most 90 s and up to two figure renders of at most 60 s. No
coupled ODE run was launched and no historical numerical allowance was
reset. Attempt 1 failed after 10.1501 s due to a Series indexing error;
attempt 2 succeeded under Python -O after 11.8162 s including process
startup. The independent-method scalar audit succeeded after 13.9649 s.
Only one figure render was used; its standalone wall time was not measured.
The method-check call before results existed failed as a dependency error
and is retained in `execution/FAILURE_REPAIR.json`.

Source-full ZIP integrity was checked by CRC and SHA-256 of every member.
Provider upload/readback receipts are separate from local archive creation
and from scientific acceptance. Publication uses the GitHub connector:
the cloud shell had no Git push credentials. Local archive commits and
connector publication commits have different metadata/SHA; their complete
Git trees were compared for exact equality before publication. This is
explicit tree byte identity, not an unsupported claim of commit identity.

The pre-loop inventory contains 372 REI PR records and 426 remote heads.
This is all-state/head enumeration, not semantic verification of every
historical branch, conversation or backup. New work consumes the pinned
source family and five explicitly scoped donor decisions; unrelated old
audits and completed solver maps are reused within their existing scope.
