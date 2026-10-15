# REI Σ–π 초기조건 응답: 실제 비선형 전단 퇴화 연구

2026-10-15 KST. 소스: rei_bianchi PR145의 source-locked Einstein–Boltzmann–Vlasov positive canonical FV (HEAD 54e29dff5a90c0a785cb6dcfb004403614ca403b), 원본 canonical_fv.py SHA256 91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5. 본 대화에서 사용자 Ubuntu 로컬 코드 작성·실행. 별도 local Codex나 native subagent 호출 없음. 원본 AX08 solver/checkpoint 및 PR145 코드는 수정하지 않았다.

## 1. 초기 전단과 π_ab는 독립적인 실물리 조건

비틸트 축대칭 Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), sigma^i_j=diag(-s,-s,2s), s=dot b. 따라서 사용자 표기 Sigma=sqrt(sigma_ab sigma^ab/2)/H=sqrt3 abs(s)/H; signed orientation은 별도. 기존 signed q_ref=s_ref/H_FLRW(a_ref)는 소스 호환 IC 어댑터다.

이용한 실제 parent source는 다음을 적분한다.

ds/dln(a)=-3s+(8 pi G/(c² H)) Pi_s,
Pi_s=(P_parallel-P_perp)/3=Pi_gamma+Pi_nu+Pi_massive.

원본 광자/중성미자 각도 초기분포는 W=1+kappa P2(mu), massive original nonbaryonic Fermi–Dirac 입자 초기분포는 W_m=1+A_m P2(mu). 부호 있는 q, 광자 kappa_gamma, 중성미자 kappa_nu, massive A_m 네 개를 독립적으로 바꿔 계산한다. Mass fraction f_m=.1은 원본 비바리온 Omega_m의 일부에서 차감해 dust와 double count하지 않았고, m/T_ref=30, radial24×angular12 positive Gauss3, gamma/nu L=8; gamma에만 원본 frozen H/He electron donor에 따른 Thomson.

Wolfram15.0.1에서 P2 평균0, P2² 평균1/5, gamma의 초기 Einstein forcing derivative H0² Omega_gamma/(5 Href² a_ref⁴), 정확한 shear variation-of-constants 항등식 0 검증. 수치 초기 RHS를 이 도함수와 비교한 새 회귀시험 통과. 이 결과는 EoR ionizing photon stress가 실제로 닫혔다는 뜻이 아니다.

## 2. 물리적 국소 미분 응답

기준 p=(signed q_ref,kappa_gamma,kappa_nu,A_m)=(0,.2,.2,.5), zbar20→4. 두 경로를 실제 실행: (A) gamma+nu collisionless와 positive massive, (B) 원본 ZERO H/He 완료 이력 312238행의 전자밀도를 gamma Thomson에 일방향으로만 공급. B경로 frozen original history SHA256 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f.

B경로 zbar4 signed s/H=7.524262950691145e-5, Sigma_end=1.303240572010518e-4, 원본 parent PR145 수치와 일치. A경로 Sigma_end=1.309027031229716e-4.

중심 유한차분 halfsteps=(.001,.02,.02,.05)를 사용해 signed s/H_end의 네 초기조건에 대한 gradient 계산:

[0.1143388669411, 0.000172728112875, 0.000120338812119, 0.0000332453070855].

차분 크기를 절반으로 줄인 뒤 B경로 최대 상대 signed shear derivative 차이 약9.65e-7, A경로5.06e-8. Source H² constraint 상대 잔차~2.22e-16, photon/nu number conservation 및 massive positive cell 검증.

단위를 명시한 5개 source-forward observable O=(signed s/H,b,E_gamma2,E_nu2,Pi_m/rhocrit), 관례적 column scales dp=(.001,.02,.02,.05), row scales dO=(1e-4,1e-4,.04,.04,1e-4)를 정의한다. 이 선언한 스케일의 normalized Jacobian singular values [5.99333,0.107032,0.102506,0.0985882], model rank4, condition~60.79. 이는 소스 내부 구조적 국소 분리가 가능한지를 보여 주는 값이며 관측 공분산/우주론적 사후분포/검출 significance가 아니다.

## 3. 실제 비선형 같은 후기 전단, 다른 초기 π의 쌍

원본 Einstein+massive FD FV+gamma/nu+실제 frozen H/He one-way Thomson 동일한 물리. Brent root로 photon kappa_gamma를 해마다 실제 변화시켜 다음을 구성했다.

| Initial parameter | A | B |
| q_signed | 0 | +0.00005 |
| initial kappa_gamma | .2 | .16690125893290458 |
| initial kappa_nu | .2 | .2 |
| initial massive A_m | .5 | .5 |
| zbar4 signed s/H | 7.524262950691145e-5 | 7.524262950698135e-5 |

두 후기 scalar 차이6.9903935071e-17. 그러나 같은 epoch:
- b_B-b_A=+2.119624069299008e-5
- E_gamma2_B-E_gamma2_A=-.0064648606591750715
- E_nu2_B-E_nu2_A=-3.511883062740778e-5
- Pi_massive_norm_B-Pi_massive_norm_A=-4.94478e-8

둘 다 실제 positive angular distribution과 H constraint를 만족한다. 하나의 scalar 최종 signed shear 또는 Sigma는 4개의 초기 IC 기원을 유일하게 결정하지 못한다. Nonzero local d(s/H)/d kappa_gamma인 영역에서 implicit-function theorem이 국소 같은 후기 전단 수준집합을 예측하고, 이번 계산은 그 실제 비선형 두 점이다. 다른 source angular quadrupole과 background metric 정보를 측정하면 구분 가능성이 있으나 관측 창함수·잡음·likelihood를 아직 모델링하지 않아 실제 관측 판별 가능성은 미인증이다.

## 4. 실제 코드·tests·병렬화

- response.py: source-frozen 4-input × 5-output Jacobian at all 101 epochs, two finite-difference resolutions, no donor/real HHe donor two lanes.
- degeneracy.py: independent exact forward solve from physically distinct IC and Brent gamma root, full state histories 121 epochs, source positivity and Einstein H constraint.
- test_response.py: 새 소스 잠금, 초기 Sigma, positive FD, analytic gamma initial forcing, true nonlinear degeneracy, constraint/number positivity, derivative refinement 등 15 PASS. 부모 original canonical FV 18 source physics tests는 별도 Pytest 18 PASS. 처음 부모 unittest 방식은 massive_radial imports 실패; 올바른 original pytest/PYTHONPATH로 재실행 PASS, 테스트 기준은 미완화.
- parallel_bench.py: 16개 독립 Einstein+FV+gamma/nu 본연의 물리 초기조건, 실제 host 3반복 중앙값 serial .419585s, two processes .303001s (1.385x), four processes .197414s (2.125x). 모든 출력 완전 동일; 이 측정은 NO HHe donor *performance lane*이며 native REI H/He solver speedup 주장이 아니다.
- 3개 실제 플롯: 같은 후기 전단의 서로 다른 시간 이력, 상이한 radiation/metric, 선언한 normalized response Jacobian.

## 5. 다른 repo 최신 기여 및 과학적 범위

PR145는 이미 canonical Vlasov positive cell/Einstein을 구성했고, BASS PR161은 mass/ν/gamma 독립 source와 one-way HHe 실제 electron을 연결했다. REI PR142는 이미 near-zbar4 native C13 HHe+Einstein short-window pilot이며, PR143/144는 외부 stellar reservoir, Case-A escaped radiation pi와 recoil에 따른 GR Q^mu 미닫힘을 실제 source 계산으로 확인했다. 따라서 본 결과는 이들 physics 재구현이 아니라 **이미 구현된 독립 초기 Σ–π source를 실제 후기사용량에서 구별할 수 있는지 검증하는 새로운 forward sensitivity**이다.

Full polarized E/B Thomson, source full stellar gravity/escape Q^mu, baryonic recoil, 실제 cold zbar20→4 two-way HHe feedback, 관측 정보손실/weak lensing·CMB likelihood, AX11 numerical admission 모두 NOT_ESTABLISHED. 원본 REI owner checkout, mass FV parent PR145, source donor raw data, native solver와 checkout은 미변경.

다음 연구: C15 native short-window two-way source를 이 IC 쌍에서 같은 physical clock으로 실행하고, 기존 open Q^mu 에너지/운동량 closure 범위 내에서 HII/HeII/Tgas와 photon quadrupole 관측 proxy를 비교하여 sensitivity transfer; 차분오차와 source uncertainty를 사후 likelihood에 분리해 넣을 것.
