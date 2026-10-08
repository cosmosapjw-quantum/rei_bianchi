# Independent final review: tracked transport and 0.0008 suffix

**Findings-first verdict:** the initial diff had an energy-loss handoff omission and an endpoint-only comparison scope limitation. A targeted source correction to the handoff was observed during this review; publication can remain scoped exploratory, with the full continuum/error authority HOLD. The current cutoff-entry guard also needs the small canonical-state correction below. This report distinguishes the executed pre-review binary from source edits made during the review.

Review is read-only: git diff/status, local source, existing logs and JSON. No new science, provider, observer, arithmetic probe or tests were executed by this reviewer.

## Findings and dispositions

### T1 — High: V3 energy discrepancy was reconciled but not propagated (targeted correction observed)

`numeric/source/rei-next-nodes/short-hhe-midpoint/src/radiation.rs:24–50,250`; `canonical_owner.rs::kernel_tracked`.

The initially reviewed `reconcile_node_energy` formed energy from number, added old energy loss and value discrepancy, then the caller passed only `stock.number` to the kernel. The reconciled energy uncertainty affected the continuity check and was then discarded from the next owner/node. Number loss propagation alone does not preserve the V3 energy-specific discrepancy.

During the review the root changed the kernel signature to take `stock_energy` as well: outgoing stock energy now attenuates that tracked input, redshift energy integrates it, absorbed energy derives from that integral, and heat explicitly receives the incoming energy-loss term. This addresses the identified omission at those uses by inspection. It does not certify upstream coefficient errors or establish the final source edit produced the already stored suffix; exact command/binary/result identities must distinguish the existing run from the corrected path.

Minimal acceptance follow-through: retain original suffix evidence and explicitly label its loss-authority limitation, or verify the corrected path in the already authorized bounded scope. Do not overwrite old receipts or silently assign their results to the new source.

### T2 — Medium: cutoff-entry check can erase a positive canonical tail whose scalar projection is zero

`numeric/source/rei-next-nodes/short-hhe-midpoint/src/radiation.rs:192–203`.

For `tau <= s0`, the runtime tests scalar `f != 0.0` and otherwise returns `Owners::default()`. An extended-range nonempty input with binary64 projection zero is therefore silently treated as structural empty. This is the very state distinction the new transport path introduces. The repaired replay already tests `!stock.number.value.is_empty()`.

Minimal correction: use the canonical emptiness predicate at runtime too (and preserve the existing unsupported-initial-outflow error). This is a domain-boundary defect; no evidence was seen that a valid generated suffix actually supplied such an off-domain nonempty node. No full campaign rerun is needed for this one-line guard repair.

### T3 — Medium: comparison_48 certifies the endpoint, not all common history rows

`repair_20261008/compare_common_48.py:18–29`; `comparison_48.json`.

The script reads `endpoint_48.csv`, `endpoint_96.csv` and `endpoint_48.csv`, producing one temporal and one tail row comparison. The PHASE receipts prove integration reached the 0.0008 endpoint, but this comparison alone does not prove the original 37-field limits hold at every common intermediate epoch.

Minimal correction: label the claim `0.0008 integration complete; endpoint refinement passed`, or compare already saved coarse/tail histories with the matching even-index fine rows. This requires no new evolution. Continue to exclude full z12→10 and continuum validation.

### T4 — Medium for unique accounting claims, conservative rather than false-PASS: reconcile can count correlated uncertainty twice

`numeric/source/rei-next-nodes/short-hhe-midpoint/src/radiation.rs:35–48`; `canonical_owner.rs` direct heat loss addition.

Reconciliation adds the number-derived expected-energy loss to the old energy loss. The latter generally already includes uncertainty descended from the same incoming number. After the T1 fix, heat also combines a number-derived uncertainty path with the full energy-loss path. These sums are conservative but do not establish non-duplicated uncertainty accounting. Repeated reconciliation may unnecessarily inflate bounds.

Minimal scope correction: call the result a conservative enclosure and avoid a unique/no-double-count claim. If nonduplication is required, retain a decomposition of shared number-induced and independent energy-specific terms; do not subtract guessed overlaps. For the reconciliation union alone, a maximum of separately valid enclosures after shifting centers can avoid an unnecessary sum, but that requires its invariant to be specified first. This is not evidence that the stored scalar evolution is wrong.

## Items that now look correct in the reviewed scope

- The active transaction passes `old.canonical()[j]`; segment-to-segment input is the tracked output. Positive number stock below the binary64 floor survives the `tracked_scale` / `tracked_add` value path, while inherited number loss participates in those operations.
- Stock and source are separate positive terms in the characteristic convolution; source is not folded into old stock or added twice. Each emitted owner still has its distinct source formula. Coefficients are evaluated in binary64 and treated as the scoped given coefficients; exp/integral/provider approximation authority remains unclosed. In particular, a coefficient itself underflowing to zero at a much larger optical depth is not automatically solved by scaling the stock.
- `record.rs` now correctly maps durable scalar order `N,U,QN,QE,red,...` to ledger order with `[0,1,3,4,2,5,6,7,8,9,10,11,12]`.
- Replay retains the final segment's canonical number/energy pair, restores its canonical logs, and applies the same outflow routing before comparing node ledgers. This repairs the previous scalar-only final-pair restoration defect.
- `repair-record-replay-live-b.log` records two actual midpoint acceptances and leaves full-Wide admission HOLD. It is existing evidence, not a run performed by this reviewer.
- V3 persistence carries the tracked fields; this final diff does not replace the codec or silently remigrate old HEAD files.

## Existing suffix evidence and correct claim ceiling

The stored phase receipts report:

| Branch | completed new suffix | last epoch | max original three gates |
|---|---:|---:|---|
| coarse | 17→48, 31 advances | −2.564149357461537 | 0.7422992, 0.00594034, 0.00742653 |
| fine | 34→96, 62 advances | −2.564149357461537 | 0.3719737, 0.00613533, 0.00746802 |
| tail | 17→48, 31 advances | −2.564149357461537 | 0.8776295, 0.00656331, 0.00769745 |

Existing `repair-comparison-48b.log` reports endpoint temporal maximum allowance ratio 0.023932797389989293, tail 4.080871757717751e-12, and source ratios below 0.197. The corrected source comparison subtracts prior from final cumulative Simpson integrals, consistent with the resumed suffix's emitted-owner difference. These observations support the stated endpoint discrete comparison for that run.

The inspected TASK_RETURN was still the prior k16 closeout, so the new closeout must be updated rather than presented as already audited current documentation. Report new execution counts and per-binary evidence, preserve all k17 diagnostic failures and costs, retain `NOT_REACHED_FULL_Z12_TO10`, `NOT_VALIDATED` continuum and physical HOLD. Neither this completed short horizon nor replay success closes spectral reconstruction, original-kernel/provider/state uncertainty, historical prefix errors or global residual/Jacobian propagation.

No repository files were modified by this reviewer. Only this `/tmp` report was created. Findings have been sent to the root; this one review pass is complete.

## Targeted correction verification (single requested follow-up)

Read only the changed `kernel_tracked` block, cutoff-entry branch, and `compare_common_48.py`. No code execution, new numerical calculation, provider call, or additional review scope was introduced.

1. **Energy handoff corrected.** `kernel_tracked(stock, stock_energy, ...)` now propagates the carried energy through outgoing U and redshift-energy integration; B is scaled from that tracked redshift integral. Consequently the V3 discrepancy/loss carried by `reconcile_node_energy` is no longer discarded before those owners. The direct positive heat certificate is explicitly reconstructed from tracked photon number and source with its own positive coefficients. It no longer adds the separate carried-energy loss a second time to this independent reconstruction. This confirms the requested path correction; upstream coefficient/model error authority remains outside it.
2. **Cutoff-entry corrected.** The early `tau <= s0` branch now checks `!initial.number.value.is_empty()`. A nonempty canonical tail with scalar projection zero is refused rather than returned as structural empty. This resolves T2.
3. **32-row alignment corrected.** The driver histories contain newly accepted rows after the first index: coarse `history_16_48` is k17…48; fine `history_28_96` starts at k29, so slice `[5::2]` selects k34,36,…96, matching coarse k17…48; tail `history_14_48` starts at k15, so `[2:]` selects k17…48. Each selection has 32 rows. The script now compares these histories and explicitly labels that scope, resolving the endpoint-only limitation T3. It does not claim these 32 rows include every earlier historical epoch or full z12→10.

**Targeted disposition:** T1's missing handoff, T2 and T3 are corrected by source inspection. The direct-heat duplicate addition identified during T1 repair is removed. The earlier T4 observation about conservative overlap inside reconciliation itself still limits a broad claim of globally unique uncertainty accounting; it does not invalidate the corrected path as a conservative scoped implementation. Execution receipts for the corrected source and the existing full-claim HOLD remain the root's closeout responsibility. This requested correction check is complete without further tests or scope expansion.
