# F4: 원본 BASS21 저장 이력의 자기일관적 순간 화학평형과 비평형 기억

**범위/출처:** original BASS owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`, 원본 193-epoch trajectory SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`, 원래 BASS AtomicNetwork Python byte SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`. 수치 원본은 read-only PR276 full source archive SHA256 `58815601324ade9871077236dccee25cbbfe126141ee9af3d7da9ed9ffdb56f2`에 중첩된 original BASS saved trajectory이며 **새 IVP는 수행하지 않는다**.

## 방정식과 구체적 구성

원래 BASS의 H1, D, He3, He4, Li6, Li7의 양의 핵종 총수 `N_i=sum_q Y_{iq}`는 본 *pilot*에서 보존된다 (n/T 원래 초기 0, 관련 weak transfer 0). `Y=n_species/n_b`, `n_e=n_b q^T Y`, `x=ln(a/a_ref)`, `H=dx/dt>0`. 21종 BASS native photo+RR+DR+weak source는 별도의 원본이고, 본 연구는 초기 n/T=0에서 내부 6개 비영 핵종의 전하재분배만 다룬다. 외부 `T(z)`, `UV(z)`, `n_b(z)`, `H(z)`는 저장된 원본 BASS 값이며 BASS 광원은 원래 prescribed external field이다. PR259 ON_refined의 **300 K bath/REI17**을 대체하거나 부르는 계산이 아니다.

핵종 i, 전하 q=0..Z_i에 대해 원래 BASS `rates`의 upward 광전리율 `lambda_iq=photo_s[i,q]` [s^-1] 및 downward 방사+dielectronic 재결합 계수 `alpha_i,q=rr_m3_s[i,q]+dr_m3_s[i,q]` [m^3/s]를 이용한다. 고정된 양의 `n_e`, `T`, `UV`에서 charge-generator `M_i(n_e)`는 

`(M_i)_{q+1,q}=lambda_iq`, `(M_i)_{q-1,q}=n_e alpha_iq`, `1^T M_i=0`; 모든 off-diagonal은 비음수이다. **자기일관적 순간 평형**은 `M_i(n_b x_e*)Y_i*=0`, `sum_q Y_iq*=N_i`, `x_e*=sum_i sum_q q Y_iq*`의 대수적 연립계이다.

이를 직접 풀 수 있다. 양의 계수를 가지는 source의 현재 193점에서

\[
\pi_{iq}(n_e) =\frac{c_{iq}\, n_e^{-q}}{\sum_{r=0}^{Z_i} c_{ir}\,n_e^{-r}},\quad c_{i0}=1,\quad c_{iq}=\prod_{k=0}^{q-1}\frac{\lambda_{ik}}{\alpha_{i,k+1}}.
\]

여기서 `n_e` [m^-3], `c_iq`가 상응하는 단위를 가져 전체 상대비가 무차원이다. `pi`는 비음수, 총합1. 이것은 단일 핵종의 **조건부** 전자밀도에 대한 birth-death stationary distribution이며 최종 전자밀도도 동시에 찾아야 한다.

## 유일성과 엄밀한 범위

`m_i(n_e)=sum_q q*pi_iq`, `v_i=sum_q(q-m_i)^2 pi_iq>=0`라 정의하면

\[
\frac{\mathrm d m_i}{\mathrm d\ln n_e}=-v_i,
\qquad
G(x)=\sum_i N_i m_i(n_bx)-x,
\qquad
G'(x)=-1-\frac{\sum_i N_i v_i}{x}<0\quad(x>0).
\]

현재 193 source point에서 모든 `lambda>0,alpha>0`이므로 `G(0+)=sum_i N_i Z_i>0`; 반면 `G(sum_i N_i Z_i)<0`이고 따라서 **유일한 양의 자기일관적 평형 전자분율** `x_e*`가 존재한다. 이 유일성은 원래 BASS의 특정 finite-source 조건에서 성립한다. UV가 정확히 0이거나 추가 입자 생성/소멸, 외부 금지 반응을 더하는 다른 모형의 보편적인 theorem은 아니다. `Wolfram` 실제 상징 검산: `n*d<q>/dn+Var(q) -> 0` (four-charge generic positive coefficients), 2-state 추가 체크 0.

## 저장 이력과 평형의 물리적 비교

7개의 예시가 아닌 **원본 193개 BASS 저장 epoch**에서 original `Y,T,UV,nb,H`로 193차례 독립적인 algebraic scalar root `G(x_e*)=0`을 구한다. 검증 결과 최대 absolute fixed-point residual `8.881784197001252e-16`, 최대 native `F21(Y*)` residual `3.8456969129524326e-30 baryon^-1 s^-1`, 193x6 총 1158개 signed/formatted isotope rows 저장. `Y_i` 원본 isotope totals와 평형 `Y_i*`는 동일한 BASS native inventory를 사용한다.

- 초기 `z=20` BASS saved `x_e=1.5099503200860547e-4`, `x_e*=5.481402546679904e-7`; **평형이라면** 순간 electron/Thomson opacity rate의 비율 `x_e*/x_e-1=-0.9963698` (광학깊이 적분 아님).
- 최대 **절대 electron difference**는 저장 `z=10.316825125`, actual `0.11228197304710612`, instantaneous equilibrium `0.21640086318509405`, 차 `+0.10411889013798793` electron/baryon. H1의 TV 거리 최대 `0.130138934688`가 같은 지점에서 나타난다.
- `z=2` BASS saved `0.8774564518451783` vs equilibrium `0.8774564664487833`, 차 `1.46036e-8`.
- He4 TV 최대 `0.10270881986` at `z=9.9779171301`; Li7 TV `~0.9999981` at `z=20`에서 `~4.4895e-5` at `z=2`. Li 원본 초기 charge가 +1로 정해진 것과 100 K 극저 UV의 평형이 다르다는 **source 모델 내부 결과**이다.

같은 source의 instantaneous frozen-charge relaxation gap/H는 H1에서 z20 `9.36e-5`에서 z2 `1.51e5`로 증가하며 Li7은 z20 `7.78e-5`에서 z2 `549.3`. `gap/H`는 시간-변화하는 bath에 대한 전역 adiabatic 정리나 실제 화학 이력 재구성을 의미하지 않는다. 작은 `gap/H`와 nonstationary source를 함께 읽어야 하며 `gap/H` 하나로 history가 평형임을 보장하지 않는다.

전자 source의 변화에 비례하는 pointwise Thomson RHS는 원본 source가 이미 `tau_x=K n_b x_e/H`를 사용하므로, 동일 frozen K,H,nb일 때만 `tau_x*/tau_x=x_e*/x_e`이다. **이것은 기존 source의 재평가이며 실제 원본 tau stored를 다시 적분하거나 관측 CMB tau에 제약을 준 것이 아니다.** 원본 REI17/BASS21 inventory/UV/electron/Grackle/nuclear/fast/timestep source mismatch 미해결. Production, F4, L4 gate 유지.

## 근거와 비판적 제한

Original BASS `AtomicNetwork` code and immutable stored trajectory are direct numerical source. The finite birth-death stationary measure is a basic continuous-time Markov-generator consequence, and `-Var(q)` identity is directly derived, Wolfram verified; not a new literature no-go. Related chemical coarse-graining: Tóth, Li, Rabitz and Tomlin, SIAM J Appl Math 1997, DOI `10.1137/S0036139995293294`. Physical UVB distinction: Puchwein, Haardt, Haehnelt, Madau MNRAS 2019 DOI `10.1093/mnras/stz222`. These external references are context only; source-specific numeric values are self-produced.
