# 후속 구현 계약 — 공통 Case A provider와 광자 흡수 모멘트

단위: \(\texttt{HERE_RUX03_COVARIANT_EXCHANGE_04}\)의 코딩 인계  
기준일: 2026-10-13 KST / 2026-10-12 UTC  
적용 source: rei_bianchi PR114 \(\texttt{a5c958c414dea41216b445c05f58df837f05cacb}\)  
정확한 tree·파일 identity: [현재 source 지도](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/source_map/CURRENT_SOURCE.json)

## 1. 구현 순서와 보존할 의무

**기존 \(\texttt{HERE_RUX03_PRIMARY_PROVIDER_03}\)은 pending으로 유지한다.** 먼저 공통 계수·원시 사건·포획 운동에너지 모멘트를 ordinary point, conservative point, endpoint, interval/root, paired caller에 연결한다. 기존 네 기체 변수, 광자 소거, H/He 양성 갱신, 잔차·야코비안, root inclusion과 source birth 소유는 [직전 코딩 계약](sandbox:/workspace/scratch/a868870ed554/primary_theory_03_work/dossier/CODING_CONTRACT_KO.md)을 따른다.

그 위에 **같은 원시 photon absorption events로 에너지·운동량·각도 모멘트를 반환하는 provider**를 추가한다. 이 후속 단위의 완료 근거는 실제 사건 소비 경로에서 아래 출력이 계산되고, 독립 참조값과 단일 소비 검사를 통과하는 것이다. 현재 원래의 \(\texttt{RUX02 + RUX03 -> RUX04 -> RUX05}\) 연결과 owner 완료 상태는 그대로 보존한다.

순서는 다음과 같다.

1. PRIMARY_PROVIDER_03의 공통 coefficient/event 표현과 실제 point/interval 소비를 완성한다.
2. 동일한 사건 객체와 node identity를 이용해 이 계약의 모멘트 출력을 연결한다.
3. 지정된 고정 프레임에서 공간 힘의 적합성을 확인한다.
4. 일반적인 \(f_g^a\ne0\)를 동적으로 소비하려면 §10의 공통 기체 속도 이론·이산화 의무를 먼저 완성한다.

이 문서는 2–3의 계산 계약과 4의 정확한 선행 문제를 정한다. 현재 이론의 새 symbolic 결과는 §9에, 앞으로 실행할 native 검사는 §8에 구분해 기록한다.

## 2. 물리·각도 표현·입력의 계약

### 2.1 공통 프레임과 유지할 물리

\[
g=(-+++),\quad u_au^a=-1,\quad U^a=cu^a,\quad
h^a{}_b=\delta^a{}_b+u^au_b,\quad
\dot X=cu^a\nabla_aX.
\]

사건률과 photon energy는 동일한 기체 정지 프레임에서 평가한다. 기존 one-temperature, charge-neutral, nonrelativistic H/He gas, 보존된 H/He nuclei, warm FT03 Case A 영역 \(30000\le T\le110000\ {\rm K}\), 선택된 CI/RR/두 DR·포획 kinetic moments·primary absorption을 유지한다. 기존 ionization energy와 cross-section activation cutoff의 서로 다른 역할도 유지한다. CR/RCT/HH는 기존 설정대로 off다. [과학 계약](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/dossier/SCIENTIFIC_CONTRACT.md)을 이 입력 선택의 기준으로 사용한다.

### 2.2 현재 \(\mu\) node는 azimuth 평균 ring이다

현재 \(\texttt{ConditionalPhotonNode}\)의 \(\mu_q\)는 symmetry axis에 대한 방향 cosine이다. 한 node는 azimuth를 평균한 spectral/angular ring이며, 그 \(n_q\)와 \(N_q\)에는 이미 해당 ring의 quadrature weight가 포함된다. 따라서 이 node의 각도 평균은

\[
\langle e^{\hat i}\rangle_q=(0,0,\mu_q),\qquad
\langle e^{\hat i}e^{\hat j}\rangle_q
=\operatorname{diag}\!\left(
\frac{1-\mu_q^2}{2},\frac{1-\mu_q^2}{2},\mu_q^2\right).
\tag{K1}
\]

\(\mu_q\)만으로 임의의 azimuth를 골라
\((\sqrt{1-\mu_q^2},0,\mu_q)\)라는 단일 ray를 만들면 다른 모멘트를 계산하게 된다. 현재 adapter는 (K1)을 사용한다. 명시적 3차원 방향을 받는 별도 adapter를 만들 경우에는 unit \(e_q^a\)와 그 방향에 적분된 count를 입력 계약으로 추가한다.

개별 photon의 \((\mathcal E/c)(u+e)\)는 null이다. Ring 평균 \((\mathcal E/c)(u+\mu e_z)\)는 양의 null photon momenta를 평균한 벡터이므로 \(|\mu|<1\)에서 timelike일 수 있다. 개별 photon의 null 검사를 ring 평균에 적용하지 않는다. 아래 positivity bound는 두 표현에서 모두 성립한다.

### 2.3 필수 입력

이름은 개념적 interface다. 실제 Rust 자료형은 기존 owned bundle과 공통 scalar/Jet 표현에 맞춘다.

| 입력 | 단위·형태 | 소유와 허용 조건 |
|---|---|---|
| \(t_*,a_{\rm rel},b,H,s\) | s, dimensionless, s\(^{-1}\) | 하나의 stage가 공급한 geometry. \(V=a_{\rm rel}^3>0\) |
| \(n_H,n_{\rm He},x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w\) | proper cm\(^{-3}\), fractions, eV/H | 현재 공통 gas candidate. 물리 simplex와 provider domain |
| \(E_q,\mu_q\) | eV, dimensionless | finite \(E_q>0,\ |\mu_q|\le1\), 기존 cross-section domain |
| \(N_q\) | reference cm\(^{-3}\) | 모멘트를 평가할 **현재 candidate**의 node count, finite \(N_q\ge0\) |
| \(S_{q,\rm ref}\) | reference cm\(^{-3}\) s\(^{-1}\) | 해당 stage 소유의 외부 photon source, finite·nonnegative. §5의 source 소유 선택 적용 |
| \(\mathcal R_{iq}\) | proper cm\(^{-3}\) s\(^{-1}\), node × 3 | 기존 owned bundle의 원시 흡수 사건. 순서 HI, HeI, HeII. finite·nonnegative |
| \(\mathcal Q_{\rm esc}\)와 기존 thermal/binding 사건 출력 | proper erg cm\(^{-3}\) s\(^{-1}\) | 같은 Case A 소비의 결과. escape angular closure를 별도 tag로 명시 |
| \(c,\epsilon_{\rm eV}\), binding/cutoff identity | cm/s, erg/eV, eV | 기존 model 상수 재사용 |

\[
\mathcal E_q=\epsilon_{\rm eV}E_q=\hbar\omega_q,\qquad
n_q=\frac{N_q}{V},\qquad
\mathfrak s_q=\frac{S_{q,\rm ref}}{V},\qquad
\mathcal R_{iq}=c\,n_i\sigma_i(E_q)n_q.
\tag{K2}
\]

모든 node 배열과 \(\mathcal R_{iq}\)의 row는 같은 node identity·에너지·순서를 공유한다. 배열 길이가 같다는 사실만으로 재정렬된 row를 결합하지 않는다. 원시 사건을 전달받은 모멘트 소비자는 \(\mathcal R\)을 다시 평가하거나 \(c\)를 한 번 더 곱하지 않는다.

## 3. 출력과 계산식

### 3.1 상태 모멘트와 흡수 모멘트

상태 모멘트에는 \(n_q\), 상호작용 모멘트에는 \(\mathcal R_{iq}\)를 사용한다.

| 출력 | 정의 | 단위 |
|---|---|---|
| Photon number \(n_\gamma\) | \(\sum_qn_q\) | cm\(^{-3}\) |
| Energy density \(\rho_\gamma\) | \(\sum_q\mathcal E_qn_q\) | erg cm\(^{-3}\) |
| Axial energy flux \(q_z\) | \(c\sum_q\mathcal E_qn_q\mu_q\) | erg cm\(^{-2}\) s\(^{-1}\) |
| \(P_\parallel\) | \(\sum_q\mathcal E_qn_q\mu_q^2\) | erg cm\(^{-3}\) |
| \(P_\perp\) | \(\tfrac12\sum_q\mathcal E_qn_q(1-\mu_q^2)\) | erg cm\(^{-3}\) |
| \(\Delta P\) | \(P_\parallel-P_\perp\) | erg cm\(^{-3}\) |
| \(\pi_{\hat i\hat j}\) | \(\operatorname{diag}(P_\perp-\rho_\gamma/3,P_\perp-\rho_\gamma/3,P_\parallel-\rho_\gamma/3)\) | erg cm\(^{-3}\) |
| Shear power \(\sigma:\pi\) | \(2s\Delta P\) | erg cm\(^{-3}\) s\(^{-1}\) |
| Channel absorption power \(\mathcal Q_{{\rm abs},i}\) | \(\sum_q\mathcal E_q\mathcal R_{iq}\) | erg cm\(^{-3}\) s\(^{-1}\) |
| Channel absorption force \(f_{{\rm abs},z,i}\) | \(\sum_q\mathcal E_q\mathcal R_{iq}\mu_q/c\) | erg cm\(^{-4}\) |
| Total \(\mathcal Q_{\rm abs},f_{{\rm abs},z}\) | 각 channel의 합 | 각각 위 단위 |

현재 ring adapter에서 \(q_x=q_y=f_{{\rm abs},x}=f_{{\rm abs},y}=0\)이다. 이것은 azimuth 평균의 결과다. \(\mu\)-반사 대칭을 추가하지 않은 일반 입력에서는 \(q_z\)와 \(f_{{\rm abs},z}\)가 남을 수 있다.

흡수 운동량에는 항상 **전체 photon energy \(\mathcal E_q/c\)**를 쓴다. Photoheating의 \(\epsilon_{\rm eV}(E_q-\chi_i)\)를 momentum weight로 사용하지 않는다. 같은 사건의 에너지 분할은

\[
\mathcal Q_{{\rm heat,PI},i}
=\sum_q\epsilon_{\rm eV}(E_q-\chi_i)\mathcal R_{iq},\qquad
\mathcal Q_{{\rm bind,PI},i}
=\sum_q\epsilon_{\rm eV}\chi_i\mathcal R_{iq},
\tag{K3}
\]
\[
\mathcal Q_{{\rm abs},i}
=\mathcal Q_{{\rm heat,PI},i}+\mathcal Q_{{\rm bind,PI},i}.
\]

이는 [공변 사건 유도](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/derivations/COVARIANT_EVENT_EXCHANGE.md) 식 (4)–(7)의 계산식이다. CI/RR/DR와 kinetic power는 기존 공통 사건 ledger가 계속 소유한다.

### 3.2 같은 사건의 local exchange 출력

현재 common-frame isotropic Case A escape closure를 명시적으로 선택하면

\[
\mathcal L^a=(\mathcal Q_{\rm esc}/c)u^a,\qquad f_{\rm esc}^a=0.
\tag{K4}
\]

이를 위한 출력 tag에는 기체 프레임과 \(\texttt{ComovingIsotropicEmissionMoment}\) 선택을 남긴다. 기존 \(\mathcal Q_{\rm esc}\)만으로 새 photon count·spectrum·escape stress evolution을 생성하지 않는다. \(\mathcal Q_{\rm esc}=0\)에서는 power와 momentum이 모두 0이다.

외부 source를 이 stage가 직접 소유할 때 그 모멘트는

\[
\mathcal Q_{\rm ext}=\sum_q\mathcal E_q\mathfrak s_q,\qquad
f_{{\rm ext},z}=\sum_q\mathcal E_q\mathfrak s_q\mu_q/c.
\tag{K5}
\]

기체 정지 orthonormal frame의 \((0,x,y,z)\) 성분으로

\[
\mathcal A^{\hat a}
=(\mathcal Q_{\rm abs}/c,0,0,f_{{\rm abs},z}),\quad
\mathcal S^{\hat a}
=(\mathcal Q_{\rm ext}/c,0,0,f_{{\rm ext},z}),
\]
\[
G_g=\mathcal A-\mathcal L,\qquad
G_{\gamma,p}=-\mathcal A+\mathcal S,\qquad
G_{\rm esc}=\mathcal L.
\tag{K6}
\]

따라서 같은 event object에서
\(G_g+G_{\gamma,p}+G_{\rm esc}=\mathcal S\)를 구성한다.
\(\mathcal Q_g=\mathcal Q_{\rm abs}-\mathcal Q_{\rm esc}\)는 binding을 포함한 gas power이고, 기존 thermal power와 구별한다.

## 4. 정규화와 cgs → SI 경계

직전 PRIMARY_THEORY_03의 reference/proper/per-H 계약을 그대로 사용한다.

\[
N_q=Vn_q,\quad n_{H,\rm ref}=Vn_H,\quad
p_q=\frac{N_q}{n_{H,\rm ref}}=\frac{n_q}{n_H},
\]
\[
\mathcal P_{iq}=\frac{\mathcal R_{iq}}{n_H},\qquad
S_q^{(H)}=\frac{S_{q,\rm ref}}{n_{H,\rm ref}}
=\frac{\mathfrak s_q}{n_H}.
\tag{K7}
\]

Per-H power가 eV/H/s라면 proper cgs power로 갈 때 \(n_H\epsilon_{\rm eV}\)를 곱한다. 원시 proper 사건을 받은 경우에는 \(n_H\)를 추가로 곱하지 않는다. \(A_{iq}=hV_*\mathcal R_{iq}\)라는 reference integrated event를 받은 adapter는 \(h>0\)에서 \(\mathcal R=A/(hV_*)\)로 대응한다. \(h=0\)은 직접 사건률 또는 zero-step 계약으로 처리해 \(0/0\)을 만들지 않는다.

AXI 단위 경계는 다음과 같다. 새 flux와 force는 기존 energy/power의 변환계수와 다르다.

| cgs 값 | SI 값으로의 배수 | SI 단위 |
|---|---:|---|
| \(n\), \(\mathcal R\) | \(10^6\) | m\(^{-3}\), m\(^{-3}\) s\(^{-1}\) |
| \(\mathcal E\) | \(10^{-7}\) | J |
| \(\rho,P,\pi\) | \(0.1\) | J m\(^{-3}\) = Pa |
| \(\mathcal Q,\sigma:\pi\) | \(0.1\) | W m\(^{-3}\) |
| \(q\) | \(10^{-3}\) | W m\(^{-2}\) |
| \(f\), \(G^{\hat a}\) | \(10\) | N m\(^{-3}\) |
| \(c_{\rm cm/s}\) | \(10^{-2}\) | m/s |

예를 들어
\(\mathcal Q_{\rm SI}/c_{\rm SI}
=10\,\mathcal Q_{\rm cgs}/c_{\rm cgs}\)이므로 (K6)의 시간·공간 성분은 같은 배수 \(10\)으로 변환된다. Native의 eV 인수, cgs 사건, AXI SI 결과를 한 자료형 안에서 이름 없이 혼합하지 않는다. 변환은 한 boundary에서 수행하고 결과 schema에 단위를 기록한다.

## 5. 사건·weight·birth·endpoint energy의 단일 소유

### 5.1 한 bundle에서 한 번 소비

현재 \(\texttt{CaseAEventBundle::into_ledger}\)는 owned \(\texttt{photo_by_node}\)를 node와 zip해 소비한다. 이 loop에서 \(\mathcal Q_{{\rm abs},i}\)와 \(f_{{\rm abs},z,i}\)를 함께 누적하거나, 동일 immutable 사건 view를 사용하는 공통 선형 투영에 그 소비를 위임한다. Aggregate FT03 RHS를 따로 더하고 새 사건을 다시 더하는 경로를 만들지 않는다.

현재 state loop가 계산하는 \(\rho_\gamma,\Delta P\)에는 \(q_z,P_\parallel,P_\perp\)를 대응시킨다. 상태 모멘트와 사건 모멘트는 같은 candidate와 node index를 공유한다. 반환되는 summary는 읽기 전용 진단이며, 다시 소비할 source bundle이 아니다.

안정적인 계산에서는
\[
M_{{\rm abs},z}=\sum_{iq}\mathcal E_q\mathcal R_{iq}\mu_q
\]
를 먼저 signed compensated sum으로 누적하고 \(f_z=M_z/c\)로 출력할 수 있다. 이때 \(|M_z|\le\mathcal Q_{\rm abs}\)를 직접 검사할 수 있다. 기존 compensated summation/finite guard를 재사용하고, 음의 사건률·무한 결과를 조용히 clipping하지 않는다.

### 5.2 Weight와 angular Jacobian

현재 \(\texttt{N_q}\)와 \(\texttt{S_ref}\)는 quadrature에 적분된 값이다. \(\texttt{photon_emission_log}(E,z)\)는 angle-integrated 값이고, 현재 stage source에는 이미 \(w_q/\mathcal R_q^3\)가 들어 있다. 모멘트에서는 이 값을 사용한 뒤 \(1/V\)만 필요한 위치에 적용한다. **Weight, \(2\pi\), \(d\mu/2\), \(\mathcal R^{-3}\)를 다시 곱하지 않는다.** (K1)의 \(1/2\)는 transverse second moment 자체의 계수다.

### 5.3 Source birth와 history work

직전 계약의 두 표현 중 하나를 명시적으로 선택한다.

\[
\Phi(p^-+hS^{(H)},0)=\Phi(p^-,S^{(H)}).
\tag{K8}
\]

현재 paired caller처럼 birth를 primary 입력에 이미 더한 경우에는 primary stage source를 0으로 둔다. 직접 source를 받는 adapter는 birth 전 incoming photon과 같은 endpoint source를 받는다. Source vector (K5)와 누적 external injection도 해당 owner에서 한 번 기록한다. Caller가 소유한 birth의 power를 zero-source primary RHS에 다시 넣지 않는다.

Endpoint-energy BE history를 연결할 때 필요한 자료는 서로 구별한다.

- \(N^-\): **물리 history의 birth 전** incoming reference photon.
- \(N_{\rm stage,in}\): caller가 transport/birth를 반영해 만든 primary 입력.
- \(N^+\): candidate endpoint 또는 받아들인 endpoint count.

History work는 첫 번째 자료를 쓴다.

\[
\mathcal W_{\gamma,\rm geom}
=-\sum_q(\mathcal E_q^+-\mathcal E_q^-)N_q^-.
\tag{K9}
\]

반응·source·흡수 momentum은 같은 endpoint \(\mathcal E_q^+,\mu_q^+\)에서 평가한다. (K9)는 그 BE stage의 정확한 product-rule ledger다. 현재 \(\texttt{axisym_conditional::work_ref}\)는
\(\dot W_{\rm ref}=V(H\rho_\gamma+2s\Delta P+2Hu_{\rm th})\)라는 **순간 work 도함수**를 반환하고, \(\texttt{ProductionInterval}\)은 이를 누적 counter로 ODE 적분한다. 일반적으로 반응·source로 \(N_q(t)\)가 변하는 연속 적분의 photon work는 \(\int\sum_q\nu_q\mathcal E_qN_q\,dt\)다. (K9)는 endpoint reaction/source placement로 정의한 이산 ledger이며, transparent·source-free로 \(N_q\)가 일정한 경우에는 같은 characteristic의 정확한 연속 적분과도 일치한다. 연속 DOP853 history에 BE correction을 자동으로 더하지 않는다. 자세한 소유와 유도는 직전 계약 §5 및 [광자 기하 유도](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/derivations/GEOMETRY_AND_PAIRED_BEAMS.md) G50–G56을 따른다.

## 6. 양성성·bounds·zero guard

### 6.1 수학적 bounds

\[
\rho_\gamma\ge0,\quad
P_\parallel,P_\perp\ge0,\quad
P_\parallel+2P_\perp=\rho_\gamma,
\]
\[
|q_z|\le c\rho_\gamma,\qquad
-\rho_\gamma/2\le\Delta P\le\rho_\gamma,\qquad
\mathcal Q_{{\rm abs},i}\ge0.
\tag{K10}
\]

전단 일 \(2s\Delta P\)와 유한 work는 부호를 가진다. 방향 압축이 광자에 에너지를 주는 경우를 허용한다.

전체 방향 표현에서 \(w_{iq}=\mathcal E_q\mathcal R_{iq}\ge0\), \(|e_q|=1\)이므로 삼각부등식으로

\[
c|f_{\rm abs}|
=\left|\sum_{iq}w_{iq}e_q\right|
\le\sum_{iq}w_{iq}
=\mathcal Q_{\rm abs}.
\tag{K11}
\]

Ring은 \(|\langle e\rangle|=|\mu|\le1\)이므로 같은 결과를 준다. 이는 \(\mathcal A^2\le0\)인 future causal absorption source의 양성 조건이기도 하다.

\(\mathcal Q_{\rm abs}=0\)이면 모든 \(w_{iq}=0\)이므로 \(f_{\rm abs}=0\)이다. 이 branch에서는 힘 fraction을 나누어 계산하지 않고, \(\texttt{zero_absorption=true}\)와 \(\texttt{force_fraction=None}\)처럼 정의역을 표시한다. 0 absorption에서 nonzero force가 반환되면 입력/구현 오류로 처리한다.

양의 power에서는
\[
r_{\rm force}=\frac{c|f_{\rm abs}|}{\mathcal Q_{\rm abs}}\in[0,1]
\tag{K12}
\]
를 쓴다. **분모는 gross absorbed power \(\mathcal Q_{\rm abs}\)**다.
\(\mathcal Q_g=\mathcal Q_{\rm abs}-\mathcal Q_{\rm esc}\)는 0 또는 음수가 될 수 있고, energy cancellation이 공간 힘을 없애지 않으므로 force bound의 정규화로 사용하지 않는다.

### 6.2 부동소수점 기준의 출처

현재 AXI의 \(\texttt{closed(sum,scale)}\)는 finite·nonnegative scale을 확인한 뒤

\[
scale=0:\ sum=0,\qquad
scale>0:\ |sum|\le128\,\epsilon_{\rm mach}\,scale
\tag{K13}
\]
을 사용한다. 위치는 \(\texttt{axisym_coupling.rs}\) 102–110이다. 기존 scalar ledger의 이 gate를 유지한다.

새 선형 모멘트의 C1 수용 초안은 같은 predicate와 gross scale을 사용하는 것이다. 예를 들어 paired fixed-frame force는 \(\texttt{closed}(M_z,\mathcal Q_{\rm abs})\), pressure trace는 각 energy-density 항의 gross 합으로 검사한다. Force inequality는 \(|M_z|\le\mathcal Q_{\rm abs}\) 또는 같은 scale의 roundoff 초과분 검사로 구현한다. Channel/state의 단일 변화량 검사도 예상값과 입력 항의 gross scale을 기록한다.

C1은 실제 summation 순서·precision·source revision과 함께 이 기준을 고정한다. 차이가 발견되면 식·입력·합산 오차 원인을 먼저 확인하고, 허용오차를 넓힌 결과를 원래 기준의 통과로 기록하지 않는다. 정확한 수학적 zero와 이 roundoff 판정을 결과에서 구별한다.

## 7. 고정 프레임의 적합성과 실제 callsite

지정된 geodesic common gas, homogeneous pressure, isotropic escape에서 공간 방정식은

\[
\frac{\rho_g+p_g}{c^2}a^a+D^ap_g
=f_{\rm abs}^a-\ell_{\rm esc}^a,\qquad
a=0,\quad Dp_g=0,\quad\ell_{\rm esc}=0.
\tag{K14}
\]

따라서 이 적용의 적합성은 \(f_{\rm abs}=0\)으로 판별한다. \(q_z=0\)은 (K14)의 대체 조건이 아니다.

새 provider는 일반 허용 입력의 모멘트를 계산하고, 예를 들어
\(\texttt{CompatibleWithPrescribedGeodesicFrame}\) 또는
\(\texttt{RequiresMomentumEvolutionOrSpecifiedSupport}\)처럼 적합성을 함께 반환할 수 있다. Nonzero force 자체는 유효한 모멘트 출력이다. 이를 소비할 gas momentum equation이 없는 현재 scalar stage의 적용 범위는 별도로 표시한다.

고정 입력 [STATIC_INPUT_PARITY.json](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/source_map/STATIC_INPUT_PARITY.json)은 2,904 node 중 1,452 opposite-\(\mu\) pair의 \(q_{\rm eV}\), weight, 초기 count가 bitwise 같음을 기록한다. 현재 API는 각 count/source를 독립적으로 받으며 pair equality를 강제하지 않는다. 따라서 fixed IC의 정적 근거, paired 수학적 보존 조건, 일반 API의 실제 입력 검사를 구별한다. Mutable state의 장기 parity는 해당 실행 근거로만 보고한다.

| 현재 source 위치 | 후속 구현 의무 |
|---|---|
| \(\texttt{axisym_conditional.rs}\) 84–119 | 현재 node와 summary의 schema·단위 확인. 새 fields의 버전/직렬화 계약 설정 |
| 같은 파일 \(\texttt{CaseAEventBundle::into_ledger}\), 220–318 | 같은 node별 \(\mathcal R_{iq}\) 소비에서 full-energy absorption power와 force를 함께 생성 |
| 같은 파일 node loop 388–405 | 같은 \(N_q/V\)에서 \(q_z,P_\parallel,P_\perp,\pi,\sigma:\pi\) 계산 |
| 같은 파일 실제 AXI 소비 431–483 | SI boundary 및 기존 scalar derivative/work와의 일치 유지; 새 read-only moment summary 반환 |
| \(\texttt{coupled_primary.rs}\), \(\texttt{ft03_interval.rs}\), \(\texttt{paired_runtime.rs}\) | PRIMARY_PROVIDER_03 공통 표현을 먼저 연결. 새 모멘트가 interval 출력으로 사용되면 같은 node/원시 사건의 interval 선형 투영으로 lift |
| \(\texttt{python/source_bound_interval.py::stage}\) | 동일 시점 geometry/source·이미 적분된 weight·reference count를 공급하는 owner 유지 |

현재 \(\texttt{PrimaryPacket}\)은 energy/count만 가지므로, 그 경로에서 새 모멘트를 요청할 때에는 caller가 해당 packet에 연결된 방향 자료를 명시적으로 공급해야 한다. 원래 node/characteristic identity에 연결된 읽기 전용 metadata를 사용하고, energy만 보고 방향을 재구성하지 않는다. Node를 합치는 adapter는 필요한 energy별 첫째·둘째 각도 모멘트와 absorption 가중치를 보존하는 별도 대응을 제시한다.

Interval 모멘트를 포함관계로 주장할 경우에는 \(E,\mu\)가 고정된 stage에서 같은 expression graph를 interval/Jet으로 평가한다. Eliminated photon \(N_q(y)\)의 gas derivative도 기존 \(\Phi\)를 통해 전달한다. Point에서 계산한 새 모멘트를 Jet 상수로 감싸는 방식은 이 도함수 계약을 충족하지 않는다. 읽기 전용 point 진단만 구현한 단계는 그 범위로 기록하며, gas velocity를 implicit 네 변수에 조용히 추가하지 않는다.

현재 positional RHS/EVENTS protocol은 실제 schema를 읽어 보존하거나 명시적 새 version/별도 응답으로 확장한다. 새 scalar/vector field의 순서·단위·frame/closure tag를 receipt에 남긴다.

## 8. 앞으로 실행할 최소 native 판별 사례

다음은 **후속 코딩 단계의 수용 사례**다. 이 문서를 작성하며 native code를 실행한 결과가 아니다. Raw event fixture는 내부 단일 소비와 선형 투영을 검증하고, 실제 FT03/native stage 비교는 선택된 provider 경로를 검증한다.

| 사례 | 입력과 정확한 참조값 | 검출할 오류 |
|---|---|---|
| Zero absorption | 모든 \(\mathcal R_{iq}=0\), photons는 0 또는 양수 허용. \(\mathcal Q_{\rm abs}=f_{\rm abs}=0\), force fraction은 undefined branch | 0 나눗셈, photon flux를 absorption force로 대용 |
| 한 channel의 단일 사건 변화 | 동일 candidate의 node \(q\), channel \(i\)에 test-only \(\delta\mathcal R>0\). \(\delta Q_{\rm abs}=\mathcal E_q\delta\mathcal R,\ \delta f_z=\mathcal E_q\mu_q\delta\mathcal R/c\) | 사건 두 번 소비, heat energy를 momentum에 사용 |
| 같은 변화의 scalar 분할 | \(\delta Q_{\rm heat}=\epsilon_{\rm eV}(E_q-\chi_i)\delta\mathcal R,\ \delta Q_{\rm bind}=\epsilon_{\rm eV}\chi_i\delta\mathcal R\). 고정 photon state의 \(q,P\)는 변하지 않음 | state moment와 event moment 혼동 |
| 하나의 \(\mu=0\) ring | \(q=f_z=P_\parallel=0,\ P_\perp=\rho/2,\ \Delta P=-\rho/2\) | 임의 azimuth의 단일 ray로 잘못 치환 |
| 하나의 axial ring \(\mu=\pm1\) | \(q_z=\pm c\rho,\ f_z=\pm Q_{\rm abs}/c,\ P_\parallel=\rho,\ P_\perp=0\) | \(c\)·force 부호·sharp bound 오류 |
| Matched opposite pair | 같은 \(E,N,S,\mathcal R_i\), 반대 \(\mu\). \(q_z=f_z=0\), \(\Delta P\)는 일반적으로 nonzero | even stress와 odd moment 혼동 |
| Zero-flux spectral counterexample | 반대 axial 방향에 \(U_+=U_-=U_0/2>0,\ \kappa_+=2\kappa,\ \kappa_-=\kappa>0\). \(q=0,\ f_z=\kappa U_0/2,\ Q_{\rm abs}=3c\kappa U_0/2,\ r_{\rm force}=1/3\) | \(q=0\)만으로 fixed-frame 적합성 승인 |
| Two/six-beam family | G39–G42의 \(\eta=1,2/3,1/3\). \(q=f=0,\ \sigma:\pi=s\rho(3\eta-1)\) | pressure factor \(1/2\), shear sign, moment 합산 |
| Net gas power cancellation | \(Q_{\rm esc}=Q_{\rm abs}>0\)이고 \(f_{\rm abs}\ne0\)인 fixture. \(Q_g=0\), gross force bound는 finite | \(Q_g\) 정규화, isotropic escape의 잘못된 force 상쇄 |
| Exchange/단위 | (K3),(K6)와 cgs→SI 변환을 동일 raw 사건에서 비교. 시간·공간 four-force 성분 모두 ×10 | power ×0.1을 flux/force에 오용 |
| Source와 finite work | birth 선합산/직접 source 표현의 (K8) 동치, (K9)의 birth 전 \(N^-\), endpoint momentum. G43–G49의 exact \(H=0\) family를 reference 사용 | source 두 번 합산, incoming/endpoint count 혼동 |

Spectral counterexample의 \(2:1\) opacity는 양의 원시 사건을 만드는 대수 fixture다. 이를 실제 Verner 두 에너지의 측정 비율로 기록하지 않는다. 실제 coefficient 경로에는 native provider가 반환한 값과 기존 frozen 입력을 사용한다.

단일 사건 witness는 기존 \(\texttt{CaseAEventBundle}\) 소비를 통해 출력 변화가 나타나는지 확인한다. 보존량만 보는 검사는 모든 channel이 두 번 더해져도 일부 항등식을 만족할 수 있으므로, 정확한 변화량을 함께 대조한다. 테스트용 주입은 public production의 FT03 선택 정책을 바꾸지 않는다.

새 실제 stage 비교는 source/build receipt, 입력 SHA, 명령, native 호출 수, raw 출력, 위 residual/scale을 남긴다. C1의 고정된 기준을 충족하면 변경 없는 이전 history suite를 다시 돌리는 대신, 남은 새 구현 의존성으로 진행한다.

## 9. 현재 완료된 검산과 새 native 실행의 구별

이번 THEORY04의 실제 새 symbolic 검산은 **45 unique groups = 24 + 5 + 16**이다.

| 실제 근거 | 계산 범위 | 상태 |
|---|---|---|
| [XACT_COVARIANT_RESULT.json](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/XACT_COVARIANT_RESULT.json) | 24 xAct tensor groups: projector/null photon/full-energy absorption/escape/교환/observer 및 gas·radiation differential projections | 모두 True, tensor residual 모두 0 |
| 같은 결과의 별도 scalar groups | 5개: reference-mass 소거, thermal 복원, spectral force 반례, observer normalization | 모두 True |
| [GEOMETRY_EXACT_RESULT.json](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/GEOMETRY_EXACT_RESULT.json) | 16개: local-frame algebra, directional redshift, paired-beam moments, BE allocation·work·exact family | 모두 True |
| [EXECUTION_RECORD.md](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/EXECUTION_RECORD.md) | 실제 kernel/package identity, 입력·원응답, 진단과 성공 경로 | 보존됨 |
| 이번 새 native build/RHS/ODE/history | 이 모멘트 provider 구현 및 §8 사례 | 미실행; 후속 CODING 의무 |

최종 root 실행은 Wolfram Language 15.0.1, xAct/xTensor 1.3.0을 실제 load하고 supported pure-Wolfram xPerm backend를 사용했다. \(\texttt{xPermExternalBackend=false}\)를 그대로 기록한다. 초기 smoke checks, 이전 성공 시도, 이전 PRIMARY_THEORY_03의 47개 symbolic groups는 이 45개에 다시 더하지 않는다.

이 근거는 계약 식의 증명·정확한 기호 검산이다. Native callsite가 새 fields를 실제로 한 번 계산하고 소비했다는 근거는 §8의 후속 실행으로 만든다.

## 10. Nonzero gas momentum을 소비하기 위한 다음 이론 의무

일반 \(f_g\ne0\)에 대해 다음을 하나의 공통 기체 속도 모델로 구성해야 한다.

1. **운동 변수와 공간 방정식.** \(u^2=-1\)을 보존할 velocity/rapidity 좌표와 lab/normal observer를 고르고, (K14)의 acceleration·pressure gradient를 진화시킬 식과 초기조건을 정한다. 외부 support를 선택하면 그 force와 energy-work의 소유를 명시한다.
2. **기체 프레임의 사건 입력.** 고정 observer photon \(p_q^a\)에서
   \(\mathcal E_{q,u}=-c u_ap_q^a\),
   \(e_{q,u}^a=cp_q^a/\mathcal E_{q,u}-u^a\)를 구성하고, 에너지·각도·phase-space measure 및 proper 사건률 변환을 유도한다. 원자 cross section은 이 \(\mathcal E_{q,u}/\epsilon_{\rm eV}\)에서 평가한다.
3. **Momentum–energy 동시 이산화.** 동일 \(\mathcal A-\mathcal L\)의 두 투영을 kinetic·thermal·binding energy와 함께 소비하는 update를 정한다. 중성 기준 질량에 이미 포함된 전자 rest mass를 다시 더하지 않고, \( \rho_g+p_g \)의 inertia를 사용한다.
4. **방향 표현과 transport.** Axial bulk motion으로 ring 표현을 유지할지, 일반 방향으로 확장할지 먼저 정한다. 일반 boost가 만드는 azimuth 의존성과 photon flux/pressure transport를 공급할 상태 또는 closure가 필요하다.
5. **Observer reference와 판별식.** 이미 증명된
   \[
   \mathcal Q_g(n)=\gamma[\mathcal Q_g(u)-c\beta v_af_g^a]
   \]
   및 isotropic escape의 boosted projection을 local reference로 사용하고, 새 동적 scheme의 보존·양성·공간 수지와 해당 근사 차수를 검증한다.

이 항목이 완성되면 general force를 실제 velocity evolution에 넣는 코딩 계약으로 넘어간다. 현재 moment provider는 그 입력을 계산하고 fixed-frame 적합성을 판별하는 단계다. 별도 all-Bianchi abundance/reference-current/class-B D2.3 문제나 종별 상대 속도 모델을 이 계약에 추가하지 않는다.

## 11. 완료 영수증과 재개점

추가 moment provider의 완료 영수증에는 다음이 필요하다.

- PRIMARY_PROVIDER_03의 완료 또는 정확한 남은 callsite와 그 상태.
- 새 source commit, 변환·frame·angular/escape closure tag, 출력 schema.
- 같은 raw events를 사용한 실제 production 경로와 읽기 전용 summary의 연결.
- §8의 입력·참조값·명령·raw 출력·수용 기준·결과; 기존과 새 실행의 구분.
- \(\mathcal Q_{\rm abs}=0\) guard, gross-force bound, 실제 fixed-frame 적합성 결과.
- Nonzero force 입력에 남은 §10 의무와 다음 이론 단위의 입력.

이 계약의 source mapping은 [SOURCE_MAP.md](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/source_map/SOURCE_MAP.md), 식은 [COVARIANT_EVENT_EXCHANGE.md](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/derivations/COVARIANT_EVENT_EXCHANGE.md) 및 [GEOMETRY_AND_PAIRED_BEAMS.md](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/derivations/GEOMETRY_AND_PAIRED_BEAMS.md), 이산화와 source 소유는 직전 PRIMARY_THEORY_03 코딩 계약에 연결한다.
