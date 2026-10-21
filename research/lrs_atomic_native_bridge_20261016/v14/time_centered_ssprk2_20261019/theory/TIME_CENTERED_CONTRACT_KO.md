# V14 후속: 닫힌 모멘트의 시간 중심화와 기체 결합

작성일: 2026-10-19. 이 문서는 root가 정한 이론·판정 계약이다. 독립 LRS opt-in 연구이며 production v3/rux와 연결하지 않는다. 기존 실행 84이력, 제조 76문제, Python57 검증은 재사용 근거로만 둔다.

## 1. 해결할 구체적 문제

이전 projection 진단은 고정 기체에서 매 스텝 두 모멘트로 스펙트럼을 다시 복원한 뒤 노드별 정확 지수 감쇠를 적용했다. 복원 R, 모멘트 A, 선형 노드 감쇠 생성자 L에 대해 Phi_h=A exp(hL)R이며, 매끄러운 동일 support branch에서

    Phi_h - Phi_(h/2) o Phi_(h/2)
      = (h^2/4) A L (I - R' A) L R + O(h^3).

따라서 개별 지수의 정확성이 닫힌 모멘트 ODE의 정확한 시간 진화를 뜻하지 않는다. 이 O(h^2) 국소 결함을 줄이는 작업이 이번 변경의 목적이다. 에너지 bin closure 자체와 물리적 원자율은 그대로 둔다.

## 2. 실제 native 노드에서 forward Euler

기존 positive reconstruction과 Verner 단면적을 사용한다. node l의 수 f_l은 /H, reference energy q_l, 물리적 에너지 E_l=r_l q_l이다. 세 흡수종 j에 대해

    kappa_j,l = c n_j sigma_j(E_l),  kappa_l=sum_j kappa_j,l.
    f_l^FE = (1-h kappa_l) f_l,
    P_j = h sum_l kappa_j,l f_l,
    B_photo = sum_j chi_j P_j,
    Q_photo = h sum_(j,l) (E_l-chi_j) kappa_j,l f_l.

광속 c와 원자율은 native 값을 사용한다. h는 초, kappa는 s^-1다. 실제 사용 노드에서 h max(kappa)<=1을 만족해야 한다. 위반은 AXBI_SSP_CFL이며 음수 제거, clipping, 자동 rate 완화는 하지 않는다.

같은 양의 노드 가중치를 N, U_ref, P, B, Q 모두에 사용하면 고정 geometry에서 N0-NFE=sum P, Uphysical0-UphysicalFE=B_photo+Q_photo가 성립한다. 실제 quadrature 적합 잔차와 binary64 반올림은 따로 기록한다. h=0 또는 흡수종이 없는 cell은 원 상태 identity를 보존한다. Delta support는 U_ref=qN의 정확한 표현을 유지한다.

## 3. 새로운 광자 연산

    M*  = FE_h(M0; gbar)
    M** = FE_h(M*; gbar),  반드시 M*를 다시 prepare
    M1  = (M0+M**)/2
    (P,B,Q)1 = [(P,B,Q)FE0 + (P,B,Q)FE1]/2.

이는 SSPRK(2,2)의 실제 forward-Euler 조합이다. 기존 지수 map을 이 식에 넣는 방식은 사용하지 않는다. 고정 gas의 닫힌 모멘트 RHS F에 대해 M1=M0+hF+(h^2/2)F'F+O(h^3)이다. 예측은 local full-versus-two-halves O(h^3), 고정 총 시간의 global refinement O(h^2)다.

고정 support의 {N>=0, lo N<=U_ref<=hi N}는 convex cone다. 두 FE stage의 CFL이 성립하면 각각의 노드 measure와 최종 convex combination의 모멘트가 이 cone에 속한다. 이는 광자 stage의 조건부 결과다.

Delta의 증폭식은 1-tau+tau^2/2다. 지수 exact-semigroup와 ulp 단위 일치는 이번 방법의 기준이 아니다. Exp(-tau)와의 차이는 tau^3/6-tau^4/24+O(tau^5)이며 고정 총 시간에서는 유한한 2차 오차가 기대된다.

## 4. 네 기체 unknown의 공통 midpoint 결합

g=(x_HII,y_HeII,z_HeIII,w_eV/H), C(g)는 native source-free CI/RR/DR/CE/FF/signed-CMB, Q(M,g)는 광자 사건·열의 gas RHS다. Newton trial g1마다 gbar=(g0+g1)/2를 만들고 두 광자 FE stage 모두 같은 gbar를 사용한다.

    M* = M0+h F(M0,gbar)
    M1 = M0+h/2 [F(M0,gbar)+F(M*,gbar)]
    g1-g0 = h C(gbar)+h/2 [Q(M0,gbar)+Q(M*,gbar)].

H=C+Q라 두면, 매끄러운 physical solution branch에서

    M1 = M0+h F0+h^2/2 (F_M F0+F_g H0)+O(h^3)
    g1 = g0+h H0+h^2/2 [(C_g+Q_g)H0+Q_M F0]+O(h^3).

두 식은 결합 ODE의 Taylor 전개와 일치한다. 특히 F_g H와 Q_M F의 혼합항을 포함한다. endpoint gas만 넣거나 old gas만 쓰면 일반적으로 이 혼합항의 계수가 틀린다. Wolfram의 실제 형식 함수 전개에서 h^2 잔차 {0,0}을 얻었다. P,Q를 미정 함수로 사용한 warning은 원 출력과 함께 보존했다. 이 검산은 native 실행이나 전체 시간 정확도의 증거를 대신하지 않는다.

기체는 기존 4변수 Newton/line-search/domain 검사를 쓴다. 평균 AbsorptionResult를 add_absorption_rhs에 한 번 전달한다. 온도는 w와 fractions에서 기존 EOS로 재구성한다. 기체의 양수성은 해의 admissible domain과 nonlinear solve 성공에 의존하며 광자 SSP 정리에서 자동으로 나오지 않는다.

## 5. 사건과 전체 회계

Y=.2454/[4(1-.2454)], 모든 사건은 total-H 기준이다. e=x+Y(y+2z), B=chi_H x+Y[chi_HeI y+(chi_HeI+chi_HeII)z]. 원시 P/C/R/D로 species, electron, binding 변화를 각각 재구성한다.

    Delta(w+B)+E_escape+W_gas-E_CMB = Q_photo+P_binding.
    Delta(N_photon)+P_total+Delta(N_boundary)-Delta(N_source) = 0.
    Delta(U_photon)+Delta(W_photon)+Delta(U_boundary)-Delta(U_source)
      +Q_photo+P_binding = 0.

초기 photon seed를 source ledger에 기록한 출력에서는 N_initial/U_initial을 다시 빼지 않도록 delta convention을 명시한다. 새 CSV는 실제 initial/final inventory와 boundary photon N/U를 함께 기록해 위 분리 회계를 재구성할 수 있게 한다. 기존 CSV의 누락 필드에 관한 과거 주장은 소급해서 바꾸지 않는다.

## 6. 실행·판정 범위

1. 같은 고정 기체/MD14 broad 및 delta60에서 새 transport local/global 진단. 기존 지수 결과는 재사용한다.
2. 양의 MD14 초기 photon과 evolving gas의 fixed-geometry 이력. 초기 packet은 z20에서 dt_seed=1e16 s의 source 적분으로 만들되 이를 지난 우주론 시간으로 해석하지 않는다.
3. GL2 physical births의 짧은 source-on, positive-seed source-disabled 대조. 기존 FLRW scope, log-midpoint geometry, 실제 birth 위치와 source weights를 유지한다.

실행 예산과 정확한 설정은 기록된 contract/command/receipt에 둔다. 원 default/adaptive/checkpoint/MD14/Verner/Grackle/EOS 본문을 바꾸지 않는다. 첫 진단은 별도 child module과 이름이 명시된 opt-in API다. Newton residual에 들어간 두 stage CFL을 만족하지 못하면 실제 실패로 보존하고 root가 다음 유한한 실행을 결정한다.

판정은 고정 support의 매끄러운 닫힌 모멘트 ODE, 유한 nonstiff 구간, 충분한 nonlinear solve의 조건부 2차 consistency와 실제 관측값으로 나눈다. source-on 일반 2차, uniform stiff, CaseB, fullEoR, signed Bianchi, 일반 native 4차는 승격하지 않는다. 실제 성공 범위 밖은 HOLD다.

## 7. 실제 외부 근거와 독립 검토

Exa와 SciSpace를 실제로 사용해 SSP/realizability 원문을 확인했다. SSP convex-FE 계수 1의 일반 근거는 Gottlieb, Shu & Tadmor, SIAM Review 43 (2001), 89–112, DOI 10.1137/S003614450036757X, Lemma2.1 및 Prop4.1/Eq4.1이다.

https://math.umd.edu/~tadmor/pub/linear-stability/Gottlieb-Shu-Tadmor.SIREV-01.pdf

새 native 결합 Taylor 전개와 회계는 이 프로젝트에서 직접 유도했으며 논문이 보증한 native 결과로 표현하지 않는다. root와 분리된 두 Astra 계열 subagent가 이론/source 및 실제 raw 결과를 검토한다. 구현은 AGENTS.md에 따라 별도 요청 모델 gpt-6.1-sol coding agent가 수행하며, 요청 모델과 관측 가능한 실행 신원은 구별한다.
