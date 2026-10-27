# CR 적분 반환의 보존적 REI 연결과 정규화 미분

## 결과와 근거 상태

이번 이론 단위는 CR PR107의 실제 적분 진단 반환을 기존 REI 25좌표와 별도의 retained-photon 수·에너지 포트에 연결하는 식을 완성한다. 포획된 fast 전자 수와 이온 전하를 함께 줄이면 열적 전자 수가 보존되고, 이온 결합에너지·fast kinetic energy·retained photon energy의 합이 보존된다. 물리적 사건률이나 시간 이력을 생성하지 않고도, 공급자가 반환한 세 적분량과 기준밀도에 대한 정확한 interface JVP를 구성할 수 있다.

현재 이론 판정은 **DERIVED_CONSERVATIVE_INTEGRATED_DIAGNOSTIC_LIFT**다. 아래 식과 한 번의 Wolfram 기호 검산은 이론 근거이며, 실제 consumer 구현·새 수치 검사·C9 채택은 해당 단계의 결과로 별도 기록한다. 원본 DAG의 작업 **32/88**, 중앙 **27/88**은 이 이론 문서만으로 변하지 않는다.

동결 권위는 상위 [FROZEN_CONTRACT.md](../FROZEN_CONTRACT.md)다. CR science source는 `4e72c89b714431eb4c6ae07def777bbf72a5ae4c`, REI 기준 source는 `ee6746ab172f862dddfdec63b59e5e3707b59eaa`다.

## R3. 대상·전제·주장 정렬

### 공급자가 실제 반환한 자료

CR의 `INTEGRATED_EVENT_EXPORTS.json`에는 8개 numerical case와 3개 source redshift의 조합에 해당하는 24개 반환이 있다. 각 행은 별개의 대안이며, 24행을 한 사건의 여러 성분처럼 더하지 않는다. 파일의 Git blob은 `3284a00148f5e16522f1c28e5db350f345c2b797`, SHA256은 `c6da1e2f8a079c123ab218875c27bd6f5bc73beb5465832cc28a9275b455e1b1`, 크기는 91,839 bytes다.

공급자는 다음 사건을 다룬다.

\[
{}^4{\rm He}^{2+}+e_{\rm fast}
\longrightarrow {}^4{\rm He}^{+}(1s)+\gamma_{\rm retained}.
\]

REI native species index는 He4II가 11, He4III가 12다. 원자 문턱은 \(I=54.42\,\mathrm{eV}\), \(I_J=I\times1.602176634\times10^{-19}\,\mathrm J\)다. isotope 대응은 elemental He에서 He4로의 조건부 대응이다. stationary heavy target, zero recoil, nonrelativistic scalar isotropic ensemble, ground spontaneous capture, frozen bath를 전제로 한다. 지원 photon energy는 54.42–50000 eV다.

고정 bath는 \(T=10000\,\mathrm K\), \(n_e=0.14\,\mathrm{cm}^{-3}\), \(n_{{\rm HeIII}}=0.01\,\mathrm{cm}^{-3}\), \(\ln\Lambda=20\)이며, HI/HII/HeI/HeII/HeIII 수밀도는 \((.9,.1,.07,.02,.01)\,\mathrm{cm}^{-3}\)다. 이것을 이전 PW19 donor의 \(T=14919.863839279506\,\mathrm K\) 상태와 동일시하지 않는다.

실제 반환에서 \(n_b\), exposure, event rate, instantaneous RHS, emission time history, emission spectrum, physical heating은 null이다. `finite_coupled_abundance_update=false`와 `state_update_applied=false`를 보존한다. source qualification의 legacy `source_commit`은 저장된 이전 chain의 출처이며, 현재 export 파일이 있는 science commit과 의미가 다르다. 두 출처를 그대로 구분한다.

### 세 적분량과 좌표

한 행에서

\[
A=N_{\rm cap}\ge0\quad[\mathrm{m}^{-3}],\qquad
K=-U_{\rm fast}\ge0\quad[\mathrm{J\,m}^{-3}],\qquad
G=U_{\gamma,\rm retained}\ge0\quad[\mathrm{J\,m}^{-3}]
\]

를 읽는다. 이들은 rate가 아니라 proper-volume integrated diagnostic이다. 원래 저장된 일곱 signed energy reservoir, canonical event ID, source ID, frame, qualification을 함께 보존한다. 이미 SI로 바뀐 수치를 다시 변환하지 않는다.

공급자의 에너지 조건은

\[
\epsilon_E=G-K-I_JA,
\qquad
\frac{|\epsilon_E|}{|G|+|K|+|I_JA|}
\le2\times10^{-13}.
\]

실제 \(G\)는 독립된 관측 입력으로 유지한다. 이를 \(K+I_JA\)로 대체하여 residual을 인위적으로 0으로 만들지 않는다. 모든 항이 정확히 0인 경우에는 residual도 정확히 0인 별도 경계로 처리한다.

Per-baryon projection에는 consumer가 명시적으로 지정한 \(b=n_b>0\)가 필요하다. 이를 주지 않으면 proper-volume 반환과 null projection을 유지한다. 검사의 \(b=1.4\times10^6\,\mathrm{m}^{-3}\)는 선언된 정규화 fixture다. bath의 수밀도에서 계산한 물리 상태를 공급자 대신 승인하는 값이 아니다.

## R4. 표현의 선택

세 후보를 비교한다.

| 후보 | 필요한 추가 입력 | 이번 선택 |
|---|---|---|
| 적분량을 ODE rate로 환산 | 실제 exposure 또는 source-matched time history | 입력이 없으므로 해당 포트는 null 유지 |
| 평균 photon energy를 단색 spectrum으로 전달 | 실제 spectrum 또는 정당화된 closure | 평균은 moment ratio로 유지 |
| 실제 적분량을 conservative diagnostic과 별도 photon port로 전달 | 명시적 정규화와 기존 native species/energy 벡터 | 이번에 구성·구현할 표현 |

선택한 표현은 공급자의 완성된 count·energy 결과를 실제 consumer에서 이용하고, 다음 photon transport나 source-history 작업에 필요한 양을 잃지 않는다. 기존 25좌표의 의미와 순서를 유지한다.

\[
Z_{25}=(Y[21],\zeta,w_{\rm nt},w_{\rm ext},\ell),
\qquad \ell=\log(T/\mathrm K).
\]

Retained photon count와 energy는 별도 포트 \((\eta_\gamma,w_\gamma)\)로 둔다. 필요할 때만

\[
Z_{27}=(Z_{25},\eta_\gamma,w_\gamma)
\]

라는 diagnostic serialization을 사용한다. 이 표기는 새로운 27-state ODE client를 뜻하지 않는다.

## R5. 보존적 구성과 미분

### 5.1. Event map

\[
a=\frac{A}{b},\qquad
k=\frac{K}{b},\qquad
g_\gamma=\frac{G}{b},\qquad
s=e_{11}-e_{12}.
\]

Diagnostic increment는

\[
\begin{aligned}
\Delta Y&=a\,s, &
\Delta\zeta&=-a, &
\Delta w_{\rm nt}&=-k,\\
\Delta w_{\rm ext}&=0, &
\Delta\ell&=0, &
\Delta\eta_\gamma&=a, &
\Delta w_\gamma&=g_\gamma.
\end{aligned}
\]

모든 다른 native 행은 정확히 0이다. Photon을 native external ledger에 중복 기입하지 않는다. \(w_{\rm ext}\)는 이전과 같은 signed external-transfer ledger다.

### 5.2. 전하·열적 수·핵종 보존

Native 전하 벡터를 \(q\), 질량수 벡터를 \(m\)이라 두면

\[
\mathbf1^Ts=0,\qquad q^Ts=-1,\qquad m^Ts=0.
\]

원자핵 수와 baryon 수가 보존된다. 전체 전하가 요구하는 자유전자 중 fast 전자를 뺀 열적 전자 abundance는

\[
g=q^TY-\zeta.
\]

따라서

\[
\Delta g=q^T\Delta Y-\Delta\zeta=-a-(-a)=0.
\]

Monatomic thermal pool의 입자 abundance

\[
\chi=(\mathbf1+q)^TY-\zeta
\]

도 \(\Delta\chi=0\)다. Selected event는 thermal kinetic energy를 바꾸지 않으므로

\[
U_{\rm th}=\frac32 k_B b T\chi
\]

에서 \(T\)와 \(\ell\)의 event increment도 0이다. 이는 fast 전자를 bath에 열적으로 편입시키는 PR237의 assimilation 항과 다른 사건 소유권에서 나온다.

### 5.3. 에너지 보존

Native 누적 ionization-energy 벡터를 \(B\)라 두자. 기존 `atomic_network.py`는 coefficient의 연속 문턱을 더해 \(B\)를 만든다. He4 indices10/11/12와 coefficient `2:1`의 54.42 eV를 확인했으므로

\[
B^Ts=B_{11}-B_{12}=-I_J
\]

다. 누적 floating-point subtraction의 일치는 정당화된 residual로 판정한다.

\[
B^T\Delta Y+\Delta w_{\rm nt}+\Delta w_\gamma
=\frac{-I_JA-K+G}{b}
=\frac{\epsilon_E}{b}.
\]

열·external·recoil·escape의 selected-model increment는 0이다. Fast-removal diagnostic을 photon과 binding의 합에 한 번 더 더하지 않는다. 이 관계는 세 입력 적분량의 에너지 제약을 그대로 consumer에 옮긴다.

### 5.4. 일반 interface JVP

\(I_J\)는 고정된 원자 입력이다. 세 moment와 정규화의 독립된 방향 \((dA,dK,dG,db)\)에 대해

\[
da=\frac{dA}{b}-a\frac{db}{b},\qquad
dk=\frac{dK}{b}-k\frac{db}{b},\qquad
dg_\gamma=\frac{dG}{b}-g_\gamma\frac{db}{b}.
\]

이들을 event map의 \((a,k,g_\gamma)\) 자리에 넣으면 JVP가 된다. Tangent는 signed real 값이다. Base moment의 nonnegativity 조건을 tangent에 잘못 적용하지 않는다.

에너지 residual의 미분은

\[
d\left(\frac{\epsilon_E}{b}\right)
=\frac{dG-dK-I_JdA}{b}-\frac{\epsilon_E\,db}{b^2}.
\]

에너지와 양립하는 tangent subspace는 \(dG=dK+I_JdA\)다. 그 방향에서는 inherited floating-point residual의 quotient 미분만 남는다. 이 조건을 만족하지 않는 방향에서는 위 식의 비영 값이 올바른 derivative다. API가 이를 임의로 0으로 투영하면 일반 interface 미분을 잃는다.

이 미분은 공급자가 돌려준 적분량에 대한 consumer derivative다. CR physical parameter에 대한 \(dA,dK,dG\) 자체를 이번 작업이 계산했다는 뜻은 아니다.

### 5.5. 기준밀도 정규화

\(b=\beta r\)인 reference normalization에서는

\[
\Delta X=\beta\,\Delta Z,\qquad
d\Delta X=\beta\,d\Delta Z+\Delta Z\,d\beta
\]

를 density-like 행에 적용한다. 27좌표 serialization의 density-like 행은 indices0–23,25–26이고, logT index24는 제외한다.

\[
db=\beta\,dr+r\,d\beta
\]

를 만족하는 방향을 대입하면, 예를 들어

\[
d\left(\beta\frac{A}{b}\right)
=d\left(\frac{A}{r}\right)
=\frac{dA}{r}-\frac{A,dr}{r^2}.
\]

따라서 \(\beta\)의 중간 표현에 의존하지 않고 direct proper-volume/reference quotient와 일치한다. Energy와 photon-count 행도 같은 계산으로 닫힌다.

### 5.6. 적분량의 clock 불변성

Continuous RHS는 \(d\eta/dt=H>0\) 아래 \(F_\eta=F_t/H\)로 변한다. 그러나 적분량은

\[
\int F_t\,dt=\int\frac{F_t}{H}\,d\eta
\]

로 같은 값이다. 형식적인 point-event도

\[
\delta(t(\eta)-t_0)=H(t_0)\delta(\eta-\eta_0)
\]

이므로 같은 cancellation을 갖는다. 따라서 integrated diagnostic을 \(H\)로 나누지 않으며, unrelated clock 방향의 derivative는 0이다. 이 계산은 실제 반환에 없는 emission time history를 만들어 쓰지 않는다. PR237의 continuous source/JVP 계약은 그대로 유지한다.

### 5.7. 변하는 reference의 endpoint algebra

동일한 physical volume에서 두 reference 값을 명시했다고 하자. 실제 물리 밀도 변화 \(\Delta n\)와 초기 normalized coordinate \(x_-\)를 알면

\[
x_+=\frac{r_-x_-+\Delta n}{r_+}.
\]

이를 미분하면

\[
dx_+=\frac{r_-dx_-+x_-dr_-+d\Delta n}{r_+}
-x_+\frac{dr_+}{r_+}.
\]

LogT는 density rebase를 받지 않고 값과 tangent를 그대로 전달한다. 이 유틸리티는 고정 volume의 좌표 algebra이며, source history나 expansion evolution을 계산하지 않는다.

기존 연속방정식 convention은 별도로

\[
\dot r+3Hr=R_r,\qquad
\dot n+3Hn=S,\qquad
F_x=\frac{S-xR_r}{r},
\]

\[
dF_x=\frac{dS-R_rdx-x,dR_r}{r}-F_x\frac{dr}{r}
\]

로 유지한다. Reference의 \(R_r\)를 total \(\dot r\)와 혼동하지 않는다.

### 5.8. Capacity 진단

Nonnegative manufactured capacities \(n_{{\rm HeIII}},N_{\rm fast},U_{\rm fast}\)와 \(A,K>0\)에 대해, amplitude \(s\ge0\)의 제거량이 각 capacity 이하일 필요충분조건은

\[
s\le s_{\max}
=\min\left(
\frac{n_{{\rm HeIII}}}{A},
\frac{N_{\rm fast}}{A},
\frac{U_{\rm fast}}{K}
\right).
\]

이는 세 선형 부등식을 교차시킨 결과다. 분모가 0인 제약은 제거량도 0인 경계에서 제한하지 않는 것으로 처리하고, 직렬화에서는 무한대를 null과 명시적 상태로 표현한다. 함수 min의 tie에서 일반적인 미분 가능성을 주장하지 않는다.

이 진단은 count·energy capacity만 검사한다. 실제 captured submeasure가 초기 fast distribution의 부분인지, frozen bath를 얼마나 갱신해야 하는지, 시간 이력이 무엇인지는 별도 입력 의무다. 따라서 capacity 통과를 finite physical state update의 승인으로 승격하지 않는다.

## R6. 독립 검산과 이론 검토

[SYMBOLIC_CHECKS.json](SYMBOLIC_CHECKS.json)에 한 번의 실제 Wolfram Language 입력·출력을 보존했다. 10초 time constraint 아래 다음 residual이 0이었다.

- thermal count와 conservative energy;
- 명시적 quotient JVP와 symbolic differentiation;
- \(b=\beta r\) reference 대응;
- endpoint rebase의 derivative.

기호 계산은 \(G=K+I_JA\)인 tangent-compatible 표현을 사용했다. 일반적인 독립 \(G\) 방향과 residual 미분은 §5.4에서 직접 유도했다. 실제 source-data 검산과 구현 검사는 C6–C9에서 다룬다. 원격 CPU는 `UNKNOWN_NOT_ZERO`다.

이 문서의 작성자는 scientific consumer/checker를 구현하지 않는다. Root가 이론을 별도로 검토하고, 구현 뒤 작성자가 code/raw result를 검토하는 역할 분리를 유지한다. Theory reviewer의 원자료 접근 범위와 code 구현 독립성을 검토 기록에 명시한다.

## R7. 판별 질문과 실제 검산 연결

기호 검산에서 열로 \(K\)를 중복 전달하는 식은 \(K/b\), photon을 중복 소유하는 식은 \((K+I_JA)/b\)의 에너지 residual을 남겼다. 이를 새 checker의 discriminating control과 연결한다.

동결한 수치 검증은 actual24 대안의 독립 projection, Decimal50 oracle, 두 finite-difference step과 동일한 analytic operand scale, reference cancellation, clock invariance, endpoint quotient, capacity boundary를 다룬다. 기존 suite·CR solver·quadrature·IVP를 재실행하지 않는다.

실제 수치값은 count 약 \(10^{-12}\,\mathrm{m}^{-3}\), energy 약 \(10^{-29}\,\mathrm{J\,m}^{-3}\)인 행을 포함한다. 따라서 `max(1,tiny)` 같은 무차원 floor 대신 행의 단위를 가진 operand sum으로 scale을 정한다. 정확한 zero 행은 따로 검사한다. Universal convergence order나 full physical Jacobian은 이 두-step 판별의 주장에 포함되지 않는다.

## R8. 이론 판정과 NG1–NG7

이번 결과는 지정된 사건과 입력 포트의 보존적 구성 및 미분이다. 불가능성·배제 정리를 새 성과로 제안하지 않는다.

| 항목 | 이번 적용 결과 |
|---|---|
| NG1 대상·양화 | 사건·정의역·positive normalization을 명시했다. 전체 kinetic model을 배제하는 명제는 제시하지 않았다. |
| NG2 증명 | Event 보존, quotient/JVP, clock 불변성, endpoint algebra를 직접 유도했다. |
| NG3 비자명성·비공허성 | 실제 admitted24 적분 반환에 연결하고 continuous RHS와 integrated quantity의 다른 clock 동작을 판별한다. |
| NG4 장애 기작 | 새 no-go의 장애 기작을 주장하지 않는다. 누락된 physical 입력은 정확한 의존성으로 관리한다. |
| NG5 과학적 귀결 | Retained radiation을 external/thermal ledger와 분리하고, 실제 공급량을 다음 consumer로 보존한다. |
| NG6 원전 비교 | Primary RR count/kinetic moment 근거를 확인했다. 새 물리 kernel·rate 또는 문헌 우선권을 주장하지 않는다. |
| NG7 독립 검토 | Symbolic check와 root 이론 검토를 연결하고, 구현/raw/figure의 별도 검토를 수행한다. |

Strong no-go 채택 상태는 `NOT_PROPOSED`다. 수학적으로 닫힌 구성은 derived로 보존하며, 공급자 입력 부재를 일반적인 불가능성으로 바꾸지 않는다.

## R9. 코드에 넘기는 계약

Implementation은 native25와 separate photon port를 반환한다. Flattened27은 serialization에만 쓰며 기존 native25의 index와 의미를 바꾸지 않는다. 명시적 \(b\)가 없는 reader path는 원래 proper-volume 자료를 유지한다. Actual source rows의 null rate/history/spectrum/heating과 false finite-update 상태를 보존한다.

Base number와 energy는 nonnegative finite real이어야 하고 \(b\)는 positive finite real이어야 한다. Bool·nonfinite·unsupported frame/channel/support·duplicate event·alternative batch 합산 시도를 거부한다. Signed tangent는 허용하되 finite real인지 검사한다. Zero event와 zero amplitude는 별도 정상 경계다.

기존 exporter의 `validate_event`만 명시적으로 재사용할 수 있다. Source copying이 이전 source generator·solver·suite의 실행을 허용하지 않는다. 새 checker의 독립 expected 값은 consumer를 호출하여 만들지 않고, 명시적 row formula를 Decimal로 계산한다.

원래 source energy 기준 \(2\times10^{-13}\), 새 algebra \(2\times10^{-14}\), mixed FD \(2\times10^{-8}\) 및 두 step \(2\times10^{-4},10^{-4}\)를 그대로 유지한다. 기준 변경이 필요해지면 실패와 이유를 먼저 root에 반환한다.

## R10. 이론 인계와 다음 입력

이번 이론 단위에서 전달한 것은 event/energy ownership, native species 대응, 일반 3-moment JVP, 기준밀도·clock·endpoint 식, capacity 진단, 검증할 mutant와 원래 허용오차다. 실제 구현 및 결과의 상태는 C5–C10 기록이 결정한다.

이후 물리적 결합을 확대하려면 source-matched duration/history 또는 별도로 자격화된 instantaneous source, retained-photon spectrum/measure, 동일 scenario의 transport 및 native client 입력이 필요하다. 기존 conditional mean energy를 단색 spectrum으로 대체하지 않고, CR capture hazard를 thermal assimilation rate로 바꾸지 않는다.

문헌 검색·출처 적용 범위는 [SOURCE_FINDINGS.md](SOURCE_FINDINGS.md)와 [SOURCE_FINDINGS.json](SOURCE_FINDINGS.json)에 모았다. 비용·게시·백업·DAG 상태는 상위 unit의 권위 기록을 따른다. 이 이론 작성은 새로운 과학 numerical run이나 기존 owner budget 사용을 동반하지 않았다.

