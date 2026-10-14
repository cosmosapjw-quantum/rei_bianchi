# 실제 이온화 이력의 유한 구간 Thomson 관측량

목표는 완료된 F08 S0 이력의 `n_e`를 BASS 수신 API에 실제로 전달하고, 이후 그 수신 결과로부터 FLRW–Bianchi I 차이와 오차의 적용 범위를 계산하는 것이다. 새 IGM의 source/transport owner 작업과 독립적이다.

## 정의와 단위

공급된 값은 같은 물질 frame의 proper electron density이다. 입력 cm⁻³에서 m⁻³로 정확히 10⁶을 곱한다. 표본마다 `D_gas_normal_observer=1`인지 검사한다. 정상 관측자 clock `t`[s]에서

\[
q(t)=c\sigma_T n_e(t)D(t),\qquad
\tau(t)=T_{\rm tail}+\int_t^{t_f}q(s)ds,\qquad S(t)=e^{-\tau(t)}.
\]

기존 BASS 상수 `c=299792458 m/s`, `sigma_T=6.6524587e-29 m²`를 그대로 사용한다. 상수 재추정이나 새 유한온도 보정을 하지 않는다. proper density에 `a⁻³`을 또 곱하지 않는다. `D`도 다시 곱하지 않는다. `D=1`인 동질계의 동일 normal-time 끝점을 비교하므로 여기서 얻는 차이는 물질 이력 차이이며 방향별 관측 redshift 면의 차이가 아니다.

## 실제 수신과 보간

각 source endpoint의 `n_e`로부터 기존 `ElectronState`와 scattering API의 q를 계산한다. 조성 분율이 없는 집계 density 입력에는 `ElectronState(ne,0,1,0,0)`를 사용해 저장된 집계 density를 전달한다. 이는 종 조성을 추정하거나 순수 수소 시나리오로 바꾸는 것이 아니다.

표본 사이에 endpoint 선형 보간을 명시하고, cell rate는 `(q_i+q_{i+1})/2`로 둔다. 이 rate로 native `integrate_clock_visibility(NormalSeconds)`를 실행하면 endpoint optical depth와 cell probability는 그 선형 보간의 적분과 정확히 일치한다(산술 오차 제외). 내부 시각의 rate/visibility peak까지 원래 연속해와 동일하다는 주장은 하지 않는다.

\[
 d_i=\frac{q_i+q_{i+1}}2\Delta t_i,\quad
 P_i=e^{-\tau_{i+1}}(1-e^{-d_i}),\quad
 \sum_iP_i=e^{-T_{\rm tail}}-e^{-\tau(t_0)}.
\]

`P_i/Δt_i`는 cell 평균 visibility이다. 유한 구간의 확률을 1로 재정규화하지 않는다.

## tail의 결정과 미결정

공급자는 observer tail을 제공하지 않았다. 본 실행의 `tail=0`은 **지정한 유한 구간의 diagnostic**이다. 실제 우주에서 그 이후의 opacity가 0이라는 가정이나 검증이 아니다. 별도 `tail=0.1`은 API stress control이며 관측값이 아니다. 동일한 비음수 공통 tail `T`를 덧붙이면 τ 차이는 불변이고 survival/cell-mass 차이는 `exp(-T)`로 배율 변환된다. 서로 다른 미지 tail은 차이의 부호도 바꿀 수 있다.

## 조건부 box를 전파하는 두 번째 루프

공급된 endpoint box `l_i <= n_i <= u_i`가 동시에 유효하다는 조건에서 양의 quadrature weight 때문에

\[
 L_j=k\sum_{i\ge j}\Delta t_i(l_i+l_{i+1})/2,
 \quad U_j=k\sum_{i\ge j}\Delta t_i(u_i+u_{i+1})/2,
 \quad k=c\sigma_T10^6.
\]

따라서 Δτ(BI−FLRW)의 조건부 구간은 `[L_BI−U_F, U_BI−L_F]`. Box의 출처는 실제 binary stage density 및 gas fraction boxes이며 연속 density/물리 불확실성이나 전체 시간 적분 global certificate가 아니다. 로컬 implicit root의 조건부 box를 독립적인 global trajectory enclosure로 승격하지 않는다. 오차에는 native arithmetic, endpoint box, 이력 해상도 변화, 보간/continuum, 원자 데이터/물리 모델을 분리해 둔다. T0/T1/T2 차이와 경험적 비율은 diagnostic이며 rigorous continuum bound를 대체하지 않는다.

`T_tail in [a,b]`가 독립적으로 주어지면 survival은 `[exp(-(b+U)), exp(-(a+L))]`, cell mass는 `[exp(-(b+U_right))*(1-exp(-d_lo)), exp(-(a+L_right))*(1-exp(-d_hi))]`로 안전하게 감쌀 수 있다. 같은 endpoint를 공유하는 상관을 버린 구간이므로 보수적이다. 미지 tail을 임의 오차 막대로 숫자화하지 않는다.

## 근거 상태

- 일반 opacity 정의: NASA LAMBDA의 reionization optical-depth 설명과 일치. https://lambda.gsfc.nasa.gov/resources/graphic_history/taureionzation.html (2026-10-07 읽음).
- source/API 계약: 고정 Git source와 입력 manifest가 authority. 문헌은 이 시나리오의 physical admission 근거가 아니다.
- 식의 선형 구간 전파/공통 tail 배율: 본 작업에서 유도; 별도 reviewer가 검토.
- 수치/구현: Loop1/Loop2 실행 결과가 연결될 때만 PASS를 부여.
- CLASS manual 직접 본문 요청은 502 실패; 검색 snippet은 핵심 근거로 사용하지 않음.
