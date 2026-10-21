# V15 native stage mapping and independent algorithm review

작성: 2026-10-19 UTC. 검토자: /root/dropbox_v15_intake, parent와 별도 source/theory 검토.
상태: SOURCE_MAPPING_AND_CONDITIONAL_ORDER_DERIVATION_COMPLETE.
이 문서는 구현자가 만든 새 결과를 아직 판정하지 않는다. 현재 native 파일을 읽고 다음 구현의 수학적 계약을 정한다.

## 1. 실제 입력과 구현 위치

V14 baseline은 source/results commit 806ad09be146486a492f62393e0a2c578330acf5,
최종 전달 ddfa6f5210ed6e17b54c0757fc23ed40d16f18c6에 대응한다.
원 native anchor는 f6046418d15e2f44418dfbc04ca67999f389a7df이며 V13 parent는
7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e다.

읽은 native 경로는
/workspace/scratch/6af5e9e6c737/v15_work/native_owner/rust/rei_microphysics/이며,
원 inputs는 v14_work/REI_LRS_V14_PROJECTION_DIAGNOSTIC_20261019_20261019T075954Z_staging/input/의
v12/native_owner, v13, v14 복원 사슬이다.
이 검토는 native 코드 실행이나 source 변경을 하지 않았다.

| 실제 파일/함수 | 현재 기능과 필요한 연결 |
|---|---|
| src/axbi_covariant_transport.rs: AbsorptionNode, PreparedAbsorption | nodes와 template은 private. node는 cell, q, number, sigma[3], excess_ev[3]를 가진다. |
| PreparedAbsorption::evaluate_with_rule | 고정 스펙트럼에 BackwardEuler 또는 Exponential 감쇠. 같은 node에서 잔존 N/U, photo rate, 사건, binding, heat를 계산한다. |
| CovariantTransport::prepare / prepare_legacy_serial / prepare_cell | 현재 N/U/support와 GeometrySnapshot으로 positive reconstruction 및 threshold-cut quadrature를 만든다. |
| cell_quadrature | 수·1차모멘트 적합을 검증한다. 제한은 64 epsilon N 및 128 epsilon energy_scale. node positions와 panel 수는 상태·threshold geometry에 의존한다. |
| CovariantTransport::validate_state | occupied cell의 lo N <= U <= hi N, empty exact zero, endpoint delta의 U==q N를 검증한다. |
| src/axbi_driver.rs: ResidualContext::evaluate_source_clocks | unknown=[x_HII,x_HeII,x_HeIII,w_eV/H]와 old gas로 gas midpoint를 구성하고 opacity를 평가한다. |
| compose_source_free_rhs | AllMid에서 CI/RR/DR/CE/FF/CMB를 midpoint로 결합한다. 모든 사건·열·escape·electron 항을 일관되게 재구성한다. |
| add_absorption_rhs | 이미 적분된 AbsorptionResult 사건·열을 dt와 nH로 rate로 변환해 gas RHS에 한 번만 더한다. |
| Driver::chemical_stage | gas 4변수 Newton, 기존 jacobian_columns 및 solve4, line search, event/gas ledgers와 last_clock_rhs commit의 소유자. 처음의 prepared spectrum은 Newton 동안 고정된다. |
| Driver::tentative | geometry to log-midpoint -> source placement -> chemical_stage -> geometry to end. opt-in clock의 dt는 Delta ln(a)/H_mid. |
| Driver::set_source_clocks | q_ref==0, same_h==false, BASS background absent를 강제한다. old initial energy를 새 시작 상태에 맞춘다. |
| src/axbi_physical_birth.rs: Driver::fixed_step_physical_birth | axbi_driver의 CHILD module. private tentative/inject/validate/fields에 접근하며 GL2 또는 midpoint birth에서 source를 실제 주입한다. |
| BirthMicroSegment::from_rhs | 반드시 해당 segment RHS와 segment dt를 쓴다. macro dt로 마지막 RHS만 재적분하면 회계가 잘못된다. |

공개 evaluate_with_rule(..., dt=0)는 instantaneous global photo.gamma/heat rate를 제공하지만,
absorbed_per_h는 0이며 per-cell dN/dt, dU_ref/dt를 반환하지 않는다.
따라서 dt=0 공개 API만으로 photon moment RK를 구현하는 것은 충분하지 않다.

## 2. 최소 transport 확장

기존 scalar PhotonAttenuation을 재해석하지 않고 opt-in 전용 child module 또는 같은 파일의 새 method를 권한다.
부모 transport의 private node 접근을 유지하면서 다음 두 연산을 추가하면 된다.

1. prepared node들로 instantaneous moment/event RHS 또는 nodewise forward-Euler packet을 계산한다.
2. stage-1 PhotonState를 CovariantTransport::prepare로 다시 복원하고 SSPRK(2,2)를 완성한다.

기존 prepare/positive_reconstruct/AtomicProvider::reference/cross_section,
HHeModel의 c_cm_s와 threshold_ev를 그대로 쓴다.
현재 node의 sigma 양성 여부와 excess_ev 정의를 재사용하며 threshold를 새 상수로 덮어쓰지 않는다.

각 cell/ray k의 q에 대해 현재 ray scale을 r_k라 하면 E=r_k q다. N과 U_ref는 total-H 기준.
s^-1 차원의 opacity를

  kappa_j(q,g)=c_cm_s n_j(g) sigma_j(E),  kappa=sum_j kappa_j

로 정의한다. prepared weight f_l은 각 node의 photon number/H다.
Instantaneous quadrature computational form은

  F_N,k = - sum_(l in k) kappa_l f_l
  F_Uref,k = - sum_(l in k) q_l kappa_l f_l
  p_j = sum_l kappa_(j,l) f_l
  b = sum_j chi_j p_j
  qheat = sum_(j,l) (E_l-chi_j) kappa_(j,l) f_l.

F_N와 p_j의 단위는 /H/s, F_Uref는 eV_ref/H/s, b와 qheat는 eV/H/s다.
광속을 reduced speed로 바꾸지 않는다.

FE packet은 f_l^FE=(1-h kappa_l)f_l이며, event_j=h sum_l kappa_(j,l)f_l.
허용 조건은 실제로 사용되는 두 stage 모두에서 h max_l(kappa_l)<=1이다.
동일한 node weight로 물리적 photon energy loss, binding, heat를 계산하면

  N_old-N_FE=sum_j P_j,
  Uphysical_old-Uphysical_FE=B_photo+Q_photo

가 exact arithmetic에서 성립한다.
현재 quadrature-fit/float 잔차는 별도로 계측한다.

SSPRK(2,2):

  M* = FE_h(M0;gbar)
  M** = FE_h(M*;gbar), with a fresh prepare(M*)
  M1 = 0.5 M0 + 0.5 M**
  (P,B,Q)_1 = 0.5(P,B,Q)_FE0 + 0.5(P,B,Q)_FE1.

두 FE packet은 모두 h 길이이며 마지막 1/2 weighting을 적용한다.
P/B/Q에 h/2를 한 번 더 곱하지 않는다.
대수적으로 M1=M0+h/2 [F(M0,gbar)+F(M*,gbar)]다.

광자 realizability 집합 {N>=0, lo N<=U_ref<=hi N}은 고정 support에서 convex cone다.
두 FE node measure가 nonnegative이면 그 moments와 마지막 convex combination도 이 cone에 있다.
이는 광자 stage에 대한 조건부 보존 결과다.
gas implicit midpoint의 positivity는 endpoint domain validation과 nonlinear solve 성공에 의존한다.

부동소수점 구현에서는 baseline의 compensated accumulation과 nearest-support endpoint anchoring을
재사용하는 편이 타당하다. 특히 delta endpoint의 U==q N, empty-state의 N=U=lo=hi=0을 지킨다.
단순 clamp로 음수를 지우면 사건 수와 에너지를 바꾸므로 사용하지 않는다.
h=0 또는 opacity=0에서 identity를 명시적으로 반환하면 reconstruction-fit roundoff의 불필요한
zero-step 누적을 방지한다. 일반 h에서 reconstruction defects를 order signal과 분리해 기록한다.

## 3. 기존 midpoint gas와의 2차 결합

가장 작은 계산구조 변경은 gas 4변수 Newton을 그대로 유지하는 것이다.
g=(x,y,z,w_eV/H), M=(N_k,U_ref,k), R(M)는 기존 closure,
F(M,g)는 위 moment RHS, C(g)는 photo를 제외한 AllMid native microphysics,
Q(M,g)는 photo의 gas increment vector라 하자.

각 Newton trial g1에서

  gbar=(g0+g1)/2
  M*=M0+h F(M0,gbar)
  M1=M0+h/2 [F(M0,gbar)+F(M*,gbar)]
  0=g1-g0-h C(gbar)-h/2 [Q(M0,gbar)+Q(M*,gbar)]

를 평가한다.
photo 사건과 heat를 묶은 AbsorptionResult를 기존 add_absorption_rhs에 전달하면 마지막 residual을
현재 fraction_dt와 w_dt 형태로 쓸 수 있다.
그 결과는 매 residual마다 stage-1 reconstruction이 필요하지만 unknown 차원은 4를 유지한다.

C,Q,F가 매끄럽고 고정 geometry/support의 interior branch에 있으며 g1-g0=O(h)인
물리적 해 branch를 Newton이 충분히 정확히 구했다고 가정한다.
H0=C(g0)+Q(M0,g0), F0=F(M0,g0)로 두면

  gbar=g0+(h/2)H0+O(h^2)
  M*=M0+h F0+O(h^2)
  M1=M0+h F0+(h^2/2)(F_M F0+F_g H0)+O(h^3).

gas residual의 전개는

  g1=g0+h H0+(h^2/2)[(C_g+Q_g)H0+Q_M F0]+O(h^3).

이는 결합 ODE의 두 Taylor 전개와 일치한다.
F_g H0 및 Q_M F0의 mixed terms를 명시적으로 포함하므로 고정 gas 진단에서만 성립하는
2차 주장이 아니다. 다만 성립 조건은 smooth coefficients, finite nonstiff interval,
정확한 stage solution/closure 평가의 범위다.

endpoint gas를 모든 photon stage에 넣으면 F_g H0 항의 계수가 일반적으로 1이 되어 이 전개와
맞지 않는다. 두 photon stage를 old gas로만 평가하면 그 항을 빠뜨린다.
따라서 기존 opacity_midpoint=true와 NativeClockMode::AllMid 설정을 유지해야 한다.

온도는 위 Newton unknown에 넣지 않는다. 기존 native EOS로 w와 fractions에서 재구성한다.
IgmGasState::new 및 eos는 w>0과 species simplex를 확인한다.
T derivative 진단에서 endpoint gas를 사용하는 부분은 실제 w/fraction integration과 구별한다.

## 4. 결합 사건·에너지 불변량

Y=nHe/nH이고 photo event rates/H를 p_H,p_1,p_2라 하면

  Q_species=(p_H,(p_1-p_2)/Y,p_2/Y),
  e=x+Y(y+2z),
  e_dot_photo=p_H+p_1+p_2.

B(g)=chi_H x+Y[chi_1 y+(chi_1+chi_2)z]이므로 B_dot_photo=b.
위 photon/gas stage weights가 같으면 Delta B=P_binding,
Delta w_photo=Q_heat와 photon number loss=sum P가 일치한다.

source-free microphysics는 기존 native 사건 회계로
Delta(w+B)+E_escape-E_CMB=0를 이루며 geometry split의 W_gas/W_photon은 기존 owner가 기록한다.
공통 가중치의 photo 결합은
Delta(w+B)+E_escape+W_gas-E_CMB=Q_photoheat+P_binding
항등식을 그대로 보존한다.

SSP step 내부의 두 FE event를 합해서 사용하는 경우 최종 factor 1/2를 빠뜨리거나,
gas rate를 final photons/end-gas로 다시 계산하는 경우 이 항등식이 깨진다.
새 코드의 결과는 원시 P/C/R/D와 binding/heat/escape/CMB/work를 통해 확인해야 한다.

## 5. 실제 default를 유지하는 연결 방식

최소 변경 후보는 다음과 같다.

- transport parent의 새 child module: 노드 접근과 SSP packet 구현. 기존 BE/Exponential method 본문은 유지.
- Driver의 별도 opt-in selector와 context 정보: 현재 transport 및 frozen GeometrySnapshot이 새 residual에 전달되어 stage-1 prepare가 가능해야 한다.
- evaluate_source_clocks의 opt-in branch만 새 AbsorptionResult를 사용하고, 기본 분기는 기존 메서드를 그대로 호출.
- 기존 chemical_stage의 Newton, ledger, counters, transaction 범위를 재사용.
- 기존 V14 physical_birth child adapter의 source-free tentative가 이 selector를 계승하면 birth 코드 자체를 다시 쓸 필요가 없다.
- 선택기는 default None/false이며 set_source_clocks가 허용하는 q_ref=0 등 기존 범위를 계승한다.

PhotonAttenuation에 RK 변형을 넣는 방식은 scalar attenuation_factors에 새로운 의미를 주기 쉬우므로
권장하지 않는다. 기존 SourceClockConfig struct literal을 모두 바꾸는 방식보다 별도 opt-in
method/field가 영향 범위를 명료하게 만든다.
구현자가 다른 방식을 택할 경우 실제 default 경로 보존과 API semantic distinction을 확인하면 된다.

## 6. 이번에 진척을 만드는 유한한 대조 행렬

이 항목은 제안이며 실제 실행이나 통과 결과가 아니다.
기존 62행 및 84-history campaign의 반복으로 세지 않는다.

1. 고정 매질의 새 solver 대조: 같은 MD14 broad와 delta60를 사용하되 새 SSP operator의
   local full-versus-two-halves O(h^3), fixed-total-time global self-difference O(h^2)를 검사.
   두 stage의 실제 max tau<=1을 만족하는 h를 선택하고 이를 CSV에 기록.
   legacy 결과의 동일 input 행은 기존 원시 CSV와 identity를 연결해 재사용한다.
   delta에서는 exp(-kappa t) 정확해와 비교 가능하다. 새 RK2 delta 결과는 기존 exponential처럼
   exact semigroup일 필요가 없으며 통상 유한한 2차 오차를 가진다.

2. 양의 초기 photon + evolving gas: 기존 [0.075,0.12,0.03], T=15000K와 native MD14
   positive packet을 사용하고 source는 Disabled. 기존 빈 source_off가 검사하지 않았던
   F_g H 및 Q_M F 혼합항을 실측한다. baseline packet보다 충분히 큰 photon population이
   gas 변화에 필요한 경우 injector의 동일 spectrum을 명시한 emitted dt/total N로 초기화한다.
   이 초기화 선택과 initial energy/source ledger를 분명히 보존한다.

3. 실제 source-on: V14 physical GL2 birth + 새 staged inner solver와 기존 physical GL2의
   짧은 matched endpoint refinement. 먼저 하나의 cells 설정에서 충분한 4개 이상 N을 사용.
   가장 작은 N에서 각 source-free segment의 h max tau를 확인하고 typed restriction failure를
   그대로 보존한다. FE 제한을 넘는 N을 강제로 통과시키지 않는다.
   source-on 초기 빈 cells/threshold crossing의 nonsmooth 여부와 signal floor를 함께 기록한다.

새 고정 매질 local slope≈3와 global≈2는 이번 알고리즘 수정을 구별하는 핵심 관측량이다.
원래 exp-projection의 local≈2/global≈1 지표를 새 알고리즘에서 기대값으로 그대로 쓰면 안 된다.
양의 초기 광자 coupled run에서 photoheat와 species allocation/temperature self-differences를
재구성하여 photon-stage 개선이 gas channel에 전달되는지를 본다.

모든 refinement에서는 actual end a/ln(a), source N/U, P/C/R/D, w,B,e,
CE/RR/DR/FF/CMB/escape/work, photon N 및 물리 U를 기록한다.
tau 실패는 numerical admissibility, Newton 실패는 nonlinear solve, compiler 실패는 environment/
implementation 범주로 분리한다. photon/gas inventory의 source seed 책임을 혼동하지 않는다.

## 7. 유효범위와 종료 판단

위 유도는 closed-moment system의 consistency 개선을 보인다.
spectrum closure 자체의 에너지해상도 오차는 바꾸지 않는다.
기존 계수의 threshold 또는 quadrature branch 변화가 있으면 그 구간의 실제 refinement가
판정을 결정한다. binary64 reconstruction error와 Newton tolerance floor를 차수로 해석하지 않는다.

광자 SSP coefficient는 1이고 h max kappa<=1이라는 제한을 명시적으로 사용한다.
따라서 uniform stiff accuracy, arbitrary step positivity 또는 full EoR 효율은 이 유도에서 나오지 않는다.
기존 제한 때문에 signed Bianchi도 현재 adapter의 대상이 아니다.
실제 변경 코드를 아직 읽지 않은 상태이므로 구현 PASS는 발행하지 않는다.

## 8. 실제 문헌 확인

검색일 2026-10-19. 사용자가 선택한 SciSpace에서 다음 자연어 질문을 실제 검색했다:

"Which primary papers establish second-order strong stability preserving Runge-Kutta time integration as convex combinations of forward Euler steps, and realizability preservation for moment-closure kinetic transport under forward Euler positivity restrictions?"

SciSpace 반환에서 Ketcheson2008 및 SSP survey를 찾고 다음 원문을 직접 열어 읽었다.
검색 초록만으로 이론을 채택하지 않았다.

- D. I. Ketcheson, Highly Efficient Strong Stability-Preserving Runge-Kutta Methods with
  Low-Storage Implementations, SIAM J. Sci. Comput. 30(4), 2113–2136 (2008),
  DOI 10.1137/07070485X.
  원문 https://davidketcheson.info/assets/papers/2008_explicit_ssp.pdf .
  §1은 forward Euler의 convex functional 제약을 SSP timestep 조건으로 전달한다.
  §3.3.1 Eq.(3.8)과 Pseudocode1의 s=2는 위 Heun formula다.
  이 문헌에서 전달한 내용은 시간기법과 해당 FE 전제다.

- S. Gottlieb, D. I. Ketcheson, C.-W. Shu, High Order Strong Stability Preserving Time
  Discretizations, J. Sci. Comput. 38, 251–289 (2009), DOI 10.1007/s10915-008-9239-z.
  저자 원문 https://www.davidketcheson.info/assets/papers/sspreview.pdf .
  §3.1 Eq.(3.1)에 SSPRK(2,2) formula가 명시되어 있고 coefficient=1이다.

- G. Alldredge and F. Schneider, A realizability-preserving discontinuous Galerkin scheme
  for entropy-based moment closures for linear kinetic equations in one space dimension,
  arXiv:1501.03660.
  원문 https://arxiv.org/pdf/1501.03660 .
  §3.2와 §3.4.1/Theorem3.3는 FE cell-mean realizability와 SSP convex stages를 연결한다.
  본 코드에는 spatial DG나 논문의 limiter를 가져오지 않는다.
  고정 support의 두 spectral moment cone에 대해서는 위 §2에서 별도 직접 유도를 제시했다.

이 전개의 SSP 및 convex-cone 원리는 기존 문헌의 것이다.
이번 프로젝트의 연구 기여는 실제 native spectrum 복원 경로와 gas midpoint의
mixed derivative terms, 동일 사건 가중치, 광자 에너지 및 gas binding/heat 회계를 연결한
구체적 구현과 native 수치 결과로 판정한다.

