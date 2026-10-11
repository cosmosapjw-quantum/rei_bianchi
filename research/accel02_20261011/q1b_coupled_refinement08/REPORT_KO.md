# Coupled source-entry 시간 진단

독립 판정 `PASS_COUPLED_SOURCE_ENTRY_TIME_DIAGNOSTIC_SCOPED`. 1-step endpoint와 source-only 적분을 재사용하고,2/4분할의6개 coupled substep을 새로 실행했다. 실제 gas/photon state는 substep 사이에 전달하고 old-photon radiation work를 새 state에서 다시 계산했다. Source 재평가0,1-step 재실행0이다.

267검사 PASS. Primary temporal 최대1.0354965394892139e-7은2e-6 기준 이내이고 combined-energy ledger 최대4.682563613663012e-17이다. Gas/photon/escape/CMB/work 회계는 최종 동일 gas stage에서 누적했다.

채널 상대 시간오차는 해결되지 않았다. HI/HeI의 흡수와 열은 약60%→33%,HeII는77.7%→44% 차이를 보인다. Affected-state 기준 최대3.708972917225926e-16이 local2e-7 screen 아래인 것과 채널 상대수렴은 다른 주장이다. Combined numerical-plus-model uncertainty의10% 미만이라고 판단한 결과가 아니다.

이번 단위는 단일 birth-cell의r=0 조건부 진단이다. Full UVB,CR-first,nonzero-shear history 또는 global admission은 HOLD다. 다음에는 기존 계약을 한 번 읽어 재사용 가능한 full-field/CR 입력과 실제 필요한 모델·오차예산 선택을 구분한다.
