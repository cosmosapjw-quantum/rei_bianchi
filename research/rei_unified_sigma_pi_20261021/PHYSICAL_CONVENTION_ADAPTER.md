# LRS Bianchi I physical convention adapter and constructive result

작성일: 2026-10-21 KST. 범위: 통합 D2, 제한된 collisionless PR198 lane 및 다른 lane과의 명시적 변환. 원래 계산 재실행은 0회다. 새 계산은 두 번의 Wolfram 기호 검산과 고정 PR198 순간량의 국소 미분 검산이다.

## 1. 고정 정의와 근거 상태

Signature는 (-,+,+,+), t는 proper seconds, H=dot a/a, s=dot b,
a_perp=a exp(-b), a_parallel=a exp(2b)다. 정상 congruence의 공변 orthonormal 성분은

sigma_hat=diag(-s,-s,2s), pi_X_hat=diag(-p_X,-p_X,2p_X),

이며 X=m,r이다. pi의 scalar p_X는 등방 평균압 pbar_X와 별개이고
D_X=P_parallel,X-P_perp,X=3p_X다. epsilon 또는 rho가 J/m³로 저장될 때 Einstein proper-time 계수는 K=8 pi G/c²다. 문헌에서 c=G=1로 적은 계수를 그대로 SI 변수에 적용하지 않는다.

| 양 | half contraction | full spatial Frobenius |
|---|---|---|
| shear norm | sqrt(3) abs(s) | sqrt(6) abs(s) |
| Sigma | sqrt(3) abs(s)/H | sqrt(6) abs(s)/H |
| stress norm | sqrt(3) abs(p_X)=abs(D_X)/sqrt(3) | sqrt(6) abs(p_X)=sqrt(2/3) abs(D_X) |
| Pi_X | sqrt(3) K abs(p_X)/H² | sqrt(6) K abs(p_X)/H² |

Signed 변수는 S=sqrt(3)s/H, P_X=sqrt(3)Kp_X/H²로 쓴다. 따라서 Sigma_half=abs(S),
Pi_tot,half=abs(P_m+P_r)다. 성분별 절댓값의 합은 총 tensor norm과 별도의 진단량이다.
Frobenius 값은 signed/unsigned 모두 동일 convention에서 sqrt(2)배다.

Heinzle–Uggla의 dynamical-systems 변수는 추가로 Sigma_lit²=(1/6)sum_i(sigma_i/H)²=s²/H²를 쓴다.
이 문헌 변수의 크기는 Sigma_half/sqrt(3)다. 문헌의 Sigma라는 이름만 보고 pilot 저장값에 그대로 대입하지 않는다.

근거 상태: 위 항등식은 **derived**, Wolfram 기호 검산으로 **implementation-verified (symbolic scope)**.
아래 source mapping은 회수한 실제 Python 바이트에서 확인했다. 다른 lane의 실제 저장 convention/물리 identity 판정은 그 lane의 ledger와 함께 확정한다.

## 2. Einstein equation의 부호와 보존식

혼합 공간 Ricci 성분의 차이는

c²(R^parallel_parallel-R^perp_perp)
= dot H_parallel-dot H_perp+3H(H_parallel-H_perp)
=3(dot s+3Hs).

Einstein 방정식의 해당 차이는 3K p_tot이므로

dot s+3Hs=K(p_m+p_r).

이 식은 k_ij=-dot h_ij/2인 ADM convention에서 k^i_j=-H_i delta^i_j와도 일치한다.
반대 부호의 extrinsic curvature를 쓰는 코드에서는 k에서 s로의 사상까지 함께 바꿔야 한다.

Hamiltonian constraint와 그 미분은

H²=K epsilon/3+Lambda c²/3+s²,
dot H=-K(epsilon+pbar_tot)/2-3s².

각 collisionless 성분의 에너지 보존은

dot rho_X=-3H(rho_X+pbar_X)-6s p_X,

이고 radiation은 pbar_r=rho_r/3이다. x=ln(a/a_ref)이므로

rho_m'=-3(rho_m+pbar_m)-6(s/H)p_m,
rho_r'=-4rho_r-6(s/H)p_r.

Wolfram에서 위 세 미분식을 Friedmann constraint 미분에 대입하면 residual은 정확히 0이다.
K epsilon과 K p는 s^-2, s p는 J m^-3 s^-1, x-미분 work term은 J m^-3이다.

Signed shear의 직접 계산식은

S'=-(3+h)S+P_m+P_r,  h=H'/H.

같은 내용의 적분형은

a³s=a_i³s_i+K integral[t_i,t] a(tau)³ p_tot(tau) d tau.

이 식은 instantaneous cancellation과 time-integrated geometric response를 구분하는 데 유용하다.
p_tot(t_i)=0은 그 한 순간의 source만 정한다.

## 3. 실제 PR198 source와 수식의 대응

회수 위치: source_snapshots/PR198/. 아래 hash들은 cancellation_curvature_check.json에도 기록했다.

| 물리 내용 | 실제 source object | 확인한 구현 |
|---|---|---|
| 단위 환산 | vendor/lrs_boltzmann.py::SourceLock.rhocrit_j_m3 | 3 c² H0²/(8 pi G), 따라서 K rho_crit=3H0² |
| massive phase space | vendor/canonical_fv.py::CanonicalMomentumFV | conserved Killing momenta, positive Fermi momentum profile, W_m=1+A_m P2 |
| 순간량 | CanonicalMomentumFV.moments / moment_batch | q_perp² proportional exp(-2x+2b), q_parallel² proportional exp(-2x-4b); p_s=(P_parallel-P_perp)/3 |
| Hamiltonian | pilot.py::Reduced.rhs / diagnostics | H²=H0²[dust+massive+radiation+Omega_Lambda]+s² |
| shear | pilot.py::Reduced.rhs, state[2]=s/Href | state[2]'=-3 state[2]+3H0² p_norm/(Href H) |
| radiation energy | lrs_boltzmann.py::legendre_matrix(power=4) | matrix monopole row has only entry (0,2)=-2; this gives exact anisotropic work |
| independent initial matter/radiation axes | matter_radiation_20261021/component_pilot.py::ComponentReduced.initial | A_m root for matter target, separate alpha_r for radiation; targets checked against realized axes |
| signed components and work | component_pilot.py::components | p_m and p_r separately converted to J/m³, signed P_X, work_X=-6(s/H)p_X |
| reduced radiation | pilot.py::Reduced | one common even energy vector E_0,E_2,...,E_8 for photons+exactly massless neutrinos |

Frozen file SHA256:

- pilot.py: 4cf3db0a6d2bc4803e87dcffe422faa3ebe9478bf23a16e02a9f16fe5c2e4400
- vendor/canonical_fv.py: 91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5
- vendor/lrs_boltzmann.py: 06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc
- matter_radiation_20261021/component_pilot.py: e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e

vendor/REI_BACKGROUND_FAMILY_LOCK.json의 실제 소비 필드는 cosmology의 H0/Omega들과 clock의 a_ref/a_end다.
그 파일에 남은 Sigma_definition='s/H', stress-free background 설명은 더 오래된 family의 메타데이터다.
현재 pilot의 계산 convention은 executable diagnostics의 sqrt(3)abs(s)/H다. 이 차이는 별도 삭제나 원본 수정 없이 adapter에 명시한다.

PR198 restricted reduced source는 common E_gamma=E_nu, 같은 초기 angular brightness, collisionless evolution을 이용한다.
일반 SpeciesHierarchy에는 독립 gamma/nu state와 photon-only Thomson 경로가 있지만, 해당 경로의 존재만으로 PR198 reduced 실행에 그 기능이 사용되었다고 판정하지 않는다.
Massive fraction fm=0.1은 나머지 cold dust와 분리된 비바리온 collisionless 성분이다. 이 source에서 cold dust의 anisotropic stress는 0이다.

F(q)=1/(exp(q)+1)는 conserved dimensionless momentum q의 분포다.
물리적 표기로 q=c p_ref/(k_B T_ref), M=m c²/(k_B T_ref)라 두면 코드의 dimensionless energy는 sqrt(M²+q²)다.
M=30인 분포를 nonrelativistic thermal equilibrium F(E/k_B T)로 해석하지 않는다.

## 4. 새로운 local cancellation-curvature 결과

### 전제

초기 b=0, S_0=0, p_m0+p_r0=0; 각 성분은 reflection-even이고
f_X(q,mu)=F_X(q)[1+A_X P2(mu)]이다. Massive species에는 M>0,
radiation에는 정확히 m=0을 사용하고 collision term은 없다.
W>=0의 정확한 조건은 -1<=A<=2다. 이 조건은 Wolfram의 quantified polynomial reduction으로 확인했다.

초기 angular 평균은 <P2>=A/5, 따라서

p_m0=A_m pbar_m0/5,
p_r0=A_r rho_r0/15.

이것은 초기 isotropic reference geometry에서의 식이다. b가 바뀌면 실제 순간량 적분을 사용한다.

### 유도

S_0=0에서 순간적인 momentum redshift는 isotropic하다.
massive anisotropic pressure는 같은 angular factor를 분리하여

p_m(x)=C A_m exp(-5x) integral q^4 F_m(q)/sqrt(M²+q² exp(-2x)) dq

형태로 쓸 수 있다. 상수 C는 angular normalization, 단위와 number normalization을 포함한다.
그러므로 x=0에서

p_m' = (-5+B_m)p_m,

B_m =
[integral q^4 F_m(q)/sqrt(M²+q²) * q²/(M²+q²) dq]
/
[integral q^4 F_m(q)/sqrt(M²+q²) dq].

B_m은 pressure-weighted v²/c²이며 양의 massive 분포에서 0<=B_m<1이다.
동일 순간 massless radiation은 p_r'=-4p_r이므로 cancellation 조건에서

(p_m+p_r)'_0=-(1-B_m)p_m0.

S'=-(3+h)S+P_tot를 한 번 더 미분하고 S_0=S'_0=P_tot,0=0을 사용하면

**S''_0=-(1-B_m) P_m0.**

따라서 x=0 근방에서

S(x)=-0.5(1-B_m)P_m0 x²+O(x³).

이 결과는 초기 cancellation의 실제 순간 변화 방향을 결정한다.
positive matter / negative radiation 초기 cancellation이면 초기 signed shear curvature는 음수다.
Endpoint의 크기나 전체 구간 부호는 이후 coupled evolution으로 정한다.

### 고정 source의 새 경량 검산

source의 24×12 cells, Gauss3, M=30을 그대로 사용하여

B_m = 0.031700764390593536,
A_m = 0.8274981492286657,
A_r = -0.18946529412404806

을 얻었다. 실현된 P_m0=0.00039999999999999975이고

S''_0 = -0.0003873196942437623.

4차 전진 미분 h=1e-3,1e-4,1e-5의 상대 차이는 각각
5.4060e-12, 2.3534e-11, 2.3065e-10이다.
이는 새 국소 미분식의 검산이며 기존 trajectory를 적분하지 않았다.
기록은 check_cancellation_curvature.py, cancellation_curvature_check.json,
wolfram_checks.json, wolfram_cancellation.json이다.

판정: **derived + numerically checked**, 고정 source 순간량 매핑에 한해 **implementation-verified**.
새 보편 no-go/novelty claim을 제기하지 않으므로 NG1–NG7 새 no-go admission은 적용 대상이 아니다.

## 5. Cross-lane adapter의 추가 주의점

PR213의 SPLIT_CONTRACT 및 split_sweep.py에서는 stress 변수 D_X가 pressure difference다.
따라서 D_X=3p_X이고 signed Pi=K D_X/(sqrt(3)H²)라면 PR198 signed Pi와 일치한다.
그 source는 half-contraction 및 Frobenius 값을 함께 저장한다.

또한 PR213 shear_work_X_J_m3_s=+2s D_X=+sigma:pi_X인 반면,
PR198 work_X_J_m3_per_x=-6(s/H)p_X=-sigma:pi_X/H다.
동일 물리 상태의 비교식은

work_PR198 = -work_PR213/H.

PR213 recovered contract는 a=.1999→.2, 즉 z≈4.00250125→4의 짧은 창이다.
PR198는 a=1/21→.2, 즉 z=20→4다.
Norm 사상이 같아도 구간, source, collision/UV/native coupling 및 initial distribution이 다르면
IDENTICAL_REUSABLE_CASE로 판정할 수 없다. 원자료 identity와 물리 계약을 모두 확인한다.

## 6. z=4→2가 실제로 누락됐을 때의 restart 검토

이 절은 D1이 전체 목표 구간의 누락을 확인할 때만 활성화한다.
다른 회수 lane이 이미 목표를 충족하면 불필요한 새 실행을 prune한다.

PR198 8-state endpoint를 유지한 restart는 Markov 초기값 문제의 정확한 continuation이다.
x_start=ln(21/5), x_end=ln7이고, a_end만 1/3로 확장한다.
기존 Href, a_ref, cosmology, fm, M, angular/radial grid, tolerance, L=8과 RHS는 보존한다.
state[0]=elapsed_seconds*Href는 원래 z=20 기준 accumulator를 유지한다.
b와 s/Href 및 모든 even E_l도 saved endpoint 바이트에서 이어간다.
A_m은 각 case receipt의 값을 재사용한다. 초기 axis calibration을 다시 풀지 않는다.

625 parent cases의 component-decomposition NPZ에는 state가 없으므로 원래
results/pilot/cases/*.npz를 사용한다. 신규 606개의 원래 component NPZ에는 state가 있다.
25 neutral controls는 기존 reference reuse이므로 새 trajectory로 중복 합산하지 않는다.

새 32 samples를 x4 제외, x2 포함으로 저장하면 기존 65 samples와 합쳐97개다.
join state가 정확히 원래 raw endpoint임을 검증하고,
새 구간에서 positive H/E0, finite state, massive nonnegative weights,
sampled brightness positivity, initial/parent hash 및 case uniqueness를 검사한다.
대표 2개 tail의 tighter-tolerance comparison은 새 구간의 integration error를 평가한다.
이 검토 범위는 고정 L=8 source이며 새로운 angular convergence 주장에는 해당하지 않는다.

## 7. 실제 재사용할 외부 근거와 optimization 결정

Heinzle–Uggla, Class. Quantum Grav. 23 (2006), DOI 10.1088/0264-9381/23/10/016,
arXiv:gr-qc/0512031, section2 equations(2d–f),(3),(5),(12–13)는
conserved covariant Killing momentum, stress moments, reflection symmetry,
normalized dynamical equations의 1차 근거다. 본 source의 constant canonical cell weights가 그 구조를 재사용한다.
이 논문의 single-species, Lambda=0 asymptotic 정리를 multi-sector pilot endpoint certificate로 사용하지 않는다.

Rendall–Uggla, Class. Quantum Grav. 17 (2000), DOI 10.1088/0264-9381/17/22/310,
arXiv:gr-qc/0005116는 massive LRS Einstein–Vlasov와 massless/dust asymptotics의 근거다.
Calogero–Heinzle, Physica D240 (2011)636–669, DOI 10.1016/j.physd.2010.11.015,
arXiv:0911.0667는 LRS anisotropic matter models의 broader dynamics를 비교하는 근거다.
SciSpace의 발견 메타데이터는 원래 arXiv의 2000/2009 논문을 2022로 표기했으므로
연도와 DOI는 arXiv 원본으로 교정했다.

SciPy official solve_ivp 문서는 DOP853를 높은 정확도가 필요한 non-stiff IVP에 권고한다.
vectorized=True는 독립 trajectory ensemble API가 아니다.
공식 문서는 이 옵션이 Radau/BDF의 finite-difference Jacobian에 도움이 되지만
다른 method나 작은 state에서는 오히려 느릴 수 있음을 명시한다.
따라서 이 작업에서는 검증된 DOP853를 유지하고 NumPy moment batch와 trajectory-level processes를 재사용한다.

Python3.12 ProcessPoolExecutor의 initializer 또는 multiprocessing Pool initializer를 이용하면
worker마다 읽기 전용 basis/matrix를 한 번 생성하고, 독립 case checkpoint를 쓸 수 있다.
BLAS thread 수를1로 제한하는 기존 source는 process 병렬성과 내부 BLAS 병렬성의 중첩을 줄인다.
사용가능 CPU affinity/cgroup/RAM/disk를 실행시 확인하여 worker 수를 정한다.
장시간 benchmark나 backend rewrite는 본 판정의 근거/요구사항이 아니다.

초기 massive angular weight가 1+A P2에 선형이고 reference angular monopole normalization이 A와 무관하므로,
같은 fixed cosmology에서 P_m0도 A에 선형이다.
향후 새 case 설계에서는 immutable monopole/quadrupole packet basis 재사용과 직접 선형 calibration을 고려할 수 있다.
현재 완료된606개 case를 이 이유로 다시 계산하지 않는다.

## 8. 1차 출처

- https://arxiv.org/abs/gr-qc/0512031
- https://pure.mpg.de/rest/items/item_150627_1/component/file_150626/content
- https://arxiv.org/abs/gr-qc/0005116
- https://arxiv.org/abs/0911.0667
- https://arxiv.org/abs/gr-qc/9505017
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- https://docs.scipy.org/doc/scipy/tutorial/parallel_execution.html
- https://docs.python.org/3.12/library/concurrent.futures.html

외부 검색11개 Exa results와 SciSpace10개 후보에서 관련 1차 자료만 채택했다.
문헌의 근거와 본 문서의 직접 유도/국소 계산은 위 각 절에 구분했다.

## 9. Lane B의 실제 회수 이후 확정된 추가 매핑

D1 회수 source: recovery_backups/laneB_recovered/package/.
original91+3은 별도 full-state source를 실행했고, wrapper는 실행 SHA256으로 식별한다.
역사적 publication parent가 PR199였다는 사실과 실제 실행 wrapper가 Git에 게시됐다는 사실은 구분한다.
원래 wrapper에는 UNPUBLISHED_WITH_SHA256 identity를 유지한다.

네 파일 canonical_fv.py, species_hierarchy.py, lrs_boltzmann.py,
REI_BACKGROUND_FAMILY_LOCK.json은 A와 B 사이 byte-identical임을 직접 확인했다.
B의 kernel pin은 PR147 3b85dedce84d37b3e165da00685a8a984950aafe다.

| 항목 | A PR198 | B recovered original/component |
|---|---|---|
| 저장 norm | half contraction | full Frobenius와 half를 둘 다 저장, grid는 Frobenius |
| nominal radiation/geometry state | 8-state even common energy vector | 40-state separate gamma/nu energy+number plus geometry/zero thermal accumulator |
| refined source | A 이전 검토 범위 참조 | 56-state L12,48×24Gauss3 |
| physics kernels | canonical massive Vlasov + collisionless common massless IC | 같은 vendor bytes, separate massless state가 같은 초기조건/연산자로 진화 |
| 시간 구간 | z20→4 | 기존 z20→4, 요청한 새 tail z4→2는 별도 실행 |
| 사용 가능한 case reuse | A 내부 original625 및 신규606 유지 | B original91 중 component grid와 동일한35만 exact reuse |
| A/B 관계 | explicit norm/state adapter 뒤 비교 | 코드 실행 identity와 grid가 다르므로 automatic raw-case substitution은 안 함 |

B의 component_adapter.py에서 A_m=P_m/K_m, alpha_r=P_r/K_r는 Frobenius target에 대한 직접 선형 calibration이다.
reference angular monopole normalization의 A_m 독립성, positive quadrature 및 고정 H_i로부터 정확히 유도된다.
Refined guard는 바뀐 radial quadrature에서 같은 물리 target을 다시 calibration한다.
실제 실행 전 gate가 승인된 원 contract hash는
af54cb19a9ed9cbfe39f8b27ca6db8b57524ed86a5079ca6cf892a990d3187c8이다.

새 unified contract는 B1의140 nominal+3 refined만 추가하고35 references의 원 raw를 유지한다.
B2는 그 결과143와 original94의 full endpoint를 합친237개 unique state를 z4→2로 연장한다.
237=231 nominal+6 guards이며,175 joint-grid points와91 radiation-baseline points는35개를 공유한다.
이 수를 더해266개의 독립 nominal IVP라고 쓰지 않는다.

B2의 old121+new32=153 sample 원칙, x4=ln(21/5)→ln7,
40/56 entries 전부 보존, proper-time accumulator 보존,
original6 guard/nominal pairs의 z2 endpoint comparison<=2e-6는
해당 변경 구간에 맞는 PHYS-MATH contract다.
original.validate의 hard-coded121 epochs/a_end=.2 조건은 B1에 유지하고,
B2에는 새32 tail 및153 joined sample의 endpoint 조건을 별도 구현한다.
새 tail 시작값을 z20 physical-axis calibration gate에 잘못 대입하지 않는다.

최종 prereview: UNIFIED_EXECUTION_CONTRACT.md에 대한 PHYS_MATH_CONTRACT_REVIEW.json 참조.
계약 승인과 새 code/raw/figure 검토는 별개의 상태다.


