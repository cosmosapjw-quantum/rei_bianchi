# BR04 계약 복원과 가설 심사

## 작업 범위와 재사용

부모 PR #202의 검증된 양의 출생 적분을 그대로 사용한다. 이번 변경은 질량·출생연령 분포 진단과 두 추가 시간–출생 교차 격자다. 105개 부모 crate 파일과 donor 입력을 SHA-256으로 대조한 뒤 복사했다. 원 production owner, source construction, `JointCxSplit`, CX half flow 및 S10 four-corner timestep 제어는 수정하지 않는다. 별도 `br04/Cargo.toml`을 선택할 때만 새 진단 API가 포함된다.

이전 단계의 광자수 수렴 개선과 평균 연령·방향 관측량의 비수축이 출발점이다. 작은 원장 잔차는 보존식의 실행 일관성을 검증한다. 이 잔차를 출생 분포 또는 시간 적분 오차로 재해석하지 않는다.

## 식과 실제 코드 경로

| 계약 | 실제 코드 | 이번 단위의 역할 |
|---|---|---|
| 원 source와 H/He/D opacity | `crate/owner_src/`, `crate/src/full_network.rs` | hash가 같은 부모 입력; 새 물리 입력 없음 |
| 양의 상수-opacity 출생 quadrature | `crate/fitted_birth.rs::rule` | 실제 node/weight를 읽음; 변경 없음 |
| birth time/geometry/Killing path | `crate/ap_midpoint.rs::ApMidpointBridge` | native 경로 재사용, 진단 때문에 cohort를 합치지 않음 |
| CX와 원장·예산 제어 | `crate/ap_budget.rs::attempt`, 기존 네트워크 모듈 | 두 native 실행에서 그대로 사용 |
| 질량과 분포 비교 | `crate/birth_age_certificate.rs::compare_nodes` | emitted/survivor를 각각 own-mass 정규화하고 mass defect 별도 반환 |
| 안정적인 CDF/W1 | 같은 모듈의 `reference_quantile`, `left_area`, `right_area`, `plateau_area` | 비음수 plateau 면적과 작은 광학깊이 극한 |
| scalar 교차 격자 | `crate/examples/birth_age_study.rs` | 실제 노드를 전체 관측 시각 age로 이동·스케일하여 비교 |
| 384 원 source label | 별도 source-age example과 `inputs/AP_FROZEN_SOURCE_INPUTS.csv` | label별 검산 후 혼합분포의 상계 계산 |
| native finite difference | `scripts/analyze_time_age.py` | 원 CSV decimal 문자열로 독립 차분·원장 계산; 물리 상태는 쓰지 않음 |

구현된 각 경로는 실제 실행 결과와 연결된다. CDF와 W1의 전체 native 이력 모니터는 아직 연결하지 않았으며, 이론의 frozen reference 인증을 native 절대오차 인증으로 부르지 않는다.

## 제한된 가설과 제거 검사

| 가설 | 예측 | 제거 검사 | 이번 판정 |
|---|---|---|---|
| H1: 정확한 photon mass가 유한 cohort의 age 분포 오차를 숨긴다 | mass는 맞으나 KS/W1은 유한하고 r에 민감 | 실제 노드의 정확 CDF 적분, 별도 moment 비교 | 직접 지지됨 |
| H2: 시간과 birth 오차가 현재 격자에서 독립 additive power law다 | 같은 r pair의 mixed difference가 작거나 일관된 dominant power를 보임 | 두 완전한 Nt×r rectangle | 연령·q2의 큰 상호작용 때문에 현재 데이터로 채택하지 않음 |
| H3: 비수축은 mean/q2 비율의 정규화만으로 생겼다 | raw age numerator와 E_gamma q2에서는 현상이 사라짐 | primitive numerator도 동일하게 차분 | 증가하는 mixed defect가 남아 단독 설명으로 배제 |
| H4: 아주 작은 tau에서 안정식 평가가 잘못된다 | 투명 극한에서 W1 불연속 | min-subnormal 및 zero-opacity 테스트 | 실제 초기 실패를 발견·수정; failure log 보존 |
| H5: 작은 원장 잔차면 모든 오차가 충분히 작다 | 원장과 분포 지표가 함께 작아짐 | frozen mass-exact rule의 KS/W1 측정 | 성립하지 않음 |
| H6: 새 물리·source identity 변화가 관측차를 일으켰다 | source hash 또는 native config 불일치 | 118 입력 hash, binary identity, CSV configuration 대조 | 변경 없음 확인; 이 두 실행의 설명으로 배제 |

H1과 H2를 주요 검증축으로 삼고, H3과 H4를 독립 대안으로 확인했다. 이 판정은 현재 유한 격자에 대한 것이다. 향후 더 미세한 격자에서 안정적인 점근 영역이 나타날 가능성을 배제하지 않는다.

## 응답 안정성의 남은 의무

동결 문제의 W1/KS는 정해진 연령 measure 사이의 차이를 직접 계산한다. 진화하는 기체에서 birth quadrature 변경은 전자밀도, 온도, species opacity를 다시 바꿀 수 있다. 여기에 이론의 Lipschitz/BV bound를 쓰려면 opacity/source/gas response 및 threshold crossing의 안정성을 별도로 확보해야 한다. 이번 코드는 그 가정을 몰래 추가하지 않는다.

S10 four-corner 제어기의 동일성은 이번 연구에서 계산한 사후 time–birth mixed difference와 구별한다. 사후 진단을 계산했다는 사실은 원 제어기에 새 error estimator를 연결했다는 뜻이 아니다.
