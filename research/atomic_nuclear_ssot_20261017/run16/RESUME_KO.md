# RUN16 최신 과학 재개 기록

기준: 2026-10-19 UTC/KST. 최종 원격 전달 정보는 `DELIVERY.json`, `RESUME_DELIVERY.json`이 존재하면 함께 읽는다.

## 먼저 선택할 결과

Branch는 `research/rei-run16-gas-path-sensitivity-20261019`, base는 RUN15 최종 `c875005e30d9de1ce7f426898e46fe912068412c`다. 첫 소스 checkpoint는 `2cc5e0862dbe9770ef83c0b2437e27627ec26524`다. Remote HEAD는 시작 시 다시 확인한다.

1. `results/GAS_PATH_RESPONSE.json`의 E16/T32를 현재 fixed-path sensitivity 결과로 쓴다. Core S=`1.1803145305707004e-10 comoving m^-3`, uniform HI elasticity magnitude=`0.9972065222179413`. Standard-PCHIP minus tight-PCHIP relative response=`+5.070228489801907e-7`, tight denominator. 이는 실제 IVP gas-path bound가 아니다.
2. `feedback/prefix_stephalf_execution01/PREFIX_STEP_HALVING.json`이 최신 prefix 결과다. 첫 birth 이전 code-z `[0,0.004989333151072248]`, 원래 gas 5변수만 새로 계산했다. 첫 birth 직전 HI=`0.9000000534472483`, T=`9999.925747777985 K`. Archived-knot PCHIP minus native는 HI 상대 `-1.5712776951781748e-6`, T `+0.04470254583975475 K`.
3. `feedback/execution01/RECORDED_STATE_FEEDBACK.json`은 세 보존 상태의 점 Jacobian/defect다. `results/FEEDBACK_BLOCK_SCALES.json`은 같은 점의 log-norm comparison 척도다. 두 파일을 전 구간 bound로 사용하지 않는다.

코드의 z는 `(X-0.7)/0.0004`이며 cosmological redshift가 아니다. Prefix에는 활성 photon이 없고, 별도 escape/CMB/event ledger도 없다. 이 결과는 full transport restart checkpoint가 아니다.

## 이번에 실제 완료한 계산

새 focused tests 5개 PASS. Response의 세 GL order 계산, native point RHS85회, 짧은 prefix IVP3개(62+62+122=246 RHS)를 완료했다. 합계 native RHS331회. Full transport IVP0, 완료된 M2 standard/tight 재실행0, 과거 test suite 재실행0.

첫 prefix A/B는 4-step grid가 동일했다. 이를 보존하고 C를 8-step으로 추가했다. C/B 공통 sample의 HI 상대차는 float64에서0, T차 최대3.637978807091713e-12K였다. 정확해에 대한 rigorous bound라는 주장은 없다. 모든 코드와 원자료는 완료 상태로 동결됐다.

## 다음 실제 미완료 노드

기존 `P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION` 안의 **첫 birth 이후 gas reconstruction / full-source residual / admissible tube comparison**이 다음이다. 원래 DAG를 교체한 새 DAG가 아니다.

가장 직접적인 다음 bounded unit:

- H/D/He invariant manifold를 지키는 gas reconstruction을 만들고 이번 첫-birth 기체 reference 편향을 초기 오차에 포함한다.
- 같은 경로에서 원래 geometry·birth·threshold partition을 따라 optical depths와 전체 photo absorption/heating을 계산한다.
- `r=hat_g'−F(hat_g)` residual의 시간 구간 상한과 tube의 `mu_inf(A), ||B||, ||C||`를 구성한다. 점의 값을 sup bound로 대체하지 않는다.
- Continuous-source spectral forcing defect와 fixed-support survivor functional bound를 분리해 결합한다.

75.895%의 fixed-path gas sensitivity가 첫 tight checkpoint gap에 놓인다는 결과가 자원 배치의 근거다. C1 knot-preserving bump는 명시적 prescribed-path 진단 가족이며 실제 ODE 해가 아니다.

## 반복 금지 및 기존 미해결 보존

RUN13 M2 standard/tight는 COMPLETE archived6241segments40357dimensions다. checkpoint3071에서 재시작하지 않는다. Original M1/M2 sub-H component 차이약51.99%는 여전히 미수렴 증거다. 전체 survivor tolerance agreement나 작은 conservation residual을 spectral error bound로 바꾸지 않는다.

RUN15 소실 전 네 optical native cases는 기록상 완료됐지만 raw histories/driver bytes가 완전히 회수되지 않았다. Transcript를 원본이나 restart state로 재구성하지 않는다. RUN15 새 quadrature binary의 byte mismatch는 별도 미해결이고, 원래 gas binary SHA는 그대로 유지된다.

Uniform native m4 NOT_RUN, continuous spectral refinement, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8은 유지한다. PR199 실제 최신 파일의 age64 block-max는 이미 COMPLETE/NO_REPEAT이며 여기의 gas bound로 혼합하지 않는다.

## 재현과 전달

`REPRODUCE_KO.md`를 따른다. 원본 입력은 run13/recovered, 상속한 kernel/comparator는 run15, 새 source와 evidence는 run16이다. 사용한 native gas executable SHA256은 `3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`다. 추가분 ZIP의 manifest와 외부 baseline 의존성을 확인한다. 원격 업로드/metadata/다운로드 SHA/과학 재현은 별도 지위다.
