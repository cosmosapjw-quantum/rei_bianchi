# 첨부 DAG 기반 후속 연구계획 독립 판정

**판정: ACCEPT_PLAN_OVERLAY**  
검토 시각: 2026-10-12T07:59:33.455786+00:00  
검토자: `/root/b1_decision_review` — 후보 계획 작성과 구현에 참여하지 않은 최종 계획 검토 역할.

첨부 DAG를 현재 B1 이후의 실행 순서와 재사용 경계에 연결한 계획을 채택한다. 이 판정의 대상은 후속 계획이며, 기존 B1 과학 판정과 RUX 물리 결과의 승인을 구분한다. 검토한 문서의 bytes/SHA-256은 `PLAN_DECISION.json`의 `reviewed_file_identities`에 고정했다. 남은 계획 승인 blocker는 없다.

## 확인한 핵심 조건

| 항목 | 판정 근거와 유지할 경계 |
|---|---|
| 원 DAG 구조 | 원래 RUX00–RUX16의 17개 ID와 21개 의존성 edge가 보존됐다. 중복 ID·누락 의존성이 없고 위상 파동 순서가 모든 edge와 일치한다. 원본 `main_critical_path` 배열은 순차 실행 명령으로 해석하지 않는다. |
| 다음 현지 과제 | `HERE_RUX00_INPUT_AND_OWNER_01`에서 필요한 authority를 고정하고 RUX02 입력 점검과 RUX03 사건·과정 담당 점검을 독립 부분부터 병렬 진행한다. RUX01의 기존 산출물 연결은 이 경로를 막지 않는다. |
| RUX 상태 | 17개 노드 모두 `PLANNED_NOT_RUN`이다. 계획 작성이나 구조 확인을 노드 PASS 또는 physical admission으로 올리지 않았다. |
| B1 재사용 | 기존 `PROMOTE_SCOPED_PYTHON`만 유지한다. B1 과학 보고서·독립 DECISION·리뷰의 SHA가 변하지 않았으며, 재사용으로 완전히 닫히는 RUX 노드는 없다. 기존 transport 13회와 NCP 0회는 과거 B1 실행 수다. |
| RUX06 잔여 gate | B1의 exact LRS characteristic·공통 physical-energy/frame·null 결과는 재사용 가능하다. 실제 소비자 이산화의 photon-number propagation ledger, frequency-face flux telescoping, 선택 시나리오 remap/domain은 여전히 미완료다. |
| RUX10 잔여 gate | proper density·Thomson 단면적·B-clock 투영 규약은 재사용하되, RUX09의 승인된 종별 physical proper ne(t), visibility 정의·정규화, observer interval/tail은 새로 충족해야 한다. tail이 없으면 유한 구간 결과로 범위를 제한한다. |
| HE/CR/HH | RUX03/04의 이른 source/domain·중요도 점검과 RUX11에 의존하는 정식 RUX12/13/14 효과 평가를 분리했다. 이른 점검은 정식 노드를 닫지 않는다. 일반 H/He baseline은 선택적 정밀 캠페인으로 밀리지 않는다. |
| CR 과정 | `named_process_mapping=UNRESOLVED`가 유지된다. S15의 point photon-stock 결과와 저장소 약칭만으로 hard-particle/deposition provider를 확정하지 않는다. |
| 출처 권위 | 원 첨부 4개 파일은 manifest의 bytes/SHA와 일치하며 S01–S17 registry 값도 보존됐다. 외부 archive에 대한 첨부의 주장은 실제 exact evidence intake 전까지 attachment-reported 상태다. |

기존 B1의 native gate는 **HOLD_RUNTIME_ENVIRONMENT**, native parity는 **NOT_RUN**이다. 이번 계획의 채택은 Python benchmark를 native 완료, 실제 결합 EoR history 또는 총 observer τ/visibility로 확장하지 않는다. 근거는 `ACTIVE_DAG.json`의 retained evidence·RUX06/10 residual gates와 `REUSE_AND_GAP_MAP.json`이다.

## 검토 중 발견한 원 지침 보존 사항

원본 handoff는 Verner 단면적의 photon cutoff와 이온화 binding energy를 별도로 보존하도록 명시했다. 새 문서의 일반적인 binding-cutoff 표현만으로는 이 구분이 충분히 고정되지 않아 보완을 요청했다. 최종본은 `DEVELOPMENT_PLAN_KO.md`의 RUX03 문단, handoff 3번, `ACTIVE_DAG.json`의 `RUX03.distinct_threshold_fields`에 `photon_cross_section_cutoff_eV`와 `ionization_binding_energy_eV`를 HI/HeI/HeII별 별도 필드로 두고 source·용도를 각각 보존하며 상호 대체·동일값 가정을 금지한다. 이 한 건은 승인 전에 해결됐다. DAG edge와 실행 상태는 바뀌지 않았다.

## 실행·인계 범위

이번 재편 및 이 검토의 물리·ODE·transport·collision·native build·NCP·새 physical-input archive intake는 각각 **0회**다. 검토에서는 문서/JSON 읽기와 구조·파일 SHA 확인만 수행했으며 프로젝트 solver를 실행하지 않았다. B1 과학 검증을 다시 열지 않았다.

현재 NCP 작업 목록은 빈 배열이고 `NO_CURRENT_HEAVY_WORK`가 유지된다. 다음 packet의 새 ODE/transport 실행도 0회다. 우선 현지에서 입력과 과정 권위를 확인하고, 누락된 필수 입력은 정확한 필드와 한 개의 입력 선정 과제로 반환한다. 이후 실제로 남은 독립 계산이 무겁다는 측정 근거와 해당 과제의 물리 gate가 갖춰졌을 때만 NCP를 구체화한다. 64코어·128GB는 사용자 제공 사양이며 provider attestation으로 기록하지 않고, 실제 affinity·quota·NUMA·가용 RAM을 기준으로 분할과 최소 20% 메모리 여유를 정한다.

## 최종 식별값과 종료

| 검토 대상 | SHA-256 |
|---|---|
| `ACTIVE_DAG.json` | `8005f02399edb089964113280c920d4e7aa36354c8265aded2ae3c3a1fdedb4b` |
| `DEVELOPMENT_PLAN_KO.md` | `952108f54cf9b1f1d7f7c5e1a6110e16dab6352f1396b3c8a258ecef570bc11f` |
| `NCP_LOCAL_CODEX_HANDOFF_KO.md` | `a7e483fb1eaca78323bc4adc4ded445808690331b0ce60a821b0129562531da3` |
| 기존 `../review/DECISION.json` | `d09ab153a7b66220c479a008719d63533e1c6de900d3767547c236ecb486bb36` |

현재 `DAG_STRUCTURE_CHECK.json`은 최종 DAG 39,028 bytes와 위 SHA에 결합돼 있다. 전체 16개 근거 파일 식별값은 별도 판정 JSON에 있다. 검토한 계획의 bytes는 전달 시 유지하고, 게시·백업 영수증은 별도 산출물에 기록한다. 이 상태로 계획 검토를 종료하며 같은 계획에 대한 추가 검토나 B1 재실행, 자동 NCP 착수는 요청하지 않는다.
