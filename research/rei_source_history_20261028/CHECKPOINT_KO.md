# Source-history QSS verification: 실행 전 checkpoint

날짜: 2026-10-28 UTC. 단위: `rei_source_history_20261028`.
선택 단계: PhysMath Research Loop 1.3 C2/C10, 현재 source 연결·제한된 검증과 인계.

기준은 PR245 실제 HEAD `cc17c2481f3f1057062efe0cbfb505114a0e8cfc`이다. 새 branch는 `research/rei-source-history-20261028`이다. 기존 illustrative external-source operator와 저장된201 epochs를 재사용한다. 이번 단위는 source-history/QSS의 실제 검증과 full17 coupled solver 준비를 진행한다. 향후 coupled IVP 실행은 아직 승인하지 않았으며 최종 구체적 제안에서 별도 명시한다.

사용자는 이전 요청에서 “예산 증액은 승인할게”라고 승인했고 최신 요청에서 다음 노드를 계속 완료하도록 지시했다. Controller는 이전 승인 planning30/presentation65 누적 ceiling이 유지된다고 판정했다. 이전 closeout의 원래 정책 상한10/30 복귀 기록과 누적 비용은 보존하며, 닫힌 이전 실행 예약을 재개하지 않는다. 이번 단위의 새 유한 할당은 `BUDGET_AUTHORIZATION.json`에 기록한다. 이번 ceiling은 이전 사용자 승인30/65를 넘지 않는다.

새 실행 전 상태는 NOT_RUN이다. Tests child2CPU s/wall20s, QSS diagnostic child2CPU s/wall20s, saved-data plot child3CPU s/wall30s, 단일 worker·3GiB·자동재시도0이다. Main595.225063/600 NO_MORE_IVPs, 타 담당자 예약, 누적 debit 및 UNKNOWN_NOT_ZERO를 유지한다. 이 checkpoint와 budget의 게시가 실제 실행보다 먼저 이루어져야 한다.

PR244는 별도 moving-knot caloric derivative 단위다. 확인 HEAD `0da7cac8c064238913b6f49108f4fbfd5edd7523`, 갱신2026-10-28T10:17:09Z이며 authority 상태는 PROPOSED_NOT_APPROVED_NOT_RUN이다. 그 기록의 과거 ledger/proposed20/60을 최신 실제 debit으로 더하지 않으며 해당 담당자 예약을 유지한다.

원래 DAG working33/88, central28/88, delta0; fast4/7을 이어받는다. 새 검증 결과를 얻기 전 추가 과학 수용이나 진전으로 올리지 않는다. 원래 NO_MORE_IVPs 최초 발행자/사용자 원문을 확인했다는 주장은 하지 않는다. 확인한 historical machine-readable 정책은 `research/rei_expanded_event_consumer/lumina_resume_20261026/BUDGET_POLICY.json`, blob `d1998ca467a40bf9f093e48945e06b6fcf693c9f`이며 scope는 “This REI research campaign and continuing bounded work under the same original budget ledger”이다.

다음 행동: 두 파일의 원격 게시·선택 readback을 확인하고 controller가 동결 과학 계약에 따라 이번 non-IVP 실행을 진행한다. Full17 coupled solver는 준비 산출물로 유지하고 실행하지 않는다.

## 첫 tests 전 할당 amendment01

Root는 provider201rate evaluations와 RHS checks의 미측정 비용을 고려하여 첫 tests의 child CPU2→4s, reservation2.3→4.5s를 승인했다. 위 최초 할당 문단은 이력으로 보존한다. Tests wall20s/attempt1, diagnostic child2/reserve2.3/wall20, plot child3/reserve3.5/wall30, worker1/3GiB/자동재시도0은 유지한다. 새 planning reservation 합6.8과 inherited19.204540885의 합26.004540885는 기존 승인30 이내다. 기존 ceiling을 추가로 올린 것이 아니며 main595.225063/600 NO_MORE_IVPs와 new debit0은 불변이다. 이 amendment와 budget 갱신 게시·readback 전 첫 tests를 실행하지 않는다.
