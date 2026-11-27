# BASS_HE: fastest track과 원자 확장 lane의 연결 계획

## 결정

현재 공개 rate exporter를 재사용하여 **원자 데이터 공급기**의 역할을 마무리한다. 종·기하·광수송을 새로 구현하지 않는다. 원자 이론 완결을 R1의 선행조건에서 제거하되 B5C2와 그 이전 coherent/continuum 연구는 별도 lane으로 봉인·보존한다. 새 기본 source의 자동 선택이나 gate 승격은 하지 않는다.

앞선 보고서의 KF96 단독 우선 권고는 이번 최신 repo read로 수정한다. B3에는 이미 GM25/W82의 1.70e-13 cm3/s 공급기가 있다. KF96의 1e-14와 함께 **두 문헌 nominal source와 off control**의 시나리오 family를 만든다. 17배 차이를 확률적 confidence interval로 읽지 않는다. 공통 적용구간 1000–10000 K 밖의 계산을 위해 무근거 clamp/외삽을 추가하지 않는다. source 간 비교가 관심 결과를 바꾸면 먼저 그 반응·조건만 좁혀 해결하며 전체 ab initio 프로그램을 자동 재개하지 않는다.

## 이미 있는 제품과 활용 경로

| 자산 | 정확한 현재 경로 | 이번 사용 |
|---|---|---|
| strict B3 rate/count API | `research/shared_c64/20261003/EOR_B3_ATOMIC_EXPORT_v1/src/bass_he_atomic_export/` | request/packet·one-provider-per-reaction·null moments를 그대로 활용 |
| 기존 source registry | 위 경로의 `registry.py` | GM25 core identity 유지; KF96 별도 source를 additive 확장 |
| EOR T4 source assembler | `research/shared_c64/20261003/EOR_T4_RATE_SOURCE_v1/T4_RECORD_KO.md`와 SHA-bound ZIP | species/event/chemical ledger 설계 재사용; 별도의 새 cosmology solver를 만들지 않음 |
| B5C2 inner boundary | `research/shared_c64/20261004/EOR_B5C2_INNER_BOUNDARY_v1/` | legacy 자료; fastest track에서 실행 불필요 |
| C2G/C2H1 coherent/exterior DAG | `legacy_sources/`에 원본 경로 보존 | state-resolved/coherent 관측량 요구 때만 재개 |

T4 전체 코드가 이 Git namespace에 모두 있다고 추정하지 않는다. 전체 ZIP의 SHA/locator를 LEGACY_LANE.json에 고정한다. 이번에는 원 T4 ZIP을 Dropbox에서 실제 회수하여 SHA-256·CRC를 확인했고, 원16-node DAG/반응registry/gaps/claims/next-step의6개 파일을 legacy_sources/T4_archive에 byte 그대로 복사했다. 원 scientific runtime를 실행하지 않았다. 필요한 실행 노드가 T4 내부 코드를 실제 필요로 할 때만 정해진 archive를 복원한다.

## 단계와 종료 조건

1. **HE-P0 — 채팅 선행 연구(완료):** source conflict와 원문 확인, exact stoichiometry·energy·units 유도/검산, 최신 B5C2 read 및 legacy source 백업. 과학runtime의 완료와 구별한다.
2. **HE-F1 — B3 source family(구현 예정):** 기존 GM25 core는 byte 보존, KF96용 별도 source evaluator를 추가하고 source 명시 선택을 요구한다. 각 domain별 양끝·범위 밖·다른종·double-count·null moment의 focused test만 실행한다. 기존 B5C2 과학 suite는 실행하지 않는다.
3. **HE-F2 — 소비자 계약 연결(예정):** atomic packet의 rate/count와 rei의 density/event/photon/heat ownership을 일대일 결속한다. photon spectrum/mean energy가 null일 때 열 source를 0이라고 추측하지 않는다. 선택한 제한 closure의 별도 ID 또는 해당 channel scope 제외를 연구 계약으로 명시한다. 결정권과 thermal implementation은 rei_bianchi다.
4. **HE-F3 — 응용 종결(예정):** REI-F09가 한 번 실행한 공통 atomic paired-sensitivity 결과를 검토·수락한다. HE가 별도 campaign을 중복 실행하지 않는다. 같은 source scenario를 FLRW와 Bianchi 양쪽에 적용했는지 확인한다. off/KF96/GM25의 짝지은 결과 변화와 수치 오차를 분리한다. 한 번의 preregistered campaign에서 robust/not-robust를 보고하면 응용 공급 역할을 닫는다. `atomic_exact_rate_certified=false`는 유지한다.
5. **HE-L1/L2/L3 — 대기 lane:** 아래 조건이 성립하면 해당 하나만 재개한다. source 밖의 결과를 보고하기 위해 legacy PASS를 가정하지 않는다.

## 원계획을 호출하는 세 경로

- **L1 thermal RCT precision:** 시나리오 선택이 과학 결론을 바꾸거나 현행 source domain 밖으로 진입하면서 더 나은 공개 근거가 없으면 B5C3부터. B5C2가 남긴 실제 inner V−2/R, Gamma remainder→regular solution→matching error를 먼저 해결하고, 이후 cross-section→Maxwell rate→moment로 연결한다. finite-radius eigenvalue agreement를 전체 오차 상계로 사용하지 않는다.
- **L2 fast-ion populations:** CR/fast He, state-resolved populations, stopping을 실제 연구할 때 CollisionDB/Liu 별도 source lane을 연다. 단면적 frame·energy-per-u·channel sum·license를 고정하고 중복 nl/n/total을 금지한다. 이 경로가 thermal RCT를 대체하지 않는다.
- **L3 coherent/continuum:** complex amplitudes, phase-sensitive observables, continuum closure가 요구될 때만 보존된 C2G DAG와 C2H1 delta로 복귀한다. 데이터 표의 population σ로 phase나 off-diagonal kernel을 복원하지 않는다.

새 legacy 결과가 나와도 소비자 외형을 바꾸지 않는 것이 연결 원칙이다. 동일 reaction_id, 단위, domain, frame, state semantics, uncertainty 의미, photon/heat moments의 availability를 충족한 새로운 provider_id로 등록한다. 기존 source와 parallel validation→한계내 receiver 비교→명시적 선택 변경 순서이며 조용한 default 교체는 없다.

## PR 단위

| 작업 PR 단위 | 목적·범위 | 검증·수락 | 의존성 |
|---|---|---|---|
| HE-DOC-0 (이 패키지) | 선행 연구·DAG·legacy 실물·handoff 게시 | JSON/해시/수식 산술 확인; product 실행 주장 없음 | 없음 |
| HE-PR-1 | 기존 B3의 KF96 source 대안 및 source family manifest | 기존 GM25 출력 보존, 정확한 17비율, source별 domain 거절, no-default/no-double-count | HE-P0 |
| HE-PR-2 | atom↔rei packet 계약 시험·energy null handling | 원자 provider에 density/opacity/geometry 없음; 소비자 event ledger와 일치 | HE-F1 및 rei provider contract |
| HE-PR-3 | paired sensitivity 결과와 atomic supply closure | observable 변화/수치 error/source choice 분리; 결론 보존여부 기록 | HE-F2 및 REI-F09 sensitivity 결과 |
| HE-L-PR-* | 선택적으로 B5C3/fast-ion/coherent 확장 | 해당 원 DAG gate와 receiver provider compatibility | reopen trigger |

이는 새 Git branch를 만들라는 지시가 아니다. 기존 branch에 단계별 bounded commit을 추가하며 현재 draft PR #17에 이 연구 프로그램 링크를 유지한다. PR #17은 역사적 변경이 누적된 draft로 현재 mergeable=false이다. 이 작업은 merge하지 않으며 이전 scope를 덮어쓰지 않는다. root 게시가 만든 actual commit/tree/backup receipt를 최종 기준으로 삼는다.

## 비용과 중단 규칙

채팅이 source 조사·유도·구현 설계의 권위다. Codex는 먼저 TASKS.json의 첫 ready 작업과 지정 파일만 읽는다. 뒤의 scientific runtime 노드가 자원 한계를 실제 측정하기 전까지 NCP64·MPI를 새 필수조건으로 만들지 않는다. 숫자 정밀도/과학모형/허용오차를 바꾸어 실행을 통과시키지 않는다. 공통예산·domain·photon closure가 빠졌으면 그 사실과 최소 입력만 반환하고 완료된 원자 연구 전체를 재감사하지 않는다.

HE-F2의 ledger가 미완료이면 optional REI-F09만 대기한다. rei_bianchi REI-F08의 명시적 baseline scope는 독립적으로 진행하며, atomic sensitivity 미완료를 모든 재이온화 연구의 blocker로 만들지 않는다.
