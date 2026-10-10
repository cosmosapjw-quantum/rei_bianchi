# 다음 local Codex 시작문

`cosmosapjw-quantum/rei_bianchi`의 `research/broad-history-acceleration-20261010`을 fetch하고, `research/broad_history_20261010/RESUME.json`, `REPORT_KO.md`, `SCIENTIFIC_CONTRACT.md`, `DAG.json`, `BLOCKERS.json`, `independent/DECISION.json`부터 읽어라. GitHub publication receipt의 정확한 commit도 확인하라.

REI-ACCEL01의 R15/HG97-B reduced20→4 history는 실제 수행되어 검증되었다. **그림을 다시 만들기 위해 RUN001/002를 반복하거나 이미 완료된 PHYS21/22, CR02B, E13C3, HH_PHYS03 검산을 재시작하지 마라.** N1과 N2를 병렬로 수행하고, BASS 담당은N4, CR 담당은C1, REC 담당은A_REC를 별도 진행하라. 한 node의 실제 코드·입력·first failure·측정값을4시간마다 durable checkpoint로 남겨라.

N1: 기존 IGM owner `39c39eab1cc2f1a215723680accc123e67ef13b6`의 low-T CaseA 구현과 physical stack `8d9526a75e85202764e845c7d5d79d7f903e7c55`의 HM12 source/background를 실제 call-site 기준으로 결합해라. R15 적분 방출률로 존재하지 않는 photon spectrum을 만들지 마라. HM12 native spectrum은 z15.93을 넘지 않으므로 full spectral history는 예를 들어15.9→4로 고정하고 초기 복사·기체·CaseA cooling/emission/escape 계약을 먼저 명시하라. 기존 native receiver의 고온·짧은 구간 guard를 삭제해서 통과시키지 마라.

N2: HE E13C3의 지수 보정은 고정 affine path에서 검증된 후보이지 새 gas history가 아니다. HH PHYS03는 N/E 보존에도 chronology/remap 편향이 남음을 보였다. 이 결과를 사용해 native source chronology와 적분 성능을 개선하되, **유한시간 전체15.9→4 paired history의 owner-fixed 관측량 오차**로 판정하라. 엄밀한 국소 remainder certificate를 전체 계산의 자동 선행조건으로 삼지 마라. 물리·수치 budget을 실행 전에 선언하고 failure 때문에 완화하지 마라.

N4: 새 `*_BASS_CELLS.csv`는 producer quadrature로 정의한 proper-time 평균 전자밀도 schema다. 기존 snapshot schema와 구별해 native adapter와 source identity를 작성하고 실제 `fixed_time_optical_depth`/visibility primitive로 수신하라. 동일 proper-time 경계 tau와 observed-z 방향별 tau를 구분하라. 후자에는 실제 null-covector endpoint inversion과 observer tail이 필요하다.

C1: `DH_10_1000_eV_PR25`와 `BEQ_BED_CCC_0p1_900_eV_PR27`는 다른 인과적 모형이다. 공통 source/bath/energy/channel contract에서 비교한 뒤 선택하라. PR25의 NIST PHYS02C가 PR27의 atomic-consistency task를 해결했다고 간주하지 마라. CR-off 또는 pure heat로 실제 CR-on 요구를 대체하지 마라.

원래 He/HH/CR 정밀 연구의 source와 현재 blocker는 별도 lane으로 유지하라. 없음/null인 RCT spectrum·heat·recoil을 가정값으로 채워 physical PASS를 만들지 마라. 새로운 code/evidence가 준비되면 별도 독립 decision review를 받고 additive branch/PR로 게시하고 Drive/Dropbox 기존 전달 폴더에 checkpoint를 보관하라. 기존 owner branch를 force-push하거나 merge하지 마라.
