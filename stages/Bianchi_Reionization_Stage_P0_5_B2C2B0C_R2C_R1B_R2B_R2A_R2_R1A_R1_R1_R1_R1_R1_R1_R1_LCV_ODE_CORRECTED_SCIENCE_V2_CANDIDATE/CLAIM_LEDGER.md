# CLAIM AND PROVENANCE LEDGER

Labels are closed to `IMPLEMENTED`, `VALIDATED`, `DERIVED`, `SPECIFIED`,
`PROPOSED`, `SPECULATIVE`, `DEPRECATED`, and `FORBIDDEN`. `VALIDATED` always
names its test domain; it never implies active trajectory or publication
authority.

| ID | Label | Claim | Evidence binding | Ceiling / falsifier |
|---|---|---|---|---|
| C-01 | `IMPLEMENTED` | N decodes finite binary64 inputs exactly as rationals, performs bounded exact finite algebra, and exports rational endpoints outward to finite binary64. | `analysis/verified_backend.py` | Not a transcendental or production ODE backend. |
| C-02 | `VALIDATED` | The exact arithmetic fixtures and negative/resource cases pass in the observed runtime. | run 005, 22-test group; run 007/008 exact vector | Falsified by any excluded exact value or mutation test failure. |
| C-03 | `DERIVED` | For input binary64 `[1e20,1,-1e20]`, the exact rational sum is `1`; the predecessor returned near-zero interval excludes it. | predecessor E-003 plus successor run 007/008 | This is one counterexample and one corrected shadow vector, not active reachability. |
| C-04 | `IMPLEMENTED` | N certifies finite rational point systems only, dimension at most three, with exact determinant/solve/residual and outward coordinate bounds. | `analysis/certificate_adapter.py` | Nonpoint intervals are deliberately unsupported. |
| C-05 | `VALIDATED` | For the two reproduced 2x2 systems, the exact solutions `(4,7)` and `(30001/10011,32/10011)` are enclosed and independently replayed. | runs 005, 007, 008; `validation/independent_exact_oracle.py` | Does not repair or validate general Krawczyk interval systems. |
| C-06 | `DERIVED` | Under the declared per-H number convention, `N_HeII/N_H = Y_He x_HeII`; pure HeII introduces `Y_He` once, not twice. | `SCIENTIFIC_CONTRACT.md`; run 007/008 | Selecting this convention for active science requires D-02 owner authority. |
| C-07 | `IMPLEMENTED` | N computes opacity as `scale sigma_s N_s/N_H`, checks an optional exact helium inventory ratio, and uses direct `raw_s/sum(raw)` shares. | `analysis/corrected_physics.py` | Units, tables and active model binding remain external. |
| C-08 | `VALIDATED` | Per-H, trace/underflow retention, owner permutation, negative/nonfinite/provenance, zero-opacity and inconsistent-current cases pass locally. | run 005; run 007/008 | This validates helper contracts only. |
| C-09 | `IMPLEMENTED` | N requires exactly ten authoritative evidence gates; worker self-success cannot admit. | `analysis/admission_contract.py` | No actual solver evidence set is produced here. |
| C-10 | `VALIDATED` | Deleting, failing, making inconclusive, duplicating or assigning wrong authority to any required evidence fails closed in local tests. | run 006; run 007/008 | Does not validate contents of future evidence artifacts. |
| C-11 | `IMPLEMENTED` | N provides a pure total FSM with pause-only resume and byte-identical no-write terminal absorption before action decoding. | `analysis/terminal_fsm.py` | Not wired to the active controller. |
| C-12 | `VALIDATED` | All typed state/action pairs return a result; all terminal outcomes absorb typed and malformed actions in local tests. | run 006; run 007/008 | Active predecessor behavior remains unchanged. |
| C-13 | `IMPLEMENTED` | Audit capture records exact binary streams, resolved executable hash/stat, argv/cwd, a fresh explicit environment, Git/runtime identity, time/output termination and raw hashes. | `tools/capture_audit_run.py` | Import roots are not recursive content seals; output secrets are not scanned. |
| C-14 | `VALIDATED` | Five dedicated capture-policy tests pass after the sole repair-closeout. | run 004 | The combined all-N discovery remains a preserved failed run. |
| C-15 | `VALIDATED` | Every one of 1,012 frozen predecessor ordinary files matches its preimplementation SHA-256. | run 009; `PREDECESSOR_SHA256SUMS.txt` | Does not cover untracked bundles, which were intentionally untouched and unread. |
| C-16 | `SPECIFIED` | D-01--D-07 enumerate the missing backend, convention, defect/error, QoI, event, identity/reference and active-routing authorities. | `DECISION_GATES.md` | A specification is not closure evidence. |
| C-17 | `PROPOSED` | After D-gate closure, the N primitives may be integrated behind a shadow/dual-run controller before any promotion decision. | final report next-work sequence | Requires a newly authorized work unit and new tests. |
| C-18 | `SPECULATIVE` | Fixed-branch block-local plus low-rank structure may improve performance. | blocker #18 | No benchmark was run; no speedup is claimed. |
| C-19 | `DEPRECATED` | Treating predecessor `certified=True`, schema-v1 `ACCEPT`, or `solve_ivp.success` alone as scientific admission is not an accepted claim rule. | reproduced witnesses; closed N admission contract | Historical artifacts remain forensic; they are not rewritten. |
| C-20 | `FORBIDDEN` | Claiming all 32 issues closed, a corrected trajectory, pinned parity, production readiness, endpoint accuracy, or publication authority from this work is forbidden. | open D-01--D-07; failed runs 001--003; no active route/reference execution | Requires all applicable gates and independent execution evidence. |

## Evidence tier ordering

For this delivery the strongest achieved tier is local primitive validation:

`source diagnosis -> implemented shadow primitive -> captured local tests -> independent point-certificate replay`

The following higher tiers were not attempted:

`active integration -> exact pinned-runtime replay -> independent corrected reference parity -> global/QoI/event error admission -> scientific promotion`.
