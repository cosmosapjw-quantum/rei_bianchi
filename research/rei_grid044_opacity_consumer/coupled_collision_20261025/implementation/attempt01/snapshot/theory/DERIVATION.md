# 선택된 광자–원자 충돌 연산자와 기준밀도 정규화

이번 유도는 16개 에너지 packet과 원 명세의 21개 원자·동위원소 상태를 연결하는 순간 충돌 연산자, 40×40 상태 Jacobian, 두 외부 source 진폭 미분을 구성한다. 이전 frozen-radiation target Jacobian에서 빠져 있던 광자→표적 및 표적→광자 cross block이 새 결과이다. 전체 목표에서 위치는 **N3 충돌 인터페이스 → N4 유한 연산자 검증**이며, 원 N6는 HOLD이다.

## 1. 정의와 채택 범위

시간은 normal observer의 proper second, metric signature는 \((-+++)\), \(c=299792458\ {\rm m\,s^{-1}}\)이다. \(n_{\rm ref}>0\)는 proper 기준밀도, \(N_j=n_{\gamma,j}/n_{\rm ref}\), \(y_i=n_i/n_{\rm ref}\), \(E_j\)는 normal tetrad에서 측정한 eV 에너지이다. 상태 순서는
\[
z=(N_0,\ldots,N_{15},y_0,\ldots,y_{20},B,K,X_{\rm ext})
\]
로 고정한다. 21개 표적 순서는 IMPLEMENTATION_CONTRACT.json에 있으며 원 명세의 Li6→Li7 순서를 보존한다. 원 provider의 Li7→Li6 배열에는 이름으로 대응한다. 전자는 별도 상태로 중복 진화시키지 않고 \(y_e=q_{\rm ion}^{T}y\)로 정한다.

각 adjacent charge edge \(e\)는 lower \(l(e)\), upper \(u(e)\), threshold \(\chi_e\), elemental channel \(a(e)\)를 갖는다. incidence 행렬은 \(S_{ie}=\delta_{i,u(e)}-\delta_{i,l(e)}\). 13개 edge와 HI, HeI, HeII, LiI, LiII, LiIII의 기존 단면적을 재사용한다. 동위원소 사이 electronic rate equality는 상속된 모델 가정이다. LiI는 64.39eV 아래 PH2, 그 이상 원 PH1 outer-2s valence 분기를 사용한다.

\(B\)는 neutral reference에서 누적 ionization potential \(\epsilon_i\)에 대한 redundant ledger로 \(B=\epsilon^T y\)에서 시작한다. \(K\)는 primary electron에 주입된 에너지이며 열적 에너지나 secondary deposition closure가 아니다. \(X_{\rm ext}\)는 외부에서 주입된 photon energy의 ledger이다. 세 에너지는 모두 eV/reference이며 total energy에는 \(B\)만 한 번 넣는다.

## 2. 물리적 밀도에서 quotient 항 유도

Proper 밀도 \(\rho\)와 기준밀도가
\[
\dot\rho+3H\rho=C,\qquad
\dot n_{\rm ref}+3Hn_{\rm ref}=S_{\rm ref}
\]
를 만족하면 직접 미분하여
\[
\frac{d}{dt}\frac{\rho}{n_{\rm ref}}
=\frac{C}{n_{\rm ref}}-\Lambda\frac{\rho}{n_{\rm ref}},
\qquad
\Lambda=\frac{\dot n_{\rm ref}+3Hn_{\rm ref}}{n_{\rm ref}}
=\frac{S_{\rm ref}}{n_{\rm ref}}
\]
를 얻는다. 따라서 현재 Href가 conserved comoving nuclei density로 \(a^{-3}\)에 비례하면 **\(\Lambda=0\)**이다. 시간 의존성만을 이유로 추가 \(-3H\)를 넣으면 희석을 중복 계산한다. 실제로 생성되는 기준종을 선택하면 해당 생성률로 \(\Lambda\)를 정해야 한다.

본 API는 순간 \(n_{\rm ref},E_j,q_{sj}\)를 독립 입력으로 고정한다. \(\Lambda\)와 선택적 상태 gradient \(g=\nabla_z\Lambda\)를 공급하면 모든 normalized coordinate에 동일한 quotient 항을 적용한다. 이는 국소 미분 계약이다. 기준밀도가 상태 자체의 함수라면 \(k=c n_{\rm ref}\sigma\)의 chain rule과 기준좌표 사상을 추가로 지정해야 한다. 물리적 기준종의 생성망을 이번 연산자로 대체하지 않는다.

## 3. 한 사건에서 결합된 방정식

\[
k_{ej}=c\,n_{\rm ref}\,\sigma_{a(e)}(E_j),\qquad
r_{ej}=k_{ej}\,y_{l(e)}N_j,\qquad
q_j=\sum_s\alpha_s q_{sj}.
\]
\(k\)의 단위는 s\(^{-1}\), \(r\)는 events/reference/s이다. \(q_{sj}\)는 MODEL_CONFIG의 물리적 amplitude \(A_s\)를 이미 포함한 frozen source template이고, \(\alpha_s\)는 그와 구분되는 독립 무차원 multiplier이다. 채택된 단면적은 \(E_j<\chi_e\)에서 0이다. Photon 하나의 흡수가 ionic charge를 1 증가시키고, \(\chi_e\)를 ionization energy로 저장하며 \(E_j-\chi_e\)를 primary electron에 전달한다. 이에 따라
\[
\begin{aligned}
F_{N_j}&=q_j-\sum_e r_{ej}-\Lambda N_j,\\
F_{y_i}&=\sum_{ej}S_{ie}r_{ej}-\Lambda y_i,\\
F_B&=\sum_{ej}\chi_e r_{ej}-\Lambda B,\\
F_K&=\sum_{ej}(E_j-\chi_e)r_{ej}-\Lambda K,\\
F_{X_{\rm ext}}&=\sum_j E_jq_j-\Lambda X_{\rm ext}.
\end{aligned}
\]
외부 source power는 \(X_{\rm ext}\)와 photon에 들어가며 gas heating으로 직접 들어가지 않는다. Source의 escape factor 및 spectral/angular normalization은 producer가 공급한 \(q_{sj}\)에 한 번만 포함한다.

## 4. 완전한 선택 충돌 Jacobian

사건율의 유일한 collision state 미분은
\[
\frac{\partial r_{ej}}{\partial y_i}
 =k_{ej}N_j\delta_{i,l(e)},\qquad
\frac{\partial r_{ej}}{\partial N_k}
 =k_{ej}y_{l(e)}\delta_{jk}.
\]
각 사건의 변화 column을
\[
m_{ej}=(-{\bf e}_j,\;S_{\cdot e},\;\chi_e,\;E_j-\chi_e,\;0)^T
\]
로 놓으면 \(F_{\rm col}=\sum m_{ej}r_{ej}\), \(J_{\rm col}=\sum m_{ej}(\nabla r_{ej})^T\)이다. 따라서
\[
\boxed{J=J_{\rm col}-\Lambda I-zg^T}.
\]
예를 들어
\[
J_{N_j,y_i}=-\sum_e k_{ej}N_j\delta_{i,l(e)},\quad
J_{y_i,N_j}=\sum_e S_{ie}k_{ej}y_{l(e)}
\]
이며 두 cross block을 모두 구현해야 한다. 전체 결합 Jacobian은 Metzler가 아니다. Fixed-radiation target subblock의 generator 구조와 full coupled 구조를 구분한다.

Source template 진폭을 독립 parameter로 미분할 때
\[
\partial_{\alpha_s}F=
(q_{s0},\ldots,q_{s15},0_{21},0,0,\sum_jE_jq_{sj})^T
\]
이다. 이 partial에서는 photon state \(N\)를 고정한다. Fixture 생성식 \(N=(1\,{\rm s})q\)를 함께 미분하면 다른 total derivative가 된다. \(\Lambda\)가 진폭에 의존하면 추가 \(-z\,\partial_{\alpha_s}\Lambda\)가 필요하나 현재 source columns는 \(\Lambda\)를 고정한다.

선택적 \(\partial_{n_{\rm ref}}F\)는 per-reference source, \(E,\Lambda\) 고정 시 \(F_{\rm col}/n_{\rm ref}\)이다. Proper emissivity \(j_{\rm proper}\)를 고정하고 \(q=j_{\rm proper}/n_{\rm ref}\)로 정의한 sensitivity에는 추가 \(-Q/n_{\rm ref}\)가 있다. 두 derivative를 혼용하지 않는다.

## 5. 불변량, 에너지와 양성

Isotope census 행렬 \(C_{\rm iso}\)와 baryon weights \(A\)는 \(C_{\rm iso}S=0,\ A^TS=0\)이므로
\[
C_{\rm iso}F_y=-\Lambda C_{\rm iso}y,\qquad
A^TF_y=-\Lambda A^Ty.
\]
즉 proper 물리량의 보존과 reference-normalized 표현의 quotient 변화가 양립한다. 전자 생성 및 binding constraint는
\[
q_{\rm ion}^TF_y=\sum r_{ej}-\Lambda y_e,\qquad
F_B-\epsilon^TF_y=-\Lambda(B-\epsilon^Ty).
\]
따라서 \(\sum r_{ej}\)가 physical electron production per reference이고 \(q_{\rm ion}^TF_y\)는 normalized electron abundance derivative이다.

Photon+electron event count \(L=\sum_jN_j+y_e\)는
\[
\dot L+\Lambda L=\sum_jq_j
\]
를 만족한다. 선택 충돌계의 energy-accounting ledger
\[
{\cal E}=E^TN+B+K-X_{\rm ext}
\]
에 대해서 frozen \(E\)에서 \(w^TF=-\Lambda w^Tz\), \(w=(E,0_{21},1,1,-1)\)이다. 미분된 identity는
\[
w^TJ=-\Lambda w^T-(w^Tz)g^T.
\]
이는 source energy와 binding을 이중 집계하지 않는 검사식이다.

실제 characteristic packet 에너지가 변하면
\[
\frac{d{\cal E}}{dt}+\Lambda{\cal E}=\dot E^TN.
\]
Normal observer의 directional redshift는 기존 geometry에서
\(\dot E=-[H+\sigma_{ab}e^ae^b]E\)이며 LRS에서는
\(-[H+s(3\mu^2-1)]E\)이다. 이 항은 expansion/shear work이다. 현재 angle-integrated source fixture는 directional packet transport를 복원하지 않으므로 \(\dot E\)는 명시적으로 공급한 frozen 진단 입력으로만 취급한다.

Nonnegative source와 상태에서 어떤 \(N_j=0\)이면 그 coordinate의 depletion이 사라진다. 어떤 \(y_i=0\)에서도 outgoing 사건이 사라지고 incoming 사건만 남는다. \(-\Lambda z_i\)도 영면에서 0이다. \(B,K,X_{\rm ext}\)의 영면에서도 주입률은 비음수이다. 따라서 선택 ODE vector field는 nonnegative orthant에 접한다. 이는 임의의 유한 timestep integrator에 대한 양성 보증과는 별도 명제이다.

## 6. 기준 표현의 실제 동등성

양의 smooth \(r(t)\)로 기준을 바꾸어
\[
n_{\rm ref}'=r n_{\rm ref},\quad z'=z/r,\quad
q'=q/r,\quad \Lambda'=\Lambda+u,\quad u=\dot r/r
\]
라 두면 \(r'_{ej}=r_{ej}/r\)이고
\[
F'(z')=F(z)/r-u z'
\]
를 얻는다. 이는 같은 physical density와 source를 다른 reference로 표현한 좌표 동등성이다. \(\Lambda\ne0\) 테스트는 이 관계와 affine \(\Lambda(z)\) Jacobian을 검사한다. 새 baryon production의 증거로 사용하지 않는다.

## 7. 실제 입력과 연결한 유한 fixture

기존 MODEL_CONFIG의 stellar 및 external IGM source를 z=2에서 평가한다. Saved continuous normalizer와 기존 source window, escape fraction, amplitudes를 그대로 재사용한다. Energy intervals는
\([5,5.392,13.6,24.59,54.42,64.39,75.64,122.5,150]\)eV이며 interval당 GL2로 16개 node를 만든다. \(q_{sj}=w_j q_s(E_j,z=2)\), \(N_j=(1\,{\rm s})\sum_s q_{sj}\)로 정한다.

이 fixture는 원 source의 실제 함수와 단면적에 연결된 **unit-exposure operator point**이다. 이전에 진화한 z=2 photon inventory나 target history를 복원한 결과는 아니다. GL2 합이 continuous total source와 정확히 같도록 다시 renormalize하지 않는다. 이번 finite algebra gate와 이전 continuum refinement gate를 별도로 보존한다. 실제 Href는 \(5.151254745827818\,{\rm m^{-3}}\), \(\Lambda=0\)이다.

Target y는 이전 opacity AGGREGATE_PAYLOAD의 target_fixture.y_per_Href를 정확히 재사용한다. 이 positive conditional API fixture의 총 n=T=1e-20/Href는 trace 입력 검사용이며 cosmic abundance를 뜻하지 않는다. 별도 zero-face control에서는 n,T_0,T_1만 0으로 둔다. 정확한 21개 값과 원 payload SHA를 계약에 보존한다.

1초 exposure에서는 photon-target collision derivative가 external injection에 비해 매우 작다. Centered FD는 injection을 끈 같은 collision Jacobian에서 검사하고 source derivative를 별도 검사한다. Complex-step은 injection을 켠 kernel에서 검사가 가능하다. Scaling은 derivative component/subblock characteristic magnitude와 conservation 항들의 절댓값 합을 사용한다. 단위가 다른 작은 physical derivative에 \(\max(1,|J|)\)를 적용하면 zero Jacobian이 통과할 수 있으므로 사용하지 않는다. 특히 rare Li6/Li7 및 trace-T crossblock은 모든 active entry별 상대 CS 검사와 structural zero 검사로 확인한다. 전체 row norm만으로 희귀종 검사를 대체하지 않는다. 허용치는 CS \(2\times10^{-12}\), FD \(2\times10^{-5}\), ledger/reference \(3\times10^{-12}\)이다.

## 8. 세 물리 축과 확보된 근거

| 축 | 현재 결과 |
|---|---|
| 대칭성·게이지 | 기존 LRS/reflection geometry와 fixed normal observer를 유지한다. Spatial coordinate rescaling과 reference normalization 변경은 실제 observer 또는 물리적 source 변경과 구분된다. |
| 불변량 | Isotope/baryon census, charge-derived electrons, binding consistency, photon/electron 사건 수, 에너지 분배와 quotient/redshift identities를 직접 유도하였다. |
| 실제 관측가능량 | Normal observer에서의 photon absorption, target ionization event rate, primary electron injection, source power를 명시된 finite 상태에서 계산하는 인터페이스다. 관측자료에 대한 calibration은 별도 의무다. |

Photon-conserving radiative transfer 문헌은 photon sink와 ionization source의 공통 사건율 사용을 뒷받침한다. Reynolds 등은 coupled radiation/chemistry solve와 Jacobian block 사용의 선행 맥락을 제공한다. 본 quotient term, finite-state ledger 및 block 식은 위에서 직접 유도하였고 문헌 abstract를 상세 공식의 근거로 확대하지 않았다. Source metadata와 실제 도구 접근 기록은 SOURCES.json에 둔다.

Wolfram 대표 block 검산은 arbitrary coefficients의 6-state collision/source/Jacobian/quotient residual 60개를 0으로 반환했다. Xext를 포함한 7-state energy-gradient 및 reference-rescaling 검산은 15개를 0으로 반환했다. 첫 Xext 실행의 symbol warning과 이를 변수명으로 교정한 실제 재실행을 모두 보존한다. Remote CPU는 제공되지 않았다. xAct가 필요한 새 tensor curvature 계산은 없어 실행하지 않았다.

본 이론 agent는 local numerical science를 실행하지 않았다. 실제 40-state provider/fixture 실행 결과는 implementation 결과와 independent review가 별도로 판정한다. n/T 생성, neutron decay의 p feed, CR/중성미자/inverse-beta, LiI core/Auger와 secondary thermal deposition은 원래 열린 물리 의무로 유지된다. 현재 constructive result에 strong no-go 주장은 없다.

## 9. 재개 지점

이 계약으로 full 40-state kernel, source columns, quotient-aware identities 및 reference-equivalence tests를 구현하고 기존 source campaign 잔여 예산 내에서 한 번 실행한다. 통과 시 original N3/N4의 선택 충돌 consumer 의무를 닫고, 실제 radiation transport/continuous field와 thermal/nuclear source 확장 의무를 구분해 다음 노드로 전달한다. Whole-goal physical completion percentage는 정의된 가중치가 없으므로 임의 수치로 만들지 않는다.

