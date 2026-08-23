# ODE SOLVER FOUR-LOOP INTEGRATED FINAL AUDIT

Date: 2026-08-23  
Repository: `rei_bianchi/rei_bianchi`  
Bound HEAD: `111b6ace750e36e218df7fc9626c6bad2ec19971`  
Bound Git tree: `2f541ee051f0844bdeed88fd2dcba2a0c54ab035`  
Successor: `LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE` (N)  
Classification: `TEST_ONLY_NOT_SCIENCE`  
Final engineering verdict: `PARTIALLY_CONFIRMED`  
Promotion decision: `HOLD / FORBIDDEN`

## 1. Executive conclusion

The four-loop evidence does not support “all ODE issues are fixed.” It supports
a narrower and useful conclusion:

1. Five high-risk predecessor contract surfaces were reproduced or directly
   bounded: signed-sum false containment; two exact-solution-excluding linear
   certificates; double helium abundance under the declared per-H convention;
   nonabsorbing terminal re-entry; and stronger-evidence-free admission.
2. An additive N shadow implements owner-neutral mitigations: exact bounded
   rational algebra, an independently replayable small point-system
   certificate, explicit per-H opacity/direct shares, closed evidence
   admission, an absorbing terminal FSM, and bounded raw audit capture.
3. The decisive successor primitives have captured green evidence: 5 capture
   tests, 22 numerical/physics tests, 11 admission/FSM tests, two byte-identical
   integrated vectors, and 1,012/1,012 predecessor file hashes.
4. Three confirmatory capture runs failed and remain part of the result. They
   exposed a user-site dependency, one N probe-path error, and an ambient-PATH
   assumption. The sole repair-closeout addressed those mechanisms, but the
   exact failed aggregate commands were not rerun because the preregistered
   same-failure retry budget was exhausted.
5. D-01--D-07 remain open. There is no qualified transcendental/general
   interval backend, continuous defect/global/QoI error argument, complete
   hybrid-event policy, corrected independent reference, exact pinned parity,
   or active routing. Therefore no corrected trajectory, endpoint, production
   readiness, or publication claim is authorized.

Preregistered hypotheses are adjudicated as follows:

- H1 (“full scientific admission now”) is falsified by every open D-gate.
- H2 (“useful owner-neutral additive successor with explicit retained
  blockers”) is confirmed at local primitive/shadow level, subject to the
  preserved integration-test failure.
- H3 (“no safe code change before all decisions”) is falsified by the additive
  primitives and predecessor-custody proof.

## 2. Scope, custody, and completeness ceiling

All writes were confined to one isolated linked worktree:

`/tmp/rei-ode-integrated-audit.ZcRbz6/worktree`

The original checkout remained on branch
`agent/precalc-adaptive-history-parallel-runtime` at the bound HEAD. Its tracked
tree was initially clean. Exactly two pre-existing untracked bundle files were
named for custody but never opened, hashed, moved, modified, packaged, or
deleted. No commit, push, merge, reseal, package, production history, parity,
BDF, endpoint, or publication execution was performed.

`PREDECESSOR_SHA256SUMS.txt` freezes every Git-tracked ordinary file across the
eight predecessor aliases A/P/V/C/S/R2A/U/B. Captured run 009 verified all
1,012 entries without failure. The N directory is additive and remains
untracked; the active driver does not import it.

The 32-item universe is a frozen, mechanically complete inventory of the four
available loop artifacts. It is not proof that no undiscovered defect exists.
Two requested standalone current-REI seed reports were not recoverable as
complete artifacts; R1 physics and R2 math/algorithm/coding are consequently
seed-only/unverified. The complete harness artifacts are R3 physics design and
R4 coding design/HOLD. Wrong-root `rec_bianchi` artifacts were excluded by
repository/HEAD/tree/model mismatch. Full provenance is in
`FOUR_LOOP_PROVENANCE.md`.

## 3. What changed in code

### 3.1 Exact arithmetic shadow

`analysis/verified_backend.py`:

- separates binary64, decimal-text and integer-ratio provenance;
- decodes finite binary64 exactly and carries `Fraction` internally;
- implements exact interval add/subtract/multiply/divide-away-from-zero and
  integer powers;
- sums at most 4,096 binary64 terms exactly under a 16,384-bit numerator and
  denominator ceiling;
- exports each rational endpoint with direction chosen by exact comparison to
  the nearest binary64;
- returns typed nonfinite, zero-divisor, overflow, resource-limit and
  unsupported-transcendental outcomes.

It deliberately supplies no NumPy fallback for `exp`, `log`, `sqrt` or
noninteger power. This converts an unproved enclosure into an explicit block.

### 3.2 Exact point-system certificate

`analysis/certificate_adapter.py` accepts only finite point intervals with
dimension 1--3. It computes a rational determinant and Gaussian elimination,
requires `det(A) != 0`, recomputes `Ax-b=0` exactly, outward-encloses each
coordinate, and binds the canonical input digest.

`validation/independent_exact_oracle.py` imports no candidate arithmetic. It
uses normalized integer pairs, a permutation determinant, exact residuals,
binary64 integer ratios, and digest reconstruction. A nonpoint interval is
`NONPOINT_INTERVAL_UNSUPPORTED`; it is never laundered as a Krawczyk proof.

### 3.3 Physics-specific shadow

`analysis/corrected_physics.py` makes the convention visible. For absorber
species `s`,

`r_s = N_s/N_H`, `N_H > 0`,

and

`kappa_s = scale * sigma_s * r_s`.

If `x_HeII` is a fraction within helium and
`Y_He = N_He/N_H`, then

`N_HeII/N_H = Y_He x_HeII`.

Thus pure HeII under this declared per-H convention carries `Y_He` once. The
successor vector with `N_H=1000`, `N_He=79`, `N_HeII=79`, `sigma_HeII=5` and
`scale=7` gives abundance `79/1000` and opacity `553/200`, rather than a
second `79/1000` factor.

For positive total `K = sum_s kappa_s`, every share is directly

`p_s = kappa_s/K`.

No floating complement or positive floor is used. Exact zero opacity returns a
typed vacuum, while nonzero current with zero opacity is a distinct typed
inconsistency. The helper checks an optional exact helium/hydrogen inventory
ratio but does not choose units, vacuum photon disposition, trace policy, table
regimes, or the active model convention.

### 3.4 Closed admission and total controller semantics

`analysis/admission_contract.py` admits only `SOLVED` with exactly one
authoritative PASS for each of ten gates: finite state, physical domain,
residual, enclosure, expected terminal, event completeness, physical
invariants, complete diagnostics, execution identity and corrected lineage.
Residual, enclosure, event completeness and physical invariants require
independent authority. Missing, duplicate, wrong-authority and inconclusive
evidence block; a predicate failure rejects. Worker self-success is recorded
but has no admission authority.

`analysis/terminal_fsm.py` separates READY, RUNNING, PAUSED and TERMINAL.
Terminal absorption is evaluated before action decoding, making even malformed
actions byte-identical no-write self-loops. Resume is legal only from PAUSED;
completion requires a complete cursor and closeout predicate; other illegal
actions fail closed to `BLOCKED_PROTOCOL`.

### 3.5 Audit capture

`tools/capture_audit_run.py` launches only a fully resolved absolute executable
with `shell=False`, no inherited environment, fixed public PATH, bounded
explicit import roots, monotonic timeout, per-stream byte limits and process
group termination. It incrementally preserves raw binary stdout/stderr and
records executable SHA/stat, argv/cwd, environment, Git HEAD/tree/status,
runtime, UTC interval, monotonic duration, return/signal and stream hashes.

The runner rejects secret-like argv before output-directory creation. It does
not scan captured output for secrets and its import-root identity is not a
recursive dependency content seal. Those negative statements are part of the
contract.

### 3.6 Final code hashes

| File | SHA-256 |
|---|---|
| `analysis/verified_backend.py` | `4ea3c587a534728890b971422ffffb2e2e698801e5857afcecae86a646b79d34` |
| `analysis/certificate_adapter.py` | `43df358987a4583625152cf4647d27cf1d3e236f13ec9a089b52d4cffa45802f` |
| `analysis/corrected_physics.py` | `a7469d650e9fa40f25e347f6a94ed66728dc3cca0c53cb6d8b90abd35c129b42` |
| `analysis/admission_contract.py` | `e276751536f16e596820fd7e5cb9eba44331b20344abe37b5bb7cc7c25e1b2df` |
| `analysis/terminal_fsm.py` | `0497a58e31cb77d10894de737cdb8926b145f39f2a7aba6c0bcd1cc0b00c3504` |
| `validation/independent_exact_oracle.py` | `c6ff9d059bf48a51017efa8e60fa44c505114a812cd7fdcaf06b2c5fe2c962b3` |
| `tools/capture_audit_run.py` | `a1b57fb46fe777c54e7f28cd1dd2229aa376c80d6a08550ddcb25129057dc1bf` |
| `tools/predecessor_red_probe.py` | `f40328c2561b0ffa3f99964866348423448f0834fefb04ba8fd59026cc4c750e` |
| `tools/successor_vector_probe.py` | `b38ab594f5ddde8cb9edb302dd27b7aca4f4d980150bb1fa0511b7db6c044603` |
| `tools/verify_predecessor_manifest.py` | `58f4e3fa1ddaa07f3039c2ede913a813c4e2ea89df00c2b8140d91beb78d1c0d` |

Test-file hashes and every evidence-file hash are supplied by the additive file
manifest used by the independent review.

## 4. Concrete predecessor findings

### 4.1 Signed cancellation

For binary64 inputs with hex values

`[0x1.5af1d78b58c40p+66, 0x1.0000000000000p+0, -0x1.5af1d78b58c40p+66]`,

the exact rational sum is `1`. The predecessor interval was approximately
`[-5e-324,5e-324]` and does not contain `1`. This falsifies universal
containment of the helper. The N exact sum returns `[1,1]` in binary64.

### 4.2 False point certificates

For `A=[[2,-1],[-5,3]], b=[1,1]`, predecessor `certified=True` produced
consumer upper bounds below exact `(4,7)` in both coordinates. For
`A=[[11,-10000],[-10,10001]], b=[1,2]`, it excluded exact
`(30001/10011,32/10011)` in both coordinates while certified. These fixtures
falsify the helper/consumer success predicate; they do not prove either matrix
occurs on the active trajectory.

N exactly certifies and independently replays these two point systems. General
interval systems remain blocked.

### 4.3 Helium factor

Under the declared comparison `YHE=79/1000`, the predecessor expression
contains `YHE^2=6241/1000000`, while the pure-HeII per-H number inventory is
`79/1000`; their ratio is `79/1000`. This is a convention-bound algebraic
witness, not unilateral authority to rewrite the active model.

### 4.4 Terminal and admission gaps

A tracked fake-worker run reached `BLOCKED_TABLE_EVENT`; resume executed a new
attempt and advanced attempts/transitions, so the state was not absorbing.
Independent monkeypatch localization also showed duplicate finishing from
`COMPLETE_UNSEALED`.

Separately, three current-schema PASS rows were accepted without explicit
solver outcome, residual bound, expected terminal, event-set completeness,
source-tree hash or complete-diagnostics predicate. That demonstrates an
admission-language ceiling; it does not prove the accepted fixture is
physically false.

## 5. Captured execution results

Ten captured runs and their exact commands, cwd, start/end UTC, monotonic
duration, executable/environment/Git identities, exit codes and stream hashes
are in `VALIDATION_LEDGER.md`, `AUDIT_RUN_INDEX.json`, and `audit_runs/`.

The successful confirmatory cells are:

- run 004: 5/5 audit-capture tests;
- run 005: 22/22 arithmetic/certificate/physics tests;
- run 006: 11/11 admission/FSM tests;
- runs 007/008: byte-identical 2,824-byte integrated vectors, stdout SHA-256
  `e353ab05f9158e319f69d3251a890ee29ca587fbcf194654a74f1c7ccac13b1b`;
- run 009: 1,012/1,012 predecessor files match;
- run 010: CPython 3.12.3, NumPy 2.4.2, SciPy 1.17.0, pandas 3.0.0 with exact
  import paths.

The preserved failures are:

- run 001: initial fresh environment could not import user-site NumPy;
- run 002: aggregate N discovery reached 37 displayed passing tests, then the
  shadow test setUpClass hit one extra `R1` in a probe path;
- run 003: 46/49 neighbor tests passed; three launcher tests required ambient
  PATH.

The repair-closeout explicitly bound the user-site import root, corrected the
path constant, and provided recorded `PATH=/usr/bin`. Dedicated post-repair
capture tests pass. Runs 002/003 nevertheless remain failed and unrerun; this
is why the verdict is partial rather than fully confirmed.

The dependency root is direct-listing identified, not recursively sealed, and
the observed versions differ from the older declared pins. Local green is not
pinned parity.

## 6. Post-implementation disposition of all 32 items

“Shadow mitigation” below never means active closure.

| # | Issue | N result | Remaining authority/blocker |
|---:|---|---|---|
| 1 | extra HeII `YHE` | per-H one-factor derivation implemented and locally validated | active convention/unit/table binding; D-02/D-07 |
| 2 | false Krawczyk certificate | both point fixtures exactly certified and independently replayed | general interval/nonlinear theorem/backend; D-01/D-07 |
| 3 | signed-sum false containment | exact bounded summation returns exact 1 | active arithmetic routing and transcendental closure; D-01/D-07 |
| 4 | one-nextafter/transcendental gap | rational endpoints export outward; transcendentals explicitly refuse | qualified elementary backend; D-01 |
| 5 | strict-positive log/logit zero faces | no silent chart extrapolation added | owner boundary/chart semantics; D-02 |
| 6 | 54 eV complement cancellation | all shares formed directly from raw measures | active opacity ownership/table integration; D-02/D-07 |
| 7 | vacuum/floor ambiguity | zero opacity and inconsistent current are distinct typed outcomes | photon disposition/trace policy; D-02 |
| 8 | full/two-half is not LTE | no false LTE label added | dense reconstruction and LTE theorem; D-03 |
| 9 | no continuous defect | retained | defect construction/norm/coverage; D-03 |
| 10 | no global-error control | retained | stability/propagation theorem; D-03/D-04 |
| 11 | no QoI budget | retained | owner QoIs and budgets; D-04 |
| 12 | photon validator self-cancellation | admission demands independent invariant evidence | independent physical oracle not yet implemented; D-04/D-06 |
| 13 | energy validator tautology | same fail-closed gate, no replacement oracle | independent energy accounting; D-04/D-06 |
| 14 | grazing events missed | event-completeness gate blocks admission | all-root/tangency method; D-05 |
| 15 | multiple/simultaneous events | event-completeness gate blocks admission | multiplicity/order/coalescence policy; D-05 |
| 16 | no production event localization | retained | active locator integration; D-05/D-07 |
| 17 | no conservative restart/rebuild | explicit FSM action exists but no physics restart | conservative state/map rebuild; D-05/D-07 |
| 18 | unused block/low-rank structure | no code or benchmark; nonblocking opportunity | performance study after correctness; D-07 |
| 19 | legacy BDF domain/extrapolation | no rewrite or replay | upstream partial limitation retained; D-06 |
| 20 | legacy BDF admission | closed N admission specified, not applied | corrected reference and active binding; D-06/D-07 |
| 21 | non-independent BDF oracle | independent oracle exists only for small point fixtures | independent corrected trajectory oracle; D-06 |
| 22 | pinned/live runtime mismatch | exact runtime/import identity captured | exact dependency lock/replay remains open; D-06 |
| 23 | unauthenticated parity | no parity claim made | controller-consumed exact lineage parity; D-06 |
| 24 | terminal resume semantics | absorbing pure FSM implemented and validated | active controller migration/state compatibility; D-07 |
| 25 | package over-collection | no package operation | admitted/forensic manifest split; D-07 |
| 26 | symlink/path containment | runner resolves main executable/cwd/import root | package descriptor/hardlink/race custody retained; D-07 |
| 27 | bare PATH/tool identity | main executable hash/stat plus fixed public PATH recorded | nested active-tool identity and pinned runtime; D-06/D-07 |
| 28 | weak candidate validation | closed ten-gate contract implemented | actual independently generated evidence and route; D-03--D-07 |
| 29 | quadratic ancestry/custody | not benchmarked or altered | scaling redesign/benchmark; D-07 |
| 30 | incomplete resource forecasting | capture time/output caps implemented | disk/inode/process/solver/package budgets; D-07 |
| 31 | unbounded worker buffering | audit runner incrementally spools bounded streams | active worker transport migration; D-07 |
| 32 | nonfinite/overflow gaps | shadow inputs/intermediates have typed tests/resource ceilings | full active transformed/nested/external coverage; D-01/D-07 |

Active scientific closure count is therefore zero of 32. This is not because
the shadow changes are ineffective; it is because active closure requires
integration and evidence not authorized or available in this work unit.

## 7. Retained decision gates

All seven remain `UNRESOLVED`:

- D-01: qualified outward transcendental/general interval backend and theorem;
- D-02: model-owner convention, units, boundary/vacuum/table semantics;
- D-03: dense reconstruction, norm, continuous defect, LTE/global propagation;
- D-04: authoritative QoIs and local/global/event/QoI budgets;
- D-05: all-root/grazing/simultaneous-event ordering and conservative restart;
- D-06: corrected reference identity, complete ABI, pinned runtime and
  independently consumed parity;
- D-07: active routing, resource/package/custody and release authority.

Closing one gate cannot supply evidence for another. `DECISION_GATES.md` is the
machine-reviewable register.

## 8. Literature applicability

Rump's verification-method survey supports theorem-matched rigorous arithmetic
as the standard of claim, but cannot validate this implementation by citation.
SciPy 1.17 documents that step-sign-change event detection may miss multiple
crossings inside a step, so algorithmic success cannot establish the N
event-completeness gate. Python 3.12 documents memory buffering by
`communicate()` and recommends fully qualified executable paths; that supports
the bounded incremental recorder design but is not proof of an active-worker
exploit. Sources and applicability limits are fixed in `SCIENTIFIC_CONTRACT.md`.

## 9. External-audit procedure

An auditor should begin from the exact worktree and:

1. verify original HEAD/tree and confirm N is the sole worktree addition;
2. run `tools/verify_predecessor_manifest.py` with bytecode disabled and verify
   `checked_file_count=declared_file_count=1012`, `failures=[]`;
3. for every `audit_runs/*/manifest.json`, recompute its sidecar and the raw
   stdout/stderr SHA-256, then compare `AUDIT_RUN_INDEX.json`;
4. inspect runs 001--003 before reading the repair narrative; they must remain
   failures;
5. inspect the source hashes, exact-oracle independence and nonpoint/
   transcendental refusal paths;
6. verify no predecessor imports N and no active routing/package/reference
   artifact was added;
7. treat `CLAIM_LEDGER.md` labels and D-gates as the maximum claims.

The independent review is stored separately as
`INDEPENDENT_AUDIT_REVIEW.md`. It binds the exact pre-review report and additive
file-manifest hashes; its verdict must not be generalized beyond that preimage.

## 10. Required next work before promotion

The safe order is:

1. model owner resolves D-02 conventions and provides executable limiting-case
   fixtures;
2. numerical owner selects and qualifies D-01, then proves continuous defect,
   global and QoI bounds under D-03/D-04;
3. hybrid-system owner specifies and validates D-05 all-root/restart behavior;
4. establish a corrected independent reference, exact runtime/ABI and parity
   evidence for D-06;
5. integrate N behind a shadow dual-run route, with fail-closed evidence
   production and resource/package custody under D-07;
6. only then run a newly authorized trajectory and promotion audit.

Until all applicable steps close, the only defensible conclusion is:

`OWNER-NEUTRAL SHADOW MITIGATIONS IMPLEMENTED AND LOCALLY VALIDATED;
ACTIVE ODE/SCIENCE PROMOTION FORBIDDEN.`
