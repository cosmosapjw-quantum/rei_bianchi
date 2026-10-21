# D9: 팽창 감쇠를 제거한 성분별 shear 누적 기여

## 결과와 연구 위치

판정: **PASS_SCOPED_D9**. 기존 175개 nominal component-grid trajectory의 153개 저장 epoch를 사용해 matter, photon, exactly massless neutrino의 누적 shear source를 계산했다. 새 IVP, ODE callback, momentum-moment 재계산은 각각 0개다. 독립 PHYS-MATH, PHYS-MATH-CODE 및 실제 그림 검토가 끝났으며, 아래 결론은 이 제한된 collisionless LRS Bianchi I 모형과 저장 sample quadrature에 적용된다.

현재 연구의 직접적인 성과는 부호반전의 원인을 성분별 누적 응력으로 설명하는 것이다. 초기 Sigma_F=0.003, P_r=-0.001인 다섯 조건에서 radiation의 누적 음의 기여는 모두 초기 양의 shear보다 크다. P_m,i=+0.0003인 조건만 충분한 양의 matter 기여를 축적해 z=2에서도 양의 shear를 유지한다. P_m,i=0인 조건에서도 matter의 이후 기여는 0이 아니다.

기존 D8의 네 인접 저장 sample 부호반전 구간은 다른 대화의 새 게시본에서 이미 완성되어 있었다. PR199 a3cb0606341688affb6aea29990e960e53188d32와 보존 commit eb8042b729051f4700bd5d88d6781c4620009bcb, PR216의 별도 consumer 결과, 원래 B2 raw의 SHA256/indices/저장값을 대조해 동일성을 확인했다. D9에서는 D8 분석을 다시 실행하지 않았고 중앙 DAG의 오래된 ready flag만 교정했다.

## 1. 정확한 기하·단위·부호

Signature는 (-,+,+,+), proper-time metric은

\[
ds^2=-c^2dt^2+a_\perp^2(dx^2+dy^2)+a_\parallel^2dz^2,\quad
a_\perp=ae^{-b},\quad a_\parallel=ae^{2b}.
\]

H=dot(a)/a, s=dot(b), sigma_ij=diag(-s,-s,2s), pi_X,ij=diag(-p_X,-p_X,2p_X)로 놓는다. p_X는 J/m^3이고 K=8 pi G/c^2다. 같은 normal orthonormal frame의 tensor를 더한다. Half-contraction을 쓰는 PR198과 달리 이 B pilot은 full spatial Frobenius convention이다.

\[
S_F=\sqrt6\frac{s}{H},\qquad P_X=\sqrt6\frac{Kp_X}{H^2},\qquad
\Sigma_F=|S_F|,\quad \Pi_{\rm tot,F}=|P_m+P_r|.
\]

절댓값은 성분 tensor를 더한 뒤 취한다. Photon과 neutrino의 저장 signed stress는 별도로 적분하지만, 이 모형에서 초기 brightness와 collisionless operator를 공유한다는 제한은 그대로다.

방향별 expansion은 H_perp=H-s, H_parallel=H+2s다. Einstein 공간 성분의 parallel-minus-perpendicular 차에서는 등방 pressure와 cosmological constant가 소거된다. H_parallel-H_perp=3s 및 pressure 차 3(p_m+p_r)를 사용하면

\[
\dot s+3Hs=K(p_m+p_r)
\]

를 얻는다. 이는 실제 canonical_fv.rhs 및 species_hierarchy.rhs의 shear source와 일치한다. Rendall의 Einstein–Vlasov 원전 Sec.2, Eqs.(2.1)–(2.14)는 이 기하/kinetic 대응의 문헌 근거다. 원전의 H는 extrinsic-curvature trace로, expanding branch에서 여기의 H와 H_paper=-3H 관계를 갖는다. 원전의 compact-support 가정이나 먼 미래 점근정리를 현재 혼합 성분·Lambda 모형의 유한 구간 결과에 자동 적용하지 않는다.

원전: https://arxiv.org/pdf/gr-qc/9505017

## 2. 적분인자와 성분별 누적 기여의 유도

x=ln(a/a_i)이므로 d/dx=H^-1 d/dt다. 정의를 미분하면

\[
S_F'=\sqrt6\left(\frac{\dot s}{H^2}-\frac{s\dot H}{H^3}\right)
=-\left(3+\frac{H'}H\right)S_F+P_m+P_r.
\]

임의의 양의 expanding solution에 대해

\[
M(x)=\left(\frac{a}{a_i}\right)^3\frac{H}{H_i}>0,\quad
\frac{M'}M=3+\frac{H'}H,\quad Q=MS_F
\]

로 정의하면

\[
Q'=M(P_m+P_r),\qquad
Q(x)=S_{F,i}+I_m(x)+I_r(x),\quad
I_X(x)=\int_{x_i}^{x}M(u)P_X(u)\,du.
\]

따라서 물리적으로 읽기 쉬운 최종 형태는

\[
\boxed{S_F(x)=\frac{S_{F,i}}{M(x)}+\frac{I_m(x)}{M(x)}+\frac{I_r(x)}{M(x)}}.
\]

첫 항은 그 실제 기하를 따르는 initial-shear memory이고 나머지는 각각의 누적 응력 기여다. 같은 식의 proper-time 표현은 d(a^3s)/dt=K a^3(p_m+p_r)다. Wolfram의 실제 symbolic substitution에서 x 표현과 proper-time 표현의 잔차가 모두 정확히 0이었다.

이 식은 비선형으로 결합된 하나의 계산된 trajectory 위에서 성립하는 정확한 항등식이다. M과 p_X 자체가 그 trajectory의 geometry와 분포에 의존하므로, 초기조건이 다른 여러 해를 선형 결합할 수 있다는 뜻은 아니다. 이번 분석에서 재사용한 선형 연산은 저장된 source의 적분과 tensor sum이다.

## 3. 부호반전과 norm cusp

M>0이므로 signed shear의 부호는 Q의 부호와 같다. S_F,i>0이면 누적 source가 -S_F,i에 도달할 때 부호반전이 가능하다. 이는 순간 total stress가 0인 조건과 다르다.

단순 zero x_c에서

\[
S_F'(x_c)=P_{\rm tot}(x_c),\qquad
\left.\frac{dS_F}{dz}\right|_{z_c}=-\frac{P_{\rm tot}(z_c)}{1+z_c}.
\]

P_tot(x_c)≠0이면 Sigma_F=|S_F|는 국소적으로 |P_tot(x_c)| |x-x_c|+O((x-x_c)^2)의 cusp를 가진다. Signed tensor와 geometry는 매끄러울 수 있다. D9는 연속 x_c를 계산하지 않으며, 아래 D8 저장 구간만 사용한다.

| P_m,i | 시간 진행 방향의 저장 z 구간 | 기존 D8 sample index |
|---:|---:|---:|
| -0.0003 | 2.9353050508 → 2.8729833462 | 135–136 |
| -0.0001 | 2.5758703349 → 2.5192408407 | 141–142 |
| 0 | 2.4086580994 → 2.3546766722 | 144–145 |
| +0.0001 | 2.2492649203 → 2.1978077332 | 147–148 |

## 4. 실제 z=2 성분 budget

다음 수치는 초기 S_F,i=0.003, P_r,i=-0.001의 다섯 조건이다. M(z=2)는 약 19.19214다. I_m/I_r와 Q는 무차원이며, Q=S_F,i+I_m+I_r라는 관계를 검사한다. 표의 표시 정밀도는 해석을 위한 반올림이며 전체 double 값은 results/endpoints_175.csv/json에 보존한다.

| P_m,i | I_m(z=2) | I_r(z=2) | 저장 Q(z=2) | 저장 S_F(z=2) |
|---:|---:|---:|---:|---:|
| -0.0003 | -3.7947441e-4 | -3.3044642e-3 | -6.8393857e-4 | -3.5636382e-5 |
| -0.0001 | -1.2889867e-4 | -3.3055306e-3 | -4.3442928e-4 | -2.2635787e-5 |
| 0 | -3.6147091e-6 | -3.3060639e-3 | -3.0967854e-4 | -1.6135693e-5 |
| +0.0001 | +1.2166664e-4 | -3.3065971e-3 | -1.8493040e-4 | -9.6357343e-6 |
| +0.0003 | +3.7222150e-4 | -3.3076634e-3 | +6.4558094e-5 | +3.3637771e-6 |

다섯 조건에서 radiation의 누적 기여는 매우 가깝지만 정확히 같지는 않다. 각 해의 geometry가 달라지기 때문이다. 초기 matter stress를 증가시키면 이 단면에서 endpoint의 양의 matter 기여가 커져 마지막 조건이 양의 shear를 유지한다. 이 finite slice 밖에서의 보편 단조성이나 전역 보간 정리는 주장하지 않는다.

특히 nominal P_m,i=0 조건은 독립적인 물리 정보다. 초기 matter 분포의 stress가 0이어도 이후 anisotropic expansion 아래의 누적 matter source는 I_m=-3.6147091e-6이다. 따라서 '초기 matter stress가 0'과 'matter anisotropic stress가 전 구간 0'은 다른 조건이다. 이 관측은 다음 연구 단위에서 정확한 kinetic pressure-moment 방정식으로 설명할 수 있다.

Gamma/nu 분리 값도 저장했다. 예를 들어 P_m,i=0 조건의 I_gamma=-0.001956245704577758, I_nu=-0.0013498181542253766이며 합이 I_r다. 이 분해가 독립적인 photon/neutrino 초기조건 또는 collision operator의 검증을 뜻하지는 않는다.

## 5. 샌드박스 계산과 오차 해석

175개 nominal ×153 epochs, 총 26,775개 저장 시점에서 검사했다. 35개 historical reference는 alias로 유지되어 신규 trajectory 수에 기여하지 않는다. Python3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8을 사용했다.

각 case의 scale=max(|S_F,i|, max_x(|I_m|+|I_r|), 1e-12)에 대해 R=Q-S_F,i-I_m-I_r를 기록했다. 미리 고정한 max_x|R|/scale≤2e-5를 175/175가 통과했고, 최대값은 1.473444875767401e-6이다. 네 D8 구간의 양 끝점에서는 재구성 부호가 모두 일치했고 최대 |R/Q|=2.022140048467199e-5였다. 고정 기준은 0.1이다.

각 성분의 endpoint Simpson-minus-trapezoid 차도 저장했다. 전 grid 최대 절댓값은 matter 5.032897063895255e-9, radiation 9.589891269328257e-9다. 이 차는 sampling/quadrature 민감도를 보여주는 진단이며 정밀한 수렴 certificate가 아니다. 작은 total residual만으로 서로 상쇄될 수 있는 개별 성분의 오차를 엄밀히 제한했다고 주장하지 않는다.

SciPy cumulative_simpson은 실제 저장 간격을 입력받아 epoch 축으로 누적 적분했다. 해당 API와 불규칙 sampling의 처리 근거는 사용 버전의 공식 문서에서 확인했다: https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.cumulative_simpson.html

Production은 한 process/한 numerical thread에서 CPU9.233895646초, wall9.763839518초, peakRSS136736KiB로 끝났다. 별도 reader 검산과 그림 수정은 CPU4.95775초였다. 이는 수행 기록이며 다른 구현 대비 가속배수 측정이 아니다.

실제 네 software control은 quadratic primitive, nonconstant integrating factor의 source-free decay, 같은 기하에서 반대 성분의 exact cancellation, nonmonotone x rejection이다. 초기에 발견된 case/species broadcast 오류는 production 전에 고쳤고 실패 기록을 보존했다. 이후 독립 검토에서 약한 decay control과 진단 범례 겹침을 고쳤으며, 175개 분석을 재실행하지 않았다.

## 6. 구현상 절감과 NCP 준비

이번 구현은 매 sample에서 massive moments를 다시 구성하지 않는다. 이미 저장한 H,s 및 species stress를 한 번씩 읽고, case×epoch×species 배열의 broadcasting과 SciPy 누적 적분을 사용한다. 원래 full state 또는 worker별 ODE solver가 필요하지 않아 이 작은 unit을 64개 process로 분할할 과학적 필요가 없다.

동일 계산에 필요한 배열은 1,189,308-byte lossless compact NPZ로 함께 게시한다. 모든 compact array의 save/load equality 및 대표 full/compact reader의 13개 diagnostic exact equality를 검사했다. 원래 175 raw SHA256, source/config, 35 aliases, 원래 실패 receipt와 saved-raw 복구는 JSON mapping에서 추적 가능하다. 이 compact 자료는 원래 IVP와 독립적인 새 수치 실행으로 세지 않는다.

NCP에서는 이미 설치된 Python/NumPy/SciPy/Matplotlib로 repository의 run_ncp.sh를 실행할 수 있다. 별도 C++ 구현이나 dependency 교체는 필요 없다. 이번 D9의 NCP 실행은 NOT_RUN이며, 현재 과학적으로 빠진 D9 case는 없다. Optional reproduction은 README의 create-only output 명령을 따른다.

새로 발견한 PR215의 reflected native96×16 kernel은 warm96×32 paired quadrature의 구현이다. 현재24×12 Gauss3 canonical FV에 바로 대체하지 않는다. 기존 source pins와 제한을 보존하며, reflection pair folding/shared moments/compensated sums는 나중에 matching adapter가 필요한 방법 후보로 정리했다. VigilODE의 새 manufactured/stencil 결과도 별도 lane이며 현재 DOP853 결과의 동등성을 자동 보증하지 않는다.

## 7. 다음 단일 과학 노드와 보존 판정

선택된 다음 노드는 **D10_ZERO_INITIAL_MATTER_STRESS_GENERATION**이다. 먼저 collisionless kinetic pressure-moment 방정식을 LRS convention으로 유도하고, P_m,i=0인 기존35조건의 저장 이력에서 shear-induced matter quadrupole의 부호와 누적 크기를 대조한다. 새 IVP가 필요한지 그 후 판단한다. 현재 단위는 D9에서 닫으며 D10을 실행 완료로 표시하지 않는다.

PR198 PASS_SCOPED_PRELIMINARY, AGE NATIVE_AGE_TIME_CONVERGENCE=HOLD, NONLINEAR_GRACKLE_RESPONSE_BOUND=NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED 및 V12 기존 제한은 그대로다. D9의 status는 derived + numerically checked + implementation-verified이며, 최종 Git/provider 보존 상태는 각 실제 publication/backup receipt를 따른다.
