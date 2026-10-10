# REI PHYS20 research state — completed

PHYS19의 지정 후속 `PHYS20_DIRECTIONAL_BIANCHI_I_ABSORPTION_HEATING_RESPONSE`를 완료했다. 기준 입력 commit은 `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`이다.

최종 단계: bounded theoretical derivation, focused numerical validation, independent final decision 완료.

독립 판정은 **PROMOTE**, 범위는 `PHYS21_SECOND_ORDER_SCALAR_SHEAR_RESPONSE`의 근거로 사용하는 것이다. 검토 대상 보고서 SHA256은 `42d05d3a96a962728d7deac7d380e71914cdbf31b360a1fec13161a913ea974e`다. 판정 상세와 검산의 실행 identity는 `independent/DECISION_REVIEW.json`에 있다.

`PHYSICS_CONTRACT.json`은 검토 당시의 intake 계약을 보존한다. 그 안의 IN_PROGRESS는 intake 시점 기록이다. 최종 상태는 이 파일과 `RESULTS_SUMMARY.json`을 따른다.

## 닫힌 물리 질문

- Physical birth-angle source와 current-angle response의 정확 측도.
- Causal opacity를 포함한 absorption/primary heating의 선형 방향 응답.
- Smooth isotropic continuum과 선형화된 coupled scalar feedback의 조건부 first-variation 상쇄.
- Actual midpoint grid의 일반 전단 leakage, selected xy 대칭, 정확 second/fourth moments.
- Free-photon quadratic benchmark와 source birth-time artifact.
- Threshold line cusp에 의한 무조건 quadratic-onset 주장 반례.

## 남은 질문

다음 물리 연구는 실제 evolving gas에 대한 second-order scalar forcing과 causal feedback의 분리·유도다. 온도·ion fraction·scalar optical depth의 실제 2차 계수와 부호는 아직 계산하지 않았다.

`physical=HOLD`; `[160,161] FAIL`, `tick160`, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED 유지. 이 연구에서 native/gas IVP/이전 proof 실행은 0회다. Production source/default/runtime_returns 변경은 0이다.
