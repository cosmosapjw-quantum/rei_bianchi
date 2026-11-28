# BASS_HE AUDIT1: 적대적 감사, 해석적 최적화, 독립 구현 검증

2026-09-26. `PAPER_DERIVED_REIMPLEMENTATION / NOT_AUTHOR_CODE`.
이 보고서는 중단된 DR8 실행을 재개한 기록이 아니다. 복구된 DR7 코드와 기존 반환 데이터를 먼저 감사한 뒤 새 연구 커널을 구현·검증하고 제한된 pilot를 실행했다.

## 1. 권위와 범위

1차 자료는 Gusev–Solov'ev–Vinitsky, CPC 286 (2023) 108662 [1], 첨부 Stolterfoht et al., PRA 81 (2010) 052704 [2], DR7 배포 archive, 사용자 및 sandbox 반환 ZIP 7개다. `evidence/INPUT_INVENTORY.json`과 `TRANSPORT_AUDIT.json`이 실제 bytes/해시/manifest 판정이다. DR8 잔존 디렉터리는 DR7을 설명하는 README 두 개뿐이었다. 완성된 DR8 실행 코드·과학 결과를 복구했다고 주장하지 않는다.

7개 반환 ZIP의 내부 manifest 241개가 모두 일치했고 기록상 작업 55개가 성공했다. 이는 전송 무결성 및 실행 기록의 일관성이다. 과학적 정확성, branch 판정의 충분성, 물리모형의 적용 가능성까지 증명하지 않는다. 기존 결과는 삭제하거나 소급하여 다른 계산의 결과로 바꾸지 않았다.

현재 감사 범위는 복구된 DR1–DR7 충돌 계산 구현과 DR8 준비 상태다. 전체 He 원자물리 MICRO-0의 모든 rate authority, RR/DR energy moments, RCT spectrum, EoR production network까지 재감사한 것은 아니다.

## 2. 적대적 감사 결과

### A01 — 치명적: 두 spectral root의 일치만으로 branch point를 판정할 수 없다

기존 branch solver는 두 sheet의 continued-fraction residual과 `p_a²-p_b²=0`을 풀었다. 그러나 matching index는 서로 다른 물리방정식이 아니라 같은 spectral equation의 서로 다른 표현(chart)이다. 두 풀이가 동일한 정상 eigenroot로 수렴하면 branch가 아닌 곳에서도 모두 0이 된다.

실제로 R=1 a0, E=-3.033352518074749 Eh에서 legacy 조건의 최대 잔차가 5.551115123125783e-16이었다. 반면 단일 spectral Jacobian의 singular values는 (3.316546053956542,0.9536625915881077), determinant는 -3.1628659049375076이었다. 즉 regular root다. 증거: `BRANCH_FALSE_POSITIVE_WITNESS.json`.

수정: F(z,R)=0, z=(p,lambda)에 대해 det(F_z)=0을 함께 풀고, simple-fold의 transversality/curvature를 확인한다. 이어서 실제 continuation으로 1회전 sheet 교환과 2회전 복귀를 검사한다. 다섯 reference-seeded branch 모두 새 검사를 통과했다. 이는 부동소수점 numerical certificate이지 interval arithmetic에 의한 존재·유일성 정리는 아니다. 전역 blind enumeration도 아니다.

### A02 — 중대: 작은 잔차와 행렬 정상화는 충분한 과학 gate가 아니다

기존 Qother/S23의 20-panel 결과는 40/80-panel 결과와 크게 달랐다. 이것은 단순 적분 오차와 sheet hop을 구분하지 못한 상태였으며, 모든 '작업 성공'을 수렴으로 읽어서는 안 된다. 새 contour 커널은 두 sheet의 상대 gap, analytic-Jacobian tangent predictor, 필요시 step bisection을 사용한다. 미해결 gap collapse를 0으로 대체하지 않는다.

새 32/64/128-panel 검사에서도 S23의 관측차수는 약 1.78이었다. Q 네 개의 약 4차 거동을 모든 branch에 확장하지 않는다. 다만 S23의 64→128 상대 변화는 1.71e-7이었다. 이 작은 변화는 엄밀한 오차상한이 아니다.

### A03 — 모형 차이: Eq. (50)의 확률 곱은 coherent scattering amplitude가 아니다

[1]의 Eq. (50)는 확률 행렬을 곱한다. 두-level 동일 crossing 두 번이면 off-diagonal probability는 2p(1-p)이다. coherent 두 경로에서는 상대 위상에 따라 4p(1-p)sin²(phi)가 될 수 있고, 균일 위상평균에서만 2p(1-p)로 환원된다 [3]. 현재 모델이 그런 위상평균을 정당화하는 관측량인지 별도 판단이 필요하다. probability stochasticity나 독립 RK4 일치만으로 interference·실제 cross section을 검증하지 않는다.

### A04 — source convention 미해결: Eq. (52)/Eq. (55)의 factor two

[1]은 Eq. (52)에 exp(-Delta/v), Eq. (55)에 exp(-2Delta/v)를 인쇄한다. 같은 Delta 정의를 썼다면 다르지만, 저자 코드 없이 두 Delta의 정규화까지 동일하다고 단정할 수 없다. 새 실행기는 factor=1/2를 이름 있는 별도 정책으로 보존한다. 어느 것이 저자의 정확한 CR_SECTION implementation이라고 판정하지 않는다.

### A05 — 치명적 observable 함정: identity survival tail은 elastic cross section이 아니다

P_ii(rho)→1이면 2pi∫P_ii rho d rho는 발산한다. 유한 rho_max로 자른 값도 면적 pi rho_max²라는 임의 기하학 성분을 포함한다. 본 구현은 off-diagonal indexed-state transition area만 계산하며, loss는 off-diagonal 합으로 얻는다. 이것은 실제 elastic amplitude의 위상 정보를 대체하지 않는다.

### A06 — 채널 의미론: upper united-atom shell과 physical ionization/capture를 중복 계수하면 안 된다

[1]은 상위 Nmax shell을 ionization surrogate로 취급한다. 같은 population을 동시에 독립된 bound capture와 ionization에 더하면 전하/입자 ledger가 무너진다. 새 API는 disjoint bound/sink labels를 요구한다. 현재 pilot는 물리적 capture/ionization 총합을 출력하지 않고 indexed-state probability와 off-diagonal area만 저장한다. 이 선택은 원문의 surrogate를 숨기지 않고 observable promotion을 보류하는 것이다.

### A07 — 적용 범위: straight-line 모형은 저에너지 END 계산과 같은 물리가 아니다

[1]의 R=(vt,rho,0), small-R Eq. (47), approximate S-series matching boundary는 그대로 모델 가정이다. [2]는 낮은 에너지의 rotational/isotope 효과에서 궤적 편향과 접근 최소거리의 중요성을 명시한다. 고정 직선 궤적 코드를 빠르게 만든 것이 저에너지 물리 정확성을 올려 주지는 않는다. 특히 30–300 eV/u의 채널별 END 결과와 비교할 때 collision energy convention과 궤적을 함께 고정해야 한다.

### A08 — 구현: cache 동시 작성과 resume identity

새 cache의 초기 구현에도 동시 쓰기 경쟁이 있었다. 서로 다른 payload 8개가 같은 key에 접근했을 때 7개가 성공하는 반례를 먼저 기록했다. `fcntl` per-key lock, atomic rename, file+directory fsync로 수정했고 충돌 시 하나만 채택한다. cache lock inode는 지우지 않는다. RUN_BINDING은 source/environment/parameters가 바뀐 resume을 거부하며, 기존 run 디렉터리의 무조건 덮어쓰기도 거부한다.

### A09 — 작은 채널의 소거: 차분형 확률 update도 안전하지 않을 수 있다

새 sparse kernel의 초안에서 yi+p(yj-yi) 형태는 p=1, (yi,yj)=(1,1e-80)일 때 작은 채널을 0으로 지웠다. 두 exact swap 후 원래 작은 population이 돌아와야 한다는 테스트를 먼저 실패시킨 뒤, (1-p)yi+p yj라는 convex form으로 수정했다. 기존 pilot/두 quadrature의 geometry는 그대로 보존하고 assembly만 다시 계산하여 최대2.22e-16 차이를 확인했다. `RED_RARE_CHANNEL.txt`, `ASSEMBLY_RECHECK.json`이 증거다. 극단적인 exp(-u)≈1의 complement 정밀도 문제까지 전 구간 해결했다고 주장하지 않는다.

## 3. 해석적 유도에 근거한 최적화

### 3.1 Spectral Jacobian과 simple fold

F=(F_xi,F_eta), z=(p,lambda). F_z가 invertible이면 implicit-function theorem으로 z(R)가 analytic하므로 그 지점은 두 sheet의 square-root branch가 아니다. 따라서 필요한 조건은 F=0 및 det F_z=0이다. 오른쪽/왼쪽 null vectors v,w에 대해 w*F_R≠0, w*F_zz[v,v]≠0이면 국소적으로

eta² = -2 (w*F_R)/(w*F_zz[v,v]) (R-Rc) + higher terms.

이 식은 branch solver의 조건, monodromy 초기 두 sheet seed, endpoint regularization의 근거다. discriminant 접근 자체의 문헌 근거는 [4]이며, 본 continued-fraction Jacobian 및 numerical tests는 이 구현의 직접 유도다.

Continued-fraction 재귀 D_s=B_s-A_s C_(s+1)/D_(s+1)에 대해

dD_s=dB_s-(dA_s C+A_s dC)/D + A_s C dD/D².

p,lambda,R에 대한 analytic derivatives를 같은 재귀에 실어 보낸다. complex finite difference와 real finite difference 양쪽으로 독립 검산했다. spectral residual이 작다는 판정과 Jacobian rank 판정을 분리한다.

### 3.2 Rotating frame을 정확히 제거한다

논문의 atomic units를 코드에 그대로 사용한다. 단위를 복원하려면 ell_i=L_i/hbar, Ecal의 단위는 energy/length²로 놓는다:

i hbar dA/dt = [Ecal R² ell_x² + hbar theta_dot ell_z] A.

A=G B, G=exp(-i theta ell_z), theta=atan2(rho,x), x=vt를 대입하면 -i hbar G†Gdot가 rotating-frame 항을 정확히 상쇄한다. G†ell_x G=cos(theta)ell_x-sin(theta)ell_y이므로

i hbar dB/dx = (Ecal/v) (x ell_x-rho ell_y)² B.

기존 rho/(x²+rho²) spike가 없어지고 매끄러운 quadratic polynomial Hamiltonian이 된다. 이것은 approximation을 바꾼 것이 아니라 같은 Eq. (47)의 정확한 representation change다. rho=0에서도 원래 회전좌표의 singular chart 대신 연속 head-on limit을 처리한다. 확률은 최종적으로 rotating frame 및 molecular Lx basis로 다시 변환한다.

이 Hamiltonian은 m_z parity를 보존하므로 두 invariant subblock으로 분해한다. 각 subblock에는 2점 Gauss sample을 이용한 4차 Magnus generator를 사용한다 [5]:

K=h(H1+H2)/2 + i sqrt(3) h² [H1,H2]/12, U_step=exp(-iK).

H1,H2가 Hermitian이면 K도 Hermitian이므로 각 단계는 반올림 오차 범위에서 unitary다. unitary라는 사실은 정확한 time discretization을 뜻하지 않으므로 별도 step convergence를 검사했다. NumPy batch `eigh`는 energy/rho별 작은 Hermitian block을 동시에 처리한다.

### 3.3 Observable만 전파한다

Eq. (51)/(53)는 identity의 두 행만 바꾸므로, 특정 initial column을 위한 full dense d×d product는 불필요하다. incoming에는 큰-ReRc부터, outgoing에는 작은-ReRc부터 2행 update를 적용한다. 선택한 C개 initial columns에 대해 crossing update 비용은 O(K C), 현재 dense P_rot 적용 비용은 O(d² C)이며 batch 크기만큼 곱해진다. P_rot의 작은 block을 직접 적용하면 후자도 더 줄일 수 있지만 이번 구현에서는 dense batch multiplication을 유지했다. 기존 dense product와 absorbing block을 포함한 비가환 테스트에서 동일성을 확인했다.

column-stochastic M은 l1 contraction이다. 따라서 operator error의 telescoping bound는

||P-P_tilde||_1 <= ||P_rot-P_rot_tilde||_1 + 4 sum_k |p_k-p_k_tilde|

(동일 crossing을 양쪽에서 한 번씩 쓰는 경우)로 억제된다. exp(-c Delta/v)에 대한 |dp|≤(c/v)exp(-c Delta_min/v)|dDelta|와 결합하면 contour tolerance를 observable sensitivity에 배분할 수 있다. 이는 직접 유도된 조건부 상한이며, 아직 실제 Delta interval certificate를 만들지 않았으므로 자동 pruning에는 사용하지 않는다.

### 3.4 Geometry/energy 분리와 quadrature

static Coulomb + straight-line source model에서는 Rc가 rho,v와 무관하고 Delta(rho)는 v와 무관하다. 같은 Delta를 energy와 factor=1/2 정책마다 다시 계산할 이유가 없다. 이 separability는 dynamical basis나 bent-trajectory 모델로 그대로 승계할 수 없다.

X(s)=Re Xc+i Im Xc(2s-s²)로 두면 gap=O(1-s), dX/ds=O(1-s)라 변환 integrand가 O((1-s)²)이다. 이 좌표에서 Simpson 적분을 한다. endpoint zero는 검증된 simple fold일 때만 쓴다.

Eq. (54)는 u=rho²로 바꾸면 pi∫P(sqrt(u)) du다. 모든 support discontinuity와 rotational matching boundary를 구간 경계로 넣고 interior Gauss nodes만 샘플한다. energy/exponent lanes는 이미 구한 geometry에서 vectorize하며 독립 geometry job만 process parallelism으로 실행한다. 각 프로세스 BLAS thread=1이다.

## 4. 탐색한 대안과 이번 선택

| 대안 | 장점 | 위험/비용 | 이번 결정 |
|---|---|---|---|
| continued fractions + analytic J + fold/monodromy | 기존 ODE convention 유지, branch 오판정 제거 | chart pole와 global sheet association은 여전히 관리 필요 | 구현 |
| prolate-spheroidal collocation / generalized eigensolver | recurrence와 독립된 검증 경로 | 경계·metric·truncation 및 complex eigenvector tracking 새 개발 필요 | 다음 독립 oracle 후보 |
| 기존 rotating frame adaptive RK / angle 재매개화 | 구현 단순, 비교 경로 확보 | 좁은 spike 또는 끝점 stiffness | 기존 high-resolution 비교용 보존 |
| exact gauge + parity Magnus4 | singular chart 제거, unitary, batch 가능 | approximate physical R_cut는 여전히 남음 | 구현·측정 |
| coherent amplitude/density-matrix transport | Stückelberg phase와 coherence 추적 | phase/connection coefficients가 추가로 필요 | 별도 physics track; 기존 확률에 임의 phase 추가 금지 |
| dynamical/bent-trajectory END 또는 coupled-channel | 저에너지 trajectory 효과를 직접 다룸 | 별도 전자–핵 동역학, basis 검증 필요 | 물리 적용범위 확대의 우선 후보 [2] |
| Numba/Rust CF, GPU batch | 대형 grid에서 throughput 가능 | 정확한 bottleneck 및 compile/runtime 부담 | profiling 뒤 결정; 이번에는 CPU vectorization/process만 |
| 하나의 complex-R contour를 모든 rho에서 재사용 | geometry solve 횟수 추가 감소 가능 | homotopy가 다른 branch/cut를 넘지 않는다는 증거 필요 | 아직 사용하지 않음 |

SciSpace에서 [6–8]도 후보로 발견했지만 이번 응답에서 그 전체 원문/수치 payload를 검사한 것은 아니다. 첨부 [1–2]와 직접 유도·실행 증거가 현재 판정의 중심이다. CodeRabbit CLI는 미설치였고 설치 URL도 DNS 실패하여 외부 CodeRabbit review는 수행되지 않았다. 본 감사는 그 도구의 리뷰인 것처럼 표시하지 않는다.

## 5. 실제 실행과 아직 닫히지 않은 것

수치는 `evidence/RESULT_SUMMARY.json`, `PILOT_EXECUTION_LOG.txt`, `DISCRETIZATION_AUDIT.json`, `QUADRATURE_COMPARISON.json`을 기준으로 한다.

- 새 branch 5개: simple-fold + 1/2회전 monodromy 모두 통과. 원문 값과 최대 위치 차이는 약 1.664e-5 a0. CF depth 96→144의 최대 변화는 2.44e-13 a0.
- action rho=0: Q branch 4개의 관측차수 약 3.94–4.003. S23는 1.78이므로 범용 4차 수렴을 주장하지 않는다.
- 회전 workload 6개: legacy512-step median 0.2945 s, 새 batch32-step 0.01359 s, 약 21.67배. 새32→64 matrix 최대 차이 1.51e-8, legacy512와 차이 9.94e-7. 전체 solver가 21배 빨라졌다는 주장은 아니다.
- 작은 radial quadrature order1/2는 각각 geometry24/48건, 2 workers에서 약15.9/32.2 s. 오류로 종료한 geometry는 없었다.
- 하지만 order1→2에서 indexed-state transition vector의 상대 l1 변화가 최대25.94%다. **Eq. (54)는 수렴하지 않았다.** 한 total의 0.09% 변화만 보고 채널 전체가 수렴했다고 선언하지 않는다.
- exponent=1/2도 미해결 정책이다. 낮은 에너지에서 큰 observable 차이를 만든다. source ambiguity를 fit으로 감추지 않는다.

이 버전의 gate는 '수정된 연구 커널과 제한된 pilot 검증'이다. physical He-H production cross sections, RCT photon-energy moment, thermal CT2 adapter, full MICRO-0, 전역 hidden-crossing enumeration은 여전히 열려 있다. 다음 bounded unit은 component-wise error estimator를 갖춘 support-split adaptive u quadrature이며, 그 전에 S23 endpoint/path 오차와 inherited rotational R_cut sensitivity를 분리한다.

## 참고문헌/권위 상태

[1] Gusev et al., CPC 286,108662 (2023), DOI 10.1016/j.cpc.2023.108662. 첨부 원문 및 pp.11–13/17–18 확인.
[2] Stolterfoht et al., PRA81,052704 (2010), DOI 10.1103/PhysRevA.81.052704. 첨부 원문, 특히 p.4 trajectory limitation.
[3] Shevchenko, Ashhab & Nori, Phys.Rep.492,1–30 (2010), DOI 10.1016/j.physrep.2010.03.002; arXiv:0911.1917. coherent phase 의존성 문헌 근거; 위 2×2 identity는 직접 유도.
[4] Amore & Fernández, arXiv:1911.00452 (2019), Exceptional points of parameter-dependent Hamiltonians. abstract상 discriminant 방법 확인; 본 F/J 구현은 직접 유도.
[5] Blanes et al., Phys.Rep.470,151–238 (2009), DOI 10.1016/j.physrep.2008.11.001; arXiv:0810.5488. Magnus 구조 보존 방법의 문헌 근거.
[6] Krstic & Janev, PRA47,3894 (1993), DOI 10.1103/PhysRevA.47.3894. SciSpace metadata/abstract 후보, full-text 미감사.
[7] Grozdanov & Solov'ev, PRA90,032706 (2014), DOI 10.1103/PhysRevA.90.032706. dynamical-basis 후보, full-text 미감사.
[8] Grozdanov & Solov'ev, EPJD (2018), DOI 10.1140/epjd/e2018-80758-x. hidden-crossing 적용범위 후보, full-text 미감사.


## 7. AUDIT2: support-split adaptive Eq. (54)와 모델 민감도

AUDIT1의 fixed-order order1/2 비교는 indexed-state vector에서 최대 25.94% 차이를 보였으므로 Eq. (54) 수렴 gate를 열어 둘 수 없었다. AUDIT2에서는 단순히 order를 높이는 대신 물리적으로 알려진 불연속을 먼저 분리하고, `u=rho^2`를 사용하여 `2*pi*rho drho = pi du`로 바꿨다. 모든 Eq. (52) support cutoff와 inherited rotational matching boundary를 정확한 subinterval 경계로 넣고, 각 smooth interval에서 embedded Gauss-Kronrod pair를 사용한다. 수렴 판정은 총합 하나가 아니라 모든 material indexed-state component에 `atol+rtol*|I_i|`를 적용한다.

저비용 adaptive lane은 Gauss-3/Kronrod-7, 독립 verification lane은 Gauss-7/Kronrod-15다. 2% exact support-split GK7은 7 intervals, 49 evaluations, refinement 없이 component-wise gate를 통과했다. 이후 `Delta(rho)`가 현재 static-Coulomb/straight-line model에서는 energy 및 exponent factor와 독립이라는 separability를 이용해 `u=rho^2`의 local-cubic surrogate를 도입했다. 이 surrogate는 branch support 밖으로 extrapolate하지 않으며 exact held-out geometry validation을 런타임 gate로 요구한다.

10개 exact sentinel의 최대 상대 Delta 오차는 `1.388034624856879e-05`였고 threshold `2e-4`를 통과했다. 별도의 212 exact cached GK15 point에 대한 적대적 hold-out에서는 최대 상대오차가 `4.3469e-05`였으며 worst branch는 S23였다. 이것은 numerical held-out evidence이지 전역 interpolation error theorem은 아니다.

0.2% adaptive target에서 GK7은 8 intervals / 63 evaluations / 1 refinement, GK15는 7 intervals / 105 evaluations / 0 refinement였다. 두 독립 quadrature lane의 최대 component 상대차이는 `3.3442230407223834e-05`, 전체 vector relative L1 차이는 `4.3540716529505146e-06`이었다. S23 contour를 32->64 panels로 올린 별도 검산의 최대 상대 변화는 `2.2470166629794012e-06`였다.

그러나 numerical convergence가 물리모형 gate를 닫지는 않는다. rotational matching radius를 ±10% 변화시키면 total indexed reaction-loss area는 0.5 keV/u factor-2 lane에서 약 `-6.44% / +6.82%` 이동한다. 이는 0.2% quadrature target보다 훨씬 크다. factor-1 0.5 keV/u는 약 `-0.478% / +0.510%`, 고에너지 5 keV/u lane은 더 작았다. 따라서 low-energy 결과의 dominant uncertainty는 현재 적분오차가 아니라 matching-radius authority와 model choice다.

또한 nominal indexed reaction-loss area는 exponent factor=1과 2 사이에서 크게 다르다. 0.5 keV/u에서는 약 `21.0036` 대 `1.95526 a0^2`, 5 keV/u에서는 `148.5255` 대 `60.4574 a0^2`다. Eq. (52)/Eq. (55)의 factor-of-two source convention은 단순 수치오차가 아니라 결과를 지배하는 독립 gate다.

따라서 AUDIT2의 판정은 `SCOPED_NUMERICAL_EQ54_CONVERGENCE_PASS`이며, `PHYSICAL_PRODUCTION_CROSS_SECTION`은 주장하지 않는다. stochastic-vs-coherent dynamics, low-energy trajectory validity, upper-shell semantics, exponent normalization, rotational matching-radius authority는 계속 OPEN이다. 구조화된 수치는 `evidence/DR8_ADAPTIVE_SURROGATE_STUDY.json` 및 `evidence/DR8_FINAL_VERIFICATION.json`에 기록한다.
