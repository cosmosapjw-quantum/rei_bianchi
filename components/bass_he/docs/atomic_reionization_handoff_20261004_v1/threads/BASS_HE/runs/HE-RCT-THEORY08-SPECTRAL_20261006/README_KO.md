# HE-RCT-THEORY08: 광자 1차 모멘트의 사영 spectral operator

판정은 CONDITIONAL_SPECTRAL_OPERATOR_AND_FINITE_CHECKS_PASS__PHYSICAL_MOMENTS_OPEN이다. THEORY07 이후의 미해결 이론을 진행했다. 실제 He V_i/V_f/d 또는 산란해를 수치입력으로 채택하지 않았고 source mean은 null이다. 새 native/history/consumer/root mutation0이다.

## 새 형식적 결과

최종 He+(1s)+H+ threshold를0,입사 energy E>0,Q>0,S=E+Q로 둔다. H_i=T+Q+V_i,H_f=T+V_f는 self-adjoint real BO nuclear operators다. D_a는 전하를 포함한 전이 dipole(C m),q_a=D_a chi이다. P_E=P_c*1_[0,S](H_f)는 선택된 해리 continuum과 positive photon support의 reducing projector다.

E1 spontaneous single-photon,leading radiative probability,recoil-free COM에서

    sigma_m = [V/(3*pi*epsilon0*hbar^4*c^3*v_i)]
              *sum_a <q_a|P_E*(S-H_f)^(m+3)|q_a>.
    photon mean at E = M4/M3, M_n=sum_a<q_a|P_E*(S-H_f)^n|q_a>.

V는 relative incoming box normalization이며 flux=v_i/V다. photon quantization volume은 별도이고 이미 소거됐다. first energy moment가 quartic인 이유는 photon phase space의 epsilon^3이다. M4>=0,M4<=S*M3,M4^2<=M3*M5가 따른다.

energy-normalized radial u의 continuum overlap M_JJ'=integral u_f*d*u_i dR로 쓰면

    sigma_m = 2*pi/(3*epsilon0*hbar^3*c^3*k_i^2)
              *sum_(J,J'=J+-1)w_JJ' integral_0^S (S-e)^(m+3)*|M_JJ'|^2 de.

Sigma->Sigma에서 w=J 또는J+1이며 추가 final DOS/k_f/4pi를 중복 곱하지 않는다. 출사 He+와H+는 repulsive Coulomb 경계와 energy normalization이 필요하다. free Bessel final wave는 일반적으로 맞지 않는다. 실제 Coulomb scattering을 이번에 실행한 것은 아니다.

## Local gap 근사의 누락항과 bound

Delta=Q+V_i-V_f,K=S-H_f에 대해 K D chi=Delta D chi-[T,D]chi. Radial J->J'에서는 hbar^2/(2mu)*(d''u+2d'u') 외에 hbar^2*[J(J+1)-J'(J'+1)]du/(2mu R^2)가 남는다. radial d가 상수라도 rotation term은 사라지지 않는다.

s_n=D*Delta^n*chi,r_n=K^n*q-s_n이면 r_(n+1)=K*r_n-[T,D*Delta^n]chi다. 실제 entrance residual rho=(H_i-S)chi를 사용하면 -D*Delta^n*rho가 추가된다. |M_n-L_n|은 projected commutator norm의 S-weighted sum과 (I-P_E) leakage norm의 합으로 제한된다. detailed Eq25가 실제 평가할 error contract다. local A*Delta를 정확값이라 하지 않으며 actual norm은 미평가다.

모든 final eigenvalue가 허용구간 안인 합성2x2 model에서 true(M3,M4)=(175,625),local=(172,580),mean relative error=12/215≈5.58%다. 다른 finite model에서는 full completeness로 projector를 지우면 mean이 available energy4를 넘고, positive-photon cutoff를 지우면 cubic rate=-44가 된다. actual He spectrum의 숫자나 bound state 존재를 주장하는 반례가 아니다.

## 선택적 recoil 모델과 검산

NR pair COM recoil만 넣으면 s=epsilon+epsilon^2/(2M_f*c^2)이며 spectral weight는 epsilon_r(s)^(m+3)/(1+epsilon_r(s)/(M_f*c^2))다. 분모는 delta-function Jacobian이며 energy만 치환해서는 안 된다. full relativistic model 또는 실제 recoil 평균은 아니다.

실제 verifier1회,exit0: SymPy39groups/72scalar,양의 continuum측도4개 x50/80자리 xmoment0/1/2,70자리3x3spectral-route 대조,비영/비정상 반례4개. quadrature 최대상대잔차1.59878115888e-51,finite matrix2.158642519e-71. tests-after이며 independent scientific review/interval/actual He evaluation은 NOT_RUN이다. 기존 suites는 재실행하지 않았다.

원전: West–Lane–Cohen PRA26,3164(1982),DOI10.1103/PhysRevA.26.3164의pages2-3 optical/spectrum-bypass 내용과 Hilborn arXivphysics/0202029 SecVI SI E1 conventions. 본 projector/defect theorem을 원전의 제공 결과처럼 인용하지 않는다. 원PDF는 배포하지 않는다.

다음은 HE-RCT-THEORY09_PROJECTED_CONTINUUM_REALIZATION이다. 실제 source-bound potentials/dipole와 continuum normalization을 결속해 sigma0/sigma1을 같은 projected kernel에서 계산한다. 물리값이나 현행 addon 채택을 이 형식적 결과에서 자동 승인하지 않는다. source moments null,baseline OFF,physical HOLD,HE-F2globalfalse,HE-F3/F09blocked,Eq55NOT_RUN,legacy PARKED_OPEN 유지.

Git은 본 요약,입력/계약/반환/검증과 실제 executed verifier의 byte identity와 명령 로그를 보존한다. 전체29식 유도,실행한 verifier 원문과 개별 결과/로그는 BASS_HE_RCT_THEORY08_SPECTRAL_20261006_v1.zip에 있다. 정확 archive/cloud identity는 DELIVERY_RECEIPT.json을 따른다.
