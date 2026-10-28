# 외부 source 및 n/T 모형 — 실행 전 checkpoint

기준은 `cosmosapjw-quantum/rei_bianchi` PR243의 실제 확인한 HEAD
`48c5656c3ff396edf61390214c40cbdcc203f172`이다. 기준 tree는
`7153c3bc6e9ee4493e8bc7af10ebe69fae73e227`이다.
새 branch는 `research/rei-external-sources-20261028`이다.

사용자의 “예산 증액은 승인할게”에 따라 현상론적 external source+n/T 모형의
한정 실행을 준비한다. 새로운 IVP는 실행하지 않는다. 이 checkpoint 시점에는
과학 계산·검사·평가·렌더가 모두 NOT_RUN이다. 지금 게시하는 파일은 이 문서와
`BUDGET_AUTHORIZATION.json` 두 개뿐이며 PR 생성과 최종 백업은 후속 전달 단계다.

원래 DAG는 작업33/88, 중앙28/88, 이번 증가0; 기존 빠른 경로는4/7이다.
원래 `ROUTE_KO.md` F4 문구는 “n/T 생성·붕괴·광핵·역약반응의 실제 source/rate와 적용 구간 확정”이다.
그 문서의2/7은 준비 당시 snapshot이고 실제 후속 전달의4/7을 되돌리지 않는다.
이번 현상론적 모형은 사용자가 허용한 별도 범위다. 실제 물리 source 완료 여부와
현상론적 산출물 판정은 구별하며, 기존 CR113 및 다른 공급자 예약은 보존한다.

Planning 누적17.295332885 CPU초, 원래 상한10에서 임시 누적상한30;
presentation 누적54.561494494, 원래30에서 임시65로 승인되었다.
Main595.225063/600, NO_MORE_IVPs는 그대로다.
검사 child최대4 CPU초/wall20초/예약4.5, 평가3/wall20/예약3.5,
그림3/wall30/예약3.5이며 단일 worker, 최대3GiB, 자동 재시도0이다.
입수·저작 등 미계측 비용은 UNKNOWN_NOT_ZERO다.
종료 시10/30으로 복귀하고 누적 debit을 유지한다.

다음 행동은 검증된 기준에 이 두 파일의 checkpoint commit을 게시한 뒤,
controller의 고정 계약에 따라 이미 승인된 유한 작업을 수행하는 것이다.
