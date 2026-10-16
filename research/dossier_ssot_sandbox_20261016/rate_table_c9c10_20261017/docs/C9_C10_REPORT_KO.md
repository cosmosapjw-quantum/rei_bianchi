# REI rate-table RT-C9/C10 scoped review and handoff (2026-10-17 KST)

기준: [PR #177](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/177), commit `2f4103968cc26061a62dc7931c27c2fe86d75cd8`, PR #150 frozen Grackle owner. C8 기존 PASS(`3.8172670e-7 < 1e-5`) 보존, 재실행하지 않았다.

## 1. 핵심 C9 findings

**F-C9-01: parallelism-confounded speedup.** C8에서 4-worker table versus *serial* direct로 제시한 5.303x ordered, 2.505x random은 lookup table 단독 효과가 아니다. 새 동일 worker=4 및 동일 입력 N=262144의 3번 독립 실행, 각 실행 7회 rotated median으로 다음 측정:

- ordered: speedup(min, median, max) = (1.450, 1.608, 2.054)x.
- random: speedup(min, median, max) = (1.268, 1.371, 1.375)x.
- 32768-쿼리 경우 random speedup 1.06–1.14x 수준; 작은 표본의 첫 복원 시도에서는 0.82x도 관측했으므로 workload-dependent. timing medians과 raw를 JSON에 보존.
- measured build 0.13–0.15s; 262144 calibration에서 amortization 약 1.8–3.4 million queries, 그러나 32768에서 다른 break-even이 나온다. universal break-even이 아님.

**F-C9-02: temperature derivative lacks a uniform approval.** 값 `O(h²)`/log derivative `O(h)` 분리. 본 C9에서 표본 `|Δg'|` 최대 6.57e-3; Jacobian 및 full Newton source-on solver는 HOLD. 분기 내부 smooth curvature bound을 전 구간에 인증하지 않았다.

**F-C9-03: actual RHS source and conservation.** 4 gas fraction states × 9 temperature points = 36 source-identical cases. 최대 양자/반응 정규화 차이 1.395e-08; energy 6.667e-09; temperature derivative RHS 8.129e-09; conservation ledger 1.227e-16. Exact prepared temperature identity compared with actual EOS, stale bundle throws IGM_PREPARED_TEMPERATURE_MISMATCH.

**F-C9-04: typed domain near T=1e6.** Initial test fixture used `from_temperature(1e6)` whose EOS reconstruction slightly exceeded upper source domain, correctly rejected. No clipping/guard change; repaired fixture to 9.99e5 K. First wrong-layout restore `include_str!` failure and new crate Cargo.lock ordering remain recorded as environment errors.

## 2. Implementation and tests

`review/c9_independent_review.rs` contains actual source-mounted Rust tests, four/four PASS, code source unchanged; `policy/` is a **standalone advisory** crate, nine/nine Rust tests PASS plus cargo fmt and standalone strict clippy PASS. Original full-library Clippy `-D warnings`: FAIL with 52 inherited warnings (new C9 test diagnostics 0); this is not a production build failure.

C10 policy `choose()` returns Direct on source identity mismatch, derivative/Jacobian need, unmatched worker/pattern, insufficient memory, insufficient expected amortization or value accuracy fail. For a demonstrably matched workload, table may be recommended only if predicted net speedup ≥1.10, savings ≥1.50× build cost, with source sample `max rel ≤1e-5`. **This is a planning reference and does not opt-in any native production source.** Input predictions and row medians remain empirical and require actual workload profiling.

## 3. Claim/decision

- C9: `PASS_SCOPED_TESTS_AND_NUMERICAL_METHOD_AUDIT`, `independent_external_actor=NOT_RUN` (no native delegation); new objective Rust tests provide partly independent instrumentation.
- C10: `IMPLEMENTED_AND_TESTED_ADVISORY_POLICY`, durable reproducible handoff and backup; native production integration NOT_RUN.
- FULL_EOR, source-on Newton Jacobian, Bianchi paired history: HOLD unchanged. No accidental semantic/byte mixing; old PR150 and PR177 have not been mutated.
- Positive next execution: if native consumer needs table, run task-owned paired nontrivial RHS/Newton source-on point pilot and actual workload profile. Otherwise continue SA-01/SA-02 or ISO-EOS as resource permits. Do not repeat frozen full NCP campaigns.
