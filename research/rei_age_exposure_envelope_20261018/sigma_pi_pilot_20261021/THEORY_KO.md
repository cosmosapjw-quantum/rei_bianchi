# Non-tilted Bianchi I Sigma–Pi pilot: 이론과 최적화 선택

2026-10-21 (Asia/Seoul). 식은 아래 명시한 모형에서 derived, 기존 구현은 PR145/147 source intake로 확인했다. 새 격자의 numerically checked 상태는 RUN_RECEIPT와 독립 검토를 따른다. 입력·검사·예산의 정확한 계약은 PILOT_CONTRACT.md다.

## 1. 계산 대상과 tensor convention

첫 pilot은 non-tilted Bianchi I의 축대칭 LRS 부분공간에서 초기 \((\Sigma_i,\Pi_i)\)를 독립적으로 조절하고, \(z_{\rm bar}=20\to4\) 동안 Einstein–kinetic 배경을 진화시킨다. 양의 초기 전단 orientation과 anisotropic stress의 양·음 두 sheet를 보존한다. \(\Pi_i=0\) 중복을 제거한 91개 초기값이다.

Cold dust, 우주상수, 광자/질량 없는 중성미자 energy·number hierarchy, canonical-momentum massive Vlasov species를 포함한다. Massive species에는 전체 \(\Omega_m\)의10%를 할당하고 cold dust에서 동일하게 뺀다. 초기 massive 분포는 isotropic, \(mc^2/(k_BT_{\rm ref})=30\)이다. 공통 photon/nu 초기 quadrupole로 \(\Pi_i\)를 지정한다.

Species 할당과 tensor orientation은 2차원 parameter plane을 정의하는 추가 물리 조건이다. Norm 두 개만으로 일반 Bianchi I 초기자료 전체가 정해지지는 않는다. 이 source-free kinetic background에는 native H/He thermal/ionization feedback, stellar UV emission, polarized Thomson이 포함되지 않는다. 기존 age/time HOLD와 production admission NOT_ISSUED를 보존한다.

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,\qquad
H=\dot a/a,\quad s=\dot b.
\]
직교 공간 frame에서
\[
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s),\quad
\pi^i{}_j=\operatorname{diag}(-p_s,-p_s,2p_s),\quad
p_s=(P_\parallel-P_\perp)/3.
\]
그러므로
\[
\sigma_{ab}\sigma^{ab}=6s^2,\quad
\pi_{ab}\pi^{ab}=6p_s^2,\quad
\sigma_{ab}\pi^{ab}=6sp_s.
\]

Public axis는 Frobenius norm을 사용한다:
\[
\Sigma_F=\frac{\sqrt6|s|}{H},\qquad
\Pi_F=\frac{\sqrt6\kappa_t|p_s|}{H^2},\qquad
\kappa_t=\frac{8\pi G}{c^2}=c^2\kappa_E,\quad
\kappa_E=\frac{8\pi G}{c^4}.
\]
\(p_s\)는 J/m³, H는1/s이므로 \(\kappa_t p_s\)는1/s²다. Einstein coefficient \(\kappa_E\)를 사용할 경우 \(\Pi_F=c^2\kappa_E\|\pi\|/H^2\)라고 적어야 dimensionless가 된다. H/c를 역길이로 쓰는 geometric convention과 동등하다.

기존 PR145/147의 Sigma는
\[
\Sigma_{\rm half}=\sqrt{\sigma_{ab}\sigma^{ab}/2}/H
=\sqrt3|s|/H=\Sigma_F/\sqrt2.
\]
두 값을 모두 출력하고 adapter에서만 변환한다. 기존 Pi_*_J_m3는 species별 \(p_s\) coefficient다. 총 norm은 signed coefficient들을 먼저 합산하여 계산한다:
\[
p_s=\sum_Ap_{s,A},\qquad
\Pi_F=\frac{\sqrt6\kappa_t}{H^2}\left|\sum_Ap_{s,A}\right|.
\]
Species norm을 먼저 더하면 cancellation이 사라진다. Signed \(\Pi_{F,s}\)와 shear \(s\)를 저장한다. Signed shear norm \(\Sigma_{F,s}=\sqrt6s/H\)는 저장된 \(s,H\)로 정확히 재구성하며 endpoint 그림에도 이 부호를 보존한다.

Wolfram evaluator에서 trace와 contraction 결과 \((0,0,6s^2,6p_s^2,6sp_s)\)를 확보했다. Undefined symbolic H 경고는 변수 H가 있는 식에서 발생했다. 선행 WolframContext 호출은 internal error였고 검색 성공으로 기록하지 않는다.

## 2. Einstein–kinetic 일치의 직접 유도

Energy density \(\rho\)와 평균 pressure \(\bar p\)를 J/m³로 쓰면
\[
3H^2=\kappa_t\rho+\Lambda c^2+3s^2,\qquad
\dot s+3Hs=\kappa_t p_s,
\]
\[
\dot\rho+3H(\rho+\bar p)+6sp_s=0.
\]
Hamiltonian constraint를 미분하여
\[
6H\dot H
=\kappa_t[-3H(\rho+\bar p)-6sp_s]
+6s[-3Hs+\kappa_t p_s]
=-3\kappa_tH(\rho+\bar p)-18Hs^2
\]
를 얻는다. 따라서 expanding branch H>0에서
\[
\dot H=-\tfrac12\kappa_t(\rho+\bar p)-3s^2.
\]
Anisotropic work 항이 정확히 상쇄된다. 원 code의 energy monopole \(J'_0=-2(s/H)J_2\), \(p_s=\rho_{\rm ref}J_2/(3a^4)\)는 같은 \(-6sp_s\) work를 구현한다. Prime은 \(x=\ln(a/a_i)\) 미분이다.

H가 constraint로 직접 계산되므로 numerical Hamiltonian residual은 조립 일관성 검사다. 독립적인 dynamics 오차 추정은 세 refined corner와 보존량·양성성 검사로 구분한다.

## 3. 입력 norm에서 실제 분포로 가는 map

\(b_i=0,a_i=1/21\)에서 원 source의
\[
H_{\rm ref}^2=H_0^2D_i,\qquad
D_i=\Omega_ma_i^{-3}+\Omega_ra_i^{-4}+\Omega_\Lambda
\]
를 유지한다. Massive initial energy norm이1이므로 matter budget은 같다.
\[
H_i^2=\frac{H_{\rm ref}^2}{1-\Sigma_{F,i}^2/6},\qquad
s_i=\frac{\Sigma_{F,i}}{\sqrt6}H_i.
\]
Positive-density branch는 \(\Sigma_{F,i}<\sqrt6\)다.

Photon/nu 초기 brightness \(W(\mu)=1+kP_2(\mu)\), \(k_\gamma=k_\nu=k\)에서 \(\langle P_2^2\rangle=1/5\)이므로 \(E_2=N_2=k/5\). Monopole은 k와 독립이고
\[
p_{s,\mathrm{rad},i}
=\frac{\rho_{\rm crit,0}\Omega_r k}{15a_i^4},\qquad
\rho_{\rm crit,0}=\frac{3c^2H_0^2}{8\pi G}.
\]
따라서
\[
k=\frac{5a_i^4H_i^2}{\sqrt6H_0^2\Omega_r}\Pi_{F,s,i}.
\]
실제 초기 state에서 이 map을 다시 검산한다.

원 API의 \(|k|\le1/2\) 안에서는 \(W\ge1-|k|\ge1/2\). 독립 계약 검토에서 이번 grid의 최대 \(|k|=0.33548963507834245\), 양·음 sheet의 \(W_{\min}=0.6645103649216575\)를 확인했다. 고정 species family의 domain은
\[
\Pi_{F,i}\le\frac{\sqrt6}{10}\frac{\Omega_ra_i^{-4}}{D_i}
\left(1-\frac{\Sigma_{F,i}^2}{6}\right).
\]
이는 이번 radiation-allocation family의 입력 조건이며 다른 matter model을 배제하는 정리가 아니다.

## 4. Canonical momentum과 재사용

Bianchi I spatial Killing momentum은 collisionless geodesic에서 일정하다. Reflection-even 분포는 energy flux0과 양립한다. Conserved covariant momentum과 stress integrals는 Heinzle–Uggla(2006),section2의 Einstein–Vlasov formulation에서 확인했다.

초기 physical momentum을 \(q=cp_i/(k_BT_{\rm ref})\), \(M=mc^2/(k_BT_{\rm ref})\)로 무차원화하면
\[
\frac{E}{k_BT_{\rm ref}}
=\sqrt{M^2+e^{-2x}q^2[(1-\mu_i^2)e^{2b}+\mu_i^2e^{-4b}]}.
\]
Canonical populations는 일정하고 metric-dependent energy/pressure weight만 다시 평가한다. Distribution remapping이나 spatial grid가 필요하지 않다. 원24×12cells,Gauss3는2592packets이며 NumPy 배열 연산으로 moments를 계산한다.

PR147 pin3b85dedce84d37b3e165da00685a8a984950aafe에서 최소 Python3개와 lock,MIT license를 재사용한다. Active dynamics는 PR145/147 RHS이며, lock의 역사적 stress-free q_ref prescription은 active equation으로 가져오지 않는다. Lock의 cosmology와 clock만 채택한다.

## 5. 이번에 채택하는 최적화

| 변경 | 제거하거나 제한하는 비용 | 물리 보존 조건 |
|---|---|---|
| Worker별 Legendre matrix cache | Case마다 반복하는 quadrature/polynomial setup | (L,order,power) 전체 key,immutable array |
| Worker별 SourceLock | 동일JSONparse/hash | Exact source bytes |
| 고정 massive packets 공유 | 동일 canonical grid/weights 구축 | Mass,amplitude,resolution key 동일 |
| 독립 process IVP | 가장 어려운 case가 전체 adaptive step을 제한 | 각 DOP853와 error norm 독립 |
| BLAS/OpenMP1 | Process×inner threads oversubscription | Import 전에 적용 |
| Case checkpoint/resume | 중단 뒤 완료 계산 반복 | Source+input identity 일치 |
| 가용자원 dispatch | 타 세션 때문에 host 전체 STOP | 자기 worker 수만 조절,nice10 |

Gamma와 nu의 초기 brightness 및 collision operator가 같으면 동일 ODE의 유일성으로 두 hierarchy의 equality가 유지된다. Odd multipole은 reflection-parity invariant subspace다. 후속 state reduction의 근거는 되지만 이번 pilot은 원 state norm과 adaptive step 규칙을 그대로 사용한다.

PR210/211 rate sharing/T-table은 native chemistry 연결 때 재사용할 수 있다. 현재 collisionless background에는 rate evaluation이 없으므로 그 도입은 이번 pilot의 필수 최적화가 아니다. VigilODE PR77의 특수 band-plus-rankone 구조도 현재 RHS와 동일하다고 확인되지 않아 solver를 교체하지 않는다.

새 speedup ratio,64core scaling 또는 peak-memory reduction을 주장하지 않는다. 이번 성과는 반복 setup 제거, 독립 dispatch, 공유 자원 운영의 실제 코드와 pilot 결과다.

## 6. 검증 범위

DOP853 rtol3e-11,atol3e-13은 원값이다. 모든 nominal case에서 finite state,endpoint,positiveH,canonical nonnegativity, 원number tolerance5e-11,initialnorm mismatch5e-12,64angular-node sampled brightness를 검사한다. 기존 fullsuite/native/benchmark는 반복하지 않는다.

새 domain의 세 corners만 L12,48×24,Gauss3로 계산한다. \(\Sigma_F,\Pi_{F,s},b\) endpoint absolute difference와 H relative difference2e-6은 이번 preliminary stability gate다. PR199의0.005 chemistry criterion을 대체하지 않는다. 세 점의 결과를 global error bound로 확대하지 않는다.

## 7. 1차 자료

- Heinzle & Uggla, CQG23(2006)3463–3489,doi:10.1088/0264-9381/23/10/016, [primaryPDF](https://pure.mpg.de/rest/items/item_150627_1/component/file_150626/content),section2equations(2)–(4). Conserved covariant momentum,reflection symmetry,stress integrals를 현재SI/LRS convention으로 연결했다.
- Lee,Nungesser&Tod,[arXiv:1911.04937](https://arxiv.org/abs/1911.04937): small-anisotropy massless asymptotics의 문헌 위치를 SciSpace/Exa로 확인. 이번 massive+dust+Lambda finite pilot에 그 theorem을 적용하지 않는다.
- [PR147 source](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/3b85dedce84d37b3e165da00685a8a984950aafe/research/rei_bass_hierarchy_backreaction_20261015): active code와 기존 finite-resolution evidence.
- [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html), [Python process execution](https://docs.python.org/3/library/concurrent.futures.html): 선택한 integrator와 process API의 공식 자료. 구현은 실제Python3.12에 있는 API만 사용한다.

Fresh source/backup coverage와 exact pins는 intake보고서에 기록했다. REI/VigilODE의 전체 branch/PR metadata pagination은 완료됐고, 상세 source는 관련 후보를 읽었다. 모든 과거 대화·모든 branch bytes를 읽었다고 표현하지 않는다.

