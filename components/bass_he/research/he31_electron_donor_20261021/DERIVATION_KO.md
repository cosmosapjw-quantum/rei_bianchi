# HE31 유도와 구현 대응

## 1. 핵 보존, 전자 census, clock

non-tilted homogeneous Bianchi I의 proper volume은 V∝a³이다. H/He 핵 수를
보존하는 prescribed donor에서 N_H=a³n_H, N_He=a³n_He는 상수다. 따라서

\[
 n_e(a)=a^{-3}\{N_H x_{\rm HII}(a)
       +N_{\rm He}[x_{\rm HeII}(a)+2x_{\rm HeIII}(a)]\}.
\]

0≤x_HII≤1, x_HeII≥0, x_HeIII≥0, x_HeII+x_HeIII≤1이면
0≤a³ne≤N_H+2N_He다. log(a)에서 a³ne를 shape-preserving PCHIP로 보간하면
각 구간의 값은 양 끝값 사이에 있으므로 같은 상한과 양성을 보존한다. 이는 입력
knot 사이를 정의하는 명시적 보간 근사다. 원래 화학 ODE의 전역 오차와는 별개다.

η=ln(a/a_ref)에 대해

\[
n_e'+3n_e=a^{-3}\{N_H x_{\rm HII}'
+N_{\rm He}(x_{\rm HeII}'+2x_{\rm HeIII}')\}.
\]

proper ne[cm^-3]에서 GammaT=c_cgs sigmaT_cm² ne는 s^-1이다.
SI에서는 ne[m^-3]=10^6 ne[cm^-3], sigmaT[m²]=10^-4 sigmaT[cm²],
c[m/s]=10^-2 c[cm/s]이므로 같은 rate를 준다.

\[
\tau(a_0,a)=\int_{\ln a_0}^{\ln a}\frac{c\sigma_Tn_e(e^u)}{H_{\rm target}(u)}\,du.
\]

source에서 저장한 tau는 source clock의 적분이다. target Bianchi의 H가 달라지면
같은 ne(a)라도 tau를 새 clock으로 적분한다. 실행기는 원래40 physics state에
tau 한 개를 진단 state로 더하고 `tau'=GammaT/H_target`를 계산한다. 원래 RHS의
첫 성분이 H_ref/H이므로 이 성분을 이용하면 tau를 얻기 위해 FV moments를 두 번
평가할 필요가 없다.

## 2. Thomson angular gain과 species 분리

비상대론적 정지 electron의 elastic unpolarized kernel은
K(n,n')=3[1+(n·n')²]/(16pi)다. axisymmetric 분포에서 방위각을 적분하면

\[
(Gf)(\mu)=\frac38\int_{-1}^{1}
\left[1+\mu^2v^2+\frac12(1-\mu^2)(1-v^2)\right]f(v)\,dv.
\]

Legendre mode에 작용시키면 G P_0=P_0, G P_2=P_2/10이고 그 밖의 mode에는
0이다. 따라서 J_l=<f P_l>에서 collision은

\[
J_0'|_T=0,\quad J_2'|_T=-\frac9{10}\frac{\Gamma_T}{H}J_2,
\quad J_l'|_T=-\frac{\Gamma_T}{H}J_l\ (l\ne0,2).
\]

에너지와 photon-number monopole을 보존한다. collision-only 구간에서는
J_l(a)=J_l(a0)exp[-d_l tau]다. Bianchi Liouville matrix와 damping diagonal은
일반적으로 commute하지 않으므로 실제 결합 궤적에서는 전체 RHS를 적분한다.
마지막 Pi_rad에 단일 exp(-tau)를 곱하는 사후처리는 이 결합 방정식이 아니다.

full polarized Thomson에서는 intensity quadrupole이 polarization을 생성하므로
현재 scalar closure와 별개 state가 필요하다. 이 단위는 기존 D3 unpolarized
closure를 유지한다. photon에는 위 직접항이 있고 neutrino와 massive matter에는
없다. 세 species는 Einstein H와 shear를 통해 간접적으로 상호 작용한다.

## 3. Prepared FV moments

고정 canonical packet의 q_perp², q_parallel²와 normalized weights w를 미리
구성한다. 현재 상태의 A=exp(-2η+2b), B=exp(-2η-4b), C=exp(-3η)에 대해

\[
E_i=\sqrt{m^2+Aq_{\perp,i}^2+Bq_{\parallel,i}^2},\qquad
\rho=C\sum_iw_iE_i,
\]
\[
P_\perp=\frac{CA}{2}\sum_i\frac{w_iq_{\perp,i}^2}{E_i},\qquad
P_\parallel=CB\sum_i\frac{w_iq_{\parallel,i}^2}{E_i}.
\]

이 식은 기존 quadrature의 재배열이다. packet, amplitude, normalization, mass,
Gauss rule은 동일하다. 세 scalar exponential, 한 energy 배열과 한 inverse-energy
배열, 세 weighted reduction으로 평가한다. 고정 weighted momentum도 한 번 준비한다.
batch는 지정 chunk에 한정한다. 얻는 이점은 반복 연산·임시 배열의 제거이며,
NCP 실측 속도 비율은 이번 경량 검증의 주장이 아니다.

η 미분과 b 미분을 직접 적용하면

\[
\partial_\eta\rho=-3(\rho+\bar P),\quad
\partial_b\rho=-6p_m,\quad n(\eta)e^{3\eta}=n(0),
\]

따라서 임의 b(η)에 대해 rho'+3(rho+Pbar)+6b' p_m=0이다.
기존 원본과 몇 상태의 값을 비교하고, 이 derivative identity를 원래 mass-shell
합의 독립 미분으로 확인한다. 변경하지 않은 237개 완료 궤적을 다시 적분하지 않는다.
실제 receiver 범위는 0≤η≤ln7이다. 매우 큰 η의 subnormal 영역에서는 연산 순서에
따라 원본이 먼저 underflow할 수 있다. 독립 검토에서 m/Tref=1e5, η=245의
rho는 원본0, prepared6.217e-320이었다. 이 영역의 상대·bitwise parity는 주장하지 않는다.

## 4. 실제 검산과 문헌

Wolfram Language의 kernel 적분 결과는 gain eigenvalues {1,0,1/10,0,0},
loss {0,1,9/10,1,1}; 전자 dilution 식과 SI/cgs rate의 symbolic residual은 모두0이다.
실제 호출·응답은 evidence/WOLFRAM_ALGEBRA.json에 보존한다.

문헌 탐색에는 Exa와 SciSpace를 실제 사용했다. 원전 연결은 Ma & Bertschinger
(1995), arXiv:astro-ph/9506072; Hu, Scott, Sugiyama & White (1995),
arXiv:astro-ph/9505043; Friedrich et al.(2012), arXiv:1201.0602다.
마지막 문헌의 H/He 결합과 OTS 구분을 source별 closure 유지에 사용한다.
새 외부 atomic rate나 full polarization 알고리즘을 이 비교에 혼합하지 않는다.
