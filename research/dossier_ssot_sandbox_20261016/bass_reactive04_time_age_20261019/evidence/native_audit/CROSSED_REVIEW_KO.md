# BR04 independent crossed native review

## 판정과 입력

**CROSSED_FINITE_GRID_DIFFERENCES_MEASURED / PASS_SCOPED.** 추가 N16r4와 N64r4 이력은 합계 80개 accepted macrostep을 완료했다. 기존 7개 이력의 검증된 raw bytes를 재사용해 2개 완전한 time–birth rectangle을 구성했다. 최종 시각은 모두 8e12 s이고 SIGNED_MINUS, donor grid 121, 원 spectrum, opacity panel 4, CX rtol=1e-12 및 atol=1e-14를 고정했다.

새 자료의 CSV SHA, receipt 행수와 최종 행, stderr, 명령 및 모든 시간 endpoint가 일치했다. 입력 파일은 감사 중 byte 단위로 유지됐다.

| 새 사례 | Accepted rows | 실측 wall (s) | CSV SHA-256 |
|---|---:|---:|---|
| ap_n16_r4 | 16 | 21.288939389 | `70f5c1a66598cba6de3486b8bc871c38bd013f636cb982aa6261dfafb948d185` |
| ap_n64_r4 | 64 | 182.382421414 | `4e2a2735b01c6545ee260a5f54bbd96bf75a4c44d677041fd9d8c89593f594f4` |

두 사례의 wall 합은 203.671360803 s이다. 개별 wall 합이며 병렬 campaign 경과시간이나 CPU time으로 바꾸어 읽지 않는다.

## 독립 원장과 양성성

내부 maxN/maxE를 oracle로 사용하지 않고 primitive 에너지 열로 photon + gas thermal + gas binding + escaped + signed CMB를 합산해 initial + source + signed geometry work와 비교했다. 광자수는 surviving + absorbed − source, species 사건수는 HI + HeI + HeII + DI − total absorbed를 계산했다.

| 새 80개 행에서의 최대 상대 잔차 | 값 |
|---|---:|
| number_relative | 1.498944591397518e-14 |
| energy_relative | 1.023410791803022e-15 |
| species_relative | 3.523160968073022e-16 |

수출된 DII population, 네 photoabsorption 사건수, 광자수 및 양의 에너지 저장 항은 모두 비음수다. Age moment support·variance 및 에너지 가중 P2의 범위도 통과했다. 전체 13-species population vector는 CSV에 없으므로 그 전체 벡터의 비음수성을 이 감사에서 직접 검증한 것으로 확대하지 않는다. 원장 잔차는 원장 일관성의 근거이고 시간·birth 수렴의 증거는 아래 실제 차분으로 따로 평가한다.

## Fixed-r 시간열

아래 두 차수는 동일 N16/32/64 삼중 격자에서 계산했다. r2의 네 격자 중 더 미세한 N32/64/128 차수와 혼동하지 않는다.

| 관측량 | r2 형식 p (N16/32/64) | r4 형식 p (N16/32/64) | r4 Δ16→32 | r4 Δ32→64 |
|---|---:|---:|---:|---:|
| photons_com3 | 1.00564147 | 1.00542858 | -4.548991137e-13 | -2.265953167e-13 |
| mean_age_s | -1.37680866 | 0.49561136 | -6.717569802e+5 | -4.764510638e+5 |
| second_age_s2 | -1.30775864 | 0.13498148 | -5.388072717e+16 | -4.906818278e+16 |
| q2 | -1.51257206 | 0.05921942 | -2.409204301e-12 | -2.312314003e-12 |
| DI | 0.65651320 | 0.65651318 | 1.578632263e-10 | 1.001499681e-10 |
| T_K | 1.81875395 | 1.81873632 | -1.589455587e-4 | -4.505616380e-5 |
| gas_thermal_com3 | 1.82079224 | 1.82077443 | -1.237161857e-27 | -3.502021455e-28 |
| thermal_change_com3 | 1.81559901 | 1.81558147 | -1.272976893e-27 | -3.616396484e-28 |
| geom_work | 1.48086601 | 1.48111051 | 6.992643694e-29 | 2.504855688e-29 |

r4에서 mean age, second moment 및 q2의 시간 차분 크기가 감소하는 양상이 관측됐다. 해당 형식 차수는 약 0.496, 0.135, 0.059이므로 이 격자는 이들 관측량의 2차 시간 수렴을 승인하는 근거가 되지 않는다. 광자수의 형식 차수는 약 1.005, 열·온도의 차수는 약 1.82로 관측량마다 다르다. DI의 r4 시간 차수는 약 0.657이다.

## Mixed difference

D_tr = [F(2N,2r)−F(N,2r)]−[F(2N,r)−F(N,r)]를 r=2에서 계산했다. 단위는 원래 관측량의 단위다. 마지막 열은 N32→64 rectangle의 D_tr를 그 rectangle의 r4 시간 차분으로 나눈 signed 비다.

| 관측량 | D16,32 | D32,64 | D32,64 / Δ_t(r4) |
|---|---:|---:|---:|
| photons_com3 | 3.089728800e-16 | 1.204482455e-16 | -5.31556641e-4 |
| mean_age_s | 2.688387544e+5 | 1.966212806e+6 | -4.12678857e+0 |
| second_age_s2 | 9.036097716e+16 | 3.080117324e+17 | -6.27721906e+0 |
| q2 | 3.685457597e-12 | 1.507686898e-11 | -6.52025156e+0 |
| DI | -1.732658800e-18 | 2.761989000e-19 | 2.75785310e-9 |
| T_K | -6.621100000e-10 | -7.385100000e-10 | 1.63908761e-5 |
| gas_thermal_com3 | -5.272200000e-33 | -5.813900000e-33 | 1.66015545e-5 |
| thermal_change_com3 | -5.285212000e-33 | -5.897689000e-33 | 1.63081925e-5 |
| geom_work | -5.263653000e-33 | -6.131307000e-33 | -2.44776856e-4 |

두 번째 rectangle의 mean-age 및 q2 혼합 차분 크기는 해당 r4 시간 차분보다 각각 약 4.13배와 6.52배 크다. Birth 해상도 변화가 시간 차분에 미치는 영향을 무시하는 분리는 이 관측량에서 뒷받침되지 않는다. 두 rectangle 사이의 mixed 차분은 mean age와 q2에서 증가했다. 따라서 양의 h 차수 하나가 지배하는 mixed error 점근 구간을 이 두 rectangle로 확인하지 못했다.

이 증가 양상은 정규화 전의 Σ(N age)와 E_gamma*q2에도 있다. 해당 혼합 항의 형식 h 차수는 각각 약 −2.866과 −2.031로, mean age 및 q2의 약 −2.871과 −2.032에 가깝다. 이는 비율을 취하는 단계만의 효과로 설명할 수 있는 관측이 아니다. 어느 연산 또는 panel 전환이 주도하는지는 추가 오차 분해의 입력으로 남는다.

DI의 두 mixed 차분은 부호가 바뀌어 형식 차수를 부여하지 않았다. 온도와 gas thermal의 mixed 효과는 전체 관측량에 대해 약 7e-14로 작다. 내부 CX/roundoff 오차가 그 작은 차분보다 작은지 별도 교정하지 않았으므로 이 수로 지배 물리·수치 차수를 추론하지 않는다.

## 식별 범위와 다음 입력

F=F_star+A h^p+B epsilon^q+C h^p epsilon^q+R, epsilon=1/r를 가정하면 D_tr는 C h^p epsilon^q(2^(-p)−1)(2^(-q)−1)+Delta_t Delta_r R이다. 작은 D_tr는 mixed sensitivity가 작다는 자료를 주지만 순수 시간·birth 항 A와 B를 결정하지 않는다. 실제 birth panel은 tau=kappa*h에 따라 바뀌므로 epsilon은 명목 parameter다.

다음 가장 작은 입력은 N16r8 또는 N64r8 하나로, 두 r pair의 mixed sensitivity를 비교할 수 있다. N128r4는 더 미세한 시간열을 연장한다. 현재 결과는 fixed-r4 age/angular 시간 차분의 감소를 관측했고, 동시에 이를 2차 수렴으로 승인하기에는 해상도 결합이 남아 있음을 수치로 특정했다. LONGSPAN_SOLUTION과 전체 time–birth–spectrum–angle 수렴 상태는 이 scoped 결과와 별도로 유지한다.

전 공통 시각의 차분은 `crossed/MIXED_DIFFERENCES.csv`, 모든 입력 identity·전량·비율·형식 차수는 `crossed/TIME_AGE_ANALYSIS.json`에 보존했다. 실제 raw native 실행은 부모 연구자가 수행했으며 이 독립 Python 분석은 새 native 이력을 실행하지 않았다.
