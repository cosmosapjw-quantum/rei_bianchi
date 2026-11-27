# E13C10 최초 N32 후보에 대한 독립 검토

역할: 실제 독립 decision reviewer. 후보 구현·이론·제조해 통제 설계에 기여하지 않았다. 고정 소스와 실제 저장된 결과를 읽어 판단했다. 이 기록은 최초 실패를 보존하는 중간 검토이며 후속 후보를 미리 승인하지 않는다.

검토한 초기 source lock은 `95963e73c8764e19b1a88caf0c9721f8d422d0ebc3940bb17e4a5d43d7e06e3a`다. 실제 연구 하네스의 `PROJECT_INSTRUCTIONS.md`, `05_independent_adversarial_review.md`와 코딩 하네스의 `AGENTS.md`, `09_independent_diff_review.md`를 읽었다. 그 다음 E13C10 계약, 작업 계획, 세 후보 코드, Peano 유도, 제조해 통제 설계·소스·영수증, 원본 `directed_interval.py`, `local_enclosure.py`, `path_enclosure.py`, `off_path_worker.py`, `common.py` 및 E13C9 `signed_volterra.py`의 해당 부분을 읽었다.

## 수학·소스 검토

midpoint 오차의 양의 C² Peano kernel과 질량 `Δ³/24`는 올바르다. 원본 Jet2가 정규화 좌표 x의 실제 두 번째 도함수를 반환하므로 구현의 배율 `h/(24 N³)`이 적절하다. 기존 coefficient의 고정 source/mask, 양의 elementary-function domain, exact binary64 입력과 segment 경계를 유지한다. 새 원리를 정당화하는 데 네 번째 도함수가 필요하지 않다.

후보가 첫 forcing 적분에 새 incoming gain을 더하고, 기존 E13C9 prefix와 finite Volterra remainder를 새 carry에서 재계산하는 연결에는 현재까지 이론·구현 blocker를 발견하지 않았다. 기존 fine-grid norm bound는 incoming correction과 무관하므로 해당 입력·N·P·source identity가 보존될 때 재사용할 수 있다. 같은 격자 첫 적분의 포함 정리와 다른 격자 및 stitched path의 raw 포함은 별개다.

## 실제 N32 판정: 입장 실패

`runs/N32/node_000001/RESULT.json` SHA-256은 `2ef13dd726c3555e0e65ec3bc39a2f771d4cebf8ce7510b7ba54d70556b00536`, node 1976 결과는 `b338d2322cc3713b0d01e1fe734e27ee1944d111cf7be8da787d1c6e265b5b98`다. 두 COMPARISON의 정확한 Fraction 폭과 endpoints를 독립 확인했다.

| 경로 | raw 포함 | 폭 비증가 | 모든 구간 overlap | P 새 폭/기존 폭 | H 새 폭/기존 폭 |
|---|---:|---:|---|---:|---:|
| 1 | 12/34 | 16/34 | 참 | 54.8129068182 | 2253.73803943 |
| 1976 | 0/34 | 14/34 | 참 | 1.55711501858 | 1.66913823483 |

node 1의 QN과 QE는 새 폭이 각각 기존의 약 `0.000397607552140`, `0.00239910653790`배여도 기존 구간에 포함되지 않는다. signed curvature가 보존한 중심 이동이 기존 symmetric 구간의 상단에 접근하기 때문이다. 따라서 폭 감소만으로 raw 포함을 선언할 수 없다. 이 실패는 거친 N32의 수치 admission 실패이며, 그 자체로 C² 포함 정리나 모든 제조해 통제가 실패했다는 의미는 아니다.

초기 후보에 대한 결론은 `HOLD_RAW_ADMISSION_FAILED`다. `evidence/FIRST_N32_RAW_ADMISSION_FINDING.json`과 원시 파일을 유지한다. 현재 미실행인 후속 수정의 성공을 추정하지 않는다. 후속 후보는 변경된 source·실행 계약·독립 통제·실제 170개 raw metric과 원래 50% P/H 기준을 다시 만족해야 한다.

## 문서 해석 주의

`evidence/SELECTED_INPUTS.json`의 일부 최상위 provenance와 cache-policy 문장은 E13C9의 historical source-mapping 문맥이다. 후속 E13C10 정책을 설명할 때 이 역사 필드를 현재 실행 지시로 제시하지 않아야 한다. 원본 전체 RESULT SHA는 midpoint를 포함한 전체 saved subtree의 identity를 이미 포괄한다.

독립 검토에서 captured coefficient 평가, 기존 과학 실행 반복, NCP 실행은 0이다. 후속 최종 판정은 아직 `PENDING`이다.
