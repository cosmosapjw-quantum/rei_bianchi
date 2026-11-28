# ANGTHERM02 owner delta: 1d7fb4c → 906f217

## R2 진행 판정

**HE-ANG의 source/frame/event 공급자 계약은 그대로 진행할 수 있다.** 이번 변경은 conditional trace-Li 실험 소유자의 실제 실행 결과 추가이며, H1의 두 전자·ion 공동 분포나 경험적 각분포 공급자를 새로 제공하지 않는다. HE-X1 이론·32 fixture·독립 검토·raw/code 재실행은 필요하지 않다. 별도 HE-ANG-contract의 동결 예산만 사용하고 ANGTHERM02 ledger는 이전하지 않는다.

ANGTHERM02 소유자 예약은 유지한다. 관측된 새 HEAD는 `906f217f412500fd8d4129818e70a4064439c945`이며 PR221과 branch ref를 각각 새로 읽어 동일함을 확인했다. 중앙 계약의 `1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c`는 이전 예약 관측으로 보존한다. 기존 감사 파일은 수정하지 않았다.

## 실제 변경 범위

비교는 1 commit ahead / 0 behind다. 변경 52개는 모두 `research/rei_lithium_threshold_20261023/` 안에 있다. 변경 목록에 AGENTS, 기존 THEORY_CONTRACT, source pin 또는 handoff 파일 변경은 없다. DAG 1개가 수정되고 구현·관측 결과·review 대기 문서·국소 점근식 등이 추가됐다.

PR221은 open/draft다. PR body는 여전히 ANGTHERM01과 이전 local-flow를 설명하므로 최신 ANGTHERM02 상태로 사용하지 않는다. 실제 새 상태는 고정된 DAG/검토 문서에서 읽었다.

## 완료된 실행과 남은 승인

DAG의 현재 판정은 `NUMERICAL_GATES_OBSERVED_PASS_CONTROLLER_AND_FRESH_REVIEW_PENDING`, checkpoint는 `IMPLEMENTED_OBSERVED`다. 소유자가 선택한 10/10 conditional Li cases를 완료했고 저장된 비교 문서는 모든 수치 gate가 통과했다고 기록한다. 이는 **컨트롤러 판정과 reconstructed actual-code/result의 fresh independent review 완료를 뜻하지 않는다.** 새 INDEPENDENT_REVIEW도 그 승인을 pending으로 명시한다.

따라서 현재 예약의 read-only reuse / no execution-or-repair / 여기서 신규 사례0 조건을 유지한다. 소유자의 완료 trajectory를 재실행하거나 그 예약을 해제하지 않는다.

## 변경된 누적 budget

- 한도: CPU120 s / wall180 s, invocation CPU60 s / wall90 s, memory1 GiB, 1 thread.
- 누적 debit: **CPU101.807817 s / wall132.03456183798698 s**.
- 보존된 MEASURED 합계: CPU39.859224000000005 s / wall40.04769261898764 s.
- 초기 lost preflight의 actual CPU/wall은 unknown이며, 원 command cap **CPU60 / wall90 s**를 보수적으로 debit했다.
- 별도로 보존된 tool-history lost-log 비용도 ledger에 포함된다.
- 기록된 debit을 차감한 여유: CPU18.192183 s / wall47.96543816201302 s. 이 값은 **charged bookkeeping**이며 전체 실제 실행시간의 측정치가 아니다. **HE-ANG에 이전 불가**다.

이 확인에서는 저장된 JSON만 읽었다. 소유자의 실행 수나 budget을 초기화하지 않았다.

## HE-ANG 관련 물리 범위

새 THRESHOLD_ASYMPTOTIC은 보존된 초기 방향 `mu0` 및 fixed-q measure `dmu0` 아래의 LiI 광이온화 문턱을 다룬다. 명시된 smooth background/fit 조건에서 최종 transverse crossing의 활성 angular width와 ionization coefficient는 `t^(1/2)`, excess-photoelectron heating coefficient는 `t^(3/2)`이다. 문서 자체가 새 수치 gate·수렴차수 주장·전역 온도 오차 경계를 추가하지 않는다고 명시한다.

이는 H1 electron-impact source의 inclusive count2 정규화, lab/COM frame mapping, exchange/label 규약, 두 전자와 recoil ion event correlation을 해결하지 않는다. 따라서 HE-ANG의 기존 의무는 모두 그대로다. 이후 HE-RESERVOIR 또는 REI coupling이 이 Li provider를 선택한다면 그때 소유자 fresh review/판정과 prescribed-bath 한계를 확인해야 한다.

## 증거와 배송 범위

원 compare/PR221/ref JSON은 `owner_delta_906f217/`에, 선택된 변경 source 7개는 그 아래 snapshot에 저장했다. 선택된 7개 blob은 compare의 Git blob과 모두 일치한다. 출처 URL·SHA256·Git blob 및 상세 판정은 `OWNER_DELTA_906f217.json`에 있다.

`delivery/IMPLEMENTED_OBSERVED.json`은 donor closure와 보존된 실행 산출물을 기록한다. 이 선택 delta 문서만으로 새 ANGTHERM02 archive의 Dropbox/Drive 최종 ACK를 확정하지 않는다. 기존 중앙 S0/S1 확인과 새로운 소유자 delivery 상태를 섞지 않는다.

이번 delta 감사의 새 과학 실행0, IVP0, render0, 원격 mutation0이다. 기존 전체 intake의 사실은 당시 관측으로 보존했다.
