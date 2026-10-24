# REI-L1: 유한 elemental-HI 광이온화 공급과 비열적 에너지 소유권

## 판정과 이번 이론 단위

L0의 실제 root 판정은 ADMITTED_SCOPED이다. 해당 ADMISSION.json은 SRC-01의 새 단일 child 검증, 독립 source review, 기존 근거의 재사용과 보존된 예산 초과를 구분한다. 이 문서는 그 뒤의 **선택 L1 이론 구성**이며 L1 수치 승인이나 물리 열화 승인이 아니다. 새 수치 실행, CAS, donor replay, Git 변경은 하지 않았다. L0의 남은 1초 SRC-01 배정을 L1 실행 예산으로 전환하지 않는다.

선택 모델은 **ELEMENTAL_HI_PW19_Z2_479_FINITE_PI_WITH_EXPLICIT_NONTHERMAL_RESERVOIR**이다. 이는 실제 공급된 유한 광자장과 같은 광이온화 사건의 원자·결합·일차 전자 장부를 연결한다. 이 문서에서 제안하는 여섯 소유자 adapter와 L0 사영은 아래에서 유도한 구성이다. 기존 문헌이나 donor가 이 adapter 전체를 이미 구현했다는 주장은 하지 않는다.

현재 scientific pin은 bass_cr의 b8882d026887f375acf90768d4e3740eb03da226에서 실제 읽은 C23B 입력이다. C23B 자체의 원 과학 게시 commit은 54477b285e0c712610453bca1408a076af43521d이다. 이후 중앙·CR·HE·HH·BASS의 moving-head 반환은 root의 별도 조사 대상이며 이 선택 입력을 암묵적으로 교체하지 않는다.

| 고정 항목 | 선택 |
|---|---|
| 채널 | ground-state elemental HI; isotope identity를 H1/D/T로 자동 매핑하지 않음 |
| source epoch | z = 2.479 한 점; redshift interpolation 또는 cosmic evolution 없음 |
| 광자 지지집합 | 13.6 ≤ E ≤ 50000 eV |
| 문턱 | χ = 13.6 eV, 공급자 convention 유지 |
| source representation | positive source table의 log S–log E 선형 보간이라는 공급자의 선언 |
| target/frame | bath-rest ground-state target, zero-recoil approximation |
| angular model | 명시적으로 선택한 isotropic scalar closure |
| deposition | 기본 선택 동역학은 no-deposition; physical secondary_heat는 null |
| 포함하지 않은 사건 | RR/DR/CI/CX, secondary reactions, nuclear channels, transport, Einstein feedback |

원료 계약: [C23B source contract](https://github.com/cosmosapjw-quantum/bass_cr/blob/b8882d026887f375acf90768d4e3740eb03da226/research/cr_c23b_source_frame_20261023/source_providers/CONTRACT.json), blob e40e4093ea56c2427cf3a79bd5d29ed6d2edad2e. [Atomic coverage](https://github.com/cosmosapjw-quantum/bass_cr/blob/b8882d026887f375acf90768d4e3740eb03da226/research/cr_c23b_source_frame_20261023/source_providers/ATOMIC_SOURCE_COVERAGE.json), blob 263e710d31673611f6bfdbbda08e5f4f5f755482. [C23B final authority](https://github.com/cosmosapjw-quantum/bass_cr/blob/b8882d026887f375acf90768d4e3740eb03da226/research/cr_c23b_source_frame_20261023/delivery/C23B_FINAL_AUTHORITY_20261023.json).

## 1. 같은 사건 측도에서 수와 네 에너지 모멘트를 얻는다

E는 eV 단위의 광자 에너지 좌표이고

\[
c_{\rm erg}=1.602176634\times10^{-12}\ {\rm erg/eV},
\qquad
c_J=1.602176634\times10^{-19}\ {\rm J/eV}
\]

로 둔다. source table의 값은

\[
S(E)=4\pi\nu J_\nu,\qquad [S]={\rm erg\,s^{-1}\,cm^{-2}}
\]

이며 d ln E당 스펙트럼 에너지량이다. E-bin 전체 에너지가 아니고, 4π도 이미 들어 있다. 따라서 같은 table에 4π를 다시 곱하거나 dE와 d ln E를 혼용하면 안 된다.

광자 흡수의 target당 proper-time 사건 측도는

\[
d\mu(E)
 = {4\pi J_\nu\over h\nu}\sigma(E)\,d\nu
 = {\sigma(E)S(E)\over c_{\rm erg}E}\,d\ln E
 = {\sigma(E)S(E)\over c_{\rm erg}E^2}\,dE .
\]

여기서 dν/ν = dE/E를 사용했다. σ가 cm²이고 S가 위 단위이므로 dμ의 차원은 target당 s⁻¹이다. 단위가 다른 에너지 좌표를 입력하면 c_erg와 미분 측도를 함께 변환해야 한다.

영반동 모델에서 일차 전자 운동에너지 좌표 κ = E−χ이며 dκ = dE다. 그러므로

\[
q_{\rm primary}(\kappa)
 = {d\mu\over d\kappa}
 = {\sigma(\kappa+\chi)S(\kappa+\chi)\over
 c_{\rm erg}(\kappa+\chi)^2},
\quad
0\le\kappa\le50000-\chi .
\]

이 식은 공급자 source contract의 q_i(K)와 같다. 아래에서는 분포 좌표 κ와 적분된 운동에너지 공급률 K를 구별한다.

\[
\begin{aligned}
A &= \int d\mu,\\
B &= \int \chi\,d\mu = \chi A,\\
P &= \int E\,d\mu,\\
K &= \int (E-\chi)\,d\mu .
\end{aligned}
\]

A는 target당 proper-second 사건률이다. B, P, K는 eV per target per proper second이다. 같은 비음수 측도에서 적분하면 실수 산술에서

\[
B+K-P=0,\qquad B-\chi A=0.
\]

이는 새 물리적 stopping 법칙이 아니라 선택한 단일 광이온화 사건의 에너지 분할이다. E<χ의 광이온화 사건률 0은 해당 채널의 물리적 threshold zero다. E>50000의 event rate는 공급자 fit 밖의 **unknown/null**이며 0으로 채우지 않는다. 선택한 유한 모델에서는 그 구간을 포함하지 않았다고 밝힌다. 원래 photon intensity 자체가 그 구간에서 0이라는 뜻은 아니다.

### 저장된 원자 측도

공급자의 양의 quadrature 원자들을 (κ_j, w_j)로 쓰면

\[
A_{\rm atom}=\sum_j w_j,\quad
B_{\rm atom}=\sum_j \chi w_j,\quad
K_{\rm atom}=\sum_j \kappa_jw_j,\quad
P_{\rm atom}=\sum_j(\chi+\kappa_j)w_j.
\]

이는 같은 저장 원자의 재사용에 대한 이론식이다. 이번 이론 단위에서는 CSV payload를 읽거나 적분하지 않았다. 실제 원본 열 이름, 저장된 광자/전자 에너지의 표현 관계와 summation convention은 raw 원자 복구 후 그대로 결속해야 한다. 원자가 이미 공급자 계산에서 잃은 정보는 consumer의 exact arithmetic으로 복원할 수 없다.

## 2. target 정규화는 한 번만 적용한다

보존되는 기준수밀도를 n_ref로 두고, 같은 proper-volume 단위의 target 밀도를 n_HI라 하자.

\[
X_{\rm HI}=n_{\rm HI}/n_{\rm ref},\qquad
m=aX_{\rm HI}.
\]

a는 고정 shape에 대한 명시적 진폭이다. 현재 실제 source 선택은 a=1이다. a에 대한 미분은 adapter의 선형 민감도이며 다른 a에서 새로운 physical-source calibration을 했다는 뜻이 아니다.

Href당 모멘트율은 (mA,mB,mP,mK)이다. 또는 처음부터 proper-volume 소스를 만들려면 (a n_HI A,a n_HI B,a n_HI P,a n_HI K)를 사용한다. 두 정규화를 동시에 적용하지 않는다.

\[
Q^{\rm SI}_{A}
 =n_{\rm ref}^{\rm SI} c_J q_A^{\rm perHref}
 =n_{\rm HI}^{\rm SI} a c_J\,(\hbox{해당 target당 에너지율}).
\]

n_HI가 cm⁻³이면 SI 변환은 n_HI^SI=10⁶ n_HI다. source 식에서 이미 σ(cm²)와 flux(cm⁻²)가 상쇄됐으므로 추가 area 변환을 다시 넣지 않는다.

공급자 원자는 bath frame에 있다. parent-rest boost를 추가하지 않으며, 기존 boost API를 통과해야 한다면 명시적인 u=0 identity만 허용한다. reference inventory의 선언이 없는데 X_HI의 총량을 임의로 1로 정하지 않는다. 선언한 elemental-H 전체 abundance 안에서 HI/HII를 보존한다.

## 3. 입자 장부: free electron과 thermal electron은 다르다

proper time의 선택 PI 반응율 R=mA에 대해

\[
\dot X_{\rm HI}=-R,\qquad
\dot X_{\rm HII}=+R,\qquad
\dot X_{e,\rm all}=+R .
\]

따라서 elemental target 핵 수와 전하가 보존된다.

\[
{d\over dt}(X_{\rm HI}+X_{\rm HII})=0,
\qquad
{d\over dt}(X_{\rm HII}-X_{e,\rm all})=0 .
\]

흡수 광자 수는 같은 사건수로 −R이다. 일차 전자를 비열적 pool에 보관하는 기본 모델에서는

\[
\dot X_{e,\rm nt}|_{\rm PI}=R,\qquad
\dot X_{e,\rm th}|_{\rm PI}=0,\qquad
X_{e,\rm all}=X_{e,\rm th}+X_{e,\rm nt}.
\]

새 전자를 free electron으로 센다는 사실만으로 thermal heat capacity에도 즉시 넣을 수 없다. thermal electron과 nonthermal electron을 모두 한 번씩 전하에 더해서도 안 된다. 이 두 number pools는 여섯 에너지 소유자와 나란히 존재하는 입자 장부이며 새 에너지 소유자를 뜻하지 않는다.

## 4. 여섯 에너지 소유자의 보존적 source

L0의 앞 다섯 소유자 순서를 유지하고 일차 비열적 전자 에너지를 여섯째로 추가한다.

| index | 소유자 | 선택 PI 사건 하나의 전달 |
|---:|---|---:|
| 0 | gas_thermal | 0 |
| 1 | binding | +χ |
| 2 | uv_radiation | −E |
| 3 | dynamic_escape_radiation | 0 |
| 4 | source_reservoir | 0 |
| 5 | primary_nonthermal | +(E−χ) |

\[
v_{\rm PI}^{(6)}(E)
 =(0,\chi,-E,0,0,E-\chi)^T,\qquad
{\bf1}^Tv_{\rm PI}^{(6)}=0.
\]

따라서 같은 정확한 측도의 적분은

\[
q_{\rm PI}^{(6)}
 =m(0,B,-P,0,0,K)^T .
\]

source가 공급한 일차 kinetic excess는 primary_nonthermal의 소유다. 여기서 gas_thermal=0은 선택한 **NO_DEPOSITION_SELECTED_MODEL**의 source 규칙이다. 공급자가 보고한 physical secondary_heat=null을 관측된 heat=0으로 바꾼 것이 아니다.

별도 deposition energy rate D와 finite source-reservoir→UV energy feed J를 기호로 두면

\[
d=(1,0,0,0,0,-1)^T,\qquad
f=(0,0,1,0,-1,0)^T,
\]

\[
q^{(6)}=m(0,B,-P,0,0,K)^T+Dd+Jf.
\]

D와 J는 eV per Href per proper second이다. 선택 기본 모델은 D=0이다. 임의의 D를 실제 stopping rate라고 만들거나, D만으로 전자의 thermal-number 전환까지 추론하지 않는다. 유한 stock의 positivity와 시간진화는 이 local source adapter 밖의 후속 모델 의무다.

외부 prescribed source의 공급 J_ext라면 source_reservoir에서 차감하지 않고

\[
f_{\rm ext}=(0,0,1,0,0,0)^T,\qquad
q^{(6)}=m v+Dd+J_{\rm ext}f_{\rm ext}
\]

로 둔다. 전체 source 합은 정확한 moment model에서 J_ext이다. 외부 공급을 0으로 숨겨 closed model이라고 부르면 안 된다. energy feed J 하나는 spectral photon count를 정하지 않으므로 실제 feed가 선택되면 같은 source의 number/energy measure를 따로 결속해야 한다.

고정 PW19 스펙트럼은 instantaneous prescribed field이다. 위 UV 흡수 항을 정의했다고 유한 photon stock의 depletion과 source shape 변화를 동시에 해결한 것은 아니다. finite energy support와 finite radiation inventory는 별개의 선언이다. 고정 source를 계속 유지하면서 실제 UV state도 진화시키려면 replenishment/transport와 일치하는 공급 계약이 더 필요하다.

L0의 proper-time per-reference balance

\[
\dot u_A+3Hp_A+\sigma:\pi_A=q_A
\]

와 단위를 맞추지만, 이번 이론은 q_A의 local exchange를 구성한다. primary_nonthermal의 equation of state, pressure trace, transport, redshift work 또는 Einstein source를 새로 공급하지 않는다.

## 5. 저장된 summary는 각각 반올림된 입력이다

선택 [CASES.json](https://github.com/cosmosapjw-quantum/bass_cr/blob/b8882d026887f375acf90768d4e3740eb03da226/research/cr_c23b_source_frame_20261023/source_providers/runs/c23b_pw19_spectral_source_20261023_v1/CASES.json)의 z2.479/HI row는 다음 값들을 따로 저장했다. blob은 61bcbc0b44206f496534da6bdffcdfe1731ad063이다.

| 기호 | 저장된 값 |
|---|---:|
| A | 1.1871043740697437e−12 target⁻¹ s⁻¹ |
| B | 1.6144619487348515e−11 eV target⁻¹ s⁻¹ |
| P | 2.058084202785955e−11 eV target⁻¹ s⁻¹ |
| K | 4.4362225405110365e−12 eV target⁻¹ s⁻¹ |
| positive atoms in selected row | 4368 |
| secondary_heat_eV_per_target_s | null |

구현은 반드시 두 잔차를 별도로 반환한다.

\[
r_B=B-\chi A,\qquad r_E=B+K-P.
\]

표시된 십진 문자열을 **정확한 십진수**로 해석한 종이 위 산술은

\[
\begin{aligned}
\chi A &= 1.614461948734851432\times10^{-11},\\
r_B^{\rm decimal\ spelling} &= +6.8\times10^{-28},\\
B+K &= 2.05808420278595515\times10^{-11},\\
r_E^{\rm decimal\ spelling} &= +1.5\times10^{-27}.
\end{aligned}
\]

에너지율 단위는 eV target⁻¹ s⁻¹이다. **이 값은 실행한 binary64 검산 결과가 아니다.** binary64에 대응하는 정확한 dyadic 입력 잔차와 실제 연산 순서의 floating residual은 별도 실행에서 보고해야 한다. 이번에는 그 실행을 하지 않았다.

공급자가 따로 저장한 energy_ledger_residual_eV_per_target_s는 −1.6155871338926322e−27이고 energy_ledger_relative는 7.849956438641673e−17이다. 그 원래 부호·연산 순서·정의는 보존한다. 이 필드를 우리의 r_E로 이름만 바꾸거나 십진수 잔차와 같아야 한다고 요구하지 않는다.

중요한 구현 규칙은 다음과 같다.

- B를 χA로 덮어쓰지 않는다.
- P를 B+K로 덮어쓰지 않는다.
- K를 P−χA 또는 P−B의 큰 수 차로 복원하지 않는다.
- 작은 잔차를 임의의 물리 소유자에 넣어 보존을 인위적으로 맞추지 않는다.
- 독립 반올림 summary mode와 같은 positive-atom measure에서 재구성한 mode를 구분한다.
- target 정규화를 적용한 source 합은 summary mode에서 m r_E이다. 이를 실제 input defect로 보고하며 adapter arithmetic error와 분리한다.

따라서 summary를 사용하는 six-owner vector의 합을 무조건 machine zero로 요구하는 것은 올바른 검증이 아니다. 정확히 표현된 입력으로 계산한 m r_E와 출력 source 합의 차이가 adapter의 수치 오차다. source consistency 자체의 r_B,r_E 허용 기준은 별도다.

## 6. 방향미분과 Jacobian 열의 합

고정 source shape와 pinned χ, E support에서 m=aX라 하자.

\[
\delta m=a\,\delta X+X\,\delta a.
\]

공급자 모멘트를 동결한 six-owner source의 방향미분은

\[
Dq[\delta X,\delta a,\delta D,\delta J]
 =\delta m(0,B,-P,0,0,K)^T+\delta D\,d+\delta J\,f.
\]

열벡터로는

\[
\partial_X q=a\,v,\quad
\partial_a q=X\,v,\quad
\partial_D q=d,\quad
\partial_J q=f .
\]

정확한 같은-measure 모멘트일 때 각 열의 합은 0이다. 독립 반올림 summary mode에서는

\[
{\bf1}^TDq=r_E\,\delta m .
\]

외부 공급은 위 식에 δJ_ext가 추가된다. source moment를 별도 방향으로 바꾸는 형식적 미분은

\[
\delta q_{\rm PI}
 =\delta m\,v+
 m(0,\delta B,-\delta P,0,0,\delta K)^T .
\]

같은 fixed-support 사건 측도를 perturb한 경우 δB=χδA, δP=δB+δK가 실수 산술에서 성립한다. 그러나 이 이론적 관계를 이용해 실제 independent rounded tangent inputs를 덮어쓰면 안 된다. χ, threshold, 지원 구간, isotope label, source z의 변화는 현재 선택 계약의 매개변수가 아니다. 그 변화에서 임의 미분을 제공하지 않는다.

입자 장부도 같은 δR=Aδm를 쓴다.

\[
\delta\dot X_{\rm HI}=-A\delta m,\quad
\delta\dot X_{\rm HII}=+A\delta m,\quad
\delta\dot X_{e,\rm nt}=+A\delta m.
\]

X=0 또는 a=0에서도 표현이 정의된다. 0인 반응률로 나누어 상대 미분을 만들 필요가 없다. 양의 상태 경계에서의 방향은 물리 domain 안에 머무르는 방향으로 해석한다.

나중 구현은 J−mP 같은 작은 net source와 aδX+Xδa 같은 상쇄를 출력 직전에 반올림해야 한다. 개별 큰 항을 먼저 반올림해 유효한 작은 net을 지우는 경로를 다시 만들지 않는다. 이는 L0 SRC-01에서 닫은 source/JVP 의미를 유지하기 위한 요구다. 새 적분이나 원 donor 검증의 반복을 요구하는 규칙은 아니다.

## 7. isotropic STF 0은 선택한 closure다

같은 bath-rest frame에서 명시적 isotropic angular model을 사용한다. 각 에너지에서 angular probability를 dΩ/(4π)로 선언하면

\[
\int n_i\,{d\Omega\over4\pi}=0,\qquad
\int\left(n_in_j-\frac{\delta_{ij}}3\right){d\Omega\over4\pi}=0.
\]

따라서 이 선언된 source submodel의 flux와 STF injection은 0이다. 이 0은 측정된 DDCS, recoil correlation 또는 실제 radiation angular distribution에서 얻은 수치가 아니다. scalar S(E)만으로 anisotropic distribution을 복원한 것도 아니다.

필요 PSD/moment-cone 조건과 source-positive measure의 역할은 유지한다. 그러나 isotropic STF 0이 nonthermal pressure trace, kinetic closure, global realizability 또는 empirical transport를 제공하지 않는다. 같은 isotropic model 안의 X/a 변화에 대한 STF 미분은 0이다. angular perturbation은 현재 모델 바깥이므로 그 미분까지 0으로 반환하지 않는다. zero-recoil 에너지 근사에서 photon/ion momentum의 일반 four-force를 주장하지 않는다.

## 8. L0로의 사영은 순간 열화 모델을 명시했을 때만 물리적으로 해석한다

대수적으로 에너지 좌표들을 합치는 선형 사상

\[
\Pi(u_{\rm th},u_b,u_\gamma,u_{\rm esc},u_s,u_{\rm nt})
 =(u_{\rm th}+u_{\rm nt},u_b,u_\gamma,u_{\rm esc},u_s)
\]

을 적용하면

\[
\Pi v_{\rm PI}^{(6)}
 =(E-\chi,\chi,-E,0,0)^T
\]

가 되어 L0의 PI 열을 얻는다. 그러나 합쳐진 첫 좌표를 gas thermal이라고 해석하려면 별도의 물리/모델 가정이 필요하다.

명시적인 **INSTANT_DEPOSITION_MODEL**은 각 새 primary electron의 kinetic energy를 즉시 thermal pool로 보내고 nonthermal initial stock은 없다고 선언한다. source 수준에서

\[
D=mK,\qquad \Lambda=mA
\]

를 두며, Λ는 nonthermal electron에서 thermal electron으로 이동하는 number rate다.

\[
\dot X_{e,\rm nt}|_{\rm dep}=-\Lambda,\qquad
\dot X_{e,\rm th}|_{\rm dep}=+\Lambda.
\]

PI와 deposition을 합하면 새 nonthermal energy/number의 저장은 0이고, source vector는

\[
q_{\rm inst}^{(6)}
 =m(K,B,-P,0,0,0)^T
\]

이다. 여섯째 좌표를 없애면 L0-compatible five-owner source가 된다. **여전히 K는 저장된 직접 kinetic moment를 쓴다.** summary mode의 r_B,r_E는 그대로 남으며 P−χA로 K를 복원하지 않는다.

이 모델의 미분에서는 D가 독립 입력이 아니다.

\[
\delta D=K\delta m,\qquad
\delta\Lambda=A\delta m,
\qquad
Dq_{\rm inst}=\delta m(K,B,-P,0,0,0)^T .
\]

순간 열화 가정이 없을 때는 raw K를 thermal heat로 출력하지 않는다. 실제 stopping provider의 energy partition, time dependence 및 secondary ionization/excitation이 있는 모델은 그 provider의 계약을 사용한다. 단지 X/a source dependence를 미분하는 것으로 stopping Jacobian을 얻을 수 없다.

열적 상태의 정의가 이상기체 내부에너지 u_th=(3/2)k_B T N_th를 쓴다면 thermal particle 증가도 온도 미분에 들어간다.

\[
\dot T_{\rm source}
 ={2q_{\rm th}\over3 k_B N_{\rm th}}
 -{T\over N_{\rm th}}\dot N_{\rm th}.
\]

여기서 에너지 단위에 맞춘 k_B를 써야 한다. no-deposition model의 새 일차 전자는 N_th에 즉시 들어가지 않는다. instant model은 Λ의 thermal-number 이동을 포함한다. 이 식은 모델 선택 시 필요한 local conversion이며 이번에 temperature evolution을 실행했다는 뜻이 아니다.

문헌 맥락으로 [Furlanetto–Stoever, arXiv:0910.4410](https://arxiv.org/abs/0910.4410)은 전자 에너지와 ionized fraction에 따라 heat/ionization/excitation 분할이 달라짐을 다룬다. [Pawlik–Schaye, arXiv:1008.1071v2, equations14–17](https://arxiv.org/html/1008.1071v2)는 complete thermalization 가정을 명시하고 secondary electrons의 효과를 경고한다. 이 논점은 root가 확인한 primary 문헌 맥락으로 사용했다. 여기서 구성한 six-owner adapter 자체가 그 논문에 제시됐다는 인용은 아니다.

## 9. 고정 HANDOFF의 조건부 선행과 현재의 다음 행동

고정 [REI handoff](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17/research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md)의 선택-provider 해석을 따른다. 선택한 채널에 해당하는 공급자 조건만 활성화한다.

- L0는 root의 실제 scoped admission을 재사용한다.
- 선택 elemental-HI PI source는 C23B의 정확한 source/domain/normalization을 결속한다.
- CR_N4_STOPPING_KERNEL은 supplied fast electrons의 thermalization을 물리적으로 주장할 때 필요하다. 기본 no-deposition model에서 secondary_heat=null을 보존하면 그 공급자를 임의로 만들어 완료할 필요가 없다.
- WU_D_PI_RR_MATCHED는 isotope-specific D PI/RR number/energy를 주장할 때 필요하다. 지금은 D와 RR를 선택하지 않았다.
- REC-LINE02 또는 REC-FIELD는 native line, actual spectral/Compton exchange를 선택할 때 적용한다. 이번 선택은 그 채널이 아니므로 모든 REC 공급자를 기다리는 AND 조건을 만들지 않는다.
- HE full angular source, nuclear particle ownership, nonzero beta와 Einstein feedback은 이번 scalar instantaneous PI adapter에서 선택하지 않았다.

L1 future owned path는 research/rei_source_pair_binding/**이다. 기존 C23B/ANGTHERM/HE/HH/REC owner source를 변경하지 않는다. 새 model or provider absence는 **INPUT_DEPENDENCY**이지 strong no-go가 아니다. 더 작은 선택 모델에서 명확히 정의할 수 있는 source를 구성했고, 앞으로 필요한 raw input/실행 budget/admission을 분리한다.

full L1 admission은 아직 pending이다. 이번에 raw atoms의 내용/열을 읽지 않았고 새 L1 수치 실행 예산도 결속하지 않았다. 현재 할 수 있는 구체적인 다음 단계는 아래 implementation contract 권고를 root가 고정한 뒤 lower-tier executor가 허용 경로 안에서 summary-preserving adapter와 analytic JVP를 정적으로 준비하는 것이다. actual atom reuse 검증 및 새 consumer 수치 checks는 별도 현행 budget/stop contract가 생겼을 때만 실행한다. 공급자 quadrature, 완료 campaign, CAS, IVP를 다시 돌릴 필요는 없다.

whole-model/all-owner overall completion은 null이다.
