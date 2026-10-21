# Native tiny observer control: scoped scientific record

## Outcome and scope

One authorized q0 birth2 observer-off/on pair completed with both native exits zero. No source repair, retry, age32 run, age64 rerun, or NCP campaign was performed. Production scientific admission remains **NOT_ISSUED**. This result checks passive observer behavior for this tiny case; it does not establish age convergence or RMS dilution causality.

The configuration used n_mu8, source_subdivisions8, transport_cells8, time_factor1, block-max, binary64 RPC, one transport thread, tight=false, unchanged original tolerances and ledger gates, max_rhs200000, and a 60-second cap for each run. The copied executable was used without changing the readback-verified original B1 file.

| Quantity | Observer off | Observer on |
|---|---:|---:|
| Controller exit | 0 | 0 |
| Outer wall seconds | 2.376692178993835 | 2.5250529639961314 |
| RHS calls | 1302 | 1302 |
| Saved accepted solver steps | 84 | 84 |
| Native domain errors | 0 | 0 |
| Photon normalized final residual | 1.1929597340350156e-11 | 1.1929597340350156e-11 |
| Energy normalized final residual | 1.279000990894289e-14 | 1.279000990894289e-14 |

The original final ledger thresholds remained 1e-8. Both outputs passed the original validation.

## Exact comparison and its storage limit

All three saved accepted_coordinates_event0/1/2.npy whole-state snapshots, setup.json, endpoint.json, observations.json, and ledgers.json are byte-identical. Solver-return calls, errors, interval records, status, failure, server exit, numerical configuration and estimator identity match exactly. Timing and RSS differ as expected for separate executions; diagnostic metadata is present only in the on run.

Accepted interval-endpoint x values are equal through the identical interval records. The original solver does not persist every internal adaptive-step x/y array, so this report does not claim a full internal-step array byte comparison. The native wrapper has no existing RHS byte-stream recorder; actual native stream identity is **NOT_RECORDED**. The separately reviewed deterministic local RPC fixture did compare every scheduled RHS byte exactly, including rollback.

## Passive telemetry and rollback accounting

The observer recorded three successful retained interval attempts, 87 error-estimator invocations, 84 accepted estimates and three rejected estimates. Its 84 retained accepted estimates equal the original solver step count. Every diagnostic block maximum equals the actual unchanged controller norm returned by the once-called inherited estimator.

There was no actual interval rollback in this tiny native case. The separately reviewed deterministic fixture manufactured a DomainError rollback containing locally accepted estimates and verified that its discarded attempt contributes zero final-trajectory accepted steps. The native result does not replace that fixture's coverage.

## Actual birth jumps

The source-jump reader found exactly two unique AVAILABLE records, with active transitions0→1 and1→2 at the actual source birth clocks. Nonbirth coordinates, gas coordinate bits and ledger coordinate bits remained unchanged across each injection. The new physical snapshots are separate from the unchanged legacy observations schedule.

Exact Fraction arithmetic on stored binary64 terms gives Δ(N+photo−sources) of:

- Event0: 1/73786976294838206464 = +1.3552527156068805e-20.
- Event1: -291706928068029447/21267647932558653966460912964485513216 = -1.371599384158768e-20.

These are exact stored-term residuals, not a full simulation roundoff certificate and not a new admission gate. Full rational records are retained in SOURCE_JUMP_DIAGNOSIS.json and the original pre/post data in on/data/source_jumps.json.

## Identities

- Original native revision: 35d9747a0bbedcafdb568467ce7c1e7a25f965b6.
- Copied B1 binary SHA256: 89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4.
- Computational base and off executed solver SHA256: 78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620.
- Diagnostic transform SHA256: 11eb2462b2907a480f66d79a297d6daac4d45ea45b7600204667db0b854a69eb.
- On executed solver SHA256: ab240948846a3a09e2bb60767af206e3865f6528a8673c90de177582569596f7.
- Python: 3.12.14; NumPy: 2.3.5; SciPy: 1.17.0.

Full commands, caps, config, hashes, output hashes, stdout/stderr, solver returns and raw compact results are retained beside this report. Generated solver scripts make the executed source identities reviewable. The executable copy is a backup artifact; it is excluded from the text publication manifest and remains bound by its verified hash.
