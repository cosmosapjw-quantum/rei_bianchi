# PR243 추가 관측과 실행 제안 갱신

새 PR244 게시 시점에 확인한 PR243의 실제 종료 원문을 추가로 읽었다. 이 기록은 앞서 고정한 source census와 단계 capsule 뒤에 붙는 변경 근거다. 기존698 commits/70 PRs라는 당시 snapshot의 수와 immutable 파일을 다시 쓰지 않는다. 전수조사나 닫힌 scientific suite를 반복하지 않았다.

## 실제 읽은 범위

PR243 head `48c5656c3ff396edf61390214c40cbdcc203f172`의 PR metadata, 마지막 commit metadata, BUDGET_CLOSEOUT.json, RUN_STATUS.json, RUN_REPORT_KO.md, RUN_DELIVERY_RECEIPT.json을 읽었다. 위 네 원문을 supplements/pr243에 그대로 저장했다. Git blob과 원격 경로는 PR243_SOURCE_IDENTITY.json에 있다. 원래 numerical sources·plots·review 전체를 다시 검사하거나 그 unit을 독립적으로 재채택한 것은 아니다.

PR243은 저장된17상태 abundance와 별도 조건부 n/T 생성·붕괴 진단을 전달했다. 빠른 경로4/7과 원래 DAG33/88, 중앙28/88,delta0를 보고한다. n/T의 all-bare, instantaneous-thermalization, passive-reservoir 조건과 서로 다른 source lineage를 유지한다. 실제 비열적 source/감속/탈출 및 daughter charge/energy mapping은 남아 있다. 현재 moving-knot derivative를 구현했다는 source는 아니며, 본 단위에 필요한 실제 recipient EOS나 physical callback f_T를 공급하지 않는다.

## 실제 달라진 의존성: 누적 비용

직접 읽은 BUDGET_CLOSEOUT은 PR242의 planning16.586967885/presentation50.928518494를 inherited_charged로 포함한 뒤, 새 관측 비용과 reserve를 더해 **planning17.295332885, presentation54.561494494**로 닫았다. 따라서 PR242 값을 이 새 수치에 또 더하지 않는다. PR243의 승인18/55는 종료됐고 원래10/30이 복원됐다. 새 scope/allowance가 필요하다는 원문도 명시되어 있다.

처음 준비한 presentation cap56/reserve4는 이 추가 비용을 반영하면 부족하다. 그러므로 최종 제안을 **planning 누적20/reserve2, presentation 누적60/reserve4**로 갱신한다. 알려진 charge와 제안 reserve의 부분합은 각각19.295332885와58.561494494다. 미계측 비용은UNKNOWN_NOT_ZERO이므로 전역 비용의 정확한 합이나 budget PASS를 뜻하지 않는다.

AGENTS의 원래 기준 대비50% 이상 증액은 별도 승인이 필요하다는 조항이 적용된다.20/60은 아직 승인되지 않았다.18/55, 기존 예약, main595.225063/600 NO_MORE_IVPs 및 타 owner 권한을 재사용하거나 옮기지 않는다. 현재 대화의 별도 F1 display0.037도 기존 다른 provenance와 임의로 합치지 않는다.

## 변경 범위와 재개

새 권한 원장은 `execution/CURRENT_EXECUTION_AUTHORITY.json`이다. 기존 `EXECUTION_PROPOSAL.md`와 stage capsule은 당시 제안을 담은 역사적 원문으로 보존한다. 원래 runner에 적힌 historical PR242 수치도 현재 원장이 아니며, 실행 후 campaign accounting은 최신 권한 원장을 기준으로 별도 additive receipt에 기록한다.

수학식·물리 전제·CaloricBranch dependency·구현·A–G tests·runner의 작업량/명령·plot source는 바뀌지 않았다. 따라서 기존 actual independent theory/static review와6개 source SHA를 재사용한다. 새 scientific finding이나 runtime 결과는 없다. R1–R10+C1–C5=15/20 및 C6–C8 NOT_RUN/C9 runtime NOT_COMPLETE/C10 pending 상태도 그대로다.

이 supplement와 최신 원장을 추가 게시·이중백업한 뒤, 최종 handoff는20/60 제안만을 현재 제안으로 안내한다.
