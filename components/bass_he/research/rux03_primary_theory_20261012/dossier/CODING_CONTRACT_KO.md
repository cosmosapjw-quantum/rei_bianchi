# 다음 구현 계약 — HERE_RUX03_PRIMARY_PROVIDER_03

이 계약의 수학적 선행 작업은 `HERE_RUX03_PRIMARY_THEORY_03`이다. 적용 source는
rei_bianchi PR114 `a5c958c414dea41216b445c05f58df837f05cacb`이며, 현재 callsite와
파일 hash는 `../source_map/`에 있다. 다음 코딩 루프에서는 이 계약을 C1 입력으로
사용한다.

## 1. 구현할 결과

현재 conditional 경로의 Case A 사건 provider와 기존 implicit primary가 같은
rate coefficient·포획 운동에너지 모멘트·사건 투영을 사용하도록 연결한다.
기존 광자 소거, H/He의 양성 갱신, 네 기체 변수, 보존형 thermal proposal,
구간 자동미분과 root inclusion을 이 공통 정의 위에 유지한다.

최소 구현 단위는 **공통 계수 → 원시 사건·모멘트 → 기체 잔차**를 ordinary point,
conservative point, endpoint, interval/root 모두에 연결하는 것이다. 현재
caller가 birth를 primary 입력에 이미 합산하는 경우에는 그 소유 구조를 사용한다.
이번 이론의 source-aware 식은 같은 사건 수지를 직접 stage source로 표현할 때의
완성된 계약도 제공한다.

## 2. 공통 provider의 수학적 자료형

| 항목 | 개수·단위 | 정의와 의무 |
|---|---|---|
| CI 계수 beta | 3, cm³/s | 현재 warm fit, candidate T에서 평가 |
| RR 계수 alpha | 3, cm³/s | HII→HI, HeII→HeI, HeIII→HeII |
| DR 계수 delta | 2, cm³/s | 두 채널 모두 HeII→HeI |
| RR kinetic 계수 kappa | 3, erg·cm³/s | rate와 별개의 포획 에너지 모멘트 함수 |
| DR kinetic 계수 zeta | 2, erg·cm³/s | 현재 delta × 고정 captured energy |
| 고정 stage photon 자료 | node별 E, sigma, incoming p와 source | E는 eV, sigma는 cm²; source 소유자는 §5에서 선택 |

각 계수의 point와 interval/Jet 구현은 동일한 고정 상수와 선택된 provider identity를
사용한다. 현재 DR 상수의 binary64 pin을 포함해 실제 기존 식을 보존한 후 변경된
계산 경로를 검증한다. 기존 `Ft03Coefficients`가 제공하는 rate와 moment 정보를
이 공통 계수 객체로 옮길 수 있다. 기존 event-bundle guard에 맞춰
`alpha_i(T)=0 ⇒ kappa_i(T)=0`, `delta_r(T)=0 ⇒ zeta_r(T)=0`도 공통 객체의
허용 조건으로 유지한다. 현재 FT03 식은 이 조건을 만족한다.

개념적 인터페이스는 다음과 같다. 구체적인 Rust 추상화는 기존 crate 구조에 맞춘다.

```text
CaseACoefficients<Scalar>
    beta_ci[3], alpha_rr[3], alpha_dr[2]
    rr_kinetic_coeff[3], dr_kinetic_coeff[2]

coefficients(T: Scalar) -> CaseACoefficients<Scalar>
primitive_events(coefficients, nH, f, fractions, photon_events)
    -> CaseAEventBundle<Scalar>
consume_bundle(bundle) -> species_rhs, thermal_power, escape_power, diagnostics
```

`Scalar`의 point/Jet 평가가 같은 수학적 표현을 사용한다. 계수 자체를 제공하므로
population=0인 point 경계에서 `event/(population*n_e)` 같은 복원 나눗셈이
필요하지 않다. 진단 summary는 사건을 다시 RHS에 더하는 입력으로 사용하지 않는다.

## 3. 실제로 함께 바꿀 callsite

| 파일·경로 | 구현 의무 | 대응 식 |
|---|---|---|
| `axisym_conditional.rs::ThermalEventProvider`, `CaseAEventBundle` | 현재 proper-cgs event/moment 경계를 공통 계수·투영에 대응; 기존 실제 소비와 단위 유지 | SHARED §1, §4 |
| `coupled_primary.rs::raw`, `endpoint` | 집계된 FT03 RHS와 새 사건을 중복 더하지 않고 공통 평가의 species/thermal/escape를 소비 | 식 (2)–(6), (9) |
| `primary_stage_step` | 같은 계수의 I_i,r_i로 기존 H/He proposal; 새 candidate에서 endpoint 재평가 | 식 (19)–(23) |
| `primary_stage_step_conservative` | 같은 사건의 absorption·escape·binding으로 보존형 proposal, 기존 compensation 유지 | 식 (15)–(17) |
| `interval_rhs`, `ft03_interval_rhs` | 같은 선택과 계수 식으로 value/gradient/Hessian; 광자 분모의 gas 의존성 포함 | 식 (24)–(30) |
| `primary_stage_root` | canonical thermal residual의 새 interval field에서 centre, derivative, preconditioner, inclusion 계산 | 식 (8), §3.2, §5.2 |
| `paired_runtime.rs::endpoint` | conservative point와 ordinary-point-based root에 같은 provider를 전달; photon birth/transport의 기존 stage 입력 유지 | SOURCE_MAP §5, 아래 §5 |

현재 root centre는 ordinary point에서 얻고, paired caller는 conservative point와
root를 함께 사용한다. 따라서 두 point 변형과 interval 중 일부만 provider를
바꾸는 것으로 이 계약을 완료하지 않는다.

## 4. 잔차·야코비안·구간의 공통 정의

기본 상태는 `y=(x_HII,x_HeII,x_HeIII,w_eV/H)`다. 기본 잔차는

\[
F=(v-v^0-hG,\;w-w^0-h[Q-2Hw]).
\]

같은 사건으로 만든 보존형 energy row는

\[
F_E=(1+2hH)w-w^0+\Delta B+hQ_{esc}-\sum_qE_qA_q,
\quad F_E=F_w+\nabla B\cdot F_v.
\]

이 항등식은 gas root 밖에서도 성립한다. 모든 point/interval 평가에 같은 사건을
사용하면 새 provider에서도 같은 식이 성립한다. endpoint acceptance에는 고정된
canonical residual과 원래 프로젝트의 물리·수치 guard를 사용한다.

구간 계약은 전체 입력 box에서 coefficient value와 필요한 미분이 포함되는 것이다.
구간 사칙연산·초월함수·chain rule로 구성한 동일 expression graph가 이 포함관계를
전체 residual에 전달한다. 현재 positive point domain과 strictly interior interval
domain의 차이를 유지한다. 현재 30000..110000 K box qualification을 적용한다.

RR kinetic moment Hessian을 alpha의 미분으로 만들면 alpha''' 항이 생긴다.
현재처럼 kappa의 명시적 analytic expression을 Jet으로 평가하면 그 미분 의존성이
직접 전달된다. f64로 한 번 계산한 moment를 Jet 상수로 감싸는 경로는 채택할
미분 계약과 다르므로 이 연결 지점을 실제 derivative witness로 확인한다.

## 5. photon source와 geometry의 정확한 소유

소스 aware 광자 식은 다음과 같다.

\[
p_q^+=\frac{p_q^-+h s_q^{(H)}}{1+h\lambda_q(y)},\quad
\lambda_q=c n_H\sum_a\ell_a(y)\sigma_{aq}.
\]

동일한 stage source를 입력에 미리 더해 놓는 표현도 정확히 같다.

\[
\Phi(p^-+h s^{(H)},0)=\Phi(p^-,s^{(H)}).
\]

현재 `paired_runtime.rs`는 source birth를 photon 입력에 더한 다음 primary를
호출한다. 그 경로에서는 primary의 별도 source를 0으로 두면 된다. 직접 source를
받는 새 adapter에서는 birth를 합산하기 전 incoming photon과 동일 시점 source를
전달한다. **birth는 이 두 표현 중 한 곳에서 합산한다.** parent photon box에도
같은 선택을 반영한다.

reference/proper/per-H 변환은

\[
N=Vn_\gamma,\quad n_{H,ref}=Vn_H,\quad
p=N/n_{H,ref},\quad s^{(H)}=S_{ref}/n_{H,ref}=s_{proper}/n_H.
\]

기존 HM12 node source에는 quadrature weight와 angular Jacobian이 들어 있다.
기존 callback이 반환한 `S_ref`를 사용한 뒤 위 변환을 한 번 적용한다.

endpoint node energy가 달라지는 history에 이 BE stage를 넣을 때는, root가 얻은
photon 수와 prescribed energy의 정확한 product rule을 사용한다. eV/reference
단위의 photon geometry work는

\[
W_{\gamma,geom}=-\sum_q(E_q^+-E_q^-)N_q^-.
\]

여기서 `N^-`는 물리 history의 birth 전 incoming reference photon이다. transport
후에 source를 합산한 primary 입력은 별도로 구분한다. 기존 continuous RHS나
그 DOP853 history에 이 BE 전용 correction을 그대로 더하지 않는다. 이 식은
선택한 endpoint-energy BE stage의 history ledger를 구성하는 식이다.

## 6. 최소 판별 검증

| 검증 대상 | 구체적인 판별 내용 | 근거 |
|---|---|---|
| 기본 provider 일치 | 같은 입력에서 기존 FT03 event/moment 및 residual과 공통 평가를 비교; source revision을 고정 | 기존 source/evidence + 식 (19)–(20) |
| 한 채널의 단일 소비 | HeIII RR alpha에 rho, kappa에 epsilon_eV eta rho를 주입하고 실제 residual shift를 비교 | 식 (31)–(33) |
| 도함수 일관성 | constant perturbation의 population/전자수 미분은 식 (34)–(35), rho(T)=rho_star(T/T_star)²의 thermal w/ww 미분은 식 (35a)–(35b)에 비교 | exact symbolic witnesses |
| 광자 feedback | source가 0/양수인 경우 원잔차 복원과 gas derivative를 확인; 투명 경계와 HeI/HeII 경쟁을 포함 | PHOTON 식 (22),(30)–(41) |
| thermal 잔차 동치 | root 밖 candidate에서도 F_E−F_w−b·F_v=0; photon, escape, source 회계까지 합친 식 확인 | SHARED 식 (11)–(15) |
| 실제 point/root 연결 | ordinary/conservative point와 paired caller가 같은 provider를 사용하고 현재 root gate가 새 field에서 평가됨을 확인 | 실제 source callsite |
| history 연결을 구현할 경우 | birth 한 번 합산과 finite-step photon energy product rule; source 없는 투명 redshift 예제 | PHOTON 식 (60)–(64) |

한 채널 witness의 정확한 기대값은, 같은 candidate에서

\[
r_\delta=n_H f b[x+f(a+2b)]\rho,
\quad \delta F=h r_\delta(0,-1/f,1/f,\eta),
\]

\[
\delta F^E=h r_\delta(0,-1/f,1/f,\chi_{HeII}+\eta).
\]

보존량만으로는 사건의 두 번 소비를 검출하지 못하므로 이 알려진 단일 변화량을
실제 경로에 대조한다. 허용오차는 기존 관련 시험의 기준과 새 구현의 수치적
민감성을 읽고 C1에서 고정한다. 이 theory unit에서 새 실행 tolerance를 임의로
부여하지 않았다.

운동에너지 계수의 온도 미분은 `rho(T)=rho_star(T/T_star)^2`와 동일한
`delta kappa=epsilon_eV eta rho(T)`를 쓰는 companion으로 확인한다. 양의 내부
candidate에서 thermal residual의 w 미분은 `2h eta r_delta/w`, ww 미분은
`2h eta r_delta/w^2`다. constant perturbation만으로는 이 온도 의존성의 누락을
판별하지 못하므로 두 witness의 역할을 각각 유지한다.

수정한 경로와 그 의존성의 검증이 닫히면 다음 owner 연결로 진행한다. 직전
EVENT_BRIDGE_02의 176개 native tests와 11-history/B1 계열 캠페인은 변경 없는
결과의 재사용 근거다. 새 native 실행이 필요하면 source/build identity가 연결된
실행을 실제로 수행하고 결과를 별도로 기록한다.

## 7. 완료 및 후속 의존성

이 구현 단위의 채택 결과는 동일 provider가 실제 implicit point와 root/interval에서
소비된다는 source·실행 근거다. 이어서 RUX02의 physical source 입력과 RUX03의
rate-domain 조건을 맞춰 RUX04 scenario lock을 완성한다. 원래의

`RUX02 + RUX03 → RUX04 → RUX05`

연결을 유지한다. 이번 이론 유도는 그 첫 구현 단위에 필요한 식, 미분, source 소유와
판별 witness를 완성한 선행 결과다.
