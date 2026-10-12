# HERE_RUX03_EVENT_BRIDGE_02: 실제 Case A 사건 소비

이 변경은 PR97의 기존 `SourceBoundConditional` 생산 경로를 확장한다.
그 경로는 이미 FT03 RR/CI/DR, 임의 개수 광자 node의 PI와 AXI 우변을
결합하고 있었다. 이번에 새로 만든 것은 **개별 사건과 운동에너지 항을
묶은 소유권 있는 bundle을 실제 우변에서 소비하는 경계**와 그 진단이다.
PR101의 clean-build receipt 수정을 포함한 PR97 commit
`1400093cdd121d8e6adb51ffeb360102a48653bf`가 정확한 기준 소스다.

## 실제 호출 관계

`source_bound_interval.py::ProductionInterval.rhs`는 기존 `RHS` 프로토콜을
그대로 호출한다. `ConditionalSession` → `SourceBoundConditional.evaluate`
→ `evaluate_detailed` → 고정된 FT03 provider → `CaseAEventBundle.into_ledger`
→ `axisym_coupled_derivative`가 실제 경로다. `EVENTS`는 같은 detailed
evaluation에서 실제 소비된 사건과 source를 반환하는 읽기 전용 진단이다.
계산을 마친 뒤 진단용 원자율을 따로 다시 평가하지 않는다.

Public 생산 API는 고정된 FT03/Case A 정책을 유지한다. 내부 test provider는
한 사건의 차분을 검사하는 목적으로만 쓰이며 다른 물리 provider의 admission이
아니다. bundle을 `self`로 소비한 뒤 반환하는 summary는 다시 소비할 수 있는
source bundle이 아니다. 반환된 진단 수치를 수정해도 생산 우변은 바뀌지 않는다.

## 사건식과 단위

세 edge의 순 사건률은 다음과 같다.

\[
J_a=C_a-R_a+P_a-\delta_{a,\mathrm{HeI}}(D_1+D_2).
\]

종별 source의 순서는 `(HI,HII,HeI,HeII,HeIII,e)`이며

\[
s=(-J_H,J_H,-J_{\mathrm{HeI}},
J_{\mathrm{HeI}}-J_{\mathrm{HeII}},J_{\mathrm{HeII}},
J_H+J_{\mathrm{HeI}}+J_{\mathrm{HeII}}).
\]

따라서 H와 He 원자핵 수가 각각 보존되고 전자 source는 이온 전하 source와
같다. 모든 원시 사건률은 proper cm^-3 s^-1이다. `Ft03Rhs`에서 이미 계산한
RR captured kinetic power `K_RR,a`와 DR captured resonance power `K_DR,k`를
노출한다. 재결합 계수로부터 임의의 평균 광자 에너지를 가정하지 않는다.

\[
\dot u_{\rm th}=
-\sum_a(C_a\chi_a+K_{\rm RR,a})-\sum_k K_{\rm DR,k}
+\sum_{i,a}P_{ia}(E_i-\chi_a),
\]

\[
\dot u_{\rm bind}=\sum_aJ_a\chi_a,\qquad
\dot u_{\rm esc}=\sum_a(R_a\chi_a+K_{\rm RR,a})
+\sum_k(D_k\chi_{\rm HeI}+K_{\rm DR,k}).
\]

위 식의 에너지는 동일한 단위로 환산해 사용한다. 코드의 power 단위는
erg cm^-3 s^-1이다. node별 광자 흡수 사건 `P_ia`가 동일 node의 광자수 손실,
종별 이온화, 결합 에너지 증가, 광전가열에 모두 들어간다. 외부 방출 power와
광자 reservoir는 기존 단계 입력을 사용한다. AXI 경계의 SI 변환은 수밀도에
10^6, 에너지 밀도와 power에 0.1이다. reference photon은 N=a_rel^3 n이다.

Case A escape에서는 재결합의 탈출 **에너지**만 기록한다. 방출 광자수와
스펙트럼은 미정이다. Optional CR/RCT/HH는 OFF이며, T/에너지 domain,
HM12 입력, 팽창·shear work, 시간 적분법과 기존 tolerance는 바꾸지 않는다.

## EVENTS 프로토콜

`BIND`와 stage 입력 형식은 기존 `RHS`와 같다. 새 `EVENTS` 결과는 37개의
유한한 수이고 source는 모두 proper cgs 단위이다. 아래 번호는 0부터 시작한다.

| 인덱스 | 값 |
|---|---|
| 0–2 | CI 사건률: H, HeI, HeII edge |
| 3–5 | RR 사건률: 동일 edge의 역방향 |
| 6–7 | HeII→HeI DR 두 항의 사건률 |
| 8–10 | 실제 node에서 합산한 PI 사건률 |
| 11–13 | RR captured kinetic power |
| 14–15 | DR captured resonance power |
| 16–18 | 종별 PI heat power |
| 19–21 | 종별 흡수 광자 energy power |
| 22–26 | HI, HII, HeI, HeII, HeIII source |
| 27 | 전자 source |
| 28 | 외부 공급−흡수를 합친 광자수 source |
| 29–33 | photon, thermal, binding, escape, external power |
| 34 | 단계 온도 K |
| 35–36 | 기존 광자수/에너지 정규화 residual |

## 의미 있는 검증

보존적인 bundle을 두 번 더해도 보존식 residual은 0일 수 있다. 그래서
`injected_heiii_rr_event_is_consumed_once_by_actual_axi_rhs`는 내부 provider에서
HeIII RR를 +δ, captured kinetic power를 +δ·7 eV만큼 바꾼다. 이는 제조된
test source다. 실제 AXI source와 최종 우변에서 HeII +δ, HeIII −δ,
전자 −δ, binding −χ_HeII δ, heat −7 eV·δ, escape +(χ_HeII+7 eV)δ가
정확히 한 번 나타나야 한다. 광자와 외부 공급은 같아야 한다.

별도 Decimal60 원시 사건 기준은 저장된 실제 warm 초기 입력에서 작성했다.
거의 평형인 net source의 상대오차 대신 개별 사건과 gross-event scale을
사용한다. 초기/비초기 실제 stage probe 이후 변경된 binary로 기존 생산
runner의 선택 구간만 실행한다. source·binary·실행·검증 결과는 각각의
evidence receipt를 따른다. 이 문서 자체는 실행 성공 증거가 아니다.

## 검증 범위

이 변경이 닫는 것은 선택된 조건부 생산 경로의 사건 bundle 소비다. 전체
RUX03 owner 의무, diffuse radiation, FullCoupledOts, cold history 또는
연속계 오차 인증은 이 변경으로 완료 처리하지 않는다. 이전 결과의 동일한
부분은 재사용하고, 실제 바뀐 호출 경로에 필요한 검사만 수행한다.
