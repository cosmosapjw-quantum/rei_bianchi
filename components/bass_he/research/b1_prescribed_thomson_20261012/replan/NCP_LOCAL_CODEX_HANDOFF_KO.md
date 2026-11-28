# Local / NCP Codex handoff — 사용자 첨부 RUX DAG와 B1 결과 반영

## 현재 결정

이 packet의 `replan/ACTIVE_DAG.json`과 `replan/DEVELOPMENT_PLAN_KO.md`가 다음 일정의 기준이다. 상위의 B1 `REPORT_KO.md`, `review/DECISION.json`, `NCP_LOCAL_CODEX_HANDOFF_KO.md`는 완료된 한정 연구의 증거로 보존한다. 첨부 원본은 `replan/inputs/`에 있으므로 사용자가 다시 파일을 보낼 필요가 없다. 실제 게시 ref와 백업은 `PUBLICATION.json` 및 외부 전달 영수증을 따른다.

- B1 science: `PROMOTE_SCOPED_PYTHON`
- B1 original native: `HOLD_RUNTIME_ENVIRONMENT`
- Python–Rust parity: `NOT_RUN`
- RUX00–16: 계획 노드. 이번 재편에서 새 physical 실행 없음
- active next packet: `HERE_RUX00_INPUT_AND_OWNER_01`
- new NCP work units: `[]`
- E13C11: `PARKED_PENDING_OBSERVABLE_NEED`

계획 승인, 파일 업로드 ACK, byte 복구, scientific PASS, physical admission은 서로 다르다. 첨부 문서의 archive 존재 보고를 physical-input PASS로 처리하지 않는다.

## HERE에서 다음 연구 루프를 시작할 때

주 coupled-runtime 작업 저장소는 `cosmosapjw-quantum/rei_bianchi`다. 현재 작업 branch와 AGENTS.md를 읽고 기존 dirty 변경을 보존한다. 이번 BASS_HE 문서 게시를 rei_bianchi/bass production 통합·병합으로 간주하지 않는다. 2026-10-04 GLOBAL_DAG/EXECUTION_STATE는 역사 자료로 유지한다.

1. **RUX00:** 다음 소비자가 실제로 쓰는 source·입력·완료 영수증을 exact ref로 고정한다. B1의 이미 고정된 code/input/receipt를 재사용하고, 누락된 authority만 확인한다. F08/SYNC02/SYNC03 및 완료된 HE/CR/HH 계산은 다시 실행하지 않는다.
2. **RUX02와 RUX03를 독립 부분부터 병렬 처리한다.** RUX02는 v2/P01/P02A/P03A/source-delta 후보의 manifest·포함 관계와 필요한 실제 member를 읽어, 배경/epoch·H/He IC·T·spectrum/source history·closure·callback을 점검한다. 중복된 완전 archive 복구를 반복하지 않는다. RUX03는 종별 rate·opacity·재결합 광자·가열 사건의 담당 구현·단위·domain을 기록한다.
3. Case A explicit photons와 case B OTS, local HI absorption과 effective MFP의 동일 사건 중복을 막는다. Photon stock을 rate로, 누적 heat를 power로 바꾸지 않는다. CR라는 이름으로 hard-particle provider를 추정하지 않는다. 첨부 S15와 RUX13의 과정 매핑은 현재 UNRESOLVED다.
   Verner 단면적의 `photon_cross_section_cutoff_eV`와 이온화의 `ionization_binding_energy_eV`는 종별로 별도 source/용도와 함께 보존하고, 서로 대체하거나 같다고 가정하지 않는다.
4. 결과는 `SOURCE_AUTHORITY_LOCK.json`, `RETAINED_RESULTS.json`, `PHYSICAL_INPUT_ADMISSION.json`, `ATOM_OWNER_MATRIX.json`, `RATE_DOMAIN_MAP.json`, 정확한 누락 필드 및 다음 최소 과제로 반환한다. RUX01은 필요한 기존 그림을 재사용하고 B1 그림·CSV를 새 계산 없이 연결한다.
5. 필수 physical 입력이 빠지면 `PHYSICAL_HOLD`와 한 개의 구체적 입력 선정 과제로 닫는다. source-null을 0으로 채우거나 F08 13.7 eV fixture를 H/He source로 확대하지 않는다. 완전한 입력과 사건 정의가 확인된 경우에만 RUX04의 시나리오·오차 기준을 고정하고 다음 결합 구간으로 진행한다.

일반 H/He 화학·흡수·광가열은 선택한 모델이 요구하는 baseline이다. RUX12–14는 추가 정밀도 또는 특정 과정의 조건부 확장이다. Domain/필요성·짧은 RHS 민감도 선별은 RUX03/RUX04에서 할 수 있고, 정식 physical matched-history 영향 평가는 RUX11 뒤의 해당 노드에서 수행한다.

B1을 RUX06 전체 PASS로 처리하지 않는다. B1은 semi-Lagrangian occupation pullback이며, 소비자 보존형 수송의 frequency-face flux telescoping과 전파 photon-number ledger는 별도다. B1을 RUX10 전체 PASS로 처리하지도 않는다. RUX09의 actual physical ne(t), visibility·observer-tail 조건은 아직 없다.

## 이 프롬프트를 NCP에서 받은 경우

**현재 할 일은 상태 반영이며 새 과학 작업은 0개다.** RUX00–03의 경량 intake나 완료된 B1 13개 수송 실행을 NCP 작업으로 옮기지 않는다. B1은 HERE에서 이미 완료됐고 새 중량 work list가 없다. compiler 확보만을 위해64코어128GB allocation을 만들지 않는다.

새 중량 packet이 제공될 때만 그 packet의 미실행 work list를 따른다. 해당 RUX04·RUX07 등 선행 gate, 관측량·수치 목표, exact source/input, HERE pilot wall/CPU/RSS, 독립 scenario 수, 유용한 병렬 이득, 실행 명령과 fresh output/checkpoint/반환 규칙이 모두 있어야 한다. 가용 topology/affinity/quota/NUMA·RAM으로 rank/thread를 정하고, 중첩 병렬을 막고 실가용 RAM의20% 이상을 남긴다. 시간 순서와 Thomson으로 결합된 각도를 독립 job처럼 나누지 않는다.

현재 반환 문구:

> RUX 후속 계획 반영. B1 Python 결과는 보존, native/parity는 HOLD/NOT_RUN. 다음 경량 작업은 HERE의 RUX00 후 RUX02/RUX03 병렬 intake. 새 NCP work 0, E13C11 대기. 완료 계산은 재시작하지 않았음.

새 host attestation·NCP 실행 성공·physical EoR 채택을 선언하지 않는다. 실행하지 않은 gate는 해당 NOT_RUN/HOLD 상태로 유지한다.
