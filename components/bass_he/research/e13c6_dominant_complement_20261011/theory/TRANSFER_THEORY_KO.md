# E13C6: 일반 두 구간 complement 경로의 동일 목표 전달 계약

## 결론과 근거 상태

**이론 결론 — derived.** OFF node 101·102와 410·413의 새 enclosure는 각 node에 고정된 두 captured segment의 동일한 연속 문제를 풀 때 기존 full-finite 항과 비교할 수 있다. 첫 incoming defect는 정확히 0이고, 둘째는 첫 구간의 true endpoint에서 둘째 frozen 초기값을 뺀 값이다. 첫 구간의 coefficient remainder, 수치 반경, exact-frozen/captured 표현 차이를 함께 전달해야 한다. Energy seam은 signed stock jump이며 whole-path energy ledger에서 뺀다.

이 결론은 PR21의 `E13C5_DOMINANT_COMPLEMENT_TRANSFER_ADMISSIBILITY01`을 구체화한다. 직접 읽은 PR19 원 이론 및 `path_enclosure.py`의 `local_integrals`, `frozen_outputs_and_gains`, `remainder_bounds`, `segment`, `seam`, `run_track`과 일치한다. `local_enclosure.py`의 `Coefficients` 및 `integrands`도 직접 대조했다. 원 source를 수정하거나 후보 경로의 coefficient를 평가하지 않았다. [S1–S4]

**실행 근거 — implementation-verified, exact toy scope.** 별도 `theory_controls/exact_transfer_toys.py`를 한 번 실행하여 41개 정확 대수 검사를 통과했다. 후보 scientific solver 및 coefficient 호출은 0회다. 이 기여자는 최종 독립 decision reviewer가 아니다. 실제 네 node의 입력 binding·계산 성공·최종 numerical acceptance는 owner와 별도 reviewer의 자료에서 판정한다.

호스트가 제공한 모델 identity는 **GPT-6 Astra Pro**다. 적용한 연구 하네스는 GPT-6 Astra v4.0.0의 `PROJECT_INSTRUCTIONS.md`, state 템플릿 및 phase 6·7이다. 하네스의 비어 있는 state 템플릿은 프로젝트의 실행 증거로 사용하지 않았다.

## 1. 고정한 문제, 단위, 두 구간 경계

경로의 각 구간 $j=1,2$에서

\[
s=\ln a,\qquad u=s-a_j\in[0,h_j],\qquad t=u/h_j\in[0,1]
\]

로 둔다. `row.a`는 여기서 $a_j$라는 log-scale-factor 구간 시작값이며, scale factor $a=\exp s$ 자체와 구별한다. 코드의 `Jet2` 미분은 $t$에 대한 미분이다. 정확한 연속 목표와 frozen reference는

\[
P_j'=q_j(u)-\Lambda_j(u)P_j,\qquad
F_j'=q_{f,j}-L_jF_j,\qquad F_j(0)=f_{0,j},
\tag{1}
\]
\[
E_j(u)=E_{0,j}e^{-u},\quad
\Lambda_j=\sum_i\lambda_{i,j},\quad
L_j=\sum_i\lambda_{if,j}.
\tag{2}
\]

여기서 prime은 $d/du$다. $u,h,s,L,\Lambda$는 무차원이며, $P$와 number moment는 상속된 photons/H/dη 정규화를 유지한다. $q$는 그 정규화의 $u$당 source이고, energy·heat·redshift moment는 eV를 곱한 정규화다. 원 coefficient의 $c=2.99792458\times10^{10}$ cm/s 및 상수들은 원 binary64 정의를 유지한다. 이 계산은 새로운 GR 유도나 단위계 변경이 아니다. [S3,S4]

원 CSV 숫자는 binary64로 읽힌 값을 exact lift한다. $q_f,\lambda_{if},f_0,E_0,a_j,h_j$를 새로운 midpoint 평가나 더 짧은 decimal로 교체하지 않는다. Energy CSV는 원 binary64 `1.602176634e-12` [erg/eV]의 exact lift $\epsilon$으로 한 번 나눈다. 이 규칙의 변경은 단순 정밀화가 아니라 목표의 변경이다.

Gas는 같은 captured stage의 old/new 값과 같은 선형 보간 $\theta=(a_j-s_0+u)/(s_1-s_0)$으로 정한다. Source-on과 species mask도 같은 captured branch다. 초기 후보 분류는 PR21 보고서에 근거하며, 이후 새 `inputs/PATH_CONTROLS.json`의 8개 control과 `OLD_PATHS_OFF4.jsonl`의 네 saved path를 직접 읽어 아래 경계를 확인했다. 원 CSV 추출·전체 archive identity 검증은 owner의 입력 provenance와 구분한다. [S1,S2,S5]

| Node | 첫 구간 E0 [eV], 표시 반올림 | 첫 captured n = 둘째 f0, 원 문자열 | Saved true anchor의 strict sign |
|---|---:|---|---|
| OFF 101 | 13.7709313089640 | `7.86123915551072451e-6` | negative |
| OFF 102 | 13.7891218455897 | `7.85874555775688219e-6` | negative |
| OFF 410 | 18.5942559793316 | `6.85444260596829698e-6` | negative |
| OFF 413 | 18.6419685297833 | `6.84331043363154800e-6` | positive |

네 경로 모두 step 1/segment 0 → step 2/segment 0이고, 첫 `f0=0`, source-on, HI-only이다. HeI/HeII의 frozen opacity는 0이다. 두 구간의 boundary time 문자열도 같으며 각 구간 `h`는 `5.20833333350623207e-7`이다. Saved 첫 incoming interval은 정확히 [0,0]이고 둘째 incoming은 네 경우 모두 strict positive이다. 모든 `anchored` flag가 false인데도 세 anchor는 음수, 한 anchor는 양수로 저장되어 있어 flag만으로 seam을 없앨 수 없다는 점이 실제 자료에서도 드러난다. [S5]

Weight의 원 문자열은 101/102에서 `1.26606234609413413e-3`, 410/413에서 `1.26606234609413651e-3`다. 두 그룹이 같은 표시 근삿값을 갖더라도 exact point weight는 다르므로 uniform weight로 치환하지 않는다.

첫 구간의 초기조건과 photon-continuous seam은

\[
P_1(0)=f_{0,1}=0,\qquad
P_2(0)=P_1(h_1).
\tag{3}
\]

따라서 $e_j=P_j-F_j$의 incoming은

\[
e_{1,a}=0,\qquad e_{2,a}=P_1(h_1)-f_{0,2}.
\tag{4}
\]

이 정의가 모든 resolution과 precision에서 동일해야 한다. 첫 구간을 다시 평가하면서 $f_{0,1}=0$을 유지하는 것과 둘째 incoming을 0으로 재설정하는 것은 다른 작업이다. 후자는 동일 경로의 연속 문제를 보존하지 않는다.

## 2. Exact response와 frozen first variation의 구별

한 구간에서 지표 $j$를 생략하고

\[
\delta q=q-q_f,\quad \delta\lambda_i=\lambda_i-\lambda_{if},\quad
\delta\Lambda=\Lambda-L,\quad r=\delta q-\delta\Lambda F
\]

라 하면

\[
e'+\Lambda e=r.
\tag{5}
\]

정확한 Duhamel 표현은

\[
e(u)=\Phi(u,0)e_a+\int_0^u\Phi(u,v)r(v)\,dv,
\quad
\Phi(u,v)=\exp\!\left[-\int_v^u\Lambda(w)\,dw\right].
\tag{6}
\]

$\Lambda\ge0$이면 $0<\Phi(u,v)\le1$다. 따라서 동일 forcing의 incoming 차이에 대한 exact endpoint 반응은 선형이며 부호를 보존한다. 새 경로에 이 성질을 적용할 때도 각 경로의 $q,\Lambda,F$는 그대로 유지한다. 다른 node의 transfer coefficient나 remainder를 복사하는 근거가 되지는 않는다.

실제 원 구현은 (6)을 새로운 ODE solve로 평가하지 않는다. Incoming interval에서 exact stored center $c$와 outward radius $\eta\ge0$를 골라

\[
|e_a-c|\le\eta,\qquad (e^{(1)})'+Le^{(1)}=r,\quad e^{(1)}(0)=c
\tag{7}
\]

라는 frozen first variation을 적분하고 그 remainder를 제한한다. 위첨자 (1)은 first variation을 뜻하며 구간 번호 아래첨자와 구별한다. 즉 incoming first-variation gain은 $e^{-Lh}$이며, exact coefficient response $\Phi(h,0)$와 일반적으로 다르다. 차이는 remainder에 포함된다. 두 gain을 설명 없이 섞으면 증명과 구현의 추적성이 끊긴다. [S3]

$J(z,h)=\int_0^h e^{-zu}\,du$, $J(0,h)=h$로 두면 zero-incoming first variation $d_X$에 대한 incoming 증분은 $g_Xc$다.

| $X$ | $g_X$ |
|---|---|
| Photon endpoint | $e^{-Lh}$ |
| Species count $A_i$ | $\lambda_{if}J(L,h)$ |
| Species absorbed energy $B_i$ | $\lambda_{if}E_0J(L+1,h)$ |
| Species heat $H_i$ | $\lambda_{if}[E_0J(L+1,h)-\chi_iJ(L,h)]$ |
| Redshift $Z$ | $E_0J(L+1,h)$ |
| Source number/energy $Q_N,Q_E$ | $0$ |
| Endpoint energy stock | $E_he^{-Lh}$ |

각 종의 active heat weight $E(u)-\chi_i\ge0$를 전체 구간에서 확인하면 해당 heat gain도 비음수다. Inactive species는 frozen/continuous opacity가 모두 정확히 0이어야 한다. Code의 cutoffs와 binding energies $\chi_i$는 서로 다른 고정 상수이며 일치하도록 수정하지 않는다. [S4]

Number/energy first-variation ledger의 우변에는 incoming 중심이 남는다.

\[
d_P+g_Pc+\sum_i(d_{A_i}+g_{A_i}c)-d_{Q_N}=c,
\tag{8}
\]
\[
E_h(d_P+g_Pc)+\sum_i(d_{B_i}+g_{B_i}c)
+d_Z+g_Zc-d_{Q_E}=E_0c.
\tag{9}
\]

둘째 구간에서 이 우변을 0으로 검사하면 정상 incoming을 오류로 분류하거나 실제 incoming 누락을 은폐할 수 있다.

## 3. Incoming 반경과 local coefficient remainder

$\delta_a=e_a-c$, $R=e-e^{(1)}$라 두면

\[
R'+LR=-\delta\Lambda e,\quad R(0)=\delta_a.
\tag{10}
\]

원 fixed-gas domain의 $\Lambda\ge0,F\ge0$를 사용하여

\[
B_r=\int_0^h\bigl(|\delta q|+|\delta\Lambda|F\bigr)du,
\quad
S=|c|+\eta+B_r,\quad \|e\|_\infty\le S
\tag{11}
\]

를 얻는다. 구간 끝까지의 kernel을

\[
W(v)=e^{-L(h-v)},\quad K_0(v)=J(L,h-v),
\quad K_E(v)=E(v)J(L+1,h-v)
\]

로 정의하면 remainder의 정확한 구조는

\[
R_P=g_P\delta_a-\int_0^h W\delta\Lambda e\,dv,
\tag{12}
\]
\[
R_{A_i}=g_{A_i}\delta_a+
\int_0^h[\delta\lambda_i-\lambda_{if}K_0\delta\Lambda]e\,dv,
\tag{13}
\]
\[
R_{B_i}=g_{B_i}\delta_a+
\int_0^h[E\delta\lambda_i-\lambda_{if}K_E\delta\Lambda]e\,dv,
\tag{14}
\]
\[
R_{H_i}=g_{H_i}\delta_a+
\int_0^h[(E-\chi_i)\delta\lambda_i
-\lambda_{if}(K_E-\chi_iK_0)\delta\Lambda]e\,dv.
\tag{15}
\]

Redshift의 coefficient kernel은 $-K_E\delta\Lambda$다. 따라서 종별 bound는

\[
|R_X|\le |g_X|\eta+S\int_0^h|T_X(v)|\,dv.
\tag{16}
\]

각 whole-cell interval이 적분 kernel을 포함하고 outward quadrature가 적분을 포함한다는 것이 실제 inclusion 근거다. $N$을 바꾼 결과끼리 겹치는 것은 이 근거를 대체하지 않는다. Source moments는 incoming에 의존하지 않으므로 이 coefficient-coupling remainder가 0이고, 해당 signed integral의 수치 반경은 여전히 따로 존재할 수 있다.

총 count에서 $\sum_iT_{A_i}=W\delta\Lambda$, $\sum_ig_{A_i}=1-g_P$다. 그러므로

\[
R_P+R_{A,\rm tot}=\delta_a,
\quad
|R_{A,\rm tot}|\le(1-g_P)\eta+S\int W|\delta\Lambda|.
\tag{17}
\]

Photon의 incoming bound $g_P\eta$를 total-count incoming bound로 복사할 수 없다. Energy도

\[
E_hR_P+R_{B,\rm tot}+R_Z=E_0\delta_a
\tag{18}
\]

이므로 incoming 항을 별도로 운반한다. 서로 다른 완결된 증명에서 얻은 valid coefficient upper bound 두 개의 최소값은 쓸 수 있다. 한 증명의 incoming 항과 다른 증명의 일부 coefficient 항을 선택하여 미증명된 조합을 만들면 안 된다. 원 `remainder_bounds`는 이 구분을 따른다. [S3,S4]

구현의 `nonlinear_upper`는 (16)의 coefficient-coupling remainder 이름이다. $P$의 원 ODE는 선형이다. Incoming $c$가 고정된 $O(1)$이면 일부 remainder는 coefficient variation에 대해 $O(\varepsilon)$이므로 이를 전부 2차 물리 correction이라고 해석하지 않는다.

## 4. Captured 표현, 둘째 incoming, 누적 moment

Captured 첫 endpoint를 $n_1$라 하면

\[
\rho_{P,1}=F_1(h_1)-n_1,\qquad
\kappa=n_1-f_{0,2},
\]
\[
e_{2,a}=e_1(h_1)+\rho_{P,1}+\kappa
       =[P_1(h_1)-n_1]+\kappa.
\tag{19}
\]

원 `segment`의 `true_minus_captured_interval`에는 이미 $\rho_P$가 포함되어 있다. 그러므로 `seam`은 그 correction interval에 `captured_photon_stitch_residual` $\kappa$를 더한다. 이 결과는 (4)와 정확히 같은 목표다. $\rho_P$를 여기서 다시 더하면 이중 반영이고, frozen-only defect를 그대로 쓰면 누락이다. Captured 입력에서 $\kappa=0$을 확인했어도 $\rho_P=0$은 따라오지 않는다.

새 incoming center는 outward interval 안에서 택한 저장된 exact decimal이며, 재중심화의 rounding을 반경에 포함한다. 새 node의 $e_{2,a}$를 다른 node에서 복사하거나 이전 $N$의 incoming을 고정하여 둘째 segment만 다시 평가하면, 그 사실을 별도 mixed-resolution 계약으로 정의해야 한다. 이번 독립 work unit은 두 segment를 같은 $N,P$로 순서대로 평가하도록 하는 것이 직접적이다.

Moment $M_X$의 captured increment $C_{X,j}$에 대해

\[
M_{X,j}-C_{X,j}
=(M_{X,j}-M_{f,X,j})+(M_{f,X,j}-C_{X,j}),
\tag{20}
\]
\[
\Delta M_{X,\rm path}=\Delta M_{X,1}+\Delta M_{X,2}.
\tag{21}
\]

누적 moment의 기존 반경은 두 번째 photon damping gain을 곱하지 않고 그대로 더한다. 이미 흡수·방출·redshift된 moment는 다음 photon stock과 동일한 상태 변수가 아니다. Final photon은 마지막 endpoint이며 두 endpoint photon을 더하지 않는다.

Native energy stock은 $E_hn$과 정확히 같다고 가정하지 않는다.

\[
\rho_U=E_hF_h-U_{\rm cap}/\epsilon
=E_h\rho_P+[E_hn-U_{\rm cap}/\epsilon].
\tag{22}
\]

원 코드의 직접 energy-stock 표현을 유지하고 대괄호 항을 삭제하지 않는다. 비영인 deterministic representation shift 자체는 불확실성이나 오차 반경이 아니다. 그 shift를 포함하는 수치 interval의 폭과 구별해야 한다.

## 5. Energy seam은 signed stock jump다

두 구간 경계의 에너지 차와 true anchor는

\[
\Delta E=E_{0,2}-E_{0,1}e^{-h_1},\qquad
J_{\rm seam}=\Delta E\,P_1(h_1).
\tag{23}
\]

구간별 identity

\[
E_{j,h}P_j(h_j)-E_{0,j}P_j(0)
+B_{{\rm tot},j}+Z_j-Q_{E,j}=0
\]

를 더하면

\[
E_{2,h}P_2(h_2)-E_{0,1}P_1(0)
+\sum_{j=1}^2(B_{{\rm tot},j}+Z_j-Q_{E,j})
-J_{\rm seam}=0.
\tag{24}
\]

따라서 whole-path ledger에서는 anchor를 뺀다. $\Delta E$의 부호를 절댓값으로 바꾸거나 heat/redshift에 흡수하면 기존 관측량 정의가 바뀐다. `anchored=false`는 $\Delta E=0$이라는 exact statement가 아니므로 이 flag만으로 seam을 없애지 않는다. [S3]

Native photon baseline을 쓴 분해는

\[
J_{\rm seam}=\Delta E\,n_1+
\Delta E\,[P_1(h_1)-n_1].
\tag{25}
\]

둘 다 같은 signed $\Delta E$를 사용한다. $\Delta E\in D$, $P_1(h_1)\in I_P$이면 직접 interval product $D I_P$는 안전하다. 중심·반경으로 풀어 쓸 경우 $\eta_E\eta_P$ 교차항을 버리지 않는다. Number에는 해당 energy anchor를 넣지 않는다.

## 6. Old/new enclosure의 엄밀한 비교와 교체

각 후보의 target key는 적어도 `(OFF, node, ordered segment keys, exact row/stage definition, source/mask, initial stock, photon carry, signed energy seam, spectral weight, observable, captured baseline, reduction route)`를 고정한다. Source archive/hash는 그 정의의 운반 identity이며 정의 자체를 대체하지 않는다. 다음 조건을 모두 충족한 뒤 새 항의 admission을 판정한다.

1. 원 PR20 captured row/stage와 새 control이 동일한 binary64 lift이고, 두 segment의 시간·photon·η·weight seam을 확인한다. 첫 $f_0=0$, positive point weight, source/mask, no-outflow와 stage domain을 확인한다.
2. Frozen definition, continuous coefficient definition, constants, units, true-vs-captured reference 및 전역 moment representation이 동일하다.
3. Old와 new 각각의 interval validity가 해당 source·input 및 실제 execution evidence에 결합되어 있다. Endpoint는 유한하고 $L\le U$다. Overlap만을 validity의 근거로 삼지 않는다.
4. 새 inputchecker가 일반 두-segment 경로를 검사한다. 원 `run_track`의 `REUSED`는 OFF 0/700의 특정 local row뿐이므로 새 101/102/410/413에서 다른 node의 local certificate를 재사용하지 않는다.
5. Signed energy seam과 incoming/cumulative propagation이 완결된다. Zero-containing number/energy/heat ledger는 필요한 consistency check지만, 잘못된 target도 zero-containing interval을 만들 수 있어 충분조건은 아니다.
6. A/B/H total의 전역 비교는 양쪽 모두 **세 species interval의 합**을 쓴다. 원 solver가 추가로 제공하는 dedicated total certificate를 새 쪽에만 대입하지 않는다. OFF/KF/GM를 합하지 않는다.

이 조건에서 $x\in I^{\rm old}$ 및 $x\in I^{\rm new}$이면

\[
x\in I^\cap=I^{\rm old}\cap I^{\rm new}.
\tag{26}
\]

통계적 독립은 필요 없다. 두 valid 같은-target interval의 교집합은 비어 있을 수 없다. Empty intersection은 target mismatch, certificate/implementation 오류 또는 evidence failure를 조사할 사건이며, hull·평균·사후 tolerance로 덮지 않는다. 서로 다른 target의 interval overlap은 (26)을 허용하지 않는다.

Primary 보고는 same-target 확인 후 old/new containment, endpoint overlap, 실제 width change를 그대로 남긴다. $I^{\rm new}\subseteq I^{\rm old}$이면 직접 교체가 nested refinement다. Nested가 아니어도 새 interval이 valid이면 같은 목표의 replacement지만 폭이 넓어질 수 있다. Intersection을 사용한다면 raw new 결과와 별도로 표시하여 실제 새 방법의 성능과 old 지식과의 결합을 구분한다.

## 7. $N$ 상향의 효과와 제거하지 못하는 항

Signed first-variation integrand를 $f_X(t)$라 하면 한 cell의 validated midpoint remainder는

\[
\left|h\int_{j/N}^{(j+1)/N}f_X(t)dt-
\frac hN f_X\!\left(\frac{2j+1}{2N}\right)\right|
\le \frac{hM_{X,j}}{24N^3},
\quad M_{X,j}\ge\sup_{\rm cell}|f_X''(t)|.
\tag{27}
\]

고정 branch에서 global $M_X<\infty$가 있으면 합은 $hM_X/(24N^2)$ 이하이다. 이것이 원 `local_integrals`의 수치 적분 component가 갖는 조건부 감소율이다. 실제 cell $M_{X,j}$, interval dependency, Decimal outward rounding 및 incoming은 함께 변할 수 있으므로 전체 path radius가 정확히 $N^{-2}$로 감소하거나 모든 $N$에서 단조 nested일 필요는 없다. [S3,S4]

현재 출력 radius는 구조적으로

\[
r_X(N,P)=r_{X,\rm num+repr}(N,P)
+|G_X(P)|_{\rm up}\eta_a
+S_{\rm up}(N,P)\,T_{X,\rm up}(N,P)
\tag{28}
\]

이다. Endpoint·local moment별 이 세 항과 이전 누적 moment 반경을 별도로 기록하면 다음 투입이 어떤 항을 줄이는지 판별할 수 있다.

고정 $q,\Lambda,F,c,\eta_a$와 같은 first-variation bound route에서 $N\to\infty$는 수치 적분 오차를 줄일 수 있지만 $|g_X|\eta_a$와 일반적으로 비영인 analytic bound $S\int|T_X|$를 자동으로 0으로 만들지 않는다. 예를 들어 $\Lambda=L=0$의 정확한 local 적분에서도 $g_P=1$이므로 고정 incoming radius는 그대로 남는다. 실제 두-segment refinement에서는 첫 segment가 개선되면 둘째 $\eta_a$도 줄 수 있으므로 이를 항상 고정된 숫자라고 취급하지 않는다.

여기서 말하는 remainder floor는 **선택한 enclosure 공식 및 고정 incoming interval의 표현상 한계**다. 실제 exact solution의 오차에 대한 양의 하한, 모델의 본질적 불확실성, 모든 알고리즘의 lower bound를 뜻하지 않는다. 같은 target에 더 강한 analytic response나 correlated reduction을 유도하면 달라질 수 있다. (N32/P60), (N128/P60), (N512/P60), (N32/P80)은 해상도와 rounding을 구분하는 사전 고정 비교로 해석할 수 있지만, 이전 node의 실행시간과 축소율은 새 node에 대한 보장으로 쓰지 않는다.

## 8. 전체 finite 폭의 실제 개선 가능 상한

같은 OFF 관측량 $X$와 같은 species-sum/Minkowski route에서 baseline을 PR21의 두 OFF replacement 이후 hybrid로 고정한다. 원 양의 spectral weight $w_p$를 한 번 적용한 per-path interval의 폭을 $b_{p,X}\ge0$라 하면

\[
W_X=\sum_{p=0}^{2439}b_{p,X},\quad
B_{K,X}=\sum_{p\in K}b_{p,X},\quad
F_{K,X}=\sum_{p\notin K}b_{p,X}.
\tag{29}
\]

선택 $K$만 바꿀 때 새 폭과 감소량은

\[
W_X^{\rm new}=F_{K,X}+\sum_{p\in K}b^{\rm new}_{p,X},
\quad
G_{K,X}=B_{K,X}-\sum_{p\in K}b^{\rm new}_{p,X}\le B_{K,X}.
\tag{30}
\]

따라서 $W_X>0,F_{K,X}>0$이면

\[
\frac{G_{K,X}}{W_X}\le\frac{B_{K,X}}{W_X},\qquad
\frac{W_X}{W_X^{\rm new}}\le\frac{W_X}{F_{K,X}}.
\tag{31}
\]

PR21에서 정확한 saved rational 결과를 반올림해 보고한 기존 ceiling은 다음과 같다. 이 수치는 실제 새 solver의 개선율이 아니다. [S1]

| OFF 목표 | 선택 $K$ | 해당 두 항을 폭 0으로 만들어도 가능한 감소 비중 |
|---|---|---:|
| Photon | 101, 102 | 0.7871572984% |
| Species-sum absorption count | 101, 102 | 0.8814078231% |
| Species-sum absorbed energy | 101, 102 | 0.6295980743% |
| Species-sum heat | 410, 413 | 0.2974840851% |

네 node를 모두 평가하는 $K=\{101,102,410,413\}$의 ceiling은 두 항별 ceiling과 별도로 계산했다. `PREDECESSOR_BUDGET.json`에 저장된 exact rational endpoint에서 아래 5개 지표 모두 predecessor = retained outside K4 + old K4 identity를 직접 확인하고 식 (29)–(31)을 적용했다. 이는 saved-data arithmetic이며 새 coefficient 평가가 아니다. Exact 값은 `review/FOUR_NODE_MAX_GAIN_CEILING.json`에 있다. [S5]

| OFF 목표 | K4 최대 상대 폭 감소 [%], 표시 반올림 | 전체 폭의 최대 old/new 비 |
|---|---:|---:|
| Photon | 1.103075264116881 | 1.011153787309998 |
| Species-sum absorption count | 1.184151043335031 | 1.011983412133152 |
| Species-sum absorbed energy | 0.921774055100526 | 1.009303497779756 |
| Species-sum heat | 0.338926683880846 | 1.003400793033864 |
| Signed whole-path anchor | 0.404623669521600 | 1.004062675240856 |

단위가 다른 photon/heat 비중을 더하지 않는다. 실제 global replacement를 하면 유지한 2436개 항의 직접 합과 새 네 항의 합으로 구성하며, 그 retained 항에는 앞서 승인한 OFF 0/700의 N512 결과가 그대로 들어간다. Rounded aggregate에서 old 항을 일반 interval subtraction으로 제거하지 않는다. Already-weighted old field에 weight를 다시 곱하지 않는다.

현재 외부에서 주어진 물리 tolerance는 없다. 그러므로 성공 기준은 target-preserving validated enclosure와 실제 component별·관측량별 improvement의 보고다. Top-node 선정만으로 의미 있는 물리 accuracy 달성이나 continuum spectral error 제어를 선언할 수 없다. Finite quadrature node 사이 모델, gas 재진화, physical/production, actual photon·heat·recoil delivery 및 receiver adoption은 이 루프에서 승격되지 않는다.

## 9. 실제 검산과 다음 판단에 필요한 증거

Exact toy는 $\Lambda=0$, 각 구간 $h=1$인 제조 모델을 사용한다.

\[
F_1=2+u,\quad q_1=1+u,\quad P_1=2+u+u^2/2;
\]
\[
F_2=3+2u,\quad q_2=2-u,\quad P_2=7/2+2u-u^2/2.
\]

첫 incoming은 0, 둘째는 $1/2$, 최종 photon은 5다. 둘째 incoming을 0으로 리셋하면 $9/2$가 되어 정확히 $1/2$만큼 틀린다. Energy는 실제 계약과 같은 $E_j=E_{0,j}e^{-u}$를 쓰고 $T=e^{-1}$의 다항식환 $\mathbb Q[T]$에서 ledger를 검사했다. $E_{0,2}=5$ 및 $1/2$를 사용하여 양·음 seam을 모두 확인했다. $T$의 부호 판정에는 유한 $e$ Taylor 합과 유리수 geometric-tail bound만 사용했다.

41개 검사에는 nonzero frozen/native representation과 photon gap의 전달, 누적 moment의 부당한 damping 반례, signed seam 누락/부호 반전 반례, fixed incoming radius, wrong-target overlap 및 fixed weighted-width floor가 포함된다. 실제 결과는 **exit 0, 실패 0, 0.0054768940초, 최대 RSS 11,392 KiB**다. 이 숫자는 toy 실행의 비용이며 새 네 후보의 계산 비용을 뜻하지 않는다. 원본 소스 SHA는 실행 전후 동일하다.

이 기여에서 닫힌 것은 two-segment 전달 및 비교의 수학적 계약과 좁은 exact algebra controls다. 실제 네 경로의 source-bound input checker, old/new output 및 whole-cell domain evidence, 실제 resource receipt와 별도 독립 decision이 있어야 해당 네 경로의 numerical admission이 닫힌다. 이 요구를 추가적인 물리·전역 감사 루프로 확대할 필요는 없다.

## 직접 읽은 source와 재현 포인터

- **[S1]** `intake/PR21_REPORT_KO.md`: 입력 계보, 일반 2segment 후보, weighted-width ceiling. SHA `75b1c7e885729c1bd5b86d583ba4b5149a9b369efa1d102a2307ee5c4884f193`.
- **[S2]** `dependencies/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1/NEXT_DAG.json`: 이번 node·candidate union·fixed-input·claim ceiling. SHA `dd60e12a6d5c6dbb8a2de1ffe7885e9b40f43c3885e81bb9651b217b482b35c2`.
- **[S3]** `dependencies/pr19/BASS_HE_E13C5_INCOMING_ANCHOR_ENCLOSURE_20261011_v1/THEORY.md` 전체 및 `code/path_enclosure.py` 전체. Source SHA는 각각 `16ef3e4f7ed51c2ace87f7e36570917f3a1074c55dfe7bce5d9c7849d9c069e5`, `c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73`.
- **[S4]** 같은 PR19 root의 `code/local_enclosure.py`: 상수·`Coefficients`·`integrands`까지 직접 읽음. 나머지 CLI 전체를 다시 검토하지 않음. SHA `fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370`.
- **[S5]** `BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1/inputs/`의 `PATH_CONTROLS.json`, `OLD_PATHS_OFF4.jsonl`, `PREDECESSOR_BUDGET.json`. SHA는 각각 `315cdd87854bba1a5ccf2d875a7a58f216853ecc8ddd2e250b50be8904add73d`, `6535bd33ea4e4334dc314a8b730d47d799d6ab3e583d605fa998d3a159aed0e0`, `2fb4367dae98ea9d07b5e6363489584110eea087c3c74791534e6f4cc5306e9f`.
- **실제 toy code:** `review/theory_controls/exact_transfer_toys.py`, SHA `41d70dc4d7e2afa0cbaa708d083aa57bac9104392aa355cedad7f8b601d9fcae`.
- **실제 toy result:** `review/theory_controls/EXACT_TRANSFER_TOY_RESULTS.json`, SHA `4fac91e01b970e9377af43fdff001df64819444a222d10e97880f0b4fda29840`.
- **읽은 파일 identity:** `review/TRANSFER_THEORY_READ_IDENTITIES.json`. 수학 유도와 exact toy가 근거이며 외부 문헌의 새 주장을 사용하지 않았다.
