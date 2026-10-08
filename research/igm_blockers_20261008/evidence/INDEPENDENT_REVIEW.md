# Independent review — IGM blockers 2026-10-08

Review base: `a735650542f712005c5e6b381ffd6464278345cb`; current worktree, production formatting commit and untracked `research/igm_blockers_20261008/`. Review contract: `/tmp/igm-blockers-contract.json`, finite acceptance SHA `6f017883ef6a21b9890974a4bad8936f6ba882d7e11b2c6ae2aa24f47d9da7d0`. Reviewer did not implement adapters or numeric lane. One review round and one targeted repair closeout; no full campaigns.

## Reviewed source and observed checks

- BASS adapter consumes two pinned PR86 accepted midpoint records, checks full projected records, exact epoch/gas continuity and background identity. Three time edges use `Δln(a)/H_mid`. Proper nuclear density receives `1e6` once before unchanged source-pinned `ElectronState`; source computes `D=1` once. Finite observer tail 0 and +1/8 preserve mass without renormalization. Decimal70 compares optical depths, edge survival, and interval mass independently.
- BASS copied module SHA values match `SOURCE_PIN.json`. Reviewed native visibility/clock source and bridge call directly.
- REC packet retains actual endpoint rational gas/electron/EOS data and 2440 original binary64 spectrum rows. `background[5]` CMB bath is separate from finite ionizing grid. Exact six moments and signed arithmetic defects are transferred by the same-state linear PR87 source map; continuum/provider/time uncertainties remain UNKNOWN, Gate I/matched/physical HOLD.
- REC positive stored products have minimum `1.4626828713918707e-24`, well above normal binary64 minimum. The finite positive-sum roundoff estimate does not encounter subnormal product issues in these saved rows.
- Donor intake preserves conditional synthetic E7 premises, different-state ENERGY04 and first-cell-only BRIDGE12; none is asserted to provide cold IGM continuum authority.

Reviewer commands (2026-10-08):

```
python3 research/igm_blockers_20261008/bass/verify.py --output /tmp/igm-review-bass-20261008
python3 -m unittest discover -s research/igm_blockers_20261008/rec -p 'test_*.py'
```

Both exit 0; BASS compiled source and ran two prescribed-tail consumers; REC 4 tests pass. No new photon observer/provider/RHS/history call. Reviewer BASS subcommands carry bounded CPU/wall receipts in temporary RESULT.json; combined shell wall 0.679s.

## Findings and stopping rule

No BASS/REC correctness finding at this scoped boundary. Initial CI omission of new actual consumer tests was reported to owner and repaired: current workflow runs actual BASS verify, REC unittest and REC CLI. Targeted source closeout passed. Numeric lane still being implemented; preliminary direct inspection found conservation-budget losses charged but photo-delta gas residual losses not yet charged. This interim document is not final acceptance of that lane or z=12→10 validation.

Residual scientific limitations: frozen midpoint BASS cells are a normal-time surrogate, not certified continuous opacity; outside-window optical depth UNKNOWN. REC is an initial-condition candidate, not consumer Gate I or matched evolution admission. Exact saved quadrature arithmetic does not bound the continuous spectrum or integration-time error.

MAJOR pending numeric repair: `numeric/source/rei-next-nodes/short-hhe-midpoint/src/coupled.rs`, evaluate/photo_delta and candidate norm. Tracked readout bounds for absorption number/energy enter the gas residual, but current `norm(ev.r)` contains only point residual. Conservation budget bounds do not cover this separate original TOL gate. Propagate an/be bounds through the absolute linear photo_delta coefficients, charge them with original `[1e-14,1e-14,1e-14,1e-26]` allowances, and add a negative regression where point residual passes but bound-aware residual fails. Do not widen tolerances.

Review will close after one inspection of ready numeric source/results and targeted repair. No adjacent donor/campaign rerun or recursive assurance expansion is authorized by this review.


## Targeted numeric repair closeout

Direct inspection of ready research code confirms the earlier MAJOR is repaired. `coupled::evaluate` carries canonical readout bounds of `an[3]` and `be[3]` through absolute photo-delta coefficients, including helium-fraction division and threshold heat subtraction. `represented_norm` adds those bounds before dividing by the original TOL; Newton stopping, line search and committed `State.norm` use that same bound-aware norm. Original TOL is unchanged. N/E conservation separately charges active/owner readout bounds. This is a representation-loss guard, not a continuum residual propagation theorem.

The ledger mismatch issue is also repaired: arbitrary scalar/canonical disagreement now rejects, while intentional active N/E extraction captures bounds then explicitly clears those two ledger components. Remaining fields keep canonical value/loss, occurrence and coefficient accounting. Migration source now binds the three declared immutable partial HEAD hashes before accepting the old envelope, and preserves exact flat grid/clock/state plus canonical roundtrip under the explicit 8192-node/16MiB format. Historical prefix losses remain NOT_MEASURED.

Reviewer independently compiled a temporary standalone native call to the new owner implementation and checked its emitted Wide mantissa/exponent/loss with Python Fraction, rather than using binary64 as its own oracle. Both actual failed operands `(2.7403074891849688e-303,1.4493951880436e-6)` and nonexact NORMAL `(3.141592653589793,0.123456789)` have exact product error enclosed by stored canonical loss plus readout quantization. Actual positive subnormal readout is `3.97178848858453282e-309`, canonical exponent -1025; no zero replacement. Compile/execution/oracle shell exit 0, wall 0.048s, no science calls. Temporary sources/output: `/tmp/igm-independent-owner.rs`, `/tmp/igm-independent-owner.out`.

Reviewer command `python3 research/igm_blockers_20261008/numeric/compare_numeric.py 10` exited 0. Original 37-field next-common-epoch comparison worst temporal allowance ratio `0.023870094710654346`, tail `1.1136936817246132e-12`; all three source checks below 0.034. Independent parsing of live checkpoint envelopes and canonical trailers confirmed checksums and nonnegative loss/coefficient fields, observed sizes 78621/87837 bytes. No reviewer advance executed.

Scoped decision: targeted representation/residual repair and first common-epoch release gate pass. Entire suffix, later horizons, migration-negative controls and remote CI require their actual execution evidence in final task return. An endpoint-only comparison must not be reported as every-common-epoch refinement. No full z=12→10 or continuum approval follows from this review. Old unmeasured loss, spectral reconstruction/quadrature, source integration and time propagation remain separate claim limits.


## Final numerical scope boundary

Inspected the final read-only `radiation::gamma` repair: identical node/provider/epoch factors are multiplied and summed through canonical Tracked values; partial arithmetic and optional readout quantization bounds are retained and checked against the original Gamma observable allowance. This recovers the accepted-state observer without evolving the state. It does not repair stock transport or assert continuum source error.

Raw terminal failures are genuine positive transported-stock subnormals: coarse/tail attempted k12 at `3.812277937532397e-309`, fine attempted k23 at `3.79902930489655e-309`. Accepted endpoints remain coarse/tail k11 and fine k22, same epoch `-2.56445769079487`. The guarded full-stock path remains rejected; loosening its scalar guard without canonical per-node N/E and incoming-loss/source-characteristic propagation would not satisfy the approved model integrity requirements. Final numeric decision: arithmetic/first-epoch repair PARTIAL_PASS; full 0.0008 suffix, z=12→10 and continuum validation NOT_COMPLETED. Historical and newly observed failures remain evidence.

Final test finding (reported for one local closeout, not a new review round): `negative_checkpoints.py` initially labelled three stale-checksum corruptions as missing_loss, duplicate_loss and wrong_epoch. All three returned CHECKSUM, so these observations prove envelope corruption rejection only. The last-byte mutation changes a canonical active-loss exponent, not the epoch. For semantic tests recompute the outer payload checksum, mutate the actual state epoch, and assert the specific canonical/clock decoder refusal. Original recorded five owner tests do not exercise a point-residual PASS versus bound-aware residual rejection; absence of that regression is a remaining validation gap until supplied. These test defects do not imply the inspected arithmetic implementation is wrong and do not authorize another campaign.

Remote CI terminal status must be received by the parent closeout. This review does not certify a pending external run.

## Final test finding closed

Inspected corrected source and raw results without rerunning science. The semantic controls now recompute the envelope hash after mutating its payload. Missing redshift-owner loss returns `MISSING_OWNER_LOSS_OR_COEFFICIENT`; changing the actual stored state epoch returns `NEW_ACCEPTED_CLOCK`; appending a second canonical payload trailer returns `NEW_ACCEPTED_CLOCK`. All exit 2 with only configuration startup counters `[1,1,0]`. The case historically labelled `duplicate_loss` tests a duplicated canonical payload trailer; it does not establish detection of arbitrary numerical doubling of a legitimate budget. `wrong_epoch` now uses the actual state offset after context/k/elapsed, so it tests the stated clock condition.

Inspected `coupled::representation_tests`: a point residual 0.6 with representation bound 0.5 passes the point test and fails the original bound-aware gate; residual 0.2 plus bound 0.3 equals 0.5, confirming one charge. Raw `residual-tests.log` has 7/7 PASS, including those two regressions. Earlier test finding is closed within this same review round. No implementation defects remain open at the scoped consumer/arithmetic/partial-migration boundary. Numerical stock transport and continuum authority remain the declared unfinished work, and remote CI reception remains the parent closeout responsibility.
