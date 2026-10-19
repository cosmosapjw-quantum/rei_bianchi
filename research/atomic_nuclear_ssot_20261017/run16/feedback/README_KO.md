# RUN16: gas residual과 opacity feedback의 실행 가능한 연결

이 작업은 **기존 RUN13 tight 상태 세 개에서 native gas RHS 85회를 실제
평가**했다. 새 IVP·기존 native 전체 테스트·기존 RUN13 적분 재실행은 모두
0회다. 계산된 국소 Jacobian, 실제 photon forcing과 보간 경로의 point defect를
모두 보존했다.

가장 직접적인 결과는 첫 광자 birth 이전인 `z=0`에서 확인한 중성 H 기울기다.
실제 native RHS의 상대 변화율은 `+1.1919346288534569e-5 / z`인데,
긴 첫 checkpoint 구간을 잇는 PCHIP의 기울기는
`-3.0297124257765243e-4 / z`다. 부호가 반대다. 이는 저장 endpoint가 틀렸다는
뜻이 아니라, 그 endpoint들을 잇는 보간 경로가 native 해로 검증되지 않았다는
구체적인 증거다.

세 평가 시점은 `z=0`, 첫 tight checkpoint인 `z=0.7609039888237062`,
`z=1`이다. 첫 tight checkpoint 이전의 구간이 전체 정규화 시간의 약76.09%를
차지한다. 긴 시간 간격과 survivor 오차 기여도의 크기는 구별해야 하며,
그 기여도는 별도의 RUN16 functional-response 계산으로 평가한다.

| 이번 실행에서 확인한 항목 | 실제 결과 |
|---|---|
| Native gas RHS 호출 | 85회; native 호출시간0.006673초 |
| 전체 진단 시간 | 1.023867초 |
| 원본 source·input·evidence 검증 | 112개를 실행 전후 해시 대조; 변경 없음 |
| gas Jacobian의 두 finite-difference step 비교 | 상대 matrix-norm 차이 최대1.83e-10 |
| analytic photon block과 별도 finite difference 비교 | 최대6.72e-9 |
| 전체 block assembly와 원래 section_rhs 비교 | 절대 차이 최대6.35e-18 |
| native gas Jacobian norm | 약33.6 |
| 같은 Jacobian의 infinity logarithmic norm | 약0.14; 큰 음의 CX 대각 성분 보존 |
| 새 IVP 및 과거 테스트 재실행 | 0회 |

Jacobians의 값은 저장된 시점의 수치 척도다. 구간 전체의 Lipschitz 상수나
stability certificate로 사용하지 않았다. 가장 빠른 gas 고유값은 약
`-16.74 / z`이며, 초기 charge-exchange-only Jacobian도 따로 계산해 출처를
분리했다. Photon opacity의 thermal 직접 미분은 이 prescribed model에서
0이지만, thermal→gas chemistry→neutral density 경로의 feedback은 남는다.

## 실제 다음 미완료 노드

다음 작업은 원본의 finite packet 또는 연속 스펙트럼 source에 대해 **gas
재구성 경로의 전체 residual과 physical tube를 통제하는 것**이다. 실제
수행 가능한 방법은 보존 gas knots로 정한 경로에서 optical depth를 원래
geometry·threshold partition에 따라 다시 quadrature하고, gas RHS residual을
구간별로 계산·포함하는 것이다. 이는 완료된 RUN13 coupled IVP의 재실행을
요구하지 않는다. 다만 quadrature error와 derivative tube enclosure를
인증해야 하므로 이번 point 검사만으로 완료되지는 않는다.

Source 연속화의 gas forcing 오차는 모든 관련 흡수 이벤트와 가열 항을 포함해야
한다. Endpoint에서 소멸한 photon band도 앞선 시간의 gas heating에는 기여할
수 있다. 작은 sub-H survivor 하나의 오차나 작은 ledger residual을 전체
opacity feedback 오차로 승격하지 않는다.

## 파일과 검증 지위

- [원래 native 식에서 유도한 block 구조·오차 부등식·다음 계산](DERIVATION_AND_NEXT_NODE.md):
  `DERIVED`; 조건부 결과의 미충족 전제 명시.
- [새 실행 소스](recorded_state_feedback.py): 원본 소스를 읽기만 하며,
  binary/source/input identity를 확인한 후 실제 gas server를 호출한다.
- [실제 결과 JSON](execution01/RECORDED_STATE_FEEDBACK.json): `NUMERICALLY_CHECKED`.
- [Native 입력·응답 수치 기록](execution01/NATIVE_RHS_VALUE_TRACE.jsonl): 실제85회;
  parsed f64 value 기록이며 원시 wire-byte 기록이라고 주장하지 않는다.
- [다음 노드 입력 계약](NEXT_NODE_INPUT_CONTRACT.json): 필요한 연속 재구성,
  residual envelope, tube, source forcing와 event 정보.
- [실행 영수증](EXECUTION_RECEIPT.json): exact command, 실행환경, 코드·결과 SHA.

원본 gas executable SHA는
`3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`이고,
읽은 clean Git HEAD는 `6405bcba8ec654bf3ab98182be344cd8c3915b97`이다.
이번 native 실행은 RUN15에서 실제 재빌드한 그 바이너리를 사용했다.
원래 standard/tight의 과거 수렴 결과나 전체 테스트 결과를 새 PASS로
재분류하지 않았다.

`P4-S4C-SPECTRAL-EDGE-SUPPORT`의 coupled continuum bound,
between-checkpoint gas tube, spectral forcing error는 여전히 `UNRESOLVED`다.
