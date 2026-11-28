# R10A rho freeze impact separation: bounded return

**판정: `SURROGATE_REBUILD_UNRESOLVED`.** 고정 holdout은 허용된 Q23 midpoint split 1회 후 통과했지만, 실제 GK15 적분 node에서 새 exact sentinel이 상대오차 `1.4166e-3`을 보였다. `2e-4` admission threshold의 7.08배다. 32→64 contour panel 차이는 `3.44e-8`이므로 이 문제를 contour panel 오차로 돌릴 수 없다. `attempt2/THREE_LANE_RESULT.json`과 `APPENDIX_A_COMPARISON.json`은 보존된 **탐색 결과**이며 R10A의 확정 정량 판정이 아니다. 추가 interpolation 전환이나 두 번째 refinement는 recovery handoff가 허용하지 않는다.

## 출처와 범위

- PR15 HEAD/tree: `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`.
- PR17 source HEAD/tree: `f7d47d62f48d04da7b32d1dca945b107ffa1fb29` / `1661635d34ce3e04f1eadb0a841be648b016b01c`.
- Restored R10A handoff Git blob: `38546ac82ebbd15f70560bd1cc2631537db44ddc`; recovery handoff and five restored companion blobs matched expected IDs.
- Author FORTRAN remains static evidence only: R9 classified factor-two direct on stored Delta, but `SECTION` selects `CMES(1)` for all rho. It was neither copied to production nor executed here.
- Historical DR8 raw anchor table was not recovered with provenance. Current Git/local run outputs and bounded Drive/Dropbox title searches did not supply it. `SURROGATE_SOURCE=FRESH_R10A_REBUILD_NOT_DR8_BYTE_REPRODUCTION`.
- Scope: Nmax=3, five existing branches, E=0.5/5 keV/u; only F2-RHO, F2-FROZEN, F1-RHO. No new channel or physical cross-section claim.

## 방법과 검증

The research-only adapter feeds constant branch-specific Delta(0) through the existing Eq50/54 batch path inside unchanged support. RED: 3 genuine behavioral failures from `NotImplementedError` stubs, exit 1; GREEN focused: 3 passed. Research runner uses depth 96, contour panels 32, rotation steps 32, gk7 seed nodes and fixed holdouts, then support-split gk15 adaptive integration at rtol `2e-4`, atol `1e-10`, max 96 intervals. These are explicit `NEW_R10A_NUMERICAL_CONTRACT` values, not a claim of DR8 parameter byte identity.

Initial anchors were 9 per branch (0, support endpoint, 7 gk7 nodes). Fixed holdouts were support fractions 0.125, 0.375, 0.625, 0.875, 0.95, 0.99, excluded from fitting. Q23 exceeded the gate initially; one permitted midpoint split added child gk7 nodes (24 anchors total), yielding fixed-holdout maximum `6.26e-6`. Other maxima: S23 `1.9715e-4`, Qother `1.35e-5`, Q12 `1.3015e-4`, Qm1 `1.2821e-4`. Full anchor/holdout rows, exact hex values, and branch diagnostics are in `attempt2/SURROGATE_MANIFEST.json` and `attempt2/BRANCH_DIAGNOSTICS.json`.

An exploratory check of conditioning warnings found exactly one GK15 node warning, Q23 at rho/support `0.7132835427565373`. Its fresh exact Delta disagreed with the surrogate by `1.4166389817345478e-3` at 32 panels. A 64-panel repeat gave `1.4166045154428908e-3`. This invalidates the heldout-only surrogate admission for a quantitative integrated claim. The fixed holdout gate's PASS and the GK15 integrator's embedded estimator do **not** bound this interpolation error.

## 격리된 탐색 수치

The three-lane adaptive evaluation itself converged numerically on 7 support-split GK15 intervals, 105 evaluations, zero refinements; worst normalized embedded component estimator `0.612`; maximum column-sum defect `1.28e-14`. Its surrogate failure takes precedence.

| Lane | Indexed loss 0.5 keV/u (a0²) | Indexed loss 5 keV/u (a0²) | Appendix-A six-shell multiplicative RMS |
|---|---:|---:|---:|
| F2-RHO | 1.95513 | 60.45247 | 1.9757 |
| F2-FROZEN | 6.51644 | 113.65791 | 2.7896 |
| F1-RHO | 21.00135 | 148.51972 | 64.0075 |

All table entries are **exploratory, not admitted**. F2-FROZEN/F2-RHO indexed-loss ratio is 3.333 at 0.5 keV/u and 1.880 at 5 keV/u. This suggests R9 I2 can have a large implementation-level effect. It does not improve overall Appendix-A reproduction in this provisional calculation; the six-shell RMS worsens from 1.976 to 2.790, and dominant n=2,3 RMS worsens from 1.413 to 1.708. The candidate interpretation is Case B, conditional on a validated surrogate or exact integration.

Every Appendix-A metric in the machine-readable comparison is labeled `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`. The six printed shell values were read from Gusev et al., CPC 286 (2023) 108662, Appendix A PDF pages 18-19 at `https://theor.jinr.ru/~esolovev/papers/CPC23.pdf`, private-readonly PDF SHA256 `10ad09d05127c38f43d98502b1f56aba7caa8cc02571dfbdce6fc947f3a15cf4`. Source PDF bytes were not committed. The local HTTPS certificate chain did not validate; byte hash and agreement with prior repository n=3/DR9B checks are recorded. Nmax upper-shell sink and source shell-n3 capture overlap and are not disjoint physical channels.

## 열린 점과 gates

Factor-two remains the preferred **research interpretation** from the prior R9/R10 source/literature record; this failed R10A numerical admission does not change production policy. Beyond rho freezing, bounded source differences include author STCKLBR2's segmentwise absolute imaginary accumulation versus the clean-room full-contour action and the author's printed 300 impact steps versus this adaptive integration. These are possible residual contributors, not a quantitative attribution. The Q23 surrogate conditioning failure must be resolved under a newly authorized numerical contract before R9 I2 impact can be closed.

`CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.

Not run: production Eq55 or Eq50/54 changes, CODE-I02 matrix, 56-action replay, worker sweep, R1/R2, L2/Krawczyk, author FORTRAN, full repository pytest. No production source/default/tolerance was changed.

## Publication and backup

The new timestamped PR17 namespace contains the complete anchor/holdout manifest, exact-node failure, quarantined lane outputs, comparison table, commands, and gate ledger. The 640484-byte evidence ZIP (SHA256 `2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75`) was uploaded create-only to the established Drive folder and Dropbox dossier folder. Both raw download readbacks matched SHA256 and passed ZIP CRC; details and object IDs are in `BACKUP_RECEIPT.json`. The archive predates that receipt and does not contain the receipt itself. Restore verification establishes archive byte identity, not scientific validity.
