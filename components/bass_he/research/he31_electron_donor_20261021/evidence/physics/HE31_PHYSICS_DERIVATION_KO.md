# HE31: H/He donor → 광자 Thomson 연산자와 canonical FV 준비 평가기

## 판정과 실행 범위

기존 `CanonicalFVSpecies`는 proper 전자수밀도 callback을 이미 지원한다. HE31의 유효한 추가 기여는 실제 H/He ionic census, 밀도·시간 단위, 입력 내용 SHA와 유효 구간을 함께 묶은 donor와 이를 실제 생성자에 전달하는 driver다. 기존 `ElectronHistory`와 `SmoothElectronHistory`도 범위 밖 보간을 금지한다. 따라서 단순히 이 보간기를 다시 만드는 작업을 새로운 물리 연결이라고 부르지 않는다.

현재 40상태 계는 massive collisionless nonbaryonic matter, photons, massless neutrinos를 분리하고, 광자 energy/number multipole에만 **elastic unpolarized Thomson**을 적용한다. 여기서 적은 유도는 이 모형과 정확히 맞는 연결 규약이다. 공유 vendor는 수정하지 않았고, 새로운 물리 궤적·ODE 적분·속도 벤치마크는 실행하지 않았다. 준비 평가기의 결과는 author algebraic validation이며 독립적인 최종 과학 승인과 구분한다.

## 1. H/He ionic census와 밀도 단위

HII의 H 핵당 분율을 $x_{\rm HII}$, HeII/HeIII의 He 핵당 분율을 $x_{\rm HeII},x_{\rm HeIII}$라 쓰면

\[
n_e^{\rm proper}=n_{\rm H}^{\rm proper}x_{\rm HII}
 +n_{\rm He}^{\rm proper}(x_{\rm HeII}+2x_{\rm HeIII})
=n_{\rm H}^{\rm proper}[x_{\rm HII}+f_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII})],
\quad f_{\rm He}=n_{\rm He}/n_{\rm H}.
\]

이 식은 charge counting의 직접 결과다. He 열이 이미 H 핵당 abundance이면 $f_{\rm He}$를 다시 곱하지 않는다. `xe = ne/nH`를 주는 donor이면 `ne=nH*xe`다. 핵 분율은 음수가 없어야 하고, HI+HII 및 HeI+HeII+HeIII의 합을 해당 donor 허용오차로 확인한다. 숨은 재정규화나 음수 clipping으로 입력 오류를 지우지 않는다. 질량분율 $Y$에서 $f_{\rm He}=Y/[4(1-Y)]$를 쓰는 경우에는 원자 질량을 1:4로 근사하는 source convention까지 기록한다. donor가 이미 $f_{\rm He}$를 지정하면 그 값을 재사용한다.

단위와 부피 규약은 다음과 같다.

| 입력 | proper cm⁻³로의 변환 |
|---|---|
| proper cm⁻³ | 그대로 |
| proper m⁻³ | $10^{-6}$을 곱함 |
| 오늘의 $a=1$ 기준 comoving cm⁻³ | $a^{-3}$을 곱함 |
| 기준시각 $a_{\rm ref}$의 proper nuclei density | $(a_{\rm ref}/a)^3$을 곱함 |

이미 proper인 밀도에 $a^{-3}$을 다시 곱하면 안 된다. LRS 척도인자 $a_\perp=a e^{-b}$, $a_\parallel=a e^{2b}$에서는 부피가 $a_\perp^2a_\parallel=a^3$라서 $b$에 따른 추가 부피 인자가 없다.

electron history는 Thomson rate를 공급한다. 이 단계에서 전자를 새로운 Friedmann 질량 성분으로 추가하지 않는다. source의 isotropic baryons는 기존 Ωm 예산에 들어 있으며, canonical massive 성분은 source 생성자가 baryon과 겹치지 않도록 제한하는 별도 nonbaryonic 분포다.

## 2. Proper time, conformal time, log a

우주론적 정상계에 정지한 전자, cold elastic Thomson 조건에서

\[
\Gamma_T=c\sigma_T n_e^{\rm proper},\qquad
d\tau_T=\Gamma_T\,dt.
\]

D3 consumer의 고정 값은 $c=2.99792458\times10^{10}\,\mathrm{cm\,s^{-1}}$, $\sigma_T=6.6524587051\times10^{-25}\,\mathrm{cm^2}$다. 이것을 $n_e[\mathrm{cm^{-3}}]$와 곱하면 s⁻¹이다. SI로는 $c=299792458\,\mathrm{m\,s^{-1}}$, $\sigma_T=6.6524587051\times10^{-29}\,\mathrm{m^2}$, $n_e[\mathrm{m^{-3}}]=10^6n_e[\mathrm{cm^{-3}}]$이며 두 계산은 동일하다. donor와 consumer의 과거 σT 반올림 값이 다르면 consumer 상수를 몰래 바꾸지 말고 identity에 두 값을 적는다.

ODE의 $\eta=\ln(a/a_{\rm ref})$는 무차원이고 $d\eta/dt=H$다. 따라서

\[
g(\eta)=\frac{d\tau_T}{d\eta}=\frac{\Gamma_T}{H},
\qquad
d\tau_T=-\frac{\Gamma_T}{(1+z)H}dz.
\]

시간이 앞으로 갈수록 z는 감소하고 τT는 증가한다. 관측자에서 과거까지 적분한 optical depth 정의를 쓸 때는 적분 한계로 이 부호를 반영한다. conformal time $d t=a\,d\eta_c$를 쓰는 문헌의 κ-dot는 $a\Gamma_T$이고, $c=1$로 쓰면 $a n_e\sigma_T$다. Ma & Bertschinger §5.5, 식 (59)–(64)는 proper ne와 이 conformal-time convention을 명시한다. [원전](https://arxiv.org/pdf/astro-ph/9506072)

donor 보간기의 독립변수가 `log(a)`라면 ODE의 `eta`와는 `log(a_ref)`만큼 다르다. 기존 callback은 `density(a)`를 받아 이 차이를 내부에서 처리한다. homogeneous non-tilted 전자는 주어진 proper-time 두 끝점 사이에서 scalar rate를 준다. 방향별 관측 redshift는 끝점 선택을 바꾸지만, callback에 임의의 $a,b,1+z$ 인자를 추가하지 않는다.

**구현상 구별:** 기존 `y[0]`는 elapsed proper time × Href다. source가 이 변수를 `tau`라고 부르더라도 optical τT가 아니다. 현재 40상태를 유지하려면 τT는 별도 진단으로 적분하거나 계산 구간 밖의 독립 누적량으로 관리한다. 같은 상태 칸을 덮어쓰지 않는다.

## 3. 기존 real Legendre 규약의 Thomson kernel

unpolarized differential kernel은

\[
K(\mathbf n,\mathbf n')=\frac{3}{16\pi}(1+\cos^2\chi)
=\frac1{4\pi}\left[1+\frac12P_2(\cos\chi)\right].
\]

D3는 $J_l=\tfrac12\int_{-1}^1 F P_l d\mu$, $F=\sum_l(2l+1)J_lP_l$를 쓴다. addition theorem과 Legendre 직교성을 적용하면 gain은 $J_0+\tfrac12J_2P_2$이고, moment별 gain eigenvalue는 $1,0,1/10,0,\ldots$다. 따라서

\[
C_l=-\Gamma_T d_lJ_l,
\qquad d_0=0,\quad d_2=9/10,\quad d_l=1\ (l\ne0,2).
\]

이것이 `thomson_coeffs`와 정확히 같다. l=1도 식에는 포함되지만 현재 반사 대칭 LRS 상태에서는 dipole이 0이다. elastic scattering은 주파수를 바꾸지 않으므로 energy와 number angular moment에 같은 감쇠행렬을 쓴다. collision monopole은 0이며, 팽창·shear에 의한 energy 변화는 그대로 남는다. 예컨대 기존 energy Liouville matrix의 $A_{02}=-2$다.

Ma & Bertschinger 식 (59)–(64)와 Tram & Lesgourgues §2.1 식 (2.3)–(2.4)는 full polarized source를 포함한다. MB의 Fourier multipole에는 $(-i)^l$가 있으므로 real homogeneous D3와 계수의 겉보기 부호를 직접 대조하면 안 된다. scalar kernel을 위처럼 직접 투영하면 $9/10$이 모호하지 않다. [MB95](https://arxiv.org/pdf/astro-ph/9506072), [Tram & Lesgourgues 2013](https://arxiv.org/pdf/1305.3261)

## 4. Integrating factor의 사용 범위

현재 광자 계를 $J'=v A J-g D J$, $v=s/H$, $D=\operatorname{diag}(d_l)$, $\tau_T'=g$로 쓰자. $U_l=e^{d_l\tau_T}J_l$이면

\[
U_l'=v\sum_m A_{lm}e^{(d_l-d_m)\tau_T}U_m.
\]

collision만 있는 구간의 정확한 update는 $J_l\mapsto e^{-d_l\Delta\tau_T}J_l$다. 이는 좋은 local oracle이며 split method를 쓴다면 collision substep을 정확히 처리할 수 있다. 다만 $A,D$는 commute하지 않는다. 실제 $ (AD-DA)_{02}=-9/5\ne0$다. 또한 live Einstein source가 광자 stress에 반응한다. 따라서 완료된 collisionless D3 궤적에 감쇠 인자를 사후 곱하는 것으로 live Thomson 궤적을 대체할 수는 없다. HE31 ready driver는 기존 RHS에 실제 donor callback을 연결하는 경로를 사용해야 한다.

## 5. Full polarization과의 작은 정확한 비교

기존 B1 `native/upstream_polarization.py`는 screen coherency matrix의 Thomson gain을 재사용 가능한 형태로 구현한다. B1의 axisymmetric convention $I=F+i_2P_2$, $Q_S=q(1-\mu^2)$에서 collision-only 계는

\[
\frac{d}{d\tau_T}\binom{i_2}{q}=
\begin{pmatrix}-9/10&-2/5\\-3/20&-2/5\end{pmatrix}\binom{i_2}{q}.
\]

고유값은 $-1,-3/10$이다. 처음 $q=0$일 때

\[
\frac{i_2(\tau_T)}{i_2(0)}=\frac{6e^{-\tau_T}+e^{-3\tau_T/10}}7,
\qquad
\frac{q(\tau_T)}{i_2(0)}=\frac3{14}(e^{-\tau_T}-e^{-3\tau_T/10}).
\]

scalar slice의 $e^{-9\tau_T/10}$와 intensity 차이는 처음 $3\tau_T^2/100+O(\tau_T^3)$이다. $i_2\ne0$이면 $q'= -3i_2/20\ne0$라서 처음 polarization이 없다는 사실만으로 그 상태가 계속 유지되지는 않는다. 현 HE31은 기존 full40의 명시된 unpolarized approximation을 유지한다. 이 2×2 결과는 독립적인 collision-only 비교이며 새로운 polarized Einstein trajectory 계산을 요구하지 않는다. 기호 검산 결과는 `THEORY_ALGEBRA_CHECK.json`에 있다.

## 6. Positive canonical FV 준비 평가기의 유도

원본의 고정 packet number를 $N_j$, reference energy normalization을 $R$라 하고 $w_j=N_j/R$를 한 번 계산한다. conserved canonical momentum으로

\[
Q_{\perp j}^2=q_j^2(1-\mu_j^2),\quad Q_{\parallel j}^2=q_j^2\mu_j^2,
\quad \alpha=e^{-2\eta+2b},\quad\beta=e^{-2\eta-4b},\quad r=e^{-\eta},
\]
\[
E_j=\sqrt{m^2+\alpha Q_{\perp j}^2+\beta Q_{\parallel j}^2}.
\]

그러면 같은 quadrature의 moments는

\[
\rho=r^3\,w\cdot E,\quad
P_\perp=\frac{r^3\alpha}{2}(w Q_\perp^2)\cdot E^{-1},\quad
P_\parallel=r^3\beta(w Q_\parallel^2)\cdot E^{-1}.
\]

준비 단계에서 $Q_\perp^2,Q_\parallel^2,w,wQ_\perp^2,wQ_\parallel^2$를 immutable binary64 배열로 만든다. 평가마다 energy와 inverse-energy의 두 packet 배열만 사용하고, `sqrt` 한 번, `reciprocal` 한 번, dot reduction 세 번을 수행한다. 원본의 quadrature, amplitude, 질량, normalization, state domain, cell number와 `FVMoments` class는 그대로다. source configuration이나 상태를 둥글린 cache key로 바꾸지 않는다.

이는 정적 연산·임시 배열 감소이며 측정된 속도 향상은 아니다. 준비 배열의 상주 메모리는 증가한다. N packets와 C canonical cells에 대해 array payload는 $8(5N+C)$ bytes다. scalar 작업 배열은 $16N$ bytes이고 batch 작업 행렬은 기본 64 MiB로 제한한다. 입력 상태와 출력(Nstates,3)의 O(Nstates) 공간, Python·BLAS 내부 overhead는 이 cap 밖이다. 호출 간 mutable scratch를 공유하지 않아 동시 read-only 사용이 가능하다. outer sweep 병렬화에서는 worker당 BLAS thread=1을 유지한다.

ACCEL02의 반사 angular pair/Neumaier kernel은 별도 `MassiveDistribution` 96×32 quadrature를 대상으로 한다. 여기서의 positive compactified canonical FV 분포와 discretization identity가 다르므로 그 kernel을 그대로 대체하지 않았다. HE31에서 재사용한 것은 준비된 불변계수와 결합 moment 계산이라는 구현 원칙이다.

## 7. 보존 항등식과 실제 확인

위 식을 $b'=v$를 따라 직접 미분하면

\[
\rho'+3(\rho+\bar P)+6b'\pi_s=0,\quad
\bar P=(2P_\perp+P_\parallel)/3,\quad
\pi_s=(P_\parallel-P_\perp)/3,
\qquad n'+3n=0.
\]

`PREPARED_MOMENTS_CHECK.json`은 nominal 및 mass-domain 경계 분포 2개, 상태 6개씩에서 원본 scalar moments와 새 scalar/batch를 비교했다. 최대 moment 상대차는 $3.691846187591282\times10^{-16}$, energy-work scaled residual은 $1.3615622634293834\times10^{-15}$, number residual은 $4.440892098500626\times10^{-16}$이다. 원본 `FVMoments` 타입, immutable arrays, 상태 도메인, 2상태 workspace cap도 확인했다. ODE와 benchmark는 0회다.

dot reduction 순서는 원본 elementwise sum과 달라 bitwise 일치를 주장하지 않는다. stress가 0을 지나는 곳에서는 큰 pressure 두 값의 차이로 얻는 π의 상대오차가 의미를 잃을 수 있다. component parity와 절대 stress 오차로 판단해야 한다. 이 소수 상태의 검사는 원본 모델의 전체 과학적 convergence 인증을 새로 부여하지 않는다.

## 8. 실제 donor를 선택할 때 보존할 경계

* B1 R15의 `ne=(nH+nHe)*Q`는 HII와 HeII가 같은 Q라는 source closure다. HeIII 및 residual electron census를 복원한 데이터가 아니다.
* B1 R15와 HE18 cold full histories의 확인된 범위는 z20→4다. z2까지의 값을 외삽해서 donor를 완성하지 않는다.
* B1 N4 `ne_eff_m3`는 proper-time cell average다. pointwise ne(a)와 같은 의미로 새 clock에 넣지 않는다. 저장된 cell optical-depth measure의 clock 재투영 규칙을 따르거나 원본 point history를 사용한다.
* HE18 warm HM12, cold source, D3 consumer는 source cosmology·thermal assumptions·history owner가 다르다. 서로 다른 provenance를 한 네이티브 연립모형으로 표시하지 않는다.
* `.density(a)`는 proper cm⁻³를 반환하고, 기존 `CanonicalFVSpecies`의 실제 생성자에 전달한다. 이전 D3 `adapter.model`의 `ne_source=None` 고정을 우회했다고 가정하지 않는다.

위 경계 안에서 donor는 **prescribed H/He electrons의 photon-opacity sensitivity**에 바로 기여한다. neutrino와 canonical massive collisionless RHS에는 Thomson 감쇠를 넣지 않는다.


### 유효 구간과 subnormal 순서 차이

독립 구현 reviewer는 원본의 coeff=r³/R가 먼저 underflow하는 극단적 late-time 상태를 확인했다. mass/Tref=10⁵, amplitude=2, 4×4 Gauss4, η=245, b=0에서 원본 rho=0, 준비 evaluator rho≈6.217×10⁻³²⁰이다. 준비 evaluator가 유효 입력을 거부한다는 뜻은 아니며, 부동소수점 곱셈 순서가 subnormal 구간에서 달라진 결과다. 실제 HE31 물리 범위는 $0\le\eta\le\ln7$이고 여기에서 binary64 tolerance parity를 사용한다. η=1000에서 두 값이 0이라는 소수 상태 검사는 전체 eta 영역의 부동소수점 동등성을 보장하지 않는다. 이 관찰에 따른 새 ODE·benchmark는 수행하지 않았다.
