# 보존 F08 끝점 비교 — 저장 자료 후처리

분류: **SYNTHETIC / PRESCRIBED_DISCRETE**. 이 보고서는 기존에 기록된 결과를 읽어 끝점 차이를 표시한 saved-data postprocess이다. 이전 ODE를 실행하거나 새 물리 계산을 승인하지 않았다.

원자료는 끝점 15행이며 모두 t = 1e13 s이다. 7개 이름별 해상도에서 BI − FLRW를 비교한다. BI는 이 합성·처방 이산 모형 안의 counterfactual shear 비교이며 물리적 EoR, QV, 하늘 신호, 연속체 오차 상계 또는 새 scientific PASS를 뜻하지 않는다.

상속한 campaign status: `PRESCRIBED_DISCRETE_PAIRED_HISTORY_INDEPENDENT_PASS`. 상속한 scientific_admission: `HOLD`. 새 후처리 status: `SAVED_DATA_POSTPROCESS_COMPLETE`; 새로운 scientific admission은 발급하지 않는다.

## 끝점 차이

아래 값은 저장된 BI 끝점에서 같은 해상도의 FLRW 끝점을 뺀 값이다. 그림의 가로축은 이름별 범주이며 시간축이 아니다. 끝점만으로 중간 시간 이력을 복원하지 않는다. 오차막대는 붙이지 않았다.

| 해상도 | ΔxHII | ΔT (K) | ΔGamma_HI (s^-1) | Δphoton_u (eV/H) |
|---|---:|---:|---:|---:|
| T0 | 2.85204465933e-07 | -0.00213078732486 | 8.52016099135e-19 | -4.96915592441e-06 |
| T1 | 2.85133106237e-07 | -0.00213062355033 | 8.52064089494e-19 | -4.96776077163e-06 |
| T2 | 2.85097355501e-07 | -0.00213053957123 | 8.5208788843e-19 | -4.96706198749e-06 |
| S0 | 2.72130656676e-07 | -0.00201601273875 | 8.01608224488e-19 | -4.74069695955e-06 |
| S2 | 2.92732505125e-07 | -0.00219139747787 | 8.78786470398e-19 | -5.09817932448e-06 |
| A0 | 2.87454196002e-07 | -0.00215506071982 | 8.64299652724e-19 | -4.99780638052e-06 |
| A2 | 2.84681731411e-07 | -0.00212526314863 | 8.49231368232e-19 | -4.96280683238e-06 |

![범주별 끝점 반응](endpoint_response.png)

## 기존 ledger의 별도 기록

다음 표는 원래 ledger에 기록된 T0 BI − FLRW의 final_difference와 max_abs를 그대로 구분해 옮겼다. max_abs는 기존 matched endpoint 집합에서 기록한 최대 절대 차이로, 이 15행 CSV로 재계산한 값이 아니다. final_difference와 max_abs는 서로 대체할 수 없고 물리적 불확실성 또는 오차막대가 아니다.

| 관측량 | recorded final_difference | recorded max_abs |
|---|---:|---:|
| x_HII | 2.85204465933e-07 | 2.85204465933e-07 |
| temperature_K | -0.00213078732486 | 0.00401473085367 |
| gamma_HI_per_s | 8.52016099135e-19 | 9.37270011733e-18 |
| photon_u_ev_per_h | -4.96915592441e-06 | 4.96915592441e-06 |

T0_EPS_HALF도 저장된 끝점 비교에 한해 사용했다. (EPS_HALF − FLRW)/(BI − FLRW) 비율은 아래의 범위 제한 진단이며 약한 전단 정리나 보편적 스케일링 증명이 아니다.

| 관측량 | half/full 끝점 비율 |
|---|---:|
| x_HII | 0.249997155487 |
| temperature_K | 0.249994027724 |
| gamma_HI_per_s | 0.249992714481 |
| photon_u_ev_per_h | 0.249997447355 |

## 출처와 범위

원본 receipt와 private raw 경로는 복사하지 않았다. 기존 source pin과 범위를 사용하며, 아래 SHA256은 이번에 읽은 공개 저장 파일의 byte identity만 기록한다.

| 원본 경로 | SHA256 |
|---|---|
| `runs/rei_fastest_v1/paired/paired_history.csv` | `1eb412dd5dcaabfabe4480f4eb53c2461431cd7098883c4043a2daa1daf6dec4` |
| `runs/rei_fastest_v1/paired/campaign_summary.json` | `47483f9adf3a1952c974433a10c4fa3fc2d55452a624c43bce5d9a53bf3c7015` |
| `runs/rei_fastest_v1/paired/difference_error_ledger.json` | `4cc864a984b90c13feb69c82e6e0f939199ead1f90356d39d77abf15429546a3` |

상속한 ledger 설명: Measured discrete differences at matched physical endpoints; no rigorous continuum/model/fit/observational uncertainty claim

physical_fit_error: `NOT_MEASURED`; continuum_error_bound: `NOT_ESTABLISHED`; QV: `NOT_EVALUABLE`. 원래 허용 범위를 확대하지 않는다.
